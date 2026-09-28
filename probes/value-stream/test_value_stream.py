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

    def test_graph_off_reproduces_r12(self):
        m = v.mean_measures([o.job((("design", "institutions"), "best six", "base", k)) for k in range(4)])
        self.assertAlmostEqual(m["clean"], 24.9, delta=0.1)       # orgs_results.txt, r12

    def test_r17_beats_the_review_barrier_with_dependencies(self):
        import deps
        def run(gate, barrier):
            return v.mean_measures([deps.org_job(({"COUPLING": 0.25}, ("design", "institutions"), "best six", "base",
                                                  gate, barrier, k)) for k in range(3)])
        r17, barrier = run("accepted", False), run("built", True)
        self.assertGreater(r17["clean"], 1.1 * barrier["clean"])
        self.assertLess(r17["drops"].get("stale_rework", 0), barrier["drops"].get("stale_rework", 0))

    def test_reserved_steps_break_in_an_outage_but_floors_do_not(self):
        import searched as sr
        def run(d, variant):
            return v.mean_measures([sr.job((d, "best six", "base", variant, 0.0, k)) for k in (40, 41, 42)])["clean"]
        inst = run("institutions", "outage")
        self.assertLess(run("searched (population 12)", "outage"), 0.8 * inst)     # planning reserved for absent models
        self.assertGreater(run("adaptive institutions", "outage"), 0.95 * inst)

    def test_held_cards_count_as_scaler_demand(self):
        import scaler_held as sh
        m0 = v.mean_measures([sh.job((0.25, "mixed", "elastic, r12.2 Scaler", k)) for k in range(3)])
        m1 = v.mean_measures([sh.job((0.25, "mixed", "elastic + held demand", k)) for k in range(3)])
        self.assertGreater(m1["seat_h"], m0["seat_h"])                            # the Scaler now provisions for held work

    def test_hand_backs_cut_failed_builds(self):
        import trifecta as tf
        def run(ready):
            return v.mean_measures([tf.job(("steady", dict(AMBIG_SCALE=0.9, READY_CHECK=ready), k)) for k in range(3)])
        off, on = run(False), run(True)
        self.assertGreater(on["drops"].get("handback", 0), 0)
        self.assertLess(on["drops"]["test_fail"], 0.8 * off["drops"]["test_fail"])


if __name__ == "__main__":
    unittest.main()
