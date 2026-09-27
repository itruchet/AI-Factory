"""Portfolio probe: model mixes, removals, golden rules and the optimal portfolio.

Idea-stage probe for docs/idea/constitutional-factory.md (r8). Results: portfolio_results.txt
ALL OUTCOMES ARE SYNTHETIC. Benchmark scores are public figures used as priors;
costs, caps, speeds and the Factory-specific offsets are labelled assumptions.

World model (hidden from the rules):
  - five difficulty tiers; pass chance on a tier-d card is
    logistic(1.7 * (c - d + 1)) for capability c;
  - c comes from a model's Artificial Analysis (AA) Intelligence Index score,
    normalised to the current frontier, plus a Factory-specific offset: public
    benchmarks are priors, not our workload;
  - the normalised-score bands are anchored so that a model exactly on a band
    edge can just sustain that tier at the quality standard.

Rules (the r7 lean set, each switchable for the golden-rules ablation):
  hardest_first  R3  pull the hardest licensed tier first (off: random licensed tier)
  promotion      R5  credit ladder with compulsory trial cards
  demotion       R5  two-speed demotion, batch-judged, two strikes
  allowance      R4  slots grow on success, halve when over the standard
  escalation     R6  retry once elsewhere, then up a tier (off: retry same tier)
  reserve        R7  capped models keep a 75% hard-work reserve
  velocity       R5  cycle-time standard for promotion and demotion
  fast_track     R5  new models need little credit until their first failed promotion

Run: python3 probes/pull-rules/portfolio.py
"""

from __future__ import annotations

import itertools
import math
import random
import statistics
from collections import deque, defaultdict
from dataclasses import dataclass, field

HOURS, WEEK = 336, 168
TIERS = (1, 2, 3, 4, 5)
TOP = 5
DURATION = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6}
COST = {1: 1, 2: 2, 3: 4, 4: 6, 5: 10}           # subscription units per card
VALUE = COST
STANDARD = {1: .15, 2: .18, 3: .20, 4: .22, 5: .25}
SURGE = {1: 5.0, 2: 3.0, 3: 2.0, 4: 1.0, 5: 0.5}   # cards per hour: overloads today's portfolio
DEMAND = {d: 0.85 * r for d, r in SURGE.items()}    # nominal: today's portfolio at ~90% load
VELOCITY_STANDARD = 1.5
PROMOTE_CREDIT, MARKDOWN_DEBIT, FAST_TRACK_CREDIT = 20, 4, 5
TRIALS, BATCH, FAST_WINDOW = 20, 20, 10
GROSS, MARGINAL, SLOW = 2.0, 1.25, 1.5
HARD_RESERVE = 0.75
ALL_RULES = ("hardest_first", "promotion", "demotion", "allowance", "escalation",
             "reserve", "velocity", "fast_track")
GOLDEN = ("hardest_first", "promotion", "demotion", "reserve", "fast_track")

# --- Normalised banding from Artificial Analysis --------------------------------
# Score as % of the current frontier score -> prior landing tier.
BANDS = [(95, 5), (85, 4), (70, 3), (50, 2), (0, 1)]
# Capability at each band edge: the c at which that tier's standard is just met.
ANCHORS = [(20, 1.02), (50, 1.89), (70, 2.82), (85, 3.74), (95, 4.65)]
FRONTIER_SCORE = 59.0                             # GPT-5.6 Sol, reported Sept 2026


def band(norm: float) -> int:
    return next(t for edge, t in BANDS if norm >= edge)


def capability(norm: float) -> float:
    """Piecewise-linear map from normalised score to capability, through the anchors."""
    pts = ANCHORS
    if norm <= pts[0][0]:
        return pts[0][1] - (pts[0][0] - norm) * (pts[1][1] - pts[0][1]) / (pts[1][0] - pts[0][0])
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if norm <= x1:
            return y0 + (norm - x0) * (y1 - y0) / (x1 - x0)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    return y1 + (norm - x1) * (y1 - y0) / (x1 - x0)


def p_pass(c: float, d: int) -> float:
    return 1 / (1 + math.exp(-1.7 * (c - d + 1)))


def sustain_tier(c: float) -> int:
    ok = [d for d in TIERS if 1 - p_pass(c, d) <= STANDARD[d]]
    return max(ok) if ok else 1


