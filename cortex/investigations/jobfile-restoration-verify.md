# Job-file restoration verification — post-fix sweep

Verified: 2026-10-22 ~11:10 EDT (read-only investigation; only this file written).
Against: fleet-jobfile-corruption-inventory.md (12 files, commit 6d7b61a corruption).
Restore evidence: all 24 file instances (12 files x live + kit trees) re-stamped
2026-10-22 08:11:33 — consistent with backup.script's reported re-stamp.

## Verdict: ALL 12 FILES RESTORED (12/12 RESTORED, 0 STILL-CORRUPTED, 0 MISSING)

Checked in BOTH named runtime trees:
- ~/.local/bin/fleet/jobs/ (live, what launchd runs)
- ~/Documents/agentic-workato-kit/bin/fleet/jobs/ (kit source)

| # | File | Live tree | Kit tree | Placeholder hits | Content check |
|---|------|-----------|----------|------------------|---------------|
| 1 | decision-inbox.script | RESTORED | RESTORED | 0 | heartbeat line -> ~/, bash -n OK |
| 2 | backup.script | RESTORED | RESTORED | 0 | heartbeat line OK, bash -n OK |
| 3 | queue-drift.script | RESTORED | RESTORED | 0 | heartbeat line OK, bash -n OK |
| 4 | instruction-miner.script | RESTORED | RESTORED | 0 | heartbeat line OK, bash -n OK |
| 5 | harness-health.script | RESTORED | RESTORED | 0 | heartbeat line OK, bash -n OK |
| 6 | value-ledger.script | RESTORED | RESTORED | 0 | heartbeat line OK, bash -n OK |
| 7 | watchdog.env | RESTORED | RESTORED | 0 | JOB_CWD=.../orca/workspaces/workbench/Workday-Development (dir exists) |
| 8 | architect.env | RESTORED | RESTORED | 0 | JOB_CWD same, dir exists |
| 9 | healer.env | RESTORED | RESTORED | 0 | JOB_CWD same, dir exists |
| 10 | uat-sweep.env | RESTORED | RESTORED | 0 | JOB_CWD same, dir exists |
| 11 | ops-autopsy.env | RESTORED | RESTORED | 0 | JOB_CWD=~/.claude (dir exists) |
| 12 | jira-triage.env | RESTORED | RESTORED | 0 | JOB_CWD=~/Documents/workbench (dir exists) |

## Method & evidence
1. Full-tree `grep -rn 'YOUR-USER'` on BOTH ~/.local/bin/fleet/ and
   ~/Documents/agentic-workato-kit/bin/fleet/ -> zero hits in either tree
   (exit 1 = no matches; wider than the 12 files, covers the whole fleet dir).
2. Per-file grep on all 24 instances -> 0 hits each; all mtimes 2026-10-22 08:11:33.
3. Content (not just placeholder-free): all 6 .env JOB_CWD lines point at real,
   existing directories under ~/ (test -d passed on all 3 distinct
   targets). All 6 .script heartbeat lines pipe to
   ~/.claude/knowledge/scripts/atomic_io.py -> heartbeat.jsonl;
   `bash -n` passes on all 6.
4. Live behavioral corroboration (heartbeat.jsonl, post-08:11 check-ins):
   - queue-drift x2 (12:11:53Z), harness-backup x1 (12:13:05Z) — script-job
     heartbeat path works.
   - jira-triage x2 (14:04:33Z, 14:04:57Z) — an .env job that previously died at
     `cd "$JOB_CWD"` now reaches the agent. Strongest single proof the cwd fix holds.
   - Remaining jobs (watchdog, architect, healer, uat-sweep, ops-autopsy, and the
     other script jobs) are nightly/weekly cadence and have not yet fired since the
     08:11 restore — expected, not a gap. Next natural check: watchdog's 23:13 run
     tonight (first .env job since restore; should end the 2-night coverage gap).

## Residual risk (none blocking)
- Unproven-by-fire jobs: 9 of 12 haven't run since restore (cadence, not defect).
  The 10-22 23:13 watchdog fire will be the first full-scale proof for the .env
  cohort — worth a glance at ~/.local/state/fleet/watchdog.log tomorrow morning.
- Inventory's follow-up stands: mods-deploy.sh renders placeholders AT DEPLOY but
  jobs/ was synced raw — the deploy-script/receipts-gate guard is still Josh's call
  and still worth filing so this class of corruption cannot re-land.
