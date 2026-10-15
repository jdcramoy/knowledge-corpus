# AIRO issue filing package — 12 tickets, ready to file (2026-10-15)

Ticket-ready specs for the 12 [AIRO] items DM'd to [colleague] on 2026-10-15
(list source: `airo-pm-feedback-2026-10.md`; evidence: `airo-mcp-playbook/`,
`domains/workato-platform.md`). Numbering matches the DM exactly so filing is
mechanical once Grace confirms the example ticket routes to her.

**Routing proposal (inferred, per `people/pm-grace-ng.md`):** file all 12 under
[colleague] (Staff PM, AIRO); she sub-routes. Proposed per-row sub-route noted.
**Proposed severity:** S1 = silent data loss / silent wrong behavior on live
assets; S2 = corruption or breakage with a visible symptom or workaround;
S3 = ergonomics/efficiency.

---

### 1. `data_table_query` 404s "API not found" — Bug, S2 — sub-route: AIRO tool infra
- **Ask:** deploy the WorkAI query route to our workspace, or ETA.
- **Evidence:** acknowledged by Ivan 2026-09-25 as work ongoing
  (https://workato.slack.com/archives/C09V3M0LS78/p1786500576216749); live
  probe 2026-10-14 on table 3fff8d6a still 404s. `data_table_list`/
  `data_table_get` work — only the query route is missing.
- **Note:** we run a hook banning the tool call until it ships (it wastes
  session turns on retry). Workaround exists (Developer-API query route,
  documented), so impact = tool parity, not data access.

### 2. Push doesn't re-register function schemas — Bug, S2 — sub-route: AIRO
- **Ask:** `recipe_builder_push` re-registers the function schema in the
  platform registry, or exposes an explicit re-register call.
- **Evidence:** BSYS-29330 build (2026-10-08). Callers keep validating the
  stale schema; `set_input_field` rejects the new param; nothing but a manual
  editor open+Save invalidates it. Full sequence in
  `airo-mcp-playbook/references/known-bugs.md` ("Callee parameter-schema
  staleness").
- **Failure mode:** silent partial deploys — call sites ship against the old
  contract or authors invent workarounds.

### 3. Capitalized `time_unit` kills schedules silently — Bug, S2 — sub-route: AIRO + scheduler team
- **Ask (AIRO half):** builder start-validation rejects or normalizes
  `time_unit` case. **(Runtime half, cross-link):** scheduled fires must not
  error without materializing job records (general item #4).
- **Evidence:** 3 dead recipes 2026-10-07/08 (recipes 82866722, 82868967,
  fix-verified 82893071). "Minutes" lands on an anchor-bearing schedule path;
  every fire errors invisibly; job list never grows; recipe auto-stops with
  `stop_cause=trigger_errors_limit`. Diagnostic signature documented.

### 4. `data_table_update` columns wipes row data — Bug, **S1 (silent data loss)** — sub-route: AIRO
- **Ask:** hard-block `columns` on populated tables, or make edits additive
  with explicit opt-in to destructive schema change.
- **Evidence:** every cell nulls and every field_id regenerates — including
  untouched columns — on any populated table; no warning, no error. Canonized
  as playbook non-negotiable #1 after a live incident.

### 5. Dynamic `table_id` silently drops the payload — Bug, **S1 (silent data loss)** — sub-route: AIRO
- **Ask:** fail loudly at push when schema resolution can't complete.
- **Evidence:** `add_record`/`update_record` with dynamic `table_id` push
  clean and write nothing; `get_records` is unaffected — so this is push-time
  schema resolution failing silently. Canonized as playbook non-negotiable #2.

### 6. Loop-state doesn't persist in the builder runtime — Bug, **S1 (silent wrong behavior)** — sub-route: AIRO runtime — **strongest repro in the set**
- **Ask:** fix variable persistence across/within foreach iterations; interim,
  document `declare_list` + aggregation as the supported idiom.
- **Evidence (attach all):** BSYS-25527 build, unmasked checkpoint step; jobs
  j-Abskrkcw-otc96x-CD, j-AbsoDnnW-TMXM68-CD, j-AbsoF9Dk-MQTK66-CD
  (2026-10-10). Updates don't survive across iterations at any nesting depth
  NOR within a single iteration; conditions silently never fire; jobs close
  green. Proven three ways including same-iteration staleness.

### 7. Every push corrupts `invoke_custom_ruby_code` steps — Bug, S2 — sub-route: AIRO
- **Ask:** lossless round-trip through `recipe_builder_push`.
- **Evidence:** BTSUP-72246 build, verified 2026-10-05, repros on every push
  since. Push rewrites `payload_asset_type` to the option TITLE ("Define
  manually"), materializes `snippet_document_static_asset` /
  `get_records` filter placeholders as "<REQUIRED FIELD PLACEHOLDER>", and
  rewrites picklist VALUES to TITLES ("istrue"→"is true"). Static checks
  pass; only the UI Test banner blocks — so agents ship it.
- **Current cost:** we run a strict push discipline (build → push → re-pull →
  fix all degradations in one pass → push ONCE → test with no further pushes).

### 8. `set_input_field` silently coerces values — Bug, S2 — sub-route: AIRO
- **Ask:** write-time mode validation — reject or round-trip scalars cleanly
  in the plain setter; make v4 `json` mode preserve containers.
- **Evidence:** plain setter JSON-stringifies every scalar (string "x" stored
  with literal quote chars; list → `"[\"x\"]"`); `set_input_field_v4_mode`
  mode=json turns hash fields into strings (pills + schema refresh break).
  Caught on prod hotfix 82120574 (2026-10-10).

### 9. Builder ergonomics bundle — Bug (UX), S3 — sub-route: **[colleague]** (recipe editor UX)
- **Ask:** reason-bearing errors + staleness warnings. Concretely: (a) action
  `add_step` rejects connector DISPLAY names with no reason (module
  snake_case names required — triggers accept display names, actions don't);
  (b) logic steps reject connector params; (c) `add_step` never displaces a
  terminal step (lands as dead code past `workflow_return_result`, position
  report lies by +1); (d) builder sessions go stale after push with no hint
  to re-pull; (e) tool-call arg shapes go sticky mid-session.
- **Evidence:** each is a canonized trap-table row in `airo-mcp-playbook`.

### 10. `recipe_builder_pull` exports sample values, not pill references — Bug, S3 — sub-route: AIRO
- **Ask:** export pill references, or flag resolved-sample rendering in the DSL.
- **Evidence:** audited mappings look hardcoded when they aren't; playbook
  non-negotiable #5 (verify against UI/`job_get` before concluding a field is
  hardcoded).

### 11. Bulk edits and lifecycle ops — Feature/Story — sub-route: AIRO roadmap
- **Ask:** bulk/batch recipe-edit tools; recipe delete/copy/force-run in MCP.
- **Evidence + demand signal:** room corroboration — bulk-update thread
  (https://workato.slack.com/archives/C09V3M0LS78/p1791569681276489); Ivan's
  asset-deletion thread asked for use cases
  (https://workato.slack.com/archives/C09V3M0LS78/p1786932973670289) — ours:
  cleaning up AIRO-created assets that missed. Note: the Developer API
  already supports all of these (our `wt` CLI does delete/copy/force-run
  today) — this is purely an MCP surface gap.

### 12. Tool-definition token cost — Feature/RFC — sub-route: AIRO + platform
- **Ask:** schema slimming or tool-search support (client-side deferred
  loading).
- **Evidence:** AIRO MCP ≈20k tokens per server, ≈41k for dev+prod attached
  together = 32% of our total harness context tax (measure_mcp.py,
  2026-10-12; `domains/harness-benchmarking.md`). Note: the docs_get-in-error
  pattern shows this team designs well for agent clients — tool-search would
  compound that.

**FILED 2026-10-15 (BSYS, assigned to Josh, S1=High/S2=Medium/S3=Low, points S1=3/S2=2/S3=1, stories 2pt):**
DM #1→BSYS-29708 · #2→BSYS-29702 · #3→BSYS-29703 · #4→BSYS-29709 · #5→BSYS-29710 · #6→BSYS-29704 · #7→BSYS-29711 · #8→BSYS-29712 · #9→BSYS-29705 · #10→BSYS-29713 · #11→BSYS-29706 · #12→BSYS-29707 (thank-you posted as comment there). Dissent verdict STANDS (thread `airo-pm-filing-2026-10-15` in `dreams/bus/dissenter.jsonl`); amendments applied: Josh-assignee, package point scheme, #9 item (b) flagged reported-not-canonized, #6 rephrased as job-runtime persistence, #2 cites BSYS-29330 comment 1132095, #7 cites the canon entry. No parent epic exists for AIRO-MCP platform feedback — proposed, not created.

**Thank-you row (file as goodwill comment on any of the above, not its own ticket):**
the docs_get reference inside schema errors is the best error design we've hit
on the platform; we hook-enforced it because models ignored the pointer (84
loads vs ~3,400 builder calls/7d) — evidence the pattern works when enforced.

---

## Filing mechanics (when routing confirms)

- Suggested split: 12 tickets as listed; #9 could be a parent with 5 subtasks
  if Grace's team prefers granular tracking.
- Every ticket: attach the playbook evidence path + job/recipe IDs above.
- Points (if our own BSYS mirror tickets are wanted for tracking): S1 rows 3,
  S2 rows 2, S3 rows 1 — but upstream filing is the ask, so only mirror if
  Josh wants them tracked on our board.
- Priority order per sender: the five S1/silent-failure rows (4, 5, 6, 7, 8 in
  DM numbering) have teeth; the rest can wait on the sync.
