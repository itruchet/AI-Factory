"""Checks for the best-six probe's mechanics and headline claims.

Run: python3 -m unittest discover -s probes/portfolio6
"""

import math
import unittest

import select6 as s

FABLE = "Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback)"
OPUS = "Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)"
SOL = "GPT-6 Sol (max)"
ASTRA = "GPT-6 Astra (high)"
GEMINI = "Gemini 3.8 Flash (high)"


class Select6Test(unittest.TestCase):
    def test_token_model_matches_hand_calculation(self):
        # Fable: 90k output tokens per reference hour at $50/M, 2.7M input at $10/M x 0.19
        ref = (90e3 * 50 + 2.7e6 * 10 * 0.19) / 1e6
        self.assertAlmostEqual(s.usd_per_ref_hour(s.C[FABLE]), ref, places=6)
        self.assertAlmostEqual(s.usd_per_busy_hour(s.C[FABLE]), ref / math.sqrt(100 / 68), places=1)

    def test_vendor_rules(self):
        mid = s.REFERENCE_MID
        self.assertFalse(s.legal([FABLE, OPUS, "Claude Fable 5.1 (Adaptive Reasoning, Max Effort, Default Fallback)"], mid))
        self.assertFalse(s.legal([FABLE, OPUS, OPUS], mid))                 # one vendor among top seats (P1)
        self.assertTrue(s.legal([FABLE, OPUS, SOL], mid))
        self.assertFalse(s.legal([GEMINI, SOL, OPUS], [GEMINI] + mid[:2]))   # a model holds one seat only

    def test_a_weekly_cap_costs_throughput(self):
        six = [OPUS, SOL, GEMINI] + s.REFERENCE_MID
        with s.Pool(2) as pool:
            free = s.evaluate(pool, [six], 2)[0]
            capped = s.evaluate(pool, [six], 2, caps={OPUS: 24, SOL: 24, GEMINI: 24})[0]
        self.assertLess(capped["ipw"], 0.85 * free["ipw"])
        self.assertGreater(free["busy"][OPUS], 60)          # an always-on seat works far past a 20x plan's hours


if __name__ == "__main__":
    unittest.main()
