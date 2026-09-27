"""Value-stream model: every step from idea to live, and organisations as mappings of steps to seats.

The r10 model followed the institutions' own tasks and stopped at the Release
Gate. Real delivery has more steps, and every organisation, the constitutional
one included, has to cover all of them. Here an organisation is only a mapping
of those steps onto seats (models), plus a few rules. That lets one engine
compare one role per step, several steps per role, several roles (a committee)
per step, pools of models per step, no organisation at all, or a new
organisation found by search.

The steps (idea to live)
  discover     capture the requirements (Inquiry; K analysts, commit-before-view)
  challenge    critique the framing (Council; optional rounds)
  [human]      ratify the intent
  design       architecture: its quality q changes card difficulty, integration
               defects and merge conflicts for the whole idea
  plan         map requirements to cards (Planning)
  plan_check   red-team the plan for missed requirements (optional)
  [human]      ratify the plan
  build        implement a card with unit tests (Work Market)
  review       code review (Assurance Court; 1 or 2 reviewers)
  security     security review of sensitive cards (optional)
  integrate    merge and CI: conflicts with work in flight, integration defects
  audit        sample re-check of accepted cards (optional)
  qa           acceptance test of the whole idea against its intent (Release Gate)
  release      approve the release (Release Gate)
  [deploy]     automated: staging, smoke test (may roll back), production
  operate      live: an escaped defect may cause an incident; someone restores
               service, then a hotfix card runs build, review, integrate, deploy

Defects have types: logic (tests, review, QA), security (security review,
partly review), integration (CI, QA, smoke). Missing intent is caught by QA.
A checker of its own work, or of work by the same model, catches SELF_CATCH as
much (correlated blind spots). Pass chance for any step is the r10 curve
p = logistic(0.12 x (Coding Index - difficulty) + ln 3).

Measured, per week after a one-week warm-up (DORA-style where they apply):
  clean ideas     live with every requirement delivered and no escaped defect
  ideas live      deployment frequency of ideas; hotfix deploys counted apart
  lead time       idea to live (median hours)
  change failure  share of idea deploys that cause at least one incident
  restore time    mean hours from incident to service restored
  $ per clean     API cost (token model of ../portfolio6) per clean idea
  bottleneck      the step whose tasks wait longest

Elasticity (r12). Seats need not be fixed. With open arrivals (ideas arrive
over time, in varying sizes and difficulty) a Scaler, i.e. plain rules in the
Ledger and no agent, starts and stops model instances every 15 minutes:
  1. price every queued task on every model licensed for it whose pass
     chance clears the quality floor: expected cost = $/busy hour x hours /
     pass chance; the cheapest wins (none clears it: the most capable);
  2. a model's target = its busy instances + ceil(its queued hours / DRAIN_H);
  3. clamp to the model's min and max (vendor rate limits);
  4. if the burn of the targets exceeds the cap ($/hour), trim the most
     expensive model first;
  5. start the shortfall now (ready after SPINUP_H); stop instances idle for
     COOL_H beyond the target;
  6. cost-band pull: an instance takes a task only if its expected cost is
     within BAND x the cheapest qualified model's, unless the task has
     waited BAND_WAIT_H (so expensive instances do not soak up cheap work).
Instances of one model are one model for independence: a model never checks
its own model's work, so a single-model swarm checks itself.

Every number below is an assumption, named here and listed in
docs/idea/value-stream.md. All outcomes are synthetic: they rank designs.
"""

from __future__ import annotations

import heapq
import math
import random
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "institutions"))
sys.path.insert(0, str(HERE.parent / "portfolio6"))
import factory_sim as fs  # noqa: E402  (Config, p_pass, population pool)
import select6 as s6      # noqa: E402  (named candidates, token cost model)

# ---------------------------------------------------------------- assumptions
R_REQ, REQ_BASE, REQ_SPREAD = 8, 50.0, 8.0
CARDS_PER_REQ = (1, 2, 2, 3)
CARD_MIX = {"easy": 0.45, "mid": 0.35, "hard": 0.20}
CARD_RANGE = {"easy": (10, 30), "mid": (30, 57), "hard": (57, 75)}
CARD_HOURS = {"easy": 0.5, "mid": 1.0, "hard": 2.5}
CARD_TOKENS = {"easy": 30e3, "mid": 80e3, "hard": 200e3}
STEP_HOURS = {"discover": 0.5, "challenge": 0.3, "design": 0.8, "plan": 1.0, "plan_check": 0.5, "qa": 0.8,
              "release": 0.3, "operate": 1.0, "integrate": 0.2}
STEP_TOKENS = {"discover": 40e3, "challenge": 25e3, "design": 60e3, "plan": 80e3, "plan_check": 40e3, "qa": 60e3,
               "release": 20e3, "operate": 60e3, "integrate": 20e3}
CARD_SHARE = {"review": 0.3, "security": 0.3, "audit": 0.5}          # effort relative to the card
DESIGN_D, QA_D, RELEASE_D, INTEGRATE_D, SECURITY_D = 60.0, 55.0, 50.0, 40.0, 65.0
DESIGN_PENALTY = 10.0          # a poor design (q -> 0) makes every card up to 10 points harder
TEST_CATCH = 0.50              # unit tests catch a logic defect
CI_CATCH = 0.60                # CI catches an integration defect
INT_BASE = 0.10                # integration defect chance per card with a perfect design (x3 at q = 0)
CONFLICT_K = 0.005             # merge conflict: 1 - exp(-k x (2 - q) x cards being built)
SEC_SHARE = 0.25               # share of cards touching sensitive code
SEC_INJECT = 0.50              # a sensitive card gets a security flaw: 0.5 x (1 - p(d + 10))
REVIEW_SEC = 0.30              # an ordinary code review spots a security flaw at 0.3 x its skill
QA_GAP, QA_DEFECT = 0.70, 0.50
RELEASE_CATCH = 0.30           # the release check catches a remaining defect
SMOKE = 0.30                   # the staging smoke test catches a logic/integration defect
INCIDENT_P = {"logic": 0.5, "integration": 0.6, "security": 0.8, "interface": 0.6}   # an escaped defect causes an incident
INCIDENT_DELAY_H = 24.0        # mean time from deploy to the incident
DEPLOY_H = 0.5
HUMAN_INTENT_H, HUMAN_PLAN_H = 4.0, 2.0
SELF_CATCH = 0.50
FALSE_REJECT = 0.03
CRITIQUE_FIND = 0.30
AMBIG_SCALE, AMBIG_PENALTY = 0.30, 0.6
LICENCE_P, REVIEW_LICENCE_P = 0.60, 0.50
ORPHAN_H = 8.0                 # R13
BLIND_P = 0.0                  # r12.1: chance a defect, or a requirement, sits in a blind spot shared by every
                               # model family: no LLM check sees it; tests, CI and smoke tests still can
