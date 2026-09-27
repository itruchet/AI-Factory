"""Our rules inside the second simulation (r12.1 cross-check).

external/ holds the independent simulation Isa supplied (built with another
assistant; unchanged). Its shared pool lets any agent claim any task first-come
first-served, and its "institutions" hold card review until the whole idea is
built. Neither is a rule of our constitution. This file subclasses it, without
editing it, to add our rules one at a time:

  licence       R2 evidence licences: an agent may take a build or check task
                only if its track-record pass chance on it clears 0.6 (checks:
                0.5; framing, planning, release: 0.6 across the idea's
                requirements). The record reflects tier skill and difficulty; it
                cannot see latent family blind spots. R13: a task waiting an hour,
                or nothing running at all, opens to anyone.
  family_review no verification or audit by the author's model family
                (instances of a family are one epistemic source).
  streaming     our institutions review each card as it is built (no
                whole-idea barrier); dependants may still start on built work.

Measured exactly as the external model does: useful idea-equivalents per week,
intent, escaped defects per release, completion, cost per useful idea, and the
original floors (intent >= 97%, escaped defects <= 0.25).

Run: python3 probes/crosscheck/our_rules_in_their_sim.py   (about 10 minutes)
"""

from __future__ import annotations

import dataclasses
import json
import math
import statistics
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "external"))
import simulator as ext  # noqa: E402

SEEDS = 24
IDEAS = 32
LICENCE_P, CHECK_P, ORPHAN_H = 0.60, 0.50, 1.0


@dataclasses.dataclass
class RConfig(ext.Config):
    licence: bool = False
    family_review: bool = False
    streaming: bool = False


class RSim(ext.Simulation):
    def est(self, a, s, reqs, size=1):
        """Track-record pass chance: tier skill vs difficulty; blind spots are not visible to a record."""
        p = ext.PROFILES[a["tier"]]
        pen = self.c.packet_context_penalty * (size - 1) ** 1.2
        return statistics.mean(1 / (1 + math.exp(-(self.c.slope * (p["score"] - self.workload[s["id"]]["difficulty"][r] - pen
                                                                    + 6 * math.log2(self.c.effort)) + math.log(3))))
                               for r in reqs)

    def eligible(self, a, row, s):
        if not super().eligible(a, row, s):
            return False
        jid, i, kind, b, g, created = row
        relax = (self.t - created >= ORPHAN_H) or not self.heap
        if self.c.family_review and kind in ("verify", "audit") and b >= 0 and not relax:
            if a["family"] == s["blocks"][b].get("family"):
                return False
        if self.c.licence and not relax and kind != "inquiry":
            if b >= 0:
                reqs = s["blocks"][b]["reqs"]
                need = LICENCE_P if kind == "code" else CHECK_P
                if self.est(a, s, reqs, len(reqs)) < need:
                    return False
            elif self.est(a, s, list(range(8))) < LICENCE_P:
                return False
        return True

    def refresh(self, s):
        if not self.c.streaming or self.c.architecture != "institutions":
            return super().refresh(s)
        return self._refresh_streaming(s)

    def _refresh_streaming(self, s):
        """Parent refresh with barrier = False, collective controls kept (institutions semantics)."""
        if s["phase"] != "work":
            return
        bs = s["blocks"]
        for b, x in enumerate(bs):
            if x["status"] == "waiting" and all(bs[d]["status"] in ("built", "verify_queued", "audit_queued", "verified") for d in x["deps"]):
                x["status"] = "code_queued"
                self.add(s, "code", b, x["generation"])
        for b, x in enumerate(bs):
            if x["status"] == "built":
                x["status"] = "verify_queued"
                self.add(s, "verify", b, x["generation"])
        for b, x in enumerate(bs):
            if x["status"] == "verified" and not x["audited"] and self.u(s["id"], "audit_sample", b) < self.c.audit_rate:
                x["status"] = "audit_queued"
                self.add(s, "audit", b, x["generation"])
        if all(x["status"] == "verified" for x in bs) and not s["release_pending"]:
            s["release_pending"] = True
            s["release_votes"] = []
            s["release_authors"] = []
            for v in range(2):
                self.add(s, "release", g=s["round"] * 2 + v)


