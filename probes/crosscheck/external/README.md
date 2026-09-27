# Factory Organization Laboratory

A runnable, discrete-event simulation comparing alternative organizations for stateless model agents. Built in response to Isa's September 27, 2026 request.

## Scope and provenance

**This is a new synthetic structural experiment, not a replication of the supplied simulation and not a replay of Artificial Analysis's 136 configurations.** No exact Artificial Analysis snapshot was available to this run. Tier skill, token rates, verbosity, price and provider limits are openly specified hypotheses in `simulator.py` and exported to `results/assumptions.json`. They are not claims about actual subscriptions or named commercial models. Numerical conclusions apply to these hypotheses; the intent is to find mechanisms, trade-offs and candidates for empirical testing.

The earlier pasted results remain an independent simulation. This laboratory does not establish that their conditional optimum is invalid. A simulation can identify an optimum within its model before field calibration. The useful question is which additional mechanisms change that optimum.

## Architectural constraints carried forward

- SQL is canonical operational state. Agent calls do not retain conversational memory, task ownership between calls or privileged personal context.
- Every invocation reloads a bounded snapshot of original intent, current planning state and dependency artifact versions. Requests, outputs, attributable events and outcomes can be inspected in SQLite.
- The event engine is ordinary scheduling software, not an LLM/Agent 70 controller. It enforces leases, capacity, independence and state transitions; it does not select a supposedly intelligent-enough model.
- Default claim policy is capability-neutral FIFO among eligible work, with a rotating randomized agent order. A separate local-self-selection scenario uses visible noisy complexity estimates and each agent's published capability/cost priors. It cannot observe true defects or hidden family blind spots.
- No reviewer verifies their own implementation. Sampled auditors differ from both implementation author and preceding verifier.
- Collective designs use two independent release-evidence submissions. Software applies the published all-objections-resolved rule. There is no permanent judge-model.
- Model size/skill and reasoning effort are distinct variables.

## The five organizations

| Organization | Work topology | Assurance and release |
|---|---|---|
| Single Checker | One fixed director frames/plans, other workers implement dependent cards | One fixed Checker handles card verification; director performs release checks |
| Elastic pipeline | Same basic stages with agents drawing from a shared pool; downstream implementation may start after upstream implementation, before assurance | Immediate pooled card verification; pooled release check |
| Institutions | Two inquiry submissions, council, plan, challenge, shared implementation market | Whole-idea implementation barrier before card verification; sampled audit; two release-evidence submissions |
| Evidence graph | Two inquiry submissions, plan, challenge; dependent work becomes available after upstream assurance | Streaming card/interface verification, sampled audit, two release-evidence submissions; no whole-idea assurance barrier |
| Packet graph | Evidence graph with multiple adjacent requirements implemented in one bounded invocation | Fewer external interfaces, longer invocations, less task-level parallelism; no retained agent memory |

The packet design changes **artifact granularity**, not agent affinity. A different agent may implement, verify or rework the packet using SQL state. Packets group requirement IDs in topological order; this first implementation does not optimize graph partitioning. The packet-size experiment explores 1, 2, 4 and 8 requirements per invocation.

An equal-controls experiment gives the elastic pipeline and both graph designs the same two inquiries, council, challenge, audit and two release submissions as the institutions. This separates barrier timing from extra deliberation. It does not discard the current single-Checker organization as a useful reference.

## Event and quality model

Each idea has eight requirements, drawn from three difficulty levels, and a reproducible acyclic dependency graph. Both are paired across architectures for a seed. A finite backlog is admitted under a WIP limit; all ideas are followed to release or explicit failure. In-flight calls are drained and charged even after their idea has failed. There is no favorable deletion of incomplete observations.

A job claims a snapshot, reserves an execution slot, consumes input/output tokens and modeled time, writes an output, and releases its slot. SQL stores jobs and canonical state for every run. Detailed append-only events are also stored in the supplied example trace. Hidden evaluator state is used only to sample/score outcomes, never supplied in worker snapshots or used by the default dispatch policy.

Base probability is the supplied logistic shape:

`p = logistic(slope × (skill + role_offset − difficulty − packet_context_penalty + 6 × log2(effort)) + ln(3))`

