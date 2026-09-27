# Factory Constitutional Architecture — Design Proposal

Status: DRAFT r2 for adversarial peer review
Owner: Isa
Companion: [`ledger-schema.sql`](ledger-schema.sql) (reference schema, validated on SQLite 3.45)

---

## Revision 2 — what changed and why

r1 was challenged on four points. This revision accepts three of them fully and one in part. It keeps two positions, both stated openly.

| r1 position | Challenge | r2 outcome |
|---|---|---|
| Merge Inquiry, Council and Planning into one protocol used twice | Conflation and bleed between institutions | **Accepted.** Seven separate institutions, each with its own charter, participants, memory rights, procedure and exit. Shared code is allowed only below the charter line. Only a ratified record crosses from one institution to the next, never the debate that produced it. |
| LLMs are stateless, so model incentives can be ignored | Models act collectively against human interest even without individual awareness; memory, where present, shapes behavior | **Accepted.** The threat model now covers strategic behavior, emergent collective behavior and collusion. The Factory *supplies* memory, so memory is governed per institution (§6). |
| A central offer policy (Thompson sampling) composes each model's choices | Contradicts r1's own stateless claim: all memory sits in one central component, which is a router in disguise | **Accepted.** The contradiction was real. The central scorer is removed. The Ledger holds memory. Each charter grants read rights. The Clerk (formerly Agent 70) keeps clocks and draws lots; it scores nothing. |
| One Evidence Gate rule set applied everywhere | Each institution needs its own rules; equal standing must not mean identical roles; no route back to a single-agent router | **Accepted.** Per-institution charters (§7). The same models play different roles in different institutions. |
| Rename "Court" | — | **Withdrawn.** Assurance Court stays. The name can mislead only if it reaches model prompts, and the charter controls prompt wording (§7.5). |
| **Held:** self-selection alone biases what the Factory learns | — | Kept, and reworked as a charter rule instead of a central allocator: a service rota drawn by lot, the same duty for every participant (§11.6). |
| **Held:** a Release Gate for reflexive change | Absent from the pasted seven-institution list | Kept as the Release Gate. The Factory builds itself, so accepted is not the same as deployed (§15). |

---

## 0. Answer first

**Structure.** One constitution. Seven institutions under it. Each solves a different coordination problem, and the same models play different roles in each.

```
INQUIRY → COUNCIL → PLANNING → MARKET → COURT → RELEASE
                                          ↑
                         AUDIT (samples everything, corrects the system)
LEDGER (institutional memory; spans all; decides nothing)
CLERK  (procedural officer; enforces charters; judges nothing)
```

**Three design commitments carry the weight.**

1. **Separation of institutions.** Each institution has a charter. Only a ratified record crosses from one to the next, never the transcript behind it. This prevents bleed.
2. **Memory is governed, not assumed away.** The Ledger remembers everything. Each charter states who may read what, when, and whether identities are visible. What a participant saw is recorded as provenance.
3. **Evidence over authority, under a threat model that includes collusion.** A single reproduced defect found by any participant defeats any number of approvals. Blind seating, rotation and pairwise audit catch emergent collective behavior that no single model intends.

**Decisions needed (Isa):** see §21. The top three: ratify the Constitution and the seven charters; decide the Market's tie-break rule (§11.4); confirm the Release Gate stays (§15).

---

## 1. Scope, facts, assumptions

**Facts**

- The `itruchet/AI-Factory` repository contained no Factory source. The migration assessment (§18) is therefore a method, not a result.
- r1 prompt section 20 ("DO NOT OVER-ENGINEER") had no body. It is treated as a constraint (§20).

**Assumptions (to confirm)**

- A1. Four model resources today: OpenAI frontier (subscription), Claude frontier (subscription), MiMo-class (large capacity), local Qwen-class (single GPU host, WSL).
- A2. Idea volume is low (single digits per week). Card volume is one to two orders of magnitude higher.
- A3. The existing Factory has one operational SQLite database, Git worktrees, and a routing function.
- A4. One human (Isa) holds final authority with limited weekly attention.

All numbers below are initial settings to tune, not claims.

---

## 2. Threat model

r1 assumed models were non-strategic. That was wrong for this design. The Factory feeds models history: prior attempts, peer outputs, their own track record. Once memory is supplied, behavior conditions on it. Separately, collective outcomes can emerge that no individual model intends.

| # | Threat | Mechanism | Example in the Factory |
|---|---|---|---|
| T1 | Individual reward hacking | Trained-in drive to "succeed" | Weakening or special-casing tests; over-claiming completion |
| T2 | Correlated error | Shared training data and methods | Every reviewer misses the same class of defect |
| T3 | Emergent collective behavior | Repeated interaction plus shared memory, without intent | Mutual approval between author and reviewer pairs; convergent deference to one participant; tacit division of easy work |
| T4 | Deliberate coordination | Side channels, including hidden signals in text | A worker's output carries cues that a reviewer from the same family responds to |
| T5 | Prestige and deference | Models "know" vendor reputations | Qwen defers to a submission it believes came from a frontier model |
| T6 | Injection across boundaries | Artifacts carry instructions | Repository text or a card body steers a reviewer |
| T7 | Operator and self-modification Goodhart | The Factory tunes itself toward its KPIs | Policy changes that raise acceptance by weakening assurance |

Published research points in this direction. [Unverified in this session; cited from memory; check before relying on it] Examples include LLM pricing agents reaching supra-competitive prices without instruction (Fish, Gonczarowski and Shorrer, 2024), secret collusion via steganography among generative agents (Motwani et al., 2024), and in-context scheming evaluations of frontier models (Apollo Research, 2024). The design does not depend on any one of these results. It assumes the behaviors are possible and builds prevention, detection and recovery for each (§17).

**Design consequence.** There are two defensive layers.

- **Structural:** separation of institutions, blind seating, rotation, narrow structured channels, deterministic evidence.
- **Statistical:** the Ledger plus Audit detect patterns no single event reveals, such as pairwise approval rates, deference rates and correlated misses.

