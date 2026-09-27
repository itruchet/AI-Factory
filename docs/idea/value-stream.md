# Idea to live: organisations, elasticity and budget (r12)

Stage: **IDEA**. Market: Artificial Analysis snapshot of 27 Sep 2026.

**Probes**
- [`probes/value-stream/`](../../probes/value-stream/) (new):
  - `vs_sim.py`: the step model and the Scaler;
  - `orgs.py`: organisations compared, plus a search for a new one;
  - `elastic.py`: fixed seats against elastic instances, budget caps, model menus and scale.
- [`probes/portfolio6/`](../../probes/portfolio6/): the r11 probes, re-run, plus `token_invariance.py` and `whatif_mimo.py`.
- [`probes/institutions/operating_models.py`](../../probes/institutions/operating_models.py): the same comparison on the r10 task model.

All outcomes are synthetic. They rank designs; they do not forecast the Factory. `*` marks a Coding Index estimated from AA's Intelligence Index.

---

## 1. Answer

1. **Organisation: keep the institutions.** The analysis now runs on every real step from idea to live:
   - Institutions produce the most clean ideas of every named design in all 10 roster and scenario cases.
   - No organisation (each agent does everything alone) delivers 44–61% of that. Peer review delivers 49–83%, and the current Director → Worker → Checker 46–79%.
   - A search for a new organisation lands on the institutions again, plus a few step affinities.
   - The rules that carry the result are evidence licences and independence.
2. **Capacity: elastic, not six seats.** The six are a **menu of models**. Plain Ledger rules, with no agent involved, start and stop instances of them at each step as work arrives. Against six fixed seats:
   - Median lead time stays at 18–19 h under every demand pattern, while fixed seats reach 30–327 h.
   - Growth and surges are absorbed: 40–49 clean ideas a week against 26–28.
   - Cost per clean idea falls by half in normal work ($19–23 against $40–43).
   - One exception: when the work is much harder, elastic is faster but about 27% dearer.
3. **Budget: spend follows demand; cap the burn rate, not the seats.**
   - About $20 per clean idea at the base token model, so 25 ideas a week is about $1,700 a month.
   - A burn cap of about **2× the trailing average** lost nothing in any test. A cap below the average burn let backlogs explode.
   - Scale is efficient up to about **100 ideas a week**. Beyond that, merge contention and vendor rate limits push the marginal cost of an extra clean idea to 2–4× the cost at 25–50 ideas a week.
4. **The menu:**
   - **Anchors:** Claude Opus 5.5\* and GPT-5.6 Terra, from two vendors, for the hardest work.
   - **Fast top tier:** Muse Spark 1.3 and Gemini 3.8 Flash.
   - **Mid:** DeepSeek V4.1 Flash\*, GPT-6 Luna\* and Ling 3.0 Flash.
   - Opus and Terra are a genuine near-tie. Holding both costs nothing unless used, gives the most clean output on hard work, and meets rule P1 (two top-tier vendors).
5. **Tokens only.** Elastic capacity needs 30–48 concurrent instances at peak, which a subscription cannot supply.

**Your points, answered**
- **Muse Spark:** API access confirmed (§7).
- **MiMo:** V2.6-Pro is assessed; V2.6-Flash and UltraSpeed are not yet scored by AA (§7).
- **Data residency:** removed as a constraint (§8).
- **Measured token use:** no longer a gate (§6).

---

## 2. The value stream: every step from idea to live