@dataclass(frozen=True)
class Model:
    """A model type. Scores are reported AA figures; everything else is an assumption."""
    key: str
    label: str
    aa: float            # reported AA Intelligence Index
    offset: float        # ASSUMED Factory-specific deviation from the benchmark
    speed: float         # ASSUMED duration multiplier (>1 slower)
    concurrency: int     # ASSUMED parallel slots
    cap: float | None    # ASSUMED weekly units; None = uncapped
    usd_month: float     # plan price or ASSUMED amortised cost
    vendor: str

    @property
    def norm(self) -> float:
        return 100 * self.aa / FRONTIER_SCORE

    @property
    def c(self) -> float:
        return capability(self.norm) + self.offset


CATALOG = {
    "sol": Model("sol", "GPT-5.6 Sol", 59, -0.15, 0.9, 6, 1400, 200, "openai"),
    "opus": Model("opus", "Claude Opus 5.5", 58, 0.10, 1.0, 6, 1400, 200, "anthropic"),
    "terra": Model("terra", "GPT-5.6 Terra", 55, 0.0, 0.8, 6, 900, 100, "openai"),
    "luna": Model("luna", "GPT-5.6 Luna", 51, 0.0, 0.7, 6, 900, 60, "openai"),
    "mimo": Model("mimo", "MiMo-V2.6-Pro", 46, 0.25, 0.7, 10, None, 50, "xiaomi"),
    "qwen": Model("qwen", "Qwen3.8 27B (local)", 34, -0.30, 1.6, 3, None, 120, "local"),
    "coder": Model("coder", "Qwen3 Coder Next (local)", 9, 0.0, 0.8, 4, None, 60, "local"),
    # Stress-test types (hypothetical):
    "overrated": Model("overrated", "Overrated model (benchmark says tier 4)", 55, -1.3, 0.8, 6, None, 100, "other"),
    "slowmax": Model("slowmax", "Slow max-effort frontier", 58, 0.10, 2.4, 6, 1400, 200, "anthropic"),
}


@dataclass
class Agent:
    m: Model
    idx: int
    home: int
    joins: int = 0
    active: bool = True
    cap_scale: float = 1.0
    c_shift: float = 0.0                      # silent change in true capability
    allowance: int = 0
    used: float = 0.0
    busy: list = field(default_factory=list)
    credit: int = 0
    need: int = PROMOTE_CREDIT
    trials: list = field(default_factory=list)
    batch: list = field(default_factory=list)
    strikes: int = 0
    recent: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=BATCH)))
    cycle: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=BATCH)))
    done: list = field(default_factory=list)   # (hour, tier, ok)
    homes: list = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"{self.m.key}{self.idx}"

    @property
    def cap(self) -> float | None:
        return None if self.m.cap is None else self.m.cap * self.cap_scale

    def duration(self, d: int) -> int:
        return max(1, math.ceil(DURATION[d] * self.m.speed))


@dataclass
class Card:
    tier: int
    born: int
    true: int = 0                             # true difficulty (can exceed the label)
    attempts: int = 0
    failed_by: set = field(default_factory=set)


def tier_median(agents, d):
    meds = [statistics.median(a.cycle[d]) for a in agents if len(a.cycle[d]) >= 5]
    return statistics.median(meds) if meds else None


