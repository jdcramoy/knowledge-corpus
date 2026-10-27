# Estate Monitor — project knowledge

Canonical repo (split from event-process-mcp 2026-10-12):
`~/orca/projects/estate-monitor/` — CLAUDE.md is the project brain;
docs/estate-monitor/HANDOFF.md is the resume point; BUILD_LEDGER.md is the
asset/evidence log with every build gotcha.

Jira: epic **BSYS-29554** (13pts) — platform 29555, notification contract
29556, reaction-to-ticket 29557, confluence docs 29558 (all In UAT); prod
promotion 29559 (Backlog, Josh-gated); phase 2: 29565 Triage Genie +
29566 local harness hook (design agreed, build-ready).

Identity: dev project 18242571 (folders 35778609-612); connections
22286384 (alerts bot, profile 46357) + 22286593 (events, profile 46359);
Slack app A0C806UGHQF; channel C0C805U47FZ. Manifest 361281 (18 assets),
mirrored to repo manifests/BSYS-29554.manifest.json.

**2026-10-11/12 ESTATE MONITOR built (BSYS-29511) — the go-forward monitor.**
Josh pivoted from per-app monitors to a net-new shared platform: dev
project 18242571 "Estate Monitor", 6 tables (158779–84: Scope/Asset
Registry/Signal Ledger/Incident State/Thresholds/Ops Audit), 12 recipes ALL
RUNNING (IDs in orca repo docs/estate-monitor/BUILD_LEDGER.md), explicit
scope-row enrollment (seeded: Event360 dev, Multi-Genie dev, [DEMO] HR
Genie, GW Semantic dev, default), thresholds config-driven, recovery
pings green + env-coded, daily 03:00 digest, full audit trail. UAT'd
end-to-end (stop→incident→Slack→restart→resolve→green ping). Manifest
**361281** ready for prod promotion (Josh-gated). New monitors: add a
scope row, done. Existing Event360/HR Genie families stay until parity
window ends. Gotchas: foreach steps serialized with name="foreach" block
recipe start (null the name via code PUT after each push);
account_property('Environment') call-form unsafe in data-table params
(use f-string there, binding in Slack formulas); AIRO identity can't
access new projects — build in legacy folder then move via folder-only
PUT; connection triggers carry no recipe linkage (default scope row
catches them); shared_account_disconnected apps-multiselect needs new
apps added manually.

**2026-10-12 Estate Monitor updates (Josh asks #2/#3):** all EM Slack
messages render `<url|Recipe Name>` links; thresholds are PROJECT
properties on 18242571 (EM Error Burst Window Minutes/EM Error Burst Count/
EM Staleness Minutes/EM Handled Exception Window Minutes/EM Handled
Exception Count; fallback chain property→table row→default; NOTE wt
properties upsert ignores --project → env-level strays; project-scoped
needs POST /api/properties with STRING project_id); zArchive exclusion in
EM | Resolve Scope (downcased contains — standing rule, all captures
inherit); scope = Josh's five dev project roots (13683566 BT Managed MCP,
14570285 MCP | MOPs widened prefix, 15643451 HR Self Service Genie,
17981834 GW Semantic MCP, 17923915 Multi-Genie). NEW: missed-start-event
safety net in EM | Evaluate Service Health — open stop incidents get live
get_recipe proof each 5-min sweep, resolve + green ping on active=true
(proven 02:17:59 UTC). Gotchas: RecipeOps get_recipe exposes `active`
boolean (no running field; stopped_for_error nil); boolean pills defeat
is_true AND f-string =="true" compares — ruby `x == true ? 'a' : 'b'`;
AIRO push "running" refusal lags stop by ~1 min; foreach>if>ELSE>monitor
misaligns loop-item pills to previous iteration (use sibling-ifs).

**2026-10-12 Estate Monitor Confluence docs (external BT, BTI space).**
Parent "Estate Monitor Architecture" 2945056782 (child of BTI space home)
+ 5 children: How to Add a Project 2943877330 (linked prominently from
parent's first section), Capture Layer 2944925770, Incidents/Alerting/
Recovery 2944368687, Thresholds & Configuration 2944532515, Reporting &
Auditability 2944761939. Written name-only (NO Workato asset/recipe/folder
IDs or URLs) so the set survives dev→prod promotion. Atlassian MCP
markdown gotcha: table cells split on `|` — "EM | X" table names break
cells; safe in body text and backticked code. Read-back verification
(guardrail) caught the broken table on the parent's v2.

**2026-10-12 EM notification format round (Josh feedback):** every alert
carries `*Scope:* <project url|path-prefix last segment>` (fallback scope =
"Estate-wide (fallback)"); env renders ONCE (env-coded header only, no
*Environment:* line); recoveries lead 🟢 (incidents keep 🔴/🔵); burst
Issue text drops the raw scope key. ROOT CAUSE of ops-channel noise: EM |
Route Incident was left in the legacy Event360 Operational Monitoring
folder → monitor watched its own maintenance stops. Fixed: router moved to
EM project (folder-only PUT) AND Resolve Scope excludes downcased paths
containing `estate monitor` or `operational monitoring` — STANDING RULE:
monitors never monitor monitors. Proven: post-fix maintenance = zero
self-incidents. Raw-PUT gotchas: serialize THE MUTATED tree (twice the PUT
silently shipped the reloaded original — success:true no-op); guard strings
must match actual serialized text (`'workspace_fallback' ?`); removing a
mid-string segment "from NL to NL" eats both joins (re-add one). Registry
Folder path goes stale after folder moves (upsert is minimal-field);
RecipeOps get_recipe folder.path is the runtime truth.

**2026-10-12 EM dedicated Slack bot LIVE.** "Connection failed: Error
while processing the user info" root cause = the INSTALLED token predated
the manifest's scope additions (missing users:read breaks Workbot's
post-OAuth identity lookup). Fix chain: manifest → re-request approval →
REINSTALL (approval alone doesn't refresh the token). Verify a token's
real scopes: read xoxb from the OAuth page DOM (Copy blocks synthetic
clicks), auth.test → x-oauth-scopes header. Connection 22286384 (profile
46357) connected by Josh; all 4 posting recipes rebound to it; registrar/
SH/daily moved out of legacy folder — all 11 EM recipes in project
18242571. Proof: stop/start of 82256903 → incident + 🟢 recovery both from
Estate Monitor Alerts (B0C8HHDA389). EM no longer posts as Event360's bot.

**2026-10-12 EM reaction-to-ticket LIVE.** 🎫 reaction on an incident
alert → BSYS Bug (Bug type 10013, 3pts via customfield_10057, labels
estate-monitor+env, reporter integrations.ai) → thread reply → ticket
lands in Josh's queue for the standing jira-autotriage loop. Architecture:
EM | Capture Ticket Reaction 82971161 (Slack new_event trigger, event
name estate_monitor_incident) + router writes incident Correlation ID =
`slack_alert|<channel>|<message ts>` (key-only lookup — no schema change);
idempotency via audit key `<incident key>|ticketed` gating the create.
Infra: profile 46359 (slack PROVIDER — profiles are provider-specific),
connection 22286593, reactions:read scope + reinstall.
**HARD-WON LESSONS:** (1) bot-event delivery requires channel MEMBERSHIP
— chat:write.public posts without it, events don't flow; invite the bot.
(2) api.slack.com's own event-subscriptions save is BROKEN (omits
app_event_types → invalid_arguments silently swallowed); save via
in-page fetch replay of developer.apps.events.subscriptions.updateSubs
with both bot_event_types AND app_event_types. (3) Workato JS snippets:
destructure with EXACT schema field names (snake_case) — camelCase binds
undefined silently. (4) set_condition rhs is BARE (quotes compile into
the comparison). (5) ruby() bindings on trigger pills resolve empty —
use f-string pills. (6) Workbot post_bot_message DOES thread
(advanced.thread_ts). UAT proof: jobs j-AbwCNLf6 (ticket filed for a
REAL incident, BSYS-29550) + j-AbwCQEhE (idempotent).