| # | Step | Who covers it in the constitution | What it changes in the model |
|---|---|---|---|
| 1 | Discover the requirements (K analysts, commit before view) | Inquiry | Captures each requirement with the analyst's pass chance |
| 2 | Challenge the framing | Council | Finds missed requirements |
| – | Human ratifies intent (4 h) | Isa | Delay |
| 3 | **Design / architecture** | Planning | Design quality q scales all card difficulty (+10 points at q = 0), integration defects (×3) and merge conflicts (×2) |
| 4 | Plan: requirements to cards | Planning | Maps captured requirements; weak planners write ambiguous cards |
| 5 | Red-team the plan | Planning | Finds unmapped requirements |
| – | Human ratifies plan (2 h) | Isa | Delay |
| 6 | Build a card, with unit tests | Work Market | Logic defect if the builder fails; security flaw on sensitive cards (25%); tests catch 50% of logic defects |
| 7 | Code review | Assurance Court | Catches logic defects; security flaws only at 0.3× skill |
| 8 | **Security review** (sensitive cards) | Assurance Court | Catches security flaws |
| 9 | **Merge and CI** | Work Market | Conflicts with the cards being built, which are redone; integration defects, 60% caught by CI |
| 10 | Audit (10% sample) | Audit | Re-checks accepted cards |
| 11 | **Acceptance test (QA) of the whole idea** | Release Gate | Finds missing intent and remaining defects |
| 12 | Release approval | Release Gate | Last check (30%) |
| – | **Deploy: staging smoke test, then production** | automated | 30% of remaining defects roll back from staging |
| 13 | **Live: incident, restore, hotfix** | *none of the eight* | An escaped defect causes an incident with probability 0.5–0.8 (security highest). Someone restores service, then a hotfix card runs build → review → merge → deploy |

The steps in **bold** were missing from the r10 model.

**The gap:** step 13, live operation, belongs to none of the eight institutions. The constitution stops at the Release Gate, but the value stream does not. Design must assign it. For example, the Release Gate could own rollback, the Work Market could take hotfix cards, and the Ledger could mark change-failure rate and restore time as evidence (§10).

**Where the work goes** (institutions, the six): build 55% of seat-hours, review 16%, merge 9%, security 4%, QA 3%, planning 3%, everything else 10%. The longest waits are for design (5.5 h) and build (4.9 h).

---

## 3. Organisations as mappings of steps onto models

An organisation here is only a mapping: which seats may do which step, plus rules. The same engine therefore covers:
- one role per step;
- several steps per role;
- several roles (a committee) per step;
- pools of models per step;
- no organisation;
- an organisation found by search.

| Design | Mapping |
|---|---|
| No organisation (solo) | Each seat owns an idea and does every step itself, including checking its own work |
| Peer | As solo, but review, QA and release by another seat |
| Director → Worker → Checker (today) | Director: discover, design, plan, release, live. Checker: review, QA. Workers: build, merge. Cards routed by the Director's noisy estimate |
| Orchestrator | One lead does every thinking and checking step; workers build, merge, run live |
| Functional roles (several steps per role) | Architect (design, plan, red team), product (discover, challenge, QA), reviewer (review, security, audit), release/operations, developers. Fixed; best of a swap search over who holds which role |
| Institutions | Every seat may pull every step, gated by evidence licences and independence |
| Pools per step ("bunches of models") | Anchor: design, plan, red team, security, release. Fast top: discover, challenge, review, QA, audit, live. Mid: build, merge |
| Searched | For each step, which pools may do it, plus committee sizes and optional steps; found by coordinate search from the institutions |

**Rosters and scenarios:**
- Rosters: the six; and 12 seats drawn from the AA population in natural-tier proportions (anchor = top two, fast = the other top-tier seats, mid = the rest).
- Scenarios: base; harder work; security-heavy (50% sensitive cards); weak tests (tests 30%, CI 40%); heavy merge contention.

### 3.1 Results: clean ideas a week as a share of the institutions', across all 10 cells (`orgs_results.txt`)

"Clean" means the idea went live with every requirement delivered and no escaped defect.

| Design | Worst | Mean | Best | Change-failure rate, the six, base |
|---|---|---|---|---|
| **Institutions** | 100% | 100% | 100% | 11% |
| Searched (most clean ideas) | 95% | 107% | 120% | 9% |
| Pools per step | 48% | 69% | 97% | 8% |
| Peer | 49% | 68% | 83% | 13% |
| Director → Worker → Checker | 46% | 59% | 79% | 18% |
| Functional roles | 47% | 59% | 68% | 12% |
| No organisation (solo) | 44% | 53% | 61% | 29% |
| Orchestrator | 39% | 44% | 60% | 16% |

