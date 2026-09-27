# Best six: three top seats, three mid seats (r11)

Stage: **IDEA**. Market: Artificial Analysis (AA) snapshot of **27 Sep 2026**. Probes: [`probes/portfolio6/`](../../probes/portfolio6/) (`select6.py`, `robust6.py`, `subs6.py`; results in the matching `*_results.txt`). The model is the r10 institutional throughput simulation ([`institutional-throughput.md`](institutional-throughput.md)), staffed with named models instead of random draws.

> **r12 note.** This is the r11 record. r12 re-ran every probe after two model fixes, one idea in flight per seat (work-in-progress 6, not 4) and ranking on **clean** ideas. The current figures are in [`probes/portfolio6/`](../../probes/portfolio6/) (`*_results.txt`). They move the numbers below, not the shape of the answer: one strong anchor, the two fastest top-tier models, then three fast cheap models.
>
> r12 also changes the frame: the six are a **menu of models**, and Ledger rules start and stop instances of them as work arrives. It confirms Muse Spark API access and drops the US data-residency option. See [`value-stream.md`](value-stream.md).

All outcomes are synthetic. They rank options; they do not forecast the real Factory's output. `*` marks a Coding Index that is **estimated**. AA had not yet published a Coding Index for models released after 9 Sep, so their score comes from a fit on the AA Intelligence Index (top end: RMSE 1.5 points, n = 34).

---

## 1. Answer

**Recommended six (all six pay per API token):**

| Seat | Model | Vendor | Coding | $/1M in / out | Speed t/s | Job it wins in the model |
|---|---|---|---|---|---|---|
| Top | **Claude Opus 5.5 (Max)** | Anthropic | 80.6* | 4 / 20 | 82 | Anchor: hardest cards, planning, red team, release checks |
| Top | **Muse Spark 1.3 (xhigh)** | Meta | 76.5 | 1.25 / 4.25 | 243 | Fast top-tier volume: mid and hard cards, reviews |
| Top | **Gemini 3.8 Flash (high)** | Google | 76.3 | 0.75 / 3.75 | 278 | Fast top-tier volume; Google's strongest AA coding model |
| Mid | **DeepSeek V4.1 Flash (Max)** | DeepSeek | 71.6* | 0.30 / 1.20 | 222 | Fast, cheap; open weights |
| Mid | **GPT-6 Luna (max)** | OpenAI | 68.0* | 0.10 / 0.50 | 154 | Cheapest fast seat; covers the OpenAI vendor slot |
| Mid | **Ling 3.0 Flash** | InclusionAI | 50.6 | 0.07 / 0.22 | 373 | Easy cards and Inquiry at very high speed; open weights |

Model output for this six: **34.7 ideas a week**, 99.7% of intent delivered, 0.04 escaped defects per idea, about **$26 per idea** on API tokens. The API bill is about **$890 a week (~$3,860 a month)** under the base token assumptions. The plausible range is $1,500–12,900 a month (§4.3).

**Why not the premium trio (Fable 5.1 + GPT-6 Astra + Gemini)?** The model puts it at 85% of the best throughput, at **$72 per idea** (2.8× the cost). Fable and Astra are the slowest top-tier models (56–68 t/s) and the most expensive ($10/$50). Most of the work does not need them: 80% of cards are easy or mid. One frontier anchor is enough, and Opus 5.5 does that job at 40% of Fable's price.

**Tokens vs subscriptions, for the top three: tokens.** Details are in §4. In short:
1. **Plans are sized for a person, not a round-the-clock seat.** An always-on seat works 125–135 hours a week. A $200 plan covers about 24–40 of those hours, so full cover needs 4–6 plans per seat.
2. **Hybrid saves little.** Hybrid means a plan first, then API tokens past the cap. It saves only 5–12% for the recommended six.
3. **Plan-only is cheap, but slower and against the intended use.** It cuts the bill by about 45% per idea, but throughput falls to 81–83%. Consumer plans are meant for one person's own use, and an unattended multi-agent Factory is not that. [Unverified: check each vendor's current terms; this is not legal advice.]

---

## 2. What changed from the earlier framing

- **"Top" and "mid" are price classes, not capability classes.** Using natural tiers from the Coding Index, every one of the twelve best-value models is **top tier** (≥ 56.8), including MiMo-V2.6-Pro, GLM 5.3 Flash, Gemini 3.8 Flash and DeepSeek V4.1 Flash. Capability at the top has become cheap. The seat classes used here are therefore:
  - **top:** blended price ≥ $2/M;
  - **mid:** < $2/M.
  - Gemini 3.8 Flash ($1.50) could fill either.
