"""What-if: Xiaomi MiMo-V2.6-Pro-UltraSpeed in the six.

Xiaomi released the MiMo-V2.6 series on 22 Sep 2026: V2.6-Pro (on AA: Coding
Index 76.1*, 43 tokens/s, $0.435/$0.87), V2.6-Flash ($0.14/$0.28) and
V2.6-Pro-UltraSpeed ($4.35/$8.70; "same quality as Pro", vendor claims up to
10-20x Pro's output speed). AA has not scored Flash or UltraSpeed, so they are
not candidates yet (rule P6: a trial seat first). This probe asks whether
UltraSpeed would earn a seat if the speed claim holds: it replaces each seat of
the recommended six in turn, at 116, 430 and 860 tokens/s.

Run: python3 probes/portfolio6/whatif_mimo.py   (about 1 minute)
"""

from __future__ import annotations

from multiprocessing import Pool
from pathlib import Path

import select6 as s

HERE = Path(__file__).parent
SEEDS = 8
SIX = ["Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "Muse Spark 1.3 (xhigh)",
       "Gemini 3.8 Flash (high)", "DeepSeek V4.1 Flash (Reasoning, Max Effort)", "GPT-6 Luna (max)", "Ling 3.0 Flash"]
PRO = s.C["MiMo-V2.6-Pro"]


def ultraspeed(tps):
    name = f"MiMo-V2.6-Pro-UltraSpeed @{tps} t/s (what-if)"
    s.C[name] = dict(PRO, name=name, base="MiMo-V2.6-Pro-UltraSpeed", p_in=4.35, p_out=8.70,
                     price=(3 * 4.35 + 8.70) / 4, speed=float(tps))
    return name


def main():
    names = {tps: ultraspeed(tps) for tps in (116, 430, 860)}
    cands = [SIX] + [SIX[:i] + [n] + SIX[i + 1:] for n in names.values() for i in range(6)]
    with Pool() as pool:
        rows = s.evaluate(pool, cands, SEEDS)
    base = rows[0]
    lines = [f"MiMo-V2.6-Pro-UltraSpeed what-if ({SEEDS} seeds). Cost per busy hour: "
             + ", ".join(f"{t} t/s ${s.usd_per_busy_hour(s.C[n]):.2f}" for t, n in names.items()),
             f"  recommended six: {base['clean']:.1f} clean ideas/wk ({base['ipw']:.1f} ideas), ${base['usd_clean']:.1f}/clean idea",
             f"  {'replaces':<34} {'speed':>6} {'clean/wk':>8} {'vs six':>7} {'$/clean':>7}"]
    for r in rows[1:]:
        out = next(n for n in SIX if n not in r["six"])
        new = next(n for n in r["six"] if n not in SIX)
        lines.append(f"  {s.label(out):<34} {s.C[new]['speed']:6.0f} {r['clean']:8.1f} {r['clean'] / base['clean'] - 1:+7.0%} {r['usd_clean']:7.1f}")
    print("\n".join(lines))
    (HERE / "whatif_mimo_results.txt").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