def run(keys: list[str], rules=ALL_RULES, events=None, seed: int = 1, start: str = "aa",
        demand=DEMAND, mis_tier: float = 0.0) -> dict:
    """Simulate a portfolio. keys: model keys (repeat a key for more instances).

    start: 'aa' = licences start at the AA band (prior); 'cold' = everyone at tier 1
    with the fast track.
    """
    rules = set(rules)
    rng = random.Random(seed)
    counts = defaultdict(int)
    agents = []
    for k in keys:
        m = CATALOG[k]
        counts[k] += 1
        home = band(m.norm) if start == "aa" else 1
        agents.append(Agent(m, counts[k], home))
    for a in agents:
        a.allowance = a.m.concurrency
        if start == "cold" and "fast_track" in rules:
            a.need = FAST_TRACK_CREDIT
    queues = {d: deque() for d in TIERS}
    carry = defaultdict(float)
    peak_backlog = peak_hard = 0

    def may_pull_lower(a, d, hour):
        if d >= a.home or "reserve" not in rules or a.cap is None:
            return True
        rate = a.m.concurrency * COST[a.home] / a.duration(a.home)
        return (WEEK - hour % WEEK) * rate * HARD_RESERVE < a.cap - a.used - COST[d]

    for hour in range(HOURS):
        if hour % WEEK == 0:
            for a in agents:
                a.used = 0.0
        if events:
            events(hour, agents)
        for d, rate in demand.items():
            carry[d] += rate
            while carry[d] >= 1:
                true = min(TOP, d + 1) if rng.random() < mis_tier else d
                queues[d].append(Card(d, hour, true))
                carry[d] -= 1

        order = [a for a in agents if a.active and hour >= a.joins]
        rng.shuffle(order)
        for a in order:
            finished = [b for b in a.busy if b[0] <= hour]
            a.busy = [b for b in a.busy if b[0] > hour]
            for end, begin, card in finished:
                d = card.tier
                ok = rng.random() < p_pass(a.m.c + a.c_shift, max(d, card.true))
                a.done.append((hour, d, ok, card.born))
                rec, cyc = a.recent[d], a.cycle[d]
                rec.append(ok)
                cyc.append(end - begin)
                rate = rec.count(False) / len(rec)
                if "allowance" in rules:
                    if ok:
                        a.allowance = min(a.m.concurrency, a.allowance + 1)
                    elif rate > STANDARD[d] and len(rec) >= 5:
                        a.allowance = max(1, a.allowance // 2)
                med = tier_median(agents, d)
                if d > a.home and "promotion" in rules:
                    a.trials.append((ok, end - begin))
                    if len(a.trials) == TRIALS:
                        fails = sum(not s for s, _ in a.trials) / TRIALS
                        own = statistics.median(t for _, t in a.trials)
                        fast = "velocity" not in rules or med is None or own <= VELOCITY_STANDARD * med
                        if fails <= STANDARD[d] and fast:
                            a.home = d
                            if a.need != FAST_TRACK_CREDIT:
                                a.need = PROMOTE_CREDIT
                        else:
                            a.need = min(2 * PROMOTE_CREDIT, max(a.need, PROMOTE_CREDIT) * 2)
                        a.trials, a.credit = [], 0
                elif d == a.home:
                    a.credit = a.credit + 1 if ok else max(0, a.credit - MARKDOWN_DEBIT)
                    if "demotion" in rules:
                        a.batch.append(ok)
                        last = list(rec)[-FAST_WINDOW:]
                        gross = len(last) == FAST_WINDOW and last.count(False) / FAST_WINDOW > GROSS * STANDARD[d]
                        marginal = slow = False
                        if len(a.batch) == BATCH:
                            over = a.batch.count(False) / BATCH > MARGINAL * STANDARD[d]
                            a.strikes = a.strikes + 1 if over else 0
                            marginal = a.strikes >= 2
                            slow = "velocity" in rules and med is not None and len(cyc) >= 5 and \
                                statistics.median(cyc) > GROSS * SLOW * med
                            a.batch = []
                        if a.home > 1 and (gross or marginal or slow):
                            a.home -= 1
                            rec.clear()
                            a.batch, a.strikes, a.credit, a.need = [], 0, 0, PROMOTE_CREDIT
                if not ok:
                    card.attempts += 1
                    card.failed_by.add(a.name)
                    if "escalation" not in rules or card.attempts % 2 == 1:
                        queues[d].appendleft(card)
                    elif d < TOP:
                        card.tier = d + 1
                        queues[d + 1].appendleft(card)
                    else:
                        queues[TOP].appendleft(card)

            slots = a.allowance if "allowance" in rules else a.m.concurrency
            while len(a.busy) < slots:
                tiers = list(range(a.home, 0, -1))
                if "hardest_first" not in rules:
                    rng.shuffle(tiers)
                if "promotion" in rules and a.home < TOP and a.credit >= a.need and len(a.trials) < TRIALS:
                    tiers = [a.home + 1] + tiers
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
            a.homes.append(a.home if a.active and hour >= a.joins else None)
        peak_backlog = max(peak_backlog, sum(len(q) for q in queues.values()))
        peak_hard = max(peak_hard, len(queues[4]) + len(queues[5]))

    return {"agents": agents, "queues": queues, "peak_backlog": peak_backlog, "peak_hard": peak_hard}


# --- Metrics -----------------------------------------------------------------------

def spearman(xs, ys):
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
    return num / den if den else float("nan")


def metrics(res: dict) -> dict:
    agents = res["agents"]
    acc = [(d, ok) for a in agents for _, d, ok, _ in a.done]
    hard_waits = [h - born for a in agents for h, d, ok, born in a.done if ok and d >= 4]
    value = sum(VALUE[d] for d, ok in acc if ok)
    caps, diffs = [], []
    for a in agents:
        work = [d for h, d, _, _ in a.done if h >= WEEK]
        if len(work) >= 5:
            caps.append(a.m.c + a.c_shift)
            diffs.append(statistics.mean(work))
    capped = [a for a in agents if a.m.cap is not None]
    return {
        "value": value,
        "accepted": sum(ok for _, ok in acc),
        "markdown_rate": sum(not ok for _, ok in acc) / max(1, len(acc)),
        "hard_done": sum(1 for d, ok in acc if ok and d >= 4),
        "easy_done": sum(1 for d, ok in acc if ok and d <= 2),
        "backlog_hard": sum(len(res["queues"][d]) for d in (4, 5)),
        "backlog_easy": sum(len(res["queues"][d]) for d in (1, 2)),
        "backlog": sum(len(q) for q in res["queues"].values()),
        "peak_backlog": res["peak_backlog"],
        "peak_hard": res["peak_hard"],
        "alignment": spearman(caps, diffs) if len(set(caps)) >= 3 else float("nan"),
        "frontier_easy": (sum(COST[d] for a in capped for _, d, _, _ in a.done if d <= 2)
                          / max(1, sum(COST[d] for a in capped for _, d, _, _ in a.done))) if capped else float("nan"),
        "hard_wait": statistics.mean(hard_waits) if hard_waits else float("nan"),
        "usd_month": sum(a.m.usd_month for a in agents),
    }


def mean_metrics(keys, n=10, **kw) -> dict:
    rows = [metrics(run(keys, seed=s, **kw)) for s in range(n)]
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows if not (isinstance(r[k], float) and math.isnan(r[k]))]
        out[k] = statistics.mean(vals) if vals else float("nan")
    return out


