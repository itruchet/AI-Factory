"""Institutional throughput simulation of the Factory.

A discrete-event simulation of work flowing through the institutions, staffed
by agents drawn from the real Artificial Analysis Coding Index population
(../aa-tiers/aa_coding_2026-09-09.csv: 136 current, priced configurations).
Nothing here refers to the Factory's current models. Every assumption is a
named constant below and is listed in docs/idea/institutional-throughput.md.

Two organisations are modelled on the same world:

  baseline      Director -> Worker -> Checker. One Director frames and plans
                every idea alone and pushes each card to a worker tier by its
                own estimate of difficulty. Workers are dedicated to their
                queue. One Checker reviews everything. No council, red team,
                audit or independent release check.

  institutions  Inquiry (K independent submissions) -> Council (critique
                rounds + synthesis) -> Planning (D parallel decompositions,
                reconciliation, red team) -> Work Market -> Assurance Court
                -> Audit (sample) -> Release Gate. Agents pull tasks; nobody
                assigns. An agent may take a task only if its expected pass
                rate on that task clears the licence floor (Inquiry is open
                to all, for diversity). Downstream work is pulled first
                ("stop starting, start finishing"); cards hardest-first.

World model (same for both):
  - an idea has R requirements, each with its own difficulty;
  - framing captures requirements, planning maps them to cards; anything
    missed becomes an intent gap that the release check may catch (loop
    back to planning) or that ships (lost coherence);
  - each card has a difficulty in Coding Index units; an agent passes a task
    of difficulty D with p = logistic(SLOPE * (ci - D) + P0);
  - failed work is caught by tests (TEST_CATCH), then by review (reviewer
    skill), then audit and release checks; anything left escapes;
  - task time scales with the agent's measured output speed; cost is the
    agent's real blended price times the task's tokens.

Other operating models (r12), same world, same agents:

  solo          "no model": each agent owns one idea end to end, reviews and
                releases its own work; no licences, no independence
  peer          solo, but review and release by any other agent
  orchestrator  one lead agent frames, plans, checks every card and releases;
                workers build (the common orchestrator-subagent pattern);
                built as the baseline with the Director and Checker merged
  swarm         shared pull queue with none of the rules: no licences, no
                independence, first-come not hardest-first, one analyst, no
                council, no red team, no audit
  self-licensed the institutions, but each agent licenses itself on its own
                confidence, overstated by OVERCONF Coding Index points

An author checking its own work (or the same model checking it) catches
SELF_CATCH as much as an independent reviewer of equal skill. Optional
shared-codebase contention: a finished card conflicts with the cards other
agents are building with probability 1 - exp(-conflict_k x active cards),
and must be redone.

Run: python3 probes/institutions/factory_sim.py
"""

from __future__ import annotations

import csv
import heapq
import math
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE.parent / "aa-tiers" / "aa_coding_2026-09-09.csv"

# ---------------------------------------------------------------- real data
TIER_EDGES = (56.8, 29.9)          # natural-tier breaks from ../aa-tiers/tiering.py


def tier_of(ci: float) -> int:
    return 1 if ci >= TIER_EDGES[0] else 2 if ci >= TIER_EDGES[1] else 3


@dataclass(frozen=True)
class Config:
    name: str
    ci: float
    price: float     # USD per 1M tokens (blended)
    speed: float     # output tokens per second

    @property
    def tier(self) -> int:
        return tier_of(self.ci)


def load_pool() -> dict[int, list[Config]]:
    pool = defaultdict(list)
    for r in csv.DictReader(open(DATA)):
        if r["deprecated"] == "True" or r["price_blended_usd_per_1m"] in ("", "None") \
                or r["output_tokens_per_s"] in ("", "None", "0") or float(r["coding_index"]) <= 0:
            continue
        c = Config(r["name"], float(r["coding_index"]), float(r["price_blended_usd_per_1m"]), float(r["output_tokens_per_s"]))
        pool[c.tier].append(c)
    return pool


POOL = load_pool()

