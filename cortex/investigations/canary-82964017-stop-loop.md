# INVESTIGATION: canary 82964017 stop loop — why restart does not hold

Written: 2026-10-15 (read-only investigation; nothing changed). Builds on prior autopsies:
`cortex/investigations/gws-mutation-chain-canary-82964017.md` (2026-10-13) and
`cortex/investigations/82964017-trigger-autopsy.md` (2026-10-13). All claims below are
backed by live reads or cited bus records; live reads re-verified this session.

Recipe: https://app.workato.com/recipes/82964017 (dev, folder 35404884, project 17981834)
Governing ticket: BSYS-29560 — https://workato.atlassian.net/browse/BSYS-29560
(Backlog, unassigned, as of this writing)

## What the canary does

`gw_semantic_mutation_chain_canary` is the hourly mutation-invariant canary for the
GW Semantic / Otto gateway (BSYS-29560, upgraded from the BSYS-29504 daily drill).
Once per hour at :07 it exercises the FULL two-phase mutation gate — compile, prepare,
persist-plan (recipe 82284937), claim (82285042), commit — four times against a sandbox
Google Slides deck: create deck, create slide, undo slide, delete deck
(`drive.files.delete@v3`, always-confirm challenge). It asserts provider receipt bodies
on all four commits and a zero-residue check, and writes a drill row into data table
`workspace_health_alert_state` (156399) that the BSYS-29478 sentinel digest reads. It
posts to #gw-semantic-alerts (C0C6S3VT4KF) only on failure or recovery — so when the
canary is DOWN, it is silent by design (cortex: "the canary that exists to catch silent
failures is itself silent"). Its job is to catch a silent regression in the mutation
gate within the hour; while stopped, the estate is blind on that invariant.

## Timeline of stops (PT = UTC-7)

- 2026-10-12 07:37 PT — last healthy scheduler-fired job (j-Abw3HHba-WhY6kb-CD), daily-drill era.
- 2026-10-12 16:39:28 PT — version 12 pushed (hourly upgrade; trigger rewritten, chain-D
  steps 24-30 added). Zero build-ledger rows. Confirmed via live `wt api get`: updated_at
  and version_no=12 unchanged to this day.
- 2026-10-12 16:33-17:31 PT — five on-demand test runs, all green. The 17:31 job's clock
  output already shows the scheduler never fired successfully again (`on_demand: True`,
  `last_job_time: 2026-10-12T07:37`).
- 2026-10-12 ~17:35 PT — recipe restarted after testing; trigger service begins polling
  the malformed config and erroring on poll. Trigger errors never surface as job failures.
- 2026-10-12 21:34:42 PT — STOP #1: Workato auto-stop, stop_cause=trigger_errors_limit
  (60 consecutive trigger errors, ~4h at ~4min poll cadence). Sentinel 82964161 fired on
  this stop (bus, cortex 2026-10-13T02:55).
- 2026-10-13 01:52-06:08Z — cortex verdicts: DEFECT (not a go-live pause), then autopsy
  verdict "trigger config drift" with fix-forward proposal; dev gate = Josh
  (bus threads recipe-health-82964017-stopped, gws-mutation-chain-canary).
- 2026-10-13 21:48Z (14:48 PT) — RESTARTED (bus: canary-82964017-restarted). Restart-only:
  live record still shows updated_at = Oct 12 16:39 PT, version_no = 12. No config change.
- 2026-10-14 01:45Z — health sweep flags stopped again; watchdog 03:47Z notes it
  "self-resolved" (implies a second quick restart; 12 succ / 0 fail, Running at 03:47Z).
- 2026-10-13 19:33 PT, 2026-10-14 00:20 + 00:45 PT — three green Scheduler-by-Workato
  jobs post-restart, but at erratic non-:07 times with `on_demand: true` in the clock
  output (j-AbwmnP4K, j-AbwsNdfB, j-AbwsnCR9 — verified via job reads this session).
- 2026-10-14 05:36:25 PT (12:36Z) — STOP #2: live `wt api get /api/recipes/82964017`:
  running=False, stop_cause=trigger_errors_limit, stopped_at=2026-10-14T05:36:25-07:00.
  Same stop cause as Stop #1.
- 2026-10-14 13:23Z / 17:33Z — cortex live recipe_get re-confirms genuinely stopped;
  escalation card filed ~17:05Z (registry gw-semantic-mutation-chain-canary-escalation).
- 2026-10-14 19:04Z onward — workato-health sweep-mutes the flag as owned/pending;
  escalations at 5h, 7h, 9h, 19h, 21h pending-decision age. Attention-queue row #4:
  "restart-only proven not to hold."
- 2026-10-16 00:09Z sweep — still stopped (~42.5h and counting).

## Root-cause hypothesis (CONFIRMED, evidence-cited)

**Trigger config drift from the v12 push; every stop is the platform's 60-consecutive-
trigger-errors auto-stop re-tripping on the same malformed trigger block.**

Live trigger block on 82964017 (raw code, re-read this session, byte-identical to the
Oct-13 autopsy finding):

    input: {"time_unit":"Minutes","trigger_every":"60","trigger_at":"00:07"}
    dynamicPickListSelection: {"time_unit":"Days"}
    visible_config_fields: ["time_unit","trigger_at","trigger_every"]

Three defects, all from the same cause (picklist set by label, not option ID):

1. `input.time_unit` = "Minutes" — the picklist LABEL. Stored value must be the option
   ID, lowercase "minutes". Healthy twin 82966998 (EM 5-min, running) stores "minutes".
   Classic AIRO recipe-builder picklist hazard: set_input_field with raw text.
2. `dynamicPickListSelection.time_unit` = "Days" — stale daily-drill-era leftover
   contradicting the input. Correctly set picklists can never disagree (daily sibling
   82963931: input "days" + selection "Days" agree).
3. `trigger_at: "00:07"` — orphaned field; does not exist for the Minutes unit (healthy
   twin's visible_config_fields = [time_unit, trigger_every] only).

Evidence refs:
- cortex bus 2026-10-13T05:04 recipe-health-82964017-stopped
  ("canary-82964017-autopsy-verdict-trigger-config-drift", confidence high).
- cortex bus 2026-10-13T06:08 gws-mutation-chain-canary ("canary-82964017-root-cause").
- `~/.claude/knowledge/cortex/investigations/82964017-trigger-autopsy.md` (full walk).
- Live reads this session: stop_cause=trigger_errors_limit on BOTH stops; trigger block
  unchanged; updated_at/version still the v12 push.
- Recipe-local corroboration: every other clock recipe in the estate (82966988/82966998
  5-min EM sweepers, 82951201 hourly sentinel, 82963931 daily) ran clean through both
  windows — this is not a platform incident.
- Docs anchor: RecipeOps "Recipe stopped by Workato" — 60 consecutive trigger errors:
  https://docs.workato.com/connectors/recipeops/triggers/recipe-stopped-by-workato.html

Co-traveling but NOT the stop cause: 13-14 static DatapillInvalidPath inconsistencies on
chain-D steps 26-32 (stale output-schema snapshots on steps 25/27/30). Runtime-proven
innocent: the last green jobs executed chain D end-to-end through those exact pills
(compile READY, MUTATION_PLAN_PREPARED, MUTATION_COMMITTED, deck_deleted=yes). Still a
real second defect (start-time validation can reject it; this family returned
config_errors on start once before, 2026-10-11T05:54Z) — watchdog holds it as P2-watch
(bus 82964017-static-dsl-datapill-drift, 2026-10-14T03:30/03:47).

## Why restart does not hold

The defect lives in the PERSISTED recipe config (step 0 trigger block), not in runtime
state. A restart changes nothing the trigger service reads: polling resumes against the
same malformed Franken-config (label-instead-of-ID unit, contradictory Days selection,
orphaned trigger_at), every poll raises, the consecutive-error counter climbs, and
Workato auto-stops the recipe again. Proof the fix was never applied: updated_at is
still 2026-10-12T16:39 PT and version_no is still 12 on the live record — every restart
since Oct 13 has been restart-only. Two independent stops with the IDENTICAL
stop_cause (trigger_errors_limit) confirm the re-trip, not a new failure mode.

The green jobs after the Oct-13 21:48Z restart are not evidence of a healthy trigger:
they are erratic catch-up-style scheduler events (00:20 and 00:45 PT are 25 minutes
apart, not hourly :07; clock output `on_demand: true`). Successful event deliveries
appear to intermittently reset the consecutive-error counter — which explains why the
second life lasted ~15h instead of ~4h — but they only change HOW LONG the recipe
survives, not WHETHER it stops. Stop #2 landed at 05:36 PT Oct 14 regardless.

Blindness amplifier: the canary posts to #gw-semantic-alerts only on drill
failure/recovery, so a STOPPED canary posts nothing. Detection currently depends on the
hourly workato-health sweep flagging `stopped`, which is now muted pending the Josh
decision — the estate is effectively unmonitored on the mutation invariant until the
fix lands.

## Recommended fix owner

**Josh (dev gate) — fix-forward per the standing autopsy proposal; restart-only is off
the table.** The exact fix is already written up in
`~/.claude/knowledge/cortex/investigations/82964017-trigger-autopsy.md` ("PROPOSED
fix-forward", Fix A + Fix B) and gated on Josh since 2026-10-13. In short:

1. Fix A (the stop cause): pull 82964017, re-set the trigger through the builder with
   picklist OPTION IDs — design intent is hourly at :07, so unit "hours",
   trigger_every 1, trigger_at 00:07 — push, then verify the RAW code (input.time_unit
   lowercase option ID, dynamicPickListSelection in agreement, no orphaned fields; the
   DSL export does not surface this), then start and assert config_errors is empty.
2. Fix B (the co-traveling defect): refresh chain-D output schemas on steps 25/27/30
   (update_step same connector+action, or remove/re-add if the schema cache refuses),
   re-verifying pill mappings afterward.
3. Done-criterion: the next SCHEDULER-fired :07 job (clock output must NOT say
   on_demand: True) completes with drill_ok='true' / deck_deleted=yes; running=True and
   stop_cause=None two hours post-start; a RESOLVED post lands in #gw-semantic-alerts.

Open decision parked with Josh (attention-queue row #4, escalation registry
gw-semantic-mutation-chain-canary-escalation): platform-team escalation vs adding a
schedule-freshness guard ("first scheduled fire within 2x interval after any start").
Build-time guardrail proposed for the canon: post-push assertion on raw recipe code
that time_unit is the lowercase option ID and matches dynamicPickListSelection.

Not verified in this session: the exact consecutive-error counter reset semantics
(whether successful event deliveries reset it) — inferred from the two different
time-to-stop values; does not change the root cause or the fix. Nothing else
unverified; no writes of any kind were made to Workato, Jira, or Slack.