COUPLING = 0.0                 # r12.2: dependency graph. Each ordered requirement pair (p < r) is an edge
                               # "r needs p" with this probability (0.25 in the cross-check model; 0 = r12)
INTERFACE_P = 0.10             # an interface fault at each edge a card builds across: 0.10 x (1.25 - 0.5 x pass)
IFACE_MULT = {"accepted": 1.0, "built": 1.5, "absent": 3.0}   # the builder read reviewed work, unreviewed work,
                               # or only the plan's contract (upstream not built yet) [assumption]
IFACE_REVIEW = 0.95            # review catches it at this x skill when the upstream work it read was reviewed;
IFACE_REVIEW_BLIND = 0.30      # at this x skill when it was not (nothing reviewed to check against)
FAMILY_BLIND_P = 0.0           # r12.1 (from the cross-check model): each requirement x model family pair has a
FAMILY_BLIND_MULT = 0.4        # latent blind spot with this chance; that family's pass/catch chance on the
                               # requirement is x0.4, at every step. Other families are unaffected.
CONTEXT_PENALTY = 0.0          # r12.1: packets. Every unit in a packet of k requirements is
                               # CONTEXT_PENALTY x (k - 1)^1.2 points harder (the cross-check model's form;
                               # 2.5 there): a longer context makes each part harder to get right
DIRECTOR_NOISE = 12.0
PRIORITY = ["operate", "release", "qa", "integrate", "security", "review", "audit", "build", "plan_check", "plan",
            "design", "challenge", "discover"]            # downstream first
ALL_STEPS = set(PRIORITY)


def p_pass(ci, d):
    return 1 / (1 + math.exp(-(fs.SLOPE * (ci - d) + fs.P0)))


# ---------------------------------------------------------------- entities
@dataclass(eq=False)
class Seat:
    cfg: fs.Config
    idx: int
    cls: str = ""                  # pool label: A (anchor), F (fast top), M (mid)
    busy_until: float = 0.0
    last_end: float = 0.0
    busy: dict = field(default_factory=lambda: defaultdict(float))

    def hours(self, base):
        return base * math.sqrt(100 / max(self.cfg.speed, 10))


@dataclass(eq=False)
class Idea:
    iid: int
    start: float
    req_d: list
    captured: set = field(default_factory=set)
    mapped: set = field(default_factory=set)
    cards: list = field(default_factory=list)
    stage: str = "discover"
    pending: int = 0
    rounds_left: int = 0
    design_q: float = 0.5
    plan_ci: float = 60.0
    authors: dict = field(default_factory=lambda: defaultdict(set))
    owner: Seat | None = None
    gap_loops: int = 0
    hotfix: bool = False
    done: bool = False
    shift: float = 0.0             # this idea's difficulty offset (open arrivals)
    blind_req: set = field(default_factory=set)   # requirements no model notices
    fam_blind: dict = field(default_factory=dict)  # (requirement, family) -> blind?
    deps: dict = field(default_factory=dict)       # requirement -> prerequisite requirements
    held: list = field(default_factory=list)       # cards waiting for prerequisites
    await_review: list = field(default_factory=list)   # cards waiting for the review barrier


@dataclass(eq=False)
class Card:
    idea: Idea
    band: str
    d: float
    sensitive: bool
    ambiguous: bool
    defects: set = field(default_factory=set)
    blind: set = field(default_factory=set)       # defects no LLM check can see
    units: list | None = None      # packet: [(difficulty, sensitive, ambiguous), ...]
    reqs: tuple = ()               # requirements this card implements
    version: int = 0               # r12.2: incremented at each build
    built: bool = False            # passed its unit tests, not yet reviewed
    read: dict = field(default_factory=dict)   # id(prerequisite card) -> version it was built against
    held_since: float = 0.0
    base_h: float = 0.0            # packet: summed build hours of its units
    author: str = ""
    reviewers: set = field(default_factory=set)
    attempts: int = 0
    accepted: bool = False
    allowed: set | None = None     # director routing


@dataclass(eq=False)
class Task:
    step: str
    idea: Idea
    card: Card | None = None
    d: float = 0.0
    born: float = 0.0
    exclude: set = field(default_factory=set)
    incident_t: float = 0.0


@dataclass
class Org:
    """An organisation = which seats may do which step, plus rules."""
    name: str
    pools: dict = field(default_factory=dict)       # step -> set of seat idx (missing = every seat)
    licences: bool = True                            # evidence licences (and R13 relaxations)
    independence: bool = True                        # author never checks own work (relaxed by R13)
    by_family: bool = False                          # r12.1: nor does any model of the author's family (vendor)
    hold_h: float = 2.0                              # "hybrid" gate: waiting limits (reviewed, then built, then contract)
    dep_gate: str = "accepted"                       # r12.2: a dependent card may start when its prerequisites are
                                                     # "accepted" (R17: reviewed and merged), "built" (tests passed,
                                                     # not reviewed) or "none" (ignore the graph, as r12 did)
    review_barrier: bool = False                     # r12.2: hold all review until every card of the idea is built
    owner_steps: frozenset = frozenset()             # steps only the idea's owner may do
    K: int = 2
    challenge: int = 1
    plan_check: bool = True
    security: bool = True
    audit: float = 0.10
    reviewers: int = 1
    routing: str = "pull"                            # or "director": cards routed on a noisy estimate
    workers: frozenset = frozenset()                 # director routing: seats that build


