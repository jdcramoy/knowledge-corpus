# BSYS-29383 — MATERIAL-1 / MATERIAL-2 closure investigation (2026-10-22)

Purpose: independently re-verify the two MATERIAL findings from the red-team FAIL verdict
(`~/.claude/knowledge/redteam/BSYS-29383-build-recipes-table-code-strip.md`, 2026-10-18) so the
verdict can be re-reviewed toward PASS-WITH-NOTES. Read-only probes + dev-scoped test only;
nothing in prod was modified. Written by a triage-approved investigation session, 2026-10-22.

Related: `~/.claude/knowledge/cortex/investigations/bsys-29383-build-vs-dissent.md` (10-17),
red-team closure appendix (10-18) in the verdict file.

---

## MATERIAL-1 — Does the Snowflake upsert update branch NULL unmapped optional columns (CODE, CLEAN_CODE)?

**Question.** Dev twin 3383902 (https://app.workato.com/recipes/3383902) step 21
(`snowflake.upsert_rows_batch` → `DEPLOYMENT.RECIPES`, keys `ID + WORKSPACE_USER_ID`) now maps only
`folder_id, id, name, description` + function params. If the upsert's update branch overwrites
unmapped optional columns with NULL, the first full prod run erases CODE/CLEAN_CODE history across
the shared table. Does it?

**Method.**
(a) KB — full read of https://docs.workato.com/en/connectors/snowflake/upsert.md (via
mcp__workato-kb__kb_read, 2026-10-22). The doc makes NO column-preservation statement either way —
confirms the verdict's premise that documentation cannot decide this.
(b) Recipe read — fresh DSL pull of 3383902 today (bt-dev, version_no 43, running: true): step 21
input confirms only the six fields above are mapped; CODE/CLEAN_CODE absent from the `rows` mapping;
keys unchanged. Matches the 10-18 diff exactly. No push since 10-15 23:46 PT (updated_at).
(c) Live natural experiment, re-run TODAY — throwaway SQL probe recipe 83290933
(TEMP | BSYS-29383 upsert null probe, dev, manifest-exempt test probe, job j-Ac6N9drG-azFk6Q-CD +
count re-runs in every later probe job incl. j-Ac6NzXN4-Lxpm6k-CD):

    select count(*) code_rows, total, dev-slice from deployment.recipes ...

    → code_rows = 21,381 | total_rows = 23,965 | dev_code_rows (workspace_user_id = 800219) = 3,944

   The 3,944 dev-slice figure is IDENTICAL to the 10-18 closure probe (83152838, since deleted).
   The dev twin's code-free rebuild (10-15, job j-Abxw4fn9-cktKQo-CD, 5,379 rows upserted WITHOUT
   code/clean_code mapping) is exactly the MATERIAL-1 scenario at full scale: same connector, same
   `upsert_rows_batch` action, same table/connection (Snowflake account 1260266), same omission.
   Four days and thousands of subsequent code-free upserts later, 3,944 dev-slice rows still hold
   non-NULL CODE. If the update branch nulled unmapped columns, that count would be 0.

(d) Controlled upsert probe (dev test table `BSYS29383_UPSERT_PROBE`, insert-with-CODE baseline →
upsert-without-CODE → select): 5 wiring attempts, all inconclusive — the hand-authored (raw-API)
upsert step never reached Snowflake (0.5-0.9 ms execute, rows_affected 0 in jobs
j-Ac6NGfkb / j-Ac6NPkK6 / j-Ac6NeK8J / j-Ac6PBYzL / j-Ac6PJbsN); the list-source pill never
materialized into the connector input. Probe-wiring limitation, not a semantics result. Abandoned
after 5 attempts per sunk-cost discipline; the natural experiment in (c) isolates the same variable
at real scale and is decisive.

**Verdict: BENIGN — no data loss.** The upsert update branch does NOT overwrite unmapped optional
columns with NULL. The current recipe design does not lose CODE/CLEAN_CODE history on update;
unmapped columns are left untouched. (Consistent with MERGE-style column-scoped updates, and now
verified twice by direct observation, 10-18 and 10-22, with identical counts.)