# ---------------------------------------------------------------- assumptions
SLOPE, P0 = 0.12, math.log(3)       # pass = 75% when ci equals task difficulty; +10 points ~ +1.2 logits
LICENCE_P = 0.60                    # an agent may take a task it passes at least 60% of the time
R_REQ = 8                           # requirements per idea
REQ_BASE, REQ_SPREAD = 50.0, 8.0    # requirement difficulty ~ N(50, 8) Coding Index points
CARDS_PER_REQ = (1, 2, 2, 3)        # cards generated per mapped requirement (drawn uniformly)
CARD_MIX = {"easy": 0.45, "mid": 0.35, "hard": 0.20}
CARD_RANGE = {"easy": (10, 30), "mid": (30, 57), "hard": (57, 75)}
TEST_CATCH = 0.50                   # share of defective outputs caught by automated tests
FALSE_REJECT = 0.03                 # correct work wrongly rejected at review
AMBIG_SCALE = 0.30                  # card ambiguity = 0.30 x planner's failure rate
AMBIG_PENALTY = 0.6                 # pass chance multiplier on an ambiguous card
CRITIQUE_FIND = 0.30                # council critic finds a missed requirement: 0.3 x pass rate
RELEASE_GAP_CATCH = 0.70            # release check notices an unmapped requirement
RELEASE_DEFECT_CATCH = 0.50         # release/integration check catches a remaining defect
AUDIT_RATE = 0.10
HUMAN_FRAMING_H, HUMAN_PLAN_H = 4.0, 2.0   # human ratification delays (both organisations)
DIRECTOR_NOISE = 12.0               # baseline Director's error estimating card difficulty
REVIEW_LICENCE_P = 0.50             # a reviewer must pass the card itself at least half the time
ORPHAN_H = 8.0                      # R13: hours a task may wait with nobody licensed before
                                    # a card is split (two cards, 10 points easier) or any other
                                    # task opens to the organisation's most capable agents
SPLIT_EASIER = 10.0
SELF_CATCH = 0.5                    # own-work (or same-model) review catches half as much (r12)
OVERCONF = 10.0                     # self-assessed licence: agents overrate themselves by 10 points (r12)

# task: (base hours at 100 tokens/s, tokens, difficulty offset or fixed difficulty)
TASK_HOURS = {"inquiry": 0.5, "critique": 0.3, "synthesis": 0.5, "decompose": 1.0, "reconcile": 0.6,
              "redteam": 0.5, "release": 0.5}
TASK_TOKENS = {"inquiry": 40e3, "critique": 25e3, "synthesis": 40e3, "decompose": 80e3, "reconcile": 50e3,
               "redteam": 40e3, "release": 30e3}
TASK_DIFF = {"inquiry": REQ_BASE, "critique": REQ_BASE + 5, "synthesis": 55, "decompose": REQ_BASE + 8,
             "reconcile": 60, "redteam": REQ_BASE + 10, "release": 50}
CARD_HOURS = {"easy": 0.5, "mid": 1.0, "hard": 2.5}
CARD_TOKENS = {"easy": 30e3, "mid": 80e3, "hard": 200e3}
REVIEW_SHARE, AUDIT_SHARE = 0.3, 0.5         # review and audit effort relative to the card
PRIORITY = ["release", "audit", "review", "card", "redteam", "reconcile", "decompose", "synthesis",
            "critique", "inquiry"]             # downstream first


def p_pass(ci: float, d: float) -> float:
    return 1 / (1 + math.exp(-(SLOPE * (ci - d) + P0)))


# ---------------------------------------------------------------- entities
@dataclass
class Agent:
    cfg: Config
    idx: int
    roles: set | None = None          # None = pulls anything it is licensed for
    busy_until: float = 0.0
    busy_by_kind: dict = field(default_factory=lambda: defaultdict(float))
    queue: list = field(default_factory=list)   # baseline push queue
    spend: float = 0.0                          # USD after warm-up
    tokens: float = 0.0                         # tokens after warm-up
    cap_h_week: float | None = None             # subscription cap: busy hours per week, then idle
    week_used: dict = field(default_factory=lambda: defaultdict(float))

    @property
    def tier(self):
        return self.cfg.tier

    def hours(self, base: float) -> float:
        return base * math.sqrt(100 / max(self.cfg.speed, 10))


