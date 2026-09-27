"""Capability sort: do the rules put more capable models on harder cards?

Idea-stage probe for docs/idea/constitutional-factory.md (r8, rules R1-R13).
ALL NUMBERS ARE SYNTHETIC.

Model of the world (hidden from the rules):
  - five difficulty tiers;
  - each model has one capability score c; its chance of passing a card of
    difficulty d is logistic(1.7 * (c - d + 1)), an item-response curve;
  - each model has a speed; each subscription a weekly cap that resets.

The rules see only outcomes: accepted or marked down, and cycle time.

Scenario (two weekly windows, 336 hours):
  - start from an INVERTED mapping: Claude and GPT licensed only to tier 2,
    MiMo and Qwen licensed to tier 4;
  - hour 60: a new model joins at tier 1 (R11);
  - hour 110: Qwen is upgraded (more capable and faster);
  - hour 200: Claude is silently degraded by its provider.

Policies compared:
  static    the starting mapping never changes
  ladder    R1-R6: promotion and demotion, but agents may pull any tier they
            hold, so capable agents can drift to easy work
  reserve   R1-R7 lean: the ladder with hardest-first pull for every agent, plus
            one extra rule for capped agents: below its home tier, a capped
            agent may spend only the cap above a hard-work reserve. New models
            get a fast track (low credit need until their first failed
            promotion). This is the recommended rule set.
  home-tier the r6 floor: the ladder plus the home-tier rule. No drifting down, except:
            help-down in capability order (a card must wait HELP_AFTER hours
            per tier of distance before an agent further above may take it,
            so the least over-qualified agents help first); and, for capped
            agents, surplus release above the hard-work reserve.
            Demotion is two-speed: gross failure after 10 cards; marginal
            failure only after two consecutive failing batches of 20.
            Promotion back-off is capped.

Run: python3 probes/pull-rules/capability_sort.py
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

HOURS = 336
WEEK = 168
TIERS = (1, 2, 3, 4, 5)
TOP = max(TIERS)
ARRIVALS = {1: 5.0, 2: 3.0, 3: 2.0, 4: 1.0, 5: 0.5}   # cards per hour
DURATION = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6}             # base hours per card
COST = {1: 1, 2: 2, 3: 4, 4: 6, 5: 10}                # subscription units per card
VALUE = COST
STANDARD = {1: .15, 2: .18, 3: .20, 4: .22, 5: .25}   # quality: max markdown rate
VELOCITY_STANDARD = 1.5                               # max cycle time vs tier median
PROMOTE_CREDIT, MARKDOWN_DEBIT = 20, 4
STRETCH_TRIALS, WINDOW = 20, 20
FAST_WINDOW, GROSS_FACTOR = 10, 2.0                   # gross failure demotes after 10 cards
MARGINAL_FACTOR = 1.25                                # marginal failure: two failing batches of 20
DEMOTE_FACTOR = 1.5                                   # velocity hysteresis
MAX_NEED = 2 * PROMOTE_CREDIT                         # back-off cap
FAST_TRACK_CREDIT = 5                                 # a new model's credit need until its first failed promotion
HELP_AFTER = 6                                        # hours per tier of distance before help-down
HARD_RESERVE = 0.75


def p_pass(c: float, d: int) -> float:
    return 1 / (1 + math.exp(-1.7 * (c - d + 1)))


@dataclass
class Agent:
    name: str
    c: float                      # hidden capability
    speed: float                  # hidden duration multiplier (>1 slower)
    concurrency: int
    cap: float | None             # weekly units; None = uncapped
    home: int                     # highest licence
    joins: int = 0
    allowance: int = 0
    used: float = 0.0
    busy: list = field(default_factory=list)
    credit: int = 0
    batch: list = field(default_factory=list)     # home-tier outcomes, judged every WINDOW cards
    strikes: int = 0                              # consecutive batches over the marginal line
    need: int = PROMOTE_CREDIT
    stretch: list = field(default_factory=list)
    hist: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=WINDOW)))
    cycle: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=WINDOW)))
    done: list = field(default_factory=list)   # (hour, tier, ok)
    homes: list = field(default_factory=list)  # home tier per hour
    log: Counter = field(default_factory=Counter)

    def duration(self, d: int) -> int:
        return max(1, math.ceil(DURATION[d] * self.speed))


@dataclass
class Card:
    tier: int
    born: int
    attempts: int = 0
    failed_by: set = field(default_factory=set)


def roster() -> list[Agent]:
    # Inverted start: the most capable models are licensed lowest.
    return [
        Agent("claude", c=4.8, speed=1.0, concurrency=6, cap=1400, home=2),
        Agent("gpt", c=4.6, speed=0.9, concurrency=6, cap=1400, home=2),
        Agent("mimo", c=3.4, speed=0.7, concurrency=10, cap=None, home=4),
        Agent("qwen", c=2.0, speed=1.6, concurrency=4, cap=None, home=4),
        Agent("newmodel", c=3.9, speed=0.9, concurrency=6, cap=None, home=1, joins=60),
    ]


def events(hour: int, agents: dict[str, Agent]) -> None:
    if hour == 110:
        agents["qwen"].c, agents["qwen"].speed = 3.0, 1.0      # upgrade
    if hour == 200:
        agents["claude"].c = 3.5                              # silent degradation


def ideal_tier(a: Agent) -> int:
    """Highest tier the agent can sustain at the quality standard (hidden truth)."""
    ok = [d for d in TIERS if 1 - p_pass(a.c, d) <= STANDARD[d]]
    return max(ok) if ok else 1


def tier_median(agents, d: int) -> float | None:
    meds = [statistics.median(a.cycle[d]) for a in agents if len(a.cycle[d]) >= 5]
    return statistics.median(meds) if meds else None


def run(policy: str, seed: int = 1, start=roster) -> dict:
    assert policy in ("static", "ladder", "home-tier", "reserve")
    rng = random.Random(seed)
    agents = start()
    by_name = {a.name: a for a in agents}
    queues = {d: deque() for d in TIERS}
    carry = defaultdict(float)
    replanned = 0
    for a in agents:
        a.allowance = a.concurrency
        if a.joins > 0 and policy != "static":
            a.need = FAST_TRACK_CREDIT                          # fast track for new entrants

    def may_pull_lower(a: Agent, d: int, hour: int) -> bool:
        if policy in ("static", "ladder") or d >= a.home:
            return True
        if policy == "reserve":                                 # hardest-first; capped agents
            if a.cap is None:                                   # keep a hard-work reserve
                return True
            home_rate = a.concurrency * COST[a.home] / a.duration(a.home)
            return (WEEK - hour % WEEK) * home_rate * HARD_RESERVE < a.cap - a.used - COST[d]
        behind = bool(queues[d]) and hour - queues[d][0].born >= HELP_AFTER * (a.home - d)
        if a.cap is None:
            return behind
        home_rate = a.concurrency * COST[a.home] / a.duration(a.home)
        hours_left = WEEK - hour % WEEK
        if hours_left * home_rate * HARD_RESERVE >= a.cap - a.used - COST[d]:
            return behind and d == a.home - 1
        return True

    for hour in range(HOURS):
        if hour % WEEK == 0:
            for a in agents:
                a.used = 0.0                                   # subscription reset
        events(hour, by_name)
        for d, rate in ARRIVALS.items():
            carry[d] += rate
            while carry[d] >= 1:
                queues[d].append(Card(d, hour))
                carry[d] -= 1

        order = [a for a in agents if hour >= a.joins]
        rng.shuffle(order)
        for a in order:
            finished = [b for b in a.busy if b[0] <= hour]
            a.busy = [b for b in a.busy if b[0] > hour]
            for end, begin, card in finished:
                d = card.tier
                ok = rng.random() < p_pass(a.c, d)
                a.done.append((hour, d, ok))
                a.log[(d, ok)] += 1
                if policy == "static":
                    if not ok:
                        queues[d].appendleft(card)
                    continue
                h, cyc = a.hist[d], a.cycle[d]
                h.append(ok)
                cyc.append(end - begin)
                rate = h.count(False) / len(h)
                if ok:
                    a.allowance = min(a.concurrency, a.allowance + 1)
                elif rate > STANDARD[d] and len(h) >= 5:
                    a.allowance = max(1, a.allowance // 2)
                median = tier_median(agents, d)
                if d > a.home:                                   # stretch card
                    a.stretch.append((ok, end - begin))
                    if len(a.stretch) == STRETCH_TRIALS:
                        fails = sum(not s for s, _ in a.stretch) / STRETCH_TRIALS
                        own = statistics.median(t for _, t in a.stretch)
                        if fails <= STANDARD[d] and (median is None or own <= VELOCITY_STANDARD * median):
                            a.home = d
                            if a.need != FAST_TRACK_CREDIT:
                                a.need = PROMOTE_CREDIT
                            a.log["promoted"] += 1
                        else:
                            a.need = min(MAX_NEED, max(a.need, PROMOTE_CREDIT) * 2)
                        a.stretch, a.credit = [], 0
                elif d == a.home:
                    a.credit = a.credit + 1 if ok else max(0, a.credit - MARKDOWN_DEBIT)
                    a.batch.append(ok)
                    recent = list(h)[-FAST_WINDOW:]
                    gross = len(recent) == FAST_WINDOW and \
                        recent.count(False) / FAST_WINDOW > GROSS_FACTOR * STANDARD[d]
                    marginal = slow = False
                    if len(a.batch) == WINDOW:                  # judged in batches, not rolling
                        over = a.batch.count(False) / WINDOW > MARGINAL_FACTOR * STANDARD[d]
                        a.strikes = a.strikes + 1 if over else 0
                        marginal = a.strikes >= 2                   # two strikes
                        slow = median is not None and len(cyc) >= 5 and \
                            statistics.median(cyc) > DEMOTE_FACTOR * VELOCITY_STANDARD * median
                        a.batch = []
                    if a.home > 1 and (gross or marginal or slow):
                        a.home -= 1
                        a.log["demoted"] += 1
                        h.clear()
                        a.batch, a.strikes, a.credit, a.need = [], 0, 0, PROMOTE_CREDIT
                if not ok:                                       # R6 escalation
                    card.attempts += 1
                    card.failed_by.add(a.name)
                    if card.attempts % 2 == 1:
                        queues[d].appendleft(card)
                    elif d < TOP:
                        card.tier = d + 1
                        queues[d + 1].appendleft(card)
                    elif card.attempts >= 6:
                        replanned += 1
                    else:
                        queues[TOP].appendleft(card)

            slots = a.allowance if policy != "static" else a.concurrency
            while len(a.busy) < slots:
                tiers = list(range(a.home, 0, -1))
                if policy != "static" and a.home < TOP and a.credit >= a.need \
                        and len(a.stretch) < STRETCH_TRIALS:
                    tiers = [a.home + 1] + tiers                 # compulsory stretch
                card = None
                for d in tiers:
                    if not may_pull_lower(a, d, hour):
                        continue
                    if queues[d] and (a.cap is None or a.used + COST[d] <= a.cap):
                        pick = next((c for c in queues[d] if a.name not in c.failed_by), None)
                        if pick is not None:
                            queues[d].remove(pick)
                            card = pick
                            break
                if card is None:
                    break
                a.used += COST[card.tier]
                a.busy.append((hour + a.duration(card.tier), hour, card))
        for a in agents:
            a.homes.append(a.home if hour >= a.joins else None)

    return {"agents": agents, "backlog": {d: len(q) for d, q in queues.items()}, "replanned": replanned}


def capability_at(a: Agent, hour: int) -> float:
    """True capability at a given hour, replaying the scenario's events."""
    if a.name == "qwen" and hour >= 110:
        return 3.0
    if a.name == "claude" and hour >= 200:
        return 3.5
    return {"claude": 4.8, "gpt": 4.6, "mimo": 3.4, "qwen": 2.0, "newmodel": 3.9}[a.name]


