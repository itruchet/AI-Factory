"""Market simulation on real Artificial Analysis coding data.

Idea-stage probe for docs/idea/constitutional-factory.md (r9). The model pool,
scores, prices and speeds are real (aa_coding_2026-09-09.csv). Everything else
is a labelled assumption: how scores turn into pass rates, the Factory's
demand mix, card sizes, value per card, slots per seat, and the market's
future (drawn from the observed release cadence).

Tiers are the natural tiers found by tiering.py: three Jenks groups on the
current configurations. Card tiers are ABSOLUTE: the Factory's work does not
get harder when better models are released.

Allocation uses the five golden rules (hardest first, promotion by credit,
two-speed demotion, fast track for entrants; the hard-work reserve applies
only to capped seats, and API seats are uncapped).

Experiments
  E1  homogeneous portfolios: all top tier vs all middle vs all bottom
  E2  every mix of six seats across the three tiers (28 mixes)
  E3  portfolio size: 3 to 12 seats
  E4  26-week rolling market: new models arrive at the observed rate, models
      deprecate, vendors have outages, and three portfolio policies compete:
        static      keep the starting seats
        chase       swap in the top new release by leaderboard score at once
        evidence    a trial seat earns its place on Ledger value per dollar,
                    with a 10% margin to avoid churn
        guarded     evidence, plus portfolio rules P1/P2: always keep two
                    top-tier seats from two vendors, and no vendor above
                    half the seats

Run: python3 probes/aa-tiers/market_sim.py
"""

from __future__ import annotations

import csv
import math
import random
import statistics
from collections import deque, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent

# --- Real data ---------------------------------------------------------------------
TIER_LOW = {1: 56.8, 2: 29.9, 3: 0.0}          # Jenks 3-tier lower bounds (tiering.py)
TIER_HIGH = {1: 81.6, 2: 56.8, 3: 29.9}
CARD_FLOOR = {1: 56.8, 2: 29.9, 3: 10.0}        # easiest card in each tier (ASSUMED for tier 3)
TIERS = (1, 2, 3)                               # 1 = hardest


def tier_of(ci: float) -> int:
    return 1 if ci >= TIER_LOW[1] else 2 if ci >= TIER_LOW[2] else 3


@dataclass(frozen=True)
class Config:
    name: str
    creator: str
    ci: float
    price: float          # USD per 1M tokens, blended 3:1
    speed: float          # output tokens per second
    released: str

    @property
    def tier(self) -> int:
        return tier_of(self.ci)


def load_pool() -> list[Config]:
    rows = csv.DictReader(open(HERE / "aa_coding_2026-09-09.csv"))
    pool = []
    for r in rows:
        if r["deprecated"] == "True" or r["price_blended_usd_per_1m"] in ("", "None"):
            continue
        sp = float(r["output_tokens_per_s"] or 0)
        ci = float(r["coding_index"])
        if sp <= 0 or ci <= 0:
            continue
        pool.append(Config(r["name"], r["creator"], ci, float(r["price_blended_usd_per_1m"]), sp, r["release_date"]))
    return pool


POOL = load_pool()
BY_TIER = {t: [c for c in POOL if c.tier == t] for t in TIERS}

# --- Assumptions (Factory side) ----------------------------------------------------
STANDARD = {1: 0.25, 2: 0.20, 3: 0.15}          # max markdown rate per tier
SLOPE = 0.15                                    # logit change per Coding Index point
TOKENS = {1: 150_000, 2: 60_000, 3: 20_000}     # tokens per card (input + output)
BASE_HOURS = {1: 2.0, 2: 1.0, 3: 0.5}           # cycle time at 100 output tokens/s
VALUE = {1: 10.0, 2: 4.0, 3: 1.0}               # value points per accepted card
SLOTS = 4                                       # parallel cards per seat
PYRAMID = {1: 2.0, 2: 4.0, 3: 6.0}              # cards per hour: most work is easy
HARD_HEAVY = {1: 4.0, 2: 4.0, 3: 2.0}
PROMOTE_CREDIT, DEBIT, FAST_TRACK, TRIALS, BATCH = 20, 4, 5, 20, 20