# ---------------------------------------------------------------- demand and elasticity
@dataclass
class Demand:
    """Open arrivals. rate(t) in ideas per hour; sizes and shifts are (value, weight) lists."""
    rate: object
    rate_max: float
    sizes: tuple = ((R_REQ, 1.0),)
    shifts: tuple = ((0.0, 1.0),)

    def next_gap(self, rng, t):                    # thinning (Lewis-Shedler)
        dt = 0.0
        while True:
            dt += rng.expovariate(self.rate_max)
            if rng.random() < self.rate(t + dt) / self.rate_max:
                return dt

    def draw(self, rng):
        n = rng.choices([v for v, _ in self.sizes], weights=[w for _, w in self.sizes])[0]
        sh = rng.choices([v for v, _ in self.shifts], weights=[w for _, w in self.shifts])[0]
        return n, sh


@dataclass
class Scaler:
    models: list                                   # fs.Config of each model the Ledger may start
    rate: dict                                     # model -> API $ per busy hour
    cls: dict = field(default_factory=dict)
    min_n: dict = field(default_factory=dict)
    max_n: dict = field(default_factory=dict)
    default_max: int = 8                           # vendor rate limits [assumption]
    total_max: int | None = None                   # ceiling on all running instances
    cap_usd_h: float | None = None                 # burn cap on running instances
    every: float = 0.25
    drain_h: float = 2.0                           # aim to clear each model's queue within 2 hours
    spinup_h: float = 0.05
    cool_h: float = 0.5
    band: float | None = 1.5                       # cost-band pull: an instance takes a task only if its expected
                                                   # cost is within band x the cheapest qualified model's (None = off)
    band_wait_h: float = 1.0                       # ... unless the task has waited this long
    strict: bool = True                            # instances pull only work they clear the quality floor on
    floor: float = 0.80                            # start a model only if its pass chance on the task >= floor
                                                   # (0.8 maximised clean output in the floor sweep; 0.6 = the licence floor)


