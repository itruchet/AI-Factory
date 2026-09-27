"""Dependency graphs (r12.2): the value-stream model re-run with requirements that depend on each other.

Each ordered pair of an idea's requirements (p < r) is an edge "r needs p" with
probability COUPLING (0.25 as in the cross-check model; 0.10 and 0.65 as
sensitivities). What changes when requirements depend on each other:
  - a dependent card may start only when its prerequisites are ready:
        accepted  R17: reviewed and merged
        built     tests passed, not yet reviewed (the usual practice)
        none      ignore the graph (r12 behaviour; the builder sees only the plan)
    and a whole-idea review barrier can hold all review until every card is built;
  - a card built against a prerequisite version that later changes is stale and
    must be rebuilt (invalidation cascade);
  - an interface fault may arise at each edge a card builds across: 0.10 x
    (1.25 - 0.5 x pass) x 1 / 1.5 / 3 for reviewed / unreviewed / absent upstream
    work; review catches it at 0.95 x skill when the upstream was reviewed, 0.30
    x skill when not; CI at 0.30;
  - "useful" counts a requirement only if it and all its prerequisites are right.

D1  gating policies for the institutions: coupling 0.10 / 0.25 / 0.65, the six
    and the 12-seat population
D2  every organisation re-run at coupling 0.25 (institutions, pools and the
    searched designs use R17; the others build on built work)
D3  fixed seats vs elastic instances re-run at coupling 0.25, every demand pattern
D4  the graph together with family blind spots (18%)
D5  which gate: R17, a hybrid with waiting limits, unreviewed, contract-first; interface-fault sensitivity

Run: python3 probes/value-stream/deps.py   (about 30 minutes on 4 cores)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import elastic as e
import orgs as o
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 6
FOUND = json.load(open(HERE / "orgs.json"))["found"]
POLICIES = {"R17: build on reviewed work": ("accepted", False), "build on unreviewed work": ("built", False),
            "whole-idea review barrier": ("built", True), "ignore the graph (r12)": ("none", False)}


def with_globals(knobs, fn):
    saved = {k: getattr(v, k) for k in knobs}
    for k, x in knobs.items():
        setattr(v, k, x)
    try:
        return fn()
    finally:
        for k, x in saved.items():
            setattr(v, k, x)


def org_job(args):
    knobs, spec, rname, scenario, gate, barrier, seed = args

    def go():
        snap = o.set_scenario(scenario)
        try:
            seats = o.roster(rname, seed)
            org = o.spec_org(spec, seats)
            if gate is not None:
                org.dep_gate, org.review_barrier = gate, barrier
            return v.measure(v.Sim(org, seats, seed=seed, wip=len(seats)).run())
        finally:
            o.restore(snap)
    return with_globals(knobs, go)


def el_job(args):
    knobs, dname, kind, names, arg, seed = args
    return with_globals(knobs, lambda: e.job((dname, kind, names, arg, seed, None)))


def mean(pool, fn, jobs):
    res = pool.map(fn, jobs, chunksize=1)
    return [v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS]) for i in range(len(jobs) // SEEDS)]


def row(label, m, ref=None):
    usd = f"  ${m['usd_clean']:4.0f}/clean" if m["usd_week"] == m["usd_week"] else ""
    rel = f"  ({m['clean'] / ref:4.0%})" if ref else ""
    return (f"  {label:<40} {m['clean']:5.1f} clean  {m['useful']:5.1f} useful ({m['ideas']:5.1f} live)  CFR {m['cfr']:4.0%}  "
            f"lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h{usd}  stale {m['drops'].get('stale_rework', 0):4.1f}/idea{rel}")


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    with Pool() as pool:
        say("D1  GATING POLICIES for the institutions (clean = live, full intent, no escaped defect; useful = requirement-equivalents right with their prerequisites)")
        for rname in ("best six", "population 12"):
            for c in (0.10, 0.25, 0.65):
                jobs = [({"COUPLING": c}, ("design", "institutions"), rname, "base", g, b, k)
                        for g, b in POLICIES.values() for k in range(SEEDS)]
                res = mean(pool, org_job, jobs)
                say(f"\n[{rname} / coupling {c}]")
                for lab, m in zip(POLICIES, res):
                    say(row(lab, m, res[0]["clean"]))
                    out.setdefault("D1", {}).setdefault(rname, {}).setdefault(str(c), {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nD2  ORGANISATIONS re-run with dependencies (coupling 0.25); share = of the institutions' clean ideas")
        for rname in ("best six", "population 12"):
            specs = [("design", d) for d in o.DESIGNS if d != "functional roles"] + [("functional", tuple(FOUND[rname]["functional"])),
                                                                                      ("search", FOUND[rname]["clean"])]
            labels = [s[1] if s[0] == "design" else "functional roles" if s[0] == "functional" else "searched (clean)" for s in specs]
            for sc in ("base", "harder work", "heavy contention"):
                jobs = [({"COUPLING": 0.25}, sp, rname, sc, None, False, k) for sp in specs for k in range(SEEDS)]
                res = mean(pool, org_job, jobs)
                ref = res[labels.index("institutions")]["clean"]
                say(f"\n[{rname} / {sc}]")
                for lab, m in zip(labels, res):
                    say(row(lab, m, ref))
                    out.setdefault("D2", {}).setdefault(rname, {}).setdefault(sc, {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nD3  FIXED vs ELASTIC re-run with dependencies (coupling 0.25)")
        cfgs = {"fixed six": ("fixed", e.SIX, 1), "fixed 24": ("fixed", e.SIX, 4), "elastic (six models, rules)": ("elastic", e.SIX, None)}
        for d in ("steady", "bursty", "growth", "mixed", "surge", "harder"):
            jobs = [({"COUPLING": 0.25}, d, *spec, k) for spec in cfgs.values() for k in range(SEEDS)]
            res = mean(pool, el_job, jobs)
            say(f"\n[{d}]")
            for lab, m in zip(cfgs, res):
                say(row(lab, m) + f"  backlog {m['backlog']:4.0f}")
                out.setdefault("D3", {}).setdefault(d, {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nD4  DEPENDENCIES (0.25) WITH FAMILY BLIND SPOTS (18%), the six")
        items = [("institutions, R17", ("design", "institutions"), "accepted", False),
                 ("institutions, unreviewed", ("design", "institutions"), "built", False),
                 ("institutions, barrier", ("design", "institutions"), "built", True),
                 ("peer", ("design", "peer"), None, False), ("no organisation (solo)", ("design", "no organisation (solo)"), None, False),
                 ("Director-Worker-Checker", ("design", "Director-Worker-Checker"), None, False)]
        jobs = [({"COUPLING": 0.25, "FAMILY_BLIND_P": 0.18}, sp, "best six", "base", g, b, k) for _, sp, g, b in items for k in range(SEEDS)]
        res = mean(pool, org_job, jobs)
        for (lab, *_), m in zip(items, res):
            say(row(lab, m, res[0]["clean"]))
            out.setdefault("D4", {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nD5  WHICH GATE, AND HOW SENSITIVE: contract-first (ignore the graph) depends on how often building against")
        say("    only the plan breaks an interface (x3 base; x6 sensitivity). Hybrid = R17, but after 2 h build on unreviewed")
        say("    work, after 4 h on the plan's contract.")
        pol = {"R17: reviewed": ("accepted", False), "hybrid (R17 + waiting limits)": ("hybrid", False),
               "unreviewed": ("built", False), "contract-first (ignore the graph)": ("none", False)}
        for rname in ("best six", "population 12"):
            for c in (0.25, 0.65):
                for mult in (3.0, 6.0):
                    knobs = {"COUPLING": c, "IFACE_MULT": {"accepted": 1.0, "built": 1.5, "absent": mult}}
                    jobs = [(knobs, ("design", "institutions"), rname, "base", g, b, k) for g, b in pol.values() for k in range(SEEDS)]
                    res = mean(pool, org_job, jobs)
                    say(f"\n[{rname} / coupling {c} / contract-only interface faults x{mult:.0f}]")
                    for lab, m in zip(pol, res):
                        say(row(lab, m, res[0]["clean"]))
                        out.setdefault("D5", {}).setdefault(rname, {}).setdefault(f"{c}/{mult}", {})[lab] = {k: x for k, x in m.items() if k != "waits"}

    (HERE / "deps_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "deps.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
