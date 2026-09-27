"""Best six: three top seats and three mid seats from the 27 Sep 2026 AA market.

Idea-stage probe for docs/idea/best-six.md. Results: select6_results.txt, select6.json.

Market: candidates_2026-09-27.csv (Artificial Analysis snapshot of 27 Sep 2026,
165 current priced configurations). Coding Index is AA's own score where AA
has published one (9 Sep data); for models released after that it is
estimated from AA's Intelligence Index (fit on the top end, RMSE 1.5 points,
n = 34) and marked * everywhere. One configuration per model: the strongest.

Seat classes (by price, because that is what "top" and "mid" buy):
  top  blended API price >= $2 per 1M tokens (the premium frontier offers)
  mid  blended API price <  $2 per 1M tokens, Coding Index >= 29.9
Gemini 3.8 Flash is Google's strongest coding model on AA and costs $1.50,
so it is allowed in either class. Every candidate's natural tier (top >= 56.8,
mid 29.9-56.8, from ../aa-tiers/tiering.py) is reported alongside.

Portfolio rules applied as hard constraints (Idea Record 5.1):
  P1  at least two vendors among the top seats
  P2  no vendor holds more than half the seats (3 of 6)

Evaluation: the institutional throughput model (../institutions/factory_sim.py)
with the sizing found in r10: Inquiry K=2, Planning D=1 plus red team, one
council round, audit 10%, work-in-progress limit 4 (about 0.7 x headcount).
Agents work around the clock; every figure is per week after a one-week warm-up.

Cost model (replaces the simulator's relative token counts; all assumptions):
  a task's work is fixed; at 100 tokens/s it takes the simulator's base hours.
  While working, a model generates for GEN_DUTY of the time (the rest is tool
  calls and tests); an agent loop reads IN_PER_OUT input tokens per output
  token, CACHE_HIT of them from the prompt cache at CACHE_PRICE of list price.
  So output tokens per task = base hours x 100 x 3600 x GEN_DUTY, and the API
  bill is AA's listed input and output prices applied to those tokens.

Stages:
  S1  every vendor-legal top trio, with a reference mid trio
  S2  every mid trio, with the three best top trios from S1
  S3  the leading sixes re-run on more seeds; vendor-outage and
      estimate-risk checks (estimated Coding Index scores cut by 3 points)
  S4  top seats on API tokens vs subscriptions (capped, throttled or hybrid)

Run: python3 probes/portfolio6/select6.py   (about 15 minutes on 4 cores)
"""

from __future__ import annotations

import csv
import itertools
import json
import math
import random
import statistics
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "institutions"))
import factory_sim as f  # noqa: E402

DATA = HERE / "candidates_2026-09-27.csv"
SIZING = dict(K=2, D=1, council_rounds=1, redteam=True, audit=True, wip=4)
QUALITY = dict(coherence=0.97, escaped=0.25)
SEEDS_SCAN, SEEDS_FINAL = 4, 12

# ---------------------------------------------------------------- token model (assumptions)
GEN_DUTY = 0.25        # share of a working hour the model is generating
IN_PER_OUT = 30.0      # input tokens read per output token in an agent loop
CACHE_HIT = 0.90       # share of input served from the prompt cache
CACHE_PRICE = 0.10     # cached input billed at 10% of list (OpenAI lists $1 vs $10 for Astra)
REF_TPS = 100.0

# ---------------------------------------------------------------- candidates
TOP_NAMES = [
    "Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback)",
    "Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)",
    "GPT-6 Astra (high)",
    "GPT-6 Sol (max)",
    "GPT-5.6 Terra (max)",
    "Grok 4.7 (xhigh)",
    "Grok 4.6 (high)",
    "Muse Spark 1.3 (xhigh)",
    "Kimi K3 (max)",
    "GLM-5.3 (max)",
    "Qwen3.8 Max (0902)",
    "Gemini 3.8 Flash (high)",
]
MID_NAMES = [
    "Gemini 3.8 Flash (high)",
    "MiMo-V2.6-Pro",
    "Step 5 Preview",
    "GLM 5.3 Flash",
    "Qwen3.8-Flash-Next",
    "DeepSeek V4.1 Flash (Reasoning, Max Effort)",
    "GPT-6 Luna (max)",
    "MiniMax-M3",
    "MiMo-V2.5",
    "Qwen3.8 27B (medium)",
    "Inkling Small",
    "Ling 3.0 Flash",
    "Gemma 4 31B (Reasoning)",
]
REFERENCE_MID = ["MiMo-V2.6-Pro", "GLM 5.3 Flash", "DeepSeek V4.1 Flash (Reasoning, Max Effort)"]


