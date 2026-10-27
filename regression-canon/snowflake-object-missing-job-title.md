# Failure canon: snowflake-object-missing-job-title

- **recipe:** [72253404](https://app.workato.com/recipes/72253404) — **PROD** (workspace 3535598, "Environment Production (Workato AHQ | AI)"). Do NOT route via the dev `josh-us` profile: `wt recipes get 72253404 --profile josh-us` returns 404; read-only via `--profile josh-prod`.
- **job:** j-Ab6WfCtx-LfmAdm-CD (prod, failed 2026-07-30T20:21:10-07:00, inside the incident window)
- **canonized:** 2026-10-20T08:33:43Z
- **failure class (refined 2026-10-22):** schema-drift-object-missing (was provisional connection-auth — see Autopsy refinement below)
- **error signature:** `fail-database-bridge-error-sql-compilation-error-object`
- **status:** tested (closed 2026-10-22; fixture authored, execution prod-gated)

## Error signature

`fail-database-bridge-error-sql-compilation-error-object` — Database bridge error: SQL compilation error:
Object 'JOB_TITLE' does not exist or not authorized.
(error_type: Database adapter error)

## Trace map (trace-derived; autopsy names the true origin)

- **origin candidate:** line 2 (snowflake/run_custom_sql) — first step with an error record
- **victim step:** line 2 (snowflake/run_custom_sql) — last step with an error record (where the job died)
- **top-level error:** Recipe function by Workato: new call for function: Calling job ID=j-Ab6Wew8G-H9YXNh-CD, Calling recipe ID=72253397, and Email=kristine.im@workato.com

## Classification

REFINED 2026-10-22: **schema-drift-object-missing** (Snowflake object-level
existence/grant break). Definitively NOT connection-auth: (a) the same
connection 16469882 served successful queries before, during (other steps),
and after the incident; (b) the error text is object-scoped ("Object
'JOB_TITLE' does not exist or not authorized"); (c) the shipped v2 fix
(BSYS-27648 "Update job_title") was a query re-point to `E.BUSINESS_TITLE`,
not a re-auth; (d) sibling recipe 72253403 threw bridge-level errors in the
same window — a Snowflake-side schema/grant change, not a Workato connection
fault. Zero failures of any kind since 2026-07-30T20:41 (~12 weeks of negative
evidence; live probe 2026-10-19/20: running:true at ~2.5-min cadence).

## Fixture status

AUTHORED 2026-10-22: `fixtures/prod-72253404-schema-drift.json` — documents
the class-reproduction test for schema-drift-object-missing. `expect` is
deliberately EMPTY and the fixture is PROD-GATED: the recipe lives in
Production (workspace 3535598), so filling expect would make
regression-nightly's fixture phase run `wt fixture run` against a prod recipe
every night. Execution needs Josh's explicit prod-test go.

Class-reproduction test definition (what the fixture encodes):
- GIVEN a Snowflake connection (same type as 16469882) whose target schema has
  NO object named by the query
- WHEN the recipe runs `run_custom_sql` referencing the missing object (the
  v1 form: `LEFT JOIN JOB_TITLE J`)
- THEN the step fails with `Database bridge error: SQL compilation error:
  Object '<NAME>' does not exist or not authorized` (error_type: Database
  adapter error) — and the failure classifies schema-drift-object-missing,
  NOT connection-auth, provided the same connection also serves a successful
  trivial query in an adjacent step (the auth-health discriminator).

## Canon entry

appended to ~/.claude/knowledge/regression-canon/canon.jsonl (signature fail-database-bridge-error-sql-compilation-error-object)

## Close-out

1. workato-autopsy on [j-Ab6WfCtx-LfmAdm-CD](https://app.workato.com/recipes/72253404) — DONE 2026-10-20 (see refinement below).
2. Fixture authored 2026-10-22 (`fixtures/prod-72253404-schema-drift.json`) — class-reproduction definition recorded; execution is prod-gated (Josh's go).
3. Fix: shipped 2026-07-30 (v2 BSYS-27648 query re-point); proven by zero failures since 2026-07-30T20:41, live-verified 2026-10-19/20.
4. Canon entry closed to `tested` 2026-10-22 via close_gate (evidence: fixture authored + 12-week zero-recurrence probe).

## Autopsy refinement (workato-autopsy, 2026-10-20 — read-only PROD engagement)

- Recipe under autopsy: parent listener 72253397 (prod); victim step line 10 call_recipe -> child FUNC 72253404; ORIGIN = child step 2 `snowflake.run_custom_sql` (LEFT JOIN JOB_TITLE).
- Class refinement: NOT connection-auth — connection 16469882 auth was healthy throughout; this is an OBJECT-LEVEL existence/grant break (`Object 'JOB_TITLE' does not exist or not authorized`). Class A (8,128 child fast-fails with unserializable `{}` errors, Jun 23–Jul 21) is the same Snowflake/bridge incident one error-mode earlier (sibling 72253403 trace j-Ab3XP83n-KkYahr-CD proves bridge-level `Can't set TIMEZONE = UTC` in the same window).
- Closure: child v2 "BSYS-27648: Update job_title" authored 2026-07-30 20:45:12, four minutes after the last failure. Zero SQL-object failures since.
- Amplifier (the live residual defect): parent step 1 re-selects ALL status="new" rows oldest-first; status only cleared at step 29. Poison rows from May 2026 are re-processed to this day (~1,500 billed tasks/run, 288 runs/day). Proposed fix: staleness guard + per-record error isolation with explicit `error` status (never silent), + child failure canary. Full report: estate-reviews/ops-listener-72253397-autopsy-2026-10-20.md. All remediation is PROD-GATED.
