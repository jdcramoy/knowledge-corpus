# Investigation: morning-brief 10-19 run miss — launchd/log attribution

Dispatched 2026-10-20T00:08:40Z (cortex pulse, lookup class, flash headless).
Headless agent could not write this file (sensitive-path gate); findings
harvested from `~/.local/state/cortex/dispatch-20261020T000840Z.log` by the
pulse session per sanctioned-persistence doctrine.

## Verdict

The brief never ran on 2026-10-19 because the machine was **powered off**
07Z–15Z UTC. Separately, a bigger finding: the durable cron tasks
`[morning-brief-daily]` and harness-docs-sync are GONE from
`scheduled_tasks.json` — likely wiped by the librarian's weekly rearm.

## The evidence

1. **Machine-level outage, not job-level.** `garden-reports/heartbeat.jsonl`
   hourly census for Oct 19 UTC: hours 07Z–14Z = zero entries (every job —
   session-shadow at 1-min cadence, workato-health, cortex — went dark
   simultaneously). Last entry before the gap: `{"ts": "2026-10-19T06:22:26Z",
   "job": "session-shadow"}`. First after: `{"ts": "2026-10-19T15:51:24Z",
   "job": "ops-visibility"}`.
2. **Powered OFF, not asleep.** `pmset -g log` for Oct 19 shows exactly one
   transition: `2026-10-19 11:51:00 -0400 Start — powerd process is started` —
   a fresh boot. No Sleep/Wake events all day. launchd does not retro-fire
   missed `StartCalendarInterval` jobs at boot (only at wake-from-sleep).
3. **launchd config intact, never invoked.**
   `~/Library/LaunchAgents/com.josh.fleet.brief.plist` (mtime Oct 7, Hour=7
   Minute=13) still loaded, `launchctl list` exit 0. But
   `~/.local/state/fleet/brief.log` ends at `2026-10-18 07:14:48 brief: done
   validated` — no Oct 19 start bookend. Zero bytes of run-job.sh output on
   Oct 19 = zero invocations.
4. **The cron writer no longer exists.** `workbench/.claude/scheduled_tasks.json`
   (mtime Oct 19 13:10, 1514 bytes) holds exactly ONE task — the librarian
   weekly rearm (`0fde60dd`). Zero matches for morning-brief or
   harness-docs-sync. The `[morning-brief-daily]` task (`e9bd64af`) from the
   10-18 investigation is gone. Either someone cleaned up quietly, or the
   librarian self-rearm ("re-create, then delete the old one") wiped unrelated
   durable tasks when it rewrote the file. If the latter, every durable cron
   task in that project is one rearm away from deletion.
5. **Why Josh read stale content.** No Oct 19 brief was produced; newest file
   = the stray `2026-10-19.md` (born Oct 18 07:44:55, the hallucinated-date
   write), so "read newest brief" paths served Oct 18's data. The loadout job
   couldn't help — 07:45 was also inside the powered-off window.
6. **Prior findings tie-in.** The 10-18 double-write attribution (fleet job +
   cron task) holds. Unlike the pulse-heartbeat-skip false alarm, this gap is
   real and physical — corroborated by the boot event.

## Not verified

- Who/what rewrote `scheduled_tasks.json` at 13:10 Oct 19 (transcripts of
  session `3df5be5d` around that time not swept — heavy read).
- Whether any durable tasks beyond morning-brief-daily and harness-docs-sync
  were lost in the rewrite.