def load():
    rows = {r["name"]: r for r in csv.DictReader(open(DATA))}
    out = {}
    for name in dict.fromkeys(TOP_NAMES + MID_NAMES):
        r = rows[name]
        out[name] = dict(name=name, base=r["base"], vendor=r["creator"], released=r["released"],
                         ci=float(r["coding_index"]), est=r["coding_estimated"] == "True",
                         price=float(r["price_blended"]), p_in=float(r["price_in"]), p_out=float(r["price_out"]),
                         speed=float(r["speed"]), open=r["open_weights"] == "True")
    return out


C = load()


def short(name: str) -> str:
    return (name.replace(" (Adaptive Reasoning, Max Effort, Default Fallback)", " Max")
            .replace(" (Reasoning, Max Effort)", " Max").replace(" (Reasoning)", ""))


def label(name: str) -> str:
    return short(name) + ("*" if C[name]["est"] else "")


def usd_per_ref_hour(m: dict) -> float:
    out_tok = REF_TPS * 3600 * GEN_DUTY
    inp = out_tok * IN_PER_OUT
    return (out_tok * m["p_out"] + inp * m["p_in"] * ((1 - CACHE_HIT) + CACHE_HIT * CACHE_PRICE)) / 1e6


def usd_per_busy_hour(m: dict) -> float:
    return usd_per_ref_hour(m) / math.sqrt(REF_TPS / max(m["speed"], 10))


# ---------------------------------------------------------------- evaluation
def roster(names, ci_shift=0.0, caps=None):
    caps = caps or {}
    agents = []
    for i, n in enumerate(names):
        m = C[n]
        ci = m["ci"] - (ci_shift if m["est"] else 0.0)
        agents.append(f.Agent(f.Config(n, ci, m["price"], m["speed"]), i, cap_h_week=caps.get(n)))
    return agents


def run_one(args):
    names, seed, ci_shift, caps = args
    sim = f.Sim("institutions", roster(names, ci_shift, caps), seed=seed, **SIZING).run()
    m = f.measure(sim)
    return dict(ipw=m["ideas_per_week"], lead=m["lead_h"], coh=m["coherence"], esc=m["escaped_per_idea"],
                util=m["utilisation"], busy={k: v["busy_h_per_week"] for k, v in m["per_agent"].items()})


def evaluate(pool, sixes, seeds, ci_shift=0.0, caps=None):
    jobs = [(tuple(s), 100 + k, ci_shift, caps) for s in sixes for k in range(seeds)]
    res = pool.map(run_one, jobs, chunksize=4)
    out = []
    for i, s in enumerate(sixes):
        rows = res[i * seeds:(i + 1) * seeds]
        busy = {n: statistics.mean(r["busy"].get(n, 0.0) for r in rows) for n in s}
        ipw = statistics.mean(r["ipw"] for r in rows)
        api_week = sum(busy[n] * usd_per_busy_hour(C[n]) for n in s)
        out.append(dict(six=list(s), ipw=ipw, sd=statistics.pstdev([r["ipw"] for r in rows]),
                        lead=statistics.mean(r["lead"] for r in rows if not math.isnan(r["lead"])) if any(not math.isnan(r["lead"]) for r in rows) else float("nan"),
                        coh=statistics.mean(r["coh"] for r in rows if not math.isnan(r["coh"])) if ipw else 0.0,
                        esc=statistics.mean(r["esc"] for r in rows if not math.isnan(r["esc"])) if ipw else 9.9,
                        util=statistics.mean(r["util"] for r in rows), busy=busy,
                        api_week=api_week, usd_idea=api_week / ipw if ipw else float("inf")))
    return out


def legal(top, mid) -> bool:
    vendors = Counter(C[n]["vendor"] for n in top + mid)
    return len({C[n]["vendor"] for n in top}) >= 2 and max(vendors.values()) <= 3 and not set(top) & set(mid)


def ok(r) -> bool:
    return r["coh"] >= QUALITY["coherence"] and r["esc"] <= QUALITY["escaped"]


