"""Does any choice depend on the token model? (r12)

The API bill rests on assumed token use per working hour (lean / base / heavy;
see select6.py). If every model's cost moved by the same factor, the choice of
models, and every Scaler decision (which compares models' costs), would not
depend on the assumption: only the dollar totals would. This probe checks it.

Run: python3 probes/portfolio6/token_invariance.py
"""

from pathlib import Path

import select6 as s

TM = {"lean": (0.15, 15, 0.95), "base": (0.25, 30, 0.90), "heavy": (0.40, 60, 0.80)}


def main():
    names = list(dict.fromkeys(s.TOP_NAMES + s.MID_NAMES))
    names = [n for n in names if s.C[n]["price"] > 0]          # a local model costs nothing in every case
    cost = {}
    for tm, (d, io, ch) in TM.items():
        s.GEN_DUTY, s.IN_PER_OUT, s.CACHE_HIT = d, io, ch
        cost[tm] = {n: s.usd_per_busy_hour(s.C[n]) for n in names}
    lines = ["TOKEN-MODEL INVARIANCE: each model's $/busy hour under lean and heavy, relative to base"]
    for n in sorted(names, key=lambda n: cost["base"][n]):
        lines.append(f"  {s.label(n):<34} base ${cost['base'][n]:5.2f}/h   lean x{cost['lean'][n] / cost['base'][n]:.2f}"
                     f"   heavy x{cost['heavy'][n] / cost['base'][n]:.2f}")
    ratios = [cost[tm][n] / cost["base"][n] for tm in ("lean", "heavy") for n in names]
    order = {tm: sorted(names, key=lambda n: cost[tm][n]) for tm in TM}
    swaps = sum(1 for i in range(len(names)) if order["base"][i] != order["heavy"][i])
    lines.append(f"  factors: lean {min(r for r in ratios if r < 1):.2f}-{max(r for r in ratios if r < 1):.2f}, "
                 f"heavy {min(r for r in ratios if r > 1):.2f}-{max(r for r in ratios if r > 1):.2f}; "
                 f"cost ranking: {swaps} of {len(names)} positions differ between base and heavy "
                 f"({sum(1 for i in range(len(names)) if order['base'][i] != order['lean'][i])} for lean)")
    disp = {tm: max(abs(order["base"].index(n) - order[tm].index(n)) for n in names) for tm in ("lean", "heavy")}
    six = ["Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "Muse Spark 1.3 (xhigh)",
           "Gemini 3.8 Flash (high)", "DeepSeek V4.1 Flash (Reasoning, Max Effort)", "GPT-6 Luna (max)", "Ling 3.0 Flash"]
    six_order = {tm: [s.label(n) for n in sorted(six, key=lambda n: cost[tm][n])] for tm in TM}
    gap = max([cost["base"][b] / cost["base"][a] for tm in ("lean", "heavy") for a in names for b in names
               if cost["base"][a] < cost["base"][b] and cost[tm][a] > cost[tm][b]] or [1.0])
    lines.append(f"  largest move in the ranking: {disp['lean']} place(s) under lean, {disp['heavy']} under heavy; "
                 f"every pair that swaps was within {gap - 1:.0%} of each other at base")
    for tm in TM:
        lines.append(f"  recommended six, cheapest first ({tm}): " + ", ".join(six_order[tm]))
    print("\n".join(lines))
    (Path(__file__).parent / "token_invariance_results.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