def p_pass(ci: float, difficulty: float, tier: int) -> float:
    z = math.log((1 - STANDARD[tier]) / STANDARD[tier]) + SLOPE * (ci - difficulty)
    return 1 / (1 + math.exp(-z))


def sustain_tier(ci: float) -> int:
    """Hardest tier whose typical card this score passes within the standard."""
    for t in TIERS:
        mid = CARD_FLOOR[t] + 0.3 * (TIER_HIGH[t] - CARD_FLOOR[t])
        if 1 - p_pass(ci, mid, t) <= STANDARD[t]:
            return t
    return 3


# --- Engine ------------------------------------------------------------------------

@dataclass
class Seat:
    cfg: Config
    home: int
    since: int = 0
    active: bool = True
    busy: list = field(default_factory=list)
    credit: int = 0
    need: int = PROMOTE_CREDIT
    trials: list = field(default_factory=list)
    batch: list = field(default_factory=list)
    strikes: int = 0
    recent: dict = field(default_factory=lambda: defaultdict(lambda: deque(maxlen=BATCH)))
    value: float = 0.0
    cost: float = 0.0
    done: int = 0
    marked: int = 0
    work_by_tier: dict = field(default_factory=lambda: defaultdict(int))

    def hours(self, t: int) -> float:
        return BASE_HOURS[t] * 100 / max(self.cfg.speed, 10)


@dataclass
class Card:
    tier: int
    difficulty: float
    born: float
    attempts: int = 0


class Factory:
    def __init__(self, seats: list[Seat], demand: dict, seed: int, entrant_fast_track=True, help_after=0.0):
        self.seats = seats
        self.demand = demand
        self.rng = random.Random(seed)
        self.queues = {t: deque() for t in TIERS}
        self.carry = defaultdict(float)
        self.t = 0
        self.value = self.cost = 0.0
        self.accepted = defaultdict(int)
        self.markdowns = 0
        self.hard_waits = []
        self.fast_track = entrant_fast_track
        self.help_after = help_after            # hours an easier card waits per tier of distance
                                                # before a more capable (pricier) seat may take it

    def add_seat(self, cfg: Config, home: int, fast=True) -> Seat:
        s = Seat(cfg, home, since=self.t)
        if fast and self.fast_track:
            s.need = FAST_TRACK
        self.seats.append(s)
        return s

    def step(self):
        rng = self.rng
        for t, rate in self.demand.items():
            self.carry[t] += rate
            while self.carry[t] >= 1:
                width = TIER_HIGH[t] - CARD_FLOOR[t]
                self.queues[t].append(Card(t, CARD_FLOOR[t] + rng.uniform(0, 0.6 * width), self.t))
                self.carry[t] -= 1
        seats = [s for s in self.seats if s.active]
        rng.shuffle(seats)
        for s in seats:
            done = [b for b in s.busy if b[0] <= self.t]
            s.busy = [b for b in s.busy if b[0] > self.t]
            for _, card in done:
                self.finish(s, card)
            while len(s.busy) < SLOTS:
                order = list(range(s.home, 4))                     # hardest licensed first
                if s.home > 1 and s.credit >= s.need and len(s.trials) < TRIALS:
                    order = [s.home - 1] + order                   # compulsory trial card
                card = None
                for t in order:
                    if self.queues[t]:
                        if t > s.home and self.t - self.queues[t][0].born < self.help_after * (t - s.home):
                            continue                           # leave it for a seat licensed nearer that tier
                        card = self.queues[t].popleft()
                        break
                if card is None:
                    break
                s.busy.append((self.t + max(1, round(s.hours(card.tier))), card))
        self.t += 1

    def finish(self, s: Seat, card: Card):
        t = card.tier
        ok = self.rng.random() < p_pass(s.cfg.ci, card.difficulty, t)
        c = s.cfg.price * TOKENS[t] / 1e6
        s.cost += c
        self.cost += c
        s.done += 1
        s.work_by_tier[t] += 1
        s.recent[t].append(ok)
        if ok:
            s.value += VALUE[t]
            self.value += VALUE[t]
            self.accepted[t] += 1
            if t == 1:
                self.hard_waits.append(self.t - card.born)
        else:
            s.marked += 1
            self.markdowns += 1
            card.attempts += 1
            self.queues[t].appendleft(card)
        # promotion (tier numbers fall as work gets harder)
        if t < s.home:
            s.trials.append(ok)
            if len(s.trials) == TRIALS:
                if s.trials.count(False) / TRIALS <= STANDARD[t]:
                    s.home = t
                    if s.need != FAST_TRACK:
                        s.need = PROMOTE_CREDIT
                else:
                    s.need = min(2 * PROMOTE_CREDIT, max(s.need, PROMOTE_CREDIT) * 2)
                s.trials, s.credit = [], 0
        elif t == s.home:
            s.credit = s.credit + 1 if ok else max(0, s.credit - DEBIT)
            s.batch.append(ok)
            last = list(s.recent[t])[-10:]
            gross = len(last) == 10 and last.count(False) / 10 > 2 * STANDARD[t]
            marginal = False
            if len(s.batch) == BATCH:
                over = s.batch.count(False) / BATCH > 1.25 * STANDARD[t]
                s.strikes = s.strikes + 1 if over else 0
                marginal = s.strikes >= 2
                s.batch = []
            if s.home < 3 and (gross or marginal):
                s.home += 1
                s.recent[t].clear()
                s.batch, s.strikes, s.credit, s.need = [], 0, 0, PROMOTE_CREDIT

    def backlog(self):
        return {t: len(q) for t, q in self.queues.items()}


