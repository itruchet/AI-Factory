"""Checks for the value-stream model's mechanics and headline claims.

Run: python3 -m unittest discover -s probes/value-stream
"""

import unittest

import elastic as e
import orgs as o
import vs_sim as v


def design(name, rname="best six", seeds=2):
    return v.mean_measures([o.job((("design", name), rname, "base", k)) for k in range(seeds)])


def elastic_run(demand, kind, names, arg, seeds=2):
    return v.mean_measures([e.job((demand, kind, names, arg, k, None)) for k in range(seeds)])


class ValueStreamTest(unittest.TestCase):
    def test_every_design_delivers(self):
        # no organisation may deadlock: structural independence waivers and R13 keep work moving
        for name in o.DESIGNS:
            for rname in ("best six", "population 12"):
                self.assertGreater(design(name, rname)["ideas"], 3, (name, rname))

    def test_institutions_beat_no_organisation_on_clean_ideas(self):
        self.assertGreater(design("institutions")["clean"], 1.3 * design("no organisation (solo)")["clean"])

    def test_elastic_cuts_lead_time_under_bursts(self):
        fixed = elastic_run("bursty", "fixed", o.SIX, 1)
        elastic = elastic_run("bursty", "elastic", o.SIX, None)
        self.assertLess(elastic["lead_p90"], 0.7 * fixed["lead_p90"])

    def test_one_model_swarm_checks_itself(self):
        one = elastic_run("steady", "elastic", [o.SIX[0]], None)
        six = elastic_run("steady", "elastic", o.SIX, None)
        self.assertGreater(one["cfr"], six["cfr"])
        self.assertGreater(one["usd_clean"], 3 * six["usd_clean"])

    def test_scaler_stops_idle_instances(self):
        m = elastic_run("bursty", "elastic", o.SIX, None)
        self.assertLess(m["seat_h"], m["peak"] * 168 * 0.8)      # instances do not stay at peak


if __name__ == "__main__":
    unittest.main()
