"""Worked example of the allocation kernel across institutions.

ALL NUMBERS ARE SYNTHETIC. They illustrate the mechanics, not real model
performance. Replace them with Ledger outcomes and real subscription terms.

Run: python3 kernel/demo.py
"""

from collections import Counter

from allocation import DETERMINISTIC, Config, Posterior, TaskClass, assign, solve_allocation, window_options

CONFIGS = [
    Config("code", DETERMINISTIC),
    Config("qwen-local", "gpu"),
    Config("mimo", "mimo_sub"),
    Config("gpt-high", "openai_sub"),
    Config("claude-high", "claude_sub"),
]

# Charter economics per task class: value, cost of failure, quality floor, floor confidence,
# and time cost per token (only where latency matters to the institution).
TASKS = [
    TaskClass("release.checks", "release", value=1, fail_cost=50, tau=0.97, z=2.0),
    TaskClass("court.review.R1", "court", value=3, fail_cost=15, tau=0.80, z=1.0, time_cost=2e-5),
    TaskClass("market.card.small", "market", value=2, fail_cost=3, tau=0.60, z=0.0, time_cost=5e-5),
    TaskClass("market.card.large", "market", value=8, fail_cost=12, tau=0.70, z=0.5),
    TaskClass("planning.decompose", "planning", value=30, fail_cost=60, tau=0.80, z=1.0),
    TaskClass("audit.replicate", "audit", value=5, fail_cost=10, tau=0.75, z=1.0),
]

# Synthetic (successes, failures, mean tokens) per cell; missing cell = not enrolled.
HISTORY = {
    ("code", "release.checks"): (400, 0, 0),
    ("qwen-local", "release.checks"): (180, 20, 1_500),
    ("claude-high", "release.checks"): (99, 1, 6_000),
    ("qwen-local", "court.review.R1"): (40, 40, 4_000),
    ("mimo", "court.review.R1"): (85, 15, 6_000),
    ("gpt-high", "court.review.R1"): (93, 7, 15_000),
    ("claude-high", "court.review.R1"): (94, 6, 15_000),
    ("qwen-local", "market.card.small"): (160, 40, 5_000),
    ("mimo", "market.card.small"): (180, 20, 8_000),
    ("gpt-high", "market.card.small"): (95, 5, 20_000),
    ("claude-high", "market.card.small"): (96, 4, 20_000),
    ("qwen-local", "market.card.large"): (10, 30, 30_000),
    ("mimo", "market.card.large"): (60, 40, 40_000),
    ("gpt-high", "market.card.large"): (85, 15, 80_000),
    ("claude-high", "market.card.large"): (88, 12, 80_000),
    ("mimo", "planning.decompose"): (5, 5, 50_000),
    ("gpt-high", "planning.decompose"): (18, 2, 120_000),
    ("claude-high", "planning.decompose"): (19, 1, 120_000),
    ("mimo", "audit.replicate"): (40, 10, 20_000),
    ("gpt-high", "audit.replicate"): (45, 5, 40_000),
    ("claude-high", "audit.replicate"): (46, 4, 40_000),
}

DEMAND = {  # tasks per window
    "release.checks": 200, "court.review.R1": 150, "market.card.small": 300,
    "market.card.large": 60, "planning.decompose": 4, "audit.replicate": 20,
}


def run(label: str, capacity: dict[str, float]) -> None:
    posteriors = {}
    for key, (s, f, tokens) in HISTORY.items():
        post = Posterior()
        for _ in range(s):
            post.observe(True, tokens)
        for _ in range(f):
            post.observe(False, tokens)
        posteriors[key] = post
    options = window_options(TASKS, CONFIGS, posteriors)
    alloc = solve_allocation(TASKS, DEMAND, options, capacity)
    print(f"\n== {label} ==   (share of tasks assigned per config, 200 seeded draws per class)")
    for task in TASKS:
        if not options[task.name]:
            print(f"  {task.name:<20} ESCALATE (no config meets floor)")
            continue
        picks = Counter(assign(task, options[task.name], posteriors, alloc.prices, label, str(i))[0] for i in range(200))
        print(f"  {task.name:<20} " + ", ".join(f"{c} {n / 200:.0%}" for c, n in sorted(picks.items())))
    for r, cap in capacity.items():
        print(f"  price[{r}] = {alloc.prices[r]:.6f}   usage {alloc.usage[r] / cap:.0%} of capacity")


if __name__ == "__main__":
    base = {"gpu": 5e6, "mimo_sub": 2e7, "openai_sub": 4e6, "claude_sub": 4e6}
    run("frontier scarce", base)
    run("frontier near reset with surplus", {**base, "openai_sub": 4e7, "claude_sub": 4e7})
