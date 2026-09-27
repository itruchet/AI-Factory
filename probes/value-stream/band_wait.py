"""Why elastic trails 24 fixed seats by 2-3 h: the cost-band wait (r12.3).

Rule 6 of the Scaler (cost-band pull) lets a task wait up to BAND_WAIT_H for a
cheaper qualified model before a dearer one may take it. With dependencies and
held demand counted, this sweeps that wait: 1 h (r12), 15 minutes, none.

Run: python3 probes/value-stream/band_wait.py   (about 5 minutes on 4 cores)
"""

from multiprocessing import Pool
from pathlib import Path

import elastic as e
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 6


def job(args):
    d, bw, k = args
    v.COUPLING = 0.25
    seats, sc = e.build("elastic", e.SIX, None)
    sc.held_weight, sc.band_wait_h = 1.0, bw
    return v.measure(v.Sim(v.Org("institutions"), seats, seed=k, wip=6, demand=e.make_demand(e.DEMANDS[d]), scaler=sc).run())


def main():
    lines = ["COST-BAND WAIT (elastic, the six models, coupling 0.25, held demand counted; lead = median/90th percentile)"]
    with Pool() as p:
        for d in ("steady", "mixed", "harder", "surge"):
            lines.append(f"\n[{d}]")
            for bw in (1.0, 0.25, 0.0):
                m = v.mean_measures(p.map(job, [(d, bw, k) for k in range(SEEDS)]))
                lines.append(f"  wait {bw:4.2f} h   {m['clean']:5.1f} clean  lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h  CFR {m['cfr']:4.0%}  "
                             f"${m['usd_clean']:4.0f}/clean")
                print(lines[-1], flush=True)
    (HERE / "band_wait_results.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
