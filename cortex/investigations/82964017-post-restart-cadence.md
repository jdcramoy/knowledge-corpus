# Investigation: 82964017 post-restart cadence — read-only (cortex dispatch 2026-10-13T21:50Z)

Task: verify post-restart trigger config + run flow vs BSYS-29560 hourly cadence AC.
Method: live `wt api GET /api/recipes/82964017` + job list (read-only), sweep trail
`workato-health/sweeps/2026-10-13T*`, cached autopsy `82964017-trigger-autopsy.md`,
cached BSYS-29560 state. No writes to Workato, no Jira posts.

## VERDICT: DEFECT — restarted on the UNREPAIRED trigger. Runs are NOT flowing hourly.

The restart put the still-malformed v12 trigger config back on the scheduler. Two
post-restart runs exist today (08:01 PT, 13:30 PT), each one ~1h after a distinct
restart, separated by a 5.5h dead gap. Root cause from the autopsy (Fix A picklist
repair) was never applied.

## (1) Current trigger/schedule configuration — STILL BROKEN, untouched since v12

Live raw code (wt api get, 2026-10-13 ~21:50Z):

    {"as":"scheduled_event_9d42","number":0,"keyword":"trigger","provider":"clock",
     "input":{"time_unit":"Minutes","trigger_every":"60","trigger_at":"00:07"},
     "dynamicPickListSelection":{"time_unit":"Days"},
     "visible_config_fields":["time_unit","trigger_at","trigger_every"], ...}

All three autopsy defects are still present, byte-for-byte:
- `input.time_unit` = "Minutes" — picklist LABEL, not the lowercase option ID ("minutes").
- `dynamicPickListSelection.time_unit` = "Days" — contradicts the input.
- `trigger_at: "00:07"` — orphaned field invalid for the Minutes unit.
Recipe record: version_no=12, updated_at=2026-10-12T16:39:28 PT (unchanged — NO push
since the v12 push that broke it). Live state: running=True, stop_cause=None,
job_count=11, 11 succeeded, 0 failed.
Recipe: https://app.workato.com/recipes/82964017

## (2) Was 13:29Z the only post-restart run? NO — two post-restart runs, but NOT flowing

Job timeline (started_at, workspace-local PT):

- 2026-10-12 17:31:58 — last pre-stop run (j-AbwEnLfz-MhBzWJ-CD)
- [auto-stop 04:34:42Z Oct 13, stop_cause=trigger_errors_limit — sweeps 10:38Z–14:40Z
  show running=False]
- **2026-10-13 08:01:31 — restart #1 fired once (j-AbwXgogH-N3eMTP-CD), succeeded**
- 5.5h ZERO runs (sweeps 15:40Z–19:42Z show running=True but last_run frozen at 08:00 PT)
- **2026-10-13 13:30:22 — restart #2 fired once (j-AbwdzRCD-HCmeCn-CD), succeeded**
- As of the 21:43Z sweep and the live read (~21:50Z): running=True, no further run.

So the real pattern is one-successful-fire-per-restart: each restart fires once
~an hour (or ~1 min for the 13:30 one) after start, then the malformed trigger
errors on every subsequent poll (poll errors create no jobs and never set fails=>
fails=0 is meaningless for this failure class), until either the ~60-consecutive-
error auto-stop (~4h at ~4min polls) or another restart. Sweep 20:43Z picked up
last_run=13:29:56 (PT) after restart #2.

### Timezone correction to the 8.2h-stale premise

The sweep's `last_run` field is workspace-LOCAL (PT), not Z. 13:29:56 PT = 20:29:56Z —
the 13:30:22 PT job. At the 21:43:48Z sweep the real gap was ~1h14m, not 8.2h. The
"8.2h stale" reading is a sweep-schema artifact (naive local timestamp labeled Z).
The staleness CONCERN is still valid but lives in the 5.5h dead gap (08:01→13:30 PT)
and the one-fire-per-restart pattern — not in the last-sweep arithmetic.

Sweep trail 2026-10-13 (id 82964017): 10:38Z–14:40Z stopped (trigger_errors_limit);
15:40Z ok last_run=08:00:28; …19:42Z same; 20:43Z + 21:43Z ok last_run=13:29:56.

Who restarted it: no API exposes start events and no build-ledger/bus row was found
for today's restarts — restart actor/time UNVERIFIED (inferred from first-fire + sweep
transitions). Nothing shows a picklist repair happened, and updated_at proves no push.

## (3) What BSYS-29560's AC requires for cadence (cached state only — no Jira posts)

From cached Jira state quoted in cortex/investigations/82964017-trigger-autopsy.md and
gws-mutation-chain-canary-82964017.md (ticket last seen 2026-10-12T23:48Z, Backlog,
unassigned):

- AC: "24h of continuous hourly runs: receipt pairs present, zero residue" + the alert
  path live-fired once.
- Design intent: hourly clock, zero-residue 4-chain mutation drill (prepare → claim →
  commit → cleanup), posts to #gw-semantic-alerts (C0C6S3VT4KF) only on failure or
  recovery (resolve-on-recovery).

Measured against that AC: cadence is broken — 2 runs in the last ~24h (08:01, 13:30 PT)
vs the 24 required, with a 5.5h silent gap. The AC clock (24h continuous) effectively
restarted at 13:30 PT Oct 13 and will break again on the next ~60-error auto-stop
unless Fix A (trigger picklist repair per the autopsy) is applied first.

## Recommendation (PROPOSAL ONLY — nothing executed)

Restarting without repairing does not satisfy BSYS-29560 and burns manual restarts
against a ~4h auto-stop clock. Fix A from the autopsy remains the gating item: re-set
the time_unit picklist with the lowercase option ID, align/clear
dynamicPickListSelection and trigger_at, push, start, then verify ONE scheduler-fired
job (clock output not on_demand) green and running=True stop_cause=None 2h later.
Then the 24h AC clock can legitimately start.

## What was NOT verified

- Who/what performed today's two restarts (no start-event API; no ledger/bus rows found).
- The exact trigger-error strings and per-poll cadence (no public endpoint; not UI-scoped).
- Whether restart #2 will reach the 60-error auto-stop ~4h after 13:30 PT (~17:30 PT /
  00:30Z Oct 14) — predicted from the documented limit, not observed.
- Live Jira state for BSYS-29560 beyond the 2026-10-12T23:48Z cached snapshot (per
  read-only/no-post scope).
