"""Robustness of the best-six choice to the assumptions that drive it.

select6.py ranks sixes under the r10 base assumptions. There, output speed
dominates: among top-tier models the Coding Index spread (74-82) moves the pass
rate on the hardest cards by only about ten points, while speed moves task time
by up to 2x. This probe re-ranks the leading sixes, plus the premium sixes Isa
asked about and a US-only mid tier, when that assumption and the work itself change:

  base            r10 assumptions (time ~ 1/sqrt(speed))
  speed-half      time ~ 1/speed^0.25 (tool calls and tests dilute generation speed)
  speed-ignored   time independent of speed
  harder-work     hard cards 65-85, mid 40-65, mix 30/35/35, requirements +8
  harder+half     both of the last two
  estimates-3     every estimated Coding Index 3 points lower

Choice rule: minimax regret, i.e. the six whose worst share of the scenario's
best clean-idea throughput is highest; sixes within two points of that are treated as
tied (seed noise is 1-3%), and the cheapest per clean idea among them is chosen.

Run: python3 probes/portfolio6/robust6.py   (after select6.py; about 5 minutes)
"""

from __future__ import annotations

import json
import math
from multiprocessing import Pool
from pathlib import Path

import select6 as s

f = s.f
HERE = Path(__file__).parent
SEEDS = 8
TIE = 0.02          # worst-case shares closer than this are within seed noise

FABLE = "Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback)"
OPUS = "Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)"
ASTRA, SOL, TERRA = "GPT-6 Astra (high)", "GPT-6 Sol (max)", "GPT-5.6 Terra (max)"
GEMINI, MUSE, GROK = "Gemini 3.8 Flash (high)", "Muse Spark 1.3 (xhigh)", "Grok 4.7 (xhigh)"
PREMIUM_TOPS = [[FABLE, ASTRA, GEMINI], [OPUS, SOL, GEMINI], [FABLE, SOL, GEMINI], [OPUS, ASTRA, GEMINI],
                [OPUS, MUSE, GEMINI], [OPUS, SOL, MUSE], [FABLE, OPUS, GEMINI], [OPUS, GROK, GEMINI]]

# governance variant: every mid seat from a US vendor, one of them run locally (Gemma 4 31B, open weights)
US_ONLY = [OPUS, MUSE, GEMINI, "GPT-6 Luna (max)", "Inkling Small", "Gemma 4 31B (Reasoning)"]

BASE_HOURS = f.Agent.hours


def speed_exp(e):
    def hours(self, base):
        return base * (100 / max(self.cfg.speed, 10)) ** e
    return hours


def harder():
    f.CARD_RANGE.update(easy=(15, 40), mid=(40, 65), hard=(65, 85))
    f.CARD_MIX.update(easy=0.30, mid=0.35, hard=0.35)
    rb = f.REQ_BASE + 8
    f.TASK_DIFF.update(inquiry=rb, critique=rb + 5, decompose=rb + 8, redteam=rb + 10, synthesis=63, reconcile=68, release=58)


SCENARIOS = {
    "base": dict(exp=0.5),
    "speed-half": dict(exp=0.25),
    "speed-ignored": dict(exp=0.0),
    "harder-work": dict(exp=0.5, harder=True),
    "harder+half": dict(exp=0.25, harder=True),
    "estimates-3": dict(exp=0.5, shift=3.0),
}


def snapshot():
    return dict(CARD_RANGE=dict(f.CARD_RANGE), CARD_MIX=dict(f.CARD_MIX), TASK_DIFF=dict(f.TASK_DIFF))


def restore(snap):
    for k, v in snap.items():
        getattr(f, k).clear()
        getattr(f, k).update(v)
    f.Agent.hours = BASE_HOURS


def main():
    prior = json.load(open(HERE / "select6.json"))
    best_mid = prior["best_value"]["six"][3:]
    sixes = []
    for r in prior["finalists"]:
        if r["six"] not in sixes:
            sixes.append(r["six"])
    for t in PREMIUM_TOPS:
        m = [n for n in best_mid if n not in t]
        if len(m) < 3:                       # the top trio already holds a mid model; take the next best mid
            m = [n for n in s.REFERENCE_MID if n not in t][:3]
        six = t + m[:3]
        if s.legal(t, m[:3]) and six not in sixes:
            sixes.append(six)

    if US_ONLY not in sixes:
        sixes.append(US_ONLY)
    snap = snapshot()
    table = {}
    for name, sc in SCENARIOS.items():
        f.Agent.hours = speed_exp(sc["exp"])
        if sc.get("harder"):
            harder()
        with Pool() as pool:                 # fork after patching so workers see the scenario
            rows = s.evaluate(pool, sixes, SEEDS, ci_shift=sc.get("shift", 0.0))
        restore(snap)
        top = max(r["clean"] for r in rows)
        for r in rows:
            table.setdefault(tuple(r["six"]), {})[name] = dict(ipw=round(r["ipw"], 2), clean=round(r["clean"], 2),
                                                              share=round(r["clean"] / top, 3),
                                                              coh=round(r["coh"], 3), esc=round(r["esc"], 3),
                                                              usd_idea=round(r["usd_idea"], 1), usd_clean=round(r["usd_clean"], 1))
        print(f"{name}: best {top:.1f} clean ideas/wk")

    lines = [f"ROBUSTNESS of the leading sixes ({SEEDS} seeds; clean ideas/week, share = of the scenario's best six)",
             "  " + " ".join(f"{k:>13}" for k in SCENARIOS) + "   worst  $/clean(base)  six"]
    ranked = sorted(table.items(), key=lambda kv: (-min(v["share"] for v in kv[1].values()), kv[1]["base"]["usd_clean"]))
    for six, v in ranked:
        worst = min(x["share"] for x in v.values())
        lines.append("  " + " ".join(f"{v[k]['clean']:6.1f} ({v[k]['share']:.0%})".rjust(13) for k in SCENARIOS)
                     + f"   {worst:.0%}  {v['base']['usd_clean']:11.0f}    "
                     + " + ".join(s.label(n) for n in six[:3]) + " || " + " + ".join(s.label(n) for n in six[3:]))
    worst_of = {six: min(x["share"] for x in v.values()) for six, v in ranked}
    best_worst = max(worst_of.values())
    tied = [(six, v) for six, v in ranked if worst_of[six] >= best_worst - TIE]
    pick = min(tied, key=lambda kv: kv[1]["base"]["usd_clean"])
    lines.append(f"\n  within {TIE:.0%} of the best worst case: {len(tied)} sixes; cheapest of them:")
    lines.append("  minimax-regret six: " + " + ".join(s.label(n) for n in pick[0]))
    print("\n".join(lines))
    (HERE / "robust6_results.txt").write_text("\n".join(lines) + "\n")
    json.dump([dict(six=list(k), scenarios=v) for k, v in ranked], open(HERE / "robust6.json", "w"), indent=1)


if __name__ == "__main__":
    main()
