# AI Factory

An AI-native software engineering Factory that converts human ideas into implemented, tested, reviewed software using multiple model families.

## Constitutional Factory (Idea stage)

- **[Idea Record](docs/idea/constitutional-factory.md)** (r9): eight institutions; agents pull cards; plain rules in the Ledger adjust what each agent may pull, based on how the next institution marks its work. Success and velocity push agents up, failure moves them down, and hardest-first pull puts more capable models on harder cards. No manager agent.
- [Pull-rules probes](probes/pull-rules/): `sim.py` (capacity and frontier caps) and `capability_sort.py` (five-tier capability sorting from an inverted start), synthetic data. `portfolio.py` (model mixes, outages, golden-rules ablation, portfolio search; results in `portfolio_results.txt`). Visual summaries: [capability sort](https://claude.ai/artifact/B5RL3EqqouYKK6fUvnETwW), [golden rules and portfolio](https://claude.ai/artifact/JwEzM4KoKyUyedsWxZq6Xg).
- [Artificial Analysis tiering and market probes](probes/aa-tiers/): real Coding Index data (`aa_coding_2026-09-09.csv`), statistical tiering (`tiering.py`), portfolio and 26-week market simulation (`market_sim.py`). [Visual summary](https://claude.ai/artifact/EKdPojnAMmQwhLtG1f5Ayd).
- **[Institutional throughput](docs/idea/institutional-throughput.md)** ([`probes/institutions/`](probes/institutions/)): discrete-event simulation of the institutions vs the Director → Worker → Checker baseline, staffed only from the Artificial Analysis population; headcount, tier mix, institution sizing, shared vs dedicated seats, and sensitivity.
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
```