def summary(f: Factory, hours: int) -> dict:
    b = f.backlog()
    return {
        "value": f.value, "cost": f.cost, "value_per_usd": f.value / max(f.cost, 1e-9),
        "hard_done": f.accepted[1], "backlog_hard": b[1], "backlog": sum(b.values()),
        "markdown_rate": f.markdowns / max(1, f.markdowns + sum(f.accepted.values())),
        "hard_wait": statistics.mean(f.hard_waits) if f.hard_waits else float("nan"),
        "per_week_value": f.value / (hours / 168), "per_week_cost": f.cost / (hours / 168),
    }


def draw(tier: int, rng: random.Random) -> Config:
    return rng.choice(BY_TIER[tier])


def static_run(counts: dict, demand=PYRAMID, hours=4 * 168, seed=0, help_after=0.0) -> dict:
    rng = random.Random(seed)
    seats = [Seat(c, c.tier) for t in TIERS for c in (draw(t, rng) for _ in range(counts.get(t, 0)))]
    f = Factory(seats, demand, seed, help_after=help_after)
    for _ in range(hours):
        f.step()
    return summary(f, hours)


def mean_static(counts, n=12, **kw):
    rows = [static_run(counts, seed=s, **kw) for s in range(n)]
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows if not math.isnan(r[k])]
        out[k] = statistics.mean(vals) if vals else float("nan")
    return out


# --- E4: rolling market ------------------------------------------------------------

def monthly_arrivals() -> dict:
    """New configurations per month by tier, from the last three release months."""
    recent = [c for c in POOL if c.released >= "2026-06-01"]
    months = 3.3
    return {t: sum(c.tier == t for c in recent) / months for t in TIERS}


ARRIVALS = monthly_arrivals()
FRONTIER_DRIFT = 1.9 / 4.35     # Coding Index points per week at the frontier (observed: +1.9/month)


def new_release(rng: random.Random, week: int) -> Config:
    """A plausible new release: a tier by observed arrival shares, a score from the
    recent releases of that tier shifted by the frontier drift, a matching price."""
    total = sum(ARRIVALS.values())
    r, acc, tier = rng.uniform(0, total), 0.0, 3
    for t in TIERS:
        acc += ARRIVALS[t]
        if r <= acc:
            tier = t
            break
    base = rng.choice([c for c in POOL if c.tier == tier and c.released >= "2026-04-01"] or BY_TIER[tier])
    ci = min(95.0, base.ci + FRONTIER_DRIFT * week * rng.uniform(0.5, 1.5))
    return Config(f"{base.creator} new-w{week}-{rng.randrange(1000)}", base.creator, ci,
                  base.price * rng.uniform(0.6, 1.2), base.speed * rng.uniform(0.9, 1.3), f"w{week}")


