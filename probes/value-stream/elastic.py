"""Elasticity: fixed seats vs model instances started and stopped by Ledger rules.

Ideas arrive over time (open system). Five demand patterns, each averaging
25 ideas a week unless stated:
  steady       Poisson, 25 a week
  bursty       two-day bursts at 2.5x, then 0.4x for five days (same mean)
  growth       ramps from 10 to 80 a week over the seven weeks
  mixed        steady rate; idea size 3, 8 or 20 requirements (40/40/20%) and
               difficulty -10, 0 or +10 points (30/40/30%)
  surge        60 a week, about twice what six fixed seats can take

Organisations (all run the institutions' rules on the value stream):
  fixed six / twelve / 24   one, two or four seats per model of the six
  elastic                   the Scaler (vs_sim.py) over the same six models,
                            0-8 instances each (vendor rate limits [assumption]),
                            quality floor 0.8 and strict cost-band pull (rule 6);
                            the cheapest-only rule (floor 0.6); and no pull rules
  elastic, one model        a swarm of one model only (Opus 5.5 / Gemini 3.8 Flash)
  elastic, two models       Opus 5.5 + Gemini 3.8 Flash
  elastic, capped           burn cap in $/hour on running instances (sweep)

Scale sweep: demand from 10 to 150 ideas a week with light and heavy merge
contention, uncapped: where does the marginal cost of a clean idea start to
rise (contention, rate limits)?

Measured: clean ideas/week, ideas live, lead time median and 90th percentile,
backlog at the end, change failure rate, $ per clean idea (API: idle instances
cost nothing), instance-hours per week, peak instances.

Run: python3 probes/value-stream/elastic.py   (about 15 minutes on 4 cores)
"""

from __future__ import annotations

import json
import math
from multiprocessing import Pool
from pathlib import Path

import orgs as o
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 4
WEEK = 168.0
SIX = o.SIX
OPUS, GEMINI = SIX[0], SIX[2]


def weekly(x):
    return x / WEEK


DEMANDS = {
    "steady": dict(rate=("const", 25)),
    "bursty": dict(rate=("burst", 25)),
    "growth": dict(rate=("ramp", 10, 80)),
    "mixed": dict(rate=("const", 25), sizes=((3, .4), (8, .4), (20, .2)), shifts=((-10, .3), (0, .4), (10, .3))),
    "surge": dict(rate=("const", 60)),
    "harder": dict(rate=("const", 25), shifts=((0, .3), (10, .4), (20, .3))),
}
TERRA = "GPT-5.6 Terra (max)"
MENUS = {
    "six with Opus 5.5 (r11)": SIX,
    "six with GPT-5.6 Terra": [TERRA] + SIX[1:],
    "seven (Opus 5.5 + Terra)": SIX + [TERRA],
    "whole shortlist (24 models)": list(dict.fromkeys(v.s6.TOP_NAMES + v.s6.MID_NAMES)),
}


def make_demand(spec, horizon=7 * WEEK):
    kind = spec["rate"]
    if kind[0] == "const":
        fn, mx = (lambda t, r=kind[1]: weekly(r)), weekly(kind[1])
    elif kind[0] == "burst":
        mean = kind[1]
        fn = lambda t, m=mean: weekly(m) * (2.5 if (t % WEEK) < 48 else 0.4)   # noqa: E731
        mx = weekly(mean) * 2.5
    else:
        a, b = kind[1], kind[2]
        fn = lambda t, a=a, b=b: weekly(a + (b - a) * min(1.0, t / horizon))     # noqa: E731
        mx = weekly(b)
    return v.Demand(fn, mx, spec.get("sizes", ((v.R_REQ, 1.0),)), spec.get("shifts", ((0.0, 1.0),)))


def configs():
    c = {"fixed six": ("fixed", SIX, 1), "fixed twelve": ("fixed", SIX, 2), "fixed 24": ("fixed", SIX, 4),
         "elastic (six models, floor 0.8)": ("elastic", SIX, None),
         "elastic, cheapest only (floor 0.6)": ("elastic", SIX, "floor0.6"),
         "elastic, no pull rules (no cost band)": ("elastic", SIX, "noband"),
         "elastic, one model: Opus 5.5": ("elastic", [OPUS], None),
         "elastic, one model: Gemini 3.8 Flash": ("elastic", [GEMINI], None),
         "elastic, two models: Opus + Gemini": ("elastic", [OPUS, GEMINI], None)}
    return c


def build(kind, names, arg):
    base = {s.cfg.name: s for s in o.roster("best six", 0)}
    for n in names:
        if n not in base:
            cfg = v.s6.roster([n])[0].cfg
            base[n] = v.Seat(cfg, 0, cls="A" if cfg.ci >= 78 else "F" if cfg.ci >= 56.8 else "M")
    if kind == "fixed":
        seats = []
        for n in names:
            for _ in range(arg):
                s = base[n]
                seats.append(v.Seat(s.cfg, len(seats), cls=s.cls))
        return seats, None
    models = [base[n].cfg for n in names]
    rate = {n: v.s6.usd_per_busy_hour(v.s6.C[n]) for n in names}
    floor = 0.6 if arg == "floor0.6" else 0.8
    cap = None if isinstance(arg, str) else arg
    mx = 48 // len(names) if len(names) < 6 else 8           # same total ceiling (48) for every elastic swarm
    sc = v.Scaler(models, rate, cls={n: base[n].cls for n in names}, default_max=mx, cap_usd_h=cap, floor=floor,
                  total_max=48)
    if arg == "noband":
        sc.band, sc.strict = None, False
    return [], sc


