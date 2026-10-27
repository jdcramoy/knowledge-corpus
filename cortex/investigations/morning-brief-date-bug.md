# Investigation: future-dated morning brief (2026-10-19.md)

- Investigated: 2026-10-18 09:20-09:40 local (session, headless cortex dispatch)
- Verdict: NOT a UTC-vs-local date bug in any script. No script computes the date at all.
  The date string is produced by the MODEL at prompt-execution time, and it hallucinated
  +1 day, then conditioned on its own wrong output from 16 minutes earlier.

## The evidence file
`~/.claude/knowledge/morning-brief/2026-10-19.md` — born+mtime 2026-10-18 07:44:55 local
(11:44:55Z). Today was Oct 18 (local EDT and UTC). Content is a full morning brief using
overnight Oct-17→18 data.

## The writer (exact)
- Scheduled task: `[morning-brief-daily]`, id `e9bd64af`, cron `13 7 * * *`, durable+recurring,
  defined in `~/Documents/workbench/.claude/scheduled_tasks.json` (project-scoped
  CronCreate task — a SECOND brief writer parallel to the fleet brief job).
- Executing session: `3df5be5d-65fd-4735-871d-0d16dd1a578e` (cwd ~/Documents/workbench — the
  long-lived Oct-16 "3js system map" session that hosts all scheduled-task fires for that project).
- Write: transcript line 5200, tool Bash at 2026-10-18T11:44:54.870Z:
  `cat > ~/.claude/knowledge/morning-brief/2026-10-19.md <<'EOF'` — there is NO thinking block
  and NO `date` command anywhere in the turn. The model wrote "2026-10-19" straight into the
  heredoc.
- After the write it POSTED the brief to Slack DM (channel D0A40K944M7, Slack ts
  1792323907.437779) — the prompt's "skip quietly if confirmation cannot be answered" confirm
  gate did NOT hold, because the session runs bypassPermissions. Josh received a live DM.

## Why the fire was late (07:43 for a 07:13 cron)
The session was busy running the harness-docs-sync task; scheduled prompts only fire when the
REPL is idle, so delivery landed at 11:43:00.125Z (07:43 local). This made the cron brief RACE
the fleet brief job (launchd com.josh.fleet.brief, 07:13), which had already written the
CORRECT `2026-10-18.md` at 07:14:34.

## Where the +1 day came from
- The prompt says write to `morning-brief/<today>.md` but never instructs running `date`;
  the model must recall the date from context.
- Context held the correct date: system-reminder at 04:00:59Z said "Today's date is now
  2026-10-18".
- Origin of the wrong belief: the SAME session, 16 minutes earlier (07:28 local), labeled a
  git commit `harness-docs sync 2026-10-19` (agentic-workato-kit commit 9041363) — while 25
  minutes before that (07:03, commit 2a67b80) it had correctly used "sync 2026-10-18". The
  model drifted +1 with no computation, then echoed its own erroneous commit label when the
  brief task arrived. Self-conditioning on its own recent output, not a timezone bug.
- Proof by contrast: the fleet brief job's prompt embeds literal `$(date +%F)` which the
  headless agent evaluates via Bash -> always the true local date (2026-10-07 through
  2026-10-18.md all correct, ~2KB each; the cron task is the only wrong-dated file in the dir).

## Impact
- The loadout job ("read the NEWEST file in morning-brief/") already mis-read 2026-10-19.md as
  today's brief at 07:45, and will again tomorrow unless the file is removed.
- Two brief writers run daily and race; the cron one also DMs Slack without an effective
  confirm gate in bypassPermissions sessions.

## Recommended fixes (NOT applied — read-only investigation)
1. Delete or rename `~/.claude/knowledge/morning-brief/2026-10-19.md` so the loadout job
   stops treating tomorrow as the newest brief. (Needs Josh's go or next session.)
2. Harden the `[morning-brief-daily]` prompt (id e9bd64af in workbench scheduled_tasks.json):
   replace `<today>.md` with "run `date +%F` via Bash and use its output verbatim for the
   filename and title" — the same mechanism that keeps the fleet brief correct.
3. Consider deleting the duplicate cron brief writer entirely (fleet brief job owns the file;
   keep the cron task only if the Slack DM step is wanted) — two writers racing is the
   structural bug.
4. Side finding: FOUR duplicate `[harness-docs-sync-nightly]` tasks now exist in
   scheduled_tasks.json (ids 017afeef, cca9ad06, a1c65627, 504715c9) — the "self-rearm"
   instruction creates a new task without deleting its own row first; each rearm adds a copy.
   Same bug class the brief task will hit after 4 more days.
5. The cron brief wrote its heartbeat with a plain `>>` append, violating the atomic_io rule
   stated in its own prompt.

## Files/scripts ruled out (checked, not the writer)
- `~/Library/LaunchAgents/com.josh.fleet.brief.plist` + `~/.local/bin/fleet/run-job.sh` +
  `jobs/brief.prompt` — fleet brief ran 07:13:05-07:14:48, wrote 2026-10-18.md correctly.
- `com.josh.fleet.loadout.plist` + loadout job — started 07:45:05, only READ the 2026-10-19
  file (session ec86c2a6).
- `com.josh.gw-semantic-dashboard.plist` (07:42) — python snapshot script, no brief writes.
- All of ~/.claude/knowledge/scripts/ — no morning-brief writers (only readers/trackers).
