"""Builds the Factory ingestion pack from the Idea Record, the probe results and the hand-written seeds in src/.

Nothing in the constitution, experiments, decisions, twin parameters, model menu or predictions is typed by hand:
each is extracted from its source file here, so the pack cannot drift from the evidence. Hand-written content
(cards, approvals, open items, measures, operating parameters, claims) lives in src/ and is cross-checked by
test_pack.py.

Run: python3 pack/build_pack.py          (writes factory-pack.json, CARDS.md, manifest.json)
     python3 pack/build_pack.py --check  (exit 1 if the committed pack is out of date)
"""

import hashlib
import json
import re
import sys
from dataclasses import fields
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
IDEA = ROOT / "docs/idea/constitutional-factory.md"
PACK_VERSION = "1.0"
SCHEMA = "factory-pack/1"

sys.path.insert(0, str(ROOT / "probes/value-stream"))
import vs_sim  # noqa: E402
import select6  # noqa: E402  (on sys.path through vs_sim)

SEVEN = [("Claude Opus 5.5 (Adaptive Reasoning, Max Effort, Default Fallback)", "Anchor"),
         ("GPT-5.6 Terra (max)", "Anchor"),
         ("Muse Spark 1.3 (xhigh)", "Fast top tier"),
         ("Gemini 3.8 Flash (high)", "Fast top tier"),
         ("DeepSeek V4.1 Flash (Reasoning, Max Effort)", "Mid"),
         ("GPT-6 Luna (max)", "Mid"),
         ("Ling 3.0 Flash", "Mid")]

