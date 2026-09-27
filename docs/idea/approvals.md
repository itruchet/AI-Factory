# Approval register: Idea-to-Live Factory, from decision to card backlog

Owner: Isa. Scenario: **Amend** the existing Factory. Source: Idea Record r12.3 ([`constitutional-factory.md`](constitutional-factory.md)) and its r10–r12.3 analyses.

**The change needs 14 approval records in three gates before its first card enters the backlog.**
- **Isa signs 13 of them.**
- **Six are first drafted by Planning in the existing Factory,** because the institutions do not exist yet.
- **The last (AR-14, creating the cards) is done by the Factory** under the ratified plan.

The change is built by today's Factory under Isa's ratification (principle 8: no change approves itself).

Status key: **Ready** = the evidence exists and the record can be signed now. **To produce** = a design output must be written first.

---

## Gate 1: Decide the idea (exit Idea stage)

One sitting. All evidence exists.

| # | Record | What is approved | Evidence | Owner | Status |
|---|---|---|---|---|---|
| AR-01 (H1) | **Constitution** | The eight principles (§6); the five golden allocation rules (§3.2); rules R1–R20. R1–R13 cover pull, licences and governance; R14–R20 cover the Scaler, no training on our data, the burn cap, evidence-gated dependencies, family independence, high-impact floors, and trial-only configurations | Idea Record §2–§5.8; `value-stream.md`, `dependencies.md`, `crosscheck.md`, `institutions-vs-searched.md` | Isa | Ready |
| AR-02 (H4, revised) | **Model portfolio** | The rolling policy (P1, P2, P6–P8) and the starting **menu of seven models on API tokens**:<br>• anchors: Opus 5.5, GPT-5.6 Terra;<br>• fast top tier: Muse Spark 1.3, Gemini 3.8 Flash;<br>• mid: DeepSeek V4.1 Flash, GPT-6 Luna, Ling 3.0 Flash.<br>This replaces "start from today's four models" | `best-six.md`; `value-stream.md` §4.3; `robust6_results.txt` | Isa | Ready |
| AR-03 (H5) | **Work tiers** | Three absolute tiers for cards | Idea Record §5.2; `tiering_results.txt` | Isa | Ready |
| AR-04 (H6) | **Trial operating rules** | The Scaler with:<br>• held demand counted;<br>• 15-minute target;<br>• 1-hour cost wait;<br>• quality floor 0.8;<br>• cost band 1.5.<br>Also R15 (no data-training tiers; Muse Spark's Contributor tier excluded), R16 burn cap, R17–R19, and R20 for any searched configuration | Idea Record §5.5–§5.8 | Isa | Ready |
| AR-05 (H7, new) | **Trial budget** | Monthly ceiling **about $2,500** for about 25 ideas a week, with the hourly burn cap at 2× the trailing average. The expected spend is about $1,700 a month; the range is $1,000–8,500 depending on real token use. Optional: value per clean idea [PLACEHOLDER], used only to decide how far to scale | `value-stream.md` §5 | Isa | Ready |
| AR-06 (H3) | **Exit Idea stage** | Move to design under the Amend scenario | Idea Record §12 | Isa | Ready once AR-01 to AR-05 are signed |

---

## Gate 2: Design records (the change, made fit to build)

Produced by the existing Factory's planning (Director), since the institutions do not exist yet. Ratified by Isa where marked.

| # | Record | What it must contain | Owner | Status |
|---|---|---|---|---|
| AR-07 | **Alignment Record** for the Idea-to-Live Factory | Intent; what is in and out of the trial; assumptions carried (the token model, synthetic parameters); minority positions; open experiments X1–X14. This is the constitution's first human touchpoint | Drafted by Planning; **ratified by Isa** | To produce |
| AR-08 (H2) | **Quality standards and constants** | Maximum markdown rate per institution and tier; initial window, hysteresis, stretch trials and back-off. Set from real variance in shadow running | Planning proposes; **Isa approves** | To produce |
| AR-09 | **Design answers** (Idea Record §11.2) | Mapping of R1–R20 onto the existing Factory's cards, SQLite state, worktrees and workflow engine; R8 reason codes; Ledger views at pull time; SQL as operational state with Git as artifact authority; tests, CI and typed contracts as first-class evidence; interfaces named in plans. **Two are Isa's:** (a) who owns live operation (incident, restore, hotfix); (b) which ideas need human ratification, and her weekly attention budget | Planning; **Isa for (a) and (b)** | To produce |
| AR-10 | **Vendor and data terms** | API accounts with six vendors (Anthropic, OpenAI, Meta, Google, DeepSeek, InclusionAI); no-training terms confirmed for every tier used (R15); rate limits recorded as Scaler caps; key custody; Muse Spark availability for UK and KSA accounts [Unverified]; review of the terms for Heliosvera IP [a qualified adviser where terms are unclear] | **Isa** | To produce |
| AR-11 | **Protected governance paths** | Before the Factory edits its own rules, the paths holding the constitution, charters and Ledger rules are protected: changes pass the Release Gate and Isa, and nothing approves itself. This is Phase 0 in the parked design notes | Planning; **Isa approves** | To produce |
| AR-12 | **Trial plan** | Scope (about 25 ideas a week, which idea types); duration [PLACEHOLDER: at least 4 weeks after a shadow week]; measures (clean ideas, change-failure rate, cost per clean idea, lead time, token use per card, coupling, escaped defects every model family missed); success and kill criteria from X1–X14; rollback to Director → Worker → Checker | Planning; **Isa approves** | To produce |

---

## Gate 3: Onto the card backlog

| # | Record | What it must contain | Owner | Status |
|---|---|---|---|---|
| AR-13 | **Ratified Plan** | Cards with acceptance contracts and a dependency graph (R17 applies to this build too), in phases:<br>• Phase 0: Ledger, token metering, protected governance paths, model adapters reporting usage and throttles;<br>• Phase 1: licences, pull, Court, the Scaler, API routing for the seven models;<br>• Phase 2: Audit and Release Gate;<br>• Phase 3: Inquiry, Council and Planning automation;<br>• plus live operation.<br>Each phase has entry and exit criteria | Planning; **ratified by Isa** | To produce |
| AR-14 | **Backlog admission** | The ratified cards are created in the existing Factory's backlog, tagged by phase. **Only Phase 0 cards are admitted first;** each later phase is admitted when the previous one passes the Release Gate | Existing Factory (Director), under AR-13 | To produce |

---

## After the backlog (for completeness; not needed to get there)

- A Release Gate promotion for each phase (principle 8).
- The trial go / no-go at the end of the trial plan (AR-12 criteria).
- Constitutional amendments as the trial teaches: human-ratified, as a new version.

---

## Isa's sittings

| Sitting | Records | What it takes |
|---|---|---|
| 1: decide | AR-01 to AR-06 | Read the Idea Record §5.5–§5.8 and this register; about 60–90 minutes |
| 2: frame | AR-07, AR-10, AR-11 | After Planning drafts them |
| 3: commit | AR-08, AR-09 (a, b), AR-12, AR-13 | After Planning drafts them; the cards follow automatically (AR-14) |

---

## What I still need

1. **The existing Factory's backlog:** where it lives and how cards are created there. This repository holds the Idea Record and the probes, not the Factory's code or its SQLite backlog.
2. **Current card and idea volumes,** to size the trial scope in AR-12.
3. **Trial duration and start date** [PLACEHOLDER].
4. **Value per clean idea** (optional) [PLACEHOLDER].
5. **Who holds the vendor accounts and API keys** (AR-10).