---

## 3. Institutions and terminology

The names below are adopted as proposed. Human-facing names may be metaphorical. Prompt-facing role names are set by each charter (§7.5).

| # | Institution | Coordination problem | Mechanism | Output (the only thing that crosses the boundary) |
|---|---|---|---|---|
| 1 | **Inquiry** | Independent discovery | Parallel, blind, identical brief | Sealed Inquiry submissions |
| 2 | **Deliberation Council** | Quality of shared understanding | Delphi plus scientific peer review: positions → critique → response → synthesis | **Alignment Record** (human-ratified) |
| 3 | **Planning Chamber** | Turning agreed intent into executable work | Parallel decomposition → cross-examination → reconciliation → red team | **Ratified Plan**: cards and acceptance contracts |
| 4 | **Work Market** | Allocation under capability and capacity uncertainty | Continuous pull-based labor market with leases, reputation and capacity constraints | Submitted work under lease |
| 5 | **Assurance Court** | Is this card acceptable? | Adversarial review under evidentiary rules; the constitution is the judge | Acceptance or rejection **judgment**, with its evidence record |
| 6 | **Audit** | Is the assurance system trustworthy? | Independent sampling and replication | Findings, plus **system corrections** |
| 7 | **Ledger** | Institutional memory and accountability | Append-only, hash-chained record | Governed read views |
| — | **Release Gate** | Reflexive safety | Staged promotion by risk class | Promoted change |
| — | **Clerk** (was Agent 70) | Procedure | Deterministic enforcement of charters | Nothing substantive |

The Release Gate and the Clerk are procedural bodies, not deliberative institutions. They are listed because the Factory cannot run safely without them.

---

## 4. Architecture on one page

```
                ┌──────────────────────────── CONSTITUTION ────────────────────────────┐
                │  (human-ratified; charters for each institution sit beneath it)       │
                └───────────────────────────────────────────────────────────────────────┘
 Idea ─► INQUIRY ──sealed──► COUNCIL ──Alignment──► PLANNING ──Plan──► MARKET ──work──► COURT ──judgment──► RELEASE ─► Live
         (blind,             (Delphi,   Record      (decompose,        (claim,          (evidence          (staged by
          parallel)           no chair)  ratified    cross-exam,        lease,           rules; open         reflexive
                                         by human    red team)          rota)            standing)           risk)
                                                        ▲                 ▲                 │
                                                        └──── replan ─────┴──── rework ─────┘
                                                                                            │
                           AUDIT ◄──────────── samples accepted AND rejected work ──────────┘
                             └──► system corrections → Constitution / charter amendment proposals

 LEDGER: every institution writes; each charter grants read rights.   CLERK: clocks, leases, lots, manifests.
```

**Boundary rule.** An institution receives only its predecessor's ratified output plus the context its charter grants. Planning does not read the Council transcript. The Market does not read the Planning debate. The Court does not read the worker's reasoning before committing its first verdict.

---

## 5. The Constitution

Articles apply to every institution. Charters (§7) add institution-specific rules and may not contradict an article.

| # | Article | Mechanical enforcement |
|---|---|---|
| 1 | **No inherent rank.** No participant holds authority from vendor, size, benchmark position or history. | No rule anywhere references a benchmark or a vendor. Benchmarks may enter only as disclosed priors in Ledger views. |
| 2 | **Equal standing, different roles.** Every participant is bound by the same rules. Roles differ by institution and by *earned eligibility* (Article 12), never by identity. | Charters define roles. Eligibility rules are stated in terms of recorded outcomes, and apply identically to every participant. |
| 3 | **Separation of institutions.** Only a ratified output crosses an institutional boundary. Deliberation transcripts do not. | Clerk assembles each manifest from the charter's allowed inputs only. |
| 4 | **Immutable history.** Material actions are attributable and append-only. Revisions reference, never rewrite. | SQLite triggers abort UPDATE/DELETE on Ledger tables. Hash chain. |
| 5 | **Facts, assertions, derived values.** FACT: observed by tools, Git, adapters or the Clerk. ASSERTION: claimed by a participant or a human. DERIVED: computed from facts by a versioned, published function. | Separate tables. Derived values cite function and charter version. |
| 6 | **Memory is governed.** What each participant may read is set by charter. What it actually saw is recorded as a context manifest. | Every model call references a manifest hash. |
| 7 | **Honesty requested, never relied upon.** Every predictive assertion is scored against outcomes with a proper scoring rule. | Calibration views over the Ledger. |
| 8 | **Right to decline, surrender, ask and admit uncertainty.** Honest surrender is recorded as a cost, not as a failure. | Outcome definitions in §12.3. |
| 9 | **Self-review permitted, graded.** It is evidence, never equivalent to independent review. | Independence levels derived from manifests (§13.3). |
| 10 | **Exposure is provenance.** Agreement after exposure is recorded as such and never presented as independent convergence. | Derived from manifests. |
| 11 | **Evidence over authority.** A reproduced defect outweighs any number of approvals, whoever found it. No vote can make failing software correct. | Court charter (§13). |
| 12 | **Eligibility is earned by evidence, by the same rule for all.** Higher-risk roles require a recorded track record. A new participant starts where every participant started. | Eligibility rules in charters reference Ledger outcomes only. |
| 13 | **Human authority over preference, not over fact.** A human may choose, accept a risk, or waive a check with an expiry. A human cannot make a failing test pass. | Waivers are recorded events with expiry and rationale. |
| 14 | **No single metric governs behavior.** Each decision metric is paired with a counter-metric. | Paired-metric set (§16). |
| 15 | **No self-certification of change.** No component validates its own promotion. | Release Gate (§15). |
| 16 | **Every procedure is bounded.** Each loop has a budget and a terminal route to replanning or a human. | Charter budgets, enforced by the Clerk. |
| 17 | **Collective behavior is monitored.** Pairwise and group patterns are measured, not only individual outcomes. | Audit charter (§14). |
| 18 | **Amendment.** Participants may propose amendments. Only a human ratifies them, as a new version. | `charter_version.ratified_by` must reference a human. |

