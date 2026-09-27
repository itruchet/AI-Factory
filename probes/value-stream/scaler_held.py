"""The Scaler counts cards held behind prerequisites as demand (r12.3).

With dependencies (dependencies.md), elastic instances trailed 24 fixed seats by
2-4 h of median lead time: the Scaler started instances only for queued work,
and cards waiting on a prerequisite's review were invisible to it until
released. Here a held card counts as build demand for the model that would take
it. Also tested with the work-conserving target the cross-check adopted (clear
queued work within 15 minutes rather than 2 hours).

  r12.2 Scaler          held cards not counted, 2-hour target
  + held demand         held cards counted (weight 1), 2-hour target
  + held, 15-minute     held cards counted, 15-minute target (R14 as amended)

Run: python3 probes/value-stream/scaler_held.py   (about 15 minutes on 4 cores)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import elastic as e
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 6
CONFIGS = {"fixed six": ("fixed", 1, None), "fixed 24": ("fixed", 4, None),
           "elastic, r12.2 Scaler": ("elastic", 0.0, 2.0),
           "elastic + held demand": ("elastic", 1.0, 2.0),
           "elastic + held demand, 15-min target": ("elastic", 1.0, 0.25)}


def job(args):
    coupling, dname, label, seed = args
    kind, a, b = CONFIGS[label]
    saved = v.COUPLING
    v.COUPLING = coupling
    try:
        if kind == "fixed":
            seats, sc = e.build("fixed", e.SIX, a)
        else:
            seats, sc = e.build("elastic", e.SIX, None)
            sc.held_weight, sc.drain_h = a, b
        sim = v.Sim(v.Org("institutions"), seats, seed=seed, wip=6, demand=e.make_demand(e.DEMANDS[dname]), scaler=sc)
        return v.measure(sim.run())
    finally:
        v.COUPLING = saved


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    say("SCALER COUNTS HELD CARDS AS DEMAND (institutions, R17, the six models; lead = median/90th percentile)")
    with Pool() as pool:
        for coupling, demands in ((0.25, ("steady", "bursty", "growth", "mixed", "surge", "harder")),
                                  (0.65, ("steady", "surge", "harder"))):
            for d in demands:
                jobs = [(coupling, d, lab, k) for lab in CONFIGS for k in range(SEEDS)]
                res = pool.map(job, jobs, chunksize=1)
                ms = [v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS]) for i in range(len(CONFIGS))]
                say(f"\n[coupling {coupling} / {d}]")
                for lab, m in zip(CONFIGS, ms):
                    say(f"  {lab:<38} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h  "
                        f"CFR {m['cfr']:4.0%}  ${m['usd_clean']:4.0f}/clean  peak {m['peak']:3.0f}  seat-h {m['seat_h']:5.0f}  "
                        f"backlog {m['backlog']:4.0f}")
                    out.setdefault(str(coupling), {}).setdefault(d, {})[lab] = {k: x for k, x in m.items() if k != "waits"}
    (HERE / "scaler_held_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "scaler_held.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
