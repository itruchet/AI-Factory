# Constitutional Factory — Idea Record

Stage: **IDEA** (not design)
Scenario: **Amend** the existing Factory (confirmed by Isa's sense check)
Owner: Isa
Revision: r5 (supersedes r1–r4)

The idea, stated at concept level. Every question analysis can settle is settled here. Every remaining question is routed to an experiment, to design, or to Isa. The central mechanism has been stress-tested in a simulation ([`probes/pull-rules/`](../../probes/pull-rules/), synthetic data, 3 passing tests). Earlier design material is parked in [`../design-parked/`](../design-parked/); the r3–r4 allocation maths is superseded ([`probes/_superseded/`](../../probes/_superseded/)).

---

## 0. The idea in one paragraph

The Factory is a chain of eight institutions under a constitution. At every institution, AI agents **pull** cards from a queue. Nobody assigns work. What each agent may pull is governed by **plain rules written into the Ledger**. Each institution's output is **marked** by the next institution. Marks feed back by rule:
- agents whose work is marked down get fewer and easier cards;
- agents whose work is accepted get more and harder cards;
- cards that keep failing climb to more capable agents, or go back to be rewritten.

Each agent sees its own record when it pulls, so it knows its capability. Fast, accurate agents naturally do more work. No agent, model or router manages any of this. The rules are the management.

---

## 1. The problems the idea must solve

| # | Problem |
|---|---|
| P1 | A central router is a cognitive single point of failure and a hidden hierarchy. |
| P2 | Capability is contextual, unknown in advance, and drifts as providers change models. |
| P3 | Subscriptions reset, throttle and change terms without notice. |
| P4 | Work is mismatched to capability: frontier reasoning on simple work, weak models on hard work. |
| P5 | Models mark their own work, and share blind spots. |
| P6 | Groupthink, prestige and emergent collusion. |
| P7 | Agents cherry-pick easy work, which hides weakness. |
| P8 | A single metric gets gamed. |
| P9 | The Factory amends itself, including its own rules. |
| P10 | Human attention is scarce. |
| P11 | Memory is power: whoever holds history controls the system. |

---

## 2. Verdict: rules, not Jev

Jev (TypeSafe's typed-decision model) was proposed in r4 as a "System 1" layer for small judgments. Every judgment it would make can instead be made by a rule or a count, and Jev would be one more agent in the control path.

| Criterion | Rules in the Ledger | Jev |
|---|---|---|
| Another agent in control? | **No** | Yes |
| Reproducible | By construction: same record, same result | Only if every answer is stored |
| Can be steered by content | No | Yes; the vendor states that input can move its answers |
| Explainable | Every decision cites a rule and a count | A probability without reasons |
| Dependency | None | Early-access product; price may be subsidized |
| Cold start | Starts from today's working mapping | Forecasts would help, but the mapping already exists |
| Per-card nuance | Card tier from card facts, corrected by escalation | Finer-grained forecasts |

What each proposed Jev job becomes:

| Proposed Jev job | Rules replacement |
|---|---|
| Card difficulty | Tier set by Planning rules (size, files, risk paths, dependencies); raised automatically when a card fails (R6) |
| Forecast of whether an agent will succeed | The agent's own record at that tier (R4, R5) |
| Defect triage | Deterministic checks first: build, tests, static analysis |
| Mapping critiques to propositions | Agents must cite proposition IDs in structured output; the rule checks coverage |
| Anomaly detection in releases | Control limits on canary metrics |

**Verdict: rules. Jev is not needed.** Its one real advantage, per-card nuance, is covered by escalation: a card that proves harder than its tier moves up. Any future model, Jev included, may enter only as a **worker inside an institution** under the same rules. It never enters the control logic.

---

## 3. The rule system

These rules are the whole of "management". They run identically in every institution. Only the **standards** differ by institution.

| # | Rule | What it does |
|---|---|---|
| R1 | **Pull** | An agent with a free slot pulls the next card. No one assigns work. |
| R2 | **Licence** | Each card has a difficulty tier. An agent may pull only tiers it holds a licence for. Licences form a ladder: holding tier 2 implies tier 1. |
| R3 | **Hardest first, oldest first** | An agent pulls the oldest card in the highest tier it is licensed for. It cannot pick within a tier. |
| R4 | **Allowance** | Each agent has a number of slots. An accepted card adds one, up to its concurrency limit. A markdown that takes its recent markdown rate **over the standard** halves them. Normal error within the standard costs nothing. |
| R5 | **Ladder** | After sustained success at its top tier, an agent receives **stretch cards** from the tier above. Meeting that tier's standard on them earns the licence. A full window **well over** the standard (1.5×) loses the top licence. The gap between the two thresholds (hysteresis) stops licences flapping on noise. A failed promotion attempt doubles the wait before the next one (back-off). |
| R6 | **Escalation** | A marked-down card is retried once at its tier by a **different** agent, then moves up a tier. A card that fails repeatedly at the top tier returns to Planning. The card is then suspect, not the agents. |
| R7 | **Pacing** | An agent on a capped subscription may work below its top tier only while its remaining cap is above the pro-rata line for the window. Near reset the line reaches zero, so leftover capacity is used freely. |
| R8 | **Attribution** | Every markdown carries a reason backed by evidence, and it lands on the agent that caused it: implementation → implementer; unclear or wrong card → the card's author in Planning; review miss found later → the reviewer who passed it, and the implementer; infrastructure → nobody. |
| R9 | **The marker is marked** | Reviewers are workers too. A pass later overturned by Audit, or a markdown overturned as unfounded, counts against the reviewer under R4–R5 in the Court. Marking is accountable in both directions. |
| R10 | **Self-awareness** | When pulling, an agent sees its own record: licences, allowance, recent rate against the standard, and the reasons behind its recent markdowns. It may decline a card with no markdown. Repeated declines at a tier return that licence: honest self-assessment reallocates work; it is not punished. |
| R11 | **Start state** | Licences and allowances start from today's predetermined mapping. It worked, so it is the starting point. The rules move it on evidence from day one. A new model starts at tier 1 and climbs by stretch cards. |
| R12 | **Late marks** | An Audit finding weeks later applies like an immediate markdown, counted twice, because escaped defects cost more. |
| R13 | **No orphan tiers** | If cards wait at a tier with no licensed agent for longer than a set time, the best-performing agent one tier below gets stretch cards. If there is none, the card is split in Planning or escalated to Isa. |

**Constants set once in the constitution:** window size, hysteresis factor, stretch-trial count, back-off, late-mark weight. **Standards set per institution by Isa:** the maximum acceptable markdown rate for each tier. These are the "KPI and standards".

### 3.1 Key points the rules encode

1. **One feedback loop serves all eight institutions.** Each institution's output is the next institution's input, and the next institution's acceptance is the mark. Institutions stay separate, each with its own charter, standards and memory rules. They share only the feedback rule, not their content.
2. **Marks must land on the right producer.** A failed build card may be the card writer's fault, not the coder's. Without attribution (R8), Planning never learns and coders are punished for bad cards.
3. **Markers must be marked.** Otherwise reviewers can wave work through, or reject it for nothing, at no cost (R9).
4. **Measure against the standard, not against perfection.** The simulation's first rule set halved allowances on every single markdown. Across 20 runs, accepted work fell 32% and an average of 540 cards were left in the queue at week end. Every agent errs sometimes; only errors beyond the standard should cost work.
5. **Cards fail too.** Escalation (R6) separates "this card is hard" from "this agent is weak".
6. **Self-awareness comes from memory, not introspection.** A model cannot know its own capability on this Factory's work. The Ledger can tell it. Seeing its own markdown reasons also lets it improve within the task, not only be reallocated.
7. **Start from what works.** The predetermined mapping is the starting state, not a thing to be discarded (R11).
8. **Speed is throughput.** A fast agent finishes sooner and pulls again. If it is also accurate, it takes more work. If it is fast and sloppy, R4 cuts its slots.

---

## 4. The eight institutions

| # | Institution | Coordination problem | Who pulls | What marks its output |
|---|---|---|---|---|
| 1 | **Inquiry** | Independent discovery | Every model, on the same brief, committing before seeing any other submission | Council: which propositions survive into the Alignment Record |
| 2 | **Deliberation Council** | Shared understanding | Every Inquiry participant; anonymous; no chair; no vote | Isa's ratification; Planning's clarification requests |
| 3 | **Planning Chamber** | Intent → executable cards | Decomposers blind in parallel, then reconciliation and red team | Market: cards declined as unclear; Court: rejections attributed to the card |
| 4 | **Work Market** | High-volume execution | Every agent, by R1–R13 | Court |
| 5 | **Assurance Court** | Is this work acceptable? | Reviewers, blind to author; open standing to challenge with evidence | Audit: overturned passes and overturned rejections |
| 6 | **Audit** | Is assurance trustworthy? | Auditors outside the work's provenance chain, on random and risk-weighted samples | Planted defects with known answers; Isa's sample |
| 7 | **Ledger** | Memory and the rules | Nobody. It is where rules run and marks are kept. | Replay: any decision can be recomputed from the record |
| 8 | **Release Gate** | Is an accepted change safe to run inside the Factory? | Approvers from different families, blind, with one seated dissenter | Canary results against criteria fixed in advance |

### 4.1 Institution-specific protections

| Institution | Main risk | Protection |
|---|---|---|
| Inquiry | Anchoring | No peer outputs visible until everyone has committed |
| Council | Prestige and dominance | Anonymous labels; random reading order; every proposition must appear in the synthesis; one objection keeps a point disputed |
| Planning | Anchoring on the first plan | Blind parallel decomposition; red team separate from reconciler |
| Market | Cherry-picking easy work | Hardest-first, oldest-first pull; no choice within a tier (R3) |
| Court | Self-marking; knowing the author | Blind review; deterministic checks first; a reproduced defect beats any number of approvals |
| Audit | Unrepresentative samples | Random plus risk-weighted sampling; planted defects as ground truth |
| Release | Post-hoc rationalization | Criteria fixed before data; seated dissenter; cooling-off period; no version approves itself |

---

## 5. Capacity and subscriptions under pull

**Correction to r4.** r3–r4 treated capacity as something to price and optimize centrally, and treated slowness as a cost. In a pull system neither is needed:

- **Using capacity is simply pulling.** An agent with subscription left keeps pulling. When throttled, it stops. When its window resets, it resumes. No component has to track this for allocation.
- **Speed is good.** Faster agents complete more cards. At the standard, that is more accepted work, which is the KPI.
- **Leftover capacity is used automatically.** An agent with nothing at its top tier pulls from lower tiers.
- **One risk remains, and one rule covers it.** A frontier agent could burn its weekly cap on easy cards early in the week and be throttled when hard cards arrive. Pacing (R7) lets it drop down a tier only while it is ahead of the pro-rata line. Hard work is never restricted. At reset the line reaches zero, so nothing is wasted.

All subscription forms fit without special handling: 5-hour rolling windows, weekly caps, peak-hour reductions, plan multipliers, MiMo's large pool, and Qwen's local GPU slots. Each simply determines when an agent can pull. In the simulation, frontier agents used 89–100% of their weekly caps and the hard-card queue stayed near empty.

**Human attention.** Isa's touchpoints are fixed by the constitution:
- setting each institution's standards;
- ratifying Alignment Records;
- constitutional amendments;
- governance changes at the Release Gate;
- R13 escalations.

Everything else runs on the rules.

---

## 6. The constitution (principles)

1. **Capability earns work, never authority.** Licences are earned by record and lost by record, by the same rules for every model.
2. **No manager.** No agent, model or router allocates work. Plain rules in the Ledger do.
3. **Evidence over authority.** A reproduced defect beats any number of approvals, whoever found it.
4. **Facts and claims are kept apart.** Test results, commits and timings are facts. "This is done" is a claim until the next institution marks it.
5. **Separation of institutions.** Only a ratified output crosses an institutional boundary, never the debate behind it.
6. **Memory is governed.** The Ledger holds all history. Each institution's charter says who sees what. Every agent sees its own record.
7. **Accountability in both directions.** Producers are marked by the next stage; markers are marked by Audit.
8. **No self-certification.** No change approves itself. Rule changes pass the Release Gate and Isa.

---

## 7. Memory: who sees what

| Institution | Sees | Never sees |
|---|---|---|
| Inquiry | The brief and engineering context | Peer outputs; identities |
| Council | Anonymized submissions | Identities |
| Planning | The Alignment Record, including minority positions | The Council transcript |
| Market | The card, its contract, and **its own record** (R10) | Others' records or identities |
| Court | Artifact, contract, evidence; other verdicts only after committing its own | The author's identity and reasoning |
| Audit | Contract and final artifact | Review discussion |

Showing an agent only its own record gives it self-awareness. It gets no information to defer to, compete with, or collude with other agents.

---

## 8. Threats and how the rules answer them

| Threat | Answer |
|---|---|
| Central intelligence (P1) | There is no allocator to fail or capture. Rules are replayable from the Ledger. |
| A weak agent keeps failing (P4) | R4 cuts its slots; R5 removes its top licence; R10 shows it why. |
| A strong agent on simple work (P4) | R3 sends it to its hardest licensed work first; R7 paces its drop-downs. |
| Cherry-picking easy work (P7) | R3: no choice within a tier. Declines return licences (R10). |
| Card hoarding | Slots are capped by allowance and concurrency. |
| Rubber-stamp or hostile reviewing (P5) | R9: reviewers are marked by Audit in both directions. |
| Bad cards blamed on coders | R8 attribution; R6 returns repeat failures to Planning. |
| Noise making licences flap | Hysteresis and full windows (R5). |
| Wasted retry cycles | Back-off on failed promotions (R5); retry by a different agent (R6). |
| Hard cards starving | R6 escalation; R13 orphan-tier rule. |
| Frontier cap exhausted early | R7 pacing. |
| Collusion between producer and marker (P6) | Blind review; Audit marks the marker; planted defects. |
| Groupthink (P6) | Commit before view; anonymity; seated dissent. |
| Gaming the markdown rate (P8) | Marks come from a different institution, audited later; late marks count double (R12). |
| Rules edited by the Factory itself (P9) | Rule changes pass the Release Gate and Isa. No change approves itself. |
| Provider silently changes a model | Its record moves; the rules follow the record. |

---

## 9. Evidence from the simulation (synthetic)

**Setup.** One weekly window. Four agents with hidden true success rates by tier. Qwen is wrongly licensed for tier 2, as a predetermined mapping might do. Cards arrive continuously. Results are the mean over 20 runs.

| Allocation | Accepted | Marked down | Qwen tier-2 markdowns | Backlog at week end |
|---|---|---|---|---|
| Static predetermined mapping | 1,660 | 266 (13.8%) | 116 | 0 |
| **Pull rules R1–R13 (final)** | **1,657** | **217 (11.6%)** | **36** | 5 |

- **Throughput held; markdowns fell 18%.** Qwen's failures on work beyond it fell 69%. It was demoted to tier 1, where it succeeds.
- **Self-correction works both ways.** When Qwen was upgraded mid-week, it re-earned tier 2 in most runs with no intervention.
- **The first rule set failed**, and that was informative (figures from the probe's first iteration, preserved in git history). It halved allowances on every markdown, used short noisy windows, escalated after one failure and started every allowance at one. Accepted work fell 32%. The fixes are now rules: measure against the standard, hysteresis, retry before escalating, start from the existing mapping, back-off.

---

## 10. Settled by analysis (not for Isa)

| Question | Settlement |
|---|---|
| Jev or rules | Rules (§2) |
| Subscription terms | Not needed. Pull plus throttling handles them; one pacing rule covers frontier caps (§5) |
| How a failing agent gets less work | R4 allowance and R5 ladder, against the standard (§3) |
| How an agent knows its capability | Its own record at pull time (R10) |
| Starting point | Today's predetermined mapping (R11) |
| Who is at fault when a card fails | Attribution by evidenced reason (R8) |
| Who checks the checkers | Audit marks reviewers; planted defects mark auditors (R9) |
| Card difficulty | Planning rules set the tier; escalation corrects it (R6) |
| Migration | Amend (Isa's sense check); mapping onto existing components happens in design |

---

## 11. Open items, typed and routed

### 11.1 Experiments (each can prove the idea wrong)

| # | Hypothesis | Falsified if |
|---|---|---|
| X1 | Pull rules match the static mapping's throughput with fewer markdowns on real work | Throughput drops more than 3%, or markdowns do not fall |
| X2 | Seeing its own markdown reasons improves an agent's next attempt | No change in its rework rate |
| X3 | Attribution (R8) improves card quality in Planning | Card-caused markdowns do not fall |
| X4 | Marking the markers (R9) reduces escaped defects | Audit escape rate unchanged |
| X5 | Pacing (R7) prevents frontier exhaustion without idle capacity at reset | Tier-3 backlog at cap exhaustion, or more than 10% of cap unused at reset |
| X6 | Anonymity reduces deference in the Council | Adoption by source unchanged |
| X7 | Universal Inquiry participation adds unique value from every model | A model's surviving contributions stay near zero |

### 11.2 Design-stage questions (for the Planning Chamber)

- Tier definitions per institution: which card facts set the tier.
- Mapping R1–R13 onto the existing Factory's cards, SQLite state, worktrees and workflow engine.
- Reason codes for R8, and the evidence each one requires.
- Initial constants: window, hysteresis, stretch trials, back-off.
- The Ledger views each agent sees at pull time (R10).

### 11.3 Isa's decisions

| # | Decision |
|---|---|
| H1 | Ratify the constitution's eight principles (§6) and rules R1–R13 (§3) |
| H2 | Set the standard per institution and tier: the maximum acceptable markdown rate. These are the KPI standards. Design can propose starting values. |
| H3 | Approve exit from Idea stage into design |

---

## 12. Idea-stage exit check

| Criterion | Status |
|---|---|
| Every problem P1–P11 has a mechanism | Met (§3–§8) |
| No agent or model in the control path | Met (§2) |
| Central mechanism tested for failure modes | Met (simulation; first version failed and was corrected) |
| Every open item typed and routed | Met (§11) |
| Only decisions that are genuinely Isa's are left to Isa | Met (§11.3) |

**Status: ready to exit Idea stage on H1–H3.**

---

## 13. Risks carried into design

- **Marks are only as good as the markers.** The whole loop rests on the Court and Audit being reliable. That is why R9, planted defects and Isa's sample exist.
- **Real success rates may be noisier than the simulation.** Window and hysteresis constants must be set from real variance in design.
- **Low-volume institutions learn slowly.** Inquiry and Council handle few items, so their feedback loops take months to settle. Market and Court settle within days.

---

**Takeaway:** ratify R1–R13 and set the standards (H1–H2). The rules then manage the Factory, starting from the mapping that already works.