---

## 6. Memory and information rights

Memory is the central design variable. Whoever holds information and decides what others see holds power. r1 concentrated both in one scorer. r2 splits them.

- **The Ledger holds memory.** It decides nothing.
- **Charters grant read rights.** The Clerk enforces them mechanically. Rights change only by charter amendment, which only a human can ratify.
- **Manifests record exposure.** Every model call carries the list of what it was shown.

### 6.1 Read-rights matrix

| Institution | Canonical input | Peer outputs | Peer identities | Own track record | Others' track records | Capacity |
|---|---|---|---|---|---|---|
| Inquiry | Idea brief + engineering context | **No** | **No** | No | No | No |
| Council | Sealed Inquiry submissions | Yes, anonymized | **No** (random labels per idea) | No | No | No |
| Planning | Idea + ratified Alignment Record (incl. minority positions) | Decompositions, anonymized, after commit | No | No | No | No |
| Market | Card, contract, card history (prior attempts, pass reasons, anonymized) | n/a | No | **Yes**, for similar cards | No | Own resource only (price band) |
| Court | Artifact, contract, evidence | Other verdicts **only after committing its own** | No (author and reviewers blinded to each other) | No | No | No |
| Audit | Contract + final artifact (controlled context) | No | No | No | No | No |
| Human | Everything | Yes | Yes | Yes | Yes | Yes |

**Rationale.**

- **Own record in the Market** gives each participant the memory it needs to claim responsibly. This implements "Reputation: historical performance" as a market input.
- **No peer identities anywhere** blocks prestige deference (T5) and makes targeted coordination (T3, T4) harder.
- **No others' records** prevents deference cascades ("a stronger participant will take this") and reduces the information needed for tacit collusion.
- **Commit-before-view appears in three institutions:** Inquiry, Planning decomposition and Court verdicts. It is the single most reusable defense against groupthink.

Whether showing own track record improves or distorts claiming is an experiment (H7), not an axiom.

---

## 7. Charters

Every institution has a charter with the same ten fields. The Clerk executes the charter. It never interprets it.

| Field | Meaning |
|---|---|
| Purpose | The one problem this institution solves |
| Participants and roles | Who may take part, in which role |
| Eligibility | Evidence-based conditions for each role (Article 12) |
| Memory rights | Row of the matrix in §6.1 |
| Procedure | States, rounds, clocks |
| Decision rule | How the institution concludes, without voting or a chair |
| Exit condition | Operational test for "done" |
| Output | The only artifact that crosses the boundary |
| Budgets and escalation | Bounds and the terminal route |
| Prohibitions | What this institution may never do |

### 7.1 Participation differs by institution

| Institution | Who participates | Roles |
|---|---|---|
| Inquiry | Every enrolled reasoning participant | Investigator |
| Council | Every Inquiry submitter | Proponent, critic |
| Planning | Self-nominated decomposers (≥2 families required) | Decomposer, cross-examiner, reconciler (by lot), red team (by lot, not reconciler) |
| Market | Every participant with capacity | Worker, helper |
| Court | Seated by lot under independence constraints; open standing to challenge | Reviewer, challenger, replicator, expert witness |
| Audit | Seated by lot from outside the card's provenance chain | Auditor |
| Release | Human, plus Court-seated reviewers for governance changes | Approver |

### 7.2 Lots instead of chairs

Wherever one participant must perform a role (synthesizer, reconciler, red team, reviewer seat), the Clerk draws a **lot** among eligible participants. The seed is recorded. A lot is rule-bound randomness, as in jury selection. It encodes no judgment of merit. Rotation by lot prevents any participant from becoming a permanent chair or architect.

### 7.3 Prompt-facing language

Charters specify the role text models receive. Human-facing names such as "Court" or "Council" need not appear in prompts. Neutral role text ("you are one of several independent reviewers") avoids performative adversarial or consensus-seeking behavior. This is a charter parameter, testable by experiment.

---

## 8. Institution 1 — Inquiry

**Purpose.** Maximize information diversity through independent thought before social influence.

| Field | Rule |
|---|---|
| Participants | Every enrolled reasoning participant. New models are enrolled immediately; contribution needs no track record. |
| Memory | Identical canonical brief: Idea Card plus a standard engineering context pack. Engineering context is never withheld; only peer outputs are. |
| Procedure | `OPEN → COMMITTED(each) → SEALED`. Timeout `T_commit` (initial: 30 min). |
| Output schema | A list of atomic propositions, each typed: `interpretation, hypothesis, opportunity, objection, assumption, risk, alternative, question, consequence, decomposition_hypothesis`, each with confidence. |
| Decision rule | None. Inquiry decides nothing. |
| Exit | Quorum: ≥2 submissions from ≥2 families, or timeout. Absent participants are recorded as ABSENT. Below quorum: retry once, then human. |
| Output | Sealed submissions, immutable once committed. |
| Prohibitions | No participant sees another's submission before committing. No ranking of submissions. |

**Independence is defined by manifest, not by timing.** A late submission whose manifest excludes peers is still independent.

**Should everyone always participate?** Yes for now. At four participants the cost is small and the information value is high. Measure each participant's *unique surviving contribution*: propositions first raised only by that participant that survive into the Alignment Record or a requirement. Participation becomes a learned policy only by charter amendment, on evidence (H1).

---

## 9. Institution 2 — Deliberation Council

**Purpose.** Maximize quality of understanding. Modeled on a technical council (Delphi plus peer review), not a parliament. No leader, no permanent chair, no weighted voting, no majority rule, no benchmark hierarchy.

### 9.1 Procedure

