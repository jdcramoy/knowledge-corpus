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
