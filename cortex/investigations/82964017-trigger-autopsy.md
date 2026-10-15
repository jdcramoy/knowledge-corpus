# TRIGGER AUTOPSY: gw_semantic_mutation_chain_canary (82964017, dev)

Written: 2026-10-13, read-only autopsy (follows cortex/investigations/gws-mutation-chain-canary-82964017.md).
Recipe: https://app.workato.com/recipes/82964017 (folder 35404884, project 17981834)
Governing ticket: BSYS-29560. Last green job: https://app.workato.com/recipes/82964017/job/j-AbwEnLfz-MhBzWJ-CD

## VERDICT: root cause = TRIGGER CONFIG DRIFT from the v12 push (16:39 PT Oct 12). The 13 DatapillInvalidPath inconsistencies are a REAL but SEPARATE defect — runtime-proven innocent of this stop.

Origin: the trigger block itself (step 0). Victim: the whole recipe (zero jobs created
after the upgrade) and downstream the frozen mutation_drill row in
workspace_health_alert_state (156399) that the BSYS-29478 sentinel digest reads.

## Timeline (PT = UTC-7)

- 2026-10-12 07:37 PT — last SCHEDULER-fired job (j-Abw3HHba-WhY6kb-CD), daily-drill era config.
- 2026-10-12 16:39:28 PT — version 12 pushed (BSYS-29560 hourly upgrade: trigger rewritten, chain D steps 24-30 added). Confirmed via `wt api get /api/recipes/82964017` (updated_at, version_no=12, version_author Joshua Cramoy). ZERO build-ledger rows for this push — built outside ledger discipline (per prior investigation).
- 2026-10-12 16:33–17:31 PT — five ON-DEMAND test runs, all succeeded (16:33, 16:35, 16:37, 16:39, 17:31:58 = j-AbwEnLfz-MhBzWJ-CD). The 17:31 job's clock output shows `on_demand: True` and `last_job_time: 2026-10-12T07:37:00` — i.e. the scheduler never successfully fired again after 07:37.
- ~17:35 PT (inferred) — recipe restarted after testing; trigger service begins polling the malformed config and erroring every poll.
- 2026-10-13 03:35:02Z (20:35 PT) — health sweep: running=True, fails=0 (trigger errors never surface as job failures).
- 2026-10-13 04:34:42Z (21:34:42 PT) — Workato auto-stop, stop_cause=trigger_errors_limit (stopped_at from live recipe record). Fits the documented 60-consecutive-trigger-errors rule: ~4h at a ~4 min poll cadence = 60 errors.
- 2026-10-13 04:35:30Z — health sweep flags stopped.

## The smoking gun: malformed clock trigger block (raw recipe code, wt api get)

Current (broken) trigger block on 82964017:

    {"as":"scheduled_event_9d42","keyword":"trigger","provider":"clock","name":"scheduled_event",
     "input":{"time_unit":"Minutes","trigger_every":"60","trigger_at":"00:07"},
     "dynamicPickListSelection":{"time_unit":"Days"},
     "visible_config_fields":["time_unit","trigger_at","trigger_every"]}

Healthy twin — EM | Evaluate Service Health (82966998, running, every 5 min):

    {"as":"scheduled_event_47cd","keyword":"trigger","provider":"clock","name":"scheduled_event",
     "input":{"time_unit":"minutes","trigger_every":"5"},
     "visible_config_fields":["time_unit","trigger_every"]}

Three defects in the canary's block, all pointing the same way:
1. `input.time_unit` = "Minutes" — the picklist LABEL. The stored value must be the option ID, lowercase "minutes" (compare 82966998). Classic AIRO recipe-builder picklist hazard: set_input_field with raw text instead of the picklist option ID.
2. `dynamicPickListSelection.time_unit` = "Days" — stale leftover from the daily-drill era, contradicting the input. A picklist set correctly through the builder updates both; they can never legitimately disagree (daily sibling 82963931: input "days" + selection "Days" agree).
3. `trigger_at: "00:07"` — a field that does not exist for the Minutes unit in the healthy config (visible_config_fields there is only [time_unit, trigger_every]); orphaned from the old daily schedule shape.

At trigger-poll time the platform evaluates this Franken-config (label-instead-of-value
unit, Days selection vs Minutes input, orphaned trigger_at) and raises — every poll,
~60 consecutive errors, auto-stop. Corroboration that this is recipe-local, not
platform: every other clock recipe in the estate (EM 5-min sweepers 82966988/82966998,
hourly sentinel 82951201, daily 82963931) ran clean through the same window.

