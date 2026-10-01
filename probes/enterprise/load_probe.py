"""Load probe: enterprise systems of record on primitive stores (r12.10).

Question: can one Factory carry project management, incident (ITSM), HCM, CRM and ERP, and where does it break first?

Every system of record is rebuilt from a few primitive record types (primitives.md):
  Party, Asset, Agreement, Work, Balance, Event, Content, Rule, plus Relations in the read model.
They live in eight primitive stores, physically separated only where a reason demands it:
  S1 identity (people and organisations: personal data, crypto-shredding keys, residency)
  S2 balances (double-entry quantities: money, leave, stock, budget: strictly transactional, peak batches)
  S3 work (cards, tickets, incidents, cases, opportunities: high-churn state machines)
  S4 records (assets, agreements: reference data)
  S5 event log (append-only, hash-chained)
  S6 content (documents and artifacts: object storage)
  S7 policy (rules, runbooks, charters: read-mostly, protected)
  S8 read model (cross-domain views: the lakehouse)

Three designs are loaded with the same month of work, hour by hour:
  D1 one store       every primitive in one database node; one global hash chain written per event;
                     cross-domain reports read the transactional store
  D2 silos per SoR   one database per system of record, as today; a chain per system written per event;
                     cross-domain reports and agent context fan out to every system; no shared read model
  D3 primitives      the eight stores, each partitionable; a hash chain per domain, sealed in batches;
                     reports and agent context read the read model

The workload is per employee-hour [ASSUMPTION throughout: rates, operation counts and node capacities are
illustrative and are swept in the sensitivity run]. Results are reported as the busiest hour of the month:
nodes needed at 60% target utilisation for components that scale out, utilisation for components that do not,
agent instances against the vendor rate-limit cap, and agent cost per month.

Run: python3 probes/enterprise/load_probe.py   (seconds; no model spend)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).parent
STORES = ["S1 identity", "S2 balances", "S3 work", "S4 records", "S5 events", "S6 content", "S7 policy", "S8 read model"]
SHORT = {"S1 identity": "S1", "S2 balances": "S2", "S3 work": "S3", "S4 records": "S4", "S5 events": "S5",
         "S6 content": "S6", "S7 policy": "S7", "S8 read model": "S8"}

# ---------------------------------------------------------------- capacities [ASSUMPTION]
CAP = dict(
    db_write=3000.0,          # row writes per second per database node at full use
    db_read=30000.0,          # row reads per second per database node
    chain_serial=1000.0,      # appends per second to one hash chain written and flushed per event
    chain_batched=100000.0,   # appends per second to one hash chain sealed in batches
    workflow=2000.0,          # durable workflow steps per second per workflow-engine database (Hatchet on Postgres)
    policy=20000.0,           # policy decisions per second per policy-engine instance (OPA or Cedar)
    read_query=200.0,         # analytical queries per second per read-model node
)
TARGET_UTIL = 0.6
AGENT_CAP = {"rate limits as modelled (48)": 48, "raised limits (500)": 500}
AGENT_USD_H = 1.20            # $ per busy agent hour: Gemini 3.8 Flash on the token model (select6)

# ---------------------------------------------------------------- workload [ASSUMPTION]
# Each request type: rate per employee per business hour, the system of record it belongs to, and its operations:
# reads/writes per primitive store, event appends, workflow steps, policy decisions, read-model queries,
# and agent seconds. 'librarian' requests vary in shape and go to agents unless promoted (R25).
W = lambda **k: k
REQUESTS = {
    "card update":           dict(sor="PM",   rate=0.50,  ops=W(r={"S3 work": 2}, w={"S3 work": 1}, ev=1, wf=1, pol=1)),
    "planning help":         dict(sor="PM",   rate=0.02,  ops=W(r={"S3 work": 20, "S6 content": 2}, ev=1, pol=1, q=2, agent=60), librarian=True),
    "ticket":                dict(sor="ITSM", rate=0.02,  ops=W(r={"S4 records": 1, "S1 identity": 1}, w={"S3 work": 2}, ev=2, wf=3, pol=1)),
    "ticket triage":         dict(sor="ITSM", rate=0.01,  ops=W(r={"S3 work": 5, "S4 records": 3}, ev=1, pol=1, q=1, agent=30), librarian=True),
    "monitoring signal":     dict(sor="ITSM", rate=1.00,  ops=W(r={"S3 work": 1}, ev=1, wf=0.1), always=True),
    "HR question":           dict(sor="HCM",  rate=0.05,  ops=W(r={"S1 identity": 1, "S2 balances": 2, "S4 records": 1}, pol=2, q=1, agent=20), librarian=True),
    "leave booking":         dict(sor="HCM",  rate=0.005, ops=W(r={"S2 balances": 1, "S1 identity": 1}, w={"S2 balances": 2, "S3 work": 1}, ev=2, wf=2, pol=2)),
    "CRM interaction":       dict(sor="CRM",  rate=0.06,  ops=W(r={"S1 identity": 1}, w={"S3 work": 1, "S1 identity": 0.2, "S6 content": 0.3}, ev=1, wf=1, pol=1)),
    "account research":      dict(sor="CRM",  rate=0.02,  ops=W(r={"S1 identity": 3, "S3 work": 10, "S6 content": 3}, pol=1, q=2, agent=15), librarian=True),
    "ERP posting":           dict(sor="ERP",  rate=0.50,  ops=W(r={"S4 records": 1}, w={"S2 balances": 2}, ev=2, wf=2, pol=1)),
    "cross-domain report":   dict(sor="ALL",  rate=0.01,  ops=W(pol=1, q=5, agent=90), librarian=True),
}
PAYROLL = dict(w={"S2 balances": 40}, ev=40, wf=5, pol=1)        # per employee, monthly run, day 28, 10:00-14:00
CLOSE_MULT = 10.0                                                # ERP postings x10 on the last two business days
COMMERCE = dict(r={"S1 identity": 1}, w={"S2 balances": 4, "S4 records": 1}, ev=3, wf=3, pol=1)   # per customer order
PROMOTED = dict(wf=2, q=3)                                       # a promoted librarian request: a fixed workflow and view


def hours():
    """Each hour of a 30-day month: (day, hour, business-hours flag)."""
    for day in range(1, 31):
        weekday = (day - 1) % 7 < 5
        for h in range(24):
            yield day, h, weekday and 9 <= h < 18


def load(employees, commerce_peak, promotion):
    """Per-hour demand on every component, as rates per second."""
    out = []
    for day, h, biz in hours():
        dem = dict(r={s: 0.0 for s in STORES}, w={s: 0.0 for s in STORES}, ev={}, wf=0.0, pol=0.0, q=0.0, agent=0.0,
                   fanout=0.0, rs={}, ws={})   # rs / ws: row reads and writes by system of record (for silos)
        for name, rq in REQUESTS.items():
            if rq.get("always"):
                k = 1.0
            else:
                k = 1.0 if biz else 0.05
            if rq["sor"] == "ERP" and day in (29, 30) and biz:
                k *= CLOSE_MULT
            per_s = employees * rq["rate"] * k / 3600
            ops = rq["ops"]
            frac_agent = 1.0
            if rq.get("librarian"):
                frac_agent = 1.0 - promotion
                dem["wf"] += per_s * promotion * PROMOTED["wf"]
                dem["q"] += per_s * promotion * PROMOTED["q"]
            for s, n in ops.get("r", {}).items():
                dem["r"][s] += per_s * n
                dem["rs"][rq["sor"]] = dem["rs"].get(rq["sor"], 0.0) + per_s * n
            for s, n in ops.get("w", {}).items():
                dem["w"][s] += per_s * n
                dem["ws"][rq["sor"]] = dem["ws"].get(rq["sor"], 0.0) + per_s * n
            dem["ev"][rq["sor"]] = dem["ev"].get(rq["sor"], 0.0) + per_s * ops.get("ev", 0)
            dem["wf"] += per_s * ops.get("wf", 0)
            dem["pol"] += per_s * ops.get("pol", 0)
            dem["q"] += per_s * ops.get("q", 0) * (frac_agent if rq.get("librarian") else 1.0)
            dem["agent"] += per_s * ops.get("agent", 0) * frac_agent
            if rq["sor"] == "ALL":
                dem["fanout"] += per_s * ops.get("q", 0) * (frac_agent + promotion)
        if day == 28 and 10 <= h < 14:                                   # payroll run spread over four hours
            per_s = employees / (4 * 3600)
            for s, n in PAYROLL["w"].items():
                dem["w"][s] += per_s * n
                dem["ws"]["HCM"] = dem["ws"].get("HCM", 0.0) + per_s * n
            dem["ev"]["HCM"] = dem["ev"].get("HCM", 0.0) + per_s * PAYROLL["ev"]
            dem["wf"] += per_s * PAYROLL["wf"]
            dem["pol"] += per_s * PAYROLL["pol"]
        if commerce_peak:
            diurnal = 0.5 + 0.5 * math.sin(math.pi * (h - 8) / 12) if 8 <= h <= 20 else 0.2
            orders = commerce_peak * max(0.2, diurnal)
            for s, n in COMMERCE["r"].items():
                dem["r"][s] += orders * n
                dem["rs"]["COMMERCE"] = dem["rs"].get("COMMERCE", 0.0) + orders * n
            for s, n in COMMERCE["w"].items():
                dem["w"][s] += orders * n
                dem["ws"]["COMMERCE"] = dem["ws"].get("COMMERCE", 0.0) + orders * n
            dem["ev"]["COMMERCE"] = dem["ev"].get("COMMERCE", 0.0) + orders * COMMERCE["ev"]
            dem["wf"] += orders * COMMERCE["wf"]
            dem["pol"] += orders * COMMERCE["pol"]
        out.append(dem)
    return out


def assess(design, demand, cap, agent_cap):
    """Busiest-hour figures for one design. Components that scale out report nodes needed; components that cannot
    (a single database for everything, a single chain) report utilisation, where above 100% means it fails."""
    res = {}
    report_rows = 5 * 2000                      # rows a cross-domain report scans when there is no read model

    def worst(fn):
        return max(fn(d) for d in demand)

    if design == "D1 one store":
        res["database (one node)"] = ("util", worst(lambda d: sum(d["w"].values()) / cap["db_write"]
                                                    + (sum(d["r"].values()) + d["fanout"] * report_rows) / cap["db_read"]))
        res["hash chain (global, per event)"] = ("util", worst(lambda d: sum(d["ev"].values()) / cap["chain_serial"]))
    elif design == "D2 silos per SoR":
        sors = ["PM", "ITSM", "HCM", "CRM", "ERP", "COMMERCE"]
        for sor in sors:
            def u(d, sor=sor):        # each silo carries its own reads and writes, plus a share of every report's fan-out
                return d["ws"].get(sor, 0.0) / cap["db_write"] + (d["rs"].get(sor, 0.0) + d["fanout"] * report_rows / 5) / cap["db_read"]
            res[f"database: {sor} silo"] = ("util", worst(u))
            res[f"hash chain: {sor} (per event)"] = ("util", worst(lambda d, sor=sor: d["ev"].get(sor, 0.0) / cap["chain_serial"]))
    else:
        for s in STORES:
            if s in ("S5 events", "S8 read model"):
                continue
            res[f"{SHORT[s]} {s.split(' ', 1)[1]} (nodes)"] = ("nodes", worst(
                lambda d, s=s: d["w"][s] / cap["db_write"] + d["r"][s] / cap["db_read"]) / TARGET_UTIL)
        res["hash chain: busiest domain (batched)"] = ("util", worst(lambda d: max(d["ev"].values() or [0]) / cap["chain_batched"]))
        res["read model (nodes)"] = ("nodes", worst(lambda d: d["q"] / cap["read_query"]) / TARGET_UTIL)
    res["workflow engine (databases)"] = ("nodes", worst(lambda d: d["wf"] / cap["workflow"]) / TARGET_UTIL)
    res["policy engine (instances)"] = ("nodes", worst(lambda d: d["pol"] / cap["policy"]) / TARGET_UTIL)
    peak_agents = worst(lambda d: d["agent"])                  # agent-seconds per second = busy instances
    res["agents (instances at peak)"] = ("agents", peak_agents / TARGET_UTIL, agent_cap)
    month_agent_h = sum(d["agent"] for d in demand)            # instance-seconds per second summed over hours = hours
    res["agent cost ($/month)"] = ("usd", month_agent_h * AGENT_USD_H)
    return res


def first_bottleneck(res):
    worst_name, worst_v = None, 0.0
    for k, v in res.items():
        if v[0] == "util":
            x = v[1]
        elif v[0] == "agents":
            x = v[1] * TARGET_UTIL / v[2]
        else:
            continue
        if x > worst_v:
            worst_name, worst_v = k, x
    return worst_name, worst_v


def fmt(v):
    if v[0] == "util":
        return f"{v[1]:6.0%}" + (" FAILS" if v[1] > 1 else "")
    if v[0] == "nodes":
        return f"{max(1, math.ceil(v[1])):4d} node(s)"
    if v[0] == "agents":
        need = math.ceil(v[1])
        return f"{need:5d} needed / cap {v[2]}" + (" OVER CAP" if need > v[2] else "")
    return f"${v[1]:,.0f}"


def main():
    lines, out = [], {}

    def say(x=""):
        print(x, flush=True)
        lines.append(x)

    say("ENTERPRISE LOAD PROBE: busiest hour of a month with payroll run and month-end close [illustrative capacities]")
    say("Per design: busiest database (utilisation of one node, or nodes needed), busiest hash chain, workflow databases,")
    say("agent instances needed at peak against the modelled cap of 48, agent cost a month, and the first limit reached.")
    scales = (1_000, 10_000, 100_000)
    for commerce in (0, 1_000, 10_000):
        for promotion in (0.0, 0.7):
            say(f"\n[customer orders peak {commerce:,}/s; librarian work promoted {promotion:.0%}]")
            for emp in scales:
                demand = load(emp, commerce, promotion)
                for design in ("D1 one store", "D2 silos per SoR", "D3 primitives"):
                    res = assess(design, demand, CAP, AGENT_CAP["rate limits as modelled (48)"])
                    db = {k: v for k, v in res.items() if k.startswith(("database", "S"))}
                    dbk = max(db, key=lambda k: db[k][1])
                    ch = {k: v for k, v in res.items() if k.startswith("hash chain")}
                    chk = max(ch, key=lambda k: ch[k][1])
                    ag = res["agents (instances at peak)"]
                    name, x = first_bottleneck(res)
                    dbtxt = (f"{dbk.split(' (')[0]} {db[dbk][1]:.0%}" if db[dbk][0] == "util"
                             else f"{dbk.split(' (')[0]} {max(1, math.ceil(db[dbk][1]))} node(s)")
                    say(f"  {emp:>7,} | {design:<16} | db: {dbtxt:<28} | chain {ch[chk][1]:6.1%} | workflow "
                        f"{max(1, math.ceil(res['workflow engine (databases)'][1]))} | agents {math.ceil(ag[1]):4d}/48 | "
                        f"${res['agent cost ($/month)'][1]:>8,.0f}/mo | first limit: {name.split(' (')[0]} {x:.0%}"
                        + ("  FAILS" if x > 1 else ""))
                    out.setdefault(f"{commerce}|{promotion}|{emp}", {})[design] = {k: list(v) for k, v in res.items()}
    say("\nSENSITIVITY: D3 at 100,000 employees, 1,000 orders/s, 70% promoted; every capacity x0.25 / x1 / x4")
    for m in (0.25, 1.0, 4.0):
        cap = {k: v * m for k, v in CAP.items()}
        res = assess("D3 primitives", load(100_000, 1_000, 0.7), cap, 48)
        nodes = {k: math.ceil(v[1]) for k, v in res.items() if v[0] == "nodes"}
        say(f"  x{m}: most nodes {max(nodes.values())} ({max(nodes, key=nodes.get)}); "
            f"batched chain {res['hash chain: busiest domain (batched)'][1]:.1%}; agents {math.ceil(res['agents (instances at peak)'][1])}")
        out[f"sensitivity|{m}"] = {k: list(v) for k, v in res.items()}
    (HERE / "load_probe_results.txt").write_text("\n".join(lines) + "\n")
    json.dump(out, open(HERE / "load_probe.json", "w"), indent=1)


if __name__ == "__main__":
    main()