**Reading:**
- **No organisation ships plenty but little of it is clean.** With the six it takes 28 ideas a week live but only 14 clean; 29% of its deploys cause incidents, and 46% on harder work. Peer review recovers most of that, but not with a weak roster: 49–58% with the 12-seat population, where no licence keeps weak models off hard work.
- **Fixed roles cost throughput.** Functional roles and pools per step idle some seats while others queue. Pools per step does well with the six (81–97%) and badly with a weak roster (48–56%).
- **One lead, whether orchestrator or Director, is a ceiling.** Lead times reach up to 250 h with the 12-seat population.
- **The search confirms the institutions.**
  - With the six, it keeps every step open to every pool except design (moved off the anchor so the anchor stays free for hard cards) and audit.
  - With the 12-seat population, it adds step affinities: planning by the anchors, discovery and security by fast top-tier models, merging by mid models. That gains 6–20%.
  - It kept licences, independence and every optional step (council, red team, security review, audit) in every case.
- **The cheapest organisation (searched for clean ideas per dollar) is a false economy.** It costs $12–29 per clean idea, but delivers about half the clean output (41–52%) and doubles lead time.

The same comparison on the r10 task model (`operating_models_results.txt`) ranks the designs the same way. Its ablation adds that licences, independence and the red team carry the clean output; council, audit, a second analyst and a second planner add little in a model that has no collusion or drift. They stay, because they guard against risks the model does not contain.

---

## 4. Elasticity: model instances, started and stopped by rules

### 4.1 The Scaler: rules in the Ledger, not an agent

Every 15 minutes:
1. **Price.** Price each queued task on every model licensed for it whose pass chance clears the **quality floor (0.8)**. Expected cost = $/busy hour × hours ÷ pass chance, and the cheapest wins. If none clears the floor, the most capable model takes it (R13).
2. **Target.** A model's target = its busy instances + ⌈its queued hours ÷ 2 h⌉.
3. **Clamp.** Clamp to each model's limit: 8 instances each, 48 in all [assumption standing in for vendor rate limits].
4. **Burn cap.** If the targets' burn exceeds the cap, trim the most expensive model first.
5. **Start and stop.** Start the shortfall (ready in 3 minutes). Stop instances that have been idle for 30 minutes beyond target.
6. **Cost-band pull.** An instance may take a task only if it clears the floor and its expected cost is within **1.5×** the cheapest qualified model's, unless the task has waited an hour. Without this rule, expensive instances started for hard cards soak up cheap work.

**Independence across instances.** Instances of one model count as one model for independence, so a model never checks its own model's work.

**Demand arrives over time:**
- **Steady:** 25 ideas a week.
- **Bursty:** two-day bursts at 2.5×.
- **Growth:** 10 → 80 ideas a week.
- **Mixed:** ideas of 3, 8 or 20 requirements, at −10, 0 or +10 difficulty.
- **Surge:** 60 ideas a week.
- **Harder:** +0, +10 or +20 difficulty.

### 4.2 Results (`elastic_results.txt`, 4 seeds)

| Demand | Fixed six: clean / lead p50–p90 / $ per clean | Fixed 24 | **Elastic (six models, rules 1–6)** |
|---|---|---|---|
| Steady | 19.7 / 30–49 h / $43 | 19.4 / 16–21 h / $51 | **20.1 / 19–26 h / $19** |
| Bursty | 20.6 / 41–67 h / $40 | 19.6 / 16–22 h / $51 | **19.2 / 19–27 h / $21** |
| Growth | 25.7 / 101–220 h / $42 (110 ideas waiting) | 38.8 / 16–23 h / $48 | **40.7 / 19–26 h / $23** |
| Mixed sizes and difficulty | 19.2 / 36–66 h / $46 | 20.0 / 16–26 h / $55 | **21.0 / 19–37 h / $32** |
| Surge (60 a week) | 28.1 / 327–508 h / $41 (201 waiting) | 51.8 / 16–22 h / $46 | **49.2 / 18–25 h / $22** |
| Harder | 14.2 / 43–96 h / $71 | 15.9 / 19–44 h / $81 | 13.3 / 26–61 h / $90 |

