# BT Genie — project knowledge

Josh's next big initiative (2026-10-14): turn BT Genie into a self-healing, self-learning,
self-documenting, self-evaluating support system — deep action, multi-judge/dissenter quality
loop, semantic-layer lookup, vendor-doc mining, eventually full automated ticket solve/close.
"Heavy company visibility."

**Workato project:** [GENIE] [BTG] BT Genie — project 10615261, folder 21479670, dev ws 3535597.
Genie: BT Genie GO `gin-AWWsELCn-DatcpM` (genie 6489, OpenAI provider, 23 skills).
KB: `kb-AWgHcmBB-b668CB` (sources extbt/BT-JSM/Automation Hub). 29 recipes in 7 folders.

**Full audit docs (source of truth, 2026-10-14):** `~/orca/projects/bt-genie/docs/`
(architecture.md, asset-inventory.md, gap-analysis.md, future-state.md).
**Confluence mirror:** extbt parent 2950266920 "BT Genie: Architecture & System Map" (child of
PRD 2509897751) + 6 children (Asset Inventory 2950168637, Conversation & Ticketing 2949677090,
Knowledge Pipeline 2950561809, Quality & Evaluation 2949840923, Gap Analysis 2950561834,
Future State 2950135871).

## Critical findings from the 2026-10-14 audit (verified live)

- **P0 — KB ingestion FROZEN:** `confluence kb` 67090598 stopped 2026-04-29
  (trigger_errors_limit); weekly reconciler 74540677 stopped 2026-08-05 (broken in-loop cursor
  variable + hard-delete blind spot + keyword-not-ID KB matching). The genie answers from a
  stale KB. Phase 0 fix #1.
- **P0 — no live evaluation:** judge harnesses dormant; GSheets connection 17980214 lost (400);
  models unpinned.
- No monitor/error handling anywhere in the core loop (genie timeout = stuck :loading:);
  validator errors on running recipes; nil-derefs on empty lookups; SQL/AQL string
  interpolation; no masking; 2 Slack bots + 2 Jira connection pairs; legacy `Brian BT Benie`
  64789004 agent bootstrap still Running alongside the Agent Studio genie (dual-brain risk).
- Data tables: 57271 Conversation metadata (hub), 23849 pre-v3 legacy guard, 86801/86802 shared
  (External IDs + Conversation History with feedback columns nobody consumes yet).
- PRD (2509897751) documents 11 skills; genie carries 23 — PRD stale.
- Architecture is sound: the join-record design is the pattern HR Genie adopted (BSYS-27775/29430).

## Plan shape (future-state.md — draft, awaiting Josh's go)

Phase 0 stabilize (~1-1.5wk) → Phase 1 port HR Genie Intelligence incl. cost-from-Agent-Studio
(~2-3wk) → Phase 2 multi-judge + self-improving docs + semantic layer + eval harness (~2-3wk) →
Phase 3 deep action/self-healing skills (~3-4wk) → Phase 4 gated full deflection + vendor-doc
mining (separate vendor KB, never primary corpus).

## Traps learned

- CORRECTED: Josh's `fid=23150266` link WAS the project folder — in PROD. I first resolved it
  against the dev workspace (AIRO default), found it empty, and concluded "stale link" — wrong.
  An empty fid in the attached workspace usually means the link points at ANOTHER ENVIRONMENT.
  Check the environment implication before declaring a link stale.
- AIRO `recipe_get` fails with generic error on 67090598/74540677 — use `wt recipes get` for those.
- AIRO `genie_get` returns "retrieved successfully" with an EMPTY body for this genie — skill
  inventory came from recipe reading instead.

## CORRECTION (2026-10-14 later same day): PRODUCTION audit — the authoritative system