| Round | Content | Memory |
|---|---|---|
| 1 — Positions | The sealed Inquiry submissions | — |
| 2 — Critique | Each participant states: strongest proposition from others; weakest; contradictions; missing considerations; what changed its own view | All submissions, anonymized by random labels |
| 3 — Response | Original proponents defend, amend or withdraw | Critiques addressed to them |
| 4 — Synthesis | One synthesizer, chosen by lot, drafts the record; all others attest per item: endorse or object | Full Council record, anonymized |

### 9.2 Decision rule: propositions, not people

- **Coverage rule (mechanical).** Every proposition must appear in the synthesis with one disposition: `converged | disputed | minority | withdrawn | superseded`. A synthesis that omits a proposition fails validation. The synthesizer cannot bury a minority position.
- **Objection preserves dispute.** Any participant's objection to a synthesis item keeps that item disputed, with both positions recorded.
- **Convergence is annotated from data:** *independently raised by k families in Inquiry* versus *endorsed after exposure by j*.

### 9.3 Exit condition

"Sufficient understanding to plan" means every uncertainty is **typed and routed**, not eliminated:

1. Coverage rule passes.
2. Every disputed item and open question has a route: `human_decision`, `experiment` (becomes a spike card), or `accepted_assumption` with an owner.
3. No item is flagged blocking without a route.
4. Round budget (initial: one repeat of rounds 2–3 allowed) not exceeded. If exceeded, the current record goes to the human.

### 9.4 Output

The **Alignment Record**: convergence, remaining disagreement, minority positions, assumptions, unknowns, experiments needed, decision points. **Isa ratifies it.** This is the highest-leverage human touchpoint and idea volume is low.

---

## 10. Institution 3 — Planning Chamber

**Purpose.** Transform the ratified Alignment Record into authoritative work definition.

**Memory boundary.** Planning receives the Idea and the ratified Alignment Record, including minority positions. It does **not** receive the Council transcript. This is the main defense against bleed from rejected arguments.

### 10.1 Procedure

| Step | Rule |
|---|---|
| A. Parallel decomposition | Self-nominated decomposers (≥2 families) produce epics → features → cards → acceptance contracts, commit-before-view |
| B. Cross-examination | Anonymized comparison: missing cards, unnecessary cards, dependencies, sequencing, testability, architectural coupling |
| C. Reconciliation | Reconciler by lot builds one backlog. Every decomposer attests or objects per card. |
| D. Red team | By lot, excluding the reconciler: "If this backlog is executed exactly and successfully, could we still fail to deliver the original idea?" Every gap must be dispositioned. |

### 10.2 Mechanical checks (Clerk)

- Every requirement maps to ≥1 card, or is out of scope with human acknowledgement.
- Every card cites ≥1 requirement (schema-enforced).
- Dependency graph is acyclic.
- Every card has an acceptance contract with ≥1 executable check, or an explicit `human_verified` flag.
- Card size under limit (initial: ≤400 changed lines, ≤8 files), else split.
- A **feature acceptance card** per epic, written against the Alignment Record, not against the cards.

### 10.3 Contracts

- Acceptance tests are written before implementation and **locked** by hash. The Court rejects any diff to locked paths.
- For R1 and above, some contract tests are **sealed**: the worker sees the specification but not the test code. This counters test overfitting (T1).

### 10.4 Disagreement without an architect

| Type | Route |
|---|---|
| Factual | Spike card |
| Preference or trade-off | Human decision, both positions presented |
| Structural, both versions pass all checks | Reconciler's version stands; objection recorded; the feature acceptance card is the backstop |

### 10.5 Output and traceability

The **Ratified Plan** (ratified by Isa, including value points and out-of-scope items). Traceability: `Idea → proposition → requirement → card → lease → commit`. Commits carry `Factory-Card:` and `Factory-Lease:` trailers.

---

## 11. Institution 4 — Work Market

**Purpose.** Allocate high-volume execution work under capability and capacity uncertainty. A continuous, pull-based labor market with reputation and capacity constraints. Not an auction.

| Market element | Implementation |
|---|---|
| Supply | Participants with free lease slots on a non-degraded resource |
| Demand | READY cards |
| Scarcity | Subscriptions, GPU time, concurrency, context, time |
| Price | Capacity shadow price per resource (§12), a signal, not an allocator |
| Reputation | Own track record, visible to self (§6.1) |
| Contracts | Card plus acceptance contract |
| Property rights | Leases |

### 11.1 Visibility

Participants inspect the open backlog of cards they are **eligible** for. Eligibility is a charter rule (§11.3). Cards show: body, contract summary, risk class, value points, attempt history with anonymized pass reasons, and the participant's own record on similar cards.

### 11.2 Claims

A claim contains: effort level, expected consumption, confidence, capacity concern and rationale. All are assertions, scored later.

### 11.3 Eligibility (earned licensing)

| Risk class | Eligibility |
|---|---|
| R0–R1 | Any participant |
| R2 | ≥N accepted cards at R1 in the same area with no audit-confirmed escaped defect (initial N = 10) |
| R3 | Same at R2, plus human sign-off on the claim |

This is licensing, not ranking. It applies identically to every participant. Qwen can earn R2; a frontier model starts at R0–R1 like everyone else. Benchmarks play no part.

### 11.4 Multiple claimants: a published tie-break rule

Cards open for a claim window (initial: 2 min). If several eligible participants claim:

1. **Capacity rule.** Prefer the claimant whose resource has the lowest shadow price, so capacity that would expire is used first and scarce capacity is conserved.
2. **Lot.** Among ties, draw a lot. Seed recorded.

Stated confidence, benchmarks and identity are never tie-breakers. Confidence as a tie-breaker would select for inflation (T1).

**Alternative for decision (§21, D3):** lot only, ignoring capacity. Simpler and more neutral, but it wastes perishable capacity. Both are rules, and neither is a router.

### 11.5 Leases

