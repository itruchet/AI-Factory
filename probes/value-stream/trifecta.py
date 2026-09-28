"""Quality, cost and speed together; hand-backs of unfit cards; human rounds (r12.7).

Isa's direction: optimise for the sweet spot of quality, cost and speed, not quality alone; institutions must hand
back cards that are not fit to build; human time is measured and counted, not excused.

Configuration throughout: institutions, elastic Scaler (R14 with held demand, 15-minute target), R17 at 25% coupling,
the seven-model menu.

  T1 readiness   R21: the puller checks a card is fit to build (10% of its hours) and hands back an insufficiently
                 specified card to Planning, against building it and failing (r12 behaviour: clarified after 3
                 failed attempts). Insufficient cards at the model's rate (base) and at 3x (poorly specified work).
  T2 trifecta    the Scaler prices a success as ($ + time value x hours) / pass chance; time value swept.
  T3 latency     time to first token per call added to every task [ILLUSTRATIVE assumption: no measured latency
                 yet]: max-effort reasoning 15-20 s, xhigh 10 s, high 5 s, non-reasoning 1 s; 40 calls per hour.
  T4 human       Isa sends intent or plan back for another round with chance 0 / 25% / 50%.

Run: python3 probes/value-stream/trifecta.py   (about 8 minutes on 4 cores)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import elastic as e
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 12
SEVEN = e.SIX + [e.TERRA]
LATENCY = {e.SIX[0]: 20.0, e.TERRA: 20.0, "DeepSeek V4.1 Flash (Reasoning, Max Effort)": 15.0, "GPT-6 Luna (max)": 15.0,
           "Muse Spark 1.3 (xhigh)": 10.0, "Gemini 3.8 Flash (high)": 5.0, "Ling 3.0 Flash": 1.0}
BASE = dict(READY_CHECK=False, AMBIG_SCALE=0.30, TIME_VALUE=0.0, TTFT_S={}, CALLS_PER_H=0.0, HUMAN_RETURN_P=0.0)


def job(args):
    demand, params, seed = args
    saved = {k: getattr(v, k) for k in list(BASE) + ["COUPLING"]}
    try:
        for k, x in {**BASE, **params, "COUPLING": 0.25}.items():
            setattr(v, k, x)
        seats, sc = e.build("elastic", SEVEN, None)
        sc.held_weight, sc.drain_h = 1.0, 0.25
        sim = v.Sim(v.Org("institutions"), seats, seed=seed, wip=6, demand=e.make_demand(e.DEMANDS[demand]), scaler=sc)
        m = v.measure(sim.run())
        m["lat_h"] = sum(s.lat for s in sim.seats + sim.retired) / ((sim.horizon - sim.warmup) / 168)
        return m
    finally:
        for k, x in saved.items():
            setattr(v, k, x)


def cells():
    out = []
    for d in ("steady", "mixed"):
        for amb in (0.30, 0.90):
            for ready in (False, True):
                out.append(("T1", d, f"insufficient cards x{amb / 0.30:.0f}, {'hand back (R21)' if ready else 'build and fail (r12)'}",
                            dict(AMBIG_SCALE=amb, READY_CHECK=ready)))
        for tv in (0.0, 0.5, 2.0, 5.0, 20.0):
            out.append(("T2", d, f"time value ${tv:g}/h", dict(READY_CHECK=True, TIME_VALUE=tv)))
        for lat in (False, True):
            for tv in (0.0, 2.0):
                out.append(("T3", d, f"latency {'on' if lat else 'off'}, time value ${tv:g}/h",
                            dict(READY_CHECK=True, TIME_VALUE=tv, TTFT_S=LATENCY if lat else {}, CALLS_PER_H=40.0 if lat else 0.0)))
        for hr in (0.0, 0.25, 0.5):
            out.append(("T4", d, f"Isa sends back {hr:.0%}", dict(READY_CHECK=True, HUMAN_RETURN_P=hr)))
    return out


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    cs = cells()
    jobs = [(d, p, k) for _, d, _, p in cs for k in range(SEEDS)]
    with Pool() as pool:
        res = pool.map(job, jobs, chunksize=1)
    say("QUALITY, COST AND SPEED (institutions, elastic, R17 at 25% coupling, the seven-model menu; lead = median/90th h)")
    last = None
    for i, (t, d, lab, _) in enumerate(cs):
        m = v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS])
        m["lat_h"] = sum(r["lat_h"] for r in res[i * SEEDS:(i + 1) * SEEDS]) / SEEDS
        if (t, d) != last:
            say(f"\n[{t} / {d}]")
            last = (t, d)
        dr = m["drops"]
        say(f"  {lab:<44} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h  "
            f"CFR {m['cfr']:4.0%}  ${m['usd_clean']:5.1f}/clean  hand-backs {dr.get('handback', 0):4.2f}/idea  "
            f"failed builds {dr.get('test_fail', 0):4.2f}/idea  human returns {dr.get('human_return', 0):4.2f}/idea  "
            f"latency {m['lat_h']:5.0f} h/wk")
        out.setdefault(t, {}).setdefault(d, {})[lab] = {k: x for k, x in m.items() if k != "waits"}
    (HERE / "trifecta_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "trifecta.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
