# Institutional Throughput — Working and Results

Stage: IDEA (analysis to inform design)
Code: [`probes/institutions/`](../../probes/institutions/) · Visual summary: [Factory Throughput Model](https://claude.ai/artifact/KqT8mPfqWx69EobtZ4Ybx3) · Data: [`probes/aa-tiers/aa_coding_2026-09-09.csv`](../../probes/aa-tiers/aa_coding_2026-09-09.csv)

This analysis does not start from the Factory's current models. It starts from the whole Artificial Analysis Coding Index population, staffs each organisation with agents drawn from that population, and simulates work moving through it. The question it answers: how many agents, of which tiers, in which institutions, give the most coherent work through the pipeline, and where does each organisation bottleneck?

---

## 1. What is modelled

### 1.1 Two organisations on the same world

| | Baseline: Director → Worker → Checker | Institutions |
|---|---|---|
| Framing | One Director writes one analysis | **Inquiry:** K agents write independent analyses (commit before view). **Council:** each participant critiques; one synthesis. |
| Planning | Same Director decomposes alone | **Planning:** D agents decompose in parallel; one reconciler; a red team that is not the reconciler |
| Allocation | Director pushes each card to a worker tier by its own estimate of difficulty | Agents **pull**. An agent may take a task only if its expected pass rate clears the licence floor. Cards are taken hardest-first; downstream work first |
| Workers | Dedicated to their queue; a failed card returns to the same worker | Any licensed agent; a failed card goes to a different agent first |
| Review | One Checker reviews every card | **Court:** any licensed agent other than the author |
| Audit | None | **Audit:** 10% of accepted cards, re-checked |
| Release | Director signs off | **Release Gate:** checks for remaining defects and unmapped requirements |
| Human | Ratifies the plan (4 h) | Ratifies framing (4 h) and plan (2 h) |

Both run 24 hours a day for seven weeks. The first week is discarded as warm-up. A work-in-progress limit equal to the headcount keeps a steady queue of ideas. Each result is the mean of four runs with different agents drawn and different random outcomes.

### 1.2 Agents come from the real population

Agents are drawn at random from the 136 current, priced configurations with measured speed, split by the three natural tiers found in [`../../probes/aa-tiers/tiering.py`](../../probes/aa-tiers/tiering.py):

| Tier | Coding Index | Configurations | Share of population |
|---|---|---|---|
| Top | 58–82 | 63 | 46% |
| Middle | 30–57 | 40 | 29% |
| Bottom | 4–29 | 33 | 24% |

Each agent keeps its real Coding Index (skill), blended price (cost) and output speed (time).

### 1.3 The world

**Ideas.** Each idea has R = 8 requirements. Requirement *r* has a difficulty dᵣ ~ Normal(50, 8) in Coding Index points.

**Skill.** An agent with Coding Index *c* succeeds at a task of difficulty *d* with probability

  p(c, d) = 1 / (1 + e^−(0.12 (c − d) + ln 3))

so p = 75% when c = d, and each 10 points of skill adds about 1.2 log-odds.

**Framing.**
- Inquiry participant *i* captures requirement *r* with probability p(cᵢ, dᵣ).
- Each council critic finds a still-missing requirement with probability 0.3 × p(c, dᵣ + 5).
- Because requirements differ in difficulty, easy ones are found by everyone and hard ones are missed by many. Independent views help most on the hard ones.

**Planning.**
- A decomposer maps a captured requirement into cards with probability p(c, dᵣ + 8). The reconciled plan keeps any requirement mapped by any decomposer.
- The red team finds an unmapped requirement with probability p(c, dᵣ + 10).
- Each mapped requirement becomes 1–3 cards.
- A card is ambiguous with probability 0.3 × (1 − p(c_reconciler, 60)). An ambiguous card multiplies the worker's pass rate by 0.6.

**Cards.** Card difficulty is easy (10–30), middle (30–57) or hard (57–75), in proportions 45 / 35 / 20.

**Quality gates.** A card attempt succeeds with probability p(c_worker, d_card). A defective output then passes through four gates:

| Gate | What it does | Probability |
|---|---|---|
| Automated tests | Catch the defect | 50% |
| Review | Catches it | p(c_reviewer, d_card + 5) |
| Audit | Re-checks a sample of accepted cards | 10% sampled; catches with p(c_auditor, d_card) |
| Release Gate | Catches a remaining defect | 50% |
| Release Gate | Notices an unmapped requirement, sending the idea back to Planning (at most twice) | 70% |

Correct work is wrongly rejected 3% of the time.

**What leaves.** An idea is released when all its cards are accepted and the release check passes.
- **Coherence:** the share of its requirements that were mapped and built.
- **Escaped defects:** defective cards that got through every gate.

**Time and cost.** Task time = base hours × √(100 / output speed). The square root reflects that tool and test execution does not speed up with the model. Cost = blended price × task tokens.

**Orphans (constitution R13).** Three deadlocks appeared in development, and all are real:
- a card harder than anyone present;
- an independence rule that cannot be met with too few agents;
- a dedicated seat nobody else may cover.

The rule applied, as the constitution states it:
- after 8 hours, an orphaned card is split into two cards 10 points easier;
- any other orphaned task opens to agents within 10 points of the organisation's best;
- the independence requirement is waived, and the waiver is recorded;
- after 16 hours, seat restrictions are lifted, and that waiver is recorded too.

---

## 2. Assumptions and where they come from

| Assumption | Value | Source | Tested in |
|---|---|---|---|
| Agent skill, price, speed | Per configuration | **Artificial Analysis data** | — |
| Natural tiers | 3 (breaks 29.9, 56.8) | **Statistical analysis of that data** | — |
| Skill curve slope | 0.12 log-odds per point | Assumption | E5: 0.08 and 0.18 |
| Pass rate at equal skill and difficulty | 75% | Assumption | — |
| Requirement difficulty | N(50, 8) | Assumption | E5: +5 |
| Requirements per idea / cards per requirement | 8 / 1–3 | Assumption | — |
| Card difficulty mix | 45 / 35 / 20 | Assumption | E5: 65/25/10 and 25/35/40 |
| Tests catch | 50% of defects | Assumption | E5: 30% and 70% |
| Licence floor | 60% pass (50% for reviewers) | Constitution (earned licence) | — |
| Council, planners, red team, audit | K = 3, D = 2, 1 round, on, 10% | Constitution defaults | E3: all varied |
| Task times and tokens | Tables in `factory_sim.py` | Assumption | — |
| Human ratification | 4 h framing, 2 h plan | Assumption | — |
| Director's error judging card difficulty | ±12 points | Assumption | — |

**What this cannot tell you.** It cannot give absolute throughput for your Factory. Task times and demand are assumed, so read the *ratios, ceilings and bottleneck locations*, not the absolute ideas-per-week. It cannot model correlated blind spots between vendors, human review load, or cards that depend on one another.

---

## 3. Results

All figures are means of four runs. Full output: [`probes/institutions/experiments_output.txt`](../../probes/institutions/experiments_output.txt); raw data: `results.json`.

### 3.1 Headcount: the baseline hits a ceiling, the institutions do not (E1)

Tiers are drawn in the population's proportions (46% top, 29% middle, 24% bottom).

| Agents | Baseline ideas/wk | Baseline busiest role | Institutions ideas/wk | Institutions longest wait | Intent delivered (B → I) | Escaped defects/idea (B → I) | $/idea (B → I) |
|---|---|---|---|---|---|---|---|
| 3 | 7.1 | Top-tier worker, 99% | 7.0 | Planning, 12 h | 91% → 100% | 0.23 → 0.10 | 9.3 → 16.9 |
| 6 | 14.3 | Middle-tier worker, 99% | 21.4 | Planning, 9 h | 91% → 99% | 0.23 → 0.10 | 6.4 → 10.4 |
| 9 | 23.8 | **Checker, 94%** | 33.6 | Planning, 11 h | 90% → 99% | 0.29 → 0.15 | 8.5 → 8.6 |
| 12 | 24.4 | **Checker, 100%** | 42.9 | Council critique, 16 h | 91% → 99% | 0.30 → 0.18 | 8.6 → 10.1 |
| 24 | 24.5 | **Checker, 100%** | 92.0 | Council critique, 21 h | 90% → 99% | 0.29 → 0.22 | 9.5 → 10.4 |
| 32 | 21.9 | **Checker, 100%** | 124.6 | Council critique, 30 h | 90% → 99% | 0.27 → 0.24 | 11.5 → 9.6 |

**Working.**
- **The baseline has a structural ceiling of about 24 ideas a week.** From nine agents onward the single Checker is 94–100% busy. Every extra worker adds queue, not output: lead time rises from 62 to 201 hours. Below nine agents, the bottleneck is whichever worker tier the Director over-assigns, because the Director pushes work by its own estimate of difficulty.
- **The institutions scale linearly: about 3.6–3.9 ideas a week per agent** from four agents upward. There is no single role that every card must pass through.
- **The institutions' bottleneck moves as headcount grows.** Planning is the bottleneck with few agents, because only top-tier agents are licensed for it. From 12 agents, Council critique waits longest. That wait lengthens lead time but does not cap throughput, because downstream work is pulled first.
- **Institutions cost more per idea when small.** Three independent analyses and two planners are overhead. From nine agents the cost is within about 15% of the baseline's, and at 32 agents it is lower ($9.6 against $11.5).

**Drop-offs per idea at 12 agents** (rework loops the work goes through):

| Loop | Baseline | Institutions |
|---|---|---|
| Automated tests fail the card | 4.6 | 2.9 |
| Review rejects the card | 4.1 | 2.3 |
| Release Gate finds a remaining defect | none: shipped | 0.29 |
| Release Gate finds a missing requirement (back to Planning) | none: shipped | 0.25 |
| **Total rework** | **8.7** | **5.8** |

Hardest-first pulling and licences put capable agents on hard cards, so less work fails in the first place. The institutions' extra loops catch problems the baseline ships.

### 3.2 Tier mix (E2)

Every mix of top/middle/bottom agents at 6, 9 and 12 agents. Quality floor: at least 97% of intent delivered and at most 0.25 escaped defects per idea.

| 12 agents | Top/mid/bottom | Ideas/wk | Lead h | Intent | Escaped/idea | $/idea |
|---|---|---|---|---|---|---|
| All top | 12/0/0 | **51.9** | 36 | 100% | 0.07 | 14.7 |
| **Cheapest within 90% of best** | **5/7/0** | **47.3** | — | ≥97% | ≤0.25 | **8.4** |
| Population mix | 6/3/3 | 42.9 | 56 | 99% | 0.18 | 10.1 |
| Cheapest per idea overall | 4/7/1 | 41.2 | 57 | 99% | 0.18 | 8.1 |
| All middle | 0/12/0 | 20.2 | 111 | 98% | **0.42 (fails)** | 8.2 |
| All bottom | 0/0/12 | 0.7 | 228 | 92% | 0.91 (fails) | 42.9 |

The same pattern holds at 6 agents (cheapest within 90% of best: 4/1/1) and at 9 (4/5/0).

**Working.**
- **Top-tier agents maximise throughput**, because they pass hard cards first time and are licensed for every institution.
- **Middle-tier agents are the cost lever.** Replacing top with middle agents up to about 55–60% of seats cuts cost per idea by about 40% for a 9% loss of throughput.
- **At least one top-tier agent is needed at every size.** Without one, hard cards and planning cannot meet the quality floor. An all-middle team lets 0.42 defects per idea escape, because it cannot review hard cards reliably.
- **Bottom-tier agents are close to worthless in this pipeline.** They are licensed only for easy cards, and those are already absorbed by capable agents pulling hardest-first. In the population they are a quarter of the models; in the ideal Factory they are 0–1 seats.

### 3.3 Institution sizing (E3; 12 agents, population mix)

| Setting | Ideas/wk | Lead h | Intent | Escaped/idea | $/idea | Reading |
|---|---|---|---|---|---|---|
| Inquiry K=1 | 44.4 | 66 | 98.6% | 0.15 | 9.6 | |
| **Inquiry K=2** | 43.6 | 59 | 99.1% | 0.17 | 9.9 | Most of the coherence gain |
| Inquiry K=3 | 42.9 | 56 | 99.4% | 0.18 | 10.1 | |
| Inquiry K=5 | 42.2 | 53 | 99.6% | 0.20 | 10.3 | Diminishing returns |
| **Planners D=1** | 45.4 | 52 | 98.9% | 0.19 | 9.7 | Red team covers most gaps |
| Planners D=2 | 42.9 | 56 | 99.4% | 0.18 | 10.1 | |
| Planners D=3 | 40.7 | 58 | 99.2% | 0.19 | 10.6 | No gain |
| Council rounds 0 | 45.3 | 59 | 98.6% | 0.16 | 9.6 | |
| **Council rounds 1** | 42.9 | 56 | 99.4% | 0.18 | 10.1 | |
| Council rounds 2 | 40.7 | 54 | 99.6% | 0.18 | 10.6 | |
| **No red team** | 45.2 | **73** | **97.2%** | 0.15 | 9.6 | Biggest single coherence lever; also cuts gap loops |
| No audit | 44.8 | 55 | 99.2% | 0.20 | 9.7 | Small effect at 10% sampling |
| **WIP limit 4** | 35.0 | **24** | 99.6% | 0.21 | 10.1 | Short lead, low throughput |
| **WIP limit 8** | 42.3 | 39 | 99.1% | 0.18 | 10.0 | Best balance |
| WIP limit 12 | 42.9 | 56 | 99.4% | 0.18 | 10.1 | |
| WIP limit 24 | 41.0 | 102 | 99.2% | 0.19 | 10.7 | More WIP only adds waiting |

**Working.**
- **Each deliberation step trades about 5% throughput for 0.5–1 point of intent coherence.** Two Inquiry participants, one Council round and one red team capture most of the gain.
- **The red team is worth more than a second planner.** Removing it drops coherence by 2.2 points and adds 17 hours of lead time through release-gate loops.
- **The WIP limit behaves as Little's law predicts.** Throughput saturates at a WIP of about 0.7 × headcount; beyond that, extra ideas in progress only lengthen lead time.

### 3.4 Shared pool vs dedicated seats (E4; 12 agents)

| Organisation | Ideas/wk | Lead h | Intent | Escaped/idea | Utilisation |
|---|---|---|---|---|---|
| **Shared pool (agents pull any licensed work)** | **42.9** | **56** | 99.4% | 0.18 | **84%** |
| Dedicated: 1 inquiry, 1 council, 2 planning, 6 market, 1 court, 1 release | 23.5 | 73 | 99.4% | 0.11 | 51% |
| Dedicated: 2/1/2/4/2/1 | 28.5 | 63 | 99.4% | 0.10 | 59% |
| Dedicated: 1/1/1/7/1/1 | 23.0 | 78 | 99.6% | 0.11 | 49% |

**Working.**
- **Dedicated seats lose 34–46% of throughput.** A seat idles while work queues at another institution; utilisation falls from 84% to about 50%.
- **Their one gain is fewer escaped defects,** because review is fixed to top-tier agents.
- **The first run of this experiment deadlocked.** The Release seat went to an agent not licensed to release, and seat rules forbade anyone else. Seats need the orphan rule (R13) to lift seat restrictions too; the model now does this after 16 hours and records a waiver.

### 3.5 Sensitivity (E5; 12 agents)

| Assumption changed | Baseline ideas/wk | Institutions ideas/wk | Ratio | Intent (B → I) | Escaped (B → I) | Best 12-agent mix |
|---|---|---|---|---|---|---|
| None | 24.4 | 42.9 | 1.76× | 91% → 99% | 0.30 → 0.18 | 12/0/0 |
| Flatter skill curve (0.08) | 27.8 | 44.4 | 1.60× | 86% → 99% | 0.25 → 0.21 | 12/0/0 |
| Steeper skill curve (0.18) | 22.2 | 43.1 | 1.94× | 94% → 99% | 0.29 → 0.13 | 8/4/0 |
| Weak tests (30%) | 23.9 | 43.2 | 1.80× | 90% → 99% | 0.33 → 0.23 | 12/0/0 |
| Strong tests (70%) | 26.1 | 43.8 | 1.68× | 90% → 99% | 0.19 → 0.12 | 12/0/0 |
| Easy-heavy work (65/25/10) | 32.6 | 59.7 | 1.83× | 90% → 99% | 0.15 → 0.14 | 8/4/0 |
| Hard-heavy work (25/35/40) | 17.1 | 28.3 | 1.66× | 92% → 99% | 0.57 → 0.22 | 12/0/0 |
| Harder requirements (+5) | 26.3 | 43.0 | 1.63× | 85% → 99% | 0.26 → 0.19 | 8/4/0 |

**Working.** Under every assumption set:
- the baseline's bottleneck is the Checker;
- the institutions deliver 1.6–1.9× the throughput;
- intent coherence rises to 99%;
- fewer defects escape.

The throughput-maximising mix is always top-heavy with no bottom tier. With easier work or a steeper skill curve it shifts to about two-thirds top and one-third middle.

---

## 4. The ideal numbers

These follow from the working above. Absolute ideas per week rest on assumed task times; the ratios and proportions do not.

| Question | Answer | Evidence |
|---|---|---|
| How many agents? | **About one agent per 3.7 ideas a week** of demand, plus headroom for surges | Throughput is linear at 3.6–3.9 ideas/wk per agent from 4 agents (§3.1) |
| Minimum team | **4 agents** | At three agents the institutions only match the baseline (7.0 vs 7.1) at almost twice the cost per idea; at four they already beat it (14.3 vs 11.0) |
| Tier mix | **About 40–45% top tier, the rest middle tier, bottom tier 0–1 seat** | Cheapest within 90% of maximum throughput at 6, 9 and 12 agents: 4/1/1, 4/5/0, 5/7/0 (§3.2) |
| For maximum throughput or hard-heavy work | **All or nearly all top tier** | 12/0/0 is best in five of eight assumption sets; 8/4/0 in the other three (§3.5) |
| Never | **Zero top-tier agents** | No mix without a top-tier agent meets the quality floor |
| Inquiry participants | **2** (3 for high-stakes ideas) | §3.3 |
| Planners | **1 plus a red team** | The red team beats a second planner (§3.3) |
| Council rounds | **1** | §3.3 |
| Audit sampling | **About 10%**; its value is calibration, not throughput | §3.3 |
| Work in progress | **About 0.7 × headcount** | Little's law behaviour (§3.3) |
| Organisation | **Shared pool; agents pull any work they are licensed for** | Dedicated seats lose 34–46% (§3.4) |
| Baseline Director–Worker–Checker | **Capped at one Checker's capacity** | About 24 ideas/wk here, whatever the headcount (§3.1) |

---

## 5. What this changes in the Idea Record

1. The Director → Worker → Checker bottleneck is structural: a single mandatory role. The institutions remove it because Court work is pulled by any licensed agent.
2. The bottom tier of the market has almost no place in a pull-based Factory. Portfolio rules should target top and middle tiers.
3. R13 (no orphans) is load-bearing, not a corner case. It must relax licences, independence and seat rules, each with a Ledger record, or small teams deadlock.
4. Deliberation (Inquiry, Council, red team) costs about 5% throughput per step and buys intent coherence. Two analysts, one council round and a red team is the efficient point.

