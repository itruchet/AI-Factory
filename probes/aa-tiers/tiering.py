"""How many natural tiers do coding models fall into?

Data: Artificial Analysis Coding Index for every scored model configuration
(model x reasoning effort), snapshot 2026-09-09, from the public daily mirror
github.com/Maicarons/artificial-analysis-leaderboards (prices from its
2026-09-26 snapshot). See aa_coding_2026-09-09.csv.

Five independent methods estimate the number of groups k in the 1-D scores:
  GMM-BIC     Gaussian mixture; k with the lowest Bayesian information criterion
  Jenks-GVF   Fisher-Jenks optimal breaks; smallest k whose goodness of variance
              fit reaches 0.90 (and 0.95)
  KDE modes   number of peaks in a kernel density estimate (Silverman, Scott)
  Gap         Tibshirani gap statistic with k-means and 100 uniform references
  Silhouette  k-means k with the highest mean silhouette

Each runs on three views, so the answer does not hinge on one filter:
  all         all 256 scored configurations
  current     configurations not marked deprecated
  per model   best-scoring configuration of each base model

Run: python3 probes/aa-tiers/tiering.py      (needs numpy, scipy, scikit-learn)
"""

from __future__ import annotations

import csv
import re
import statistics
from pathlib import Path

import numpy as np
from scipy.stats import gaussian_kde
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.mixture import GaussianMixture

HERE = Path(__file__).parent
DATA = HERE / "aa_coding_2026-09-09.csv"
K_MAX = 10


def load() -> list[dict]:
    rows = list(csv.DictReader(open(DATA)))
    for r in rows:
        r["coding_index"] = float(r["coding_index"])
        r["deprecated"] = r["deprecated"] == "True"
        r["base"] = re.sub(r"\s*\(.*\)\s*$", "", r["name"]).strip()
    return [r for r in rows if r["coding_index"] > 0]      # one row scores 0: unscored


def views(rows):
    best = {}
    for r in rows:
        if r["base"] not in best or r["coding_index"] > best[r["base"]]["coding_index"]:
            best[r["base"]] = r
    return {
        "all": rows,
        "current": [r for r in rows if not r["deprecated"]],
        "per model": list(best.values()),
    }


def jenks(x: np.ndarray, k: int) -> tuple[list[float], float]:
    """Exact Fisher-Jenks breaks by dynamic programming. Returns (upper bounds, GVF)."""
    x = np.sort(x)
    n = len(x)
    cs, cs2 = np.concatenate([[0], np.cumsum(x)]), np.concatenate([[0], np.cumsum(x * x)])

    def ssd(i, j):  # sum of squared deviations of x[i:j]
        s, s2, m = cs[j] - cs[i], cs2[j] - cs2[i], j - i
        return s2 - s * s / m
    cost = np.full((k + 1, n + 1), np.inf)
    back = np.zeros((k + 1, n + 1), dtype=int)
    cost[0][0] = 0
    for c in range(1, k + 1):
        for j in range(c, n + 1):
            best, arg = np.inf, 0
            for i in range(c - 1, j):
                v = cost[c - 1][i] + ssd(i, j)
                if v < best:
                    best, arg = v, i
            cost[c][j], back[c][j] = best, arg
    bounds, j = [], n
    for c in range(k, 0, -1):
        i = back[c][j]
        bounds.append(float(x[j - 1]))
        j = i
    gvf = 1 - cost[k][n] / ssd(0, n)
    return sorted(bounds), float(gvf)


def kde_modes(x: np.ndarray, bw: str) -> int:
    grid = np.linspace(x.min() - 5, x.max() + 5, 2000)
    y = gaussian_kde(x, bw_method=bw)(grid)
    return int(np.sum((y[1:-1] > y[:-2]) & (y[1:-1] > y[2:])))


def gap_statistic(x: np.ndarray, refs: int = 100, seed: int = 0) -> int:
    rng = np.random.default_rng(seed)
    X = x.reshape(-1, 1)

    def wk(data, k):
        km = KMeans(n_clusters=k, n_init=10, random_state=0).fit(data)
        return np.log(km.inertia_ + 1e-12)
    gaps, sks = [], []
    for k in range(1, K_MAX + 1):
        ref = [wk(rng.uniform(x.min(), x.max(), size=(len(x), 1)), k) for _ in range(refs)]
        gaps.append(np.mean(ref) - wk(X, k))
        sks.append(np.std(ref) * np.sqrt(1 + 1 / refs))
    for k in range(1, K_MAX):
        if gaps[k - 1] >= gaps[k] - sks[k]:
            return k
    return K_MAX


