# AI Directory (Patricia's) — folder 30049351, project 15489424

**What it is:** MCP-served inventory of the Workato estate for BT Enterprise Architecture.
Downstream consumer: AI Asset Registry sync (BSYS-25832/25833) pulls stats from "Patricia's AI Directory MCP".

**NOT the same as** the [AI] [BT] [AIAR] AI Asset Registry vibe-app project (folder 31391241,
BSYS-25527/25528) — Josh corrected this 2026-10-18; see memory `ai-directory-is-folder-30049351`.

## Re-architecture SHIPPED 2026-10-18 (BSYS-29779, dev)

| Asset | ID | Role |
|---|---|---|
| AI Directory \| Asset Inventory | table 161989 / 4c6640c1-4271-48e4-872b-6ad5c0141744 | master, 1 row per asset, key `env:type:source_id` |
| AI Directory \| Sync State | table 161990 / d7a10522-4ca8-42ea-9dd5-dbca2aca5bd2 | append-only reconciliation history |
| FUNC \| AI Directory \| Query Assets | 83153983 | core paginated query (snippet-built server-side filters + Search-records cursor) |
| FUNC \| AI Directory \| Stats | 83153984 | aggregates; unrolled 3-page read + snippet group-by |
| ai_directory_list_assets | 83153991 (skl-Ac3Bttbt-sNcePK-CD) | MCP tool |
| ai_directory_stats | 83154017 (skl-Ac3C84dX-WGwNks-CD) | MCP tool |
| SYNC \| AI Directory \| Estate | 83154018 | hourly, delta-only writes, tombstones, sync-state row |
| MON \| AI Directory \| Verify | 83154123 | hourly canaries + freshness + reconciliation + duplicate/enum scan; LOUD Slack (EM alerts bot, C0C805U47FZ) + job-fail |
| MCP server | **dev twin mcps-AYLxxYnE-AXY-CD** (gateway 5953.apim...) + prod mcps-AYN6hEpB-33T-CD | the EXISTING directory servers; 2 new tools attached to the dev twin (16→15 after get_asset removal) |
| Manifest | **371519** (supersedes 367175, destroyed) | UI-shape: whole-tree scope (33 rows, only edited checked, 0 Not-found), **includes mcp_server row 5953** so tool bindings auto-attach on import; ZIP 13 entries verified; mirror at ~/orca/projects/ai-directory/manifests/bsys-29779.manifest.json |

v1 sync scope: **genies only** (Snowflake AGENTIC_GENIES, user_id 3535598, data_center US → 55 rows).
OLD 19 FUNCs (70868737…71708545) still running = parallel-run; stop only on Josh's cutover go.

