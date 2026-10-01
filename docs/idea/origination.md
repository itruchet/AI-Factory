# Edge cases, self-origination and the ratification envelope (r12.11)

Stage: amendment AR-19, ready for Isa's signature. Code: [`probes/value-stream/origination.py`](../../probes/value-stream/origination.py) → `origination_results.txt`, 8 seeds per cell. All results are synthetic. The new mechanisms are off by default, and with them off the model reproduces every earlier result (tests pass).

**Isa's direction, 1 Oct 2026, in her words:** "We do not need a ninth stage but definitely require self originated ideas. I disagree further briefs would load as that is a good problem to solve."

**Configuration:**
- the institutions;
- the elastic Scaler, with held demand, a 15-minute target and a time value of $0.5 an hour;
- R21 hand-backs and R17 at 25% coupling;
- the seven-model menu.

---

## 1. Answer

1. **The Factory originates its own ideas through the institutions it already has (R27).** The Ledger raises signals by rule from its own record. Each signal becomes a brief that Inquiry works like one of Isa's. No ninth institution, and no agent in the control path.
2. **Ratification stops being the ceiling (R28).** Isa sets an envelope. Ideas inside it are ratified by rule, and she samples 10% afterwards. Ideas outside it queue for her, in order of value per minute of her time. In the model, 80% inside the envelope turns a cap of 16–18 clean ideas a week into 56, on 3.6 of her hours.
3. **Edge cases become evidence, not opinion (R26).** Failure scenarios in every contract become tests hidden from the builder. A model of another family writes challenge tests before it reads the code. Audit checks the tests by mutation score.
4. **Challenge tests pay only where blind spots differ by family,** so the Ledger keeps them by tier on evidence. Blind spots shared by every family need mechanical exploration (property-based, boundary and fuzz inputs) and human-ratified failure scenarios; their catch rate is unmeasured.

---

## 2. How it works without a ninth stage

| Need | Where it lives | Rule |
|---|---|---|
| Notice that something should be built | **Ledger**, by rule: escaped defects or incidents clustering on a component; all-family misses; repeated hand-backs or stale rebuilds; rising cost per clean idea; repeated agent work (R25); a weekly standing brief | R27 |
| Turn the signal into ideas | **Inquiry**, blind and in parallel, with typed propositions: opportunity, alternative, risk, failure scenario and others | R27, C3.05 |
| Agree what the idea is | **Council**, as today | – |
| Ratify it | **Envelope rule** inside Isa's bounds, with her 10% sample; **Isa** outside them | R28 |
| Keep it honest | Originated ideas are capped at 20% of the monthly ceiling and marked by the value they realise; Isa's overturns narrow the envelope at once | R27, R28 |
| Make edge cases evidence | Failure scenarios → sealed tests (Planning); challenge tests (Review); mutation score (Audit) | R26 |

**Ideation and testing are one chain.** Each Inquiry participant names the failure scenarios it would test, blind. Families miss different things, so their union covers more than any one. The scenarios the Council keeps become acceptance criteria, then sealed tests.

**Until Inquiry exists (Phase 3),** the collective pulls originated briefs like any card, and Planning or the card's author writes failure scenarios. Origination (C1.21), the envelope (C1.22) and challenge tests (C1.20) start in Phase 1.

---

## 3. What was added to the model

