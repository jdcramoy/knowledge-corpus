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
REVIEWER TOPOLOGY CORRECTION (Josh, 2026-10-15): the reviewer is NOT a sequential verdict gate — it's a REAL-TIME observer riding the EM | AI Action Log stream (new-record trigger → critique → feedback rows the doer reads before its next action); interjections are themselves memory; terminal verdict + grade at the end. No round-trip pass/round structure; pass cap = fuse only. Also: the Sherpa's AIRO Execution Genie (gin-AbMRcfDh, 96 skills) + run_airo_build_in_steps driver = reusable prior art for the phase-3 write toolkit (adopt, don't rebuild).