Defaults: slope 0.12; top/middle/bottom skill 72/56/38; difficulty 40/56/72 with 40%/40%/20% sampling probabilities. These numerical values are assumptions, not measurements. Base success is 75% when effective skill equals difficulty. A hidden family-specific requirement blind spot reduces the probability to 40% of its base value. It is shared across stages and invocations. An explicit bounded repair increment, 0.025 per attempt up to three increments, represents information gained from failed evidence.

Other explicit assumptions:

- Reference edge probability: 0.25 for every ordered requirement pair. Reference interface-decoherence parameter: 0.10.
- Reference family-blind-spot probability: 0.18. Sensitivities include 0 and 0.45. Each requirement/family pair has its own latent blind spot.
- Two synthetic top-tier families and one family each for middle and bottom represent a four-source portfolio. This intentionally couples tier composition with family diversity, as in that portfolio. The zero-blind-spot scenario isolates the diversity mechanism. It is not a universal property of intelligence tiers.
- Reconstruction/interpretation error: 0.025 per implementation requirement, varied to 0.12. This represents misinterpreting an accurate SQL snapshot, not SQL losing context or agents relying on conversation history.
- Packet context penalty: `2.5 × (packet_size − 1)^1.2` skill points. Packet output volume grows linearly with requirement count; input grows more slowly to represent reused shared context.
- Unit tests catch each implementation defect with probability 0.50. These are simulated tests, distinct from the actual simulator unit tests in `test_simulator.py`.
- Review probability depends on the reviewing model, task difficulty, effort and its latent blind spot. An audit samples 10% of blocks in collective designs. Interface checks are charged to streaming assurance or final release as appropriate.
- Rewriting a block invalidates dependent artifact versions. Already running obsolete jobs finish, are charged and discarded. This measures rework despite durable SQL state.
- At most four implementation attempts per block and two release-reopen rounds. Exhausted cases fail explicitly. Recovered missing intent reopens the implementation plan; this is deliberately a costly full-plan rebuild in this first model.
- Collective release requires two distinct evidence submissions; unresolved objections cause rework or failure. Positive submissions cannot override an outstanding objection.
- No false-positive reviewer objections, malicious behavior, human correction, schema outages or semantic defects between otherwise independent ideas are modeled. There is no actual LLM, Git merge or test-runner execution. Artifact revisions are represented symbolically in SQL; production Git should remain the artifact authority.

## Time, cost and constrained capacity

Duration includes sampled output volume, tier verbosity, reasoning-effort multiplier, token speed, fixed snapshot/latency overhead and implementation tool time. Cost uses input/output volumes and separate illustrative prices. Nothing treats tokens/second as entire task completion time or per-token price as total task cost.

Prices are illustrative USD-equivalent assumptions, not verified bills. The default costs omit fixed subscriptions, GPU purchase, support and human correction. Compare relative inference economics within this model, not expected real spending.

Unconstrained mode allows each logical agent one concurrent invocation. Constrained mode shares these **hypothetical** provider caps: top-A 2, top-B 2, middle 4, bottom 1. Quota mode adds reservations of 8/8/36/24 execution-hours per 24 simulated hours. These are stress-test parameters, not asserted limits on Isa's subscriptions. Calls reserve their full duration against the start day's quota; they are not preempted at a reset.

## Metrics

- Released ideas per synthetic week: released cohort / drained elapsed hours × 168. Finite-cohort normalization, not a steady-state production forecast.
- Useful idea-equivalents per synthetic week: correctly delivered requirements / 8 / drained elapsed hours × 168. A requirement counts only when included, free of its own implementation/interface defects, and all prerequisite requirements are correct. Failed ideas contribute zero.
- Intent: share of original requirements included in released ideas. This is distinct from semantic correctness and therefore cannot alone measure coherent useful delivery.
- Escaped defects: implementation plus interface defects per released idea. Counts need not equal the percentage of defective ideas. Propagated consequences are reflected in useful output rather than counted repeatedly as new defects.
- Completion: released / all admitted ideas. Explicitly report this to avoid favoring an organization that abandons difficult work.
- Cost per useful idea-equivalent: includes failed, reworked and discarded work in its numerator.
- Lead time is admission-to-terminal-release for released ideas; failed outcomes remain in `outcomes` with their own elapsed time. Backlog before admission is excluded; makespan includes it.
- Utilization: reserved execution time / (logical headcount × drained elapsed time). It is not provider hardware utilization.

## Experiments and uncertainty