**What the rules are worth** (same six models):

| Variant | Clean output vs full rules | $ per clean | Change-failure rate |
|---|---|---|---|
| No cost-band pull (rule 6 off) | −3% to −15% | +36% to +78% | +0 to +3 points |
| Cheapest-only (floor 0.6) | −12% to −35% | −8% to −57% | 15–20% |

- **Rule 6 is worth keeping:** without it the same output costs 36–78% more.
- **The cheapest-only floor is a false economy:** it saves money only by shipping defects.

**A swarm of one model fails on independence and cost:**

| Swarm | Change-failure rate | $ per clean idea |
|---|---|---|
| Opus 5.5 only | 16–23% | $205–312 |
| Gemini 3.8 Flash only | 17–25% | $44–69 |
| Opus + Gemini | 11–14% | $70–135 |
| Six-model menu | 9–13% | $19–32 (normal work) |

**Diversity of models is load-bearing.**

**Fixed seats sized for the peak** (24) match elastic on output and are faster by 2–3 h. But they cost 1.7–2.7× as much per clean idea, because idle expensive seats pull cheap work. They also need the peak known in advance.

**Harder work is the one case where elastic costs more** (+27%). Most of that work clears the 0.8 floor only on Opus or Terra, so the Scaler starts many anchor instances. The trade is faster delivery (p90 61 h against 96 h) for higher cost.

### 4.3 Which models on the menu (`elastic_results.txt`, MENU)

| Menu | Steady: clean / $ | Mixed | Harder | Surge |
|---|---|---|---|---|
| Six with Opus 5.5 | 20.1 / $19 | 21.0 / $32 | 13.3 / $90 | 49.2 / $22 |
| Six with GPT-5.6 Terra | 21.0 / $18 | 20.4 / $26 | 14.8 / $68 | 48.1 / $19 |
| **Seven (both anchors)** | 19.6 / $20 | 20.0 / $31 | **15.5** / $85 | 47.9 / $21 |
| Whole shortlist (24 models) | 18.8 / $19 | 19.3 / $52 | 13.4 / $169 | 45.1 / $22 |

**Reading:**
- **Opus against Terra is within noise** on clean output. Terra is 5–25% cheaper. Opus had the lower change-failure rate on steady and harder work, Terra on mixed and surge.
- **The seven-model menu gives the most clean output on hard work** and costs little more elsewhere. It keeps two top-tier vendors per rule P1, since instances of both can run at once.
- **A bigger menu is not better.** With all 24 models, a free local model (Gemma 4 31B) takes 21–31% of the work. It is slow, lead time rises by 6 h, and with hard work Fable 5.1 is started at $8 an hour.
- **A local model earns a place only as a cost floor** for easy cards, if lead time matters less than cash.

The fixed-seat re-run (r11 probes) says the same thing: every leading six has the same shape, and the anchor seat is a near-tie between Opus 5.5, GPT-5.6 Terra, GPT-6 Sol\* and Grok 4.6 (`robust6_results.txt`).

---

## 5. Budget: optimal spend and the cap sweet spot

Under API tokens an idle instance costs nothing, so **spend is set by demand, not by headcount**. Monthly figures use 52/12 weeks.

**Cost to serve demand** (elastic, six models, base token model, light contention):