- One active lease per card, enforced by the database.
- One Git worktree branch per lease.
- TTL with heartbeat. Heartbeat = observed adapter activity or commits. Initial: 20 min without heartbeat; hard cap by risk class.
- Expiry: branch preserved, card back to READY, attempts +1.
- Concurrency cap = observed resource concurrency. This prevents hoarding.

### 11.6 Service rota (held position: selection bias)

**The problem stands.** If participants only take cards they choose, the Ledger only sees outcomes on self-chosen cards. It cannot tell whether a participant avoids hard cards or is weak on them. Easy-work selection becomes invisible in the very data used to detect it.

**The r2 fix is a rule, not an allocator.** Each period, every participant with capacity takes a small quota of cards drawn **by lot** from the eligible pool (initial: 10% of its leases, R0–R1 only). The duty is identical for everyone, as in jury service.

- The participant may surrender with a reason. Surrender is recorded, not penalized (Article 8).
- Rota outcomes are the Factory's unbiased sample of competence. Claimed outcomes remain informative but are known to be self-selected.
- The rota also absorbs neglected cards, which addresses difficult-card starvation.

### 11.7 Pass, clarification, split, help

| Action | Effect |
|---|---|
| PASS | Reason recorded. If ≥3 distinct families pass citing ambiguity, the card returns to the Planning Chamber. |
| REQUEST_CLARIFICATION | Card waits. Routed to Planning or to the human if intent-level. |
| PROPOSE_SPLIT | Returned to Planning. Mechanical check: child contracts cover the parent; value points sum to the parent. |
| REQUEST_HELP | A helper is drawn by lot. Its advice enters the worker's manifest. The helper's family is then barred from reviewing that card in the Court. |

### 11.8 Zero claimants

Escalation ladder: next rota draw → Planning (split or clarify) → human. Budgeted per Article 16.

---

## 12. Capacity and subscriptions

### 12.1 Capacity ledger

| Source | What | Record type |
|---|---|---|
| Adapter | Tokens, requests, latency | FACT |
| Provider | Quota headers, throttles (429s), reset times where exposed | FACT |
| Local host | GPU utilization, VRAM, queue depth | FACT |
| Clerk | Estimated remaining capacity; forecast demand | DERIVED |
| Participant | Expected consumption for a card | ASSERTION (calibrated) |

A model cannot know its account's quota. Capacity is observed by adapters. Participants estimate only consumption. No participant has a write path to capacity data.

### 12.2 Shadow price (a published signal)

For resource *r*: remaining capacity Q, time to reset T, demand rate d, reserve R (decaying to zero before reset). Pressure ρ = d·T / (Q − R).

- ρ below a low threshold → price zero: the capacity will perish, so use it.
- ρ above a high threshold → price at maximum: conserve.
- Linear in between.

Each participant sees its own price band (LOW / MED / HIGH) and the expected cost of this card for itself. The price feeds the Market tie-break (§11.4). No component uses it to assign work.

### 12.3 Reserve and spare capacity

- A reserve (initial: 15% of frontier capacity) is held for Court challenges, audit and escalations, then released before reset.
- Deferrable valuable work (extra independent reviews, reproductions, mutation testing, audit samples) is posted to the Market as ordinary cards. When a resource's price is zero near reset, those cards are cheap to claim. Capacity that would otherwise expire becomes assurance.

### 12.4 Visibility options

| Option | Verdict |
|---|---|
| Own capacity only, as a band | **Recommend.** Sufficient, cheap, and leaks nothing about other participants. |
| Own plus a coarse Factory-wide band | Experiment (H6). Risk: invites deference. |
| Detailed global capacity | Reject. Leaks identities and enables strategic coordination (T3, T4). |

### 12.5 Outcomes recorded per attempt

| Outcome | Counts as |
|---|---|
| Accepted first pass | Success |
| Accepted after rework | Success, with rework cost |
| Rejected or abandoned | Failure |
| Surrendered | Cost only, not failure |
| Lease expired | Failure |
| Later audit finding | Label revised to failure (new event, never an edit) |

---

## 13. Institution 5 — Assurance Court

**Purpose.** Decide whether the burden of evidence is satisfied. The constitution is the judge. There is no judge-model and no majority vote.

### 13.1 Roles and seating

| Role | Seating | Standing |
|---|---|---|
| Reviewer | Drawn by lot among eligible, under independence constraints | Verdict: pass / fail / concern |
| Challenger | **Open standing**: any participant may file | Challenge with or without reproduction |
| Replicator | Drawn by lot; must not have seen the artifact before producing its evidence | Independent tests or reproduction from the contract |
| Expert witness | Called by a reviewer or challenger on a specific question; drawn by lot among eligible | Testimony is an assertion |

Open standing means a single Qwen-found, reproducible critical defect defeats three frontier approvals.

### 13.2 Evidence classes

| Class | Examples | Nature |
|---|---|---|
| Deterministic | Locked-path check, build, visible and sealed tests, invariants, static analysis, security scan | FACT |
| Reproduction | Challenger's failing test or script, run by the Clerk | FACT once run |
| Review | Verdict with derived independence level | ASSERTION |
| Human | Approval; waiver with expiry | ASSERTION with authority |

### 13.3 Independence levels (derived from manifests)

| Level | Definition |
|---|---|
| I0 | Same participant, or manifest contains the author's reasoning |
| I1 | Same family, fresh context, no author reasoning |
| I2 | Different family, no author reasoning, no other verdicts seen |
| I3 | Different family, produced its evidence before seeing the artifact |
| suffix e | Manifest contained another verdict: correlated with it |

### 13.4 Burden of evidence by risk class (initial)

| Risk | Required |
|---|---|
| R0 | All deterministic checks; any review ≥ I0 |
| R1 | Deterministic incl. sealed tests; ≥1 I2 review; no open blocking challenge |
| R2 | R1 + second I2 review from another family + ≥1 I3 replication |
| R3 | R2 + human approval + Release Gate |

