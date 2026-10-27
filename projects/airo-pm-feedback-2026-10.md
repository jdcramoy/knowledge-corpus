# AIRO PM feedback list — [colleague] meeting prep (2026-10-14)

Resliced issue list for the AIRO PM sync. Segmentation: **[AIRO]** items file
with [colleague] (Staff PM, AIRO; tool-level ones route to [colleague], her report).
**General** items are platform/API-surface issues owned by other PMs (RLM,
scheduler, data-tables API, Enterprise MCP, editor). Ownership of general rows
is INFERRED from surface, not confirmed.

Full context: `people/pm-grace-ng.md` (her file), `domains/harness-benchmarking.md`
(cost numbers), `skills/airo-mcp-playbook/` (trap catalog). Slack room:
#airo-beta-testing (C09V3M0LS78).

## Status

- Meeting 2026-10-14. DM drafted with the 12 [AIRO] items + 1 thank-you.
- Josh holds filing until Grace confirms the example ticket routes to her first.
- Top opener: data_table_query 404, acknowledged by Ivan 2026-09-25 as "work
  ongoing", still 404ing on live probe 2026-10-14 (table 3fff8d6a).

## [AIRO] items (file with Grace)

1. data_table_query tool 404s "API not found" — known since 2026-09-25
   (Ivan: <https://workato.slack.com/archives/C09V3M0LS78/p1786500576216749>),
   still broken on live probe 2026-10-14. Ask: deploy WorkAI query route / ETA.
2. data_table_update columns param wipes all row data on populated tables
   (nulls cells, regenerates field IDs, even untouched columns). Playbook
   non-negotiable #1. Ask: hard-block or additive edits.
3. Dynamic table_id on add_record/update_record silently drops entire
   parameters payload (get_records unaffected = push-time schema resolution).
   Ask: fail loudly at push.
4. recipe_builder loop-state defect: declare_variable updates don't persist
   across or within foreach iterations; jobs close green. BSYS-25527; jobs
   j-Abskrkcw-otc96x-CD / j-AbsoDnnW-TMXM68-CD / j-AbsoF9Dk-MQTK66-CD
   (2026-10-10). STRONGEST repro. Ask: fix persistence; document declare_list
   aggregation as the supported idiom meanwhile.
5. Every recipe_builder_push corrupts invoke_custom_ruby_code steps (picklist
   values → titles, placeholders materialized). BTSUP-72246, verified
   2026-10-05. Ask: lossless round-trip.
6. set_input_field silently JSON-stringifies scalars; v4_mode json converts
   containers to strings. Prod-hotfix 82120574 (2026-10-10). Ask: write-time
   mode validation.
7. Builder ergonomics bundle: reasonless display-name vs module-name
   rejections, logic steps rejecting connector params, terminal steps never
   displace, sessions stale after push, sticky call-shapes. Ask: reason-bearing
   errors + staleness warnings.
8. recipe_builder_pull exports datapills as resolved sample values — mappings
   look hardcoded. Ask: export pill references or flag them.
9. Clock scheduler: capitalized time_unit accepted by builder, every fire
   silently errors with zero job records → trigger_errors_limit auto-stop.
   3 dead recipes 2026-10-07/08. AIRO half = builder validation; platform half
   = silent no-job-record erroring (general #4).
10. AIRO push doesn't re-register function schemas in the platform registry;
    stale schema until manual editor Save (BSYS-29330, 2026-10-08). Ask: push
    re-registers or expose re-register call.
11. Roadmap asks: bulk/batch recipe-edit tools + recipe lifecycle ops
    (delete/copy/force-run) in MCP. Room corroboration: bulk-update ask
    <https://workato.slack.com/archives/C09V3M0LS78/p1791569681276489>; Ivan's
    asset-deletion thread asked for use cases
    <https://workato.slack.com/archives/C09V3M0LS78/p1786932973670289>.
12. Context cost: AIRO MCP ≈20k tokens/server, dev+prod ≈41k = 32% of harness
    context tax (measure_mcp.py, 2026-10-12, harness-benchmarking.md). Ask:
    schema slimming / tool-search support.
13. Export-manifest package build fails when any included asset references a
    connection that lives in a sibling subfolder — engine errors "Connection
    Home/<project>/Connections/CON | X is not found under Home/<project>/Automation"
    even though the manifest row correctly anchors the connection in /Connections
    (verified by in-page read-back of manifest 368059; 3 export attempts
    2026-10-19/20, identical error, row shapes varied). Blocks ZIP-level
    manifest verification. Ask: export engine should resolve connection deps
    from the manifest's own row paths, not co-location with the referencing
    recipe.
14. API package import T.must-fails in prod for mcp_server/agentic asset
    types — the import path nil-crashes on those asset classes (observed
    during the gslides prod-incident recovery, 2026-10-14; worked around by
    manual tool re-add). Ask: make the import path tolerate or clearly
    reject agentic/mcp_server assets instead of a T.must nil crash.
15. Builder session semantics are BY DESIGN but agent-hostile (Josh verdict
    2026-10-20; agents now trained on both, playbook non-negotiables #6/#7):
    (a) `session_id` shared across tool families — a recipe-builder session
    id reused for `genie_update` pollutes the request URL with the recipe's
    full JSON → `414 Request-URI Too Large`; (b) first `set_input_field` on
    a brand-new step rejects "not available in the current input schema"
    until a `get_input_schema` warm-up call on that step. Ask: server-side
    session isolation per tool family, and auto-warm the input schema on
    step creation.

Thank-you: docs_get reference in schema error messages = best error design on
the platform; hook-enforced on our side because models ignored it (84 loads vs
~3,400 builder calls/7d).

## General product items (other PMs — ownership inferred)

1. Prod package import fails for packages containing mcp_server/agentic_*
   members: "Passed nil into T.must". Owner: deployment/RLM API PM. Verified
   live 2026-10-12 (same zips import in dev; recipe/connection packages import
   in prod). Blocks headless MCP-server promotion. Cross-link [AIRO] ticket.
2. Export manifests: UI-only creation, forced transitive dependency closure,
   selections freeze at creation, cannot be deleted. Owner: RLM PM. Evidence:
   workato-platform.md manifest sections (2026-10-05); wt does manifest CRUD
   via Developer API, proving the API surface exists.
3. Package import rewrites Genie send-event trigger handles (env-scoped
   picklist ids; RLM remaps genie_id only) → "Genie is not found", all green.
   Owner: RLM remap logic. 2026-10-10 P2, ~15h outage.
4. Scheduler silent-error accumulation: scheduled fires error without creating
   job records → invisible failure → auto-stop. Owner: scheduler/runtime PM.
5. Job status green ≠ correctness: monitor-caught failures close "succeeded"
   (BSYS-29488, 4,144/0 history). Owner: runtime/monitoring PM. Ask:
   per-iteration step-count telemetry.
6. Enterprise MCP server tool config has no write surface: vua_required/
   personalization creation-time-only, PATCH 200-but-ignored, no create route.
   Owner: Enterprise MCP feature PM (probed 2026-10-12).
7. Recipe editor save rewrites function flow_id numeric→label; start-validation
   rejects as blank. Owner: recipe editor PM = [colleague] surface.
8. Data-table REST split across hosts with undocumented payload shape
   (data-tables.workato.com, {"document": {...}}; found after 8 failed guesses).
   Owner: data-tables API PM.
9. VUA "End user's connection" drifts intermittently after personalized-recipe
   pushes. Owner: Agent Studio/identity PM (2026-09-11).
10. API infra feedback: WAF 302-redirects python-urllib clients on newer routes
    with valid bearer tokens (RESOLVED on our side 2026-10-07 via UA/Accept
    headers). Owner: API infra. Suggest tolerance or docs note.

Not fileable (context only): wt recipes copy clones trigger UUIDs (our CLI);
silent CLI start/stop no-ops (community surface); Ruby ruby() formula
restrictions (documented platform behavior).
