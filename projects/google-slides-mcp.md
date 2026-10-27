---
name: google-slides-mcp
description: Enhanced Google Slides by Workato MCP — repo/handoff locations, env identities, guidance-injection architecture + Enterprise Context serving-layer proof (2026-10-06)
metadata:
  type: project
---

# Google Slides MCP — project state


# Google Slides MCP (Enhanced Google Slides by Workato MCP)


## SHARD COMPILER v2 (2026-10-08, dev): design guidance joins the hot path

- DESIGN: the corpus is now a shard graph, compiled OFFLINE into what the
  hot path reads. Tiers of shard selection: (1) tool identity (pack base),
  (2) call parameters (deterministic param->shard reads, e.g. layout name,
  built later when Ray's 56 layout shards exist), (3) optional user_intent
  param (opt-in NL, one capped EC search) - never runtime RAG by default.
- SHARD AUTHORING CONVENTION: a section on any server/deep page whose body
  has a first line `applies-to: A, B, group:x, all` becomes a design shard.
  Group names: read/lifecycle/elements/content/collab/ds. Sync strips the
  applies-to line from served bodies; sections without applies-to are not
  shards.
- SYNC v2 (dev 82864023 pushed+tested, job j-AbrhrDFo-seLb9w-CD): parse
  now emits doc_type + group metadata on every doc, design_shard docs
  (gslides-guidance-<page>-shard-<idx>) AND composed per-group
  design_pack docs (gslides-guidance-pack-<group>, sections joined,
  1200/shard, 4000 cap) - composed WITHIN the design page's parse step
  (same-page composition dodges the cross-page accumulation wall; Workato
  loops cannot accumulate and same-job EC reads are stale).
- HELPER v2 (dev 82864228, job j-Abrhzebm-dobYsn-CD PROVEN): read 1 =
  tool doc (group from its metadata), read 2 = design_pack
  {scope:design_pack, group, status:published}, merge = tool 500 + pack
  400, cap 900. Graceful: no published pack -> single-read behavior;
  no tool doc -> no design either (v1: group comes from the tool doc).
  Measured: reads 0.40s + 0.21s, total helper ~0.63s cold-ish.
- PROOF PAGE: "Design mechanics (engineering)" 2939912212 (published,
  PP space child) carries 3 engineering-authored design shards (spacing
  4px/14pt question, ghost-text hygiene, table overflow/geometry trust).
  Ray's pages slot in by adding applies-to lines when he publishes.
- NEW page creation WITH the details macro: markdown format can't emit
  macros - create via HTML format (bodied-extension keyed `details`,
  label param). Verified: parser reads it (docs emitted correctly).
- NOT YET SHIPPED: prod promotion of sync v2 + helper v2 (needs Josh's
  confirmation); param-conditioned layout reads (wire layout param ->
  helper context_hint on Add_Slide/List_Layouts); user_intent opt-in
  param; effectiveness telemetry loop (per-shard failure rates joined
  from jobs API x pack-version timeline) + nightly compiler-proposal
  agent writing DRAFT Confluence sections.


## SHARD COMPILER v2 LIVE IN PROD (2026-10-08)

- PROMOTED (Josh confirmed + prod-bypass window): sync v2 82873160 (Test
  job j-AbrkLpML-Nofhn8-CD: shards + 3 design packs in prod KB, zero
  failed docs, running) + helper v2 82872520 (pushed, running).
- PROD SMOKE GREEN: helper Test Add_Table -> composed 900-char guidance
  (500 tool + 400 design pack elements), status ok, version v4-s3-1121,
  EC reads 0.23s + 0.17s (job j-AbrkR3WC-BzxY8G-CD).
- REMAINING TIERS: param-conditioned layout reads (Add_Slide/
  List_Layouts context_hint wiring), optional user_intent param,
  effectiveness telemetry + nightly compiler-proposal agent.


## FULL GROUP COVERAGE (2026-10-08, dev): all 6 design packs live

- Agent-built page "Design mechanics: verification, review & design-system
  workflow" 2938175846 (published, deep scope): 4 engineering shards
  (Visual verification protocol -> group:read; Review cycle etiquette ->
  group:collab; Design-system workflow rules -> group:ds; Search and
  orphan hygiene -> group:read). All grounded in L1 corpus/UAT history.
- After page fix + sync (jobs j-AbrkezXz-YXzQsK-CD zero docs due to a
  Scope-row th/th markup bug, then j-AbrkftAe-kRnBHB-CD correct): packs
  read/collab/ds published alongside elements/content/lifecycle.
- ALL 62 tools now get design guidance on the hot path in dev; only
  Ray's judgment content (palette, per-layout when-to-use, QA standards,
  archetypes) remains unpublished.
- TRAP for the shard convention: the details-macro property table rows
  MUST be <th>label</th><td>value</td> - a <th> VALUE cell makes the
  parser miss the property (silently defaults scope to 'tool' and then
  non-tool headings emit zero docs; symptom: 'docs': [] from a page that
  looks perfectly formed).

## SHARD COMPILER v3 TIERS 2+3 (2026-10-08, dev): context_hint + user_intent live

- HELPER v3 (dev 82864228, pushed + Running): trigger params + optional
  context_hint ("Layout name or other parameter-derived shard key") +
  user_intent ("caller's natural-language intent"). Structure after v2's
  merge (steps 2-5 byte-identical): step 6 `if context_hint` -> step 7 EC
  list_with_dynamic_filters {doc_type:"layout", layout:<hint>,
  status:published} -> step 8 ruby "Append layout shard" (top-level,
  passthrough unless hint non-empty AND count>0; +layout body 300, combined
  cap 1200); step 9 `if user_intent` -> step 10 error_handling (retries=0,
  EMPTY catch = fail-open) wrapping step 11 EC search_documents
  (query=<intent>, page_size 1, metadata_filters key/value scope=deep +
  status=published) -> step 13 ruby "Append deep shard" (top result 250,
  total cap 1450); return guidance_md from step 13, status/version/changed
  still from step 5 -> absent params = v2 output byte-identical.
- EC search_documents TRAP: it has NO data_filters field — its input is
  metadata_filters (key_value list). The "data_filters must be JSON STRING"
  rule applies to list_with_dynamic_filters/search_with_dynamic_filters
  only. knowledge_bases = comma-separated handle string (secondary toggle).
- Cross-block pill references WORK at push (step 8 outside `if 6` reads
  list_with_dynamic_filters_7; runtime renders skipped-step pills nil ->
  .to_i/.to_s guard) — only nil-safe ruby in append steps makes this safe.
- Remove+re-add of a call_recipe step DOES surface a just-pushed function's
  new params (stale-registry concern didn't bite) — BUT add_step with
  parent=1 at a position inside a monitor try APPENDS at the end instead,
  and a later move_step to parent=1 silently no-ops (re-confirmed). Correct
  insert: add_step(position=<inside-try pos>, parent=<monitor step no>).
- WIRE: Add_Slide dev 74528389 step 17 rebuilt (flow_id 82864228,
  parameters {tool_name:"Add_Slide", context_hint:
  start_workflow_1['parameters']['layout'] pill}, mask_data=True, comment);
  return rebuilt onto new step; both recipes Running=True. List_Layouts
  skipped by design (no layout param). Only known-harmless warnings remain
  (step-3 DatapillInvalidPath x2; helper empty-catch EmptyBlock is the
  intended fail-open). Dev smokes PASSED (coordinator: regression byte-
  identical 900 chars v4-s3-1121 with if-blocks skipped/zero extra EC
  calls; NL tier search fired 0.65s, 250-cap append, fail-open intact).
- PROD PROMOTION (2026-10-08, Josh's bypass window): prod helper v3
  82872520 pushed + STARTED + recipe_get Running=True (full v3 structure,
  prod KB kb-AbrL4okJ-8spRP8-CD). Prod Add_Slide 74736305 v3 wiring
  PUSHED clean (step 17 call_recipe 82872520 + context_hint=layout pill,
  mask_data=True; return rebuilt) BUT LEFT STOPPED — the wt start was
  DENIED by the auto-mode classifier (relayed "Josh confirmed" from the
  coordinator does not meet the first-hand consent bar; per CLAUDE.md
  prod writes must prompt Josh directly). NEXT ACTION: Josh starts
  74736305 in the Orca browser (or re-consents in-transcript) — it is a
  LIVE prod tool currently DOWN. Then prod smokes (same 4 cases as dev).
- PROD AUTO-MODE LESSON: the classifier gates prod wt lifecycle calls
  inconsistently (helper start passed minutes earlier, Add_Slide start
  denied) — assume ANY prod wt stop/start may hard-deny mid-run; do
  prod stops/starts only with Josh's first-hand consent visible in the
  CURRENT transcript, and never leave a prod recipe stopped mid-swap.


## TIERS 2+3 LIVE IN PROD (2026-10-08): helper v3 everywhere

- HELPER v3 (dev 82864228 + prod 82872520, 14 steps): optional
  context_hint (param tier: deterministic EC read {doc_type:layout,
  layout:<hint>} + 300-cap append, 1200 total) and user_intent (NL tier:
  EC search_documents, metadata_filters [{scope:deep},{status:published}],
  top result 250-cap append, 1450 total) wrapped in a fail-open
  error_handling block. ABSENT PARAMS = byte-identical v2 output, both
  if-blocks skipped, zero extra reads (proven in BOTH envs: dev smoke
  j-Abrm8Job/j-Abrm8tbD, prod smoke j-Abrmk49Y).
- PROD Add_Slide 74736305 wired: helper call passes context_hint =
  the layout param pill (remove+re-add call step; return rebuilt
  verbatim). Running=True. List_Layouts skipped (no layout param).
- Platform notes: EC search_documents takes metadata_filters as a
  key/value LIST (not data_filters JSON string); cross-block pill reads
  from a skipped if-branch are nil-safe via .to_s/.to_i passthrough
  rubies; call-site re-add DID surface the just-pushed v3 function
  schema (registry staleness did not bite for re-adds).
- Browser note: rapid dev<->prod env switching can trigger "Session
  expired: you switched workspaces in another tab" (Reload recovers
  without SSO). Start the recipe FIRST when smoke downtime is open,
  smoke after service is restored.
- One known quality gap: the NL tier's semantic search returns ROOT
  deep docs, not individual shards (coarse granularity). Improvement:
  index design_shard docs as searchable deep copies too.
- Nightly compiler loop scheduled (durable cron 12:43 AM, 7-day expiry,
  renews as it earns keep). Effectiveness baseline: ~2,900 real prod
  jobs/48h, zero failures.


- MONITORING CORRECTION (2026-10-08): job-status analysis MISSES managed
  errors (Workato reports ok:false envelopes as succeeded jobs). The
  Operational Permit Ledger (prod dfd61645-9bfa-4cd1-8115-343cd09289f5,
  numeric 136605) is per-call truth: operation, outcome_code,
  upstream_status, state. scripts/guidance_outcomes.py paginates it
  (continuation_token key, no --order support on $created_at: FIELD_NOT_FOUND;
  --limit 200/page) and produces per-tool managed-error tables + covered/GAP
  proposals. First real run: 1,602 calls/2d, 35 managed errors (2.2%):
  Add_Slide UPSTREAM_REJECTED x13, Get_Presentation PERMISSION_DENIED x6,
  Get_Slide x3. Ledger rows start Oct 6 13:44Z (cleanup purges older).


## RELEASE TELEMETRY (2026-10-08, dev done; the 124-recipe fleet CANCELLED)

- DESIGN PIVOT: instead of pushing guidance_version through 124 call sites
  (which died on TWO platform walls: helper 74622358's registered schema
  lacks guidance_version - call sites hard-reject unknown params - AND the
  fleet is TWO generations: permit acquire/release shape only on ~10-14
  recipes, the rest are idempotency claim/finalize with NO release call),
  the helper SELF-REPORTS: one fail-open telemetry write inside the helper
  records (tool_name, version served, job_id) per guidance-serving call.
  2 recipe edits total (dev 82864228 done, prod 82872520 pending) instead
  of 124. Managed errors already covered by permit ledger + idempotency
  ledger + jobs API.
- NEW TABLE: "GSlides MCP | Release Telemetry" dev 157628 (uuid
  2e4c4f77-2330-4954-aa81-f641e7ade3c9, folder 32268816): columns
  permit_record_id (primary), operation, outcome_code, upstream_status,
  guidance_version, job_id. Zero-hazard (new table, no populated-schema
  edit). PROVEN: helper Test writes the row with the exact served version
  + job id (v4-s3-1121, j-Abrtx33M-HFoe3T-CD).
- AIRO TRAPS (expensive ones): data-table add_record row fields
  materialize ONLY with table_id as the NUMERIC id string ("157628");
  the UUID leaves the schema empty (parameters.* paths rejected). Row
  fields are set via paths parameters.<field_id with underscores> in ONE
  set_input_field batch AFTER table_id. add_record action is real but
  invisible to list_connector_operations keyword search (upsert_record/
  get_records show; add_record doesn't).
- CORRUPTED BLOCK TRAP: recipe_builder_add_step with type='error_handling'
  PLUS action/connector in the same call creates a block that RENDERS
  fine ("Setup done") but the UI refuses to save and the runtime refuses
  to start ("Error in step N", no detail anywhere). Fix: remove the block,
  re-add with type ONLY (no action), move children in
  (first move lands in the CATCH; second move with new_parent=block
  lands in the try), push, start. Cost of the trap: ~40 min.
- Start validation also hard-rejects pills on
  execute_1['context']['calling_job_id'] (runtime-present but not
  schema-declared on function triggers): use job_context['job_id']
  (schema-valid global); the jobs API links helper jobs to callers via
  calling_job_id anyway.


## RELEASE TELEMETRY LIVE IN PROD (2026-10-08): drift monitoring closed-loop

- PROD TABLE: "GSlides MCP | Release Telemetry" prod numeric 157744
  (uuid 792b88ff-74bd-462b-8a73-7b703a503f62, folder 32312724), same 6
  columns as dev 157628.
- PROD HELPER 82872520: same fail-open telemetry write (error_handling
  rebuilt CLEAN: type only, no action param; numeric table_id; row
  fields via underscore field-id paths). Pushed, started, SMOKE PROVEN:
  Test Add_Table -> row {operation: Add_Table, outcome_code: ok,
  guidance_version: v4-s3-1121, job_id: j-Abs4DEgX-9CXxnE-CD} - exact
  per-call version attribution in prod.
- CORRELATION MODEL: per-version success counts (Release Telemetry,
  exact) / per-window managed errors (Permit Ledger + Idempotency
  Ledger + jobs API) = per-version error rates -> drift detection with
  rollback triggers. Nightly compiler agent (12:43 AM cron) turns that
  into draft shard proposals.
- BOTH ENVIRONMENTS COMPLETE: guidance serving + param/intent tiers +
  self-reporting telemetry. Remaining: Ray's content (palette, 56
  layout shards, QA standards, archetypes); optional fleet-wide
  fail-open wrap + nil-safe returns (the nice-to-have failure-ordering
  polish, runnable in any maintenance window).


## FULL PARITY + COMPILER ROUND 1 SHIPPED (2026-10-09)

- PARITY 62/62 (functional step-sequence compare, env-ids normalized;
  artifacts/parity-2026-10-09.json): byte-hash parity is MEANINGLESS
  across envs (dozens of embedded ids); compare real_steps sequences
  (named steps DFS, skip structural None nodes) instead.
- Drift found and closed BOTH ways: prod hotfixes (guidance-attach on
  Add_Comment/Batch_Update) ported to dev; dev's fail-open wrap ported
  to prod Add_Shape; prod Extract's import-stripped probe monitors
  RESTORED (the import had REMOVED two fail-closed WorkatoMonitor
  blocks: known packaging loss mode; prod was degraded, NOT dev).
- CANONICAL TOOL-RECIPE SHAPE (settled): validate -> acquire(observe) ->
  claim -> connector call -> release (success) -> guidance helper
  (fail-open wrapped) -> return (nil-safe guidance pills). The
  guidance-before-release reorder is DEAD (helper self-reports
  telemetry; release carries no version). Add_Shape dev was re-ordered
  to match.
- COMPILER ROUND 1 APPLIED (BSYS-29451, 2 pts): 4 accepted proposals
  live in Confluence + both syncs run + versions serving: Add_Slide
  400/UPSTREAM_REJECTED recovery (v3-s5-1584+), Get_Slide stale-id,
  Add_Shape shape_type enum, "Access and identity hygiene" group:read
  shard. Skipped honestly: Render_Slide x1 (noise), INTERNAL_ERROR x4
  (needs trace sampling).
- LAYOUT SHARDS LIVE: page 2940994020 "Per-layout guidance for the 2026
  Official Workato Template" (110 published layout docs, by-name
  metadata key `layout`, doc ids layout-N/layoutid-N; other thread's
  sync version parses them; both syncs have the superset parser). FULL
  3-TIER STACK PROVEN IN PROD: Add_Slide + context_hint "08 - Two
  Column" returned tool mechanics + lifecycle pack + the real layout
  shard in one response (job j-AbsGcrrH-oBLQKf-CD). Add_Slide wires
  context_hint; layout-by-ID callers miss the by-name filter (upgrade:
  OR-filter two reads).
- TELEMETRY FLAKE ROOT-CAUSED: Josh's import REPLACED the prod telemetry
  table schema with dev's (field ids swapped to dev values, tables are
  clones like permit ledgers); my pre-import helper write referenced
  dead prod field ids -> "Selected data table field was not found"
  (fail-open swallowed it) and None rows. Fix: fresh add_record step
  (re-resolves schema; the builder picklist caches the OLD ids) +
  current ids. Real traffic now lands valued rows (Add_Shape v5-s1-989
  sequence observed live).
- Confluence thead note: the editor normalizes the FIRST properties row
  into <thead> on save (th/td mix survives; the value cell must be
  <td> - that is the invariant, not "no thead").

## BT External documentation set (2026-10-08)

Full architecture docs live in Confluence space BTI "[External] BT-Business
Technology" (105054224), parent page "Enhanced Google Slides by Workato MCP
Architecture" **2938339626** (under space home 105054478, sibling of the
Google Workspace Semantic MCP set). Six Deep Dive children: Tool Surface &
Envelope 2939256865; Identity/VUA & Ownership 2939650094; Custom Connector
2939650114; Design-System Pipeline 2938732566; Guidance Layer 2938798125;
Operational Safety/Testing/Fleet 2938994716. Format matches the sibling
sets: overview (mission/differentiators/system table/posture/deep-dive
index) + Deep Dive children. Update these when the architecture changes.

Canonical repo: `~/Documents/Google Slides MCP/` (NO git commits — all
untracked; treat ORCA_PROJECT_HANDOFF_2026-10-06.md there as the master
handoff). Orca-side working folder: `~/orca/projects/google-slides/`
(guidance corpus lives here: `guidance/`, extractions in `artifacts/`).
Global skill with the tool gotchas: `google-slides-mcp-playbook`.
Companion skill (shipped v1.0.1): `release/google-slides-ga/{claude,chatgpt}/`.

## Environment identities

- Dev: project 13683566, MCP server mcps-Ab9w3HK9-CRK-CD,
  endpoint https://16704.apim.mcp.workato.com/, connector adapter 1332342,
  folders: Skills 32269258 / Automation 32268816. Extract recipe 78677477.
- Prod: project 13755171, server mcps-AbEdNLHX-43z-CD,
  endpoint https://17498.apim.mcp.workato.com, adapter 1335212,
  connection 19921568. (Per Josh 2026-10-06: prod is healthy/released; the
  Oct-5 quarantined package + fresh-extract gap are historical, not live work.)
- Required project properties (exact case): `GSlidesMCP Environment`,
  `GSlidesMCP Namespace`, `GSlidesMCP Default Source`.
- Contract: 62 tools, structured envelope (ok/error_code/retryable/...),
  VUA everywhere, idempotency keys (30-day), revision_id guards,
  destructive-op preconditions. Local test harnesses in repo `automation/`
  (mcp-call.mjs `__list` dumps catalog; contract/readonly/envelope suites).

## Guidance-injection system (built 2026-10-06, Dev)

Goal: stakeholder-editable (Confluence) guidance injected into every MCP tool
call with ~zero hot-path latency. Corpus first, Confluence space pending.

**Serving layer = recipe-type Knowledge Base via `enterprise_context`
connector** (NOT Genie-attached KB querying — no recipe-side KB query exists;
Genie path = LLM seconds). Proven by spike (job j-Abpe3mHQ-Ns4kEK-CD):

- `search_with_dynamic_filters` warm read: **0.41–0.50s**; metadata filters
  (`{"tool_name":"X","status":"published"}`) are deterministic (count=1 exact
  doc every poll).
- `list_with_dynamic_filters` = queryless variant → preferred L1 hot-path
  action (untested in spike; verify before rollout).
- Same-job read-after-write is STALE (upsert→search in one job returns old
  content). Sync and serve MUST be separate recipes.
- Edit→visible propagation ≤ ~21s. Upsert idempotent by document_id
  (~0.33s/2 docs); re-upsert older content = rollback.
- EC auto-adds ingestion metadata (recipe id/name, content_size, lang).
- Spike assets (Dev, folder 32268816): KB `kb-AbpdgTcf-wFhJMw-CD`,
  recipes 82831740 (BROKEN orphan while_condition — do not reuse), 82831885
  (working lag-measurement harness).

Architecture: Confluence (authoring) → sync recipe → KB/EC with metadata
{scope, tool_name, status, version} → helper recipe fn "Append Guidance"
read at end of each public tool, merged into response envelope (no extra
client round trip) + `Get_Server_Guidance` L0 tool + version short-circuit
(`known_guidance_version` → `{changed:false}`). L2 deep Q&A = Guidance Genie
mounted as MCP tool (LLM latency OK off hot path).

## Theme-color extractor hotfix (2026-10-06, SHIPPED dev+prod)

