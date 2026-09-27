# Idea-to-Live Factory: ingestion pack

**For:** the existing Factory (Director → Worker → Checker), and Isa.
**What it is:** everything the Factory needs to rebuild itself as the constitutional institutions. Rules, evidence, measures, approvals, open items and card seeds, in one machine-readable file (`factory-pack.json`) with a readable card list (`CARDS.md`).
**How to use it:** [`INGEST.md`](INGEST.md).

---

## 1. Intent: the draft Alignment Record for AR-07

**Change.** Replace Director → Worker → Checker with the eight constitutional institutions under rules R1–R20.
- Agents pull cards; nobody assigns work.
- Licences are earned by evidence.
- Capacity is elastic instances of a seven-model menu on API tokens.
- Every rule runs in the Ledger, not in an agent.

**Why.** In the value-stream model, the institutions deliver the most clean ideas of every organisation tested (CL-07, CL-08).
- With 25% dependency coupling, the institutions with R17 deliver 19.4 clean ideas a week with the six models.
- Director → Worker → Checker delivers 10.3 on the same work.
- These are synthetic results. The trial exists to test them on real work.

**In scope**
- Protecting governance.
- Measuring today's Factory.
- A simulation twin calibrated on those measurements.
- The rules and institutions, cut over phase by phase with rollback.
- A trial judged against pre-registered predictions.

**Out of scope**
- Data-residency analysis (OI-14; future).
- Any model tier that trains on our data (R15).
- Kernel assignment from the parked design.

**Assumptions carried.** Every simulator constant is listed in `twin_parameters` as assumed until C0.12 calibrates it. The token model, pass curve, catch rates and demand are synthetic.

**Minority positions and conflicts**, recorded so none is silently resolved:
- **OI-12:** R11 and §5.1 disagree on where a new model starts.
- **C3.01:** the institutional model found two Inquiry analysts sufficient, while X7 tests universal participation.
- **C1.07:** R7 protects subscription caps, but the menu runs on API tokens, so R7 is dormant unless a capped seat is admitted.

---

## 2. What Isa's answers of 27 Sep 2026 changed

| Question | Isa's answer | What the pack does |
|---|---|---|
| Where the backlog lives | The existing Factory runs Director → Worker → Checker and moves to the institutions | The Factory ingests this pack. The Director first produces a Fit Report (C0.00) against the real code, because the pack's author has not seen it |
| Card and idea volumes | Build the infrastructure to measure, validate and understand against the simulation | Phase 0 measures today's Factory (C0.04–C0.11) and packages the simulation as a twin (C0.10). It calibrates the twin (C0.12), backcasts today's Factory (C0.13, X9) and pre-registers predictions before the trial (C0.14) |
| Trial dates | Set once the cards are in the backlog | AR-12 is split. **AR-12a** (criteria and measurement) comes before the backlog; **AR-12b** (dates and scope) comes after, from the backlog forecast and measured demand |
| Vendor accounts and keys | The Owner; hashed in the Factory | AR-10 key custody is settled. C0.05 keeps secrets out of the Ledger and records fingerprints. **Residual (OI-04):** [Inference] a hash cannot call an API, so confirm where the usable credential is held |
| Value of a clean idea | No action, no value. Measure idea → artifact cost, then ratification → production → return | The idea value ledger (C0.09) records both segments (M06, M07). AR-05 keeps the initial ceiling (CL-04) and resets it from measured volume |

---

## 3. Approval records

**Sixteen records in three gates.** Isa signs fifteen; AR-14, the backlog admission, is done by the Director. Full detail is in [`docs/idea/approvals.md`](../docs/idea/approvals.md) and `factory-pack.json` → `approvals`.

| Gate | Records | When |
|---|---|---|
| 1. Decide | AR-01 constitution; AR-02 portfolio; AR-03 tiers; AR-04 trial rules; AR-05 budget and value measure; AR-06 exit Idea stage | Now; all Ready |
| 2. Onto the backlog | AR-07 Alignment Record and authority to ingest; AR-11 protected paths; AR-12a trial criteria; AR-13 Ratified Plan; AR-14 admission of Phase 0 | After ingestion and the Fit Report |
| 3. Just in time | AR-08 standards (before C1.06); AR-10 vendor terms (before C1.03); AR-09a live-operation owner (before C2.03); AR-09b ratification tiers (before C3.04); AR-12b trial dates (before CT.01) | During the build |

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
