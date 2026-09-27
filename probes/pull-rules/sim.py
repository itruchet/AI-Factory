"""Pull-rules probe: do dumb, rules-based feedback loops allocate work well?

Idea-stage feasibility check for docs/idea/constitutional-factory.md (r5).
No agent manages allocation. Agents pull cards; rules adjust what each may pull.

ALL NUMBERS ARE SYNTHETIC. They illustrate dynamics, not real model performance.

Rules exercised (numbering as in the Idea Record, section 3):
  R1 pull         agents with a free slot pull; nobody assigns
  R2 licence      an agent may pull only tiers it is licensed for
  R3 hardest-first  pull the oldest card in the highest licensed tier
  R4 allowance    AIMD against the standard: while the rolling markdown rate is
                  within the tier's standard, each accepted card adds a slot; a
                  markdown that takes the rate over the standard halves slots
  R5 ladder       licences are a contiguous ladder. Promote via stretch cards
                  that must meet the higher tier's standard; demote only the top
                  tier, and only on a full window well over its standard
                  (hysteresis: promote at the standard, demote at 1.5x it, so
                  normal variance cannot make licences flap). A failed promotion
                  attempt doubles the wait before the next one (back-off)
  R6 escalation   a marked-down card is retried once at its tier by another
                  agent, then goes up one tier; repeated failure at the top tier
                  sends it back to Planning (the card, not the agent, is suspect)
  R7 pacing       capped subscriptions work below their top tier only while
                  remaining cap is above the pro-rata line for the window
  R11 start state  licences and allowances start from today's predetermined
                  mapping (amend scenario); the rules move them from there

Run: python3 probes/pull-rules/sim.py
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field

HOURS = 168                      # one weekly subscription window
TIERS = (1, 2, 3)
STANDARD = {1: 0.15, 2: 0.20, 3: 0.25}   # max tolerated markdown rate per tier
PROMOTE_AFTER = 20               # accepted cards at top tier before stretch trials
STRETCH_TRIALS = 15              # stretch cards per promotion attempt; pass = within standard
DEMOTE_FACTOR = 1.5              # hysteresis: demote only above 1.5x the standard
WINDOW = 20                      # rolling window for allowance and demotion
FIRST_VERSION = False            # True reverts allowance and demotion to their first (rejected) form
ARRIVALS = {1: 6, 2: 3, 3: 1}    # cards arriving per hour by tier
DURATION = {1: 1, 2: 2, 3: 4}    # hours of work per card by tier
COST = {1: 1, 2: 3, 3: 8}        # subscription units per card by tier


@dataclass
class Agent:
    name: str
    concurrency: int
    cap: float | None                         # weekly units; None = uncapped
    p: dict[int, float]                       # true success probability by tier (hidden)
    licences: set[int]
    allowance: int = 0                        # 0 = start at full concurrency (R11)
    used: float = 0.0
    busy: list = field(default_factory=list)  # [(finish_hour, card)]
    top_streak: int = 0
    promote_after: int = 20                   # grows by back-off after a failed attempt
    stretch: list = field(default_factory=list)
    history: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=WINDOW)))
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


def run(agents: list[Agent], adaptive: bool = True, seed: int = 7, change=None) -> dict:
    rng = random.Random(seed)
    queues = {t: deque() for t in TIERS}
    next_id, replanned, waits = 0, 0, defaultdict(list)

    for a in agents:
        a.allowance = a.allowance or a.concurrency

    def pace_ok(a: Agent, hour: int) -> bool:
        if a.cap is None:
            return True
        return (a.cap - a.used) / a.cap >= (HOURS - hour) / HOURS

    for hour in range(HOURS):
        if change:
            change(hour, agents)
        for t in TIERS:
            for _ in range(ARRIVALS[t]):
                queues[t].append(Card(next_id, t, hour))
                next_id += 1

        order = agents[:]
        rng.shuffle(order)                     # agents work concurrently; no fixed pecking order
        for a in order:
            # finish work, get marked by the next stage (the Court)
            done = [(f, c) for f, c in a.busy if f <= hour]
            a.busy = [(f, c) for f, c in a.busy if f > hour]
            for _, card in done:
                ok = rng.random() < a.p[card.tier]
                is_stretch = card.tier > a.top
                a.history[card.tier].append(ok)
                a.log[(card.tier, "accepted" if ok else "marked_down")] += 1
                if ok:
                    waits[card.tier].append(hour - card.born)
                if not adaptive:
                    if not ok:
                        queues[card.tier].appendleft(card)  # static: retry same tier
                    continue
                h = a.history[card.tier]
                over = h.count(False) / len(h) > STANDARD[card.tier]
                # R4 AIMD allowance, measured against the standard
                if FIRST_VERSION:
                    a.allowance = min(a.concurrency, a.allowance + 1) if ok else max(1, a.allowance // 2)
                elif ok:
                    a.allowance = min(a.concurrency, a.allowance + 1)
                elif over and len(h) >= 5:
                    a.allowance = max(1, a.allowance // 2)
                # R5 ladder
                if is_stretch:
                    a.stretch.append(ok)
                    if len(a.stretch) == STRETCH_TRIALS:
                        if a.stretch.count(False) / STRETCH_TRIALS <= STANDARD[card.tier]:
                            a.licences.add(card.tier)
                            a.log[("promoted_to", card.tier)] += 1
                            a.promote_after = PROMOTE_AFTER
                        else:
                            a.promote_after *= 2          # back-off
                        a.stretch, a.top_streak = [], 0
                elif card.tier == a.top:
                    a.top_streak += 1 if ok else 0
                way_over = h.count(False) / len(h) > DEMOTE_FACTOR * STANDARD[card.tier]
                if card.tier == a.top and len(a.licences) > 1 and len(h) == WINDOW \
                        and (way_over or FIRST_VERSION and over):
                    a.licences.discard(card.tier)
                    a.log[("demoted_from", card.tier)] += 1
                    h.clear()
                    a.top_streak = 0
                # R6 escalation: retry once at the same tier elsewhere, then go up
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
                tiers = sorted(a.licences, reverse=True)                     # R3 hardest first
                wants_stretch = adaptive and a.top < 3 and a.top_streak >= a.promote_after \
                    and len(a.stretch) < STRETCH_TRIALS
                if wants_stretch:
                    tiers = [a.top + 1] + tiers
                card = None
                for t in tiers:
                    if t < a.top and adaptive and not pace_ok(a, hour):     # R7 pacing
                        break
                    if queues[t] and (a.cap is None or a.used + COST[t] <= a.cap):
                        # never hand a card straight back to an agent that just failed it
                        pick = next((c for c in queues[t] if a.name not in c.failed_by), None)
                        if pick is not None:
                            queues[t].remove(pick)
                            card = pick
                            break
                if card is None:
                    break
                a.used += COST[card.tier]
                a.busy.append((hour + DURATION[card.tier], card))
            a.allowance_trace.append(a.allowance)

    backlog = {t: len(q) for t, q in queues.items()}
    return {"agents": agents, "backlog": backlog, "replanned": replanned, "waits": waits}


def roster() -> list[Agent]:
    # R11: start from a predetermined mapping. Qwen is (wrongly) licensed for tier 2.
    return [
        Agent("claude", concurrency=6, cap=1400, p={1: .97, 2: .93, 3: .85}, licences={1, 2, 3}),
        Agent("gpt", concurrency=6, cap=1400, p={1: .96, 2: .92, 3: .83}, licences={1, 2, 3}),
        Agent("mimo", concurrency=10, cap=None, p={1: .93, 2: .84, 3: .55}, licences={1, 2}),
        Agent("qwen", concurrency=4, cap=None, p={1: .88, 2: .45, 3: .20}, licences={1, 2}),
    ]


def report(label: str, result: dict) -> None:
    print(f"\n== {label} ==")
    total_ok = total_bad = 0
    for a in result["agents"]:
        ok = {t: a.log[(t, "accepted")] for t in TIERS}
        bad = {t: a.log[(t, "marked_down")] for t in TIERS}
        total_ok += sum(ok.values())
        total_bad += sum(bad.values())
        rate = sum(bad.values()) / max(1, sum(ok.values()) + sum(bad.values()))
        used = f"{a.used / a.cap:.0%} of cap" if a.cap else "uncapped"
        moves = [f"{k[0].split('_')[0]} T{k[1]}" for k in a.log if isinstance(k[0], str) and k[0] in ("promoted_to", "demoted_from")]
        print(f"  {a.name:<7} accepted T1/T2/T3 {ok[1]:>4}/{ok[2]:>3}/{ok[3]:>3}  "
              f"markdown rate {rate:5.1%}  licences {sorted(a.licences)}  {used}  {', '.join(moves)}")
    w3 = result["waits"][3]
    print(f"  total accepted {total_ok}, marked down {total_bad} "
          f"({total_bad / max(1, total_ok + total_bad):.1%}); replanned {result['replanned']}; "
          f"backlog {result['backlog']}; tier-3 median wait {sorted(w3)[len(w3) // 2] if w3 else '-'} h")


def totals(result: dict) -> tuple[int, int, int]:
    ok = sum(a.log[(t, "accepted")] for a in result["agents"] for t in TIERS)
    bad = sum(a.log[(t, "marked_down")] for a in result["agents"] for t in TIERS)
    return ok, bad, sum(result["backlog"].values())


def seeds_summary(n: int = 20) -> None:
    global FIRST_VERSION
    print(f"\n== Mean over {n} seeds: accepted / marked down / backlog at end ==")
    for label, adaptive, first in [("static predetermined", False, False),
                                   ("first allowance/demotion", True, True),
                                   ("final rules", True, False)]:
        FIRST_VERSION = first
        rows = [totals(run(roster(), adaptive=adaptive, seed=s)) for s in range(n)]
        ok, bad, back = (sum(r[i] for r in rows) / n for i in range(3))
        qwen_t2 = sum(next(a for a in run(roster(), adaptive=adaptive, seed=s)["agents"]
                           if a.name == "qwen").log[(2, "marked_down")] for s in range(n)) / n
        print(f"  {label:<24} {ok:7.0f} / {bad:5.0f} ({bad / (ok + bad):5.1%}) / {back:5.0f}   "
              f"qwen tier-2 markdowns {qwen_t2:5.1f}")
    FIRST_VERSION = False


if __name__ == "__main__":
    report("Static predetermined mapping (no feedback)", run(roster(), adaptive=False))
    adaptive = run(roster(), adaptive=True)
    report("Pull rules with feedback", adaptive)
    q = next(a for a in adaptive["agents"] if a.name == "qwen")
    print("  qwen allowance, every 12 h:", q.allowance_trace[::12])

    def qwen_upgrade(hour, agents):
        if hour == 84:  # a better Qwen version is deployed mid-week
            next(a for a in agents if a.name == "qwen").p.update({1: .97, 2: .90, 3: .45})
    upgraded = run(roster(), adaptive=True, change=qwen_upgrade)
    report("Pull rules; Qwen upgraded at hour 84", upgraded)
    q = next(a for a in upgraded["agents"] if a.name == "qwen")
    print("  qwen allowance, every 12 h:", q.allowance_trace[::12])

    seeds_summary()