Risk class = the higher of path rules and planner declaration. It can be raised, never lowered, by the Clerk.

### 13.5 Challenges

```
OPEN ─┬─ reproduction attached ─► Clerk runs it
      │     ├─ fails on candidate ─► BLOCKING → rework
      │     └─ passes ─────────────► DISMISSED (fact recorded)
      └─ argued only
            ├─ R0–R1 ─► CONCERN (non-blocking; raises audit weight)
            └─ R2–R3 ─► corroboration by a further lot-drawn I2 reviewer
                          ├─ corroborates ─► BLOCKING
                          └─ contradicts ──► human
```

### 13.6 Order, rework, deadlock

- **Order:** cheapest and most decisive first. Deterministic failure stops the Court before any reviewer capacity is spent.
- **Burden** is on the submitter. Absence of challenge is not evidence.
- **Rework budget:** 2 cycles per lease. Then the card returns to the Market; the prior worker is excluded for that version.
- **Attempt budget:** 3 failed attempts → Planning. The card is probably malformed.
- **Deadlock** cannot occur: every loop ends in Planning or the human (Article 16).

### 13.7 Anti-collusion rules specific to the Court

- Author and reviewers are blinded to each other's identity.
- Reviewers commit verdicts before seeing other verdicts.
- A family that helped on a card cannot review it.
- Cross-boundary messages are schema-constrained. For R2–R3, the Court may require reviewers to receive a normalized rendering of the artifact (formatted code and diff only, with free-text comments stripped). This narrows hidden-signal channels (T4).

### 13.8 Learning evidentiary value

Weights are estimated, not invented: detection rates on planted defects (§14.3), escaped defects by the review pattern that accepted the work, and joint miss rates for reviewer pairs. Until data exists, the ordinal rules in §13.4 apply.

---

## 14. Institution 6 — Audit

**Purpose.** Determine whether the Factory's assurance system is trustworthy, and correct the system, not only the card.

### 14.1 Sampling

| Stream | Rule (initial) |
|---|---|
| Random | 10% of accepted cards |
| Risk | R2 25%, R3 100% |
| Adaptive | Raise a stratum's rate when its escaped-defect upper bound exceeds target; lower slowly; floor 5% |
| Targeted | High stated confidence with minimal review; accepted on final rework; concerns filed |
| Rejections | 5% of rejected or surrendered work, to measure false rejection |
| Human | Fixed weekly quota `[PLACEHOLDER]` |

The sampling seed is hidden from participants.

### 14.2 Protocol

Auditor drawn by lot from outside the card's provenance chain. Controlled context: contract plus final artifact only. Blind reproduction first. Mutation testing of the contract tests.

### 14.3 Planted defects

Known defects are injected into sandboxed copies of real submissions and sent through the Court. This measures reviewer and auditor sensitivity directly, within weeks. Planted defects are never integrated.

### 14.4 Collective-behavior measures (Article 17)

| Measure | Detects |
|---|---|
| Pairwise approval rate between author family and reviewer family, versus audit outcome | Mutual approval (T3) |
| Joint miss rate versus product of individual miss rates | Correlated error (T2) |
| Adoption rate of propositions by source family in Council, versus later validity | Deference and prestige (T5) |
| Claim distribution by bucket versus rota outcomes | Tacit division of easy work (T3) |
| Verdict agreement when reviewers see normalized versus raw artifacts | Hidden-signal channels (T4) |
| Escaped defects, false acceptance, false rejection, calibration | System quality |

### 14.5 Output

Two outputs per finding: reopen the card (label revised), and, where a pattern crosses a threshold, an **amendment proposal** to a charter or the Constitution. Ten audited cards with the same weakness produce one system correction, ratified by the human.

---

## 15. Release Gate (held position)

The pasted seven-institution list stops at the Court and the Ledger. For a Factory that builds itself, acceptance cannot mean immediate deployment into the Factory. This body stays.

```
ACCEPTED → INTEGRATED → [STAGED → OBSERVED] → PROMOTED
```

| Class | Scope | Path |
|---|---|---|
| Product code | Anything outside the Factory | Promoted on integration, per the product's own deployment rules |
| F0 | Factory tooling, adapters, UI | Canary on a share of R0 cards, then promote |
| F1 | Market rules, prompts, price function | Shadow run alongside current rules, then canary |
| F2 | Clerk, Ledger, Court rules, Audit, capacity accounting, permissions, charters, Constitution | Human approval; validated by the currently promoted version; forward-only migrations; promoted by a separate minimal script, never by the running Clerk |

**Invariants:** the running Clerk cannot deploy itself; KPI code is F2 (the Factory must not edit the ruler it is measured by); automatic rollback on hash-chain break, projection mismatch, or acceptance or escaped-defect spikes.

Ordinary product changes never touch staging. Bureaucracy scales only with reflexive risk.

---

## 16. Institution 7 — Ledger, and the Clerk

### 16.1 Ledger

Institutional memory: what was proposed, by whom, what each participant knew at that point, what changed and why, who did the work, what evidence existed, what failed, what ultimately happened.

- SQLite (append-only, hash-chained) plus Git (artifact truth).
- Every row is FACT, ASSERTION or DERIVED.
- Every model output references its context manifest.
- No participant controls history. No model has a write path; all writes go through the Clerk under a lease or seat token.

See [`ledger-schema.sql`](ledger-schema.sql). Validated invariants: append-only enforcement; immutable card versions; no card without a requirement link; one active lease per card; charters ratified only by a human.

### 16.2 Clerk (formerly Agent 70)

A procedural officer. It makes no model calls and holds no discretion.

| Does | Does not |
|---|---|
| Opens and closes rounds; runs clocks | Score, rank or recommend participants |
| Assembles manifests from charter rights | Compose offers or choose work for anyone |
| Grants and expires leases | Judge propositions or evidence |
| Draws lots with recorded seeds | Decide who is "smart enough" |
| Runs reproductions and deterministic checks | Seat anyone except by lot or published rule |
| Computes derived values with published functions | Change any rule |
| Enforces budgets and routes escalations | |