def analyse(x: np.ndarray) -> dict:
    X = x.reshape(-1, 1)
    bics = [GaussianMixture(k, n_init=10, random_state=0).fit(X).bic(X) for k in range(1, K_MAX + 1)]
    gvf = {k: jenks(x, k)[1] for k in range(2, K_MAX + 1)}
    sil = {k: silhouette_score(X, KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X))
           for k in range(2, K_MAX + 1)}
    return {
        "n": len(x),
        "gmm_bic": int(np.argmin(bics)) + 1,
        "jenks_90": min(k for k, g in gvf.items() if g >= 0.90),
        "jenks_95": min(k for k, g in gvf.items() if g >= 0.95),
        "kde_silverman": kde_modes(x, "silverman"),
        "kde_scott": kde_modes(x, "scott"),
        "gap": gap_statistic(x),
        "silhouette": max(sil, key=sil.get),
        "gvf": gvf,
    }


def tiers(x: np.ndarray, k: int) -> list[tuple[float, float, int]]:
    """Jenks tiers, highest first: (low, high, count)."""
    bounds, _ = jenks(x, k)
    xs = np.sort(x)
    out, lo = [], xs.min()
    for b in bounds:
        members = xs[(xs >= lo) & (xs <= b)]
        out.append((float(members.min()), float(members.max()), len(members)))
        above = xs[xs > b]
        lo = above.min() if len(above) else b
    return out[::-1]


FOCUS = ["GPT-5.6 Sol", "Claude Opus 5", "Claude Fable 5.1", "GPT-6 Astra", "GPT-5.6 Terra", "GPT-5.6 Luna",
         "MiMo-V2.5-Pro", "MiMo-V2.5", "Qwen3.8 27B", "Qwen3 Coder Next", "Qwen3.8 Max"]

if __name__ == "__main__":
    rows = load()
    results = {}
    print("Number of natural tiers suggested by each method\n")
    print(f"  {'view':<10} {'n':>4} {'GMM-BIC':>8} {'Jenks .90':>10} {'Jenks .95':>10} {'KDE Silv.':>10} "
          f"{'KDE Scott':>10} {'Gap':>5} {'Silhouette':>11}")
    for name, rs in views(rows).items():
        x = np.array([r["coding_index"] for r in rs])
        a = analyse(x)
        results[name] = a
        print(f"  {name:<10} {a['n']:>4} {a['gmm_bic']:>8} {a['jenks_90']:>10} {a['jenks_95']:>10} "
              f"{a['kde_silverman']:>10} {a['kde_scott']:>10} {a['gap']:>5} {a['silhouette']:>11}")
    votes = [v for a in results.values() for k, v in a.items() if k not in ("n", "gvf")]
    print(f"\n  all votes: {sorted(votes)}  median {statistics.median(votes)}")
    print("\n  Jenks goodness of variance fit by k (current view):")
    print("   " + "  ".join(f"k={k}: {g:.3f}" for k, g in results["current"]["gvf"].items()))

    x = np.array([r["coding_index"] for r in views(rows)["current"]])
    for k in (3, 4, 5, 6):
        print(f"\n  {k} tiers on current configurations (Jenks breaks), highest first:")
        for i, (lo, hi, n) in enumerate(tiers(x, k), 1):
            print(f"    T{i}: {lo:5.1f} - {hi:5.1f}   {n:3d} configurations")

    print("\n  Where the Factory's models sit (all scored configurations):")
    for key in FOCUS:
        hits = sorted((r for r in rows if r["base"] == key), key=lambda r: -r["coding_index"])
        if hits:
            span = f"{hits[-1]['coding_index']:.1f}-{hits[0]['coding_index']:.1f}" if len(hits) > 1 else f"{hits[0]['coding_index']:.1f}"
            print(f"    {key:<20} {span:>12}  ({len(hits)} effort levels)")
