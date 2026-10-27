# Investigation: dreamer heartbeat stopped (job=dreamer, last beat 2026-10-21T03:51:38Z)

- **Investigated:** 2026-10-23, session at cwd ~/.claude/knowledge
- **Verdict:** NOT a bug in the dreamer script. The 10-22 23:43 nightly dreamer run was
  killed mid-flight by the workato-watchdog's own "WAKE THE DREAMER" remediation
  (`launchctl kickstart -k`) at 23:47:26 — six seconds after the dream report landed,
  ~3 min before the run would have completed and heartbeated.
- **Scope:** read-only investigation; nothing changed except this report.

## Evidence chain (each step cited)

1. **Plist/runner:** `~/Library/LaunchAgents/com.josh.fleet.dreamer.plist` fires daily
   23:43 → `~/.local/bin/fleet/run-job.sh dreamer`. The heartbeat is
   written MECHANICALLY by the runner (`write_heartbeat()` in run-job.sh) only AFTER a
   validated run completes. `jobs/dreamer.env`: TIMEOUT=1800, bypassPermissions.
2. **10-21 night (first miss):** machine asleep at 23:43; launchd fired the job late at
   23:58:58; claude died with `API Error: ... (ENOTFOUND)` (network/DNS outage), both
   attempts rc=1 → `fleet-validation.jsonl` row `2026-10-22T06:38:27Z … "ran rc=1"
   "retry-exhausted"`. No dream, no heartbeat. This is the gap the nightly-receipts-gate
   ESCALATION 2026-10-22T11:07Z flagged (gardener/watchdog/dreamer/backup all missing —
   whole-fleet network outage night). Pre-existing condition, correctly escalated.
3. **10-22 23:43:02** — dreamer fired on schedule (invocation A), claude session
   `57650a8c-fb52-4b40-b8e0-e32f5aa9b883` (transcript in
   `~/.claude/projects/-Users-<user>--claude/`). Dream report
   `~/.claude/knowledge/dreams/2026-10-22.md` written 23:47 PT. Run still mid-flight.
4. **10-22 23:43:19** — the nightly watchdog sweep spawned a workato-watchdog subagent
   (transcript `~/.claude/projects/-Users-<user>-Documents-workbench/
   158b1995-bb59-4163-92be-1f31faf0db6f/subagents/agent-a1629afbe7130e644.jsonl`).
5. **10-22 23:47:26** — that subagent found a P1 ([BTG 2.0] Pending Message Sweeper,
   recipe 83291436, 68+ consecutive 5-min failures), set arousal 0.9, and per its brief
   fired `launchctl kickstart -k gui/$(id -u)/com.josh.fleet.dreamer` (tool call
   timestamped `2026-10-23T03:47:26.787Z` in the transcript).
6. **10-22 23:47:32** — launchd SIGKILLed the running instance (bash A **and** claude A
   — claude's final `-p` response never reached the OUT capture, so it died mid-run) and
   immediately restarted the job (invocation B). B hit the now-stale
   `/tmp/fleet-dreamer.lock` (A's `trap 'rm -rf "$LOCK"' EXIT` never ran — SIGKILL skips
   traps) → logged `already running, skipping` → exit 0.
7. **Aftermath:** dream report exists; heartbeat never appended (runner dead before
   `write_heartbeat`); no validation-ledger row for the killed run; watchdog report
   `garden-reports/2026-10-22-watchdog.md` lines 44-45 confess both actions:
   "Adrenaline set (arousal 0.9, by workato-watchdog) for the P1." / "Dreamer kicked
   (launchctl com.josh.fleet.dreamer) — incident posture."
8. **Why no code branch explains it:** the dreamer's report-write happens mid-run; the
   heartbeat comes from the runner after completion (plus the model's own check-in phase
   at the END of the prompt — never reached). Kill between the two = report without
   heartbeat. No early-exit, wrong-label, or guard path in run-job.sh produces this.

## The precise broken line

`~/.claude/agents/workato-watchdog.md`, section "The neuromodulation writer (when a P1
exists, mandatory first)" (~line 118-121):

    Then WAKE THE DREAMER (event-driven, not scheduled):
    `launchctl kickstart -k gui/$(id -u)/com.josh.fleet.dreamer`

`kickstart -k` unconditionally SIGKILLs the running instance and restarts. It cannot
know whether the dreamer is mid-run, and 23:43-23:50 nightly it ALWAYS is. Any P1
discovered during the nightly watchdog sweep (23:13-23:17 fleet lane, and this 23:43
interactive-lane sweep) lands inside the dreamer's run window — the two schedules
collide by construction.

## Minimal fix (PROPOSED, NOT APPLIED — Josh's go required)

Change the wake instruction to the lock-aware path the harness already has — the shared
mkdir lock in run-job.sh makes a concurrent start a harmless no-op
("already running, skipping"):

    If the dreamer is already mid-run (lock /tmp/fleet-dreamer.lock held), do NOT
    kick; the night run is already live and will see the incident. Wake it with:
    `bash ~/.local/bin/fleet/run-job.sh dreamer` (lock-aware; no-op if running),
    NEVER `launchctl kickstart -k` (kills the running instance mid-run).

Alternative one-token fix: drop the `-k` (`launchctl kickstart gui/.../dreamer`)
— without -k, kickstart no-ops when the job is already running. The run-job.sh path is
preferred because it also inherits probe/env handling and cannot double-dream.

## Self-heal status

The stale lock `/tmp/fleet-dreamer.lock` (mtime 10-22 23:43) is >6h old as of 05:43
10-23 and will be broken by the stale-lock rule at the next invocation — the 10-23
23:43 nightly run self-heals and should heartbeat normally. The missing 10-22 heartbeat
row is permanent (append-only ledger); the 10-21 gap is already adjudicated by the
nightly-receipts-gate escalation.

## Related observations (no action taken)

- run-job.sh's `validated()` counts a non-empty OUT capture as work evidence, so a
  killed-mid-run run WITH partial output would still be validated and heartbeated —
  here OUT held only the two startup warnings and the runner died before evaluating.
  The runner's own liveness is a single point of failure above both heartbeat paths.
- dream-nightly.sh (headless fallback lane) shares the same lock and was NOT involved.
