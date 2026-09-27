# AI Factory

An AI-native software engineering Factory that converts human ideas into implemented, tested, reviewed software using multiple model families.

## Architecture

- [Constitutional architecture — design proposal](docs/architecture/constitutional-factory.md)
- [Ledger reference schema (SQLite)](docs/architecture/ledger-schema.sql)
- [Allocation kernel](kernel/allocation.py): minimum sufficient intelligence, capacity shadow prices, Thompson assignment, Neyman audit sampling, SPRT release decisions

## Kernel

```
python3 -m unittest discover -s kernel   # tests
python3 kernel/demo.py                    # worked example (synthetic data)
```