Docs anchor: RecipeOps "Recipe stopped by Workato" — Workato stops a recipe after 60
consecutive trigger errors (https://docs.workato.com/connectors/recipeops/triggers/recipe-stopped-by-workato.html).

## Why the DatapillInvalidPath lead is NOT the stop cause (but still a defect)

All 13 inconsistencies sit on chain D (steps 26-32), referencing stale output-schema
snapshots on steps 25/27/30 (internal names compile_reviewed_operation_abe5,
prepare_confirmable_mutation_15ed, commit_confirmed_mutation_0071 — recreated-step
signatures). Runtime proof of innocence: the last green job (17:31 PT) executed chain D
end-to-end with those exact pills:

- line 25 (step 26 gate): `{'condition': True}` — pill `compile_reviewed_operation_25['compiler_status']` resolved to READY.
- line 26 (step 27 prepare): `{'success': True, 'status': 'MUTATION_PLAN_PREPARED', 'capability_id': 'drive.files.delete@v3', ...}` — real output through the "invalid" pills.
- line 29 (step 30 commit): `{'success': True, 'status': 'MUTATION_COMMITTED', ...}` — sandbox deck deleted, zero-residue.
- line 31 (step 32 verdict): `drill_ok='true', detail='checked=2026-10-13|ok=yes|...|deck_deleted=yes'`.

So the pills resolve correctly at runtime; the inconsistency is a design-time
schema-cache artifact. It is still a real second defect: (a) start-time validation can
reject recipes with broken mappings — this recipe family already returned config_errors
on start on 2026-10-11T05:54Z (build-ledger row, BSYS-29502 session); (b) any future
schema edit on steps 25/27/30 can silently sever these mappings.

## Classification

Primary: **config drift** — trigger config malformed by the v12 AIRO push
(picklist label-vs-value + stale dynamicPickListSelection + orphaned field).
Secondary (co-traveling, not causal here): **datapill schema-snapshot drift** on steps 26-32.

## PROPOSED fix-forward — PROPOSAL ONLY, nothing executed

Fix class: **root-fix** on both items. NO containment (no error-monitor wrappers —
this is a canary; masking its failures corrupts the exact signal it exists to produce,
per BSYS-29582 doctrine). The canary's own resolve-on-recovery design posts RESOLVED to
#gw-semantic-alerts on the first green scheduled run — free all-clear signal.

### Fix A — repair the trigger (the stop cause)

Design intent per description: hourly at :07. Recommended semantics: **Hours unit,
every 1 hour, at :07 past** (Minutes/60 anchors to start time, not clock-:07; Hours is
the unit that owns trigger_at).

1. `recipe_builder_pull(82964017)`.
2. `recipe_builder_get_picklist(step=1, field_path="time_unit")` — capture the option IDs (expect lowercase values: "minutes"/"hours"/"days").
3. `recipe_builder_set_input_field(step=1, ...)` with the picklist OPTION ID for hours (`value: "hours"`), `trigger_every: "1"`, `trigger_at: "00:07"`.
4. `recipe_builder_push`.
5. Verify via `wt api get /api/recipes/82964017` raw code: `input.time_unit` is the lowercase option ID AND equals `dynamicPickListSelection.time_unit`; no fields outside the unit's visible_config_fields. The DSL export does NOT surface this — check raw code or it didn't happen.
6. `wt recipes start 82964017` — assert `success: true` AND `config_errors` empty (this family failed start validation before; the response carries it).

### Fix B — refresh the stale chain-D schemas (the 13 inconsistencies)

1. Same pulled session: `recipe_builder_update_step` on steps 25, 27, 30 with the SAME connector + action (forces output-schema re-resolution).
2. `recipe_get` must then show zero DatapillInvalidPath. If the builder's schema cache refuses to refresh (known AIRO staleness), fallback: remove and re-add steps 25-30 with identical config and rewire the pills.
3. Re-verify pill mappings after any set_input_field touch (known silent-replacement hazard).

### Verification criterion (the exact line a fixed job must show)

The next :07-boundary SCHEDULER-fired job (clock output must NOT say `on_demand: True`)
completes succeeded with line 31 `drill_ok='true'...deck_deleted=yes`; `wt api get`
shows running=True, stop_cause=None two hours post-start; a RESOLVED post lands in
#gw-semantic-alerts (C0C6S3VT4KF) because the frozen mutation_drill row predates the stop.

### The test that would have caught it

- Build-time (fixture for the canon): post-push assertion on raw recipe code —
  `input.time_unit == dynamicPickListSelection.time_unit`, value is lowercase option ID,
  no config fields outside the unit's visible set. Catches label-vs-value and stale
  selection at push time, before any poll errors.
- Runtime (already half-built): the fleet liveness sentinel (82951201) corroborates
  staleness with stop_cause=trigger_errors_limit — the gap was paging latency, not
  detection. A "first scheduled fire within 2x interval after any start" assertion
  closes it for scheduler recipes specifically.

## What was NOT verified

- The exact trigger-error strings: no public API exposes them (`/api/recipes/:id/trigger_errors` = 404); the UI trigger-errors tab was not opened (read-only scope, browser not warranted for a proposal).
- The precise per-poll cadence and the exact restart timestamp (~17:35 PT is inferred from stopped_at minus 60-error window; not directly observed).
- That re-setting the picklist via AIRO actually repairs dynamicPickListSelection — that is Fix A step 5's verification, not yet executed (read-only dispatch).
- The frozen mutation_drill row in table 156399 from this session (data_table_query 404'd on that ID here); staleness is carried from the prior investigation, which confirmed it.
- Canon fixture not yet filed: canonize-failure.py wants a failed job ID and this failure class produced none (trigger-level, zero failed jobs). Canon entry to be filed as a signature entry (stop_cause=trigger_errors_limit + picklist/selection mismatch) alongside the fix.
