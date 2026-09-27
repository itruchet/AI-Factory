# Idea-to-Live Factory: ingestion pack

**For:** every agent in the Factory, and Isa.
**What it is:** everything the Factory needs to rebuild itself as the constitutional institutions. Rules, evidence, measures, approvals, open items and card seeds, in one machine-readable file (`factory-pack.json`) with a readable card list (`CARDS.md`).
**How to use it:** [`INGEST.md`](INGEST.md).

---

## 1. Intent: the draft Alignment Record for AR-07

**Change.** Replace role routing (Director → Worker → Checker) with the eight constitutional institutions under rules R1–R20. There are no named roles: from the first card, agents pull as a collective and another family checks.
- Agents pull cards; nobody assigns work.
- Licences are earned by evidence.
- Capacity is elastic instances of a seven-model menu on API tokens.
- Every rule runs in the Ledger, not in an agent.

**Why.** In the value-stream model, the institutions deliver the most clean ideas of every organisation tested (CL-07, CL-08).
- With 25% dependency coupling, the institutions with R17 deliver 19.4 clean ideas a week with the six models.
- Director → Worker → Checker delivers 10.3 on the same work.
- These are synthetic results: the baseline, until live data replaces them.

**How it is built: dog food, not a lab.**
- No study period, shadow run or trial. Each part is switched on for the Factory's own work once it passes its acceptance contract, then improved from live data.
- Baselines come from this analysis: the cost model, the R19 floors, the model's predictions.
- Live metering and the actual costs the Owner enters (invoices, subscriptions, cloud credits) replace the baselines.
- Weekly alarms (C0.15) open a card when live results fall more than 25% outside the model, or when an experiment's falsification criterion is met. They never stop work.

**In scope**
- Protecting governance.
- Live measurement from day one.
- Live operation inside the Factory: detect, restore, hotfix.
- The rules and institutions, switched on phase by phase.
- A model of the Factory, refitted weekly on CPU with no model spend.

**Out of scope**
- Data-residency analysis (OI-14; future).
- Any model tier that trains on our data (R15).
- Kernel assignment from the parked design.
- Lab spend: replays, shadow periods, trials.

**Assumptions carried.** Every simulator constant is listed in `twin_parameters` as assumed until C0.12 fits it from live data.

**Conflicts recorded, not silently resolved**
- **OI-12:** R11 and §5.1 disagree on where a new model starts. [PROPOSED] Artificial Analysis band as prior, corrected live.
- **C3.01:** two Inquiry analysts (model sizing) against universal participation (X7). Live data decides.
- **C1.07:** R7 protects subscription caps; the menu runs on API tokens, so R7 is dormant unless a capped seat is admitted.

---

## 2. What Isa's answers of 27 Sep 2026 changed

| Question | Isa's answer | What the pack does |
|---|---|---|
| Where the backlog lives | The existing Factory runs Director → Worker → Checker and moves to the institutions | The pack's cards load into one pull queue. The collective pulls from the first card (C0.17), and each puller grounds its card in the code. A card whose premise fails returns with evidence (R8); no role pre-reads the code |
| Volumes and validation | Measure and understand against the simulation, but no lab: build it, use it, monitor and improve | Measurement is live from day one (C0.11). The model is refitted weekly (C0.12) and compared with live results (C0.15). No shadow periods, replay or backcast gate |
| Trial dates | No trial | AR-12 is a monitoring and improvement plan. Experiments X1–X14 are judged continuously (C4.01) |
| Vendor accounts and keys | The Owner; hashed in the Factory | Settled. C0.05 keeps secrets out of the Ledger and records fingerprints. **Residual (OI-04):** [Inference] a hash cannot call an API, so confirm where the usable credential is held |
| Value of an idea | Baseline from the analysis; actuals replace it; the Owner provides real costs | Unit USD. Each idea gets a baseline cost and expected return at intake; metered spend, Owner-entered costs and recorded returns replace them (C0.09; M06, M07) |
| Live operation | Part of the Factory | C0.16 from Phase 0: the Ledger detects incidents, the owner reverts, hotfixes are ordinary cards. Until the Release Gate exists, incidents and restores are top-priority cards any agent pulls; then the Release Gate owns them (C2.03) [PROPOSED] |

---

## 3. Approval records

**Fifteen records in three gates.** Isa signs fourteen; AR-14 is a mechanical load into the pull queue. Full detail is in [`docs/idea/approvals.md`](../docs/idea/approvals.md) and `factory-pack.json` → `approvals`.

| Gate | Records | When |
|---|---|---|
| 1. Decide | AR-01 constitution; AR-02 portfolio; AR-03 tiers; AR-04 operating rules; AR-05 budget and value measure; AR-06 exit Idea stage | Now; all Ready |
| 2. Onto the backlog | AR-07 Alignment Record and authority to ingest; AR-08 baseline standards; AR-09a live operation; AR-11 protected paths; AR-12 monitoring and improvement plan; AR-13 Ratified Plan; AR-14 admission of Phase 0 | Straight after Gate 1; then Phase 0 loads |
| 3. Just in time | AR-10 vendor terms (before C1.03); AR-09b ratification tiers (before C3.04) | During the build |

---

## 4. Why the pack can be trusted

`test_pack.py` fails the build if any of the following checks fails.

**Nothing invented**
- Rule, experiment and decision text is verbatim from the Idea Record.
- Every operating parameter is quoted from its rule.
- Every figure in hand-written text is a claim, re-read from its source result file.
- Every measure names a simulator field that exists.
- No secret patterns appear anywhere in the pack.

**Nothing forgotten**
- The Idea Record is complete: R1–R20, X1–X14, H1–H7, 8 principles, 8 institutions, 11 problems and 5 golden rules.
- Every live rule, golden rule, principle, institution and problem is traced by a card.
- Every experiment is both instrumented and judged.
- Every design question and risk is routed.
- Every decision has an approval record.
- Every measure is recorded by a card.
- Every simulator constant is listed for calibration.

**Plan is sound**
- The card graph is acyclic and phase-ordered.
- Every card after C0.02 sits behind protected governance.
- Approvals come in order, and just-in-time approvals are wired to their cards.
- No card ratifies itself.

**Current**
- The committed pack equals a fresh build.
- Every source and evidence file matches its sha256.

---

## 5. Files

| File | Written by |
|---|---|
| `factory-pack.json` | `build_pack.py` (do not edit) |
| `CARDS.md` | `build_pack.py` (do not edit) |
| `manifest.json` | `build_pack.py`: sha256 of every pack file |
| `src/cards.json`, `src/approvals.json`, `src/open_items.json`, `src/measures.json`, `src/parameters.json`, `src/claims.json` | Hand-written seeds, cross-checked by the tests |
| `INGEST.md` | The Factory's ingestion protocol |

```
python3 pack/build_pack.py                 # rebuild factory-pack.json, CARDS.md, manifest.json
python3 pack/build_pack.py --check         # is the committed pack current?
python3 -m unittest discover -s pack       # integrity checks
```