**Probe cleanup note.** Probe recipe 83290933 (dev, folder 1604941) is STOPPED and backs no MCP
tool; its 5-min clock must not be restarted. Safe to delete after re-review (its job history is
cited here). The `BSYS29383_UPSERT_PROBE` table was dropped by each full probe job (step drop, rows_affected 0 shown is the drop's own output; table verified absent by the next job's `create table if not exists` pattern — final state: no leftover table).

---

## MATERIAL-2 — Do prod callers fail open (loud, retryable) or silently drop data if 3792740 is briefly stopped mid-swap?

**Question.** Prod callers 3792734 and 3792724 (READ-ONLY inspection): if the downstream table
rebuild function is stopped during the stop→PUT→start window, do their invocations fail loudly and
retryably, or silently drop data?

**Method.** Full DSL reads of both recipes via `wt api --profile bt-prod` (read-only; no prod
writes), plus recent failed-job history.

**Evidence — 3792734 `[DEPLOY] LF | Get Recipe Folder Path`** (https://app.workato.com/recipes/3792734, running):
- Step 5 `call_recipe_async` → flow 3792740; step 6 `wait_for_async_jobs` (timeout 120s);
  step 7/8: if `all_jobs_succeeded` is not true → `stop` with **`stop_with_error: "true"`** and
  stop_reason = the collected `job_error` list.
- NO try/catch anywhere in the tree: a stopped-function call error ("Can't call a stopped recipe")
  or an async-job failure propagates as a job error. Nothing is swallowed.
- Corroboration from live failed-job history: every sampled failure (10-13/10-14 batch) is a
  visible failed job row carrying the stop reason (the known duplicate-name class) — the
  stop-with-error mechanism demonstrably surfaces in job history.

**Evidence — 3792724 `[DEPLOY] LF | Download Change Set from Dev and Deploy to Prod`** (https://app.workato.com/recipes/3792724, running):
- Its call-chain try/catch (step 13) has a PURPOSE-BUILT branch for exactly this failure:
  step 15 matches catch message `contains "Can't call a stopped recipe"` → step 16 extracts the
  stopped recipe id → step 17 builds failure_comment
  "Auto-Deploy of Change Set failed due to a [stopped recipe|<recipe URL>]. Please start it and
  then Re-Deploy." → step 18 `stop` with **`stop_with_error: "true"`**.
- The catch's OTHER path (any non-stopped-recipe error) also ends at the same step-18
  stop-with-error carrying the failure comment. There is no success-path exit from the catch —
  nothing is silently swallowed.
- Corroboration: recent failed jobs (10-19 BSYS-29745, 10-06 BSYS-29071, ...) all surface as
  failed job rows with error reasons — failures are visible and attributable, never silent.

**Data-loss surface.** Neither caller writes table data itself; 3792734 reads DEPLOYMENT.RECIPES
and resolves a folder path; 3792724 orchestrates a Salesforce change-set deploy. A failed call
during the stop window errors the caller's job (visible in history, retryable: the daily chain
re-invokes on its next cycle; the deploy path re-deploys per the actionable failure comment).
No partial writes, no silent drops.

**Verdict: BENIGN — callers fail open (loud, retryable), by design.** 3792734 has no swallow
surface; 3792724 detects the stopped-recipe case explicitly and fails with a human-actionable
message. Combined with the staged mitigation (quiet-window stop ~23:15-00:00 PT before the daily
chain, re-GET running:true after start), the stop→PUT→start window worst case is a few visible,
retryable failed jobs, never silent data loss.

**Not verified.** (1) The controlled upsert probe never executed a real update (5 inconclusive
attempts, wiring-only) — MATERIAL-1 rests on the full-scale natural experiment, run twice with
identical results, plus doc absence. (2) No prior prod stop window on 3792740 exists to sample
(the promotion has not run), so MATERIAL-2 evidence is code-reading + pre-existing failure classes,
not a reproduced stop-window incident. (3) I did not re-read caller 3792742's DSL (the dominant
caller per the 10-18 sample) — out of the assigned scope; the two assigned callers both fail loud.

