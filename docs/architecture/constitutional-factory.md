# Factory Constitutional Architecture — Design Proposal

Status: DRAFT r3 for adversarial peer review
Owner: Isa
Companions: [`ledger-schema.sql`](ledger-schema.sql) (reference schema, validated on SQLite 3.45) · [`../../kernel/allocation.py`](../../kernel/allocation.py) (allocation kernel, 15 passing tests) · [`../../kernel/demo.py`](../../kernel/demo.py) (worked example, synthetic data)

---

## Revision 3 — what changed and why

| r2 position | Challenge | r3 outcome |
|---|---|---|
| Agent 70 becomes a "Clerk" | A Clerk is still an agent in all but name. Control must be logic inside the Ledger and backlog, based on sound mathematical inference. | **Accepted.** No actor sits in the control path. The **Ledger kernel** is database constraints plus pure mathematical functions over Ledger rows. Every output is reproducible from (rows, charter, seed), so anyone can verify it by replay (§16.2). |
| One bias fix for all: a service rota drawn by lot | The optimal selection-bias strategy differs by institution | **Accepted.** Each institution faces a different bias and gets its own strategy, chosen from standard statistical methods (§7.4). The Market rota is replaced by Thompson sampling, which explores exactly as much as uncertainty justifies. |
| Release Gate as a procedural body | It is an eighth institution, needing its own rules against groupthink among experts | **Accepted.** Institution 8 with its own charter: pre-registered criteria, independent commit-before-view, dissent by draw, decision by sequential test on canary data (§15). |
| Capacity as a signal only | Intelligence must be matched to the task. No point spending frontier reasoning on simple work. This must be mathematically modelled, monitored and trialled per institution. | **Accepted, with one qualification.** New §12: minimum sufficient intelligence per task class, computed from Ledger posteriors, capacity shadow prices (Lagrange duals) and time cost. Implemented and tested in `kernel/`. Qualification: subscription capacity that would expire unused costs nothing, so using it is not waste. Time cost is what keeps over-qualified models off simple work when capacity is spare. |
| Market clears by claims and tie-breaks | Superseded by the kernel | Assignment by seeded Thompson sampling at shadow prices, with recorded propensity. Models keep the right to decline, surrender, ask and split (§11). |

## Revision 2 — what changed and why

r1 was challenged on four points. This revision accepts three of them fully and one in part. It keeps two positions, both stated openly.

| r1 position | Challenge | r2 outcome |
|---|---|---|
| Merge Inquiry, Council and Planning into one protocol used twice | Conflation and bleed between institutions | **Accepted.** Seven separate institutions, each with its own charter, participants, memory rights, procedure and exit. Shared code is allowed only below the charter line. Only a ratified record crosses from one institution to the next, never the debate that produced it. |
| LLMs are stateless, so model incentives can be ignored | Models act collectively against human interest even without individual awareness; memory, where present, shapes behavior | **Accepted.** The threat model now covers strategic behavior, emergent collective behavior and collusion. The Factory *supplies* memory, so memory is governed per institution (§6). |
| A central offer policy (Thompson sampling) composes each model's choices | Contradicts r1's own stateless claim: all memory sits in one central component, which is a router in disguise | **Accepted.** The contradiction was real. The central scorer is removed. The Ledger holds memory. Each charter grants read rights. The Clerk (formerly Agent 70) keeps clocks and draws lots; it scores nothing. |
| One Evidence Gate rule set applied everywhere | Each institution needs its own rules; equal standing must not mean identical roles; no route back to a single-agent router | **Accepted.** Per-institution charters (§7). The same models play different roles in different institutions. |
| Rename "Court" | — | **Withdrawn.** Assurance Court stays. The name can mislead only if it reaches model prompts, and the charter controls prompt wording (§7.3). |
| **Held:** self-selection alone biases what the Factory learns | — | Kept, and reworked as a charter rule instead of a central allocator: a service rota drawn by lot, the same duty for every participant (§11.6). |
| **Held:** a Release Gate for reflexive change | Absent from the pasted seven-institution list | Kept as the Release Gate. The Factory builds itself, so accepted is not the same as deployed (§15). |

---

## 0. Answer first

**Structure.** One constitution. Eight institutions. Underneath them, a Ledger whose own logic (the kernel) is mathematics, not an agent.

```
INQUIRY → COUNCIL → PLANNING → MARKET → COURT → RELEASE GATE
                                          ↑
                         AUDIT (samples everything, corrects the system)
LEDGER  (memory + kernel: constraints and pure functions; decides by computation, never by judgment)
```

**Four design commitments carry the weight.**

1. **Separation of institutions.** Each institution has a charter. Only a ratified record crosses from one to the next, never the transcript behind it. This prevents bleed.
2. **Memory is governed.** The Ledger remembers everything. Each charter states who may read what, and whether identities are visible. What a participant saw is recorded as provenance.
3. **Evidence over authority, under a threat model that includes collusion.** A single reproduced defect found by any participant defeats any number of approvals.
4. **Minimum sufficient intelligence, computed.** For each task class in each institution, the kernel assigns the configuration (model × reasoning effort) with the best expected net value among those whose Ledger record clears that institution's quality floor. Net value prices in failure cost, capacity scarcity and time. Plain code is a configuration too, and wins wherever it is sufficient.