def rolling(policy: str, seed=0, weeks=26, seats=6, demand=PYRAMID, outage_p=0.04, deprecate_p=0.02):
    rng = random.Random(seed * 7 + 1)
    start = random.Random(seed)
    initial = [draw(1, start), draw(1, start), draw(2, start), draw(2, start), draw(3, start), draw(3, start)][:seats]
    f = Factory([Seat(c, c.tier) for c in initial], demand, seed)
    trial: Seat | None = None
    trial_start = 0
    market: list[Config] = []
    log = []
    down_until = {}
    for week in range(weeks):
        # market events
        n_new = sum(rng.random() < a / 4.35 for a in ARRIVALS.values() for _ in range(3)) // 1
        market.extend(new_release(rng, week) for _ in range(n_new))
        for s in f.seats:
            if s.active and s is not trial and rng.random() < deprecate_p:
                s.active = False                              # vendor deprecates the model
                s.cfg = s.cfg
        vendors = {s.cfg.creator for s in f.seats if s.active}
        for v in vendors:
            if rng.random() < outage_p:
                down_until[v] = f.t + rng.choice([24, 48, 72])
        # policy
        active = [s for s in f.seats if s.active]
        if policy in ("chase", "evidence", "guarded"):
            while len(active) < seats and market:              # backfill retired seats
                best = max(market, key=lambda c: c.ci / (c.price + 0.05))
                market.remove(best)
                active.append(f.add_seat(best, best.tier))
        if policy == "static":
            while len(active) < seats:                         # replace like for like
                gone = next(s for s in f.seats if not s.active and not getattr(s, "replaced", False))
                gone.replaced = True
                c = draw(gone.cfg.tier, rng)
                active.append(f.add_seat(c, c.tier, fast=False))
        if policy == "chase" and market:
            top = max(market, key=lambda c: c.ci)
            worst = min(active, key=lambda s: s.cfg.ci)
            if top.ci > worst.cfg.ci + 3:
                worst.active = False
                market.remove(top)
                f.add_seat(top, top.tier)
        if policy == "guarded":                                # immediate repair seat (P1)
            inc = [s for s in f.seats if s.active and s is not trial]
            if not diverse(inc, seats) and len(inc) <= seats:
                have = {s.cfg.creator for s in inc if s.home == 1}
                need = [c for c in market if c.tier == 1 and c.creator not in have]
                if need:
                    fix = max(need, key=lambda c: c.ci / (c.price + 0.05))
                    market.remove(fix)
                    f.add_seat(fix, fix.tier)
                    spare = sorted((s for s in inc if s.home != 1), key=lambda s: s.value / max(s.cost, 1e-6))
                    if len(inc) + 1 > seats and spare:
                        spare[0].active = False
        if policy in ("evidence", "guarded"):
            if trial is None and market:
                pool = market
                incumbents = [s for s in f.seats if s.active]
                if policy == "guarded" and not diverse(incumbents, seats):
                    have = {s.cfg.creator for s in incumbents if s.home == 1}
                    need = [c for c in market if c.tier == 1 and c.creator not in have]
                    pool = need or pool                        # fill the missing top-tier vendor first
                cand = max(pool, key=lambda c: c.ci / (c.price + 0.05))
                market.remove(cand)
                trial = f.add_seat(cand, cand.tier)
                trial_start = f.t
            elif trial is not None and f.t - trial_start >= 2 * 168:
                incumbents = [s for s in f.seats if s.active and s is not trial]
                vpd = lambda s: s.value / max(s.cost, 1e-6) * (1 if s.done >= 10 else 0)
                ranked = sorted(incumbents, key=vpd)
                if policy == "guarded":
                    ranked = [w for w in ranked if diverse([s for s in incumbents if s is not w] + [trial], seats)]
                worst = ranked[0] if ranked else None
                repairs = policy == "guarded" and not diverse(incumbents, seats) and \
                    diverse([s for s in incumbents if s is not worst] + [trial], seats) if worst is not None else False
                if worst is not None and trial.done >= 20 and (repairs or (vpd(trial) > 1.10 * vpd(worst)
                                                                          and trial.value > 0.5 * worst.value)):
                    worst.active = False                       # trial earns the seat
                elif len(incumbents) >= seats:
                    trial.active = False                       # trial released
                trial = None
        # run the week with outages applied
        for _ in range(168):
            for s in f.seats:
                if s.active and down_until.get(s.cfg.creator, -1) > f.t:
                    s.paused = True
                elif getattr(s, "paused", False):
                    s.paused = False
            paused = [s for s in f.seats if getattr(s, "paused", False) and s.active]
            for s in paused:
                s.active = False
            f.step()
            for s in paused:
                s.active = True
        act = [s for s in f.seats if s.active]
        vendors_now = [s.cfg.creator for s in act]
        log.append({
            "top_vendor_share": max(vendors_now.count(v) for v in set(vendors_now)) / len(vendors_now),
            "vendors": len(set(vendors_now)),
            "top_tier_seats": sum(s.home == 1 for s in act),
            "top_tier_vendors": len({s.cfg.creator for s in act if s.home == 1}),
            "week": week, "value": f.value, "cost": f.cost,
            "seats": [(s.cfg.name, round(s.cfg.ci, 1), s.home, round(s.cfg.price, 2)) for s in act],
            "homes": sorted(s.home for s in act), "backlog": sum(f.backlog().values()),
            "backlog_hard": f.backlog()[1],
        })
    swaps = sum(1 for s in f.seats) - seats
    return f, log, swaps


