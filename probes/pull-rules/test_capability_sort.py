"""Checks that the rules sort models by capability (synthetic data).

Run: python3 -m unittest discover -s probes/pull-rules
"""

import statistics
import unittest

import capability_sort as cs

SEEDS = range(8)


def runs(policy):
    return [cs.run(policy, seed=s) for s in SEEDS]


def home_at(result, name, hour):
    return next(a for a in result["agents"] if a.name == name).homes[hour]


class CapabilitySortTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.static, cls.lean = runs("static"), runs("reserve")

    def test_more_capable_models_work_harder_cards(self):
        lean = statistics.mean(cs.alignment(r, cs.WEEK, cs.HOURS) for r in self.lean)
        static = statistics.mean(cs.alignment(r, cs.WEEK, cs.HOURS) for r in self.static)
        self.assertGreater(lean, 0.7)
        self.assertLess(static, 0.0)  # the inverted start stays inverted without the rules

    def test_inverted_start_is_sorted_within_a_week(self):
        # Claude and GPT start at tier 2, MiMo and Qwen at tier 4.
        for r in self.lean:
            self.assertGreaterEqual(home_at(r, "claude", cs.WEEK - 1), 4)
            self.assertGreaterEqual(home_at(r, "gpt", cs.WEEK - 1), 4)
            self.assertLessEqual(home_at(r, "qwen", 100), 3)

    def test_new_model_climbs_to_its_tier(self):
        # joins at hour 60 at tier 1; its true tier is 4, close to that tier's standard
        new = [next(a for a in r["agents"] if a.name == "newmodel") for r in self.lean]
        self.assertTrue(all(a.homes[cs.WEEK - 1] >= 3 for a in new))
        self.assertGreaterEqual(sum(max(h for h in a.homes if h) >= 4 for a in new), 6)

    def test_degraded_model_is_moved_down(self):
        moved = [home_at(r, "claude", cs.HOURS - 1) <= 4 for r in self.lean]
        self.assertGreaterEqual(sum(moved), 6)

    def test_lean_rules_keep_output(self):
        lean = statistics.mean(cs.totals(r)["value"] for r in self.lean)
        static = statistics.mean(cs.totals(r)["value"] for r in self.static)
        self.assertGreater(lean, static)


if __name__ == "__main__":
    unittest.main()