**2026-10-12 assignee detection + Jira structure.** Reaction tickets
auto-assign to the failing recipe's LAST EDITOR: handler v3 = get_recipe
→ last_version.user_email → jira.find_user → accountId → assignee_id.
UAT: BSYS-29553 assigned to Josh (job j-AbwDB48P). Jira: epic **BSYS-29554**
(13pts) with retro stories BSYS-29555/56/57/58 (In UAT) + 29559 (prod
promotion, Backlog). NOTE BSYS-29511 is the OLD Event360 monitor story
(BSYS-28196) — not the Estate Monitor. Phase 2 design agreed (parallel,
read-only, 🤖 on demand): **BSYS-29565** Recipe Triage Genie (Agent
Studio genie, AIRO MCP read-only tools, invoked by handler on 🤖,
autopsy comment via integrations.ai Jira conn) + **BSYS-29566** local
harness hook (launchd watcher, wt dt query watermark, headless claude -p
jira-autotriage dispatch). Manifest 361281 → 18 assets, mirrored to
repo manifests/BSYS-29554.manifest.json. Gotcha: fresh-session
select_connections silently drops providers (workato_app) → start fails
account_id-blank; re-select ALL providers.

**KB architecture for the Triage Genie (BSYS-29565, agreed direction):**
three tiers — (1) DISTILLED knowledge tree synced into Workato Knowledge
Bases, one KB per domain mirroring the local INDEX.md; source of truth =
git tree/GitHub backup; programmatic sync on a hook (post-build auto-save
fires it). (2) Confluence connector TOOL for human runbooks — never a KB
pipeline. (3) raw 24k-doc corpus NOT mirrored — live fetch. Rationale: the
distilled tree is the 1% with 90% of the value; the full RAG++ corpus
can't/shouldn't mirror. Verify Workato KB ingestion caps at build time.

**2026-10-13 PHASE 2 BUILT (swarm: lead + Builder A + Builder B; BSYS-29565/29566, both In UAT).** Genie **EM | Recipe Triage** (gin-AbwEPzbk, READ-ONLY — 4 recipe-backed skills: Incident Context 82993646, Job History 82993654, Recipe Details 82993655, Confluence Lookup 82993656; the external AIRO MCP cannot attach to an in-platform genie — recipe-backed skills are the Workato-native equivalent). KB tier-1 live: 4 KBs (manifest ids 43777–43780) fed by **EM | KB Sync** recipe 82993520 + `~/.claude/knowledge/scripts/em_kb_sync.py` (192 docs, idempotent upsert-by-doc-ID, Enterprise-context ingestion path; caps: 16 MB/doc, 8k-char chunks). Handler v2 (82971161 v16): 🤖 branch → correlation → `|triaged` gate → genie invocation → Jira comment → thread reply → audit; fail-open. Local hook (Builder B): launchd `com.josh.estate-monitor.triage-watcher` 60s, polls Ops Audit Log via `wt dt query` (NEEDS THE UUID, numeric id 400s), headless claude -p per ticketed row, lockfiles+watermark in ~/.local/state/estate-monitor/. Shared triage-comment contract on tickets from both paths (see ledger). Manifest 361281 → 32 rows. OPEN: webhooks.workato.com notify endpoint dropping deliveries (~17:20 PT) — final UAT needs Josh's REAL 🤖 reaction; arch maps at knowledge projects/estate-monitor/architecture/ + repo docs/architecture/.


Related: [[event-process-mcp]] (the monitored Event360 app), [[workato-platform]] (wt CLI + platform traps).

**2026-10-13 triage note (hook path):** BSYS-29593 autopsy of the HR Genie
collector storm (82862205) found the fix already deployed (wait budget 5→60s
+ classifier page-commit defer branch, per BSYS-29519 plan) — storm self-ended
when that revision landed. Two open items: (1) EM recovery detection missed a
resolved transition for recipe_failed|82862205 despite recovery 2026-10-12 —
recipe_failed incidents that recover while open may never post 🟢 (Ops Audit
Log gap); (2) hook vs Genie dual-path triage race — duplicate check is not
atomic across paths (BSYS-29593 got two corroborating bug/high comments,
1136552 + 1136556). HR Genie collector starvation risk under sustained
backlog: 60s wait budget vs ~2h observed queue latency → every cycle defers.

