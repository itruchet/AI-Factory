# Institutional Throughput — Working and Results

Stage: IDEA (analysis to inform design)
Code: [`probes/institutions/`](../../probes/institutions/) · Data: [`probes/aa-tiers/aa_coding_2026-09-09.csv`](../../probes/aa-tiers/aa_coding_2026-09-09.csv)

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

**Orphans (constitution R13).** Two deadlocks appeared in the first runs, and both are real:
- a card harder than anyone present;
- an independence rule that cannot be met with too few agents.

The rule applied, as the constitution states it:
- after 8 hours, an orphaned card is split into two cards 10 points easier;
- any other orphaned task opens to agents within 10 points of the organisation's best;
- the independence requirement is waived, and the waiver is recorded.

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

RESULTS_PLACEHOLDER