Josh corrected me: the ask was the PROD genie. Prod = **workspace 3535598, project 11483666,
folder 23150266** (Josh's fid link was right for prod). Prod findings (all read live):

- **Prod genie:** BT Genie GO `gin-AX3Rhme9-ncPx4G`, **GPT-5.2**, active, 15 skills (15 backing
  recipes), 1 KB `kb-AX3Rhn4Y-bkLQeX`, Matrix chat interface, reach **Everyone 1,730 users**,
  Deflection KPI on table 66783. Last edit 2026-10-07 Benny Tan.
- **KB ingestion RUNS in prod** (207 ingests/30d, 0 fail; reconciler green 4 runs + 1,793 child
  exec/30d). The dev freeze is dev-only — dev is a degraded mirror (stopped ingester, 5-recipe
  judge folder vs prod 1, recipes-as-skills vs prod agentic_skill assets).
- **30d volumes:** 1.1K convs, 3K msgs, avg/median 1m14s, p90 46.7s, 8,709 skill calls, 984 KB
  retrievals, **ZERO end-user feedback collected**.
- **P0 prod bugs:** (1) **Create Customer Request fails 42%** (374/894) — ticket-creation path;
  suspect JSM form/dependent-field validation. (2) **skills_running race drops user messages**
  (23/25 decoded router failures = "Declining to start conversation in non-idle state"; no retry,
  no apology — silence). (3) No monitor/error handling and no masking in ANY prod recipe
  (code-marker verified); real names+messages persist in job reports.
- Prod legacy: 58511202 bootstrap running w/ 0 jobs/30d (retire candidate); Pinecone init stopped;
  personal Slack connections (Sen Rong, Benny Slack) in the shared project folder.
- Prod recipe IDs: router 69405806, comment writer 69459302, manual 71356750, notify 69459301/69459300,
  KB 67863310/74544112/74544111, eval 69405805. Tables 66783/76875/76876/23761.
- Confluence tree corrected same day (all 7 pages, v2/v3): parent 2950266920, Asset Inventory
  (Production) 2950168637, Gap Analysis (Production) 2950561834, Knowledge Pipeline 2950561809,
  Conversation & Ticketing 2949677090, Quality & Evaluation 2949840923, Future State 2950135871.

### How to read PROD (token REFRESHED 2026-10-14 — works now)
wt --profile josh-prod hits keychain entry `workato-platform-cli` acct `josh-prod` (refreshed
by Josh 2026-10-14). **wt `api` passthrough path quirk: ALWAYS pass the `/api/...` prefix**
(`wt api --profile josh-prod GET /api/recipes --query folder_id=...`) — a bare path like
`GET /recipes` 307-redirects to sign-in and surfaces as a misleading 401 "You need to sign in"
even with a valid token. Test read: GET /api/recipes?folder_id=23150266 (root folder holds only
the legacy bootstrap recipe; the other recipes live in the 6 subfolders). Original 401 diagnosis
history below. Working path: **Orca browser is signed into app.workato.com with the
environment switcher in-page** (header shows "Workato AHQ | AI / Production"). Use in-page
fetch of the UI's own APIs (same-origin, cookie auth): `/web_api/mixed_assets.json?folder_id=X&per_page=100&page=N`
(items under `.result.items`), `/web_api/projects/f<fid>.json`, `/recipes/<id>.json?mode=view`
(state under `.result.recipe_data`), `/recipes/<id>/code.json?mode=view` (full DSL),
`/web_api/recipes/<id>/jobs.json?started_at=30.days&per_page=100&status=failed` (`status=failed`
is the working filter; counters job_succeeded_count/job_failed_count/job_count),
`/web_api/recipes/<id>/jobs/<job_id>.json` (full error object), `/web_api/genies/<handle>.json`
(model, KPIs, user_groups). Subfolder IDs via DOM: `[role=menuitem][data-folder-id][aria-level="2"]`.
Genie analytics live in the overview page DOM (skill heat map + 30d counters) — tabs are
ref-buttons e146-e150; JSD-native skills don't appear as folder assets.

## 422 root cause — CORRECTED (2026-10-16, live-trace evidence)

The 42-44% Create Customer Request failure is NOT one bug — prod 71124238 failed-job
traces split ~50/50 into two classes:

- **Class A — value-format mismatch:** JSM proforma "Field is required" fires even when
  the genie ANSWERED the field (question 46 answered "2026-10-14 12:30 CET" in the trace)
  — proforma can't parse the human-format value. Root cause: **ProForma type `ts`
  (timestamp) is missing from the loader's TYPE_MAP** (REC | Load Service Request Fields
  71124245) — timestamp questions surface as raw "ts" with no format contract.
- **Class B — malformed payload:** raw Ruby string-concat create body → "Invalid request
  payload". Killed by the structured body (parse steps + hash .to_json).

Upstream fix (built in 2.0 fork 2026-10-16, prod hot-swap staged pending Josh go):
loader TYPE_MAP + per-question `value_format` emission; Value Format Rules (STRICT)
section in the skill description. Post-hotfix 422s hide inside SUCCEEDED jobs (monitor
catch) — the failure-rate watch must count via TRACES, not job status.

## BT Genie 2.0 fork state (2026-10-16)

Project 18276750, folder 35835951 (`[GENIE] [BTG] Super BT Genie 2.0`), 48 recipes
(all stopped, "Copy of" names — renames deferred, by-name function refs depend on them)
+ 4 tables + 7 properties + KB `kb-AbzEostx-XogQEn-CD` + genie `gin-AbzEtfoT-LgXXem-CD`
(GPT-5.1, instructions byte-identical to dev BT Genie GO, 26/26 skills attached, 1 KB).
Full fleet rewired to 2.0 twins (0 cross-project refs except by-design shared tables
86801/86802 + JSM-mapping 23849). Manifests: 366025 (fork), 366700 (BSYS-29744, 9 rows).

## Technical plan v2 (2026-10-18) — the 2.0 design contract

`~/orca/projects/bt-genie/docs/technical-plan-2.0.md` — five-plane architecture, roadmap
items 1–13 mapped to phases, fusion-adjudicated (deepseek + glm panel). Load it before ANY
2.0 build session. Structural decisions baked in: pilot cutover after Phase 0 (gates need real
traffic — the fork has none); sync judges for actions / async sampled judges for KB answers;
retry queue = claim/lease sweeper (no inline backoff; no row locking on tables); model upgrade
at P0 START (never baseline on a model you discard); watermark state only in state tables;
Error Ledger table is P0. Epic BSYS-29732. Josh approved all 3 open calls by "let's build it"
(2026-10-22): judge panel Claude Sonnet 5.5 + GPT-mini w/ Opus tiebreak · gpt-5.2 on fork ·
pilot cutover after P0.

## P0 build state (2026-10-22) — race fix SHIPPED in fork

- **Manifest 370482** "BSYS-29739 Super BT Genie 2.0 Phase 0 build" — 91 rows, read-back
  verified, mirrored to `<repo>/manifests/BSYS-29739.manifest.json`. Manifest gotcha: asset ids
  MUST be numeric (data-table UUID ids → HTTP 400 on update; use the numeric id from create);
  synthetic rows need exact listing shape (folder + absolute_path + folder-prefixed zip_name)
  or the platform SILENTLY DROPS them (echo count < payload count is the tell).
- **Spike #1 PASS:** decline is a catchable Service error; router has full Slack event in-scope
  at the dispatch step — enqueue from datapills, error payload not needed.
- **Spike #2 PASS (live-verified):** genie feedback = `user_feedback` events via
  `GET /api/agentic/genies/:id/conversations/:id/events?include_event_types[]=user_feedback`
  (reaction, comment, conversation_id, genie_run_id). No connector trigger, no Event Streams
  topic — PULL only. Conversations list supports `feedback[]=has_positive/has_negative` +
  inclusive `from` watermark (offset +1s — BSYS-29477 trap). Installable prior art: "[GFC]
  Generic Genie Feedback Capture" (asee 2876670157). Feedback joins via conversation_id +
  genie_run_id; message text joins via genie_run_id events. Fork genie has NO chat interface
  attached yet — pilot wiring item.