**2026-10-13 PHASE 2.5 BUILT + LIVE-PROVEN (BSYS-29607).** `EM | Capture Triage Request`
(82997363, folder 35778610): Jira label `send-to-triage` on any BSYS/BTSUP ticket →
FULL genie pipeline (triage genie verdict comment → Triage Dissenter review comment,
CONCUR/CONTEST) → label swap to `triaged-by-genie` → audit rows `triage-requested|`/
`triaged|<key>|<issue-updated-ts>`. Trigger = Jira real-time trigger on connection
18702724 [COR] PRODUCTION with JQL `project in (BSYS, BTSUP) AND labels = "send-to-triage"`
— **labels JQL DOES register** despite the docs allowlist hint. **Trigger runtime/declared
schema mismatch:** runtime changelog = {id, items} but declared = {histories} — foreach
over declared paths loops zero (green job, no work) and runtime-true paths fail start
validation; workaround = gate on get_issue labels state + dedupe on `fields.updated`.
Re-triage = remove + re-add the label; loop guard = the JQL stops matching post-swap.
Reporting funnel: `labels = send-to-triage AND labels = triaged-by-genie`. Dissenter
genie pre-existed (gin-AbwKFbFE, 39393). UAT: BSYS-29612 double-event → 2 full runs,
dissenter CONCUR then CONTEST (caught real verdict defects). Manifest 361281 → 38 rows.
NOT live-proven: fail-open catch path. Open: genie preamble leakage (reasoning text
before the `## 🤖 Automated triage` header) — genies' instruction hardening didn't fully
take; post-prod polish candidate.

**2026-10-13 PHASE 2.5 POLISH (BSYS-29607, recipe v10).** ONE consolidated comment per run: triage genie → dissenter (first line CONCUR/CONTEST) → if CONTEST one bounded revise pass → js_eval consolidate (extract verdict from the 'Automated triage (Estate Monitor)' header line onward + one **Adversarial check:** line before **Evidence:**) → single create_comment. Genies do NOT reliably emit `##` — match the substring in any line. MCP reader warning: getJiraIssue markdown re-renders bodies with `\***` escapes + list artifacts — verify comment quality from the JOB TRACE's final_body, not the MCP read. Post-push first-start does not deliver webhook events (Jira real-time registration lags publish) — recycle once after every push. New: BSYS-29629 (3pts monthly epic rotation, stateless current-epic-by-JQL) + BSYS-29630 (2pts assignee = requester).
BSYS-29630 (assignee = requester) DROPPED by Josh 2026-10-13 — overcomplicating it; users self-assign when labeling. Only BSYS-29629 (epic rotation) remains queued.

**2026-10-13 PHASE 2.6a BUILT (BSYS-29629) — monthly epic rotation.** Epic **BSYS-29634** "Estate Monitor - 2026-10" = October bucket; state = latest `epic-rotated|<key>` row in Ops Audit Log (audit log IS the state). Handler 82971161 hot-swapped: both create_issue branches set parent from the state row (blank-guarded, fail-open) — first real filing proves runtime. Watchdog recipe **EM | Monthly Epic Rotate (83019866, daily 01:23)** Slack-alerts on overdue rotation. Rotation EXECUTION runs LOCALLY (launchd com.josh.estate-monitor.epic-rotate, day 1 08:37 → harness-hook/em-epic-rotate.sh → headless claude via Atlassian MCP) because **BSYS Epic creation is BT-Team-gated** (Jira issue-type permission — same account via raw HTTP fails identically; connection 16164098 has epic rights but is bound to a FOREIGN Jira site). Long-term: grant integrations.ai@workato.com BT Team → fold into Workato. Gotchas: `wt dt create-record` fails silently without the required Created at column; Bug cannot parent to New Project/Feature (Epic-only parents); fixture BSYS-29632 = UAT artifact.
User-facing auto-triage doc live on Confluence (BTI space): "Auto-Triage: asking the Estate Monitor genies to triage a ticket" (page 2948759758, child of Estate Monitoring & Triage 2945056782) — the two labels, usage, re-triage, JQL funnel, monthly-epic rollup.
PENDING (2026-10-13): org grant of BT Team membership to integrations.ai@workato.com (Josh asked). When it lands: test Epic create via connection 18702724 (probe pattern: create + close, force-run), then fold the epic rotation into Workato recipe 83019866 (mismatch branch becomes create+close+audit-row) and retire the local launchd job com.josh.estate-monitor.epic-rotate. Until then the local job + watchdog design stands.

**2026-10-14 EPIC ACCESS GRANTED — rotation fully in Workato.** BT Team membership for integrations.ai@workato.com landed; Epic creation + Close via connection 18702724 proven. Live rollover test (job j-AbwtnrNQ): mismatch → created BSYS-29665 → audit row → closed old → Slack announce. Current epic = **BSYS-29665** (state row). Gotcha: update_issue_status fails "transition not valid" on JUST-CREATED issues with every name — works on an existing epic later; close goes LAST in the rotate chain. Local launchd rotate job RETIRED (plist removed; script kept with retired header).

