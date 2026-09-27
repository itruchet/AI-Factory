"""Checks that the pull rules meet the Idea Record's claims (synthetic data).

Run: python3 -m unittest discover -s probes/pull-rules
"""

import unittest

import sim


def mean_over_seeds(adaptive, change=None, n=12):
    runs = [sim.run(sim.roster(), adaptive=adaptive, seed=s, change=change) for s in range(n)]
    ok = sum(sim.totals(r)[0] for r in runs) / n
    bad = sum(sim.totals(r)[1] for r in runs) / n
    qwen_t2_bad = sum(next(a for a in r["agents"] if a.name == "qwen").log[(2, "marked_down")] for r in runs) / n
    qwen_t2 = sum(2 in next(a for a in r["agents"] if a.name == "qwen").licences for r in runs) / n
    return ok, bad, qwen_t2_bad, qwen_t2


class PullRulesTest(unittest.TestCase):
    def test_failing_agent_gets_less_of_the_work_it_fails(self):
        _, _, static_q, _ = mean_over_seeds(adaptive=False)
        _, _, rules_q, share = mean_over_seeds(adaptive=True)
        self.assertLess(rules_q, 0.5 * static_q)
        self.assertLess(share, 0.2)  # qwen ends the week without tier 2 in most runs

    def test_throughput_is_kept_and_markdowns_fall(self):
        static_ok, static_bad, _, _ = mean_over_seeds(adaptive=False)
        rules_ok, rules_bad, _, _ = mean_over_seeds(adaptive=True)
        self.assertGreater(rules_ok, 0.97 * static_ok)
        self.assertLess(rules_bad, static_bad)

    def test_improved_agent_earns_work_back(self):
        def upgrade(hour, agents):
            if hour == 84:
                next(a for a in agents if a.name == "qwen").p.update({1: .97, 2: .90, 3: .45})
        _, _, _, share = mean_over_seeds(adaptive=True, change=upgrade)
        self.assertGreater(share, 0.5)  # re-licensed for tier 2 in most runs


if __name__ == "__main__":
    unittest.main()
