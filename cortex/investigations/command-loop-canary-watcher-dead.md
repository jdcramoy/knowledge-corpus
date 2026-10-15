# Command-loop canary failure — watcher dead, fix landed 2026-10-15 12:12Z (read-only investigation, 2026-10-15 ~14:57Z)

**VERDICT: same root cause as the Oct-14 investigation — dead plist interpreter — and it is ALREADY FIXED (12:12Z today). All three daily failures (Oct 13/14/15 at ~10:05Z) are one incident. The 10:05Z cluster is a schedule artifact: the canary fires once daily at 06:05 local (10:05 UTC, EDT), so every result is stamped ~10:05Z. Today's failure was the last one measured BEFORE the fix landed. Tomorrow's 10:05Z tick should go green.**

## Answers

### (1) Is the command-watcher alive right now and polling?
YES. Evidence:
- `launchctl print gui/<uid>/com.josh.agent-command-watcher`: `last exit code = 0` (was 78 before the fix), state active. PID "-" between ticks is normal for a StartInterval=60s on-demand job.
- `/tmp/agent-command-watcher.log` fresh write at 13:34Z today (a real directive executed, BTSUP-76729-related output) — 82 min before this investigation.
- Backlog proof of polling: the three stuck canary rows were consumed in a ~2s burst at 12:13:17–12:13:19Z, one minute after the 12:12Z reload — the watcher's first tick swept the queue.

### (2) Why do canary rows time out at the same hour daily?
Two layers:
- **Same-hour clustering is an artifact.** `com.josh.fleet.canary` runs once daily at StartCalendarInterval 06:05 local = 10:05 UTC. The canary itself polls the row every 15s for the full 300s SLA, so the failure is a genuine SLA miss, not a polling-window artifact — but every result (pass or fail) is stamped ~10:05Z because that is the only run time.
- **The genuine miss cause was the plist interpreter path.** The plist pointed at unversioned `/opt/homebrew/bin/python3`, removed by a Homebrew python upgrade on Oct 12 (between the 12:27Z pass and EOD). Every 60s launchd tick failed to spawn (last exit 78), the log froze Oct 12 13:48Z, and no queue row was processed until the repoint. It was NOT "watcher processing but not marking done" — queue reads today show the Oct 13/14/15 rows were still `pending` until the fix, then went `done` with `selfcheck ok at 2026-10-15T12:13:*` result notes.

### (3) Same root cause as the open plist-repoint triage row, or new?
SAME. Triage row `agent-command-watcher-plist-repoint` (triage/queue.jsonl, sourced from the Oct-14 investigation `command-canary-1005-double-failure.md`) named exactly this defect. It was executed and marked `fixed` at **2026-10-15T12:14:37Z** by a harness-fix session: ProgramArguments repointed `/opt/homebrew/bin/python3` → `/opt/homebrew/bin/python3.14`, launchctl reloaded, exit 78 → 0, selfcheck-ok lines at 12:13Z. Verified independently here: plist mtime Oct 15 08:12 EDT (= 12:12Z), on-disk plist now references python3.14 (symlink exists, Cellar 3.14.8_2), queue rows show the backlog consumed.
- The other row, `canary-silent-stop-watch` (Workato recipe 82964017 gw_semantic_mutation_chain_canary dark ~6h), is UNRELATED — that is about recipe-side canaries having no liveness surface, not the local Slack command loop.

### (4) Smallest fix
Already applied; nothing left to change for the root cause. Remaining tail work (for Josh / a write-enabled session):
1. **Re-run the canary now instead of waiting for tomorrow's 10:05Z tick** (NEVER-wait rule): `python3 ~/.claude/knowledge/scripts/command-canary.py` — expect PASS. This also overwrites the stale FAIL in `garden-reports/command-canary-status.json`, which the replay-gym freshness invariant and morning brief read. (Not done here: read-only session; the canary writes a queue row and a Slack ack.)
2. Note the three "failed" rows are now `done` with result note `selfcheck ok at 2026-10-15T12:13Z` — their Slack acks posted 2 days late for Oct 13/14 rows; cosmetic only, no action needed.
3. Optional hardening (from the Oct-14 report, still unapplied): sweep remaining fleet plists for unversioned interpreter paths, and/or add exit-78 telemetry so "watcher spawn-dead" is distinguishable from "watcher not polling" without a manual launchctl check.
4. The `canary-silent-stop-watch` row stays open on its own merits (recipe 82964017 is stopped, per the 14:04Z owned-asset sweep).

## Evidence appendix (all live, this session ~14:50-14:57Z)
- plist ProgramArguments: `/opt/homebrew/bin/python3.14 ~/.local/bin/agent-command-watcher.py`; plist mtime 2026-10-15 08:12 EDT.
- `/opt/homebrew/bin/`: python3.11, python3.12, python3.14 present; NO unversioned `python3` (confirms original breakage and correctness of repoint target).
- Queue (read-only query via watcher module API): rows `canary:2026-10-13T10:05:02`, `canary:2026-10-14T10:05:05`, `canary:2026-10-15T10:05:05` all status `done`, result notes `selfcheck ok at 2026-10-15T12:13:17/18/19Z`.
- `command-canary-status.json`: FAIL, checked 2026-10-15T10:05:05Z, row d7b1b16d — stale relative to the 12:12Z fix; will flip green on next canary run.
- Heartbeat: PASS 10-12 10:05Z and 12:27Z; FAIL 10-13, 10-14, 10-15 (all ~10:05-10:10Z) — three consecutive daily failures, one root cause.

## NOT verified (read-only scope)
- A fresh end-to-end canary PASS post-fix (needs a write: injects a queue row + posts a Slack ack).
- Whether the delayed 12:13Z acks for the Oct 13/14 rows actually landed in room C0C7JHJKHRU (cosmetic; the rows are done).
- Tomorrow's 10:05Z scheduled tick (future event).