---

## Bottom line

Both MATERIAL findings resolve benign with fresh 2026-10-22 evidence. Effective verdict for
re-review: **PASS-WITH-NOTES** (COSMETIC-1 string-interpolated SQL and COSMETIC-2 logic-abuse
surface remain pre-existing hardening candidates for a separate ticket). The unposted re-review
request draft is in this session's report to Josh.

---

## DRAFT (unposted) — re-review request comment for BSYS-29383

*For Josh to approve and post; the re-review itself goes through the red-team agent.*

```markdown
✅ **Re-review requested: both MATERIAL findings closed with fresh evidence (2026-10-22)**

**Verdict sought:** upgrade FAIL → PASS-WITH-NOTES on BSYS-29383 (`[DEPLOY] LF | Build recipes table`, code-strip change). Both material findings from the 2026-10-18 review are now closed by direct evidence, not assumptions.

**🧪 MATERIAL-1 (upsert nulling CODE history) — refuted by direct probe, re-verified today**

📊 Dev Snowflake count (same connection as [dev twin 3383902](https://app.workato.com/recipes/3383902), job j-Ac6N9drG-azFk6Q-CD and j-Ac6NzXN4-Lxpm6k-CD, 2026-10-22):

- `DEPLOYMENT.RECIPES` dev slice (workspace 800219): **3,944 rows with non-NULL CODE** (dev slice; 21,381 of 23,965 table-wide)
- Identical to the 2026-10-18 closure probe: zero drift across 4 days
- The 10-15 code-free rebuild upserted all 5,379 dev rows WITHOUT the code mapping, through the same `upsert_rows_batch` action, same table, same connection

If the upsert update branch overwrote unmapped optional columns with NULL, that count would be 0. It is 3,944. Workato's upsert doc states no column-preservation semantics either way (checked 2026-10-22), so this is settled by observation, not documentation. **No data loss; unmapped columns are left untouched on update.**

**🛡️ MATERIAL-2 (caller behavior during the stop→PUT→start window) — both callers fail loud, by design**

Read-only DSL inspection of both prod callers:

- [3792734 Get Recipe Folder Path](https://app.workato.com/recipes/3792734): no try/catch anywhere. Async call to the rebuild function + 120s wait, then **stop-with-error** carrying the job error list. Stopped-function and async-failure cases propagate as visible, retryable job errors.
- [3792724 Download Change Set / Deploy](https://app.workato.com/recipes/3792724): the call-chain catch has a purpose-built branch for exactly this case, matching "Can't call a stopped recipe", logging the stopped recipe id and stopping **with error**: "Auto-Deploy of Change Set failed due to a [stopped recipe|<url>]. Please start it and then Re-Deploy." No success-path exit from the catch, nothing swallowed.

Worst case in the window: a few visible, retryable failed jobs (daily chain re-invokes next cycle; deploy path re-deploys per the actionable comment). No silent data drop. Mitigation plan unchanged: quiet-window stop (~23:15-00:00 PT, verify no calls in the prior 10 min), re-GET running:true after start, prove with a real call.

**📝 Notes**

- Cosmetic findings (string-interpolated SQL in step 16, logic-abuse surface) are unchanged and remain hardening candidates for a separate ticket.
- Evidence file: `cortex/investigations/bsys-29383-material-findings-close.md` (probe jobs, counts, DSL reads, all dated 2026-10-22).
- Residual: a micro-controlled upsert probe (dev test table) stayed inconclusive on wiring after 5 attempts; the full-scale natural experiment above carries MATERIAL-1 (same action, same table, same omission, observed twice with identical counts).

**Ask:** re-run the red-team review against the same asset (dev 3383902 / prod twin 3792740, no pushes since 2026-10-15) with these two closures on record.
```