def run_one(cfg):
    return RSim(cfg).run()


VARIANTS = {
    "external institutions (barrier, FIFO)": dict(architecture="institutions"),
    "external evidence graph (FIFO)": dict(architecture="evidence_graph"),
    "institutions + streaming review": dict(architecture="institutions", streaming=True),
    "institutions + licences": dict(architecture="institutions", licence=True),
    "institutions + streaming + licences": dict(architecture="institutions", streaming=True, licence=True),
    "institutions + streaming + licences + family review": dict(architecture="institutions", streaming=True, licence=True, family_review=True),
    "evidence graph + licences": dict(architecture="evidence_graph", licence=True),
    "evidence graph + licences + family review": dict(architecture="evidence_graph", licence=True, family_review=True),
}
MIXES = [(6, 3, 3), (4, 7, 1), (10, 2, 0)]
SCENARIOS = {"reference": {}, "correlated_errors": {"correlation": 0.45}, "no_family_blindspots": {"correlation": 0.0}}


def job(args):
    scen, var, mix, seed = args
    cfg = RConfig(ideas=IDEAS, mix=mix, seed=seed, **SCENARIOS[scen], **VARIANTS[var])
    r = run_one(cfg)
    return dict(scenario=scen, variant=var, mix="/".join(map(str, mix)), seed=seed,
                **{k: r[k] for k in ("useful_week", "intent", "defects", "completion", "cost_useful", "lead")})


def ci95(xs):
    m = statistics.mean(xs)
    h = 2.069 * statistics.stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else 0.0   # t(23)
    return m, h


def main():
    jobs = [(sc, var, mix, 900 + s) for sc in SCENARIOS for var in VARIANTS for mix in MIXES for s in range(SEEDS)
            if sc == "reference" or mix == (6, 3, 3)]
    with ProcessPoolExecutor() as ex:
        rows = list(ex.map(job, jobs, chunksize=4))
    lines = [f"OUR RULES INSIDE THE EXTERNAL SIMULATION ({SEEDS} paired seeds, {IDEAS} ideas each; 95% t intervals)",
             "useful idea-equivalents/week | intent | escaped defects per release | completion | cost per useful | floors (intent>=0.97, defects<=0.25)"]
    table = {}
    for sc in SCENARIOS:
        for mix in MIXES:
            sel = [r for r in rows if r["scenario"] == sc and r["mix"] == "/".join(map(str, mix))]
            if not sel:
                continue
            lines.append(f"\n[{sc} / mix {'/'.join(map(str, mix))}]")
            base = {r["seed"]: r["useful_week"] for r in sel if r["variant"] == "external institutions (barrier, FIFO)"}
            for var in VARIANTS:
                rs = [r for r in sel if r["variant"] == var]
                u, uh = ci95([r["useful_week"] for r in rs])
                gain, gh = ci95([r["useful_week"] / base[r["seed"]] - 1 for r in rs])
                intent = statistics.mean(r["intent"] for r in rs)
                d, dh = ci95([r["defects"] for r in rs])
                comp = statistics.mean(r["completion"] for r in rs)
                cost = statistics.mean(r["cost_useful"] for r in rs)
                ok = "PASS" if intent >= 0.97 and d <= 0.25 else "    "
                lines.append(f"  {var:<52} {u:6.1f}±{uh:4.1f}  vs ext. inst. {gain:+5.0%}±{gh:3.0%}  intent {intent:.3f}  "
                             f"defects {d:.2f}±{dh:.2f}  completion {comp:.2f}  ${cost:5.2f}  {ok}")
                table.setdefault(sc, {}).setdefault("/".join(map(str, mix)), {})[var] = dict(
                    useful=u, useful_ci=uh, gain=gain, gain_ci=gh, intent=intent, defects=d, defects_ci=dh, completion=comp, cost_useful=cost,
                    passes=bool(ok.strip()))
    text = "\n".join(lines)
    print(text)
    (HERE / "our_rules_in_their_sim_results.txt").write_text(text + "\n")
    json.dump(table, open(HERE / "our_rules_in_their_sim.json", "w"), indent=1)


if __name__ == "__main__":
    main()