**Decisions needed (Isa):** see §21. The top three: ratify the Constitution and the eight charters; set the economics for each task class (value, failure cost, quality floor, time cost; §12.4); approve Phases 0–1 (§20).

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
| 7 | **Ledger** | Institutional memory, accountability and control logic | Append-only, hash-chained record plus the kernel: constraints and pure functions | Governed read views; derived values; assignments; prices |
| 8 | **Release Gate** | Is an accepted change safe to run, especially inside the Factory itself? | Pre-registered criteria, sequential testing on canary data, independent approvers | Promoted change |

Agent 70 no longer exists as an actor. Its former duties are the Ledger kernel (§16.2): logic that anyone can replay and verify.

---

## 4. Architecture on one page

```
                ┌──────────────────────────── CONSTITUTION ────────────────────────────┐
                │  (human-ratified; charters for each institution sit beneath it)       │
                └───────────────────────────────────────────────────────────────────────┘
 Idea ─► INQUIRY ──sealed──► COUNCIL ──Alignment──► PLANNING ──Plan──► MARKET ──work──► COURT ──judgment──► RELEASE ─► Live
         (blind,             (Delphi,   Record      (decompose,        (assign by       (evidence          (sequential
          parallel)           no chair)  ratified    cross-exam,        kernel math,     rules; open         tests,
                                         by human    red team)          lease)           standing)           pre-registered)
                                                        ▲                 ▲                 │
                                                        └──── replan ─────┴──── rework ─────┘
                                                                                            │
                           AUDIT ◄──────────── samples accepted AND rejected work ──────────┘
                             └──► system corrections → Constitution / charter amendment proposals

 LEDGER: every institution writes; charters grant read rights; the kernel computes posteriors, prices, assignments, seats.
```

**Boundary rule.** An institution receives only its predecessor's ratified output plus the context its charter grants. Planning does not read the Council transcript. The Market does not read the Planning debate. The Court does not read the worker's reasoning before committing its first verdict.

---

## 5. The Constitution

Articles apply to every institution. Charters (§7) add institution-specific rules and may not contradict an article.

| # | Article | Mechanical enforcement |
|---|---|---|
| 1 | **No inherent rank.** No participant holds authority from vendor, size, benchmark position or history. | No rule anywhere references a benchmark or a vendor. Benchmarks may enter only as disclosed priors in Ledger views. |
| 2 | **Equal standing, different roles.** Every participant is bound by the same rules. Roles differ by institution and by *earned eligibility* (Article 12), never by identity. | Charters define roles. Eligibility rules are stated in terms of recorded outcomes, and apply identically to every participant. |
| 3 | **Separation of institutions.** Only a ratified output crosses an institutional boundary. Deliberation transcripts do not. | The kernel assembles each manifest from the charter's allowed inputs only. |
| 4 | **Immutable history.** Material actions are attributable and append-only. Revisions reference, never rewrite. | SQLite triggers abort UPDATE/DELETE on Ledger tables. Hash chain. |
| 5 | **Facts, assertions, derived values.** FACT: observed by tools, Git, adapters or the kernel. ASSERTION: claimed by a participant or a human. DERIVED: computed from facts by a versioned, published function. | Separate tables. Derived values cite function and charter version. |
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
| 16 | **Every procedure is bounded.** Each loop has a budget and a terminal route to replanning or a human. | Charter budgets, enforced by the kernel. |
| 17 | **Collective behavior is monitored.** Pairwise and group patterns are measured, not only individual outcomes. | Audit charter (§14). |
| 18 | **Amendment.** Participants may propose amendments. Only a human ratifies them, as a new version. | `charter_version.ratified_by` must reference a human. |

---

## 6. Memory and information rights

Memory is the central design variable. Whoever holds information and decides what others see holds power. r1 concentrated both in one scorer. r2 splits them.

- **The Ledger holds memory.** It decides nothing.
- **Charters grant read rights.** The kernel enforces them mechanically. Rights change only by charter amendment, which only a human can ratify.
- **Manifests record exposure.** Every model call carries the list of what it was shown.

### 6.1 Read-rights matrix

| Institution | Canonical input | Peer outputs | Peer identities | Own track record | Others' track records | Capacity |
|---|---|---|---|---|---|---|
| Inquiry | Idea brief + engineering context | **No** | **No** | No | No | No |
| Council | Sealed Inquiry submissions | Yes, anonymized | **No** (random labels per idea) | No | No | No |
| Planning | Idea + ratified Alignment Record (incl. minority positions) | Decompositions, anonymized, after commit | No | No | No | No |
| Market | Card, contract, card history (prior attempts, decline reasons, anonymized) | n/a | No | **Yes**, for similar cards | No | Own resource only (price band) |
| Court | Artifact, contract, evidence | Other verdicts **only after committing its own** | No (author and reviewers blinded to each other) | No | No | No |
| Audit | Contract + final artifact (controlled context) | No | No | No | No | No |
| Human | Everything | Yes | Yes | Yes | Yes | Yes |

**Rationale.**

- **Own record in the Market** gives each assignee the memory it needs to accept or decline responsibly. The kernel uses the full record; the participant sees only its own.
- **No peer identities anywhere** blocks prestige deference (T5) and makes targeted coordination (T3, T4) harder.
- **No others' records** prevents deference cascades ("a stronger participant will take this") and reduces the information needed for tacit collusion.
- **Commit-before-view appears in three institutions:** Inquiry, Planning decomposition and Court verdicts. It is the single most reusable defense against groupthink.

Whether showing own track record improves or distorts accept and decline decisions is an experiment (H7), not an axiom.

---

## 7. Charters

