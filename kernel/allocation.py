"""Ledger allocation kernel.

Pure functions over Ledger outcomes. No model calls, no hidden state, no
discretion: every output is reproducible from (ledger rows, charter params,
seed). This is the "probabilistic determinism" layer of the constitutional
architecture (docs/architecture/constitutional-factory.md, section 12).

Pipeline:
    outcomes  -> Posterior per (config, task class)          [Bayesian update]
    posterior -> quality floor filter per task class         [minimum sufficient intelligence]
    eligible  -> Lagrangian dual over capacity, per window   [shadow prices, expected shares]
    per task  -> seeded Thompson sample at window prices     [exploration + assignment,
                                                              with recorded propensity]

Standard library only.
"""

from __future__ import annotations

import hashlib
import math
import random
from collections import defaultdict
from dataclasses import dataclass

DETERMINISTIC = "deterministic"  # resource name for plain code: no capacity limit, no tokens


# ---------------------------------------------------------------------------
# Posterior: what the Ledger has observed about one (config, task class) cell
# ---------------------------------------------------------------------------

@dataclass
class Posterior:
    """Beta posterior on success probability plus a running mean of token use."""

    alpha: float = 1.0
    beta: float = 1.0
    tokens_n: int = 0
    tokens_mean: float = 0.0

    @classmethod
    def from_prior(cls, mean: float, strength: float) -> "Posterior":
        """Benchmark-derived prior: `strength` pseudo-observations centred on `mean`."""
        return cls(alpha=1.0 + mean * strength, beta=1.0 + (1.0 - mean) * strength)

    def observe(self, success: bool, tokens: float) -> None:
        if success:
            self.alpha += 1.0
        else:
            self.beta += 1.0
        self.tokens_n += 1
        self.tokens_mean += (tokens - self.tokens_mean) / self.tokens_n

    def decay(self, factor: float) -> None:
        """Shrink evidence toward the uniform prior; handles provider model drift."""
        self.alpha = 1.0 + (self.alpha - 1.0) * factor
        self.beta = 1.0 + (self.beta - 1.0) * factor

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    @property
    def sd(self) -> float:
        a, b = self.alpha, self.beta
        return math.sqrt(a * b / ((a + b) ** 2 * (a + b + 1.0)))

    def lower(self, z: float) -> float:
        return self.mean - z * self.sd


# ---------------------------------------------------------------------------
# Task classes and configurations
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Config:
    """An execution configuration: model x effort, drawing on one capacity resource."""

    name: str
    resource: str


@dataclass(frozen=True)
class TaskClass:
    """A bucket of work inside one institution, with charter-set economics."""

    name: str
    institution: str
    value: float        # value points of a success
    fail_cost: float    # rework + downstream + escape cost of a failure, in value points
    tau: float          # quality floor: minimum acceptable success probability
    z: float            # floor confidence: 0 = posterior mean, >0 = demand a lower bound
    time_cost: float = 0.0  # value points per token of elapsed time (latency proxy), set by charter


@dataclass(frozen=True)
class Option:
    config: Config
    p: float            # posterior mean success probability
    tokens: float       # expected tokens per task


def seed_for(*parts: str) -> int:
    """Stable seed from ledger identifiers, so any draw can be replayed."""
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    return int(digest[:16], 16)


def net_value(task: TaskClass, option: Option, price: float) -> float:
    """Expected value of success, minus expected cost of failure, minus the
    capacity it consumes (shadow price) and the time it takes (charter rate).

    Under a subscription every model's marginal cash cost is zero until its
    capacity binds. The time term is what makes over-qualified configs lose on
    simple work even when capacity is spare.
    """
    cost_per_token = price + task.time_cost
    return option.p * task.value - (1.0 - option.p) * task.fail_cost - cost_per_token * option.tokens