| Mechanism | Rule in the model | Status |
|---|---|---|
| Challenge tests (R26) | At first review, a model of another family writes tests from the contract (30% of the card's hours). They catch a defect an LLM check can see at 0.6 × its pass chance, subject to family blind spots. | Effort and catch rate are assumptions |
| Mechanical exploration (R26) | Catches a defect in a blind spot shared by every family at 0% or 25% | **No measured rate**; swept |
| Isa's attention (R28) | A weekly budget, spread over the week; 5 minutes per ratification, intent and plan (about 10 an idea, DQ7) | 5 hours a week is **illustrative**: Isa sets the real budget (OI-10) |
| Envelope (R28) | A share of ideas is ratified by rule at once; 10% of those take Isa's time afterwards, and nothing waits on them | Swept: 0%, 50%, 80% |
| Self-origination (R27) | More ideas on top of 25 briefs a week: +0, +25, +50 | The model cannot value an idea |

---

## 4. Results

### Ratification (O): 5 hours of Isa's attention a week

| Ideas a week | Isa ratifies all | Envelope 50% | Envelope 80% | Unlimited Isa (reference) |
|---|---|---|---|---|
| 25 (briefs only) | 18.5 clean; lead 37 h; 4.1 h of Isa | 18.0; 24 h; 2.2 h | 18.7; 21 h; 1.2 h | 18.8; 24 h |
| 50 (+25 originated) | 18.1 clean; lead 326 h; 5.0 h | 37.4; 29 h; 4.5 h | 37.8; 20 h; 2.4 h | 38.7; 24 h |
| 75 (+50 originated) | 16.1 clean; lead 488 h; 5.0 h | 45.6; 30 h (p90 355 h); 5.0 h | **56.4; 21 h; 3.6 h** | 54.9; 24 h |

Clean ideas per week; median lead time; Isa's hours a week.

**Findings:**
- **Without the envelope, Isa is the ceiling at any volume above today's.** Output caps at 16–18 clean ideas a week and ideas wait two to three weeks. Quality and cost do not change; only speed and volume do.
- **With 80% inside the envelope, the ceiling is gone at 75 ideas a week.** Output matches unlimited attention, on 3.6 hours of hers. The envelope also skips her fixed turnaround, so lead time falls below the reference.
- **Half inside is not enough at 75 a week:** her budget fills again and the slowest tenth of ideas wait over two weeks.
- **The envelope widens on evidence (R28).** The model does not include overturns. In practice, the share inside grows only as Isa's sample confirms the rule ratifications (X23).

### Edge cases (E): challenge tests against blind spots

| Blind spots | Review only | Challenge tests | + exploration 25% |
|---|---|---|---|
| None, steady | 18.8 clean; 0.24 escaped/idea; CFR 12%; $27.8 | 18.3; 0.23; 13%; $33.4 | same |
| Family 18%, steady | 12.8; 0.41; 22%; $49.8 | **14.6; 0.34; 18%; $48.5** | same |
| All-family 18%, steady | 2.9; 0.44; 23%; $148 | 2.8; 0.43; 23%; $169 | 3.0; 0.39; 22%; $154 |
| None, mixed | 18.8; 0.23; 12%; $66.8 | 18.5; 0.23; 13%; $77.6 | same |
| Family 18%, mixed | 13.7; 0.42; 20%; $128 | 13.6; 0.40; 20%; $142 | same |
| All-family 18%, mixed | 5.8; 0.48; 25%; $177 | 5.3; 0.45; 24%; $210 | 5.7; 0.45; 20%; $147 |

Clean ideas per week; escaped defects per idea; change-failure rate; $ per clean idea.

**Findings:**
- **Challenge tests pay where blind spots differ by family.** At the cross-check's reference (18% family blind spots), steady work gets 17% fewer escaped defects, change failures down from 22% to 18%, and 14% more clean output, at no extra cost per clean idea.
- **They cost 16–20% per clean idea where review already catches the defect.** Most remaining escapes are integration and security defects, which CI, the security review and smoke tests own. Hence R26 keeps challenge tests by tier on evidence.
- **On mixed work they change little.** Large, hard ideas fail mostly at integration and interfaces.
- **Model-written tests do not reach blind spots shared by every family.** Challenge tests alone change nothing there. Mechanical exploration at an assumed 25% trims escaped defects by about 11% on steady work. That rate is a guess until C1.20 measures it.

### What the model cannot say

- **Whether originated ideas are worth building.** An originated idea counts like a briefed one. X22 judges them on realised value per dollar against Isa's briefs.
- **Whether rule ratification keeps Isa's intent.** The model's Isa adds delay, not judgment. X23 judges it on her sample's overturn rate.
- **Sealed scenario tests and mutation score.** Not modelled; measured from Phase 1 (M26).

---

## 5. What changes

**Amendment proposed (AR-19):**
- **R26** edge cases are evidence; **R27** self-origination; **R28** the ratification envelope (the mechanism for AR-09b).
- **P12:** the Factory waits to be told.
- **Experiments X21–X23; measures M26–M28;** operating parameters PR-23 to PR-25 [PROPOSED].
- **Cards:** C1.20 (sealed and challenge tests), C1.21 (origination), C1.22 (envelope and attention queue), C2.06 (mutation score), C3.05 (typed propositions). C3.04 now builds on C1.22.

**Isa's to set (AR-09b, OI-10):**
- her weekly attention budget, in hours;
- the envelope's starting bounds and its ceiling.

**Not changed:** the eight institutions, the golden rules, and every touchpoint that is Isa's alone: amendments, standards, governance changes and R13 escalations.

**Takeaway:** sign AR-19 and set the envelope in AR-09b, so the Factory can originate its own ideas without Isa's hours becoming the ceiling.
