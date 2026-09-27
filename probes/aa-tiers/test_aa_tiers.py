"""Checks for the Artificial Analysis tiering and market probes.

Run: python3 -m unittest discover -s probes/aa-tiers   (needs numpy, scipy, scikit-learn)
"""

import statistics
import unittest

import numpy as np

import market_sim as m
import tiering as t


class TieringTest(unittest.TestCase):
    def test_data_supports_few_natural_tiers(self):
        rows = t.views(t.load())["current"]
        a = t.analyse(np.array([r["coding_index"] for r in rows]))
        votes = [a[k] for k in ("gmm_bic", "jenks_90", "kde_silverman", "kde_scott", "gap", "silhouette")]
        self.assertLessEqual(statistics.median(votes), 3)
        self.assertGreaterEqual(a["gvf"][5], 0.95)          # five tiers already explain 95%
        self.assertLess(a["gvf"][7] - a["gvf"][5], 0.02)    # more tiers add almost nothing


class MarketTest(unittest.TestCase):
    def test_top_tier_only_costs_most_for_the_same_value(self):
        top = m.mean_static({1: 6}, n=6)
        mixed = m.mean_static({1: 3, 2: 3}, n=6)
        self.assertGreater(mixed["per_week_value"], 0.99 * top["per_week_value"])
        self.assertLess(mixed["per_week_cost"], 0.8 * top["per_week_cost"])

    def test_bottom_tier_only_cannot_do_hard_work(self):
        self.assertEqual(m.mean_static({3: 6}, n=4)["hard_done"], 0)

    def test_guarded_evidence_policy_beats_chasing_and_standing_still(self):
        res = {p: [m.rolling(p, seed=s) for s in range(4)] for p in ("static", "chase", "guarded")}
        vpd = {p: statistics.mean(f.value / f.cost for f, _, _ in r) for p, r in res.items()}
        hard = {p: statistics.mean(sum(w["backlog_hard"] > 20 for w in log) for _, log, _ in r) for p, r in res.items()}
        share = {p: statistics.mean(statistics.mean(w["top_vendor_share"] for w in log[-8:]) for _, log, _ in r)
                 for p, r in res.items()}
        self.assertGreater(vpd["guarded"], 2 * vpd["static"])
        self.assertGreater(vpd["guarded"], 5 * vpd["chase"])
        self.assertLess(hard["guarded"], hard["static"])
        self.assertGreater(share["chase"], share["guarded"])  # chasing concentrates on one vendor


if __name__ == "__main__":
    unittest.main()