**2026-10-14 PHASE 3 DESIGNED (Builder/Remediator Genies — epic BSYS-29666, 29pts, 6 stories 29667–29672, all Backlog; build kickoff = Josh, tomorrow 2026-10-15).** Spec: ~/.claude/knowledge/specs/estate-monitor-phase3-builder-genies.md (+ repo docs/estate-monitor/PHASE3_DESIGN.md). Key design: doer/reviewer genie pair (EM | Builder anthropic / EM | Build Reviewer openai), same write-skill toolkit (recipe-backed skills executing Workato REST via project-property token), containment = AHQ | AI Development / AHQ | AI Production environments; bounded passes (3 doer / 2 review rounds); trigger = send-to-build label on ticket WITH triage verdict; self-learning = Build Memory KB + 3-strike lesson promotion (dissenter-gated) + Solved-Issues pre-query + BSYS all-time bug corpus; KB scale = Enterprise Context measured, then Snowflake Cortex Search tier; manifest write-back to the tickets' Workato Manifest Link field; genies' failures monitored by EM itself. Confluence roadmap page (2949578886) tracks phase status.
Phase-3 rev 2 (Josh corrections, 2026-10-14): NO staging-to-prod — manifest-as-you-go + build report on the ticket IS the record; executor auth = token as a SECRET + Workato DEV API; generic Dev API executor skill ({method,path,body} + route guardrails) instead of endpoint-per-skill — the full Dev API reference lives as a KB; KB estate = many domain-partitioned KBs holding the FULL corpus (integration/AI/engineering); every genie action logs to EM | AI Action Log (action, reason, confidence, actor, ticket, evidence); reviewer GRADES solutions vs best practices at APPROVE; build reports on tickets are INGESTED back into the KBs; phase 3.6 = Dreamer genie (BSYS-29673, 8pts): cross-surface association + per-recipe architecture review, clustered/scored proposals (threshold math) into a proposals data table + daily Slack digest, proposes-never-applies. Epic total now 34pts. Roadmap page updated (v2).
PHASE 3 FUSION (2026-10-14, kimi-k3+deepseek-v4-pro+glm-5.3-flash, all 3 answered; log: models-evals/fusion.jsonl): top convergent adoptions — Replay Gym (solved incidents → regression farm gating ALL genie-stack changes), Shadow-Doer on-ramp (propose-only weeks → per-route success calibration), earned-autonomy ladder (L0-L3 per route×failure-class; THE intelligence product: falling human cost per fix), verify-before-grade (deterministic harness before the LLM reviewer), KB report cards (retrieval win-rates → self-pruning knowledge estate), value receipts ($X/month avoided as a query), tripwires/coroner/blast-radius graph (new story BSYS-29674, 3pts), approval cards, revert memory, plan-first pass 0 + provenance pins. Epic 29666 now 37pts/8 stories. Spec rev 3; roadmap page v3. HR-genie intelligence flywheel (events API → collector → judge → rollup → gap miner → eval harness → analyst + dashboards; 90-DAY CONTENT PURGE = capture early) is the pattern for the EM intelligence layer, minus encryption/masking (no employee PII in build telemetry).
SHADOW-MODE ON-RAMP DROPPED (Josh, 2026-10-14): dev is rollback-able; success scores come live during ramp-up. Doer writes from day one.
PHASE 3.0 BUILD STARTED (BSYS-29667): AI Action Log table 160244 (3fff8d6a-...) created; Build Memory KB kb-AbwxrfxE-znnxrC-CD created; Manifest Link field = customfield_10494 (URL). Remaining: route-catalog KB compile, executor skill (needs Dev API token as secret — Josh), AHQ AI envs (org-level). Shadow-mode dropped by Josh (rollback-able dev).

## Phase 3.1 live (2026-10-16): send-to-build → Doer

The build leg of the Phase 3 loop is live: `send-to-build` label (requires
`triaged-by-genie` present) → EM | Capture Build Request (83144038) →
EM | Builder genie (gin-AbzHEWNT-QzhREk-CD, sonnet-4-6, 3-pass cap) →
EM Build | Dev API Executor skill (83143984, skl-AbzHDreG-acsnGp-CD) via
CON | EM Builder Dev API (22328081) → build report on the ticket → label
`built-by-genie`. Audit: claim-first rows in both EM | Ops Audit Log and
EM | AI Action Log (160244, contracts synced). Manifest 366787 (11 rows,
read-back verified).

Hard-won gotchas:
- Workato API connector v53 token field is "User token" — Dev-API create with
  `input: {api_token:...}` silently stores nothing → async 401. Fill via UI.
- AIRO recipe_builder: `move_step` silently no-ops across if/elsif boundaries;
  elif chains must be contiguous — build sibling ifs instead; `!` and `nil?`
  are "unsafe/unsupported" in set_condition ruby (use ternary arithmetic);
  multi-statement ruby (`;`) fails formula validation.
- The Dev API token (keychain EM_BUILDER_DEV_API_TOKEN) is a federated
  service-account JWT (wrkaus-eyJ...), region-agnostic (200 on both
  www.workato.com and app.workato.com).
- Jira connection 18702724 moved to * Connections (2026-10-20); EM manifests filter connection deps.
- Pre-image snapshots wired (2026-10-18 late): executor 83143984 writes a
  Builder | Revert Snapshots (ea56cf30/161968) row BEFORE every PUT/PATCH
  adhoc call. **UPGRADED 2026-10-19 (real pre-image):** each branch now runs
  an adhoc GET first (steps 13 PUT / 17 PATCH, mnemonic "pre-image get") and
  the snapshot stores `'pre-image: ' + body.to_s[0, 3000]` — the actual
  response body (full recipe JSON for /api/recipes/:id), truncated to 3000
  chars for the string column. Steps: PUT 13 GET → 14 snapshot → 15 write;
  PATCH 17 GET → 18 snapshot → 19 write. Version at capture stays "pre-write";
  revert replay 83152884 consumes the snapshot key. Not yet live-fired on a
  real PUT/PATCH. Remaining v1 executor gaps: no status code in adhoc output;
  no rate cap; Reviewer genie (3.2) pending; test story filing blocked on
  Atlassian MCP re-auth.

## E2E PROVEN (2026-10-16 late): the full Phase 3 build leg works

BSYS-29612 send-to-build test: claim → Doer (read verdict, 2 audited GETs,
BUILD-COMPLETE no-op, correct contract behavior) → report comment 1141723 →
built-by-genie → build-complete row. AI Action Log claimed→executed pairs
live. Dedupe swallowed a duplicate webhook delivery (<1s no-op job).
**New standing gotcha: Jira real-time triggers started via REST can silently
skip webhook registration — after REST-start, prove the webhook with a real
event before trusting the running flag.** v1 gap: executed rows' Evidence
excerpt is null (adhoc-GET body pill) — fix next pass.

## EVIDENCE HARDENING (2026-10-17): the triage genie can no longer fabricate