- **Speed matters more than a few Coding Index points.** Within the top tier, the spread of 74–82 changes the pass rate on the hardest cards by about ten points. Output speed changes task time by up to 2× (§5, robustness).
- **Three statistically mid-tier seats cost about 6% of throughput**, for example Inkling Small + Ling 3.0 Flash + Gemma 4 31B at 33.8 against 35–37 ideas a week. The mid seats should still be fast.

---

## 3. How the six was chosen (working)

**Candidates.** One configuration per model, taken from 165 current priced AA configurations:
- 12 for the top seats: Fable 5.1, Opus 5.5*, GPT-6 Astra, GPT-6 Sol*, GPT-5.6 Terra, Grok 4.7*, Grok 4.6, Muse Spark 1.3, Kimi K3, GLM-5.3, Qwen3.8 Max* and Gemini 3.8 Flash;
- 13 for the mid seats: Gemini 3.8 Flash, MiMo-V2.6-Pro*, Step 5 Preview*, GLM 5.3 Flash*, Qwen3.8-Flash-Next, DeepSeek V4.1 Flash*, GPT-6 Luna*, MiniMax-M3, MiMo-V2.5, Qwen3.8 27B, Inkling Small, Ling 3.0 Flash and Gemma 4 31B.

Google has no Gemini Pro newer than 3.1 Pro Preview (Feb 2026; 68.8) on AA, so Gemini 3.8 Flash stands for Google. The full table is in `select6_results.txt`.

**Hard constraints** (Idea Record §5.1):
- **P1:** at least two vendors among the top seats.
- **P2:** no vendor holds more than 3 of the 6 seats.
- A model holds one seat only.

**Institution sizing** (r10 ideal): Inquiry K=2, one planner plus a red team, one council round, 10% audit, and a work-in-progress limit of 4. Agents pull work around the clock. Results are per week, after one week of warm-up.

**Stages:**

| Stage | What | Result |
|---|---|---|
| S1 | 219 legal top trios with a reference mid trio (MiMo-V2.6-Pro*, GLM 5.3 Flash*, DeepSeek V4.1 Flash*), 4 seeds | Every top-10 trio contains Muse Spark and/or Gemini 3.8 Flash (the two fastest top-tier models). The spread is 21.2–29.5 ideas/wk. |
| S2 | 1,320 legal sixes (the 5 leading top trios × every mid trio) | Fast mid seats win: Ling 3.0 Flash (373 t/s) appears in every top-12 six. The leading sixes reach 35–37 ideas/wk. |
| S3 | 12 finalists on 12 seeds, with a vendor-outage test and estimated scores cut by 3 points | Leaders sit within noise of each other (33–37 ± 1–3). Losing the most important vendor for a week costs 13–20%. |
| Robustness | 21 sixes (finalists, the premium trios, a US-only mid tier) under 6 assumption sets | See §5. **Minimax regret** (the best worst case, ties within 2 points broken by cost) picks the recommended six. |

**Why Opus 5.5 rather than Fable 5.1 as the anchor:**
- Both are the most robust sixes, at 95% of the best in their worst scenario.
- Opus costs $26 per idea against Fable's $44.
- Opus-anchored sixes are **best in the harder-work scenarios**: the recommended six scores 98% and 100% of best.
- The caveat: Opus 5.5's Coding Index is estimated (80.6*). Cutting it by 3 points leaves the six at 95–98% of best.

**Why not the cheapest six?** Muse Spark + GLM-5.3 + Gemini with the same mids costs $16 per idea but falls to 88–93% of best when work gets harder. It has no frontier anchor. It is the fallback if Anthropic becomes unavailable.

---

## 4. Tokens vs subscriptions for the top seats

### 4.1 Facts (sourced, September 2026)

| Plan | Price | Top-model allowance | Status |
|---|---|---|---|
| Claude Max 5x / 20x | $100 / $200 a month | Weekly cap across models, not published. Community reports: about 15–35 (5x) and 24–40 (20x) Opus hours a week. Fable 5.1 is included, up to 50% of weekly usage. | Opus 5.5 is the current Opus on Max |
| ChatGPT Pro 5x / 20x | $100 / $200 a month | GPT-6 Astra in Codex: 25–225 (5x) or 100–900 (20x) local messages per 5 hours; weekly limits may apply | **New 20x sign-ups paused** |
| Google AI Ultra 5x / 20x | $99.99 / $199.99 a month | No published agent limits | — |
| GLM Coding Plan (Z AI) | $18 / $80 / $168 a month | Credits refresh on a 5-hour and a weekly window | Mid-seat option if GLM is used |
| API list prices (AA) | Opus 5.5 $4/$20; Astra and Fable $10/$50 (Astra cached input $1); Gemini 3.8 Flash $0.75/$3.75; Muse Spark $1.25/$4.25 per 1M tokens | — | — |

