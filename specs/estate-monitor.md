# Spec: Estate Monitor — estate-wide Workato monitoring platform

- **Slug**: `estate-monitor` (no ticket key yet; file one if this becomes a BSYS Story)
- **Written**: 2026-10-11 by spec-distiller, from live-investigation facts supplied by the main session
- **Spec gate**: the builder MUST cite this file in its report; `~/.claude/knowledge/scripts/spec-score.py` runs against it post-build. Criteria keep exact nouns (recipe names, table names, key prefixes, project IDs) so scoring is mechanical.
- **Environment**: DEV ONLY at launch (workspace 3535597). Prod is a later, separately-approved promotion.

## Goal

One net-new, configuration-driven Workato monitoring system that watches any enrolled project/folder for failures, stop/starts, bursts, outages, degradation, and handled exceptions — with Slack alerting, recovery detection, full audit trail, and a deploy-time enrollment row — so per-app monitors are never hand-built again.

## Scope

**IN**
- New dedicated `Estate Monitor` project in dev (owned by no app).
- RecipeOps workspace-event ingestion gated by explicit Scope rows (project/folder ID + Slack channel).
- Error monitoring, error thresholds, recovery monitoring for error bursts AND service outages, stop/start notifications, service degradation, handled-exception monitoring with thresholds.
- All knobs in project properties + data tables; reporting (digest) and auditability (append-only tables).
- Seed scope rows for the three known dev projects (below).
- Lifecycle manifest assembled during the build (promotion-orchestrator/manifest-hygiene pattern: every asset recorded with name, type, folder path).

**OUT**
- Touching, replacing, or disabling ANY existing monitor (Event360 family, BSYS-29503 observability monitor, HR Genie / Multi-Genie alerting). Parity window first; retirement is a later decision.
- Auto-enrollment of projects (Josh locked: explicit scope rows only, carried by deploy checklist).
- Production deployment, prod scope rows, prod Slack channels.
- Harness-side (launchd/Claude) monitoring changes — `workato-health.py`, watchdog agent, estate-architect stay as-is.
- Remediation/auto-restart of failed monitored recipes. Estate Monitor observes and notifies; it never mutates monitored assets.

## Acceptance criteria