`experiments.py` exports every seed-level row. The main sweep contains 1,890 runs: 13 topology scenarios (12 paired seeds; the equal-controls scenario has four organizations), headcount/capacity scaling, all 91 twelve-agent tier mixes for two organizations (three screening seeds), packet sizes under three coupling settings, and effort levels. Cohorts contain 20 ideas, or 32 in the scaling experiment.

Three seeds are screening, not confirmation. `confirm.py` performs fresh-seed confirmation of selected configurations and focused mechanism comparisons. `analyze.py` computes seed-level 95% t intervals. These intervals quantify Monte Carlo uncertainty conditional on this model; they do not quantify uncertainty about real-world parameters. Paired comparisons use per-seed differences. The same generated workload is paired, but distinct workflow paths consume different model assignments and outcome trials.

Original quality floors are retained as a named screen: mean intent >=97%, mean escaped defects <=0.25. A separate completion measure is always shown. No configuration is called feasible if none passes those floors. The highest useful-output configuration can still fail a quality floor; those are different claims.

## Run and inspect

Python 3.10+ is sufficient for the simulator and sweeps. Analysis/figures use pandas, numpy, scipy and matplotlib.

```bash
python -m unittest -v
python simulator.py --architecture evidence_graph --mix 6,3,3 --ideas 32 --audit results/example_trace.sqlite
python experiments.py --mode full --workers 6
python confirm.py
python analyze.py
```

`simulator.py` also exposes `Config` and `run(Config(...))` for parameter changes. Profile data can be replaced in `PROFILES` after a versioned empirical calibration; the current bundle does not implement an Artificial Analysis importer or automatically treat a benchmark score as Factory truth.

SQL inspection examples:

```sql
SELECT kind, COUNT(*), AVG(ended-started), AVG(started-created)
FROM jobs WHERE started IS NOT NULL GROUP BY kind;
SELECT time, idea, event, payload FROM events ORDER BY seq;
SELECT idea, result FROM outcomes;
```

## What the next empirical experiment should identify

Estimate per-stage competence, reviewer detection given an actual producer's error, family-correlated errors, interpretation error from exact SQL snapshots, dependency graph density, revision fan-out, token/call distributions, and independently measured provider concurrency/quotas. Preserve model, effort, harness and version in every observation. These observations replace exposed assumptions; they do not require abandoning simulation until every quantity is known.

## Elasticity extension

The user's follow-up changes the main control variable from fixed agent staffing to variable concurrent invocations from each model. `elasticity.py` runs 768 additional experiments across two organizations, four arrival/workload regimes and four controllers, with 24 paired seeds and 48 ideas per run.

The four controllers use the same model portfolio, same backend limits and same quality rules:

1. **Fixed small:** one concurrent invocation per available model family (maximum four).
2. **Full shared pool:** immediately start eligible work up to the same backend maxima (maximum nine).
3. **Queue autoscale:** desired concurrency responds to ready-job count, apportioned by explicit backend caps. Actual calls fall to zero when no eligible work exists.
4. **Work autoscale:** estimate backlog service time using stage-level EWMA observations, plus noisy complexity tags for variable workloads. Desired concurrency responds to estimated time-to-drain. Ready work receives a deterministic priority for release/assurance, dependency unlocking and queue age. No LLM controls these rules.

There are 20 possible logical worker identities, including replicas of each model family, in every elasticity experiment. They are maximum invocation slots, not 20 running models. Backend caps are 2 + 2 + 4 + 1. Replica count does not multiply quota or physical GPU capacity. Invocation input is reloaded from SQL each time. Scale-down means no new leases beyond the target; running work is never killed to meet a lower target. Completed invocations retain no context.

Burst arrivals release eight ideas every three synthetic hours. The variable-work case alternates easier and harder waves; both outcome difficulty and token volume vary. End-to-end time includes waiting from arrival, unlike admitted lead time. The dense-burst case raises both dependencies and interface-error likelihood.

This implementation has no standing fee for idle logical identities. Consequently, it cannot honestly claim autoscaling saves money merely by deleting idle agents. Savings or losses come from work selection, failures, rework and the resulting model-call mix. Queue-autoscale and a full shared pool may behave similarly. The work-aware rule is tested rather than assumed superior.

The initial work-aware rule estimates total ready service demand, apportions concurrency across model-family caps, and lets ready-job priority determine the realized stage staffing. It does not implement separate predictive per-stage controllers, provider-specific rate-limit telemetry, credit-aware market clearing or learned routing. Those would be distinct extensions.

