"""Recorded behaviour as the oracle, and the Council against a single model (r12.12).

Isa's direction (5 Oct 2026): build AR-20 with option A. The regression set is recorded live use, never a lab set.

Configuration throughout: institutions, elastic Scaler (R14 with held demand, 15-minute target, time value $0.5 an
hour), R21 hand-backs, R17 at 25% coupling, the seven-model menu.

  P  replay      R29: at merge, recorded live use is replayed against the old and the new version. A logic,
                 integration or interface defect that changes replayed behaviour is caught at 25% or 50% (coverage
                 x detection) [assumption: no measured coverage yet], including defects in blind spots shared by every
                 family, because the oracle is past behaviour, not a model. Replay is compute, not model time. Swept
                 against blind spots (none; 18% within a family; 18% shared by every family) and against R26
                 challenge tests.
  C  council     X24: framing by the institutions (two Inquiry analysts, one Council round) against a single model
                 framing alone (one analyst, no Council round), with and without family blind spots.

The model has no regressions apart from defects: every defect a card carries is treated as reachable by replay at the
swept rate. New behaviour with no recordings yet is the reason the rate is well below 1.

Run: python3 probes/value-stream/replay.py   (about 12 minutes on 4 cores)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import elastic as e
import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 8
SEVEN = e.SIX + [e.TERRA]
BASE = dict(READY_CHECK=True, TIME_VALUE=0.5, COUPLING=0.25, BLIND_P=0.0, FAMILY_BLIND_P=0.0, CHALLENGE_TESTS=False,
            BLIND_TEST_CATCH=0.0, REPLAY_CATCH=0.0)
BLIND = {"no blind spots": {}, "family blind spots 18%": dict(FAMILY_BLIND_P=0.18),
         "all-family blind spots 18%": dict(BLIND_P=0.18)}
CHECKS = {"review only (r12.11)": {}, "challenge tests (R26)": dict(CHALLENGE_TESTS=True),
          "replay 25%": dict(REPLAY_CATCH=0.25), "replay 50%": dict(REPLAY_CATCH=0.50)}
FRAMING = {"institutions (2 analysts, 1 Council round)": {}, "single model (1 analyst, no Council)": dict(K=1, challenge=0)}


def job(args):
    demand, params, org, seed = args
    saved = {k: getattr(v, k) for k in BASE}
    try:
        for k, x in {**BASE, **params}.items():
            setattr(v, k, x)
        seats, sc = e.build("elastic", SEVEN, None)
        sc.held_weight, sc.drain_h = 1.0, 0.25
        sim = v.Sim(v.Org("institutions", **org), seats, seed=seed, wip=6, demand=e.make_demand(demand), scaler=sc)
        return v.measure(sim.run())
    finally:
        for k, x in saved.items():
            setattr(v, k, x)


def cells():
    out = []
    for d in ("steady", "mixed"):
        for b, bp in BLIND.items():
            for c, cp in CHECKS.items():
                out.append(("P", f"{d} / {b}", c, e.DEMANDS[d], {**bp, **cp}, {}))
    for d in ("steady", "mixed"):
        for b in ("no blind spots", "family blind spots 18%"):
            for f, fp in FRAMING.items():
                out.append(("C", f"{d} / {b}", f, e.DEMANDS[d], BLIND[b], fp))
    return out


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    cs = cells()
    jobs = [(d, p, o, k) for _, _, _, d, p, o in cs for k in range(SEEDS)]
    with Pool() as pool:
        res = pool.map(job, jobs, chunksize=1)
    say("RECORDED BEHAVIOUR AS THE ORACLE; THE COUNCIL AGAINST A SINGLE MODEL (institutions, elastic, R17 at 25% "
        "coupling, R21, time value $0.5/h, the seven-model menu; lead = median/90th h)")
    last = None
    for i, (t, grp, lab, _, _, _) in enumerate(cs):
        m = v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS])
        if (t, grp) != last:
            say(f"\n[{t} / {grp}]")
            last = (t, grp)
        dr = m["drops"]
        say(f"  {lab:<44} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  lead {m['lead']:4.0f}/{m['lead_p90']:4.0f} h  "
            f"CFR {m['cfr']:4.0%}  escaped {m['escaped']:4.2f}/idea  coherence {m['coherence']:5.1%}  "
            f"${m['usd_clean']:6.1f}/clean  replay catches {dr.get('replay_fail', 0):4.2f}/idea  "
            f"challenge catches {dr.get('challenge_fail', 0):4.2f}/idea")
        out.setdefault(t, {}).setdefault(grp, {})[lab] = {k: x for k, x in m.items() if k != "waits"}
    (HERE / "replay_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "replay.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
