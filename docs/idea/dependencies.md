# Dependency graphs: the value-stream model re-run (r12.2)

Stage: **IDEA**. Code: [`probes/value-stream/vs_sim.py`](../../probes/value-stream/vs_sim.py) (dependency graph, gates, staleness, interface faults; off by default) and [`probes/value-stream/deps.py`](../../probes/value-stream/deps.py) → `deps_results.txt`, 6 seeds per cell.

All outcomes are synthetic. With the graph off, the model reproduces r12 exactly (institutions with the six: 24.9 clean ideas a week), and a test checks this.

---

## 1. Answer

1. **R17 now rests on our own model, not only on the supplied one.** Building only on reviewed work matches or beats every alternative in every case tested:
   - building on unreviewed work;
   - a whole-idea review barrier;
   - building to the plan's contract;
   - a hybrid with waiting limits.
   The margin grows with coupling. At high coupling, R17 delivers 1.2–1.3× the clean output of building on unreviewed work, and 1.8–1.9× that of the barrier.
2. **The institutions lead every named design in all 6 cases,** and the lead is wider than without dependencies. Peer review delivers 48–67% of the institutions' clean ideas (80% without dependencies), today's Director → Worker → Checker 37–68%, and no organisation 41–64%. A searched design matches or beats the institutions (100–129%) by adding step affinities; it keeps licences, independence and R17.
3. **Elasticity holds.** With dependencies, elastic instances deliver the clean output of 24 fixed seats, within 0–5% in normal work, at 55–59% less cost per clean idea (43% less with mixed work). The exception again is much harder work: elastic delivers 14% fewer clean ideas at 20% higher cost. Six fixed seats cannot absorb growth or surges: 145–226 ideas are left waiting.
4. **Dependencies and family blind spots compound.** At 25% coupling with 18% family blind spots, the institutions with R17 keep the most clean output. A barrier keeps 80% of it, peer review 55%, Director → Worker → Checker 43% and no organisation 23%.

---

## 2. What was added

| Mechanism | Rule in the model | Source |
|---|---|---|
| Dependency graph | Each ordered requirement pair (p < r) is an edge "r needs p" with probability 0.10 / **0.25** / 0.65 | Coupling range from the supplied model |
| Gate: when may a dependent card start? | **R17:** prerequisites reviewed and merged. **Unreviewed:** prerequisites built. **Contract-first:** start at once, building to the plan's interface. **Hybrid:** R17, but build on unreviewed work after 2 h and to the contract after 4 h | Policies to compare |
| Review barrier | Hold all review until every card of the idea is built | The supplied model's "institutions" |
| Staleness | A card built against a prerequisite version that later changes must be rebuilt (invalidation cascade). A card built to the contract is not stale; its risk is the interface fault | Supplied model |
| Interface faults | At each edge a card builds across: 0.10 × (1.25 − 0.5 × pass chance), × 1 / 1.5 / 3 when the builder read reviewed work / unreviewed work / only the contract. Review catches at 0.95 × skill when the upstream work was reviewed, 0.30 × skill when not; CI at 0.30; QA, release and smoke as other defects | Supplied model; multipliers are assumptions, contract ×6 tested |
| Useful output | A requirement counts only if it and all its prerequisites are right | Supplied model's "useful idea-equivalents" |

Clean ideas (live, full intent, no escaped defect) stay the headline measure.

---

## 3. Which gate (D1, D5; institutions)

Clean ideas a week, as a share of R17 in brackets:

| Roster / coupling | R17: reviewed | Unreviewed | Whole-idea barrier | Contract-first (×3) | Hybrid |
|---|---|---|---|---|---|
| The six / 0.10 | 22.8 | 22.6 (99%) | 20.4 (89%) | 18.1 (80%) | – |
| The six / 0.25 | **19.4** | 18.4 (95%) | 15.0 (77%) | 12.4 (64%) | 16.9 (87%) |
| The six / 0.65 | **11.8** | 9.6 (81%) | 6.2 (53%) | 3.8 (32%) | 8.5 (72%) |
| Population 12 / 0.10 | 18.5 | 18.5 (100%) | 15.9 (86%) | 17.6 (95%) | – |
| Population 12 / 0.25 | **13.8** | 13.6 (99%) | 11.4 (82%) | 11.5 (83%) | 13.0 (94%) |
| Population 12 / 0.65 | **6.7** | 5.2 (78%) | 3.8 (57%) | 2.9 (44%) | 4.9 (73%) |

**Why R17 wins:**
- It has the fewest stale rebuilds: 2.3 per idea against 8.5 under the barrier at 0.25 for the six, and 7.9 against 31.1 at 0.65.
- Its interface faults are caught at review, against work that has itself been checked.

**Why building on unreviewed work comes close at low coupling:** with few edges, there is little to invalidate.

**Why the barrier is worst:** it builds everything on unchecked work and then finds faults all at once, so the invalidation cascades are the largest.