def job(args):
    dname, kind, names, arg, seed = args[:5]
    k = args[5] if len(args) > 5 else None
    seats, scaler = build(kind, names, arg)
    spec = DEMANDS[dname] if isinstance(dname, str) else dict(rate=("const", dname))
    sim = v.Sim(v.Org("institutions"), seats, seed=seed, wip=6, demand=make_demand(spec), scaler=scaler, conflict_k=k)
    return v.measure(sim.run())


def evaluate(pool, items, conflict=None):
    jobs = [(d, *spec, k, conflict) for d, spec in items for k in range(SEEDS)]
    res = pool.map(job, jobs, chunksize=1)
    return [v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS]) for i in range(len(items))]


def row(label, m):
    return (f"  {label:<38} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h  "
            f"backlog {m['backlog']:4.0f}  CFR {m['cfr']:4.0%}  ${m['usd_clean']:5.0f}/clean  ${m['usd_week']:6.0f}/wk  "
            f"seat-h {m['seat_h']:5.0f}  peak {m['peak']:3.0f}  util {m['util']:.2f}")


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    cfg = configs()
    with Pool() as pool:
        say("FIXED vs ELASTIC (institutions' rules on the idea-to-live value stream; lead = median/90th percentile)")
        for d in DEMANDS:
            items = [(d, spec) for spec in cfg.values()]
            res = evaluate(pool, items)
            say(f"\n[{d}]")
            for label, m in zip(cfg, res):
                say(row(label, m))
                out.setdefault("compare", {}).setdefault(d, {})[label] = {k: x for k, x in m.items() if k != "waits"}
        say("\nBUDGET CAP sweep, elastic six models ($/hour of running instances at API rates)")
        caps = [2, 5, 10, 20, 40, None]
        for d in ("growth", "surge", "bursty"):
            items = [(d, ("elastic", SIX, c)) for c in caps]
            res = evaluate(pool, items)
            say(f"\n[{d}]")
            full = res[-1]
            for c, m in zip(caps, res):
                say(row(f"cap {'none' if c is None else '$' + str(c) + '/h'}", m) + f"  ({m['clean'] / full['clean']:4.0%} of uncapped)")
                out.setdefault("caps", {}).setdefault(d, {})[str(c)] = {k: x for k, x in m.items() if k != "waits"}
            ok = [(c, m) for c, m in zip(caps, res) if m["clean"] >= 0.95 * full["clean"] and m["lead_p90"] <= 1.25 * full["lead_p90"]]
            c, m = ok[0]
            say(f"  sweet spot: the lowest cap within 5% of uncapped clean output and 25% of its p90 lead time: "
                f"{'none' if c is None else '$' + str(c) + '/h'} (spend ${m['usd_week']:.0f}/wk = ${m['usd_week'] * 52 / 12:.0f}/month)")
            out.setdefault("sweet", {})[d] = dict(cap=c, usd_week=m["usd_week"])

        say("\nMENU: which models the Scaler may start (floor 0.8, 48 instances in all); a model costs nothing unless used")
        for d in ("steady", "mixed", "harder", "surge"):
            res = evaluate(pool, [(d, ("elastic", names, None)) for names in MENUS.values()])
            say(f"\n[{d}]")
            for label, m in zip(MENUS, res):
                say(row(label, m))
                out.setdefault("menus", {}).setdefault(d, {})[label] = {k: x for k, x in m.items() if k != "waits"}
            use = res[-1]["busy_model"]
            tot = sum(use.values())
            say("  whole shortlist, share of busy hours: " + ", ".join(
                f"{v.s6.label(n)} {h / tot:.0%}" for n, h in sorted(use.items(), key=lambda kv: -kv[1]) if h / tot >= 0.02))
        say("\nSCALE: elastic six models, uncapped, demand from 10 to 150 ideas a week; merge contention light (k=0.005) and heavy (k=0.02)")
        for kname, kval in (("light", 0.005), ("heavy", 0.02)):
            rates = [10, 25, 50, 100, 150]
            res = evaluate(pool, [(r, ("elastic", SIX, None)) for r in rates], conflict=kval)
            say(f"\n[contention {kname}]")
            prev = None
            for r, m in zip(rates, res):
                marg = (m["usd_week"] - prev["usd_week"]) / max(1e-9, m["clean"] - prev["clean"]) if prev else float("nan")
                say(row(f"{r} ideas/wk arriving", m) + f"  marginal ${marg:5.0f}/clean")
                out.setdefault("scale", {}).setdefault(kname, {})[r] = dict({k: x for k, x in m.items() if k != "waits"}, marginal=marg)
                prev = m

    (HERE / "elastic_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "elastic.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
