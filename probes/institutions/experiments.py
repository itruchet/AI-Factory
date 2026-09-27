"""Experiments on the institutional throughput model (factory_sim.py).

E1  headcount scaling: baseline (Director-Worker-Checker) vs institutions,
    tiers in proportion to the real Artificial Analysis population
E2  tier mix: every mix of top/middle/bottom agents at 6, 9 and 12 agents
E3  institution sizing: Inquiry participants K, planners D, council rounds,
    red team, audit, work-in-progress limit
E4  shared pool vs seats dedicated to one institution
E5  sensitivity of the headline results to the main assumptions

Writes results.json (for the report page) and prints tables.
Run: python3 probes/institutions/experiments.py   (about 10 minutes)
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

import factory_sim as f

HERE = Path(__file__).parent
SEEDS = 4
POP = {1: 63, 2: 40, 3: 33}                              # real pool by natural tier
SHARE = {t: n / sum(POP.values()) for t, n in POP.items()}
QUALITY = dict(coherence=0.97, escaped=0.25)             # service floor for "ideal" answers


def split(n: int, share=SHARE) -> dict:
    c = {t: int(n * share[t]) for t in share}
    while sum(c.values()) < n:
        t = max(share, key=lambda t: n * share[t] - c[t])
        c[t] += 1
    return c


def inst(counts, **kw):
    return f.mean_measure(lambda rng: ("institutions", f.draw_agents(counts, rng)), n=SEEDS, **kw)


def base(workers, **kw):
    return f.mean_measure(lambda rng: ("baseline", f.baseline_org(workers, rng)), n=SEEDS, **kw)


def slim(m):
    keep = ("ideas_per_week", "lead_h", "coherence", "escaped_per_idea", "cost_per_idea", "utilisation")
    out = {k: round(m[k], 3) for k in keep}
    out["seat_waivers"] = round(m["drops_per_idea"].get("seat_rule_waived", 0.0), 3)
    out["busiest_role"] = max(m["role_util"], key=m["role_util"].get)
    out["busiest_util"] = round(m["role_util"][out["busiest_role"]], 3)
    out["longest_wait"] = max(m["wait_h"], key=m["wait_h"].get) if m["wait_h"] else "none"
    out["longest_wait_h"] = round(m["wait_h"].get(out["longest_wait"], 0.0), 2)
    out["wait_h"] = {k: round(v, 2) for k, v in m["wait_h"].items()}
    out["drops"] = {k: round(v, 3) for k, v in m["drops_per_idea"].items()}
    return out


def e1():
    rows = []
    print("\nE1 headcount scaling (tiers in population proportion)")
    print(f"  {'N':>3} {'mix':>9} | {'base i/wk':>9} {'lead':>5} {'coh':>5} {'esc':>5} {'$/idea':>6} {'busiest':>14} "
          f"| {'inst i/wk':>9} {'lead':>5} {'coh':>5} {'esc':>5} {'$/idea':>6} {'longest wait':>18}")
    for n in (3, 4, 6, 9, 12, 16, 20, 24, 32):
        wip = max(2, n)
        b = slim(base(split(n - 2), wip=wip))
        i = slim(inst(split(n), wip=wip))
        rows.append(dict(n=n, mix=split(n), baseline=b, institutions=i))
        mix = "/".join(str(split(n)[t]) for t in (1, 2, 3))
        print(f"  {n:>3} {mix:>9} | {b['ideas_per_week']:9.1f} {b['lead_h']:5.0f} {b['coherence']:5.2f} {b['escaped_per_idea']:5.2f} "
              f"{b['cost_per_idea']:6.1f} {b['busiest_role']:>9} {b['busiest_util']:.2f} | {i['ideas_per_week']:9.1f} {i['lead_h']:5.0f} "
              f"{i['coherence']:5.2f} {i['escaped_per_idea']:5.2f} {i['cost_per_idea']:6.1f} {i['longest_wait']:>10} {i['longest_wait_h']:5.1f}h")
    return rows


def e2():
    out = {}
    print("\nE2 tier mix (institutions); best mixes meeting the quality floor")
    for n in (6, 9, 12):
        grid = []
        for n1 in range(n + 1):
            for n2 in range(n + 1 - n1):
                n3 = n - n1 - n2
                m = slim(inst({1: n1, 2: n2, 3: n3}, wip=n))
                m["mix"] = [n1, n2, n3]
                grid.append(m)
        ok = [g for g in grid if g["coherence"] >= QUALITY["coherence"] and g["escaped_per_idea"] <= QUALITY["escaped"]]
        best_tp = max(ok, key=lambda g: g["ideas_per_week"]) if ok else None
        best_cost = min(ok, key=lambda g: g["cost_per_idea"]) if ok else None
        homog = {t: next(g for g in grid if g["mix"][t - 1] == n) for t in (1, 2, 3)}
        pop = next(g for g in grid if g["mix"] == [split(n)[1], split(n)[2], split(n)[3]])
        out[n] = dict(grid=grid, best_throughput=best_tp, best_cost=best_cost, homogeneous=homog, population=pop)
        print(f"  N={n}: {len(ok)}/{len(grid)} mixes meet the floor")
        for label, g in (("all top", homog[1]), ("all middle", homog[2]), ("all bottom", homog[3]),
                         ("population mix", pop), ("best throughput", best_tp), ("cheapest per idea", best_cost)):
            if g:
                print(f"    {label:<18} {'/'.join(map(str, g['mix'])):>8}  {g['ideas_per_week']:6.1f} ideas/wk  lead {g['lead_h']:5.0f} h  "
                      f"coherence {g['coherence']:.2f}  escaped {g['escaped_per_idea']:.2f}  ${g['cost_per_idea']:.1f}/idea")
    return out


def e3():
    n = 12
    counts = split(n)
    print(f"\nE3 institution sizing at N={n} ({'/'.join(str(counts[t]) for t in (1, 2, 3))})")
    rows = {}

    def run(label, **kw):
        kw.setdefault("wip", n)
        m = slim(inst(counts, **kw))
        rows[label] = m
        print(f"    {label:<22} {m['ideas_per_week']:6.1f} ideas/wk  lead {m['lead_h']:5.0f} h  coherence {m['coherence']:.3f}  "
              f"escaped {m['escaped_per_idea']:.2f}  ${m['cost_per_idea']:.1f}/idea")
    for k in (1, 2, 3, 4, 5):
        run(f"Inquiry K={k}", K=k)
    for d in (1, 2, 3):
        run(f"Planners D={d}", D=d)
    for r in (0, 1, 2):
        run(f"Council rounds={r}", council_rounds=r)
    run("No red team", redteam=False)
    run("No audit", audit=False)
    for w in (4, 8, 12, 18, 24):
        run(f"WIP limit={w}", wip=w)
    return rows


def dedicated_builder(n: int, plan: dict):
    """plan: institution -> number of seats; tiers assigned best-first to the most demanding."""
    order = ["planning", "council", "release", "court", "market", "inquiry"]   # most demanding first
    kinds = {"inquiry": {"inquiry"}, "council": {"critique", "synthesis"}, "planning": {"decompose", "reconcile", "redteam"},
             "market": {"card"}, "court": {"review", "audit"}, "release": {"release"}}

    def build(rng):
        agents = f.draw_agents(split(n), rng)
        agents.sort(key=lambda a: -a.cfg.ci)
        i = 0
        for inst_name in order:
            for _ in range(plan.get(inst_name, 0)):
                agents[i].roles = set(kinds[inst_name])
                i += 1
        for a in agents[i:]:
            a.roles = {"card"}
        return "institutions", agents
    return build


def e4():
    n = 12
    print(f"\nE4 shared pool vs dedicated seats (N={n})")
    rows = {}
    shared = slim(inst(split(n), wip=n))
    rows["shared pool"] = shared
    plans = {
        "dedicated A (1/1/2/6/1/1)": dict(inquiry=1, council=1, planning=2, market=6, court=1, release=1),
        "dedicated B (2/1/2/4/2/1)": dict(inquiry=2, council=1, planning=2, market=4, court=2, release=1),
        "dedicated C (1/1/1/7/1/1)": dict(inquiry=1, council=1, planning=1, market=7, court=1, release=1),
    }
    for label, plan in plans.items():
        rows[label] = slim(f.mean_measure(dedicated_builder(n, plan), n=SEEDS, wip=n))
    for label, m in rows.items():
        print(f"    {label:<28} {m['ideas_per_week']:6.1f} ideas/wk  lead {m['lead_h']:5.0f} h  coherence {m['coherence']:.3f}  "
              f"escaped {m['escaped_per_idea']:.2f}  util {m['utilisation']:.2f}  longest wait {m['longest_wait']} {m['longest_wait_h']:.1f} h")
    return rows


SENSITIVITY = {
    "baseline assumptions": {},
    "flatter skill curve (SLOPE 0.08)": {"SLOPE": 0.08},
    "steeper skill curve (SLOPE 0.18)": {"SLOPE": 0.18},
    "weak tests (TEST_CATCH 0.3)": {"TEST_CATCH": 0.3},
    "strong tests (TEST_CATCH 0.7)": {"TEST_CATCH": 0.7},
    "easy-heavy work (65/25/10)": {"CARD_MIX": {"easy": 0.65, "mid": 0.25, "hard": 0.10}},
    "hard-heavy work (25/35/40)": {"CARD_MIX": {"easy": 0.25, "mid": 0.35, "hard": 0.40}},
    "harder requirements (+5)": {"REQ_BASE": 55.0},
}


def apply(overrides):
    saved = {}
    for k, v in overrides.items():
        saved[k] = getattr(f, k)
        setattr(f, k, v)
    if "REQ_BASE" in overrides:
        saved["TASK_DIFF"] = dict(f.TASK_DIFF)
        rb = overrides["REQ_BASE"]
        f.TASK_DIFF.update(inquiry=rb, critique=rb + 5, decompose=rb + 8, redteam=rb + 10)
    return saved


def restore(saved):
    for k, v in saved.items():
        if k == "TASK_DIFF":
            f.TASK_DIFF.clear()
            f.TASK_DIFF.update(v)
        else:
            setattr(f, k, v)


def e5():
    print("\nE5 sensitivity (N=12, population mix): does the conclusion hold?")
    rows = {}
    for label, ov in SENSITIVITY.items():
        saved = apply(ov)
        try:
            b = slim(base(split(10), wip=12))
            i = slim(inst(split(12), wip=12))
            grid = []
            for n1 in range(0, 13, 2):
                for n2 in range(0, 13 - n1, 2):
                    m = slim(inst({1: n1, 2: n2, 3: 12 - n1 - n2}, wip=12))
                    m["mix"] = [n1, n2, 12 - n1 - n2]
                    grid.append(m)
            ok = [g for g in grid if g["coherence"] >= QUALITY["coherence"] and g["escaped_per_idea"] <= QUALITY["escaped"]]
            best = max(ok, key=lambda g: g["ideas_per_week"]) if ok else None
        finally:
            restore(saved)
        rows[label] = dict(baseline=b, institutions=i, best_mix=best["mix"] if best else None,
                           best_tp=best["ideas_per_week"] if best else None)
        print(f"    {label:<34} baseline {b['ideas_per_week']:5.1f} i/wk ({b['busiest_role']}) | institutions "
              f"{i['ideas_per_week']:5.1f} i/wk  ratio {i['ideas_per_week'] / b['ideas_per_week']:.2f}  coherence "
              f"{b['coherence']:.2f} -> {i['coherence']:.2f}  escaped {b['escaped_per_idea']:.2f} -> {i['escaped_per_idea']:.2f}  "
              f"best mix {best['mix'] if best else '-'}")
    return rows


if __name__ == "__main__":
    results = dict(e1=e1(), e2=e2(), e3=e3(), e4=e4(), e5=e5())
    json.dump(results, open(HERE / "results.json", "w"), indent=1, default=str)
    print("\nwrote results.json")
