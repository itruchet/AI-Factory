# Cross-check with a second simulation (r12.1)

Stage: **IDEA**. This note compares our value-stream model with an independent simulation Isa supplied, built with another assistant. Each model was run with the other's mechanisms. All outcomes are synthetic in both.

| | Location |
|---|---|
| Supplied simulation (unchanged) | [`probes/crosscheck/external/`](../../probes/crosscheck/external/): code, README, summary results, figure |
| Our rules inside it | [`probes/crosscheck/our_rules_in_their_sim.py`](../../probes/crosscheck/our_rules_in_their_sim.py) → `our_rules_in_their_sim_results.txt` |
| Its mechanisms inside ours | [`probes/value-stream/crosscheck.py`](../../probes/value-stream/crosscheck.py) → `crosscheck_results.txt` |

---

## 1. Answer

1. **The two simulations agree once their definitions are aligned.**
   - Their "institutions" differs from ours in two ways our constitution does not require:
     - card review waits until the whole idea is built;
     - any agent claims any task, first come first served, with no evidence licences.
   - Their better design, the **evidence graph**, is close to our institutions plus one scheduling rule: a card that depends on another starts only after that card has passed review.
   - Their own conclusion matches ours: persistent institutional rules, elastic stateless invocations, work-conserving leases, SQL state, no controlling agent.
2. **Our evidence licences are the largest single quality lever in their model as well.** Added to their designs they:
   - raise useful output by 6–29% (institutions) and 5–22% (evidence graph);
   - cut escaped defects by 6–65%.
   - With no family blind spots, licences alone make their institutions pass the original quality floors.
3. **Adopt three rules from the cross-check:**
   - **R17, evidence-gated dependencies:** build on reviewed work only; review each card as it lands.
   - **R18, family independence:** no model checks work by its own family.
   - **R14 amended:** the Scaler aims to clear queued work within 15 minutes (work-conserving).
4. **The residual risk is blind spots shared by every model family.** No amount of model independence fixes them. At 18%, every design loses 78–80% of its clean output in our model. Deterministic evidence (tests, CI, typed contracts) and human-ratified acceptance criteria are the only defence. Measure the rate in the trial (X11).
5. **Packets (several requirements in one model call) are a boundary condition in both models.** Keep one requirement per invocation until measured interface costs say otherwise.

---

## 2. How the two models differ

| | Our value-stream model | Supplied model |
|---|---|---|
| Skill vs work | Real AA Coding Index 50–82 against cards 10–75 | Tiers 72 / 56 / 38 against difficulty 40 / 56 / 72: a harder world |
| Dependencies | None between requirements | Random graph (25% of pairs); upstream errors invalidate dependants; interface errors at edges |
| "Institutions" | Pull with evidence licences; each card reviewed as built | Whole-idea build barrier before review; first-come claims, no licences |
| Correlated error | Same-model check at 0.5×; (r12.1) family and all-family blind spots | Family blind spot per requirement (18%): pass/catch ×0.4 at every stage |
| Capacity | Elastic Scaler with quality floor, cost-band pull and burn cap; API cost | Fixed / full pool / queue / work-predictive controllers; illustrative prices |
| Metric | Clean ideas (live, full intent, no escaped defect), change-failure rate | Useful idea-equivalents (correct requirements with correct prerequisites), floors |
| Live operation | Incidents, restore, hotfix | Not modelled |
| State | Implicit | SQL, stateless invocations, keyed randomness, paired seeds |

**What each model contributes:**
- The supplied model adds dependency graphs, invalidation cascades, family blind spots, packets, a stateless SQL design and paired-seed statistics.
- Ours adds real market data, evidence licences, cost routing, live operation and budget.

---

## 3. Our rules inside the supplied model (`our_rules_in_their_sim_results.txt`)

24 paired seeds, 32 ideas, 95% intervals. Useful idea-equivalents a week; change vs their institutions; escaped defects per release; floors are intent ≥ 97% and escaped defects ≤ 0.25.

