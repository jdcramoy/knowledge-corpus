# Knowledge Index — routing table

One line per knowledge file. Read the line, load the file if relevant to the
current work. Update the line whenever you update a file.

## Domains (cross-project: load whenever working in this domain, any project)

- [AI-spend ROI framework](roi/framework.md) — leadership-defensible cost-to-value story (2026-10-11/12): three Josh-personal spend surfaces, $17,319 2026 YTD; narrative law, burst-vs-steady ruling, scripts + weekly job in file
- [Frontier stack](domains/frontier-stack.md) — 10-idea fusion build LIVE 2026-10-11 (Estate Twin, Integrity Mesh, Calibration Ledger, Saga Protocol, Skill League, Chaos Canary, Shadow Estate); contracts in scripts/frontier/CONTRACTS.md; nightly 04:43
- [Needs-josh interview skill](../.claude/skills/needs-josh/SKILL.md) — /needs-josh (2026-10-26): parses registry needs rows, stale-checks each against live evidence BEFORE rendering (dead asks close themselves), verbose clickable decision cards, verdicts write back via mission-control; built after Josh discovered 50+ asks he had never seen
- [Claim lifecycle layer](domains/claim-lifecycle.md) — BUILT 2026-10-23: claim-latency.py, autonomy.py earned-trust engine, session-closeout.py; contracts in scripts/lifecycle/CONTRACTS.md; bimodality verdict due ~10-30
- [Model gateway playbook](domains/model-gateway-playbook.md) — multi-model harness on the Workato AI gateway: roster, verdicts, bench script, agent model pins, fusion skill; sonnet stays glm-5.3-flash (Josh)