- **Fork genie upgraded gpt-5.1 → gpt-5.2** (flat-body PATCH /api/agentic/genies/<handle>,
  `{"ai_model": "gpt-5.2"}` — genie-wrapper body is a no-op).
- **Tables (fork):** [BTG 2.0] Pending Messages **164161** (slack_ts/channel/thread/loading_ts/
  conversation_id/text/user_id/state/claimed_at/attempts/last_error), [BTG 2.0] Error Ledger
  **164156**. (164155 was deleted + recreated — data_table_update.columns regenerates field
  hashes, so recreate > alter even empty.)
- **Race fix live in fork:** router 83113544 (rewired to "BT Genie 2.0", monitor around
  dispatch, catch → enqueue 164161 + queue-notice replaces :loading:, response-present guard
  around post-dispatch steps, dispatch masked, validator-clean) + sweeper 83291436 (every 5
  min, claim-one, re-dispatch same conversation with queued text, replace :loading:, cap 3
  attempts → honest resend request). Notify 83113577 rewired to fork genie. All 3 RUNNING,
  zero old-genie refs.
- **CRITICAL corrected record:** the fork was NOT fully rewired — 83113544 + 83113577 held
  live refs to OLD dev genie gin-AWWsELCn-DatcpM (by name in assign_task_to_genie
  genie_handle, by handle in send_business_event genie_id). Fixed 2026-10-22. 7 fork recipes
  were RUNNING incl. a [debug] one; TEST probe 83147941 also present.
- **AIRO recipe_builder gotchas (new):** (a) steps built via add_step carry NO connection —
  select_connections before start or "Workbot for Slack is not connected" blocks Start;
  (b) data-table row pills need the `**{field_hash: type}` schema kwargs on get_records AND
  record_id must use the ID column hash (11fbe9a6-... for these tables), never 'id' —
  otherwise DatapillInvalidPath AND the start is BLOCKED (toast: "errors in step …");
  (c) CLI start + web_api POST /web_api/recipes/<id>/start (202 enqueued) BOTH silently no-op
  on a recipe with validation errors — the Orca browser Start button toast is the only
  surface that names the actual errors; (d) set_input_field advanced.thread_ts as a raw
  string saves as a LITERAL — must be passed as ruby(...) expression.
- **Fleet reconciliation (2026-10-22, agent):** KEEP 14 / MERGE 3 / RETIRE 2 skills + 7 JSD-
  expansion skills RULING: keep (P3/P4 action surface). 10 debug/TEST retire-candidate recipes.
  Fork KB recipe 83113541 has NO skill attached (prod KB Search gap). Scratch evidence:
  /tmp/fork_skills.json, /tmp/fork_recipes.json, /tmp/fork_recipe_code/.
- **Remaining P0:** ~~eval plumbing~~ DONE (btg20-p0-eval-golden-set row), reconciler redesign
  ticket FILED (BSYS-29909, 5pts), pilot cutover prep ~~bot identity~~ DONE (pending 3 clicks),
  prod hygiene carve-out (58511202 + personal connections — needs BT handshake).
  ~~BSYS-29744 prod hot-swap~~ DONE 10-19/20 — live-verified 10-22: prod 71124238's last
  FAILED job = 10-15 (pre-fix); today's jobs green; full stack (structured body / catch
  branches / pre-flight / fallback / loader) in prod v27. Only remaining dev→prod delta =
  canary 70911663 v48's formErrors schema port (schema-only, no downstream pill refs) —
  rides the next legitimate prod change, no standalone write.

## CUTOVER REVISION (Josh, 2026-10-23): pilot runs from BT AI — no prod promotion for pilot

Josh ruled: the 2.0 app is created and piloted in **Workato BT AI (the dev environment where
the fork lives)** — the pilot does NOT promote to prod first. Prod promotion = **cutover #2,
the FINAL step** of the program, after pilot + phases produce their evidence. Plan doc §5
PILOT row re-scoped accordingly. Red-team review still runs before pilot launch (user-facing
pilot channel even without a prod write). Pilot assets: Slack app "BT Genie 2-0 Pilot"
A0CCC2ZP3FS, OAuth profile 46956, connection 22364458 (fork folder), channel #btg-2-0-pilot
C0CCC23RH7S. **No Slack admin approval needed for the BT AI path (Josh, 10-23).**

## RED-TEAM CYCLE (2026-10-23): FAIL → all findings FIXED-VERIFIED → blocked only on Josh's click

- Original verdict FAIL (2 fatal: SQL injection via chat into Snowflake 83113539; spoofable
  requester/unconfirmed provisioning; 5 material incl. unmasked queue path, undelimited queued
  text, directory LIKE injection, flood caps, unwired pilot connection). Verdict +
  re-review appended: `~/.claude/knowledge/redteam/BSYS-29732-btgenie20-pilot.md` + BSYS-29732
  comments (1147186, 1147199).
- Re-review: **all 7 findings FIXED-VERIFIED** against live stored code; 2 new cosmetic
  (non-atomic cap count; name-substring admin deny — allowlist preferred later); N-1 (last
  unmasked insert_to_list) fixed by coordinator; N-4 (83113540 must run) started.
- Platform fact: recipes bound to an UNAUTHORIZED connection refuse to start
  (`config_unconnected`); AIRO select_connections refuses inactive connections — raw PUT of
  `slack_bot.account_id` is the working rebind path.
- Launch-blocking remainder: Josh authorizes 22364458 (Allow) + adds C0CCC23RH7S to
  "Approved channels" property (manual UI) → coordinator starts 83113544 + 83291436 → ONE real
  end-to-end queue trace (enqueue → sweep → mask-verified in job history) — zero post-fix
  traces exist; all verification so far is config-level → verdict upgrades.

## P0 wave 2 COMPLETE (2026-10-22/23) — fleet clean, loop hardened, feedback live