def diverse(seats_after: list, limit: int) -> bool:
    """P1: two top-tier seats from two vendors. P2: no vendor above half the seats."""
    top = [s for s in seats_after if s.home == 1]
    vendors = [s.cfg.creator for s in seats_after]
    cap = math.ceil(limit / 2)
    return len(top) >= 2 and len({s.cfg.creator for s in top}) >= 2 and \
        all(vendors.count(v) <= cap for v in set(vendors))


def weekly(log, key):
    out, prev = [], 0.0
    for w in log:
        out.append(w[key] - prev)
        prev = w[key]
    return out


# --- Reporting ---------------------------------------------------------------------

def e1():
    print("\n== E1 Homogeneous portfolios (6 seats, 4 weeks, real configs drawn per tier, 12 draws) ==")
    print(f"  {'portfolio':<22} {'value/wk':>9} {'$/wk':>8} {'value/$':>8} {'hard done':>9} {'hard left':>9} {'all left':>9} {'markdown':>9}")
    for label, counts in (("all top tier", {1: 6}), ("all middle tier", {2: 6}), ("all bottom tier", {3: 6})):
        for dlabel, dem in (("pyramid", PYRAMID), ("hard-heavy", HARD_HEAVY)):
            m = mean_static(counts, demand=dem)
            print(f"  {label + ', ' + dlabel:<22} {m['per_week_value']:9.0f} {m['per_week_cost']:8.0f} {m['value_per_usd']:8.1f} "
                  f"{m['hard_done']:9.0f} {m['backlog_hard']:9.0f} {m['backlog']:9.0f} {m['markdown_rate']:8.1%}")


def e2(demand=PYRAMID, label="pyramid"):
    print(f"\n== E2 Every mix of six seats ({label} demand), mean of 12 draws ==")
    print(f"  {'top/mid/bottom':<15} {'value/wk':>9} {'$/wk':>8} {'value/$':>8} {'hard left':>9} {'all left':>9}")
    rows = []
    for n1 in range(7):
        for n2 in range(7 - n1):
            n3 = 6 - n1 - n2
            m = mean_static({1: n1, 2: n2, 3: n3}, demand=demand)
            rows.append(((n1, n2, n3), m))
    ok = [r for r in rows if r[1]["backlog_hard"] <= 20 and r[1]["backlog"] <= 200]
    for mix, m in sorted(rows, key=lambda r: -r[1]["per_week_value"])[:10]:
        flag = "" if (mix, m) in ok else "  (misses service level)"
        print(f"  {'/'.join(map(str, mix)):<15} {m['per_week_value']:9.0f} {m['per_week_cost']:8.0f} {m['value_per_usd']:8.1f} "
              f"{m['backlog_hard']:9.0f} {m['backlog']:9.0f}{flag}")
    if ok:
        best_vpd = max(ok, key=lambda r: r[1]["value_per_usd"])
        best_val = max(ok, key=lambda r: r[1]["per_week_value"])
        print(f"  best value meeting service level: {'/'.join(map(str, best_val[0]))}; "
              f"best value per $: {'/'.join(map(str, best_vpd[0]))}")
    return rows


