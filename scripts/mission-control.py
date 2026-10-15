#!/usr/bin/env python3
"""mission-control.py — the in-flight work registry and its projections.

Josh's 2026-10-11 problem: multiple sessions run parallel work, agents report
in jargon, and nothing joins in-flight state across sessions/projects. This is
the join. Event-sourced per the store-discipline law: sessions APPEND events
to mission-control/events.jsonl (validated); registry.json and board.html are
DERIVED projections only this script writes.

Subcommands:
  fold     rebuild registry.json from the events log (last event per
           workstream wins; done rows older than 14d drop off the board)
  board    render mission-control/board.html (auto-refresh, groups by state)
  needs    print workstreams in state needs-josh (for briefs and /today)
  add      append one event (used by the closeout ritual and seeding):
           --event claim|closeout|state|note --workstream SLUG --project P
           --jira KEY --jira-title T --what ... --why ... --end ...
           --needs ... --state in-flight|needs-josh|blocked|done --by WHO
Zero-LLM. Plain-English fields are REQUIRED — the whole point.
"""
import argparse
import datetime as dt
import json
import os
import sys

HOME = os.path.expanduser("~")
MC = os.path.join(HOME, ".claude", "knowledge", "mission-control")
EVENTS = os.path.join(MC, "events.jsonl")
REGISTRY = os.path.join(MC, "registry.json")
BOARD = os.path.join(MC, "board.html")
sys.path.insert(0, os.path.join(HOME, ".claude", "knowledge", "scripts"))
from atomic_io import atomic_append, atomic_append_validated, atomic_write  # noqa: E402

SCHEMA = {
    "required": ["ts", "event", "workstream", "state", "by"],
    "enums": {"event": {"claim", "closeout", "state", "note"},
              "state": {"in-flight", "needs-josh", "blocked", "done"}},
    "timestamps": ["ts"],
}
STATES = ["needs-josh", "blocked", "in-flight", "done"]
STALE_DONE_DAYS = 14
STALE_NONDONE_HOURS = 24


