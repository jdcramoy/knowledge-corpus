# Insights Dashboards — Production Recreation Spec (captured 2026-10-11)

Purpose: exact recreation guide for Josh's HR Genie Workato Insights dashboards when the
intelligence platform promotion (BSYS-29498) executes. Everything below was read from the
DEV environment (org "Workato AHQ | AI", environment_id 3535597) via the dashboards' own
CrowQL APIs — chart definitions, series data, table rows, KPI values, and full query
bodies. Nothing was modified in dev; prod was not touched.

Evidence assets (same folder, `dashboard-doc-assets/`):
- `crowql-queries-all-boards-20261011.json` — all 76 CrowQL query bodies, verbatim (source of truth for every pane's query below).
- Screenshots: `operational-health-{top,mid,bottom}.png`, `adoption-{top,mid,bottom}.png`, `restricted-legacy-{top,mid,bottom}.png`, `product-facts-v2-{top,mid,bottom}.png`.

---

## 0. Platform mechanics (how these dashboards work — needed for recreation)

- Insights dashboards are identified by a **handle** (`idb-...`). Handles will differ in prod; recreate by content, not handle.
- Each widget fires one query: `POST /insights/crow-ql/api/v2/execute?source=standalone-dashboard` with body `{"query":{"id":"<query-uuid>"},"filters":[],"userTimezone":"America/New_York"}`. Query definitions are readable at `GET /insights/crow-ql/api/v2/queries/{id}`; dashboard filters at `GET /insights/crow-ql/api/v3/filters?id={id}`. All bodies are archived in the JSON asset above.
- Widgets render via Highcharts (outer `chart.type` is always `line`; the real type is the **series** type: `pie`, `column`, or `area`).
- Every query references tables by **UUID** (insights data-model id). UUIDs will NOT carry to prod — **all sources must be re-pointed by table NAME** (section 2).

### Source tables referenced (dev UUID → keep the NAME in prod)

| Table name (exact, recreate with this name) | Dev insights UUID | In promoted telemetry pipeline? |
|---|---|---|
| HR Genie \| MCP Tool Usage Events | `5c1e0b4e-edbc-40f9-af99-85e4b27f6094` | Feeder (App Event Ledger 156842 path) |
| HR Genie \| Handled Error Events | `0f01a0a9-885e-4baf-ac25-e85b8831ff76` | Feeder |
| HR Genie \| Deflection Outcome Events | `c0dc6d12-0bb0-446f-97f9-170af3590640` | Feeder |
| HR Genie \| Conversation Tool Execution Events | `de566e62-a2d4-4688-9162-3e1a8905fbbf` | Feeder |
| HR Genie \| Conversation Telemetry Classifications | `ab9ba380-7cba-472c-bbe5-c35f22a24308` | Feeder |
| HR Genie \| Intelligence Metrics | `4ff9aaa4-8b1a-4c5c-ae64-d0822644ffbc` | YES — pipeline table 156862 |
| HR Genie \| Telemetry Coverage State | `842f2639-5a98-4ef1-9fc2-c7cfbbca0475` | YES — pipeline table 156843 |
| HR Genie \| Knowledge Gap Queue | `fe2431ac-a939-4c43-b096-c8e1be0b9310` | Feeder |
| HR Genie Notification Assignment Facts | `6391da11-9887-4f61-aed2-07de24a93ba4` | Feeder (notification family) |
| HR Genie \| Product Metrics Daily v2 | `0b830b77-3788-4a6e-abdc-66c1695e80bf` | Downstream of pipeline (k≥10 rollup) |

(App Event Ledger 156842, Telemetry Collector State 156849, Topic Taxonomy 156850 are
pipeline tables not read directly by any pane; collectors read them.)

---

## 1. Dashboard inventory (5 found in dev)

| # | Title | Handle | Role |
|---|---|---|---|
| 1 | HR Genie — Operational Health · Development | `idb-Abrogbz8-Qhf8Ea-CD` | Primary — recreate in prod |
| 2 | HR Genie — Product Analytics · Restricted Legacy · Development | `idb-Abrntmt9-RYgtWH-CD` | KEEP THE "Restricted Legacy" LABEL (standing rule). Recreate only if history parity is wanted |
| 3 | HR Genie — Adoption, Outcomes & Intelligence · Development | `idb-Abrcwzdm-P9h39R-CD` | **Authoritative product-analytics board** — recreate in prod |
| 4 | HR Genie — Anonymous Product Facts v2 · Development | `idb-Abse8QCG-GLWTT9-CD` | This IS the handle the older note called "approved replacement" — exists and is live. Recreate in prod |
| 5 | HR Genie / Workday MCP · Development | `idb-AbpgHKW9-D9TseG-CD` | First-generation operational board (the "older pair in history"). Do NOT recreate; queries shared with boards 1/3 |

**Authoritative call:** Board 3 (Adoption, Outcomes & Intelligence) is the current
product-analytics surface; Board 4 (Anonymous Product Facts v2, `idb-Abse8QCG-GLWTT9-CD`)
is the approved privacy-threshold (k≥10) anonymous layer the old note referenced. Board 2
stays labelled Restricted Legacy and is superseded — its label stands, its content matches
board 3's data.

Boards 1 and 2 carry a dashboard-level filter; boards 3 and 4 do not (windows are baked
into each query).

---

## 2. Board 1 — "HR Genie — Operational Health · Development" (`idb-Abrogbz8-Qhf8Ea-CD`)

Purpose: single-pane operational health of the HR Genie estate — runtime, job status,
failures, telemetry coverage, execution channels. Left rail: "🔵 DEV / HR Genie /
Operational health · Development — Rolling 30 days; flagged test usage excluded. Runtime
is tool-job duration, not chat latency or labor saved. Median / P95 always show the
timed-job sample. Statuses count distinct job/channel/status…"

Dashboard filter: **"Reporting window within : Last 30 days"** — filter id
`1b7dbe4e-c1c2-4599-831b-45fc73129e81`, CrowQL: `DATE_BETWEEN(<ts>, CURRENT_DATE_WITH_OFFSET("day", -30), CURRENT_DATE())`
applied to `started_at` (MCP Tool Usage Events) and `Occurred At` (Handled Error Events).
(9 widgets; queries q-1..q-6 below.)

| # | Pane | Type | Source (by NAME) | Query / filters / window | Recreation notes |
|---|---|---|---|---|---|
| 1 | Captured tool runtime · median / P95 ms / timed jobs | Data table, 3 measure cols | HR Genie \| MCP Tool Usage Events | Inner AGG `MAX(latency_ms)` group by `job_id, app_type`; outer MEDIAN, P95, COUNT. Filters: `is_test IS FALSE`, `job_id NOT NULL`, `latency_ms NOT NULL`, `latency_ms > -1` + dashboard 30-day window (q-1 `3c653e22`) | Current values: median 1502 / P95 4288 / 163 timed jobs. No row-group column |
| 2 | Captured job-status evidence · distinct job / channel / status pairs | Data table | HR Genie \| MCP Tool Usage Events | AGG COUNT group by `status`, inner dedupe by `job_id, app_type, status`; `is_test IS FALSE`, `job_id NOT NULL` + window (q-2 `714210d8`) | 1 row: succeeded 163 |
| 3 | (KPI) Usage telemetry · last captured collection | KPI big-value | HR Genie \| MCP Tool Usage Events | `MAX(collected_at)` + window (q-3 `14a3737c`) | Shows 10/09/2026, 1:44 AM. Promotion-affected: `collected_at` semantics change with the page-commit cutover |
| 4 | Tool runtime breakdown · median / P95 ms / timed jobs | Data table | HR Genie \| MCP Tool Usage Events | Same as pane 1 grouped by `tool_name` (q-4 `6fd29292`) | 18 rows. Full row list archived in `operational-health-mid.png` |
| 5 | Workday authorization failures · distinct affected jobs / day | Column chart (series type `column`), title "Failure occurrence day", subtitle "Distinct affected jobs" | HR Genie \| Handled Error Events | Dedupe by `Job ID`; COUNT by day. Filters: **`Environment EQUALS "Development"`**, `Fingerprint ICONTAINS ":workday_rest:"`, `Fingerprint ICONTAINS ":Authorization_error:"`, `Job ID NOT NULL` + window (q-5 `97047618`) | Oct 2: 4, Oct 3: 1, Oct 7: 1 |
| 6 | Top handled failures · event / signature volume | Data table | HR Genie \| Handled Error Events | AGG COUNT group by `Recipe Name, Error Category, Error Code`, sorted desc, limited; **`Environment EQUALS "Development"`** + window (q-6 `29d89cc1`) | Top: REC \| Time-Off Event Hub / DOWNSTREAM_FUNCTION / HANDLED_RETRY_EXHAUSTED / 18405; FUNC \| Send Genie Event / 7097; FUNC \| Create App Link for User / 6962 |
| 7 | Reported telemetry coverage · registered assets | Pie | HR Genie \| Telemetry Coverage State | AGG COUNT group by `coverage_status`, no window (snapshot; q-7 `ebaa8e5b`, group-owned by board 3) | COVERED 24 (46.2%), QUIET 17 (32.7%), UNINSTRUMENTED_OFF 6 (11.5%), DARK 3 (5.8%), STOPPED 2 (3.8%) |
| 8 | Coverage detail · latest reported state | Data table | HR Genie \| Telemetry Coverage State | Full scan, cols `asset_name, last_emission_at, coverage_status, last_checked_at` (q-8 `5a7b67b5`) | 19 rows |
| 9 | Captured execution channels (null = unknown channel) | Pie | HR Genie \| MCP Tool Usage Events | Dedupe `job_id, app_type` → COUNT by `app_type`, `is_test IS FALSE`, no window (q-9 `cc115cc5`) | mcp 138 (84.7%), No data 17 (10.4%), genie_gateway 3, test_mode 3, slack 2 |

---

## 3. Board 3 — "HR Genie — Adoption, Outcomes & Intelligence · Development" (`idb-Abrcwzdm-P9h39R-CD`) — AUTHORITATIVE product analytics

Purpose: adoption/outcome/value story of HR Genie. Left rail text "🔵 DEV / HR Genie /
Rolling 30 days · flagged tests excluded. Users = distinct captured tool-user IDs…" plus
numbered section notes 02 Value, 03 Activity, 04 Speed, 05 Adoption, 06 Quality, 07 Health,
08 Coverage, 09 MCP & Genie (full texts in `adoption-*.png`; recreate verbatim).

**No dashboard filter** — each query bakes its window. ~15 KPI tiles, 9 tables, 6 charts.

### KPI tiles (in order, with current values)

| KPI label | Value | Source table (NAME) | Query semantics |
|---|---|---|---|
| Active tool users · 30 days | 4 | HR Genie \| MCP Tool Usage Events | COUNT of dedupe by `user_id`; `is_test IS FALSE`, `started_at DATE_BETWEEN last-30d`, `user_id NOT NULL` |
| Tool executions · 30 days | 163 | HR Genie \| MCP Tool Usage Events | COUNT of dedupe by `job_id, app_type`, `is_test IS FALSE`, last-30d |
| Verified approvals · 30 days | 6 | HR Genie \| Deflection Outcome Events | COUNT dedupe `event_key`; `verified IS TRUE`, `outcome_type IENDS_WITH "_APPROVED"`, `is_test IS FALSE`, `occurred_at` last-30d |
| Successful Genie actions · 30 days | 130 | HR Genie \| Conversation Tool Execution Events | COUNT dedupe `tool_event_id`; `call_result = "SUCCESS"`, `is_test IS FALSE`, `occurred_at` last-30d |
| Successful KB searches · 30 days | 36 | HR Genie \| Conversation Tool Execution Events | Same + `tool_name = "enterprise_search"`, `tool_type = "BUILTIN"` |
| Verified HR tickets · 30 days | 7 | HR Genie \| Deflection Outcome Events | Same as approvals but `outcome_type = "HR_TICKET_CREATED"` |
| Captured conversations · 30 days | 276 | HR Genie \| Intelligence Metrics | `SUM(metric_value)` WHERE `metric_name = "conversations_total"`, `metric_date` last-30d |
| User turns · 30 days | 357 | HR Genie \| Intelligence Metrics | Same, `metric_name = "user_turns_total"` |
| Captured notifications · 30 days | 67 | HR Genie \| Intelligence Metrics | Same, `metric_name = "notifications_total"` — **digest-adjacent, see staleness flags** |
| First notification → verified decision · median min | No data | HR Genie Notification Assignment Facts | `MEDIAN(response_minutes)` WHERE `state = "LINKED_DECISION"`, `is_test IS FALSE` — **stale family, see flags** |
| Verified within 1h · mature captured assignments · % | No data | HR Genie Notification Assignment Facts | `COUNT_IF(verified_within_1h)/COUNT(*)` over rows `age_seconds >= 3600`, `is_test IS FALSE` |
| Verified within 24h · mature captured assignments · % | No data | HR Genie Notification Assignment Facts | Same over `age_seconds >= 86400` |
| Median tool job runtime · ms | 1.5K (1494) | HR Genie \| MCP Tool Usage Events | Same as board 1 pane 1 (shared q-1 `3c653e22`) |
| P95 tool job runtime · ms | 4.28K (4288) | HR Genie \| MCP Tool Usage Events | Same shared query |
| Usage telemetry · last collected | 10/10/2026, 6:47 AM | HR Genie \| MCP Tool Usage Events | `MAX(collected_at)` (shared q-3 `14a3737c`) |

### Tables

| Pane title | Cols | Source (NAME) | Query / window | Notes |
|---|---|---|---|---|
| Repeat tool use · users with ≥2 jobs / captured users / % · 30 days | Count of matched rows / Count of rows / repeat_captured_users_pct | HR Genie \| MCP Tool Usage Events | Dedupe `user_id, job_id` → per-user count → `COUNT_IF(repeat_captured_user)`, COUNT; last-30d | 3 / 4 / 75 |
| 1h conversion evidence · verified n / mature n / % | verified_within_1h_pct | HR Genie Notification Assignment Facts | age≥3600 conversion ratio | "No results yet" |
| No linked action observed · age in hours · by workflow (n shown) | family / Median / Count / Max of observed_no_action_age_hours | HR Genie Notification Assignment Facts | `not_delivery_only IS FALSE`, `observed_no_action_age_hours >= 0`, group `family` | "No results yet" |
| 24h conversion evidence · verified n / mature n / % | verified_within_24h_pct | HR Genie Notification Assignment Facts | age≥86400 ratio | "No results yet" |
| Notification linkage coverage · non-test · since Oct 8 | family / state / Count of rows | HR Genie Notification Assignment Facts | COUNT group `family, state`, `is_test IS FALSE`, no date window | "No results yet" |
| Notification → verified decision · minutes by workflow / action (n shown) | family / bp_category / action / Median / P95 of response_minutes / Count | HR Genie Notification Assignment Facts | `state = "LINKED_DECISION"`, group `family, bp_category, action` | "No results yet" |
| First notification → validated skill invocation · min by workflow (n shown) | family / Median / P95 of notification_to_invocation_minutes / Count | HR Genie Notification Assignment Facts (+join) | `coherent_assignment_cycle IS TRUE`, `notification_to_invocation_minutes >= 0`, `first_notified_at NOT NULL` | "No results yet" |
| Most-used tools · 30 days | tool_name / Count of rows | HR Genie \| Conversation Tool Execution Events | COUNT dedupe `tool_event_id, tool_name`, `call_result = "SUCCESS"`, `is_test IS FALSE`, last-30d, sorted | get_my_time_off_balances 19, list_my_pending_tasks 16, view_benefit_elections 12, get_my_manager 10, … |
| Verified business outcomes · 30 days | outcome_type / Count of rows | HR Genie \| Deflection Outcome Events | COUNT dedupe `event_key, outcome_type`, `verified IS TRUE`, `is_test IS FALSE`, `occurred_at` last-30d | HR_TICKET_CREATED 7, INBOX_TASK_APPROVED 5, TIME_OFF_REQUEST_SUBMITTED 4, TIME_OFF_REQUEST_CANCELLED 2, DIRECT_REPORT_TIME_OFF_APPROVED 1 |
| Conversation evidence classes · 30 days | classification / Count of rows | HR Genie \| Conversation Telemetry Classifications | COUNT dedupe `conversation_id, classification`, `is_test IS FALSE`, `occurred_at` last-30d | SKILL_ASSISTED 51, KB_ONLY_CANDIDATE 20, ESCALATED_HR_TICKET_CREATED 5 |
| Evaluation scores & sample sizes · daily | metric_date / metric_name / dimension / metric_value | HR Genie \| Intelligence Metrics | `metric_name = "judge_score_avg"` rows (companion `judge_score_n` rows), `metric_date` last-30d, no aggregation | 10/07 correctness 4.8, helpfulness 2.5, tone 3.8; 10/08 5 / 3.4 / 4.2 … |
| Knowledge gaps · queued demand | signal_type / topic / Sum of demand_count | HR Genie \| Knowledge Gap Queue | `SUM(demand_count)` group `signal_type, topic`, no window | judge_issue_tag/abandoned_loop 4; unknown_topic_cluster/UNKNOWN 5 |
| Knowledge-gap age · current dated gaps · hours / demand / n | state / Count / Median / Max of gap_age_hours / Sum of demand_count | HR Genie \| Knowledge Gap Queue | computed `gap_age_hours >= 0`, group `state` | open: 2 gaps, median 1.33h, max 1.33h, demand 9 |
| Top handled failures · 30 days | Recipe Name / Error Category / Error Code / Count of rows | HR Genie \| Handled Error Events | Same as board 1 pane 6 (shared q-6), **`Environment EQUALS "Development"`** | Same top rows as board 1 |
| Coverage detail · latest reported state | asset_name / last_emission_at / coverage_status / last_checked_at | HR Genie \| Telemetry Coverage State | Full scan (shared q-8) | 19 rows |
| Successful Genie actions by tool · 30 days | tool_name / Count of rows | HR Genie \| Conversation Tool Execution Events | SUCCESS dedupe by tool, sorted | enterprise_search 36, get_my_time_off_balances 14, list_my_pending_tasks 13, … 19 rows |

### Charts

| Pane title | Type | Source (NAME) | Query | Series data |
|---|---|---|---|---|
| Daily active tool users · 30 days | Column | HR Genie \| MCP Tool Usage Events | dedupe `user_id` + day, `is_test IS FALSE`, last-30d | 19 daily points Sep 12–Oct 7, values 1–3 (max 3 on Oct 7-ish days) |
| Top 5 conversation topics · 30 days | Column | HR Genie \| Intelligence Metrics | `SUM(metric_value)` WHERE `metric_name = "user_turns"` group `dimension`, `metric_date` last-30d, sorted, top 5 | all 104, PROFILE_UPDATE 81, UNKNOWN 65, PTO_REQUEST 33, PAY 28 |
| Captured feedback · 30 days | Pie | HR Genie \| Intelligence Metrics | `SUM(metric_value)` WHERE `metric_name = "feedback"` group `dimension` | negative 3 (60%), positive 2 (40%) |
| Workday authorization failures · affected jobs / day | Area series | HR Genie \| Handled Error Events | Same as board 1 pane 5 (shared q-5, `Environment EQUALS "Development"`) | Oct 2: 4, Oct 3: 1, Oct 7: 1 |
| Reported telemetry coverage · registered assets | Pie | HR Genie \| Telemetry Coverage State | Shared q-7 | Same as board 1 |
| Captured execution channels · 30 days | Pie | HR Genie \| MCP Tool Usage Events | Shared q-9 | Same as board 1 |

---

## 4. Board 2 — "HR Genie — Product Analytics · Restricted Legacy · Development" (`idb-Abrntmt9-RYgtWH-CD`)

**KEEP THIS LABEL — standing rule; do not suggest unlabelling.** Content = board 3's data
under the older layout/wording (section texts 02 Value … 09 MCP & Genie; KPI "19 Verified
business outcomes · aggregate"; tables "Top 10 captured tools · distinct jobs per tool",
"Feedback polarity · captured rating counts · scope unknown", "Conversation evidence
classes · distinct conversations"; chart "Daily active captured tool users"). Has the same
dashboard filter "Reporting window within : Last 30 days" (same CrowQL shape as board 1).
Owns 7 of the shared queries (`2101a7a9` active users, `8b31766b` executions,
`a25bc40a` approvals, `614d437d` outcomes, `afd5291b` classes, `0cae2e41` top tools,
`b94375ef` daily-active chart) and reuses board 3's pool for the rest. Current values
match board 3 (4 / 163 / 6 / 130 / 36 / 7 / 276 / 357 / 67; feedback negative 3 positive 2).

Recreate in prod ONLY if historical parity is wanted; do not recreate silently as the
primary board.

---

## 5. Board 4 — "HR Genie — Anonymous Product Facts v2 · Development" (`idb-Abse8QCG-GLWTT9-CD`)

The v2 board from the older note — **exists, live, and is the approved anonymous
(k≥10) reporting layer.** No dashboard filter. 3 widgets, all reading ONE table by scan:
**HR Genie | Product Metrics Daily v2** (dev UUID `0b830b77-3788-4a6e-abdc-66c1695e80bf`),
cols `metric_date, metric_name, metric_value, contributor_count, sample_count,
privacy_policy_version, source_coverage, generated_at`; `privacy_policy_version =
HRG_PRODUCT_V2_K10`, `source_coverage = COMPLETE_CURSOR_PAGED`.

1. Table "Anonymous daily product facts · k≥10" — filtered scan of the v2 table. Rows: 10/09 active_users 18 (contributors 18, sample 85); conversations_total 82 (16, 79); events_total 558 (18, 85); user_turns_total 89 (16, 79).
2. Column chart "Daily product activity · anonymous aggregates" — `metric_value` by `metric_name`.
3. Column chart "Privacy threshold coverage · contributing users" — `contributor_count` by `metric_name`.

---

## 6. Promote-time deltas (apply during prod recreation)

1. **Table id remap by NAME.** Every query re-points to the prod table UUID; use the
   names in the section-0 table. The five pipeline tables (App Event Ledger 156842,
   Telemetry Collector State 156849, Telemetry Coverage State 156843, Intelligence
   Metrics 156862, Topic Taxonomy 156850) get NEW prod ids under the page-commit cutover
   (checkpoint owner + caller registry; new/renamed state tables) — never copy dev UUIDs.
2. **`Environment EQUALS "Development"` → `"Production"`** in the Workday-authorization
   and Top-handled-failures queries (board 1 panes 5–6; board 3 same).
3. **Stale panes — BSYS-27724 Manager PTO Digest retired today (removed from batch, closed
   Won't Do).** The whole notification-conversion family reads `HR Genie Notification
   Assignment Facts` / `notifications_total` and charts the notification→decision pipeline
   the digest would have joined: KPIs "Captured notifications", "First notification →
   verified decision · median min", "Verified within 1h/24h · mature captured
   assignments · %", and tables "1h/24h conversion evidence", "No linked action observed",
   "Notification linkage coverage · since Oct 8", "Notification → verified decision",
   "First notification → validated skill invocation". All currently render "No data / No
   results yet". Flag each at recreation: either drop, or keep with a caption that the
   digest layer is retired (conversion story terminates at single-request pings). Do not
   rebuild digest-specific expectations.
4. **Dev-only test data:** the `is_test IS FALSE` filters exclude flagged tests, but the
   channels pie still shows a `test_mode` slice (3 jobs, 1.8%) and board 3's own "03
   Activity" note concedes counts can include Development tests. In prod, re-baseline all
   counts (Sep 12–Oct 7 dev history will not exist in prod tables).
5. **Naming:** drop the "· Development" suffixes from all dashboard titles; the left-rail
   "🔵 DEV" badge is a dev-only text widget — replace with a prod-appropriate label.
   Handles will differ (fine).
6. **Board 2 stays labelled Restricted Legacy** if recreated; board 3 is the authoritative
   product-analytics board; board 4 is the approved anonymous layer.
7. **Timezone:** queries execute with `userTimezone: "America/New_York"` — keep in prod.
8. **`collected_at` KPIs** (panes 3/"last collected") depend on collector checkpoint
   semantics, which the page-commit cutover changes — re-verify the collectors populate
   `collected_at` after the cutover before trusting these tiles.

---

## 7. Prod recreation runbook

For each board (1, 3, 4; board 2 optional):

1. Workato → Insights → **New dashboard**; title = exact title minus "· Development".
2. Add dashboard filter (boards 1 and 2 only): Reporting window, operator `within (date
   between)`, start `now-30d` (CURRENT_DATE_WITH_OFFSET day −30), end `today`; bind it to
   the `started_at` column of "HR Genie | MCP Tool Usage Events" and the "Occurred At"
   column of "HR Genie | Handled Error Events".
3. Add text widgets (left rail + numbered section notes) verbatim from the screenshots.
4. For each pane in the section-2/3/5 tables: add widget → pick chart type (pie / column /
   area / data table / KPI number) → select the source table **by name in prod** → rebuild
   the aggregation exactly as written in the "Query" column (group-by fields, aggregate
   functions MEDIAN/P95/COUNT/COUNT_IF/SUM/MAX, inner dedupe aggregations, filters,
   window). The CrowQL JSON asset `dashboard-doc-assets/crowql-queries-all-boards-20261011.json`
   is the field-by-field source of truth — each body nests `Filter → Aggregate → TableScan`
   bottom-up.
5. Apply the section-6 deltas while building (Environment filter value, dropped digest
   panes or their caption, prod names without suffixes).
6. Set each widget title exactly as listed; keep KPI tile order from the screenshots
   (`*-top.png`, `*-mid.png`, `*-bottom.png`).
7. Verify: switch the reporting window and confirm each pane loads; compare shapes (pie
   slice counts, table column sets) against the screenshots — values will differ (fresh
   prod data).