def fmt(r, n_top=3) -> str:
    t = " + ".join(label(n) for n in r["six"][:n_top])
    m = " + ".join(label(n) for n in r["six"][n_top:])
    return (f"{r['ipw']:5.1f}±{r['sd']:.1f} ideas/wk  lead {r['lead']:4.0f} h  coh {r['coh']:.3f}  esc {r['esc']:.2f}  "
            f"${r['usd_idea']:6.0f}/idea  ${r['api_week']:6.0f}/wk  | {t} || {m}")


def one_distinct_base(names) -> bool:
    return len({C[n]["base"] for n in names}) == len(names)


# ---------------------------------------------------------------- subscriptions (sourced facts + assumptions)
# Monthly prices are published. Capacity is not: vendors do not publish hour or token
# figures, so ranges below are community-reported (Claude Max) or assumed by analogy
# (ChatGPT Pro, Google AI Ultra). Hours = hours of agent work on that plan's top model.
WEEKS_PER_MONTH = 52 / 12
PLANS = {
    "Claude Max 20x ($200)": dict(vendor="Anthropic", usd=200, hours=(24, 40), note="community-reported Opus hours/week; Fable capped at 50% of weekly usage"),
    "Claude Max 5x ($100)": dict(vendor="Anthropic", usd=100, hours=(15, 35), note="community-reported Opus hours/week"),
    "ChatGPT Pro 20x ($200)": dict(vendor="OpenAI", usd=200, hours=(24, 40), note="Astra 100-900 messages per 5 h; hours assumed = Claude Max 20x; new sign-ups paused"),
    "ChatGPT Pro 5x ($100)": dict(vendor="OpenAI", usd=100, hours=(8, 20), note="Astra 25-225 messages per 5 h; hours assumed pro rata"),
    "Google AI Ultra 20x ($199.99)": dict(vendor="Google", usd=199.99, hours=(24, 40), note="no published agent limits; hours assumed = other 20x plans"),
    "Google AI Ultra 5x ($99.99)": dict(vendor="Google", usd=99.99, hours=(8, 20), note="no published agent limits; assumed"),
}


def sub_modes(pool, six, base_row, seeds):
    """Top seats on API, on a capped subscription (seat idles at the cap), or hybrid (API past the cap)."""
    top = six[:3]
    rows = []
    for name in top:
        vendor = C[name]["vendor"]
        rate = usd_per_busy_hour(C[name])
        h = base_row["busy"][name]
        for plan, p in PLANS.items():
            if p["vendor"] != vendor:
                continue
            for cap in p["hours"]:
                sub_week = p["usd"] / WEEKS_PER_MONTH
                capped = evaluate(pool, [six], seeds, caps={name: cap})[0]
                over = max(0.0, h - cap)
                rows.append(dict(seat=label(name), plan=plan, cap_h=cap, busy_h=round(h, 1), rate=round(rate, 2),
                                 api_week=round(h * rate), sub_week=round(sub_week),
                                 hybrid_week=round(sub_week + over * rate),
                                 breakeven_h=round(sub_week / rate, 1),
                                 subs_to_cover=math.ceil(h / cap),
                                 capped_ipw=round(capped["ipw"], 1), base_ipw=round(base_row["ipw"], 1),
                                 note=p["note"]))
    return rows


def all_top_capped(pool, six, seeds):
    """Every top seat on one 20x subscription at the low and high cap, no API overflow."""
    out = {}
    for lo_hi in (0, 1):
        caps = {}
        for n in six[:3]:
            plans = [p for p in PLANS.values() if p["vendor"] == C[n]["vendor"] and p["usd"] > 150]
            if plans:
                caps[n] = plans[0]["hours"][lo_hi]
        out["low cap" if lo_hi == 0 else "high cap"] = dict(caps={label(k): v for k, v in caps.items()},
                                                            **evaluate(pool, [six], seeds, caps=caps)[0])
    return out


