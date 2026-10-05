# Ingestion protocol

**Reader:** every agent in the Factory.
**Task:** load this pack's cards into the pull queue and start work as a collective, so the Factory rebuilds itself as the constitutional institutions.
**Authority:** AR-07 authorises loading. Cards enter the queue only after AR-13 (ratified plan) and AR-14 (mechanical load).

There are no named roles. From the first card, the Factory works the way the constitution says it will:
- **Nobody assigns work.** An agent with a free slot pulls the oldest ready card it is licensed for (R1, R3). Starting licences come from what each model already did well (R11).
- **Another family checks.** A model of a different family checks every card, after the deterministic checks: tests and CI (R18).
- **Each card is grounded in the code by its puller.** The puller reads the files the card touches and cites them with the commit.
- **Splits are recorded.** A puller may split a card into child cards that together meet its acceptance contract.
- **A card whose premise does not hold goes back to its author** (Planning) with evidence (R8). It is not reshaped.
- **The rules in the Ledger do the managing.** Card C0.17 encodes this operating mode in the Factory's code.

---

## The integrity contract

These rules are also in `factory-pack.json` → `integrity_rules`.

1. **Do not infer.** A `[PLACEHOLDER]` or open item (`OI-*`) is resolved only by its named resolver. Record the resolution.
2. **Keep the labels.**
   - `[PROPOSED]` is a design proposal Isa ratifies in AR-13.
   - `[Unverified]` and `[Inference]` stay until evidence closes them.
3. **Simulation outputs are the baseline, never measured facts.** Live data replaces them (C0.12).
4. **Rule text is verbatim.** R1–R20, X1–X14 and H1–H7 change only by amendment: the Release Gate and Isa (principle 8).
5. **Seeds are split, never reshaped.** Merging, dropping or widening a seed needs Isa.
6. **The pack wins over the parked design.** Do not build kernel assignment, Thompson sampling or shadow prices.
7. **No secrets.** No key, token or credential goes into the pack, the Ledger, a card or a log. Record fingerprints only (C0.05).
8. **Dog-food build.** No lab, shadow period or trial. Switch each part on for the Factory's own work once it passes its acceptance contract, and improve it from live data.

---

## Steps

| # | Step | Gate |
|---|---|---|
| 1 | **Verify.** `python3 pack/build_pack.py --check` and `python3 -m unittest discover -s pack` pass; the sha256 of every file in `manifest.json` matches | – |
| 2 | **Ratify.** Isa signs Gate 1 (AR-01 to AR-06), then Gate 2 (AR-07, AR-08, AR-09a, AR-11, AR-12, AR-13) | AR-13 |
| 3 | **Load.** Phase 0 cards go into the pull queue with their pack card IDs (mechanical; nobody chooses) | AR-14 |
| 4 | **Pull.** The collective pulls. C0.01 (register the pack) and C0.02 (protected paths) come first by dependency. C0.17 (the pull queue) encodes the operating mode | – |
| 5 | **Next phase.** Each later phase loads when the previous phase's exit is approved: through the interim gate for Phases 0–1 (another family's pass plus Isa), then through the Release Gate | Phase exit |

**Just-in-time approvals:** a card stays unpullable until every record in its `requires_approval` is signed.
- AR-10 before C1.03.
- AR-09b before C3.04.
- AR-15 (amendment: quality, cost and speed; readiness hand-back) before C1.14 and C1.19.
- AR-16 (amendment: institutions as harnesses; model flexibility; central memory) before C0.18, C0.19 and C2.05.
- AR-18 (amendment: primitives and industrialising the repeated) before C2.05.
- AR-19 (amendment: edge cases, self-origination and the ratification envelope) before C1.20, C1.21, C1.22, C2.06 and C3.05.
- AR-09b before C1.22 as well as C3.04: the envelope runs from Phase 1.
- AR-20 (amendment: recorded behaviour, lessons, decision rights and outcomes) before C1.23, C1.24, C1.25, C2.07, C3.06 and C3.07.

## What comes back to Isa

- The weekly report and alarms (C0.15).
- Cards returned under R8 with evidence.
- Ratification requests the rules route to her, and her sample of rule ratifications (C1.22, C3.04).
- Phase-exit approvals.

## Where each part of the pack lives

| `factory-pack.json` key | What it is | Source |
|---|---|---|
| `constitution` | Idea, problems, rules, constants, golden rules, institutions, human touchpoints, portfolio rules, principles, threats, settled questions, experiments, design questions, decisions, risks, findings §5.3–5.8 | Extracted from `docs/idea/constitutional-factory.md` |
| `operating_parameters` | The numbers the rules fix, each quoted from its rule | `src/parameters.json`, checked against rule text |
| `menu` | The seven models on API tokens | `probes/portfolio6/select6.json` |
| `measures` | What the Factory records, and the simulator field it compares with | `src/measures.json` |
| `twin_parameters` | Every assumed constant in the model, refitted weekly from live data | Read from `vs_sim.py` and `select6.py` |
| `predictions` | The model's baseline figures | Probe result JSON files |
| `claims` | Every figure used in hand-written text, with its source | `src/claims.json`, verified |
| `approvals` | 21 approval records in four gates | `src/approvals.json` |
| `open_items` | What the pack does not know, and who resolves it | `src/open_items.json` |
| `phases`, `cards` | 5 phases, 55 card seeds with acceptance contracts and a dependency graph | `src/cards.json` |
| `sources`, `evidence_files` | Full text of the Idea Record and evidence documents; hashes of every probe file | Repository |