INSTITUTION_IDS = {"Inquiry": "Inquiry", "Deliberation Council": "Council", "Council": "Council",
                   "Planning Chamber": "Planning", "Planning": "Planning", "Work Market": "Market", "Market": "Market",
                   "Assurance Court": "Court", "Court": "Court", "Audit": "Audit", "Ledger": "Ledger",
                   "Release Gate": "ReleaseGate", "Release": "ReleaseGate"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


# ---------------------------------------------------------------- Idea Record parsing
def section(md: str, heading: str) -> str:
    """The text directly under the first heading that starts with `heading`, up to the next heading of any level."""
    m = re.search(rf"^#+ {re.escape(heading)}.*$", md, re.M)
    if not m:
        raise KeyError(heading)
    rest = md[m.end():]
    end = re.search(r"^#+ ", rest, re.M)
    return rest[:end.start()] if end else rest


def tables(text: str) -> list[list[list[str]]]:
    """Every table in `text`, as rows of cells (header and rule skipped)."""
    blocks, cur = [], []
    for ln in text.splitlines() + [""]:
        if ln.startswith("|"):
            cur.append(ln)
        elif cur:
            blocks.append([[c.strip() for c in r.strip().strip("|").split("|")] for r in cur[2:]])
            cur = []
    return blocks


def table(text: str) -> list[list[str]]:
    return tables(text)[0]


def bullets(text: str) -> list[str]:
    return [ln[2:].strip() for ln in text.splitlines() if ln.startswith("- ")]


def numbered(text: str) -> list[str]:
    return [re.sub(r"^\d+\.\s+", "", ln).strip() for ln in text.splitlines() if re.match(r"^\d+\.\s", ln)]


def unbold(s: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"\1", s).strip()


def parse_idea(md: str) -> dict:
    c = {}
    c["idea"] = section(md, "0. The idea").strip()
    c["problems"] = [dict(id=f"problem.{r[0]}", text=r[1]) for r in table(section(md, "1. The problems"))]
    rules = []
    for r in table(section(md, "3. The rule system")):
        name = r[1]
        note = re.search(r"\*\((.+?)\)\*", name)
        status = "active"
        if note and "dropped in r8" in note.group(1) and "velocity" not in note.group(1):
            status = "dropped"
        elif note and "optional" in note.group(1):
            status = "optional"
        rules.append(dict(id=r[0], name=unbold(re.sub(r"\*\(.+?\)\*", "", name)), note=note.group(1) if note else None,
                          status=status, text=r[2]))
    c["rules"] = rules
    m = re.search(r"^\*\*Constants set once in the constitution:\*\*.*$", md, re.M)
    c["constants"] = m.group(0)
    c["key_points"] = numbered(section(md, "3.1 Key points"))
    golden = []
    for r in table(section(md, "3.2 Golden rules")):
        gid = re.match(r"\*\*(G\d) (.+?)\*\*\s*(\((R\d+)\))?", r[0])
        if gid:
            golden.append(dict(id=gid.group(1), name=gid.group(2), rule=gid.group(4), removal_cost=r[1], verdict=unbold(r[2])))
        else:
            golden.append(dict(id=None, name=r[0], rule=None, removal_cost=r[1], verdict=unbold(r[2])))
    c["golden_rules"] = golden
    inst = []
    prot = {r[0]: dict(main_risk=r[1], protection=r[2]) for r in table(section(md, "4.1 Institution-specific"))}
    mem = {r[0]: dict(sees=r[1], never_sees=r[2]) for r in table(section(md, "7. Memory"))}
    for r in table(section(md, "4. The eight institutions")):
        name = unbold(r[1])
        short = INSTITUTION_IDS[name]
        pk = next((k for k in prot if INSTITUTION_IDS.get(k) == short), None)
        mk = next((k for k in mem if INSTITUTION_IDS.get(k) == short), None)
        inst.append(dict(id=f"institution.{short}", number=int(r[0]), name=name, problem=r[2], who_pulls=r[3],
                         marked_by=r[4], protection=prot.get(pk), memory=mem.get(mk)))
    c["institutions"] = inst
    c["human_touchpoints"] = bullets(section(md, "5. Capacity and subscriptions"))[-5:]
    assert c["human_touchpoints"][0].startswith("setting each institution"), c["human_touchpoints"]
    p8 = [r for t in tables(section(md, "5.1 The model portfolio")) for r in t if re.match(r"P\d$", r[0])]
    p9 = [r for t in tables(section(md, "5.2 Tiers from real data")) for r in t if re.match(r"P\d$", r[0])]
    r8 = [dict(id=f"portfolio.{r[0]}@r8", revision="r8", text=unbold(r[1]), evidence=r[2]) for r in p8]
    r9 = [dict(id=f"portfolio.{r[0]}", revision="r9", text=unbold(r[1])) for r in p9]
    active = {p["id"] for p in r9}
    for p in r8:
        p["status"] = "superseded by r9 wording" if p["id"].split("@")[0] in active else "evidence only; not in H4"
    for p in r9:
        p["status"] = "active (H4)"
    c["portfolio_rules"] = r9 + r8
    c["principles"] = [dict(id=f"principle.{i + 1}", text=t) for i, t in enumerate(numbered(section(md, "6. The constitution")))]
    c["threats"] = [dict(threat=r[0], answer=r[1]) for r in table(section(md, "8. Threats"))]
    c["settled"] = [dict(question=r[0], settlement=r[1]) for r in table(section(md, "10. Settled"))]
    c["experiments"] = [dict(id=r[0], hypothesis=r[1], falsified_if=r[2]) for r in table(section(md, "11.1 Experiments"))]
    c["design_questions"] = [dict(id=f"DQ{i + 1}", text=t) for i, t in enumerate(bullets(section(md, "11.2 Design-stage")))]
    c["decisions"] = [dict(id=r[0], text=r[1]) for r in table(section(md, "11.3 Isa's decisions"))]
    c["risks"] = [dict(id=f"RK{i + 1}", text=t) for i, t in enumerate(bullets(section(md, "13. Risks")))]
    c["findings"] = [dict(id=f"§{h}", text=section(md, h).strip()) for h in
                     ("5.3 Institutional throughput", "5.4 The best six", "5.5 Idea to live", "5.6 Cross-check",
                      "5.7 Dependency graphs", "5.8 Institutions or the searched")]
    return c


# ---------------------------------------------------------------- evidence extraction
def twin_parameters(measures: list[dict]) -> list[dict]:
    """Every assumed constant in the simulator, with the measure that can calibrate it."""
    by_field = {}
    for m in measures:
        for f in (m.get("sim_field") or "").split(","):
            if f.strip():
                by_field.setdefault(f.strip(), []).append(m["id"])
    src = (ROOT / "probes/value-stream/vs_sim.py").read_text().splitlines()
    out = []
    skip = {"HERE", "PRIORITY", "ALL_STEPS"}
    for mod, path, names in ((vs_sim, "probes/value-stream/vs_sim.py", None),
                             (select6, "probes/portfolio6/select6.py", ("GEN_DUTY", "IN_PER_OUT", "CACHE_HIT", "CACHE_PRICE"))):
        lines = (ROOT / path).read_text().splitlines()
        for name in names or [n for n in vars(mod) if n.isupper() and n not in skip]:
            v = getattr(mod, name)
            if not isinstance(v, (int, float, dict, tuple, list)) or isinstance(v, bool):
                continue
            ln = next((i for i, s in enumerate(lines) if re.match(rf"^\s*{name}\b.*=", s) or re.match(rf"^[A-Z_, ]*\b{name}\b[A-Z_, ]*=", s)), None)
            comment = lines[ln].split("#", 1)[1].strip() if ln is not None and "#" in lines[ln] else None
            out.append(dict(name=name, value=v, source=f"{path}:{ln + 1}" if ln is not None else path, comment=comment,
                            status="assumed", calibrate_with=by_field.get(name, [])))
    for f in fields(vs_sim.Scaler):
        if f.name in ("models", "rate", "cls", "min_n", "max_n"):
            continue
        out.append(dict(name=f"Scaler.{f.name}", value=f.default, source="probes/value-stream/vs_sim.py (class Scaler)",
                        comment=None, status="rule setting (PR-01..PR-09) or assumed", calibrate_with=[]))
    assert src  # vs_sim source present
    return out


def menu() -> list[dict]:
    cand = {r["name"]: r for r in json.load(open(ROOT / "probes/portfolio6/select6.json"))["candidates"].values()}
    out = []
    for name, role in SEVEN:
        c = cand[name]
        out.append(dict(name=name, vendor=c["vendor"], role=role, coding_index=c["ci"], coding_index_estimated=c["est"],
                        usd_per_m_input=c["p_in"], usd_per_m_output=c["p_out"], output_tokens_per_s=c["speed"],
                        billing="API tokens", source="probes/portfolio6/select6.json (Artificial Analysis snapshot 27 Sep 2026)"))
    return out


KEEP = ("ideas", "clean", "cfr", "lead", "lead_p90", "usd_week", "backlog")


def pick(m: dict) -> dict:
    out = {k: round(m[k], 3) for k in KEEP if k in m}
    out["usd_clean"] = round(m["usd_week"] / m["clean"], 2) if m.get("clean") else None
    if "drops" in m:
        out["stale_rework_per_idea"] = round(m["drops"].get("stale_rework", 0.0), 3)
    return out


def predictions() -> dict:
    sh = json.load(open(ROOT / "probes/value-stream/scaler_held.json"))
    dp = json.load(open(ROOT / "probes/value-stream/deps.json"))
    el = json.load(open(ROOT / "probes/value-stream/elastic.json"))
    return dict(
        _about="Uncalibrated synthetic predictions: means over seeds, per week. They are the prior for C0.14, which "
               "replaces them with a calibrated run. Never treat them as measured. Metrics: ideas and clean per week; "
               "cfr = change-failure rate; lead and lead_p90 in hours; usd_week; usd_clean = usd_week / clean.",
        trial_configuration=dict(
            description="Institutions, elastic Scaler with held demand and 15-minute target (R14), R17, the six (r11 roster), coupling 0.25",
            source="probes/value-stream/scaler_held.json [0.25][demand]['elastic + held demand, 15-min target']",
            by_demand={d: pick(v["elastic + held demand, 15-min target"]) for d, v in sh["0.25"].items()}),
        fixed_six_reference=dict(
            description="Same work on six fixed seats",
            source="probes/value-stream/scaler_held.json [0.25][demand]['fixed six']",
            by_demand={d: pick(v["fixed six"]) for d, v in sh["0.25"].items()}),
        backcast_prior=dict(
            description="Director -> Worker -> Checker against the institutions, the six, coupling 0.25, base scenario (for C0.13 and X1)",
            source="probes/value-stream/deps.json [D2]['best six']['base']",
            by_design={k: pick(dp["D2"]["best six"]["base"][k]) for k in ("Director-Worker-Checker", "institutions")}),
        seven_model_menu=dict(
            description="The approved seven-model menu, elastic, without a dependency graph (the menu was not re-run with dependencies)",
            source="probes/value-stream/elastic.json [menus][demand]['seven (Opus 5.5 + Terra)']",
            by_demand={d: pick(v["seven (Opus 5.5 + Terra)"]) for d, v in el["menus"].items()}),
        gap="The trial configuration was simulated with the six (r11 roster); the seven-model menu only without dependencies. C0.14 must run the calibrated twin on the menu actually approved.")


def dig(obj, path):
    for p in path:
        obj = obj[p]
    return obj


def verify_claims(claims: list[dict]) -> list[dict]:
    out = []
    for c in claims:
        s = c["source"]
        if "json" in s:
            got = dig(json.load(open(ROOT / s["json"])), s["path"]) * s.get("scale", 1)
            ok = abs(got - c["value"]) <= s["tol"] * abs(c["value"])
            out.append(dict(c, verified=ok, found=round(got, 3)))
        else:
            ok = s["contains"] in (ROOT / s["text"]).read_text()
            out.append(dict(c, verified=ok))
    return out


SOURCES = [
    ("docs/idea/constitutional-factory.md", "authoritative", True),
    ("docs/idea/approvals.md", "authoritative (register; mirrors src/approvals.json)", True),
    ("docs/idea/value-stream.md", "evidence", True),
    ("docs/idea/dependencies.md", "evidence", True),
    ("docs/idea/institutions-vs-searched.md", "evidence", True),
    ("docs/idea/crosscheck.md", "evidence", True),
    ("docs/idea/best-six.md", "evidence", True),
    ("docs/idea/institutional-throughput.md", "evidence (r10; superseded where r11-r12.3 differ)", True),
    ("docs/design-parked/constitutional-factory-design-notes.md",
     "parked r3 design: superseded wherever it conflicts with the Idea Record (notably kernel assignment, Thompson sampling and shadow prices, replaced by pull rules R1-R20)", False),
    ("docs/design-parked/ledger-schema.sql", "parked reference schema: append-only Ledger ideas reusable; draw and assignment tables superseded by pull (R1)", False),
]


def build() -> tuple[dict, str]:
    md = IDEA.read_text()
    src = {n: json.load(open(HERE / "src" / f"{n}.json")) for n in
           ("cards", "approvals", "open_items", "measures", "parameters", "claims")}
    evidence_files = sorted(p for p in (ROOT / "probes").rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    pack = dict(
        schema=SCHEMA, pack_version=PACK_VERSION, owner="Isa", scenario="Amend the existing Factory",
        from_organisation="Director -> Worker -> Checker", to_organisation="Constitutional institutions (Idea Record r12.4)",
        integrity_rules=[
            "Do not infer. A value marked [PLACEHOLDER] or an open item is resolved only by its named resolver.",
            "[PROPOSED] marks a design proposal for Isa to ratify in AR-13, not evidence.",
            "[Unverified] and [Inference] mark statements that are not confirmed; keep the label until evidence closes it.",
            "Simulation outputs are synthetic hypotheses, never measured facts.",
            "Rule, experiment and decision text is verbatim from the Idea Record; change it only by constitutional amendment (principle 8).",
            "Card seeds may be split, never merged, dropped or widened without an approved delta in AR-13.",
            "This pack supersedes the parked design wherever they conflict.",
            "No secret, key or credential belongs in the pack, the Ledger or a card.",
        ],
        constitution=parse_idea(md),
        operating_parameters=src["parameters"]["parameters"],
        menu=menu(),
        measures=src["measures"]["measures"],
        twin_parameters=twin_parameters(src["measures"]["measures"]),
        predictions=predictions(),
        claims=verify_claims(src["claims"]["claims"]),
        approvals=src["approvals"],
        open_items=src["open_items"]["items"],
        phases=src["cards"]["phases"],
        cards=src["cards"]["cards"],
        sources=[dict(path=p, status=s, sha256=sha(ROOT / p), text=(ROOT / p).read_text() if embed else None)
                 for p, s, embed in SOURCES],
        evidence_files=[dict(path=rel(p), sha256=sha(p)) for p in evidence_files],
    )
    return pack, cards_md(pack)


# ---------------------------------------------------------------- human-readable card list
def cards_md(pack: dict) -> str:
    out = ["# Card seeds: Idea-to-Live Factory", "",
           f"Generated by `pack/build_pack.py` from `pack/src/cards.json` (pack {pack['pack_version']}). Do not edit by hand.", "",
           "Each seed is a unit of intent with an acceptance contract. The Director splits seeds into Factory cards after the Fit Report (C0.00); "
           "seeds are never merged, dropped or widened without an approved delta in AR-13.", ""]
    for ph in pack["phases"]:
        out += [f"## Phase {ph['phase']}: {ph['name']}", "", ph["intent"], "",
                "**Entry:** " + "; ".join(ph["entry"]) + ".", "", "**Exit:** " + "; ".join(ph["exit"]) + ".", ""]
        for c in (c for c in pack["cards"] if c["phase"] == ph["phase"]):
            out += [f"### {c['id']} {c['title']}", "", c["intent"], "",
                    f"- **Owner after migration:** {c['owner_after']}. **Executed by:** {c['executed_by']}.",
                    f"- **Depends on:** {', '.join(c['depends_on']) or 'none'}. **Approvals first:** {', '.join(c['requires_approval']) or 'none'}."
                    + (f" **Ratified by:** {c['ratified_by']}." if c["ratified_by"] else ""),
                    f"- **Traces:** {', '.join(c['traces'])}." + (f" **Measures:** {', '.join(c['measures'])}." if c["measures"] else "")
                    + (f" **Open items:** {', '.join(c['open_items'])}." if c["open_items"] else ""),
                    "", "Scope:"] + [f"- {s}" for s in c["scope"]] + ["", "Acceptance:"] + \
                   [f"- [ ] {a}" for a in c["acceptance"]] + ["", "Evidence: " + "; ".join(c["evidence"]) + ".", ""]
    return "\n".join(out)


def dump(obj) -> str:
    return json.dumps(obj, indent=1, ensure_ascii=False, default=list) + "\n"


def main():
    pack, md = build()
    outputs = {"factory-pack.json": dump(pack), "CARDS.md": md}
    files = sorted(set(["README.md", "INGEST.md", "build_pack.py", "test_pack.py"] +
                       [f"src/{p.name}" for p in (HERE / "src").glob("*.json")]))
    manifest = dict(schema=SCHEMA, pack_version=PACK_VERSION,
                    files={f: hashlib.sha256((outputs[f] if f in outputs else (HERE / f).read_text()).encode()).hexdigest()
                           for f in sorted(files + list(outputs))})
    outputs["manifest.json"] = dump(manifest)
    if "--check" in sys.argv:
        stale = [f for f, t in outputs.items() if not (HERE / f).exists() or (HERE / f).read_text() != t]
        print("pack up to date" if not stale else f"stale: {stale}")
        sys.exit(1 if stale else 0)
    for f, t in outputs.items():
        (HERE / f).write_text(t)
    bad = [c["id"] for c in pack["claims"] if not c["verified"]]
    print(f"wrote {', '.join(outputs)}; {len(pack['cards'])} cards; claims unverified: {bad or 'none'}")


if __name__ == "__main__":
    main()
