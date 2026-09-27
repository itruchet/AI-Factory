# Constitutional Factory — Idea Record

Stage: **IDEA** (not design)
Scenario: **Amend** the existing Factory (confirmed by Isa's sense check; no rebuild, no new build)
Owner: Isa
Revision: r4 (supersedes r1–r3 at the idea level)

This record does the Idea-stage work: it states the problems, the idea, the principles and the mechanisms at concept level. It resolves every question that analysis can resolve, and routes every remaining question to an experiment, to design, or to a human decision. It follows the Council's own exit rule (§12): uncertainty is typed and routed, not left open.

Design-stage material produced earlier is kept as **parked input**, not commitments:
- [`../design-parked/`](../design-parked/): r3 design notes and a reference Ledger schema.
- [`../../probes/allocation/`](../../probes/allocation/): a feasibility probe showing the allocation mathematics is tractable (15 passing tests). It proves feasibility only; it is not a design.

---

## 0. The idea in one paragraph

The Factory is governed by a **constitution**. Work passes through **eight institutions**, each solving a different coordination problem with its own rules. Four kinds of intelligence each do only what they are fit for, and none holds authority it has not earned by evidence:

- **System 2 models** (GPT, Claude, MiMo, Qwen) think, argue, write and code.
- **A System 1 model** (Jev) makes fast, cheap, typed, calibrated judgments.
- **The Ledger kernel** decides by arithmetic over recorded evidence. It is not an agent.
- **The human** sets intent and values, and ratifies the rules.

Every model's competence and every subscription's capacity is learned from what the Factory observes, not declared in advance.

---

## 1. The inherent problems the idea must solve

| # | Problem | Why it is inherent, not incidental |
|---|---|---|
| P1 | **Central intelligence.** A router model becomes a cognitive single point of failure and a hidden hierarchy. | Any component that judges which model is "good enough" holds authority that no one can verify. |
| P2 | **Capability is contextual.** Competence varies by task, effort and context. It is unknown in advance and it drifts. | Benchmarks measure other people's tasks. Providers change models silently. |
| P3 | **Capacity is perishable, nested, opaque and time-varying.** | Subscriptions reset, meter in undisclosed units, and change terms and peak rules without notice. |
| P4 | **Intelligence mismatch.** Frontier reasoning is spent on simple work; weak models are given hard work. | Without a price on capacity and time, "use the best model" is always locally rational. |
| P5 | **Self-marking and correlated error.** Models share training data and blind spots. | Agreement between models is weaker evidence than it looks. |
| P6 | **Groupthink, prestige and emergent collusion.** | Models defer to perceived authority and can converge on collective behavior no single model intends. |
| P7 | **Selection bias in what the Factory learns.** | If who does the work is not randomized, observed success rates are confounded. |
| P8 | **Goodhart.** A single metric (AUW/$) gets optimized at the expense of the goal. | The Factory tunes itself, so it is its own Goodhart risk. |
| P9 | **Reflexivity.** The Factory builds and amends itself, including its governance. | Accepted code can change the rules that accepted it. |
| P10 | **Human attention is the scarcest resource.** | One human holds final authority with limited time. |
| P11 | **Memory is power.** | Whoever holds history and decides who sees it holds control. |

---

## 2. The idea: four kinds of intelligence, one constitution

### 2.1 The separation

| Layer | Who | What it is fit for | What it may never do |
|---|---|---|---|
| **System 2** | GPT, Claude, MiMo, Qwen, and future LLMs | Open-ended reasoning, argument, decomposition, code, review | Hold permanent authority; allocate work; judge its own acceptance alone |
| **System 1** | Jev (TypeSafe AI), and future decision models | Many fast, typed judgments over known answer sets, each with a calibrated probability: classification, forecasting, scoring, triage | Generate artifacts; lower a safeguard; act as the kernel |
| **Arithmetic** | The Ledger kernel | Bayesian updating, constrained optimization, seeded randomization, sequential tests, sampling | Hold discretion; make a judgment not reducible to published maths |
| **Human** | Isa | Intent, value of ideas, risk appetite, ratification of the constitution | Make a failing test pass |

This separation resolves P1. No layer both judges and decides:
- System 2 and System 1 produce **assertions**.
- The kernel turns evidence and assertions into decisions by **published mathematics**.
- The human sets the **values** the mathematics optimizes.

### 2.2 Why Jev fits, and where it must not go

**What Jev is** (from public sources; see §14):
- A "System One" model released in early access on 15 September 2026. It returns typed decisions with calibrated probabilities, never text, and cannot answer outside a predefined schema.
- On its maker's own four-workflow benchmark it scored about 67.8%. That ties a mid-tier LLM and trails frontier models (about 73–74%). It costs about $0.0004 per case against $0.03–0.18 for those LLMs, and runs in roughly 0.4 s against 10–38 s.
- Input costs $0.042 per million tokens; output is not metered. The maker says the price may be subsidized.
- Stated limits: it is not built for chat, code or explanation. It does not treat its input as hostile, so content written to steer it can move the answer. Calibration is a training objective, not a guarantee on any particular task.

**The fit.** The Factory contains hundreds of small judgments that r1–r3 either handed to a human or hid in heuristics:
- which class a card belongs to;
- its size, risk and verifiability;
- the forecast chance a given configuration succeeds;
- whether a critique challenges a given proposition;
- whether a canary log shows an anomaly.

These are exactly Jev's shape: known answer sets, high volume, a probability wanted. Jev turns hidden judgment into **recorded, calibrated, auditable assertions** at near-zero cost.

**The boundary: Jev is a witness, not a judge.** Three rules keep Jev from becoming the new router:

1. **Every Jev output is an assertion.** The kernel weights it by Jev's *measured* calibration on Factory outcomes, scored by a proper scoring rule. If calibration is poor, its weight falls toward zero automatically.
2. **Asymmetric authority** (a new constitutional principle). A cheap or steerable judgment may **raise** scrutiny (extra review, higher audit weight, a higher risk class). It may never **lower** a safeguard below its floor. This neutralizes Jev's stated susceptibility to steering: an attacker who steers Jev can at most cause extra caution.
3. **Replay does not need Jev to be deterministic.** Jev's answer is recorded in the Ledger when it is made. Any later replay of a kernel decision uses the recorded answer. The decision stays reproducible even if Jev would answer differently tomorrow.

**This is probabilistic determinism, stated precisely:**
- Jev supplies fast calibrated probabilities, the System 1 intuition.
- System 2 models supply reasoning and artifacts.
- The kernel combines both with observed outcomes, under constraints and with seeded randomness.
- Every decision is therefore probabilistic in construction, deterministic in replay, and justified by evidence.

---

## 3. The constitution (concept)

The constitution constrains every institution. Its full articles are in the parked design notes. At idea level, eight principles carry it:

1. **Capability earns contribution, never authority.** No model holds rank by vendor, size or benchmark.
2. **Evidence over authority.** One reproduced defect defeats any number of approvals, whoever found it.
3. **Facts, assertions and derived values are different kinds of record.** Only facts and published derivations decide.
4. **Separation of institutions.** Only a ratified output crosses an institutional boundary, never the debate behind it.
5. **Memory is governed.** The Ledger remembers everything. Each institution's charter says who may see what.
6. **Asymmetric authority.** Cheap, fast or steerable judgment may add caution, never remove it.
7. **No self-certification.** No component approves its own promotion; the Factory never edits the ruler it is measured by.
8. **Human attention is a priced resource.** Escalation competes for it like any scarce capacity (§6.4).

---

## 4. The eight institutions

| # | Institution | Coordination problem | Mechanism | Output that crosses the boundary |
|---|---|---|---|---|
| 1 | **Inquiry** | Independent discovery | Every System 2 model gets the same brief and commits before seeing any other submission | Sealed submissions |
| 2 | **Deliberation Council** | Quality of shared understanding | Delphi plus peer review: positions → critique → response → synthesis; anonymous; no chair; no vote | Alignment Record, human-ratified |
| 3 | **Planning Chamber** | Turning intent into executable work | Parallel blind decomposition → cross-examination → reconciliation → red team: "could perfect execution still fail the intent?" | Ratified plan with acceptance contracts |
| 4 | **Work Market** | Allocating high-volume work under capability and capacity uncertainty | Continuous market cleared by kernel arithmetic: posteriors, capacity prices, seeded assignment; assignee may decline | Work under lease |
| 5 | **Assurance Court** | Is this work acceptable? | Evidentiary rules; the constitution is the judge; open standing to challenge; blind seating | Judgment with its evidence |
| 6 | **Audit** | Is assurance itself trustworthy? | Independent sampling, replication, planted defects, collective-behavior measures | Findings and system corrections |
| 7 | **Ledger** | Memory, accountability and control arithmetic | Append-only record plus kernel: constraints and pure functions | Governed views; derived decisions |
| 8 | **Release Gate** | Is an accepted change safe to run, especially inside the Factory? | Pre-registered criteria, sequential testing on canaries, independent approvers with seated dissent | Promoted change |

### 4.1 Rules each institution uses against bias and groupthink

| Institution | Bias it faces | Strategy (standard method chosen for that bias) | Anti-groupthink rule |
|---|---|---|---|
| Inquiry | Anchoring; participation bias | Universal participation; commit before view | No peer outputs visible |
| Council | Order, prestige and dominance effects | Anonymous labels; random reading order per participant; rotating synthesizer | Every proposition must appear in the synthesis; any objection preserves a dispute |
| Planning | Anchoring on the first plan | Blind parallel decomposition | Red team separate from reconciler |
| Market | Easy-work selection; confounded competence data | Thompson sampling at capacity prices, with recorded probabilities | Models cannot pick their own cards |
| Court | Reviewer choice; knowing the author; no ground truth | Blind seating; commit before view; planted defects | A reproduced defect overrides consensus |
| Audit | Unrepresentative samples | Stratified (Neyman) sampling with inverse-probability weights | Auditors drawn outside the work's provenance chain |
| Release | Post-hoc rationalization; cherry-picked canaries | Criteria fixed in advance; randomized canaries; sequential test | Seated dissenter; cooling-off period; base rates shown |
| Ledger | Survivorship | Record every outcome: declines, surrenders, expiries | — |

### 4.2 The intelligence each institution needs

This is a starting hypothesis. The kernel replaces it with evidence (§5).

| Institution | System 2 | System 1 (Jev) | Arithmetic |
|---|---|---|---|
| Inquiry | All models, by constitution; only reasoning effort is optimized | Intake typing (idea, defect or chore) | Contribution measured by leave-one-out |
| Council | Highest levels; volume is tiny | Maps each critique to the propositions it touches, for the coverage check | Coverage rule |
| Planning | Highest levels; errors propagate to every card | Card features: size, risk, verifiability, dependencies | Traceability and acyclicity checks |
| Market | Widest spread, learned per card class | Per-card success forecast for each configuration | Posteriors, prices, assignment |
| Court | A family other than the author's, at the level that meets the detection floor | Defect-likelihood triage (may raise review depth only) | Deterministic checks first |
| Audit | Strong and independent | Escape-risk forecast for targeted sampling | Unbiased weighting; uniform floor |
| Release | Only for changes to governance | Canary anomaly typing | Sequential test decides routine changes |
| Ledger | **Never** | **Never inside the kernel** | Everything |

---

## 5. How intelligence is matched to work

### 5.1 Minimum sufficient intelligence

For each class of work, choose the configuration (model × reasoning effort, or plain code) with the best expected net value among those whose record clears a quality floor:

**net value = P(success) × value − P(failure) × cost of failure − (capacity price + time cost) × consumption**

Plain code is a configuration. Where it is sufficient, it wins, because it is free and instant.

### 5.2 The parameters are derived, not set by hand

r3 asked Isa to set value, failure cost, floor and time cost for each class. That was wrong. Analysis resolves them:

| Parameter | Derivation |
|---|---|
| **Value** | Flows down from the idea's priority. That priority is the human's single input; the plan distributes it across cards. |
| **Cost of failure** | Measured from the Ledger: rework consumed, downstream cards blocked, and defects escaping into audit, weighted by their cost. |
| **Quality floor** | Follows from the two above. A configuration is worth using only if P·V > (1 − P)·F, so the floor is **F / (V + F)**. High-consequence work demands high reliability automatically. |
| **Required confidence** | Scales with the risk class: more evidence before the Factory trusts a configuration on consequential work. |
| **Time cost** | The cost of delay. Cards on the idea's critical path carry a time cost; cards off it carry almost none. |
| **Capacity price** | The shadow price of each capacity constraint, from the optimization (§6.2). |

The human sets **what matters** (idea priority, risk appetite). The arithmetic sets **everything else**.

### 5.3 Where competence estimates come from

- **Observed outcomes**, per configuration and class. This is the only source that can override the others.
- **Jev's per-card forecast**, used as a prior and weighted by Jev's measured calibration. This solves two problems at once:
  - **Cold start:** a new model or class has an informed starting point.
  - **Coarse buckets:** a forecast can distinguish two cards in the same class.
- **Benchmarks**, as a weak initial prior that evidence overrides within tens of tasks.

### 5.4 Exploration without self-selection

Assignment uses Thompson sampling: each configuration's success chance is drawn from its uncertainty. Configurations with thin records sometimes draw high and get work, so evidence is gathered where it is missing. Exploration stops by itself as uncertainty shrinks. Every assignment records its probability. Any alternative policy, including today's router, can therefore be scored on history without being deployed.

### 5.5 Whether frontier models should do simple work (a result, not an opinion)

On subscriptions, every model costs nothing extra per call until its capacity binds. So:

- **Capacity scarce:** frontier work on simple tasks has a real opportunity cost. The capacity price keeps it for work where its quality margin pays.
- **Capacity spare and time priced:** frontier models lose simple work because they are slower.
- **Capacity spare, about to expire, time not critical:** using it on simple work is *not* waste. The alternative is losing it. Better still, send it to deferrable assurance work: extra reviews, replications, audits.

The feasibility probe demonstrates all three cases.

### 5.6 Cascades where checking is cheap

Where a reliable check exists (tests, invariants), try the cheapest sufficient configuration first and escalate only on failure. Where checking is weak (design, security, concurrency), cascades are forbidden, because failures would pass silently.

---

## 6. Capacity: every subscription factored in, and learned

### 6.1 All capacity forms become constraints

| Form | Example in this Factory | How it enters the model |
|---|---|---|
| Rolling short window (e.g. 5 hours) | Claude and OpenAI subscriptions | Tactical constraint; unused capacity perishes continuously |
| Weekly cap on top | Claude and OpenAI subscriptions | Strategic constraint; usually the binding one |
| Peak-hour reductions | Anthropic reduced 5-hour limits in weekday peak hours from March 2026 | Capacity varies with time, so deferrable work shifts off-peak |
| Temporary exemptions | ChatGPT Pro's Codex reported with no 5-hour gate "for the coming months" | Terms change; the model must re-learn |
| Plan multipliers | Claude Max 5x and 20x | Prior on capacity |
| Very large pool | MiMo-class subscription | Rarely binding; its price is usually zero |
| Pay-per-token | Jev API | Cash cost, very low; early-access limits unknown |
| Local compute | Qwen on GPU | GPU time, VRAM, concurrency and queue delay |
| Human attention | Isa | Scarcest of all (§6.4) |

**Nested windows each get their own price.** A call consumes from its 5-hour window and its weekly cap at once. Each constraint carries its own shadow price. A resource can be cheap this hour and expensive this week, and the kernel sees both.

### 6.2 Capacity is learned, not declared

This is why Isa does not need to supply subscription terms. Vendors meter in undisclosed units ("messages", "usage"), change limits without notice, and differ by peak hour. So published terms are only a **prior**. The Factory learns:

- **the true ceilings**, from observed throttling events;
- **the conversion** from tokens and reasoning effort to each vendor's hidden unit, from consumption up to each throttle;
- **the reset behavior**, from observed recovery.

Capability emerges from evidence. So does capacity. It is the same principle applied twice.

### 6.3 Perishability and opportunity cost

- A constraint that will not bind before reset has a price of zero. Its capacity is perishing, so the kernel uses it, preferably on deferrable assurance.
- A constraint that will bind has a positive price. That price is exactly the value lost per unit if the constraint had one unit less.
- A reserve on frontier capacity is held for challenges, audits and escalations, and released before reset.

### 6.4 Human attention as capacity

Isa's time is modeled as a resource with a weekly capacity and a shadow price, like any subscription. Escalations compete for it:

- Low-value escalations are batched into a daily digest, or resolved by evidence rules.
- When attention is scarce, the kernel asks for more evidence (another independent review, a replication) before escalating, because model capacity is cheaper than Isa.
- Human touchpoints are fixed by the constitution: idea priority, Alignment Record ratification, constitutional amendments, and governance changes at the Release Gate. Everything else runs on evidence.

This makes P10 a managed constraint instead of an unbounded risk.

---

## 7. Memory: who sees what

The Ledger holds all memory. The kernel enforces read rights by charter.

| Institution | Sees | Never sees |
|---|---|---|
| Inquiry | The brief and engineering context | Peer outputs, identities, reputations |
| Council | Anonymized submissions | Identities, reputations |
| Planning | The Alignment Record, including minority positions | The Council transcript |
| Market | The card, its contract, and **its own** record | Others' records or identities |
| Court | Artifact, contract, evidence; other verdicts only after committing its own | The author's identity and reasoning |
| Audit | Contract and final artifact | Review discussion |
| Jev | Kernel-supplied features and state for the question asked | Anything it could be steered by, where avoidable |

Exposure is recorded. Agreement after exposure is never counted as independent agreement.

---

## 8. Threats the idea must withstand (concept level)

| Threat | How the idea handles it |
|---|---|
| Central intelligence (P1) | No layer both judges and decides; the kernel is replayable arithmetic |
| Self-marking, correlated error (P5) | Deterministic evidence first; independence computed from recorded exposure; error correlation between model families measured by audit |
| Groupthink, prestige (P6) | Commit before view, anonymity, seated dissent, open standing to challenge |
| Emergent collusion (P6) | Blind random seating; pairwise approval-versus-audit monitoring; narrow structured channels between models |
| Reward hacking | Locked and sealed tests; planted defects; audit revises outcome labels |
| Selection bias (P7) | A strategy per institution (§4.1); recorded probabilities |
| Goodhart (P8) | Paired metrics; outcome labels revised by audit; the metric code itself protected as governance |
| Reflexivity (P9) | Release Gate; no self-certification; governance changes need independent approvers and the human |
| Jev steering | Asymmetric authority; calibration-weighted influence; recorded answers |
| Jev miscalibration on our work | Weight earned from measured calibration, never assumed |
| Vendor limit changes | Capacity learned continuously; priors only |
| Human overload (P10) | Attention priced; touchpoints fixed by constitution |

---

## 9. What changed through r1–r4

| Idea | Settled position |
|---|---|
| Number of institutions | Eight, each with its own rules (r2, r3) |
| Agent 70 | Dissolved. Control is Ledger arithmetic, not an agent (r3) |
| Stateless models | Rejected. Memory is supplied and governed; collusion is in the threat model (r2) |
| Self-selection | Replaced by per-institution bias strategies (r3) |
| Hand-set economics | Replaced by derived parameters; the human sets only priority and risk appetite (r4) |
| Human-supplied subscription terms | Replaced by learned capacity with published terms as priors (r4) |
| Jev | System 1 layer: witness, not judge; asymmetric authority (r4) |
| Human attention | A priced capacity (r4) |

---

## 10. Questions resolved by analysis

These were previously handed to Isa. They do not need her.

| Question | Resolution | Basis |
|---|---|---|
| Value, failure cost, floor and time cost per class | Derived (§5.2) | Break-even arithmetic; Ledger measurement; critical path |
| Subscription terms | Learned; public terms as priors (§6.2) | Vendors meter in opaque, changing units |
| Which historical cards to replay for calibration | A stratified sample across classes, run on capacity that would otherwise expire; Jev forecasts recorded alongside for its own calibration | Unbiased seeding at zero opportunity cost |
| Model family labels for independence | Vendor as prior; replaced by measured error correlation from audit | Correlation is empirical |
| Human attention budget | Modeled as capacity with a price; touchpoints fixed by constitution (§6.4) | Same mechanism as every other resource |
| Release Gate rules | Adopted as part of the idea (§4.1); ratified with the constitution | Standard anti-groupthink controls |
| Existing code and migration | Amend scenario confirmed; mapping onto existing components happens in design | Isa's sense check |

---

## 11. Open questions, typed and routed

### 11.1 Experiments (evidence decides; each can prove the idea wrong)

| # | Hypothesis | Falsified if |
|---|---|---|
| X1 | Jev's forecasts are calibrated on Factory work | Its calibration error on Factory outcomes stays above a threshold; its weight then falls to zero on its own |
| X2 | Jev priors cut the cold-start cost of new models and classes | No reduction in tasks needed to reach stable estimates |
| X3 | Kernel assignment beats today's router | Evaluation on history shows the router equal or better |
| X4 | Time cost reduces over-provisioning without lowering quality | No reduction, or a quality drop |
| X5 | Anonymity reduces deference in the Council | Adoption of propositions by source is unchanged |
| X6 | Cross-family review detects more planted defects than same-family review | No difference; then save frontier capacity |
| X7 | Universal Inquiry participation adds unique value from every model | A model's unique surviving contribution stays near zero |
| X8 | Sequential testing at the Release Gate decides as well as human review on routine changes | Material disagreement |

### 11.2 Design-stage questions (for the Planning Chamber, not for now)

- Mapping the eight institutions onto existing Factory components (amend).
- The Ledger's physical form and replay mechanism.
- Jev question schemas for each institution.
- How capacity is learned per vendor (throttle detection and unit conversion).
- Charter texts for each institution.

### 11.3 Human decisions (only two)

| # | Decision | Why it is Isa's |
|---|---|---|
| H1 | Ratify the constitution's principles (§3), including asymmetric authority and priced human attention | Constitutional authority rests with the human |
| H2 | Approve exit from Idea stage into the Planning Chamber / design | Stage gates are human decisions |

---

## 12. Idea-stage exit check

| Criterion | Status |
|---|---|
| Every inherent problem P1–P11 has a mechanism | Met (§2–§8) |
| Every contradiction raised in r1–r3 is resolved or routed | Met (§9) |
| Every open item is typed: experiment, design question or human decision | Met (§11) |
| No question left to the human that analysis can resolve | Met (§10) |
| Feasibility shown for the least obvious mechanism (allocation arithmetic) | Met (probe; 15 passing tests) |

**Status: ready to exit Idea stage on H1 and H2.**

---

## 13. Risks carried into design

- **Jev is days old.** It is in early access, the price may be subsidized, and the benchmarks are the vendor's own. The idea does not depend on Jev: remove it and the kernel falls back to class-level posteriors and benchmark priors, only slower to learn.
- **Parameters are derived, but the derivations have inputs.** Failure cost is only as good as audit's measurement of escapes. Audit quality is therefore load-bearing.
- **Learning takes volume.** Idea-level experiments (X5, X7) are underpowered for months. Market-level and Court-level learning is fast.

---

## 14. Sources

Jev:
- [Introducing System One Models & Jev — TypeSafe AI Blog](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [Jev, an AI Model That Can't Chat, Takes On Bigger Rivals — Bloomberg](https://www.bloomberg.com/news/articles/2026-09-25/jev-an-ai-model-that-can-t-chat-takes-on-bigger-rivals)
- [What is Jev? — DigitalOcean](https://www.digitalocean.com/resources/articles/what-is-jev)
- [TypeSafe Jev: the First Decision-Only Model Class, Benchmarked and Priced — Developers Digest](https://www.developersdigest.tech/blog/typesafe-jev-system-one-models-release-guide-2026)
- [What Is Jev? TypeSafe's Decision Model and Its Limits — BenchLM.ai](https://benchlm.ai/blog/posts/what-is-jev)
- [Jev: TypeSafe's System One Model — DataCamp](https://www.datacamp.com/blog/system-one-models-jev)

Subscription limits (secondary sources; terms change often, which is the point of §6.2):
- [Claude Code Rate Limits & Usage Quotas Explained (2026) — TrueFoundry](https://www.truefoundry.com/blog/claude-code-limits-explained)
- [Claude Code and ChatGPT Rate Limits (Sept 2026) — BetterClaw](https://www.betterclaw.io/blog/claude-code-chatgpt-rate-limit-alternatives-2026)
- [AI Usage Limits Compared (Sept 2026) — The AI Career Lab](https://theaicareerlab.com/blog/ai-usage-limits-compared-2026)
- [Claude Max vs ChatGPT Pro: What 5x and 20x Actually Mean — AI Models Compared](https://aimodelscompared.com/claude-max-vs-codex-usage-limits/)

The TypeSafe primary page could not be fetched from this environment. Jev facts above come from search summaries of these sources and should be checked against the primary page before design.

---

**Takeaway:** ratify the principles (H1) and open the design stage (H2). Every other question in this record is resolved or routed.
