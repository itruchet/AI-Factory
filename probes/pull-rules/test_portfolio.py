"""Checks for the portfolio probe's claims (synthetic data).

Run: python3 -m unittest discover -s probes/pull-rules
"""

import statistics
import unittest

import portfolio as p

CURRENT = ["sol", "opus", "mimo", "qwen"]
RECOMMENDED = ["sol", "opus", "mimo", "mimo", "coder"]


class GoldenRulesTest(unittest.TestCase):
    def test_golden_rules_match_the_full_set(self):
        for kw in (dict(keys=CURRENT), dict(keys=CURRENT, events=p.easy_first_tight, demand=p.EASY_SURGE)):
            full = p.mean_metrics(n=6, rules=p.ALL_RULES, **kw)
            gold = p.mean_metrics(n=6, rules=p.GOLDEN, **kw)
            self.assertGreater(gold["value"], 0.98 * full["value"])
            self.assertGreater(gold["hard_done"], 0.95 * full["hard_done"])

    def test_hardest_first_protects_hard_work_under_tight_caps(self):
        kw = dict(keys=CURRENT, events=p.easy_first_tight, demand=p.EASY_SURGE)
        gold = p.mean_metrics(n=6, rules=p.GOLDEN, **kw)
        without = p.mean_metrics(n=6, rules=tuple(r for r in p.GOLDEN if r != "hardest_first"), **kw)
        self.assertLess(without["hard_done"], 0.95 * gold["hard_done"])

    def test_overrated_model_is_moved_to_its_true_tier(self):
        m = p.CATALOG["overrated"]
        self.assertGreater(p.band(m.norm), p.sustain_tier(m.c))
        for s in range(6):
            r = p.run(["sol", "opus", "overrated", "mimo", "coder"], seed=s, rules=p.GOLDEN)
            a = next(x for x in r["agents"] if x.m.key == "overrated")
            self.assertEqual(a.homes[-1], p.sustain_tier(m.c))

    def test_real_models_land_on_their_benchmark_band(self):
        lands = {k: [] for k in p.REAL_MODELS}
        for s in range(6):
            for a in p.run(p.REAL_MODELS, seed=s, start="cold", rules=p.GOLDEN)["agents"]:
                lands[a.m.key].append(a.homes[-1])
        exact = 0
        for k, tiers in lands.items():
            landed, band = statistics.median_low(tiers), p.band(p.CATALOG[k].norm)
            self.assertLessEqual(abs(landed - band), 1, k)
            exact += landed == band
        self.assertGreaterEqual(exact, 6)  # local Qwen sits on a band edge and may land one below


class PortfolioTest(unittest.TestCase):
    def test_current_mix_depends_on_one_bulk_vendor(self):
        m = p.mean_metrics(CURRENT, n=6, rules=p.GOLDEN, events=p.vendor_outage("xiaomi"))
        self.assertFalse(p.meets(m))

    def test_recommended_mix_survives_every_single_vendor_outage_and_surge(self):
        for vendor in ("openai", "anthropic", "xiaomi", "local"):
            m = p.mean_metrics(RECOMMENDED, n=6, rules=p.GOLDEN, events=p.vendor_outage(vendor))
            self.assertTrue(p.meets(m), vendor)
        self.assertTrue(p.meets(p.mean_metrics(RECOMMENDED, n=6, rules=p.GOLDEN, demand=p.SURGE)))

    def test_single_top_tier_vendor_makes_hard_work_wait(self):
        even = p.mean_metrics(["sol", "luna", "mimo", "qwen", "coder"], n=6, rules=p.GOLDEN,
                              events=p.vendor_outage("openai"))
        rec = p.mean_metrics(RECOMMENDED, n=6, rules=p.GOLDEN, events=p.vendor_outage("openai"))
        self.assertGreater(even["hard_wait"], 2 * rec["hard_wait"])


if __name__ == "__main__":
    unittest.main()
