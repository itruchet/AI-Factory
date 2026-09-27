"""Tests for the allocation kernel. Run: python3 -m unittest discover -s kernel"""

import unittest

from allocation import (
    DETERMINISTIC, Config, Option, Posterior, TaskClass, assign, cascade_cost,
    neyman_allocation, over_provisioning, solve_allocation, sprt, window_options,
)

CODE = Config("code", DETERMINISTIC)
LOCAL = Config("local", "gpu")
MID = Config("mid", "mid_sub")
FRONTIER = Config("frontier", "frontier_sub")

SIMPLE = TaskClass("simple", "market", value=1.0, fail_cost=0.5, tau=0.6, z=0.0)
HARD = TaskClass("hard", "planning", value=10.0, fail_cost=20.0, tau=0.8, z=1.0)


def cell(successes: int, failures: int, tokens: float) -> Posterior:
    post = Posterior()
    for _ in range(successes):
        post.observe(True, tokens)
    for _ in range(failures):
        post.observe(False, tokens)
    return post


class PosteriorTest(unittest.TestCase):
    def test_observe_and_decay(self):
        post = cell(8, 2, 100)
        self.assertAlmostEqual(post.mean, 9 / 12)
        post.decay(0.5)
        self.assertAlmostEqual(post.alpha, 5.0)
        self.assertAlmostEqual(post.beta, 2.0)

    def test_prior_strength_is_weak(self):
        prior = Posterior.from_prior(0.9, strength=4)
        for _ in range(20):
            prior.observe(False, 10)
        self.assertLess(prior.mean, 0.3)  # evidence overrides a benchmark prior quickly


class AllocationTest(unittest.TestCase):
    def setUp(self):
        self.posteriors = {
            ("local", "simple"): cell(90, 10, 2_000),
            ("mid", "simple"): cell(95, 5, 3_000),
            ("frontier", "simple"): cell(98, 2, 8_000),
            ("local", "hard"): cell(3, 17, 20_000),
            ("mid", "hard"): cell(30, 30, 30_000),
            ("frontier", "hard"): cell(90, 10, 60_000),
        }
        self.configs = [LOCAL, MID, FRONTIER]

    def test_quality_floor_excludes_insufficient_configs(self):
        opts = window_options([SIMPLE, HARD], self.configs, self.posteriors)
        self.assertEqual([o.config.name for o in opts["hard"]], ["frontier"])
        self.assertEqual(len(opts["simple"]), 3)

    def test_scarce_frontier_is_kept_for_hard_work(self):
        opts = window_options([SIMPLE, HARD], self.configs, self.posteriors)
        cap = {"gpu": 1e9, "mid_sub": 1e9, "frontier_sub": 55 * 60_000}  # barely covers hard work
        alloc = solve_allocation([SIMPLE, HARD], {"simple": 500, "hard": 50}, opts, cap)
        self.assertEqual(alloc.shares["hard"], {"frontier": 1.0})
        self.assertLess(alloc.shares["simple"].get("frontier", 0.0), 0.1)
        self.assertLessEqual(alloc.usage["frontier_sub"], cap["frontier_sub"] * 1.05)

    def test_perishing_frontier_capacity_absorbs_simple_work(self):
        # Surplus that would expire at reset has zero opportunity cost, so using
        # it on simple work is not waste. The price stays at zero.
        opts = window_options([SIMPLE, HARD], self.configs, self.posteriors)
        cap = {"gpu": 1e9, "mid_sub": 1e9, "frontier_sub": 1_000 * 60_000}
        alloc = solve_allocation([SIMPLE, HARD], {"simple": 500, "hard": 50}, opts, cap)
        self.assertEqual(alloc.prices["frontier_sub"], 0.0)
        self.assertEqual(alloc.shares["simple"], {"frontier": 1.0})

    def test_scarcity_raises_price_and_surplus_zeroes_it(self):
        opts = window_options([HARD], self.configs, self.posteriors)
        scarce = solve_allocation([HARD], {"hard": 50}, opts, {"frontier_sub": 10 * 60_000})
        surplus = solve_allocation([HARD], {"hard": 50}, opts, {"frontier_sub": 1_000 * 60_000})
        self.assertGreater(scarce.prices["frontier_sub"], 0.0)
        self.assertEqual(surplus.prices["frontier_sub"], 0.0)

    def test_no_eligible_config_escalates(self):
        weak = {("local", "hard"): cell(1, 9, 1_000)}
        opts = window_options([HARD], [LOCAL], weak)
        alloc = solve_allocation([HARD], {"hard": 5}, opts, {"gpu": 1e9})
        self.assertEqual(alloc.unserved, ["hard"])

    def test_deterministic_code_is_free_and_preferred_when_sufficient(self):
        checks = TaskClass("checks", "release", value=1.0, fail_cost=5.0, tau=0.95, z=1.0)
        posts = {("code", "checks"): cell(500, 0, 0), ("frontier", "checks"): cell(99, 1, 5_000)}
        opts = window_options([checks], [CODE, FRONTIER], posts)
        alloc = solve_allocation([checks], {"checks": 100}, opts, {"frontier_sub": 1e9})
        self.assertEqual(alloc.shares["checks"], {"code": 1.0})