| Mix 6/3/3, reference (18% family blind spots) | Useful / week | vs their institutions | Escaped defects | Floors |
|---|---|---|---|---|
| Their institutions (barrier, first-come) | 208 ± 12 | – | 0.80 | no |
| Their evidence graph (first-come) | 256 ± 13 | +25% ± 8% | 0.83 | no |
| Institutions + streaming review | 234 ± 15 | +15% ± 10% | 0.90 | no |
| Institutions + licences | 248 ± 15 | +21% ± 8% | 0.53 | no |
| Institutions + streaming + licences | 279 ± 13 | +36% ± 9% | 0.48 | no |
| … + family review | 271 ± 16 | +32% ± 8% | 0.40 | no |
| Evidence graph + licences | **311 ± 14** | **+52% ± 10%** | 0.46 | no |
| Evidence graph + licences + family review | 304 ± 13 | +49% ± 11% | **0.36** | no |

**Across the other cases** (full table in the results file):

- **Mix 10/2/0, reference:** evidence graph + licences + family review reaches 397 a week, with escaped defects 0.24 and intent 0.983. It **passes the floors**, the first configuration to do so at the reference blind-spot rate in this model. Its own report found none among its shortlisted mixes.
- **Mix 4/7/1, reference:**
  - Licences add 17–37%.
  - Family review cuts defects to 0.30–0.37, but costs throughput: with a middle-heavy mix few families can review.
- **No family blind spots:** institutions + licences passes the floors (defects 0.22). Every licensed design passes; no unlicensed design does.
- **Correlated errors (45%):** licences still add 27–57%, but no design comes near the floors. This is §4's residual risk.

**Reading:**
- **Their barrier costs about 6–17%** (institutions + streaming review).
- **Their first-come claiming costs more:** licences move the most defects.
- **Building only on reviewed work adds a further 6–12%** (evidence graph + licences vs institutions + streaming + licences).
- **Family review trades a little throughput for fewer escaped defects.**

---

## 4. Their mechanisms inside our model (`crosscheck_results.txt`, the six, 6 seeds)

### C1: Blind spots shared within a model family

Each requirement × family pair is blind with probability b; that family's pass and catch chances are ×0.4.

Clean ideas a week, and as a share of what each design delivers at b = 0:

| b | Institutions | Peer | Director-Worker-Checker | No organisation | Institutions, 24 seats |
|---|---|---|---|---|---|
| 0% | 25.0 | 19.5 | 16.4 | 14.8 | 98.1 |
| 5% | 23.4 (94%) | 17.7 (91%) | 14.5 (89%) | 11.1 (75%) | 90.6 (92%) |
| 18% | 19.2 (77%) | 12.6 (65%) | 10.5 (64%) | 5.4 (37%) | 75.9 (77%) |
| 45% | 10.7 (43%) | 4.8 (25%) | 4.1 (25%) | 1.1 (8%) | 42.8 (44%) |

**Findings:**
- **The institutions' advantage grows with shared mistakes:** 1.7× no organisation at b = 0, 3.6× at 18%, 9.7× at 45%.
- **More seats of the same models scale output but do not remove shared mistakes.** Clean output per seat and change-failure rate are unchanged at 12 or 24 seats, which reproduces their "more agents do not remove shared mistakes".
- **Barring same-family review changes nothing for the six**, because the six are six vendors. It matters for the seven-model menu, where OpenAI has two models (R18).

### C2: Blind spots shared by every family

No LLM check can see the defect or requirement; tests, CI and smoke tests still can.

| b | Institutions | Peer | Director-Worker-Checker | No organisation |
|---|---|---|---|---|
| 0% | 25.0 | 19.5 | 16.4 | 14.8 |
| 5% | 15.6 (−38%) | 12.5 | 10.2 | 9.2 |
| 18% | 5.4 (−78%), intent 0.82 | 3.9 | 3.6 | 3.3 |

