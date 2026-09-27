# AI Factory

An AI-native software engineering Factory that converts human ideas into implemented, tested, reviewed software using multiple model families.

## Constitutional Factory (Idea stage)

- **[Idea Record](docs/idea/constitutional-factory.md)** (r12.6): eight institutions; agents pull cards; plain rules in the Ledger adjust what each agent may pull, based on how the next institution marks its work. Success and velocity push agents up, failure moves them down, and hardest-first pull puts more capable models on harder cards. No manager agent.
- [Pull-rules probes](probes/pull-rules/): `sim.py` (capacity and frontier caps) and `capability_sort.py` (five-tier capability sorting from an inverted start), synthetic data. `portfolio.py` (model mixes, outages, golden-rules ablation, portfolio search; results in `portfolio_results.txt`). Visual summaries: [capability sort](https://claude.ai/artifact/B5RL3EqqouYKK6fUvnETwW), [golden rules and portfolio](https://claude.ai/artifact/JwEzM4KoKyUyedsWxZq6Xg).
- [Artificial Analysis tiering and market probes](probes/aa-tiers/): real Coding Index data (`aa_coding_2026-09-09.csv`), statistical tiering (`tiering.py`), portfolio and 26-week market simulation (`market_sim.py`). [Visual summary](https://claude.ai/artifact/EKdPojnAMmQwhLtG1f5Ayd).
- **[Institutional throughput](docs/idea/institutional-throughput.md)** ([`probes/institutions/`](probes/institutions/)): discrete-event simulation of the institutions vs the Director → Worker → Checker baseline, staffed only from the Artificial Analysis population; headcount, tier mix, institution sizing, shared vs dedicated seats, and sensitivity. [Visual summary](https://claude.ai/artifact/KqT8mPfqWx69EobtZ4Ybx3).
- **[Best six](docs/idea/best-six.md)** ([`probes/portfolio6/`](probes/portfolio6/)): three top and three mid seats chosen from the 27 Sep 2026 Artificial Analysis market by the institutional model; robustness across six assumption sets; top seats on API tokens vs subscriptions (capped, hybrid).
- **[Idea to live](docs/idea/value-stream.md)** ([`probes/value-stream/`](probes/value-stream/)): every step from idea to live; organisations as mappings of steps onto models (no organisation, peer, Director → Worker → Checker, orchestrator, functional roles, institutions, pools per step, and a searched design); elastic model instances started and stopped by Ledger rules; budget and burn cap. [Visual summary](https://claude.ai/artifact/XVowDeyPNUthrzjwS7fCB9).
- **[Cross-check](docs/idea/crosscheck.md)** ([`probes/crosscheck/`](probes/crosscheck/)): an independent simulation Isa supplied (`external/`, unchanged), with our rules added to it, and its mechanisms (family blind spots, packets, controller aggressiveness) added to ours.
- **[Dependency graphs](docs/idea/dependencies.md)** (`probes/value-stream/deps.py`): requirements that depend on each other; gates (R17, unreviewed, barrier, contract-first, hybrid), stale rebuilds, interface faults; organisations and elasticity re-run.
- **[Institutions or the searched design](docs/idea/institutions-vs-searched.md)** (`probes/value-stream/searched.py`): the searched design out of sample, under outages, with a new model and with elastic capacity; adaptive licence floors (R19) and trial configurations (R20).
- **[Approval register](docs/idea/approvals.md):** the 15 records, in three gates, from decision to the card backlog.
- **[Ingestion pack](pack/README.md)** ([`pack/`](pack/)): what the existing Factory ingests to rebuild itself: the constitution extracted verbatim, operating parameters, the model menu, measures, simulator parameters to calibrate, predictions, approvals, open items and 40 card seeds with acceptance contracts and a dependency graph. [`INGEST.md`](pack/INGEST.md) is the ingestion protocol for the collective (no named roles); `test_pack.py` checks that nothing is invented or left out.
- [Parked design notes](docs/design-parked/): earlier design-stage material.
- [Superseded probe](probes/_superseded/): r3–r4 allocation maths, replaced by the pull rules.

```
python3 probes/pull-rules/sim.py                    # capacity simulation
python3 probes/pull-rules/capability_sort.py        # capability sorting simulation
python3 probes/pull-rules/portfolio.py              # mixes, outages, golden rules, portfolio search (~3 min)
python3 -m unittest discover -s probes/pull-rules   # checks of the Idea Record's claims
pip install numpy scipy scikit-learn                # for the tiering probe
python3 probes/aa-tiers/tiering.py                  # how many natural tiers
python3 probes/aa-tiers/market_sim.py               # portfolios and rolling market
python3 -m unittest discover -s probes/aa-tiers
python3 probes/institutions/experiments.py          # institutional throughput (~10 min)
python3 -m unittest discover -s probes/institutions
python3 probes/portfolio6/select6.py                # best six from the current market (~10 min)
python3 probes/portfolio6/robust6.py                # robustness of the choice
python3 probes/portfolio6/subs6.py                  # tokens vs subscriptions for the top seats
python3 -m unittest discover -s probes/portfolio6
python3 probes/portfolio6/token_invariance.py       # do choices depend on token use?
python3 probes/portfolio6/whatif_mimo.py            # MiMo-V2.6-Pro-UltraSpeed what-if
python3 probes/institutions/operating_models.py     # other organisations on the r10 task model (~10 min)
python3 probes/value-stream/orgs.py                 # organisations on the idea-to-live steps, plus search (~20 min)
python3 probes/value-stream/elastic.py              # fixed vs elastic, caps, menus, scale (~25 min)
python3 -m unittest discover -s probes/value-stream
python3 probes/value-stream/crosscheck.py           # blind spots, packets, Scaler aggressiveness (~15 min)
python3 probes/crosscheck/our_rules_in_their_sim.py # our rules inside the supplied simulation (~10 min)
python3 probes/value-stream/deps.py                 # dependency graphs: gates, organisations, elasticity (~40 min)
python3 probes/value-stream/scaler_held.py          # Scaler counts held cards as demand (~15 min)
python3 probes/value-stream/band_wait.py            # the cost-band wait behind elastic's lead-time gap (~5 min)
python3 probes/value-stream/searched.py             # institutions vs searched design (~30 min)
python3 -m unittest discover -s probes/crosscheck
python3 pack/build_pack.py                          # rebuild the ingestion pack
python3 -m unittest discover -s pack                # pack integrity: nothing invented, nothing forgotten
```
