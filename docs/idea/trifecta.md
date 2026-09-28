# Quality, cost and speed: the trifecta, hand-backs and human rounds (r12.7)

Stage: amendment proposed (AR-15). Code: [`probes/value-stream/trifecta.py`](../../probes/value-stream/trifecta.py) → `trifecta_results.txt`, 12 seeds per cell. All results are synthetic. The new mechanisms are off by default, and with them off the model reproduces r12–r12.3 exactly (tests pass).

**Configuration:**
- the institutions;
- the elastic Scaler, with held demand and a 15-minute target;
- R17 at 25% coupling;
- the seven-model menu.

---

## 1. Answer

1. **Optimise quality, cost and speed together; the sweet spot is a time value of about $0.5 an hour.**
   - Until now the Scaler priced a success as $ ÷ pass chance. Speed never entered the choice of model: a faster model uses more tokens an hour, so its cost per task is the same.
   - Adding a time value to the price brings speed in: ($ + time value × elapsed hours) ÷ pass chance.
   - At $0.5 an hour, cost and quality hold and lead time falls slightly.
   - Beyond $2 an hour, speed is bought at a poor cost.
2. **Latency matters for speed, not money.** Waiting for a first token is not billed, but it lengthens every call on the critical path. Once time is priced, the Scaler routes around slow models.
3. **Unfit cards must be handed back before anyone builds on them (R21).** In the model, hand-backs cut failed builds by 13–43% with no loss of clean output. The model is conservative here: it finds insufficient detail only at build, while the Factory has also found it late, after review and further down the pipeline.
4. **Human time is measured, not excused.** Each send-back round from Isa costs lead time, measured like any institution's work. Hand-backs and clear acceptance criteria reduce send-backs.

---

## 2. What was added to the model

| Mechanism | Rule in the model | Status |
|---|---|---|
| Readiness hand-back (R21) | The puller checks each card (10% of its hours). An insufficiently specified card is spotted with pass chance at difficulty 55 and handed back to Planning, which rewrites it. Before this, such a card was built, failed up to three times, then clarified. | Shares and difficulties are assumptions |
| Trifecta price (R14) | ($/busy hour × hours + time value × elapsed hours) ÷ pass chance | Time value swept |
| Latency | Elapsed time adds calls × time to first token. Latency is waiting and is not billed. | **Illustrative only:** 15–20 s for max-effort reasoning models, 10 s xhigh, 5 s high, 1 s non-reasoning; 40 calls per hour of work. No measured latency yet. |
| Human rounds | At intent and plan ratification, Isa sends the work back for another round with chance 0 / 25% / 50% | Swept |

---

## 3. Results

### Trifecta (T2): time value in the Scaler's price

| Time value | Steady: clean / lead p50–p90 / $ per clean | Mixed |
|---|---|---|
| $0 (r12.3) | 18.9 / 25–44 h / $28.1 | 18.3 / 25–116 h / $80.1 |
| **$0.5 an hour** | **18.7 / 24–44 h / $28.3** | **18.6 / 23–103 h / $69.7** |
| $2 an hour | 19.0 / 23–39 h / $36.9 | 17.1 / 19–86 h / $80.7 |
| $5 an hour | 19.4 / 21–34 h / $39.5 | 18.8 / 20–89 h / $92.3 |
| $20 an hour | 19.6 / 21–37 h / $50.0 | 19.1 / 20–85 h / $99.1 |

**Findings:**
- Quality holds throughout: change-failure rate stays at 12–14%, and clean output is flat within noise. The R19 floors keep it there.
- Buying speed beyond $0.5 an hour costs 31–78% more per clean idea on steady work than at $0.
- **The sweet spot is $0.5 an hour, with $2 an hour when speed matters more.** It is a Ledger parameter, moved on live evidence.

### Latency (T3), illustrative

| Case | Steady: lead p50–p90 / $ per clean | Mixed |
|---|---|---|
| No latency, time value $0 | 25–44 h / $28.1 | 25–116 h / $80.1 |
| Latency, time value $0 | 28–51 h / $28.8 | 27–127 h / $71.3 |
| Latency, time value $2 | 24–41 h / $37.4 | 22–98 h / $78.1 |

Instances wait 160–285 hours a week for first tokens. That time is not billed, but it lengthens every idea. Pricing time moves work to faster-responding models and more than recovers the lead time.

### Hand-backs (T1)

| Insufficient cards | Steady: failed builds per idea, build and fail → hand back | Mixed |
|---|---|---|
| At the model's rate | 1.26 → 0.95 (−25%) | 2.36 → 2.05 (−13%) |
| 3× (poorly specified work) | 1.84 → 1.05 (−43%) | 3.01 → 1.96 (−35%) |

**Findings:**
- Clean output and change-failure rate are unchanged within noise. On mixed work, cost per clean idea varies about ±15% between seeds of the same design.
- The saving in wasted builds is paid for by the 10% check on every card. Cheaper checks, or insufficient detail found later in the pipeline, make R21 pay more.

### Human rounds (T4)

| Isa sends back | Steady: lead p50–p90 | Mixed | Rounds per idea |
|---|---|---|---|
| 0% | 25–44 h | 25–116 h | 0 |
| 25% | 28–47 h | 27–105 h | 0.78 |
| 50% | 33–55 h | 32–131 h | 2.38 |

Quality and cost are unchanged; each round costs speed. The levers:
- clearer Alignment Records;
- the Council's challenge round;
- R21, which stops unfit work reaching Isa.

---

## 4. What changes

**Amendment proposed (AR-15):**
- **R14:** the price includes the time value, starting at $0.5 an hour.
- **R21:** the readiness hand-back.
- **Experiments X15 and X16.**

**Measured from day one:**
- latency split from generation and tool time (M08);
- hand-backs and rounds per card at every boundary (M21);
- Isa's turnaround and send-backs (M22);
- quality, cost and speed per model and step (M23).

The illustrative latency figures give way to measured ones in the first week of metering.

**Takeaway:** sign AR-15 so the Scaler weighs speed with cost and quality, and every institution hands back unfit cards.