Josh's rule (absolute): EVIDENCE is the product. The BSYS-29763 verdict was
built from the ticket description alone — no live reads. Now: triage genie
has a step-0 ACCESS GATE (live-read the target recipe via Recipe Details
first; unreachable = ACCESS-LIMITED verdict, no diagnosis, owning-team
guidance only) + evidence rule (ticket text is a LEAD; no live read = no
classification; HIGH confidence requires a personal trace read). Dissenter
must CONTEST verdicts lacking live reads ("FABRICATION RISK" marker) and
checks its own access first. Capture recipe 82997363 flips access-limited
verdicts to `triage-access-limited` (never triaged-by-genie → can never
fire a build). LIVE-PROVEN on the BSYS-29763 re-run: 3 failed live reads
named, leads-only language, zero fabrication, CONCUR.

Gotchas: the genie may spell the marker "ACCESS LIMITED" (space) — the label
swap normalizes (strip spaces/hyphens, match ACCESSLIMITED). Multi-statement
ruby/regex/local-vars pass set_input_field but fail start with "expression
is unsafe". `wt manifests update` breaks the in-page /export_manifests/<id>.json
route (404) — verify manifests by EXPORTING THE PACKAGE and ZIP-inspecting
(`wt packages export <id>` → poll /api/packages/<op> → download signed URL
with plain curl) — the strongest verification anyway.

## Builder report style (Josh, 2026-10-17): TIGHT, not verbose

First real build report was "too wordy" — good detail for the record, but the
same facts appeared in findings + plan + calls. Builder contract now: verdict
first, every fact ONCE, compact step table, verification caveats only where
non-obvious, ticket-history narration capped at one line, 30-second scan
target. Detail belongs in the audit log (EM | AI Action Log), not the comment.

## AI Builder project split (2026-10-18)

Builder/Red-Team/Planner stack moved to the new **AI Builder** project
(18300022). EM keeps monitoring + triage. Interface = the Jira ticket labels.
Key ids: Builder genie gin-AbzwXgbY-tho9wC-CD, capture build 83152798,
executor 83152799, Jira History 82800→83152800, AI Action Log 161960,
Build Memory kb-AbzwXh8b, Route Catalog kb-AbzwXhJJ, Planner
gin-AbzwcYko-bBE9oL-CD, Red Team gin-Abzwd8po-fkcpP9-CD (gpt-5.4).
AIRO MCP: the Builder service token authorizes app.workato.com/airo_mcp
directly (Bearer, stateless JSON-RPC tools/call — no OAuth dance); the
executor now accepts absolute-path airo_mcp POSTs (no "delete" in body).
ACL TRAP: service-account-created projects get "Everyone else in DEV: No
access" — listed in the UI but the page 404s, AIRO permission-denied, and no
project_grants POST route exists. Josh flips Access control from the list
card. Planner = always-plan contract (triage verdict OR epic frame → Build
Plan → Builder).

**Autonomy ladder (2026-10-18).** Executor 83143984 now gates every call
through Builder | Autonomy Ladder (161967) BEFORE the claim row: Search
records eq-filter on Route family with a computed family key (nested ternary,
exact seeded family strings); Level 0 → audit row (ticket|L0|ts,
l0_refused) + return L0-PROPOSE-ONLY, nothing executed; no row = default
level 1. Family vocabulary is recipe-side (Search-records has NO contains
operand — matching is a dynamic eq value); levels stay table-driven. PUT
/api/recipes/:id (code updates) and manifests/packages are propose-only.
set_condition rhs must be BARE (quoted rhs stores literal backslash-quotes).

**Failure-learning on build failures (2026-10-19).** Capture Build Request
83152798 (BT | AI Builder, v12, running) now writes a postmortem signature
doc to EM | Build Memory `kb-AbzwXh8b-kxpYwx-CD` (the project-18300022 twin
of the two same-named Build Memory KBs) on every failure terminal: (a) the
fail-open catch path after the build_failed audit row, class build-failed;
(b) after the label swap when it lands build-flagged-security or
build-needs-review, class security-flagged / needs-review. Mechanism:
EM | KB Sync (82993520) is a WEBHOOK recipe, not callable — both paths do
HTTP POST (`rest.make_request_v2`, CON | HTTP 19788749) to
webhooks.workato.com/.../em_kb_sync with
`{sync_id, kb_handle, docs:[{id,title,body,source_url}]}`; a JS snippet
builds the doc id (`build-memory/build-failures/<ticket>-<ts>.md`), title,
and signature body (route families from the plan, failing-step error,
caught-by control — no payloads/secrets). Both KB writes sit in
error-handling monitors (retries 0, empty catch = swallow) so a KB outage
never flips fail-open. Gotchas confirmed: set_condition rhs must be BARE
(re-hit live); KB Sync webhook URL is the invocation contract, doc id is the
upsert key. Manifest BSYS-29667 mirror row re-pointed 83144038→83152798;
whole-manifest staleness (old project IDs) flagged for Josh.

**Verdict-receipt tamper-evidence upgrade (2026-10-19, fusion CRITICAL #1).**
Receipts now bind the VERDICT BODY, not just the description. Triage capture
82997363's consolidator JS (step 12) computes `verdict_hash` (FNV-1a of the
final comment body) + `desc_hash`; receipt step 19 writes both plus the new
"Verdict hash" column. Build capture 83152798's gate (step 6 if) is now 4
clauses: labels AND receipt-exists AND desc-hash-match AND stale-check ==
'false' — new step 5 JS Date.parse-compares ticket `updated` vs receipt
`Created at` (fail-open to stale='false'; receipt-exists clause still gates),
receipt lookup rewired to the regenerated Ticket key field_id. Table 161966
"Builder | Verdict Receipts" is now 6 cols; ALL field_ids were REGENERATED by
the AIRO data_table_update (empty table, so no cell loss) and every
referencing step was rewired same-session. NEW GOTCHA: raw
`wt api PUT /api/data_tables/:id` with the full columns array SILENTLY
IGNORES new columns (200s, no error, 3 attempts) — new columns only land via
AIRO data_table_update, which regenerates every business field_id (refresh
table_id on each step to re-cache, then re-set all parameter keys). Both
recipes verified `running:true` by re-GET after restart.

