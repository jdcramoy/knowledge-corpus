# BSYS-29383 — Material-findings closure evidence (MATERIAL-1, MATERIAL-2)

**Context:** dispatched 2026-10-22/23 from a /triage session (Josh approved Build-now) to close the two
MATERIAL findings behind the FAIL verdict in
`~/.claude/knowledge/redteam/BSYS-29383-build-recipes-table-code-strip.md` (2026-10-18 02:14).
Asset under review: PROD twin 3792740 "Build recipes table", change staged on DEV twin
[recipe 3383902](https://app.workato.com/recipes/3383902). This session did NOT edit the verdict file
and did NOT dispatch the re-review; the parent session sequences that.

A prior build session appended its own "closure evidence" to the verdict file on 2026-10-18 (count
probe = 3,944 rows still holding CODE, probe recipe 83152838 — now deleted/404). Per the
verify-don't-assume rule this session re-derived the evidence independently. The prior controlled-probe
recipe 83290933 was re-inspected and found **broken** (its upsert step ran with `rows_affected: 0` —
the update branch never fired, so it proved nothing); the count evidence was re-confirmed live and then
superseded by the query-history evidence below, which is stronger than either prior artifact.

---

## MATERIAL-1 — Does the upsert update branch overwrite unmapped CODE / CLEAN_CODE with NULL?

**Question:** step 21 of the twin upserts to `DEPLOYMENT.RECIPES` keyed `ID + WORKSPACE_USER_ID`,
mapping only `folder_id, id, name, description, workspace_user_id, workato_api_connection_name`
(CODE/CLEAN_CODE remain `optional: true` in the connector schema, unmapped). If the connector's update
branch writes the full row, the first full prod run silently erases the historical CODE column across
the shared table.

### Method + evidence

**(a) Workato KB (docs)** — read in full:
https://docs.workato.com/en/connectors/snowflake/upsert.md — confirms the doc states NOTHING about
column preservation on the update branch (the verdict's reading was correct; the doc is silent). The
same doc lists the single-row upsert, batch upsert, and the "Run custom SQL" action. No other docs
page visited states upsert update-branch column semantics.

**(b) Live probes (dev Snowflake, bt-dev profile, no prod data touched):**

1. **Re-confirmed the at-scale natural experiment** — dev-twin count query re-run inside throwaway
   probe recipe 83290933, job `j-Ac6PJbsN-onLWrG-CD` (succeeded, 2026-10-22 15:26 PT):
   `code_rows = 21381` of `total_rows = 23965`; dev partition (`workspace_user_id = 800219`)
   `dev_code_rows = 3944`. The dev twin's code-free rebuild (2026-10-15 23:51-23:57 PT,
   job `j-Abxw4fn9-cktKQo-CD`, succeeded) re-upserted the full 5,379-row inventory without CODE
   mapped; 8 days later thousands of rows in that same partition still hold non-NULL CODE. If the
   update branch nulled unmapped columns, that count would be 0.

2. **DECISIVE — the connector's actual SQL, from Snowflake QUERY_HISTORY.** Throwaway probe recipe
   83296330 (deleted after run), job `j-Ac6Y9ddD-saPL9A-CD` (succeeded), read
   `snowflake.account_usage.query_history` for `query_type = 'MERGE'` against the shared table:

   - **Post-change MERGE (2026-10-22 20:25:38-20:26:09 PT, four batches):**
     ```sql
     MERGE INTO "DEPLOYMENT"."RECIPES" T
     USING (SELECT Column1 AS "FOLDER_ID", Column2 AS "ID", Column3 AS "NAME",
            Column4 AS "WORKSPACE_USER_ID", Column5 AS "WORKATO_API_CONNECTION_NAME",
            Column6 AS "DESCRIPTION" FROM VALUES (?,?,?,?,?,?),(?,?,?,?,?,?), ...)
     ON (T."ID" = S."ID" AND T."WORKSPACE_USER_ID" = S."WORKSPACE_USER_ID")
     WHEN MATCHED THEN UPDATE SET
        T."FOLDER_ID"=S."FOLDER_ID", T."NAME"=S."NAME",
        T."WORKATO_API_CONNECTION_NAME"=S."WORKATO_API_CONNECTION_NAME",
        T."DESCRIPTION"=S."DESCRIPTION"
     WHEN NOT MATCHED THEN INSERT ("FOLDER_ID","ID","NAME","WORKSPACE_USER_ID",
        "WORKATO_API_CONNECTION_NAME","DESCRIPTION") VALUES (...)
     ```
     The UPDATE SET and the INSERT column list contain **only the mapped columns. CODE and
     CLEAN_CODE are not referenced anywhere.** Unmapped optional columns cannot be overwritten.

   - **Pre-change MERGE (2026-10-14 20:35 PT, before the rebuild) — corroborates the diff's intent:**
     the old mapping carried `Column7 AS "CODE"` with literal `NULL` bind values
     (`(?,?,?,?,?,NULL,?)` per row) — i.e. the OLD recipe wrote NULL CODE through the 16MB-byte-guard
     formula. That is exactly the behavior the change removes.

**Verdict: CLOSED — refuted.** Workato's Snowflake `upsert_rows_batch` emits a MERGE whose
`WHEN MATCHED THEN UPDATE SET` covers only the mapped columns; unmapped optional columns
(CODE/CLEAN_CODE) are left untouched. Existing rows keep CODE; new rows get NULL. The erase-history
scenario cannot occur. Remediation required: none. (Optional, separate ticket: Workato's upsert doc
should state column-preservation semantics — the doc gap is what made this finding possible.)

**Probe-path note (honest trail):** the controlled insert-then-upsert-then-read-back probe was also
attempted 4 times via API-authored recipes (83296201/83296265/83296267/83296270, all deleted) and once
via AIRO + once via the Orca browser UI; the browser path was blocked by repeated session-expiry
collisions with a concurrent session also using the browser. The SQL renders fine from the API but the
upsert step's `rows` pill mapping does not render from CLI-authored DSL (silently dropped at render
time — `rows_affected: 0` or "'Rows' must be present"). The query-history evidence supersedes it and is
stronger anyway: it is the connector's real emitted SQL against the real shared table.

