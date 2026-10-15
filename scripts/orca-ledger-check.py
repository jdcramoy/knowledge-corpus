#!/usr/bin/env python3
"""orca-ledger-check.py — enforce the orca-browser traps ledger's self-training
contract. Stdlib only, read-only, bounded.

Scans recent Claude Code session transcripts for BROWSER-FAILURE signatures,
then diffs the days those occurred against the dated rows in the orca-browser
skill's traps ledger. A failure day with no ledger row means a session hit a
browser trap and never taught the skill — the exact drift the ledger exists to
prevent (Josh-approved dreamer check, 2026-10-10).

Verdicts per day: MISSING (browser failures, no ledger row), COVERED (row
exists), or CLEAN (no browser failures found).

Output: human summary on stdout + JSON at
~/.claude/knowledge/dreams/data/<today>-orca-ledger.json (beside the
dream-mine digest). Exit code 0 always (advisory); use --strict to exit 1
when MISSING days exist.

Usage:
  python3 orca-ledger-check.py [--days 2] [--max-file-mb 30] [--selftest]
"""

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

HOME = os.path.expanduser("~")
PROJECTS = os.path.join(HOME, ".claude", "projects")
SKILL = os.path.join(HOME, ".claude", "skills", "orca-browser", "SKILL.md")
OUT_DIR = os.path.join(HOME, ".claude", "knowledge", "dreams", "data")

# Transcript text signatures of browser-failure work. Deliberately concrete —
# each traces to a real diagnosed failure on this harness.
SIGNATURES = [
    re.compile(r"browser_no_tab"),                       # orca CLI tab error
    re.compile(r"silent(ly)? (no-op|noop|did nothing|does nothing)", re.I),
    re.compile(r"no handler fired", re.I),
    re.compile(r"orca .{0,40}(failed|error)", re.I),
    re.compile(r"snapshot .{0,30}(stale|lag)", re.I),
    re.compile(r"clicked? but (nothing|no)", re.I),
    re.compile(r"menu closed: False"),
]
# Tool-result markers that mean the text is an OBSERVATION, not chatter.
RESULT_KEYS = ("toolUseResult", "tool_result")

LEDGER_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|", re.M)


def ledger_dates(path):
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8", errors="replace") as f:
        return set(LEDGER_ROW.findall(f.read()))


def iter_transcripts(days):
    cutoff = (dt.datetime.now() - dt.timedelta(days=days)).timestamp()
    for path in glob.glob(os.path.join(PROJECTS, "*", "*.jsonl")):
        if os.path.getmtime(path) < cutoff:
            continue
        yield path


def scan_file(path, max_bytes):
    """Yield (date_iso, signature, snippet) for browser-failure signature hits.

    Only TOOL-RESULT lines are scanned: skill listings, system reminders, and
    assistant prose quote the same phrases (a skill description literally says
    "silent no-ops") and bury the signal. A tool result is a real observation.
    """
    size = os.path.getsize(path)
    if size > max_bytes:
        return  # bounded: skip monsters rather than stream-split them
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"attachment"' in line:
                continue
            # Reading/writing the skill (or this script) quotes the rule text
            # into tool results — that's the ledger describing itself, not a
            # failure observation.
            if "Hard-won rules" in line or "orca-ledger-check" in line:
                continue
            if not ('"toolUseResult"' in line or '"tool_result"' in line):
                continue
            if not any(s.search(line) for s in SIGNATURES):
                continue
            date = None
            snippet = ""
            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", "")
                date = ts[:10] if ts else None
                snippet = json.dumps(entry)[:600]
            except ValueError:
                snippet = line[:300]
            for sig in SIGNATURES:
                if sig.search(line):
                    yield (date or "unknown", sig.pattern[:40], snippet[:200])
                    break  # one verdict per line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--max-file-mb", type=int, default=30)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        print("SELFTEST: signature table + ledger parser")
        sample = "| 2026-10-10 | after closing a dropdown ... | cause | lesson |"
        row = LEDGER_ROW.search(sample)
        assert row and row.group(1) == "2026-10-10", "ledger parser broke"
        hit = SIGNATURES[0].search("... browser_no_tab error ...")
        assert hit, "signature table broke"
        print("SELFTEST OK: parser + signatures behave")
        return

    covered = ledger_dates(SKILL)
    ledger_birth = min(covered) if covered else today
    today = dt.date.today().isoformat()
    days_hits = {}
    scanned = 0
    for path in iter_transcripts(args.days):
        scanned += 1
        for date, sig, snippet in scan_file(path, args.max_file_mb * 1024 * 1024):
            days_hits.setdefault(date, []).append({"sig": sig, "file": os.path.basename(path), "snippet": snippet})

    verdicts = {}
    for date in sorted(days_hits, reverse=True):
        if date in covered:
            verdicts[date] = "COVERED"
        elif date < ledger_birth:
            verdicts[date] = "PRE_LEDGER"  # ledger didn't exist yet: backfill candidate
        else:
            verdicts[date] = "MISSING"

    missing = [d for d, v in verdicts.items() if v == "MISSING"]
    pre_ledger = [d for d, v in verdicts.items() if v == "PRE_LEDGER"]
    report = {
        "date": today,
        "transcripts_scanned": scanned,
        "ledger_rows": sorted(covered, reverse=True)[:10],
        "failure_days": verdicts,
        "missing_rows": missing,
        "pre_ledger_days": pre_ledger,
        "hits": {d: v[:3] for d, v in list(days_hits.items())[:5]},
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"{today}-orca-ledger.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=1)

    print(f"orca-ledger-check: {scanned} transcripts, {len(days_hits)} browser-failure day(s)")
    for date, verdict in verdicts.items():
        print(f"  {date}: {verdict} ({len(days_hits[date])} hits)")
    print(f"report: {out}")
    if not verdicts:
        print("  CLEAN: no browser-failure signatures in window")
    if pre_ledger:
        print(f"PRE-LEDGER days (backfill candidates): {', '.join(pre_ledger)}")
    if missing:
        print(f"MISSING LEDGER ROWS for: {', '.join(missing)} — propose rows in the dream report")
        if args.strict:
            sys.exit(1)


if __name__ == "__main__":
    main()