- [Agentic platform lessons](domains/agentic-platform-lessons.md) — HARD-EARNED 2026-10-10: every collection proof needs a volume assertion on what LANDED (100x under-collection); Otto codebase study, 12 code-cited lessons
- [Workato platform](domains/workato-platform.md) — THE platform behavior/traps hub: observability, ops coverage, dev/prod CLI split, change-tracking layer, import/remap laws, prod destructive-action contract, legacy-tree mining; SOPs live as global skills
- [Estate reviews + staged remediations](estate-reviews/) — estate-architect reports and execution artifacts (archive staging, prod-personal-connections plan, ops-listener autopsy, Frontify token, corpus indexer flag)
- [Orchestration router](domains/orchestration-router.md) — solo/fanout/pipeline/team decision engine (hard rules then 6-feature score); teams-vs-fanout doctrine in file
- [Workato Terraform provider](domains/workato-terraform-provider.md) — private repo, dev-live-tested 2026-10-19; Josh ruling: bootstrap/UAT/API-truth yes, prod+manifests+hotfixes no, ambiguity holds
- [Workato API dead ends](domains/workato-api-dead-ends.md) — CONFIRMED-404 ledger (recipe snapshots, custom_adapter GET/versions, manifests list) + dt-UUID/trap ledger; Josh rule 2026-10-13: append every 404/permanent failure same session, check before probing undocumented endpoints
- [Tech review lessons learned](domains/tech-review-lessons-learned.md) — FTR feedback mined from [requester]'s comments on 17 deployment requests (2026-04→2026-10, 2026-10-21): chronic three = hardcoded env-specific values, loop-heavy logic, dev/prod connection-name mismatch; 9 lessons with ticket citations; enforcement checklist lives in workato-development-playbook SKILL.md
- [Workato review guard](scripts/workato-review-guard.py) — LIVE 2026-10-27: Patricia's BSYS-29592 five DR-review findings as mechanical checks (R1 loop-pill hygiene, R2 batch-where-possible WARN, R3 no hardcoded Slack IDs, R4 bot identity for bot posts, R5 adapter titles ≤30) — read-only wt GETs; modes --recipe/--folder/--files/--adapter-code; wired into promotion-readiness row 9, workato-skill-builder build-time step, manifest-review item 8, playbook doctrine "Review-ready build standards (Patricia review 2026-10-20)"
- [Manifest review](domains/manifest-review.md) — REVIEW-side RLM manifest audit (BSYS-29510): live-verify posture, locate-by-manifest-id, cheap connector closure, connection-promotion ruling, blocking/non-blocking comment format
- [Workato Slack bot connections](domains/workato-slack-bot-connections.md) — standing rules: never personal user connections; workspace-owned BT-approved app per integration; genie Slack-trigger silent-death triage
- [Google Sheets browser editing](domains/google-sheets-browser-editing.md) — Playwright/Sheets editing: CSV-export read-back, Name-box hidden-row trap, stale-profile-lock fix
- [Orca browser](~/.claude/skills/orca-browser/SKILL.md) — global skill; Workato UI automation (env switcher dev↔prod, Enterprise MCP tool-description dialog, native-setter textarea + served-description verify, Test-recipe cycle, translocation fix)
- [claude.ai web](~/.claude/skills/claude-ai-web/SKILL.md) — global skill (2026-10-15): drive claude.ai in Orca browser; Tiptap composer = fresh-ref focus + orca type; artifacts/dashboards/motion have NO API
- [Workday platform](domains/workday-platform.md) — Workday SOAP/WSDL/WQL knowledge; lookups via workday-wsdl-lookup + wql-query-builder skills; developer-site corpus in KB; payment-election + WQL laws in file
- [MCP operations](domains/mcp-operations.md) — MCP reconnect/reauth ops across clients; claude.ai enterprise connector controls; Research-mode hijack incident SOP
- [Claude Code mods](domains/claude-code-mods.md) — workato-guardrails v1.0.0 (15 hooks incl. push identity guard + prod-write confirm gate), session-budget plugin, grill-gate, /reload-session; patch ~/mods, cp to cache, plugin test
- [Claude Code docs canon](domains/claude-code-docs-canon.md) — official-docs best practices (fetched 2026-10-07); section 5 = deliberate harness divergences, never propose reverting
- [Josh Model + context compiler](specs/2026-10-23-josh-model-context-compiler-design.md) — preference/precedent store + josh-model.py + hook 16 first-prompt briefing; scribe+propose only; LIVE 2026-10-26 after the process-is-not-defined silent-no-fire fix (trap writeup in domains/claude-code-mods.md); seed 83 rows, recall@8 baseline 1.000; Phase 2 = miner drafts emitter, /triage preference lane, hit-rate join
- [Project Dreamer](domains/project-dreamer.md) — 7th agent, nightly 00:37 architecture dreamer for PROJECTS; advisory-only, dissenter-gated, cap 3/night; drift-gate + gym/canary live