```bash
python elasticity.py
python analyze.py
```

## Controller threshold sensitivity

`tune_elasticity.py` adds 240 fresh-seed runs. It tests target-drain times of 0.10, 0.25, 0.50 and 1.00 hours against a full shared pool on the same workloads. This identifies whether a poor autoscaling result belongs to the controller class or to the particular threshold. It is a sensitivity experiment; the best threshold was not separately confirmed after selection.

## Results from this build

The final bundle contains **4,250 completed seeded runs and 133,768 simulated idea instances**. Idea instances across paired alternatives are repeated comparative workloads, not 133,768 unique empirical tasks. Nine actual software tests pass. Ten stored run rows spanning the original sweep reproduce exactly with the final simulator source. The figure was rendered and inspected.

Key results, conditional on this model:

- Evidence-graph useful output exceeds the staged-institution variant by **17.9%**, with a paired bootstrap 95% interval **8.5% to 28.5%**, when deliberation, sampled audit and release-evidence counts match. There are 24 paired confirmation seeds. This comparison specifically tests the modeled barrier/dependency policies; it does not establish that all institutional designs impose such barriers.
- For the evidence graph under variable burst workloads, allowing up to nine shared concurrent invocations produces **2.40x** the useful output of a four-call ceiling, with a paired 95% interval **2.28x to 2.52x**. End-to-end mean falls from **20.31 to 4.07 synthetic hours**. The same model portfolio supplies the extra replicas. This is a hypothetical capacity-envelope comparison, not proof of actual provider allowances.
- Queue autoscaling delivers **2.33x** the four-call reference. The initial work-aware controller (0.5-hour target) delivers **1.91x**, or **20.6% less** useful output than the full shared pool. Its lower target concurrency leaves capacity unused.
- In fresh threshold sensitivity runs, the 0.10-hour work-aware target is **3.4% below** the full pool; its paired interval is **-8.8% to +2.3%**. This does not establish a difference. A 1.00-hour target is **50.2% below** the full pool. Start with a work-conserving lease rule, not an unvalidated conservative demand predictor.
- With dense dependencies, fusing all eight requirements performs much better if the additional invocation context penalty is removed, but much worse if that penalty applies. This is a boundary-condition result. It supports measuring the packet-size/coherence trade-off, not recommending long-context agents or retained agent memory.
- For the 10-top/2-middle evidence graph, increasing latent family blind-spot probability from 5% to 18% changes escaped defects from about **0.18 to 0.35 per release**, despite high intent coverage. Replica independence is distinct from epistemic independence.
- The original 97% intent / 0.25 escaped-defect floors are **not met by any of the seven shortlisted mixes in reference-regime confirmation**, although two configurations appeared to pass during three-seed screening. The all-top evidence graph is close, at approximately 0.27 escaped defects, and its uncertainty interval crosses the threshold. This is an unresolved feasibility result under the added assumptions, not evidence that the earlier simulation's optimum is mathematically invalid.
- In the low-blind-spot scenario, the 10-top/2-middle graph does meet those point-estimate floors. Quality feasibility therefore changes with the error structure, not just tier counts.

The elasticity controllers also miss the original quality floors under their tested mixed-model reference regime. Their throughput comparisons are experimental findings, not deployment approval. `results/summary.csv`, `paired_comparisons.csv`, and `mix_quality_intervals.csv` preserve these distinctions. Cost figures remain hypothetical inference equivalents.

## Decision implied by the experiments

Use persistent institutional rules and an elastic population of stateless invocations over an evidence/dependency graph. Keep intelligence providers, logical worker identities, active model calls, institution labels and backend concurrency separate. Let SQL-backed leases and explicit capacity counters start ready work and allow completed invocations to disappear. Preserve useful-work accounting, not just card count.

The immediate tested scheduling candidate is work-conserving: launch eligible work whenever a legal backend slot and budget reservation exist; no fixed person-like seat is required at any stage. Deadline/age fairness, provider token reservations and anti-starvation guarantees should be explicit in the real executor. The simulation tests basic age/evidence priority, not a complete production controller.

Do not infer that a larger logical swarm can break a dependency chain or duplicate a provider's quota. Do not infer that many replicas of a model make an independent evidence quorum. Preserve original intent and evidence references outside model custody, and test semantic coherence at dependency boundaries.
