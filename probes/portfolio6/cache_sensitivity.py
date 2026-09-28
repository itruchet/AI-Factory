"""How much cost per task depends on the prompt-cache hit rate (r12.8).

Fresh context per pull (R24) and routing through an aggregator such as OpenRouter both put the cache hit rate at
risk. The token model reads 30 input tokens per output token, with 90% of input served from cache at 10% of list
price. This prints each menu model's cost per task at lower hit rates, as a multiple of the 90% baseline.

Run: python3 probes/portfolio6/cache_sensitivity.py
"""

import json
from pathlib import Path

import select6 as s

HERE = Path(__file__).parent
MENU = ["Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "GPT-5.6 Terra (max)",
        "Muse Spark 1.3 (xhigh)", "Gemini 3.8 Flash (high)", "DeepSeek V4.1 Flash (Reasoning, Max Effort)",
        "GPT-6 Luna (max)", "Ling 3.0 Flash"]
HITS = (0.9, 0.8, 0.7, 0.5, 0.0)


def main():
    saved = s.CACHE_HIT
    base = {n: s.usd_per_ref_hour(s.C[n]) for n in MENU}
    out, lines = {}, ["COST PER TASK AS A MULTIPLE OF THE 90% CACHE-HIT BASELINE (token model: 30 input per output, cache at 10%)"]
    for h in HITS:
        s.CACHE_HIT = h
        out[str(h)] = {n: round(s.usd_per_ref_hour(s.C[n]) / base[n], 3) for n in MENU}
        vals = out[str(h)].values()
        lines.append(f"  cache hits {h:4.0%}: x{min(vals):.2f} to x{max(vals):.2f}")
    s.CACHE_HIT = saved
    lines.append("  For comparison: OpenRouter's fee is 5.5% on bought credits (x1.055); BYOK carries no fee below $25,000 a month of list-price use [Unverified: third-party guides].")
    print("\n".join(lines))
    (HERE / "cache_sensitivity_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "cache_sensitivity.json", "w"), indent=1)


if __name__ == "__main__":
    main()
