# Ingestion protocol: for the existing Factory

**Reader:** the Director of the existing Factory (Director → Worker → Checker).
**Task:** ingest this pack, check it against your own codebase, and put the ratified cards on your backlog so the Factory rebuilds itself as the constitutional institutions.
**Authority:** AR-07 (Isa) authorises steps 1–4 only. Nothing reaches the backlog before AR-13 and AR-14.

---

## The integrity contract

These rules are also in `factory-pack.json` → `integrity_rules`. They apply to every card built from this pack.

1. **Do not infer.** A `[PLACEHOLDER]` or an open item (`OI-*`) is resolved only by its named resolver. Record the resolution; do not guess it.
2. **Keep the labels.**
   - `[PROPOSED]` is a design proposal for Isa to ratify in AR-13, not evidence.
   - `[Unverified]` and `[Inference]` stay attached until evidence closes them.
3. **Simulation outputs are hypotheses.** Everything under `predictions`, `claims` and the Idea Record's findings is synthetic. Never report it as measured.
4. **Rule text is verbatim.** Rules R1–R20, experiments X1–X14 and decisions H1–H7 are extracted word for word from the Idea Record. They change only by constitutional amendment: the Release Gate and Isa (principle 8).
5. **Seeds are split, never reshaped.** You may split a card seed into several Factory cards. Merging, dropping or widening a seed needs an approved delta in AR-13.
6. **The pack wins over the parked design.** `docs/design-parked/` is r3 material. Where it conflicts with the pack, the pack wins. In particular, do not build kernel assignment, Thompson sampling or shadow prices: pull rules replace them.
7. **No secrets.** No key, token or credential goes into the pack, the Ledger, a card or a log. Record key fingerprints only (C0.05).

---

## Steps

| # | Step | Output | Gate |
|---|---|---|---|
| 1 | **Verify.** Run `python3 pack/build_pack.py --check` and `python3 -m unittest discover -s pack` at the pack's commit. Check the sha256 of every file in `manifest.json`. | Pass, or stop and report | – |
| 2 | **Read.** Read `factory-pack.json` in full: the constitution, operating parameters, menu, measures, twin parameters, predictions, approvals, open items and cards. The embedded `sources` carry the full Idea Record and evidence documents. | – | – |
| 3 | **Fit Report (card C0.00).** Map every card seed onto your codebase, answer every open item marked "Fit Report", and list proposed deltas with evidence (file paths and commit). | Fit Report | AR-07 |
| 4 | **Draft for Isa.** Draft AR-11 (protected path list, from the Fit Report) and AR-12a (measures, shadow period, trial configuration, success and kill criteria from X1–X14). | Drafts | – |
| 5 | **Ratification.** Isa signs AR-11, AR-12a, then AR-13: the card seeds plus the approved deltas, with every `[PROPOSED]` threshold accepted or changed. | Ratified Plan | AR-13 |
| 6 | **Admission (AR-14).** Create the Phase 0 cards only. Each Factory card carries its pack card ID and the pack version. | Phase 0 backlog | AR-14 |
| 7 | **Report the mapping.** Record pack card ID → Factory card ID(s) in the Ledger (C0.01) as cards are created. | Mapping | – |
| 8 | **Later phases.** Admit each phase only after the previous phase's exit is approved. For Phases 0–1 that is the interim gate (Checker plus Isa, C0.02); from Phase 2 it is the Release Gate (C2.02). | Next phase | Phase exit |

**Just-in-time approvals** (Gate 3): do not start a card until every record in its `requires_approval` is signed.
- AR-08 before C1.06.
- AR-10 before C1.03.
- AR-09a before C2.03.
- AR-09b before C3.04.
- AR-12b before CT.01.

---

## What to return to Isa

1. The verification result (step 1).
2. The Fit Report (step 3), including every answered open item.
3. The drafts of AR-11 and AR-12a (step 4).
4. After admission, the card mapping (step 7) and the backlog forecast. AR-12b sets the trial dates from that forecast.

## Where each part of the pack lives

| `factory-pack.json` key | What it is | Source |
|---|---|---|
| `constitution` | Idea, problems, rules, constants, golden rules, institutions (with protections and memory), human touchpoints, portfolio rules, principles, threats, settled questions, experiments, design questions, decisions, risks, findings §5.3–5.8 | Extracted from `docs/idea/constitutional-factory.md` |
| `operating_parameters` | The numbers the rules fix, each quoted from its rule | `src/parameters.json`, checked against rule text |
| `menu` | The seven models on API tokens | `probes/portfolio6/select6.json` |
| `measures` | What the Factory must record, and the simulator field it compares with | `src/measures.json` |
| `twin_parameters` | Every assumed constant in the simulator, to calibrate | Read from `vs_sim.py` and `select6.py` |
| `predictions` | Uncalibrated predictions: the prior for C0.14 | Probe result JSON files |
| `claims` | Every figure used in hand-written text, with its source | `src/claims.json`, verified |
| `approvals` | 16 approval records in three gates | `src/approvals.json` |
| `open_items` | What the pack does not know, and who resolves it | `src/open_items.json` |
| `phases`, `cards` | 5 phases, 45 card seeds with acceptance contracts and a dependency graph | `src/cards.json` |
| `sources`, `evidence_files` | Full text of the Idea Record and evidence documents; hashes of every probe file | Repository |
