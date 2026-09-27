"""Checks that the pull rules meet the Idea Record's claims (synthetic data).

Run: python3 -m unittest discover -s probes/pull-rules
"""

import unittest

import sim


def mean(policy, arrivals=sim.steady, change=None, n=12):
    return sim.mean_summary(policy, arrivals=arrivals, n=n, change=change)


def qwen_t2_share(change, n=12):
    runs = [sim.run(sim.roster(), "bands", seed=s, change=change) for s in range(n)]
    return sum(2 in next(a for a in r["agents"] if a.name == "qwen").licences for r in runs) / n


class PullRulesTest(unittest.TestCase):
    def test_failing_agent_gets_less_of_the_work_it_fails(self):
        self.assertLess(mean("bands")["qwen_t2_markdowns"], 0.5 * mean("static")["qwen_t2_markdowns"])

    def test_throughput_and_value_are_kept(self):
        static, bands = mean("static"), mean("bands")
        self.assertGreater(bands["accepted"], 0.97 * static["accepted"])
        self.assertGreater(bands["value"], 0.99 * static["value"])
        self.assertLess(bands["marked_down"], static["marked_down"])

    def test_accurate_and_fast_upgrade_earns_harder_work(self):
        def upgrade(hour, agents):
            if hour == 84:
                q = next(a for a in agents if a.name == "qwen")
                q.p.update({1: .97, 2: .90, 3: .45})
                q.speed = 0.9
        self.assertGreater(qwen_t2_share(upgrade), 0.5)

    def test_accurate_but_slow_agent_stays_on_easier_work(self):
        def accurate_only(hour, agents):
            if hour == 84:
                next(a for a in agents if a.name == "qwen").p.update({1: .97, 2: .90, 3: .45})
        self.assertLess(qwen_t2_share(accurate_only), 0.2)

    def test_scarce_frontier_is_kept_for_hard_work(self):
        sim.FRONTIER_CAP = 900
        try:
            pacing, bands = mean("pacing", sim.easy_first), mean("bands", sim.easy_first)
        finally:
            sim.FRONTIER_CAP = 1400
        self.assertGreater(bands["t3_accepted"], 1.1 * pacing["t3_accepted"])
        self.assertLess(bands["frontier_easy_share"], 0.05)
        self.assertGreater(bands["value"], pacing["value"])


if __name__ == "__main__":
    unittest.main()