**Builder | KB Search skill (83179640, 2026-10-19):** end-to-end proof
complete via genie-mediated TEST probe (deleted after). Defect found+fixed:
the JS formatter's array-pill binding arrived as a Ruby-inspect string, so
the skill ALWAYS returned count:0 ("No matches found") despite the search
hitting — bisect-proven (same query/config in a plain step returned 5 docs
in the same job). Fix = `.to_json` on the pill (`=_dp(...).to_json`) +
`JSON.parse` guard in the snippet; post-fix proof: count:5, top hit
"Connections (Route Catalog)" 12513c76d465f52bac111b897a121d6d score 1.0,
genie answer cited the id. Gotchas re-confirmed: (1) after restarting a
skill recipe, the FIRST genie conversation can race tool registration and
report "no such tool" — retry once before diagnosing; (2) the skill's
kb_name / metadata_filter_json / top_k params are accepted but NOT wired
(silently ignored; page_size fixed 5) — Josh to decide on ticketing.

## Estate Watchtower v1 (2026-10-19): third project built, then stopped on a heartbeat-source flaw

- New project **Estate Watchtower** — folder 35890140, project_id 18311278 (Data Tables subfolder 35890151). New projects get ZERO project grants → AIRO builder denies folder access until you copy grants: `wt api PUT /api/projects/:id/project_grants` with `{"project_grants":[{"assignment_type":"UserGroup","assignment_id":...,"project_role_id":...}]}` (config param must be a JSON string on raw recipe PUTs).
- Watcher recipe 83185818 (clock minutes/15 — minutes cadence has NO trigger_at field; WorkatoMonitor(retries=0,sleep=2) fail-open wrapper; `present` operand on `records` pill is the proven emptiness test, `blank` compiles to a string-falsy trap; slack **slack_bot** connector `post_bot_message`, NOT slack.post_message_to_channel — AIRO select_connections can't bind a slack_bot connection to the slack provider, needs raw PUT config). Heartbeats table 162338 / c8a4e0e1-5653-4e46-b2d2-ed8ba3521792.
- E2E proven (2 force-runs: alerts delivered to #estate-monitor-ops, heartbeat rows landed), then **STOPPED**: the specced heartbeat source — Ops Audit Log AI Builder copy 161961 (uuid 1cdb108a-…; task conflated it with the EM original c4019066-…/158784) — has zero rows EVER; EM original last wrote Oct 11. Captures post to Slack but don't write audit rows routinely ⇒ permanent 15-min false "dark" alarms. Restart after Josh picks the true signal; Asset Registry expected_running row deferred (registering a stopped recipe = perpetual staleness incident).
- manifest-creation split-guard refuses cross-project DEP rows (connection in EM project, table 161961 in AI Builder) — prepared payload at `orca/projects/estate-monitor/manifests/estate-watchtower-v1-prepared.manifest.json` awaits Josh's ruling.

## Collector Liveness SLO (BSYS-29746, built 2026-10-16, verified live 2026-10-19)

HR Genie collector fleet liveness, traffic-independent (reads state-table watermarks, not traffic —
a quiet weekend cannot false-alarm, a frozen watermark cannot hide):
- Recipe [83115194](https://app.workato.com/recipes/83115194) MON | HR Genie | Collector Liveness SLO —
  hourly, folder 35712141, running. Per registry row: now − last_run > multiplier × interval OR
  status ∉ healthy set → finding; findings upsert into 161166, cleared findings resolve; ANY finding
  raises `COLLECTOR_LIVENESS_SLO_BREACH` so the job FAILS LOUD (estate fail-visible pattern).
- Tables: [Registry 161165](https://app.workato.com/data_tables/f3abf1fe-7706-4edc-889d-787b3d191eb0)
  (11 rows: 82862205, 82178793, 82863111 ×6 watermarks, 82863906, 82959451 one-shot, 78545249 via
  aggregate 141250) and [Findings 161166](https://app.workato.com/data_tables/983303e1-21a6-4638-8194-c838d85325c4).
- Proof: injected stale probe → j-Abxw9sY6-XEnYka-CD FAILED LOUD with STALE+DEGRADED findings;
  95/96 hourly jobs green through 2026-10-19; probe finding resolved. Manifests 366450 / 366451
  (UI row-count read-back still pending Josh). Adding a NEW collector = add one registry row; no
  recipe edit.

## Recovery-evidence gap proven on the stop class + containment plan v2 (BSYS-29808, 2026-10-20)

First proven stop-class resolve-without-audit-row: recipe 82863630 stopped 21s (patricia@,
03:05:16→03:05:37 PT), registrar 82966985 resolved + 🟢 pinged in 24s, but Ops Audit Log shows
NO `recovered` transition (opened→ticketed→triage-in-progress→triage_failed) and the auto-filed
ticket shipped stale. Key structural fact: tickets file via human 🎫 reaction (hours late) while
auto-recovery is machine-speed — BSYS-29808's `|ticketed` row landed 4h07m AFTER the resolve —
so ticket surfacing needs BOTH a resolve-time leg (FUNC looks up `|ticketed`) AND a filing-time
leg (handler 82971161 reads Incident State Status/Resolved at, steps 5/15, and posts/corrects).
Plan v2 (3pts, dual dissent: CONTEST→revised→CONCUR) posted as comment 1143890; full plan in
projects/estate-monitor/bsys-29808-recovery-evidence-plan.md. Awaiting Josh's build go.
Gotchas: incident keys are per-occurrence (timestamp suffix — no cross-cycle dedupe overlap);
registrar's existing audit keyspace is `recipe_started|<recipe_id>|<job_id>` (no collision with
`<key>|recovered`); handler's ticket-emoji branch is gated Status=open so B2 must live in the
robot_face branch inside try(30)/catch(48).

## Collector Watermark FUNC Guard (BSYS-29746 proposal 2, built 2026-10-16, verified + closed out 2026-10-19)

First entry of the collector-framework FUNC library: shared recipe function
[83115345](https://app.workato.com/recipes/83115345) "FUNC | HR Genie | Inclusive Watermark
Advance (+1s)" (folder 35712141, running) — inputs `last_wm` + `fallback_seconds`, outputs
`from_iso` / `basis` (offset | fallback_blank | fallback_unparseable) / `prev_wm`. Guard:
`from_t = wm_t + 1` (identical to BSYS-29477's inline fix), blank/unparseable → 86400s lookback,
future watermark raises WATERMARK_IN_FUTURE. Collector 82862205 step 4 calls it; step 5 consumes
`from_iso`. Equivalence proven from traces both sides (inline boundary pair on BSYS-29477:
j-AbsPQPwN/j-AbsPQth6; live post-switch run j-Ac3wDpkx: wm 15:00:28 → from_iso 15:00:29Z,
basis offset; 372/372 FUNC jobs green). New collectors inherit the guard by calling this FUNC —
never re-inline the offset. Manifests: bundle 366450 (has both assets) + dedicated ZIP-verified
[368055](https://app.workato.com/export_manifests/368055) (29 rows, connection rows omitted).
Gotchas: recipe functions export as plain `recipe` manifest rows; job traces age out of job_get
(cite from the job-list title line); connection rows can break package builds with folder-placement
mismatches — drop them per BSYS-29667 precedent.

## 2026-10-21 — agent-flow re-verification, dissent consolidation hardening, drift audit

- EM agent flow (recipes + genies + launchd) verified ALL ON; nothing had actually been off.
- Triage + Dissenter post as ONE consolidated Jira comment (since 82997363 v18, 10-19);
  2026-10-21 hardened BOTH assemblers (82997363 v19, 82971161 v29) with a `norm()` spacing
  stage: unescape literal \n, collapse 2+ blank lines, blank line before AND after ##/###
  headers, single trailing newline. Hot-swapped live, read-back verified, restarted.
- DataGenie drift estate audit: pipeline is drafts-only (no Snowflake connection in any of
  the 9 recipes; Apply_Log all "Proposed"); Drift Check/Investigation/Remediation genies
  stopped 10-20 20:25 PT and left stopped; Drift Fix Genie = drafts-only, Josh said don't
  touch it. Last-night table deletion has no trace in Workato — decisive trace is
  Snowflake ACCOUNT_USAGE.ACCESS_HISTORY/QUERY_HISTORY once the table is named.

## 2026-10-22 — PARKED: external-channel triage (#hr-genie-ops)
- Josh wants 🤖/🎫 triage on the HR Genie watchdog's OWN alerts in #hr-genie-ops
  (C0BSRRWR2KB, private, bot U0BTJ9HNY8Y) — NOT EM alerts there. Parked until EM is live
  in prod (BSYS-29559); full design in repo BUILD_LEDGER 2026-10-22. Bot invite prereq:
  U0C9A0WBB88 must join the private channel (delivery + posting).

## 2026-10-22 — BUILT: Recovery Evidence FUNC (BSYS-29808, plan v2 shipped)
- FUNC | EM | Recovery Evidence 83290928 (EM Functions folder 35778611): Leg A writes
  `<incident-key>|recovered` (search-then-create, idempotent — re-run returns
  `false_recovered_row_exists`), Leg B1 posts the resolve-time recovery comment on the
  ticketed row's ticket via the /browse/ anchor + [COR] Jira 18702724. Fail-open
  (retries 0, log-and-swallow catch). Wired: registrar 82966985 step 10 (after resolve
  claim); ESH 82966998 steps 18/32/44 (degraded/connection/safety-net resolvers);
  handler 82971161 B2 filing-time leg (monitor 25: if Resolved at -> recovery-facts
  comment + update_issue corrected business-impact line) at the end of the robot_face
  filing branch. All running:true, post-push ESH sweep green.
- Proven live both orderings: ticket-first (BSYS-29902: 1 recovered row + B1 comment,
  registrar job j-Ac6NKcNm-mzBaxA-CD comment_posted=true) and recovery-first
  (BSYS-29903/29904: B2 comment + corrected description). Happy path + idempotency:
  caller 83291371 jobs j-Ac6NHmCM/j-Ac6NHsdd. Fixture tickets are TEST filings.
- Build lessons: (1) AIRO builder DID auto-rewrite ruby() bindings on insert-renumber
  this time — the "bindings don't renumber" trap did NOT fire (builder version drift;
  still verify with recipe_builder_show after every insert). (2) move_step STRIPS the
  moved step's fields — re-set flow_id/parameters after any move. (3) add_step inside a
  monitor try APPENDS at try-end regardless of position (3rd confirmation). (4) Unicode
  in AIRO-set ruby() strings still lands as literal \uXXXX text — write ASCII in machine
  comments. (5) Package export FAILS when a manifest row references a connection outside
  the source project ("not found under <project>") — strip * Connections rows (BSYS-29667
  class) before citing; manifest 370497 read-back + ZIP verified after the strip.

## 2026-10-22 — FIXED: triage-comment formatting (BSYS-29808 scope addition)
- Both assemblers (handler 82971161 step 48, Capture Triage Request 82997363 step 12) now
  emit Jira WIKI markup, not GFM: ** -> *, backticks -> {{code}}, ## -> h3., ### -> h4.,
  ```fences``` -> {code}. The integrations.ai Jira connection renders wiki markup
  (proven: descriptions with single-* render bold); GFM ** escaped to literal \***.
- Raw-dump class GUARDED: no consolidation header in the genie output -> minimal formatted
  fallback posts (verdict line + adversarial check + evidence bullets + suppression note),
  never the raw dump; the old "[consolidation notice] raw output follows" path is gone and
  the 1./a. numbered-opener artifact can't survive (detection strips digits/letters/emoji
  openers before the marker match). Closeout for the triage-genie-raw-output-dumps memory.
- Proven: probe comments 1146967/1146968 on BSYS-29904 (A/B vs broken 1146951) and REAL
  pipeline verdict 1146977 on BSYS-29906 (contested->revised path, renders clean).
- Probe-loop observation: TEST probes got started/stopped by a second AIRO actor
  ("Workato AHQ | AI") mid-test (probe 2 14:24, probe 1 14:55) — likely the parallel
  session re-running choreography; FUNC recorded those recoveries correctly. If probe
  cycles get noisy, add an expected-stop-tolerant flag on Monitor Scope rows (triage
  suggestion, not built).

## 2026-10-23 — FIXED: build-report formatter (BSYS-29808 scope addition #2)
- Build pipeline 83144038 (EM | Capture Build Request) step 10 sanitizer got the SAME
  GFM->wiki contract as the triage assemblers, plus a scaffold strip: drop empty list
  nodes, flatten indented outline items (the genie's "1.->a.->i. Triage Verdict (as
  read)" skeleton) to clean h4/paragraph text. Proven end-to-end on BSYS-29904
  (job j-Ac6RgW4A-GQJQoB-CD -> report comment 1147085, read back clean).
- Trigger gotcha learned: after a push + stop/start cycle on a jira.updated_issue_webhook
  recipe, the Jira webhook needs the restart to re-register (two Jira updates delivered
  nothing until stop/start); labels-only edits may not bump issue `updated` — nudge with
  a real content update. force-run is scheduler-trigger-only (422 on webhook recipes).

## 2026-10-24 — BUILT: session-scoped audit layer (BSYS-29944, live-verified in dev)

- **EM | Session Log** table 164689 (UUID 020eb6ed, EM audit folder 35873192): session_key =
  skill-trigger `context.conversation_id` (native — no new plumbing), actor, action, target,
  reason, confidence, outcome (executed|l0_refused|refused|reconciler_run|unattributed_change),
  ticket_key, payload_ref, occurred_at. Queryable index; full request/response JSONL per session
  in FileStorage at `/em-audit-<conversation_id>.jsonl` (flat — see gotcha below).
- **Both executors gained 2 steps** (83143984 v1 + 83152799 v2, both running): FileStorage append +
  Session Log row via the data-tables records API. Verified live end to end on BOTH: v2 job
  j-Ac8CCxWn, v1 job j-Ac8CeEWC (real genie call, full chain, real conversation ID in the row).
- **Ladder hardening:** `/api/agentic/* (genie lifecycle)` = level 0 (propose-only) — live probe
  returned L0-PROPOSE-ONLY with audit row (j-Ac8CJzLn). Genie start/stop/create can no longer be
  executed by the Builder genie without Josh. v1 family-key updated; v2 ladder-gate parity deferred.
- **Reconciler** [83326270](https://app.workato.com/recipes/83326270) (daily 1440min, running):
  fetch inventory (2 pages) → try-read prior snapshot (catch = first-run baseline, logger marker)
  → **drift gate FIRST** (js throws "EM INVENTORY DRIFT: created=[...] deleted=[...]" — the failed
  job IS the alert) → Session Log row → snapshot overwrite. Gate-before-snapshot ordering is
  load-bearing: a drifted run must never re-baseline. Drift-throw NOT yet proven — blocked by the
  schema-service degradation (below); self-heals on recovery.
- **Probe harness:** TEST BSYS-29944 session-audit probe 83326118 (manifest-exempt, stopped):
  clock 60min + workato_genie assign_task_to_genie — the reliable skill-invocation test surface
  (headless API not enabled in this workspace; MCP gateway doesn't serve these skills).
- **Manifests 371307/371310 need UI REBUILD** — created via create_manifest.py before the
  2026-10-24 doctrine change (UI-built only). Rebuild via RLM > New manifest before promotion.

### 2026-10-24 (later) — deferred items CLOSED
- **Reconciler drift-throw PROVEN**: job j-Ac8DCazx failed with `EM INVENTORY DRIFT (BSYS-29944):
  created=[] deleted=[...named tables...]` — the failing job IS the alert. Re-baseline flow proven
  (snapshot delete → baseline → clean); reconciler steady on a fresh snapshot. Gotchas: delete_file
  reports "File not found" even when it works; FileStorage content pill is a stub string in traces
  (lazy-load display) but delivers real bytes to js_eval.
- **v2 ladder gate deployed** via records-API query (`POST /api/v1/tables/:uuid/query`, server-side
  where-filter on Route family) — immune to the schema-service degradation. Start-validated, running.
  Live-fire through a healthy genie is IMPOSSIBLE by design: the genie reads the ticket + ladder KB
  and refuses at its own policy layer ("Route Blocked: /api/agentic/* is Level 0") — defense-in-depth
  confirmed. Executor-gate live-fire = component verification only (start validation + curl-verified
  shapes + v1's identical live-proven mechanism).
- Formula-transpiler traps: ruby hash literals in formulas → `# INVALID RUBY FORMULA` corruption
  (build JSON by string concat + to_json); condition bindings must use TYPED pills (root pills → nil
  at runtime); formula whitelist has no map/sort/size/to_h/JSON.generate/iso8601.
- Manifests 371307/371310 still need the UI rebuild (Josh).

**+ 2026-10-26 (verdict run):** watcher v1 83185818 was DELETED 2026-10-20 (delete-and-rebuild, cortex/investigations/recipe-deletions-404-1021.md); v2 83196679 "Estate Watchtower | Watcher" is an UNFINISHED STUB (empty trigger, 0 jobs) — the 352-353 section above describes the pre-rebuild state and the one-field table_id repoint is now moot (v1 gone). Watchtower still dark; finishing v2 (with heartbeat source 158784, row-flow re-verified at build time) is an open builder-session task. Full re-verify block in dreams/proposals/2026-10-20-em-watchtower-heartbeat-repoint.md.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Estate Monitor](projects/estate-monitor.md) — **estate-wide Workato monitoring platform** (epic BSYS-29554; canonical repo ~/orca/projects/estate-monitor/ — CLAUDE.md + docs/estate-monitor/HANDOFF.md + BUILD_LEDGER.md); dev project 18242571, 11 recipes + 6 tables + reaction handler; phase 1 (alert→🎫→auto-assigned BSYS Bug→thread reply, idempotent) LIVE+UAT in dev; phase 2 filed (29565 Triage Genie read-only on 🤖, 29566 local harness hook) awaiting swarm; prod promotion 29559 Josh-gated; standing rules: monitors never monitor monitors (zArchive + estate monitor + operational monitoring exclusions in-resolver), claim-first recovery, audit everything