# ---------------------------------------------------------------- simulation
class Sim:
    def __init__(self, org: Org, seats: list[Seat], seed: int, wip: int, horizon=7 * 168, warmup=168, conflict_k=None,
                 demand: "Demand | None" = None, scaler: "Scaler | None" = None, packet: int = 0):
        self.packet = packet                        # requirements per build invocation (0 = unit cards, r12)
        self.demand, self.scaler, self.retired = demand, scaler, []
        self.next_seat = len(seats)
        self.instance_h, self.peak = 0.0, len(seats)
        self.org, self.seats, self.rng = org, seats, random.Random(seed)
        self.wip, self.horizon, self.warmup = wip, horizon, warmup
        self.conflict_k = CONFLICT_K if conflict_k is None else conflict_k
        self.t, self.seq, self.events = 0.0, 0, []
        self.queues = defaultdict(list)
        self.open_ideas, self.next_id = [], 0
        self.building = 0
        self.top_ci = max(c.ci for c in scaler.models) if scaler else max(s.cfg.ci for s in seats)
        self.log = defaultdict(list)
        self.wait = defaultdict(list)
        self.drops = defaultdict(int)

    # plumbing
    def at(self, t, fn, *args):
        self.seq += 1
        heapq.heappush(self.events, (t, self.seq, fn, args))

    def run(self):
        self.at(2.0, self.orphan_sweep)
        if self.demand:
            self.at(self.demand.next_gap(self.rng, 0.0), self.arrive)
        else:
            for _ in range(self.wip):
                self.new_idea()
        if self.scaler:
            self.at(0.0, self.scale)
        self.dispatch()
        while self.events and self.events[0][0] <= self.horizon:
            self.t, _, fn, args = heapq.heappop(self.events)
            fn(*args)
            self.dispatch()
        return self

    def enqueue(self, task):
        task.born = self.t
        self.queues[task.step].append(task)

    # eligibility
    def eligible(self, s: Seat, task: Task) -> bool:
        org, aged = self.org, self.t - task.born >= ORPHAN_H
        relax = org.licences and aged                      # R13 belongs to the rule set
        if task.step in org.owner_steps:
            owner = task.idea.owner
            if owner is None:
                if any(i.owner is s and not i.done for i in self.open_ideas if i is not task.idea):
                    return False
            elif owner is not s:
                return False
        pool = org.pools.get(task.step)
        if pool is not None and s.idx not in pool and not (org.licences and self.t - task.born >= 2 * ORPHAN_H):
            return False
        if task.card is not None and task.card.allowed is not None and task.step == "build" and not relax:
            if s.idx not in task.card.allowed:
                return False
        if org.independence and s.cfg.name in task.exclude and not relax and not self.forced(task):
            return False
        if org.by_family and org.independence and task.card is not None and task.step in ("review", "security", "audit") \
                and not relax and task.card.author and self.family(s.cfg) == self.family_of(task.card.author):
            return False
        if self.scaler and self.scaler.band and self.t - task.born < self.scaler.band_wait_h:
            if self.task_cost(s.cfg, task) > self.scaler.band * self.cheapest(task):
                return False                               # cost-band pull: leave it to a cheaper qualified model
            if self.scaler.strict and task.step not in ("discover", "challenge") and \
                    p_pass(s.cfg.ci, task.card.d if task.card is not None else task.d) < self.scaler.floor:
                return False                               # ... and to a model that clears the quality floor
        if not org.licences or task.step in ("discover", "challenge"):
            return True
        if task.step in ("review", "audit", "security"):
            ok = p_pass(s.cfg.ci, task.card.d) >= REVIEW_LICENCE_P
        else:
            ok = p_pass(s.cfg.ci, task.d) >= LICENCE_P
        if not ok and task.step != "build" and aged:
            ok = s.cfg.ci >= self.top_ci - 10              # R13: open to the most capable
        return ok

    def permitted(self, s: Seat, task: Task) -> bool:
        """Owner and pool rules only (what the organisation's structure allows)."""
        if task.step in self.org.owner_steps and task.idea.owner is not None and task.idea.owner is not s:
            return False
        if task.step == "build" and task.card is not None and task.card.allowed is not None and s.idx not in task.card.allowed:
            return False
        pool = self.org.pools.get(task.step)
        return pool is None or s.idx in pool

    def forced(self, task: Task) -> bool:
        """Every seat the structure permits is excluded: the role-holder does it anyway (recorded)."""
        allowed = [x for x in self.seats if self.permitted(x, task)]
        if allowed and all(x.cfg.name in task.exclude for x in allowed):
            if not getattr(task, "waived", False):
                task.waived = True
                self.drops["independence_impossible"] += 1
            return True
        return False

    def orphan_sweep(self):
        """R13: split build cards nobody may take after ORPHAN_H hours (rule-based organisations only)."""
        if self.org.dep_gate == "hybrid":
            for idea in self.open_ideas:
                self.release_held(idea)
        if self.org.licences:
            for task in list(self.queues["build"]):
                if self.t - task.born >= ORPHAN_H and not any(self.eligible(s, task) for s in self.seats):
                    self.queues["build"].remove(task)
                    c = task.card
                    c.idea.cards.remove(c)
                    self.drops["split"] += 1
                    for _ in range(2):
                        n = Card(c.idea, c.band, max(5.0, c.d - 10), c.sensitive, c.ambiguous, reqs=c.reqs)
                        c.idea.cards.append(n)
                        self.send_card(n)
        self.at(self.t + 2.0, self.orphan_sweep)

    def dispatch(self):
        free = [s for s in self.seats if s.busy_until <= self.t]
        self.rng.shuffle(free)
        for s in free:
            for step in PRIORITY:
                q = self.queues[step]
                cands = [t for t in q if self.eligible(s, t)] if q else []
                if not cands:
                    continue
                task = max(cands, key=lambda t: t.d) if step == "build" and self.org.licences else cands[0]
                q.remove(task)
                if task.step in self.org.owner_steps and task.idea.owner is None:
                    task.idea.owner = s
                self.start(s, task)
                break

    @staticmethod
    def base_hours(task: Task) -> float:
        if task.card is not None and task.step in ("build", "review", "security", "audit"):
            h = task.card.base_h or CARD_HOURS[task.card.band]
            return h * (1.0 if task.step == "build" else CARD_SHARE[task.step])
        return STEP_HOURS[task.step]

    def start(self, s: Seat, task: Task):
        dur = s.hours(self.base_hours(task))
        if task.step == "build":
            self.building += 1
        s.busy_until = self.t + dur
        if self.t >= self.warmup:
            s.busy[task.step] += dur
            self.wait[task.step].append(self.t - task.born)
        self.at(self.t + dur, self.finish, s, task)

    def finish(self, s, task):
        s.last_end = self.t
        if task.step == "build":
            self.building -= 1
        getattr(self, "on_" + task.step)(s, task)

    # elasticity: rules, not an agent
    def licensed(self, cfg, task) -> bool:
        if not self.org.licences or task.step in ("discover", "challenge"):
            return True
        if task.step in ("review", "audit", "security"):
            return p_pass(cfg.ci, task.card.d) >= REVIEW_LICENCE_P
        return p_pass(cfg.ci, task.d) >= LICENCE_P

    def task_cost(self, cfg, task) -> float:
        """Expected cost of a success: $/busy hour x hours / pass chance."""
        h = self.base_hours(task) * math.sqrt(100 / max(cfg.speed, 10))
        succ = p_pass(cfg.ci, task.card.d if task.card is not None else task.d)
        return self.scaler.rate[cfg.name] * h / max(succ, 0.05)

    def best_model(self, task):
        """The cheapest model that may take the task and clears the quality floor (cached per task)."""
        if getattr(task, "best", None) is not None:
            return task.best
        sc, best, best_cost = self.scaler, None, float("inf")
        for cfg in sc.models:
            if self.org.independence and cfg.name in task.exclude and not self.forced(task):
                continue
            if not self.licensed(cfg, task):
                continue
            succ = p_pass(cfg.ci, task.card.d if task.card is not None else task.d)
            if succ < sc.floor and task.step not in ("discover", "challenge"):
                continue
            cost = self.task_cost(cfg, task)
            if cost < best_cost:
                best, best_cost = cfg, cost
        task.best = best or max(sc.models, key=lambda c: c.ci)          # R13: the most capable
        return task.best

    def cheapest(self, task) -> float:
        return self.task_cost(self.best_model(task), task)

    def scale(self):
        sc = self.scaler
        demand = defaultdict(float)
        for q in self.queues.values():
            for task in q:
                best = self.best_model(task)
                demand[best.name] += self.base_hours(task) * math.sqrt(100 / max(best.speed, 10))
        count = defaultdict(int)
        busy = defaultdict(int)
        for s in self.seats:
            count[s.cfg.name] += 1
            busy[s.cfg.name] += s.busy_until > self.t
        target = {}
        for cfg in sc.models:
            n = busy[cfg.name] + math.ceil(demand[cfg.name] / sc.drain_h)
            target[cfg.name] = max(sc.min_n.get(cfg.name, 0), min(sc.max_n.get(cfg.name, sc.default_max), n))
        if sc.total_max is not None:
            while sum(target.values()) > sc.total_max:
                cut = [m for m in target if target[m] > max(sc.min_n.get(m, 0), busy[m])]
                if not cut:
                    break
                target[max(cut, key=lambda m: sc.rate[m])] -= 1
        if sc.cap_usd_h is not None:
            while sum(target[m] * sc.rate[m] for m in target) > sc.cap_usd_h:
                cut = [m for m in target if target[m] > max(sc.min_n.get(m, 0), busy[m])]
                if not cut:
                    break
                m = max(cut, key=lambda m: sc.rate[m])
                target[m] -= 1
        for cfg in sc.models:
            for _ in range(target[cfg.name] - count[cfg.name]):
                seat = Seat(cfg, self.next_seat, cls=sc.cls.get(cfg.name, ""))
                seat.busy_until = seat.last_end = self.t + sc.spinup_h
                self.next_seat += 1
                self.seats.append(seat)
        for s in list(self.seats):
            m = s.cfg.name
            if count[m] > target[m] and s.busy_until <= self.t and self.t - s.last_end >= sc.cool_h:
                self.seats.remove(s)
                self.retired.append(s)
                count[m] -= 1
        if self.t >= self.warmup:
            self.instance_h += len(self.seats) * sc.every
            self.peak = max(self.peak, len(self.seats))
        self.at(self.t + sc.every, self.scale)

    @staticmethod
    def family(cfg):
        c = s6.C.get(cfg.name)
        return c["vendor"] if c else cfg.name

    @staticmethod
    def family_of(name):
        c = s6.C.get(name)
        return c["vendor"] if c else name

    def fb(self, idea, reqs, cfg) -> float:
        """Family blind-spot multiplier for this model on any of these requirements."""
        if not FAMILY_BLIND_P:
            return 1.0
        fam = self.family(cfg)
        for r in reqs:
            key = (r, fam)
            if key not in idea.fam_blind:
                idea.fam_blind[key] = self.rng.random() < FAMILY_BLIND_P
            if idea.fam_blind[key]:
                return FAMILY_BLIND_MULT
        return 1.0

    def own(self, s, author):
        return SELF_CATCH if s.cfg.name == author else 1.0

    # ideas
    def arrive(self):
        n, shift = self.demand.draw(self.rng)
        self.new_idea(size=n, shift=shift)
        self.at(self.t + self.demand.next_gap(self.rng, self.t), self.arrive)

    def new_idea(self, hotfix_card=None, size=None, shift=0.0):
        idea = Idea(self.next_id, self.t, [self.rng.gauss(REQ_BASE + shift, REQ_SPREAD) for _ in range(size or R_REQ)],
                    shift=shift)
        if BLIND_P:
            idea.blind_req = {r for r in range(len(idea.req_d)) if self.rng.random() < BLIND_P}
        if COUPLING:
            idea.deps = {r: [q for q in range(r) if self.rng.random() < COUPLING] for r in range(len(idea.req_d))}
        self.next_id += 1
        if hotfix_card is not None:
            idea.hotfix, idea.stage, idea.design_q = True, "build", 0.8
            idea.owner = hotfix_card.idea.owner
            c = Card(idea, hotfix_card.band, hotfix_card.d, hotfix_card.sensitive, False)
            idea.cards.append(c)
            self.send_card(c)
            return
        self.open_ideas.append(idea)
        k = 1 if "discover" in self.org.owner_steps else self.org.K
        idea.pending = k
        for _ in range(k):
            self.enqueue(Task("discover", idea, d=REQ_BASE))

    def on_discover(self, s, task):
        idea = task.idea
        for r, d in enumerate(idea.req_d):
            if r not in idea.blind_req and self.rng.random() < p_pass(s.cfg.ci, d) * self.fb(idea, (r,), s.cfg):
                idea.captured.add(r)
        idea.authors["discover"].add(s.cfg.name)
        for t in self.queues["discover"]:
            if t.idea is idea:
                t.exclude.add(s.cfg.name)                  # commit-before-view: other analysts
        idea.pending -= 1
        if idea.pending == 0:
            idea.rounds_left = 0 if "challenge" in self.org.owner_steps else self.org.challenge
            self.challenge_round(idea)

    def challenge_round(self, idea):
        if idea.rounds_left <= 0:
            self.at(self.t + HUMAN_INTENT_H, self.to_design, idea)
            return
        idea.pending = max(1, len(idea.authors["discover"]))
        for _ in range(idea.pending):
            self.enqueue(Task("challenge", idea, d=REQ_BASE + 5))

    def on_challenge(self, s, task):
        idea = task.idea
        for r, d in enumerate(idea.req_d):
            if r not in idea.captured and r not in idea.blind_req and \
                    self.rng.random() < CRITIQUE_FIND * p_pass(s.cfg.ci, d + 5) * self.fb(idea, (r,), s.cfg):
                idea.captured.add(r)
        idea.pending -= 1
        if idea.pending == 0:
            idea.rounds_left -= 1
            self.challenge_round(idea)

    def to_design(self, idea):
        self.enqueue(Task("design", idea, d=DESIGN_D))

    def on_design(self, s, task):
        idea = task.idea
        idea.design_q = p_pass(s.cfg.ci, DESIGN_D)
        idea.authors["design"].add(s.cfg.name)
        self.enqueue(Task("plan", idea, d=REQ_BASE + 8))

    def on_plan(self, s, task):
        idea = task.idea
        for r in idea.captured:
            if self.rng.random() < p_pass(s.cfg.ci, idea.req_d[r] + 8) * self.fb(idea, (r,), s.cfg):
                idea.mapped.add(r)
        idea.plan_ci = s.cfg.ci
        idea.authors["plan"].add(s.cfg.name)
        if self.org.plan_check and "plan_check" not in self.org.owner_steps:
            self.enqueue(Task("plan_check", idea, d=REQ_BASE + 10, exclude={s.cfg.name}))
        else:
            self.at(self.t + HUMAN_PLAN_H, self.make_cards, idea, None)

    def on_plan_check(self, s, task):
        idea = task.idea
        for r in range(len(idea.req_d)):
            if r not in idea.mapped and r not in idea.blind_req and \
                    self.rng.random() < p_pass(s.cfg.ci, idea.req_d[r] + 10) * self.own(s, next(iter(idea.authors["plan"]))) \
                    * self.fb(idea, (r,), s.cfg):
                idea.mapped.add(r)
        self.at(self.t + HUMAN_PLAN_H, self.make_cards, idea, None)

    def make_cards(self, idea, only):
        rng = self.rng
        new = []
        self._units_by_req = {}
        for r in (sorted(idea.mapped) if only is None else only):
            self._units_by_req[r] = []
            for _ in range(rng.choice(CARDS_PER_REQ)):
                band = rng.choices(list(CARD_MIX), weights=list(CARD_MIX.values()))[0]
                lo, hi = CARD_RANGE[band]
                d = rng.uniform(lo, hi) + DESIGN_PENALTY * (1 - idea.design_q) + idea.shift
                new.append(Card(idea, band, d, rng.random() < SEC_SHARE,
                                rng.random() < AMBIG_SCALE * (1 - p_pass(idea.plan_ci, 60)), reqs=(r,)))
                self._units_by_req[r].append(new[-1])
        if self.packet and new:
            new = self.pack(new, idea)
        idea.cards.extend(new)
        idea.stage = "build"
        for c in new:
            self.send_card(c)
        if not new:
            self.check_idea(idea)

    def pack(self, units, idea):
        """Group the unit cards of every `packet` requirements into one build invocation."""
        per_req, out = self._units_by_req, []
        reqs = list(per_req)
        for i in range(0, len(reqs), self.packet):
            us = [u for r in reqs[i:i + self.packet] for u in per_req[r]]
            pen = CONTEXT_PENALTY * (len(reqs[i:i + self.packet]) - 1) ** 1.2
            band = max((u.band for u in us), key=lambda b: CARD_HOURS[b])
            out.append(Card(idea, band, max(u.d for u in us) + pen, any(u.sensitive for u in us), any(u.ambiguous for u in us),
                            units=[(u.d + pen, u.sensitive, u.ambiguous) for u in us],
                            base_h=sum(CARD_HOURS[u.band] for u in us), reqs=tuple(r for r in reqs[i:i + self.packet])))
        return out

    # cards
    # dependency graph (r12.2)
    def graph_on(self, idea):
        # "hybrid" waits by the clock: the sweep (every 2 h) re-checks held cards
        return bool(idea.deps) and self.org.dep_gate != "none"

    def prereqs(self, card):
        idea = card.idea
        if not idea.deps:
            return []
        need = {q for r in card.reqs for q in idea.deps.get(r, ()) if q not in card.reqs and q in idea.mapped}
        return [c for c in idea.cards if c is not card and need.intersection(c.reqs)] if need else []

    def ready(self, card):
        if not self.graph_on(card.idea):
            return True
        pcs = self.prereqs(card)
        if self.org.dep_gate == "built":
            return all(c.built or c.accepted for c in pcs)
        if self.org.dep_gate == "hybrid":                 # R17 with waiting limits
            waited = self.t - card.held_since if card in card.idea.held else 0.0
            if all(c.accepted for c in pcs):
                return True
            if waited >= self.org.hold_h and all(c.built or c.accepted for c in pcs):
                return True
            return waited >= 2 * self.org.hold_h
        return all(c.accepted for c in pcs)

    def stale(self, card):
        if not self.graph_on(card.idea):
            return False
        for pc in self.prereqs(card):
            r = card.read.get(id(pc))
            if r == -1:                                   # built to the plan's contract: a later upstream build
                continue                                  # does not invalidate it (interface risk was charged)
            if r is None or r != pc.version:              # new prerequisite, or the version read has changed
                return True
        return False

    def release_held(self, idea):
        for c in list(idea.held):
            if self.ready(c):
                idea.held.remove(c)
                self.enqueue_build(c)

    def send_card(self, card):
        card.accepted = False
        card.built = False
        if card in card.idea.await_review:
            card.idea.await_review.remove(card)
        if not self.ready(card):
            if card not in card.idea.held:
                card.held_since = self.t
                card.idea.held.append(card)
            return
        self.enqueue_build(card)

    def enqueue_build(self, card):
        if self.org.routing == "director":
            est = card.d + self.rng.gauss(0, DIRECTOR_NOISE)
            ws = [s for s in self.seats if s.idx in self.org.workers]
            ok = [s for s in ws if p_pass(s.cfg.ci, est) >= LICENCE_P]
            pick = min(ok, key=lambda s: s.cfg.ci) if ok else max(ws, key=lambda s: s.cfg.ci)
            card.allowed = {s.idx for s in ws if s.cfg.name == pick.cfg.name}
        t = Task("build", card.idea, card, d=card.d)
        if self.org.independence and self.org.routing == "pull" and card.attempts % 2 == 1 and card.author:
            t.exclude = {card.author}                       # a failed card goes to someone else next
        self.enqueue(t)

    def on_build(self, s, task):
        card = task.card
        card.attempts += 1
        card.author = s.cfg.name
        card.reviewers = set()
        card.version += 1
        pcs = self.prereqs(card)
        contract = self.org.dep_gate == "none"
        card.read = {id(pc): (pc.version if (pc.built or pc.accepted) and not contract else -1) for pc in pcs}
        card.defects, card.blind = set(), set()
        if card.units:                                 # a packet is right only if every unit is
            p, clean_sec = 1.0, 1.0
            for d, sens, amb in card.units:
                p *= p_pass(s.cfg.ci, d) * (AMBIG_PENALTY if amb and card.ambiguous else 1.0)
                if sens:
                    clean_sec *= 1 - SEC_INJECT * (1 - p_pass(s.cfg.ci, d + 10))
            sec = 1 - clean_sec
        else:
            p = p_pass(s.cfg.ci, card.d) * (AMBIG_PENALTY if card.ambiguous else 1.0)
            sec = SEC_INJECT * (1 - p_pass(s.cfg.ci, card.d + 10)) if card.sensitive else 0.0
        p *= self.fb(card.idea, card.reqs, s.cfg)
        if self.rng.random() >= p:
            card.defects.add("logic")
        if sec and self.rng.random() < sec:
            card.defects.add("security")
        for pc in pcs:                                   # an interface fault at each edge built across
            seen = "absent" if contract else "accepted" if pc.accepted else "built" if pc.built else "absent"
            if self.rng.random() < INTERFACE_P * IFACE_MULT[seen] * (1.25 - 0.5 * min(1.0, p)):
                card.defects.add("interface")
        self.mark_blind(card)
        if "logic" in card.defects and self.rng.random() < TEST_CATCH:
            self.drops["test_fail"] += 1
            if card.ambiguous and card.attempts >= 3:
                card.ambiguous = False
                self.drops["clarify"] += 1
            self.send_card(card)
            return
        self.to_review(card)

    def mark_blind(self, card):
        for k in card.defects - card.blind:
            if BLIND_P and self.rng.random() < BLIND_P and k not in getattr(card, "_seen", ()):
                card.blind.add(k)
        card._seen = set(card.defects)

    @staticmethod
    def vis(card):
        """Defects an LLM check can see."""
        return card.defects - card.blind

    def to_review(self, card):
        card.built = True
        idea = card.idea
        if self.org.dep_gate == "built":
            self.release_held(idea)
        if self.org.review_barrier and not idea.hotfix:
            if not all(c.built or c.accepted for c in idea.cards):
                if card not in idea.await_review:
                    idea.await_review.append(card)
                return
            waiting, idea.await_review = idea.await_review, []
            for c in waiting:
                if c.built and not c.accepted:
                    self._review(c)
        self._review(card)

    def _review(self, card):
        self.enqueue(Task("review", card.idea, card, d=card.d + 5, exclude={card.author} | card.reviewers))

    def on_review(self, s, task):
        card = task.card
        if self.stale(card):
            self.drops["stale_rework"] += 1
            self.send_card(card)
            return
        f = self.own(s, card.author) * self.fb(card.idea, card.reqs, s.cfg)
        v = self.vis(card)
        if "interface" in v:
            base = IFACE_REVIEW if all(pc.accepted for pc in self.prereqs(card)) else IFACE_REVIEW_BLIND
            if self.rng.random() < f * base * p_pass(s.cfg.ci, card.d):
                self.drops["interface_reject"] += 1
                self.send_card(card)
                return
        caught = ("logic" in v and self.rng.random() < f * p_pass(s.cfg.ci, card.d + 5)) or \
                 ("security" in v and self.rng.random() < f * REVIEW_SEC * p_pass(s.cfg.ci, card.d + 10))
        if caught or (not card.defects and self.rng.random() < FALSE_REJECT):
            self.drops["review_reject"] += 1
            self.send_card(card)
            return
        card.reviewers.add(s.cfg.name)
        if len(card.reviewers) < self.org.reviewers:
            self._review(card)
        elif card.sensitive and self.org.security and "security" not in self.org.owner_steps:
            self.enqueue(Task("security", card.idea, card, d=SECURITY_D, exclude={card.author}))
        else:
            self.enqueue(Task("integrate", card.idea, card, d=INTEGRATE_D + 10 * (1 - card.idea.design_q)))

    def on_security(self, s, task):
        card = task.card
        f = self.own(s, card.author) * self.fb(card.idea, card.reqs, s.cfg)
        v = self.vis(card)
        if ("security" in v and self.rng.random() < f * p_pass(s.cfg.ci, SECURITY_D)) or \
           ("logic" in v and self.rng.random() < 0.2 * f * p_pass(s.cfg.ci, card.d)):
            self.drops["security_reject"] += 1
            self.send_card(card)
            return
        self.enqueue(Task("integrate", card.idea, card, d=INTEGRATE_D + 10 * (1 - card.idea.design_q)))

    def on_integrate(self, s, task):
        card, q = task.card, task.card.idea.design_q
        if self.stale(card):
            self.drops["stale_rework"] += 1
            self.send_card(card)
            return
        if self.rng.random() < 1 - math.exp(-self.conflict_k * (2 - q) * self.building):
            self.drops["merge_conflict"] += 1
            self.send_card(card)
            return
        if self.rng.random() < INT_BASE * (1 + 2 * (1 - q)):
            card.defects.add("integration")
            self.mark_blind(card)
        if ("integration" in card.defects and self.rng.random() < CI_CATCH) or \
           ("interface" in card.defects and self.rng.random() < 0.5 * CI_CATCH) or \
           ("logic" in card.defects and self.rng.random() < 0.2):
            self.drops["ci_fail"] += 1
            self.send_card(card)
            return
        card.accepted = True
        self.release_held(card.idea)
        if self.org.audit and self.rng.random() < self.org.audit and not card.idea.hotfix:
            self.enqueue(Task("audit", card.idea, card, d=card.d, exclude={card.author} | card.reviewers))
        self.check_idea(card.idea)

    def on_audit(self, s, task):
        card = task.card
        if self.vis(card) and self.rng.random() < self.own(s, card.author) * self.fb(card.idea, card.reqs, s.cfg) * p_pass(s.cfg.ci, card.d):
            self.drops["audit_catch"] += 1
            if card.idea.stage in ("build", "qa", "release") and not card.idea.done:
                card.idea.stage = "build"                  # pulled back before release
                self.send_card(card)
            else:
                self.drops["audit_too_late"] += 1

    def check_idea(self, idea):
        if idea.stage != "build" or not all(c.accepted for c in idea.cards):
            return
        if idea.hotfix:
            idea.stage = "deploy"
            self.at(self.t + DEPLOY_H, self.deploy, idea)
            return
        idea.stage = "qa"
        self.enqueue(Task("qa", idea, d=QA_D, exclude=set(idea.authors["plan"])))

    def on_qa(self, s, task):
        idea, rng = task.idea, self.rng
        if idea.stage != "qa":                             # stale: pulled back by an audit
            return
        old = [c for c in idea.cards if self.stale(c)]
        if old:                                            # built against work that has since changed
            idea.stage = "build"
            for c in old:
                self.drops["stale_rework"] += 1
                self.send_card(c)
            return
        gaps = [r for r in range(len(idea.req_d)) if r not in idea.mapped and r not in idea.blind_req and rng.random() < QA_GAP * p_pass(s.cfg.ci, idea.req_d[r]) * self.fb(idea, (r,), s.cfg)]
        bad = [c for c in idea.cards if self.vis(c) and rng.random() < QA_DEFECT * self.own(s, c.author) * self.fb(idea, c.reqs, s.cfg) * p_pass(s.cfg.ci, c.d)]
        idea.authors["qa"].add(s.cfg.name)
        if bad or (gaps and idea.gap_loops < 2):
            idea.stage = "build"
            for c in bad:
                self.drops["qa_defect"] += 1
                self.send_card(c)
            if gaps and idea.gap_loops < 2:
                idea.gap_loops += 1
                self.drops["qa_intent_gap"] += 1
                idea.mapped.update(gaps)
                self.at(self.t + HUMAN_PLAN_H, self.make_cards, idea, gaps)
            return
        idea.stage = "release"
        self.enqueue(Task("release", idea, d=RELEASE_D, exclude=set(idea.authors["qa"]) | set(idea.authors["plan"])))

    def on_release(self, s, task):
        idea = task.idea
        if idea.stage != "release":                         # stale: pulled back by an audit
            return
        bad = [c for c in idea.cards if self.vis(c) and self.rng.random() < RELEASE_CATCH * self.own(s, c.author) * self.fb(idea, c.reqs, s.cfg)]
        if bad:
            idea.stage = "build"
            for c in bad:
                self.drops["release_defect"] += 1
                self.send_card(c)
            return
        idea.stage = "deploy"
        self.at(self.t + DEPLOY_H, self.deploy, idea)

    # live
    def deploy(self, idea):
        if idea.done or idea.stage != "deploy":
            return
        bad = [c for c in idea.cards if c.defects & {"logic", "integration", "interface"} and self.rng.random() < SMOKE]
        if bad:
            idea.stage = "build"
            self.drops["smoke_rollback"] += 1
            for c in bad:
                self.send_card(c)
            return
        idea.done = True
        incidents = 0
        for c in idea.cards:
            for kind in c.defects:
                if self.rng.random() < INCIDENT_P[kind]:
                    incidents += 1
                    self.at(self.t + self.rng.expovariate(1 / INCIDENT_DELAY_H), self.incident, idea, c)
        if self.t >= self.warmup:
            key = "hotfixes" if idea.hotfix else "ideas"
            correct = []                                   # a requirement is useful only if it and all its prerequisites are right
            for r in range(len(idea.req_d)):
                ok = r in idea.mapped and not any(c.defects for c in idea.cards if r in c.reqs)
                correct.append(ok and all(correct[q] for q in idea.deps.get(r, ())))
            self.log[key].append(dict(lead=self.t - idea.start, coherence=len(idea.mapped) / len(idea.req_d),
                                      escaped=sum(1 for c in idea.cards if c.defects), incidents=incidents,
                                      useful=sum(correct) / len(idea.req_d)))
        if not idea.hotfix:
            self.open_ideas.remove(idea)
            if not self.demand:
                self.new_idea()

    def incident(self, idea, card):
        t = Task("operate", idea, card, d=card.d + 5)
        t.incident_t = self.t
        self.enqueue(t)

    def on_operate(self, s, task):
        if self.t >= self.warmup:
            self.log["restore"].append(self.t - task.incident_t)
        self.new_idea(hotfix_card=task.card)


