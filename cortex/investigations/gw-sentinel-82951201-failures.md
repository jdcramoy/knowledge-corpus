# Investigation — dev recipe 82951201 gw_fleet_liveness_sentinel new failures

Investigated 2026-10-11T09:1xZ (cortex-dispatched headless read-only probe; triggered by the
owned-asset sweep flag of 2026-10-11T08:12Z). READ-ONLY throughout: AIRO dev MCP job/recipe
reads, one `wt api GET /api/recipes/82951201`, local file reads. Nothing was changed.
Recipe: https://app.workato.com/recipes/82951201

## Verdict (TL;DR)

The 3 "new failures" are a tight 24-minute burst (07:05-07:13 UTC, 2026-10-11) of HTTP 400
Bad Request errors — a blank parent_id interpolated into /api/folders?parent_id= — that
ended when a guard fix was pushed at 07:28:25Z. They are NOT continuous code failures and
NOT a sleep/launchd artifact: the sentinel runs on Workato's cloud scheduler and executed
hourly through the ENTIRE stall window with successes. The burst is coincident with the
trailing edge of the stall window, but the causal story is an active edit/fix session
overlapping the window, not the machine stall. Liveness data is NOT stale: recovery was
same-hour and the downstream heartbeat gap was ~22 minutes, far below any silence threshold.

## (a) Failure timestamps and count, last 48h

Job list (dev ws 3535597): 51 jobs total, 48 succeeded, 3 failed. All 3 failures in the
burst; zero failures in the prior 48h outside it.

| Job | Started (local -07:00) | UTC | Status |
|---|---|---|---|
| j-AbtK39dX-YGRPdk-CD | 2026-10-11 00:05:42 | 07:05:42Z | FAILED |
| j-AbtK8AwG-EsNELc-CD | 2026-10-11 00:09:58 | 07:09:58Z | FAILED |
| j-AbtKAKPw-L4EgRF-CD | 2026-10-11 00:13:04 | 07:13:04Z | FAILED |
| j-AbtKCYke-J6BRtH-CD | 2026-10-11 00:16:15 | 07:16:15Z | succeeded (recovery) |

Sweep corroboration (workato-health/sweeps/): verdict "ok" through 2026-10-11T06:11:18Z,
first "new-failures" at 07:11:43Z (fails=2), fails=3 by 08:12:10Z. state.json
failed_counts["82951201"] = 3.

## (b) Failure class — exact error line (most recent failed trace)

Job j-AbtKAKPw-L4EgRF-CD, line 8 ("List project child folders", __adhoc_http_action):

    400 Bad Request: {"message":"Invalid parameter 'parent_id' value \"\": Must be a number."}

Request path observed in the trace inputs: /api/folders?parent_id=&per_page=100.
The earliest failure (j-AbtK39dX-YGRPdk-CD) is the identical class on the identical line.
Mechanism: the folder-detail step (GET /api/folders/{self_folder_id}) returned an object
with an empty parent_id; the next step interpolated it blank into the child-folders call.
This is a parameter-validation failure, not auth, not rate limiting. The CURRENT recipe code
contains a skip-with-log guard for exactly this class (steps 9-11, event
sentinel_parent_id_empty, clean no-op instead of the 400) — comments inside it cite
"2026-10-11 400 Bad Request class, recipe-health-82951201-new-failures".

Key sequencing evidence:
- Recipe updated_at = 2026-10-11T00:28:25-07:00 (07:28:25Z) — between the last failure
  (00:13) and the 00:29 success. The guard fix landed right before recovery.
- The failed traces show DIFFERENT step layouts (00:05 job: lines 5=http/6=http/7=ruby;
  00:13 job: lines 5=http/6=ruby/7=http) — the code changed between failures, so an edit/
  test session was iterating mid-burst. The five runs at 00:05/00:09/00:13/00:16/00:29
  local all sit off the recipe's :54 hourly anchor, consistent with Test executions from
  that session rather than scheduler ticks (Test runs of a clock recipe render the same
  "Scheduler by Workato" title, so scheduled-vs-Test cannot be distinguished from the title
  alone — flagged as an inference, not a verified fact).

## (c) Correlation with the sleep/launchd stall window (2026-10-10 08:00Z - 2026-10-11 09:00Z)

EDGE-CLUSTER, THEN RESUME — and causally independent of the stall:

- The sentinel executes on Workato's cloud scheduler, not local launchd. The hourly job
  record is CONTINUOUS through the whole window: 01:54 through 23:54 local on 10-10 all
  present and succeeded (17 hourly runs inside the window), so the machine stall never
  touched collection. A launchd stall cannot produce this failure signature at all.
- The 3 failures cluster in 8 minutes (07:05-07:13Z), ~2h before the window's stated end
  (09:00Z), with recovery 3 minutes after the last failure. There is no spread of failures
  across the window — nothing continuous about it.
- The failures ended with a recipe push (guard) at 07:28:25Z, i.e. they are the visible
  residue of a fix session iterating during the window (the same window in which the
  cortex pulse lane was down), not degradation of the deployed logic. The pre-burst
  scheduled run at 23:54 local succeeded, and every run after 00:29 local succeeds
  (00:29, 00:54, 01:54 local).

## (d) Blast radius — consumers of sentinel output

1. Gateway-silence monitor 82830607 (the main one): reads sentinel heartbeat events
   (capability_id fleet_liveness_sentinel, sentinel-hb- prefix) from data table
   workspace_learning_events_v3
   (https://app.workato.com/data_tables/8693bbe5-3e60-4538-b021-89cbcdb5c04f)
   with no event-type filter. Failed runs die at line 8, BEFORE the step-27 heartbeat
   write, so the 3 failed runs wrote no heartbeat. Resulting gap: ~22 minutes
   (23:54 -> 00:16 local) against an hourly cadence — far below any 3x-interval silence
   threshold. No stale liveness signal propagated.
2. #gw-semantic-alerts daily digest (channel C0C6S3VT4KF): posted once/UTC-day by
   successful runs. Post-recovery runs on 10-11 succeeded, so the digest should have
   posted on schedule; the digest also folds in conformance_freshness and mutation_drill
   rows, which were never stale because the outage window was under an hour.
3. Anomaly DM to Josh (U0A3R9AVAMA): fires only on FLEET anomalies found by the
   sentinel's evaluation, not on the sentinel's own failure — unaffected.
4. Local consumers: workato-health sweeps + state.json failed_counts (this flag's
   source) and the triage queue entry — both reflect the flag and are now answered by
   this report. The sentinel writes to no triage file or dashboard directly.

## What was NOT verified

- Whether the daily digest line for 2026-10-11 actually posted to #gw-semantic-alerts
  (Slack read not performed; inferred from successful post-recovery runs).
- The step-7/8 output payloads inside the failed traces (job_get shows the failed line's
  inputs/outputs only), so the precise upstream reason the folder-detail response carried
  an empty parent_id is inferred from the guard's own documentation, not observed raw.
- Scheduled-vs-Test classification of the 5 off-anchor runs (titles are identical for
  both on clock recipes) — stated as inference above.
- data_table_query against 155508 to directly confirm the heartbeat gap returned HTTP 404
  (query route unavailable in this environment); the gap is derived from job traces instead.
