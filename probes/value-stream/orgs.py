"""Organisations compared on the idea-to-live value stream, and a search for a better one.

Every organisation below is a mapping of the same steps (vs_sim.py) onto the
same seats. Seats belong to three pools: A (anchor: the strongest model),
F (fast top-tier), M (mid). The designs:

  no organisation    solo: each seat owns an idea and does every step itself
  peer               solo, but review, QA and release by another seat
  Director-Worker-   the current Factory: a Director frames, designs, plans,
    Checker          releases and runs live; a Checker reviews and tests;
                     workers build and integrate; cards routed by the Director
  orchestrator       one lead does every thinking and checking step; workers
                     build, integrate and run live
  functional roles   one role per step family (product, architect, reviewer,
                     release and operations, developers); fixed assignment,
                     best of a swap search over which model holds which role
  institutions       every seat may pull every step, gated by evidence
                     licences and independence (r10 sizing, all optional
                     steps on)
  pools per step     "bunches of models": A designs, plans, secures and
                     releases; F discovers, reviews, tests, operates; M builds
                     and integrates; rules on
  searched           a new organisation: for every step, which pools may do
                     it, plus committee sizes and optional steps, found by
                     coordinate search from the institutions

Rosters: the recommended six (A = Opus 5.5; F = Muse Spark 1.3, Gemini 3.8
Flash; M = DeepSeek V4.1 Flash, GPT-6 Luna, Ling 3.0 Flash), and a 12-seat draw
from the Artificial Analysis population (A = top two, F = the other top-tier
seats, M = the rest). Scenarios: base, harder work, security-heavy, weak tests,
heavy merge contention.

Run: python3 probes/value-stream/orgs.py   (about 20 minutes on 4 cores)
"""

from __future__ import annotations

import itertools
import json
import random
import statistics
from dataclasses import replace
from multiprocessing import Pool
from pathlib import Path

import vs_sim as v

HERE = Path(__file__).parent
SEEDS = 4
SIX = ["Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "Muse Spark 1.3 (xhigh)",
       "Gemini 3.8 Flash (high)", "DeepSeek V4.1 Flash (Reasoning, Max Effort)", "GPT-6 Luna (max)", "Ling 3.0 Flash"]
STEPS = sorted(v.ALL_STEPS)
POOL_SETS = [frozenset(c) for n in (1, 2, 3) for c in itertools.combinations("AFM", n)]


# ---------------------------------------------------------------- rosters
def roster(name, seed):
    if name == "best six":
        seats = [v.Seat(v.s6.roster([n])[0].cfg, i) for i, n in enumerate(SIX)]
        for s, c in zip(seats, "AFFMMM"):
            s.cls = c
        return seats
    rng = random.Random(1000 + seed)
    cfgs = [rng.choice(v.fs.POOL[t]) for t, n in {1: 6, 2: 3, 3: 3}.items() for _ in range(n)]
    cfgs.sort(key=lambda c: -c.ci)
    seats = [v.Seat(c, i) for i, c in enumerate(cfgs)]
    for i, s in enumerate(seats):
        s.cls = "A" if i < 2 else "F" if s.cfg.tier == 1 else "M"
    return seats


def idx(seats, classes):
    return {s.idx for s in seats if s.cls in classes}


# ---------------------------------------------------------------- designs
def solo(seats):
    return v.Org("no organisation (solo)", licences=False, independence=False, owner_steps=frozenset(v.ALL_STEPS),
                 K=1, challenge=0, plan_check=False, security=False, audit=0.0, dep_gate="built")


def peer(seats):
    return v.Org("peer", licences=False, independence=True,
                 owner_steps=frozenset(v.ALL_STEPS - {"review", "qa", "release"}), K=1, challenge=0,
                 plan_check=False, security=False, audit=0.0, dep_gate="built")


def dwc(seats):
    d, c = seats[0].idx, seats[1].idx
    w = {s.idx for s in seats[2:]}
    pools = {st: {d} for st in ("discover", "design", "plan", "release", "operate")}
    pools.update(review={c}, qa={c}, build=w, integrate=w)
    return v.Org("Director-Worker-Checker", pools=pools, licences=False, independence=True, K=1, challenge=0,
                 plan_check=False, security=False, audit=0.0, routing="director", workers=frozenset(w), dep_gate="built")


def orchestrator(seats):
    lead = seats[0].idx
    w = {s.idx for s in seats[1:]}
    pools = {st: {lead} for st in ("discover", "design", "plan", "review", "qa", "release")}
    pools.update(build=w, integrate=w, operate=w)
    return v.Org("orchestrator", pools=pools, licences=False, independence=False, K=1, challenge=0,
                 plan_check=False, security=False, audit=0.0, routing="director", workers=frozenset(w), dep_gate="built")


