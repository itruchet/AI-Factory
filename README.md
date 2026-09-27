# AI Factory

An AI-native software engineering Factory that converts human ideas into implemented, tested, reviewed software using multiple model families.

## Constitutional Factory (Idea stage)

- **[Idea Record](docs/idea/constitutional-factory.md)** (r6): eight institutions; agents pull cards; plain rules in the Ledger adjust what each agent may pull, based on how the next institution marks its work. Success and velocity push agents up to a home tier they may not drift below. No manager agent.
- [Pull-rules probe](probes/pull-rules/): simulation testing rules R1–R13 against a static mapping and the r5 pacing rule (synthetic data).
- [Parked design notes](docs/design-parked/): earlier design-stage material.
- [Superseded probe](probes/_superseded/): r3–r4 allocation maths, replaced by the pull rules.

```
python3 probes/pull-rules/sim.py                    # simulation
python3 -m unittest discover -s probes/pull-rules   # checks of the Idea Record's claims
```
