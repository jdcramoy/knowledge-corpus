# Scheduled-tasks wipe attribution — 2026-10-19 13:10:54 EDT

Bounded read-only investigation (flash lookup class), 2026-10-19. Evidence: session transcripts
under ~/.claude/projects/, ps record of pid 74326, file mtimes, backup file
`workbench/.claude/scheduled_tasks.json.bak-20261016-dedupe`.

## VERDICT

**The librarian agent is INNOCENT. The wipe was performed by the Claude Code harness itself, at
session `--resume` startup.** At 13:10:53 EDT Josh launched `claude --dangerously-skip-permissions
--resume 3df5be5d-65fd-4735-871d-0d16dd1a578e` (pid 74326 — resuming the librarian/Atlas session).
**One second later, 13:10:54 EDT**, the harness rewrote `workbench/.claude/scheduled_tasks.json`
keeping ONLY the single task that session had created itself, silently dropping all 8 tasks created
by other sessions. Full overwrite from session-local state, not a merge.

## Evidence chain

1. `stat` on the file: mtime **Oct 19 13:10:54 2026** (EDT).
2. `ps -p 74326`: `claude --dangerously-skip-permissions --resume 3df5be5d-...` **STARTED Mon Oct 19
   13:10:53 2026** — one second BEFORE the mtime. (Still alive at ~21:00 — Josh's live session.)
3. The surviving task `0fde60dd` carries `createdAt` 1792375711142 = **2026-10-19T02:08:31 UTC**
   (the librarian's own CronCreate), but `createdByPid` 74326 / `createdByProcStart` "Mon Oct 19
   17:10:53 2026" (UTC) — **re-stamped by the resuming process**, proving pid 74326 re-serialized
   the file.
4. Transcript `3df5be5d-...jsonl` has **zero tool calls between 17:10:53 UTC and the first user
   message at 19:15:57 UTC** ("WHere are we at with the three.js map?"). The write happened at
   startup, ~2 hours before any model turn — a harness write, not a model write.
5. Exhaustive transcript sweep (all projects, incl. subagent transcripts) for Oct 19
   `scheduled_tasks`/`CronDelete`/`CronCreate` activity: **no model-side write to the file anywhere
   between 02:08:31 UTC and end of day**. Only CronCreate hits were non-durable/smoke tasks in
   other projects.

## Why the librarian's rearm flow is NOT the culprit (but is adjacent)

Session 3df5be5d (the librarian run) was active Oct 19 02:07–02:08 UTC (Oct 18 ~22:07 EDT). Its
flow: read the file (8 fleet tasks + 4 `[harness-docs-sync-nightly]` copies), run a **python
json.dump full-overwrite dedupe** at 02:08:12 ("kept 8 tasks (dropped 3 duplicate
harness-docs-sync)"), then CronCreate the new durable librarian task 0fde60dd at 02:08:31 →
9 tasks. That flow PRESERVED all 8 fleet tasks. Its "delete the old one" only ever targets the
librarian's own prior task (d5023099, created Oct 11, already expired/absent before this run).

**Real bug found in passing:** the librarian's 02:08:12 dedupe was itself a raw full-overwrite
write to scheduled_tasks.json via Bash/python, bypassing CronDelete — same mechanism class as the
Oct 16 dedupe that produced `.bak-20261016-dedupe`. Correct this time, but it is the pattern to
ban for this file.

## Root-cause mechanism (harness, inferred from evidence)

On `--resume`, the harness re-persists the resumed session's OWN scheduled-task state over
`<project>/.claude/scheduled_tasks.json`. The survivor is exactly the one task whose
`createdBySessionId` equals the resumed session; durable tasks created by OTHER sessions are
invisible to that state and get dropped. Fresh (non-resume) session starts do not hit this —
Oct 19 morning sessions ran fine against the 9-task file. Mechanism inferred, not source-verified
(cc 2.1.289).

## Tasks lost (present 02:08:31 UTC -> absent 13:10:54 EDT) — 8 of 9

| id | task | cron | last (re)created |
|---|---|---|---|
| e9bd64af | morning-brief-daily | 13 7 * * * | Oct 16 11:43 UTC (rearm by 90ed4349) |
| 504715c9 | harness-docs-sync-nightly | 57 6 * * * | Oct 18 11:27 UTC (newest of 4 dupes) |
| 9cc2f965 | brain-gardener-nightly | 43 22 * * * | Oct 17 03:13 UTC (rearm by 5526b97a) |
| 64dba4c6 | workato-watchdog-nightly | 13 23 * * * | Oct 17 03:43 UTC (rearm by 5526b97a) |
| 440c1f87 | jira-triage-fleet | 23 9 * * 1-5 | Oct 13 13:25 UTC (d15587bc) |
| cc84cd69 | estate-architect-weekly | 37 6 * * 1 | Oct 12 11:07 UTC (8084840d) |
| b4fed8af | corpus-indexer-weekly | 7 6 * * 1 | Oct 12 10:37 UTC (8084840d) |
| 6cf5146d | board-minutes-weekly | 27 6 * * 1 | Oct 12 10:27 UTC (6ca94de6) |

Sole survivor: **0fde60dd** — librarian weekly (37 21 * * 0), because the resumed session created it.

IDs cross-verified from the rearm sessions' CronCreate tool_results (90ed4349, 5526b97a, 3df5be5d,
8084840d, d15587bc) and the Oct 16 backup. First missed firings if not restored: corpus-indexer +
estate-architect + board-minutes + harness-docs-sync the morning of Oct 20, jira-triage 09:23,
morning-brief 07:13. (Related: `morning-brief-run-missed-1019.md` in this directory.)

## Recoverability & recommendations

- All 8 prompts are fully recoverable from the CronCreate tool_use blocks in the transcripts of the
  sessions listed above (and 6 of 8 directly from `.bak-20261016-dedupe`).
- Rule to adopt: NEVER write scheduled_tasks.json directly (Bash/python json.dump); CronCreate/
  CronDelete only — direct writes make resume-clobber undetectable and non-atomic.
- Harness-level fix to request: resume must MERGE durable tasks by id, not overwrite with
  session-local state.

## What was NOT verified

- The exact harness source path performing the resume-time rewrite (mechanism inferred from the
  re-stamped createdByProcStart + 1-second timing + survivor set, not from cc source).
- Whether any of the 8 fired AND completed final runs on Oct 19 morning before the 13:10 wipe —
  no Oct 19 morning rearm writes found in transcripts, so no contradiction with the wipe account.
