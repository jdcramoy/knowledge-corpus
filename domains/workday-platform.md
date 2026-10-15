# Workday Platform — domain knowledge

Project-scoped Workday build knowledge. The WSDL/SOAP and WQL PROCEDURES are
global skills (workday-wsdl-lookup, wql-query-builder) — always use those
instead of touching raw WSDL files.

## Key facts

- Workday MCP (end-user): employee/manager self-service only — every request
  scoped to the signed-in user (worker=me); managers limited to direct
  reports. Consolidated Approval runs the parent business-process operation
  atomically; never expose internal task/event/child WIDs.
- Workday SOAP: Human_Resources / Staffing / Compensation / Payroll
  namespaces; operation lookups via the pre-built JSON index (skill) — raw
  .wsdl/.xsd files are too large to read directly.
- WQL: data-source discovery first (field/filter inspection), then query;
  delivery format per requester.
- Workday tools: ~/Documents/Workday/tools/workato-dev.py — portable CLI
  wrapper for routine inspection + explicit lifecycle actions.

## Project state pointers

- Workday End-User MCP skill intake: Workday-Development repo
  `docs/workday/project-memory/WORKDAY-MCP-SKILL-STAGING.md` — gated staging
  for the future `workday-mcp-playbook` skill; findings enter there with
  evidence, skill is created only at ≥5 PROMOTABLE entries (or repeat
  incident). All Workday-MCP sessions must feed it.
- Workday Development project: ~/.claude/projects/-Users-<user>-orca-workspaces-workbench-Workday-Development/memory/
- Payment-election security requirements: ~/Documents/Claude/workday-payment-election-security-requirements.md

## End-user WQL authorization gap (confirmed 2026-10-02)

- End-user (VUA OAuth) principals get `HTTP 403 {"error":"permission
  denied","code":"S22","severity":"Critical"}` on the WQL report API
  (data source `allBusinessProcessTransactionsAwaitingPersons`) even
  though REST `Get_Worker(worker=me)` and `Get_Inbox_Tasks` succeed, and
  the same query succeeds under the ISU connection. Tenant security-
  domain grant gap; blocks BSYS-28312 (BP approval status) and is the
  same class as BSYS-26817 (`Get_Calculated_Time_Blocks`). Grant request
  raised with the Workday admin 2026-10-02; on hold until 2026-10-03.
  If the answer is "WQL is ISU-only by design", the fallback is a
  brokered fixed-identity read — which weakens the caller-scoped AC3
  model, so confirm before redesigning.

## WQL `allWorkers` carries leave status directly (2026-10-05, BTSUP-72246)

- `allWorkers` (ISU-accessible) exposes `onLeave` (boolean), `firstDayOfLeave`,
  `estimatedLastDayOfLeave`, `email_PrimaryWork` (validated live:
  `SELECT worker, email_PrimaryWork FROM allWorkers WHERE email_PrimaryWork = 'x'`
  returns the worker WID in `worker.id`). This makes "is this worker on leave
  today/soon" answerable with ONE WQL query — no dedicated LOA source needed.
- The dedicated leave WQL sources (`leaveOfAbsenceOutstandingByDateRange`,
  `leaveOfAbsenceRequests`, `leaveOfAbsenceByEstimatedLastDayOfLeave`,
  `allTimeOffs`, `topLevelOrganizationsAndSubordinates`) are all "inaccessible"
  to the BT ISU (exists-but-no-security-domain) — don't burn probes on them;
  use allWorkers fields instead. (Consistent with the RDDS ISU-inaccessibility
  pattern below.)
- Future-dated approved leaves don't flag `onLeave` until the start date —
  lookahead booleans only cover workers already on leave.
- Email-filtered allWorkers WQL is the clean email→WID resolution path
  (better than REST get_staffing_worker: one call, no 19s staffing latency).

## Business Process REST API (2026-10-05, BSYS-28312) — the right way to read BP status

- Base: `https://{host}/api/businessProcess/v1/{tenant}`. Endpoints: `GET /events/{id}`,
  `/events/{id}/inProgressSteps`, `/completedSteps` (past approvers via
  `completedByPerson`), `/remainingSteps` (ordered future chain),
  `GET /events?worker=`/`?initiator=` (self-scoped discovery; requires one of the two).
