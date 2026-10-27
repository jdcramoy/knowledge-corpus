# Investigation: nightly-receipts-gate escalation — four jobs "no fresh output" for run-date 2026-10-20

- Investigated: 2026-10-21 ~12:45-13:00 EDT (read-only, nothing modified/started/stopped/reloaded)
- Escalation source: `nightly-receipts-gate.py` run 2026-10-21T07:17:16-04:00 (launchd `com.josh.kb-receipts-gate`, fired 07:07, last exit 1), bus rows in `dreams/bus/nightly-receipts-gate.jsonl`
- Headline: **only ONE of the four jobs actually failed to produce output** (watchdog). Gardener and backup both produced fresh artifacts; registry-backup produced a fresh artifact with one degraded step. The other three REDs are gate-side artifacts of (a) a filename-pattern gap and (b) a TCC privacy denial.
- Root event: **2026-10-20 ~07:29 EDT — the harness-docs sync (kit commit `6d7b61a`, 07:30:43, "mods divergence copied back RE-PLACEHOLDED") rewrote 12 fleet job config files in BOTH `~/Documents/agentic-workato-kit/bin/fleet/jobs/` and the deployed `~/.local/bin/fleet/jobs/` with literal `/Users/YOUR-USER/` template placeholders.** The canonical source `~/.claude/knowledge/config/fleet/jobs/` is CLEAN (real paths). All 12 corrupted files share mtime Oct 20 07:29. The kit commit itself warns "raw rsync could break live mods" — the fleet/jobs sync was exactly such a raw copy, no placeholder render.

## Per-job verdicts

### 1. gardener — com.josh.fleet.gardener, fire 22:43 — FALSE ALARM (ran fine)
- Fired 2026-10-20 22:43:05 EDT, ran, "done validated" 22:50:14. `launchctl print`: last exit code 0.
- Artifacts written: `garden-reports/2026-10-20-gardener-weekly-full.md` (12-finding weekly pass) + `garden-reports/2026-10-20-brain-gardener.md` + heartbeat `2026-10-21T02:49:59Z`. fleet-validation.jsonl: `valid / validated-clean` at 02:50:14Z. gardener.env is clean (uses `$HOME`).
- Why the gate flagged it: gate expects `garden-reports/{run_date}-brain-gardener-**nightly**.md`. 2026-10-20 was a WEEKLY night — the job wrote `-gardener-weekly-full.md` instead. The gate's filename pattern has no weekly-variant match. Gate log: "RED gardener run-date 2026-10-20 — missing: ...2026-10-20-brain-gardener-nightly.md".
- Verdict: job healthy, output exists, gate pattern mismatch only.

