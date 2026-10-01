"""Checks for the enterprise load probe's headline claims.

Run: python3 -m unittest discover -s probes/enterprise
"""

import unittest

import load_probe as lp


def run(design, emp, orders, promoted):
    return lp.assess(design, lp.load(emp, orders, promoted), lp.CAP, 48)


class LoadProbeTest(unittest.TestCase):
    def test_internal_systems_do_not_strain_one_database(self):
        r = run("D1 one store", 100_000, 0, 0.0)
        self.assertLess(r["database (one node)"][1], 1.0)

    def test_agents_are_the_first_limit_for_internal_work(self):
        r = run("D3 primitives", 100_000, 0, 0.0)
        self.assertEqual(lp.first_bottleneck(r)[0], "agents (instances at peak)")

    def test_promotion_cuts_agent_load(self):
        self.assertLess(run("D3 primitives", 100_000, 0, 0.7)["agents (instances at peak)"][1],
                        0.4 * run("D3 primitives", 100_000, 0, 0.0)["agents (instances at peak)"][1])

    def test_customer_volume_breaks_one_store_and_per_event_chains_but_not_primitives(self):
        self.assertGreater(run("D1 one store", 1_000, 1_000, 0.7)["hash chain (global, per event)"][1], 1.0)
        r = run("D3 primitives", 1_000, 1_000, 0.7)
        self.assertLess(r["hash chain: busiest domain (batched)"][1], 0.1)


if __name__ == "__main__":
    unittest.main()