# ---------------------------------------------------------------- main
def main():
    lines = []

    def say(s=""):
        print(s)
        lines.append(s)

    say("CANDIDATES (27 Sep 2026 AA snapshot; * = Coding Index estimated from Intelligence Index)")
    say(f"  {'model':<34} {'vendor':<10} {'released':<10} {'coding':>6} {'tier':>4} {'$in':>6} {'$out':>6} {'t/s':>5} {'$/busy h':>8} open")
    for n in dict.fromkeys(TOP_NAMES + MID_NAMES):
        m = C[n]
        cls = "top" if n in TOP_NAMES and n not in MID_NAMES else "mid" if n not in TOP_NAMES else "both"
        say(f"  {label(n):<34} {m['vendor']:<10} {m['released']:<10} {m['ci']:6.1f} {f.tier_of(m['ci']):>4} {m['p_in']:6.2f} "
            f"{m['p_out']:6.2f} {m['speed']:5.0f} {usd_per_busy_hour(m):8.2f} {'yes' if m['open'] else 'no':>4}  {cls}")

    with Pool() as pool:
        # S1
        tops = [t for t in itertools.combinations(TOP_NAMES, 3) if one_distinct_base(t)]
        cands = [list(t) + REFERENCE_MID for t in tops if legal(list(t), REFERENCE_MID)]
        s1 = evaluate(pool, cands, SEEDS_SCAN)
        s1.sort(key=lambda r: -r["ipw"])
        say(f"\nS1 top trios with reference mid ({' + '.join(label(n) for n in REFERENCE_MID)}): {len(s1)} legal trios")
        for r in s1[:12]:
            say("  " + fmt(r))
        say("  ...")
        for r in s1[-3:]:
            say("  " + fmt(r))
        cheap_top = sorted([r for r in s1 if ok(r) and r["ipw"] >= 0.9 * s1[0]["ipw"]], key=lambda r: r["usd_idea"])[:3]
        say("  cheapest per idea within 10% of the best throughput:")
        for r in cheap_top:
            say("  " + fmt(r))

        # S2
        best_tops = []
        for r in s1 + cheap_top:
            t = r["six"][:3]
            if t not in best_tops:
                best_tops.append(t)
            if len(best_tops) >= 3:
                break
        for r in cheap_top:
            if r["six"][:3] not in best_tops:
                best_tops.append(r["six"][:3])
        mids = [list(m) for m in itertools.combinations(MID_NAMES, 3) if one_distinct_base(m)]
        cands = [t + m for t in best_tops for m in mids if legal(t, m)]
        s2 = evaluate(pool, cands, SEEDS_SCAN)
        s2.sort(key=lambda r: -r["ipw"])
        say(f"\nS2 mid trios with the leading top trios: {len(s2)} legal sixes")
        for r in s2[:12]:
            say("  " + fmt(r))
        strict_mid = [r for r in s2 if all(f.tier_of(C[n]["ci"]) == 2 for n in r["six"][3:])]
        if strict_mid:
            say("  best with three statistically mid-tier models (Coding Index 29.9-56.8):")
            for r in sorted(strict_mid, key=lambda r: -r["ipw"])[:3]:
                say("  " + fmt(r))
        cheap6 = sorted([r for r in s2 if ok(r) and r["ipw"] >= 0.9 * s2[0]["ipw"]], key=lambda r: r["usd_idea"])[:5]
        say("  cheapest per idea within 10% of the best throughput:")
        for r in cheap6:
            say("  " + fmt(r))

        # S3
        finalists = []
        for r in s2[:8] + cheap6:
            if r["six"] not in finalists:
                finalists.append(r["six"])
        fin = evaluate(pool, finalists, SEEDS_FINAL)
        est = {tuple(r["six"]): r for r in evaluate(pool, finalists, SEEDS_FINAL, ci_shift=3.0)}
        say(f"\nS3 finalists on {SEEDS_FINAL} seeds; outage = worst week-long loss of one vendor; est-3 = estimated scores 3 points lower")
        for r in fin:
            worst = None
            for v in {C[n]["vendor"] for n in r["six"]}:
                rest = [n for n in r["six"] if C[n]["vendor"] != v]
                o = evaluate(pool, [rest], SEEDS_SCAN)[0]
                if worst is None or o["ipw"] < worst[1]:
                    worst = (v, o["ipw"])
            r["outage_vendor"], r["outage_ipw"] = worst
            r["est3_ipw"] = est[tuple(r["six"])]["ipw"]
            say("  " + fmt(r))
            say(f"      without {worst[0]}: {worst[1]:.1f} ideas/wk ({worst[1] / r['ipw']:.0%});  est-3: {r['est3_ipw']:.1f} ideas/wk;  "
                f"busy h/wk " + ", ".join(f"{label(n).split(' (')[0]} {r['busy'][n]:.0f}" for n in r["six"]))
        fin.sort(key=lambda r: -r["ipw"])
        best_tp = fin[0]
        best_value = min([r for r in fin if ok(r) and r["ipw"] >= 0.9 * best_tp["ipw"]], key=lambda r: r["usd_idea"])
        resilient = max([r for r in fin if ok(r) and r["ipw"] >= 0.9 * best_tp["ipw"]],
                        key=lambda r: (round(r["outage_ipw"] / r["ipw"], 2), -r["usd_idea"]))
        say("\n  best throughput: " + fmt(best_tp))
        say("  best value:      " + fmt(best_value))
        say("  most resilient:  " + fmt(resilient))

        # S4
        say("\nS4 top seats: API tokens vs subscription (one plan per seat)")
        say("  capped = seat stops at the plan's weekly hours; hybrid = plan first, API past the cap")
        subs = {}
        for tag, r in (("best value", best_value), ("best throughput", best_tp)):
            rows = sub_modes(pool, r["six"], r, SEEDS_SCAN)
            subs[tag] = dict(six=r["six"], rows=rows, all_capped=all_top_capped(pool, r["six"], SEEDS_SCAN))
            say(f"  [{tag}] six at {r['ipw']:.1f} ideas/wk, API ${r['api_week']:.0f}/wk")
            say(f"    {'seat':<22} {'plan':<30} {'cap h':>5} {'busy h':>6} {'$/h':>5} {'API $/wk':>8} {'sub $/wk':>8} "
                f"{'hybrid $/wk':>11} {'b/e h':>5} {'subs':>4} {'capped i/wk':>11}")
            for x in rows:
                say(f"    {x['seat']:<22} {x['plan']:<30} {x['cap_h']:>5} {x['busy_h']:>6} {x['rate']:>5} {x['api_week']:>8} "
                    f"{x['sub_week']:>8} {x['hybrid_week']:>11} {x['breakeven_h']:>5} {x['subs_to_cover']:>4} {x['capped_ipw']:>11}")
            for k, v in subs[tag]["all_capped"].items():
                say(f"    all top seats on one 20x plan, {k} {v['caps']}: {v['ipw']:.1f} ideas/wk "
                    f"({v['ipw'] / r['ipw']:.0%} of uncapped)")

        # token-model sensitivity for the API bill
        say("\nS5 API bill sensitivity (best value six, $/idea)")
        global GEN_DUTY, IN_PER_OUT, CACHE_HIT
        saved = (GEN_DUTY, IN_PER_OUT, CACHE_HIT)
        sens = {}
        for lbl, (d, io, ch) in {"base (0.25, 30, 0.90)": saved, "lean (0.15, 15, 0.95)": (0.15, 15, 0.95),
                                 "heavy (0.40, 60, 0.80)": (0.40, 60, 0.80)}.items():
            GEN_DUTY, IN_PER_OUT, CACHE_HIT = d, io, ch
            wk = sum(best_value["busy"][n] * usd_per_busy_hour(C[n]) for n in best_value["six"])
            wk_top = sum(best_value["busy"][n] * usd_per_busy_hour(C[n]) for n in best_value["six"][:3])
            sens[lbl] = dict(api_week=round(wk), top_week=round(wk_top), usd_idea=round(wk / best_value["ipw"], 1))
            say(f"  {lbl:<24} ${wk:7.0f}/wk  (top seats ${wk_top:6.0f})  ${wk / best_value['ipw']:6.1f}/idea")
        GEN_DUTY, IN_PER_OUT, CACHE_HIT = saved

    (HERE / "select6_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(dict(candidates=C, s1=s1[:30], s2=s2[:40], finalists=fin, best_throughput=best_tp, best_value=best_value,
                   resilient=resilient, subscriptions=subs, sensitivity=sens, plans=PLANS,
                   assumptions=dict(GEN_DUTY=GEN_DUTY, IN_PER_OUT=IN_PER_OUT, CACHE_HIT=CACHE_HIT, CACHE_PRICE=CACHE_PRICE,
                                    sizing=SIZING, quality=QUALITY)),
              open(HERE / "select6.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