- **User-scoped natively**: a caller-invisible event returns HTTP 404 `not found` (code S21) —
  no existence leak. Works under the end-user OAuth identity (Workato VUA REST connection).
  This beats WQL `allBusinessProcessTransactionsAwaitingPersons` (current-awaiting only, ISU
  grant problem) and the SOAP Get_Event_Details (Workato's SOAP adhoc action fails start
  validation with hidden `account_id: can't be blank` on the SOAP connection).
- Workato plumbing: `workday_rest.__adhoc_http_action` with ABSOLUTE URL + declared `output`
  schema resolves pills cleanly; use path-bound `ruby(to_json)` for array outputs.

## Worker-scoped BP events via the native adapter action (2026-10-05, BSYS-28312)

- The workday_rest adapter ships `get_business_process_events(worker=<wid>,
  limit=)` — worker-scoped BP event discovery with a compiled output schema
  (id, descriptor, status, for, overallBusinessProcess, initiator, dueDate,
  subBusinessProcesses). Under a VUA connection it returns only the events the
  CALLER can see (native scoping preserved) — verified: Josh's identity
  returned the subject's 12 events including a live Promotion comp change.
- This is the replacement for a raw `/events?worker=` adhoc GET when a
  downstream step must reference pills (the adhoc schema-designer output never
  compiles for NEW mnemonics — see workato-platform notes).
- Resolver token-matching lesson (BSYS-28312): business-process-type filters
  must match TOKENS, not substrings — "Request Compensation Change" does not
  substring-match "Compensation Change: Libby Alden"; strip stopwords
  ("request", "status", …) and require all remaining tokens to appear.

## Dual SOAP+REST custom SDK connector spike (2026-10-08, research)