def window_options(
    tasks: list[TaskClass],
    configs: list[Config],
    posteriors: dict[tuple[str, str], Posterior],
) -> dict[str, list[Option]]:
    """Apply each task class's quality floor. Only sufficient configs remain.

    With z > 0 the floor uses a lower credible bound, so a config needs both a
    good record and enough of it. With z = 0 the posterior mean is enough.
    """
    options: dict[str, list[Option]] = {}
    for task in tasks:
        eligible = []
        for config in configs:
            post = posteriors.get((config.name, task.name))
            if post is None:
                continue  # config not enrolled for this class by charter
            if post.lower(task.z) >= task.tau:
                eligible.append(Option(config, post.mean, post.tokens_mean))
        options[task.name] = eligible
    return options


# ---------------------------------------------------------------------------
# Capacity: shadow prices are the dual variables of the capacity constraints
# ---------------------------------------------------------------------------

@dataclass
class Allocation:
    prices: dict[str, float]                    # value points per token, per resource
    shares: dict[str, dict[str, float]]         # task class -> config name -> share
    usage: dict[str, float]                     # expected tokens per resource
    unserved: list[str]                         # classes with no eligible config: escalate


def solve_allocation(
    tasks: list[TaskClass],
    demand: dict[str, float],
    options: dict[str, list[Option]],
    capacity: dict[str, float],
    iterations: int = 400,
    step: float = 0.5,
) -> Allocation:
    """Maximise expected net value subject to per-resource token capacity.

    Lagrangian relaxation with projected subgradient on the prices. Each
    iteration, every task class picks its best eligible config at current
    prices; prices rise on over-subscribed resources and fall toward zero on
    under-used ones. Averaging the choices over the second half of the run
    recovers fractional shares that respect capacity on average.

    A price of zero means the resource will not be exhausted this window:
    unused subscription capacity is perishing, so using it costs nothing.
    """
    by_name = {t.name: t for t in tasks}
    prices = {r: 0.0 for r in capacity}
    unserved = [name for name, opts in options.items() if not opts]
    active = {name: opts for name, opts in options.items() if opts}

    ratios = [by_name[n].value / o.tokens for n, opts in active.items() for o in opts if o.tokens > 0]
    scale = max(ratios, default=1.0)

    counts: dict[str, dict[str, int]] = {n: defaultdict(int) for n in active}
    burn_in = iterations // 2
    for it in range(1, iterations + 1):
        usage = {r: 0.0 for r in capacity}
        for name, opts in active.items():
            task = by_name[name]
            best = max(opts, key=lambda o: (net_value(task, o, prices.get(o.config.resource, 0.0)), o.config.name))
            if best.config.resource in usage:
                usage[best.config.resource] += demand[name] * best.tokens
            if it > burn_in:
                counts[name][best.config.name] += 1
        for r, cap in capacity.items():
            gradient = (usage[r] - cap) / cap
            prices[r] = max(0.0, prices[r] + scale * step / math.sqrt(it) * gradient)

    shares = {
        name: {cfg: c / (iterations - burn_in) for cfg, c in sorted(cfg_counts.items())}
        for name, cfg_counts in counts.items()
    }
    tokens_of = {(n, o.config.name): o.tokens for n, opts in active.items() for o in opts}
    resource_of = {o.config.name: o.config.resource for opts in active.values() for o in opts}
    usage = {r: 0.0 for r in capacity}
    for name, cfg_shares in shares.items():
        for cfg, share in cfg_shares.items():
            r = resource_of[cfg]
            if r in usage:
                usage[r] += demand[name] * share * tokens_of[(name, cfg)]
    return Allocation(prices=prices, shares=shares, usage=usage, unserved=unserved)


