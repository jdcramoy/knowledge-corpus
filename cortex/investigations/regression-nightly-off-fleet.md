# Investigation: regression-nightly off-fleet 4+ nights

Investigated: 2026-10-15 (dispatch dispatch-1792094846.log, cortex P1). READ-ONLY: nothing re-armed, deleted, or modified.

## Verdict

**UNLOADED — deleted by an agent, not failed, not expired.** The job's only scheduler
registration ever was a Claude Code durable CronCreate task (`d9579292`, project-scoped
to `~/Documents/workbench`, cron `13 0 * * *` = 00:13 nightly). On **2026-10-12
04:43:24 UTC (00:43 EDT)** the very session executing that night's run CronDeleted it,
having mis-identified the morning-brief task as a "duplicate" regression task via a
substring match. There has been no registration since; the last 3 nights (Oct 13/14/15)
never fired because nothing existed to fire. The suite itself is healthy — the Oct 12
run completed and reported normally 7 minutes after its own schedule was deleted.

## What the registration actually was (vs what the docs say)

- `domains/workato-platform.md` line 977: "Cron 00:13 nightly (d9579292), self-rearming,
  heartbeat-stamped". This is **wrong about the mechanism**: `d9579292` is not a Unix cron
  entry. Transcript evidence (`projects/-Users-<user>-Documents-workbench/
  b34c1197-...jsonl` line 4484, 2026-10-07T11:29:05Z): a `CronCreate` call,
  `durable: true`, `recurring: true`, cron `13 0 * * *`, persisted to
  `~/Documents/workbench/.claude/scheduled_tasks.json`. The tool result literally said
  "Auto-expires after 7 days."
- Consequences of the mislabel:
  - `crontab -l` is genuinely empty (verified today; exit 0, no output) — the Oct 13
    brew-python3-unlink blast-radius sweep checked the real crontab, found it empty, and
    recorded "crontab: empty — zero cron consumers" as *normal*. The deletion was
    invisible to every OS-level check (no launchd plist ever existed either — verified
    in `~/Library/LaunchAgents`, the backup repo `~/Documents/josh-orca/launchagents/`
    full git history, and `config/fleet/` full git history).
  - CronCreate tasks fire only inside a live, idle REPL of the owning project
    (workbench — now the post-split archive). Even a surviving task was fragile.

## The delete, blow by blow (session 8084840d, transcript lines 1277-1294)

1. The regression-nightly task fired normally at 00:13 EDT Oct 12 in session 8084840d
   (that session also hosted the watchdog fire at 23:43 EDT).
2. Prompt step 1 is the self-rearm check: "find the task whose prompt STARTS WITH
   [regression-nightly]". The session instead ran a python one-liner with
   `if 'regression-nightly' in json.dumps(t)` — a **whole-JSON substring match**.
