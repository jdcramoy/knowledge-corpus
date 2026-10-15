# BSYS-29461 — Wire harness-dreamer and project-dreamer fleet jobs into the heartbeat contract

Epic: [BSYS-29454](https://workato.atlassian.net/browse/BSYS-29454) (Agent Harness Operations — Watcher, Registry & Fleet Hygiene) · Ticket: [BSYS-29461](https://workato.atlassian.net/browse/BSYS-29461) · Plan filed 2026-10-10 (jira-autotriage planning pass)

## Background

Watchdog triage finding `heartbeat-blindspot-dreamer-jobs` (2026-10-09) flagged that the harness-dreamer (23:43 nightly) and project-dreamer (00:37 nightly) fleet jobs never wrote to `~/.claude/knowledge/garden-reports/heartbeat.jsonl`, so skipped nights were undetectable — the dashboard showed them healthy on stale data.

**The finding's premise is stale.** Live verification on 2026-10-10 shows both jobs were wired into the heartbeat contract when the run-job.sh v2 fleet runner rolled out (2026-10-08): their launchd plists invoke the fleet runner, the runner writes the heartbeat mechanically on validated success, and both jobs produced `done validated` heartbeat rows on their most recent scheduled runs. A prior triage pass reached the same conclusion (Josh's comment 1134566, 2026-10-09). A jira-autotriage dashboard render from 2026-10-09 already skipped this ticket as "verified already done".

So this ticket is a **verification-only close, not a build**. The plan below documents the existing wiring (so the close comment cites the actual mechanism), the acceptance criteria with live evidence, and the residual hygiene items — none of which gate the ACs.

## Business Requirements

- A skipped or dead fleet job is visible within one dashboard refresh.

## Technical Requirements

**No file changes are required.** The wiring already exists end to end:

1. `~/Library/LaunchAgents/com.josh.fleet.dreamer.plist` — `/bin/bash ~/.local/bin/fleet/run-job.sh dreamer`, StartCalendarInterval 23:43.
2. `~/Library/LaunchAgents/com.josh.fleet.project-dreamer.plist` — `/bin/bash ~/.local/bin/fleet/run-job.sh project-dreamer`, StartCalendarInterval 00:37.
3. `~/.local/bin/fleet/run-job.sh` (117 lines, byte-identical to the kit copy at `~/Documents/agentic-workato-kit/bin/fleet/run-job.sh`, confirmed by `diff -q`) — runner v2: on success writes `{"ts":...,"job":"<name>"}` to `heartbeat.jsonl` mechanically; stub detection (empty output + no heartbeat delta) → 1 retry → append to `garden-reports/fleet-validation.jsonl` for watchdog escalation.
4. Job defs `jobs/dreamer.env` + `dreamer.prompt` and `jobs/project-dreamer.env` + `project-dreamer.prompt` in the kit fleet dir (`CLAUDE_JOB=yes`, TIMEOUT=1800, `--permission-mode acceptEdits`).
5. `~/.claude/knowledge/dashboard.html` renders `fleet-dreamer` and `fleet-project-dreamer` machine-health chips (ok dots, schedule, last-run age) and table rows with fleet-log tails, from live heartbeat/log data.

### Optional hygiene items (NOT required for AC; only if Josh wants them)

- **Double heartbeat row per dreamer run** — each dreamer's prompt asks the model to append its own heartbeat check-in (e.g. `job":"harness-dreamer"` line 89) in addition to the runner's mechanical `job":"dreamer"` write. Cosmetic only; dashboard uses last-row-per-job semantics. Removing the prompt-side check-in would be a one-line prompt edit in the kit, but the runner comment says the check-in "stays allowed", so leave as is.
- **Stale dashboard P2 line** — `dashboard.html` line 201 still lists "dreamer heartbeat blind spot (BSYS-29461)" in the Watchdog summary. Regenerating the dashboard after the ticket closes clears it.
- **Job-name coupling** — `run-job.sh` greps `"job": *"$NAME"` against the plist-passed name; a future rename of `dreamer`/`project-dreamer` job defs must stay in sync with the plist arg. Note for the estate-architect, no action now.

### Rollback posture

Nothing to roll back — zero edits to live files. The optional items are single-file edits with git-tracked kit copies (`~/Documents/agentic-workato-kit`) as the restore point.

