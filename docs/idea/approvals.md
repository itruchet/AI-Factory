# Approval register: Idea-to-Live Factory, from decision to card backlog

Owner: Isa. Scenario: **Amend** the existing Factory through the ingestion pack ([`pack/`](../../pack/)), as a **dog-food build**. Source: Idea Record r12.6 ([`constitutional-factory.md`](constitutional-factory.md)) and Isa's answers of 27 Sep 2026. The machine-readable copy is `pack/src/approvals.json`; `pack/test_pack.py` checks that the two agree.

**Status, 27 Sep 2026: Gates 1 and 2 are signed** (AR-01 to AR-13, except the just-in-time AR-09b and AR-10). The `[PROPOSED]` values in AR-08, AR-09a and AR-13 are accepted as proposed. Next: AR-14 loads the Phase 0 cards into the pull queue.

**Status, 5 Oct 2026: every Gate 4 amendment is signed** (AR-15 to AR-20). Still open: AR-09b (Isa sets the envelope's bounds and ceiling; no fixed weekly budget, her decision of 1 Oct 2026), AR-10 (vendor and data terms, to produce) and AR-14 (the mechanical load).

**Twenty-one approval records in four gates.**
- **Isa signs twenty.** AR-14 is a mechanical load of the ratified cards into the pull queue.
- **Gates 1 and 2 put the change on the backlog.**
- **Gate 3 records are signed just in time,** before the first card that needs them starts.

**What changed with Isa's answers:**
- **No lab.** There is no study period, shadow run, replay or trial. Each part is switched on for the Factory's own work once it passes its acceptance contract, then improved from live data.
- **Baselines from the analysis, replaced by actuals.** Costs come from live metering plus the actual costs the Owner enters. Value is in USD per idea.
- **Live operation is part of the Factory** (AR-09a).
- **AR-12 is a monitoring and improvement plan.** AR-12a and AR-12b are withdrawn.
- **AR-08 and AR-09a move to Gate 2.** Both have derived baselines ready to sign.
- **No named roles.** From the first card, the Factory's agents pull as a collective and another family checks. Each card's puller grounds it in the code, and a card whose premise fails returns with evidence (R8). There is no pre-read report, so all of Gate 2 is ready except the load.

Status key:
- **Ready:** the evidence or baseline exists; the record can be signed now.
- **To produce:** a draft must be written first.

---

## Gate 1: Decide the idea (exit Idea stage)

One sitting. All evidence exists.

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-01 (H1) | **Constitution** | The eight principles, the five golden allocation rules and rules R1–R20, as extracted verbatim in the pack | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-02 (H4) | **Model portfolio** | The rolling policy (P1, P2, P6–P8) and the starting menu of seven models on API tokens. This replaces "start from today's four models" | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-03 (H5) | **Work tiers** | Three absolute tiers for cards | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-04 (H6) | **Operating rules** | For the build and live use: the Scaler (R14) with held demand counted, a 15-minute target, a 1-hour cost-band wait, quality floor 0.8 and cost band 1.5. Also R15 (no data-training tiers), R16 (burn cap), R17–R19, and R20 for any searched configuration | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-05 (H7) | **Budget and value measure** | An initial monthly ceiling of about $2,500, with the hourly cap at 2× the trailing seven-day average. Baselines come from the cost model; live metering and the actual costs the Owner enters (invoices, subscriptions, cloud credits) replace them, and the ceiling resets from actuals. Value in USD: a baseline per idea at intake, then actual cost to artifact (M06) and actual return (M07) | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-06 (H3) | **Exit Idea stage** | Move to design under the Amend scenario, through the pack | Isa | **Signed by Isa, 27 Sep 2026** |

---

## Gate 2: Onto the backlog

| # | Record | What is approved | Owner | Status |
|---|---|---|---|---|
| AR-07 | **Alignment Record and authority to ingest** | The pack's intent, assumptions, experiments and open items (`pack/README.md` §1). It authorises loading the pack, and nothing else until AR-13 | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-08 (H2) | **Quality standards and constants** | Initial maximum markdown rate per step: 1 minus the R19 floor. That is 20% for design, plan, plan red-team, security review, acceptance test and release; 40% for other steps; 50% for review [PROPOSED]. Adjusted from live variance | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-09a | **Owner of live operation** | Live operation is part of the Factory. The Ledger detects incidents; the owner restores by reverting the causing change; hotfixes are ordinary cards through the Market and Review. Until the Release Gate exists, incidents and restores are top-priority cards pulled by any agent and checked by another family; then the Release Gate owns them [PROPOSED]. This extends the Release Gate's charter, so it is a constitutional amendment | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-11 | **Protected governance paths** | The protected path categories: constitution, charters, Ledger rules, Scaler and burn-cap settings, and the pack. The puller of C0.02 confirms the exact paths in the code. Interim gate until the Release Gate exists: another family's pass plus Isa | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-12 | **Monitoring and improvement plan** | Measures M01–M20. A weekly report and alarms: when live results fall more than 25% outside the model, or any X1–X14 falsification criterion is met, a card is opened; work does not stop. Amendments pass the Release Gate and Isa | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-13 | **Ratified Plan** | The pack's card seeds (40 at signing; AR-15 adds C1.19), with every `[PROPOSED]` value accepted or changed. Later changes arrive as evidenced returns under R8 | Isa | **Signed by Isa, 27 Sep 2026** |
| AR-14 | **Backlog admission** | Load the Phase 0 cards into the pull queue, each carrying its pack card ID. This is a mechanical load: nobody chooses or assigns. Later phases load on phase-exit approval: through the interim gate for Phases 0–1, then through the Release Gate | Ledger load | To produce |

---

## Gate 3: Just in time

| # | Record | What is approved | Before | Owner | Status |
|---|---|---|---|---|---|
| AR-10 | **Vendor and data terms** | The self-hosted gateway (C0.19) as the one model interface. Vendor accounts held by the Owner. Direct routes for the two anchors. OpenRouter as the first aggregator route: the Owner's own keys, sticky sessions, data collection denied. Vercel AI Gateway as a trial route [Unverified terms]. No-training terms for every tier and route (R15); rate limits as Scaler caps; Muse Spark in the Owner's region [Unverified]; adviser review of vendor and aggregator terms for Heliosvera IP. Key custody: the Owner holds all keys (OI-17 resolved). Speech-to-text and voice vendors for C2.07, with where each processes audio | C1.03, C2.07 | Isa | To produce |
| AR-09b | **Ratification tiers and attention budget** | Which ideas need Isa's ratification and which the Council may ratify. No fixed weekly attention budget: Isa's time varies, so her turnaround is measured instead (Isa, 1 Oct 2026). AR-19 (signed) sets the mechanism (R28): an envelope ratified by rule, her random 10% sample, and a queue for the rest; the bounds and ceiling are hers | C1.22, C3.04 | Isa | Open: Isa decides |

---

## Gate 4: Amendments

| # | Record | What is approved | Before | Owner | Status |
|---|---|---|---|---|---|
| AR-15 | **Amendment: quality, cost and speed; readiness hand-back** | R14 amended: the Scaler prices a success as ($ + time value × elapsed hours, latency included) ÷ pass chance, weighing quality, cost and speed together; time value starts at $0.5 an hour and moves on live evidence. New R21: every institution hands back cards that are not fit for purpose before any build spend. Human steps are timed stages, measured like any institution. New experiments X15, X16; measures M21–M23 ([`trifecta.md`](trifecta.md)) | C1.14, C1.19 | Isa | **Signed by Isa, 28 Sep 2026** |
| AR-16 | **Amendment: institutions as harnesses; model flexibility; central memory** | Principle 9 (models are interchangeable) and principle 10 (memory is central; context is fresh). R22: each institution runs its own harness; harness edits are predicted, trialled and adopted on evidence. R23: model swap by configuration. R24: fresh, cache-first context from the Ledger. X17–X19; M24–M25. Editorial: the reviewing institution is named Review ([`harnesses.md`](harnesses.md)) | C0.18, C0.19, C2.05 | Isa | **Signed by Isa, 28 Sep 2026** |
| AR-17 | **Amendment: the North Star** | In Isa's words: "A self-governing agentic factory: cards flow through a graph of institutional harnesses, every move is a rule-checked transition in the Ledger, agents pull the work and earn their licences on evidence, and the whole system is tuned to deliver defect-free output at the sweet spot of quality, cost and speed." Metric: defect-free outputs delivered per week, within Isa's cost and lead-time bounds (for software, clean ideas). Direction: a domain-neutral core; software is the first domain pack | – | Isa | **Signed by Isa, 1 Oct 2026** |
| AR-18 | **Amendment: primitives and industrialising the repeated** | R25: repeated agent work is promoted to deterministic paths on evidence; exceptions return to agents; agents never write records directly. Target architecture: eight primitives in eight stores separated only where needed; Hatchet under the Ledger, Postgres per store, batched per-domain chains, OPA or Cedar, DuckDB over Iceberg ([`primitives.md`](primitives.md)). Load tiers: T1 agents and T2 systems of record on this design; T3 high-throughput deferred (OI-19), with five seams kept now. X20 | C2.05 | Isa | **Signed by Isa, 1 Oct 2026** |
| AR-19 | **Amendment: edge cases, self-origination and the ratification envelope** | R26: edge cases are evidence (failure scenarios, sealed tests, challenge tests by another family before the code is read, mutation score). R27: the Factory originates its own ideas through the existing institutions, with no ninth; Ledger signals become briefs, capped at 20% of the monthly ceiling, marked by realised value. R28: the ratification envelope, the mechanism for AR-09b. P12, X21–X23, M26–M28. In Isa's words: "We do not need a ninth stage but definitely require self originated ideas. I disagree further briefs would load as that is a good problem to solve." ([`origination.md`](origination.md)) | C1.20, C1.21, C1.22, C2.06, C3.05 | Isa | **Signed by Isa, 1 Oct 2026** |
| AR-20 | **Amendment: recorded behaviour, lessons, decision rights and outcomes** | R29: recorded live use is the regression oracle, replayed old against new at merge and before canary; option A, no lab set. R30: lessons from corrections, scoped, approved, expiring, owned by the Factory or a user. R31: decision rights; outward actions ask by default; spending, signing and regulated claims never without Isa or the owning user. R32: dissent credited by outcome. P13–P14, X24–X27 (including the Council against a single model), M29–M33. Voice front end in English and Arabic (C2.07). Direction: EvryMynd joins for user-owned sovereign memory and an agent council (OI-20) ([`replay-and-judgment.md`](replay-and-judgment.md)) | C1.23, C1.24, C1.25, C2.07, C3.06, C3.07 | Isa | **Signed by Isa, 5 Oct 2026** |

---

## After the backlog

- A phase-exit approval for each phase: through the interim gate for Phases 0–1, then through the Release Gate.
- Amendment cards opened by the weekly alarms or by a falsified experiment (C4.01). Each is human-ratified and becomes a new version.

---

## Isa's sittings

| Sitting | Records | What it takes |
|---|---|---|
| 1: decide | AR-01 to AR-07 | Read the Idea Record §5.5–§5.8, `pack/README.md` and this register |
| 2: commit | AR-08, AR-09a, AR-11, AR-12, AR-13 | Can follow Sitting 1 at once. The Phase 0 cards then load (AR-14) and the collective starts pulling |
| Just in time | AR-10, AR-09b | Each when its card is next. AR-09b now comes in Phase 1, before C1.22 |

---

## What is still open

The open items live in `pack/src/open_items.json`, each with its resolver. The ones that need Isa:
- **OI-04:** [Inference] a hash cannot authenticate an API call, so confirm where the usable credential is held.
- **OI-10:** ratification tiers and attention budget (AR-09b). AR-19 (signed) sets the mechanism; Isa sets the envelope's bounds and its ceiling. No fixed weekly budget (Isa, 1 Oct 2026).
- **OI-12:** the starting licence for new menu models. [PROPOSED] Artificial Analysis band as prior, corrected live; decided in AR-13.
- **Actual costs:** the Owner enters invoices, subscriptions and cloud credits into the value ledger (C0.09) as they are paid.