def assign(
    task: TaskClass,
    options: list[Option],
    posteriors: dict[tuple[str, str], Posterior],
    prices: dict[str, float],
    *seed_parts: str,
    mc_samples: int = 2000,
) -> tuple[str, float]:
    """Thompson sampling for one task at the window's shadow prices.

    Each eligible config's success probability is drawn from its posterior;
    the task goes to the highest net value. Uncertain configs sometimes draw
    high and receive work, so evidence accumulates where it is missing, and
    exploration fades as posteriors tighten. No tuned exploration rate.

    Returns (config name, propensity). The seed comes from Ledger identifiers,
    so the draw is replayable. The propensity is estimated by replaying the
    same computation `mc_samples` times under a derived seed, and is recorded
    so any alternative policy can be evaluated off-policy by inverse weighting.
    """
    def pick(rng: random.Random) -> str:
        def sampled_value(o: Option) -> float:
            post = posteriors[(o.config.name, task.name)]
            sampled = Option(o.config, rng.betavariate(post.alpha, post.beta), o.tokens)
            return net_value(task, sampled, prices.get(o.config.resource, 0.0))
        return max(options, key=lambda o: (sampled_value(o), o.config.name)).config.name

    choice = pick(random.Random(seed_for("assign", task.name, *seed_parts)))
    replay = random.Random(seed_for("propensity", task.name, *seed_parts))
    hits = sum(pick(replay) == choice for _ in range(mc_samples))
    return choice, max(hits, 1) / mc_samples


# ---------------------------------------------------------------------------
# Supporting estimators used by specific institutions
# ---------------------------------------------------------------------------

def cascade_cost(stages: list[tuple[float, float]]) -> tuple[float, float]:
    """Expected cost of trying cheaper configs first and escalating on failure.

    `stages` is [(cost, p_resolved_and_verified), ...] in escalation order.
    Only valid where a reliable verifier decides "resolved" (tests, invariants).
    Returns (expected cost, probability nothing resolves).
    """
    expected, p_reach = 0.0, 1.0
    for cost, p in stages:
        expected += p_reach * cost
        p_reach *= 1.0 - p
    return expected, p_reach


def neyman_allocation(strata: dict[str, tuple[int, float, float]], budget: int) -> dict[str, int]:
    """Audit sample sizes per stratum: n_h proportional to N_h * S_h / sqrt(c_h).

    `strata` maps name -> (population N_h, defect-rate std dev S_h, unit cost c_h).
    Minimises estimator variance for a fixed audit budget.
    """
    weights = {h: n * s / math.sqrt(c) for h, (n, s, c) in strata.items()}
    total = sum(weights.values()) or 1.0
    return {h: min(strata[h][0], max(1, round(budget * w / total))) for h, w in weights.items()}


def sprt(failures: int, trials: int, p0: float, p1: float, alpha: float = 0.05, beta: float = 0.10) -> str:
    """Wald sequential probability ratio test on a canary's failure rate.

    H0: failure rate <= p0 (acceptable). H1: failure rate >= p1 (regression).
    Returns 'promote', 'reject' or 'continue'. Criteria are fixed before data
    arrives, so no reviewer can rationalise a result after seeing it.
    """
    llr = failures * math.log(p1 / p0) + (trials - failures) * math.log((1 - p1) / (1 - p0))
    if llr <= math.log(beta / (1 - alpha)):
        return "promote"
    if llr >= math.log((1 - beta) / alpha):
        return "reject"
    return "continue"


def over_provisioning(assignments: list[tuple[TaskClass, str, float]], options: dict[str, list[Option]]) -> float:
    """Tokens spent above the cheapest config that met the quality floor.

    `assignments` is [(task class, config used, tokens used), ...]. Returns the
    share of all tokens that were avoidable. This is the "intelligence waste"
    KPI: high values mean capable models are doing work a cheaper one could do.
    """
    spent = avoidable = 0.0
    for task, _cfg, tokens in assignments:
        spent += tokens
        cheapest = min((o.tokens for o in options.get(task.name, [])), default=tokens)
        avoidable += max(0.0, tokens - cheapest)
    return avoidable / spent if spent else 0.0
