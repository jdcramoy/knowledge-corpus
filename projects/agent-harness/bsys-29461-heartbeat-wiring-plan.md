# BSYS-29461 — Wire harness-dreamer and project-dreamer fleet jobs into the heartbeat contract

Epic: BSYS-29454 (Agent Harness Operations). Status: Backlog. Points: 1 (set 2026-10-09).
Prior artifacts: `agent-harness-operations/BSYS-29461-plan.md`, `agent-harness-operations/BSYS-29461-dreamer-heartbeat-wiring.md`, `multi-genie-orchestration/BSYS-29461-verification.md`.

## Background

Workato-watchdog finding `heartbeat-blindspot-dreamer-jobs` (2026-10-09) claimed the two dreamer fleet jobs never write to `knowledge/garden-reports/heartbeat.jsonl`, leaving skipped nights invisible. Three passes (2026-10-09, 10-10, 10-11 morning) found the premise stale: both jobs are wired through the run-job.sh v2 fleet runner, which appends a heartbeat row mechanically on validated success and escalates stubs via retry to `fleet-validation.jsonl`.

## 2026-10-11 evening re-verification (this pass)

Verdict unchanged: wiring is live, nothing to build. Live evidence:

- Fleet logs: `~/.local/state/fleet/dreamer.log` line `2026-10-10 23:48:03 dreamer: done validated`; `~/.local/state/fleet/project-dreamer.log` line `2026-10-11 00:48:19 project-dreamer: done validated`.
- Git-committed heartbeat rows (backup commit 61b8175, 2026-10-10 23:33): `dreamer` rows through `2026-10-10T03:48:59Z`, `project-dreamer` rows through `2026-10-10T04:46:15Z`.
- Plists: `com.josh.fleet.dreamer.plist` (23:43) and `com.josh.fleet.project-dreamer.plist` (00:37) both invoke `~/.local/bin/fleet/run-job.sh`.
- `dashboard.html` renders both `fleet-dreamer` and `fleet-project-dreamer` machine-health chips.

### NEW finding (this pass): heartbeat.jsonl was reset 2026-10-11 ~21:00 local

The live `garden-reports/heartbeat.jsonl` now starts at `2026-10-11T21:11:57Z`; about 36 hours of rows are gone, including both dreamers' most recent rows. The lock file (`heartbeat.jsonl.lock`) was touched at 20:20. Wiring is not at fault; retention is. Until tonight's 23:43 / 00:37 runs repopulate the file, a dashboard refresh reads the dreamer tiles as stale from live data. Recommend filing as its own finding (heartbeat file reset or unlogged rotation). Not remediated in this pass per the no-development rule.

## Business Requirements

- A skipped or dead fleet job is visible within one dashboard refresh.

## Technical Requirements

- Both dreamer jobs run through `~/.local/bin/fleet/run-job.sh` (contract: heartbeat row on validated success, stub retry, `fleet-validation.jsonl` escalation).
- Job defs in the kit: `bin/fleet/jobs/dreamer.prompt` and `bin/fleet/jobs/project-dreamer.prompt`, deployed mirror `~/.local/bin/fleet/jobs/`.
- Heartbeat rows use job keys `dreamer` and `project-dreamer` (older rows read `harness-dreamer`); anything grepping the old name misses recent rows.

## Acceptance Criteria

- [x] Both dreamer jobs write heartbeat rows on their scheduled runs (evidenced through 2026-10-10/11 runs; git-committed rows plus fleet-log `done validated` lines)
- [x] Dashboard machine-health tiles reflect the dreamers' true last-run state (both chips render; current data depends on tonight's runs after the file reset)

## UAT Evidence

Heartbeat rows from both dreamers' next scheduled runs plus dashboard tile state. Fleet-log corroboration already on file for the last two nights.

## Risks

- The heartbeat file reset (new finding) means the dashboard's dreamer tiles go stale until the next runs; if the reset repeats nightly, retention, not wiring, becomes the real defect.
- Job-key drift (`harness-dreamer` vs `dreamer`) can make naive greps report missing rows.

## Story points

1 (already set; verification-only close recommended, no build).
