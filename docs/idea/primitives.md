# Target architecture: primitives, the library, and load (r12.10)

Stage: design direction (AR-17); rule R25 proposed (AR-18). Probe: [`probes/enterprise/load_probe.py`](../../probes/enterprise/load_probe.py) → `load_probe_results.txt`. The probe's capacities and workload are illustrative assumptions, swept ×0.25 to ×4, and it uses no model spend.

---

## 1. Answer

1. **Every system of record is a composition of a few primitives.** Project management, incident (ITSM), HCM, CRM and ERP are built from:
   - eight primitive record types: Party, Asset, Agreement, Work, Balance, Event, Content, Rule;
   - Relations between them.

   These live in eight primitive stores. Stores are separated physically only where a reason demands it: sensitivity, strict transactions, access pattern, jurisdiction or tenant.
2. **Conveyors and librarians share one library.**
   - **Conveyors:** deterministic engines handle repeated, high-volume, known-shape work and write to the stores.
   - **Librarians:** agents handle varied requests by reading through the catalogue. They never write records directly.
   - **Promotion (R25):** repeated librarian work is turned into conveyors.
3. **For internal knowledge work, storage throughput is not the constraint; agents are.**
   - Up to 100,000 employees, with a payroll run and month-end close in the same month, even a single database peaks at 57%.
   - The first limit is agent capacity and cost: 172 instances at peak against the modelled cap of 48, and about $27,600 a month.
   - Promoting 70% of librarian work cuts that to 52 instances and about $8,300 a month.
4. **Mainframe-scale throughput matters for customer-facing transactions.**
   - At 1,000 customer orders a second, one shared database fails (171–227%), and so does a hash chain written per event (300%).
   - The primitive design copes: three balance-store nodes, and per-domain chains sealed in batches at 3%.
   - At 10,000 orders a second it needs about 23 balance-store nodes and 26 workflow databases. Durable workflow steps for every order are too heavy at that volume; high-volume conveyors should be native engine code.
5. **Batched, per-domain chains remove the blockchain bottleneck.** Tamper evidence costs 3% of one chain's capacity instead of breaking it.

---

## 2. Primitives

| Primitive | What it is | Examples across systems of record |
|---|---|---|
| **Party** | Anyone who acts or is acted on | Employee, customer, vendor, contact, team, agent |
| **Asset** | Anything owned, used or tracked | Laptop, server, product, stock item, licence, software artifact |
| **Agreement** | A commitment between parties, with terms | Employment contract, customer contract, purchase order, SLA, subscription, policy enrolment |
| **Work** | A unit of work with a state machine | Card, task, ticket, incident, case, opportunity, approval |
| **Balance** | A quantity changed only by double entry | Money, leave days, stock, budget, credit |
| **Event** | An append-only fact that something happened | Posting, status change, sign-in, monitoring signal, payment |
| **Content** | Unstructured material | Documents, emails, code, images, notes |
| **Rule** | Policy, runbook, charter, threshold | Approval limits, GDPR and PDPL purposes, leave policy, pricing rules |
| *Relation* | A typed link between any two records | Owns, reports to, depends on, bought, caused |

**Systems of record as compositions:**

| System of record | Party | Asset | Agreement | Work | Balance | Event | Content | Rule |
|---|---|---|---|---|---|---|---|---|
| Project management | • | | | **●** | | • | • | • |
| Incident (ITSM) | • | **●** | • (SLA) | **●** | | **●** | • | • |
| HCM | **●** | • | **●** | • | **●** | • | • | **●** |
| CRM | **●** | • | • | **●** (opportunity, case) | | • | **●** | • |
| ERP | • | **●** | **●** | • | **●** | **●** | • | **●** |

● marks a core primitive for that system; • marks one it uses.

---

## 3. Primitive stores: physical separation only where needed

