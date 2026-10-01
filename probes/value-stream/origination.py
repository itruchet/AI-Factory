"""Edge-case tests, self-originated ideas and the ratification envelope (r12.11).

Isa's direction (1 Oct 2026): no ninth stage, but the Factory must originate its own ideas; the extra ratification
load is a problem to solve, not a reason to wait.

Configuration throughout: institutions, elastic Scaler (R14 with held demand, 15-minute target, time value $0.5 an
hour), R21 hand-backs, R17 at 25% coupling, the seven-model menu.

  E  edge cases  R26 challenge tests: at first review, a model of another family writes edge-case tests from the
                 contract alone (30% of the card's hours). Swept against blind spots: none; within one family (18% of
                 requirement x family pairs, the cross-check reference); shared by every family (18% of defects).
                 A defect in an all-family blind spot is invisible to every LLM check; mechanical exploration
                 (property-based, boundary and fuzz inputs) finds it at 0 or 25% [assumption: no measured rate].
  O  origination Self-originated ideas add demand on top of Isa's 25 briefs a week: +0, +25, +50 a week.
     and R28     Isa's attention is a budget: 5 hours a week [ILLUSTRATIVE], 5 minutes per ratification (intent and
                 plan, about 10 minutes an idea). Envelope: the share of ideas ratified by rule at once, with 10% of
                 them sampled by Isa afterwards. Unlimited Isa (a fixed 4 h + 2 h turnaround, r12.7) is the reference.

The model cannot value ideas: an originated idea counts like a briefed one. It tests whether the Factory and Isa's
attention can carry the extra flow, not whether the ideas are worth it. That is X22, judged on live value (M07).

Run: python3 probes/value-stream/origination.py   (about 10 minutes on 4 cores)
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
            BLIND_TEST_CATCH=0.0, ISA_H_WEEK=0.0, ENVELOPE=0.0)
BLIND = {"no blind spots": {}, "family blind spots 18%": dict(FAMILY_BLIND_P=0.18), "all-family blind spots 18%": dict(BLIND_P=0.18)}
TESTS = {"review only (r12.10)": {}, "challenge tests": dict(CHALLENGE_TESTS=True),
         "challenge tests + exploration 25%": dict(CHALLENGE_TESTS=True, BLIND_TEST_CATCH=0.25)}
ISA = {"Isa unlimited (reference)": {}, "Isa 5 h, ratifies all": dict(ISA_H_WEEK=5.0),
       "Isa 5 h, envelope 50%": dict(ISA_H_WEEK=5.0, ENVELOPE=0.5), "Isa 5 h, envelope 80%": dict(ISA_H_WEEK=5.0, ENVELOPE=0.8)}


def job(args):
    demand, params, seed = args
    saved = {k: getattr(v, k) for k in BASE}
    try:
        for k, x in {**BASE, **params}.items():
            setattr(v, k, x)
        seats, sc = e.build("elastic", SEVEN, None)
        sc.held_weight, sc.drain_h = 1.0, 0.25
        sim = v.Sim(v.Org("institutions"), seats, seed=seed, wip=6, demand=e.make_demand(demand), scaler=sc)
        return v.measure(sim.run())
    finally:
        for k, x in saved.items():
            setattr(v, k, x)


def cells():
    out = []
    for d in ("steady", "mixed"):
        for b, bp in BLIND.items():
            for t, tp in TESTS.items():
                out.append(("E", f"{d} / {b}", t, e.DEMANDS[d], {**bp, **tp}))
    for extra in (0, 25, 50):
        for i, ip in ISA.items():
            out.append(("O", f"25 briefs + {extra} originated a week", i, dict(rate=("const", 25 + extra)), ip))
    return out


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    cs = cells()
    jobs = [(d, p, k) for _, _, _, d, p in cs for k in range(SEEDS)]
    with Pool() as pool:
        res = pool.map(job, jobs, chunksize=1)
    say("EDGE CASES, ORIGINATION AND THE RATIFICATION ENVELOPE (institutions, elastic, R17 at 25% coupling, R21, "
        "time value $0.5/h, the seven-model menu; lead = median/90th h)")
    last = None
    for i, (t, grp, lab, _, _) in enumerate(cs):
        m = v.mean_measures(res[i * SEEDS:(i + 1) * SEEDS])
        if (t, grp) != last:
            say(f"\n[{t} / {grp}]")
            last = (t, grp)
        dr = m["drops"]
        say(f"  {lab:<34} {m['clean']:5.1f} clean ({m['ideas']:5.1f} live)  lead {m['lead']:5.0f}/{m['lead_p90']:5.0f} h  "
            f"CFR {m['cfr']:4.0%}  escaped {m['escaped']:4.2f}/idea  ${m['usd_clean']:5.1f}/clean  "
            f"challenge catches {dr.get('challenge_fail', 0):4.2f}/idea  Isa {m['isa_h']:4.1f} h/wk  "
            f"ratification wait {m['ratify_wait']:5.1f} h  open at end {m['backlog']:4.0f}")
        out.setdefault(t, {}).setdefault(grp, {})[lab] = {k: x for k, x in m.items() if k != "waits"}
    (HERE / "origination_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "origination.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