def e3():
    print("\n== E3 Portfolio size (pyramid demand; seats split 1/3 top, 1/3 middle, 1/3 bottom, rounding up at the top) ==")
    print(f"  {'seats':>5} {'mix':>7} {'value/wk':>9} {'$/wk':>8} {'value/$':>8} {'hard left':>9} {'all left':>9}")
    for n in range(3, 13):
        n1 = math.ceil(n / 3); n2 = (n - n1) // 2; n3 = n - n1 - n2
        m = mean_static({1: n1, 2: n2, 3: n3})
        print(f"  {n:>5} {f'{n1}/{n2}/{n3}':>7} {m['per_week_value']:9.0f} {m['per_week_cost']:8.0f} {m['value_per_usd']:8.1f} "
              f"{m['backlog_hard']:9.0f} {m['backlog']:9.0f}")


def e4(n=8):
    print(f"\n== E4 Rolling market, 26 weeks, four portfolio policies, mean of {n} runs ==")
    print(f"  observed arrivals per month: top {ARRIVALS[1]:.1f}, middle {ARRIVALS[2]:.1f}, bottom {ARRIVALS[3]:.1f}; "
          f"frontier drift {FRONTIER_DRIFT * 4.35:.1f} points a month")
    print(f"  {'policy':<9} {'value':>8} {'cost $':>7} {'value/$':>7} {'swaps':>6} {'hard-backlog wks':>16} "
          f"{'wk1-4 -> wk23-26':>17} {'top vendor share':>16} {'weeks <2 top vendors':>20} {'bottom seats at end':>19}")
    out = {}
    for policy in ("static", "chase", "evidence", "guarded"):
        r = defaultdict(list)
        for s in range(n):
            f, log, sw = rolling(policy, seed=s)
            wv = weekly(log, "value")
            r["value"].append(f.value); r["cost"].append(f.cost); r["swaps"].append(sw)
            r["hard"].append(sum(w["backlog_hard"] > 20 for w in log))
            r["early"].append(statistics.mean(wv[:4])); r["late"].append(statistics.mean(wv[-4:]))
            r["share"].append(statistics.mean(w["top_vendor_share"] for w in log[-8:]))
            r["thin"].append(sum(w["top_tier_vendors"] < 2 for w in log))
            r["bottom"].append(sum(1 for x in log[-1]["homes"] if x == 3))
        m = {k: statistics.mean(v) for k, v in r.items()}
        out[policy] = m
        print(f"  {policy:<9} {m['value']:8.0f} {m['cost']:7.0f} {m['value'] / m['cost']:7.1f} {m['swaps']:6.1f} "
              f"{m['hard']:16.1f} {m['early']:8.0f} -> {m['late']:<6.0f} {m['share']:16.0%} {m['thin']:20.1f} {m['bottom']:19.1f}")
    return out


def e5():
    print("\n== E5 Per-token pricing: should capable seats wait before taking easier cards? ==")
    print(f"  {'mix':<8} {'rule':<26} {'value/wk':>9} {'$/wk':>7} {'value/$':>8} {'hard left':>9} {'all left':>9}")
    for mix in ({1: 3, 2: 3}, {1: 2, 2: 2, 3: 2}, {1: 3, 2: 2, 3: 2}):
        for h, label in ((0.0, "hardest first, no wait"), (2.0, "wait 2 h per tier"), (6.0, "wait 6 h per tier")):
            m = mean_static(mix, help_after=h)
            name = "/".join(str(mix.get(t, 0)) for t in TIERS)
            print(f"  {name:<8} {label:<26} {m['per_week_value']:9.0f} {m['per_week_cost']:7.0f} {m['value_per_usd']:8.1f} "
                  f"{m['backlog_hard']:9.0f} {m['backlog']:9.0f}")


if __name__ == "__main__":
    print(f"Real pool: {len(POOL)} current, priced configurations; per tier: "
          + ", ".join(f"T{t} {len(BY_TIER[t])}" for t in TIERS))
    e1()
    e2()
    e2(HARD_HEAVY, "hard-heavy")
    e3()
    e4()
    e5()