| Store | Holds | Why it is separate |
|---|---|---|
| **S1 Identity** | Parties, especially people | Personal and special-category data; a key per person for crypto-shredding (right to erasure); residency rules |
| **S2 Balances** | Double-entry quantities | Strict all-or-nothing transactions; peak batches (payroll, month-end close, orders); partitioned by legal entity and account |
| **S3 Work** | Work items and their state machines | High churn; the Factory's own cards live here |
| **S4 Records** | Assets and agreements | Reference data; moderate change |
| **S5 Event log** | Events, with hash chains per domain sealed in batches | Append-only; tamper evidence; feeds the read model |
| **S6 Content** | Documents and artifacts | Object storage; size; retention rules |
| **S7 Policy** | Rules, runbooks, charters | Protected paths; read-mostly; must be versioned and replayable |
| **S8 Read model** | Relations and cross-domain views | Analytical access pattern; context for librarians; never written by agents |

**Further splits, only when a reason applies:**
- by **tenant** (any person or team running its own Factory);
- by **jurisdiction** (UK, KSA, Morocco data residency);
- by **legal entity** (separate books).

The primitives stay the same; only the partition changes.

---

## 4. The library: conveyors, librarians, promotion

| Library | Factory |
|---|---|
| Conveyor belt | Deterministic engines and durable workflows (Hatchet) |
| Shelves | S1–S4, S6 |
| Microfiche and catalogue | S5 event log and S8 read model, with the data catalogue (ownership, classification, lineage) |
| Librarians | Agents in institutional harnesses: read through the catalogue, never write records |
| Library rules | Policy as code (OPA or Cedar) at the gateway and the stores |
| Returns desk | Hand-backs (R21) and conveyor rejects, which become exception cards |

**R25: industrialise the repeated** (amendment proposed, AR-18):
- When a pattern of agent work recurs in a stable shape, a card proposes a deterministic path for it: a workflow, view or engine function.
- The path runs alongside the agents on the same requests. It is adopted through the Release Gate if it matches their answers at lower cost.
- Requests the deterministic path rejects go to agents as exception cards.
- Agents never write records directly; every write goes through a deterministic path.

---

## 5. The stack

[Unverified: tool features as of mid-2026.]

| Job | Tool |
|---|---|
| Conveyor (durable workflows) | **Hatchet**, already in the Factory, under the Ledger; native engine code for high-volume conveyors; Temporal only where strict replay is needed |
| Shelves S1–S4 | **PostgreSQL**, per store; partitioned by tenant, entity or jurisdiction where needed |
| Event log S5 | **Postgres outbox** with per-domain hash chains sealed in batches; Kafka or Redpanda at high event volume |
| Content S6 | Object storage |
| Policy S7 | **OPA** or **Cedar**, in front of every store and the gateway |
| Read model S8 | **DuckDB over Iceberg** (or Delta); Trino or ClickHouse as volume grows |
| Models | The self-hosted gateway (C0.19) |

---

## 6. Load probe results (`load_probe_results.txt`)

**Workload** [assumption]:
- per employee-hour rates for card updates, tickets, monitoring signals, HR questions, leave, CRM interactions, ERP postings and cross-domain reports;
- a monthly payroll run (40 balance postings per employee in four hours);
- month-end close (ERP postings ×10 for two days);
- customer orders at 0, 1,000 or 10,000 a second.

**Capacity** [assumption]:
- 3,000 row writes and 30,000 reads a second per database node;
- 1,000 appends a second for a chain written per event, 100,000 when sealed in batches;
- 2,000 workflow steps a second per workflow database;
- agent instances capped at 48 by vendor rate limits;
- $1.20 per agent hour.

**Busiest hour, internal systems of record only** (no customer orders):

