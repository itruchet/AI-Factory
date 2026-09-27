-- Factory Ledger: reference schema for the constitutional architecture.
-- Companion to docs/architecture/constitutional-factory.md r3 (sections 5-7, 11-16).
-- Kernel functions that write DERIVED rows and draws: kernel/allocation.py.
--
-- Design rules enforced here:
--   1. Ledger tables are append-only. UPDATE and DELETE abort (Article 2).
--   2. FACT, ASSERTION and DERIVED values live in separate tables (Article 3).
--   3. Every model output references the context manifest it was produced under,
--      so exposure and independence are computed, never self-declared (Articles 6-7).
--   4. Every event names the institution it belongs to; rules come from a
--      human-ratified charter version. There is no actor in the control path:
--      the kernel is these constraints plus pure functions whose every output
--      is replayable from (rows, charter_hash, seed).
--   5. Mutable operational state lives only in projection tables (suffix _state),
--      which must be rebuildable from the ledger.
--
-- Target: SQLite >= 3.35, WAL mode, on a native Linux filesystem (not /mnt/c).

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Identity and charters
-- ---------------------------------------------------------------------------

-- An actor is anything that can author an event. Model actors are execution
-- configurations (model x version x effort), not vendors.
CREATE TABLE actor (
    actor_id        TEXT PRIMARY KEY,
    kind            TEXT NOT NULL CHECK (kind IN ('model_config', 'human', 'kernel', 'tool')),
    family          TEXT,           -- lineage label, set by a human; used for independence
    model_id        TEXT,           -- provider model identifier as configured
    model_version   TEXT,           -- version string; a change creates a new actor
    effort          TEXT,           -- reasoning effort level, adapter-specific
    resource_id     TEXT REFERENCES resource(resource_id),
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Constitution and per-institution charters. Every rule and tunable number
-- the kernel applies lives here, including per task class economics
-- (value, fail_cost, tau, z, time_cost). Decisions cite a charter hash.
CREATE TABLE charter_version (
    charter_hash    TEXT PRIMARY KEY,
    institution     TEXT NOT NULL CHECK (institution IN (
                        'constitution', 'inquiry', 'council', 'planning', 'market',
                        'court', 'audit', 'release', 'ledger')),
    parent_hash     TEXT REFERENCES charter_version(charter_hash),
    rules_json      TEXT NOT NULL,          -- roles, eligibility, memory rights, procedure, budgets
    ratified_by     TEXT NOT NULL REFERENCES actor(actor_id),  -- must be a human actor
    ratified_at     TEXT NOT NULL,
    rationale       TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- The ledger proper
-- ---------------------------------------------------------------------------

-- Hash-chained event log. Every material action is one row.
CREATE TABLE event (
    seq             INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id        TEXT NOT NULL UNIQUE,
    ts              TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    institution     TEXT NOT NULL CHECK (institution IN (
                        'inquiry', 'council', 'planning', 'market', 'court',
                        'audit', 'release', 'ledger', 'human')),
    kind            TEXT NOT NULL,          -- e.g. card.assigned, lease.granted, evidence.recorded
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    subject_id      TEXT NOT NULL,          -- idea, card, lease, challenge, audit sample...
    charter_hash    TEXT REFERENCES charter_version(charter_hash),
    payload_json    TEXT NOT NULL,
    supersedes      TEXT REFERENCES event(event_id),  -- revision without rewrite
    prev_hash       TEXT NOT NULL,
    hash            TEXT NOT NULL UNIQUE    -- sha256(prev_hash || canonical(row))
);
CREATE INDEX event_subject ON event(subject_id, seq);
CREATE INDEX event_kind ON event(kind, seq);

-- What an actor was shown. Independence and exposure derive from this.
CREATE TABLE context_manifest (
    manifest_hash   TEXT PRIMARY KEY,
    items_json      TEXT NOT NULL,          -- list of {kind, ref, hash, author_actor_id}
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- Factory-observed facts: tool output, git state, usage, timings.
CREATE TABLE observation (
    observation_id  TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    source          TEXT NOT NULL CHECK (source IN ('tool', 'adapter', 'git', 'kernel', 'provider')),
    kind            TEXT NOT NULL,          -- test_result, build, tokens_used, throttle, commit...
    subject_id      TEXT NOT NULL,
    value_json      TEXT NOT NULL,
    artifact_hash   TEXT                    -- raw output stored content-addressed
);

-- Model or human claims. Never authoritative; scored later against observations.
CREATE TABLE assertion (
    assertion_id    TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    manifest_hash   TEXT REFERENCES context_manifest(manifest_hash),
    subject_id      TEXT NOT NULL,
    kind            TEXT NOT NULL,          -- p_success, expected_cost, difficulty, verdict, risk...
    value_json      TEXT NOT NULL,
    confidence      REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1))
);
CREATE INDEX assertion_scoring ON assertion(actor_id, kind);

-- Values the kernel computes from facts with a versioned pure function.
-- Reproducible from (inputs, charter_hash); neither fact nor opinion.
CREATE TABLE derived (
    derived_id      TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    kind            TEXT NOT NULL,          -- posterior, eligibility, shadow_price, independence_level, risk_class...
    subject_id      TEXT NOT NULL,
    value_json      TEXT NOT NULL,
    function_ref    TEXT NOT NULL,          -- module@git_sha
    charter_hash    TEXT NOT NULL REFERENCES charter_version(charter_hash)
);

-- ---------------------------------------------------------------------------
-- Intent, plan and cards (immutable versions)
-- ---------------------------------------------------------------------------

CREATE TABLE proposition (
    proposition_id  TEXT PRIMARY KEY,
    idea_id         TEXT NOT NULL,
    institution     TEXT NOT NULL CHECK (institution IN ('inquiry', 'council', 'planning')),
    round           INTEGER NOT NULL,
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    manifest_hash   TEXT NOT NULL REFERENCES context_manifest(manifest_hash),
    anon_label      TEXT NOT NULL,          -- per-idea random label shown to peers; identity stays here
    kind            TEXT NOT NULL,          -- interpretation, hypothesis, assumption, risk, objection...
    body            TEXT NOT NULL,
    confidence      REAL,
    responds_to     TEXT REFERENCES proposition(proposition_id),
    stance          TEXT CHECK (stance IS NULL OR stance IN ('support', 'challenge', 'amend', 'withdraw', 'question'))
);

CREATE TABLE requirement (
    requirement_id  TEXT PRIMARY KEY,
    idea_id         TEXT NOT NULL,
    body            TEXT NOT NULL,
    source_props    TEXT NOT NULL           -- JSON list of proposition_ids (traceability)
);

CREATE TABLE card_version (
    card_id         TEXT NOT NULL,
    version         INTEGER NOT NULL,
    idea_id         TEXT NOT NULL,
    requirement_ids TEXT NOT NULL CHECK (json_array_length(requirement_ids) >= 1),
    depends_on      TEXT NOT NULL DEFAULT '[]',
    kind            TEXT NOT NULL,          -- assertion by planner
    value_points    REAL NOT NULL,          -- ratified at plan; children of a split sum to parent
    contract_hash   TEXT NOT NULL,          -- hash of acceptance contract incl. locked tests
    locked_paths    TEXT NOT NULL DEFAULT '[]',
    file_scope      TEXT NOT NULL DEFAULT '[]',
    body            TEXT NOT NULL,
    created_event   TEXT NOT NULL REFERENCES event(event_id),
    PRIMARY KEY (card_id, version)
);

-- ---------------------------------------------------------------------------
-- Work market
-- ---------------------------------------------------------------------------

-- Seeded draws: every stochastic kernel decision (assignment, seat).
-- Seed, candidates and propensity are recorded so any draw can be replayed
-- and any alternative policy evaluated off-policy by inverse weighting.
CREATE TABLE draw (
    draw_id         TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    purpose         TEXT NOT NULL CHECK (purpose IN (
                        'assignment', 'synthesizer', 'decomposer', 'reconciler', 'red_team',
                        'helper', 'reviewer', 'replicator', 'expert_witness', 'auditor',
                        'approver', 'dissenter')),
    subject_id      TEXT NOT NULL,
    task_class      TEXT NOT NULL,
    candidates_json TEXT NOT NULL,          -- eligible configs with posterior params used
    prices_json     TEXT NOT NULL,          -- shadow prices in force for the window
    rng_seed        TEXT NOT NULL,
    winner          TEXT NOT NULL REFERENCES actor(actor_id),
    propensity      REAL NOT NULL CHECK (propensity > 0 AND propensity <= 1)
);

-- The assignee's response to a kernel assignment. Declines are data, not failures.
CREATE TABLE assignment_response (
    response_id     TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    draw_id         TEXT NOT NULL REFERENCES draw(draw_id),
    card_id         TEXT NOT NULL,
    card_version    INTEGER NOT NULL,
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    response        TEXT NOT NULL CHECK (response IN (
                        'accept', 'decline', 'request_clarification', 'propose_split', 'request_help')),
    reason          TEXT,
    FOREIGN KEY (card_id, card_version) REFERENCES card_version(card_id, version)
);

-- Seats in Council, Planning, Court, Audit and Release, filled by kernel draws.
CREATE TABLE seat (
    seat_id         TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    institution     TEXT NOT NULL CHECK (institution IN ('council', 'planning', 'court', 'audit', 'release')),
    role            TEXT NOT NULL,
    subject_id      TEXT NOT NULL,
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    draw_id         TEXT REFERENCES draw(draw_id)   -- NULL only for open-standing challengers
);

CREATE TABLE lease (
    lease_id        TEXT PRIMARY KEY,
    response_id     TEXT NOT NULL REFERENCES assignment_response(response_id),  -- must be 'accept'
    card_id         TEXT NOT NULL,
    card_version    INTEGER NOT NULL,
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    worktree_ref    TEXT NOT NULL,          -- git branch bound to this lease
    granted_event   TEXT NOT NULL REFERENCES event(event_id)
);

-- ---------------------------------------------------------------------------
-- Capacity ledger
-- ---------------------------------------------------------------------------

CREATE TABLE resource (
    resource_id     TEXT PRIMARY KEY,
    provider        TEXT NOT NULL,
    window_kind     TEXT NOT NULL CHECK (window_kind IN ('fixed_reset', 'rolling', 'credit_pool', 'local')),
    window_seconds  INTEGER,
    max_concurrency INTEGER,
    amortized_cost  REAL                    -- subscription fee per window, for AUW per amortized $
);

-- Adapter-observed capacity facts. Participants cannot write here.
CREATE TABLE capacity_observation (
    capacity_obs_id TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    resource_id     TEXT NOT NULL REFERENCES resource(resource_id),
    kind            TEXT NOT NULL,          -- usage, throttle_429, quota_header, reset, gpu_util, outage
    value_json      TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Assurance and audit
-- ---------------------------------------------------------------------------

CREATE TABLE evidence (
    evidence_id     TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    card_id         TEXT NOT NULL,
    card_version    INTEGER NOT NULL,
    candidate_ref   TEXT NOT NULL,          -- git sha under evaluation
    class           TEXT NOT NULL CHECK (class IN ('deterministic', 'model_review', 'reproduction', 'human')),
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    manifest_hash   TEXT REFERENCES context_manifest(manifest_hash),
    verdict         TEXT NOT NULL CHECK (verdict IN ('pass', 'fail', 'concern', 'inconclusive')),
    detail_hash     TEXT
);

CREATE TABLE challenge (
    challenge_id    TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    evidence_id     TEXT REFERENCES evidence(evidence_id),
    card_id         TEXT NOT NULL,
    candidate_ref   TEXT NOT NULL,
    actor_id        TEXT NOT NULL REFERENCES actor(actor_id),
    repro_ref       TEXT,                   -- executable reproduction; NULL means argued only
    claim           TEXT NOT NULL
);

CREATE TABLE audit_sample (
    sample_id       TEXT PRIMARY KEY,
    event_id        TEXT NOT NULL REFERENCES event(event_id),
    card_id         TEXT NOT NULL,
    card_version    INTEGER NOT NULL,
    stratum         TEXT NOT NULL,
    reason          TEXT NOT NULL CHECK (reason IN ('random', 'risk', 'adaptive', 'targeted', 'rejection', 'planted_defect', 'collusion_pattern', 'human')),
    selection_prob  REAL NOT NULL CHECK (selection_prob > 0 AND selection_prob <= 1),
    rng_seed        TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Append-only enforcement (Article 2)
-- ---------------------------------------------------------------------------

CREATE TRIGGER event_no_update BEFORE UPDATE ON event
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: event'); END;
CREATE TRIGGER event_no_delete BEFORE DELETE ON event
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: event'); END;

CREATE TRIGGER observation_no_update BEFORE UPDATE ON observation
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: observation'); END;
CREATE TRIGGER observation_no_delete BEFORE DELETE ON observation
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: observation'); END;

CREATE TRIGGER assertion_no_update BEFORE UPDATE ON assertion
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: assertion'); END;
CREATE TRIGGER assertion_no_delete BEFORE DELETE ON assertion
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: assertion'); END;

CREATE TRIGGER derived_no_update BEFORE UPDATE ON derived
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: derived'); END;
CREATE TRIGGER derived_no_delete BEFORE DELETE ON derived
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: derived'); END;

CREATE TRIGGER card_version_no_update BEFORE UPDATE ON card_version
BEGIN SELECT RAISE(ABORT, 'cards are immutable: create a new version'); END;
CREATE TRIGGER card_version_no_delete BEFORE DELETE ON card_version
BEGIN SELECT RAISE(ABORT, 'cards are immutable: create a new version'); END;

CREATE TRIGGER capacity_obs_no_update BEFORE UPDATE ON capacity_observation
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: capacity_observation'); END;
CREATE TRIGGER capacity_obs_no_delete BEFORE DELETE ON capacity_observation
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: capacity_observation'); END;

CREATE TRIGGER evidence_no_update BEFORE UPDATE ON evidence
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: evidence'); END;
CREATE TRIGGER evidence_no_delete BEFORE DELETE ON evidence
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: evidence'); END;

CREATE TRIGGER charter_no_update BEFORE UPDATE ON charter_version
BEGIN SELECT RAISE(ABORT, 'charter versions are immutable: ratify a new version'); END;
CREATE TRIGGER charter_human_only BEFORE INSERT ON charter_version
WHEN (SELECT kind FROM actor WHERE actor_id = NEW.ratified_by) IS NOT 'human'
BEGIN SELECT RAISE(ABORT, 'only a human may ratify a charter'); END;

CREATE TRIGGER draw_no_update BEFORE UPDATE ON draw
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: draw'); END;
CREATE TRIGGER draw_no_delete BEFORE DELETE ON draw
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: draw'); END;
CREATE TRIGGER response_no_update BEFORE UPDATE ON assignment_response
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: assignment_response'); END;
CREATE TRIGGER response_no_delete BEFORE DELETE ON assignment_response
BEGIN SELECT RAISE(ABORT, 'ledger is append-only: assignment_response'); END;

-- A lease can only follow an accepted assignment.
CREATE TRIGGER lease_requires_accept BEFORE INSERT ON lease
WHEN (SELECT response FROM assignment_response WHERE response_id = NEW.response_id) IS NOT 'accept'
BEGIN SELECT RAISE(ABORT, 'lease requires an accepted assignment'); END;

-- ---------------------------------------------------------------------------
-- Projections (mutable, rebuildable from the ledger)
-- ---------------------------------------------------------------------------

CREATE TABLE card_state (
    card_id         TEXT PRIMARY KEY,
    version         INTEGER NOT NULL,
    state           TEXT NOT NULL CHECK (state IN (
                        'BLOCKED', 'READY', 'OFFERED', 'LEASED', 'SUBMITTED', 'GATING',
                        'REWORK', 'ACCEPTED', 'INTEGRATED', 'STAGED', 'OBSERVED', 'PROMOTED',
                        'WAITING_CLARIFICATION', 'WAITING_HUMAN', 'REPLAN', 'SUPERSEDED', 'ABANDONED')),
    risk_class      TEXT NOT NULL CHECK (risk_class IN ('R0', 'R1', 'R2', 'R3')),
    attempts        INTEGER NOT NULL DEFAULT 0,
    ready_since     TEXT,
    last_event_seq  INTEGER NOT NULL
);

CREATE TABLE lease_state (
    lease_id        TEXT PRIMARY KEY REFERENCES lease(lease_id),
    card_id         TEXT NOT NULL,
    state           TEXT NOT NULL CHECK (state IN ('ACTIVE', 'SUBMITTED', 'SURRENDERED', 'EXPIRED', 'REVOKED')),
    heartbeat_at    TEXT NOT NULL,
    expires_at      TEXT NOT NULL,
    rework_used     INTEGER NOT NULL DEFAULT 0
);

-- One active lease per card, enforced by the database, not by convention.
CREATE UNIQUE INDEX one_active_lease_per_card
    ON lease_state(card_id) WHERE state = 'ACTIVE';
