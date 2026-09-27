# Approval register: Idea-to-Live Factory, from decision to card backlog

Owner: Isa. Scenario: **Amend** the existing Factory through the ingestion pack ([`pack/`](../../pack/)), as a **dog-food build**. Source: Idea Record r12.5 ([`constitutional-factory.md`](constitutional-factory.md)) and Isa's answers of 27 Sep 2026. The machine-readable copy is `pack/src/approvals.json`; `pack/test_pack.py` checks that the two agree.

**Fifteen approval records in three gates.**
- **Isa signs fourteen.** AR-14, the backlog admission, is done by the existing Factory's Director under the Ratified Plan.
- **Gates 1 and 2 put the change on the backlog.**
- **Gate 3 records are signed just in time,** before the first card that needs them starts.

**What changed with Isa's answers:**
- **No lab.** There is no study period, shadow run, replay or trial. Each part is switched on for the Factory's own work once it passes its acceptance contract, then improved from live data.
- **Baselines from the analysis, replaced by actuals.** Costs come from live metering plus the actual costs the Owner enters. Value is in USD per idea.
- **Live operation is part of the Factory** (AR-09a).
- **AR-12 is a monitoring and improvement plan.** AR-12a and AR-12b are withdrawn.
- **AR-08 and AR-09a move to Gate 2.** Both have derived baselines ready to sign.

Status key:
- **Ready:** the evidence or baseline exists; the record can be signed now.
- **To produce:** a draft must be written first.

---

## Gate 1: Decide the idea (exit Idea stage)

One sitting. All evidence exists.

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-01 (H1) | **Constitution** | The eight principles, the five golden allocation rules and rules R1–R20, as extracted verbatim in the pack | Isa | Ready |
| AR-02 (H4) | **Model portfolio** | The rolling policy (P1, P2, P6–P8) and the starting menu of seven models on API tokens. This replaces "start from today's four models" | Isa | Ready |
| AR-03 (H5) | **Work tiers** | Three absolute tiers for cards | Isa | Ready |
| AR-04 (H6) | **Operating rules** | For the build and live use: the Scaler (R14) with held demand counted, a 15-minute target, a 1-hour cost-band wait, quality floor 0.8 and cost band 1.5. Also R15 (no data-training tiers), R16 (burn cap), R17–R19, and R20 for any searched configuration | Isa | Ready |
| AR-05 (H7) | **Trial budget and value measure** | An initial monthly ceiling of about $2,500, with the hourly cap at 2× the trailing seven-day average. Baselines come from the cost model; live metering and the actual costs the Owner enters (invoices, subscriptions, cloud credits) replace them, and the ceiling resets from actuals. Value in USD: a baseline per idea at intake, then actual cost to artifact (M06) and actual return (M07) | Isa | Ready |
| AR-06 (H3) | **Exit Idea stage** | Move to design under the Amend scenario, through the pack | Isa | Ready once AR-01 to AR-05 are signed |

---

## Gate 2: Onto the backlog

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-07 | **Alignment Record and authority to ingest** | The pack's intent, assumptions, experiments and open items (`pack/README.md` §1). It authorises the Factory to ingest the pack and produce the Fit Report, and nothing else | Isa | Ready once AR-06 is signed |
| AR-08 (H2) | **Quality standards and constants** | Initial maximum markdown rate per step: 1 minus the R19 floor. That is 20% for design, plan, plan red-team, security review, acceptance test and release; 40% for other steps; 50% for review [PROPOSED]. Adjusted from live variance | Isa | Ready: baseline derived |
| AR-09a | **Owner of live operation** | Live operation is part of the Factory. The Ledger detects incidents; the owner restores by reverting the causing change; hotfixes are ordinary cards through the Market and Court. The owner is the Checker until the Release Gate exists, then the Release Gate [PROPOSED]. This extends the Release Gate's charter, so it is a constitutional amendment | Isa | Ready: owner proposed |
| AR-11 | **Protected governance paths** | The protected path list, and the interim gate (Checker plus Isa) until the Release Gate exists | Isa | To produce: the path list comes from the Fit Report |
| AR-12 | **Monitoring and improvement plan** | Measures M01–M20. A weekly report and alarms: when live results fall more than 25% outside the model, or any X1–X14 falsification criterion is met, a card is opened; work does not stop. Amendments pass the Release Gate and Isa | Isa | Ready |
| AR-13 | **Ratified Plan** | The pack's 42 card seeds plus the Fit Report's deltas, with every `[PROPOSED]` value accepted or changed | Isa | To produce: after the Fit Report |
| AR-14 | **Backlog admission** | Create the Phase 0 cards, each carrying its pack card ID. Later phases are admitted on phase-exit approval: through the interim gate for Phases 0–1, then through the Release Gate | Director | To produce |

---

## Gate 3: Just in time

| # | Record | What is approved | Before | Owner | Status |
|---|---|---|---|---|---|
| AR-10 | **Vendor and data terms** | API accounts with the menu's vendors; no-training terms for every tier used (R15); rate limits as Scaler caps; routes, including a second route for Muse Spark; Muse Spark in the Owner's region [Unverified]; review of the terms for Heliosvera IP by a qualified adviser where they are unclear. Key custody is settled; OI-04 remains | C1.03 | Isa | To produce |
| AR-09b | **Ratification tiers and attention budget** | Which ideas need Isa's ratification, which the Council may ratify, and her weekly attention budget | C3.04 | Isa | Open: Isa decides |

---

## After the backlog

- A phase-exit approval for each phase: through the interim gate for Phases 0–1, then through the Release Gate.
- Amendment cards opened by the weekly alarms or by a falsified experiment (C4.01). Each is human-ratified and becomes a new version.

---

## Isa's sittings

| Sitting | Records | What it takes |
|---|---|---|
| 1: decide | AR-01 to AR-07 | Read the Idea Record §5.5–§5.8, `pack/README.md` and this register |
| 2: commit | AR-08, AR-09a, AR-11, AR-12, AR-13 | After the Fit Report; the Phase 0 cards follow (AR-14) |
| Just in time | AR-10, AR-09b | Each when its card is next |

---

## What is still open

The open items live in `pack/src/open_items.json`, each with its resolver. The ones that need Isa:
- **OI-04:** [Inference] a hash cannot authenticate an API call, so confirm where the usable credential is held.
- **OI-10:** ratification tiers and attention budget (AR-09b).
- **OI-12:** the starting licence for new menu models. [PROPOSED] Artificial Analysis band as prior, corrected live; decided in AR-13.
- **Actual costs:** the Owner enters invoices, subscriptions and cloud credits into the value ledger (C0.09) as they are paid.
