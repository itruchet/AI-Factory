# Institutions as agent harnesses (r12.8)

Stage: amendment proposed (AR-16).

**Agent = model + harness.** Each institution is a harness tailored to its stage of the work:
- framing;
- planning;
- allocation;
- working;
- reviewing;
- auditing;
- releasing;
- operating.

Models are interchangeable workers inside those harnesses. The harness and the Ledger are the Factory's lasting assets: they carry the rules, the memory and the improvements. This is the same thesis as the constitution, stated in harness-engineering terms.

---

## 1. Answer

1. **Each institution is a harness.** It has its own minimal tools, context policy, feed-forward guards, feedback sensors, hand-back contract, trajectory budget and telemetry. The rules R1–R21 run inside each harness, tailored to its job (§3).
2. **One shared harness kernel** gives every institution the same primitives:
   - sandboxed file and shell access, and retrieval from the Ledger;
   - fresh context assembled per pull;
   - trace capture;
   - budgets;
   - one model interface.
3. **Model flexibility is core (principle 9, R23).**
   - Any model can replace another at any step by configuration alone. The harness, charter and Ledger do not change, and the new model re-earns its licences by evidence (R5 fast track).
   - Nothing in a harness may be written for a named model.
   - Our evidence: designs that reserve steps for named models broke when the roster changed (65% of clean output in an outage). The institutions gained 27% when a new frontier model joined (§5.8).
4. **Memory is central, and context is fresh (principle 10, R24).**
   - No agent carries memory from one pull to the next. Everything worth keeping is written to the Ledger.
   - Each pull starts from context the harness assembles for that institution's charter: rules first, then the card and its evidence.
   - Context must be assembled cache-first. At this Factory's token mix, cost per task rises 1.5× if prompt-cache hits fall from 90% to 70%, and 3.1–3.8× with no cache (`probes/portfolio6/cache_sensitivity_results.txt`). A fresh context in a stable order keeps the cache.
5. **Harnesses improve by evidence, not by retraining (R22).**
   - Failed traces are attributed to a cause: model error, tool, context, timeout or card.
   - A harness edit must carry a falsifiable prediction, is trialled on the same work (R20), and passes the Release Gate.
   - Charters and rules still need Isa (principle 8).
6. **OpenRouter changes the route, not the design (§5).**
   - It makes model swaps a one-line change and adds provider fallback.
   - At our volume, bringing our own keys carries no fee [Unverified].
   - The real cost risk is cache hits, not the fee: use sticky sessions.
   - It puts a third party in the data path, so AR-10 must cover it.
   - Treat it as one route among several, and let the Ledger measure quality, cost and speed per route (X19).

---

## 2. The shared harness kernel

| Layer | What it does | Rule |
|---|---|---|
| **Primitive tools** | Sandboxed worktree file access, sandboxed shell and CLI, retrieval from the Ledger, lifecycle hooks. Each institution gets a subset; nothing else is exposed | Least privilege per charter |
| **Model interface** | One adapter interface for every model and route (direct vendor API or OpenRouter). Model and route are configuration | R23 |
| **Context assembly** | Fresh per pull, from the Ledger, in a fixed order:<br>1. constitution and charter;<br>2. rules and the agent's own record (R10);<br>3. repository snapshot;<br>4. the card, its contract and evidence.<br>Long histories become Ledger summaries that link to their sources, never raw logs | R24; principles 4 and 6 |
| **Feed-forward guards** | Licence and floor checks (R2, R19), independence (R18), schema validation of outputs, protected paths, readiness check on arrival (R21) | Before any spend |
| **Feedback sensors** | Tests, linters, CI and typed contracts run before any model judgment | Principle 3; DQ10 |
| **Trace capture** | Every call, tool use, latency and outcome goes to the Ledger as a structured trace that failures can be attributed from | R8; M08, M24 |
| **Trajectory governance** | Budgets on tokens, time and retries per card. Loops without progress are stopped and the card is escalated or handed back | R6, R13 |
| **Versioned components** | Tools, context policies, guards and prompts are files, versioned and revertible. Changes follow R22 | R22 |

---

## 3. One harness per institution

| Stage | Institution | Job | Tools | Context (fresh per pull) | Guards | Sensors | Hands back to |
|---|---|---|---|---|---|---|---|
| Framing | **Inquiry** | Independent discovery | Repository read, Ledger retrieval; no write | The brief and engineering context; never peer outputs or identities | Commit before view | Council's survival of propositions | Brief unclear → Isa |
| Framing | **Council** | Shared understanding | Anonymised submissions; synthesis writer | Anonymised submissions only | Every proposition covered; one objection keeps a point disputed | Isa's ratification; Planning's clarification requests | Missing intent → Inquiry |
| Planning | **Planning** | Intent to executable cards | Repository read, card writer (schema) | Alignment Record with minority positions; never the Council transcript | Blind parallel decomposition; red team separate; interfaces named; tier rules | Market hand-backs; Review attributions to the card | Unratified or ambiguous intent → Council |
| Allocation | **Ledger** | Licences, pull order, Scaler, burn cap | No model: deterministic functions | – | Replay of every decision | Integrity alarm on replay mismatch | – |
| Working | **Market** | Build | Sandboxed worktree, shell, tests, own branch; no merge | The card, contract, reviewed prerequisites and its own record | Readiness check (R21), licence, R17 | Unit tests, CI, then Review's mark | Unfit card → Planning |
| Reviewing | **Review** | Is the work acceptable? | Read-only diff; run tests, linters, static analysis, reproductions | Artifact, contract, evidence; never author identity or reasoning; other verdicts only after committing | Deterministic checks first; blind; another family (R18) | Audit's overturns | Missing evidence → Market |
| Auditing | **Audit** | Is review trustworthy? | Read-only; planted-defect registry; Ledger sampling | Contract and final artifact; never the review discussion | Outside the provenance chain | Planted defects with known answers | – (marks producer and reviewer) |
| Releasing | **Release Gate** | Safe to run? | Canary controls, rollback, metrics; no code edit | Criteria fixed before data; evidence | Different families, seated dissenter, cooling-off, no self-approval | Canary against criteria | Unproven change → Review |
| Operating | **Release Gate** (AR-09a) | Incident, restore, hotfix | Revert, metrics, hotfix card writer | The incident and the change that caused it | Revert first; the hotfix is an ordinary card | Change-failure rate, restore time | – |