- [ ] A dev project named `Estate Monitor` exists, containing every asset built under this spec, and nothing else it doesn't own.
- [ ] Data tables `EM | Monitor Scope`, `EM | Signal Ledger`, `EM | Incident State`, `EM | Monitored Recipes`, `EM | Audit Log` exist with the columns in the schema section (or a `## Revision`-logged equivalent).
- [ ] Project properties exist for environment label, master enable, and global default thresholds (names per Configuration Model).
- [ ] Scope rows exist for dev projects 14570285 (Event360), 17923915 (Multi-Genie), and 15643451 (HR Genie), each with a `Slack_Channel_ID` and `Enabled = true`.
- [ ] Stopping a seeded dev recipe manually produces exactly one open `recipe_stop_user|Development|<recipe_id>` incident in `EM | Incident State` and one Slack post to that scope's channel carrying the `[DEVELOPMENT]` label.
- [ ] Restarting that recipe sets `Status = resolved`, `Resolved at`, and `Recovery notified at` on the same incident row BEFORE the green recovery post appears (claim-first ordering provable from timestamps/job trace).
- [ ] A failed job in a seeded recipe produces a `recipe_failed|Development|<recipe_id>` incident and a Slack post; a second failure of the same recipe increments `Occurrence count` instead of opening a duplicate incident.
- [ ] N failures (N = scope's `Error_Burst_Threshold`) inside the scope's window produce exactly one `error_burst|Development|<recipe_id>` incident, not N posts.
- [ ] A handled (caught) exception signal increments the handled-exception counter and alerts only when `Handled_Exception_Threshold` is crossed — a single handled exception posts nothing.
- [ ] Setting a scope row's `Enabled = false` silences all posts for that scope while signal/audit rows continue to be written (observability intact, delivery gated).
- [ ] Setting the master-enable project property to false silences the entire system without stopping any recipe.
- [ ] No signal row, incident row, Slack message, or audit row contains lead PII or raw payloads (spot-check of at least one burst incident trace).
- [ ] Every notification-outcome transition (routed, failed, retried, recovery-notified) has a corresponding `EM | Audit Log` row with Job ID.
- [ ] The daily digest recipe posts one summary per enabled scope channel listing open incidents and resolved-in-window counts.
- [ ] A manifest file (or build-ledger section) lists every created asset with name, type, folder path, and recipe/table ID — ready for manifest-hygiene dry-run.
- [ ] Estate Monitor's own recipes are NOT enrolled as a monitored scope (no self-monitoring loop); a failure of the router leaves signals unrouted but intact (fail-open, mark-routed-after-delivery).

## Architecture

Components (all in the new Estate Monitor project, dev):

1. **Scope/config layer** — `EM | Monitor Scope` table + project properties. Read at gate time by every recipe; no literals anywhere.
2. **Ingest** — RecipeOps-triggered recipes translating workspace events into privacy-safe Signal Ledger rows, gated by scope.
3. **Router/dedupe** — realtime trigger on new signal rows; stable incident keys; Incident State upsert; dispatch.
4. **Notifier** — Workbot for Slack posts, environment-coded `[DEVELOPMENT]` label, channel from scope row, contained failure (retry + log-only catch, monitoring fails open).
5. **Evaluators** — 5-min-scheduled threshold/burst/degradation evaluators reading the ledger with bounded pages.
6. **Recovery** — start-event hook resolving open stop/burst/outage incidents claim-first, then green post.
7. **Registry** — dynamic `monitored_recipe|Development|<recipe_id>` upsert on start, inactive on stop (Event360 pattern).
8. **Reporting/audit** — daily digest recipe + append-only audit rows from every mutating step.

```mermaid
flowchart LR
  subgraph Monitored estate
    R1[Event360 dev 14570285] 
    R2[Multi-Genie dev 17923915]
    R3[HR Genie dev 15643451]
  end
  RO[RecipeOps triggers<br/>start/stop/fail/conn events] --> GATE{Scope gate<br/>EM | Monitor Scope}
  R1 & R2 & R3 -.events.- RO
  GATE -->|in scope| SL[(EM | Signal Ledger<br/>append-only)]
  GATE -->|out of scope| DROP[(drop, no row)]
  SL --> ROUTER[EM | RT Signal Router<br/>dedupe by incident key]
  ROUTER --> IS[(EM | Incident State)]
  ROUTER --> DISP[EM | Slack Dispatcher<br/>Workbot, env-coded]
  DISP --> SLACK[(scope Slack channel)]
  EVAL[EM | Threshold Evaluator<br/>5-min scheduler] -->|bounded pages| SL
  EVAL --> IS
  PROBE[EM | Degradation Probe<br/>5-min scheduler] --> IS
  REC[EM | Recovery hook<br/>on recipe-start signals] -->|claim-first resolve| IS
  REC --> DISP
  REG[EM | Registry sync] --> MR[(EM | Monitored Recipes)]
  DIG[EM | Daily Digest] --> IS
  DIG --> SLACK
  ROUTER & EVAL & PROBE & REC & DISP --> AUD[(EM | Audit Log)]
  PROPS[Project properties<br/>env label, master enable, defaults] -.-> GATE & ROUTER & EVAL
```

## Data-table schemas (proposed columns)

**`EM | Monitor Scope`** — Scope key (string, unique: `scope|<env>|<project_or_folder_id>`), Environment (string), Scope type (string: `project`|`folder`), Scope ID (string), Slack_Channel_ID (string), Enabled (boolean), Error_Burst_Threshold (integer), Error_Burst_Window_Min (integer), Handled_Exception_Threshold (integer), Degradation_Enabled (boolean), Recovery_Notify (boolean), Notes (string), Created at (date_time), Created by (string).

**`EM | Signal Ledger`** (append-only, high volume) — Signal ID (string), Received at (date_time), Environment (string), Scope key (string), Signal type (string: `recipe_started`|`recipe_stopped_user`|`recipe_failed`|`conn_disconnected`|`conn_refresh_failure`|`handled_exception`|`burst_eval`|`degradation_probe`), Recipe ID (string), Recipe name (string), Job ID (string), Error class (string), Error summary redacted (string), Routed (boolean), Routed at (date_time).

**`EM | Incident State`** — Incident key (string, unique), Environment (string), Scope key (string), Incident type (string), Recipe ID (string), Status (string: `open`|`resolved`|`suppressed`), Opened at (date_time), Occurrence count (integer), Last occurrence at (date_time), Resolved at (date_time), Recovery notified at (date_time), Notification status (string), Notification attempts (integer), Notification error (string), Suppressed until (date_time).

**`EM | Monitored Recipes`** — Registry key (string, unique: `monitored_recipe|<env>|<recipe_id>`), Scope key (string), Recipe ID (string), Recipe name (string), Active (boolean), Last start at (date_time), Last stop at (date_time).

**`EM | Audit Log`** (append-only) — Audit ID (string), At (date_time), Actor recipe (string), Action (string), Entity type (string), Entity key (string), Detail (string, redacted), Job ID (string).

## Recipe inventory

| Name | Trigger | Responsibility |
|---|---|---|
| `EM | INGEST | Workspace Events` | RecipeOps: recipe started / stopped by user / failed; connection disconnected / refresh failure | Scope-gate by Scope row, append privacy-safe Signal Ledger row, audit row |
| `EM | RT | Signal Router` | New rows in Signal Ledger (realtime) | Dedupe into Incident State by stable key, occurrence counts, call dispatcher, mark routed only after delivery |
| `EM | NOTIFY | Slack Dispatcher` | Recipe function (called by router/evaluators/recovery) | Workbot post with `[DEVELOPMENT]` label, channel from scope row, retry + log-only catch, write audit |
| `EM | EVAL | Threshold Evaluator` | Scheduler, 5 min (platform minimum) | Bounded-page ledger scan; open `error_burst` / handled-exception incidents on actionable aggregate evidence only |
| `EM | PROBE | Service Degradation` | Scheduler, 5 min | Connection-health / error-rate probe per scope; outage incidents + evidence-based all-clear recovery |
| `EM | RECOVERY | Start Hook` | On `recipe_started` signals | Resolve open `recipe_stop_user|` incidents for that recipe claim-first, then green recovery post; never resolve per-job incidents on restart |
| `EM | REG | Registry Sync` | On start/stop signals | Upsert/mark-inactive `EM | Monitored Recipes` rows |
| `EM | REPORT | Daily Digest` | Scheduler, daily | Per-scope open/resolved counts + top offenders to scope channel |

**[PROPOSED-UNVERIFIED]**: folding REG into INGEST and RECOVERY into the router are both viable; keeping them separate matches the Event360 blast-radius lesson (one layer per failure domain). Builder may consolidate only with a `## Revision` note.

## Configuration model

**Project properties** (global, env-scoped, promote-safe): `EM.Environment` (label source; dev value `Development`), `EM.MasterEnable` (kill switch), `EM.DefaultSlackChannelID`, `EM.DefaultErrorBurstThreshold`, `EM.DefaultErrorBurstWindowMin`, `EM.DefaultHandledExceptionThreshold`, `EM.SuppressRepeatMinutes` (dedupe window).

**Data tables** (per-scope, business-owned, editable without redeploy): everything in `EM | Monitor Scope`. Per-scope blank threshold = inherit project-property default (resolution order: scope row → property → hard fail-safe of no alert).

Asset IDs come from `job_context` only; environment label from property only — never literals (the env-stamp and dev-ID-in-prod defect classes are the failure modes this prevents).

## Incident-key taxonomy

`recipe_failed|<env>|<recipe_id>` · `recipe_stop_user|<env>|<recipe_id>` · `error_burst|<env>|<recipe_id>` · `handled_exception|<env>|<recipe_id>|<error_class>` · `conn_disconnected|<env>|<connection_id>` · `conn_refresh_failure|<env>|<connection_id>` · `service_outage|<env>|<scope_key>`. Recovery-by-restart resolves ONLY `recipe_stop_user|` (plus evaluator-declared all-clear for `error_burst` / `service_outage`); never `recipe_failed` or per-job keys.

## Threshold semantics

- Burst = `Error_Burst_Threshold` `recipe_failed` signals for one recipe inside `Error_Burst_Window_Min` → ONE incident with occurrence count; repeat posts suppressed for `SuppressRepeatMinutes` while count accrues.
- Handled exceptions accrue silently per recipe+class; alert only at `Handled_Exception_Threshold` per window.
- Evaluator reads use bounded pages (1,000-row selectors are page caps, never dataset limits) and positive active-state allowlists for stuck detection — no negative terminal exclusions.
- Batch writes for high-volume signal rows; atomic single writes for claims/transitions.

## Recovery semantics

On `recipe_started`: search Incident State for open incidents with that Recipe ID and key prefix `recipe_stop_user|`; resolve FIRST (durable claim: Status + Resolved at), THEN post green recovery and set Recovery notified at. Idempotent by claim-first ordering. Burst/outage recovery is evaluator-declared (evidence of clean window), never restart-implied.

## Reporting / audit design

- Daily digest per enabled scope channel: open incidents, resolved-in-window, top offenders by occurrence count.
- Every state transition and notification attempt writes an `EM | Audit Log` row with Job ID — the audit trail is queryable by entity key without touching job history.
- Signal Ledger and Audit Log are append-only; retention/purge is an OPEN QUESTION below (no deletes in v1).

## Seeding plan (dev)

1. Scope row: project `14570285` (Event360 dev) → monitor Slack channel.
2. Scope row: project `17923915` (Multi-Genie dev).
3. Scope row: project `15643451` (HR Genie dev).
4. All three with default thresholds from project properties; verify gate recognition with one forced stop/start each.

## Build order (parallelizable slices)

- **Slice 0 (serial)**: project shell, five data tables, project properties. Gate for everything.
- **Slice A**: INGEST + Signal Router + Dispatcher (core path) — depends on 0.
- **Slice B**: Threshold Evaluator + Degradation Probe — depends on 0 only; parallel with A.
- **Slice C**: Recovery Hook + Registry Sync — depends on A (dispatcher).
- **Slice D**: Daily Digest + audit polish — depends on A.
- **Slice E (serial)**: seeding, UAT below, manifest assembly.

## UAT plan (dev, stop→test→observe→start, never wait for schedules)

Per acceptance criteria: forced manual stop/start of one seeded recipe (stop post → restart green recovery, claim-first timestamps); induced failure → dedupe on second failure; induced N-failure burst → single burst incident; one handled exception → silence, threshold-crossing → alert; `Enabled=false` → silent scope with intact ledger; master-enable=false → total silence; digest dry-run; PII spot-check; audit-row join check; router-kill fail-open check (signals unrouted but present).

## Manifest strategy

Assemble during the build per promotion-orchestrator/manifest-hygiene: a running manifest doc (name, type, folder path, ID per asset) updated at each slice close; manifest-hygiene dry-run before any future promotion story. Prod promotion is NOT part of this spec.

## Risks

- **Monitor self-loop**: Estate Monitor observing itself → recursion/storm. Mitigate: never seed its own project; hard exclude in scope gate. Early warning: incident keys with EM recipe IDs.
- **RecipeOps event storm** on mass stop/start (deploy imports) → router backlog. Mitigate: dedupe + suppression window; enumerate and bound backlog before restart. Early warning: ledger growth rate spike.
- **AIRO `ruby()` formula whitelist rejects `Date.new`** — use approved date idioms.
- **`data_table_update` wipes populated tables** — never mutate schema post-seed; create versioned tables instead.
- **Dynamic table_id on writes silently drops parameters** — static table bindings only.
- **Scheduler minimum 5 minutes** — degradation/burst latency floor; do not promise faster.
- **RecipeOps start can silently no-op** — verify running flag after every start.
- **Recipe exports show sample values** — never trust exports for mappings; verify in live reads.
- **Deploy imports leave overwritten RUNNING recipes STOPPED** — post-import restart step is mandatory (later, at promotion).
- **Monitor failure masks estate failure** — monitoring fails open (log-only catch), and the harness-side `workato-health.py` layer remains the meta-observer.
- **Duplicate alerting with existing per-app monitors during parity window** — expected and accepted (Josh's call); document overlap in the digest.

## Design gate (checked 2026-10-11)

- `domains/workato-platform.md` — owned-asset health monitoring (asset-fingerprint.py + workato-health.py hourly launchd sweep, alarms→triage): harness-side layer, no in-platform Slack/incident state — complements, does not cover. BSYS-29503 observability monitor: an existing per-app monitor — pattern source (burst thresholds, capped_read_alert), do not touch.
- `agents/estate-architect.md` — weekly advisory architecture review, no alerting. Ruled out as coverage.
- `agents/workato-watchdog.md` — nightly report-only autopsy/connection sweep. Ruled out (report-only, not realtime).
- `domains/frontier-stack.md` — Estate Twin is an offline snapshot twin for QA/chaos, not live monitoring. Ruled out.
- Event360 monitor family (prod folder 35283756, dev 33036555) — THE reuse pattern: RecipeOps triggers, scope gate, Signal Ledger, Incident State (31 cols), env-coded Workbot posts, dynamic registration, claim-first recovery hook.
- `promotion-orchestrator` + `manifest-hygiene` skills — manifest assembly pattern for the standing manifest order.
- `slack-bot-connection` skill — governed bot-connection path for dispatcher posts.
- Fleet schedules (`com.josh.*` launchd jobs) — Claude-side, distinct layer; no schedule collisions at 5-min Workato cadence.
- Claims ledger (`knowledge/claims/claims.jsonl`) — no standing claims conflict with this build.
- `specs/env-diff-promotion-tracking.md` — drift/change-tracking spec, different concern; no overlap.
- Conclusion: no existing in-platform estate-wide monitor; net-new build confirmed as Josh directed.

## Open questions (batched for Josh)

1. **Meta-alert channel**: where does Estate Monitor report its OWN failures (dispatcher dead, ledger write failures)? Recommend: the same dev monitor channel used for seeding, via audit-row-driven digest flag rather than realtime posts.
2. **Ledger retention**: Signal Ledger grows unboundedly. Recommend: v1 no deletes; v2 30-day rolling purge recipe. Confirm retention target.
3. **Digest time**: recommend daily 08:00 local per scope channel. Confirm.
4. **HR Genie seeding**: knowledge shows multiple dev projects (15643451 primary, others exist). Recommend seeding 15643451 only at launch. Confirm.