| Employees | One store: database / chain | Silos: busiest database / chain | Primitives: nodes / chain | Agents at peak, 0% promoted → 70% | Agent cost a month |
|---|---|---|---|---|---|
| 1,000 | 1% / 0.3% | 0% / 0.3% | 1 per store / 0% | 2 → 1 | $276 → $83 |
| 10,000 | 6% / 3% | 2% / 3% | 1 per store / 0% | 18 → 6 | $2,764 → $829 |
| 100,000 | 57% / 32% | 19% / 28% | 1 per store / 0.3% | **172 → 52** (cap 48) | $27,639 → $8,292 |

**Busiest hour with customer orders:**

| Orders a second | One store | Silos | Primitives |
|---|---|---|---|
| 1,000 | Database 171–227%, chain 300%: **fails** | Orders silo 170–179%, chain 300%: **fails** | 3 balance-store nodes, chain 3%, 3 workflow databases |
| 10,000 | **Fails** (database about 1,700%) | **Fails** | About 23 balance-store nodes, chain 30%, 26 workflow databases |

**Sensitivity:**
- **Capacities ×0.25:** at 100,000 employees and 1,000 orders a second, the workflow engine becomes the largest component (12 databases).
- **Capacities ×4:** everything fits on single nodes.
- **Agents:** the need does not change, because it is set by workload, not capacity.

**Caveat:** silos are modelled as single nodes. A real orders system would be sharded. The lesson stands: the high-volume domain needs partitioning and batched chains whatever the design.

---

## 7. What this means

1. **Agents are the scaling constraint for internal knowledge work.** Raise vendor rate limits per route (AR-10), keep elastic capacity (R14), and promote repeated work (R25).
2. **Plan for mainframe-class volume only where customers transact.** Partition the balance store, seal chains in batches, and use native engine code rather than workflow steps per order.
3. **Partition the balance store by account and legal entity from the start.** [Inference] A single hot account, such as one cash account, cannot be spread across nodes; design postings to avoid it.
4. **The primitive design is the only one of the three that passes every case.** One store and silos both fail at customer-transaction volume.

---

## 8. Load tiers (Isa, 1 Oct 2026)

| Tier | What | Volume | Binding constraint | Architecture |
|---|---|---|---|---|
| **T1 Agent interactions** | Librarian requests and agent-to-agent hand-offs | Lowest | **Cost and vendor rate limits** (the probe's first limit at scale), not storage | Gateway, elastic capacity (R14), spend cap (R16), promotion (R25) |
| **T2 Deterministic systems of record** | Project management, incident, HCM, CRM, ERP: postings, state changes, payroll, close | Middle | Peak batches (payroll, month-end close) | **This design:** Postgres per primitive store, Hatchet, outbox event log with batched chains, OPA or Cedar, DuckDB over Iceberg |
| **T3 High-throughput transactions** | Customer-facing, mainframe-class: orders, payments, many per second | Highest | Transactions per second, hot accounts | **Deferred (OI-19):** a separate architecture when a real domain needs it |

- **Tiers are set by measured load, not by department.** [PROPOSED] A domain enters T3 when its busiest store needs more than one node at 60% utilisation at peak, or its batched hash chain passes 50%, as measured live. A domain can move between tiers; its primitives stay the same.
- **Agents stay off the T3 transaction path.** They meet T3 only as librarians, through the read model, and on exceptions.

**Seams to keep now, so T3 can be added later without rework:**
1. **Keys on every write:**
   - an idempotency key, so a retried write never doubles;
   - a partition key (tenant, legal entity, account).
2. **One event contract:** every write reaches the Ledger through the outbox, in the same event format at every tier.
3. **No transaction spans two domains.** Cross-domain changes are sagas.
4. **One way in for agents:** they reach data only through the gateway, policy engine and read model.
5. **Postings avoid hot rows.** No single account takes every write.

**Candidates for T3 when it is needed** [Unverified; not a decision]:
- purpose-built ledger databases;
- distributed SQL;
- stream processing on Kafka or Redpanda.

The choice is made on measured load, through the Release Gate.

**Takeaway:** T1 and T2 run on this design now. T3 is deferred, and five seams kept today let it be added without rework.