def spearman(xs: list[float], ys: list[float]) -> float:
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def alignment(result: dict, start: int, end: int) -> float:
    """Rank correlation between true capability and mean difficulty of work done."""
    caps, diffs = [], []
    for a in result["agents"]:
        work = [d for h, d, _ in a.done if start <= h < end]
        if len(work) >= 5:
            caps.append(capability_at(a, (start + end) // 2))
            diffs.append(statistics.mean(work))
    return spearman(caps, diffs) if len(caps) >= 3 else float("nan")


def placement(result: dict, start: int, end: int) -> float:
    """Share of agent-hours where the home tier equals the ideal tier (hidden truth)."""
    hits = n = 0
    for a in result["agents"]:
        for h in range(start, end):
            home = a.homes[h]
            if home is None:
                continue
            ideal = ideal_tier(Agent(a.name, capability_at(a, h), 1, 1, None, 1))
            hits += home == ideal
            n += 1
    return hits / n if n else float("nan")


def totals(result: dict) -> dict:
    acc = sum(n for a in result["agents"] for k, n in a.log.items() if isinstance(k, tuple) for d, ok in [k] if ok)
    bad = sum(n for a in result["agents"] for k, n in a.log.items() if isinstance(k, tuple) for d, ok in [k] if not ok)
    val = sum(n * VALUE[d] for a in result["agents"] for k, n in a.log.items() if isinstance(k, tuple) for d, ok in [k] if ok)
    hard = sum(n for a in result["agents"] for k, n in a.log.items() if isinstance(k, tuple) for d, ok in [k] if ok and d >= 4)
    return {"accepted": acc, "marked_down": bad, "value": val, "hard_done": hard,
            "backlog": sum(result["backlog"].values())}


def timeline(result: dict, step: int = 24) -> None:
    print(f"  {'hour':>5} " + " ".join(f"{a.name:>9}" for a in result["agents"]) + "   alignment")
    for h in range(0, HOURS, step):  # noqa: timeline rows
        row = []
        for a in result["agents"]:
            home = a.homes[min(h + step - 1, HOURS - 1)]
            ideal = ideal_tier(Agent(a.name, capability_at(a, h + step - 1), 1, 1, None, 1))
            row.append(f"{'-':>9}" if home is None else f"{home:>5} ({ideal})")
        print(f"  {h:>5} " + " ".join(row) + f"   {alignment(result, h, h + step):+.2f}")


def work_mix(result: dict, start: int, end: int) -> None:
    """Share of each agent's working time by tier (a T5 card takes 6x a T1 card)."""
    for a in result["agents"]:
        work = Counter()
        for h, d, _ in a.done:
            if start <= h < end:
                work[d] += a.duration(d)
        n = sum(work.values())
        if n:
            mix = " ".join(f"T{d}:{work[d] / n:4.0%}" for d in TIERS)
            print(f"  {a.name:<9} {mix}")


if __name__ == "__main__":
    print("Home tier at the end of each day, with the ideal tier (hidden truth) in brackets.")
    print("Alignment = rank correlation between true capability and mean difficulty of")
    print("cards worked that day (+1.00 = most capable always on the hardest work).")
    for policy in ("static", "ladder", "home-tier", "reserve"):
        r = run(policy)
        print(f"\n== {policy} (seed 1) ==")
        timeline(r)
        print("  share of working time by tier, final 48 hours:")
        work_mix(r, HOURS - 48, HOURS)

    print("\n== Mean over 20 seeds ==")
    print(f"  {'policy':<10} {'align wk1':>9} {'align wk2':>9} {'placed wk1':>10} {'placed wk2':>10} "
          f"{'accepted':>9} {'value':>7} {'marked down':>12} {'T4-5 done':>10} {'backlog':>8}")
    for policy in ("static", "ladder", "home-tier", "reserve"):
        rs = [run(policy, seed=s) for s in range(20)]
        a1 = statistics.mean(alignment(r, 24, WEEK) for r in rs)
        a2 = statistics.mean(alignment(r, WEEK, HOURS) for r in rs)
        p1 = statistics.mean(placement(r, 0, WEEK) for r in rs)
        p2 = statistics.mean(placement(r, WEEK, HOURS) for r in rs)
        t = {k: statistics.mean(totals(r)[k] for r in rs) for k in totals(rs[0])}
        print(f"  {policy:<10} {a1:+9.2f} {a2:+9.2f} {p1:10.0%} {p2:10.0%} {t['accepted']:9.0f} {t['value']:7.0f} "
              f"{t['marked_down']:12.0f} {t['hard_done']:10.0f} {t['backlog']:8.0f}")
