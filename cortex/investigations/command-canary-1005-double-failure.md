# Command-canary 10:05 double-failure — investigation (read-only, 2026-10-14)

**VERDICT: Root cause found.** The Slack command-loop watcher (`com.josh.agent-command-watcher`,
launchd StartInterval 60s) has been dead since **2026-10-12 ~13:48Z** because its plist points at
an interpreter that no longer exists: `/opt/homebrew/bin/python3` (unversioned symlink) was
removed — likely by a Homebrew python upgrade — leaving only versioned shims
(`python3.11`, `python3.12`, `python3.14`). Every launchd tick now fails to spawn: last exit
status **78** (`EX_CONFIG`-class spawn failure), and `/tmp/agent-command-watcher.log` is
untouched since Oct 12 13:48 (the process never starts, so it never logs).

## Components
- **Canary writer:** `~/.claude/knowledge/scripts/command-canary.py` — injects a synthetic
  `selfcheck` row via the watcher's data-tables API, polls the row every 15s for 300s, then
  asserts the bot ack in room C0C7JHJKHRU. Writes `garden-reports/command-canary-status.json`
  + a `heartbeat.jsonl` row.
- **Canary scheduler:** launchd `com.josh.fleet.canary` → `run-job.sh canary`,
  **StartCalendarInterval 06:05 LOCAL = 10:05 UTC** (EDT, UTC-4). One run per day.
- **Watcher:** `~/.local/bin/agent-command-watcher.py` (plus
  `scripts/agent-command-watcher-module.py`), launchd `com.josh.agent-command-watcher`,
  StartInterval 60s.

## Why failures cluster at exactly 10:05
It is NOT a polling-window artifact and NOT a daily-only watcher schedule. The canary itself
polls the row every 15s for the full 300s SLA — the watcher just never processes the row. The
10:05 cluster exists because the canary fires exactly once daily (06:05 local / 10:05Z) and the
status JSON's `checked` field is the run-start UTC timestamp — so every daily result, pass or
fail, is stamped 10:05Z. Failures "at 10:05" simply mean the single daily canary ran while the
watcher was dead. **Genuine SLA miss**, not an artifact.

## Run history (heartbeat.jsonl, all command-canary rows)
- 2026-10-09 10:20Z FAIL — row-create response-shape bug (known, fixed same day)
- 2026-10-09 10:22Z / 18:47Z PASS (31s / 47s)
- 2026-10-12 04:59Z / 05:02Z / **10:05Z** / 12:27Z PASS (17–62s)
- **2026-10-13 10:10Z FAIL** — row e5c4410a not done in 300s
- **2026-10-14 10:10Z FAIL** — row 4ac92630 not done in 300s

Timeline is exact: last watcher log write Oct 12 13:48 → first canary failure Oct 13 10:05Z.
The breakage window begins the afternoon of Oct 12, consistent with a Homebrew upgrade that
pulled the unversioned `python3` symlink between the 12:27Z pass and end of day.

## Blast radius
`grep` across `~/Library/LaunchAgents/*.plist`: **only** `com.josh.agent-command-watcher`
references the dead `/opt/homebrew/bin/python3` path. All other fleet agents use versioned
interpreters or shell wrappers and show exit 0 in launchctl. Canaries downstream that depend on
canary freshness (replay-gym invariant, morning brief) will keep reporting stale/fail until fixed.

## Suggested fix (NOT applied — read-only session)
1. Repoint `~/Library/LaunchAgents/com.josh.agent-command-watcher.plist` ProgramArguments from
   `/opt/homebrew/bin/python3` → `/opt/homebrew/bin/python3.14` (matches the version the log
   shows it was running: Cellar python@3.14 3.14.8).
2. `launchctl unload` + `load` the plist, confirm a tick writes to /tmp/agent-command-watcher.log.
3. Re-run `python3 ~/.claude/knowledge/scripts/command-canary.py` manually (per the NEVER-wait
   rule) and expect PASS; the two stuck canary rows (e5c4410a, 4ac92630) should then be consumed
   or manually closed in the queue table.
4. Hardening (optional): point fleet plists at versioned python paths everywhere, or add a
   canary that distinguishes "watcher not polling" from "watcher spawn-dead" (exit-78 telemetry).