## Open (phase 2)
1. `list_mcp_servers` action on connector 748504 (SDK) → unlocks mcp_server asset class (the platform
   STRIPS `__adhoc_http_action` block inputs on API writes — verified 3×; builder can't author them either).
2. Skills/folders/data-tables/collaborators asset classes (list_object covers genie+skill).
3. Client-side MCP call test: server is workato_idp (OAuth via Workato Identity) — users must be in the server's end-user group (incl. Josh); run the PKCE consent flow through the Orca browser to e2e-test.
4. Dedicated Slack channel/bot for findings (currently EM alerts bot).
5. Delete probe 83154128; stop old FUNCs at cutover.

## Lessons deposited (2026-10-18)
- `config` in recipe POST/PUT must be a **JSON STRING** (double-encoded), not an array — array = 400 "Invalid parameter 'config'".
- **API writes (POST/PUT recipe) STRIP `__adhoc_http_action` block inputs** down to mnemonic/verb — author these in the editor only.
- API writes also STRIP `workflow_return_result` result mappings — but AIRO builder push preserves them (raw-PUT blocks + builder-mapped returns is the working combo).
- Raw-PUT'd blocks need **`extended_output_schema`** declaring every pill path consumers reference, or start-validation fails "Unknown data field".
- `foreach`/`if` blocks authored by builder carry `provider: workato_control` which START-VALIDATION rejects ("provider is not allowed for this step type") — strip the key via raw PUT.
- Renumber blocks DEPTH-FIRST after structural edits; top-level-only renumber leaves children out of sequence and start rejects.
- Chained data-table page reads fail "bad continuation token" when the previous page returns empty token (empty table) — don't chain on empty inventories; unroll only with a present-token guard.
- call_recipe parameter fields materialize for call sites ONLY after the callee's function schema is editor-saved (re-registered); builder-only pushes aren't enough.
- `[0]` array indexing in a pill path compiles to nonexistent `current_item`; `ruby("bindings.a.to_a[0] || {}", …)` passes validation (verify `||` at runtime).
- The MCP server publish route: `POST /web_api/mcp/servers/<handle>/publish` (PATCH `published:true` is silently ignored).
- The workspace UI has NO reachable page for a project-scoped MCP server (ai_hub/mcp/<handle> 404s; /mcp/* is the ops dashboard) — token capture needs Josh or a new UI discovery.
- Function-caller blocks: `provider: workato_recipe_function, name: call_recipe` with `extended_input_schema` (parameters object) + `visible_config_fields` enumerating EVERY active path — unlisted paths silently drop.

- MCP server auth: create defaults to hashed_token; **PUT /api/mcp/mcp_servers/<handle> with {auth_type: 'workato_idp'} flips it AFTER create** (tool_ids/tool-create routes don't exist on the Developer API — tools bind only via AIRO mcp_server_create at creation; publish via POST /web_api/mcp/servers/<handle>/publish).

## 2026-10-20 update — attached to the EXISTING dev twin server + e2e PROVEN
- Josh pointed at the dev twin (mcps-AYLxxYnE-AXY-CD, gateway https://5953.apim.mcp.workato.com, workato_idp, 13 old tools). The 2 new tools (list_assets, stats) were attached via the UI Add-tools dialog — server now serves 15 (13 old + 2 new). My standalone dev servers were deleted (wrong-auth default + toolless attempt).
- **END-TO-END PROVEN via real MCP gateway calls** (OAuth DCR+PKCE through Orca, token flow works): tools/list=15; stats → total=55, JSON by_*; list_assets → server-filtered, JSON assets, cursor round-trip PROVEN (disjoint pages); exact lookup via asset_id (count=1 / miss count=0).
- get_asset wrapper DELETED (redundant — list_assets(asset_id=...) does exact lookup; also its start-validation was blocked by the stale function-registry schema).
- **Bugs found+fixed by e2e testing:** (1) stats triple-counted 165 vs 55 — unrolled page 2/3 reads with EMPTY continuation tokens silently re-return page 1; fixed with Record-ID dedupe in the aggregate snippet. (2) by_*/assets/first_asset served as RUBY INSPECT strings — fixed by JSON.generate in snippets + string-typed result schemas. (3) `||` in a ruby() formula: validator PASSES it, runtime REJECTS it — get_asset failed "Tool execution failed" until the mapping became a pure passthrough.
- `ai-directory-dev` added to ~/.claude/mcp-on-demand.json (https://5953.apim.mcp.workato.com) — attach with `claude --mcp-config`; first use needs one OAuth consent click.

## MANIFEST CORRECTION (2026-10-24, Josh — "the manifest is fucked up")
- Manifests are **UI-shaped, not hand-crawled**: anchor at the project/folder level, whole tree included by the platform at save, ONLY session-edited assets checked; NEVER hand-pick dependency rows (six re-proofs they corrupt: dep rows stamp state:"deleted" → "Not found", exports wedge in `working`).
- **MCP-skill deploys MUST select the mcp_server row they're attached to** — without it the imported server binds nothing. For this project: mcp_server id 5953 (mcps-AYLxxYnE-AXY-CD).
- Reference implementation: `~/.claude/knowledge/scripts/build_manifest.py` (mirror-the-UI shapes). The old create_manifest.py is deprecated for creation.
- Leftover cleanup in this round: deleted manifest 367175 (destroyed) + the unused standalone dev server mcps-Ac3zPg8r-LMd-CD (33154).

## 2026-10-25 — FULL-SDK PUSH: shipped the connector actions; sync extension BLOCKED by platform (handed to Josh)
- **Connector 'Workato API' (custom_adapter 1284584, connection 19082219) v3 RELEASED**: new actions list_mcp_servers, list_user_groups, get_user_group_project_grants (additive; arity fix: output_fields lambdas MUST take |object_definitions| even unused, or extended-schema retrieval fails 'missing input/output' and start-validation calls the action 'is invalid').
- Sync extension to full estate (skills/folders/data_tables/roles via list_object; mcp_servers/user_groups via the new SDK actions) was CODED but hit three distinct platform blockers: (1) start-validation rejects NAMED custom-connector actions via the API path (even v1 actions — probe-proven), (2) UI start silently no-ops on the same, (3) added list_object steps VANISHED from the recipe after later session ops. Reverted to the verified genie-only state (running, healthy).
- RESTORE after the corruption: the raw-PUT rebuild initially produced a READ-ONLY recipe (fetch+diff only, no write tail — jobs succeeded while syncing nothing!). Detected by: sync-state row not advancing + updates computed but never applied. Lesson: after ANY structural recipe rebuild, assert the block-tree COUNT matches the design before starting.
- Path forward: Josh builds the 4 list_object steps in the EDITOR (10 min, spec in BSYS-29806) or support ticket for the named-action start-validation; then diff bindings + descriptions to full scope.

## 2026-10-25 (late) — MULTI-TYPE SYNC LIVE: 4 types, 328+ assets, all patches verified
- **metrics_json overflow FIXED**: generic normalizer capped at 9500 chars (oversized → {"truncated":true,"orig_size":N}); job j-Ac98PkYs-KK9R9t-CD succeeded after earlier 18098-char failure.
- **Folder coverage COMPLETE (123/123)**: generic list_object DOES expose per_page/page for folders (API caps 100/page; estate = 100 + 23). Unrolled page-2 step + `folders2` snippet input (schema + data binding + concat in code).
- **data_table CAPPED at 100 (true 291)**: generic list_object exposes NO page/per_page for data_table; raw API paginates but the platform action doesn't wire it. Documented in descriptions.
- **Named custom-connector actions STILL start-blocked** — 4th repro, POST-arity-fix: `list_mcp_servers` on a fresh TEST probe recipe → start fails `"name list_mcp_servers is invalid"`. Split test conclusive; mcp_server/user_group/role types stay out until platform fix. Probe deleted.
- **Stats through the live gateway**: total 334 — folder 123, data_table 100, genie 56, skill 55; by_state 323 active / 5 inactive / 6 archived. Reconciliation 328=328 healthy; idempotent deltas (creates=1, archives=1 on re-run).
- **NEW GOTCHA — raw PUT /api/recipes accepts `code` but SILENTLY IGNORES it** (200 success:true, code unchanged, updated_at advances). Snippet edits MUST go through recipe_builder set_input_field(path='code') + push.
- **NEW GOTCHA — builder edits to a RUNNING recipe are silently discarded** (add_step then remove_step left the original 16 steps; my 3 added steps vanished). Stop → edit → push → start, every time.
- **Snippet-editing recipe that works**: set_input_field step N path `code_input.schema` (declare new input) → `code_input.data.<name>` (pill binding as ruby(...) string) → `code` (concat in code) → push.
- Tool descriptions updated to full scope on all three (83153983/83153984/83154018) — requires stop→edit→start (running recipes reject metadata updates).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [AI Directory (Patricia's)](projects/ai-directory.md) — **the Workato estate directory MCP** (folder 30049351; NOT the AIAR vibe-app registry 31391241); BSYS-29779 2026-10-18: re-architected from 19 return-everything FUNCs to data-table inventory (161989) + delta-only hourly sync (83154018) + 3 paginated MCP tools (list/get/stats, server 5953-class, dev mcps-Ac3CQcch-kfM-CD) + hourly self-verify monitor (83154123, canaries+reconciliation+dupe-scan, negative-test-proven); v1 = genies (55), phase 2 = mcp_server class via new connector action; old FUNCs parallel-run until Josh cutover

## 2026-10-26 — FULL UAT PASSED + legacy benchmark (all evidence on BSYS-29779 comment 1148497)
- **Data validation through the live gateway:** genies 56 = legacy-55-unique + 1 tombstone (legacy returns 72 rows/17 DUPES — paging bug; one genie 7×). Folders 123/123 EXACT vs raw API (0 missing/extra/name mismatches). Tables: ours 100 ⊆ raw-API 291, 0 mismatches (cap = platform List-object page limit, NOT our bug; legacy FUNC confirms 291). Skills: no ground truth exists anywhere else; validated via tombstones — sync caught a REAL deletion event (8 add_asset skills) live during UAT.
- **Edge cases:** miss→count 0; invalid type→count 0 clean; name_starts/state filters exact; cursor exhaustion terminates; full inventory walk 337 rows, ZERO dupes; reconciliation 328=328.
- **Benchmark (server-side job durations):** legacy ~4.3-6.8s/call, 0.6-1.3MB single blob, 17 dupes, ruby-inspect (unparseable) payloads vs new ~0.6-0.8s/call (~8×), bounded pages, 0 dupes, clean parsed JSON.
- Legacy data-tables payload is a DOUBLE-ENCODED ruby-inspect string inside the MCP response (str[588732]) — downstream consumers literally cannot json.parse it. Strongest cutover argument.
- UAT state machine: NOT ready for cutover per Josh until he says go; gaps documented (tables 100/291, mcp_server/user_group/role platform-blocked 4×).

## 2026-10-26 (later) — COVERAGE AUDIT CORRECTED: 9 types live, data_table cap KILLED via Snowflake
- Josh rejected the "PASS w/ cap" UAT — right call. Coverage audit vs the 19 legacy FUNCs: we were at 4 types / prod-only / no usage stats; legacy covers 6 domains × 2 envs + 3 Snowflake stats FUNCs (4 legacy FUNCs not even running: Folders-Prod, both Grants, — Groups-Dev? verify at cutover).
- **Estate ground truth (raw prod API, read-only probes):** recipes 2,058 (21 pages @100), connections 343, data_tables 291, projects 124, folders 123, KBs 80, lookup_tables 49, skills ~50, genies 55. Role → list_object 400 "Unsupported"; api_client family → 401 missing_privilege (token scope); mcp_server/user_group → NOT in list_object picklist, named SDK actions still start-blocked.
- **DATA-TABLE CAP KILLED: Snowflake EDW_DB.WORKATO_USAGE.WORKATO_DB_TABLES (WHERE user_id='3535598') = exact 291-table dimension.** Sync now sources tables from Snowflake (limit=500, orderby field) instead of the capped list_object. 291/291 verified.
- **Snowflake custom-SQL gotchas:** (1) put ORDER BY in the `orderby` field, never inline; (2) `limit` field defaults to 100 — set it; (3) AIRO-pushed output_schema makes the adapter return HASH-MANGLED keys (id_b497e547 — STABLE across runs); normalize in the snippet (fallback map) + raise if any id blank.
- **Architecture: 3 type-scoped syncs** sharing inventory 161989: SYNC|Estate 83154018 (genie/skill/folder/data_table, source_key estate:prod:v1) + **SYNC|Platform 83362376 (project/connection/knowledge_base/lookup_table, estate:prod:platform)** + recipes sync STILL TO BUILD (21 pages, 2,058 rows). Each: delta-only, revive-on-reappear (no archived-reject in diff), sync-state own source_key.
- **Reconcile must be scope-aware** (count only own asset_types) AND **Record-ID-deduped** (chained page-2 reads re-serve page 1 when token empty).
- **Read truncation = re-create corruption:** any diff/recount read capped at 1,000 rows while table is bigger → rows beyond cap look "new" → re-created (dupes). Fixed with unrolled 2-page continuation reads + Record-ID dedupe in snippets; serving FUNCs (83153983/83153984) now ALSO dedupe by asset_id at read time.
- **Dupe root cause = CONCURRENT RUNS** (force-run colliding with hourly, 33s apart, both diff-then-create). Ops rule: never force-run within ~5 min of the hour; monitor dupe-scan catches recurrences hourly.
- Current inventory: 1,118 rows / 8 types / 0 dupes; reconciles healthy (596 platform, main 519+live drift). truncated flag in stats = honest "read may be behind" signal.

## 2026-10-27 (night) — RECIPES SYNC LIVE + dupe-incident root-caused; chain-aware read guards
- **Incident:** inventory ballooned 1,913→2,996 (1,083 dupes, 28 copies of some data_tables). TWO causes: (1) Estate's scheduler trigger had LOST `trigger_every` (builder/raw-PUT edits destroyed it) → platform fired at the 5-minute minimum for 2h straight; (2) diff reads were 2 pages @1,000 on a growing table → trailing rows never seen → re-created every run. Fixed: `trigger_every="1"` verified on all four syncs; reads expanded to 4 pages.
- **THE PLATFORM BUG (finally isolated): chained data-table `Search records` pages RE-SERVE PAGE 1 when handed an empty continuation token.** Healthy end-of-table (short page + empty token) hands the next page an empty token → phantom page-1 copy → phantom "more data exists" tokens. One bug, three symptoms (stale "11-row" reads, reconcile counts like 95, re-serve chains).
- **Chain-aware guard design (now in all 4 syncs' diff snippets):** bind each page's continuation token as a snippet input; a page is chain-valid only if the PREVIOUS page returned a non-empty token; exclude non-valid pages (benign re-serve); raise INVENTORY READ TRUNCATED (≥4,000), INCOMPLETE (last valid page has next token), DEGRADED (valid page re-served an earlier page's first Record ID). Corruption is structurally impossible — degradation is a LOUD failure + hourly retry.
- **PROVEN:** Estate run after fix: existing_count 1,913 (full table), creates 0, reconcile 519 healthy. Recipes run: existing 1,913, +500 creates, 1,095/2,063 converging (~500/good run).
- **Cleanup discipline learned the hard way:** my first dupe-delete script keyed rows on 'Record ID' (wrong — rows use `$record_id` via wt) and read inconsistent page sets; it nearly deleted 1,083 rows on a bogus plan. RULE: any delete batch requires a TWO-PASS read (dupes confirmed in both passes with identical record-id multisets) + row-shape assertion before the first delete.
- **set_input_field null-value hazard:** passing `"value": null` WIPES a field (wiped a snippet schema mid-edit; the recipes snippet then failed "RECIPES PAGE 1 FAILED" because p01-p21 were dropped from the schema I replaced). Setting code_input.schema REPLACES the whole schema — always include ALL entries.
- **Read-path split test:** REST (`wt dt query`, 200/page) reads the table PERFECTLY every time while recipe-side Search-records degrades — different backends. If chains keep failing: per-sync tables sized for single-page reads, or REST-read migration, are the phase-2 architecture.
- Builder mechanics: `recipe_builder_get_input_schema` on a scheduler step exposes `time_unit` + hidden required `trigger_every` AFTER time_unit is (re)set; get_records `order_direction` picklist ids are "asc"/"desc"; `wt recipes force-run` requires the recipe RUNNING; push requires STOPPED (stop→push→start, never leave stopped).
- Manifest 372420 updated to 13 checked rows (+ recipe 83367700), echo-verified 13/13 checked, 0 state-deleted; mirror refreshed. In-page verification blocked (Orca browser signed out — 401); the update echo is the platform's persisted-state read-back. **ZIP-level proof:** package export 42331460 COMPLETED with 17 files incl. mcp_server JSON + bindings .bin; evidence at ~/orca/projects/ai-directory/evidence/. **Hook fix (Josh: review):** manifest-guard's MCP read-back treated a signed-out 401 as "rows: 0" and false-blocked forever; added the same `status == 200` gate the hook's own verification stage already had (non-200 = unverifiable = pass; real 200-reads still block). SSO re-login lands on Josh's personal MS account (passkey) — only Josh can refresh the browser session.

## 2026-10-26 (night) — "PLATFORM BUG" DISSOLVED: wrong connector all along; fleet types live (11 types, 1,306 rows)
- **THE LESSON (biggest of the project):** the "named-action start-validation bug" was MY wiring error. The SDK actions live on **"Workato Platform API" (custom 1284584, provider workato_platform_api_connector_3535597_1773205949)**; the syncs used **"Workato API" (custom 474791, provider workato_api_connector_748504_1684743862)** — a DIFFERENT connector with the generic 20-type list_object but NOT my SDK actions. "name list_mcp_servers is invalid" = literally true. A probe on the CORRECT connector started FIRST TRY. Before ever calling something a platform bug: diff the connector ID the actions were released on vs the connector the recipe references.
- Fleet sync LIVE: **SYNC | AI Directory | Fleet (83363462)** (graduated TEST probe, renamed) — mcp_servers 73/73, project_roles 9/9 (list_roles added, connector v4), user_groups 100 (the /api/user_groups endpoint IGNORES the page param — hard ceiling, same for legacy). source_key estate:prod:fleet. Prod connection on 1284584: **22380884** (token = wt keychain workato-platform-cli / account josh-prod).
- Connector 1284584 v4: list_roles (GET /project_roles per_page/page). Keychain: per-PROFILE accounts (-a josh-prod), one service.
- Inventory: 1,306 rows / 11 types / 0 dupes (mcp_server 73, user_group 100, role 9 added). Reconciles healthy per scope.
- Manifest of record: **372420** (12 checked: 8 recipes incl Fleet, 2 skills, mcp_server 5953, custom_adapter 1284584; 0 Not-found; ZIP 11 asset files). 372393 + 371519 destroyed.
- REMAINING: recipes sync (2,058/21 pages, 12th type); dev-env coverage; usage-stats aggregates (Snowflake fact tables: CONVERSATIONS 9.9M rows, FLOWS 17M, MCP_TOOL_CALL_STATS 4,195 pre-agg).
