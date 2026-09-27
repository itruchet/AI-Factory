"""Checks for the institutional throughput model's headline claims.

Run: python3 -m unittest discover -s probes/institutions
"""

import unittest

import factory_sim as f
from experiments import split


def base(n, seeds=3):
    return f.mean_measure(lambda rng: ("baseline", f.baseline_org(split(n - 2), rng)), n=seeds, wip=n)


def inst(n, seeds=3, **kw):
    return f.mean_measure(lambda rng: ("institutions", f.draw_agents(split(n), rng)), n=seeds, wip=n, **kw)


class InstitutionsTest(unittest.TestCase):
    def test_baseline_hits_a_checker_ceiling(self):
        b12, b20 = base(12), base(20)
        self.assertLess(b20["ideas_per_week"], 1.1 * b12["ideas_per_week"])       # more workers, no more output
        self.assertEqual(max(b20["role_util"], key=b20["role_util"].get), "checker T1")
        self.assertGreater(b20["lead_h"], 1.3 * b12["lead_h"])                     # queues grow instead

    def test_institutions_keep_scaling(self):
        i12, i20 = inst(12), inst(20)
        self.assertGreater(i20["ideas_per_week"], 1.4 * i12["ideas_per_week"])

    def test_institutions_deliver_more_of_the_intent(self):
        self.assertGreater(inst(9)["coherence"], base(9)["coherence"] + 0.05)

    def test_small_teams_do_not_deadlock(self):
        # R13 (orphans) must keep three agents moving despite independence rules
        self.assertGreater(inst(3)["ideas_per_week"], 3)


if __name__ == "__main__":
    unittest.main()