# --- Scenarios ---------------------------------------------------------------------

PORTFOLIOS = {
    "current (2 frontier, MiMo, local Qwen)": ["sol", "opus", "mimo", "qwen"],
    "recommended (2 frontier, 2 MiMo, Coder)": ["sol", "opus", "mimo", "mimo", "coder"],
    "top-heavy (4 OpenAI/Anthropic, no cheap)": ["sol", "opus", "terra", "luna"],
    "bottom-heavy (1 frontier, cheap + local)": ["sol", "mimo", "qwen", "qwen", "coder"],
    "even spread (one per band)": ["sol", "luna", "mimo", "qwen", "coder"],
}


def outage(keys: set[str], start: int, end: int):
    def ev(hour, agents):
        for a in agents:
            if a.m.key in keys:
                a.active = not (start <= hour < end)
    return ev


def cap_cut(keys: set[str], hour_at: int, scale: float):
    def ev(hour, agents):
        if hour == hour_at:
            for a in agents:
                if a.m.key in keys:
                    a.cap_scale = scale
        if hour == WEEK:
            for a in agents:
                a.cap_scale = 1.0
    return ev


REMOVALS = {
    "no removal": None,
    "low tier out (local Qwen down, days 4-7)": outage({"qwen", "coder"}, 96, 168),
    "mid tier out (MiMo down, days 4-7)": outage({"mimo"}, 96, 168),
    "high tier out (frontier throttled, days 4-7)": outage({"sol", "opus"}, 96, 168),
    "vendor halves frontier caps from day 3": cap_cut({"sol", "opus"}, 72, 0.5),
}


