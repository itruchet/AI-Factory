"""Institutions against the searched design (r12.3): what the search found, and whether it holds.

The searched designs (orgs.py, stored in orgs.json) are the institutions plus a
few step affinities, found by coordinate search on one roster and one scenario:
  the six           design by fast/mid models only (keeps the anchor free), audit by fast
  population 12     plan by the anchors only; discover, security by fast; challenge and
                    QA by anchor + fast; review and audit by fast + mid; merge by mid
The r12 table reported them on the same random draws they were tuned on. This
probe asks five questions the search did not:

  T1  in-sample vs out-of-sample: new random draws (and, for the population,
      new rosters) the search never saw; five scenarios
  T2  transfer: each searched design applied to the other roster
  T3  vendor outage: the anchor models unavailable for the whole run; pools set
      for them are not re-labelled (R13 lifts a seat rule after 16 h)
  T4  a new model enters: Claude Fable 5.1 joins as an extra seat with no pool
      label (the institutions admit it by evidence at once)
  T5  elastic capacity: the same organisations with the Scaler
  (all also with dependencies, coupling 0.25, for T1)

And one rule-based alternative, stated before running:
  adaptive institutions  the institutions with a higher licence floor (0.8) on
      the steps whose output shapes a whole idea: design, plan, plan red-team,
      security review, acceptance test, release. It uses evidence, so it
      re-sorts itself when the roster changes; no pools.

Run: python3 probes/value-stream/searched.py   (about 30 minutes on 4 cores)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import elastic as e
import orgs as o
import vs_sim as v

HERE = Path(__file__).parent
FOUND = json.load(open(HERE / "orgs.json"))["found"]
SEEDS = 8
IN_SAMPLE = range(0, 4)          # the search's own seeds
OUT_SAMPLE = range(40, 48)       # never seen by the search (new rosters for the population)
HIGH_FANOUT = {"design": 0.8, "plan": 0.8, "plan_check": 0.8, "security": 0.8, "qa": 0.8, "release": 0.8}
FABLE = "Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback)"

DESIGNS = {
    "institutions": ("design", "institutions"),
    "adaptive institutions": ("adaptive", None),
    "searched (six)": ("search", FOUND["best six"]["clean"]),
    "searched (population 12)": ("search", FOUND["population 12"]["clean"]),
}


def build_org(spec, seats):
    kind, arg = spec
    if kind == "adaptive":
        org = v.Org("adaptive institutions")
        org.step_floor = dict(HIGH_FANOUT)
        return org
    return o.spec_org(spec, seats)


def seats_for(rname, seed, variant):
    seats = o.roster(rname, seed)
    if variant == "outage":                           # the anchor pool's models are down; nobody re-labels
        seats = [s for s in seats if s.cls != "A"]
    elif variant == "new model":                      # a stronger model joins, unlabelled
        cfg = v.s6.roster([FABLE])[0].cfg
        seats.append(v.Seat(cfg, len(seats), cls="N"))
    for i, s in enumerate(seats):
        s.idx = i
    return seats


def job(args):
    dname, rname, scenario, variant, coupling, seed = args
    saved = v.COUPLING
    v.COUPLING = coupling
    snap = o.set_scenario(scenario)
    try:
        seats = seats_for(rname, seed, variant)
        org = build_org(DESIGNS[dname], seats)
        return v.measure(v.Sim(org, seats, seed=seed, wip=len(seats)).run())
    finally:
        o.restore(snap)
        v.COUPLING = saved


def el_job(args):
    dname, demand, seed = args
    seats, sc = e.build("elastic", e.SIX, None)
    sc.held_weight, sc.drain_h = 1.0, 0.25
    base = o.roster("best six", 0)
    org = build_org(DESIGNS[dname], base)             # pools refer to the six's classes; instances inherit them
    if org.pools:
        cls_of = {s.cfg.name: s.cls for s in base}
        sc.cls = cls_of
        org.pools = {st: None for st in org.pools}    # re-derived per instance below
        org._pool_classes = {st: cls for st, cls in DESIGNS[dname][1]["pools"].items() if set(cls) != set("AFM")}
    sim = ElasticSim(org, seats, seed=seed, wip=6, demand=e.make_demand(e.DEMANDS[demand]), scaler=sc)
    return v.measure(sim.run())


class ElasticSim(v.Sim):
    """Pools by class for instances that come and go: a seat may take a pooled step if its class is in the pool."""
    def permitted(self, s, task):
        pc = getattr(self.org, "_pool_classes", None)
        if pc and task.step in pc and s.cls not in pc[task.step]:
            return False
        return super().permitted(s, task)

    def eligible(self, s, task):
        pc = getattr(self.org, "_pool_classes", None)
        if pc and task.step in pc and s.cls not in pc[task.step] and self.t - task.born < 2 * v.ORPHAN_H:
            return False
        saved, self.org.pools = self.org.pools, {}
        try:
            return super().eligible(s, task)
        finally:
            self.org.pools = saved


def mean(pool, fn, jobs, n):
    res = pool.map(fn, jobs, chunksize=1)
    return [v.mean_measures(res[i * n:(i + 1) * n]) for i in range(len(jobs) // n)]


def row(label, m, ref):
    usd = f"  ${m['usd_clean']:4.0f}/clean" if m["usd_week"] == m["usd_week"] else ""
    return (f"  {label:<28} {m['clean']:5.1f} clean ({m['clean'] / ref:4.0%})  {m['ideas']:5.1f} live  CFR {m['cfr']:4.0%}  "
            f"lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h{usd}")


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    names = list(DESIGNS)
    with Pool() as pool:
        say("T1  IN-SAMPLE vs OUT-OF-SAMPLE (share = of the institutions on the same draws)")
        for rname in ("best six", "population 12"):
            for coupling in (0.0, 0.25):
                for label, seeds, scen in (("in-sample (search seeds)", IN_SAMPLE, ["base"]),
                                           ("out-of-sample", OUT_SAMPLE, ["base", "harder work", "security-heavy", "weak tests", "heavy contention"])):
                    for sc in scen:
                        n = len(seeds)
                        jobs = [(d, rname, sc, "normal", coupling, k) for d in names for k in seeds]
                        res = mean(pool, job, jobs, n)
                        ref = res[0]["clean"]
                        say(f"\n[{rname} / coupling {coupling} / {label} / {sc}]")
                        for d, m in zip(names, res):
                            say(row(d, m, ref))
                            out.setdefault("T1", {}).setdefault(f"{rname}|{coupling}|{label}|{sc}", {})[d] = {k: x for k, x in m.items() if k != "waits"}

        for test, variant in (("T3  VENDOR OUTAGE: the anchor models unavailable", "outage"),
                              ("T4  A NEW MODEL ENTERS: Claude Fable 5.1 joins, unlabelled", "new model")):
            say(f"\n{test}")
            for rname in ("best six", "population 12"):
                for vv in ("normal", variant):
                    jobs = [(d, rname, "base", vv, 0.0, k) for d in names for k in OUT_SAMPLE]
                    res = mean(pool, job, jobs, len(OUT_SAMPLE))
                    ref = res[0]["clean"]
                    say(f"\n[{rname} / {vv}]")
                    for d, m in zip(names, res):
                        say(row(d, m, ref))
                        out.setdefault(test.split()[0], {}).setdefault(f"{rname}|{vv}", {})[d] = {k: x for k, x in m.items() if k != "waits"}

        say("\nT2  TRANSFER is inside T1: 'searched (population 12)' on the six, 'searched (six)' on the population")

        say("\nT5  ELASTIC: the six models as instances (Scaler with held demand, 15-minute target); coupling 0")
        for d in ("steady", "mixed", "harder", "surge"):
            jobs = [(dn, d, k) for dn in names[:3] for k in range(6)]
            res = mean(pool, el_job, jobs, 6)
            ref = res[0]["clean"]
            say(f"\n[{d}]")
            for dn, m in zip(names[:3], res):
                say(row(dn, m, ref))
                out.setdefault("T5", {}).setdefault(d, {})[dn] = {k: x for k, x in m.items() if k != "waits"}

    (HERE / "searched_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "searched.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