**Rules tailored per harness:**
- **Pull and licences (R1–R5, R10, R11, R19):** in every model harness, with that institution's standard (AR-08) and floor.
- **Independence (R18):** Review, Audit and Release Gate.
- **Evidence-gated dependencies (R17):** Market and Review.
- **Scaler and burn cap (R14, R16):** the Ledger, for every institution's instances.
- **Readiness hand-back (R21):** every boundary.

---

## 4. Harness evolution (R22): the unit of self-improvement

1. **Attribute.** Each failed or reworked card's trace is classified by reason code (R8):
   - model error;
   - tool or tool documentation;
   - context: missing, stale or overloaded;
   - timeout or budget;
   - card not fit for purpose.
2. **Propose.** A harness edit names the component it changes, and predicts the effect on a named measure over a stated volume of work.
3. **Trial.** The edit runs as a trial configuration on the same work (R20). A model swap never counts as a harness improvement.
4. **Adopt or revert.** The edit is adopted through the Release Gate if its prediction held (X17). Otherwise it is reverted. The record stays in the Ledger.
5. **Branch, don't overload.** When one harness serves unlike work badly, it branches by tier or domain rather than accumulating special cases.

---

## 5. OpenRouter as a route to models

**Facts** ([Unverified]: third-party guides and the OpenRouter FAQ, September 2026):
- 5.5% fee on bought credits.
- Bring-your-own-key: no fee up to $25,000 a month of list-price use, 5% above.
- Prompt caching across nine provider families, with session-based sticky routing.
- Per-request `data_collection: "deny"` or zero data retention. Anthropic does not offer zero data retention there.

**What it changes:**

| Question | Effect |
|---|---|
| Model flexibility | Stronger: one interface; swapping a model is changing a string (R23) |
| Cost at our volume | About $1,700–2,500 a month is far below $25,000, so bringing our own keys carries no fee; bought credits add 5.5% |
| Biggest cost risk | Cache hits. Losing them costs 1.5–3.8× (table below), far more than any fee. Sticky sessions and cache-first context (R24) are required |
| Resilience | Provider fallback, mainly for open-weight models hosted by several providers (supports P2) |
| Data (R15, Heliosvera IP) | A third party in the data path. `data_collection: "deny"` enforces R15 per request. The terms need AR-10's adviser review |
| Key custody | Settled by the self-hosted gateway: the Owner holds the keys; an aggregator gets a vendor key only if the Owner registers one for that route (OI-17) |
| Speed | An extra hop [Unverified: small]; measured per route (M08) |

**Cost per task against cache-hit rate** (`cache_sensitivity_results.txt`; multiple of the 90% baseline, across the seven menu models):

| Cache hits | 90% | 80% | 70% | 50% | 0% |
|---|---|---|---|---|---|
| Cost per task | ×1.00 | ×1.23–1.31 | ×1.46–1.62 | ×1.92–2.25 | ×3.08–3.81 |

**Decision (Isa, 28 Sep 2026): a self-hosted gateway, with aggregators as routes.**
- **The gateway:** a self-hosted gateway (LiteLLM, open source, or equivalent) is the Factory's one model interface (C0.19). Model flexibility lives in our own layer, and the Owner keeps the keys.
- **Routes behind it:**
  - direct vendor routes for the two anchors;
  - OpenRouter where its catalogue or provider fallback is needed;
  - Vercel AI Gateway trialled as a second aggregator route.
- **Routes are configuration,** chosen by the Ledger on measured quality, cost and speed (X19).

**Comparison of aggregators** [Unverified: vendor docs and third-party guides, September 2026]:
- None of OpenRouter, Vercel, Cloudflare, Portkey or LiteLLM marks up tokens.
- The differences are the platform fee, data path, key custody and catalogue.
- Only a self-hosted gateway keeps both the data path and the keys inside the Factory.

---

## 6. What changes

**Amendment AR-16:**

| Item | Change |
|---|---|
| Principle 9 | Model flexibility |
| Principle 10 | Central memory, fresh context |
| R22 | Harness per institution, and harness evolution |
| R23 | Model swap by configuration |
| R24 | Fresh, cache-first context |
| Experiments | X17 (harness edits), X18 (model swaps), X19 (routes) |
| Naming | The reviewing institution is named Review |

**Pack:**

| Addition | What it is |
|---|---|
| C0.18 | The harness kernel |
| C0.19 | The model and route interface |
| C2.05 | Harness evolution |
| Existing institution cards | A harness line each |
| M24 | Trajectory telemetry |
| M25 | Cache hit rate |
| OI-17 | Key custody for OpenRouter |

**Takeaway:** sign AR-16 to make each institution its own harness, keep models swappable by configuration, and assemble memory centrally and cache-first.
