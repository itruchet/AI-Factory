# Constitutional Factory — Idea Record

Stage: **IDEA** (not design)
Scenario: **Amend** the existing Factory (confirmed by Isa's sense check)
Owner: Isa
Revision: r8 (supersedes r1–r7)

The idea, stated at concept level. Every question analysis can settle is settled here. Every remaining question is routed to an experiment, to design, or to Isa. The central mechanism has been stress-tested in a simulation ([`probes/pull-rules/`](../../probes/pull-rules/), synthetic data, 17 passing tests; visual summaries: [capability sort](https://claude.ai/artifact/B5RL3EqqouYKK6fUvnETwW), [golden rules and portfolio](https://claude.ai/artifact/JwEzM4KoKyUyedsWxZq6Xg)). Earlier design material is parked in [`../design-parked/`](../design-parked/); the r3–r4 allocation maths is superseded ([`probes/_superseded/`](../../probes/_superseded/)).

---

## 0. The idea in one paragraph

The Factory is a chain of eight institutions under a constitution. At every institution, AI agents **pull** cards from a queue. Nobody assigns work. What each agent may pull is governed by **plain rules written into the Ledger**. Each institution's output is **marked** by the next institution. Marks feed back by rule:
- agents whose work is marked down get fewer and easier cards;
- agents whose work is accepted get more and harder cards;
- cards that keep failing climb to more capable agents, or go back to be rewritten.

Success and velocity push an agent up to the hardest tier it can sustain: its **home tier**. Failure moves it down. Every agent always pulls the hardest card it is licensed for, so more capable agents take harder work and less capable agents take easier work. Frontier agents also keep a reserve of their subscription for hard work. Every model therefore settles at the tier where it meets the standard. Each agent sees its own record when it pulls, so it knows its capability. No agent, model or router manages any of this. The rules are the management.

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
| R3 | **Hardest first, oldest first** | An agent pulls the oldest card in the highest tier it is licensed for. It cannot pick within a tier. When a tier runs dry, capable agents take the next-hardest work, which pushes mid-tier agents down a step. This cascade is what sorts agents by capability. |
| R4 | **Allowance** *(dropped in r8, §3.2)* | Each agent has a number of slots. An accepted card adds one, up to its concurrency limit. A markdown that takes its recent markdown rate **over the standard** halves them. Normal error within the standard costs nothing. |
| R5 | **Ladder: success and velocity push agents up** *(velocity standard dropped in r8, §3.2)* | Each accepted card at an agent's home tier earns +1 promotion credit; each markdown costs −4. Credit therefore builds only for agents that are accurate, and it builds fastest for agents that are also fast. Enough credit makes **stretch cards compulsory**: the agent's next pulls come from the tier above. It is promoted if it meets that tier's **quality standard** (markdown rate) and **velocity standard** (cycle time no more than 1.5× the tier's median) over 20 trial cards. **Demotion is two-speed:** gross failure (over 2× the standard) after 10 cards; marginal failure (over 1.25×) only after two consecutive failing batches of 20, judged in separate batches rather than a rolling window. A failed promotion doubles the credit needed next time, capped at 2×. A **new model** needs only 5 credit to start trials until its first failed promotion (fast track). |
| R6 | **Escalation** *(optional in r8, §3.2)* | A marked-down card is retried once at its tier by a **different** agent, then moves up a tier. A card that fails repeatedly at the top tier returns to Planning. The card is then suspect, not the agents. |
| R7 | **Hard-work reserve** | Below its home tier, a capped agent may spend only the part of its subscription above what it would need to work its home tier at 75% of full speed until reset. Hard work is always covered; only true surplus flows to easier work. Uncapped agents have no such limit. (r6 also barred agents from easier work outright. The simulation showed that floor sorts worse, so r7 drops it; see §9.4.) |
| R8 | **Attribution** | Every markdown carries a reason backed by evidence, and it lands on the agent that caused it: implementation → implementer; unclear or wrong card → the card's author in Planning; review miss found later → the reviewer who passed it, and the implementer; infrastructure → nobody. |
| R9 | **The marker is marked** | Reviewers are workers too. A pass later overturned by Audit, or a markdown overturned as unfounded, counts against the reviewer under R4–R5 in the Court. Marking is accountable in both directions. |
| R10 | **Self-awareness** | When pulling, an agent sees its own record: licences, allowance, recent rate against the standard, and the reasons behind its recent markdowns. It may decline a card with no markdown. Repeated declines at a tier return that licence: honest self-assessment reallocates work; it is not punished. |
| R11 | **Start state** | Licences and allowances start from today's predetermined mapping. It worked, so it is the starting point. The rules move it on evidence from day one. A new model starts at tier 1 and climbs by stretch cards. |
| R12 | **Late marks** | An Audit finding weeks later applies like an immediate markdown, counted twice, because escaped defects cost more. |
| R13 | **No orphan tiers** | If cards wait at a tier with no licensed agent for longer than a set time, the best-performing agent one tier below gets stretch cards. If there is none, the card is split in Planning or escalated to Isa. |

**Constants set once in the constitution:** batch size (20), gross and marginal demotion factors (2×, 1.25×, two strikes), promotion credit and markdown debit (+1 / −4), trial count (20), back-off cap, fast-track credit (5), hard-work reserve (75%), late-mark weight. **Standards set per institution by Isa:** for each tier, the maximum acceptable markdown rate (quality). (r8 dropped the separate velocity standard: promotion credit is counted per card, so speed already moves models up; §3.2.) These are the "KPI and standards".

### 3.1 Key points the rules encode

1. **One feedback loop serves all eight institutions.** Each institution's output is the next institution's input, and the next institution's acceptance is the mark. Institutions stay separate, each with its own charter, standards and memory rules. They share only the feedback rule, not their content.
2. **Marks must land on the right producer.** A failed build card may be the card writer's fault, not the coder's. Without attribution (R8), Planning never learns and coders are punished for bad cards.
3. **Markers must be marked.** Otherwise reviewers can wave work through, or reject it for nothing, at no cost (R9).
4. **Measure against the standard, not against perfection.** The simulation's first rule set halved allowances on every single markdown. Across 20 runs, accepted work fell 32% and an average of 540 cards were left in the queue at week end. Every agent errs sometimes; only errors beyond the standard should cost work.
5. **Cards fail too.** Escalation (R6) separates "this card is hard" from "this agent is weak".
6. **Self-awareness comes from memory, not introspection.** A model cannot know its own capability on this Factory's work. The Ledger can tell it. Seeing its own markdown reasons also lets it improve within the task, not only be reallocated.
7. **Start from what works.** The predetermined mapping is the starting state, not a thing to be discarded (R11).
8. **Success and velocity decide the tier; capability settles there.** A fast, accurate agent earns credit quickly and is pushed up. A slow or reworking agent earns slowly, or loses credit, and stays on easier work.
9. **Hardest-first does the sorting; a floor does not.** Barring capable agents from easier work made them idle and then jump to the stalest easy cards. Letting every agent pull its hardest available card sorted agents better (§9.4).
10. **The backlog per tier is the capacity signal.** Easy cards queueing while frontier capacity is scarce means more cheap capacity is needed (more local Qwen slots, more MiMo concurrency). It does not mean the frontier should drop down.

---

### 3.2 Golden rules (r8)

Each allocation rule was removed in turn and tested against six stress scenarios, each built to trigger the failure that rule exists for: cold start, tight caps with an easy-card surge, a benchmark-overrated model, silent degradation, 25% of cards mislabelled, and a slow max-effort model at the top ([`probes/pull-rules/portfolio.py`](../../probes/pull-rules/portfolio.py), 24 runs each). A rule is golden if removing it costs more than 2% of value, 5% of hard cards, 25% longer hard-card waits, or 0.10 alignment in any scenario.

| Rule | Removing it costs (worst scenario) | Verdict |
|---|---|---|
| **G1 Hardest first** (R3) | 14% fewer hard cards; hard-card waits 2.5× longer (tight caps, easy surge) | **Golden** |
| **G2 Promotion by credit and trial cards** (R5) | 83% of value (cold start: nobody climbs) | **Golden** |
| **G3 Demotion, two-speed and batch-judged** (R5) | Alignment −0.14; an overrated model is never moved down | **Golden** |
| **G4 Hard-work reserve for capped models** (R7) | 13% fewer hard cards (tight caps, easy surge) | **Golden** |
| **G5 Fast track for new models** (R5) | 2% of value; hard-card waits 73% longer (cold start) | **Golden** |
| Allowance (R4) | Nothing. It *cost* 6.5% of value under tight caps by throttling good models after normal errors | Dropped |
| Escalation (R6) | Nothing measurable, even with 25% of cards mislabelled: hardest-first already routes stuck cards upward | Optional |
| Velocity standard (R5) | Nothing measurable: credit is counted per card, so faster models already climb sooner | Dropped as a separate rule |

**The five golden rules alone matched or beat all eight in every scenario** (value −0.3% to +6.4%; hard cards −0.3% to +1.7%; markdown rate within ±0.5 points).

**Five allocation rules is the optimum found.** Removing any one of them fails a scenario; adding the other three adds nothing. The governance rules (R8 attribution, R9 markers marked, R10 self-awareness, R12 late marks, R13 no orphan tiers) protect the quality of the marks themselves. The simulation assumes marks are correct, so it cannot test them; they stay in the constitution untested.

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

**Correction to r4.** r3–r4 treated capacity as something to price and optimize centrally. In a pull system this is not needed:

- **Using capacity is simply pulling.** An agent with subscription left keeps pulling. When throttled, it stops. When its window resets, it resumes.
- **Velocity is rewarded, and it is channelled upward.** A fast, accurate agent earns promotion credit fastest (R5), so its speed goes to harder work rather than more easy work.
- **Frontier caps are protected by the hard-work reserve (R7).** A frontier agent may spend below its home tier only the capacity above what 75% of full-speed hard work would need before reset. Hard work is always covered.
- **Nothing perishes needlessly.** Surplus release lets spare capacity flow down as the reset approaches, once hard work is provably covered.

All subscription forms fit without special handling: 5-hour rolling windows, weekly caps, peak-hour reductions, plan multipliers, MiMo's large pool, and Qwen's local GPU slots. Each simply determines when an agent can pull; R7 uses only the agent's own remaining cap and time to reset.

**Human attention.** Isa's touchpoints are fixed by the constitution:
- setting each institution's standards;
- ratifying Alignment Records;
- constitutional amendments;
- governance changes at the Release Gate;
- R13 escalations.

Everything else runs on the rules.

---

### 5.1 The model portfolio: how many, of what tier

**Normalised banding from Artificial Analysis.** Each model's Intelligence Index score is divided by the current frontier score, then banded: ≥95% → tier 5; 85–95% → tier 4; 70–85% → tier 3; 50–70% → tier 2; below 50% → tier 1. The band is the model's **prior**: its starting licence and where it should land. Evidence then moves it.

| Model | AA index (reported) | % of frontier | AA band | Where the rules landed it (cold start) |
|---|---|---|---|---|
| GPT-5.6 Sol | 59 | 100% | 5 | 5 |
| Claude Opus 5.5 | 58 | 98% | 5 | 5 |
| GPT-5.6 Terra | 55 | 93% | 4 | 4 |
| GPT-5.6 Luna | 51 | 86% | 4 | 4 |
| MiMo-V2.6-Pro | 46 | 78% | 3 | 3 |
| Qwen3.8 27B (local) | 34 | 58% | 2 | 2 (1 in some runs: it sits on a band edge) |
| Qwen3 Coder Next (local) | 9 | 15% | 1 | 1 |
| *Hypothetical model the benchmark overrates* | 55 | 93% | 4 | **3**, its true tier, in 12 of 12 runs |

The last row is the point: when the benchmark is wrong about our workload, demotion (G3) finds the model's true tier within 1–8 days. Without it, the model keeps the benchmark's tier indefinitely.

**Portfolio golden rules** (from 431 portfolios, then outage and surge tests; §9.6):

| # | Rule | Evidence |
|---|---|---|
| P1 | **Two top-tier models from two different vendors.** | The even-spread mix had one top-tier vendor. An OpenAI outage pushed hard-card waits from about 6 hours to 22 hours. |
| P2 | **Bulk capacity from at least two independent sources.** | Today's mix relies on one MiMo. A three-day Xiaomi outage left 211 cards waiting; a demand surge left 603. |
| P3 | **At the bottom, fast beats clever.** | Removing local Qwen3.8 (slow reasoning) changed nothing. A fast non-reasoning local model (Coder Next) is worth its slot. |
| P4 | **Size for a surge of about 20%, not the average.** | Portfolios at ~90% load failed the surge test; the recommended mix absorbed it with 4 cards waiting. |
| P5 | **Stop at about five models.** | Seven models (+$160–250 a month) added 0.4% value. |

**Recommended portfolio (C): five models, about $560 a month.**

| Tier | Models | Role |
|---|---|---|
| 5 | GPT-5.6 Sol + Claude Opus 5.5 | Hard work, two vendors (P1) |
| 3 | 2 × MiMo-V2.6-Pro | Bulk capacity (P2) |
| 1 | Qwen3 Coder Next (local) | Fast easy work (P3) |

It has the same cost as today's mix. It meets the service level at nominal and surge demand and through a three-day outage of any single vendor, with the shortest hard-card waits of any mix tested (5.0–5.9 hours). A cheaper option ($470: Opus, Terra, Luna, MiMo, Coder Next) also survives every test, with hard-card waits about one hour longer.

**Sources for the scores** (secondary reports, September 2026; values differ by a few points between sources, and the primary site could not be reached from this environment):
- [BenchLM: AA Intelligence Index leaderboard](https://benchlm.ai/benchmarks/artificialanalysis)
- [Artificial Analysis: model leaderboard](https://artificialanalysis.ai/leaderboards/models)
- [Artificial Analysis: MiMo-V2.6-Pro](https://artificialanalysis.ai/models/mimo-v2-6-pro)
- [Artificial Analysis: Qwen3.8 27B](https://artificialanalysis.ai/models/qwen3-8-27b)
- [Artificial Analysis: Qwen3 Coder Next](https://artificialanalysis.ai/models/qwen3-coder-next)
- [OfficeChai: GPT-5.6 Sol on the Intelligence Index](https://officechai.com/ai/gpt-5-6-sol-places-second-right-behind-claude-fable-on-artificial-analysis-intelligence-index/)
- [eesel AI: MiMo V2.6 pricing](https://www.eesel.ai/blog/xiaomi-mimo-v2-6-pricing)

**Costs are assumptions:** $200 per frontier plan; $100 and $60 for the Terra- and Luna-class plans; $50 per MiMo plan; $120 and $60 a month amortised for the local models. Swap in real invoices before acting.

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
| A strong agent on simple work (P4) | R3: it always takes the hardest card it holds first; R7: capped agents spend only surplus below their home tier. |
| A slow agent holding hard cards | Promotion credit accrues per card, so a slow agent climbs slowly; P1 keeps two top-tier models so one slow model cannot hold up hard work. |
| Cherry-picking easy work (P7) | R3: no choice within a tier. Declines return licences (R10). |
| Card hoarding | Slots are capped by allowance and concurrency. |
| Rubber-stamp or hostile reviewing (P5) | R9: reviewers are marked by Audit in both directions. |
| Bad cards blamed on coders | R8 attribution; R6 returns repeat failures to Planning. |
| Noise making licences flap | Hysteresis and full windows (R5). |
| Wasted retry cycles | Back-off on failed promotions (R5); retry by a different agent (R6). |
| Hard cards starving | R6 escalation; R13 orphan-tier rule. |
| Frontier cap exhausted early | R7 hard-work reserve. |
| Collusion between producer and marker (P6) | Blind review; Audit marks the marker; planted defects. |
| Groupthink (P6) | Commit before view; anonymity; seated dissent. |
| Gaming the markdown rate (P8) | Marks come from a different institution, audited later; late marks count double (R12). |
| Rules edited by the Factory itself (P9) | Rule changes pass the Release Gate and Isa. No change approves itself. |
| Provider silently changes a model | Its record moves; the rules follow the record. |

---

## 9. Evidence from the simulation (synthetic)

**Setup.** One weekly window; four agents with hidden success rates and speeds by tier. MiMo is fast; local Qwen is slow; Qwen starts wrongly licensed for tier 2. Results are the mean over 20 runs. "Value" weights accepted cards 1 / 3 / 8 by tier.

**9.1 Tight frontier caps, easy cards front-loaded.** This is the risk raised in r5.

| Allocation | Hard cards done | Hard cards left | Frontier cap spent on easy cards | Value | Accepted cards |
|---|---|---|---|---|---|
| Static predetermined mapping | 100 | 83 | 16% | 3,293 | 1,607 |
| r5 pacing rule | 148 | 48 | 10% | 3,342 | 1,470 |
| r6 home-tier floor | 176 | 23 | 1% | 3,404 | 1,238 |
| **r7 lean rules (R3 + R5 + reserve)** | **188** | **14** | **1%** | **3,424** | 1,224 |

The lean rules complete 27% more hard cards than pacing and 88% more than the static mapping, leave the fewest behind, and deliver the most value. The cost is visible and intended: easy cards queue for the slower agents instead of consuming scarce frontier capacity. That queue is the signal to add cheap capacity (§3.1, point 10).

**9.2 Generous caps.** The rule costs almost nothing.

| Scenario | Policy | Accepted | Value | Markdowns | Hard cards done | Frontier cap used |
|---|---|---|---|---|---|---|
| Steady arrivals | Static | 1,659 | 3,792 | 226 | 163 | 95% |
| | r5 pacing | 1,654 | 3,816 | 196 | 168 | 97% |
| | **r6 home tier** | 1,628 | 3,805 | 196 | 172 | 98% |
| Easy cards front-loaded | Static | 1,697 | 3,911 | 228 | 175 | 98% |
| | r5 pacing | 1,675 | 3,872 | 194 | 177 | 98% |
| | **r6 home tier** | 1,662 | 3,892 | 201 | 180 | 99% |

**9.3 Normalisation.**
- Qwen's failed tier-2 cards fall by about two-thirds against the static mapping (68 → 24 on steady arrivals).
- An upgrade that makes Qwen **accurate and fast** earns it tier 2 in most runs.
- An upgrade that makes it **accurate but still slow** does not: it stays on easier work, as intended.

**9.4 Capability sort (five tiers, two weeks).** Five models start on an inverted mapping: Claude and GPT licensed only to tier 2, MiMo and Qwen to tier 4. A new model joins on day 2.5, Qwen is upgraded on day 4.6, and Claude is silently degraded on day 8.3. The rules see only accepted, marked down, and cycle time. Mean of 20 runs:

| Rule set | Alignment week 1 | Alignment week 2 | Value | Marked down | Tier 4–5 done | Backlog |
|---|---|---|---|---|---|---|
| Static mapping | −0.67 | −0.81 | 8,322 | 322 | 330 | 168 |
| r6 home-tier floor | +0.79 | +0.62 | 9,099 | 204 | 418 | 214 |
| **r7 lean rules** | **+0.87** | **+0.88** | **9,363** | **204** | **430** | **84** |

Alignment is the rank correlation between true capability and the difficulty of work done (+1 = most capable always on the hardest work).
- The inverted start is sorted within about four days.
- Degraded Claude is moved down to its true tier in 7 of 8 test runs; upgraded Qwen moves up to its true tier in 7 of 8.
- A model close to a tier boundary can settle one tier either side. Twenty-card samples cannot reliably separate 18% from 22% failure.

**9.5 What failed on the way, and became rules.**
- A floor barring capable agents from easier work sorted worse (week-2 alignment +0.62 vs +0.88) and doubled the backlog. Dropped in r7.
- Demotion checked on a rolling window after every card eventually demoted a model well within the standard. Now judged in separate batches, with two strikes for marginal failure.
- New models climbed about one tier per 36 hours. Now fast-tracked until their first failed promotion.
- Protecting 50% of hard-work capacity let frontier agents drift to easy work; protecting 100% left 14% of the cap unused. 75% was best under both tight and generous caps.
- Earlier (r5): halving allowances on every markdown cut output by about a third. Rules now measure against the standard.

**9.6 Model mixes and removals (five tiers, two weeks, golden rules, nominal demand at ~90% load).** Mean of 8–10 runs.

| Mix | $/mo | Value | Hard-card wait | Surge queue | Worst single-vendor outage |
|---|---|---|---|---|---|
| A Today (Sol, Opus, MiMo, local Qwen3.8) | 570 | 8,444 | 5.1 h | 603 (fails) | Xiaomi: 211 waiting (fails) |
| B Cheapest resilient (Opus, Terra, Luna, MiMo, Coder Next) | 470 | 8,405 | 6.1 h | 16 | Anthropic: wait 6.9 h (passes) |
| **C Recommended (Sol, Opus, 2 × MiMo, Coder Next)** | **560** | **8,434** | **5.0 h** | **4** | **Anthropic: wait 5.9 h (passes)** |
| D Best value (7 models) | 720 | 8,466 | 5.2 h | 2 | OpenAI: wait 6.1 h (passes) |
| E Even spread (Sol, Luna, MiMo, Qwen3.8, Coder Next) | 490 | 8,214 | 6.2 h | 477 (fails) | OpenAI: wait 21.9 h (fails) |
| Top-heavy (Sol, Opus, Terra, Luna; no cheap models) | 560 | 7,960 | 5.3 h | 1,725 (fails; 499 waiting even at nominal) | frontier throttled: 1,376 waiting |
| Bottom-heavy (Sol, MiMo, 2 × Qwen3.8, Coder Next) | 550 | 8,094 | 7.9 h | 825 (fails; 42 hard cards left even at nominal) | frontier throttled: wait 19.4 h |

How the rules degrade: when capacity is lost, losses land on easy work first. The reserve and hardest-first keep hard work flowing, and hard work catches up after the outage ends.

## 10. Settled by analysis (not for Isa)

| Question | Settlement |
|---|---|
| Jev or rules | Rules (§2) |
| Subscription terms | Not needed. Pull plus throttling handles them; the hard-work reserve protects frontier caps using only each agent's own cap and time to reset (§5) |
| Keeping frontier capacity for hard work | R7 hard-work reserve, replacing r5 pacing and the r6 floor (§9.1, §9.4) |
| Capable models on hard cards, less capable on easy | R3 hardest-first cascade plus R5 ladder (§9.4) |
| How many allocation rules | Five golden rules; allowance and velocity dropped, escalation optional (§3.2) |
| How many models, of what tier | Five: two tier-5 from two vendors, two bulk mid-tier, one fast local (§5.1) |
| Where models should land | Their Artificial Analysis band as prior; evidence corrects it (§5.1) |
| Slow agents on hard work | Per-card credit plus two top-tier models (P1); the separate velocity standard was dropped in r8 (§3.2) |
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
| X5 | The hard-work reserve (R7) keeps frontier capacity for hard work without idle capacity at reset | Hard-card backlog when a frontier cap runs out, or more than 5% of cap unused at reset |
| X8 | Dropping the velocity standard (r8) does not let slow models hold up hard work on real data | Hard-tier cycle times rise, or a hard tier is left without enough licensed agents |
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
| H1 | Ratify the constitution's eight principles (§6), the five golden allocation rules (§3.2) and governance rules R8–R13 |
| H2 | Set the quality standard per institution and tier (maximum markdown rate). Design can propose starting values. |
| H4 | Approve moving to the recommended portfolio: swap local Qwen3.8 for a second MiMo plan and local Qwen3 Coder Next (§5.1). Check real plan prices first. |
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
- **Tight frontier capacity queues easy work.** This is intended. The fix is cheap capacity, which the per-tier backlog makes visible.
- **Velocity comparisons need enough agents per tier.** With very few agents at a tier, its median cycle time is fragile. Design must set a minimum sample.
- **Low-volume institutions learn slowly.** Inquiry and Council handle few items, so their feedback loops take months to settle. Market and Court settle within days.

---

**Takeaway:** ratify the five golden rules (H1), set quality standards (H2), and move to the five-model portfolio (H4). The simulations show this mix meets the service level through surges and any single-vendor outage at today's cost.
