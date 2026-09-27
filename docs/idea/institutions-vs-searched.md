# Institutions or the searched design? (r12.3)

Stage: **IDEA**. Probe: [`probes/value-stream/searched.py`](../../probes/value-stream/searched.py) → `searched_results.txt`. 8 seeds per cell; elastic runs use 6.

All outcomes are synthetic.

---

## 1. The question

In the value-stream comparison ([`value-stream.md`](value-stream.md) §3.1), the searched design beat the institutions on most headline measures:

| | Worst | Mean | Best | Change-failure rate (the six) | $ per clean idea (the six) |
|---|---|---|---|---|---|
| Institutions | 100% | 100% | 100% | 11% | $42 |
| Searched design | 95% | 107% | 120% | 9% | $40 |

Why keep the institutions? This note tests the searched design on six questions its search never asked, then states the logic, the trade-offs, and when to prefer each.

---

## 2. What the searched design is

It is **not a different organisation.** It is the institutions, with the same licences, independence rules and optional steps, plus a few **step affinities**: some steps reserved for some pools of models.

A coordinate search found these affinities by maximising clean ideas on one roster, in the base scenario, on four random draws.

| Tuned on | Affinities found |
|---|---|
| The six | Design by fast and mid models only (keeps the anchor free for hard cards); audit by fast models |
| 12 models from the AA population | Planning by the two strongest models only; discovery and security review by fast top-tier models; challenge and acceptance test by anchor and fast; review and audit by fast and mid; merge by mid models |

**Where its advantage comes from:**
- It keeps the strongest models on the steps whose output shapes a whole idea: planning, security, acceptance.
- It keeps the weakest models off those steps.
- It moves low-skill steps, such as merging, onto cheap models.

That cuts defects at the source (lower change-failure rate) and rework (lower cost). The gain is **largest where the roster is uneven**. With the six, all models are strong and there is little to sort.

---

## 3. What the search did not test (`searched_results.txt`)

Four organisations were compared:
- the institutions;
- each searched design;
- **adaptive institutions:** the institutions with one rule added, stated before running. Steps whose output shapes a whole idea (design, plan, plan red-team, security review, acceptance test, release) need a pass chance of at least 0.8 instead of 0.6. It uses the same evidence as every licence, so it re-sorts itself when models change, and it has no pools to maintain.

### 3.1 Out of sample: new random draws (and, for the population, new rosters)

Clean ideas a week as a share of the institutions on the same draws.

**The six:**

| | Searched (six) | Searched (population 12) | Adaptive institutions |
|---|---|---|---|
| In-sample: the search's own draws, base scenario | 104% | 98% | 101% |
| Out of sample: five scenarios, no dependencies | 96–103% | 99–113% | 98–105% |
| Out of sample: five scenarios, 25% coupling | 98–103% | 97–111% | 99–110% |

**Population 12:**

| | Searched (six) | Searched (population 12) | Adaptive institutions |
|---|---|---|---|
| In-sample: base, no dependencies / 25% coupling | 96% / 102% | **116% / 126%** | 96% / 113% |
| Out of sample: five scenarios, no dependencies | 95–107% | **110–125%** | 103–139% |
| Out of sample: five scenarios, 25% coupling | 96–104% | **105–131%** | 111–127% |

**Reading:**
- **The six-tuned design was over-fitted.** Its 4% in-sample edge disappears on new draws (96–103%). It also does not transfer to the population (95–107%).
- **The population-tuned design generalises.** It holds 105–131% on rosters it never saw, because its affinities follow a general principle: the strongest models plan, the cheapest merge. It even helps the six on harder work (111–113%).
- **The adaptive rule wins on hard work.** On the population it delivers 127–139% on harder work, against 105–125% for the population-tuned design, whose change-failure rate rises to 34% there.
- **On the population's other scenarios, the searched design is ahead by 3–14 points.** The adaptive rule captures 19–77% of its gain (about half, at the median).

### 3.2 A vendor outage: the anchor models are unavailable

The pools are not re-labelled. That is the point: someone would have to notice and re-tune.

| | Institutions | Searched (six) | Searched (population 12) | Adaptive |
|---|---|---|---|---|
| The six, Opus unavailable | 100% | 98% | **65%** | 101% |
| Population 12, top two unavailable | 100% | 93% | **97%** (from 113%) | **110%** (unchanged) |

- **A step reserved for a pool that is down has nobody permitted to do it.** R13 lifts the seat rule after 16 hours; until then, planning waits.
- The population-tuned design loses its whole advantage in an outage. On the six it loses a third of its output.
- **The adaptive rule keeps its advantage,** because it asks "who clears 0.8 on this task now?", not "who holds the label?".