ROLES = [("architect", {"design", "plan", "plan_check"}), ("product", {"discover", "challenge", "qa"}),
         ("reviewer", {"review", "security", "audit"}), ("release-ops", {"release", "operate"}),
         ("developer", {"build", "integrate"})]


def role_counts(n):
    if n <= 6:
        return {"architect": 1, "product": 1, "reviewer": 1, "release-ops": 1, "developer": n - 4}
    return {"architect": 1, "product": 2, "reviewer": 2, "release-ops": 1, "developer": n - 6}


def functional(seats, order=None):
    """order: seat indices in role order (architect first ... developers last)."""
    order = order or [s.idx for s in seats]
    counts = role_counts(len(seats))
    pools, i = {}, 0
    for role, steps in ROLES:
        members = set(order[i:i + counts[role]])
        i += counts[role]
        for st in steps:
            pools[st] = members
    return v.Org("functional roles", pools=pools, licences=False, independence=True, K=counts["product"],
                 challenge=1, plan_check=True, security=True, audit=0.0, dep_gate="built")


def institutions(seats):
    return v.Org("institutions")


def pools_per_step(seats):
    a, f_, m = idx(seats, "A"), idx(seats, "F"), idx(seats, "M")
    pools = {st: a for st in ("design", "plan", "plan_check", "security", "release")}
    pools.update({st: f_ for st in ("discover", "challenge", "review", "qa", "operate", "audit")})
    pools.update(build=m, integrate=m)
    return v.Org("pools per step", pools=pools)


DESIGNS = {"no organisation (solo)": solo, "peer": peer, "Director-Worker-Checker": dwc, "orchestrator": orchestrator,
           "functional roles": functional, "institutions": institutions, "pools per step": pools_per_step}


# ---------------------------------------------------------------- scenarios
def set_scenario(name):
    snap = {k: getattr(v, k) for k in ("CARD_RANGE", "CARD_MIX", "REQ_BASE", "SEC_SHARE", "TEST_CATCH", "CI_CATCH", "CONFLICT_K")}
    snap = {k: (dict(x) if isinstance(x, dict) else x) for k, x in snap.items()}
    if name == "harder work":
        v.CARD_RANGE = dict(easy=(15, 40), mid=(40, 65), hard=(65, 85))
        v.CARD_MIX = dict(easy=0.30, mid=0.35, hard=0.35)
        v.REQ_BASE = 58.0
    elif name == "security-heavy":
        v.SEC_SHARE = 0.5
    elif name == "weak tests":
        v.TEST_CATCH, v.CI_CATCH = 0.30, 0.40
    elif name == "heavy contention":
        v.CONFLICT_K = 0.02
    return snap


def restore(snap):
    for k, x in snap.items():
        setattr(v, k, x)


SCENARIOS = ["base", "harder work", "security-heavy", "weak tests", "heavy contention"]


# ---------------------------------------------------------------- evaluation
def spec_org(spec, seats):
    """spec: ('design', name) | ('functional', order) | ('search', dict)."""
    kind, arg = spec
    if kind == "design":
        return DESIGNS[arg](seats)
    if kind == "functional":
        return functional(seats, list(arg))
    pools = {st: idx(seats, cls) for st, cls in arg["pools"].items() if set(cls) != set("AFM")}
    return v.Org("searched", pools=pools, **{k: x for k, x in arg.items() if k != "pools"})


def job(args):
    spec, rname, scenario, seed = args
    snap = set_scenario(scenario)
    try:
        seats = roster(rname, seed)
        org = spec_org(spec, seats)
        return v.measure(v.Sim(org, seats, seed=seed, wip=len(seats)).run())
    finally:
        restore(snap)


def evaluate(pool, specs, rname, scenario, seeds=SEEDS):
    jobs = [(sp, rname, scenario, k) for sp in specs for k in range(seeds)]
    res = pool.map(job, jobs, chunksize=1)
    return [v.mean_measures(res[i * seeds:(i + 1) * seeds]) for i in range(len(specs))]


def best_functional(pool, rname, scenario):
    """Swap search over which seat holds which role (fair to a fixed-role design)."""
    n = 6 if rname == "best six" else 12
    order = list(range(n))
    best = evaluate(pool, [("functional", tuple(order))], rname, scenario, 2)[0]["clean"]
    for _ in range(2):
        swaps = [tuple(order[:i] + [order[j]] + order[i + 1:j] + [order[i]] + order[j + 1:])
                 for i in range(n) for j in range(i + 1, n)]
        res = evaluate(pool, [("functional", o) for o in swaps], rname, scenario, 2)
        k = max(range(len(res)), key=lambda k: res[k]["clean"])
        if res[k]["clean"] <= best:
            break
        best, order = res[k]["clean"], list(swaps[k])
    return tuple(order)