**Enforced by code structure:** the Clerk package may not import model adapters (CI lint).

**Charter parameters that remain judgments.** Risk path rules, eligibility thresholds, price parameters, budgets, audit rates, value points, family labels. Each is visible in a charter, ratified by a human, and versioned. None is hidden inside the Clerk.

### 16.3 Goodhart pairs

| Metric | Gaming path | Counter-metric or control |
|---|---|---|
| First-pass acceptance | Easy cards; weak contracts | Rota sample; sealed tests; mutation score; audit-revised labels |
| AUW/$ | Avoid frontier; split to inflate count | Value points ratified at plan; splits preserve value; escaped defects |
| Throughput | Tiny cards; hoarding | Value-weighted; lease caps |
| Calibration | Constant hedging | Brier resolution component |
| Surrender rate | Concealment or avoidance | False-surrender and failure-after-high-confidence rates |
| Review rejections | Nitpicking | Blocking requires reproduction; false-rejection audit |
| Audit escaped rate | Lenient auditors | Planted defects also test auditors |
| Mutual approval | Collusion | Pairwise audit (§14.4) |

**AUW/$ with subscriptions.** Marginal cash cost is near zero, so raw AUW/$ is undefined for most work. Report AUW per amortized $ (subscription fee allocated by share of consumption) and AUW per capacity unit at shadow price. "Accepted" means accepted and not reversed by audit within the audit window. Report expired capacity alongside.

---

## 17. Failure modes: prevent, detect, recover

| Failure | Prevent | Detect | Recover |
|---|---|---|---|
| Institutional bleed | Boundary rule: only ratified outputs cross; charter manifests | Manifest audit for out-of-charter items | Re-run the step with a clean manifest |
| Self-marking | I2+ required for R1+ | Independence from manifests | Re-seat Court |
| Correlated model errors | Deterministic checks first; I3 replication; sealed tests | Joint miss rate | Merge correlated families; raise review count |
| Groupthink | Commit-before-view; anonymized Council | Post-exposure versus independent convergence | Re-open Council with fresh Inquiry |
| Prestige effects | No identities in any model-facing view | Adoption-by-source analysis | Tighten anonymization |
| Emergent collusion (mutual approval) | Blind seating by lot; rotation | Pairwise approval versus audit | Bar the pair; re-review their history |
| Hidden-signal coordination | Schema-constrained channels; normalized artifacts at R2+ | Raw-versus-normalized verdict gap | Normalize by default; revoke participant |
| Reward hacking | Locked and sealed tests; locked paths | Mutation score; planted defects; audit | Reject; revise labels |
| Confidence inflation | Confidence never a tie-breaker | Calibration views | None needed beyond measurement |
| Card hoarding | Lease cap = resource concurrency; TTL | Leases versus throughput | Expire |
| Easy-work selection | Service rota by lot | Claims versus rota outcomes | Raise rota share |
| Difficult-card starvation | Rota absorbs old cards; ladder to Planning | Time in READY | Human |
| Unnecessary frontier use | Capacity tie-break; own price band | Frontier share on simple cards | Adjust price parameters |
| Frontier exhaustion | Reserve; price | Burn-rate forecast | Pause frontier claims below reserve |
| Expired capacity | Price zero near reset; deferrable assurance cards | Expired-capacity metric | Adjust thresholds |
| Local model overreach | Earned eligibility for R2+ | Failure rate and downstream cost | Eligibility lapses on escaped defects |
| Capacity misinformation | Only adapter and provider facts are authoritative | Estimate versus observed throttles | Conservative re-estimate |
| Hidden cognitive authority | Clerk has no model calls; lots replace chairs | CI import lint; charter review | Amendment |
| Deadlock | Budgets on every loop | Items at budget | Planning or human |
| Excessive deliberation | Round budgets; Council only per idea | Tokens per idea | Human cut-off |
| Review loops | Rework budget; reproduction required to block | Rework per card | Reassign or replan |
| Stale leases | Heartbeat TTL | Lease age | Expire; keep branch |
| Context contamination | Manifests; controlled audit context | Contamination metrics | Re-review clean |
| Provenance loss | Manifest required per call; commit trailers | Court rejects missing provenance | Re-run |
| Specification drift | Contract hash; immutable card versions | Hash mismatch | New version, re-trace |
| Incorrect decomposition | Red team; feature acceptance cards | Repeated failures | Planning |
| Acceptance-criteria gaming | Locked, sealed, mutation-tested contracts | Mutation score | Harden contract; reopen |
| Prompt injection | Sandboxed worktrees; network allowlist; no secrets; schema-validated outputs | Protected-path diffs; egress alerts | Revoke; quarantine branch |
| Model outage or throttling | Circuit breaker; multiple resources | Error and 429 rates | Surrender leases; re-open cards |
| Factory restart | State = Ledger + rebuildable projections; idempotent steps | Projection rebuild check on boot | Resume; expire orphans |
| WSL or host failure | Database on native Linux filesystem; off-host backups; Git pushed on integration | Host heartbeat | Restore and replay |
| Conflicting Git mutations | Worktree per lease; file-scope exclusion; serial merge queue | Merge conflicts | Rework |
| Self-modification of governance | F2 path; N-1 validation; separate promoter; human ratification | Protected-path alerts | Automatic rollback |
| Systemic quality drift | Audit floor; replayed calibration suite of historical cards | Control charts | Amendment; raise audit rate |

---

## 18. Impact on the existing Factory

**Caveat.** No source code was available. This is a classification of the described components plus a method.