**Why contract-first collapses:**
- The contract is never checked against real upstream work until late.
- If a contract-only build breaks interfaces twice as often (×6 instead of ×3), it keeps only 0–13% of R17's output, and change-failure rates reach 45–90%.

**Why the hybrid loses:** a waiting limit converts waiting into rework. Every card built early on unreviewed or contract-only work carries the extra interface risk and invites staleness.

**Rule, unchanged:** R17 with no waiting limit.

---

## 4. Organisations re-run with dependencies (D2, coupling 0.25)

Non-institution designs build on unreviewed work, as they do in practice. The institutions, pools per step and searched designs use R17.

Clean ideas as a share of the institutions':

| Design | The six: base / harder / heavy contention | Population 12: base / harder / heavy contention |
|---|---|---|
| **Institutions** | 100% (19.4) / 100% (7.6) / 100% (18.3) | 100% (13.8) / 100% (3.6) / 100% (12.9) |
| Searched design | 100% / 105% / 102% | 126% / 129% / 121% |
| Pools per step | 79% / 82% / 85% | 40% / 29% / 47% |
| Peer review | 67% / 66% / 63% | 55% / 63% / 48% |
| Functional roles | 56% / 60% / 61% | 55% / 35% / 50% |
| Director → Worker → Checker | 53% / 68% / 56% | 37% / 49% / 38% |
| No organisation | 41% / 49% / 41% | 45% / 64% / 42% |
| Orchestrator | 35% / 43% / 34% | 35% / 68% / 34% |

- **The comparison with r12 (no dependencies):** peer review fell from 80% to 48–67%, and Director → Worker → Checker from 65% to 37–68%. Dependencies punish designs that build on unchecked work or funnel it through one person.
- **The population-12 harder-work shares are ratios of small numbers:** 1–4.7 clean ideas a week.
- **No organisation ships as many ideas as the institutions but few clean ones.** With the six, 20.4 ideas a week go live but only 8.1 are clean, and 41% of deploys cause incidents.

---

## 5. Fixed seats against elastic instances with dependencies (D3, coupling 0.25)

| Demand | Six fixed: clean / p50–p90 lead / $ per clean | 24 fixed | Elastic (rules) |
|---|---|---|---|
| Steady | 18.2 / 46–77 h / $57 | 20.4 / 22–38 h / $66 | **20.1 / 26–45 h / $27** |
| Bursty | 17.4 / 64–107 h / $59 | 19.8 / 22–38 h / $65 | **19.3 / 26–46 h / $27** |
| Growth | 19.4 / 154–318 h / $58, 145 waiting | 38.3 / 23–38 h / $64 | **38.1 / 25–44 h / $28** |
| Mixed | 10.9 / 295–434 h / $106, 70 waiting | 19.3 / 20–104 h / $123 | **18.3 / 23–116 h / $70** |
| Surge | 20.9 / 371–584 h / $56, 226 waiting | 45.1 / 23–39 h / $64 | **43.4 / 26–45 h / $29** |
| Harder | 10.1 / 156–251 h / $115 | 15.4 / 29–79 h / $127 | 13.3 / 42–131 h / $152 |

- **Elastic is slightly slower than 24 fixed seats** (2–4 h at the median) with dependencies.
- **The Scaler starts instances for queued work.** Dependent cards held behind their prerequisites are not in the queue, so they are not seen as demand until they are released.
- **Design note:** the Scaler could count held cards as near-term demand. It is not tested here.

---

## 6. Dependencies with family blind spots (D4; the six; coupling 0.25, blind spots 18%)

| Design | Clean ideas a week | Share of institutions with R17 | Change-failure rate |
|---|---|---|---|
| Institutions, R17 | 14.0 | 100% | 20% |
| Institutions, unreviewed | 12.7 | 91% | 23% |
| Institutions, barrier | 11.2 | 80% | 22% |
| Peer review | 7.7 | 55% | 25% |
| Director → Worker → Checker | 6.0 | 43% | 26% |
| No organisation | 3.3 | 23% | 48% |

---

## 7. What changes

**Idea Record**
- **R17 confirmed in our own model.** "Rests on the supplied model" is withdrawn from the cross-check caveats. No waiting limit: the hybrid was tested and loses.
- **Design notes:**
  - the Scaler should count cards held behind prerequisites as near-term demand;
  - interfaces between requirements should be explicit in the plan, so review can check them against reviewed upstream work.
- **X13 (new):** in the trial, measure coupling (share of requirement pairs with a dependency) and stale rebuilds per idea. R17 is falsified if building on unreviewed work gives more clean output at the measured coupling.

**Assumptions to measure:** the interface-fault multipliers (×1.5 for unreviewed, ×3 for contract-only work) and review's interface catch rate. Contract-first is very sensitive to the first. R17's lead is not: it holds under both ×3 and ×6.