- [Josh's writing voice](domains/writing-voice.md) — STANDING RULE: apply josh-writing-voice to everything published as Josh; adapt-never-mirror doctrine; voice ground truth = domains/josh-voice-corpus.md
- [Red-team gate](domains/redteam-gate.md) — STANDING ORDER 2026-10-12: every prod promotion carries a red-team verdict (skill red-team-review + agent red-team + redteam-guard.sh Stop hook); tiered depth, fatal blocks unless Josh overrides by name; verdicts in knowledge/redteam/
- [Jira autotriage loop](domains/workato-platform.md) — skill jira-autotriage: identify-triage-plan-fix with the constitutional decision matrix; hotfixes never auto-remediated; fleet job 2h
- [HR Genie auth-fix playbook](domains/hr-genie-auth-fix.md) — end-user "cannot reauthenticate" SOP: platform health check → VUA-revert trap check (tools.json vua_required) → stale runtime-child find (connection_lost_at ≈ report date) → backend reset (delete child) → canonical 11-step reconnect guide; proven 76177 + 77184
- [Dream loop + harness backup](domains/dream-loop.md) — nightly dreamer on launchd fleet, trust ladder with never_auto, /triage + sync bridge (2026-10-23), decision inbox, bus actuation (2026-10-14); backup 23:33 to github Workato-All/josh-orca
- [Knowledge write-durability stash](scripts/knowledge-write-stash.py) — LIVE 2026-10-19: 900s snapshots of bash-append ledgers into gitignored .stash/, survives filter-repo; restore command in file
- [Instruction-patch loop](instruction-patches/README.md) — corrections-to-instructions self-learning: nightly zero-LLM miner, coverage check vs instruction surface, gated applier; seed run 8/8 covered
- [Decisions engine](scripts/decisions.py) — typed-judgment primitive (OpenAI Decisions CONTRACT): UAT vs Josh verdicts FAILED 0.25-0.36, urgency inverted; wired SHADOW only; taste-class filtering closed until a tool-using judge exists
- [Decisions judgment: the Jev replica arc](domains/decisions-judgment.md) — 2026-10-23/24 arc: four backtests (ensembles dead, precedent +37pts, urgency dead), 6 levers wired, order-never-filter doctrine

- [Brain gardener](domains/brain-gardener.md) — curator AND brain-architect agent + brain-guard plugin (write-lint, usage+MCP-economics telemetry); claim ledger; dedup/harvest/docs-watch scripts; docs crawler nightly 22:31 feeding platform deltas; proposals-as-git-branch; outcomes log; gardener nightly 22:43 self-rearming
- [Brain architecture rulebook](domains/brain-architecture.md) — structural best practices the gardener audits against (Phase 2.3): size budgets per file type, hub/reference modularization SOP, thin-index rules, skill/agent description routing, prose-that-should-be-a-hook, anti-pattern catalog
- [Architecture maps](domains/architecture-maps.md) — arch-diagram skill: per-project two-level mermaid maps, auto-invoked by handoff, QA'd nightly; mermaid syntax rules in file
- [Harness documentation](domains/harness-docs.md) — repo + Confluence doc tree (BTI space, 8 pages, parent 2938830860); ID map + publish policy in kit repo docs/harness-docs/manifest.json; weekly self-rearming sync job Tue 06:57 keeps live harness / repo / Confluence from drifting; sanitizer + read-back required on every publish
- [Librarian](domains/librarian.md) — 8th agent, LIVE 2026-10-11: producer agent; consolidations on librarian/* branches, primers additive, position pieces with dissent log, weekly procurement beats; Sun 21:37
- [Library (procured content)](library/README.md) — librarian-written syntheses of external beats; sourced + dated; additive lane
- [MCP goes enterprise-grade, 2026-10](library/mcp-enterprise-shift-2026.md) — 2026-09-28 stateless MCP release + IdP-managed auth + A2A/MCP split + Atlassian MCP 220-tool rebuild; house ties: gateway header routing, dedicated-app governance, token budgeting, fleet discovery
- [Positions (position pieces)](positions/README.md) — dissenter-collaborated house positions; each carries a dissent log; branch-gated
- [Prompt optimization: DSPy + GEPA](domains/prompt-optimization-dspy-gepa.md) — BANKED 2026-10-13, parked; strongest future target = PR-002 AI-judge prompt, never measured; Pareto shortlists never decide
- [Anthropic Compliance API](domains/anthropic-compliance-api.md) — PROVEN claude.ai org-data path: keychain token, endpoints live-verified 200 (2026-10-15); check BEFORE routing org-data asks to org owners

- [Error canon loop](domains/error-canon-loop.md) — deterministic error→memory→canon reinforcement: error-sensor.py hook captures EVERY tool error to error-events.jsonl; error-canon-promoter.py promotes repeats (3x across 2+ sessions) to error-canon.jsonl; sensor injects the recorded lesson on next occurrence + the --record command that closes the loop. Born: error-ledger capture was voluntary and leaked
- [Workato dev APIs](domains/workato-dev-apis.md) — synthesis doc from the 2026-10-16 KB audit: Developer API surfaces for cold-start sessions working in this domain
- [Workato SDK internals](domains/workato-sdk-internals.md) — synthesis doc from the 2026-10-16 KB audit: connector SDK internals for cold-start sessions working in this domain
- [Cortex constitution](cortex/CONSTITUTION.md) — cortex's attention-order constitution: prod/safety first, then contradictions, coherence, curiosity
## Projects (load when working in this project)
- projects/bt-genie.md — BT Genie PROD (ws 3535598, GPT-5.2, 15 skills, 1.7k users): P0 bugs 42% Create-Request failure; Dev Super BT Genie 2.0 feedback pipeline built 2026-10-22; details in file
- projects/csm-genie/ — CSM Genie ops notes; BSYS-29646 access plan (end-user access list vs Firefighter provisioning, awaiting Josh go)
- projects/genie-destructive-gate/p1-spike.md — BSYS-29829 P1 spike DONE 2026-10-22: 57 destructive recipes on 55 genies inventoried; build phase blocked on Josh-Joel sync
- projects/valkyries-tickets-genie/ — BTSUP-78586 AHQ|AI project setup plan + VUA-keyed data isolation contract (awaiting Josh go)
- projects/bsys-25527-risk-tier-governance.md — BSYS-25527 BUILT in dev 2026-10-10 (recipe 82959473 weekly risk-tier review + 3 tables in AIAR project; live-job UAT evidence incl. gate decision loop; recipe STOPPED — slack_bot connection is the Josh-gated remaining item; loop-variable staleness + is_true-condition traps in playbook)
- projects/bsys-25528-vibe-app-registry.md — BSYS-25528 BUILT in dev 2026-10-10 (registry + snapshots + Register App API); remaining: UI activation + MCP attach + EA baseline import
- projects/workato-dev-kb.md — shareable Workato dev knowledge pack (RAG+++fractal+playbooks): v1 built local, first push Josh-gated

- [Workato KB (RAG++)](projects/workato-kb.md) — corpus hub: ~105k docs/383k chunks, 9 sources incl. Slack/Atlassian/LangChain waves; 2026-10-16 audit fixed dead BM25 leg; pipeline audit + eval gates in file
- [Drift-fix project](projects/drift-fix-project.md) — externally maintained project 10593549; 2026-10-21 overnight incident verified (table 157379 deleted, zero-ledger); findings in projects/drift-fix/
- [Google Slides MCP](projects/google-slides-mcp.md) — 62-tool GSlides MCP; guidance-injection via enterprise_context, Frontify brand sync live in prod, BSYS-29719 dev-complete 2026-10-20; prod promotion Josh-gated
- [Google Workspace Semantic MCP](projects/google-semantic-mcp.md) — self-learning semantic gateway (epic BSYS-29262): typed ops shipped, BSYS-29651 residuals closed 2026-10-24; now porting to otto; FULL-SPINE promotion manifest 372377 assembled + package 42329814 verified 2026-10-26 (DR BSYS-29592, manifest-link field status-locked in FTR); canonical repo ~/Documents/ChatGPT/Google Workspace MCP/
- [Developer API Semantic MCP](projects/dev-api-mcp.md) — 3-tool semantic gateway over the Workato Developer API (BSYS-29894, dev-only): Phase 5 + red-team closed, Phase 6 benchmark campaign live; repo ~/orca/projects/dev-api-mcp
- [Enterprise Data MCP](projects/enterprise-data-mcp.md) — Track A/B epics (BSYS-28046/28047/28048); semantic layer + learning flywheel sibling design
- [HR Genie](projects/hr-genie.md) — the HR Genie platform (notifications, intelligence platform, FY27 review cycle BSYS-29730 BUILD COMPLETE 2026-10-25); P2 hotfix + import laws + full dated changelog in file
- [GRC GDPR Emails](projects/grc-gdpr-emails.md) — privacy@workato.com → #gdpr-requests bot post (BTSUP-78086); recipe 82910707 dev-verified both paths, STOPPED pending start-vs-promote call; lessons: wt-created projects are grant-locked for AIRO, orca tab create, f-string pill slice unsupported
- [PTO platform](projects/pto-platform.md) — BSYS-26808; Spike 1 NO-GO (2026-10-10); Manager PTO Digest RETIRED (Josh); runtime lessons remain valid in file
- [Otto (workato/otto repo)](projects/otto.md) — private Workato org repo; semantic gateway port target; 7 flywheel loops live, canary on consented identity; 3.13-oracle lesson: run suite in-container before every commit
- [Baseten switch](projects/baseten.md) — canonical: ~/Documents/Claude/Baseten-Switch-Claude-Code-Master-Knowledge-Doc.md
- [AI Directory (Patricia's)](projects/ai-directory.md) — the Workato estate directory MCP (folder 30049351); BSYS-29779 re-architecture to data-table inventory + delta sync + paginated tools
- [Estate Monitor](projects/estate-monitor.md) — estate-wide monitoring platform (BSYS-29554): phase 1 live+UAT in dev; standing rule: monitors never monitor monitors
- [Event Process MCP / Event360](projects/event-process-mcp.md) — Event360/Campaign Copilot MCP app (BSYS-28196); addCalendarEvent in prod; Marketo reauth + quota signatures in file
- [Marketo EventOps MCP](projects/marketo-eventops.md) — July 2026 BSYS-26824 app; 2026-10-21 FTR blockers verified (stale manifest link + failed red-team package)
- [Workday Org Chart MCP](projects/workday-org-chart-mcp.md) — snapshot-backed org-chart MCP (skill 74594114); NO PRODUCTION promotion standing rule; canonical repo ~/orca/projects/org-chart
- [Multi-Genie Orchestration](projects/multi-genie-orchestration.md) — Main Genie routes to 12 specialists via Cloud Run gateway; POC FROZEN pending direction; read the handoff in full before any work
- [Agent harness hygiene](projects/agent-harness-hygiene.md) — harness-hygiene plans + evidence; first entry BSYS-29457 (workato-health.py mock-probe filter + dedupe-on-append + open-slug check — all 3 landed, plan = trace-verify + residue collapse, 2026-10-10)
- [Outreach by Workato MCP](projects/outreach-mcp.md) — epic BSYS-25535 + BSYS-27111 create_prospect build (2026-10-10): skill recipe 82959480 on SDK conn 15862972, dev MCP mcps-AbsoJko8-hrL-CD; traps: workato_skill.start_workflow replaces deprecated genie trigger, code_input leaf-set idiom, dev conn 19327220 CONNECTION-LOST, skill-recipe invocation paths all UI-gated
- [Seismic by Workato MCP](projects/seismic-mcp.md) — created 2026-10-10 from legacy mining: connector 1355883 v100/46 actions, MCP server mcps-AbYXRs4T-YNH-CD/30 VUA tools, BSYS-29281 never imported; Seismic OAuth PKCE + scope-rotation rule + rate-limit classes + entitlement fallback contract
- [Google Docs MCP](projects/google-docs-mcp.md) — legacy 11-tool prod-only MCP (folder 29890954); BSYS-29692 2026-10-14: structural-delete fix (delete_row/column/table + remove_bullets) built+unit-tested in dev twin 83074320, audit fixes on create_document/list_suggestions/list_mentions; live UAT pending Josh SSO; deprecate when GWS Semantic covers Docs
- [Google Calendar MCP](projects/google-calendar-mcp.md) — created 2026-10-10 from legacy mining: 17-tool dev server (BSYS-28798/28799), structured error envelope pattern (MCP isError gap), schema-default-vs-fallback drift, Gmail/Calendar Workato-MCP parity gaps (draft-delete absent, intent_scoped commits on first call)

- [Architecture lineage maps](architecture/) — 8 estate-architect lineage maps (2026-10-12): job collectors, data-hub ingest, inbox-tasks, operational monitoring, ops-job completion
- [BSYS-29828](projects/BSYS-29828/) — Genie destructive-capability approval gate technical plan (BSYS-29829)
- [Agent harness operations](projects/agent-harness-operations/) — epic BSYS-29454 ticket files: dreamer/project-dreamer heartbeat wiring (BSYS-29461) verified wired end-to-end by run-job.sh v2, close-on-evidence
- [BSYS-26808](projects/bsys-26808/) — BSYS-28412 Phase 3 remaining-work plan (2026-10-20, dissent-amended)
- [BTSUP-78227 ops genie planwise](projects/btsup-78227-ops-genie-planwise/) — root cause + staged customer reply drafts (staged, NOT posted)
- [BTSUP-78827 claude projects extract](projects/btsup-78827-claude-projects-extract/) — org-wide Claude Projects extract CSVs/JSON (2026-10-15/16)
- [BTSUP-79061 review-gen snowflake](projects/btsup-79061-review-gen-snowflake/) — Snowflake read-grant request draft for Josh to file
- [BTSUP customer replies](projects/btsup-customer-replies/) — staged reply drafts for 78227/78827/79061/79354, confirm-gated
- [Deployment request autodeploy](projects/deployment-request-autodeploy/) — BSYS-29383 autopsy: the 30-job recipe-function-execution-error class (duplicate-name resolution) + plan
- [Google Drive MCP](projects/google-drive-mcp/) — BSYS-27477 native-file content refresh plan
- [GSlides MCP tickets](projects/gslides-mcp/) — BSYS-29418 extract-design-system envelope fix + BSYS-29458 VUA-flag plans; sibling of google-slides-mcp/, consolidation pending
- [Vibe-coded governance](projects/vibe-coded-governance/) — BSYS-25526-25529 third-party AI builder governance: Lovable procurement, classification gate, registry completion, enablement
## People (durable personnel files, LOCAL-ONLY — excluded from GitHub backup)


- [Cortex coordinator](domains/cortex.md) — fleet coordinator: hourly launchd pulse (fleet job `cortex`), model routing table (config/model-routing.json), bounded dispatch authority (≤2 read-only investigations/pulse, default permission mode), attention queue feeds morning brief
- [Measure-learn-apply loop](domains/measure-learn-apply.md) — the weld contract: measure (ledgers) → learn (dreamer/gardener/evidence/governor) → apply (instruction-patch, routing proposals, canonize-failure, rehearsal); loop-closure rules with teeth (2026-10-09); **cost/quality governor LIVE 2026-10-09: cost-governor.py (daily class×model posterior table, budget alarms, proposals-only) + roi-report.py (monthly KILL/PROMOTE/KEEP per capability), fleet job `cost-governor`**; **+ VALUE ledger LIVE 2026-10-09: value-ledger.py (derive idempotent from triage/proposal/build-ledger/jira-runs; build rows keyed per TICKET not per mutation; human `note` rows for what ledgers can't see) + value-report.py (monthly value-vs-cost, imports roi-report's mapping) — fleet job `value-ledger` 23:50 derive / 1st of month report; 53 rows / 132h returned month-to-date**
- [Spec distiller + evidence agents](specs/) — **spec gate LIVE 2026-10-09 (kills wrong-approach rework, the #2 friction class): `agents/spec-distiller.md` writes `specs/<slug>.md` (goal, scope in/out, `- [ ]` objectively-verifiable criteria, design gate, risks) BEFORE any build — advisory-only, builder must cite the spec path; `agents/evidence.md` hunts last-24h "done/built/fixed/verified" claims in transcripts (grep-and-sample) + jira-triage/runs.jsonl, re-checks each vs live evidence, writes `garden-reports/evidence-<date>.md` (CONFIRMED/UNVERIFIED/FALSE, FALSE → dissenter review, nothing muted); `scripts/spec-score.py` = zero-LLM mechanical self-score (keyword overlap, humble — no evidence = MISSED) appending to `specs/<slug>-score.json`; both playbook skills reference the gate (spec before build / score cited after)**; first spec seeded: `specs/bsys-29418-prod-push.md` (in-place prod push of the 403-envelope fix to 82090477, pending Josh stop-push-start confirmation); `specs/estate-monitor.md` (2026-10-11): estate-wide monitoring platform, dev-only, explicit scope enrollment, seeds 14570285/17923915/15643451
## Rules

1. **Scope test**: makes ANY project better → domains/. Makes THIS project's
   next session better → projects/<name>.md. Is a procedure → global skill.
   Is the full canonical story → project repo; knowledge file points to it.
2. **Auto-save**: every true build/technical session deposits durable lessons
   into the project file + updates its INDEX line at session end. Q&A saves
   nothing.
3. **Absorb on touch**: loose docs in ~/Documents/Claude/ are linked here,
   not moved; when a file is next touched, absorb its durable content into
   the project file and leave the original as archive.
- [Cortex coordinator](domains/cortex.md) — fleet coordinator: hourly launchd pulse (fleet job `cortex`), model routing table (config/model-routing.json), bounded dispatch authority (≤2 read-only investigations/pulse, default permission mode), attention queue feeds morning brief
- [Measure-learn-apply loop](domains/measure-learn-apply.md) — the weld contract: measure → learn → apply with loop-closure teeth; cost governor + value ledger live (fleet jobs)
- [Spec distiller + evidence agents](specs/) — spec gate LIVE 2026-10-09 (spec before build, score cited after); evidence agent hunts 24h done-claims, FALSE goes to dissenter; spec-score.py self-scores
- [Harness next-10 review](reviews/harness-next10-2026-10-11.md) — 2026-10-11 6-lens adversarial panel, ALL 10 BUILT same day (commits ead1037/edd2a39, kit f2ded3b): store discipline live, probes+dead-man scaffold, bus epistemics, 11/11 commissioned, shadow economy, restore drill 6/6; lessons + residual gaps in domains/dream-loop.md §2026-10-11
- [Harness cost/benefit analysis](reviews/harness-cost-benefit-2026-10-11.md) — 2026-10-11: $3,371/7d segmented (Workato 91% / harness 8.6%); token volume + fleet inventory + value ledger; run-vs-build verdict + cost levers
- [Harness wave-3 science review](reviews/harness-wave3-science-2026-10-11.md) — fusion panel for physics/QM/evolution ideas: trials-factor null calibration, fluctuation-dissipation gate, QEC x ratchet cross-pollinations
- [Wave-3 science stack](domains/wave3-science-stack.md) — ALL 11 BUILT + LIVE-VERIFIED 2026-10-11 (null-miner, fdt-gate, fusion-policy, MAP-Elites, pleiotropy, spore-router SHADOW); deferred items Josh-gated
- [Harness fusion audit 2026-10-12](reviews/harness-audit-2026-10-12.md) — 3-model panel: 33+/36 VERIFIED, 0 BROKEN; P0 heartbeat.jsonl replace race root-caused; 7 findings queued to triage
- [VUA revert on push](domains/vua-revert-on-push.md) — canonical trap doc, motif vua-revert-on-push: push silently reverts VUA personalization to base identity; law = read-back verify after every push, repair via direct PUT; instances 2026-09-11, 2026-10-01 x2
- [HR Genie how-it-works](projects/hr-genie/how-it-works.md) — plain primer for cold-start: genie, VUA skills, notification platform, intelligence loop, consumer-endpoints odd duck; topology truth = system-map.mmd
- [Attention bottleneck](library/attention-bottleneck-mission-control.md) — procured 2026-10-11: field consensus on multi-agent oversight matches Mission Control design; AgentGUI drift-prevention flagged as future capability (clm-014)
- [Agent governance + MCP integration patterns, 2026-10](library/agent-governance-mcp-integration-2026-10.md) — procured 2026-10-19: MCP roadmap priorities, governance convergence with house shape; standing beat unchanged both conditions
- [Harness benchmarking A/B bench](domains/harness-benchmarking.md) — 2026-10-12 spike: vanilla arm via CLAUDE_CONFIG_DIR sandbox (env+model only), 6-task battery, headless claude -p; harness tax ~8x in-tok constant / 7.2x→1.7x wall as tasks amortize; KB task = the discriminator (vanilla hallucinated "7 tasks", full 2/2 with doc citation); artifacts bench/harness-ab/
- [Machine health: OOM postmortem](domains/machine-health.md) — 2026-10-16 crash: kb.mcp_server loads a 3.4GB index copy PER session (13 loaded ≈ 45GB) + kb.sync runaway hit 35GB; killed 42 stale sessions + TERM'd runaway, swap 30→10GB; structural fix = attach sessions to shared kb.daemon
- [Harness Dashboards MCP](projects/harness-dashboards-mcp.md) — 12-tool read-only remote MCP (GCS snapshot + FastMCP Cloud Run) feeding claude.ai Dashboards; hourly launchd sync; remaining = Josh OAuth client + connector registration
- [projects/salesforce-mcp.md](projects/salesforce-mcp.md) — SFDC picklist MCP deps (67195423/24/25); BSYS-29657 Lead 404 burst fix; UI-API NOT_FOUND semantics
- [Estate fusion audit + 5-phase build](reports/estate-fusion-audit-2026-10-13.md) — 3-model audit + PRICEBOOK/CLOSER/FIXLOOP/REAPER/SKILLCULL all built+verified; Fireworks card canonical for cost
- [Headless write path](domains/headless-write-path.md) — built-in sensitive-file gate denies knowledge-tree Write/Edit to headless lanes; --add-dir fix shape, owners, and the stdout-fence rescue convention as documented default
- [Managed Agents policy watch](domains/managed-agents-policy-watch.md) — GA-watch + liability register: which client-side governance rules deprecate when Managed Agents policies go GA on MCP tools; prod-write gate ports first
- [Slack native MCP recon](domains/slack-native-mcp-recon.md) — 2026-10-14 recon of Slack's OFFICIAL MCP (mcp.slack.com): endpoint/input/response shapes as the reference implementation for our slack-workato drafts.create surface; missions: formatted drafts in CC + copy shapes into ours
- [Knowledge corpus export](projects/knowledge-corpus.md) — team-shared brain export: v1 LIVE 2026-10-15 (org repo pushed, weekly job scheduled)
- [AIRO PM feedback list](projects/airo-pm-feedback-2026-10.md) — 2026-10-14 resliced issue list for the [colleague] sync; [AIRO] segmentation routes to [colleague] vs [colleague]
- [AIRO issue filing package](projects/airo-pm-filing-package-2026-10-15.md) — 2026-10-15 ticket-ready specs for the 12 [AIRO] items DM'd to [colleague] (source: airo-pm-feedback-2026-10.md; evidence: airo-mcp-playbook/)
- [BSYS-25529 builder enablement](projects/bsys-25529-builder-enablement.md) — Story in epic BSYS-25523; plan 2026-10-09, Phase A built 2026-10-10, updated plan 2026-10-11 (Jira comments 1134769/1134807/1134967); gated by BSYS-25526 platform procurement
- [Harness Atlas](harness-graph/) — 3D harness map v14 (single organism, 8 organ tiers, KB mycelium) at localhost:8770; public site daily 06:15 to jcramoywkto.github.io/harness-atlas; version history in the holding file + repo
- [AI-Asset-Registry](projects/ai-asset-registry.md) — Workato internal Claude/Codex plugin marketplace repo (Workato-All/AI-Asset-Registry): paired org/<name>-claude + org/<name>-chatgpt convention, both marketplaces to update, .app.json only for MCP-bound apps; first asset official-workato-brand-guidelines (PR #13, 2026-10-20)
- [Frontify MCP](projects/frontify-mcp.md) — build our own Frontify MCP (Josh 2026-10-20): read MCP over Platform GraphQL, reusing conn 22276219; full introspected schema in repo
- [Jira/Confluence REST wrapper](scripts/jira.py) — headless-safe CLI replacing the auth-fragile Atlassian MCP path; read-back verify on every write; born from the 2026-10-21 consent-page 429 outage
- [NYC customer talk](projects/nyc-customer-talk.md) — agentic-journey talk deck + HTML artifact, DONE 2026-10-21; image-based deck export workflow; Josh-approved
- [Workato Developer API Semantic MCP](../../orca/projects/dev-api-mcp/SPEC.md) — BUILT 2026-10-22 (BSYS-29894): 3-tool semantic gateway for the Workato management API, registry 332 endpoints; Phase 6 spec Josh-approved 2026-10-25; NEEDS-JOSH: dedicated API client token
- [Jev replica + verdict-state layer](scripts/triage-state.py) — 2026-10-23/24 four backtests settled the design: ensembles dead, state +10pts, precedent retrieval +37pts, LLM urgency dead; live wiring on triage cards; order-never-filter stands; primer: domains/decisions-judgment.md
- [SG lunch-and-learn brief](projects/sg-lunch-learn.md) — harness story fusion brief 2026-10-25; deck build pending Josh approval
