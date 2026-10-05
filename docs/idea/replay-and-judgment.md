# Recorded behaviour, lessons, rights and outcomes (r12.12)

Stage: amendment AR-20, signed by Isa on 5 Oct 2026. Code: [`probes/value-stream/replay.py`](../../probes/value-stream/replay.py) → `replay_results.txt`, 8 seeds per cell. All results are synthetic. The new mechanism is off by default, and with it off the model reproduces every earlier result (tests pass).

**Isa's direction, 5 Oct 2026:** build AR-20 with option A: the regression set is recorded live use, never a lab set. The voice front end serves both Isa and EvryMynd users, in English and Arabic. EvryMynd will join as a front end with sovereign memory and an agent council, carried by the Factory or through interfaces such as Cowork.

**Sources mined:** Aakash Gupta's harness-engineering guide (its eight components; the rest of the article could not be read here); a talk on recorded-session testing (Meticulous, identified from a third-party note; [Unverified]); and an analysis written for EvryMynd on preserving how a customer works.

**Configuration:**
- the institutions;
- the elastic Scaler, with held demand, a 15-minute target and a time value of $0.5 an hour;
- R21 hand-backs and R17 at 25% coupling;
- the seven-model menu.

---

## 1. Answer

1. **Recorded behaviour is the strongest check modelled so far (R29).** At 50% coverage it cuts escaped defects by 26–46% in every case, and by 39–44% in blind spots shared by every family, where model-written tests cut 0–11%. Because replay uses compute, not model time, cost per clean idea falls in most cases.
2. **Judgment compounds only if corrections are kept (R30).** An approved correction becomes a scoped lesson with an owner, a source and a review date. It survives every model swap. It is not modelled; X26 judges it live.
3. **Nothing leaves the Factory without the right to send it (R31).** Outward actions are ask by default; spending, signing and regulated claims are never allowed without Isa or the owning user.
4. **The Council is marked on outcomes, not only on approval (R32),** and must beat a single model (X24). In the model its edge is real but modest: 20–35% fewer missing requirements, up to 8% more clean output, at similar cost.

---

## 2. What was added to the model

| Mechanism | Rule in the model | Status |
|---|---|---|
| Replay at merge (R29) | After CI, a logic, integration or interface defect is caught at 25% or 50% (coverage × detection), blind spots included: the oracle is recorded behaviour, not a model | Rate **assumed**, swept; no measured coverage yet. Recording and replay compute are **not costed** |
| Single-model framing (X24) | One Inquiry analyst and no Council round, against two analysts and one round | Uses the existing organisation settings |

---

## 3. Results

### Replay (P)

| Blind spots, work | Review only | Challenge tests (R26) | Replay 25% | Replay 50% |
|---|---|---|---|---|
| None, steady | 18.8 clean; 0.24 escaped; CFR 12%; $27.8 | 18.3; 0.23; 13%; $33.4 | 18.6; 0.19; 11%; $28.3 | **20.9; 0.13; 8%; $24.6** |
| Family 18%, steady | 13.1; 0.41; 21%; $49.1 | 15.0; 0.31; 16%; $49.4 | 15.1; 0.34; 17%; $40.6 | **16.7; 0.22; 13%; $36.1** |
| All-family 18%, steady | 2.4; 0.45; 22%; $174 | 2.9; 0.40; 23%; $165 | 2.7; 0.35; 20%; $144 | **3.6; 0.25; 14%; $111** |
| None, mixed | 18.6; 0.23; 12%; $66.4 | 18.5; 0.23; 13%; $77.6 | 19.2; 0.20; 10%; $63.4 | **19.4; 0.17; 9%; $55.2** |
| Family 18%, mixed | 14.3; 0.41; 20%; $117 | 13.5; 0.40; 19%; $145 | 14.4; 0.38; 20%; $118 | **15.6; 0.27; 15%; $77.8** |
| All-family 18%, mixed | 5.5; 0.49; 24%; $157 | 5.7; 0.49; 23%; $165 | 5.6; 0.42; 21%; $155 | **6.0; 0.30; 16%; $140** |

Clean ideas per week; escaped defects per idea; change-failure rate; $ per clean idea.

**Findings:**
- **Replay reaches what models cannot.** With blind spots shared by every family, it cuts escaped defects by 44% (steady) and 39% (mixed) at 50%, and change failures from 22–24% to 14–16%. Challenge tests manage 0–11% there.
- **It pays everywhere at 50%.** Fewer escapes mean fewer incidents and hotfixes, so cost per clean idea falls 11–36%, and clean output rises 4–50%. At 25% it is cost-neutral or cheaper.
- **It does not restore missing intent.** With all-family blind spots, about 19% of requirements are never captured, and clean output stays at 3–6 a week whatever the checks. Replay catches changed behaviour, not requirements no one named. That gap belongs to human-ratified acceptance criteria and to lessons (R30).
- **Coverage is the lever.** Going from 25% to 50% gains as much as, or more than, going from none to 25%. C1.23 must measure coverage from day one.

### The Council against a single model (C)

| Work, blind spots | Institutions: clean / missing requirements / $ | Single model framing alone |
|---|---|---|
| Steady, none | 18.8 / 0.8% / $27.8 | 18.6 / 1.0% / $29.5 |
| Steady, family 18% | 13.1 / 2.6% / $49.1 | 12.1 / 4.0% / $50.3 |
| Mixed, none | 18.6 / 1.1% / $66.4 | 18.6 / 1.7% / $76.3 |
| Mixed, family 18% | 14.3 / 3.4% / $117 | 13.2 / 4.6% / $113 |

**Findings:**
- **The Council cuts missing requirements by 20–35%** and adds up to 8% clean output where blind spots differ by family. Cost per clean idea is within ±13%, and lower in three of four cases.
- **The edge is modest, so it must be shown live.** The model values a missed requirement but not Isa's review time or a material omission found late. X24 judges those.

### What the model cannot say
- **Recording and replay cost.** Compute, storage and redaction are not costed.
- **Lessons, decision rights and outcome credit.** Not modelled; judged live by X26, M31 and X27.
- **Voice accuracy in Arabic dialects.** Measured per dialect in C2.07, not assumed.

---

## 4. What changes

**Signed (AR-20, 5 Oct 2026):**
- **R29** recorded behaviour is the oracle (option A); **R30** lessons from corrections; **R31** decision rights; **R32** dissent credited by outcome.
- **P13** judgment does not compound; **P14** outward actions are ungoverned.
- **Experiments X24–X27; measures M29–M33;** parameters PR-26 to PR-28 [PROPOSED].
- **Cards:**
  - C1.23 replay;
  - C1.24 lessons;
  - C1.25 decision rights;
  - C2.07 voice front end, English and Arabic;
  - C3.06 dissent credit;
  - C3.07 the Council against a single model.
- **Direction:** EvryMynd joins as a front end (OI-20); every lesson, right and outcome carries an owner from the first card.

**Blocked until cleared:**
- **C1.23 and C2.07:** consent and recording law (OI-21, the counsel brief).
- **C2.07:** vendor terms for speech-to-text and voice providers (AR-10), and where each route processes data (OI-14).

**Takeaway:** brief counsel on OI-21 now; replay is the highest-value check in the design, and it cannot start until recording is cleared.