def fmt_row(label, m):
    return (f"  {label:<46} {m['value']:7.0f} {m['hard_done']:6.0f} {m['easy_done']:6.0f} "
            f"{m['backlog_hard']:6.0f} {m['backlog_easy']:6.0f} {m['peak_hard']:6.0f} {m['peak_backlog']:6.0f} "
            f"{m['alignment']:+6.2f} {m['frontier_easy']:7.0%} {m['usd_month']:6.0f}")


HEADER = (f"  {'scenario':<46} {'value':>7} {'T4-5':>6} {'T1-2':>6} {'hardQ':>6} {'easyQ':>6} {'pkHard':>6} "
          f"{'peakQ':>6} {'align':>6} {'F easy':>7} {'$/mo':>6}")


REAL_MODELS = ["sol", "opus", "terra", "luna", "mimo", "qwen", "coder"]


def landing_table(n=8, rules=GOLDEN):
    print("\n== Where models land vs their Artificial Analysis band (cold start at tier 1) ==")
    keys = REAL_MODELS
    lands = defaultdict(list)
    for s in range(n):
        r = run(keys, seed=s, start="cold", rules=rules)
        for a in r["agents"]:
            lands[a.m.key].append(a.homes[-1])
    print(f"  {'model':<26} {'AA':>4} {'% of top':>9} {'AA band':>8} {'true tier*':>11} {'landed (median, range)':>24}")
    for k in keys:
        m = CATALOG[k]
        ls = sorted(lands[k])
        print(f"  {m.label:<26} {m.aa:4.0f} {m.norm:8.0f}% {band(m.norm):8d} {sustain_tier(m.c):11d} "
              f"{statistics.median(ls):>12.0f} ({ls[0]}-{ls[-1]})")
    print("  * true tier = highest tier the model sustains at the standard given its ASSUMED Factory offset")


def degrade(key: str, hour_at: int, drop: float):
    def ev(hour, agents):
        if hour == hour_at:
            for a in agents:
                if a.m.key == key:
                    a.c_shift = -drop
    return ev


def easy_first_tight(hour, agents):
    """Frontier caps cut to 60% all fortnight; easy demand doubled in the first three days."""
    for a in agents:
        if a.m.cap is not None:
            a.cap_scale = 0.6


EASY_SURGE = {1: 8.5, 2: 4.0, 3: 1.7, 4: 0.85, 5: 0.425}

STRESS = {
    "current mix, nominal": dict(keys=["sol", "opus", "mimo", "qwen"]),
    "cold start, even spread": dict(keys=["sol", "luna", "mimo", "qwen", "coder"], start="cold"),
    "tight caps, easy surge": dict(keys=["sol", "opus", "mimo", "qwen"], events=easy_first_tight, demand=EASY_SURGE),
    "overrated model + Opus degrades": dict(keys=["sol", "opus", "overrated", "mimo", "qwen"],
                                            events=degrade("opus", 120, 1.2)),
    "25% of cards mislabelled": dict(keys=["sol", "opus", "mimo", "qwen"], mis_tier=0.25),
    "slow max-effort model at top": dict(keys=["slowmax", "sol", "mimo", "qwen"]),
}


def ablation(n=8):
    base = {s: mean_metrics(n=n, **kw) for s, kw in STRESS.items()}
    print("\n== Golden-rules ablation: remove ONE rule, compare with the full set ==")
    print("  worst case across six stress scenarios, each built to trigger one failure mode")
    print(f"  {'rule removed':<16} {'value':>8} {'hard done':>10} {'hard wait':>10} {'alignment':>10}  {'worst scenario':<34} verdict")
    verdicts = {}
    for rule in ALL_RULES:
        rules = tuple(r for r in ALL_RULES if r != rule)
        rows = []
        for s_name, kw in STRESS.items():
            m, b = mean_metrics(n=n, rules=rules, **kw), base[s_name]
            dv = m["value"] / b["value"] - 1
            dh = m["hard_done"] / b["hard_done"] - 1
            dw = m["hard_wait"] / b["hard_wait"] - 1 if b["hard_wait"] else 0.0
            da = 0.0 if math.isnan(m["alignment"]) or math.isnan(b["alignment"]) else m["alignment"] - b["alignment"]
            harm = max(-dv / 0.02, -dh / 0.05, dw / 0.25, -da / 0.10)
            rows.append((harm, s_name, dv, dh, dw, da))
        worst = max(rows)
        wv = min(r[2] for r in rows); wh = min(r[3] for r in rows)
        ww = max(r[4] for r in rows); wa = min(r[5] for r in rows)
        golden = worst[0] >= 1.0
        verdicts[rule] = (golden, worst[1])
        print(f"  {rule:<16} {wv:+7.1%} {wh:+9.1%} {ww:+9.0%} {wa:+10.2f}  {worst[1]:<34} "
              f"{'GOLDEN' if golden else 'optional'}")
    print("  thresholds: a rule is golden if removing it costs >2% value, >5% hard cards, "
          ">25% longer hard-card waits, or >0.10 alignment in any scenario")
    return verdicts