- **Workato schedule floor = 5 minutes** (docs: "The minimum supported interval is
  five minutes" — Scheduler trigger AND polling triggers). Staggered 5-min crons
  are the platform floor, not a design flaw; NO connector/poll arrangement beats
  it via schedule. Sub-5-min latency requires Workday-side push.
- **Workday has NO native outbound webhooks.** Push options: (1) Outbound Message
  Services (Studio integration on BP event; data-sparse, follow-up query needed);
  (2) Workday Orchestrate — Orchestration Service step in a BP definition, or
  auto-launch on Cancel/Rescind/Correct/Deny; its Send API Request component can
  POST to any external URL (e.g. a Workato webhook trigger). Orchestrate is a
  paid module — license unknown in BT tenant.
- **SDK hybrid trigger** = webhook signal + poll pull; webhook payload is
  DISCARDED in favor of fresh poll data, dedup keys defined on poll output.
  The safe pattern for Workday push (no payload trust, self-healing gaps).
- **MCP VUA requires OAuth 2.0 authorization-code-grant connections**; custom SDK
  connections qualify (Workday registered API client auth-code+refresh works).
  Constraints: no long actions, only first-level recipe functions, end users
  auth via Workato Identity. Skills recipes select "End user's connection" per action.
- SDK actions can speak SOAP (XML POST w/ custom content-type) and REST in ONE
  connector — dual-transport is a documented pattern (Sage Intacct example).
  One connector + one shared connection = all MCP skill recipes, killing the
  multi-connection auth sprawl. New skill = new named action in the connector.
- Per-user event polling source: `GET /workers/me/inboxTasks` (self-scoped,
  VUA-native) — one recipe per user's inbox stream; dedup on task ID.
  Tenant-wide `GET /events` requires worker or initiator param (no global stream).
- **VERDICT (Josh, 2026-10-08): NOT building it.** BT tenant has no Orchestrate
  → sub-5-min listening is impossible regardless, and native Workday
  SOAP+REST connectors already cover the access under VUA. Custom connector's
  only residue = named schema'd actions + merging 2 connections into 1 —
  convenience, not capability. Do not re-propose without a NEW driver
  (e.g. Orchestrate/Extend license, or per-action schema needs the native
  adhoc actions can't satisfy).
- **The 5-min floor is PER-RECIPE, not per-system** (Josh's live hack,
  2026-10-08): duplicate the polling recipe N times with minute-stamp offsets
  (0/1/2/3 min) → effective N/5-minute granularity without Workday-side push.
  This is ALREADY PRODUCTION ARCHITECTURE in HR Genie — the 4 Vegas Demo
  Cadence lanes (Inbox Task Discovery Hub + Time-Off Event Hub, offsets 1–4m)
  run permanently for 1-minute notification latency.
- **Dedup is ALREADY externalized in HR Genie** — shared ledger tables (Inbox
  Task Notification Log 132894, BP Completion Notification Log 155278, PTO
  ledgers) with event-level dedup + SKIPPED_DUPLICATE, log-before-send, plus a
  CLAIMS TABLE to serialize overlapping jobs (the Workato overlap race). The
  per-recipe trigger-dedup caveat does NOT apply: lanes converge on the shared
  ledger. Delivery-state-not-truth doctrine: every retry/reminder/close-out
  re-checks Workday live. Full model: knowledge/projects/hr-genie.md +
  Confluence "Proactive Notifications and Lifecycle Tracking" (2939650050).

## timeOffByDateTaken facts that decide OOO disputes (2026-10-06 probe, BTSUP-72246)

- **The source carries ONLY committed absence rows.** ±7d probe (all orgs,
  NO approval filter, `unitsApproved/unitsPending/unitsDenied` selected):
  employees with APPROVED time off appear with per-day rows + their original
  `approvalDate`; employees whose time off is still in approval workflow do
  NOT appear at all (not even with `unitsPending > 0` — while OTHER workers'
  pending rows DO appear in the same window, 12 of 304 rows, so pending
  rows exist for requests that have reached commitment). Net: **no rows for
  a person = their absence request never reached Workday's absence engine
  (or was never entered)** — Slack status alone proves nothing.
- **get_wql_report page cap = 200 rows** (count=1000 requested → 200/page);
  paginate via `page` for bigger windows. Tenant-wide timeOffByDateTaken
  REQUIRES the `(organizations = (...))` prompt — queries without it fail
  with "Parms are required... Provide a value for the prompt".

## Legacy-tree mining (2026-10-10) — absorbed from ~/Documents/Claude

**Payment-election security grants (BSYS-26812/14/17 class) — the actual admin spec** (source: workday-payment-election-security-requirements.md, now absorbed here):
- Domain security policies `Worker Data: Payroll (Payment Elections)` (+ the Payroll Interface variant) need **Get AND Put** for security group **`Employee as Self`**.
- Write additionally needs the **`Payment Election Enrollment Event`** business-process security policy permitting `Employee as Self` on the **`Manage Payment Elections`** initiating action; then "Activate Pending Security Policy Changes".
- Explicit do-NOT-grant list of 5 admin-only domains (in source file).
- Known risk: `Get_Payment_Election_Enrollments` / `Submit_Payment_Election_Enrollment` may be integration-only — verify via the in-tenant "View Security for Securable Item" report; if not grantable to Employee as Self, per-employee OAuth must be replaced with a constrained ISU.
- Live blocker error signature: "The task submitted is not authorized" = missing grant, not a code bug.

**BSYS-27874 gotchas (not previously in the tree):**
- Workday SOAP `Search_business_object` worker-scoping SILENTLY DROPS unless BOTH `FieldsWithMultipleValues=["Request_References/Worker_Reference__ref"]` AND `FieldsWithAttributes=["Request_References/Worker_Reference"]` are set — unscoped queries return the tenant default (CEO, Employee_ID 1) with NO error (caused a real misattribution incident). Standing rules: worker-scoped searches need an integrity guard (WID must match requested; hard-fail or skip, never fall through) and downstream checks must be ALLOWLIST, not blocklist (`!= 'UNRESOLVED'` treats new failure states as resolved).
- Email resolution: SOAP `Search_business_object` → `Worker_Data.User_ID` is ~100% populated; REST `get_worker`'s `primaryWorkEmail` is unreliable (only when flagged primary).
- REST `get_business_process_events` has a permanent structural coverage gap for ≥4 BP types (Tax Election Change, Personal Information Change, Job Change/Data Change, Verify Personal Info) — raw `GET /workers/{id}/inboxTasks` returns empty-not-403 (permission-gap shape); WQL via `allBusinessProcessTransactionsAwaitingPersons` is the fix. Canonical statement of the REST-vs-WQL coverage boundary.
- WQL performance rule: `worker` is INDEXED in `allBusinessProcessTransactionsAwaitingPersons` (0.62s) while `businessProcessType` is NOT (minutes) — never filter WQL by type; fetch unfiltered/`dateInitiated` and filter in-recipe. Also `eventRecordsAwaitingAction[].id` == the REST step/inbox-task id; `page` rejects formulas — pagination must be literal page blocks.
- Ruby date_time coercion: a `date_time`-typed datapill (e.g. Workday `creationDate`) becomes a real Ruby Time object at runtime — `.split('T')` fails with "no method 'split' for <timestamp>"; use `.strftime('%Y-%m-%d')`. Sandbox also lacks `Time.parse`/`.iso8601` (use `now`/`today`, not `Time.now`/`Date.today`).
- AIRO `set_condition` operand enum lacks `>=`/`<=` — sidestep via `ruby(... ternary ? 'true':'false')` compared `equals_to "true"`.



## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Knowledge bases versus skills](../../kb-corpus/docs/en/agentic/agent-studio/knowledge-bases-vs-skills.md)
- [MCP Monday: Workday End User, Databricks Data Explorer, and Twitter/X Are Live](../../kb-corpus/changelog/mcp-monday-workday-end-user-databricks-data-explorer-and-twitter-x-are-live.md)
- [MCP Monday: The Content Creation Stack Gets an Enterprise Brain](../../kb-corpus/changelog/mcp-monday-the-content-creation-stack-gets-an-enterprise-brain.md)
- [MCP Monday: Content Ops, Minus the Admin Panel](../../kb-corpus/changelog/mcp-monday-content-ops-minus-the-admin-panel.md)
<!-- kb-bridges:end -->

## Workday developer-site corpus in the KB (built 2026-10-15)

- developer.workday.com is AI-agent-native: `robots.txt` points at
  `/llms.txt` (curated index). All docs render as Markdown at
  `/doc/{docId}.md`. REST specs + per-service changelogs are public JSON at
  `/bundles/rest-directory-ui/public/static/openApiFiles/<specFilePath>` —
  specFilePath values come from `services_oas3.json` (127 services × 4 tiers:
  production/preview/experimental/archived). SOAP explorer serves numbered
  snapshots `soap_services.175.json` (current; .176+ 404) — operation NAMES
  only; field-level SOAP detail stays in the workday-wsdl-lookup index. Graph
  API is self-contained: GraphQL `schema.txt` under bundles/graphql-changelog.
- All of it ingests as the `workday` KB source (`kb/workday_source.py`,
  nightly core step): 1,383 doc pages + 214 REST spec/changelog markdowns +
  111 SOAP service docs + Graph schema + tenant WQL alias export (992 data
  sources / 427K fields → one RAG doc per data source).
- Tenant WQL alias lookup DB (exact-match, fast):
  `~/.claude/knowledge/workday/wql-aliases.db` — tables `datasources`
  (ds_alias, ds_name) and `fields` (ds_alias, field, field_alias), indexes on
  both field columns. Source xlsx mirrored in corpus/workday/_raw/.
- Gotchas: developer.workday.com IGNORES If-None-Match (always 200 — full
  refetch nightly; sha-skip downstream); SPA URL patterns 307→/login, only
  401 "Token invalid" (e.g. /bundles/<file>) means the path exists but is
  gated — public static asset dirs (/public/static/) stay anonymous.
- fetch_all contract fix (kb/common.py 2026-10-15): results now returned in
  JOB order; as_completed ordering + positional zip had written the asor spec
  under the absenceManagement path in the workday source. Existing corpora
  audited clean (15/15 sha-match vs live) — uniform page sizes had kept them
  aligned by luck, not by contract.
