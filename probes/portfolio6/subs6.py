"""Top seats on API tokens only vs subscriptions, for the chosen six and the premium alternatives.

Three ways to pay for a top seat:
  api      API tokens only; the seat works whenever there is work
  capped   one subscription per seat and nothing else; the seat idles once the
           plan's weekly hours are used, until the weekly reset
  hybrid   one subscription per seat, API tokens past the cap (no idle time);
           a plan is bought only where it is cheaper than API alone

Seats whose vendor sells no subscription in PLANS stay on the API in every mode.
Plan hours are ranges (select6.PLANS): community-reported for Claude Max, assumed
by analogy for ChatGPT Pro and Google AI Ultra. Fable 5.1 may use at most half
of a Max plan's weekly usage, so a Fable seat gets half the hours.

Run: python3 probes/portfolio6/subs6.py   (after robust6.py; about 2 minutes)
"""

from __future__ import annotations

import json
from multiprocessing import Pool
from pathlib import Path

import select6 as s
from robust6 import ASTRA, FABLE, GEMINI, MUSE, OPUS, SOL

HERE = Path(__file__).parent
SEEDS = 12
PLAN_20X = {"Anthropic": "Claude Max 20x ($200)", "OpenAI": "ChatGPT Pro 20x ($200)", "Google": "Google AI Ultra 20x ($199.99)"}
PLAN_5X = {"Anthropic": "Claude Max 5x ($100)", "OpenAI": "ChatGPT Pro 5x ($100)", "Google": "Google AI Ultra 5x ($99.99)"}


def plan_for(name, plans):
    p = plans.get(s.C[name]["vendor"])
    return (p, s.PLANS[p]) if p else (None, None)


def seat_cap(name, plan, level):
    lo, hi = plan["hours"]
    h = lo if level == "low" else hi
    return h / 2 if name == FABLE else h