Every institution has a charter with the same ten fields. The kernel executes the charter. It never interprets it.

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
| Planning | Decomposers seated by the kernel (≥2 families required) | Decomposer, cross-examiner, reconciler (seated), red team (seated, not reconciler) |
| Market | Every configuration with capacity; assigned by the kernel | Worker, helper |
| Court | Seated by the kernel under independence constraints; open standing to challenge | Reviewer, challenger, replicator, expert witness |
| Audit | Seated by the kernel from outside the card's provenance chain | Auditor |
| Release | Independent approvers seated by the kernel; human for F2 | Approver, dissenter |

### 7.2 Seats instead of chairs

Wherever one participant must perform a role (synthesizer, reconciler, red team, reviewer, auditor, approver), the kernel fills the seat. It uses the same assignment function as the Market (§12), for that institution's task class, subject to the charter's independence constraints. The seed and propensity are recorded.

Where a charter values neutrality over competence (for example, the Council synthesizer), the charter sets a flat quality floor so every eligible participant has a real chance. No seat is permanent, so no participant becomes a chair or an architect.

### 7.3 Prompt-facing language

Charters specify the role text models receive. Human-facing names such as "Court" or "Council" need not appear in prompts. Neutral role text ("you are one of several independent reviewers") avoids performative adversarial or consensus-seeking behavior. This is a charter parameter, testable by experiment.

### 7.4 Selection bias: the strategy per institution

Each institution faces a different bias. Each uses the standard method that is optimal, or near-optimal, for that bias. Every draw records its propensity, so any estimate can be corrected by inverse weighting.

| Institution | Bias to defeat | Strategy | Why this one |
|---|---|---|---|
| Inquiry | Participation bias; anchoring on others' views | Universal participation; commit-before-view; identical brief | With everyone taking part there is no selection to correct. Contribution is measured by leave-one-out on the record. |
| Council | Order, prestige and dominance effects | Anonymized labels; presentation order randomized per participant; synthesizer seated by draw | Randomized order removes primacy effects. Anonymity removes prestige. |
| Planning | Anchoring on the first decomposition | Parallel commit-before-view; reconciler and red team seated separately | Independent drafts are only independent if they are produced blind. |
| Market | Easy-work selection; confounded competence estimates | Thompson sampling per task at shadow prices | Asymptotically optimal regret for this problem class. Explores exactly where uncertainty is high and stops as evidence accumulates. No tuned exploration rate. |
| Court | Reviewer selection; knowing the author; lack of ground truth | Blind seating by draw; commit-before-view; **planted defects** as ground truth | Planted defects give known answers, so detection rates are measured without waiting for escapes. |
| Audit | Non-representative samples | Stratified sampling with **Neyman allocation**, plus inverse-probability weighting | Minimises estimator variance for a fixed audit budget (`neyman_allocation` in the kernel). |
| Release | Post-hoc rationalisation; canary cherry-picking | Pre-registered criteria; randomized canary assignment; **Wald sequential test** (SPRT) | Fixes the error rates before data arrives and stops as soon as evidence is sufficient (`sprt` in the kernel). |
| Ledger | Survivorship: only successes get recorded | Every outcome is logged, including declines, surrenders, expiries and non-selection | Missing failures bias every estimate upward. |

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
| 4 — Synthesis | One synthesizer, seated by the kernel, drafts the record; all others attest per item: endorse or object | Full Council record, anonymized |

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
| C. Reconciliation | A reconciler seated by the kernel builds one backlog. Every decomposer attests or objects per card. |
| D. Red team | Seated by the kernel, excluding the reconciler: "If this backlog is executed exactly and successfully, could we still fail to deliver the original idea?" Every gap must be dispositioned. |

### 10.2 Mechanical checks (kernel)

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

**Purpose.** Allocate high-volume execution work under capability and capacity uncertainty. A continuous labor market with leases, reputation and capacity constraints. It clears by computation, not by bidding.

| Market element | Implementation |
|---|---|
| Supply | Configurations (model × effort) with free lease slots on a non-degraded resource |
| Demand | READY cards, bucketed into task classes |
| Scarcity | Subscriptions, GPU time, concurrency, context, time |
| Price | Shadow price per resource: the dual variable of its capacity constraint (§12.3) |
| Reputation | Beta posterior of success per (configuration, task class), from Ledger outcomes |
| Contracts | Card plus acceptance contract |
| Property rights | Leases |

### 11.1 Clearing

When a card becomes READY, the kernel assigns it with `assign()` (§12.5): Thompson sampling among configurations that clear the class's quality floor, at the current window's shadow prices. The seed derives from the card ID and charter hash. The assignment and its propensity are written to the Ledger.

### 11.2 The assignee's rights

The assigned configuration responds with one of:

| Response | Effect |
|---|---|
| ACCEPT (effort, expected consumption, confidence) | Lease granted. Stated values are assertions, scored later. |
| DECLINE (reason) | Recorded. The card is re-assigned without that configuration. If ≥3 distinct families decline citing ambiguity, the card returns to Planning. |
| REQUEST_CLARIFICATION | Card waits. Routed to Planning, or to the human if intent-level. |
| PROPOSE_SPLIT | Returned to Planning. Mechanical check: child contracts cover the parent; value points sum to the parent. |
| REQUEST_HELP | A helper is seated by the kernel. Its advice enters the worker's manifest. The helper's family is then barred from reviewing that card in the Court. |

Declines and surrenders are data. They are never penalized (Article 8). The posterior counts them as neither success nor failure, and their cost is recorded.

### 11.3 Eligibility is the quality floor

r2's licensing rule ("≥N accepted cards before R2") is now a special case of the kernel's quality floor. A configuration is eligible for a class only when the lower credible bound of its success posterior clears the floor τ. At R2–R3 the charter sets a high τ and a high confidence z. This requires both a good record and enough of it. Qwen can earn R2 work. A frontier model with no record in that class cannot take it yet. Benchmarks enter only as weak priors that evidence quickly overrides.