### 3.3 A new, stronger model enters (Claude Fable 5.1, not yet labelled)

| Population 12 | Before | After Fable joins | Gain |
|---|---|---|---|
| Institutions | 18.8 | 23.8 | **+27%** |
| Adaptive institutions | 20.7 | 24.8 | +20% |
| Searched (population 12) | 21.1 | 25.9 | +23% |
| Searched (six) | 18.5 | 22.1 | +19% |

- **The institutions gain most from a better model.** Licences admit it to every step it clears, at once.
- **A searched design cannot use it on reserved steps** until someone assigns its pool.
- In a market that changes monthly (rules P6 and P7), that lag recurs.

### 3.4 Elastic capacity (the six models as instances, with the Scaler)

| Demand | Institutions | Searched (six) | Adaptive |
|---|---|---|---|
| Steady | 19.1 clean, $20 | 108%, $19 | 102%, $21 |
| Mixed | 19.6 clean, $30 | 95%, $36 | 105%, $35 |
| Harder | 14.6 clean, $88 | 102%, $90 | 99%, $90 |
| Surge | 47.6 clean, $22 | 99%, $21 | 97%, $22 |

**Within noise** (95–108%). With elastic capacity, the Scaler already sends each task to the cheapest model that clears the quality floor. That is a step affinity computed from evidence every 15 minutes, so fixed pools add nothing.

---

## 4. The logic

**Why the institutions, not the searched design, are the constitution:**

1. **The searched design is a configuration of the institutions, not an alternative to them.** It keeps every institutional rule, and the search itself kept licences, independence and every optional step in every run. It only adds reserved steps.
2. **Its advantage depends on the roster it was tuned for.** Where that roster is stable and uneven, the advantage is real (population: 105–131% out of sample). Where models are all strong, it is noise (the six: 96–103%).
3. **Fixed labels are brittle.** An outage of the labelled models removes the advantage or worse (65%). A new model is shut out of reserved steps until someone re-tunes. Both events are routine under the rolling-market policy.
4. **Someone has to re-run the search and re-label.** That is a central allocator by another name, the thing principle 1 rules out ("no central intelligent router"). The institutions re-sort themselves from evidence.
5. **With elastic capacity, the advantage disappears.** The Scaler's evidence-based routing does the same job continuously.
6. **Most of the gain can be had by rule.** Higher licence floors on the high-impact steps keep:
   - a lower change-failure rate (10% vs 12% with the six; equal or up to 6 points lower in 9 of 10 population cells);
   - the lower cost per clean idea ($41 vs $43).
   It survives outages and entries, and it wins on hard work. It gives up 3–14 points to the tuned design on that design's own roster type in normal work.

**Trade-offs, summarised:**

| | Institutions | Adaptive institutions (R19) | Searched design |
|---|---|---|---|
| Clean output, strong roster | 100% | 98–110% | 96–103% (six-tuned) |
| Clean output, uneven roster | 100% | 103–139% | 105–131% (population-tuned) |
| Harder work, uneven roster | 100% | **127–139%** | 105–125% |
| Anchor outage | 100% | **101–110%** | 65–97% |
| New model enters | **+27%** | +20% | +19% to +23% |
| Elastic capacity | 100% | 97–105% | 95–108% |
| Change-failure rate | baseline | equal or up to 6 points lower (9 of 10 population cells) | 6 points lower to 6 points higher (higher on hard work) |
| Maintenance | none | none (evidence) | re-search and re-label on every roster change |
| Consistent with "no central router" | yes | yes | only if the search is itself a rule |

---

## 5. When to favour which

- **Default, and the constitution: the institutions with R19 (adaptive floors).**
- **With elastic capacity (the trial's plan): the same.** Pools add nothing because the Scaler routes by evidence.
- **Fixed seats, a stable roster with uneven models, and nobody available to re-label: the searched design gains 3–14 points.** Adopt it only under R20:
  - it runs as a trial configuration;
  - it is compared with the institutions on the same work;
  - it lapses automatically when the roster changes or an outage empties a pool.
- **Never a design tuned on one roster applied to another.** The six-tuned design does not transfer, and the population-tuned one collapses on the six in an outage.

---

## 6. Rules added (Idea Record r12.3)

- **R19, high-impact licence floors.** Design, plan, plan red-team, security review, acceptance test and release require a pass chance of at least 0.8 (other steps 0.6; review 0.5). They are set from the same evidence as every licence.
- **R20, configurations are proposals.** The Ledger may propose step affinities, found by search over its own records, as a trial configuration:
  - it is compared with the institutions on the same work;
  - it is adopted only on evidence;
  - it lapses automatically when the roster changes or a reserved pool is empty.
  The constitution itself never reserves steps for named models.