# ---------------------------------------------------------------- measures
def measure(sim: Sim) -> dict:
    weeks = (sim.horizon - sim.warmup) / 168
    ideas, fixes = sim.log["ideas"], sim.log["hotfixes"]
    busy_model = defaultdict(float)
    busy_step = defaultdict(float)
    for s in sim.seats + sim.retired:
        for k, v in s.busy.items():
            busy_model[s.cfg.name] += v / weeks
            busy_step[k] += v / weeks
    usd = sum(h * s6.usd_per_busy_hour(s6.C[n]) for n, h in busy_model.items() if n in s6.C)
    leads = sorted(r["lead"] for r in ideas)
    clean = sum(1 for r in ideas if r["coherence"] >= 1.0 and r["escaped"] == 0) / weeks
    waits = {k: statistics.mean(v) for k, v in sim.wait.items() if v}
    return dict(
        ideas=len(ideas) / weeks, clean=clean, hotfixes=len(fixes) / weeks,
        useful=sum(r["useful"] for r in ideas) / weeks,
        lead=statistics.median(r["lead"] for r in ideas) if ideas else float("nan"),
        coherence=statistics.mean(r["coherence"] for r in ideas) if ideas else float("nan"),
        escaped=statistics.mean(r["escaped"] for r in ideas) if ideas else float("nan"),
        cfr=sum(1 for r in ideas if r["incidents"]) / len(ideas) if ideas else float("nan"),
        restore=statistics.mean(sim.log["restore"]) if sim.log["restore"] else float("nan"),
        usd_week=usd if all(s.cfg.name in s6.C for s in sim.seats + sim.retired) else float("nan"),
        lead_p90=leads[int(0.9 * (len(leads) - 1))] if leads else float("nan"),
        backlog=len(sim.open_ideas),
        seat_h=(sim.instance_h if sim.scaler else len(sim.seats) * (sim.horizon - sim.warmup)) / weeks,
        peak=sim.peak,
        util=sum(busy_step.values()) / max(1e-9, (sim.instance_h / weeks if sim.scaler else 168 * len(sim.seats))),
        busy_step=dict(busy_step), busy_model=dict(busy_model), waits=waits,
        bottleneck=max(waits, key=waits.get) if waits else "none",
        drops={k: v / max(1, len(ideas)) for k, v in sim.drops.items()},
    )


def mean_measures(rows: list[dict]) -> dict:
    out = {}
    for k, v in rows[0].items():
        if isinstance(v, dict):
            keys = set().union(*(r[k].keys() for r in rows))
            out[k] = {kk: statistics.mean(r[k].get(kk, 0.0) for r in rows) for kk in keys}
        elif isinstance(v, str):
            out[k] = max(set(r[k] for r in rows), key=[r[k] for r in rows].count)
        else:
            vals = [r[k] for r in rows if not (isinstance(r[k], float) and math.isnan(r[k]))]
            out[k] = statistics.mean(vals) if vals else float("nan")
    out["usd_clean"] = out["usd_week"] / out["clean"] if out["clean"] else float("inf")
    return out