### 11.4 Leases

- One active lease per card, enforced by the database.
- One Git worktree branch per lease.
- TTL with heartbeat. Heartbeat = observed adapter activity or commits. Initial: 20 min without heartbeat; hard cap by risk class.
- Expiry: branch preserved, card back to READY, attempts +1.
- Concurrency cap = observed resource concurrency. This prevents hoarding.

### 11.5 Nothing eligible

If no configuration clears the floor, the class is **unserved**. The kernel reports it; it does not lower the floor. Route: split in Planning → human. Budgeted per Article 16.

---

## 12. Intelligence and capacity allocation

This section answers: how is each institution given the right level of intelligence, subscription and tokens, with no wasted frontier reasoning on simple work, and how is this modelled, monitored and trialled?

### 12.1 Configurations and levels

A configuration is **model × version × reasoning effort**, bound to one capacity resource. Plain deterministic code is also a configuration. It has zero tokens and no capacity limit.

| Level | Example | Marginal cost |
|---|---|---|
| L0 | Deterministic code: tests, linters, schema checks, SPRT, hash checks | Zero; instant |
| L1 | Local Qwen-class | GPU time and queue delay |
| L2 | MiMo-class, large subscription | Rarely binding capacity |
| L3 | Frontier model, low effort | Scarce subscription capacity |
| L4 | Frontier model, high effort | Scarcest; slowest |

Levels are **descriptive only**. No rule references them. Assignment uses measured outcomes, never level.

### 12.2 The model

For configuration *c* on task class *k* (a bucket of work inside one institution):

- **Competence:** p(c,k) ~ Beta(α, β), updated from Ledger outcomes. The prior is benchmark-derived, worth a few pseudo-observations, and decays with a half-life so provider model changes are tracked.
- **Consumption:** t(c,k) = observed mean tokens per task.
- **Charter economics for k:** value of success V, cost of failure F (rework, downstream and escape cost), quality floor τ, floor confidence z, time cost per token θ.

**Eligibility (minimum sufficient intelligence):**

  E(k) = { c : mean(p) − z·sd(p) ≥ τ }

**Net value** at resource shadow price λ:

  NV(c,k) = p·V − (1 − p)·F − (λ_r(c) + θ_k)·t(c,k)

**Window problem** (solved per planning window, e.g. per subscription window):

  maximise Σ_k Σ_c n_k · x_ck · NV(c,k)
  subject to Σ_k n_k · x_ck · t(c,k) ≤ C_r − R_r for every resource r;  Σ_c x_ck = 1;  x_ck = 0 if c ∉ E(k)

where n_k is forecast demand, C_r remaining capacity, R_r the reserve, and x_ck the share of class k given to c.

### 12.3 Shadow prices are Lagrange multipliers

The kernel solves the window problem by Lagrangian relaxation (`solve_allocation`). The multiplier λ_r on each capacity constraint is the shadow price. It has an exact meaning: the value lost per token if resource r had one fewer token.

- If a resource will not run out before reset, λ_r = 0. Its unused capacity is perishing, so using it is free.
- If a resource is over-subscribed, λ_r rises until demand fits. Scarce frontier capacity then flows only to classes where its quality margin exceeds its price.

This replaces r2's hand-tuned pressure formula with a quantity derived from the optimisation itself.

### 12.4 Why simple work leaves frontier models: the answer and its qualification

Three terms keep over-qualified configurations off simple work:

1. **Capacity price λ.** When frontier capacity is scarce, spending it on work that L1 or L2 does nearly as well has a real opportunity cost.
2. **Time cost θ.** Frontier models at high effort are slower and use more tokens. Where the charter prices time, a cheaper sufficient configuration wins even with capacity to spare.
3. **L0 first.** Where deterministic code clears the floor, it wins outright.

**Qualification (a result from the model, not an opinion).** Under subscriptions, every model's marginal cash cost is zero until its capacity binds. If frontier capacity would expire unused and the charter puts no price on time, using it on simple work is *not* waste: the output is better and nothing is lost. The kernel reflects this. Tests `test_perishing_frontier_capacity_absorbs_simple_work` and `test_time_cost_keeps_simple_work_off_slow_configs_under_surplus` demonstrate both cases.

**Setting V, F, τ, z and θ per task class is the human's lever.** These are charter parameters, human-ratified and versioned. They are the only place where judgment enters allocation.

### 12.5 Assignment with exploration

`assign()` draws each eligible configuration's success probability from its posterior, using a seed derived from Ledger identifiers, and picks the highest net value at the window's prices. This is Thompson sampling:

- Configurations with thin records sometimes draw high and receive work, so evidence accumulates where it is missing.
- Exploration fades automatically as posteriors tighten.
- The propensity is estimated by replaying the draw and is recorded. Any alternative policy, including the legacy router, can be evaluated on logged data by inverse-propensity weighting without being deployed.

### 12.6 Institution profiles (initial hypotheses, to be learned)