---

## MATERIAL-2 — Prod caller behavior during the stop→PUT→start redeploy window

**Question:** when 3792740 is stopped for redeploy, what do prod callers 3792734 / 3792724 do? Can the
window strand in-flight work?

### Method + evidence (READ-ONLY; no stops, starts, edits, or prod writes)

Pulled both recipes' full DSL via `WORKATO_PROFILE=bt-prod wt api GET /api/recipes/<id>` plus recent
job traces, and (for completeness) the actual hot caller 3792742 identified in the verdict.

- **[3792734](https://app.workato.com/recipes/3792734) "[DEPLOY] LF | Get Recipe Folder Path"** —
  running; 8,547 ok / 501 failed lifetime; ran today (2026-10-22). Shape: recipe-function trigger →
  Snowflake select → `call_recipe_async` to 3792739 (Build folders table) → `call_recipe_async` to
  3792740 (Build recipes table) → `wait_for_async_jobs` (timeout 120s). **No error_handling or
  monitor block anywhere in the DSL** (zero matches).
- **[3792724](https://app.workato.com/recipes/3792724) "[DEPLOY] LF | Download Change Set from Dev and
  Deploy to Prod"** — running; 1,116 ok / 606 failed lifetime; last ran 2026-10-19. Does NOT call
  3792740 directly — it calls "Get Async Package Retrieve Status and Zip", "Deploy Change Set to
  Production", and async "Parse Zip and Commit Changes to Repository" (indirect deploy-chain ancestor).
  **No error handling anywhere in the DSL.**
- **[3792742](https://app.workato.com/recipes/3792742) "[DEPLOY] LF | Run deployment setup workflow"**
  (the hot caller, 15-60s cadence during active periods, 212,457 jobs / 34,367 failed ≈ 16%):
  3 async calls (Build folders / Build connections / **Build recipes table**) + wait 120s. **No error
  handling.**
- **Live failure trace (today):** 3792734 job `j-Ac6NaCEG-ocGRb3-CD` (2026-10-22 14:40:16 PT, failed) —
  a downstream function-call error propagated and failed the caller job outright; the recipe has no
  construct to contain it. 3792724 job `j-Ac3hKsta-bCnHoR-CD` (2026-10-19 10:25) failed the same way.

**Verdict: CLOSED — behavior characterized; mitigation sufficient.**
- A stop during the window makes every caller invocation that lands in the window **fail the caller
  job outright** (no retry, no queuing, no containment — callers have zero error handling).
- Work is **lost, not stranded**: nothing blocks or piles up; the next 3792742 invocation (15-60s
  later) re-runs the full fan-out, and the upserts are key-idempotent (`ID + WORKSPACE_USER_ID`), so a
  short window costs only noisy failed jobs and a skipped build cycle.
- The one real risk is a stop overlapping a long-running deploy-chain invocation (3792724 family,
  cadence ~daily at most) — that chain does not self-retry and would need a manual re-run: the
  verdict's "accept one bumpy cycle" framing, confirmed.
- The verdict's existing remediation stands and is sufficient for PASS-WITH-NOTES: (a) confirm quiet
  window (no caller activity ~10 min) before stop, (b) re-GET `running: true` after start and prove
  with one real call, (c) accept transient failed jobs in the window. **Optional hardening (separate
  ticket, not promotion-blocking):** wrap the callers' `call_recipe_async`/`wait_for_async_jobs` in
  error monitor + retry, and/or gate the hot loop on a deploy-in-progress flag.

---

## Recommended red-team verdict

**PASS-WITH-NOTES** — MATERIAL-1 refuted with connector-emitted SQL; MATERIAL-2 characterized with
live traces; cosmetic items (step-16 SQL interpolation, logic-abuse surface) remain as hardening
candidates. The parent session should request the re-review.

## Not verified / caveats

- The controlled (populate → upsert-unmapped → read-back) probe never executed end-to-end; blocked by
  the API-render limitation plus browser session collisions. Compensated by the MERGE-SQL evidence,
  which is strictly stronger for this question.
- ACCOUNT_USAGE.QUERY_HISTORY has up to ~3h latency; the "post-change" MERGEs are from 2026-10-22
  20:25-20:26 PT. The 10-15 dev rebuild's own MERGE text was not sampled (pre-10-16 rows were, at
  20:35 on 10-14, matching the old mapping).
- Did not grep all 23 deploy-family recipes' DSL for hidden CODE consumers (unchanged scope from the
  original review's noted blind spot).
- Left in place (other sessions' assets, both stopped): probe recipes
  [83290933](https://app.workato.com/recipes/83290933) (broken upsert step) and 83296438 (concurrent
  session's cleanup probe) in folder 1604941. All nine probes created by this session were stopped,
  deleted, and verified 404; the leftover `bsys29383_upsert_probe` Snowflake scratch table was dropped
  (cleanup job `j-Ac6YKFLG-9Pforw-CD` succeeded).
- Post-review pushes on either twin void the original verdict per its own terms.

## Tooling lessons (deposited)

- `wt api PUT /api/recipes/:id` reports `success: true` but **silently ignores the `code` field**
  (canary-verified). The wt-cookbook "Update recipe" entry is wrong for code changes — only
  name/description/folder update. Corrections appended to wt-cookbook SKILL.md.
- API-authored recipes (POST with code) render most steps fine, but a batch upsert's `rows` list
  mapping (____source + item pills) does not render at runtime unless the step carries the platform's
  generated `extended_input_schema` (and even then the pill binding did not resolve). Recipe-logic
  changes go through AIRO builder or the UI canvas, per the standing tooling preference.
- Workato data-tree datapills are drag-only (click does not insert); HTML5 DnD and synthetic pointer
  drags both fail against the custom drag lib. With a concurrent actor holding browser focus,
  real-input paths are unsafe — session-expiry collisions (one-workspace-per-cookie) lose all unsaved
  editor state.
