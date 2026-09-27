"""Operating models compared: the institutions against every other way to organise the agents.

Answers "institutions vs dedicated roles, but any other model, or no model?"
All organisations run on the same world, the same agents and the same work.

  institutions   r10 sizing (K=2, D=1 + red team, 1 council round, audit 10%)
  dedicated      the institutions with seats fixed to one institution each
  peer           each agent owns an idea end to end; another agent reviews and releases
  solo           "no model": each agent owns an idea end to end and checks its own work
  swarm          one shared pull queue and none of the rules
  self-licensed  the institutions, but agents license themselves (overconfident by 10 points)
  orchestrator   one lead frames, plans, checks and releases; workers build
  DWC            Director -> Worker -> Checker (the r10 baseline)

Rosters: the recommended six (../portfolio6), and draws from the Artificial
Analysis population in its natural-tier proportions at 12 and 24 agents, and a
weak-heavy 12 (2 top / 4 middle / 6 bottom).
Scenarios: base; harder work (hard cards 65-85, requirements +8); speed ignored.
Every organisation runs at its own best work-in-progress limit (0.7N, N or 1.5N),
judged on clean ideas.

Headline measure: CLEAN ideas per week = ideas released with every requirement
delivered and no escaped defect, i.e. ideas that need no follow-up.

Also: an ablation of the institutions (remove one feature at a time) to find
which institutions earn their cost.

Run: python3 probes/institutions/operating_models.py   (about 10 minutes on 4 cores)
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from multiprocessing import Pool
from pathlib import Path

import factory_sim as f
from experiments import split

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "portfolio6"))
import select6 as s6  # noqa: E402

SEEDS = 4
SIX = ["Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "Muse Spark 1.3 (xhigh)",
       "Gemini 3.8 Flash (high)", "DeepSeek V4.1 Flash (Reasoning, Max Effort)", "GPT-6 Luna (max)", "Ling 3.0 Flash"]
ROSTERS = {"best six": ("six",), "population 12": ("pop", {1: 6, 2: 3, 3: 3}),
           "population 24": ("pop", {1: 11, 2: 7, 3: 6}), "weak-heavy 12": ("pop", {1: 2, 2: 4, 3: 6})}
INST = dict(K=2, D=1, council_rounds=1, redteam=True, audit=True)
ORGS = {
    "institutions": ("institutions", INST, None),
    "dedicated": ("institutions", INST, "dedicated"),
    "peer": ("peer", {}, None),
    "solo": ("solo", {}, None),
    "swarm": ("institutions", dict(K=1, D=1, council_rounds=0, redteam=False, audit=False, licences=False,
                                   independence=False, hardest_first=False), None),
    "self-licensed": ("institutions", dict(INST, overconf=f.OVERCONF), None),
    "orchestrator": ("baseline", {}, "orchestrator"),
    "DWC": ("baseline", {}, "dwc"),
}
ABLATION = {
    "institutions (all)": INST,
    "- council": dict(INST, council_rounds=0),
    "- red team": dict(INST, redteam=False),
    "- audit": dict(INST, audit=False),
    "- second analyst (K=1)": dict(INST, K=1),
    "- licences": dict(INST, licences=False),
    "- independence": dict(INST, independence=False),
    "- hardest-first": dict(INST, hardest_first=False),
    "+ second planner (D=2)": dict(INST, D=2),
}

KINDS = {"inquiry": {"inquiry"}, "council": {"critique", "synthesis"}, "planning": {"decompose", "reconcile", "redteam"},
         "market": {"card"}, "court": {"review", "audit"}, "release": {"release"}}
ORDER = ["planning", "council", "release", "court", "market", "inquiry"]     # most demanding first


def dedicated_plan(n):
    if n <= 6:
        return {"planning": 1, "council": 1, "release": 1, "court": 1, "market": n - 4}
    k = n / 12
    plan = {"inquiry": round(2 * k), "council": round(k), "planning": round(2 * k), "court": round(2 * k), "release": round(k)}
    plan["market"] = n - sum(plan.values())
    return plan


def build(roster, seed, shape):
    kind = roster[0]
    agents = s6.roster(SIX) if kind == "six" else f.draw_agents(roster[1], random.Random(1000 + seed))
    agents.sort(key=lambda a: -a.cfg.ci)
    for i, a in enumerate(agents):
        a.idx = i
    if shape == "dedicated":
        i = 0
        for inst in ORDER:
            for _ in range(dedicated_plan(len(agents)).get(inst, 0)):
                if inst == "council" and len(agents) <= 6:
                    agents[i].roles = KINDS["council"] | KINDS["inquiry"]
                else:
                    agents[i].roles = set(KINDS[inst])
                i += 1
        for a in agents[i:]:
            a.roles = {"card"}
    elif shape == "orchestrator":
        agents[0].roles = {"director", "checker"}
        for a in agents[1:]:
            a.roles = {"worker"}
    elif shape == "dwc":
        agents[0].roles, agents[1].roles = {"director"}, {"checker"}
        for a in agents[2:]:
            a.roles = {"worker"}
    return agents


BASE_HOURS = f.Agent.hours


def set_scenario(name):
    snap = dict(CARD_RANGE=dict(f.CARD_RANGE), CARD_MIX=dict(f.CARD_MIX), TASK_DIFF=dict(f.TASK_DIFF))
    if name == "harder work":
        f.CARD_RANGE.update(easy=(15, 40), mid=(40, 65), hard=(65, 85))
        f.CARD_MIX.update(easy=0.30, mid=0.35, hard=0.35)
        rb = f.REQ_BASE + 8
        f.TASK_DIFF.update(inquiry=rb, critique=rb + 5, decompose=rb + 8, redteam=rb + 10, synthesis=63, reconcile=68, release=58)
    if name == "speed ignored":
        f.Agent.hours = lambda self, base: base
    return snap


def restore(snap):
    for k, v in snap.items():
        getattr(f, k).clear()
        getattr(f, k).update(v)
    f.Agent.hours = BASE_HOURS


def job(args):
    scenario, roster, org, kw, shape, wip, seed = args
    snap = set_scenario(scenario)
    try:
        agents = build(roster, seed, shape)
        m = f.measure(f.Sim(org, agents, seed=seed, wip=wip, **kw).run())
    finally:
        restore(snap)
    usd = sum(v["busy_h_per_week"] * s6.usd_per_busy_hour(s6.C[k]) for k, v in m["per_agent"].items() if k in s6.C)
    return dict(ipw=m["ideas_per_week"], clean=m["clean_per_week"], coh=m["coherence"], esc=m["escaped_per_idea"],
                lead=m["lead_h"], util=m["utilisation"], usd_week=usd if roster[0] == "six" else float("nan"),
                sim_cost=m["cost_per_idea"] * m["ideas_per_week"])


def mean_rows(rows):
    out = {}
    for k in rows[0]:
        vals = [r[k] for r in rows if not (isinstance(r[k], float) and math.isnan(r[k]))]
        out[k] = statistics.mean(vals) if vals else float("nan")
    return out


def n_of(roster):
    return 6 if roster[0] == "six" else sum(roster[1].values())


def run_grid(pool, scenarios, orgs):
    jobs, keys = [], []
    for sc in scenarios:
        for rname, roster in ROSTERS.items():
            n = n_of(roster)
            for oname, (org, kw, shape) in orgs.items():
                for wip in sorted({max(2, round(0.7 * n)), n, round(1.5 * n)}):
                    for seed in range(SEEDS):
                        jobs.append((sc, roster, org, kw, shape, wip, seed))
                        keys.append((sc, rname, oname, wip))
    res = pool.map(job, jobs, chunksize=2)
    grouped = {}
    for k, r in zip(keys, res):
        grouped.setdefault(k, []).append(r)
    best = {}
    for (sc, rname, oname, wip), rows in grouped.items():
        m = mean_rows(rows)
        m["wip"] = wip
        cur = best.get((sc, rname, oname))
        if cur is None or m["clean"] > cur["clean"]:
            best[(sc, rname, oname)] = m
    return best


def main():
    lines = []

    def say(x=""):
        print(x)
        lines.append(x)

    scenarios = ["base", "harder work", "speed ignored"]
    with Pool() as pool:
        best = run_grid(pool, scenarios, ORGS)
        say("OPERATING MODELS: clean ideas/week (ideas/week; coherence; escaped defects per idea) at each organisation's best WIP")
        summary = {}
        for sc in scenarios:
            say(f"\n[{sc}]")
            say(f"  {'organisation':<14} " + " ".join(f"{r:>30}" for r in ROSTERS))
            for oname in ORGS:
                cells = []
                for rname in ROSTERS:
                    m = best[(sc, rname, oname)]
                    cells.append(f"{m['clean']:5.1f} ({m['ipw']:5.1f}; {m['coh']:.2f}; {m['esc']:.2f})".rjust(30))
                    summary.setdefault(oname, {}).setdefault(sc, {})[rname] = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()}
                say(f"  {oname:<14} " + " ".join(cells))
        # share of institutions' clean output
        say("\nClean ideas as a share of the institutions' (same roster, same scenario); worst case across all twelve cells")
        worst = {}
        for oname in ORGS:
            shares = [best[(sc, r, oname)]["clean"] / best[(sc, r, "institutions")]["clean"] for sc in scenarios for r in ROSTERS]
            worst[oname] = (min(shares), statistics.mean(shares), max(shares))
            say(f"  {oname:<14} worst {min(shares):5.0%}   mean {statistics.mean(shares):5.0%}   best {max(shares):5.0%}")
        six_cost = {o: best[("base", "best six", o)] for o in ORGS}
        say("\nBest six, base scenario: API cost per clean idea (token model of ../portfolio6)")
        for o, m in six_cost.items():
            say(f"  {o:<14} ${m['usd_week']:5.0f}/wk  {m['clean']:5.1f} clean/wk  ${m['usd_week'] / max(m['clean'], 1e-9):6.1f} per clean idea  lead {m['lead']:4.0f} h")

        # ablation
        abl = {}
        say("\nABLATION of the institutions: clean ideas/week (ideas/week), base and harder work")
        say(f"  {'variant':<24} " + " ".join(f"{r + ' / ' + sc[:6]:>24}" for sc in ("base", "harder work") for r in ("best six", "population 12")))
        jobs, keys = [], []
        for sc in ("base", "harder work"):
            for rname in ("best six", "population 12"):
                roster = ROSTERS[rname]
                n = n_of(roster)
                for vname, kw in ABLATION.items():
                    for seed in range(SEEDS * 2):
                        jobs.append((sc, roster, "institutions", kw, None, max(2, round(0.7 * n)), seed))
                        keys.append((vname, sc, rname))
        res = pool.map(job, jobs, chunksize=2)
        grouped = {}
        for k, r in zip(keys, res):
            grouped.setdefault(k, []).append(r)
        for vname in ABLATION:
            cells = []
            for sc in ("base", "harder work"):
                for rname in ("best six", "population 12"):
                    m = mean_rows(grouped[(vname, sc, rname)])
                    abl.setdefault(vname, {})[f"{rname} / {sc}"] = {k: round(v, 3) for k, v in m.items()}
                    cells.append(f"{m['clean']:5.1f} ({m['ipw']:5.1f})".rjust(24))
            say(f"  {vname:<24} " + " ".join(cells))

    (HERE / "operating_models_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(dict(summary=summary, worst=worst, ablation=abl), open(HERE / "operating_models.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