3. That matched TWO tasks (L1279):
   - `d9579292` age=4.72d — the real regression task (created 2026-10-07 11:29:05 UTC)
   - `ea82875d` age=0.71d — the **morning-brief** task (cron `13 7 * * *`), whose prompt
     body lists "regression-nightly" in its heartbeat-job roster. Created 2026-10-11
     11:35:41 UTC by session 352210da, 7 min after that session CronDeleted `07c94e79` —
     which `domains/dream-loop.md` line 104 documents as the OLD morning-brief ID. So
     ea82875d is provably the morning-brief's own self-rearm successor, never a
     regression task. (Age math re-verified: 0.714d and 4.718d at the delete instant —
     exact match with the session's printout.)
4. L1291 thinking: "Two regression-nightly tasks found… a duplicate… the younger one
   (ea82875d, likely re-created last night)". It correctly noted d9579292 was under the
   5-day rearm threshold ("no re-arm needed yet") — then deleted the original anyway to
   fix the phantom duplicate. L1292: `CronDelete {"id": "d9579292"}` → "Cancelled job
   d9579292."
5. The session then ran the suite (L1297), wrote `garden-reports/regression-2026-10-12.md`
   (00:50:45 EDT), relayed the failures, and appended the heartbeat (04:50:57 UTC) —
   all AFTER the delete. It never re-checked that a regression task still existed.
   Post-action verification would have caught it instantly: the "surviving duplicate"
   fires at 07:13, not 00:13.

## Timeline

- Oct 7 11:29 UTC — `d9579292` created (durable, recurring, 00:13 daily, 7-day auto-expiry).
- Oct 8-12 — fires nightly; reports `regression-2026-10-08..12.md` written ~00:50 local.
- Oct 12 00:43 EDT — registration deleted mid-run by its own firing session (above).
- Oct 13/14/15 00:13 — never fired: no registration existed. (The 7-day expiry, Oct 14
  07:29 EDT, is a red herring for the misses — it would only have mattered from Oct 14,
  and it removes the "it would have come back on its own" possibility: it would not have.)
- Oct 15 — current `scheduled_tasks.json` holds 11 durable tasks, none for regression.
  Every survivor carries a self-rearm preamble; several (brain-gardener e3cb2117,
  watchdog e33b8a6b, jira-triage) last fired TODAY, so the workbench REPL lane itself
  is alive — only the regression entry is gone.

## Why 3 nights passed with no alarm

- The watchdog's "machine skipped last night" P0 check only watches brain-gardener and
  docs-watch heartbeats — regression-nightly is not in its coverage.
- harness-health.py contains no regression string (grepped).
- Heartbeat gaps are not alarming on their own: the Oct 9 and Oct 11 runs also wrote no
  heartbeat row (file was rewritten in the Oct 11 queue-reversion incident), so a
  missing row was not a reliable signal even before the delete.
- The cron-mislabel sent the one infrastructure sweep (Oct 13 brew-unlink) to the wrong
  surface.

## Frozen state behind the outage (from the last real run, Oct 12)

12 passed / 3 failed / 3 errors; fixtures 1 pass / 2 fail / 6 skipped. Untriaged:
82239660 + 82727069 + 82959480 ("could not start run" ERRORs), Seismic 82248514 +
82256903 FAILs, 82272814 vua_identity_probe FAIL, fixture 82863111 FAIL. Prior autopsies
(regression-unsatisfiable-tests.md, seismic-vua-probe-regression-1011.md,
82272814-vua-probe-regression.md) already classify the VUA-bound FAILs as unsatisfiable
headless by construction — the genuinely open items are the three start-ERRORs and the
82863111 fixture.

## Root cause, one sentence

A self-rearm lookup that substring-matched `regression-nightly` across whole task JSON
(instead of the prompt's "starts with") matched the morning-brief task, and the firing
session "deduped" the phantom by deleting the only real registration — an unverifiable
schedule mutation performed without a post-delete read-back.

## Fix directions (for Josh / the open triage card regression-nightly-off-fleet-4-nights — NOT executed, read-only dispatch)

- Re-arm-or-retire decision is Josh's. If re-arm: the launchd lane
  (`com.josh.fleet.regression-nightly.plist` → `run-job.sh` + `jobs/regression-nightly.env`
  with `CLAUDE_JOB=no` and a `.script` calling the python directly) removes both the
  REPL-idle dependency and the 7-day expiry class; the fleet's own deploy checklist
  (canonical copy in `config/fleet`, kit, and `~/.local/bin/fleet` identical) applies.
- If it stays a CronCreate task: the rearm lookup must anchor on
  `prompt.startswith("[regression-nightly]")`, and the prompt should require a
  post-mutation read-back (list tasks after any delete/create) — the same
  verify-after-write rule as everywhere else.
- Either way: add regression-nightly to the watchdog's heartbeat P0 watch list.
- Doc fix: `workato-platform.md` line 977 should stop calling it "Cron".

## Evidence index

- Delete event: `~/.claude/projects/-Users-<user>-Documents-workbench/8084840d-4576-4d51-a09d-47ff6f5d66b3.jsonl` lines 1277-1294 (2026-10-12T04:43:18-24Z).
- Original registration: `.../b34c1197-74bb-425a-836f-f35d458a69e1.jsonl` line 4484 (CronCreate) + line 4487 (tool result "Auto-expires after 7 days").
- Current state: `~/Documents/workbench/.claude/scheduled_tasks.json` (11 tasks, no regression entry; global `~/.claude/scheduled_tasks.json` empty).
- Last run: `~/.claude/knowledge/garden-reports/regression-2026-10-12.md` + `-latest.md` (mtime Oct 12 00:50:45); heartbeat rows Oct 8/10/12 only.
- No plist ever: `~/Library/LaunchAgents` (live), `~/Documents/josh-orca/launchagents/` (full git history), `~/.claude/knowledge/config/fleet/` (full git history), `launchctl list`, `crontab -l`.
- Morning-brief identity of ea82875d: createdAt 2026-10-11T11:35:41Z + CronDelete of its predecessor `07c94e79` at 11:35:30Z (session 352210da) + `domains/dream-loop.md:104` ("Cron 07:13 daily (id 07c94e79)").

## Not verified / out of scope

- Whether session 8084840d's substring one-liner was its own improvisation or copied
  from an earlier rearm (transcript archaeology beyond the delete window not done).
- Why no heartbeat rows exist for the Oct 9 and Oct 11 runs (attributed to the Oct 11
  queue-reversion file rewrite, not re-proven).
- No attempt was made to re-arm, run the suite, or touch any schedule state (read-only).