| Institution | Task classes (examples) | Starting expectation | What decides it |
|---|---|---|---|
| Inquiry | submission | All models take part (charter). Only **effort** is optimised. | Unique surviving contribution per token |
| Council | critique, synthesis seat | Higher levels; volume is tiny, so cost is small | Human rating of Alignment Records; downstream replan rate |
| Planning | decomposition, reconciliation, red team | Highest levels. Errors here propagate to every card. | High F, high τ; feature-card failures; replan rate |
| Market | cards by size × risk × verifiability | Widest spread. L1–L2 on small, well-tested cards; L3–L4 on large or weakly verifiable ones | Per-class posteriors |
| Court | deterministic checks, R1 review, R2 review, replication | L0 for checks. Reviews need a family other than the author's, at the level that meets the detection floor | Detection rate on planted defects |
| Audit | replication, mutation analysis | Strong and independent; low volume | Agreement with human samples |
| Release | canary metrics, SPRT, F2 review | **Mostly L0.** Models only for F1–F2 review | False promotion and false rejection |
| Ledger | all kernel functions | **L0 only. Never a model.** | Replay equality |

### 12.7 Cascades where verification is cheap

Where a reliable verifier exists (tests, invariants), a class may run as a **cascade**: try the cheapest eligible configuration, verify, escalate only on failure. Expected cost = c₁ + (1 − p₁)·c₂ + (1 − p₁)(1 − p₂)·c₃ (`cascade_cost`). Cascades are a charter option per class. They are invalid where the verifier is weak, because failures would pass silently.

### 12.8 Worked example (synthetic data)

`python3 kernel/demo.py`. All numbers are illustrative, not measurements of real models.