### 2. watchdog — com.josh.fleet.watchdog, fire 23:13 — REAL FAILURE (the one true miss)
- Fired 2026-10-20 23:13:05 EDT and died instantly. `watchdog.log`: "2026-10-20 23:13:05 watchdog: start" then "cwd fail". `watchdog.launchd.log`: `run-job.sh: line 79: cd: /Users/YOUR-USER/orca/workspaces/workbench/Workday-Development: No such file or directory`. `launchctl print`: last exit code 1.
- Root cause: `~/.local/bin/fleet/jobs/watchdog.env` (corrupted Oct 20 07:29) has `JOB_CWD="/Users/YOUR-USER/orca/workspaces/workbench/Workday-Development"` — literal placeholder. The real directory exists at `~/orca/workspaces/workbench/Workday-Development`. The canonical `config/fleet/jobs/watchdog.env` is correct.
- No 10-20 (or any newer) report: `watchdog-reports/` newest is `2026-10-19.md`. Previous night (10-19) ran fine — corruption landed 07:29 that morning. **Watchdog will also fail tonight (10-21, 23:13) until the env file is restored.** This is the gap that produced no 10-20/10-21 watchdog report (the 10-21 run hasn't fired yet at time of investigation — 23:13 tonight).
- Same corruption killed 11 other fleet configs (see "Collateral" below) — architect.env, healer.env, jira-triage.env, ops-autopsy.env, uat-sweep.env, backup.script, decision-inbox.script, harness-health.script, instruction-miner.script, queue-drift.script, value-ledger.script.

### 3. backup — com.josh.fleet.backup, fire 23:33 — RAN, ARTIFACT FRESH (two failures around a working backup)
- Fired 2026-10-20 23:33:04 EDT. The actual backup WORKED: `harness-backup` ran, and TWO commits landed in `~/Documents/josh-orca` dated 10-20 23:33 (`331cc39` 23:33:39, `5b3a7db` 23:33:53 — "harness backup 2026-10-20"). Newest-commit artifact is fresh; gate log line for the artifact check is the only thing between the gate and green.
- Failure A (job-side, corruption): `~/.local/bin/fleet/jobs/backup.script` (corrupted 07:29) writes its heartbeat via `python3 /Users/YOUR-USER/.claude/knowledge/scripts/atomic_io.py` → "can't open file ... [Errno 2]" → wrapper validation rc=2, retry, "VALIDATION FAILED after retry (ran rc=2) — job did not run; escalated" + `fleet-validation.jsonl` row `ran rc=2 / retry-exhausted` at 03:33:54Z. Same failure on 10-17 (pre-corruption — that rc=2 at 2026-10-17T03:33:26Z predates it; the script may have had a placeholder redaction earlier too, per kit commit `4a2fc1d` 10-16 "personal paths redacted to YOUR-USER per pre-commit rule").
- Failure B (gate-side, TCC): the gate's own check `git -C ~/Documents/josh-orca log -1 --format=%cI` returned exit 128 every morning run (10-19, 10-20, 10-21 gate runs all show it), while the identical command from an interactive shell returns rc=0 and `2026-10-20T23:33:53-04:00`. See TCC note below.
- `launchctl print`: last exit code 0 (the wrapper exits 0 even after escalation logging).

### 4. registry-backup — com.gwsemantic.registry-backup, fire 04:23 — RAN both nights; 10-21 degraded but artifact fresh
- Plist has runatload + calendar 04:23; logs at `/tmp/gws-registry-backup.log`. `launchctl print`: runs=3 since boot (Oct 19), last exit 0.
- 10-20 run (started 2026-10-20T08:23:05Z = 04:23 EDT): full success, 1073 rows, snapshot committed.
- 10-21 run (started 08:30:18Z): exported 1073 rows, snapshot written `exported_at 2026-10-21T08:41:47Z` (VERIFIED fresh — matches run-date 10-21), then the post-snapshot backup-table refresh upload died: node fetch `read ETIMEDOUT` → "backup-table refresh FAILED" 09:42:59Z (=05:42 EDT, matches file mtime). Network timeout to the Google Workspace MCP endpoint, not config corruption (this job's files are not in the corrupted set).
- Gate verdict was false-RED for a third reason: reading the snapshot itself failed — `[Errno 1] Operation not permitted` — every morning run (10-19, 10-20, 10-21). See TCC note.

## Why the gate couldn't see two fresh artifacts: TCC (macOS privacy)
The gate is wired into launchd (`com.josh.kb-receipts-gate`, fires 07:07 — its own docstring still says "Not wired into launchd"; that's stale). launchd-spawned `python3`/`git` have no TCC grant for `~/Documents`, so:
- snapshot read → errno 1 EPERM ("exported_at unreadable") for registry-backup
- `git -C ~/Documents/josh-orca log -1` → exit 128 for backup
Both artifacts are verifiably fresh from an interactive shell. The gate has been RED on backup + registry-backup on EVERY morning run in its log — it has never once read either Documents-based artifact from the launchd context. (The escalation message's "run-date 2026-10-20" applies to gardener/watchdog/backup; registry-backup's own row is run-date 2026-10-21.)

## Common or specific?
NOT common. Three distinct causes:
1. **Oct 20 07:29 harness-docs sync re-placeholdered 12 deployed fleet job configs** → watchdog's hard failure + backup's validation failure. Only watchdog actually lost output.
2. **Gate filename pattern** has no weekly-variant for gardener → false RED.
3. **Gate TCC denial on ~/Documents** from the launchd context → false RED on backup (git 128) and registry-backup (EPERM) every morning since wiring.
Registry-backup additionally had a genuine (non-config) network timeout on 10-21's refresh step, after the snapshot was already fresh.

## THE ONE FIX that restores receipts
Restore the deployed fleet job configs from the clean canonical tree before tonight's fires (22:43 / 23:13 / 23:33):
    cp ~/.claude/knowledge/config/fleet/jobs/* ~/.local/bin/fleet/jobs/
(per the run-job.sh DEPLOY CHECKLIST — canonical lives in the knowledge tree; the kit copy should be re-synced the same way, with mods-deploy.sh's `/Users/YOUR-USER` → real-path render, never raw rsync). This alone fixes watchdog's cd-fail (report resumes tonight) and backup's rc=2 validation heartbeat.
Two secondary gate fixes so the morning report tells the truth: (a) accept `-gardener-weekly-full.md` as the gardener artifact on weekly nights; (b) give the launchd gate context Documents access (or run the gate from the user session) so git/snapshot reads stop returning 128/EPERM.

## Collateral note
The corrupted set is wider than these four jobs: 12 files in `~/.local/bin/fleet/jobs/` (listed in section 2). architect.env, healer.env, jira-triage.env, ops-autopsy.env, uat-sweep.env and five .script files also carry `/Users/YOUR-USER/` — expect similar silent breakage in architect, healer, jira-triage, ops-autopsy, uat-sweep, decision-inbox, harness-health, instruction-miner, queue-drift, value-ledger until the same restore touches them. The single cp above fixes all 12.

Evidence trail: launchctl print (all four jobs), `~/Library/LaunchAgents/com.josh.kb-receipts-gate.plist`, `~/.local/bin/fleet/run-job.sh` + `jobs/*.{env,script}`, `~/.claude/knowledge/scripts/nightly-receipts-gate.py`, `garden-reports/{nightly-gate-state.json,nightly-receipts.jsonl,fleet-validation.jsonl,heartbeat.jsonl}`, `/tmp/kb-receipts-gate.log`, `/tmp/gws-registry-backup.log`, `~/.local/state/fleet/{gardener,watchdog,backup}.log` + `.launchd.log`, `git -C ~/Documents/josh-orca log`, kit git log (`6d7b61a`, `4a2fc1d`).