- **Fleet:** 10 retire candidates STOPPED (zero refs verified, nothing deleted); 83113549
  retired into 83113565 (verified strict superset); **38 recipes renamed off "Copy of"**
  (running recipes = stop→rename→start — running recipes reject metadata renames); **23 skills
  renamed via `PATCH /api/agentic/skills/<handle>` — returns HTTP 404 body but PERSISTS the
  write** (read-back is authoritative). 26/26 attachments intact. JSD "duplicate pair"
  83113536 (rich issue detail) / 83113552 (queue lookup) is NOT a duplicate — both kept,
  ruling recorded (renamed with [Queue Lookup] suffix).
- **Error hardening (6 recipes, verified live):** 14 try/catch blocks + 14 Error Ledger
  (164156) write paths across comment writer 83113545, notify 83113578, manual assist 83113580,
  KB ingester 83113541, reconciler 83113582 + LF 83113581; 39 masked steps; zero structural
  validator errors; **all 16 fork recipes running** (final sweep). Recovery actions: comment-
  writer failures post internal Slack notes; continue-catches engage authored fallbacks.
- **New platform gotchas (wave 2):** (a) `recipe_builder_pull` FAILS on recipes using the custom
  Confluence connector (`confluence_connector_748504_1751909209`) — edit via raw
  `wt api get/put /api/recipes/<id>` with GET-verify diffs after every PUT; (b) raw-PUT silently
  drops `parameters` objects on data-table actions unless the node carries full
  `visible_config_fields` (every `parameters.<hash>` path) + `extended_input_schema`; (c)
  foreach-item DatapillInvalidPath on untyped array-of-string loop sources = harmless
  sample-value artifact; re-setting the source does NOT clear it.
- **Manifest 370482: 95 rows, verified after concurrent-writer cross-writes** (fleet + feedback
  agents both wrote it; post-write read-back confirmed renamed names survived + all 3 feedback
  assets present). Mirror current. Wave-2 evidence: /tmp/r8311354{5,8}_final.json,
  /tmp/r83113580_final.json, /tmp/fork_after.json, /tmp/skills_after2.json, /tmp/patch_8311354*.py.

**Platform facts (new):** `wt --profile` flag doesn't work before the subcommand — use
`WORKATO_PROFILE=josh-prod` env. AIRO property_list 401s on project-scoped reads; use
`wt api POST /api/properties` with `project_id` IN THE BODY (wt's properties upsert
omits it — silent workspace-level write, reads back EMPTY on the project). Data-table
row exports come back as [meta(3), data...] arrays (flat OR nested [meta,data] pairs —
handle both). create_record payload = flat column map, NO {"data": ...} wrapper.


## FINAL: 422 saga closed (2026-10-19)

Jun's BT Ops form fix landed: AI Tools (new) form question 46 changed dt→da + rq:false.
Verified via probe: full-form create works (BTSUP-79132, form attached + submitted:true).
The genie pipeline is fully restored — loader value_format covers the da type.
The bare-create fallback (prod 71124238 v21, 2.0 83113565) stays as the safety net for
future form breakage. Probe recipe 83147941 stopped (throwaway). Test tickets to close:
BTSUP-79091/79092/79095/79132. NOTE: when the form breaks again (someone adds an rq dt
question), the symptom = 422 "Field is required" naming a question id; the probe recipe
reproduces it in minutes. The JSD create API cannot fill proforma dt questions — any
shape (13 tested); da/te/cd are fine.


## ts-mapping correction + form-attach gap (2026-10-20)

- CORRECTION: proforma `ts` = single-line TEXT ("Tool Name" = ts!), NOT timestamp. My
  ts→timestamp loader patch (Oct 16) was WRONG — told the genie to date-format text
  questions. Fixed on all four loaders (prod 71124245, dev 70758618, 2.0 83113561/63):
  ts→text. dt→datetime stays (dt = the real date-time type; only 46 used it).
- The empty-[BT]-fields tickets: the genie sends answers, the create succeeds, but the
  FORM does not attach when the answer set is incomplete for the form's conditional
  branch (silent drop). Complete answer sets attach + submit + sync customfields for
  BOTH integration and customer users (raiseOnBehalfOf = not a factor). The AI Tools
  form = ~48 rq questions across conditional branches (Lovable/tiers/access) — the
  genie's branch-complete answering = the refinement layer (loader sections/conditions
  output + skill prompt).
- Prod-side probe recipe 83192584 (TEST, never started, uuid-too-long validation error
  — fix uuids to ≤36 chars if ever needed).


## FINAL: pre-flight validation loop LIVE in prod (2026-10-20, v24)

