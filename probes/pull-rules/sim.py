"""Pull-rules probe: do dumb, rules-based feedback loops allocate work well?

Idea-stage feasibility check for docs/idea/constitutional-factory.md (r8).
No agent manages allocation. Agents pull cards; rules adjust what each may pull.

ALL NUMBERS ARE SYNTHETIC. They illustrate dynamics, not real model performance.

Rules exercised (numbering as in the Idea Record, section 3):
  R1 pull          agents with a free slot pull; nobody assigns
  R2 licence       an agent may pull only tiers it is licensed for
  R3 hardest-first pull the oldest card in the highest licensed tier
  R4 allowance     AIMD against the standard: accepted card -> +1 slot; a
                   markdown that takes the rolling rate over the standard -> halve
  R5 ladder        promotion credit: +1 per accepted card, -4 per markdown, so
                   only fast, accurate agents build credit quickly. Enough credit
                   triggers compulsory stretch cards from the tier above; passing
                   needs the tier's quality standard AND a cycle time within the
                   tier's velocity standard. Demotion from the top tier on a full
                   window well over the quality standard (1.5x, hysteresis) or
                   well over the velocity standard. Failed promotion -> back-off.
  R6 escalation    retry once at the same tier by another agent, then up a tier;
                   repeated failure at the top tier returns the card to Planning
  R7 home tier     (policy 'bands') an agent works at its home tier, its highest
                   licence, and may NOT pull easier work, except:
                     help-down: with nothing to pull at home, it helps the
                     nearest lower tier that is behind (oldest card waiting
                     more than SPILL_AGE hours). Uncapped agents may help any
                     lower tier; capped agents only the tier directly below;
                     surplus release: a capped agent keeps enough cap to work
                     its home tier at HARD_RESERVE of full speed until reset;
                     only the surplus above that may go to easier work
                   (policy 'pacing' is the r5 rule it replaces: drop down only
                   while ahead of the pro-rata spend line)
  R11 start state  licences and allowances start from today's predetermined
                   mapping (amend scenario)

Run: python3 probes/pull-rules/sim.py
"""

from __future__ import annotations

import math
import random
import statistics
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

HOURS = 168                      # one weekly subscription window
TIERS = (1, 2, 3)
STANDARD = {1: 0.15, 2: 0.20, 3: 0.25}   # quality standard: max markdown rate per tier
VELOCITY_STANDARD = 1.5          # max cycle time as a multiple of the tier's median
PROMOTE_CREDIT = 20              # promotion credit needed before stretch cards
MARKDOWN_DEBIT = 4               # credit lost per markdown
STRETCH_TRIALS = 15
DEMOTE_FACTOR = 1.5              # hysteresis on both standards
WINDOW = 20
SPILL_AGE = 6                    # hours a lower-tier card waits before the tier above may help
HARD_RESERVE = 0.75              # share of full home-tier speed a capped agent's cap is kept for
VALUE = {1: 1, 2: 3, 3: 8}       # value of an accepted card by tier (for value-weighted output)
DURATION = {1: 1, 2: 2, 3: 4}    # base hours of work per card by tier
COST = {1: 1, 2: 3, 3: 8}        # subscription units per card by tier


def steady(hour: int) -> dict[int, int]:
    return {1: 6, 2: 3, 3: 1}


def easy_first(hour: int) -> dict[int, int]:
    """Easy cards flood the first three days; hard cards arrive later in the week."""
    if hour < 72:
        return {1: 9, 2: 3, 3: 1 if hour % 5 in (0, 2) else 0}
    return {1: 4, 2: 3, 3: 2 if hour % 5 in (0, 1, 2) else 1}


