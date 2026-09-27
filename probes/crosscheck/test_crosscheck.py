"""Checks for the cross-check's headline claims.

Run: python3 -m unittest discover -s probes/crosscheck
"""

import statistics
import unittest

import our_rules_in_their_sim as m


def mean_of(variant, key, seeds=6, mix=(6, 3, 3)):
    return statistics.mean(m.job(("reference", variant, mix, 900 + s))[key] for s in range(seeds))


class CrossCheckTest(unittest.TestCase):
    def test_external_simulator_unchanged_and_runs(self):
        r = m.job(("reference", "external institutions (barrier, FIFO)", (6, 3, 3), 900))
        self.assertGreater(r["useful_week"], 0)

    def test_licences_cut_escaped_defects_in_the_external_model(self):
        self.assertLess(mean_of("institutions + licences", "defects"),
                        0.8 * mean_of("external institutions (barrier, FIFO)", "defects"))

    def test_licences_raise_useful_output_of_the_best_external_design(self):
        self.assertGreater(mean_of("evidence graph + licences", "useful_week"),
                           mean_of("external evidence graph (FIFO)", "useful_week"))


if __name__ == "__main__":
    unittest.main()