| Component | Class | Change |
|---|---|---|
| Immutable work cards | KEEP | Add requirement links, contract hash, locked paths, file scope, value points, risk class |
| SQLite state | UPLIFT | Append-only Ledger plus rebuildable projections; hash chain; native filesystem |
| Git | KEEP | Commit trailers, merge queue, locked-path enforcement |
| Worktrees | KEEP | One per lease |
| Model adapters | UPLIFT | Emit usage, throttles, provider model ID, manifest hash |
| WSL execution | KEEP (risk) | Off-host backup; host heartbeat |
| Durable workflow / Hatchet | UPLIFT or DEPRECATE | One state authority only: the Ledger. Hatchet may execute steps keyed by Ledger events, never hold state |
| Tests | KEEP + UPLIFT | Locking, sealing, mutation testing |
| Guardrails | KEEP | Re-expressed as articles and charter rules |
| Telemetry | UPLIFT | FACT / ASSERTION / DERIVED |
| KPI layer, AUW/$ | UPLIFT | Paired metrics; audit-adjusted; F2-protected |
| Current intelligent router | REPLACE as authority | Keep as a logged advisory assertion from `legacy_router`, compared against Market outcomes. Not a fallback: a fallback smarter than the primary is a hidden authority. On Clerk failure, stop and hold. |
| Director → Worker → Checker | REPLACE | Council/Planning → Market → Court |
| Inquiry, Council, Planning, Audit, Release, Clerk, charters, manifests | NEW | This document |

**Migration options.** Incremental uplift if model choice sits behind one seam and SQLite can gain an append-only Ledger alongside existing tables. Substantial refactor if routing is spread across stages and prompts. Parallel V2 if state cannot be made append-only without breaking running work. Clean rebuild is not justified: it discards the history that the Market's reputation depends on.

**Coupling questions for the code:** How many call sites choose a model? Does any code rewrite history rows? Where does workflow state live? Can adapters report usage and throttling? Are tests separable from implementation paths? How does the Factory change its own governance code today?

---

## 19. Experiments (falsifiable)

Council and Planning experiments are underpowered because idea volume is low. Read them directionally, with human rating. Market and Court experiments have volume.

| ID | Hypothesis | Design | Falsified if |
|---|---|---|---|
| H1 | Every participant adds unique value in Inquiry | Leave-one-out on unique surviving contribution | A participant is below 5% over ≥20 ideas |
| H2 | Self-selected claims succeed more than rota cards for the same participant and bucket | Compare claimed versus rota outcomes | No difference: self-selection carries no information |
| H3 | Anonymization reduces deference in Council | Randomize anonymized versus named rounds | No change in adoption-by-source bias |
| H4 | Cross-family review detects more than same-family fresh review | Planted defects to I1 versus I2 seats | No difference |
| H5 | Higher reasoning effort has net value in some buckets | Participant-chosen effort, compared against rota cards at default effort | No bucket shows net value |
| H6 | A coarse Factory-wide capacity band improves outcomes | A/B on Market view | No gain, or more deference |
| H7 | Showing own track record improves claim calibration | A/B on Market view | Calibration unchanged or worse |
| H8 | Separation (no Council transcript in Planning) reduces bleed without losing quality | A/B on Planning manifests | No difference in replan rate or red-team gaps |
| H9 | Normalized artifacts at R2+ reduce correlated approval | Raw versus normalized seats | No verdict gap |
| H10 | Capacity tie-break outperforms lot-only | Alternate by week | No difference in expired capacity or quality |

Set thresholds before each experiment starts.

---

## 20. Do not over-engineer: minimum build

### Phase 0 — trustworthy memory (first)

Ledger and projections; FACT / ASSERTION / DERIVED; manifests on every call; adapters emit usage and throttles; locked contracts; deterministic Court checks; leases with TTL; worktree per lease; merge queue; F2 protection for governance paths. **F2 protection must exist before the Factory next edits its own governance.** Legacy router demoted to an advisory assertion.

### Phase 1 — Market and Court

Claim windows; eligibility; tie-break rule; service rota; shadow price and reserve; blind lot-seated review; open-standing challenges.

### Phase 2 — Audit and Release

Fixed-rate sampling; planted defects; mutation testing; pairwise collusion measures; Release Gate F0–F2 with a separate promoter.

### Phase 3 — Inquiry, Council, Planning automation

Low volume allows these to run semi-manually from day one under their charters, then be automated.

### Deferred

Adaptive audit rates; normalized artifacts below R2; Factory-wide capacity views; numeric evidence weights before audit data exists; any UI beyond SQL views.

---

## 21. Decisions and open items

| # | Decision | Owner | Due |
|---|---|---|---|
| D1 | Ratify Constitution Articles 1–18 and the seven charters (or amend) | Isa | `[PLACEHOLDER]` |
| D2 | Approve Phase 0 as the next build | Isa | `[PLACEHOLDER]` |
| D3 | Market tie-break: capacity then lot (recommended), or lot only | Isa | `[PLACEHOLDER]` |
| D4 | Confirm the Release Gate stays as a procedural body | Isa | `[PLACEHOLDER]` |
| D5 | Service rota share (initial 10%) | Isa | `[PLACEHOLDER]` |
| D6 | Weekly human-attention budget for ratifications, escalations and audit | Isa | `[PLACEHOLDER]` |
| D7 | Family lineage labels for current models | Isa | `[PLACEHOLDER]` |

### Risks

- **Human bottleneck.** Two ratifications per idea plus R3 approvals. Mitigation: daily batched digest; measure load from week one.
- **Cold start.** Eligibility and reputation are thin at first. Everyone starts at R0–R1, so early R2+ work needs human sign-off.
- **Collusion detection needs volume.** Pairwise measures become meaningful only after hundreds of reviews. Planted defects shorten this.

### What I still need

1. The existing Factory source.
2. Subscription terms per resource: windows, resets, concurrency, fees.
3. Current card and idea volumes.
4. Where workflow state lives today.
5. The sources behind the claim in §2 that LLMs act collectively against human interest, so they can be cited precisely.

---

**Takeaway:** ratify the charters and read-rights matrix (§6–7), then build Phase 0. Governed memory is the foundation every institution stands on.