| Ideas arriving a week | Clean a week | $ per clean | Marginal $ per extra clean idea | ≈ $ a month | Lead p50–p90 |
|---|---|---|---|---|---|
| 10 | 7 | 22 | – | 680 | 20–28 h |
| 25 | 20 | 19 | 18 | 1,690 | 19–26 h |
| 50 | 37 | 21 | 22 | 3,310 | 18–26 h |
| 100 | 78 | 25 | 30 | 8,610 | 20–27 h |
| 150 | 119 | 32 | 44 | 16,400 | 24–33 h |

**With heavy merge contention:**
- The marginal cost reaches $43 at 100 a week and $86 at 150 a week.
- At 150 a week the 48-instance ceiling binds and lead time doubles (44–61 h).
- **Scale sweet spot: up to about 100 ideas a week.** Beyond it, each extra clean idea costs 2–4× what it costs at 25–50 ideas a week.

**Burn cap** (elastic, six models; output as a share of uncapped):

| Cap ($/hour of running instances) | Growth 10→80 | Surge 60 | Bursty 25 |
|---|---|---|---|
| $2 | 50%, 136 waiting | 46%, 211 waiting | 97%, p90 124 h |
| $5 | 65%, 100 waiting | 59%, 152 waiting | 98% |
| **$10** | **95%** | **98%** | **106%** |
| $20 / $40 / none | 97% / 97% / 100% | 98% / 92% / 100% | ≈100% |

The average burn for those three demands is $2.4–6.4 an hour, so a $10 cap is about 1.5–4× the average burn.

**The rule** (independent of the token model, because it is relative): cap the hourly burn at **2× the trailing seven-day average**, with a monthly ceiling set from expected demand × cost per clean idea × 1.5.

**For a trial at 25 ideas a week:**
- Expected spend is **about $1,700 a month**.
- Ceiling: about **$2,500 a month** at the base token model. The range is $1,000–8,500 from the lean to the heavy token model.
- The Ledger measures the real figure from the first week and the rule re-bases itself.