class TimeCostTest(unittest.TestCase):
    def test_time_cost_keeps_simple_work_off_slow_configs_under_surplus(self):
        quick = TaskClass("quick", "market", value=2.0, fail_cost=3.0, tau=0.6, z=0.0, time_cost=5e-5)
        posts = {("mid", "quick"): cell(90, 10, 8_000), ("frontier", "quick"): cell(96, 4, 20_000)}
        opts = window_options([quick], [MID, FRONTIER], posts)
        alloc = solve_allocation([quick], {"quick": 100}, opts, {"mid_sub": 1e9, "frontier_sub": 1e9})
        self.assertEqual(alloc.prices["frontier_sub"], 0.0)       # capacity is spare...
        self.assertEqual(alloc.shares["quick"], {"mid": 1.0})     # ...yet time cost decides


class AssignTest(unittest.TestCase):
    def setUp(self):
        self.posts = {("mid", "simple"): cell(85, 15, 3_000), ("frontier", "simple"): cell(94, 6, 3_000)}
        self.opts = window_options([SIMPLE], [MID, FRONTIER], self.posts)["simple"]

    def test_assign_is_reproducible_and_reports_propensity(self):
        first = assign(SIMPLE, self.opts, self.posts, {}, "card-42", "charter-abc")
        self.assertEqual(first, assign(SIMPLE, self.opts, self.posts, {}, "card-42", "charter-abc"))
        self.assertGreater(first[1], 0.0)
        self.assertLessEqual(first[1], 1.0)

    def test_exploration_spreads_across_tasks(self):
        picks = [assign(SIMPLE, self.opts, self.posts, {}, f"card-{i}", "c")[0] for i in range(300)]
        self.assertGreater(picks.count("frontier"), 200)  # better record wins most tasks...
        self.assertGreater(picks.count("mid"), 0)          # ...but the other still gets explored


class EstimatorTest(unittest.TestCase):
    def test_cascade_cost(self):
        cost, unresolved = cascade_cost([(1.0, 0.8), (10.0, 0.9)])
        self.assertAlmostEqual(cost, 1.0 + 0.2 * 10.0)
        self.assertAlmostEqual(unresolved, 0.2 * 0.1)

    def test_neyman_puts_more_audit_where_variance_is_high(self):
        n = neyman_allocation({"R1": (1000, 0.05, 1.0), "R2": (200, 0.3, 1.0)}, budget=60)
        self.assertGreater(n["R2"] / 200, n["R1"] / 1000)

    def test_sprt(self):
        self.assertEqual(sprt(0, 60, p0=0.02, p1=0.10), "promote")
        self.assertEqual(sprt(6, 20, p0=0.02, p1=0.10), "reject")
        self.assertEqual(sprt(1, 10, p0=0.02, p1=0.10), "continue")

    def test_over_provisioning(self):
        opts = {"simple": [Option(LOCAL, 0.9, 2_000), Option(FRONTIER, 0.98, 8_000)]}
        waste = over_provisioning([(SIMPLE, "frontier", 8_000), (SIMPLE, "local", 2_000)], opts)
        self.assertAlmostEqual(waste, 6_000 / 10_000)


if __name__ == "__main__":
    unittest.main()