| Task class | Frontier scarce | Frontier surplus near reset |
|---|---|---|
| release.checks | code 100% | code 100% |
| court.review.R1 | MiMo 41%, Claude-high 30%, GPT-high 28% | Claude-high 60%, GPT-high 40% |
| market.card.small | MiMo 97%, Qwen 3% | MiMo 94%, Claude-high 3%, Qwen 2% (time cost keeps frontier off) |
| market.card.large | Claude-high 52%, GPT-high 48% | Claude-high 76%, GPT-high 24% |
| planning.decompose | Claude-high 100% (GPT-high's record too thin to clear the floor) | Claude-high 100% |
| audit.replicate | GPT-high 56%, Claude-high 44% | Claude-high 58%, GPT-high 42% |
| Frontier shadow prices | positive; capacity 100% used | zero |

Read-outs: the release checks never touch a model; Planning demands both quality and evidence; frontier reviews shift to MiMo when frontier capacity is scarce; small cards stay off frontier models even with spare capacity because time is priced.

### 12.9 Capacity ledger

| Source | What | Record type |
|---|---|---|
| Adapter | Tokens, requests, latency | FACT |
| Provider | Quota headers, throttles (429s), reset times where exposed | FACT |
| Local host | GPU utilization, VRAM, queue depth | FACT |
| Kernel | Remaining capacity estimate; demand forecast; shadow prices | DERIVED |
| Participant | Expected consumption for a card | ASSERTION (calibrated) |

A model cannot know its account's quota. Adapters observe capacity. No participant has a write path to capacity data. A reserve (initial: 15% of frontier capacity) is subtracted from C_r for Court challenges, audit and escalations, and released before reset.

### 12.10 Minimum telemetry per model call

`institution, task_class, config (model, version, effort), resource, window, manifest_hash, tokens_in, tokens_out, latency, outcome, rework_cycles, later_audit_finding, assignment_propensity`. Nothing else is required to fit the model.

### 12.11 Monitoring

| KPI | Definition | Alarm |
|---|---|---|
| Over-provisioning | Share of tokens above the cheapest eligible configuration (`over_provisioning`) | Rising while λ = 0 and θ > 0 |
| Under-provisioning | Failures by configurations whose posterior later fell below τ | Any sustained excess |
| Posterior calibration | Predicted versus realised success per class | Outside credible band |
| Perished capacity | Capacity unused at reset | Above threshold while classes were unserved |
| Frontier burn | Projected exhaustion before reset | Earlier than reserve release |
| Unserved classes | Classes with no eligible configuration | Any |

### 12.12 Trialling models per institution

- **New model:** enrol it as new configurations with a weak benchmark prior. Thompson sampling gives it work where it could plausibly be best. Its share then grows or shrinks on evidence alone.
- **Calibration tournament (cold start):** replay a fixed set of historical cards, with known outcomes, across all configurations, using capacity that would otherwise expire. This seeds posteriors without selection bias.
- **Per-institution trial:** change a charter's enrolled configurations or economics, run in shadow with off-policy evaluation, then promote through the Release Gate.

### 12.13 Outcomes recorded per attempt

| Outcome | Posterior update |
|---|---|
| Accepted first pass | Success |
| Accepted after rework | Success, with rework cost recorded |
| Rejected or abandoned | Failure |
| Declined or surrendered | None (cost recorded) |
| Lease expired | Failure |
| Later audit finding | Revised to failure (new event, never an edit) |

---

## 13. Institution 5 — Assurance Court

**Purpose.** Decide whether the burden of evidence is satisfied. The constitution is the judge. There is no judge-model and no majority vote.

### 13.1 Roles and seating

| Role | Seating | Standing |
|---|---|---|
| Reviewer | Seated by the kernel among eligible configurations, under independence constraints | Verdict: pass / fail / concern |
| Challenger | **Open standing**: any participant may file | Challenge with or without reproduction |
| Replicator | Seated by the kernel; must not have seen the artifact before producing its evidence | Independent tests or reproduction from the contract |
| Expert witness | Called by a reviewer or challenger on a specific question; seated by the kernel among eligible | Testimony is an assertion |

Open standing means a single Qwen-found, reproducible critical defect defeats three frontier approvals.

### 13.2 Evidence classes

| Class | Examples | Nature |
|---|---|---|
| Deterministic | Locked-path check, build, visible and sealed tests, invariants, static analysis, security scan | FACT |
| Reproduction | Challenger's failing test or script, run by the kernel | FACT once run |
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

Risk class = the higher of path rules and planner declaration. It can be raised, never lowered, by the kernel.

### 13.5 Challenges

```
OPEN ─┬─ reproduction attached ─► kernel runs it
      │     ├─ fails on candidate ─► BLOCKING → rework
      │     └─ passes ─────────────► DISMISSED (fact recorded)
      └─ argued only
            ├─ R0–R1 ─► CONCERN (non-blocking; raises audit weight)
            └─ R2–R3 ─► corroboration by a further kernel-seated I2 reviewer
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

Auditor seated by the kernel from outside the card's provenance chain. Controlled context: contract plus final artifact only. Blind reproduction first. Mutation testing of the contract tests.

### 14.3 Planted defects

Known defects are injected into sandboxed copies of real submissions and sent through the Court. This measures reviewer and auditor sensitivity directly, within weeks. Planted defects are never integrated.

### 14.4 Collective-behavior measures (Article 17)

| Measure | Detects |
|---|---|
| Pairwise approval rate between author family and reviewer family, versus audit outcome | Mutual approval (T3) |
| Joint miss rate versus product of individual miss rates | Correlated error (T2) |
| Adoption rate of propositions by source family in Council, versus later validity | Deference and prestige (T5) |
| Decline patterns by class and family | Tacit division of easy work (T3) |
| Verdict agreement when reviewers see normalized versus raw artifacts | Hidden-signal channels (T4) |
| Escaped defects, false acceptance, false rejection, calibration | System quality |

### 14.5 Output

Two outputs per finding: reopen the card (label revised), and, where a pattern crosses a threshold, an **amendment proposal** to a charter or the Constitution. Ten audited cards with the same weakness produce one system correction, ratified by the human.

---

## 15. Institution 8 — Release Gate

**Purpose.** Decide whether an accepted change is safe to run, and above all whether a change to the Factory itself is safe to run inside the Factory.

```
ACCEPTED → INTEGRATED → [STAGED → OBSERVED] → PROMOTED
```

### 15.1 Scope by class

| Class | Scope | Path |
|---|---|---|
| Product code | Anything outside the Factory | Promoted on integration, per the product's own deployment rules |
| F0 | Factory tooling, adapters, UI | Canary on randomly assigned R0 cards; SPRT decides |
| F1 | Charter economics, prompts, kernel parameters | Shadow run with off-policy evaluation, then canary; SPRT decides |
| F2 | Kernel code, Ledger schema, Court rules, Audit, capacity accounting, permissions, charters, Constitution | All of F1, plus independent approvers and human ratification; validated by the currently promoted version; forward-only migrations; promoted by a separate minimal script, never by the running kernel |

### 15.2 Rules against groupthink among experts

Expert panels fail in known ways: premature convergence, deference to confident voices, post-hoc rationalisation, and suppressed dissent. Each rule below targets one.

| # | Rule | Targets |
|---|---|---|
| G1 | **Pre-registration.** Promotion criteria (metrics, thresholds, SPRT error rates p₀, p₁, α, β) are fixed in the Ledger before canary data exists. | Post-hoc rationalisation |
| G2 | **Numbers decide F0–F1.** The SPRT returns promote, reject or continue. No approver can override it except the human, and that override is recorded as a waiver. | Deference; opinion over evidence |
| G3 | **Independent commit-before-view.** F2 approvers are seated from ≥2 families, each blind to the others, and commit a verdict before seeing any other. | Cascade and anchoring |
| G4 | **Seated dissent.** One approver per F2 change is seated as dissenter, tasked to argue for rejection. The seat rotates by draw. | Premature convergence |
| G5 | **Veto by evidence.** Any reproduced regression blocks promotion, whoever found it. | Majority suppression |
| G6 | **Anonymous positions.** Approvers see verdicts labelled, never attributed. | Prestige |
| G7 | **Outside view.** Each F2 decision shows the base rate of past F2 rollbacks and escaped defects. | Overconfidence |
| G8 | **Cooling period for F2.** Minimum time between approval and promotion; any approver may withdraw during it. | Momentum |
| G9 | **No self-certification.** The version under review never evaluates itself (Article 15). | Reflexive capture |

### 15.3 Intelligence level

Mostly L0. SPRT, canary metrics, hash checks and rollback triggers are deterministic code. Models appear only as F1–F2 approvers and dissenters, seated by the kernel under this charter's floors.

### 15.4 Invariants

The running kernel cannot deploy itself. KPI and kernel code are F2: the Factory must not edit the ruler it is measured by. Automatic rollback on hash-chain break, replay mismatch, or acceptance or escaped-defect spikes. Ordinary product changes never touch staging, so bureaucracy scales only with reflexive risk.

---

## 16. Institution 7 — Ledger and kernel

### 16.1 Ledger

Institutional memory: what was proposed, by whom, what each participant knew at that point, what changed and why, who did the work, what evidence existed, what failed, what ultimately happened.

- SQLite (append-only, hash-chained) plus Git (artifact truth).
- Every row is FACT, ASSERTION or DERIVED.
- Every model output references its context manifest.
- No participant controls history. No model has a write path; all writes go through the kernel under a lease or seat token.

See [`ledger-schema.sql`](ledger-schema.sql). Validated invariants: append-only enforcement; immutable card versions; no card without a requirement link; every draw has a recorded propensity; no lease without an accepted assignment; one active lease per card; charters ratified only by a human; no agent actor type exists.

### 16.2 The Ledger kernel (replaces Agent 70)

Agent 70 is not reframed. It is dissolved. Its control duties become part of the Ledger itself, in two layers.

**Layer 1: constraints inside the database.** These rules cannot be broken by any process. Examples: append-only history; immutable cards; one active lease per card; charters ratified only by a human; valid state transitions only. They are enforced by SQLite triggers and constraints (see the schema).

**Layer 2: pure functions over Ledger rows.** Every control decision is the output of a published function:

  output = f(ledger rows, charter version, seed)

| Function | Mathematics | In `kernel/allocation.py` |
|---|---|---|
| Competence | Beta–binomial posterior with decay | `Posterior` |
| Eligibility | Lower credible bound ≥ τ | `window_options` |
| Capacity prices | Lagrangian dual of capacity constraints | `solve_allocation` |
| Assignment and seats | Seeded Thompson sampling; recorded propensity | `assign` |
| Cascades | Expected cost of escalation chains | `cascade_cost` |
| Audit sampling | Neyman allocation | `neyman_allocation` |
| Release decision | Wald SPRT | `sprt` |
| Waste monitoring | Over-provisioning index | `over_provisioning` |
| Independence levels | Set logic over context manifests | Phase 0 |
| State transitions | Event-sourced reducer: state′ = δ(state, event) | Phase 0 |

**Probabilistic determinism.** Randomness is essential for exploration and for fair seating. Every random draw is seeded from Ledger identifiers, so the same inputs always give the same output. Decisions are stochastic in design and deterministic in fact.

**Verification by replay.** Anyone can recompute any decision from the Ledger and compare. A mismatch is an integrity alarm and triggers rollback. This is the operational difference from an agent: an agent's decision can only be trusted, while a kernel decision can be checked.

**What still executes.** A process must run the functions, call adapters and advance clocks. It is plain infrastructure, like a database engine. It holds no state outside the Ledger and has no discretion. It may not import model adapters into the kernel (CI lint), and its outputs are replay-checked.

**Where judgment remains.** Only in charter parameters: V, F, τ, z and θ per task class, risk path rules, budgets, audit targets, SPRT error rates, and family labels. All are human-ratified and versioned. None is hidden in code.

### 16.3 Goodhart pairs

| Metric | Gaming path | Counter-metric or control |
|---|---|---|
| First-pass acceptance | Easy cards; weak contracts | Kernel assignment; sealed tests; mutation score; audit-revised labels |
| AUW/$ | Avoid frontier; split to inflate count | Value points ratified at plan; splits preserve value; escaped defects |
| Throughput | Tiny cards; hoarding | Value-weighted; lease caps |
| Calibration | Constant hedging | Brier resolution component |
| Surrender rate | Concealment or avoidance | False-surrender and failure-after-high-confidence rates |
| Review rejections | Nitpicking | Blocking requires reproduction; false-rejection audit |
| Audit escaped rate | Lenient auditors | Planted defects also test auditors |
| Mutual approval | Collusion | Pairwise audit (§14.4) |
| Net value (kernel objective) | Operators inflate V or deflate F to steer work | V, F, τ, θ are F2 charter parameters; human-ratified; changes shadow-tested |

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
| Emergent collusion (mutual approval) | Blind seating by seeded draw; rotation | Pairwise approval versus audit | Bar the pair; re-review their history |
| Hidden-signal coordination | Schema-constrained channels; normalized artifacts at R2+ | Raw-versus-normalized verdict gap | Normalize by default; revoke participant |
| Reward hacking | Locked and sealed tests; locked paths | Mutation score; planted defects; audit | Reject; revise labels |
| Confidence inflation | Stated confidence never enters assignment | Calibration views | None needed beyond measurement |
| Card hoarding | Kernel assigns; lease cap = resource concurrency; TTL | Leases versus throughput | Expire |
| Easy-work selection | Kernel assignment; models cannot pick cards | Declines by class | Planning review of declined classes |
| Difficult-card starvation | Every READY card is assigned; unserved classes reported | Time in READY; unserved classes | Split in Planning; human |
| Unnecessary frontier use | Shadow prices; time cost; L0 first | Over-provisioning KPI | Adjust θ in charter |
| Frontier exhaustion | Reserve; shadow price | Burn-rate forecast | Pause frontier assignment below reserve |
| Expired capacity | Price zero near reset; deferrable assurance cards | Expired-capacity metric | Adjust thresholds |
| Local model overreach | Quality floor with credible bound | Posterior calibration | Posterior falls below floor; eligibility lapses |
| Capacity misinformation | Only adapter and provider facts are authoritative | Estimate versus observed throttles | Conservative re-estimate |
| Hidden cognitive authority | No actor in the control path; kernel is pure functions | Replay check of every decision; CI import lint | Rollback to last charter version |
| Kernel misspecification | Unit tests; F2 path; shadow runs | Posterior calibration; over- and under-provisioning KPIs | Charter amendment; rollback |
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
| Current intelligent router | REPLACE as authority | Keep as a logged advisory assertion from `legacy_router`, compared against Market outcomes. Not a fallback: a fallback smarter than the primary is a hidden authority. On kernel failure, stop and hold. |
| Director → Worker → Checker | REPLACE | Council/Planning → Market → Court |
| Inquiry, Council, Planning, Audit, Release Gate, Ledger kernel, charters, manifests | NEW | This document and `kernel/` |

**Migration options.** Incremental uplift if model choice sits behind one seam and SQLite can gain an append-only Ledger alongside existing tables. Substantial refactor if routing is spread across stages and prompts. Parallel V2 if state cannot be made append-only without breaking running work. Clean rebuild is not justified: it discards the history that the Market's reputation depends on.

**Coupling questions for the code:** How many call sites choose a model? Does any code rewrite history rows? Where does workflow state live? Can adapters report usage and throttling? Are tests separable from implementation paths? How does the Factory change its own governance code today?

---

## 19. Experiments (falsifiable)

Council and Planning experiments are underpowered because idea volume is low. Read them directionally, with human rating. Market and Court experiments have volume.

| ID | Hypothesis | Design | Falsified if |
|---|---|---|---|
| H1 | Every participant adds unique value in Inquiry | Leave-one-out on unique surviving contribution | A participant is below 5% over ≥20 ideas |
| H2 | Kernel assignment beats the legacy router on net value | Off-policy evaluation with recorded propensities | Router's estimated net value is equal or higher |
| H3 | Anonymization reduces deference in Council | Randomize anonymized versus named rounds | No change in adoption-by-source bias |
| H4 | Cross-family review detects more than same-family fresh review | Planted defects to I1 versus I2 seats | No difference |
| H5 | Higher reasoning effort has net value in some classes | Effort levels as separate configurations under Thompson sampling | No class assigns high effort after posteriors converge |
| H6 | A coarse Factory-wide capacity band improves outcomes | A/B on Market view | No gain, or more deference |
| H7 | Showing own track record improves accept/decline calibration | A/B on Market view | Calibration unchanged or worse |
| H8 | Separation (no Council transcript in Planning) reduces bleed without losing quality | A/B on Planning manifests | No difference in replan rate or red-team gaps |
| H9 | Normalized artifacts at R2+ reduce correlated approval | Raw versus normalized seats | No verdict gap |
| H10 | Time cost θ reduces over-provisioning without lowering quality | Alternate θ = 0 and θ > 0 by window | No change in over-provisioning, or quality drops |
| H11 | Cascades beat direct assignment on high-verifiability classes | Alternate by window | No cost saving at equal quality |
| H12 | Release SPRT decides as well as human review on F0–F1 | Human shadow-reviews a sample of SPRT decisions | Material disagreement rate |

Set thresholds before each experiment starts.

---

## 20. Do not over-engineer: minimum build

### Phase 0 — trustworthy memory (first)

Ledger and projections; FACT / ASSERTION / DERIVED; manifests on every call; adapters emit usage and throttles; locked contracts; deterministic Court checks; leases with TTL; worktree per lease; merge queue; F2 protection for governance paths. **F2 protection must exist before the Factory next edits its own governance.** Legacy router demoted to an advisory assertion.

### Phase 1 — kernel, Market and Court

Kernel functions (already prototyped and tested in `kernel/`) wired to the Ledger; charter economics per task class; calibration tournament on historical cards; assignment with propensity; shadow prices and reserve; blind seated review; open-standing challenges; over-provisioning and calibration KPIs.

### Phase 2 — Audit and Release Gate

Neyman-allocated sampling; planted defects; mutation testing; pairwise collusion measures; Release Gate charter with SPRT and rules G1–G9; separate promoter.

### Phase 3 — Inquiry, Council, Planning automation

Low volume allows these to run semi-manually from day one under their charters, then be automated.

### Deferred

Adaptive audit rates; normalized artifacts below R2; Factory-wide capacity views; numeric evidence weights before audit data exists; hierarchical pooling across task classes; latency modelled separately from tokens; any UI beyond SQL views.

---

## 21. Decisions and open items

| # | Decision | Owner | Due |
|---|---|---|---|
| D1 | Ratify Constitution Articles 1–18 and the eight charters (or amend) | Isa | `[PLACEHOLDER]` |
| D2 | Approve Phases 0–1 as the next build | Isa | `[PLACEHOLDER]` |
| D3 | Set V, F, τ, z, θ for the first task classes (start with Market cards, Court R1 review, Release checks) | Isa | `[PLACEHOLDER]` |
| D4 | Approve Release Gate rules G1–G9 | Isa | `[PLACEHOLDER]` |
| D5 | Approve the calibration tournament: which historical cards, and which capacity windows | Isa | `[PLACEHOLDER]` |
| D6 | Weekly human-attention budget for ratifications, escalations and audit | Isa | `[PLACEHOLDER]` |
| D7 | Family lineage labels for current models | Isa | `[PLACEHOLDER]` |

### Risks

- **Human bottleneck.** Two ratifications per idea plus R3 approvals. Mitigation: daily batched digest; measure load from week one.
- **Cold start.** Posteriors are thin at first, so high floors leave R2+ classes unserved. Mitigation: calibration tournament; human sign-off for early R2+ work.
- **Mis-set economics.** The kernel optimises exactly what V, F, τ, θ say. Wrong values give wrong allocations, faithfully. Mitigation: shadow runs and the over- and under-provisioning KPIs.
- **Collusion detection needs volume.** Pairwise measures become meaningful only after hundreds of reviews. Planted defects shorten this.

### What I still need

1. The existing Factory source.
2. Subscription terms per resource: windows, resets, concurrency, fees.
3. Current card and idea volumes.
4. Where workflow state lives today.
5. The sources behind the claim in §2 that LLMs act collectively against human interest, so they can be cited precisely.
6. What "Jen" refers to (a model, a product or a method) and the role you see for it in "probabilistic determinism". The kernel must stay code, so a model can propose or check kernel mathematics in Planning or the Court, but cannot execute it.

---

**Takeaway:** set the charter economics for three task classes (D3), then build Phases 0–1. The kernel will show you, by evidence, which model each institution actually needs.