def main():
    chosen = json.load(open(HERE / "robust6.json"))
    mid = [r for r in chosen if r["six"][0] == OPUS and MUSE in r["six"] and GEMINI in r["six"]]
    mid = min(mid, key=lambda r: r["scenarios"]["base"]["usd_idea"])["six"][3:]
    sixes = {
        "chosen: Opus 5.5 + Muse Spark 1.3 + Gemini 3.8 Flash": [OPUS, MUSE, GEMINI] + mid,
        "all-subscription trio: Opus 5.5 + GPT-6 Sol + Gemini 3.8 Flash": [OPUS, SOL, GEMINI] + mid,
        "premium trio: Fable 5.1 + GPT-6 Astra + Gemini 3.8 Flash": [FABLE, ASTRA, GEMINI] + mid,
    }
    lines = [f"TOKENS vs SUBSCRIPTIONS for the top seats ({SEEDS} seeds; mid seats on API throughout: "
             + " + ".join(s.label(n) for n in mid) + ")"]
    out = {}
    with Pool() as pool:
        for title, six in sixes.items():
            base = s.evaluate(pool, [six], SEEDS)[0]
            mid_api = sum(base["busy"][n] * s.usd_per_busy_hour(s.C[n]) for n in six[3:])
            lines.append(f"\n[{title}]  {base['ipw']:.1f} ideas/wk uncapped; mid seats ${mid_api:.0f}/wk on API")
            lines.append(f"  {'seat':<24} {'busy h/wk':>9} {'$/busy h':>8} {'API $/wk':>8}   {'20x plan':<30} {'b/e h':>5} "
                         f"{'plan h':>7} {'plans to cover':>14} {'hybrid $/wk':>12}")
            seats = []
            for n in six[:3]:
                rate = s.usd_per_busy_hour(s.C[n])
                h = base["busy"][n]
                pname, plan = plan_for(n, PLAN_20X)
                row = dict(seat=s.label(n), busy_h=round(h, 1), rate=round(rate, 2), api_week=round(h * rate))
                if plan:
                    sub_w = plan["usd"] / s.WEEKS_PER_MONTH
                    lo, hi = seat_cap(n, plan, "low"), seat_cap(n, plan, "high")
                    row.update(plan=pname, sub_week=round(sub_w), breakeven_h=round(sub_w / rate, 1), plan_h=(lo, hi),
                               plans_to_cover=(-(-h // hi), -(-h // lo)),
                               # the Ledger buys a plan only where it pays: never dearer than API alone
                               hybrid_week=(round(min(h * rate, sub_w + max(0, h - hi) * rate)),
                                            round(min(h * rate, sub_w + max(0, h - lo) * rate))))
                    lines.append(f"  {row['seat']:<24} {h:9.0f} {rate:8.2f} {h * rate:8.0f}   {pname:<30} {row['breakeven_h']:5.1f} "
                                 f"{lo:3.0f}-{hi:<3.0f} {int(row['plans_to_cover'][0]):>6}-{int(row['plans_to_cover'][1]):<7} "
                                 f"{row['hybrid_week'][0]:>5}-{row['hybrid_week'][1]:<6}")
                else:
                    lines.append(f"  {row['seat']:<24} {h:9.0f} {rate:8.2f} {h * rate:8.0f}   no subscription: API only")
                seats.append(row)
            api_top = sum(r["api_week"] for r in seats)
            hyb = [sum(r.get("hybrid_week", (r["api_week"], r["api_week"]))[i] for r in seats) for i in (0, 1)]
            modes = dict(api=dict(ipw=round(base["ipw"], 1), top_week=api_top))
            modes["hybrid"] = dict(ipw=round(base["ipw"], 1), top_week=(hyb[0], hyb[1]))
            for level in ("low", "high"):
                caps = {}
                for n in six[:3]:
                    pname, plan = plan_for(n, PLAN_20X)
                    if plan:
                        caps[n] = seat_cap(n, plan, level)
                capped = s.evaluate(pool, [six], SEEDS, caps=caps)[0]
                sub_cost = sum(round(s.PLANS[plan_for(n, PLAN_20X)[0]]["usd"] / s.WEEKS_PER_MONTH) for n in caps)
                api_rest = sum(capped["busy"][n] * s.usd_per_busy_hour(s.C[n]) for n in six[:3] if n not in caps)
                modes[f"capped-{level}"] = dict(ipw=round(capped["ipw"], 1), top_week=round(sub_cost + api_rest),
                                                share=round(capped["ipw"] / base["ipw"], 3))
            lines.append(f"  top seats, API only:          ${api_top:5.0f}/wk  (${api_top * s.WEEKS_PER_MONTH:6.0f}/month)  "
                         f"{base['ipw']:.1f} ideas/wk")
            lines.append(f"  top seats, hybrid (20x plan): ${hyb[0]:5.0f}-{hyb[1]:<5.0f}/wk (${hyb[0] * s.WEEKS_PER_MONTH:6.0f}-"
                         f"{hyb[1] * s.WEEKS_PER_MONTH:<6.0f}/month)  {base['ipw']:.1f} ideas/wk  "
                         f"saves {1 - hyb[1] / api_top:.0%}-{1 - hyb[0] / api_top:.0%}")
            for level in ("low", "high"):
                m = modes[f"capped-{level}"]
                lines.append(f"  top seats, plan only ({level} cap): ${m['top_week']:5.0f}/wk (${m['top_week'] * s.WEEKS_PER_MONTH:6.0f}/month)  "
                             f"{m['ipw']:.1f} ideas/wk ({m['share']:.0%} of uncapped)")
            out[title] = dict(six=six, ipw=base["ipw"], busy=base["busy"], mid_api_week=round(mid_api), seats=seats, modes=modes)
    first = next(iter(out.values()))
    lines.append("\nAPI bill sensitivity to the token model, first six, all seats on API:")
    saved = (s.GEN_DUTY, s.IN_PER_OUT, s.CACHE_HIT)
    for lbl, (d, io, ch) in {"lean (0.15, 15, 0.95)": (0.15, 15, 0.95), "base (0.25, 30, 0.90)": saved,
                             "heavy (0.40, 60, 0.80)": (0.40, 60, 0.80)}.items():
        s.GEN_DUTY, s.IN_PER_OUT, s.CACHE_HIT = d, io, ch
        wk = sum(first["busy"][n] * s.usd_per_busy_hour(s.C[n]) for n in first["six"])
        lines.append(f"  {lbl:<24} ${wk:6.0f}/wk  ${wk * s.WEEKS_PER_MONTH:7.0f}/month  ${wk / first['ipw']:5.1f}/idea")
    s.GEN_DUTY, s.IN_PER_OUT, s.CACHE_HIT = saved
    print("\n".join(lines))
    (HERE / "subs6_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "subs6.json", "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