def vendor_outage(vendor: str):
    keys = {k for k, m in CATALOG.items() if m.vendor == vendor}
    return outage(keys, 96, 168)


def meets(m) -> bool:
    return m["backlog_hard"] <= 10 and m["backlog"] <= 100


def portfolio_search(n=4):
    """Enumerate portfolios under the golden rules; cheapest that meet the service level,
    then test the leaders against a three-day outage of each vendor and a demand surge."""
    options = {"sol": (0, 1), "opus": (0, 1), "terra": (0, 1), "luna": (0, 1),
               "mimo": (0, 1, 2), "qwen": (0, 1, 2), "coder": (0, 1, 2)}
    results = []
    for combo in itertools.product(*options.values()):
        keys = [k for k, c in zip(options, combo) for _ in range(c)]
        if not keys:
            continue
        m = mean_metrics(keys, n=n, rules=GOLDEN)
        m["keys"] = keys
        results.append(m)
    ok = [r for r in results if meets(r)]
    best = max(results, key=lambda r: r["value"])
    print(f"\n== Portfolio search: {len(results)} portfolios under the golden rules; {len(ok)} meet the service level ==")
    print("  service level at nominal demand: <=10 tier 4-5 cards and <=100 cards in total waiting after two weeks")
    print(f"  best value of any portfolio: {best['value']:.0f} at ${best['usd_month']:.0f}/mo ({describe(best['keys'])})")
    leaders = sorted(ok, key=lambda r: (r["usd_month"], -r["value"]))[:8]
    vendors = sorted({CATALOG[k].vendor for r in leaders for k in r["keys"]})
    print("\n  cheapest portfolios meeting the service level, with resilience tests:")
    print(f"  {'$/mo':>5} {'value':>6} {'hard':>5}  {'survives vendor outage':<24} {'surge queue':>11}  portfolio")
    for r in leaders:
        survived, failed = [], []
        for v in {CATALOG[k].vendor for k in r["keys"]}:
            mv = mean_metrics(r["keys"], n=n, rules=GOLDEN, events=vendor_outage(v))
            (survived if meets(mv) else failed).append(v)
        surge = mean_metrics(r["keys"], n=n, rules=GOLDEN, demand=SURGE)
        res = "all" if not failed else "fails: " + ",".join(sorted(failed))
        print(f"  {r['usd_month']:5.0f} {r['value']:6.0f} {r['hard_done']:5.0f}  {res:<24} {surge['backlog']:11.0f}  {describe(r['keys'])}")
    return results, ok


def describe(keys):
    c = defaultdict(int)
    for k in keys:
        c[k] += 1
    return ", ".join(f"{n}x {CATALOG[k].label}" if n > 1 else CATALOG[k].label for k, n in c.items())


if __name__ == "__main__":
    landing_table()

    print("\n== Model mixes under the golden rules, nominal demand (no removal), mean of 10 runs ==")
    print(HEADER)
    for label, keys in PORTFOLIOS.items():
        print(fmt_row(label, mean_metrics(keys, rules=GOLDEN)))
    print("\n== Model mixes, surge demand (+18%) ==")
    print(HEADER)
    for label, keys in PORTFOLIOS.items():
        print(fmt_row(label, mean_metrics(keys, rules=GOLDEN, demand=SURGE)))

    for label, keys in PORTFOLIOS.items():
        print(f"\n== Removals on: {label} ==")
        print(HEADER)
        for rlabel, ev in REMOVALS.items():
            print(fmt_row(rlabel, mean_metrics(keys, rules=GOLDEN, events=ev)))

    ablation(n=24)
    portfolio_search()