def read_events():
    if not os.path.exists(EVENTS):
        return
    for line in open(EVENTS, errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def fold():
    reg = {}
    for e in read_events():
        w = e.get("workstream")
        if not w:
            continue
        reg[w] = e  # last event per workstream wins
    # drop done rows older than the window
    now = dt.datetime.now(dt.timezone.utc)
    fresh = {}
    for w, e in reg.items():
        age_hours = None
        try:
            ts = dt.datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
            age_hours = (now - ts).total_seconds() / 3600.0
        except (ValueError, KeyError):
            pass
        if e.get("state") == "done":
            try:
                if (now - ts).days > STALE_DONE_DAYS:
                    continue
            except (ValueError, KeyError, NameError):
                pass
        else:
            # staleness pass for NON-done workstreams (cortex finding 2026-10-13:
            # fold previously computed no staleness here, hiding stale in-flight/
            # blocked/needs-josh rows from registry.json and board.html)
            e = dict(e)
            if age_hours is not None:
                e["age_hours"] = round(age_hours, 1)
                e["stale"] = age_hours > STALE_NONDONE_HOURS
        fresh[w] = e
    rows = sorted(fresh.values(),
                  key=lambda e: (STATES.index(e.get("state", "in-flight")),
                                 e.get("ts", "")))
    atomic_write(REGISTRY, json.dumps({"folded_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                       "workstreams": rows}, indent=1) + "\n")
    return rows


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def board(rows):
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    parts = ["""<!doctype html><html><head><meta charset="utf-8">
<title>Mission Control</title><meta http-equiv="refresh" content="300">
<style>
body{font-family:-apple-system,Helvetica,sans-serif;margin:24px;background:#0f172a;color:#e2e8f0}
h1{font-size:22px} .ts{color:#64748b;font-size:12px;margin-bottom:16px}
.card{background:#1e293b;border-radius:8px;padding:12px 16px;margin:10px 0;border-left:4px solid #475569}
.needs-josh{border-left-color:#ef4444}.blocked{border-left-color:#f59e0b}
.in-flight{border-left-color:#22c55e}.done{border-left-color:#334155;opacity:.6}
.jira{color:#38bdf8;font-weight:600} .meta{color:#94a3b8;font-size:12px}
.what{margin:4px 0}.why{color:#94a3b8;font-size:13px}
.needs{color:#fca5a5;font-size:13px;margin-top:6px}
h2{font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;margin-top:28px}
</style></head><body>
<h1>Mission Control — in-flight work</h1><div class="ts">folded %s &middot; auto-refresh 5m</div>""" % now]
    for state in STATES:
        group = [e for e in rows if e.get("state") == state]
        if not group:
            continue
        parts.append(f"<h2>{state} ({len(group)})</h2>")
        for e in group:
            jira = f'<span class="jira">{esc(e.get("jira"))}</span> — {esc(e.get("jira_title"))}<br>' if e.get("jira") else ""
            needs = f'<div class="needs">&#9888; needs Josh: {esc(e.get("needs"))}</div>' if e.get("needs") else ""
            stale = (f'<div class="needs">&#9203; STALE: no update for '
                     f'{e.get("age_hours")}h</div>') if e.get("stale") else ""
            parts.append(f"""<div class="card {state}">
{jira}<div class="what">{esc(e.get("what"))}</div>
<div class="why">why: {esc(e.get("why"))} &rarr; end: {esc(e.get("end"))}</div>
{needs}{stale}<div class="meta">{esc(e.get("workstream"))} &middot; {esc(e.get("project", ""))} &middot; by {esc(e.get("by"))} &middot; {esc(e.get("ts"))}</div>
</div>""")
    parts.append("</body></html>")
    atomic_write(BOARD, "\n".join(parts))


def needs(rows):
    for e in rows:
        if e.get("state") == "needs-josh":
            j = f" [{e.get('jira')} {e.get('jira_title')}]" if e.get("jira") else ""
            print(f"- {e.get('workstream')}{j}: {e.get('what')} — NEEDS: {e.get('needs')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["fold", "board", "needs", "add"])
    ap.add_argument("--event", dest="ev")
    ap.add_argument("--workstream")
    ap.add_argument("--project", default="")
    ap.add_argument("--jira", default="")
    ap.add_argument("--jira-title", default="")
    ap.add_argument("--what", default="")
    ap.add_argument("--why", default="")
    ap.add_argument("--end", default="")
    ap.add_argument("--needs", default="")
    ap.add_argument("--state", default="in-flight")
    ap.add_argument("--by", default="josh (session)")
    a = ap.parse_args()
    if a.cmd == "add":
        if a.what and len(a.what) < 20:
            sys.exit("refused: 'what' must be a plain-English sentence, not a fragment")
        row = {"ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "event": a.ev or "closeout", "workstream": a.workstream,
               "project": a.project, "jira": a.jira, "jira_title": a.jira_title,
               "what": a.what, "why": a.why, "end": a.end, "needs": a.needs,
               "state": a.state, "by": a.by}
        atomic_append_validated(EVENTS, row, SCHEMA)
        rows = fold()
        board(rows)
        print(f"recorded {row['event']} for {row['workstream']} -> {row['state']}; board refolded")
        if row['event'] == 'claim' and row.get('state') == 'in-flight':
            print("REMINDER (Josh 2026-10-12): if this claim involves a Workato build, open the living export manifest NOW — `wt manifests create` + mirror to <repo>/manifests/<BSYS-id>.manifest.json — BEFORE the first builder edit. Assets enter AS touched, same turn. (BSYS-29560/29564 drift: manifests opened after the pushes.)")
        return
    rows = fold()
    if a.cmd == "board":
        board(rows)
        print(f"board: {len(rows)} workstreams -> {BOARD}")
    elif a.cmd == "needs":
        needs(rows)
    else:
        print(f"folded {len(rows)} workstreams -> {REGISTRY}")


if __name__ == "__main__":
    main()
