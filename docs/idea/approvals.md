# Approval register: Idea-to-Live Factory, from decision to card backlog

Owner: Isa. Scenario: **Amend** the existing Factory through the ingestion pack ([`pack/`](../../pack/)). Source: Idea Record r12.4 ([`constitutional-factory.md`](constitutional-factory.md)) and Isa's answers of 27 Sep 2026. The machine-readable copy is `pack/src/approvals.json`; `pack/test_pack.py` checks that the two agree.

**Sixteen approval records in three gates.**
- **Isa signs fifteen.** AR-14, the backlog admission, is done by the existing Factory's Director under the Ratified Plan.
- **Gates 1 and 2 put the change on the backlog.**
- **Gate 3 records are signed just in time,** before the first card that needs them starts.

**What changed with Isa's answers:**
- The Factory ingests the pack and first checks it against its own code (Fit Report, C0.00).
- Volumes are measured, not assumed (Phase 0).
- AR-12 splits: trial criteria before the backlog (AR-12a), trial dates after it (AR-12b).
- Key custody is settled: the Owner holds the keys, hashed in the Factory.
- Value is measured in two segments rather than set in advance:
  - cost from idea to artifact;
  - return from ratification to production and monetisation.
- AR-09's mapping work moves into the Fit Report and the cards; only Isa's two decisions remain (AR-09a, AR-09b).

Status key:
- **Ready:** the evidence exists; the record can be signed now.
- **To produce:** a draft must be written first.
- **Waits on:** named work must finish first.

---

## Gate 1: Decide the idea (exit Idea stage)

One sitting. All evidence exists.

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-01 (H1) | **Constitution** | The eight principles, the five golden allocation rules and rules R1–R20, as extracted verbatim in the pack | Isa | Ready |
| AR-02 (H4) | **Model portfolio** | The rolling policy (P1, P2, P6–P8) and the starting menu of seven models on API tokens. This replaces "start from today's four models" | Isa | Ready |
| AR-03 (H5) | **Work tiers** | Three absolute tiers for cards | Isa | Ready |
| AR-04 (H6) | **Trial operating rules** | The Scaler (R14) with held demand counted, a 15-minute target, a 1-hour cost-band wait, quality floor 0.8 and cost band 1.5. Also R15 (no data-training tiers), R16 (burn cap), R17–R19, and R20 for any searched configuration | Isa | Ready |
| AR-05 (H7) | **Trial budget and value measure** | An initial monthly ceiling of about $2,500, with the hourly cap at 2× the trailing seven-day average. The ceiling resets by R16's formula once real volume is measured. Value is measured, not set: cost from idea to artifact (M06), and return from ratification to production and monetisation (M07) | Isa | Ready |
| AR-06 (H3) | **Exit Idea stage** | Move to design under the Amend scenario, through the pack | Isa | Ready once AR-01 to AR-05 are signed |

---

## Gate 2: Onto the backlog

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-07 | **Alignment Record and authority to ingest** | The pack's intent, assumptions, experiments and open items (`pack/README.md` §1). It authorises the Factory to ingest the pack and produce the Fit Report, and nothing else | Isa | Ready once AR-06 is signed |
| AR-11 | **Protected governance paths** | The protected path list, and the interim gate (Checker plus Isa) until the Release Gate exists | Isa | To produce: the path list comes from the Fit Report |
| AR-12a | **Trial criteria and measurement plan** | Measures M01–M20; the shadow periods; the trial configuration to predict; success and kill criteria from X1–X14; rollback to Director → Worker → Checker | Isa | To produce: drafted by the Director from the pack |
| AR-13 | **Ratified Plan** | The pack's 45 card seeds plus the Fit Report's deltas, with every `[PROPOSED]` threshold accepted or changed | Isa | To produce: after the Fit Report |
| AR-14 | **Backlog admission** | Create the Phase 0 cards, each carrying its pack card ID. Later phases are admitted on phase-exit approval: through the interim gate for Phases 0–1, then through the Release Gate | Director | To produce |

---

## Gate 3: Just in time

| # | Record | What is approved | Before | Owner | Status |
|---|---|---|---|---|---|
| AR-08 (H2) | **Quality standards and constants** | Maximum markdown rate per institution and tier, set from the baseline's measured variance; any constant not fixed in the constitution | C1.06 | Isa | Waits on C0.11 |
| AR-10 | **Vendor and data terms** | API accounts with the menu's vendors; no-training terms for every tier used (R15); rate limits as Scaler caps; routes, including a second route for Muse Spark; Muse Spark in the Owner's region [Unverified]; review of the terms for Heliosvera IP by a qualified adviser where they are unclear. Key custody is settled; OI-04 remains | C1.03 | Isa | To produce |
| AR-09a | **Owner of live operation** | Who owns incident, restore and hotfix | C2.03 | Isa | Open: Isa decides |
| AR-09b | **Ratification tiers and attention budget** | Which ideas need Isa's ratification, which the Council may ratify, and her weekly attention budget | C3.04 | Isa | Open: Isa decides |
| AR-12b | **Trial dates and scope** | Start, duration and scope, from the backlog forecast and measured demand | CT.01 | Isa | Waits on C0.14 and C1.18 |

---

## After the backlog (not needed to get there)

- A phase-exit approval for each phase: through the interim gate for Phases 0–1, then through the Release Gate.
- The trial go / no-go (CT.03) against AR-12a's criteria.
- Constitutional amendments as the trial teaches: human-ratified, each as a new version.

---

## Isa's sittings

| Sitting | Records | What it takes |
|---|---|---|
| 1: decide | AR-01 to AR-07 | Read the Idea Record §5.5–§5.8, `pack/README.md` and this register |
| 2: commit | AR-11, AR-12a, AR-13 | After the Fit Report and the Director's drafts; the Phase 0 cards follow (AR-14) |
| Just in time | AR-08, AR-10, AR-09a, AR-09b, AR-12b | Each when its card is next |

---

## What is still open

The open items live in `pack/src/open_items.json`, each with its resolver. The ones that need Isa:
- **OI-04:** [Inference] a hash cannot authenticate an API call, so confirm where the usable credential is held.
- **OI-05:** the source and unit for monetisation and return data [PLACEHOLDER].
- **OI-09:** who owns live operation (AR-09a).
- **OI-10:** ratification tiers and attention budget (AR-09b).
- **OI-12:** the starting licence for new menu models (R11 against §5.1), decided in AR-13.
- **OI-16:** the lengths of the shadow periods (AR-12a).