## Acceptance Criteria

- [x] Both dreamer jobs write heartbeat rows on their scheduled runs — **verified live**: dreamer row `2026-10-09T03:46:45Z` (= 2026-10-08 23:46:45 EDT, matching `dreamer.log` "done validated" at the same second) and project-dreamer rows `2026-10-09T04:41:09Z` / `04:41:42Z` (= 2026-10-09 00:41:42 EDT, matching `project-dreamer.log` "done validated"); project-dreamer history back to `2026-10-08T03:51:23Z`.
- [x] Dashboard machine-health tiles reflect the dreamers' true last-run state — **verified live**: `fleet-dreamer` chip "23:43 · 19h ago" and `fleet-project-dreamer` chip "00:37 · 18h ago", both `dot ok`, with log tails ending in `done validated`.
- [ ] Ticket closed on evidence — **Josh's gate**: the parent session posts the close comment citing this plan; no transition performed by the loop.

## Risks

- **The ticket is already closed in spirit but open in Jira** — low risk; the only failure mode is another watchdog pass re-flagging the same stale premise. Closing with evidence (this plan) kills the recurrence.
- **Stub semantics differ from the original finding's framing** — before 2026-10-08 the runner had no validation, which is when the blind spot was real. If a dreamer night ever stubs now, the runner self-retries and writes a `fleet-validation.jsonl` row (currently zero dreamer entries) rather than staying silent — that is the contract the ticket asked for.
- **Dreamer subagent write denials** — both recent runs logged mid-run Write-permission denials in the dreamer subagent; the parent session completed the outputs. Does not affect heartbeat validation (the runner counts output non-emptiness + heartbeat delta), but it degrades dream content quality. Tracked separately in dream-loop domain notes; out of scope here.

## Points

**2** as originally scoped (wire two job defs into the runner contract + verification). With the premise stale, the residual is a verification-only close — 1 point of work remaining. Recommend 2 stays on the ticket for the verification + close effort already invested across two triage passes.

## What was verified (live evidence, 2026-10-10 ~03:20 UTC)

1. `~/.claude/knowledge/garden-reports/heartbeat.jsonl` (1,102 lines, last modified Oct 9 23:24:35 EDT): grep for `dreamer` returns rows at line 6 (`2026-10-08T03:51:23Z` project-dreamer), line 89 (`2026-10-09T03:46:41Z` harness-dreamer — the model check-in), line 90 (`2026-10-09T03:46:45Z` dreamer), lines 96-97 (`2026-10-09T04:41:09Z` / `04:41:42Z` project-dreamer). Last night's 23:43/00:37 runs have not fired yet (it is 23:24 EDT on Oct 9), so the Oct 8/9 rows are the most recent scheduled runs.
2. `~/Library/LaunchAgents/com.josh.fleet.dreamer.plist` and `com.josh.fleet.project-dreamer.plist`: both invoke `run-job.sh <name>` at 23:43 / 00:37 respectively.
3. `~/.local/bin/fleet/run-job.sh` read in full (117 lines): mechanical `write_heartbeat` on validated success (line 108), stub → retry → `fleet-validation.jsonl` escalation (lines 101-115). `diff -q` against the kit copy: identical.
4. `~/Documents/agentic-workato-kit/bin/fleet/jobs/`: `dreamer.env`, `dreamer.prompt`, `project-dreamer.env`, `project-dreamer.prompt` all present.
5. `~/.claude/knowledge/garden-reports/fleet-validation.jsonl`: grep for `dreamer` — no matches (no dreamer night has ever escalated; grep rc=1).
6. `~/.local/state/fleet/dreamer.log` tail: `2026-10-08 23:46:45 dreamer: done validated`; `project-dreamer.log` tail: `2026-10-09 00:41:42 project-dreamer: done validated`.
7. `~/.claude/knowledge/dashboard.html`: `fleet-dreamer` and `fleet-project-dreamer` chips and table rows present with `dot ok`, correct schedules, last-run ages, and log tails.
8. Gossip bus outboxes `~/.claude/knowledge/dreams/bus/harness-dreamer.jsonl` (8.7 KB, Oct 8 21:31) and `project-dreamer.jsonl` (2.9 KB, Oct 9 00:39) exist — the dreamers are also posting bus findings, not just heartbeating.