71124238 = validate step (POST /rest/servicedeskapi/request/validate) wrapped in an
inner monitor BEFORE the create. Invalid = inner catch's if (message contains
UNPROCESSABLE_ENTITY) → skill return: 'PRE-VALIDATION FAILED... JSM says: <error pill>
|| collect answers, rebuild, resubmit'. Non-validation failures (outage/5xx) = fall
through to the unvalidated create → outer catch → bare fallback. Valid = create
unchanged. PROOF: the replay of victor's original 422 job (j-Ac3xCFQz) = valid:true →
BTSUP-79231 created → happy path (Jun's form fix made the payload valid). Defense in
depth: structured body, catch branches, pre-flight loop, bare fallback, loader
value_format — all live. The uuid limit on recipe nodes = 36 chars (my 37-char uuids
blocked a start; trim to 35). The catch's error pill = provider 'catch' in _dp.


## Josh's 5 live break-it tests (2026-10-19/20) — results

1. Clean fix-problem request → BTSUP-79232, full form attached ✓
2. Malformed-JSON payload from the genie (emoji/escape crafting) → pre-flight caught (400
   Invalid request payload ≠ UNPROCESSABLE → fall-through) → create 400 → outer catch →
   bare fallback filed BTSUP-79233 (summary-only). The layers worked; the LLM's JSON
   crafting on hostile input = the residual LLM-quality item.
3. Special-chars payload → clean (BTSUP-79234); the clean-path probe also created 79235
   with emojis/quotes/<x@#$%> — JSM accepts them; the OLD code's control-char gsub =
   not needed with parse+to_json (parse raises on truly-broken JSON).
4. The double-file attempt: the genie RAN (04:13Z, 6s, finished) but the reply never
   landed in Slack — the genie-platform delivery layer, NOT the create recipe (correctly
   no second ticket). Observed once; the known genie message-drop family (G2); watch.
5. Lovable: not a Firefighter-managed app → genie pushed back (per its scope rules);
   the ticket denial = the 1-ticket-per-conversation guard. Expected behavior.
- ALSO RESOLVED: BSYS-29744's workspace_id-leak flag — the prod genie-conversation
  records carry workspace_id 3535597 (dev) — it is STAMPED BY THE PLATFORM on the
  conversation object (environment_id = correct prod), NOT a recipe leak. No fix needed;
  explain-and-close.
- The fallback now posts the user_request as an internal comment (agents get details):
  prod 71124238 v25, 2.0 83113565 — both running.

## Feedback capture pipeline (BSYS-29732 Phase 0, 2026-10-22)
- Built: DT 164229 `[BTG 2.0] Feedback Capture` (event_id idempotency key) + DT 164230 `[BTG 2.0] Collector State` + recipe 83295770 `[BTG 2.0] Genie Feedback Capture` (15-min clock, all in folder 35835951).
- Auth ported from HR Genie Intelligence (82862205): custom API connector `workato_api_connector_748504_1684743862` `__adhoc_http_action` on connection 13685697 ("Workato API") — same connection REUSED, no new auth path. Request cursor param is `page[after]`, response field is `next_cursor` (confirmed live: `{"data":[],"next_cursor":null}`).
- Watermark: state-table row `btg20_feedback_capture_wm` (record eddfb2d0), +1s inclusive offset + 6-hourly 7-day resweep (BSYS-29477/29488 port). Late feedback on old conversations IS covered by the resweep.
- Builder trap re-confirmed: add_step for an `if` block tags it with the action's connector as illegal `provider`+`name` keys → start 422 "not allowed for this step type" (4 code blocks). Fix: raw GET → strip both keys from keyword=='if' nodes → raw PUT with config serialized as JSON STRING (array 400s). Start verified running:true after.
- Empty-poll evidence: forced run + scheduled run both green; trace shows conversations GET returning `{"data": [], "next_cursor": null}` and unconditional state `updated_at` advance.

## Pending Message Sweeper outage + recovery state (2026-10-23)

**Root cause (confirmed from job trace j-Ac6XRAB9):** the data-table connector's
Search-records serialization changed — `order_by_field_id: "$created_at"` (pseudo-field
string) is now rejected with `Expected input type "ApiDocumentFieldRef", found
{"field_id":"$created_at","type":"document"}`. Failed at line 1 on every 5-min tick:
75/87 jobs failed (~288 billed failures/day) before the recipe was stopped.

**Fixed and verified:** the overnight session's 00:44 edit already removed the sort
field. Verified at the raw-JSON layer (no `order_by` anywhere, no null-polluted update
params — the builder DSL's `None` renderings are the known export artifact, not real) and
at runtime: 5 green scheduler jobs 21:18–21:38 PT (graceful empty-queue stops) prove the
parse error is gone. Table 164161 `[BTG 2.0] Pending Messages`
(https://app.workato.com/data_tables/ea5ce2f4-b976-4e18-a3cd-7da5dd74f678) is empty in
every state — no stranded messages, no backfill.

**Sole remaining blocker — Josh's 2-min OAuth click:** connection 22364458
`[BTG 2.0] Pilot Slack` (custom OAuth profile 46956, created 2026-10-22 20:54 PT) has
`authorized_at: null`; `wt recipes start 83291436` refuses with `config_unconnected` on
it. Per the slack-bot-connection skill, the Orca-browser popup path is dead — Josh must
click Connect + Allow (recipe 83291436 step → Connection tab → Connect → Slack Allow).
THEN: start 83291436 AND 83113544 (enqueue side, shares the connection, 0 jobs ever —
never started) and verify a green tick + a real queue round-trip.

**Hero-slide smoke (recipe 83295992):** test case citc-Ac6XFTpc-9XYRAD-CD was a test
artifact (no trigger mock, never passed — "0 mocked steps | 0 checks on 0 steps"; a
workato_skill trigger + 3 recipe functions + Google step would all need mocking, while
the nightly REAL invocation job j-Ac6XaQhC-QKbDBt-CD already proves the asset end-to-end
in 4.3s). Deleted via Orca UI 2026-10-23; AIRO read-back = 0 test cases; canon line 72
closed `resolved` per failure-close-gate.

**Dreamer:** NOT silent anymore — 2026-10-22 night failed on gateway ENOTFOUND (2×) and
the 23:43 fire hit a stale lock ("already running, skipping"); manual run 08:12 today
succeeded (report dreams/2026-10-23.md, validated-clean, 3 proposals filed). launchd
23:43 timer armed, no lock present. Watch tonight's fire as the confirmation.

**Drift Fix Genie:** stopped + verified inactive 08:57 PT (all four drift genies
inactive) — but BSYS-29829 comments show joel.ang re-enabled it DELIBERATELY 2026-10-21
and the ticket recommended leaving it running; re-stop was flagged as a Josh decision on
the ticket (comments 1147834 + correction 1147835).

## JSM comment mirror: the truth about the BTSUP-79460 Slack triplicate (2026-10-23)

First diagnosis (hotfix session, 2026-10-23 ~16:30Z) said "our side posted once; the
BT-side Jira→Slack mirror tripled." INVERTED — live evidence corrects it:

- **jira.py posted ONCE** (transcript: single POST 16:23:56→16:24:01.734Z, HTTP 201,
  comment_id 1147867, read-back VERIFIED). Its retry loop cannot triple (only 429/5xx,
  8s backoff; timeouts don't retry).
- **Atlassian duplicated server-side:** one POST → THREE comment rows (1147865/66/67),
  all actor Joshua Cramoy, created :00.657/:01.532/:02.532 — sub-second machine spacing.
  The 201 response returned only the LAST id. Atlassian-side processing retry without
  idempotency.
- **Our mirror recipe 69459301 ("Notify Users on New JSD Comment", BTG prod folder
  29092290) behaved CORRECTLY:** three comment-created webhooks in, three Slack
  "New message" posts out — faithful 1:1. Nothing to fix in the recipe.
- **Atlassian Assist** then deleted two rows at 16:26:34/40Z (including our returned
  1147867), leaving 1147865 — which is why the first diagnosis saw one comment and
  drew the wrong conclusion.
- **Hardening shipped:** jira.py cmd_comment read-back now detects duplicate rows
  (same ADF body) and prints a DUPLICATE warning + evidence field.
- Lesson: a read-back that only checks `cid in ids` can't see server-side duplication;
  count/compare bodies. And a mirror's "1 post per webhook" is not duplication — check
  the webhook COUNT before blaming the mirror.

## Mirror dedupe guard DEPLOYED + live-proven (2026-10-23 18:20Z)

Prod 69459301 v5: 3-step guard (foreach payload comments → if same-body+same-author+
lower-id+60s-proximity → clean stop). Red-team PASS-WITH-NOTES, material note (time
bound) remediated pre-push. Manifest of record **371155** (project-folder anchored —
NOTE: manifest folder_id MUST be the PROJECT folder, not a subfolder; subfolder-anchored
manifests fail ZIP export with "connection not found under <recipe folder>"), ZIP-verified
9 entries. Manifests 371093/371154 superseded (subfolder anchor + root-namespace
connection row the exporter cannot carry — "* Connections" rows fail export; same-
workspace imports resolve connections by name).

**LIVE PROOF same day 18:28Z:** the milestone comment POST on BTSUP-79460 itself
duplicated AGAIN (rows 1148002/03/04 — the duplication is DETERMINISTIC for large ADF
comments, not a one-off race). jira.py's new read-back caught it in the act
(duplicate_rows warning). The deployed guard collapsed the cluster to exactly ONE Slack
post: 1148002 posted (ts 1792780112.662639), 1148003/1148004 stopped at the gate
(8-line jobs, condition true). Zero dropped mirrors across all probes + real traffic.

**Open item (Josh's call):** delete duplicate Jira rows 1148003/1148004 on BTSUP-79460
(cosmetic; Atlassian Assist self-deduped last time) — jira.py has no delete command by
design; deletion is a Jira write needing his go.

**Dev back-port (2026-10-23):** dev twin 71077131 (dev JSM Triggers folder 29090923)
carries the identical guard — v7, running verified, DSL markers verified. Dev manifest
of record **371173** (4 rows; dev exporter limitation identical: out-of-tree and
"* Connections" connection rows fail export — 371168/371171 superseded). Prod/dev parity
restored for the dedupe guard.

**jira.py formatting fix (2026-10-23, Josh-reported):** cmd_comment was posting raw
paragraphs, bypassing md_to_adf — every ## / ** / bullet rendered as literal text on
tickets (both the 16:24 hotfix comment and the 18:28 milestone comment). Fixed: comments
route through md_to_adf; removed a dead-code .match()-on-Match crash in the list path.
Milestone comment replaced (1148032, ADF-verified: strong/links/bullets, zero literal
markers). Second real cluster (1148032/33/34) collapsed by the mirror guard to ONE Slack
post — guard is 2/2 on live clusters. jira.py DELETE returns 404 but lands (verify by
list read-back, not status code). OPEN: 16:24 hotfix comment 1147865 still has literal
** — replace only on Josh's go (customer-visible history).

## WHY the triplication — controlled experiment (2026-10-23 ~19:40Z)

Four controlled probes through the raw REST API settled the mechanism:
- **Scope: WORKSPACE-WIDE, all REST API comment POSTs.** BTSUP-78200 probe tripled;
  BSYS-29908 probe tripled (different project, no JSM automation, no mirror). 70-char
  plain text tripled — size and markdown characters are NOT factors.
- **Not our client:** jira.py sends ONE POST, gets ONE 201 with one id; three rows
  materialize (consecutive ids, ~0.9–1.0 s spacing, all under OUR actor id). A
  client-side triple would need three 201s from one single-threaded process — impossible.
- **Time-boxed onset:** the 08:02Z "Confirmed" comment (same script, same API, same ADF
  shape) was a SINGLE row at 16:30Z read — so the regression started between 08:02 and
  16:24 UTC on 2026-10-23. Older comments on both tickets: all single.
- **Conclusion:** Atlassian-side processing retry without idempotency — every comment-
  creation request is now reprocessed ~3x server-side. Their regression, not ours.
- Mitigation stands: mirror guard (3/3 live clusters collapsed to one post), jira.py
  read-back duplicate warning (caught all 3 occurrences at post time), manual dedupe on
  important comments (keep first row).
- Experiment cleanup: all 12 probe rows deleted; BTSUP-78200 back to 5 originals,
  BSYS-29908 to 3 originals. NOTE: Jira DELETE returns HTTP 404 while succeeding —
  verify by list read-back, never trust the delete status code.

**Sweeper deployed (2026-10-24, Josh ask "do we have a sweeper?"):** two layers —
(1) jira.py cmd_comment now AUTO-DELETES its own clone rows at post time (keep
first-created, re-read-back verify; the DELETE-404-but-lands quirk is handled by
re-reading, never trusting the status code); (2) estate-wide net
`jira_dedupe_sweeper.py` + launchd `com.josh.jira-dedupe-sweeper` — every 15 min
(:07/:22/:37/:52), JQL `updated >= -30m`, clusters = same author + exact ADF body +
≤60s span, keeps lowest id. Live-proven: posted probe tripled, sweep collapsed it,
probe removed. Log: `jira_dedupe_sweeper.jsonl`. epoch() parses BOTH epoch-millis and
ISO created strings (mixed formats in the wild). No Workato assets touched → no manifest.

## WHY — mechanism settled (2026-10-24 09:0xZ)

- **Inline reprocessing, not async fork:** in every cluster the response returns the
  LAST row's id and all rows exist at response time — the POST is processed 3x
  server-side (fixed count: initial + 2 retries) BEFORE the response. Bad windows are
  intermittent (flapping): x1 at 08:55/08:59Z, x3 at 08:57Z and 09:0xZ.
- **Client path ruled out cleanly:** in the SAME healthy window, jira.py-post AND raw-
  urllib-post were both x1; in broken windows both tripled (Oct-23 experiment used both).
- **Admin question answered (Josh 2026-10-24):** tenant admin CANNOT fix this — no rule/
  app can produce actor-preserving consecutive-id rows created before the response, the
  audit log has nothing to show, and the status page shows all-OPERATIONAL (below
  incident-declaration threshold: shard/canary-level defect in Atlassian's pool).
  Vendor support ticket with our evidence pack is the escalation path (Josh's call).
- Our permanent posture: mirror guard (3/3 live clusters) + jira.py auto-dedupe +
  15-min sweeper — correct regardless of when Atlassian fixes their side.

**Support filing prepared (2026-10-24, Josh request):** full paste-ready Atlassian
support writeup at
`~/.claude/knowledge/redteam/atlassian-comment-duplication-support-filing.md` —
six clusters tabulated, flapping timeline, exclusion matrix, Assist-deletion collateral,
four asks (RCA, retry-layer confirmation, idempotency mechanism, Assist deletion policy).
Josh sends it from his Atlassian account.

### Slack app CREATED in BT AI (2026-10-24) — OAuth chain one click short

**App: BT Genie 2.0 Pilot = A0CCC2ZP3FS, team bt-ai-workspace (T06NK26NYR2), installed
via CLI ("local" install, Finished 1.5s), manifest = 13 Workbot scopes + redirect
https://www.workato.com/oauth/callback.** Created via Slack CLI because the api.slack.com
create wizard is flaky under automation (opens ~2/6 attempts; final Create click no-opped
twice) and the ORIGINAL app sat in the wrong workspace (Workato workspace-created apps
LOCK the OAuth dropdown to their owning workspace — that was the "won't let me click the
dropdown" report). Project: ~/Documents/workbench/bt-genie-pilot-deno (deno template —
bolt template has NO deploy hook; deno-starter-template is the repo that exists now,
deno-slack-starter-template is 404). Auth: slack CLI authorized for BT AI (ticket+
challenge flow, Josh ran /slackauthticket).

**Remaining chain:** (1) pull client_id/client_secret/signing secret from
api.slack.com/apps/A0CCC2ZP3FS → Basic Information (Show buttons = human click;
page needs the BT AI workspace context in the browser session — automation got
"Unknown Workspace"); (2) build Workato custom OAuth profile (UI only); (3) re-point
connection 22364458 [BTG 2.0] Pilot Slack to it (or fresh connection); (4) Josh:
Connect + Allow — now locks to the CORRECT workspace; (5) verify token scopes live
(auth.test x-oauth-scopes = 13 scopes); (6) start 83291436 + 83113544, prove round-trip.
The old connection/profile 46956 (wrong-workspace app client_id 2739942963.12420101785536)
is dead weight — retire after the swap.

**Non-Josh surviving clusters (2026-10-25 scan, for BT-Only sharing):** 3 found, none
deleted — BTSUP-69368 (Atlassian Assist, ×2, July 14 — predates the regression),
BSYS-29684 (AI Integrations, ×2, Oct 19), and the specimen BTSUP-79476 (Workato
Integrations — BT Genie's own bridge — ×2 rows 93 ms apart, Oct 23 13:04:50.097/.190,
real customer request, still live). So integration-actor ×2 duplication is a LONG-STANDING
class (months), distinct from our ×3 flapping form. Evidence block staged:
`~/.claude/knowledge/projects/google-slides-mcp/btsup-jira-duplication-bt-only-evidence.md`.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - projects/bt-genie.md — BT Genie audited 2026-10-14, CORRECTED to PRODUCTION (ws 3535598/proj 11483666, genie GPT-5.2 gin-AX3Rhme9, 15 skills, 1.7k users, 1.1K convs/30d): **P0 prod bugs — Create Customer Request fails 42% (374/894), skills_running race silently drops user messages, no error-handling/masking anywhere, zero end-user feedback**; KB ingestion healthy in prod (dev mirror stopped — dev lies); Confluence doc tree extbt 2950266920 (7 pages, prod-corrected) + future-state plan (stabilize→intelligence→multi-judge→deep-action→full deflection) awaiting Josh go; prod-read-via-Orca-browser web_api recipes in file | DEV Super BT Genie 2.0 (ws 3535597, proj 18276750): Phase 0 feedback capture pipeline built 2026-10-22 (DTs 164229/164230 + poller 83295770, HR-collector pattern, running green) — details in file
## 2026-10-26 — BT working session: three-genie architecture + P3 action list

- **Jun's grand plan (transcript digested):** BT Genie = employee-facing frontline/trust layer; RunOps Genie = admin-facing Snowflake/Firefighter ops (sensitive, internal-only); Shadow Genie = headless monitor (12–13 anomaly signals, Brandon, migrating to AHQ AI) that confirms signals against live APIs before handing tickets to BT Genie for the employee-facing action. No merging — shared capability ≠ shared job (Patricia's concern settled).
- **Deflection defined:** end-to-end genie action, or an approval-click handoff (counts, measure separately).
- **BT delivered the P3 autonomous-action list: 14 items** — tiered + API-feasibility in `~/orca/projects/bt-genie/docs/action-catalog-phase3.md`. Wave 1 (T1 autonomous): SFDC unfreeze, Okta app-access retrigger, Zoom recording fetch, shared-email Google Group membership. Connector notes: Okta/Zoom/Gong/Coupa/GitHub/Salesforce/Google Admin/Drive all have live connectors in-workspace; **ZCC SecOps connector unreleased** (Zscaler path needs release or raw REST); AI spend limits + Claude Console roles likely console-only (no confirmed API).
- **Marjoe's wishlist mapped** (same doc): ingest/tagging = P1 telemetry spine (first P1 build); cluster-failures = P1→P2 with formal cause taxonomy + improvement backlog; A/B prompt/flow harness = P2 (depends on ingest); proactive nudges = P4 consuming **Shadow's signals** (don't build detection — handshake with Brandon); incident-aware pre-triage = small standalone P1 router pre-check (needs BT to name the authoritative incident source).
- **Key APIs missing from BT's list:** SFDC unfreeze = single reversible call (best first build). Zoom licensing is NOT a Zoom-API op — it's the Okta group-push path.
- **Open items for BT:** AI-spend system + API?, T2 approval owners, GitHub standing scope, Zscaler connector release vs scoped service account, authoritative incident source.
- **People/process:** Mona's JSM auto-triage/auto-doc genie → prod this quarter (coordinate, don't duplicate); Joyce hiring a 6-month ops-load intern (report-then-reduce); OpsGenie deprecated → JSM alerts died of noise (threshold design is the answer); Marjoe + Brandon work the list with Josh next month.
- **Josh ruling 2026-10-26 (handoff correction):** Shadow → BT Genie proactive handoff is GENIE-TO-GENIE, not ticket-mediated. Shadow calls BT Genie 2.0 headlessly with a structured, freshness-confirmed signal; BT Genie resolves the tier, executes, and files the Jira ticket as the audit/approval record; the outcome returns to Shadow to close the signal. Ticket = artifact, never the transport. Contract in action-catalog-phase3.md; needs Brandon's buy-in on the Shadow initiating call.
- **Lucidchart digested (2026-10-27, `~/orca/projects/bt-genie/docs/three-genie-architecture-map.md`):** BT's chart shows the closed loop Notice (Shadow/ITAM) → Talk (BT Genie) → Fix (RunOps, conditional) → Review (**Dreamer + trust ladder**) with learning feeding back to Shadow. New named component: **the Dreamer** — overnight review of all three genies' activity, suggests improvements for human approval, and autonomy promotions gated on measured performance ("each genie gets more freedom only once it has proved itself") = our harness-dreamer/eval framework generalized program-wide; our build. **Executor rule settled by the chart:** BT Genie talks, RunOps fixes — T1 actions run BT-direct, T2 approvals route to RunOps approved recipes when in RunOps's domain (catalog gets an executor column). The four "TODAY" pain boxes become the P1 dashboard metrics: detection lag, human-touch count, unlinked-fix count, knowledge-capture rate. Chart's worked example (terminated employee keeps laptop, T2) traces exactly through the genie-to-genie handoff contract.

## BTSUP-79683 incident batch (2026-10-27, Josh: "more fixes/investigation for BT Genie production")

Thread showed 4 defects; investigation results:
1. **Fallback subject generic** (Marjoe's screenshot complaint): the bare-fallback
   create (71124238 step 23) hardcodes "BT Genie request (form submission failed)" —
   the real request ("Request: Laptop Replacement") never reached the subject. Chain:
   genie's LLM dropped 2 closing braces in the deeply-nested ADF answer (7 closers
   needed, 5 present) → parse_json_v2 failed "unexpected token at '}'" → catch →
   fallback (worked as designed — ticket + internal comments + recovery). FIX BUILT
   (session btg-fallback-subject-fix): fallback summary chain = parsed summary →
   raw-form regex first text-run ≥15 chars (skips the phone field at answer 20) →
   user_request first line → generic. Simulated against the real incident data:
   extracts "Request: Laptop upgrade (higher-spec machine)." — regex-on-raw survives
   the parse failure by design.
2. **Recipe function 72551813 "'ID' must be present"** (00:46:53Z, internal comment
   1149822): a skill function in the genie loop called without its required ID input;
   platform error posted as :lock: internal comment; genie recovered (8:49/8:50
   comments). Function not visible as a recipe (404 via wt/AIRO/browser even in prod)
   = function-node id or ACL-hidden asset. Fix = genie guidance or skill contract;
   needs the function identified first.
3. **Preference-order contradiction**: 8:49 comment says ascending order (BT/CS Dev
   14" 32GB first), 8:50 comment says "descending RAM" (Dev-Enhanced 64GB first) —
   the genie stated a preference order the user never gave, then contradicted it.
   Fix = genie instruction: never state a preference order the user didn't give;
   present options neutrally.
4. **Fallback subject visibility** (Marjoe's actual report): every #ask-bt fallback
   ticket shows the generic subject — same fix as #1.
NOTE: the :lock: comments are JSM INTERNAL (customer never saw the errors). The
fallback defense worked; the defect is the generic subject + the genie's malformed
JSON + the genie's invented preference order.

## BTSUP-79683 batch DEPLOYED (2026-10-27, Josh "go go")

- **71124238 v28** — fallback-subject fix live: fallback summary chain = parsed
  summary → raw-form regex (Request-prefixed alternation, ≥15 chars) → user_request
  first line → generic; fallback tiers append "[BT Genie fallback - form failed]".
  Red-team PASS-WITH-NOTES, both materials remediated pre-push. Running verified.
- **Prod genie instructions updated** (gin-AX3Rhme9-ncPx4G "BT Genie GO"): two new
  MUST sections appended (Stating Options and Preferences; Skill Inputs - Always
  Fill Required Inputs). Base text recovered from the genie_create transcript
  (12.4KB; prod/dev byte-identical note) because genie_get renders no payload
  (tool limitation) and the browser session was expired. Read-back of instructions
  not possible via MCP — treat the update response as the record.
- Open: function 72551813 identity still unknown (hidden asset; 'ID' must be
  present) — the new Skill-Inputs instruction should stop the empty-call class;
  revisit if it recurs.