Sources: [Claude pricing](https://claude.com/pricing), [IntuitionLabs on Claude Max](https://intuitionlabs.ai/articles/claude-max-plan-pricing-usage-limits), [TrueFoundry on Claude Code limits](https://www.truefoundry.com/blog/claude-code-limits-explained), [MorphLLM Codex pricing](https://www.morphllm.com/codex-pricing), [Christopher Alarcon on Astra limits](https://christopheralarcon.com/blog/gpt-6-astra-usage-limits-explained), [codexusage.dev](https://www.codexusage.dev/limits/astra), [eesel on Gemini pricing](https://www.eesel.ai/blog/google-gemini-3-pricing), [Suprmind on Gemini](https://suprmind.ai/hub/gemini/pricing/), [codingplan.org](https://codingplan.org/en), [MindStudio on coding plans](https://www.mindstudio.ai/blog/open-model-coding-plans-glm-kimi-deepseek).

### 4.2 Assumptions

- **Plan hours.**
  - ChatGPT Pro and Google AI Ultra are given the same hours as Claude Max: 24–40 a week for 20x and 8–20 for 5x. [Assumption: they publish messages or nothing, not hours.]
  - A Fable seat gets half of a Max plan's hours.
- **Tokens per working hour.**
  - The model generates for 25% of each working hour; the rest is tool calls and tests.
  - An agent loop reads 30 input tokens per output token; 90% come from the prompt cache at 10% of list price.
  - At 100 t/s this is 90k output and 2.7M input tokens an hour.
  - Cost per busy hour: Fable $7.96, Astra $7.21, Opus 5.5 $3.49, Sol $1.76, Muse Spark $1.59, Gemini 3.8 Flash $1.20.
- **Always-on seats.** Each seat works 125–135 hours a week in the model.

### 4.3 Results (`subs6_results.txt`)

| Top trio | Mode | Top seats $/week | ≈ $/month | Ideas/wk | All-in $/idea |
|---|---|---|---|---|---|
| **Opus 5.5 + Muse Spark + Gemini (recommended)** | API only | 812 | 3,520 | 34.7 | 25.6 |
| | Hybrid (one 20x plan per seat where it pays; API past the cap) | 717–775 | 3,110–3,360 | 34.7 | 22.9–24.6 |
| | Plan only (Muse on API: no plan identified for it) | 308–315 | 1,340–1,370 | 28.1–28.9 (81–83%) | 13.4–14.0 |
| Opus 5.5 + GPT-6 Sol + Gemini (every seat has a plan) | API only | 855 | 3,710 | 32.2 | 29.0 |
| | Hybrid | 734–817 | 3,180–3,540 | 32.2 | 25.2–27.8 |
| | Plan only | 138 | 600 | 22.5–23.9 (70–74%) | 9.0–9.6 |
| Fable 5.1 + GPT-6 Astra + Gemini (premium) | API only | 2,190 | 9,490 | 31.2 | 72.7 |
| | Hybrid | 1,833–2,014 | 7,940–8,730 | 31.2 | 61.2–67.0 |
| | Plan only | 138 | 600 | 22.0–23.0 (70–74%) | 9.3–9.8 |

Mid seats add about $78 a week on API in every row. "All-in" includes them.

**Break-even hours a week for a $200 plan against API tokens:**
- Fable: 5.8 h
- Astra: 6.4 h
- Opus 5.5: 13.2 h
- Sol: 26.2 h
- Gemini 3.8 Flash: 38.3 h (the plan barely pays)

**Plans needed to cover one always-on seat:** 4–6 per seat, or 7–12 for Fable.

**Token-model sensitivity** (recommended six, all seats on API; the end of `subs6_results.txt`):

| Token assumptions | $ per idea | $ per month |
|---|---|---|
| Lean | $10 | $1,510 |
| Base | $26 | $3,860 |
| Heavy | $86 | $12,890 |

**The token model is the largest single uncertainty in the cost figures.** Measure it in the first week of any trial.

### 4.4 Reading

1. **Plans pay only on expensive models.** A plan buys 24–40 hours of API-equivalent work for $46 a week. That is worth $190–320 on Fable or Astra, $84–140 on Opus 5.5, and at most break-even on Gemini 3.8 Flash.
2. **Plan-only is the cheapest per idea, and the institutions cushion the cap.** When a top seat hits its cap, the other seats pull its work, so throughput falls only 17–30% even though the capped seats idle for most of the week (they work 24–40 of 168 hours). That cushion is a property of pull, which a Director → Worker → Checker hierarchy would not have.
3. **Plan-only is still the wrong base for a Factory.**
   - It trades throughput for a smaller bill.
   - It needs several consumer accounts per seat to scale.
   - It depends on terms written for one person at a keyboard. [Unverified: vendor terms; seek legal review before relying on consumer plans for automated use.]
   - Weekly caps are unpublished and change without notice.
4. **Rule (P8 amended):** top seats run on **API tokens**.
   - A plan is admissible only as an optional **overflow discount** on an expensive anchor model (Opus or Fable), held by a named human operator, and only where the vendor's terms allow agent use.
   - No seat depends on a plan to exist.
   - Plans on cheap fast models (Gemini 3.8 Flash, Sol) are not worth holding.

---

## 5. Robustness (`robust6_results.txt`)

Throughput as a share of the best six under each assumption set:

| Six | base | speed counts half | speed ignored | harder work | harder + half | estimates −3 | **worst** | $/idea |
|---|---|---|---|---|---|---|---|---|
| **Opus 5.5 + Muse + Gemini ‖ DeepSeek V4.1 Flash + Luna + Ling** | 94% | 98% | 98% | 98% | 100% | 98% | **94%** | **26** |
| Fable 5.1 + Muse + Gemini ‖ DeepSeek + Inkling + Ling | 97% | 98% | 99% | 96% | 95% | 99% | 95% | 44 |
| Muse + GLM-5.3 + Gemini ‖ DeepSeek + Luna + Ling (cheapest) | 93% | 97% | 98% | 96% | 95% | 96% | 93% | 16 |
| Terra + Muse + Gemini ‖ DeepSeek + Inkling + Ling (S3 fastest) | 99% | 100% | 97% | 92% | 91% | 99% | 91% | 21 |
| Opus 5.5 + Sol + Gemini ‖ DeepSeek + Luna + Ling | 86% | 95% | 98% | 93% | 98% | 90% | 86% | 29 |
| Fable 5.1 + Astra + Gemini ‖ DeepSeek + Luna + Ling (premium) | 85% | 92% | 98% | 90% | 94% | 87% | 85% | 72 |
| Opus 5.5 + Muse + Gemini ‖ Luna + Inkling + Gemma 4 31B (US-only mid, one local) | 84% | 92% | 99% | 88% | 88% | 87% | 84% | 30 |

**Reading:**
- When speed stops mattering, every candidate converges (95–100%). The choice is then about cost and resilience.
- When work gets harder, a frontier anchor (Opus or Fable) matters and all-fast sixes drop to 78–92%.
- The recommended six is never below 94% of best.

---

## 6. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| Estimated scores (Opus 5.5*, DeepSeek V4.1 Flash*, GPT-6 Luna*) | The ranking may shift when AA publishes Coding Index scores | Cutting estimates by 3 points leaves the six at 98% of best; re-run `select6.py` when AA publishes |
| Token model (duty, input ratio, cache) | Costs vary by about ±3× | Measure tokens per card in week one; the Ledger records real cost per seat |
| Data residency. DeepSeek and Ling are Chinese-origin; the listed prices are first-party APIs | Code and prompts leave the US | Both have open weights, so run them on US-hosted inference [PLACEHOLDER: provider price]. Alternatively use the US-only mid tier (Luna + Inkling Small + Gemma 4 31B locally): −10% throughput, $30/idea |
| Muse Spark 1.3 API terms and availability for business use | A top seat may be unobtainable | [Unverified] Confirm enterprise API access. The fallback top seat is GPT-6 Sol (same six: −7 to −8%) |
| One vendor lost for a week | −13 to −20% throughput | P1 and P2 hold; R13 keeps work moving; P6 trial seat for the replacement |
| Consumer-plan terms, if plans are used | Account suspension mid-run | API is the base; plans are overflow only, held by a named person |

---

## 7. Decision needed (Isa)

1. **Approve the six on API tokens** as the starting portfolio for the first Factory trial. Owner: Isa. Date: [PLACEHOLDER].
2. **Set the data-residency rule for the mid tier:**
   - Option A: open-weight Chinese-origin models allowed only on US-hosted inference.
   - Option B: a US-only mid tier, at −10% throughput.
3. **Choose whether to hold one Claude Max 20x plan** as an overflow discount on the Opus seat. It saves about $37–93 a week and applies only if Anthropic's terms allow this use.

**What I still need:**
- Monthly budget ceiling.
- Whether code or prompts may leave the US.
- Confirmation of Muse Spark API access.
- A week of measured tokens per card from the current Factory.