@dataclass(eq=False)
class Idea:
    iid: int
    start: float
    req_d: list
    captured: set = field(default_factory=set)
    mapped: set = field(default_factory=set)
    pending: int = 0
    participants: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    stage: str = "inquiry"
    rounds_left: int = 0
    gap_loops: int = 0
    done: bool = False
    owner: object = None              # solo / peer: the agent that owns the idea


@dataclass(eq=False)
class Card:
    idea: Idea
    band: str
    d: float
    ambiguous: bool
    defective: bool = False
    accepted: bool = False
    attempts: int = 0
    worker_tier: int = 0
    author: str = ""


@dataclass
class Task:
    kind: str
    idea: Idea
    card: Card | None = None
    d: float = 0.0
    born: float = 0.0
    exclude: set = field(default_factory=set)


class Sim:
    def __init__(self, org: str, agents: list[Agent], seed: int, wip: int, K=3, D=2, council_rounds=1,
                 redteam=True, audit=True, horizon=7 * 168, warmup=168, licences=True, independence=True,
                 hardest_first=True, overconf=0.0, conflict_k=0.0):
        self.licences, self.independence, self.hardest_first = licences, independence, hardest_first
        self.overconf, self.conflict_k = overconf, conflict_k
        self.cards_active = 0
        if org in ("solo", "peer"):
            K, council_rounds, D, redteam, audit = 1, 0, 1, False, False
            licences = self.licences = False
            if org == "solo":
                independence = self.independence = False
        self.org, self.agents, self.rng = org, agents, random.Random(seed)
        self.K, self.D, self.council_rounds, self.redteam, self.audit = K, D, council_rounds, redteam, audit
        self.wip, self.horizon, self.warmup = wip, horizon, warmup
        self.t = 0.0
        self.events = []
        self.seq = 0
        self.queues = defaultdict(list)
        self.ideas_open = 0
        self.next_id = 0
        self.released = []
        self.cost = 0.0
        self.wait = defaultdict(list)
        self.drops = defaultdict(int)
        self.open_ideas = []
        if org == "baseline":
            self.director = next(a for a in agents if a.roles and "director" in a.roles)
            self.checker = next(a for a in agents if a.roles and "checker" in a.roles)
            self.workers = [a for a in agents if a.roles == {"worker"}]

    # -- event plumbing
    def at(self, time, fn, *args):
        self.seq += 1
        heapq.heappush(self.events, (time, self.seq, fn, args))

    def run(self):
        self.top_ci = max(a.cfg.ci for a in self.agents)
        if self.org != "baseline":
            self.at(2.0, self.orphan_sweep)
        for _ in range(self.wip):
            self.new_idea()
        self.dispatch()
        while self.events and self.events[0][0] <= self.horizon:
            self.t, _, fn, args = heapq.heappop(self.events)
            fn(*args)
            self.dispatch()
        return self

    # -- ideas
    def new_idea(self):
        rng = self.rng
        idea = Idea(self.next_id, self.t, [rng.gauss(REQ_BASE, REQ_SPREAD) for _ in range(R_REQ)])
        self.next_id += 1
        self.ideas_open += 1
        self.open_ideas.append(idea)
        if self.org == "baseline":
            self.push(self.director, Task("inquiry", idea, born=self.t))
        else:
            idea.pending = self.K
            for _ in range(self.K):
                self.enqueue(Task("inquiry", idea, born=self.t))

    def enqueue(self, task: Task):
        if not task.d:
            task.d = TASK_DIFF.get(task.kind, 0.0)
        task.born = self.t
        self.queues[task.kind].append(task)

    def push(self, agent: Agent, task: Task):
        if not task.d:
            task.d = TASK_DIFF.get(task.kind, 0.0)
        task.born = self.t
        agent.queue.append(task)

    # -- dispatch
    def eligible(self, a: Agent, task: Task) -> bool:
        aged = self.t - task.born >= ORPHAN_H
        if self.org in ("solo", "peer"):
            owned = task.idea.owner
            shared = self.org == "peer" and task.kind in ("review", "release")
            if not shared:
                if owned is None:          # take a new idea only when free of others
                    return not any(i is not task.idea and i.owner is a and not i.done for i in self.open_ideas)
                return owned is a
        if self.independence and a.cfg.name in task.exclude and not aged:     # R13 also relaxes independence
            return False
        if task.kind == "inquiry" or not self.licences:
            return True
        ci = a.cfg.ci + self.overconf                    # self-licensed: the agent's own (inflated) view
        if task.kind in ("review", "audit"):
            ok = p_pass(ci, task.card.d) >= REVIEW_LICENCE_P
        else:
            ok = p_pass(ci, task.d) >= LICENCE_P
        if not ok and task.kind != "card" and self.t - task.born >= ORPHAN_H:
            ok = a.cfg.ci >= self.top_ci - 10            # R13: open to the most capable
        return ok

    def orphan_sweep(self):
        """R13: split cards nobody is licensed to take after ORPHAN_H hours."""
        q = self.queues["card"]
        for task in list(q):
            if self.t - task.born < ORPHAN_H:
                continue
            if any(self.eligible(a, task) for a in self.agents):
                continue
            q.remove(task)
            card = task.card
            idea = card.idea
            idea.cards.remove(card)
            self.drops["split"] += 1
            for _ in range(2):
                c = Card(idea, card.band, max(5.0, card.d - SPLIT_EASIER), card.ambiguous)
                idea.cards.append(c)
                self.send_card(c)
        self.at(self.t + 2.0, self.orphan_sweep)

    def dispatch(self):
        week = int(self.t // 168)
        free = [a for a in self.agents if a.busy_until <= self.t
                and (a.cap_h_week is None or a.week_used[week] < a.cap_h_week)]
        self.rng.shuffle(free)
        for a in free:
            task = self.pick(a)
            if task is not None:
                self.start(a, task)

    def pick(self, a: Agent):
        if self.org == "baseline":
            return a.queue.pop(0) if a.queue else None
        for kind in PRIORITY:
            q = self.queues[kind]
            if not q:
                continue
            in_role = a.roles is None or kind in a.roles
            # R13 also lifts seat restrictions on work orphaned for twice the limit
            cands = [t for t in q if (in_role or self.t - t.born >= 2 * ORPHAN_H) and self.eligible(a, t)]
            if not cands:
                continue
            task = max(cands, key=lambda t: t.d) if kind == "card" and self.hardest_first else cands[0]
            q.remove(task)
            if self.org in ("solo", "peer") and task.idea.owner is None:
                task.idea.owner = a
            if self.independence and a.cfg.name in task.exclude:
                self.drops["independence_waived"] += 1  # recorded in the Ledger
            if not in_role:
                self.drops["seat_rule_waived"] += 1
            return task
        return None

    def start(self, a: Agent, task: Task):
        if task.kind in ("card", "review", "audit"):
            base = CARD_HOURS[task.card.band] * (1 if task.kind == "card" else REVIEW_SHARE if task.kind == "review" else AUDIT_SHARE)
            tokens = CARD_TOKENS[task.card.band] * (1 if task.kind == "card" else REVIEW_SHARE if task.kind == "review" else AUDIT_SHARE)
        else:
            base, tokens = TASK_HOURS[task.kind], TASK_TOKENS[task.kind]
        dur = a.hours(base)
        if task.kind == "card":
            self.cards_active += 1
        a.busy_until = self.t + dur
        a.week_used[int(self.t // 168)] += dur
        if self.t >= self.warmup:
            a.busy_by_kind[task.kind] += dur
            self.wait[task.kind].append(self.t - task.born)
        self.cost += a.cfg.price * tokens / 1e6
        if self.t >= self.warmup:
            a.spend += a.cfg.price * tokens / 1e6
            a.tokens += tokens
        self.at(self.t + dur, self.finish, a, task)

    # -- task outcomes
    def finish(self, a: Agent, task: Task):
        if task.kind == "card":
            self.cards_active -= 1
        getattr(self, "on_" + task.kind)(a, task)

    def on_inquiry(self, a, task):
        idea = task.idea
        for r, d in enumerate(idea.req_d):
            if self.rng.random() < p_pass(a.cfg.ci, d):
                idea.captured.add(r)
        idea.participants.append(a.cfg.name)
        if self.org == "baseline":                      # Director plans alone, right away
            self.push(self.director, Task("decompose", idea))
            return
        idea.pending -= 1
        # commit-before-view: remaining submissions must come from other agents
        for t in self.queues["inquiry"]:
            if t.idea is idea:
                t.exclude.add(a.cfg.name)
        if idea.pending == 0:
            self.start_council(idea)

    def start_council(self, idea):
        if self.council_rounds == 0:
            self.enqueue(Task("synthesis", idea))
            return
        idea.rounds_left = self.council_rounds
        self.council_round(idea)

    def council_round(self, idea):
        idea.pending = len(idea.participants)
        for name in idea.participants:
            t = Task("critique", idea)
            t.exclude = set(n for n in idea.participants if n != name) if False else set()
            self.enqueue(t)

    def on_critique(self, a, task):
        idea = task.idea
        for r, d in enumerate(idea.req_d):
            if r not in idea.captured and self.rng.random() < CRITIQUE_FIND * p_pass(a.cfg.ci, d + 5):
                idea.captured.add(r)
        idea.pending -= 1
        if idea.pending == 0:
            idea.rounds_left -= 1
            if idea.rounds_left > 0:
                self.council_round(idea)
            else:
                self.enqueue(Task("synthesis", idea))

    def on_synthesis(self, a, task):
        # the coverage rule stops a synthesis from dropping a captured requirement
        self.at(self.t + HUMAN_FRAMING_H, self.start_planning, task.idea)

    def start_planning(self, idea):
        idea.pending = self.D
        idea.participants = []
        for _ in range(self.D):
            self.enqueue(Task("decompose", idea))

    def on_decompose(self, a, task):
        idea = task.idea
        for r in idea.captured:
            if self.rng.random() < p_pass(a.cfg.ci, idea.req_d[r] + 8):
                idea.mapped.add(r)
        if self.org == "baseline":
            self.planner_ci = a.cfg.ci
            self.at(self.t + HUMAN_FRAMING_H, self.make_cards, idea, a.cfg.ci, None)
            return
        idea.pending -= 1
        idea.participants.append(a.cfg.name)
        for t in self.queues["decompose"]:
            if t.idea is idea:
                t.exclude.add(a.cfg.name)
        if idea.pending == 0:
            self.enqueue(Task("reconcile", idea))

    def on_reconcile(self, a, task):
        task.idea.reconcile_ci = a.cfg.ci
        if self.redteam:
            t = Task("redteam", task.idea)
            t.exclude = {a.cfg.name}
            self.enqueue(t)
        else:
            self.at(self.t + HUMAN_PLAN_H, self.make_cards, task.idea, a.cfg.ci, None)

    def on_redteam(self, a, task):
        idea = task.idea
        for r in range(R_REQ):
            if r not in idea.mapped and self.rng.random() < p_pass(a.cfg.ci, idea.req_d[r] + 10):
                idea.mapped.add(r)                     # red team finds a gap; planners add cards
        self.at(self.t + HUMAN_PLAN_H, self.make_cards, idea, idea.reconcile_ci, None)

    def make_cards(self, idea, planner_ci, only=None):
        rng = self.rng
        reqs = sorted(idea.mapped) if only is None else only
        new = []
        for r in reqs:
            for _ in range(rng.choice(CARDS_PER_REQ)):
                band = rng.choices(list(CARD_MIX), weights=list(CARD_MIX.values()))[0]
                lo, hi = CARD_RANGE[band]
                amb = rng.random() < AMBIG_SCALE * (1 - p_pass(planner_ci, TASK_DIFF["reconcile"]))
                new.append(Card(idea, band, rng.uniform(lo, hi), amb))
        idea.cards.extend(new)
        idea.stage = "build"
        for c in new:
            self.send_card(c)
        if not new:                                  # r12 fix: an empty plan goes to the Release Gate,
            self.check_idea(idea)                    # which finds the unmapped intent, instead of stalling

    def send_card(self, card: Card):
        task = Task("card", card.idea, card, d=card.d)
        if self.org == "baseline":
            est = card.d + self.rng.gauss(0, DIRECTOR_NOISE)
            want = tier_of(est)
            tiers = sorted({w.tier for w in self.workers})
            pick = [t for t in tiers if t <= want]
            target = max(pick) if pick else min(tiers)
            ws = [w for w in self.workers if w.tier == target]
            w = min(ws, key=lambda w: len(w.queue))
            self.push(w, task)
        else:
            self.enqueue(task)

    def on_card(self, a, task):
        card = task.card
        p = p_pass(a.cfg.ci, card.d) * (AMBIG_PENALTY if card.ambiguous else 1)
        card.attempts += 1
        card.worker_tier = a.tier
        card.author = a.cfg.name
        if self.conflict_k and self.rng.random() < 1 - math.exp(-self.conflict_k * self.cards_active):
            self.drops["merge_conflict"] += 1          # clashed with work in flight: redo
            if self.org == "baseline":
                self.push(a, task)
            else:
                self.enqueue(Task("card", card.idea, card, d=card.d))
            return
        card.defective = self.rng.random() >= p
        if card.defective and self.rng.random() < TEST_CATCH:
            self.drops["test_fail"] += 1
            if card.ambiguous and card.attempts >= 3 and self.org != "baseline":
                card.ambiguous = False                 # returned to Planning for clarification
                self.drops["clarify"] += 1
                self.at(self.t + 1.0, self.send_card, card)
                return
            if self.org == "baseline":
                self.push(a, task)                    # same worker retries
            else:
                t = Task("card", card.idea, card, d=card.d)
                t.exclude = {a.cfg.name} if card.attempts % 2 == 1 else set()
                self.enqueue(t)
            return
        review = Task("review", card.idea, card, d=card.d + 5)
        review.exclude = {a.cfg.name}
        if self.org == "baseline":
            self.push(self.checker, review)
        else:
            self.enqueue(review)

    def on_review(self, a, task):
        card = task.card
        own = SELF_CATCH if a.cfg.name == card.author else 1.0
        if card.defective and self.rng.random() < own * p_pass(a.cfg.ci, card.d + 5):
            self.drops["review_reject"] += 1
            self.send_card(card)
            return
        if not card.defective and self.rng.random() < FALSE_REJECT:
            self.drops["false_reject"] += 1
            self.send_card(card)
            return
        card.accepted = True
        if self.org != "baseline" and self.audit and self.rng.random() < AUDIT_RATE:
            self.enqueue(Task("audit", card.idea, card, d=card.d))
        self.check_idea(card.idea)

    def on_audit(self, a, task):
        card = task.card
        if card.defective and self.rng.random() < p_pass(a.cfg.ci, card.d):
            self.drops["audit_catch"] += 1
            card.accepted = False
            self.send_card(card)

    def check_idea(self, idea):
        if idea.stage == "build" and all(c.accepted for c in idea.cards):
            idea.stage = "release"
            t = Task("release", idea)
            if self.org == "baseline":
                self.push(self.director, t)
            else:
                self.enqueue(t)

    def on_release(self, a, task):
        idea = task.idea
        if idea.done or idea.stage != "release":   # r12 fix: a late audit catch could queue a second release
            self.drops["stale_release"] += 1
            return
        rng = self.rng
        if self.org == "baseline":
            gap_catch, defect_catch = 0.0, 0.0        # no independent release gate
        else:
            gap_catch, defect_catch = RELEASE_GAP_CATCH, RELEASE_DEFECT_CATCH
            if not self.independence and any(c.author == a.cfg.name for c in idea.cards):
                gap_catch, defect_catch = SELF_CATCH * gap_catch, SELF_CATCH * defect_catch
        bad = [c for c in idea.cards if c.defective and rng.random() < defect_catch]
        gaps = [r for r in range(R_REQ) if r not in idea.mapped and rng.random() < gap_catch]
        if bad or (gaps and idea.gap_loops < 2):
            idea.stage = "build"
            for c in bad:
                c.accepted = False
                self.drops["release_defect"] += 1
                self.send_card(c)
            if gaps and idea.gap_loops < 2:
                idea.gap_loops += 1
                self.drops["intent_gap_loop"] += 1
                idea.mapped.update(gaps)
                self.at(self.t + HUMAN_PLAN_H, self.make_cards, idea, a.cfg.ci, gaps)
            return
        idea.done = True
        if idea.start >= self.warmup:
            self.released.append(dict(
                lead=self.t - idea.start,
                coherence=len(idea.mapped) / R_REQ,
                escaped=sum(c.defective for c in idea.cards),
                cards=len(idea.cards)))
        self.ideas_open -= 1
        self.open_ideas.remove(idea)
        self.new_idea()


# ---------------------------------------------------------------- building organisations
def draw_agents(counts: dict, rng: random.Random, roles=None) -> list[Agent]:
    out = []
    for tier, n in counts.items():
        for i in range(n):
            out.append(Agent(rng.choice(POOL[tier]), len(out), roles))
    return out


def baseline_org(workers: dict, rng: random.Random, director_tier=1, checker_tier=1) -> list[Agent]:
    d = Agent(rng.choice(POOL[director_tier]), 0, {"director"})
    c = Agent(rng.choice(POOL[checker_tier]), 1, {"checker"})
    ws = [Agent(rng.choice(POOL[t]), 2 + i, {"worker"}) for i, t in
          enumerate(t for t, n in workers.items() for _ in range(n))]
    return [d, c] + ws


def per_agent(sim: Sim, weeks: float) -> dict:
    """Totals per model (several seats may run the same model)."""
    out = {}
    for a in sim.agents:
        r = out.setdefault(a.cfg.name, {"busy_h_per_week": 0.0, "usd_per_week": 0.0, "mtok_per_week": 0.0, "seats": 0})
        r["busy_h_per_week"] += sum(a.busy_by_kind.values()) / weeks
        r["usd_per_week"] += a.spend / weeks
        r["mtok_per_week"] += a.tokens / 1e6 / weeks
        r["seats"] += 1
    return out


def measure(sim: Sim) -> dict:
    weeks = (sim.horizon - sim.warmup) / 168
    rel = sim.released
    busy = defaultdict(float)
    for a in sim.agents:
        for k, v in a.busy_by_kind.items():
            busy[k] += v
    capacity = len(sim.agents) * (sim.horizon - sim.warmup)
    util = sum(busy.values()) / capacity
    agent_util = [sum(a.busy_by_kind.values()) / (sim.horizon - sim.warmup) for a in sim.agents]
    role_util = defaultdict(list)
    for a, u in zip(sim.agents, agent_util):
        role = next(iter(a.roles)) if a.roles else "agent"
        role_util[f"{role} T{a.tier}"].append(u)
    return {
        "ideas_per_week": len(rel) / weeks,
        "lead_h": statistics.median(r["lead"] for r in rel) if rel else float("nan"),
        "coherence": statistics.mean(r["coherence"] for r in rel) if rel else float("nan"),
        "escaped_per_idea": statistics.mean(r["escaped"] for r in rel) if rel else float("nan"),
        "cost_per_idea": sim.cost / max(1, len(rel)) if rel else float("nan"),
        "clean_per_week": sum(1 for r in rel if r["coherence"] >= 1.0 and r["escaped"] == 0) / weeks,
        "utilisation": util,
        "max_agent_util": max(agent_util),
        "busy_share": {k: v / max(1e-9, sum(busy.values())) for k, v in busy.items()},
        "role_util": {k: statistics.mean(v) for k, v in role_util.items()},
        "wait_h": {k: statistics.mean(v) for k, v in sim.wait.items() if v},
        "drops_per_idea": {k: v / max(1, len(rel)) for k, v in sim.drops.items()},
        "per_agent": per_agent(sim, weeks),
    }


def mean_measure(builder, n=6, **simkw) -> dict:
    rows = []
    for s in range(n):
        rng = random.Random(1000 + s)
        org, agents = builder(rng)
        rows.append(measure(Sim(org, agents, seed=s, **simkw).run()))
    out = {}
    for k in rows[0]:
        if k == "per_agent":            # nested: average each agent's fields over the seeds it appears in
            keys = set().union(*(r[k].keys() for r in rows))
            out[k] = {kk: {f: statistics.mean(r[k][kk][f] for r in rows if kk in r[k]) for f in next(r[k][kk] for r in rows if kk in r[k])}
                      for kk in keys}
        elif isinstance(rows[0][k], dict):
            keys = set().union(*(r[k].keys() for r in rows))
            out[k] = {kk: statistics.mean(r[k].get(kk, 0.0) for r in rows) for kk in keys}
        else:
            vals = [r[k] for r in rows if not (isinstance(r[k], float) and math.isnan(r[k]))]
            out[k] = statistics.mean(vals) if vals else float("nan")
    return out
