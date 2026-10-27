# Investigation: snowflake-object-missing-job-title (cortex, 2026-10-20, READ-ONLY)

- **canon row:** regression-canon/canon.jsonl line 56, slug snowflake-object-missing-job-title, canonized 2026-10-20T08:33:43Z, status open, provisional class `connection-auth`
- **recipe:** [72253404 — [OPS] LF | Check Job Completion | Re-provisioning all apps](https://app.workato.com/recipes/72253404) (recipe function)
- **canonized job:** j-Ab6WfCtx-LfmAdm-CD (failed 2026-07-30T20:21:10-07:00)
- **prior art:** regression-canon/snowflake-object-missing-job-title.md (has an autopsy-refinement section) + estate-reviews/ops-listener-72253397-autopsy-2026-10-20.md (full parent-listener autopsy)

## Environment correction (matters for future investigators)

- The task brief and the canon doc header label this job "(dev)" and route via the `josh-us` (DEV, workspace 3535597) profile. **Wrong workspace:** `wt recipes get 72253404 --profile josh-us` returns HTTP 404. The asset is **PROD** (workspace 3535598, "Environment Production (Workato AHQ | AI)"); all reads below used `--profile josh-prod`, GETs only. Canon doc header should read prod, not dev.

## Live state (verified via wt CLI, josh-prod, read-only, 2026-10-20 ~18:00Z)

- Recipe **running: true**, version_no 2, version_comment "BSYS-27648: Update job_title", updated 2026-07-30T20:45:12 (4 min after the last failure).
- `last_job_started_at` 2026-10-20T10:54:35-07:00 (today); recent job list shows succeeded jobs every ~2.5 min through today. (Note: `last_run_at` still shows 2026-07-30 — stale field, do not trust it; `last_job_started_at` is the live signal.)
- Counters: job_succeeded_count 112,236 / job_failed_count 10,814. The failed count exactly equals the autopsy's classified incident total (8,128 Class A bridge + 2,686 Class B JOB_TITLE) — no unaccounted failures.
- **Recurrence check (failed-jobs endpoint, newest first): newest failure = j-Ab6X3GdY @ 2026-07-30T20:41:09 — the final failure of the incident. ZERO failures of any kind after the v2 deploy (2026-07-30T20:45:12). The canonized job j-Ab6WfCtx-LfmAdm-CD (20:21:10) is the 5th-newest failure, inside the incident window. No JOB_TITLE recurrence in ~12 weeks.**

## DSL examination (wt recipes get 72253404 --raw, v2 current code)

- JOB_TITLE is referenced in exactly one place: step 2 `snowflake.run_custom_sql`, as the **output column alias** `E.BUSINESS_TITLE AS JOB_TITLE`. There is **no `JOB_TITLE` table join** anywhere in the current SQL.
- The v1 query (per the 2026-10-20 autopsy; v1 code unrecoverable via versions API) had `LEFT JOIN JOB_TITLE J` against a JOB_TITLE lookup table. The v2 fix re-pointed the query to the `BUSINESS_TITLE` column on EMPLOYEE, eliminating the object dependency.
- Snowflake connection: account_id 16469882 — healthy throughout (step 1 `search_rows` on PUBLIC.EMPLOYEE and all post-fix jobs succeed through the same connection).

## Verdict

- **Refined class: `schema-drift-object-missing` (Snowflake object-level existence/grant break) — definitively NOT `connection-auth`.** Evidence: (a) same connection serves successful queries before, during (other steps), and after the incident; (b) error text is object-scoped ("Object 'JOB_TITLE' does not exist or not authorized"); (c) the shipped fix was a query re-point (BSYS-27648), not a re-auth; (d) sibling recipe 72253403 threw bridge-level errors in the same window, consistent with a Snowflake-side schema/grant change, not a Workato connection fault.
- **Recurrence: NONE.** Zero failures since 2026-07-30T20:41; recipe green and running today at ~2.5-min cadence. The canonized failure class is resolved and has ~12 weeks of negative evidence.
- **Smallest fix proposal:** none for the failure itself (fix shipped and verified). The smallest durable actions are bookkeeping, all currently open: (1) update canon.jsonl line 56 class → `schema-drift-object-missing`, fix the "(dev)" mislabel in the canon doc; (2) per failure-close-gate, the row can move to closed only when the same run authors the regression fixture (scaffold is empty — `--skip-fixture` was used).
- **Triage card warranted: YES — but not for JOB_TITLE.** The live, money-burning defect is the parent listener [72253397](https://app.workato.com/recipes/72253397) poison-row amplifier: step 1 re-selects ALL status="new" rows oldest-first, status cleared only at step 29, so May-2026 poison rows are re-processed every 5 min (~1,500 billed tasks/run; lifetime 77.0M tasks and climbing ~1M/week). Proposed fix package (all PROD-GATED, from the autopsy): staleness guard + per-record error isolation with explicit `error` status + child failure canary. This deserves a BSYS triage card/story if one is not already filed; the JOB_TITLE class itself needs only the canon bookkeeping above.

## Scope note

Read-only throughout: no writes to Workato (dev or prod), no canon/canon.jsonl edits, no fixture changes. The only write was this file.
