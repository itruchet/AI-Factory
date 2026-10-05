# Carry-across prompt: prototype build queue into the Ideas queue

Paste everything below the line into the Ideas queue routine session, on the machine that runs the Factory.

---

**Prototype build queue: load it into the Ideas queue, ahead of the backlog, and start with "stay up".**

Isa decided on 5 Oct 2026 that the Factory is a private alpha prototype with one user, Isa. Product comes first. It must stay up and work end to end for an investor demo before any governance, risk or compliance work. Today it falls over more often than it stays up, held together by manual workarounds.

**Source of truth**
- Repository `itruchet/AI-Factory`, branch `claude/edge-case-testing-ideation-hvr7eq` (draft PR #1).
- `pack/CARDS.md` opens with "Build queue: private alpha prototype". Each card's full scope and acceptance criteria follow further down the same file.
- The machine-readable copy is the `build_queue` key in `pack/factory-pack.json`: `now` holds 27 cards in order, `later` holds 30 parked cards.

**Do this**
1. Pull that branch and read the build queue.
2. Add the 27 `now` cards to the Ideas queue in this order, at the front, ahead of the existing backlog. Tag each one `prototype-build-queue`. Give each its scope and acceptance criteria from `CARDS.md`, built in the minimal form stated below. Do not load the 30 `later` cards.
3. Add no gates. No card waits on an approval, a phase exit, consent, redaction, counsel or vendor terms. The only control is a hard monthly spending cap (C1.15). API keys stay in the environment, on Isa's own accounts.
4. The existing backlog (about 1,402 ideas carded but not started at last count) goes behind the build queue. Do not delete or re-triage it; Isa decides that later.
5. Start C0.20 now:
   - From the Factory's own logs and run history for the last 14 days, list every failure and every manual workaround: what broke, how it was fixed, and how long it took.
   - Rank the causes and fix the top three at the root.
   - Turn the most frequent manual workaround into code.
   - Merge no new feature while a top-three cause is open, unless the feature removes one.

**The queue, in order**

1. **C0.20 Stay up: kill the top failure causes and manual workarounds**: Log failures and workarounds; fix the top three causes weekly.
2. **C0.16 Live operation inside the Factory: detect, restore, hotfix**: Alert and one-step revert; hotfix as an ordinary card.
3. **C1.23 Recorded behaviour as the oracle: record, select, replay**: Record Isa's own use; replay before every merge; show differences.
4. **C0.17 The pull queue: the collective pulls from day one**: One pull queue the agents work from.
5. **C0.19 Self-hosted model gateway: any model, any route, by configuration**: One gateway; keys in the environment, on Isa's own accounts.
6. **C1.03 API access for the seven-model menu, under the data rule**: The models Isa has accounts for; no vendor-terms gate.
7. **C0.03 Append-only Ledger beside today's operational state**: An append-only log of what happened.
8. **C0.04 Adapters record usage for every model invocation**: Tokens and cost per call, for cost-per-idea numbers.
9. **C0.18 The harness kernel: one for every institution**: One shared harness: tools, fresh context, budgets.
10. **C1.01 Card schema: tier, requirements, dependencies, interfaces, contract**: Tier, requirement, contract with tests.
11. **C1.02 Tier-setting rules in Planning**: Simple tier rules.
12. **C1.17 Review**: Tests first, then a model of another family reviews.
13. **C1.11 Family independence**: No model reviews its own family's work.
14. **C1.05 Licences and pull: hardest first, oldest first**: Hardest-first pull by licence.
15. **C1.08 Attribution with evidenced reason codes**: A reason on every rejection.
16. **C1.06 The ladder: promotion, two-speed demotion, fast track**: Promotion and demotion from the record.
17. **C1.10 No orphan tiers, with recorded waivers; escalation optional**: No tier left without an agent.
18. **C1.15 Burn cap and monthly ceiling**: A hard monthly spending cap; nothing else.
19. **C3.01 Inquiry**: Two models frame the brief blind.
20. **C3.02 Deliberation Council**: One synthesis round; Isa ratifies.
21. **C3.03 Planning Chamber**: Brief to cards, with one red-team pass.
22. **C0.09 Idea value ledger: baseline at intake, actuals as they happen**: Cost and time per idea, from the log.
23. **C3.07 The Council against a single-model baseline**: Council against one model on the same briefs: the investor proof point.
24. **C1.24 Lessons from corrections: scoped, approved, expiring**: Isa's corrections become reusable lessons.
25. **C1.21 Self-origination: Ledger signals become briefs**: A weekly standing brief plus incident signals.
26. **C2.07 Voice front end: live speech, English and Arabic**: Live voice in English and Arabic, for Isa.
27. **C3.08 Investor demo path: one idea to working software, on demand**: The investor demo, end to end, five clean runs.

**Report back to Isa in one message**
- Each of the 27 cards with its queue position.
- The top three failure causes from C0.20, each with its evidence.
- What you fixed first, and what is next.
- Anything that blocked loading the queue.