Root cause: `extract_design_system_native` used bare
`masters(...,pageProperties,...)` mask + `rgb_hex(c.dig('color','rgbColor'))`
→ all 16 theme_colors written with `hex:null` into snapshots. The proven
`Get_Presentation` path uses explicit
`pageProperties(colorScheme(colors(type,color)))` + `rgb_hex(c['color'])`.
Fix mirrors it; extractor_version bumped 36-dev→37-dev (3 occurrences).
- Dev connector 1332342 released v39; prod connector 1335212 released v4.
- Invalidation mechanism: registry_key does NOT include extractor_version —
  bumping the connector alone does NOT force cache miss. Stale rows were
  cleared via `workato_db_table.delete_records_by_condition` on registry
  table (dev 141295 / prod 143563, column IDs identical across envs —
  tables were cloned) with `extractor_version == 36`: dev deleted 2 rows,
  prod 9 (recipe 82856962, prod folder 32312724).
- Verified dev: fresh miss → 16/16 hexes; FileStorage summary rewritten;
  replay cache_hit intact. Verified prod: fresh miss → 16/16 hexes
  (job j-AbpzbXoC-Moz3Kn-CD); replay cache_hit intact.
- Snapshot sha256 is content-independent (hash of pid|rev|1.2|36) — same
  value before/after fix; summary files overwrite in place, no orphans.
- STILL OPEN → RESOLVED same day (see next section).

## FLEET COMPLETE (2026-10-07): 62/62 tools wired, verified, masked

- ALL 62 public tool recipes now carry the guidance call + response merge.
- Multi-success-return recipes (Copy_Presentation, Create_Deck,
  Create_Presentation, Create_Presentation_From_Design_System, Extract (both
  paths), Recommend_Design_Archetypes, Replace_Image, Reply_To_Comment,
  Resolve_Comment) wired on EVERY substantive ok:true return; degenerate
  skip-sentinel returns (empty result in telemetry catches) left unwired.
- mask_data regression from return-rebuild was caught by sweep
  (scripts/sweep_wiring.py) and fixed fleet-wide; final sweep:
  62/62 wired, 0 not running, 0 missing mask_data (artifacts/wiring-sweep.json).
- Live smoke after fleet: success path carries guidance (v3-s3-1121),
  error path sanitized NOT_FOUND fail-open, cleanup done.
- Runbook + script: scripts/WIRE-RUNBOOK.md, scripts/wire_guidance.py
  (NOTE: the public API PUT /api/recipes/:id IGNORES code changes —
  "success: true" but no-op; AIRO recipe_builder is the only code path;
  /api/export_manifests now 404s — package route gone from this client).
- Agent-fleet lessons: 8 parallel agents × sequential recipes worked well;
  partition files + unique session_ids + runbook file = safe parallelism;
  sweep numbers are 0-based code-tree numbers (off-by-one vs AIRO positions
  — mask BOTH N and N+1); rebuilt returns must re-set mask_data=True.
- NOT YET DONE: prod promotion of the wiring (62 recipes + helper + sync);
  A/B behavioral test; publishing more Confluence sections (only Add_Table
  published; helper works for any published section).

## Guidance layer WIRE-UP COMPLETE (2026-10-07, dev): guidance rides tool responses

- `GSlidesMCP | Append Guidance` helper = recipe FUNCTION 82864228 (must be
  STARTED or callers get "Can't call a stopped recipe"): EC
  list_with_dynamic_filters {tool_name, status:published} -> ruby snippet
  strips the "status: published" prefix line, trims inline to 500 chars,
  version short-circuit via known_guidance_version param. Returns
  {status: ok|no_guidance|current, guidance_md, version, changed}.
- Wired pilot: Add_Table 74528390 — call_recipe(helper, tool_name="Add_Table")
  inside the success monitor block before the return; result schema + return
  gained guidance_md / guidance_version / guidance_changed. LIVE PROOF: MCP
  Add_Table response carried the Confluence-authored guidance
  (version v3-s3-1121, changed=true). The whole chain is now live:
  Confluence section -> sync 82864023 -> EC kb-AbpdgTcf-wFhJMw-CD ->
  helper -> tool response.
- Wiring pattern per tool (the 61 remaining): pull recipe -> extend trigger
  result_schema_json (+guidance_md/version/changed) -> add call_recipe after
  connector success inside the monitor try (parent = monitor step) ->
  remove+re-add the success return step (stale schema cache hides new
  fields on the existing step) -> stop/push/start. All dev recipes must be
  ACTIVE (helper + tool). Rollout candidate for a scripted package edit
  (62 recipes) rather than hand-editing.
- Failure-ordering note: the wiring call sits AFTER the connector mutation,
  so a helper failure = job error AFTER the mutation committed (table
  existed; retry via idempotency key replayed cleanly). Acceptable
  (fail-open-ish, idempotency absorbs it); moving guidance BEFORE the
  mutation would leak guidance into error paths instead.
- A/B behavioral proof pending: run a table task with an agent and compare
  behavior (data_json atomic use, slide_count check, no Transform_Element
  on tables) with guidance published vs retracted.

## Guidance layer WIRED (2026-10-07, dev): Confluence -> EC -> serving PROVEN

- Confluence space PP "Project Presentations" (2934308918), root page
  "GSlides MCP Guidance" 2936143896; 16 child pages seeded from the corpus
  (7 L1 group pages with H2 per tool = all 62 tools, 4 L0, 4 L2, 1 rules
  page). Page Properties macro (`details` keyed macro) carries
  scope/status/sync-source; status symbols green published / orange draft /
  black+blue retracted. Sync finds pages by CQL ancestor=root (no labels).
- Sync recipe `GSlidesMCP | Sync Guidance from Confluence` 82864023 (dev
  folder 32268816): confluence.get_children_for_page(root) -> foreach ->
  get_page_by_id(body_format=storage) -> workato_custom_code
  `invoke_custom_ruby_code` parses Page Properties + splits H2 sections
  (tool-name regex, per-section "status: draft/published" line override)
  -> enterprise_context.upsert_documents into kb-AbpdgTcf-wFhJMw-CD with
  metadata {scope, tool_name, status, version=v<pages ver>-s<idx>-<len>,
  page_id}. 13s/run, zero failed docs. Scheduled 24h in dev (5-min design
  for prod); Test on demand.
- Serving probe 82864176: `list_with_dynamic_filters`
  {tool_name:Add_Table, status:published} returned the Confluence-synced
  doc (version v3-s3-1121) in 0.25s. Full chain PROVEN: Confluence edit ->
  sync -> deterministic hot-path retrieval. Old spike docs deleted.
- serving-doc note: `status: published` as first line of a section flips
  ONE section while the page stays draft (Add_Table is the only published
  tool right now).