**No organisation of models fixes this.** Only checks outside the model families do: deterministic tests, CI, typed contracts, and people who ratify the acceptance criteria.

### C3: Packets (institutions)

Clean ideas a week:

| Requirements per invocation | No context penalty | Their penalty 2.5 × (k − 1)^1.2 |
|---|---|---|
| Unit cards (r12) | 25.0 (CFR 11%) | 25.0 |
| 1 | **26.2** (CFR 7%) | **26.2** |
| 2 | 22.8 | 21.3 |
| 4 | 19.0 | 7.9 |
| 8 | 13.8 (CFR 5%) | 10.6 |

**Our model:**
- Bigger packets lose output even with no penalty. The whole packet is redone when any part fails, and parallelism falls.
- Fewer interfaces do lower the change-failure rate.

**Their model:** fusing all eight requirements wins without a penalty, but only under dense dependencies, where their interface errors are costly.

**Both say the same thing: measure it.** Until then, one requirement per invocation: slightly better than unit cards, and the safest.

### C4: Scaler aggressiveness (target time to clear queued work)

| Target drain | Bursty: clean / p90 lead | Surge | Mixed |
|---|---|---|---|
| 0.1 h | 17.1 / 25 h | 47.7 / 24 h | 19.9 / 37 h |
| 0.25 h | 19.9 / 25 h | 47.6 / 25 h | 19.6 / 33 h |
| 2 h (r12 default) | 19.3 / 27 h | 46.8 / 25 h | 19.9 / 35 h |

**Within noise in our model.** Their model found a conservative predictor loses 20–50%. Aiming to clear the queue within 15 minutes costs nothing under API pricing (idle instances cost nothing) and protects against a poor predictor, so **R14 adopts 0.25 h**.

---

## 5. Changes to the Idea Record (r12.1)

- **R17, evidence-gated dependencies.** Review each card as it is built; there is no whole-idea barrier. A card that depends on another becomes available only when its prerequisite has passed review. A rework invalidates only the dependants whose inputs changed. The Ledger records the artifact versions each card read.
- **R18, family independence.** No model reviews, audits or releases work by a model of its own family (vendor). This extends "instances of one model are one model" to sibling models. If no other family is available, the waiver is recorded (R13).
- **R14 amended.** The Scaler is work-conserving: it aims to clear queued work within 15 minutes, within rate limits and the burn cap.
- **Packets.** One requirement per build invocation (a requirement's cards together). Fuse more only when trial data show interface errors cost more than whole-packet rework.
- **Evidence outside the model families.** Tests, CI and typed contracts are first-class evidence at review and release, not an optional check. Acceptance criteria are ratified by a person (§5.5).
- **New experiments:**
  - **X11:** measure the blind-spot rates in the trial. For each escaped defect, did any model flag it? Did any model of another family?
  - **X12:** measure interface-error cost against packet size.
- **Design question:** SQL as the canonical operational state, with stateless invocations reloading a versioned snapshot, as the supplied model assumes. This is consistent with the Ledger; Git stays the artifact authority.

**Unchanged:** the recommendation of r12:
- institutions;
- the elastic Scaler;
- the seven-model menu on API tokens;
- the burn cap.

The cross-check sharpens the institutions' scheduling rules; it does not replace them.

---

## 6. Caveats

- **Two synthetic models agreeing is not evidence about the real Factory.** It shows the conclusions survive a second set of assumptions written by a different author.
- **The supplied model's prices and tiers are illustrative, not AA data,** so its cost figures are not comparable with ours.
- **Licences in the supplied model are approximated** by the track record a Ledger would hold: tier skill against visible difficulty, with blind spots invisible. Real licences come from marks earned over time.
- **Our model now has the blind-spot mechanisms, but not dependency graphs.** The evidence-graph result rests on the supplied model. R17 should be tested again when the trial provides real dependency data.