@dataclass
class Agent:
    name: str
    concurrency: int
    cap: float | None                         # weekly units; None = uncapped
    p: dict[int, float]                       # true success probability by tier (hidden)
    licences: set[int]
    speed: float = 1.0                        # duration multiplier (hidden); >1 is slower
    allowance: int = 0                        # 0 = start at full concurrency (R11)
    used: float = 0.0
    busy: list = field(default_factory=list)  # [(finish_hour, start_hour, card)]
    credit: int = 0
    promote_after: int = PROMOTE_CREDIT
    stretch: list = field(default_factory=list)
    history: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=WINDOW)))
    cycle: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=WINDOW)))
    log: Counter = field(default_factory=Counter)
    allowance_trace: list = field(default_factory=list)

    @property
    def top(self) -> int:
        return max(self.licences)


@dataclass
class Card:
    cid: int
    tier: int
    born: int
    attempts: int = 0
    failed_by: set = field(default_factory=set)


def tier_median_cycle(agents: list[Agent], tier: int) -> float | None:
    """Median cycle time at a tier across agents with enough observations there."""
    medians = [statistics.median(a.cycle[tier]) for a in agents if len(a.cycle[tier]) >= 5]
    return statistics.median(medians) if medians else None


def run(agents: list[Agent], policy: str = "bands", seed: int = 7, change=None, arrivals=steady) -> dict:
    assert policy in ("static", "pacing", "bands", "reserve")
    adaptive = policy != "static"
    rng = random.Random(seed)
    queues = {t: deque() for t in TIERS}
    next_id, replanned, waits = 0, 0, defaultdict(list)

    for a in agents:
        a.allowance = a.allowance or a.concurrency

    def may_drop_to(a: Agent, t: int, hour: int) -> bool:
        if t >= a.top or not adaptive:
            return True
        if policy == "pacing":
            return a.cap is None or (a.cap - a.used) / a.cap >= (HOURS - hour) / HOURS
        if policy == "reserve":             # hardest-first; capped agents keep a hard-work reserve
            if a.cap is None:
                return True
            home_rate = a.concurrency * COST[a.top] / max(1, math.ceil(DURATION[a.top] * a.speed))
            return (HOURS - hour) * home_rate * HARD_RESERVE < a.cap - a.used - COST[t]
        # reached only when every tier above t had nothing this agent could pull
        behind = bool(queues[t]) and hour - queues[t][0].born >= SPILL_AGE
        if a.cap is None:
            return behind                                       # help-down, any tier
        home_rate = a.concurrency * COST[a.top] / max(1, math.ceil(DURATION[a.top] * a.speed))
        if (HOURS - hour) * home_rate * HARD_RESERVE >= a.cap - a.used - COST[t]:
            return behind and t == a.top - 1                    # help-down, one tier
        return True                                             # surplus release

    for hour in range(HOURS):
        if change:
            change(hour, agents)
        for t, n in arrivals(hour).items():
            for _ in range(n):
                queues[t].append(Card(next_id, t, hour))
                next_id += 1

        order = agents[:]
        rng.shuffle(order)                     # agents work concurrently; no fixed pecking order
        for a in order:
            done = [b for b in a.busy if b[0] <= hour]
            a.busy = [b for b in a.busy if b[0] > hour]
            for finish, start, card in done:
                ok = rng.random() < a.p[card.tier]
                is_stretch = card.tier > a.top
                a.history[card.tier].append(ok)
                a.cycle[card.tier].append(finish - start)
                a.log[(card.tier, "accepted" if ok else "marked_down")] += 1
                if ok:
                    waits[card.tier].append(hour - card.born)
                if not adaptive:
                    if not ok:
                        queues[card.tier].appendleft(card)
                    continue
                h = a.history[card.tier]
                rate = h.count(False) / len(h)
                # R4 allowance against the quality standard
                if ok:
                    a.allowance = min(a.concurrency, a.allowance + 1)
                elif rate > STANDARD[card.tier] and len(h) >= 5:
                    a.allowance = max(1, a.allowance // 2)
                # R5 ladder: credit, compulsory stretch, quality + velocity standards
                median = tier_median_cycle(agents, card.tier)
                if is_stretch:
                    a.stretch.append((ok, finish - start))
                    if len(a.stretch) == STRETCH_TRIALS:
                        fails = sum(1 for s_ok, _ in a.stretch if not s_ok) / STRETCH_TRIALS
                        own = statistics.median(c for _, c in a.stretch)
                        fast_enough = median is None or own <= VELOCITY_STANDARD * median
                        if fails <= STANDARD[card.tier] and fast_enough:
                            a.licences.add(card.tier)
                            a.log[("promoted_to", card.tier)] += 1
                            a.promote_after = PROMOTE_CREDIT
                        else:
                            a.promote_after *= 2
                        a.stretch, a.credit = [], 0
                elif card.tier == a.top:
                    a.credit = a.credit + 1 if ok else max(0, a.credit - MARKDOWN_DEBIT)
                if card.tier == a.top and len(a.licences) > 1 and len(h) == WINDOW:
                    too_poor = rate > DEMOTE_FACTOR * STANDARD[card.tier]
                    too_slow = median is not None and len(a.cycle[card.tier]) >= 5 and \
                        statistics.median(a.cycle[card.tier]) > DEMOTE_FACTOR * VELOCITY_STANDARD * median
                    if too_poor or too_slow:
                        a.licences.discard(card.tier)
                        a.log[("demoted_from", card.tier)] += 1
                        h.clear()
                        a.credit = 0
                # R6 escalation
                if not ok:
                    card.attempts += 1
                    card.failed_by.add(a.name)
                    if card.attempts % 2 == 1:
                        queues[card.tier].appendleft(card)
                    elif card.tier < 3:
                        card.tier += 1
                        queues[card.tier].appendleft(card)
                    elif card.attempts >= 6:
                        replanned += 1
                    else:
                        queues[3].appendleft(card)

            # R1 pull into free slots
            while len(a.busy) < (a.allowance if adaptive else a.concurrency):
                tiers = sorted(a.licences, reverse=True)                     # R3
                if adaptive and a.top < 3 and a.credit >= a.promote_after \
                        and len(a.stretch) < STRETCH_TRIALS:
                    tiers = [a.top + 1] + tiers                               # compulsory stretch
                card = None
                for t in tiers:
                    if not may_drop_to(a, t, hour):                           # R7
                        continue
                    if queues[t] and (a.cap is None or a.used + COST[t] <= a.cap):
                        pick = next((c for c in queues[t] if a.name not in c.failed_by), None)
                        if pick is not None:
                            queues[t].remove(pick)
                            card = pick
                            break
                if card is None:
                    break
                a.used += COST[card.tier]
                a.busy.append((hour + max(1, math.ceil(DURATION[card.tier] * a.speed)), hour, card))
            a.allowance_trace.append(a.allowance)

    backlog = {t: len(q) for t, q in queues.items()}
    return {"agents": agents, "backlog": backlog, "replanned": replanned, "waits": waits}


FRONTIER_CAP = 1400              # weekly units per frontier subscription


def roster() -> list[Agent]:
    # R11: start from a predetermined mapping. Qwen is (wrongly) licensed for tier 2.
    # Speeds are hidden: MiMo is fast; local Qwen is slow; frontier models are mid.
    return [
        Agent("claude", concurrency=6, cap=FRONTIER_CAP, p={1: .97, 2: .93, 3: .85}, licences={1, 2, 3}, speed=1.0),
        Agent("gpt", concurrency=6, cap=FRONTIER_CAP, p={1: .96, 2: .92, 3: .83}, licences={1, 2, 3}, speed=0.9),
        Agent("mimo", concurrency=10, cap=None, p={1: .93, 2: .84, 3: .55}, licences={1, 2}, speed=0.7),
        Agent("qwen", concurrency=4, cap=None, p={1: .88, 2: .45, 3: .20}, licences={1, 2}, speed=1.6),
    ]


def summarize(result: dict) -> dict:
    agents = {a.name: a for a in result["agents"]}
    ok = sum(a.log[(t, "accepted")] for a in agents.values() for t in TIERS)
    bad = sum(a.log[(t, "marked_down")] for a in agents.values() for t in TIERS)
    frontier = [agents["claude"], agents["gpt"]]
    frontier_cards = sum(a.log[(t, k)] for a in frontier for t in TIERS for k in ("accepted", "marked_down"))
    frontier_t1 = sum(a.log[(1, k)] * COST[1] for a in frontier for k in ("accepted", "marked_down"))
    frontier_cards = sum(a.log[(t, k)] * COST[t] for a in frontier for t in TIERS for k in ("accepted", "marked_down"))
    w3 = result["waits"][3]
    return {
        "accepted": ok,
        "value": sum(a.log[(t, "accepted")] * VALUE[t] for a in agents.values() for t in TIERS),
        "backlog": sum(result["backlog"].values()),
        "marked_down": bad,
        "t3_accepted": sum(a.log[(3, "accepted")] for a in agents.values()),
        "t3_backlog": result["backlog"][3],
        "t3_wait": statistics.median(w3) if w3 else float("nan"),
        "frontier_easy_share": frontier_t1 / max(1, frontier_cards),
        "frontier_cap_used": sum(a.used for a in frontier) / sum(a.cap for a in frontier),
        "qwen_t2_markdowns": agents["qwen"].log[(2, "marked_down")],
    }


def mean_summary(policy: str, arrivals=steady, n: int = 20, change=None) -> dict:
    rows = [summarize(run(roster(), policy=policy, seed=s, arrivals=arrivals, change=change)) for s in range(n)]
    return {k: sum(r[k] for r in rows) / n for k in rows[0]}


def report_agents(label: str, result: dict) -> None:
    print(f"\n== {label} ==")
    for a in result["agents"]:
        ok = {t: a.log[(t, "accepted")] for t in TIERS}
        bad = sum(a.log[(t, "marked_down")] for t in TIERS)
        used = f"{a.used / a.cap:.0%} of cap" if a.cap else "uncapped"
        moves = [f"{k[0].split('_')[0]} T{k[1]}" for k in a.log if isinstance(k[0], str)]
        print(f"  {a.name:<7} accepted T1/T2/T3 {ok[1]:>4}/{ok[2]:>3}/{ok[3]:>3}  markdowns {bad:>3}  "
              f"home tier {a.top}  {used}  {', '.join(moves)}")


def compare(arrivals, label: str) -> None:
    print(f"\n== {label}: mean over 20 seeds ==")
    print(f"  {'policy':<14} {'accepted':>8} {'value':>6} {'markdown':>9} {'backlog':>8} {'T3 done':>8} "
          f"{'T3 left':>8} {'frontier cap on easy':>21} {'frontier cap used':>18} {'qwen T2 fails':>14}")
    global HARD_RESERVE
    for policy, reserve in (("static", None), ("pacing", None), ("bands", 0.75), ("reserve", 0.75)):
        if reserve is not None:
            HARD_RESERVE = reserve
        m = mean_summary(policy, arrivals)
        label = {"bands": "home tier", "reserve": "lean reserve"}.get(policy, policy)
        print(f"  {label:<14} {m['accepted']:8.0f} {m['value']:6.0f} {m['marked_down']:9.0f} {m['backlog']:8.1f} "
              f"{m['t3_accepted']:8.0f} {m['t3_backlog']:8.1f} {m['frontier_easy_share']:21.0%} "
              f"{m['frontier_cap_used']:18.0%} {m['qwen_t2_markdowns']:14.1f}")
    HARD_RESERVE = 0.75


if __name__ == "__main__":
    report_agents("Home-tier rules, easy cards front-loaded (seed 7)", run(roster(), "bands", arrivals=easy_first))
    report_agents("r5 pacing rule, easy cards front-loaded (seed 7)", run(roster(), "pacing", arrivals=easy_first))
    compare(steady, "Steady arrivals")
    compare(easy_first, "Easy cards front-loaded, hard cards late")
    FRONTIER_CAP = 900
    compare(easy_first, "Tight frontier caps (900 units), easy cards front-loaded")
    FRONTIER_CAP = 1400