def search(pool, rname, scenario, objective="clean", passes=3):
    """Coordinate search over step -> pool subsets, committee sizes and optional steps."""
    cur = dict(pools={st: "AFM" for st in STEPS}, K=2, challenge=1, plan_check=True, security=True, audit=0.1,
               reviewers=1, licences=True, independence=True)

    def score(m):
        return m["clean"] if objective == "clean" else m["clean"] / max(m["usd_week"], 1e-9) * 1000

    base = score(evaluate(pool, [("search", cur)], rname, scenario)[0])
    knobs = [("K", (1, 2, 3)), ("challenge", (0, 1, 2)), ("plan_check", (False, True)), ("security", (False, True)),
             ("audit", (0.0, 0.1)), ("reviewers", (1, 2)), ("licences", (False, True)), ("independence", (False, True))]
    for _ in range(passes):
        improved = False
        for st in STEPS:
            opts = []
            for ps in POOL_SETS:
                c = dict(cur, pools=dict(cur["pools"], **{st: "".join(sorted(ps))}))
                opts.append(c)
            res = evaluate(pool, [("search", c) for c in opts], rname, scenario)
            k = max(range(len(res)), key=lambda k: score(res[k]))
            if score(res[k]) > base * 1.01:
                cur, base, improved = opts[k], score(res[k]), True
        for knob, vals in knobs:
            opts = [dict(cur, **{knob: x}) for x in vals if x != cur[knob]]
            res = evaluate(pool, [("search", c) for c in opts], rname, scenario)
            k = max(range(len(res)), key=lambda k: score(res[k]))
            if score(res[k]) > base * 1.01:
                cur, base, improved = opts[k], score(res[k]), True
        if not improved:
            break
    return cur


def fmt(m, cost=True):
    c = f"  ${m['usd_clean']:5.0f}/clean" if cost and m["usd_week"] == m["usd_week"] else ""
    return (f"{m['clean']:5.1f} clean/wk ({m['ideas']:5.1f} live)  lead {m['lead']:4.0f} h  CFR {m['cfr']:4.0%}  "
            f"restore {m['restore']:4.1f} h  intent {m['coherence']:.2f}{c}  bottleneck {m['bottleneck']}")


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    with Pool() as pool:
        found = {}
        for rname in ("best six", "population 12"):
            found[rname] = dict(functional=best_functional(pool, rname, "base"),
                                clean=search(pool, rname, "base", "clean"),
                                value=search(pool, rname, "base", "value") if rname == "best six" else None)
            say(f"\nSEARCHED ORGANISATION ({rname}, objective: most clean ideas)")
            for st in STEPS:
                say(f"  {st:<11} pools {found[rname]['clean']['pools'][st]}")
            say("  rules " + ", ".join(f"{k}={x}" for k, x in found[rname]["clean"].items() if k != "pools"))
            if found[rname]["value"]:
                say(f"SEARCHED ORGANISATION ({rname}, objective: clean ideas per dollar)")
                for st in STEPS:
                    say(f"  {st:<11} pools {found[rname]['value']['pools'][st]}")
                say("  rules " + ", ".join(f"{k}={x}" for k, x in found[rname]["value"].items() if k != "pools"))
        for rname in ("best six", "population 12"):
            specs = [("design", d) for d in DESIGNS if d != "functional roles"]
            specs.insert(4, ("functional", found[rname]["functional"]))
            specs.append(("search", found[rname]["clean"]))
            labels = [s[1] if s[0] == "design" else "functional roles" if s[0] == "functional" else "searched (clean)" for s in specs]
            if found[rname]["value"]:
                specs.append(("search", found[rname]["value"]))
                labels.append("searched (per $)")
            for sc in SCENARIOS:
                res = evaluate(pool, specs, rname, sc)
                inst = res[labels.index("institutions")]["clean"]
                say(f"\n[{rname} / {sc}]")
                for lab, m in zip(labels, res):
                    say(f"  {lab:<24} {fmt(m)}  ({m['clean'] / inst:4.0%} of institutions)")
                    out.setdefault(rname, {}).setdefault(sc, {})[lab] = {k: x for k, x in m.items() if k not in ("waits",)}
        # where the institutions spend their time (best six, base)
        m = evaluate(pool, [("design", "institutions")], "best six", "base")[0]
        tot = sum(m["busy_step"].values())
        say("\nWhere the institutions' seat-hours go (best six, base): " +
            ", ".join(f"{k} {x / tot:.0%}" for k, x in sorted(m["busy_step"].items(), key=lambda kv: -kv[1])))
        say("Mean wait by step (h): " + ", ".join(f"{k} {x:.1f}" for k, x in sorted(m["waits"].items(), key=lambda kv: -kv[1])))

    (HERE / "orgs_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(dict(results=out, found={r: {k: x for k, x in d.items()} for r, d in found.items()}),
              open(HERE / "orgs.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