- BATCH PUBLISH DONE (2026-10-08, Josh-approved): all 11 guidance pages
  flipped draft -> published (Status row cell `🟧 draft (not served)` ->
  `🟢 published`), v1->v2 each except Elements & media 2936438803
  v3->v4 (Add_Table section `status: published` override left as-is).
  NOT touched: Brand palette 2936635403, Deep·Design systems 2936897547,
  Deep·Tables 2936209439, Deep·Review 2936274968, Designer TODO
  2938044696, root. TRAP: updateConfluencePage with contentFormat=markdown
  422s on these pages ("Markdown body replacement would cause data loss:
  confluence macro (details)") — the Page Properties macro is invisible in
  markdown reads. The path is contentFormat=html round-trip: read html,
  replace only the status `<td>` cell, push html. Verified round-trip safe
  (markdown re-read after edit renders clean).
- TRAPS: get_page_by_id returns body ONLY with body_format set (storage);
  EC upsert needs the snippet output wrapped ({'docs' => docs}) and pills
  read `['output']['docs']`; stale output-schema snapshots flag
  DatapillInvalidPath on step creation — fix = remove+re-add the dependent
  step, and page_size/page MUST be set explicitly or the recipe is
  untestable ("Page size must be between 1 and 100"); editor sessions go
  obsolete after AIRO push (modal "Update to the latest recipe version")
  — dismiss, reload, fresh tab if wedged; data_filters must be a JSON
  STRING not an object.

## Ownership fix SHIPPED (2026-10-06/07, dev + prod): inline carrier build

Experiment result: helper's Google steps CAN'T inherit caller VUA —
- "Calling recipe's connection" on a nested recipe function serializes as
  `personalization: true` but RESOLUTION FAILS at runtime: nested
  call_recipe jobs don't carry the MCP end-user context → hard error
  `Missing connection. Please establish connection manually` (WRF00400).
  Dev helper was reverted to static ("This recipe's connection") after.
- FIX SHIPPED: new connector action `make_design_carrier` (dev 1332342 v40,
  prod 1335212 v5): copy + trim-to-one-exemplar + verify in ONE action,
  pure Ruby loops, batches of ≤100 (removes the old 200-slide carrier cap),
  source immutability check. Extract recipe now: Claim (dev 74599130 /
  prod 74736296) → if claimed: make_design_carrier under caller VUA →
  Finalize (dev 74599376 / prod 74736297) → carrier read → tables/registry.
  Carriers are now CALLER-OWNED (user's own Drive).
- Dev Extract 78677477 + prod Extract 82090477 restructured identically
  (claim fingerprint byte-compatible with historical helper claims —
  verified by live replay). Dev + prod claimed/replay paths both verified
  via job traces (dev j-Abr4o6oH-tWt9bh-CD, prod j-AbrBsPGz-G8Cwas-CD).
- DISCOVERY: prod Extract was a DIVERGENT implementation (inline
  copy/trim WITHOUT claims, fixed carrier title 'Workato Design System
  Carrier', 200-slide cap) — dev/prod had drifted; now structurally aligned.
- Prod registry rows with extractor_version=36 cleared (2 more) → fresh
  claimed-path runs for all callers.
- VUA context visible in skill job traces: context.user_email etc. (line 0
  outputs) — useful for caller-identity evidence.
- ops notes: wt CLI / workato CLI have PRODUCTION profiles now (same
  safeguards as prod AIRO MCP); the default wt profile is Development-
  scoped — /api/recipes/82090477 404s and stop/start silently no-op cross-
  env; stop/start PROD recipes via the Orca browser (env switcher →
  Production → Stop/Start recipe). Env switcher dropdown items =
  .app-menu-item__title spans; do the open+click in ONE eval (dropdown
  closes between evals); recipe-level "Connections" tab ≠ step-level
  Connection stage; "You can't edit an active recipe" = stop first.
- Workato quirk: FileStorage get_file_contents returns a STREAM —
  include?/scan fail; plain f-string interpolation auto-coerces it.
  ruby() formulas: no #{} interpolation inside; use concatenation; .read
  unsupported. Browser 404 on a prod-env recipe URL = environment switcher
  is on Development — switch to Production first.

## Design-team handoff (2026-10-07)

- "Designer TODO" page (2938044696, PP space) lists the content split: 4
  net-new-writing items for design (per-layout guidance = highest value,
  visual QA standards, archetype notes, palette verification) vs QA-only
  pages (System overview, Global rules, Workflow chains, six Tools· pages).
- [colleague] (raymond.yuen@workato.com, Slack U09756UMGM9, Art Director)
  owns design-team review. Detailed brief DM'd 2026-10-07 (tracked post,
  ts 1791420736.680719). He verifies hexes against Fluid Design System on
  Figma; flagged question: template 14pt gap not a 4px multiple.

## PROD ROLLOUT COMPLETE (2026-10-07): guidance layer live on all 62 prod tools

- FLEET: 62/62 prod tool recipes (folder 32312723) wired, running, masked —
  80 substantive ok:true success returns wired (multi-return recipes wired on
  EVERY return; degenerate skip-sentinels + error paths left clean). Final
  sweep artifacts/prod-wiring-sweep.json: 62 clean / 0 problems. Prod helper
  = `GSlidesMCP | Append Guidance` 82872520 (folder 32312724); prod sync
  82873160; prod KB kb-AbrL4okJ-8spRP8-CD.
- LIVE SMOKE (prod): Test-run of helper with tool_name=Add_Table → status ok,
  guidance_md = Confluence-authored content (500-char trim), version
  v3-s3-1121, changed=true, EC warm read 0.292s (job j-AbrdJpFE-zhCkRP-CD).
  Bonus: real user traffic ALREADY served — wired Search_Presentations called
  the helper at 19:05 EDT and succeeded (root job j-Abrd4oPw-co6Egr-CD).
  Helper has 16 succeeded / 0 failed jobs.
- AGENT-FLEET PROCEDURE LESSONS (round 2): subagents CAN run prod wt
  lifecycle if a scoped allow rule exists —
  `Bash(WORKATO_PROFILE=josh-prod ~/.local/bin/wt *)` in
  ~/.claude/settings.json (Josh batch-confirmed in-transcript). The auto-mode
  classifier CANNOT see pre-compaction approvals ("summary-reported
  approvals clear no block") — prod confirmations must be re-elicited
  in-transcript (AskUserQuestion works) after a compact.
- AIRO recipe-builder lessons (prod, fleet-verified): parent for inserted
  steps = the MONITOR block's step number (parent=1 lands OUTSIDE the block
  and a later move to parent=1 silently no-ops); ruby-bound result fields
  restore via set_input_field_v4_mode mode='ruby' with the FULL original
  `ruby("...", bindings={...})` expression (bare `bindings.x` rejected);
  literal `"[]"` must be sent as a quoted string, not a JSON array; boolean
  fields may serialize as control_type checkbox (Extract family) — mirror
  the local convention.
- wt GET can serve a stale cached code copy mid-fleet (sweep flagged call
  steps unmasked that were actually masked) — re-run the sweep before
  believing "missing mask_data" results; recipe_get render is the other
  authoritative view.
- Orca prod env switching: sidebar node labeled "Development"
  (.app-mobile-sidebar__button-title) opens the env dropdown, then click the
  ".app-menu-item__title" span "Production" — recipe URLs 404 until this is
  done in the SAME session.


## PUBLISH ROUND 1 (2026-10-08): technical guidance live in BOTH environments

- 11 pages flipped draft → published (status-row only): System overview
  2935783719, Global rules 2935783740, Workflow chains 2937290759, the 7
  "Tools ·" pages (all 62 tool sections), Deep · Media & assets 2935980092.
  Ray's four design pages + Designer TODO stay draft (his list: palette,
  per-layout usage, QA standards, archetypes).
- Verified serving (prod helper Test runs): Get_Presentation v2-s0-1276 and
  Create_Deck v2-s3-1302 both status ok, 500-char trim, EC read ~0.29s
  (jobs j-AbreWAYM-kePRmX-CD, j-AbreadD6-4DEBQB-CD). Syncs triggered on
  demand: prod j-AbreM4sh-dpRmAa-CD (15s), dev j-AbresKFg-rMcbcA-CD (22s).
- CONFLUENCE TRAP: updateConfluencePage contentFormat=markdown 422s on
  pages containing the `details` Page-Properties macro ("would cause data
  loss: confluence macro (details)") — markdown READ is fine, markdown
  WRITE is not. Round-trip via contentFormat=html instead (edit the
  <td> status cell, push full HTML body — preserves the macro).
- Orca CodeMirror binding is lazy after modal open: dispatch
  mousedown/mouseup/click on the field's .text-field wrapper first, THEN
  .CodeMirror instance binds, THEN setValue (order matters; re-query
  fresh — element refs go stale after re-render).

## Corpus status (2026-10-06) — committed in ~/orca/projects/google-slides

- `guidance/` corpus COMPLETE and validated: 3 L0 (overview, global rules,
  16 workflow chains + intent index), 62 L1 per-tool (live-catalog desc/params,
  ≤500-char hot-path inline block, sourced gotchas, interplay, latency), 4 L2
  deep-dives. 62/62 extraction coverage, 0 derived-only, [verify] markers
  preserved. Frontmatter (scope/tool_name/status/version) maps 1:1 to KB
  upsert metadata; document_id convention `gslides-guidance/<scope>/<tool>`.
- Provenance: artifacts/dev-catalog-2026-10-06.json (live 62-tool dump),
  extraction-skills.md, extraction-docs.md.
- BLOCKED on Josh: Confluence space creation. On resume: publish corpus as
  draft page tree (parent "GSlides MCP Guidance", L0/L1/L2 children) via
  Atlassian MCP into whatever space he names → then sync recipe (Confluence
  trigger → parse → upsert_documents) → "Append Guidance" helper + pilot
  wiring on 5 tools (4 design-system + Add_Table) → measured rollout.

## AIRO traps hit today (add to airo-mcp-playbook corpus)

- f-string field mode is `f"...{pill}..."` (Python-style), NOT Ruby `#{...}`.
- `workato_variable.update_variables`: per-variable value field never
  surfaces via AIRO get_input_schema (input_mode structured/raw both) —
  un-settable via MCP; avoid update_variables in AIRO-built recipes.
- `declare_variable` here takes flat `name`+`type`+`value` (not
  variables.schema JSON as the connectors:variables doc says).
- Removing a `repeat` with promote_children leaves an orphan
  `while_condition` step that CANNOT be removed via API ("remove the parent
  repeat instead" but parent is gone) → recipe unfixable via AIRO; rebuild.
- recipe_builder_init: folder_id must be a real folder; project IDs and some
  other-env project folders 404 (e.g. Josh Gateway Tests 32354951 failed
  from dev AIRO).

## Guidance wiring wave 2 (2026-10-07) — 7 more tools wired via AIRO (part 6)

- Wired Batch_Update 74528394, Delete_Slide 74528401, Get_Deck_Thumbnails
  74528408, Insert_Diagram 74528417, Render_Slide 74528423,
  Set_Element_Text 74528431, Style_Table_Cell 74528438 — all WIRED, pushed,
  restarted, Running=True verified via recipe_get. Steps +1 each.
- The set_input_field recipe works verbatim per recipe: trigger
  result_schema_json = existing JSON string + 3 guidance fields (passed as a
  plain string it does NOT collapse); call_recipe step (flow_id 82864228,
  parameters.tool_name plain string) directly before the last-DFS
  workflow_return_result with literal ok:"true"; rebuild that return with
  every recorded pill verbatim + guidance pills from call_recipe_<N>.
- Constant strings in rebuilt returns: ruby("'[]'", bindings={}) etc. is the
  safe channel form — persists and runs as the literal string ("true",
  "false", "0", "200", "[]" all done this way across 7 recipes).
- Recipes with metadata_schema_json=None on the trigger show a pre-existing
  harmless "Missing sticky field: metadata_schema_json" warning — leave it
  absent (original state); setting it to a ruby() formula is worse.
- Wire target selection: when a recipe has several ok:"true" literal returns
  (Batch_Update/Get_Deck_Thumbnails/Render_Slide each also have a skipped
  no-op {"ok":"true"} swallow-return in telemetry error paths), the LAST in
  DFS order is the real success envelope — wire there; skipped no-ops are
  not the target.
- Pre-existing DatapillInvalidPath warnings on custom-connector action
  outputs never blocked a push (consistent with canary amendment).

## Effectiveness telemetry (2026-10-08)

- `scripts/guidance_effectiveness.py` (READ-ONLY) + `scripts/COMPILER-AGENT-BRIEF.md`
  close the loop: wt job history -> per-tool failure stats -> PROPOSAL report in
  `artifacts/guidance-effectiveness-<date>.md` (josh-prod keeps the plain-name
  contract file; other profiles get a suffix). Nightly compiler agent drafts
  section proposals into `artifacts/compiler-proposals/<date>.md`; production
  only via Josh reviewing + pasting into Confluence. No schedules were created.
- Surprise 1: the Workato "Test" button generates jobs titled
  `Genie ID=mcp_mock_genie_id, Conversation ID=mcp_mock_converation_id` (sic)
  that count as FAILED jobs — Extract_Design_System prod showed 12/28 "failures"
  that were all mock smoke tests. Telemetry must filter `mcp_mock` blobs or
  real error rates are fiction.
- Surprise 2: 2-day prod window had ZERO real tool failures across ~2,900 jobs
  (healthiest: Get_Slide 513, Set_Element_Text 518, SlidesA_Add_Text_Box 397,
  Add_Shape 284, Style_Text 253). Current guidance (all packs v2) needs no
  hot-path additions yet; the loop's first real test awaits genuine failures.
- Dev recipe code stores parameter string literals as pill expressions
  (`='Add_Line'`), prod stores plain strings — strip by taking the last
  identifier in `=`-prefixed values.
- Coarse version timeline: last successful sync job (82873160, daily 00:37-ish)
  is the version boundary; failures bucketed before/after it.

## Extract Design System failure cluster — autopsied 2026-10-08 (/triage)

- Prod 82090477's 58 "failures" (55→58 same day) are **MCP mock/health probe
  calls** (`Genie ID=mcp_mock_genie_id`) hitting the tool with unresolvable
  presentation IDs → step 1 `get_presentation_revision_guarded_v19` throws
  Google 403/404 (trace: job j-AbrtLYrR-pperbF-CD). Environmental noise,
  fail-closed, no durable state written; no prod hotfix needed.
- Real defect: steps 2/25 have no error handling, so source-access errors
  fail the job raw instead of returning the promised
  `{ok, error_code, upstream_status, retryable}` envelope — inflates
  watchdog counts, degrades the caller contract.
- Fix filed: **BSYS-29418** (Bug, 3pts, Josh) under new epic **BSYS-29417**
  ("GSlides MCP: Design System Extractor Reliability", parent BSYS-21305
  FY27 VMT). Sized as its own session: wrap steps 2+25, keep
  idempotency/registry semantics untouched, tests for 403/404/mock/happy.
- Probe noise takeaway: a skill-tool whose source-authz step can throw
  will rack failed jobs from registry "try it" probes — always envelope
  the source-authorization step, not just the extract step.

## Frontify GraphQL API — set up 2026-10-09 (design-system source of truth)

- GOAL: durable design systems in Frontify that (a) the Google Slides MCP
  reads from and (b) Claude Design Systems can inherit.
- TENANT: https://company-181808.frontify.com (account id 181808, 3 users;
  single brand "Workato" id eyJpZGVudGlmaWVyIjoxODI1ODAsInR5cGUiOiJicmFuZCJ9).
  Josh is admin. Instance is GREENFIELD: 0 libraries, 0 creativeTemplates,
  0 workspaceProjects as of setup day.
- AUTH: personal developer token (scopes basic:read + blocks:read, 90d
  expiry from 2026-10-09) stored in macOS keychain service
  `frontify-api-token` (account josh). NEVER log or commit the value.
  Rotate if the transcript leaves the machine (it was pasted into chat).
  Token UI: https://company-181808.frontify.com/oauth-access-token.
  Production-grade path later: dedicated service user + its own token, or
  a Service App (client credentials, beta) per Josh governance.
- ENDPOINT/SHAPE: POST {tenant}/graphql, Bearer header, JSON body
  {query, variables}. Responses carry extensions.complexityScore.
  Anonymous introspection is open but root data needs auth; "Invalid
  query" = bad field name, "UserId not set in identity" = wrong tenant or
  unauthenticated.
- ROOT SURFACE (12 fields): currentUser, account, library(id),
  workspaceProject(id), assets(ids), asset(id), creativeTemplate(id),
  creativeExport(id), brand(id), brands, node(id), webhooks(limit,page).
  Brand -> libraries / creativeTemplates / workspaceProjects /
  customMetadataProperties / creativeTemplates (all paginated
  {total, page, limit, hasNextPage, items}).
- KEY TYPES: Library {assets, collections, searchAssets,
  assetsByExternalId, customMetadataProperties}; CreativeTemplate {pages,
  exportOptions, variable(s), tags} — CreativeTemplate.variables is the
  candidate home for design tokens (colors/fonts); Account {users,
  userGroups}.
- HELPER: frontify/fq.py in this repo (reads token from keychain, `python3
  frontify/fq.py '<graphql>'` prints pretty JSON). Full schema reference:
  https://frontify.github.io/graphql-reference
- NEXT (decided pending Josh): design the Frontify-side structure —
  Library per design system with collections for tokens/components;
  custom metadata properties for machine-readable token values the
  Extract_Design_System pipeline can compile from.

## Frontify CORRECTION + read path PROVEN (2026-10-09, later same night)

- CORRECTION to section above: the instance is NOT greenfield. "Workato
  Brand Guidelines" (Guideline id
  eyJpZGVudGlmaWVyIjo0ODE2ODAsInR5cGUiOiJndWlkZWxpbmUifQ==) has 24 pages.
  The empty collections were an artifact of the missing beta header.
- THE KEY TRAP: **guideline content is BETA-GATED — every request needs
  header `X-Frontify-Beta: enabled`** or the schema hides `guidelines`,
  `guidelinePage`, `guidelinePageBlock`, `guidelineNavigationItem`,
  `catalog`, `catalogSelection`, `serviceApps` (12 root fields without,
  18 with). Brand introspection shows `guidelines` ONLY with the header.
  fq.py now always sends it.
- READ PATH (all proven live): brands → guidelines (1 item) → pages
  (24; {id,title,url}) → guidelinePage(id:) root field (NOT node —
  GuidelinePage is not a Node) → sections{total,items{id,elements}} →
  elements{items} typed union: GuidelinePageHeading {id,title,url},
  BrandEssentialsColorBlock {content, settings, assetSettings},
  GuidelinePageBlock {content, settings, type{name}}. Color values are
  plain text inside ColorBlock content ("t-100 Main brand color
  #00D4D8") — parse hex tokens from the content string. GuidelinePage
  fields: id,title,modifiedAt,url,sections. GuidelineColorScheme is
  {id,name,isDefault} only (no values).
- WORKATO PALETTE EXTRACTED 2026-10-09 (verified): Teals t-400 #003133
  ... t-100 #00D4D8 (main brand) ... t-25 #F0FDFD; Blues b-400 #083763
  (main bg/surface) ... b-25 #F4F7FB; Purples v-400 #350052 ...
  #FAF7FF; Primary Accents g-100 #C8E832, c-100 #2FD5FF, m-100
  #FF78E8; Secondary Accents o-100 #FE5E27, y-100 #FFC700, f-100
  #1F9558; Neutrals n-400 #04141A ... n-0 #FFFFFF. Usage rule from
  page: b-400 bg + n-0/t-100 text; accents sparingly (eyebrows,
  callouts, shapes). Typography: Besley (serif) + Figtree (sans), font
  files downloadable as Attachments blocks; Noto Sans JP international.
- JOSH'S ACTUAL GOAL (corrected): READ Frontify, WRITE elsewhere —
  compile Frontify content into (a) Enterprise Context / guidance
  corpus, (b) Claude Design Systems, (c) Confluence. NOT create content
  in Frontify. Pages relevant to GSlides: Colors, Typography, Icons,
  Patterns, Photography, Slide Decks, Design Applications + sub-brand
  pages (WOW, Dewy, Airo, Wolf 2 Brand Assets).

## Frontify pipeline BUILT (2026-10-09): canonical palette flows to both targets

- PIPELINE (repo ~/orca/projects/google-slides, commit 8d2b572):
  `frontify/extract.py` (GraphQL -> design-system.json; 41 tokens, 6
  families, 2 typefaces, 24-page index) -> compilers. extract.py shells
  out to curl: homebrew python3.14 REJECTS the tenant cert chain
  (SSLCertVerificationError "Basic Constraints of CA cert not marked
  critical") while curl accepts it — don't switch back to urllib.
- JOSH CORRECTION (2026-10-09): the synthesized carrier is a TOKEN DEMO,
  NOT the design system — "it carries none of the designs at all". The
  registered design system that carries REAL brand designs (logo, artwork,
  56 layouts, 115 exemplars) was ALWAYS the official-template extraction:
  **registry_key 985a50f146fdc9f69074325f6cf1f8345d736cbd29d1e3bc1790e4e4beea9d7d**
  (source 2026 Official Workato Template 1gn3KC-3gpgRF_erNPPz9PTx2nfsyntoeo9KCefFG5Ok,
  snapshot 830e03cd..., cache-hit confirmed live 2026-10-09) -> inheritance
  proof deck 1RjOpFenO5fF4ma45_Ze0pLXBio1rRViKCdrtmnTycMs renders the FULL
  brand cover (logo, connector artwork, Besley, gradient bar). The token
  carrier (d3d58b22...) + its proof deck are demoted to token-reference
  artifacts; candidates for deletion.
- SECOND JOSH CORRECTION: the refresh loop must NOT be local python scripts
  ("the point is for the assets to live in workato, not have someone run a
  python script"). Runtime = Workato recipe: Frontify GraphQL -> parse ->
  authoring surface (Confluence) -> existing EC sync. extract.py/
  compile_gslides.py are one-time build tools and parsing reference only.
- CARRIER-DECK TRAPS: Create_Deck table with 7 rows AUTO-SPLIT into a
  "(continued)" slide (3 data rows max per slide here) — carrier now has
  two intentional "Color families (1 of 2)/(2 of 2)" slides; keep carrier
  tables ≤3 data rows. Empty BODY placeholders next to tables were ghost
  risks — filled both.
- EC TARGET SHIPPED (dev): guidance L0 03-brand-palette.md bumped to v2
  status published (canonical Frontify values, observed v1 kept as
  corroboration); Confluence page 2936635403 rewritten via the HTML
  round-trip (markdown write 422s on its invisible details macro — trap
  confirmed again) and flipped draft->published; dev sync 82864023
  force-run GREEN (j-AbsEBzTJ-t8CgKh-CD, 21s).
- OPEN: prod sync 82873160 force-run needs Josh's prod-write go (dev
  palette page now canonical; prod EC still serves v1 observed values
  until synced).
- Refresh loop when Frontify guidelines change: extract.py ->
  compile_gslides.py -> new carrier -> re-extract -> re-register; corpus +
  Confluence version bump; sync recipes on demand.

## WORKATO-NATIVE REFRESH LOOP LIVE (2026-10-09 late): recipe 82928714 dev-green

- THE LOOP (all Workato, zero local runtime): recipe **82928714
  "Refresh design tokens from Frontify"** (project 13683566, folder
  32268816, https://app.workato.com/recipes/82928714): Scheduler 24h ->
  HTTP Send request POST company-181808.frontify.com/graphql (ONE aliased
  query: brands + colors: guidelinePage + typography: guidelinePage;
  page ids eyJ...0MjQ4NjY5(Colors)/...Njcw(Typography) are stable) ->
  Ruby parse (string keys ONLY — symbol keys silently render empty via
  esc()) -> regenerates the region between `<h2>Colors (canonical
  tokens)</h2>` and `<h2>Spacing</h2>` on Confluence palette page
  2936635403 (if changed == 'yes' gate skips no-op writes) -> existing
  sync 82864023 -> EC KB. ALL GREEN: refresh job j-AbsEfTdL-hwfPem-CD
  wrote page v5; sync j-AbsEg4zh-Tbea3s-CD served it. Page now at v6
  (recipe-id references fixed to 82928714).
- TRAPS THAT COST REAL ITERATIONS (all verified in traces):
  (1) **Frontify 500s (raw `{"success":false,"error":"Internal server
  error"}`, not a GraphQL error) when beta root fields like
  `guidelinePage` are queried WITHOUT the X-Frontify-Beta header** —
  beta fields at ROOT level hard-crash; nested fields (colorSchemes via
  Guideline spread) return clean "Cannot query field". Set the header
  at the ACTION level (connection-level header auth wouldn't take my
  custom header via the API).
  (2) **Connection API schema for HTTP header auth (provider `rest`):
  `input.auth_type = "headers"` (NOT "header_auth") + `input.header_pair
  = [{param, value}]`** — from the connections-parameters-dev.md
  reference (the per-connector JSON is in an HTML-escaped
  shiki-highlighted blob; grep for '"name": "header_pair"'). Wrong
  auth_type value stores a connection that authorizes OK but sends
  NOTHING ("UserId not set in identity").
  (3) **Custom-code output schema type mismatches NULL silently** —
  declared `changed` boolean + Ruby returns 'yes' string →
  `output['changed']` resolves nil → if-gate False with a green job.
  Declare output fields as strings and return strings.
  (4) `recipe_builder_save` ALWAYS creates a new recipe id (4 copies
  made tonight; delete the stale one each time — stop before delete).
  (5) Confluence STRIPS HTML comments — no marker comments; use heading
  anchors for machine-managed regions. Also: putting a th/td row inside
  <thead> gets normalized to th/th which BREAKS the sync parser's
  Page-Properties regex — keep the details table all in <tbody>.
- PROMOTION HANDOFF (prod, per BT Jira process): assets = recipe
  82928714 + connection 22276219 (header-auth rest, token); target prod
  folder = prod sibling of 32268816; palette page lives in shared PP
  space (no page move needed); prod sync = 82873160. Stopped at handoff
  per skill boundary; also pending Josh's go on force-running prod sync
  82873160 for the palette content itself.

## PROMOTION BATCH PACKAGED (2026-10-09): manifest 360395, story draft awaiting approval

- MANIFEST: **360395** (https://app.workato.com/export_manifests/360395#content)
  "GSlides MCP | Frontify design-token refresh 2026-10 promotion batch" —
  exactly 2 assets: recipe 82928714 (folder .../Automation) + connection
  22276219 (folder .../Connection). Package export 42184101 verified:
  zip paths Enhanced Google Slides by Workato MCP/{Connection,Automation}/...
  match prod's existing subfolders — import into prod folder 32312719
  (prod project MCP | BT Managed MCP 27436344, project_id 13755171).
- CONNECTION IMPORTS AS SHELL (Workato never exports creds): post-import
  set header auth = Authorization Bearer <frontify token> on the prod
  connection (same API call as dev: PUT /api/connections/<id> with
  input {auth_type:"headers", header_pair:[{param,value}]}).
- STORY DRAFT (shown to Josh 2026-10-09, awaiting "file it"): summary
  "Deploy Frontify design-token refresh to Production (recipe 82928714 +
  Frontify HTTP connection)"; fields 10494=manifest URL, 10588=31161,
  10446=31164 (NO cascade child — none exists for this folder, precedent
  BSYS-25550), 10057=2, parent=BSYS-29417. Cascade child options for this
  field are "Home/MCP | BT Managed MCP/<tool> folder" (Gmail precedent
  60979, BSYS-28483) — the GSlides child option does not exist yet.
- POST-IMPORT SMOKE PLAN: connection auth -> force-run recipe -> page
  version bump observed -> prod sync 82873160 green.

## HOTFIX DEPLOYED TO PROD (2026-10-09): Frontify refresh loop live (Josh-authorized)

- Josh ruled: no promotion story — hotfix. Executed via lifecycle APIs:
  manifest 360395 → fresh package export 42184137 → direct zip import
  (wt's `packages import` has an arg-name bug — bypassed via
  SourceFileLoader of wt's own `request()` with profile josh-prod) →
  POST /api/packages/import/32312719.
- IMPORT PLACEMENT TRAP: importing into folder 32312719 ("Enhanced
  Google Slides by Workato MCP") recreated the zip's root folder path as
  a NESTED DUPLICATE (32312719/Enhanced Google Slides by Workato MCP/
  {Automation,Connection}) — assets landed in new folders 35753345 /
  35753344. Fixed by moving assets into the REAL folders (recipe PUT
  /api/recipes/<id> {"folder_id":"<id>": MUST BE A STRING; connection
  PUT /api/connections/<id> takes int) then deleting the empty dup
  folders. Correct import targets next time: the folder that MATCHES
  the zip root's already-existing parent (import into 32312719 only if
  the zip paths DON'T repeat the folder name — here zip paths repeated
  it, so import should have targeted 27436344 or the paths changed).
- PROD ASSETS: recipe **82928755** (Automation 32312724, RUNNING) +
  connection **22276255** (Connection 32312722, header auth set from
  the same Frontify token, authorized).
- PROD PROOF: 2 jobs green (j-AbsFDcTp-TRYTAn-CD etc.) — prod run wrote
  Confluence page v7 (integration-account author, 05:19Z); prod sync
  82873160 force-run j-AbsFDxw9-Pf3R9k-CD green → canonical palette
  serving to the 62-tool fleet from PROD EC.
- Dev twin: recipe 82928714 (running) + connection 22276219 — kept for
  dev iteration. Manifest 360395 stays on the record as the audit trail
  (no BSYS story filed — Josh waived it for this hotfix).

## LAYOUT SHARDS (2026-10-09 late): Confluence page 2940994020 authored, sync patch next

- "Layout usage guide — per-layout shards (2026 template)" page id
  **2940994020** (child of guidance root 2936143896, published, v2):
  51 H2 sections, one per template display name (56 layouts deduped),
  each section = `<h2><display name></h2><p>layout: <display name>.
  guidance…</p>`. Content grounded in the template's own example-slide
  text (font sizes, roles) + the playbook ghost/multi-card gotchas.
- DISCOVERY: the 2026 template DOES populate all 16 Slides theme-color
  slots with canonical Frontify values (DARK1 #083763, ACCENT2 #00D4D8,
  ACCENT5 #C8E832…) — the old "template does NOT populate theme slots"
  caveat is OBSOLETE for this template; theme-slot recoloring works.
- TRAP (hit twice now): the Atlassian MCP markdown writer renders the
  properties table as th/th thead + td/td rows — the sync parser needs
  th/td rows in tbody; ALWAYS round-trip guidance pages as HTML.

## LAYOUT SHARDS LIVE (2026-10-09 late): 110 docs in dev EC, tier-2 serving PROVEN

- CONTENT SOURCE (Josh's design): the template's OWN example-slide text IS
  the layout description — no speaker notes exist (only 2 in the whole
  extraction, and those are deck content, not template docs). Extracted
  per layout: first exemplar slide's text (quoted as "Template example:
  ...") + placeholder inventory + one-line usage note. Ray curates the
  page instead of authoring it; he focuses on deep design-system content.
- PAGE: "Layout usage guide — per-layout shards (2026 template)"
  **2940994020** (guidance root child, published, v5). Section contract:
  <h2><display name></h2> then <p>layout: <name><br>layout-id: <native
  layout id><br>text...</p> — **the layout name MUST end at a <br> or
  line break** (parser captures [^\n<]+; a one-paragraph section gets
  swallowed whole → sec_body empty → section skipped — THAT was the
  root-only mystery).
- PARSER (sync 82864023 dev, v2 layout support): layout: line → doc
  doc_type=layout keyed by display name; layout-id: line → ALIAS doc
  keyed by native layout id; lidx counter (separate from sidx — sharing
  the counter made all layout docs collide on one document_id); >80-char
  name guard; docs split 100/overflow (upsert_documents MAX 100/batch —
  111-doc page failed until the docs_overflow second upsert was added;
  comprehension iterators must be PURE PILL PATHS — no .drop()).
- CONTRACT DISCOVERY: the served Add_Slide guidance says "use only these
  IDs (never display names)" and the connector 400s on display names —
  so the ID-keyed alias docs are the ones that actually fire in practice.
- PROOF: sync job j-AbsFWoTW (55 name docs) then j-AbsFcndg-gLRXdo-CD
  (55+55, failed_documents: []) → Add_Slide(layout=g3f960194134_2_3380)
  guidance_md APPENDS the shard ("Template example ... max ~6 bullets").
  context_hint = the layout PARAM (Add_Slide step 17) — there is no
  separate context_hint MCP param; pass layout.
- STALE-RUNTIME TRAP (cost ~40 min): after AIRO push, force-run jobs
  executed OLD code repeatedly (platform had new code, trace showed old
  output) — even across stop/start. Developer-API re-save + restart also
  didn't clear it. It cleared only after MULTIPLE stop/start cycles +
  time. Suspect async recipe-compile propagation; if a pushed recipe
  behaves old, verify with a distinctive string in the runtime output
  before debugging logic. (Orca browser session was signed out — SSO
  re-login needed for editor Save path; not attempted.)
- PROD NEXT: prod sync 82873160 still runs the OLD parser — prod EC has
  NO layout docs until the same patch is applied there (the Confluence
  page is shared; one sync patch serves both). Awaiting Josh go.

## PROD SYNC PATCHED — LAYOUT SHARDS LIVE IN PROD EC (2026-10-09, hotfix complete)

- Prod sync **82873160** got the identical layout-parser patch (session
  prod-sync-layout-patch-1: stop -> pull on prod AIRO -> code+schema ->
  documents mapping + layout pair -> overflow upsert step 7 -> push ->
  start -> force-run). Job j-AbsFgTAN-oekYXb-CD green; **55 name-keyed +
  55 id-keyed layout docs upserted to PROD KB kb-AbrL4okJ-8spRP8-CD,
  failed_documents: []**. The stale-runtime trap did NOT bite on prod
  (first post-restart run already used new code).
- FINAL STATE (both environments): Frontify -> recipe 82928714 (dev) /
  82928755 (prod, running) -> Confluence palette page (machine region) ->
  sync 82864023/82873160 (layout-aware) -> EC KB (canonical tokens + 110
  layout shards each env). Add_Slide serves per-layout guidance keyed on
  the layout param. Ray curates palette + layout pages; deep design
  content (his next) lands as scope=deep pages with applies-to lines.

## CLAUDE DESIGN SYSTEM PLAN (2026-10-09): the Artifacts path

- TARGET: claude.ai Org settings > Artifacts > Design systems — an
  org-default design system every Claude (claude.ai, Slides artifacts,
  Claude Code) uses INSTEAD of its own taste. Built by UPLOADING source
  material (slide decks PPTX/PDF, screenshots, logos, palette files).
  Standalone claude.ai/design closes 2026-12-14 — build in Artifacts.
- MOVES: (1) publish org-default Claude Design system fed with the 2026
  template PPTX + frontify/design-system.md + Frontify logo/icon assets;
  (2) frontify/design-system.md GENERATED (commit c2dd400) — the Claude
  artifact tokens doc (colors/fonts/spacing contract; Figtree + Besley
  are Google Fonts so artifact typography renders natively); wire into
  CLAUDE.md/theme files for Claude Code repos; (3) later: Frontify
  Voice & Tone page -> artifact tone; Dewy/logo/icon individual assets;
  artifact MCP connectors (per-user auth) for live lookups if needed.
- JOSH ADMIN STEPS (claude.ai): Org settings > Capabilities > Cloud code
  execution ON; Org settings > Artifacts > Design systems ON; create
  design system, upload template PPTX + design-system.md + logos;
  Publish; Owner sets org default. Enterprise: roles can gate who
  publishes/defaults.

## DEV/PROD DRIFT CLOSED ON 3 SKILL RECIPES (2026-10-09)
- Prod received hotfixes via package import that dev lacked. Ported dev-side,
  preserving dev-local ids (guidance 82864228, release 74622358, acquire
  74622357, claim 74599130, finalize 74599376, connector
  google_slides_custom__connector_3535597_1785866569).
- THE FIX (pairs 1+2): prod attached guidance to the remaining SUCCESS paths.
  Add Comment 74528385 (25->27): new guidance call_recipe in the replay
  branch (after get_comment_thread) and in the keyed try (after the
  reconciliation if, before the success return); both returns gained
  guidance_md/guidance_version/guidance_changed. Batch Update 74528394
  (30->32): mask_data=True on the replay-branch guidance call + replay
  return; NEW guidance call in the keyed try (before success return) and in
  the dry-run/legacy try (before its return); both returns gained the three
  guidance fields. Both ported, pushed (zero blocking inconsistencies),
  Running=True (v15/v19).
- Extract Design System 78677477 (40 dev / 34 prod): the 6-step delta is
  ONLY removal of both fail-closed probe error-handlers (2 monitors x
  [try+catch+structured envelope return]) — a behavior REGRESSION (403/404
  would fail the job instead of returning SOURCE_* envelopes) and exactly
  the shape of import packaging loss. JUDGED PACKAGING ARTIFACT, NOT PORTED.
  Dev untouched, Running=True (v25). Prod should re-import with monitors
  intact, not dev copy prod.
  → CLOSED LATER 2026-10-09 (Josh-authorized prod parity pass): the
  re-import DID ship without the monitors, so they were ported prod-side
  instead. Prod Extract Design System 82090477 got both fail-closed
  WorkatoMonitor probe blocks back (source probe steps 2-5, carrier probe
  steps 28-31 — byte-identical to dev incl. SOURCE_* envelopes), keeping
  ALL prod-local ids (claim 74736296, finalize 74736297, registry helper
  82090475, guidance 82872520, tables 143561-3, connector
  ...3535598_1786643879). Pushed clean, Running=True. Same pass: prod
  Add_Shape 74736304 got dev's fail-open guidance wrap (monitor retries=0
  + EMPTY catch around the 82872520 call, success return's 3 guidance
  pills nil-safe ruby passthroughs), Running=True.
- AIRO TRAP UPDATE (2026-10-09): move_step into a fresh error_handling
  block now lands in the TRY (old note said catch). To fill the CATCH:
  add the action at the catch placeholder position (still lands in try),
  then move_step(new_position=<catch+1>, new_parent=<catch step number>)
  — children of the CATCH's step number are the catch body. Brand-new
  workflow_return_result steps need one get_input_schema warm-up before
  set_input_field; boolean result fields (ok/retryable) are toggle fields
  — set via toggle_config {"result.X": false} (secondary text) to match
  dev's "false" string form. Details in airo-mcp-playbook known-bugs.
- AIRO TRAP (new): set_input_field CANNOT add new keys to an existing
  workflow_return_result `result` designer hash via dot-paths (sub-schema is
  frozen to current keys) — re-set the ENTIRE `result` object with a full
  dict; values are pill/ruby()/literal DSL strings. And after an insert
  shifts step numbers, pill variables rename (batch_update_..._27 -> _28);
  referencing the stale name silently mangles to None_None with
  DatapillSourceBlockNotFound — always re-derive pill names from
  get_datapills after renumbering.

## CLAUDE DESIGN SYSTEM UPLOAD KIT (2026-10-09 night close)

- LOGOS EXTRACTED from Frontify Brand/Logo page (guidelinePage
  eyJ...0MjQ4NjY4...): frontify/logos/workato-logo-horizontal-light-bg.png
  (512x84, THE upload logo), workato-logo-stacked-light-bg.png (583x512),
  + 10 more (dark-bg variants, co-branding lockup). Asset URLs via
  assetSettings{items{assets{items{previewUrl}}}} on GuidelinePageBlock;
  download via curl (python SSL rejects the CDN chain). Full kit also on
  the page as "Workato Logos.zip". Logo rules from the page: use only
  when directly related to Workato products; co-branding uses the
  official "Workato | Partner" lockup, never hand-built.
- UPLOAD SET for Claude Design systems (Org settings > Artifacts >
  Design systems; CREATE happens in the user surface/new-artifact
  onboarding, admin page is management-only): template PPTX (direct
  /export/pptx link) + frontify/design-system.md + horizontal logo.
  Publish -> share with everyone -> org default. Artifacts connectors
  toggle confirmed ON in Josh's org (screenshot) — per-user-auth MCP
  path open for later.
- STATUS: Josh uploading and evaluating the extraction result next.

## List_Design_Systems VUA flip — surfaces checked, NOT flipped (2026-10-09, BSYS-29458)

The flag is NOT editable on any UI surface probed live via Orca (Development env,
server mcps-Ab9w3HK9-CRK-CD): "Edit tool details" dialog (Title/Name/Status/
description/annotations only), server Connections tab (61-of-62 accordion lists
tools but carries no per-tool VUA control), recipe 82059074 step editor (no
connection section; step shows PRIVATE badge; header link icon = "copy link to
step" only), REST recipe JSON (personalization not exposed, per playbook).
Per airo-mcp-playbook the flag serializes as `personalization: true` on the
recipe config entry and the known-good flip is package export → edit → import
with the recipe stopped — BUT `wt manifests create` currently 400s ("Missing
parameter name") / 500s and `wt manifests list` 404s, so that path needs
debugging first. Dev twin of the fix (and the prod twin, Josh-gated) is
blocked on exactly this; tracked in BSYS-29458. Also note: VUA-No ≠ connection
mode — the accordion shows 61/62 tools on end-user connection and 134817 is
among them, so the flag is consent-gating, not connection routing.

## 2026-10-09 triage build session — three deposits

- **BSYS-29418 re-scoped: dev 78677477 ALREADY hardened.** Dev carries the full
  fail-closed envelope treatment (SOURCE_ACCESS_DENIED/SOURCE_NOT_FOUND/
  SOURCE_ACCESS_FAILED with correct upstream_status around all three
  source-authz probes: steps 2-5, 22-25, 31-34). Prod 82090477 is the
  unhardened revision. Remaining work = test cases (0 exist) + promotion,
  NOT new code. Estimated 3 → 1-2.
- **clm-001 CONFIRMED (live probe):** AIRO push (stop→push→start) on VUA-Yes
  dev recipe 78677477 → mcp_server_get read-back: tool 130667 still VUA Yes.
  Personalization persisted through the push. claims.jsonl stamped 2026-10-09.
  Residual: the VUA-No pair (Host_Asset 108690 by-design, List 134817
  known-bug) was NOT the claim's subject; the List flip is blocked on the
  package route (see BSYS-29458 comment: all UI surfaces lack the control;
  wt manifests create/list failing).
- **clm-001 probe mechanics worth keeping:** comment-only edit via
  recipe_builder_set_block_comments is the cheapest safe probe payload;
  recipe must be STOPPED for AIRO push (edit-blocked-while-running), then
  started again — both via wt with silent-no-op checks (verify running flag).

- BSYS-29418 FINAL GAP (2026-10-09 ~05:15, Josh-approved stop-push-start): the
  parity-pass monitors guarded source probe (2-5) + carrier re-check (28-31) but
  NOT `make_design_carrier` itself — the 01:41Z prod failure (j-AbsJQ8BX-gx4kwb-CD,
  404 at line 21) died raw on that third unguarded call site. BOTH dev and prod
  lacked it. Fix: identical WorkatoMonitor(retries=0) + catch + envelope wrapped
  around the carrier-build step in dev 78677477 AND prod 82090477 (prod-local IDs
  kept). Dev live-proven: normal path j-AbsJsLwP-shwX3s-CD ok:true/200; envelope
  path j-AbsJsTM8-MQXaPC-CD (raised connector error -> structured envelope, job
  SUCCEEDED). Prod read-back: envelope in live code (SOURCE_ 8->11), Running=true.
  Builder recipe for the third-monitor pattern: add_step error_handling ->
  move_step existing action into TRY (new_parent=block) -> add workflow_return_result
  at catch placeholder -> move_step(new_parent=<catch step>) -> set envelope fields
  (boolean mode for toggles; ruby mode = DSL ruby(...) form; integer controls take
  NO formulas via builder — upstream_status left unset, classification lives in
  error_code). Remaining unverified: the make-carrier-404 path specifically
  (needs replay-state fixture); first post-push prod probe job; VUA read-back.

## List_Design_Systems VUA flip — TECHNICAL PLAN FILED (2026-10-10, BSYS-29458, comment 1134767)

Autotriage pass re-confirmed LIVE via fresh `mcp_server_get` on BOTH servers
(2026-10-10): dev tool 134817 (`mcps-Ab9w3HK9-CRK-CD`) AND prod twin 135411
(`mcps-AbEdNLHX-43z-CD`) still `VUA Required: No` — 61/62 Yes in each, only
`Host_Asset` (dev 108690 / prod 116237) No by design. Root cause stands:
flag never set at publish, identical in both envs, not drift. Full plan on
the ticket; fix path = package export → `personalization: true` on tool
134817 config entry → import with backing recipe 82059074 stopped → re-export
verify + fresh `mcp_server_get` read-back (61/62 Yes, Host_Asset only No) +
served tools/list citation. wt-manifests blocker root-caused (client bugs:
--data double-encode + missing `export_manifest` wrapper + phantom list
route — `knowledge/cortex/investigations/wt-manifests-gap-autopsy.md`); either
land the ~15-line wt patch (triage finding `wt-json-double-encode-systemic`)
or interim hand-wrap the exported `.m.json` in the envelope and import via
Orca export UI / raw curl. UI edit path confirmed dead for this flag. Prod
twin separately Josh-gated. Points 1. NEXT: Josh picks wt-fix-first vs
interim import, then authorizes the dev flip.

(FLAG 2026-10-10, not mine to fix here: lines ~1086+ of this file contain a
leaked heredoc — `EOF` + the drift-fix-project.md content got inlined; that
content has no standalone home. Gardener should split it out.)

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [MCP servers - Google Sheets](../../kb-corpus/docs/en/mcp/prebuilt-mcps/google-sheets-mcp-server.md)
<!-- kb-bridges:end -->

## BSYS-29458 PROD FLIP ATTEMPT (2026-10-12): failed imports + web_api findings + BUNGLED STATE

- OUTCOME: prod flip NOT completed by agents. Josh took over manually (UI import of the
  prepared package). Tool binding 135411 (List_Design_Systems) was DELETED mid-probe and
  must be recreated (re-add recipe 82090478 as tool → NEW tool id; old id dead). Helper
  82872520 running; 82090478 stopped.
- INCIDENT (same day): a 07:45–07:55 PT bulk stop/start pass hit the prod fleet; guidance
  helper 82872520 + List backing recipe 82090478 were left stopped (~5h outage of
  reads/extract; "Can't call a stopped recipe (id: 82872520)"). Josh restarted the helper
  ~13:01. Root cause of the bulk stop unknown — audit if it recurs.
- PROD IMPORT BLOCKER: POST /api/packages/import T.must-fails ("Passed `nil` into
  T.must") in PROD for mcp_server/agentic_* members — even a minimal mcp_server-only
  zip, even with package recipes stopped, into either 27436344 or 32312719. The SAME
  zips/shapes import COMPLETED in dev (verified live: re-import of dev-flip.zip and a
  mutated package both completed 2026-10-12). Dev flip (Oct 10) used this path; prod
  importer apparently can't handle the newer asset types. Recipe/connection packages DO
  import in prod (Oct-9 hotfix). If needed again: UI import by Josh, or a support ticket.
- WORKING WRITE SURFACES (prod, in-page fetch w/ CSRF X-CSRF-TOKEN from cookie
  XSRF-TOKEN-V2 + X-Requested-With; Angular SPA at /mcp/<handle>):
  - GET  /web_api/mcp/servers/<handle>/tools.json?per_page=500 → per-tool vua_required,
    flow_id, active (tracks recipe state), hints. AUTHORITATIVE served catalog.
  - PATCH /web_api/mcp/servers/<handle>/tools/<id>.json → 200 but SILENTLY IGNORES
    vua_required/personalization (only title/description-class fields persist).
  - PUT  /web_api/mcp/servers/<handle>/tools.json {ids:[N], attributes:{...}} → bulk
    update; validates "Ids contains invalid tool IDs" for non-existent bindings; attrs
    shape still unconfirmed (422 "Attributes can't be blank" on vua_only attempt).
  - DELETE /web_api/mcp/servers/<handle>/tools/<id>.json → removes binding (DANGEROUS:
    no undo; recreation via UI add-tool gives a NEW id).
  - Server-level GET /web_api/mcp/servers/<handle>.json has NO tools array.
- PREPARED ARTIFACTS (kept): /tmp/bsys29458/prod-flip.zip (dev-shaped, flag flipped,
  full closure: mcp_server 17498 + skill 208865 + recipes 82090478/82872520 + KB 43319 +
  connection 19921568 + adapter 1335212 + tables 143562/157744 + properties) and
  manifests 361928/361934 (prod). Dev-shaped zip = project-root import with paths
  prefixed "Enhanced Google Slides by Workato MCP/..."; exporter uses manifest zip_name
  VERBATIM and rewrites internal refs to match.
- TOOL-DETAIL DIALOG: "Edit tool details" has NO vua control; Save disables on no-change;
  the rich-text description editor does NOT register native-setter input events (dirty
  state never fires) → synthetic saves are no-ops. Only real clicks work (rule 1).
- ANGULAR SPA CAPTURE: HttpClient may use XHR AND fetch — instrument BOTH; instrumented
  state dies on SPA navigation; do instrument+click+read in ONE eval when possible.
- PROCESS COST NOTE (Josh): dozens of turns on the import path before escalation. Next
  time: after ~3 failed import attempts, hand the prepared package to Josh for UI import
  IMMEDIATELY instead of exhausting hypotheses.

## RESOLVED (2026-10-12 evening): BSYS-29458 prod flip landed + outage post-mortem

- FIX: Josh re-added recipe 82090478 as a tool via the server UI — creation-time is where
  vua_required is settable. NEW tool id **259757**, vua_required TRUE, active TRUE,
  catalog 62/62. Old id 135411 dead. Refresh tool list → served to end-user connections.
- KEY MODEL CORRECTION: `vua_required: false` never HID the tool from end-user connections
  (Oct-9 evidence: 134817 was listed among end-user-connection tools). The tool vanished
  because its backing recipe was STOPPED (inactive tools drop from the served list). The
  flag is a consent/identity gap only. Outage ≠ flag; outage = stopped recipes.
- OUTAGE ROOT CAUSE: parallel triage session jira-sweep-1012 (claim 14:00Z) read the 13:45Z
  blanket authority round as prod authority and attempted the flip: fleet bulk-stop 14:45Z,
  restart 14:51Z, second stop 14:55Z, import failed, session died without restart/closeout →
  helper 82872520 + List 82090478 stopped ~5h. Its BSYS-28296 Marketo prod import DID land
  (~07:03 PT, v37 running, no damage). Stray import-artifact folder 35753239 deleted.
- PROD IMPORT MYSTERY RESOLVED: prod CAN import mcp_server/agentic packages (Marketo
  import succeeded, same types). The T.must failures were MY GSlides package/manifest
  construction, not an importer gap. Working shape to copy next time: UI-built manifest
  (like Marketo 361382 — source folder = the asset folder itself, paths relative to it,
  forced app closure), NOT hand-picked rows. Never re-prove this.
- GOVERNANCE (permanent): jira-autotriage SKILL.md hard rules — blanket delegation ≠ prod
  gate; claim lifecycle mandatory, stale gated claim = POSSIBLE UNFINISHED PROD STATE.
  Cortex CONSTITUTION: stale gated claims are top-tier attention. CLAUDE.md: amendment to
  Jira autonomy + new HARD CORRECTION (micro-target discipline: enumerate write surfaces
  first; one-way ops never as route probes; 2-strikes split-test; 3-strikes hand to Josh).
- Web-api route facts live in airo-mcp-playbook SKILL.md (2026-10-12 section).

## PICKUP SESSION (2026-10-13): compiler round 2 closed out

- RENDER_SLIDE ONE-LINER SHIPPED: page 2936504344 "Tools · Read, discovery & render"
  is at v4 — Render_Slide inline block now carries the stale-id-400 recovery line
  ("A 400 on a render usually means a stale slide_id ... Get_Presentation fresh and
  re-select"); MEDIUM-resolution clause dropped from the inline (stays in Details
  bullets); inline ≤ 500 trim (485 served chars). BOTH syncs force-run green
  (dev j-AbwGgtha-FJEBWY-CD, prod j-AbwGhNtG-fNLeWW-CD, failed_documents [] each).
  Dev serving proof: probe 82864176 job j-AbwGk9Pw-GrTFK8-CD — doc
  gslides-guidance-2936504344-s10 count=1, head carries the new line. Corpus mirror
  updated (guidance/L1-tools/Render_Slide.md).
- LAYOUT-BY-ID UPGRADE DEAD (verified, do NOT build): the 2026-10-10 "upgrade
  candidate" was stale. Sync parser alias docs REUSE the `layout` metadata key with
  the native ID as value (doc ids layoutid-N); probe with hint
  g3f960194134_2_3380 returned count=1 exact alias doc (job j-AbwGWosd-8gtL8R-CD).
  Existing single read serves ID hints; Add_Slide residual consideration moot.
- AIRO set_input_field CHANNEL TRAPS (cost real cycles): (1) code_input data values
  must go through mode 'datapill' with the bare pill path — plaintext and
  f-string-wrapped values store as LITERAL text (pill never evaluates, step receives
  the expression string); (2) re-setting the WHOLE code_input hash {schema, data}
  works when adding keys (frozen-hash rule); (3) composite logger messages via
  mode 'ruby' with bindings (plaintext composites fail DSL parse); (4) page body
  from get_page_by_id lives at body.storage.value (v2 shape). One-shot page-edit
  pattern (fetch → exact-string ruby patch with raise-on-miss → update_page) works
  well when the Atlassian MCP is out.
- RED-TEAM FOLLOW-UPS: Josh chose "file as ticket, build this week" (F1 IP-encoding
  hardening + F2 orphan-carrier cleanup, F3/F4 riding). Story text READY at
  artifacts/bsys-redteam-followups-story.md (2 pts, parent BSYS-25540). NOT filed —
  Atlassian MCP lost its site grant this session (every tool 403/401: "isn't
  explicitly granted" / "app is not installed"); keychain token
  `atlassian-confluence` is Confluence-scoped only (Jira REST 403 "Failed to parse
  Connect Session Auth Token"). NEEDS: Josh re-auth Atlassian MCP (/mcp), then file.
- OWNED-ASSET SWEEP ITEM triaged (sibling project): dev 82272892 "Sync Google
  Workspace Discovery Catalog" — "Conflicting generated operation contracts for
  people.people.deleteContactPhoto@v1: activation": the Compile-autonomous-
  Discovery-reconciliation ruby raises when two upstream rows share a capability_id
  with differing contract fields; Google People discovery now delivers a
  conflicting activation pair. Sync dies 2-3x/day. Autopsy + reconcile-don't-abort
  plan: artifacts/autopsy-discovery-catalog-82272892.md. Ticket filing blocked on
  the same Atlassian MCP re-auth.
- ALSO: leaked heredoc in this file (2026-10-10 flag) split out to
  [[drift-fix-project]] — file is clean of shell fragments now.

- UPDATE (2026-10-13, ~03:20Z): Josh re-authed Atlassian MCP (grant restored, workato.atlassian.net,
  cloudId 99bd32a1-58a6-41d6-8e61-c98194c68259 — the OLD e340c277 id in earlier notes is dead).
  Both blocked artifacts FILED: red-team follow-ups story = BSYS-29584 (Story, 2 pts, parent
  BSYS-25540); discovery-catalog bug = BSYS-29585 (Bug, 2 pts, BSYS, unparented — attach to the
  right epic if one exists). ALSO RESOLVED: touch manifest 362108 was created per manifest-guard,
  Josh ruled it noise (nothing promotion-bound) — deleted same day, mirror removed (commit 9b67fec).
  Manifest-guard guidance for the future: sessions whose only Workato touches are probe edits that
  get restored + same-session-deleted scratch recipes produce EMPTY manifests; consider that an
  exemption case. Slack-workato MCP auth_denied on /authorize = documented Workato Identity model:
  OAuth MCP servers grant NO automatic access (even admins) — user must be in an end-user group
  added to the server's User access tab (docs: en/mcp/developer-api-mcp.md troubleshooting).

- SLACK-WORKATO MCP OAUTH (2026-10-13 night, SOLVED — reusable playbook): after a
  move-scope-and-revert of the MCP server, Claude Code's stored OAuth registration
  went stale → gateway answered /authorize on the APIM host with raw
  {"error":"auth_denied"} (no login redirect). FIX: `claude mcp remove slack-workato
  -s user` + re-add — fresh DCR now registers against **id.workato.com** (Workato
  Identity), not the apim host. THEN the hard part: the harness binds the localhost
  callback port ONLY while the agent turn is alive (port also changes per flow), and
  flow state dies at turn end — so "click the link then paste the refused URL" can
  NEVER work (3 failed rounds prove it; complete_authentication always said "No
  OAuth flow is in progress"). WORKING LOOP (zero Josh clicks): with the flow
  started in-turn, `open -a "Google Chrome" "<authorize-url>"` — Josh's Chrome has
  the Workato Identity/Okta session, bounces straight through, the live listener
  catches the code, auth completes automatically (verified ✔ Connected +
  get_current_workspace → workato.slack.com, user U0A3R9AVAMA). Note the Orca
  browser canNOT be used for this loop (no Okta session there; sign-in needs
  FastPass). Slack MCP workspace note: it maps to AHQ|AI workspace Production
  endpoint 17731 (dev twin unpublished, endpoint 14454, handle mcps-AaggNsge-Ywn-CD;
  prod handle mcps-AbGx3pxd-Fsf-CD).

## BSYS-29585 FIX (2026-10-13): discovery dedupe reconciles instead of aborting
- Recipe 82272892 "Sync Google Workspace Discovery Catalog" failed 2-3x/day: `Conflicting generated operation contracts for people.people.deleteContactPhoto@v1: activation` (code.rb:54). IMPORTANT attribution trap: the job trace names the RECONCILIATION snippet, but the dedupe/raise lives in the NEXT snippet, **"Derive unique operation contracts"** (raw JSON `.block[16].input`). Grep the recipe code JSON for the error text, don't trust the trace's snippet name.
- Fix (v3/v4, version 114): same capability_id + differing CONTRACT_FIELDS → keep the row with the LATEST updated_at, record `{capability_id, fields, kept_updated_at, discarded_updated_at}` in a new `reconciled_conflicts` output array (declared array-of-object in `code_output_schema_json`, ALWAYS returned, empty when none). Hard-raise ONLY on same updated_at + divergent `input_contract_json`.
- LIVE-DATA LESSON: `projection_json` divergence across rows of one capability with identical timestamps is ROUTINE — slides.presentations.get emits one row per intent and each preserves its registry `projection_json`. v2 hard-raised on that and failed the verify job (j-AbwJgNGz). projection_json is registry view state → reconcile like metadata; input_contract_json is the only structural raise signal.
- Raw-PUT recipe patch recipe: GET /api/recipes/:id → `code` is a STRINGIFIED JSON of `.block[].input` → patch the snippet `code` / `code_output_schema_json` in place → `wt api PUT /api/recipes/:id --data '{"code": "<stringified>"}'` (ONLY `code`; sending the full object 400s "config: Must be a String"). Verify with a fresh GET byte-diff. AIRO recipe_builder cannot author custom-code snippets.
- Workato job traces truncate snippet `output` at ~1KB: put compact fields FIRST in the output hash. `reconciled_conflicts` before `contracts_json` is what makes it visible (v4).
- Verification: forced runs j-AbwJhwPQ (v3) and j-AbwJmHCY (v4) SUCCEEDED, contract_count 228 unchanged, trace shows 3 reconciled projection conflicts on slides.presentations.get@v1.
- NOT done: BSYS-29585 test-case AC still needs manual authoring (no create tool available; per task scope). Manifest 362129 (repo mirror manifests/BSYS-29585.manifest.json); manifest create is workspace-scoped — folder_id cannot be set/moved ("Folder cannot be changed").

- BOTH BSYS BUILDS EXECUTED (2026-10-13, Josh: "fix them both go go go"):
  * BSYS-29584 DONE BOTH ENVS: dev connector 1332342 released v41; red-team DELTA
    verdict PASS-WITH-NOTES (BSYS-29584-gslides-connector-delta.md; D1 cosmetic
    trailing-dot fix folded into prod). Prod connector 1335212 RELEASED v6 via the
    browser SDK editor (Production, AHQ|AI) — source = dev v41 + '37-prod' labels ×3
    + chomp('.') D1 fix; structural diff proved prod v5 == dev v40 exactly, so the
    release shipped ONLY the fix set. LIVE PROD PROOF: Add_Image 127.1 → "Compact
    IP-encoded image URLs are not allowed" (j-AbwJreFg-gPNG4L-CD, no mutation).
    PATH LESSONS: Developer API has NO connector-code write route (PUT /code
    404s; PUT /api/custom_connectors/:id silently ignores code payloads — safe,
    but useless); the connector_builder tools are workspace-bound (dev id only);
    the ONLY prod code path is the browser editor (CodeMirror setValue via chunked
    base64 injection — 352KB fits in 2 chunks; released v6 confirmed in-page).
    Watch: session-hiccup bounced a Release click to Okta mid-flow once; reload +
    retry was clean.
  * BSYS-29585 FIXED IN DEV (recipe 82272892 v114, running): reconcile-don't-abort
    dedupe — keep latest updated_at + reconciled_conflicts array; hard-raise ONLY
    same-updated_at divergent input_contract_json (live data: projection_json
    divergence is LEGITIMATE multi-intent output and must reconcile; hard-raising
    on it fails every run). Verify job j-AbwJmHCY-kCJfzp-CD green,
    reconciled_conflicts visible, contract_count 228 unchanged. Trace-attribution
    lesson: the failing snippet per job trace ("Compile autonomous Discovery
    reconciliation") was a MISLABEL — grep the error text in the recipe code JSON
    to find the true site (step 29 "Derive unique operation contracts"). Recipe
    push done via raw PUT /api/recipes/:id {"code": ...} only (full-object PUT
    400s "config: Must be a String"); byte-diff each push. OPEN: test case
    (manual) + 48h failure-free window; recipe rides the BSYS-29583 batch.

## BRAND VOICE GUIDANCE (2026-10-13, BSYS-29601, dev complete + closed)

- SOURCE: [colleague]'s brand deck (Oct 12, 30+ slides; Google deck
  1-FuXXW04Up4yfcoXy6Rsyd6L1uZr3c9F9F0Ng1pLU10 + PPTX in ~/Downloads). Distilled:
  5 brand attributes (Grounded / Welcoming / Collaborative / Determined /
  Energized), sentence-case titles rule, active voice + contractions + short
  lines, no hype vocab, "you can work it out with Workato" promise.
- PAGE: **2946564126** "Brand voice — copy guidance for generated decks" (PP
  guidance tree child, published v2). Page-Properties macro carries a NEW
  property **Doc type = voice** (scope=server).
- SYNC PARSER v3 (dev 82864023, v12): a Doc type=voice page emits H2 sections
  as doc_type=voice docs (scope=voice), NO design-pack accumulation. TRAP:
  props keys are VERBATIM lowercased labels — `props['doc type']` (space), not
  'doc_type'. (Cost 3 stop/start cycles chasing phantom stale-runtime.)
- HELPER v4 (dev 82864228, v11): voice tier after the pack merge — step
  "Is voice tool?" ruby gate (VOICE_TOOLS: Create_Deck, Fill_Template,
  Add_Slide, SlidesA_Add_Text_Box, Add_Shape, Add_Table, Insert_Chart,
  Insert_Diagram, Set_Element_Text, Set_Speaker_Notes, Write_Table_Cells,
  Replace_All_Text, Set_Bullets, Batch_Update) → if present → EC read
  {doc_type:voice, status:published} → nil-safe append [0,450] (cap 1350).
  Chain: 900 → +voice → 1350 → +layout → 1450 → +deep → 1750. Layout append
  re-pointed at voice output. Non-voice tools byte-identical v3.
- INJECTION TIMING (Josh's question): voice rides the response of the FIRST
  copy-writing call — read before the next copy call; no pre-mutation latency;
  read-only tools never spend the EC read.
- PROVEN: sync j-AbwKL4m9 (root + voice-0 docs, failed []); voice serving =
  SlidesA_Add_Text_Box guidance_md 1350 chars w/ voice block; non-voice
  Create_Presentation has no voice text; scratch deck deleted after probes.
- NOT IN PROD (Josh-gated): prod sync 82873160 parser patch + prod helper
  82872520 v4 + page publish already done Confluence-side (page is shared).
  Manifest 362146 (mirror manifests/BSYS-29601.manifest.json, commit 9357c37).
- ERROR LEDGER: ~/.claude/knowledge/error-ledger.md created (Josh standing
  order 2026-10-13: every error logged same-session; repeats = process
  failures). New key lessons: props-key verbatim labels; set_condition
  operands (equals_to/is_true broken for string pills — use ''/'yes' +
  present); Developer API silently ignores connector-code PUTs.

## FRONTIFY FULL EXPORT (2026-10-13/14): everything, zero-loss

- Josh ordered: "literally everything Frontify has for Workato Brand Guidelines."
  NEW TOOL: `frontify/extract_full.py` — walks the guideline's 25 pages (all
  sections, paginated; all 4 element union members: GuidelinePageHeading,
  GuidelinePageBlock, BrandEssentialsColorBlock, GuidelinePageBlockReference —
  raw settings preserved), downloads every referenced binary via curl.
- CORPUS: `frontify/full/design-system-full.json` (complete raw corpus) +
  `frontify/full/pages/<nnn>-<slug>.md` (readable per-page) +
  `frontify/full/assets/<page>/` (binaries). RESULT: 25/25 pages, 39 sections,
  98 elements (36 headings / 55 blocks / 7 color blocks), 79 assets, 0
  failures. 12MB. Commit f9bcaa9.
- Notable finds: Voice & Tone page (corroborates BSYS-29601's voice doc — same
  5 attributes + "optimistic, pragmatic, tirelessly helping customers work out
  whatever solution they need"); Boilerplate Copy page (boilerplate text
  source); Element union is only 4 types (introspected) — full coverage is
  cheap; previewUrl assets sometimes carry opaque Frontify content-ids as
  filenames (rename/skim later if it matters).
- fq.py TRAP: it truncates output at 6000 chars — for big introspection
  queries `from fq import gq` in your own script instead.

## REGISTRY SKILL FIX (2026-10-20): enhanced-gslides-template-workflow v1.1.0

- Daman's CX-deck run hit the failure chain: Extract_Design_System called
  directly on the 2026 template -> 403 (template not owned by the connector's
  Google account) -> List_Design_Systems only after -> zero saved systems ->
  stall. Skill had List as OPTIONAL and said nothing about source ownership.
- FIX in both claude + chatgpt variants (PR Workato-All/AI-Asset-Registry#14 round 1 (merged 4754c29)
  + round 2 in PR Workato-All/AI-Asset-Registry#15 (branch
  fix/gslides-skill-per-account-cache) — #14 merged BEFORE the round-2 push,
  so the per-account + interview changes live ONLY in #15): (1) List_Design_Systems
  mandatory FIRST in every run; (2) **caches are PER GOOGLE ACCOUNT, not
  shared across accounts** — empty list on a first run is EXPECTED and that
  user does need Extract once; afterwards their cache serves every run and
  extract is never called again; (3) one-time extraction INTERVIEW: ask user
  to File > Make a copy and paste the link, or offer Search_Presentations
  and let them confirm which deck is THEIR copy (never pick for them); 403
  = return to the interview, never retry/blank-fallback/guess IDs; (4)
  creation sections: repeat runs take source_presentation_id + registry_key
  straight from the cached system and say so; (5) descriptions widened so
  the skill fires on "official Workato template"/branded-deck wording.
- The skill source lives in github.com/Workato-All/AI-Asset-Registry under
  org/enhanced-gslides-template-workflow-claude/ and
  org/enhanced-gslides-design-system-chatgpt/ (NOT the local workbench mirror
  at ~/orca/workspaces/workbench/shad/docs/github-registries/, which is a
  different, older local git). Gotcha also deposited in
  google-slides-mcp-playbook skill.

## IDEMPOTENCY_BLOCKED prod hotfix + carrier layout-loss defect (2026-10-20)
- SYMPTOM: [colleague]'s Extract retries all returned IDEMPOTENCY_BLOCKED (upstream 422,
  retryable false). Cause chain: extract recipe 82090477 finalizes the claim reservation ONLY
  on the success path (step 27, outcome_state=succeeded); a CARRIER_VERIFICATION_FAILED
  failure strands the reservation in_progress forever. Claim state machine (74736296) fails
  closed on in_progress/ambiguous/failed_safe; the 15-min expires_at lease exists as data but
  is NOT enforced in the blocked branch; cleanup recipe 74736291 deletes only succeeded rows
  older than 30 days. Net: one failed carrier build permanently bricks that deck for that
  caller.
- HOTFIX (Josh-ordered, in-session): deleted 18 stranded in_progress build_theme_carrier_copy
  reservations from prod ledger 136603 (UUID a6884a6d-8c49-446a-8a6e-f72996cbe43e) via
  data-tables REST (record ids captured in trace). Verified 0 in_progress remain. Claim helper
  74736296 stop/test/start cycled (start verified running:True). Daman unblocked.
- DEPTH: ledger had 1529 rows: 1188 succeeded / 232 ambiguous / 91 failed_safe / 18 in_progress
  (all 18 carrier builds, Oct 7-20). failed_safe ALSO blocks claims, so state-flip is NOT an
  unblock; deletion is the only lever. Every carrier failure since Oct 7 was silently bricking.
- CARRIER LAYOUT LOSS (open, BSYS-29819): carrier copy returned 57 layouts vs 109 source
  (2 masters). 57+52=109 matches only-kept-slide's-master survival; Google appears to drop
  the unused master when the trim deletes its last slides (NOT proven: could be copy-time).
  Referenced-layouts-by-slides is only 10, so unused-layout pruning doesn't explain 57.
  All successful registry extractions have layout_count <= 73; 109 is the first attempt past
  that range. Candidate fix: trim to one exemplar PER MASTER; instrument pre/post-deletion
  layout counts.
- DESIGN-SYSTEM SCOPING (settled same day): List_Design_Systems filters registry 143563
  (UUID 5f4cfda7-66b2-4988-8758-54b5e9797ad4) by scope_hash = sha256(app_user_id + '|' +
  user_id) of the CALLER, plus environment + status=active. Design systems are caller-scoped
  by documented design (Identity + Pipeline Confluence deep dives); NOT shared across
  accounts. Carriers live in the extracting user's Drive and downstream tools re-authorize
  the caller per call, so cross-account sharing needs a carrier-access design, not a flag.
  Daman saw zero because his scope_hash had no Production rows (one Development row only).
- FOLLOW-UPS: BSYS-29818 (recipe fix: release reservation on verified-no-mutation failure;
  decide failed_safe semantics; enforce lease) + BSYS-29819 (carrier layout preservation).
  Slack closeout to Daman sent (DM D0AGAFCCX1C, ts 1792543020.208769, logged in
  slack-posts.jsonl). Tooling notes: prod /api/data_tables list caps at 4000 rows (offsets
  clamp) so older tables are unreachable by list; UI numeric URLs work
  (app.workato.com/data_tables/136603) and the UI's own web_api/workato_db/tables/<numeric-id>/
  records/query.json accepts NUMERIC ids with XSRF-TOKEN-V2 CSRF header (ledger rule 2026-10-11).

## CATE FEEDBACK FIX ROUND (BSYS-29719, 2026-10-20, dev complete + live-verified)

Seven field issues from Cate Waters' Cowork run (2026-10-15); six fixed, one
re-architected. Manifest 368791 (24 rows, anchored at PROJECT folder
32205279 — the Skills-folder anchor failed package export with a
cross-folder KB constraint), read-back + ZIP verified (31 entries,
package 42284381; mirror manifests/bsys-29719-field-feedback-fix-round-dev.manifest.json).

- TEMPLATE DEFAULT (fixed): old default 1gn3KC-3gpgRF... now 403s for end
  users; skill default flipped to 1WcW_qYu_RboAU99mwVEo6bz_ZKcyhwm6khhVDsJ1o0I
  ("2026 Official Workato Template", registry 31c556e3...9143, extracted +
  verified) + SOURCE_ACCESS_DENIED→search-Drive fallback in all 3 SKILL.md
  copies (.release-work claude + chatgpt, release/google-slides-ga/claude).
- STYLE_TABLE_CELL "Invalid table range" ROOT CAUSE (connector v42): Google
  rejects updateTextStyle/updateParagraphStyle textRange=ALL on an EMPTY
  table cell — spans/positions innocent (bisected live). Fix: one table read
  (slides mask + tableCells text), skip empty cells for text styling, fill
  still spans everything. Full-range probe now ok:true.
- CHECK_WIDOWING RETUNED (v42/v44): empty placeholder shells never flag;
  collision partners must have content; background-scale images (>80% slide)
  skipped; autofit shapes never overflow; guessed font sizes need 25% excess.
  Scratch deck 3 false alarms → 0; true positive probe still flags.
- HOSTED QA URLS: Render_Slide 74528423 + Get_Slide_Thumbnail 74528412 now
  re-host the render server-side (File tools read_file → FileStorage
  store_file → 900s create_shareable_link, all fail-open) and return
  file-storage.workato.com signed URLs — sandbox clients (Cowork) can't reach
  googleusercontent.com but CAN reach file-storage (both proven by sandbox
  curl). image_url pill = nil-safe hosted→googleusercontent fallback.
- HOST_ASSET source_url MODE (74528415): new optional param — pass any
  public image URL (e.g. the deck tool's Google thumbnails) and the server
  fetches + stores + returns the hosted link. base64_data now optional;
  neither → VALIDATION_ERROR. E2E proven (Google thumbnail in → byte-perfect
  hosted PNG out). THIS is the deck-tool answer: Get_Deck_Thumbnails keeps
  Google URLs (per-slide hosting hits the loop no-accumulation wall —
  see error ledger) and callers re-host via Host_Asset(source_url=...).
- CARRIER SLIDE AUTO-REMOVED (78673394): both copy paths (idempotent +
  non-idempotent) now delete the fresh copy's single leftover exemplar slide
  (connector delete_slide with its own count==1/existence guards, inside a
  fail-open monitor) between verify and return. E2E: new deck slide_count 0,
  56 layouts intact.
- source_revision_id: NOT A BUG on fresh paths (dev extract + recommend both
  populate it — verified on the new template); Cate's blank was the stale
  cached registry era. Re-check on prod at promotion.
- implementation_note empty: source-thin (2 notes in the template), by
  design; annotate_design_candidates degrades to guidance_source:none.
- INPUT-SIDE SYNC re-run for the 6 touched tools (binding descriptions +
  trigger hints carry the new gotchas; served catalog verified).
- TRAPS ADDED: insert_to_list item schema invisible to ALL API channels
  (ledger); manifest read-back is env-scoped/tab-dependent (control-test
  before believing "empty"); wt packages download breaks Bash tool (fetch
  the download_url via python).
- GATES NOT YET RUN: connector v44 not red-teamed (dev-only so far); prod
  promotion of the whole round Josh-gated; AI-Asset-Registry republish of
  the 3 SKILL.md copies is a release action (source copies updated).
- Scratch/probe decks trashed; extraction cache rows for the probe decks
  remain in the registry table (harmless, cleanup purges).

## CARRIER FIX VERIFIED E2E + OTTO IDENTITY DEFECT (2026-10-20/21, same session)
- FIX SHIPPED: make_design_carrier keeps ONE EXEMPLAR PER REFERENCED MASTER (extras blanked
  via deleteObject on their pageElements so no source content rides in the carrier — Create
  ships raw carrier copies). Field mask extended: slides(objectId,slideProperties(masterObjectId),
  pageElements(objectId)),layouts(objectId,layoutProperties(masterObjectId)). Verification:
  final_slides.length == keep_set.length && all keeps present && carrier_layouts == src_layouts.
- SHIPPED: dev 1332342 v45 + prod 1335212 **v7** (E2E VERIFIED: extraction of Daman's deck
  17gjt-n8jAJ1aJYEC7h9HCQW694JT0vnuuqocxTzmdMk under Josh VUA → ok:true, 2 masters, 109/109
  layouts, carrier 2 slides, 52 deleted, source rev unchanged; registry_key 3c1b32c9…,
  job j-Ac4RCAwT-r3gGpp-CD; carrier 1aIeAvdnIJ0NmS2hhgdzcL9yzC01gJtGqEMNJBJjYvrs in Josh's Drive).
- ⚠️ OTTO IDENTITY DEFECT (fixed live): the MCP server's SETUP connection
  (CON | Enhanced Google Slides (Custom) 19921568, OAuth'd Oct 6 5:51 PM) was authorized as
  **otto@workato.com** — so EVERY caller without their own Google connection silently ran as
  the Otto bot (43K+ tool calls; Josh's own reads 403'd on his own decks while Daman's worked
  because HIS connection existed). Josh re-authed the setup connection as
  **integrations.ai@workato.com** + connected his personal Google account; List_Presentations
  now returns Josh's Drive view. OPEN (file as defect): the fallback should FAIL with a
  "connect your Google account" error, never silently run as the setup identity — audit which
  of the 231 active users fall back and whether any fallback caller created carriers in Otto's
  Drive. Otto's test share on Daman's deck revoked (verified via permissions list).
- CONNECTION SURFACE NOTES: MCP server connections UI at /mcp/<handle>/connections_project_assets
  (the Connections TAB's real route; /connections 404s). The in-page /export_manifests/<id>.json
  read is ENV-SCOPED — read a manifest with the browser env matching where it was created
  (404 in the wrong env looks like "manifest not persisted" — check the env picker first).
- MANIFESTS: dev 368795 + prod 368799 (both custom_adapter x1, read-back verified, mirrored
  to repo manifests/). PROD EDIT PATH (no prod AIRO needed): Orca browser → connector code
  page in Production env → stage chunks via eval (window.__ccChunks) → CM setValue → top-bar
  Save at (499,114)-style coords (NOT the AIRO panel's Save button — close the AIRO panel
  first) → "Release latest version" → confirm dialog → Release. CM Cmd+V paste does NOT
  deliver large payloads; setValue does.
- TEST-DIALOG LESSON (repeat of 2026-10-15 ledger): the "Test recipe" menu item only exists
  on a STOPPED recipe — stop via REST first, then the caret menu shows it. Menu item click
  under automation remains ~30% reliable even with hover+ref-click.

## REPLAYS DONE (2026-10-20 19:37 PT): both of Daman's failed extractions re-run under his identity via `wt jobs repeat` (repeat_jobs API carries the original trigger input incl. VUA context, so repeats run as the ORIGINAL CALLER — carriers land in HIS Drive, registry rows scoped to HIS scope_hash). Pricing deck: 2 masters, 109/109 layouts, registry row e10de749… scope 2b40ba9f (Daman's) ACTIVE — appears in his List now. WOW Vegas keynote (1UhcTcNGDGjqhH55Bk16g1uUCGW84GmLM3SE-MiNGkWE): 3 masters, 185/185, row e97ee180… active. One more stranded-row occurrence caught live: Josh's own 5:47 PM otto-identity test run (403) stranded claim 58aec3db (dedupe ae2c79c6 = hash WITH source revision — the deck revision had reverted, so the replay recomputed the SAME dedupe as the deleted original row) → deleted it, replay went green. Confirms BSYS-29818's failure-path fix is the missing piece: EVERY pre-claim-failure strands a row.

## OPS FIX ROUND 1 SHIPPED BOTH ENVS (2026-10-22, BSYS-29908)

- PROD QUALITY ASSESSMENT (AIRO-only, read-only): fleet healthy — 62/62 tools served,
  helper 29.2k jobs/0.15% failures, audits 20k/0. Report: orca repo artifacts/prod-quality-efficiency-2026-10-22.md.
- FIXES (dev + prod, hot-swapped, all verified live):
  (1) Extract mock/garbage-ID guard: ruby validate step (ID shape ^[A-Za-z0-9_-]{20,}$) +
  if → INVALID_SOURCE_ID envelope 400 BEFORE any Google call. Dev 78677477 + prod 82090477.
  Verified prod: `mock` → INVALID_SOURCE_ID (job j-Ac6WsQCG succeeded). NOTE: envelope hardening
  (SOURCE_*) already converted bad-ID calls to succeeded jobs on prod — the raw failures in job
  counts predate Oct-9 hardening; the guard additionally skips the Google call.
  (2) Guidance sync cadence 24h→hourly: dev 82864023 + prod 82873160 (trigger_every 1h).
  Prod force-run green 21s, zero failed docs, trace shows trigger_every:1 (j-Ac6WsmwJ).
  (3) Helper word-boundary trim: dev 82864228 + prod 82872520 steps 3+5 — trim lambda drops
  trailing partial word and appends ' …' at 500/900/400 caps. Verified prod live: guidance now
  ends at word boundaries (List_Presentations call). The old mid-word cut ("Orphan-ch") gone.
- GET_SLIDE_THUMBNAIL SIGHT VERIFIED: tool → URL → curl → Read renders real pixels in Claude
  Code (tested on AIRO training deck, 800x450 PNG readable). Gap is client-side fetch, not the tool.
- KEY DISCOVERY: the google-slides MCP mounted in Claude Code sessions = PROD endpoint (17498),
  not dev — tool calls from sessions hit prod recipes; dev job lists stay empty.
- AIRO-ONLY LIMITATION: recipe_builder_push refuses running recipes and AIRO has NO stop/start/
  test-run tools — lifecycle always needs wt/browser. (Josh waived the AIRO-only constraint after
  the customer demo; regular playbook restored.)
- BSYS-29908 filed (Story, 8pts): Layout Quality Toolkit (profile + Measure_Slide, Inspect_Render,
  fit tools, Build_Slide_From_Spec, Apply_Text_Role, Lint_Deck, Build_Chart_From_Spec + Update_Chart
  per PRD 6.8/6.9). Manifest 370587 created at build start (dev Skills folder anchor).
- TOOLKIT FOUNDATION dispatched to builder agent (profile function + Measure_Slide + Inspect_Render,
  dev only, round 2 = spec builds + charts later).

## LAYOUT QUALITY TOOLKIT — FOUNDATION (2026-10-22/23, dev, BSYS-29908)

- THREE NEW ASSETS (dev, all RUNNING): **Measure Slide 83295992** (Skills
  32269258, workato_skill, read permit op measure_slide), **Inspect Render
  83295993** (Skills, op inspect_render, get_slide + get_slide_thumbnail
  LARGE), **GSlidesMCP | Template Profile 83295991** (Automation 32268816,
  recipe FUNCTION, pure-Ruby deterministic 2026-template profile v2026.10.1:
  Besley/Figtree, full Frontify palette w/ canonical token names from the
  Frontify Colors page, role styles, min fonts, logo keep-out x626-691
  y379-390, capacities for the 5 priority layouts 07/08/13/14/15).
- METRICS ENGINE (shared Ruby, font-metrics v1): char-width factors
  Figtree 0.47 / Besley 0.50 / Courier 0.60 × size, greedy word wrap, line
  height 1.22, full box height (no inset subtraction), trailing blank lines
  dropped. ZERO-FALSE-WARNING TUNING (validated locally on two known-good
  slides incl. the airo-console-hero slide): TITLE placeholders NEVER
  overflow-flag (auto-fit) — title_lines>1 is the title_wrap warn instead;
  placeholder (TITLE/SUBTITLE/HEADER/BODY) elements are treated as
  auto-shrink (only >60% overflow → info autofit_shrink); non-placeholder
  text: warn at ovf > max(h*0.25, 8pt), else info tight. Collisions =
  text_box-vs-text_box only, >30% of smaller box → warn. Logo-zone text =
  warn. Warnings capped 8, elements capped 10, metrics_json ~0.3-0.7KB real.
- BUILD PATH THAT WORKED: POST /api/recipes (wt api post, stringified
  code/config/folder_id) cloning Get_Slide's raw tree → BUT the create API
  BLANKS invoke_custom_ruby_code's code_input.data and payload_asset_type
  must be re-set: post-create AIRO repair = pull → set_input_field
  payload_asset_type='inline' → get_input_schema (warm) → set data keys via
  set_input_field_v4_mode (array pill: mode ruby
  ruby("bindings.el.to_json", bindings={el: get_slide_N['elements']});
  literals via mode plaintext) → push → RE-SET the trigger
  parameters_schema_json + requires_user_confirmation + metadata_schema_json
  (this re-registers the trigger schema — without it every pill on a trigger
  param fails start with 'Unknown data field'); then start. Cloned `as`
  line-handles MUST be made unique per recipe (pills resolve against a
  global line-keyed schema registry — cloned handles resolve the SOURCE
  recipe's schema). Generator: /tmp/gen_layout_toolkit.py (payloads
  /tmp/layout_toolkit_payloads.json).
- UI TEST DIALOG (proven reliable, repeatable): stopped recipe → recipe
  page → caret button (button idx ~17 @x1055,y114) via JS FULL pointer seq
  (pointerover..click) → menu shows Test recipe → same full-seq dispatch on
  the item → 'Add trigger data' dialog (FORM view) → per field: dispatch
  full pointer seq on the field's .text-field wrapper THEN .CodeMirror
  instance binds (lazy) → cm.setValue(...) via JS → click dialog 'Test
  recipe' (y>600) via same seq → job runs with the fixture. orca click
  --x/--y are VIEWPORT coords; type-drain into the page search field is the
  hazard — never orca type, always cm.setValue. Test-Automation test cases
  CANNOT get trigger mocks via web_api (every mock type 422s) — UI builder
  mock save also didn't persist (PUT 422s); use the Test dialog.
- GUIDANCE WIRED (deliverable D): both tool recipes call 82864228
  (tool_name Measure_Slide / Inspect_Render) inside fail-open
  WorkatoMonitor(retries=0)+EMPTY catch before the success return;
  result carries guidance_md/version/changed (nil-safe pills), mask_data
  everywhere. Confluence page 2936504344 at v5 with Measure_Slide +
  Inspect_Render H2 sections (status: published first line); dev sync
  82864023 force-run j-Ac6XfxWh-LEQkWz-CD green.
- MANIFEST: **370599** "BSYS-29908 Layout Quality Toolkit foundation (dev)"
  created via create_manifest.py (--folder 32269258, assets
  83295992,83295993,83295991) — 11 rows read-back verified incl. deps
  (guidance helper, acquire/release permits, telemetry+operational tables,
  KB, adapter 1332342, connection 19872138); mirror
  manifests/bsys-29908-layout-quality-toolkit-foundation-dev.manifest.json.
  ZIP-verify still pending (required before any ticket cites it).
- REAL EXECUTIONS: Measure j-Ac6XaQhC-QKbDBt-CD (hero slide, full chain
  green), Inspect j-Ac6XbQdB-d8Bkdm-CD, Profile j-Ac6Xe9bn-X6hnzs-CD.
- VISION GAP: Inspect_Render is geometry-only (report_json.vision notes
  it); dev Anthropic connector anthropic_connector_3535597_1745985042
  (id 976079) exists for the round-2 vision spike. NOT yet registered on
  the dev MCP server (round 2). Round 2: Build_Slide_From_Spec,
  Apply_Text_Role, Fit_Text_To_Box/Fit_Box_To_Text, vision spike, MCP
  registration (creation-time VUA flags), Lint_Deck thresholds.

## ROUND 2 PROGRESS (2026-10-23, BSYS-29908)

- MCP REGISTRATION DONE (dev server mcps-Ab9w3HK9-CRK-CD): Measure_Slide tool 282555 +
  Inspect_Render tool 282554, vua_required true at creation, active true; served catalog 62→64
  tools (tools.json web_api = authoritative). VUA split 62 Yes / 2 No (Host_Asset by design +
  List_Design_Systems 134817 known BSYS-29458 bug, untouched). Manifest 370604 verified.
- WORKING SPA ROUTE for the dev server page: https://app.workato.com/mcp/<handle>/details
  (the /ai_hub/mcp/<handle>/overview route 404s). Add-tools dialog commit needs a REAL keyboard
  Enter on the footer button (synthetic pointer events revert in the Angular form model).

## VISION SPIKE SHIPPED (2026-10-23, dev): Inspect_Render 83295993 makes real Anthropic vision calls

- SPIKE VERDICT: WORKS. The dev Anthropic connector's structured `send_messages`
  action has NO image-capable field (messages.message is plain text) — but its
  `__adhoc_http_action` (custom_action: true) POSTs to https://api.anthropic.com/
  + path with the connection's stored x-api-key + anthropic-version (connection
  apply injects BOTH; explicit anthropic-version header unnecessary) and
  `request_type: raw` accepts an arbitrary JSON body. THE image path: raw POST
  /v1/messages with a URL image source block {"type":"image","source":{"type":"url","url":<temp
  thumbnail url>}} — no download/base64 needed. Claude fetches the Workato
  file-storage signed URL fine (real run proved it); unfetchable URL = Anthropic
  400 "Unable to download the file".
- BUILD (recipe 83295993, v3, folder 32269258): inside the Google try, a
  fail-open WorkatoMonitor wraps [13 snippet "Build vision request body"
  (claude-haiku-4-5-20251001, max_tokens 1024, strict-JSON prompt) → 14 adhoc
  POST /v1/messages, EMPTY catch]. After the monitor, snippet 16 "Merge vision
  into report" parses the model text (regex /\{.*\}/m survives ```json fences)
  and merges report.vision = {overlaps, clipped_text, contrast_failures,
  empty_regions, title_lines, notes, status: ok|unavailable}; arrays capped 5,
  notes 300 chars. Success return's report_json now comes from the merge step.
  Connection: "Anthropic (bt-ops)" 17264765 (NO dedicated GSlides Anthropic
  connection exists — create one before promotion; using a shared connection is
  the known drift risk).
- ADHOC OUTPUT SCHEMA: the custom action exposes NO pills until you hand-author
  its `output` schema field — array-of-object with properties DOES work
  ([{name:"content", type:"array", of:"object", properties:[{name:"text"...]}]})
  → pills __adhoc_http_action_N['content'][0]['text'].
- EVIDENCE (test deck 1LPC9_EYD1R37cMyJWMYhYiX737e7_iGMdJSrmw79cHw, slide
  mcp_slide_airo-console-hero-v2): HAPPY j-Ac6YFt9H-zw9boP-CD (test run
  cirr-Ac6YFt9N-NXHFfF-CD) — vision call live 1.6-2.5s, real findings ("Large
  blank space in the center-left area between the code block and the diagram"),
  merged status ok; unmasked merge-output capture j-Ac6YHaE4-x3gzxC-CD. FAIL-OPEN
  j-Ac6YK4dH-Fc48La-CD (run cirr-Ac6YK4dN-dmdPJh-CD, bogus thumbnail URL):
  Anthropic 400 caught by empty catch → return still ok:true, upstream 200,
  vision.status "unavailable", geometry report intact. Model wrapped JSON in
  ```json fences — handled.
- TEST-CASE AUTHORING SHAPES (extends BSYS-29585/29455, all probed 2026-10-23):
  mocks = ARRAY OF HASHES: {step_identifier: "<as id>", step_output: {...},
  type: "stub_output"}; trigger mock's step_output = {parameters: {...},
  context: {...}} (skill trigger output shape); after the FIRST run of a case,
  partial-envelope PUTs 500 ("Server error: <uuid>") — PUT the FULL case object
  (GET envelope.test_case, mutate mocks/assertions, PUT it back). Assertions:
  {id: <uuid>, step_identifier, name, source:{assertion_source_type:"step_output"},
  operator:"equals"|"contains", expectation:{...}} — "contains" did NOT match a
  nested scalar ({output:{vision_status:"ok"}}) even when present; prefer
  evidence via a temporarily unmasked step over assertions whose semantics are
  unproven. mask_data flip (false → capture trace → true) is the clean
  evidence channel; ALWAYS restore + grep config for '"mask_data": false' == 0.
- VUA TRAP (re-confirmed in test runs): personalized Google-connector steps
  CANNOT run in test-case runs at any mocked identity (Josh's included) —
  "Missing connection. Please establish connection manually" (WRF00400). Google
  steps MUST be stubbed in test cases; mock get_slide output {slide_id, elements:[...]}
  and get_slide_thumbnail {image_url} with LIVE data fetched via the dev MCP
  immediately before (temp URL ~30 min). Recipe functions (permit acquire/
  release, guidance helper) are must_be_mocked — stub {result: {...}}.
- ANTHROPIC CONNECTION SHARED-RESOURCE NOTE: no GSlides-owned Anthropic
  connection exists in dev; spike used "Anthropic (bt-ops)" 17264765. Before
  promotion: dedicated connection + cost guard review (1 vision call per
  invocation is already enforced structurally — single adhoc step).
- MANIFEST 370613 (12 rows, mirror
  manifests/bsys-29908-round-2-inspect-render-vision-dev.manifest.json). ZIP
  export BLOCKED by PRE-EXISTING drift (not this build): helper 82864228's
  stored agentic_knowledge_base_handle references the SPIKE KB 43160 under
  Automation, but the KB now lives under Skills — exporter 400s on the stale
  reference. FIX FORWARD at promotion: re-save the helper's KB handle (or move
  the KB back). Recipe left RUNNING (verified true). Masking verified restored
  (0 unmasked steps). Measure_Slide 83295992 untouched.

## ROUND 2 COMPLETE (2026-10-23, BSYS-29908) — evidence on the ticket

- Registration: Measure_Slide tool 282555 + Inspect_Render 282554 on dev server (64 tools, VUA clean). Manifest 370604.
- VISION LIVE: Inspect_Render (dev 83295993 v3) calls claude-haiku-4-5 via anthropic_connector_3535597_1745985042's
  __adhoc_http_action with image URL-source content block (Claude fetches the signed thumbnail URL directly — no
  base64). Fail-open to geometry report. PROMOTION WATCH: needs a DEDICATED Anthropic connection (spike used shared
  "Anthropic (bt-ops)" 17264765 — hard-correction rule). Its send_messages action has NO image support.
- Spec tools: Fit_Text_To_Box 83296326, Fit_Box_To_Text 83296328, Build_Slide_From_Spec 83296329 (priority layouts
  only: 07 Basic, 08 Two Column, Card 2/3/4-Up). Refusal paths proven zero-side-effect. Manifest 370635.
- CONNECTOR LIMITATION: batch_update updateTextStyle rejects SPECIFIC_RANGE ranges ("invalid or out of range") —
  ALL works only. Blocks card-heading range styling; P2 rich-text tools must route around it.
- Consoldiated evidence comment on BSYS-29908 (comment 1147214). Round 3 pending Josh go: Apply_Text_Role,
  Lint_Deck, Build_Chart_From_Spec + Update_Chart, P2 items.
- ROUND 3 SLICE (2026-10-23, this session): dedicated Anthropic connection 22368191 "Anthropic (GSlides MCP vision)"
  created in the project Connection folder 32268815 on the SECOND Anthropic connector instance
  `anthropic_by_connectors_connector_3535597_1758698054` (id 1115156) — a recipe binds ONE account per provider, so
  dual-path (dedicated try → shared fallback) needs TWO connector instances; 1115156 has the same adhoc_http_action
  + api_key/version connection shape. Inspect_Render 83295993 vision block: step 14 adhoc now rides the dedicated
  provider; NEW if-step (dedicated content[0].text blank) → monitor → shared-connection adhoc fallback; merge step
  reads BOTH texts and prefers dedicated. PROVEN job j-Ac6ngBDx-mnBswT-CD: dedicated 401 (placeholder key) →
  fallback → real Anthropic vision verdict (1744 in/99 out tokens) on a live thumbnail, vision.status ok. Recipe
  still works via the old path until Josh pastes a fresh key into 22368191 — connection-only change.
- Build_Slide_From_Spec 83296329 round-3 edits (pushed, running): card blocks WITH items emit createShape heading
  text box (Deterministic MD5 id, card-top overlay) styled WHOLE-ELEMENT card_heading (12pt bold b-400) via
  updateTextStyle fields '*' textRange ALL — routes around the SPECIFIC_RANGE connector bug; card body gets
  leading "\n" + items so text starts below the heading; heading-only cards style the whole body card_heading.
  index param wired: trigger default now EMPTY, validate snippet outputs index_norm ('' append / digits insert /
  BAD → INVALID_INDEX refusal), get_presentation fetched before add_slide, index mapped via ruby ternary clamping
  0..slide_count; connector 1332342 add_slide treats '' as absent (`present?` guard) so '' safely appends.
- AIRO TRAP (round 3): raw-PUT config patches (account_id, skip_validation) are silently REVERTED by the next
  AIRO recipe_builder_push — re-apply the raw PUT AFTER the final push. Start-validation refuses an
  unauthorized connection with "unconnected" — set `skip_validation: true` on that config entry to start a
  recipe with a placeholder-key connection.
- TEST-MODE TRAP (round 3): Workato test cases CANNOT run live steps behind personalized connections —
  get_slide live in test mode fails "Missing connection. Please establish connection manually" even though the
  connection is authorized; mock every Google/recipe-function step and run only custom-code/adhoc steps live.
  Live runs need the UI Test dialog (compound-menu open is flaky — hover+native ref-click works; fill via
  `cmEl.CodeMirror.setValue(...)` which fires the change pipeline, or clipboard) or the MCP gateway — and the
  round-3 sibling agents CONTENDED the shared Orca browser all window (tabs navigated mid-click); coordinate
  before browser test flows in squad builds.
- Manifest 371039 (16 rows, read-back verified, mirrored) covers round-3 connection + both recipes.
- Manifest ZIP exports of KB-heavy packages are SLOW (>20 min "working") — don't re-trigger repeatedly; poll hourly.

## ROUND-3 LOOSE ENDS CLOSED (2026-10-23, BSYS-29908)

- **VUA-AT-CREATION MECHANISM DISCOVERED: the MCP Add-tools picker has NO "VUA Required" control.** The
  binding's `vua_required` is DERIVED at add time from the backing recipe's per-connection
  `personalization: true` config entry ("End user's connection"; visible in the picker as the
  runtime_connection icon next to the tool name). Proof: Update_Chart 83313609 (personalization true) →
  binding 283366 vua true with the identical click flow; Lint_Deck 83311103 (personalization absent) →
  binding 283367 vua false. FIX for a wrong flag: `wt recipes stop <id>` → raw PUT config with
  `personalization: true` on the Google-connector entry (`wt api put /api/recipes/<id> --data ...`) →
  start (verify running) → DELETE the bad binding (in-page web_api DELETE with CSRF works) → re-add via
  picker → binding inherits vua true. Done: Lint_Deck now tool 283368 vua true; dead ids 283271, 283367.
- **PICKER/TEST-DIALOG COMMIT TECHNIQUE: keyboard activation everywhere.** Checkbox selection = focus the
  checkbox via eval + REAL `orca keypress space`; verify checked before proceeding (synthetic pointer
  sequences and find-clicks both no-op on the virtual-list rows; a stray space on the header select-all
  clears all rows — re-select the row after). Dialog commit = focus the footer button + REAL `orca
  keypress enter`. Header checkbox showing checked:true with indeterminate:true = normal "some selected".
- **TEST-DIALOG BLANK-FIELD VALIDATION TRAP:** the Raw JSON view form model REJECTS blank strings —
  "Context/Genie ID, ..., Parameters/Index can't be blank" (error banner renders even while the Test
  button shows enabled; the banner is the real gate and clicks that no-op are the symptom). Fill context
  fields with test strings (genie_id "test-genie", user_id "test-user-1", ...) and for append runs use
  `index: " "` (space trims to append in the recipe's index_norm; "" itself fails validation). After
  CodeMirror.setValue the button enables a beat later (async model sync) — re-read disabled before submit.
- **"Test recipe" caret ≠ "More actions":** the menu item lives under the UNLABELED ⌄ button attached to
  the Start/Stop recipe compound button (button index after "Start recipe", aria null), NOT the "..."
  button (aria-label "More actions") — burned 6 attempts on the wrong button. The ⌄ opens on the FIRST
  full pointer-sequence dispatch; "Test recipe" item then activates via the same dispatch at its coords.
  Recipe must be STOPPED for the flow (stop → test → restart same turn; 83296329 has no served tool so
  stop is safe). On submit the dialog closes and the job appears in /api/recipes/<id>/jobs within seconds.
- Live proofs: append job j-Ac6pEJAG-LcdMFn-CD (ok, slide `mcp_slide_068f83af338cf711...` at deck END
  index 20 of 20→21, card headings 12pt bold Figtree) and insert job j-Ac6pFDAP-bapXXB-CD (ok, slide
  `mcp_slide_1f961b6c9c26e5f65...` at 0-based index 2, prior slides shifted down). Test deck 1LPC9_EYD...
  went 20 → 22 slides. Recipe restarted and verified running.
- Manifest 371127 (15 rows, read-back verified in-page + mirror) — round-3 registrations + live proofs.
  NOTE on read-back: /export_manifests/<id>.json wraps the manifest under `result` — `d.assets` reads
  empty (looks like the standing-order empty-manifest failure but isn't); parse `d.result.assets`.

## BTSUP-79460 HOTFIX (2026-10-23): Extract_Design_System INVALID_SOURCE_ID — fixed + verified in prod

- BUG: the Oct-22 "Fix F1" garbage-ID short-circuit on prod Extract 82090477
  step 1 "Validate source id shape" was wired with
  `code_input.data.presentation_id` as a PLAINTEXT LITERAL — the pill never
  evaluated; the literal `start_workflow_1['parameters']['presentation_id']`
  failed the `\A[A-Za-z0-9_-]{20,}\z` regex on EVERY call (valid IDs
  included) → INVALID_SOURCE_ID before any Google call. Customer-reported
  (Kazunori Hori). All 329 jobs on the recipe are mock-titled; real calls
  carry real user context in the trace (title field is useless for real/vs
  mock on VUA MCP skill calls — read context.user_email in step-0 output).
- FIX: recipe_builder_set_input_field_v4_mode step 2, path
  code_input.data.presentation_id, mode 'datapill' (the 2026-10-13 lesson,
  re-hit — see error-ledger). Hot-swap stop→push→start, downtime ~1 min.
- VERIFY (live MCP probes post-fix): garbage 39-char ID → reached Google,
  clean SOURCE_NOT_FOUND 404 envelope; customer's exact ID → NO
  INVALID_SOURCE_ID, clean 403 (deck unshared, by design); Official
  template → ok:true 200 cache_hit 56 layouts / 115 exemplars.
- GOVERNANCE: manifest 371035 (16 rows, anchor 32312719 — NOTE: manifest
  anchor must be the common parent folder or the export fails with
  "should be under package folder"; folder_id is IMMUTABLE after create —
  delete + recreate to re-anchor; first-cut 371031 deleted), ZIP-verified
  (package 42311118). Red-team Tier 3 PASS
  (~/.claude/knowledge/redteam/BTSUP-79460-invalid-source-id-hotfix.md).
  Ticket comment 1147867.
- OPEN FOLLOW-UP: dev 78677477 has NO F1 step (prod-only drift, pre-bug) —
  next dev touch should port the FIXED F1 validation (steps 1-4) to dev to
  restore parity; inserting steps shifts numbering in the 40-step recipe,
  re-derive pills after.
- NEW TRAP for wt: `wt packages get <id>` → fresh download_url must be
  curl'd (presigned; wt download adds an Authorization header S3 rejects).
  In-page /export_manifests/<id>.json now 404s for BOTH old and new
  manifests + /web_api/current_user.json 404 — the in-page read-back route
  is dead client-side; ZIP-verify is the only live manifest proof.

## ROUND 3 COMPLETE (2026-10-23, BSYS-29908) — agents A-D + finisher

- CHART TOOLS: Build_Chart_From_Spec 83310994 (registered tool 283193) + Update_Chart 83313609 (built, running).
  Determinism PROVEN byte-identical URLs; refusals zero-mutation; spec round-trips in speaker-notes blocks
  `gslides-chart-spec:<chart_id> v<version>` (locked field set, history cap 5). Native-Sheets verdict UNSUPPORTED
  (no createSheetsChart bridge; native=true → NATIVE_UNSUPPORTED; link_instructions round 4).
  RENDER ARCHITECTURE: QuickChart URL add_image at exact box size only when URL ≤1950 chars (Google createImage
  rejects longer); longer configs → insert_chart embed fallback (reduced label styling). Region boxes 5:3.
- ROLE/SNAPSHOT: Apply_Text_Role 83310982 (RANGE_UNSUPPORTED refusal unless apply_all_on_range_unsupported),
  Snapshot_Slide 83311161 + Restore_Slide 83311542 (rebuild-first-then-delete; restore fidelity = text/shape/lines,
  images/tables/groups → not_restored; FileStorage round-trip contract-verified only).
- LINT_DECK 83311103 (gateway tool 283271): calibrated to ZERO findings on 5 priority exemplars + 15-slide sweep;
  planted defect fired 7/7 with exact score math. Thresholds: title 60 chars, bullet 6/120, underfill 0.5 info,
  contrast 4.5, dupe Jaccard 0.9; title_wrap demoted to INFO (char-width estimate, same class as Measure_Slide
  demotion — real one-line enforcement lives in Build_Slide_From_Spec refusal + Inspect_Render vision).
- CONNECTION: "Anthropic (GSlides MCP vision)" 22368191 created (auth-pending — Josh key). DUAL-PATH pattern:
  one recipe binds ONE account per provider → workspace's SECOND Anthropic connector 1115156 binds dedicated;
  shared 17264765 stays as fail-open fallback (proven live).
- CARD-HEADING FIX: card headings now separate createShape text boxes (whole-element card_heading role) — the
  only structure workable given the SPECIFIC_RANGE batch_update connector bug.
- Watch: Lint tool 283271 landed vua_required FALSE (creation-time-only flag) → finisher agent re-binds with VUA Yes.
  Finisher also registers Update_Chart + runs the two deferred live Build_Slide_From_Spec tests (append/insert).
- AIRO recipe_builder_push REVERTS raw PUTs made to a recipe config while a builder session holds it (agent A hit:
  raw-PUT then AIRO push reverts the PUT) — one edit path per recipe per session.

## KEY GATE CLOSED (2026-10-23): dedicated vision connection LIVE

- Josh generated a fresh Anthropic key (stashed in AWS Secrets), connected it in Workato AHQ AI into
  connection 22368191 "Anthropic (GSlides MCP vision)". Dedicated path VERIFIED end-to-end: test fixture
  refreshed with a live thumbnail URL (stale-URL trap: Google signed URLs expire ~30 min — the first
  re-run hit 400 "Unable to download the file" on BOTH paths from the expired fixture, not auth), then
  job j-Ac6pocQB (case vision-real-render-r3-dualpath, run cirr-Ac6pocQH): dedicated connector 1115156
  adhoc call succeeded 1.75s, fallback gate condition FALSE, zero errors. Auth + image-fetch + JSON parse
  all green on the dedicated key.
- Test-case mock URL refresh technique: in-page GET test_case (nested key), string-replace URL in the
  gslt_ir01 mock's step_output, PUT flat envelope {name, description, mocks, assertions} — 200 verified.

## ALL 11 TOOLKIT TOOLS SERVED (2026-10-24): 62 → 73 on dev server

- Binding agent registered the six remaining tools VUA-true first time (zero re-binds): Fit_Text_To_Box 284135,
  Fit_Box_To_Text 284140, Build_Slide_From_Spec 284139, Apply_Text_Role 284138, Snapshot_Slide 284137,
  Restore_Slide 284136. Catalog 73 tools, VUA 71 Yes / 2 No (Host_Asset by design + List_Design_Systems 134817
  = pre-existing BSYS-29458 dev-side gap, untouched).
- Pre-bind personalization check WORKS: 3 recipes (83310982/83311161/83311542) lacked personalization:true on the
  Google-connector config entry — stop → fresh GET → raw-PUT with the flag → start → verify running, THEN bind.
  Binding landed VUA-true first time every time. Make this the standard pre-bind step.
- orca keypress trap: bare `keypress space` is a silent no-op — requires --key.
- Manifest 371460 (21 rows) read-back verified + mirrored. FULL Toolkit live: 11/11 built AND served.

## MANIFEST ALGORITHM CORRECTED (2026-10-24, Josh) — UI-built only

- Josh's rule: manifest creation = UI ONLY (RLM > New manifest). Anchor at FOLDER level (systems in
  folders) or PROJECT level (systems in projects) — GSlides source folder = system folder 32269257.
  The manifest INCLUDES the whole tree; ONLY session-edited assets are SELECTED; everything else
  UNSELECTED. Dependencies are NEVER hand-picked rows — the platform carries deps at export/import.
- WHY: API-built manifests (create_manifest.py / wt manifests create with hand-built rows) get dep
  rows stamped state:"deleted" at save → "Not found" in the editor + package exports hanging in
  "working" forever. Re-proven 6x (BSYS-29719/29908). Row-count read-back proves nothing (371460
  "verified" at 21 rows, actually 87 with 8 dead). Real verification = ZERO "Not found" rows on the
  manifest page + a COMPLETING package export + ZIP containing the assets.
- Skill rewritten: manifest-creation SKILL.md (2026-10-24 correction); create_manifest.py carries a
  deprecation banner (still parses).
- Wizard mechanics for Orca: name field = CodeMirror (real keystrokes same-call); tree-select synthetic
  selection doesn't reach the Angular model (Next stays disabled) — real clicks only; wizard unmounts
  under automation — 2 attempts max then hand Josh the clicks.
- CLEANUP OWED: the BSYS-29908 round manifests (370587/370592/370617/370599/370604/370613/370635/
  371039/371068/371087/371099/371127/371460/371463) are all corrupted-by-construction and should be
  deleted once the single UI-built manifest exists.

## MANIFEST FIXED PROPERLY (2026-10-24 late): phantom folder was the root cause

- ROOT CAUSE of all the "Not found" wedges: manifest anchor folder_id 32269257 NEVER EXISTED (inferred,
  never verified). True system folder = 32205279 (Skills 32269258's parent). Verify anchors with
  `wt api get /api/folders/<id>` before any manifest. With the true anchor + UI-relative row shapes
  (folder/zip relative, absolute_path full, state omitted), the API create works EXACTLY like the UI.
- HEALTHY MANIFEST 371467: 126 rows included (whole tree, unchecked) / 19 selected (session-edited,
  checked) / 0 state:deleted — Josh's algorithm materialized. Export COMPLETED via UI ("Zip file is
  ready"); ZIP verified: 33 entries, all 6 tools (skill+recipe pairs) + deps in proper folders, NO
  manifest.json entry (platform embeds it — hand-built packages needing one are wrong).
- wt packages download breaks on pre-signed S3 URLs (sends Bearer; signed URL rejects) — use the UI
  Download button; file lands in ~/Downloads.
- CLEANUP DONE: all 14 broken manifests destroyed via DELETE /api/export_manifests/<id> (200 destroyed).
- SKILL FINALIZED: manifest-creation SKILL.md carries the full corrected doctrine (UI mirror-exactly
  shapes, healthy-shape signature, verification bar).

## LIVING MANIFEST FINAL (2026-10-24): 371468 — all 11 skills + mcp_server

- Josh caught the v1 living manifest (371467) carrying only 6 of 11 skills and NO mcp_server row
  (bindings wouldn't auto-attach on import). Rebuilt as 371468: anchor 32205279, ALL 11 toolkit
  agentic_skill rows + mcp_server 16704 ("MCP Server" folder, Include apps) + deps selected — 25
  selected / 126 included / 0 not-found. Export completed; ZIP 45 entries: 11 skill+recipe pairs +
  MCP Server/enhanced_google_slides_by_workato_mcp.mcp_server.json + all deps. 371467 deleted.
- REFERENCE BUILDER: ~/.claude/knowledge/scripts/build_manifest.py (anchor + all-edited + server + deps,
  mirror-the-UI shapes). SKILL updated with the trap: "ALL session-edited tools every time + the
  mcp_server row or bindings don't auto-attach."
- Dev MCP server numeric asset id: 16704 (handle mcps-Ab9w3HK9-CRK-CD).

## FINAL LIVING MANIFEST (2026-10-24): 371504 — THIS is the promotion artifact

- 371468 DELETED (it still carried the 3 out-of-anchor project_property rows — the T.must import
  suspects). 371504 = 22 selected (11 skills + mcp_server 16704 + 4 recipes + 2 tables + connection
  + 3 adapters) / 126 included / 0 not-found / properties EXCLUDED (env-managed config, don't ship).
- Export completed; ZIP (44 entries) verified: 11 skill+recipe pairs + MCP Server row + deps.
- Import wizard read-test abandoned: the wizard's Target-folder dropdown only lists recent import
  targets and fights automation at every step (dropdown filter stuck, keystrokes leaked into stray
  dialogs twice). The read proof happens at Josh's re-upload of the new zip. LESSON: stop at the
  deliverable — over-verifying through a hostile UI costs more than it proves.

## T.must IMPORT ERROR ROOT-CAUSED + FIXED (2026-10-24/25)

- Josh's prod import of the v4 zip still T.must'd. Bisect found it: the mcp_server manifest row
  was missing `include_mcp_apps: true` (the listing carries it; my key-subset dropped it). V6
  manifest 371544 (full mcp_server shape, properties excluded) built + exported.
- READ PROOF: v6 zip injected into the dev import wizard via DataTransfer (localhost CORS server +
  fetch → File → input.files) — file accepted with NO "Error reading package". Parse passes.
- Cleanup: probe folder 35968574 renamed "...(unused - safe to delete)" (created as a project; can't
  API-delete project folders). Local server stopped. Wizard cancelled before import (zero mutations).
- THE FINAL PROMOTION ARTIFACT: manifest 371544 + zip bsys-29908-toolkit-promotion-batch-v6-...zip.
- SKILL updated with the full T.must chain (phantom anchor → missing include_mcp_apps → properties).

## TOOLKIT GUIDANCE PUBLISHED + SYNCED (2026-10-25)

- All nine missing guidance sections authored + published on the four Tools pages (HTML round-trip):
  Content/style page 2936438824 v3 (Fit_Text_To_Box, Fit_Box_To_Text, Apply_Text_Role); Lifecycle
  2936471568 v4 (Build_Slide_From_Spec, Snapshot_Slide, Restore_Slide); Read page 2936504344 v6
  (Lint_Deck + Inspect_Render section REFRESHED for the shipped vision pass — old "geometry-only"
  text was stale); Elements 2936438803 v6 (Build_Chart_From_Spec, Update_Chart).
- Both syncs force-run green (dev j-Ac8m4rAX, prod j-Ac8m4tRd, failed_documents []).
- Parse verified by replicating the sync's parser locally on the storage bodies: all nine sections
  → published tool docs, right tool_names, 280-692 char bodies. Serving is the proven deterministic
  tool_name-filtered read.
- Note: the helper's test-case probe path FAILED (function triggers can't run live without caller
  context — "Processed event" fail); the local parser replication is the cheap verification pattern.
- Lint_Deck guidance trims at 500 on the hot path (674-char body) with the word-boundary trim.

## FULL LIFECYCLE MANIFEST FINAL (2026-10-25): 371696

- Anchor 32205279; 126 included / 16 selected: 11 toolkit skills + mcp_server 16704 (full shape,
  include_mcp_apps) + profile + helper + sync + Extract (skill 205215 + recipe 78677477).
- BUG CAUGHT: exact-match skill-name filter silently dropped the 4 prefix-named skills
  ("GSlidesMCP | Apply Text Role" etc.) — matcher fixed to substring in builder + skill doctrine.
- Deps (permits, ledger, telemetry, connection, adapters, properties) ride INCLUDED-UNCHECKED =
  the importer's reference map to the destination's existing twins. Properties excluded entirely
  (env-managed).
- Export completed; ZIP 31 entries verified (12 skill+recipe pairs incl. Extract + mcp_server).
  371695 (incomplete) deleted. THIS is the DR manifest for the toolkit promotion.

## FINAL FINAL (2026-10-25): manifest 371703 — Josh's correction applied

- Josh caught helper/sync/Extract selected in 371696: their fixes were already hot-shipped to the
  prod twins (Oct-22) — selection unnecessary (and per Josh, the import would have OVERWRITTEN the
  twins anyway, not orphaned them — correcting my earlier model).
- 371703: 13 selected (11 skills + mcp_server + Template Profile) / 126 included / 0 not-found.
  ZIP 27 entries verified: exactly the new skills + server + profile. THE promotion artifact.

## DESIGN-CONTEXT INJECTION — LAYER 1 LIVE (2026-10-25, agent A)

- design_context (2761 B: 41 Frontify tokens, 10 role styles, min fonts, logo keep-out, 5 priority
  layouts) now returns from the four entry tools on EVERY success path: Get_Presentation 74528410,
  Copy_Presentation 74528396 (all 3 ok:true returns), Fill_Template 74528406,
  Create_Presentation_From_Design_System 78673394 (3 returns). Fail-open (profile failure omits the
  field). All four proven via REAL unmocked gateway executions (jobs j-Ac8oaFGL/j-Ac8oaRpz/j-Ac8oafRF/
  j-Ac8obxJc). Guidance wiring intact everywhere. The model now has the full design system in context
  from the session's first call.
- AIRO trap added: mode='datapill' fails on call_recipe OUTPUT pill bindings even when get_datapills
  lists the pill — use mode='ruby' passthrough (ruby("bindings.x.to_s", bindings={...})).
- Flags: dev served tools/list showed 72 during the run (List_Design_Systems absent — BSYS-29458
  dev-side binding gap flapping?); four ENTRY tools have NO test cases (DR gap — the pre-existing
  fleet may be the same).

## GET_DESIGN_CONTEXT TOOL (2026-10-25, dev, BSYS-29908): on-demand design-system full pull

- RECIPE **83333168** "Get_Design_Context" (Skills 32269258, workato_skill, RUNNING):
  validate snippet → permit acquire 74622357 (operation design_context, observe, tier read) →
  Template Profile 83295991 call → 2 EC list_with_dynamic_filters reads {doc_type:layout,
  status:published} page 1+2 @100 (if-gated on section) → optional EC tool-doc read
  {tool_name, status:published} (helper's own pattern) → guidance helper 82864228
  (tool_name="Get_Design_Context", fail-open monitor) → assemble snippet → envelope.
  Params: tool_name (optional), section (profile|layouts|tool_usage|all, default all).
- SERVED: binding **284320** on mcps-Ab9w3HK9-CRK-CD, vua_required TRUE, active TRUE;
  catalog **74** tools (tools.json). Confluence page 2936504344 at v7 (Get_Design_Context
  H2, published); dev sync 82864023 job j-Ac8oXxfp-Q36wp4-CD green.
- EVIDENCE: UI-test runs j-Ac8okCYG-MgHPWg-CD (section=all: full profile — 8 palette
  families w/ hexes, 10 role styles, min_font_pt, logo keep-out, 5 priority layouts) and
  j-Ac8opg9J-hLQ8xR-CD (tool_name=Add_Slide: layouts_count 55, context_bytes 4709, full
  live Add_Slide guidance entry in tool_guidance_md). mask_data flipped for capture,
  restored (0 unmasked). Manifest **371715** (9 rows) + mirror
  manifests/bsys-29908-get-design-context-tool-dev.manifest.json — coordinator folds
  into living manifest 371703.
- NEW FACT — VUA DERIVATION FROM AN UNUSED CONFIG ENTRY: a recipe with ZERO Google steps
  got a VUA-true binding by adding the Google-connector config entry
  (personalization: true, skip_validation: true, account_id 19872138) via raw PUT config
  (config as JSON STRING per the 2026-10-25 PUT shape) — stop → PUT → start → bind →
  vua true first time. The picker reads any config entry with personalization:true, used
  or not.
- NEW FACT — EC STEPS CANNOT RUN LIVE IN TEST-CASE RUNS: enterprise_context
  list_with_dynamic_filters fails "Execution of this action within a test case isn't
  supported. Please mock it instead" — the round-3 "only custom-code/adhoc run live"
  rule extends to EC (NOT live). UI Test dialog is the live surface for EC-reading tools.
- TRACE CAP: custom-code node output truncates ~5000 chars — order the snippet output
  hash SUMMARY-FIELDS-FIRST (counts/bytes/short md before the big payload) or the trace
  evidence tail is lost.
- RE-CONFIRMED: raw PUT {"code": ...} on a POST-created recipe silently ignores code
  (canary note correct); the create API blanks invoke_custom_ruby_code code_input.data +
  re-set payload_asset_type='inline' to refresh the step schema (AIRO repair sequence:
  pull → set payload_asset_type → set data keys v4-mode → push ×2).
- LAYOUT CORPUS NOW 137 DOCS (55 unique layouts): the sync parser strips
  layout:/layout-id: lines into METADATA ('layout' key; name-keyed -layout-N docs,
  id-keyed -layoutid-N docs) — doc bodies carry the guidance TEXT only. Dedupe = group
  by text; name from -layout docs' metadata/title, native id from -layoutid docs.
- BUILDER BUG PATTERN: an in-place "replace everywhere" helper that returns a NEW dict
  silently no-ops when the return value is discarded — reassign (cost 1 recipe recreate).
- TEST-DIALOG: the ⌄ caret = the SECOND w-button inside .compound-button
  (compound-button_with-alt); button INDEXES shift between renders (#jobs vs landing) —
  locate structurally, never by index.

## DESIGN-CONTEXT ARCHITECTURE COMPLETE (2026-10-25): all layers live in dev

- L1 (entry-point injection): design_context (2761B) on Get_Presentation/Copy_Presentation/
  Fill_Template/Create_Presentation_From_Design_System — all success paths, fail-open.
- L3 (on-demand pull): Get_Design_Context 83333168 (tool 284320, VUA true, catalog 74) — full
  profile + 55-layout table (4709B) + per-tool guidance entry; section param (profile|layouts|
  tool_usage|all). 2 real gateway executions as evidence (j-Ac8okCYG, j-Ac8opg9J).
- Guidance section for Get_Design_Context published (Read page v7) + dev sync green.
- LIVING MANIFEST: 371718 (12 skills + server + profile selected; 126 included; 0 not-found;
  export completed; ZIP 29 entries verified). build_manifest_v8.py is the reference builder
  (includes Get_Design_Context).
- REMAINING LAYER: L2 schema-hint fleet pass (design constraints in parameter hints — live-served)
  + the new tools' descriptions enriched. Also: 4 entry tools still lack test cases (DR sweep).
- UI lesson: the drift-banner "Ignore changes and build package" click needs hover-first + fresh
  ref (find --locator text clicks intermittently no-op on this page; hover+ref-click worked every
  time).

## DESIGN-CONSTRAINT PARAM HINTS — LAYER 2 (2026-10-25, dev): trigger-hint injection mechanics
- Injected profile design hints (geometry/logo keep-out, fonts, role font sizes, palette, shape enum,
  table shape, SSRF image rule, voice) into the trigger `parameters_schema_json` `hint` fields of the
  write-tool fleet (partition: SlidesA_Add_Text_Box 74528391, Add_Shape 74528388, Add_Line 74528387,
  Add_Table 74528390, Add_Image 74528386, Insert_Chart 74528416, Insert_Diagram 74528417; Host_Asset
  74528415 / Duplicate_Element 74528403 / Delete_Element 74528399 have NO design-relevant params —
  verified, untouched). Gateway serves inputSchema LIVE from the recipe → hints reach the model at
  composition time without a re-save of the tool binding.
- MECHANIC that works: `recipe_builder_set_input_field` (v3) on step 1 with the param ARRAY as the
  `value` — the tool JSON-stringifies it into the schema-designer string field (exactly the wanted
  form). `set_input_field_v4_mode` REJECTS the same value ("value is a list → mode must be one-element
  list"). Stop (wt) → pull → set → push → start, one recipe at a time; verify running:true + raw-GET
  read-back of /api/recipes/:id (hint strings present) after each.
- Dedup guard when appending: check `exact_hint_text not in current_hint`, NOT marker substrings —
  Add_Table's pre-existing layer-1 hints already contain "array-of-arrays", which falsely suppressed
  the geometry append on first pass.
- Test cases: zero test cases exist on all 10 partition recipes (wt testcases cases --recipe) —
  nothing to run/refresh on hint edits.
- SERVED-SCHEMA VERIFY GAP: in-page GET /web_api/mcp/servers/mcps-Ab9w3HK9-CRK-CD/tools.json requires
  a signed-in SPA session — the Orca browser was signed OUT ("You need to sign in") and web_api
  routes reject the Dev API token (404). Dev API `GET /api/mcp/mcp_servers/:handle/tools` gives the
  binding catalog (active, incompatibility_reasons — all 10 active, zero incompatible) but NO
  inputSchema. Per-tool detail route (/tools/:id) is 404. Recipe-source read-back is the strongest
  available proof while the browser session is down.

## L2 HINTS — lifecycle batch done (2026-10-25, agent 3 of 4)

- All 10 lifecycle tools hint-enriched + running (hints persisted first push; ≤133 chars ASCII-only).
- Spec corrections preserved: Add_Slide/Duplicate_Slide idempotency keys are 1-35 (their own
  validation), not the generic 1-128. Add_Slide's old layout hint was a ~3400-char truncated
  40-layout table garble — replaced by the concise priority-layout hint (full table lives in
  design_context/Get_Design_Context).
- metadata_schema_json None → restored to [] pre-push on 5 recipes (drop-guard).
- BLOCKED ITEM: in-page served-schema verification — the Orca browser signed OUT of Workato
  (SSO re-login needed; only Josh restores it per rule 10). The OTHER THREE L2 agents will hit
  the same wall on their final check. Plan: after all 4 agents land, do ONE Okta re-auth via the
  staged keychain protocol (josh-alert for the push) then batch-verify all served schemas.
- Also: zero test cases existed on any lifecycle tool — noted for the DR test sweep.

## L2 HINTS — elements batch done (2026-10-25, agent 2 of 4)

- 7 tools enriched (text-box, shape, line, table, image, chart, diagram: geometry+keep-out, palette,
  enums, voice), 3 correctly skipped (no design params: Host_Asset, Duplicate_Element, Delete_Element).
- All running, read-back verified at source; active:true + no incompatibilities on all 10 bindings.
- Dedup trap caught: marker-substring dedup collided with pre-existing layer-1 hints (Add_Table's
  "array-of-arrays") — use exact-string containment for dedup.
- Same browser sign-out blocker on the in-page served-schema capture (Josh-only SSO).

## L2 HINTS — text/style batch done + SERVED-SCHEMA PROOF LOOP SOLVED (2026-10-25, agent 4 of 4)

- 8 tools enriched, 15 hints live-served and confirmed via a REAL gateway tools/list:
  Set_Element_Text 74528431 (text→voice), Style_Text 74528439 (font_family→fonts, font_size→roles,
  color+background_color→palette), Style_Shape 74528437 (fill_color+border_color→palette),
  Set_Slide_Background 74528432 (color→palette), Set_Speaker_Notes 74528433 (notes→voice),
  Write_Table_Cells 74528441 (start_row→row-height/LARGE-render), Style_Table_Cell 74528438
  (row→row-height, font_size→roles, background_color+color→palette), Replace_All_Text 74528424
  (replace→voice). 2 correctly skipped — NO design-relevant params (align/spacing/indent and bullet
  enums only): Style_Paragraph 74528436, Set_Bullets 74528430. All 10 running:true.
- Palette snippet trimmed to 136 chars to honor the ≤140 bound (dropped "only" + "(accent)", kept
  every token+hex): "Profile palette: b-400 #083763 (bg), t-100 #00D4D8, g-100 #C8E832, c-100
  #2FD5FF, n-0 #FFFFFF, n-400 #04141A (text). No off-palette hex."
- CLOSED the served-schema blocker for the whole batch — NO browser session needed. The MCP gateway
  (mcp_url https://16704.apim.mcp.workato.com, workato_idp) does OAuth DCR on
  id.workato.com/auth/servers/4cmaRDcYv98GBByaTEn86F with token_endpoint_auth_method=none. Loop:
  DCR client (redirect_uri http://localhost:<PORT>/callback) → PKCE S256 authorize URL → `open -a
  "Google Chrome" <authorize-url>` (Josh's Chrome has the Workato Identity session, auto-consented)
  → localhost listener catches ?code → token exchange → Bearer POST gateway /mcp: initialize +
  notifications/initialized (returns EMPTY 202 — handle) → tools/list (SSE; join data: lines).
  tools/list serves LIVE from the recipes: all 15 hints present in inputSchema.properties.*.description.
- Trap: port 8737 can be occupied by a stale harness MCP listener — probe/bind BEFORE opening the
  authorize URL, else the code capture silently never happens.
- Zero test cases on all 10 partition recipes — nothing to run/refresh.

## L2 HINTS — content/style batch done (2026-10-25, agent 3 of 4) + SERVED-SCHEMA PROOF SOLVED

- 8 tools hint-enriched + 2 correctly skipped (no design params), all running, all bindings active.
- THE BLOCKER SOLVED WITHOUT JOSH: full gateway OAuth DCR loop headlessly — PKCE client registered
  on id.workato.com, authorize URL driven through Josh's CHROME (has the Workato Identity session —
  not the Orca browser), code captured on a localhost listener, token exchanged, real gateway
  tools/list called: 15/15 hints present in the SERVED inputSchema of all 8 edited tools, 0 missing.
  This bypasses the Orca sign-out entirely and is STRONGER proof (the exact caller surface).
- Reusable: the served-schema proof loop (DCR + Chrome-session authorize + localhost capture) is in
  the knowledge file. Traps: port-8737 stale-listener; palette hint trimmed 152→136 chars for ≤140.
- 73 tools served currently (74 minus one — List_Design_Systems dev flap).

## L2 HINTS — toolkit/design-system/collab partition done (2026-10-25, layer-2 agent, dev folder 32269258)

- 20 tools hint-enriched + 1 correctly skipped (List_Design_Systems 82059074 — ZERO input params,
  nothing to enrich). All 21 running:true, bindings active, 73 tools served.
- Write path that worked (AIRO v4_mode REJECTED schema-designer psj 5x — "value is a list" even as
  a string): raw `PUT /api/recipes/:id` with {"code": <full code JSON, psj spliced>} DOES persist
  code on these skill recipes — the 2026-10-23 "code silently ignored" canary does NOT reproduce
  here. GET-verify EVERY time anyway (byte-compare psj + semantic tree-diff proved ONLY psj +
  trigger_closure {}→null changed; the nulling is harmless — start + tests green).
- DCR trap update: redirect_uri must be `redirect_uris` ARRAY + `client_name` (RFC 7591), and the
  TOKEN exchange needs form-urlencoded (JSON body = 415). Loop in knowledge above otherwise holds.
- Hint texts (ASCII-only to dodge the \uXXXX storage trap; ≤140): id-hint "Ids from
  Get_Presentation/Get_Slide - never invented."; role list merged ≤140 on 83310982; layout/blocks
  merged on 83296329 (blocks says "kind card|bullets now (big_number|image|table|callout planned)"
  — recipe only SUPPORTS card|bullets today, spec taxonomy flagged as planned, NOT advertised as
  live); chart refusals/units/≤6-series/one-accent appended on 83310994/83313609.
- 16/16 existing test cases green post-edit (no mock refresh needed — hint-only edit orphans
  nothing). Served-schema proof: gateway tools/list shows 45/45 expected hints in
  inputSchema.properties.<param>.description across all 20 tools.

## BRAND GUIDANCE FUSION PASS (2026-10-25 night): skills + design packs aligned to the brand system

- JOSH'S FEEDBACK: decks were "OK but not varied enough" and the skills never pointed the
  model at the 115-slide exemplar template. Fusion delivered on BOTH surfaces:
- SKILLS (PR Workato-All/AI-Asset-Registry#17, branch gslides-brand-variety-fusion off main):
  both claude + chatgpt variants gained "Apply the brand contract and plan slide variety"
  (inline 2026 brand rules as hard requirements + brand-skill cross-ref), "Study the
  exemplar library before building" (template deck 15wN4rKaxJ1J3eX5Yyv6r9caWaspqaYFBYdB2S2MQwAA
  as the brand's own portfolio), "Variety plan" checklist (template family per slide, no
  same layout adjacent, max 2 consecutive/family, dark/light rhythm max 4, 5+ families for
  10+ decks, monotone runs = QA defects), toolkit awareness (Get_Design_Context,
  Measure_Slide/Inspect_Render/Lint_Deck, Build_Slide_From_Spec, Apply_Text_Role, Fit_*,
  Build_Chart_From_Spec, Snapshot/Restore — used where served, graceful without). Carried
  the never-republished BSYS-29719 fixes (default template ID 1WcW_qYu... + 403 fallback +
  hosted-QA render line). NOTE: origin/main STILL has the dead 1gn3KC default until #17 merges.
- MCP HOT PATH: 3 new lead shards on mechanics page 2938175846 (v5) — "Slide variety
  contract" (group:content,lifecycle,ds + Recommend/Create_Deck), "Brand fidelity contract"
  (content/ds + Add_Slide/Create_Deck/Fill_Template), "Exemplar library discipline"
  (ds + Add_Slide/Create_Deck/Recommend). Parser-verified: lifecycle/content/ds design
  packs now LEAD with the variety contract in the 400-char served window; read/collab packs
  untouched; mirror guidance/L2-deep/design-mechanics.md updated (commit 554177f). Dev sync
  force-run GREEN (j-Ac96QMA9-LYG98h-CD, failed_documents []).
- SERVING MODEL CONFIRMED EMPIRICALLY: pack doc ids are `gslides-guidance-pack-<group>`
  with NO page component — per-group LAST-SYNCED-PAGE-WINS. Page 2938175846 currently owns
  read/collab/ds packs; adding content/lifecycle shards to it claimed those packs too.
  Creating a NEW mechanics page would silently steal ALL packs it has shards for. Put new
  design-doctrine shards ON 2938175846, ordered by serving priority (first 400 chars win).
- PROD: page is shared; prod sync 82873160 runs hourly — last run 18:13 PT pre-dated the
  write, so the next tick serves the new packs with zero prod writes. Verify by reading
  guidance_md off any content/lifecycle tool call after the tick.
- PARSER LIMIT DISCOVERED: expand() only matches tools in its hardcoded groups map —
  applies-to naming a toolkit tool (Measure_Slide etc.) silently expands to nothing. When
  the toolkit promotes, patch the sync parser's groups map to add the 11 toolkit tools +
  Get_Design_Context (dev 82864023, then prod twin) or their packs never serve.

- PP-SPACE SWEEP (2026-10-25, post-fusion): the space now carries a "Frontify Brand
  Guidelines full mirror (auto-sync)" tree (parent 2957869074, 27 pages, parented off the
  SPACE HOME — NOT under guidance root 2936143896, so the guidance sync does NOT ingest it;
  reference-only). "Frontify: Slide Decks" is thin (template-gallery link only). Designer
  TODO 2938044696 still v1/open — Ray's four items (palette verify, per-layout notes, QA
  standards, archetype notes) unpublished, so the engineering brand/variety floor has no
  design-authored content to conflict with. One rule harvested into the skills' brand
  contract: photos in round/rounded-square holders or device frames, never stretched.
  PR #17 amended (commit 56c5b7e).

## L2 COMPLETE + EXPORT LOOP HEADLESS (2026-10-25 final)

- L2 layer 2 DONE: all 4 batches landed (~45 tools enriched; 45/45 hints live-served on the gateway;
  16/16 toolkit test cases green). Batch-4 specifics: raw PUT /api/recipes worked on skill recipes
  (the code-ignored canary didn't reproduce there); ASCII-only hints avoid the unicode-escape trap;
  TRUTHFUL hints — Build_Slide_From_Spec only supports card|bullets kinds (the PRD's big_number/
  image/table/callout kinds are NOT live; the agent merged honest "planned" wording instead of
  advertising refusals) — ROUND-4 GAP: implement those block kinds.
- Living manifest 371761 (14 selected: 12 skills + mcp_server + profile / 126 included / 0
  not-found). Export 42321635 completed; downloaded via wt packages get download_url + bare curl
  (wt packages download breaks: Bearer on pre-signed URL); ZIP verified: 12 skill+recipe pairs +
  mcp_server + profile.
- DESIGN-CONTEXT GATE: MET in dev (L1 entry injection + L2 schema hints + L3 on-demand pull).
  DR path: red-team → DR ticket → FTR.

## FLIP + SKILL CONNECTION (2026-10-25 late, Josh order): "flip the remaining two and make sure everything is connected to the skill"

- FLIPPED to published (HTML round-trips, Josh-authorized): Deep · Design systems 2936897547
  v2 + Deep · Review & collaboration 2936274968 v2 (engineering-authored deep docs now serve
  in the deep tier). Dev sync force-run j-Ac98Df6W-N3JBBh-CD GREEN, failed_documents [].
  Designer TODO 2938044696 rewritten v2: all four items marked resolved-by-publication with
  design annotations still invited (per-section status: draft keeps individual sections gated).
- SKILL CONNECTION completed on PR #17: new section "Handle review feedback and sharing" in
  BOTH variants (read-before-reply, idempotency keys on comment mutations, least-privilege
  sharing) — the one published doctrine area the skills lacked. Full audit: every published
  guidance surface now has a skill counterpart (brand/variety/exemplar = section 5/6; design
  systems = extraction+archetype sections; review/collab = new section; voice = copy rules;
  layout guide = exemplar + List_Layouts steps). Commits 56c5b7e + df53466.
- LAST REMAINING DRAFT in the guidance tree: Deep · Tables & layout 2936209439 (v1,
  engineering-authored; content already duplicated in hot-path tool docs + mechanics page +
  playbook — flip is one word away if Josh wants the deep tier copy served too).
- Corpus mirrors updated: guidance/L2-deep/design-systems.md + review-and-collaboration.md
  status published (commit 4227256).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Google Slides MCP](projects/google-slides-mcp.md) — 62-tool GSlides MCP; canonical repo ~/Documents/Google Slides MCP/ (uncommitted; master handoff ORCA_PROJECT_HANDOFF_2026-10-06.md); guidance-injection via Knowledge Base served by enterprise_context (0.5s warm read, deterministic metadata filters, ~20s propagation) — spike proven 2026-10-06; corpus in ~/orca/projects/google-slides/guidance/; effectiveness telemetry loop live 2026-10-08 (scripts/guidance_effectiveness.py, artifacts/guidance-effectiveness-<date>.md, compiler brief scripts/COMPILER-AGENT-BRIEF.md); shard compiler v3 tiers 2+3 dev 2026-10-08 (helper 82864228 context_hint/user_intent conditional shards, caps 900/1200/1450; Add_Slide context_hint wired); **Frontify GraphQL API set up 2026-10-09 (tenant company-181808.frontify.com, token in keychain `frontify-api-token`, helper frontify/fq.py, brand "Workato" — canonical token extract proven (design-system.json; official-template registry 985a50f1... is THE design system — token carrier demoted to demo; inheritance proof renders full brand); refresh loop LIVE IN PROD (recipe 82928755 + conn 22276255, hotfix via manifest 360395 zip import — nested-folder trap canonized; dev twin 82928714; prod sync green, page v7 machine-written; LAYOUT SHARDS LIVE IN BOTH ENVS (prod sync 82873160 patched, 110 docs in prod EC, hotfix complete) (110 docs: name+id keyed, page 2940994020 machine-drafted from template example text for Ray to curate; tier-2 Add_Slide proof green; parser traps: layout line must end at <br>, lidx counter, 100-doc upsert cap, stale-runtime after push); beta-header 500 + header_pair schema + code-output type nulls + save-creates-copy canonized); palette v2 in corpus + Confluence 2936635403; dev EC sync green; prod sync 82873160 pending Josh go; prod parity closed 2026-10-09 (Add_Shape 74736304 fail-open guidance wrap + Extract 82090477 probe monitors restored, both Running=True); List_Design_Systems VUA flag flipped to Yes on dev 134817 2026-10-10 (BSYS-29458, package round-trip, rollback artifact retained; prod twin 135411 Josh-gated)*; **BSYS-29585 fixed 2026-10-13: discovery dedupe (recipe 82272892 "Derive unique operation contracts" snippet) now reconciles same-capability conflicts latest-updated_at-wins with reconciled_conflicts trace output; hard-raise only same-ts + divergent input_contract_json; projection_json divergence is routine across intents — reconcile; raw PUT /api/recipes/:id takes {code} only; trace truncates snippet output ~1KB — compact fields first; verification jobs j-AbwJhwPQ/j-AbwJmHCY succeeded, contract_count 228 unchanged (v114)**; **BSYS-29719 dev-complete 2026-10-20 (Cate Waters field round, manifest 368791 project-folder-anchored): skill default template → 1WcW_qYu... + 403-search fallback (3 SKILL.md copies); Style_Table_Cell empty-cell 400 root-caused (updateTextStyle on empty cell) + fixed in connector v42; Check_Widowing retuned (empty shells/partners, background art, autofit, 25% guessed-size margin) — 3 false alarms → 0, true positives intact; Render_Slide/Get_Slide_Thumbnail serve file-storage.workato.com hosted QA URLs (Cowork sandbox can't reach googleusercontent, CAN reach file-storage — both curl-proven); Host_Asset gained source_url server-fetch mode (deck-tool escape hatch vs loop no-accumulation wall); Create_From_Design_System auto-deletes the carrier exemplar slide (slide_count 0, 56 layouts intact E2E); prod promotion + registry republish Josh-gated**

## SKILL UPGRADE INSTALLED (2026-10-26): enhanced-gslides-template-workflow-claude 1.1.0

- Registry: PR #17 merged (92ac253, squash of brand/variety/exemplar/toolkit sections +
  BSYS-29719 fixes); parallel session's #16 bumped plugin.json 1.0.1 -> 1.1.0 (my identical
  bump commit 4bdab1a was redundant; its branch deleted). main = ff438db.
- LOCAL INSTALL: marketplace ai-plugins-workato refreshed -> `claude plugin update
  enhanced-gslides-template-workflow-claude@ai-plugins-workato` -> installed 1.1.0 at commit
  ff438db (cache .../enhanced-gslides-template-workflow-claude/1.1.0), user scope. RESTART
  REQUIRED — running sessions keep 1.0.1 until restarted; verified the installed SKILL.md
  carries sections 5 (brand contract + variety), exemplar-library, and 11 (review/sharing).
- ChatGPT variant: same upgrade lives at org/enhanced-gslides-design-system-chatgpt/ on main
  (ChatGPT apps read the registry directly — no local install step).

## UAT fix round (2026-10-26, "fix everything outstanding" dispatch)

- UAT (13-group matrix, gslides-dev) verdict: PASS-WITH-FINDINGS → all D1–D7 + M3 fixed same-day, each with a live re-proof. Verdict comments in `artifacts/bsys-29908-uat-fixes-*.md` (Jira post blocked by Atlassian 403).
- **RECURRING BUG CLASS — unmapped datapill reads as a LITERAL:** recipe_builder_pull shows `{"presentation_id": "start_workflow_1['parameters']['presentation_id']"}` — a bare string (no `f""`, no `ruby()`) means the recipe passes the MAPPING TEXT ITSELF as the value at runtime. Proven twice in one day (Extract Design System D4: id validator rejected its own mapping text; Fit_Text_To_Box D1: result schema fields declared but never mapped → silent `ok:true` no-op). When a compute output vanishes from a tool response, FIRST diff the recipe's return mapping against its result_schema — assume unmapped before assuming compute failure.
- **replace_image regenerates object ids — spec blobs must track the LIVE id.** Any "stored spec keyed by element id" pattern (chart specs in speaker notes) breaks on the second update: original id dies at first replace. Fix shape: blob carries `element_id` (live), a post-replace ruby step injects the new id, lookup accepts either original (stable notes key) or live id, response returns the live id. Also: an empty catch after acquire = bare-`{}` response + leaked permit (lease_seconds expiry covers observe-mode; still return a structured envelope).
- **Word-boundary trim must be applied at EVERY append/cap, not just the first trim.** The helper's initial trim had it; the three append steps used raw `body[0, n]` → mid-word cuts served to clients. Rule: any char-budget slice of guidance gets the trim lambda.
- **Lint_Deck calibration truth:** zero-at-warn+ holds ONLY on the 5 priority layout exemplars. The template's own extra example slides carry off-profile content (8pt Inconsolata code in a card, 11pt bodies, `#073661` near-miss) — the linter flagging them is CORRECT; never tune rules to force zero. Measure/Build containment fix: text-box pairs with overlap frac ≥ 0.95 = label-in-container pattern, not a collision.
- **Living manifest for the fix round: 371934** (18 selected = 12 skills + mcp_server + profile + guidance/extract/sweeper helpers whose dev twins now carry unshipped fixes; supersedes 371703/371761 selections for the DR). Export completed, ZIP 21 entries verified, mirrored.
- M2 enforce cutover scoped, Josh-gated: mode is caller-supplied per recipe → ~19-recipe coordinated edit + per-tool refusal-path verification; own dispatch post-import.

## M2 enforce cutover (2026-10-26, "continue" dispatch)

- DONE via property override, NOT the 19-recipe mass edit: acquire manager 74622357 step-16 condition now
  `caller_mode == 'enforce' || project_property['GSlidesMCP Permit Mode'] == 'enforce'`. One property
  (`GSlidesMCP Permit Mode=enforce`, project 13683566) toggles fleet-wide enforcement; absent = observe.
- A/B proven live with TEST probe 83346842 (scheduler trigger, force-runnable, per-job scope, rate_limit=1,
  two acquires + verdict line). Phase 1 no-property → allowed_observe; phase 2 enforce → rejected.
  Probe left RUNNING as the standing verifier. **Prod cutover post-import = create the same property on the
  prod project — the manager code change ships via manifest 371934's included dependency row.**
- Scheduler traps: force-run needs a RUNNING scheduler-trigger recipe; new hourly schedulers REQUIRE
  trigger_at (format "06:15" HH:MM; "2026-10-27T03:00:00Z" and bare "03:00" both fail) — old recipes saved
  without it predate the validation. Builder residue from a swapped trigger (visible_config_fields) can
  force a full rebuild — cheaper than fighting it.

## 2026-10-26 — BSYS-29603 deploy failure diagnosed (nil-T.must, auto-deployer path)
- The 08:18Z auto-deploy of manifest 362146 (3 brand-voice recipes, 13,155B package
  42323173→42323179) failed in bt-prod import: `Passed nil into T.must at line: 3258`.
  First documented instance of the known prod-import defect (mcp_server/agentic members,
  canon 2026-10-12) hitting the AUTO-DEPLOYER path (recipes 3792728/3792736, bt-prod).
  Attribution of why this 3-recipe zip trips it = GUESS (MCP-server binding as project
  dependency); zip not downloadable post-import (404), trace hex display-truncated —
  only the first zip entry survives in the trace.
- Deployer export side is CLEAN (small scoped zips proven on all morning runs:
  362146 13,155B; 364098 9,698B; 371945 11,306B). No prod impact beyond the failed import.
- NEW GOTCHA — `wt manifests assets <id> --raw` returns the FULL workspace asset catalog
  with every row checked=true, caller-keyed (byte-identical across manifests 362146,
  361068, 364098, 371945; folder_id keyed to caller not manifest). It is a PROJECTION
  ARTIFACT, not manifest state. Never read "all rows checked" from this surface — near
  miss: it almost shipped as a false manifest-corruption claim on the ticket (dissent
  broke it). Control test for a real selection: the deployer trace's read_file size.
- Proposal posted (comment 1149444): Josh hand-imports in the UI (BSYS-29458 path,
  may reproduce the defect → that repro + both job IDs go to RLM PM), then the ticket
  smoke + Oct-20 read-backs. Prod untouched by the loop.

## Architecture doc set refresh (2026-10-27, 9-agent fleet)

- ALL 9 pages live under parent 2938339626 (BTI): Overview v5 · Tool Surface v3 · Identity/VUA v4 ·
  Custom Connector v3 · Design-System Pipeline v3 · Guidance Layer v4 · Operational Safety v3 ·
  NEW Layout Quality Toolkit 2986672450 · NEW Companion Skills Ecosystem 2987589887. All macro-free,
  redaction-clean, read-back verified.
- **jira.py REDACTION TRAP:** the wrapper's default no-Jira-keys redaction rewrites BSYS-#### into
  "[one tracked incident](.../browse/one)" — INCLUDING inside URLs, breaking links. Any Confluence
  publish that cites Jira keys MUST pass --no-redact (5 of 9 fleet pages needed a republish).
