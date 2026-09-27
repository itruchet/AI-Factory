# AI Factory

An AI-native software engineering Factory that converts human ideas into implemented, tested, reviewed software using multiple model families.

## Constitutional Factory (Idea stage)

- **[Idea Record](docs/idea/constitutional-factory.md)** (r7): eight institutions; agents pull cards; plain rules in the Ledger adjust what each agent may pull, based on how the next institution marks its work. Success and velocity push agents up, failure moves them down, and hardest-first pull puts more capable models on harder cards. No manager agent.
- [Pull-rules probes](probes/pull-rules/): `sim.py` (capacity and frontier caps) and `capability_sort.py` (five-tier capability sorting from an inverted start), synthetic data. [Visual summary](https://claude.ai/artifact/B5RL3EqqouYKK6fUvnETwW).
- [Parked design notes](docs/design-parked/): earlier design-stage material.
- [Superseded probe](probes/_superseded/): r3–r4 allocation maths, replaced by the pull rules.

```
python3 probes/pull-rules/sim.py                    # capacity simulation
python3 probes/pull-rules/capability_sort.py        # capability sorting simulation
python3 -m unittest discover -s probes/pull-rules   # checks of the Idea Record's claims
```