**Value-based optimum.** Serve demand while the marginal cost per clean idea is below its value. The value of a clean idea is [PLACEHOLDER: Isa's value per clean idea], so the optimum is unknown. At a value above about $45 per clean idea (light contention) or $90 (heavy), serving up to 150 ideas a week pays in the model.

**The likely real ceiling is human.** Ratification of intent and plan scales with ideas. At an assumed 10 minutes an idea, 100 ideas a week is about 17 hours of your time. Design must decide which ideas need a human and which the Council can ratify (§10).

---

## 6. Token use: why measurement is not a gate (`token_invariance_results.txt`)

- Every model's cost moves by nearly the same factor under the lean (×0.33–0.42) and heavy (×3.1–3.9) token models.
- The cost ranking moves by at most two places, and only between models within 10% of each other.
- The six's cost order is unchanged apart from Ling and Luna, which are 6% apart and swap under heavy use.
- **So every choice here is independent of token use:** which models, which rules, which organisation, the Scaler's decisions and the cap rule. Only the dollar totals scale.
- **Tokens vs subscriptions holds on the re-run** (`subs6_results.txt`):
  - Plan-only delivers 61–80% of the clean output.
  - Hybrid saves 4–15%.
  - Elastic capacity needs 30–48 concurrent instances at peak, which no plan supplies.
  - Top seats stay on API tokens.
- **The trial's real token figures come from the Ledger automatically.** The test is: simulate, run the same scenario live, compare.

---

## 7. Models: Muse Spark and MiMo

### 7.1 Muse Spark 1.3 (Meta): API access confirmed

- It is served by the **Meta Model API** with a self-serve API key and OpenAI-SDK compatibility, and is also listed on OpenRouter.
- **Standard tier:** $1.25 / $4.25 per 1M tokens; prompts and completions are not used for training.
- **Contributor tier:** $0.10 / $0.20, **in exchange for Meta training on your prompts and completions**. It is **excluded**: the Factory's code and prompts are Heliosvera IP. Rule: no model tier that trains on our data.
- **Rate limits** (third-party guides; Meta's own page was not reachable from here):
  - standard tier: 3,000 requests a minute and 4M tokens a minute per team, shared by all keys;
  - contributor tier: 100 requests a minute.
  - At the base token model one busy Muse instance uses about 70k tokens a minute (about 4.3M an hour, mostly cached input), so the team limit is about 55 instances. That is well above the 8 the Scaler allows.
- **Regional rollout has been uneven**; users reported the EU still being served 1.1 at launch. [Unverified for UK and KSA.] Keep OpenRouter as the second route.

Sources: [Meta for Developers: Muse Spark](https://developer.meta.com/ai/models/muse-spark/), [Meta Model API](https://developer.meta.com/ai/products/meta-model-api/), [OpenRouter: Muse Spark 1.3](https://openrouter.ai/meta/muse-spark-1.3), [OpenRouter: Contributor](https://openrouter.ai/meta/muse-spark-1.3-contributor), [DataCamp](https://www.datacamp.com/blog/muse-spark-1-3), [Layer3 Labs: limits](https://www.layer3labs.io/guides/muse-spark-1-3-limits), [TrueFoundry](https://www.truefoundry.com/blog/muse-spark-1-3).

### 7.2 MiMo (Xiaomi)

The MiMo-V2.6 series was released on 22 Sep 2026 (MIT licence).

**MiMo-V2.6-Pro** is on AA:
- Intelligence Index 46.3, Coding Index 76.1\*, $0.435 / $0.87, 43 t/s.
- It was a candidate for every mid seat and in every search.
- It loses on speed: in the model, output speed decides more than a few Coding Index points.
- In the elastic runs with the whole shortlist it takes 4–5% of the work.

**MiMo-V2.6-Flash** ($0.14 / $0.28) and **V2.6-Pro-UltraSpeed** ($4.35 / $8.70; Xiaomi claims Pro quality at up to 10–20× Pro's speed) are **not yet scored by AA**. Under rule P6 they earn a place through a trial seat, not by announcement.

**What-if** (`whatif_mimo_results.txt`: UltraSpeed at Pro's estimated Coding Index, replacing one seat):

| UltraSpeed at | Clean output vs the six | $ per clean idea |
|---|---|---|
| 116 t/s | −6% to +2% | – |
| 430 t/s | +5% to +12% | $33–48 (six: $27) |
| 860 t/s | +16% to +22% | $38–52 |

**Watch it:** if AA confirms the speed, it earns a seat on the menu.

Sources: [Xiaomi MiMo updates](https://mimo.mi.com/docs/en-US/updates/model), [SiliconANGLE](https://siliconangle.com/2026/09/22/xiaomi-introduces-mimo-v2-6-series-open-source-ai-model-family/), [OpenRouter: UltraSpeed](https://openrouter.ai/xiaomi/mimo-v2.6-pro-ultraspeed), [OpenRouter: Flash](https://openrouter.ai/xiaomi/mimo-v2.6-flash), [VentureBeat](https://venturebeat.com/technology/better-than-deepseek-xiaomis-mimo-v2-6-pro-debuts-as-the-top-open-weights-model-in-the-world-alongside-cheaper-v2-6-flash). Opus 5.5 context, reported in September 2026 coding leaderboards: Terminal-Bench 4.0 Opus 5.5 66.4%, GPT-6 Astra 57.9%, Fable 5.1 55.8%; AA Intelligence Index Opus 5.5 57.6, the highest ([MorphLLM](https://www.morphllm.com/best-ai-model-for-coding), [BenchLM](https://benchlm.ai/benchmarks/aacodingindex)).

---

## 8. Data residency

The US-only option is removed: you are not US-based, and a single-country rule is an artificial constraint.

**Future analysis** (not now): model how the laws where models run and where data sits affect cost and efficiency. Examples are UK GDPR, the KSA Personal Data Protection Law and Morocco's Law 09-08. The model would treat jurisdiction as a property of each route to a model, the way price and speed are now. Any legal reading needs a qualified adviser.

---

## 9. Model corrections in r12 (transparency)

- **Double release** (r10 model): a late audit catch could queue a second release, counting an idea twice. Fixed; effect 0–2%.
- **Empty-plan stall** (r10 model): a plan that mapped no requirements left its idea stalled in build forever. Weak planners hit it often, which made "swarm" results near zero and flattered r10 lead times upward. Fixed: an empty plan goes to the Release Gate, which finds the missing intent.
- **Work in progress:** one idea in flight per seat (6 for the six, not 4). The six's output rises by about 14%, with lead time 24 h against 19 h.
- **Objective:** sixes are ranked on clean ideas, not ideas.

**Value-stream engine: independence deadlocks with fixed roles.**
- The Director releasing its own plan, or an owner rebuilding its own card, could exclude the only permitted seat.
- Fixed: when the structure permits no independent seat, the role-holder does it and the Ledger records a waiver.
- With Director routing, a failed card returns to the same worker, as it does today.

---

## 10. Changes to the Idea Record and open items

**Changes to the Idea Record**
- **§5.5 (new):** the value stream, organisations as step mappings, elasticity and budget.
- **Rules:**
  - R14, Scaler: rules 1–6 of §4.1.
  - R15, no data-training tiers.
  - R16, burn cap at 2× the trailing average.
  - P8 extended: capacity is elastic, bought per token.
- **Decision H6 amended:** approve the seven-model menu, the Scaler and the cap rule for the trial.

**Open items**
- **Design question:** who owns live operation (step 13)?
- **Design question:** which ideas need human ratification, given it is the likely real ceiling?
- **Experiment:** in the trial, run the same scenario live that the model ran, and compare clean output, change-failure rate and cost per clean idea.

---

## 11. Assumptions (value-stream model; all in `vs_sim.py`)

| Assumption | Value | Why |
|---|---|---|
| Pass chance | logistic(0.12 × (Coding Index − difficulty) + ln 3) | r10 curve |
| Design quality effect | +10 points card difficulty, ×3 integration defects, ×2 conflicts at q = 0 | Poor architecture raises all downstream cost [assumption] |
| Tests / CI catch | 50% / 60% | r10 test catch; CI [assumption] |
| Sensitive cards; security flaw | 25%; 0.5 × (1 − pass at d + 10) | [assumption] |
| Review spots security flaws | 0.3 × skill | Ordinary review is weak on security [assumption] |
| Own-model check | 0.5 × an independent check | Correlated blind spots [assumption] |
| QA intent / defect catch | 0.7 / 0.5 × skill | r10 release catch |
| Release / smoke catch | 30% / 30% | [assumption] |
| Incident from an escaped defect | logic 0.5, integration 0.6, security 0.8 | [assumption] |
| Merge conflict | 1 − exp(−k × (2 − q) × cards being built); k = 0.005 (heavy 0.02) | Contention grows with parallel work [assumption] |
| Human ratification | 4 h intent, 2 h plan (delay only) | r10 |
| Scaler | 15-min cycle; drain 2 h; spin-up 3 min; stop after 30 min idle; floor 0.8; band 1.5; 8 per model, 48 in all | Chosen by sweep (floor, band) or [assumption] (limits) |
| Token model | lean / base / heavy (§6) | r11 |

---

## 12. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| The model's parameters are assumptions | The rankings could change live | Every headline was tested across 3–6 scenarios. The trial compares model and reality step by step |
| Vendor rate limits are lower than 8 instances per model | Surges queue | The Scaler reads real limits; the menu has two models per class |
| Estimated scores (Opus 5.5\*, DeepSeek\*, Luna\*) | The menu order shifts | Re-run when AA publishes; the r11 −3-point test left the ranking intact |
| Human ratification becomes the bottleneck | Output stops at your hours | Tier the ratification (design question) |
| Live operation has no owner | Incidents wait | Assign it in design (§10) |
| Muse Spark regional availability | A menu model missing | OpenRouter route; Gemini 3.8 Flash covers the same class |
