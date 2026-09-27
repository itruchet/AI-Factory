"""Integrity checks for the Factory ingestion pack: nothing invented, nothing forgotten, nothing out of date.

Run: python3 -m unittest discover -s pack
"""

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
PACK = json.loads((HERE / "factory-pack.json").read_text())
C = PACK["constitution"]
CARDS = {c["id"]: c for c in PACK["cards"]}
APPROVALS = {a["id"]: a for a in PACK["approvals"]["records"]}
OPEN = {o["id"]: o for o in PACK["open_items"]}
MEASURES = {m["id"]: m for m in PACK["measures"]}
RULES = {r["id"]: r for r in C["rules"]}


def known_ids() -> set:
    ids = set(RULES) | set(CARDS) | set(APPROVALS) | set(OPEN) | set(MEASURES)
    ids |= {g["id"] for g in C["golden_rules"] if g["id"]}
    ids |= {x["id"] for k in ("problems", "principles", "institutions", "experiments", "design_questions", "decisions",
                              "risks", "portfolio_rules") for x in C[k]}
    return ids


class PackIsCurrent(unittest.TestCase):
    def test_committed_pack_matches_a_fresh_build(self):
        r = subprocess.run([sys.executable, str(HERE / "build_pack.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_source_hashes_match_the_files(self):
        import hashlib
        for s in PACK["sources"] + PACK["evidence_files"]:
            self.assertEqual(hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest(), s["sha256"], s["path"])


class NothingInvented(unittest.TestCase):
    def test_every_claim_matches_its_source(self):
        self.assertEqual([c["id"] for c in PACK["claims"] if not c["verified"]], [])

    def test_every_operating_parameter_is_quoted_from_its_rule(self):
        for p in PACK["operating_parameters"]:
            self.assertIn(p["quote"], RULES[p["rule"]]["text"], p["id"])

    def test_rule_experiment_and_decision_text_is_verbatim(self):
        md = (ROOT / "docs/idea/constitutional-factory.md").read_text()
        for x in C["rules"] + C["experiments"] + C["decisions"]:
            for field in ("text", "hypothesis", "falsified_if"):
                if field in x:
                    self.assertIn(x[field], md, x["id"])

    def test_every_reference_resolves(self):
        ids = known_ids() | {f"institution.{i}" for i in ("Market", "Court")}
        refs = []
        for c in PACK["cards"]:
            refs += [(c["id"], r) for r in c["traces"] + c["depends_on"] + c["requires_approval"] + c["measures"] + c["open_items"]]
        for a in PACK["approvals"]["records"]:
            refs += [(a["id"], r) for r in a["depends_on"] + a.get("before_cards", [])]
        for o in PACK["open_items"]:
            refs += [(o["id"], r) for r in o["blocks"] if not r.startswith("AR-05 ")]
        self.assertEqual([(s, r) for s, r in refs if r not in ids], [])

    def test_measure_simulator_fields_exist(self):
        sys.path.insert(0, str(ROOT / "probes/value-stream"))
        import vs_sim
        import select6
        sample = json.loads((ROOT / "probes/value-stream/scaler_held.json").read_text())["0.25"]["mixed"]["fixed six"]
        for m in PACK["measures"]:
            for f in (m["sim_field"] or "").split(","):
                f = f.strip()
                if not f:
                    continue
                ok = hasattr(vs_sim, f) or hasattr(select6, f) or f in sample or f == "usd_clean" or \
                    (f.startswith("drops.") and f[6:] in sample["drops"])
                self.assertTrue(ok, (m["id"], f))

    def test_menu_is_the_approved_seven_on_api_tokens(self):
        self.assertEqual(len(PACK["menu"]), 7)
        self.assertEqual({m["vendor"] for m in PACK["menu"] if m["role"] == "Anchor"}, {"Anthropic", "OpenAI"})
        self.assertTrue(all(m["billing"] == "API tokens" for m in PACK["menu"]))

    def test_no_secrets(self):
        text = "\n".join((HERE / f).read_text() for f in ("factory-pack.json", "CARDS.md", "README.md", "INGEST.md"))
        for pat in (r"sk-[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"AIza[0-9A-Za-z_\-]{35}", r"-----BEGIN [A-Z ]*PRIVATE KEY"):
            self.assertIsNone(re.search(pat, text), pat)

    def test_placeholders_are_owned(self):
        # every [PLACEHOLDER] in a card names the open item or approval that resolves it
        for c in PACK["cards"]:
            for s in c["scope"] + c["acceptance"] + [c["owner_after"]]:
                for m in re.finditer(r"\[PLACEHOLDER: ([^\]]+)\]", s):
                    self.assertTrue(re.search(r"AR-\w+|OI-\d+", m.group(1)), (c["id"], m.group(0)))


class NothingForgotten(unittest.TestCase):
    def test_the_idea_record_is_complete(self):
        self.assertEqual([r["id"] for r in C["rules"]], [f"R{i}" for i in range(1, 21)])
        self.assertEqual(sorted(x["id"] for x in C["experiments"]), sorted(f"X{i}" for i in range(1, 15)))
        self.assertEqual(sorted(d["id"] for d in C["decisions"]), sorted(f"H{i}" for i in range(1, 8)))
        self.assertEqual(len(C["principles"]), 8)
        self.assertEqual(len(C["institutions"]), 8)
        self.assertEqual(len(C["problems"]), 11)
        self.assertEqual([g["id"] for g in C["golden_rules"] if g["id"]], ["G1", "G2", "G3", "G4", "G5"])

    def test_every_live_rule_has_a_card(self):
        traced = {t for c in PACK["cards"] for t in c["traces"]}
        missing = [r["id"] for r in C["rules"] if r["status"] != "dropped" and r["id"] not in traced]
        self.assertEqual(missing, [])

    def test_every_golden_rule_principle_institution_and_problem_has_a_card(self):
        traced = {t for c in PACK["cards"] for t in c["traces"]}
        want = [g["id"] for g in C["golden_rules"] if g["id"]] + [p["id"] for p in C["principles"]] + \
               [i["id"] for i in C["institutions"]]
        self.assertEqual([w for w in want if w not in traced], [])
        # problems are answered by rules; each must be traced directly or through a rule named in its answer
        self.assertEqual([p["id"] for p in C["problems"] if p["id"] not in traced], [])

    def test_every_experiment_is_instrumented_and_judged(self):
        judged = set(CARDS["C4.01"]["traces"])
        instrumented = {t for c in PACK["cards"] if c["id"] != "C4.01" for t in c["traces"]}
        for x in C["experiments"]:
            self.assertIn(x["id"], judged)
            self.assertIn(x["id"], instrumented, x["id"])

    def test_every_design_question_and_risk_is_routed(self):
        traced = {t for c in PACK["cards"] for t in c["traces"]}
        routed = traced | {o["id"] for o in PACK["open_items"]}
        text = json.dumps(PACK["open_items"])
        for d in C["design_questions"]:
            self.assertTrue(d["id"] in routed or "Jurisdiction" in d["text"] and "Jurisdiction" in text, d["id"])
        self.assertEqual([r["id"] for r in C["risks"] if r["id"] not in traced], [])

    def test_every_decision_has_an_approval_record(self):
        covered = {a["decision"] for a in PACK["approvals"]["records"] if a["decision"]}
        self.assertEqual(covered, {d["id"] for d in C["decisions"]})

    def test_open_items_and_cards_agree(self):
        for o in PACK["open_items"]:
            for b in o["blocks"]:
                if b in CARDS:
                    self.assertIn(o["id"], CARDS[b]["open_items"], (o["id"], b))

    def test_every_measure_is_recorded_by_a_card(self):
        used = {m for c in PACK["cards"] for m in c["measures"]}
        self.assertEqual([m for m in MEASURES if m not in used], [])

    def test_every_twin_parameter_is_listed(self):
        sys.path.insert(0, str(ROOT / "probes/value-stream"))
        import vs_sim
        listed = {p["name"] for p in PACK["twin_parameters"]}
        consts = {n for n, v in vars(vs_sim).items() if n.isupper() and isinstance(v, (int, float, dict, tuple, list))
                  and not isinstance(v, bool) and n not in ("PRIORITY",)}
        self.assertEqual(consts - listed, set())


class PlanIsSound(unittest.TestCase):
    def test_dependency_graph_is_acyclic_and_phase_ordered(self):
        seen, stack = set(), set()

        def visit(i):
            self.assertNotIn(i, stack, f"cycle at {i}")
            if i in seen:
                return
            stack.add(i)
            for d in CARDS[i]["depends_on"]:
                self.assertLessEqual(CARDS[d]["phase"], CARDS[i]["phase"], (i, d))
                visit(d)
            stack.discard(i)
            seen.add(i)
        for i in CARDS:
            visit(i)

    def test_governance_is_protected_before_anything_changes(self):
        # every card except the Fit Report and pack registration depends, directly or not, on C0.02
        def ancestors(i, acc=None):
            acc = set() if acc is None else acc
            for d in CARDS[i]["depends_on"]:
                if d not in acc:
                    acc.add(d)
                    ancestors(d, acc)
            return acc
        for i in CARDS:
            if i not in ("C0.00", "C0.01", "C0.02"):
                self.assertIn("C0.02", ancestors(i), i)

    def test_approvals_are_ordered(self):
        order = {a["id"]: n for n, a in enumerate(PACK["approvals"]["records"])}
        for a in PACK["approvals"]["records"]:
            for d in a["depends_on"]:
                self.assertLess(order[d], order[a["id"]], (a["id"], d))
                self.assertLessEqual(APPROVALS[d]["gate"], a["gate"])

    def test_just_in_time_approvals_precede_their_cards(self):
        for a in PACK["approvals"]["records"]:
            for c in a.get("before_cards", []):
                self.assertIn(a["id"], CARDS[c]["requires_approval"], (a["id"], c))

    def test_counts_in_the_prose_match_the_pack(self):
        n_cards, n_ar = len(PACK["cards"]), len(PACK["approvals"]["records"])
        ingest = (HERE / "INGEST.md").read_text()
        readme = (HERE / "README.md").read_text()
        self.assertIn(f"{n_cards} card seeds", ingest)
        self.assertIn(f"{n_ar} approval records", ingest)
        words = {14: "Fourteen", 15: "Fifteen", 16: "Sixteen"}
        self.assertIn(f"{words[n_ar]} records in three gates", readme)
        self.assertIn(f"Isa signs {words[sum(1 for a in PACK['approvals']['records'] if a['signer'] == 'Isa')].lower()}", readme)

    def test_the_register_mirrors_the_approvals(self):
        md = (ROOT / "docs/idea/approvals.md").read_text()
        for a in PACK["approvals"]["records"]:
            self.assertRegex(md, rf"\| {re.escape(a['id'])}( \(H\d\))? \| \*\*{re.escape(a['title'])}\*\*", a["id"])
        self.assertIn(f"{len(PACK['cards'])} card seeds", md)

    def test_no_card_ratifies_itself(self):
        for c in PACK["cards"]:
            self.assertNotEqual(c["ratified_by"], c["executed_by"], c["id"])


if __name__ == "__main__":
    unittest.main()
