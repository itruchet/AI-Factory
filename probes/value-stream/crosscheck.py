"""Cross-check (r12.1): the second simulation's mechanisms, added to this model.

Isa supplied an independent simulation (probes/crosscheck/external/, built with
another assistant). It models mechanisms this model lacked. Each is added here
as a switch, off by default, and tested on our organisations:

  C1  blind spots shared within a model family: each requirement x family pair
      is blind with probability b; that family's pass and catch chances on the
      requirement are x0.4 at every step (their definition). b = 0, 5, 18, 45%.
      Also: more seats of the same models; review barred within a family.
  C2  blind spots shared by every family (no LLM check can see the defect or the
      requirement; tests, CI and smoke tests still can). b = 0, 5, 18%.
  C3  packets: k requirements per build invocation, with and without their
      context penalty 2.5 x (k - 1)^1.2 skill points.
  C4  Scaler aggressiveness: their result was that a work-conserving pool beats
      a conservative demand predictor. Our Scaler targets a 2-hour drain; sweep
      0.1 to 2 hours under bursty and surge demand.

Run: python3 probes/value-stream/crosscheck.py   (about 15 minutes on 4 cores)
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


def fixed(copies):
    base = o.roster("best six", 0)
    seats = []
    for s in base:
        for _ in range(copies):
            seats.append(v.Seat(s.cfg, len(seats), cls=s.cls))
    return seats


def job(args):
    kind, knobs, spec, seed = args
    saved = {k: getattr(v, k) for k in knobs}
    for k, x in knobs.items():
        setattr(v, k, x)
    try:
        if kind == "org":
            design, copies, by_family, packet = spec
            seats = fixed(copies)
            org = o.DESIGNS[design](seats)
            org.by_family = by_family
            sim = v.Sim(org, seats, seed=seed, wip=len(seats), packet=packet)
        else:                                               # elastic
            demand, drain = spec
            seats, sc = e.build("elastic", e.SIX, None)
            sc.drain_h = drain
            sim = v.Sim(v.Org("institutions"), seats, seed=seed, wip=6, demand=e.make_demand(e.DEMANDS[demand]), scaler=sc)
        return v.measure(sim.run())
    finally:
        for k, x in saved.items():
            setattr(v, k, x)


def evaluate(pool, items):
    jobs = [(kind, knobs, spec, k) for kind, knobs, spec in items for k in range(SEEDS)]
    res = pool.map(job, jobs, chunksize=1)
    return [v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS]) for i in range(len(items))]


def row(label, m):
    usd = f"  ${m['usd_clean']:5.0f}/clean" if m["usd_week"] == m["usd_week"] else ""
    return (f"  {label:<44} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  CFR {m['cfr']:4.0%}  intent {m['coherence']:.2f}  "
            f"lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h{usd}")


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    designs = ["institutions", "peer", "no organisation (solo)", "Director-Worker-Checker"]
    with Pool() as pool:
        say("C1  BLIND SPOTS SHARED WITHIN A MODEL FAMILY (the six; each requirement x family blind with probability b)")
        for b in (0.0, 0.05, 0.18, 0.45):
            items = [("org", {"FAMILY_BLIND_P": b}, (d, 1, False, 0), None) for d in designs]
            items += [("org", {"FAMILY_BLIND_P": b}, ("institutions", c, False, 0), None) for c in (2, 4)]
            items += [("org", {"FAMILY_BLIND_P": b}, ("institutions", 1, True, 0), None)]
            items = [(k, kn, sp) for k, kn, sp, _ in items]
            res = evaluate(pool, items)
            labels = designs + ["institutions, 12 seats (2 per model)", "institutions, 24 seats (4 per model)",
                                "institutions, review barred within family"]
            say(f"\n[b = {b:.0%}]")
            for lab, m in zip(labels, res):
                say(row(lab, m) + f"  ({m['clean'] / res[0]['clean']:4.0%} of institutions)")
                out.setdefault("C1", {}).setdefault(str(b), {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nC2  BLIND SPOTS SHARED BY EVERY FAMILY (invisible to every LLM check; tests, CI and smoke still see defects)")
        for b in (0.0, 0.05, 0.18):
            res = evaluate(pool, [("org", {"BLIND_P": b}, (d, 1, False, 0)) for d in designs])
            say(f"\n[b = {b:.0%}]")
            for lab, m in zip(designs, res):
                say(row(lab, m))
                out.setdefault("C2", {}).setdefault(str(b), {})[lab] = {k: x for k, x in m.items() if k != "waits"}

        say("\nC3  PACKETS: requirements per build invocation (institutions, the six); unit = r12 cards")
        for cp in (0.0, 2.5):
            res = evaluate(pool, [("org", {"CONTEXT_PENALTY": cp}, ("institutions", 1, False, k)) for k in (0, 1, 2, 4, 8)])
            say(f"\n[context penalty {cp} x (k-1)^1.2]")
            for k, m in zip(("unit", 1, 2, 4, 8), res):
                say(row(f"{k} requirement(s) per invocation" if k != "unit" else "unit cards (r12)", m))
                out.setdefault("C3", {}).setdefault(str(cp), {})[str(k)] = {kk: x for kk, x in m.items() if kk != "waits"}

        say("\nC4  SCALER AGGRESSIVENESS: target drain time (hours) for queued work; smaller = closer to work-conserving")
        for d in ("bursty", "surge", "mixed"):
            res = evaluate(pool, [("elastic", {}, (d, h)) for h in (0.1, 0.25, 0.5, 1.0, 2.0)])
            say(f"\n[{d}]")
            for h, m in zip((0.1, 0.25, 0.5, 1.0, 2.0), res):
                say(row(f"drain {h} h", m) + f"  peak {m['peak']:3.0f}  seat-h {m['seat_h']:5.0f}")
                out.setdefault("C4", {}).setdefault(d, {})[str(h)] = {k: x for k, x in m.items() if k != "waits"}

    (HERE / "crosscheck_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "crosscheck.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
