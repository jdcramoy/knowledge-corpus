# Fleet job-file corruption inventory — /Users/YOUR-USER/ placeholders

Investigated: 2026-10-21 ~21:58 EDT (read-only; nothing modified except this file).
Origin: kit commit 6d7b61a ("harness-docs sync 2026-10-20", Oct 20 07:30:43 -0400) copied
raw /Users/YOUR-USER/ placeholder paths into the live fleet jobs tree. Corruption landed
in BOTH trees simultaneously (they are identical copies — diff confirms zero differences
across all 12 files): `~/.local/bin/fleet/jobs/` and
`~/Documents/agentic-workato-kit/bin/fleet/jobs/`.

**Scope confirmed clean:** exactly 12 files, ONE `/Users/YOUR-USER/` occurrence per file,
nothing else under ~/.local/bin/fleet/ is contaminated (run-job.sh itself: 0 occurrences;
no .sh, .prompt, or .probe files affected).

## 1+2. The 12 corrupted files, the job each configures, and what it does

6 `.script` files (corruption is in the final heartbeat line only — the job's main body
uses `$HOME` and still runs; the dashboard check-in silently fails):

| # | File | Job | What it does |
|---|------|-----|--------------|
| 1 | `decision-inbox.script` | com.josh.fleet.decision-inbox | Builds Josh's one ranked, budgeted decision surface each morning (routes harness-meta out of his way) |
| 2 | `backup.script` | com.josh.fleet.backup | Runs harness-backup nightly; heartbeat keeps the dashboard backup chip green |
| 3 | `queue-drift.script` | com.josh.fleet.queue-drift | Daily rebuild-and-diff of triage-queue projection vs live queue; alarms on drift |
| 4 | `instruction-miner.script` | com.josh.fleet.instruction-miner | Nightly correction-mining for the instruction-patch loop |
| 5 | `harness-health.script` | com.josh.fleet.harness-health | Harness self-watchdog: fleet liveness, ledger freshness, queue dedup; files findings to harness-fix/queue.jsonl |
| 6 | `value-ledger.script` | com.josh.fleet.value-ledger | Derives value rows nightly; rolls value-vs-cost report on the 1st |

6 `.env` files (corruption is `JOB_CWD` — run-job.sh line 79 `cd "$JOB_CWD"` fails,
the job does ZERO work, exits 1 before the agent even launches):

| # | File | Job | What it does |
|---|------|-----|--------------|
| 7 | `watchdog.env` | com.josh.fleet.watchdog | Nightly Workato estate watchdog: connection health, stalled schedulers, failure autopsies (23:13 nightly) |
| 8 | `architect.env` | com.josh.fleet.architect | Weekly enterprise-architecture review of the Workato estate (lineage, config parity, zombie hygiene, security posture) |
| 9 | `healer.env` | com.josh.fleet.healer | Auto-remediation/healer agent over the Workday-Development workspace |
| 10 | `uat-sweep.env` | com.josh.fleet.uat-sweep | UAT sweep over the Workday-Development workspace (category sweeps, optional SWEEP_SCOPE smoke mode) |
| 11 | `ops-autopsy.env` | com.josh.fleet.ops-autopsy | Operational failure autopsy job over ~/.claude workdir |
| 12 | `jira-triage.env` | com.josh.fleet.jira-triage | The self-looping Jira identify-triage-investigate-plan loop (workbench cwd) |

## 3. launchd scheduling — all 12 ARE scheduled right now

All 12 job labels are loaded and scheduled in launchd (verified via `launchctl list` and
plists present in ~/Library/LaunchAgents/com.josh.fleet.*.plist). Notably
`com.josh.fleet.ops-autopsy` shows last-exit-status 1 in launchctl — consistent with the
cwd-fail signature. The corrupted set spans every fleet cadence: nightly (watchdog 23:13
local, backup, queue-drift, instruction-miner, value-ledger, decision-inbox morning) and
weekly/periodic (architect, healer, uat-sweep, ops-autopsy, jira-triage).

## 4. Watchdog nightly run at 23:13 on 10-20/10-21 — PRODUCED NOTHING

- The 10-20 23:13:05 run FAILED at startup: `watchdog: cwd fail` in
  ~/.local/state/fleet/watchdog.log; run-job.sh exited 1 before the agent launched.
- No watchdog report exists for 10-20 or 10-21 (~/.claude/knowledge/watchdog-reports/
  newest is 2026-10-19.md). Watchdog coverage gap is now 2 nights.
- (Timestamp note: run-job.sh logs LOCAL time; the 23:13 schedule is local, not Z.)
- As of 21:58 EDT 10-21, the 10-21 23:13 run has not fired yet — it will fail identically
  unless the fix lands first (~75 min window).
- Heartbeat corroboration: all 6 script jobs' last check-in is 10-20 03:20-11:20 UTC —
  i.e., pre-corruption. Zero check-ins in the ~36h since the corruption landed.

## 5. What breaks if not restored (3 lines) + fix assessment

- The 6 .env jobs (watchdog, architect, healer, uat-sweep, ops-autopsy, jira-triage) do
  ZERO work — run-job.sh `cd "$JOB_CWD"` fails and exits 1 before the agent launches;
  watchdog estate coverage has already been dark 2 nights with no report.
- The 6 .script jobs run their main body but the heartbeat check-in fails every run, so
  dashboard liveness chips go stale and liveness-based surfaces (morning brief, mission
  control, dashboards) read the fleet as dead.
- Every job fails EVERY scheduled fire until fixed; the failure is silent except the one
  cwd-fail log line and stale heartbeats — nothing pages Josh.

**Fix:** YES — a per-file `sed -i '' 's|/Users/YOUR-USER/|~/|g'` on all
12 files in BOTH trees is exactly right: one literal occurrence per file, no other
placeholder variants exist (verified), run-job.sh clean, sed is a pure text substitution
with no other content between the placeholder and the real path. Restore the live tree
first (~/.local/bin — that is what launchd runs), then the kit source, and re-verify with
grep before tonight's 23:13 watchdog fire.

## Recommended repair order (for the fix session, not this one)
1. sed-replace in ~/.local/bin/fleet/jobs/ (live, launchd runs this).
2. sed-replace in ~/Documents/agentic-workato-kit/bin/fleet/jobs/ (kit source parity).
3. Re-grep both trees for YOUR-USER (expect zero hits); confirm `bash -n` passes on the
   6 scripts.
4. Note: kit commit 6d7b61a's mods-deploy.sh renders placeholders AT DEPLOY — the jobs
   dir was synced raw, which is the gap that let this through. Worth a deploy-script or
   receipts-gate guard so jobs/ gets rendered too (follow-up, Josh's call).
