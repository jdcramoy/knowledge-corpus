# BSYS-29829 — P1 spike: Genie destructive-capability inventory (dev)

Date: 2026-10-22. Scope: dev estate only (workato-airo-mcp-server / wt dev profile `josh-us`,
workspace 3535597). Read-only spike — no prod contact, no genie stops/starts, no confirmation-flag
flips, no writes of any kind. Ticket: [BSYS-29829](https://workato.atlassian.net/browse/BSYS-29829)
(parent [BSYS-29828](https://workato.atlassian.net/browse/BSYS-29828)). Plan of record:
`~/.claude/knowledge/projects/BSYS-29828/bsys-29829-genie-approval-gate-plan.md`.

## Method

- Full genie inventory pulled live from the agentic API (`GET /api/agentic/genies`, paged,
  per_page=50): **278 genies** (MCP genie_list reports 259; the raw API returns a superset
  including mock/stub entries).
- Per genie, its home folder was listed via `GET /api/recipes?folder_id=<id>&per_page=100`.
  Skills = recipes in that folder with `trigger_application == "workato_skill"` (the
  recipe_builder_init_skill convention). 76 of 278 genies have >=1 such recipe; 281 skill rows
  total covering **145 unique skill recipes** (shared home folders duplicate skills across the
  genies that live there — recorded per the folder rule).
- Classification signals, cheapest first: recipe name, description, `applications`/
  `action_applications` connectors; ambiguous cases settled with ONE deep read
  (`GET /api/recipes/<id>`) of step-level connector actions. 5 parallel classification agents,
  bounded deep reads (raw reads cached in /tmp/p1-spike/deep/).
- Verdicts are STATIC evidence (names + connector actions), not runtime traces — see
  "Not verified".

## Headline counts

| Measure | Count |
|---|---|
| Genies in dev (all states) | 278 |
| Genies with >=1 attached skill | 76 |
| Skill rows (genie x skill, shared folders double-count) | 281 |
| Unique skill recipes | 145 |
| Unique DESTRUCTIVE skill recipes | **57** |
| Unique read-only skill recipes | 88 |
| Genies carrying >=1 destructive skill | **55** |

Highest-risk patterns (generic executors, not scoped writes):
1. **Snowflake arbitrary SQL** — `sql_query` (82152185), `sql_query` (74516187),
   `Query_Snowflake` (74299450): run_custom_sql, DML/DDL-capable; attached to 7+5+5 genies
   respectively (drift, SQL-generator, question-generator, checker genies).
2. **Dev API executor** — `EM Triage | Dev API Executor` (83113395): arbitrary
   method/path/body against the Workato Dev API; attached to 3 genies. This is the same class of
   ungated tool as the AIRO MCP `data_table_delete` vector named in the BSYS-29828 incident.
3. **On-prem CLI tool invocation** — `Invoke tool` (82970513) / `Invoke tool Prod` (82970514):
   arbitrary observability tools via on-prem agent; 3-4 genies each.
4. **Genie-to-genie delegation** — `Genie 1` (74562274, 4 genies), `Delegate work to query
   executor genie` (73129897, 3 genies): assign-task-to-genie; a confirmation flag on the caller
   does not cover the downstream genie's own destructive skills (headless path).
5. **Outward messages / record writes** — Slack posts (74060151), Salesforce updates (73440679,
   72999941, 73161503), quote generation (73255440), Jira ticket creation (72863824), Outreach
   email writes (72997907), Freshdesk ticket/note creation (83027814, 83028202), Workday
   time-off actions (78629762/78629763), data-table writes (82466340, 82449914, 74439702,
   73329788, 82529042, 82165970, 82235060/82235197/82240792/82263084/82604648/82837379/
   82235398, 83286155, 83234662), Snowflake semantic-layer writes (82837379, 82235398),
   file-storage writes (73133609, 82231621), OAuth reset chain (82795189), send-test-email
   (74650705).

## Enumeration table 1 — genies with attached skills (76)

| Genie | State | Skills | Destructive? |
|---|---|---|---|
| [[COR] GENIE | Slack | Intake Genie](https://app.workato.com/genies/gin-AXRGedcW-kbrpnY-CD/overview) | started | 2 | **YES (2)** |
| [Account Research Genie](https://app.workato.com/genies/gin-AbkPbrDx-YKWR8T-CD/overview) | started | 14 | **YES (2)** |
| [Alfred on Slack](https://app.workato.com/genies/gin-AaNTx8TG-JBaxPY-CD/overview) | started | 1 | no |
| [Alfred Pilot ](https://app.workato.com/genies/gin-ATXxe38H-DRrArd/overview) | started | 1 | no |
| [Alfred TESTING](https://app.workato.com/genies/gin-ATHYXgPW-9EwXcB/overview) | stopped | 1 | no |
| [Andy_17](https://app.workato.com/genies/gin-AWrmNQYc-GAW6hK/overview) | stopped | 1 | no |
| [AO Content & Talking Points Genie](https://app.workato.com/genies/gin-AbsRwcMC-otEpkz-CD/overview) | started | 14 | **YES (2)** |
| [AO Message Personalization Genie](https://app.workato.com/genies/gin-AbsRx3HH-ngfePx-CD/overview) | started | 14 | **YES (2)** |
| [Approval Gate NOT IN USE](https://app.workato.com/genies/gin-Ab3wCzaA-mTRA6L-CD/overview) | stopped | 3 | **YES (3)** |
| [Ask DD GEN Feedback Processing](https://app.workato.com/genies/gin-Ac6KoMom-nW9enK-CD/overview) | started | 3 | **YES (1)** |
| [Ask Deal Desk Genie](https://app.workato.com/genies/gin-AbrwJXaE-AxzbQE-CD/overview) | started | 3 | **YES (1)** |
| [BT Genie 2.0](https://app.workato.com/genies/gin-AbzEtfoT-LgXXem-CD/overview) | started | 1 | no |
| [CCE Assistant](https://app.workato.com/genies/gin-AbMBsRnN-K6cQ8X-CD/overview) | started | 2 | **YES (1)** |
| [Connectors Genie](https://app.workato.com/genies/gin-AapeD4kk-tkG6MD-CD/overview) | started | 2 | **YES (1)** |
| [CS Email Test](https://app.workato.com/genies/gin-AYXxwgtz-4LxNdY-CD/overview) | stopped | 3 | **YES (1)** |
| [CSM Account Information Genie](https://app.workato.com/genies/gin-AYLbN9JM-NwwoGJ-CD/overview) | stopped | 3 | **YES (1)** |
| [CSM Genie Main](https://app.workato.com/genies/gin-AYEsdreN-W6mhXm-CD/overview) | started | 3 | **YES (1)** |
| [Data Genie Testing](https://app.workato.com/genies/gin-AaQMEb4H-CebFQc-CD/overview) | stopped | 7 | **YES (5)** |
| [Deep Visibility Genie](https://app.workato.com/genies/gin-AaesxPn3-CAmwLJ-CD/overview) | started | 2 | no |
| [Demo Coordination genie 27](https://app.workato.com/genies/gin-Ac48CR8d-dPLGcH-CD/overview) | stopped | 1 | **YES (1)** |
| [Deployment Review Genie](https://app.workato.com/genies/gin-AbH9CYCf-PDdhaH-CD/overview) | stopped | 1 | no |
| [Dex_11](https://app.workato.com/genies/gin-AWpEKNAN-TbGWkY/overview) | stopped | 2 | no |
| [Drift Check Genie](https://app.workato.com/genies/gin-AbJ4d8Pr-FMbXpn-CD/overview) | stopped | 3 | **YES (2)** |
| [Drift Fix Genie](https://app.workato.com/genies/gin-AbWxkCLd-8wRwmG-CD/overview) | started | 6 | **YES (1)** |
| [Drift Investigation Genie](https://app.workato.com/genies/gin-AbQpfH8c-wafcsH-CD/overview) | stopped | 3 | **YES (2)** |
| [DSPy Semantic Search genie](https://app.workato.com/genies/gin-AabXGhko-XQf8Ga-CD/overview) | stopped | 1 | **YES (1)** |
| [DSPY_GEPA_Optimized_KB](https://app.workato.com/genies/gin-Aas6mNBp-BPMm9p-CD/overview) | started | 1 | **YES (1)** |
| [EM | Builder](https://app.workato.com/genies/gin-AbzHEWNT-QzhREk-CD/overview) | started | 1 | **YES (1)** |
| [EM | Recipe Triage](https://app.workato.com/genies/gin-AbwEPzbk-xgpoPT-CD/overview) | started | 1 | **YES (1)** |
| [EM | Triage Dissenter](https://app.workato.com/genies/gin-AbwKFbFE-BsAppE-CD/overview) | started | 1 | **YES (1)** |
| [Headless Identity Probe](https://app.workato.com/genies/gin-AbTEKa4R-RpxdwG-CD/overview) | started | 6 | no |
| [HR Genie Analyst](https://app.workato.com/genies/gin-AbrCztoB-bxckro-CD/overview) | started | 3 | no |
| [HR Management genie 1](https://app.workato.com/genies/gin-AYXCh8B6-ow4YKJ-CD/overview) | stopped | 8 | **YES (4)** |
| [Kaiyang Test Genie](https://app.workato.com/genies/gin-AWEndtCJ-Xbtsn6/overview) | started | 1 | no |
| [Lead Genie](https://app.workato.com/genies/gin-AaHn8mge-wJBBB9-CD/overview) | started | 7 | **YES (6)** |
| [mano2](https://app.workato.com/genies/gin-AbdPCsWf-M684F4-CD/overview) | started | 14 | **YES (2)** |
| [Messaging Testing genie](https://app.workato.com/genies/gin-AaN4xYFf-KpCFpk-CD/overview) | stopped | 1 | no |
| [Micah 12](https://app.workato.com/genies/gin-AbtkkkoF-xKoBEG-CD/overview) | stopped | 10 | **YES (3)** |
| [OUTDATED -- Ask Deal Desk Genie](https://app.workato.com/genies/gin-AbrwJXaJ-3LxRzA-CD/overview) | stopped | 3 | **YES (1)** |
| [OUTDATED Ask DD Ask Deal Desk Genie](https://app.workato.com/genies/gin-AaQ9DkRJ-9Ppmwx-CD/overview) | stopped | 3 | **YES (1)** |
| [PH - AccountIQ Agent](https://app.workato.com/genies/gin-AaM9Dd6w-zYTrg8-CD/overview) | started | 1 | **YES (1)** |
| [PH - ActivityIQ Agent](https://app.workato.com/genies/gin-AaMTzKTr-C3RKep-CD/overview) | started | 3 | no |
| [PH - ConversationIQ Agent](https://app.workato.com/genies/gin-AaMTppwb-knYFCt-CD/overview) | started | 3 | no |
| [PH - Customer 360 Agent](https://app.workato.com/genies/gin-AaLpz9zK-RQwpHT-CD/overview) | started | 7 | **YES (1)** |
| [PH - Insights Agent](https://app.workato.com/genies/gin-AaM3ppcB-kXYATp-CD/overview) | started | 2 | **YES (1)** |
| [PH - ProductIQ Agent](https://app.workato.com/genies/gin-AaLwLDmJ-fR3x6s-CD/overview) | started | 3 | **YES (1)** |
| [PH - Query Construction genie](https://app.workato.com/genies/gin-AaLwJ9Fs-dazPFD-CD/overview) | started | 3 | **YES (1)** |
| [PH - Query Execution genie](https://app.workato.com/genies/gin-AaLwhbNp-wf4wkH-CD/overview) | started | 3 | **YES (1)** |
| [PH - SupportIQ Agent](https://app.workato.com/genies/gin-AaMTgdDx-4HtGep-CD/overview) | started | 3 | no |
| [Pluto Security Agent](https://app.workato.com/genies/gin-Abme9fDh-R4MMhX-CD/overview) | stopped | 2 | no |
| [Prod Semantic Search Genie](https://app.workato.com/genies/gin-AbLwEmMJ-dQ33pn-CD/overview) | started | 1 | **YES (1)** |
| [Product Support genie 1](https://app.workato.com/genies/gin-AbwsfnJk-EJ8EFQ-CD/overview) | started | 6 | **YES (2)** |
| [Product Support genie 1](https://app.workato.com/genies/gin-AbtkkkoG-LwCxax-CD/overview) | stopped | 10 | **YES (3)** |
| [Prospect Research Genie](https://app.workato.com/genies/gin-Abf4L4wn-eprXXP-CD/overview) | started | 14 | **YES (2)** |
| [Question and SQL Generator ](https://app.workato.com/genies/gin-Ab3XmfF3-pTexfF-CD/overview) | started | 3 | **YES (3)** |
| [Question Generator](https://app.workato.com/genies/gin-Ab43CQ8h-63QnC6-CD/overview) | started | 3 | **YES (3)** |
| [Recipe Opportunity Genie](https://app.workato.com/genies/gin-AbJ6BLwP-fEMz6C-CD/overview) | stopped | 1 | no |
| [Remediation Genie](https://app.workato.com/genies/gin-AbYPgthA-cw4h8X-CD/overview) | stopped | 12 | **YES (8)** |
| [Review Gen Genie](https://app.workato.com/genies/gin-AbrPhraX-EmsDrB-CD/overview) | started | 1 | **YES (1)** |
| [Sample | Freshdesk Ticket Genie](https://app.workato.com/genies/gin-AbwdoDpR-cPNTKf-CD/overview) | stopped | 2 | **YES (2)** |
| [Search Semantic Layer Experiment](https://app.workato.com/genies/gin-AbAWBfok-AdxtwY-CD/overview) | started | 1 | **YES (1)** |
| [SecurityGenie](https://app.workato.com/genies/gin-AWpEFdak-ecJpFK/overview) | started | 2 | no |
| [Session Triage Genie](https://app.workato.com/genies/gin-AbEwQHoE-AAAPHM-CD/overview) | started | 4 | **YES (1)** |
| [Snowflake Checker](https://app.workato.com/genies/gin-AaxPw3Ez-JoH4pr-CD/overview) | started | 3 | **YES (3)** |
| [Software Testing genie 144](https://app.workato.com/genies/gin-AYTB9AE4-P9PdDM-CD/overview) | stopped | 3 | **YES (1)** |
| [Software Testing genie 309](https://app.workato.com/genies/gin-AafM9mQ9-oH4QJF-CD/overview) | stopped | 2 | **YES (1)** |
| [SQL Generator](https://app.workato.com/genies/gin-Ab43GtaP-nfrH8k-CD/overview) | started | 3 | **YES (3)** |
| [Support Routing genie](https://app.workato.com/genies/gin-AaRneMdT-A3gt4c-CD/overview) | stopped | 1 | no |
| [System Monitoring genie](https://app.workato.com/genies/gin-AbtkkkoH-LTbfDn-CD/overview) | stopped | 10 | **YES (3)** |
| [TPT](https://app.workato.com/genies/gin-AbwLsb3K-oGGdE3-CD/overview) | stopped | 1 | **YES (1)** |
| [Vendor Onboarding Detection Layer](https://app.workato.com/genies/gin-AbcNaNeA-opxRfk-CD/overview) | stopped | 5 | no |
| [Wil Support IDOL GO](https://app.workato.com/genies/gin-AbbPKwsA-8D9hXJ-CD/overview) | started | 1 | no |
| [Workflow Testing genie](https://app.workato.com/genies/gin-AbDAmQbE-8LWQCe-CD/overview) | stopped | 1 | **YES (1)** |
| [WOW Events FAQ genie - Dev](https://app.workato.com/genies/gin-AaJtNBoc-oN64wt-CD/overview) | started | 2 | **YES (1)** |
| [WOW Product Genie](https://app.workato.com/genies/gin-Abf9Aamn-XtBN8N-CD/overview) | stopped | 1 | **YES (1)** |
| [WSS Advisor](https://app.workato.com/genies/gin-AbJBxDYs-BJs4Y4-CD/overview) | started | 1 | **YES (1)** |

## Enumeration table 2 — the 57 unique destructive recipes (flag-placement targets)

Flag placement column: default = the native Start-workflow confirmation flag
('Require user confirmation before executing skill?' = Yes) on the skill recipe's trigger.
Generic-executor skills get the flag PLUS a recipe-level allowlist guard (flag alone cannot scope
them). Headless/delegation skills cannot rely on the flag at all (user confirmations do not fire
on the assign-task path) — those go to the Jira approval gate per plan P2.

| Skill (recipe) | Recipe URL | Attached to (genies) | Why destructive | Flag placement |
|---|---|---|---|---|
| [COR] Create Project Ticket in Jira | https://app.workato.com/recipes/72863824 | [COR] GENIE | Slack | Intake Genie | creates Jira project tickets | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| 2. Set Outreach Email | https://app.workato.com/recipes/72997907 | Lead Genie | sets/writes Outreach email | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Update SDR qualification attributes into Salesforce | https://app.workato.com/recipes/72999941 | Lead Genie | updates Salesforce qualification attributes | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| [dep] get_domain_semantic_index | https://app.workato.com/recipes/73117601 | Data Genie Testing | db_table add_record + LLM call | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Delegate work to query executor genie | https://app.workato.com/recipes/73129897 | PH - ProductIQ Agent, PH - Query Construction genie, PH - Query Execution genie | assigns task to another genie (triggers execution); invokes executor genie; chained execution | Recipe trigger flag will NOT fire (headless/agent-orchestration path) — Jira approval gate per plan P2 |
| Consolidate all data points from sub agents | https://app.workato.com/recipes/73133609 | PH - Insights Agent | appends and stores files in Workato FileStorage | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Approve or reject intent agent plan | https://app.workato.com/recipes/73137719 | PH - Customer 360 Agent | approval decision writes on agent plans | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Query Constructor - PH | https://app.workato.com/recipes/73143212 | Software Testing genie 309 | assigns task to another genie (triggers execution) | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| SEACRCH ACCOUNT METADATA | https://app.workato.com/recipes/73159209 | PH - AccountIQ Agent | Salesforce create_custom_object | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Admin modify user | https://app.workato.com/recipes/73161001 | Lead Genie | admin user modification writes | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Update Campaign Activity | https://app.workato.com/recipes/73161503 | Lead Genie | updates Salesforce campaign activity records | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Process Assign to SDR | https://app.workato.com/recipes/73161812 | Lead Genie | assigns SDR; writes Salesforce, posts Slack, Outreach | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| SDR | Set LeadGenie Status | https://app.workato.com/recipes/73162150 | Lead Genie | sets LeadGenie status via API write | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| [Ask DD] SKILL | Generate Renewal Quote | https://app.workato.com/recipes/73255440 | Ask DD GEN Feedback Processing, Ask Deal Desk Genie, OUTDATED -- Ask Deal Desk Genie, OUTDATED Ask DD Ask Deal Desk Genie | generates Salesforce/SteelBrick renewal quote records | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| [dep] find_domain_classification | https://app.workato.com/recipes/73266695 | Data Genie Testing | db_table add_record + arbitrary Snowflake SQL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| select_semantic_models | https://app.workato.com/recipes/73299489 | Data Genie Testing | db_table add_record + arbitrary Snowflake SQL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| [COR] SKILL | Adding user to a DND list | https://app.workato.com/recipes/73329788 | [COR] GENIE | Slack | Intake Genie | adds user rows to Do Not Disturb data table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| ws_get_semantic_models | https://app.workato.com/recipes/73356657 | Data Genie Testing | workato_db_table add_record write | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| find_domain_classification | https://app.workato.com/recipes/73357262 | Data Genie Testing | db_table add_record + arbitrary Snowflake SQL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| Update Opp (CSM Apps) | https://app.workato.com/recipes/73440679 | CS Email Test, CSM Account Information Genie, CSM Genie Main, Software Testing genie 144 | updates Salesforce opportunity records; updates Salesforce renewal opportunity records | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| TEST — Emit business event to Genie (janssen) | https://app.workato.com/recipes/73865652 | Demo Coordination genie 27 | emits a business event to a Genie | Recipe trigger flag will NOT fire (headless/agent-orchestration path) — Jira approval gate per plan P2 |
| Handle Slack Thread Message | https://app.workato.com/recipes/74060151 | Connectors Genie | posts Slack messages to channels (post_message_to_channel x3) | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Query_Snowflake | https://app.workato.com/recipes/74299450 | Approval Gate NOT IN USE, Question Generator, Question and SQL Generator , SQL Generator +1 more | arbitrary Snowflake SQL, can run DML/DDL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| TEST | SOAP Test | https://app.workato.com/recipes/74321231 | HR Management genie 1 | unconfigured Workday SOAP call_operation; op indeterminate | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Genie Query Log | https://app.workato.com/recipes/74439702 | WOW Events FAQ genie - Dev | workato_db_table add_record write | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| sql_query | https://app.workato.com/recipes/74516187 | Approval Gate NOT IN USE, Drift Check Genie, Drift Investigation Genie, Question Generator +3 more | Snowflake run_custom_sql: arbitrary SQL, could DML/DDL; arbitrary Snowflake SQL, can run DML/DDL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| Genie 1 | https://app.workato.com/recipes/74562274 | DSPY_GEPA_Optimized_KB, DSPy Semantic Search genie, Prod Semantic Search Genie, Search Semantic Layer Experiment | assigns task to another genie (triggers execution); deep-read: assigns task to genie for autonomous processing | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| SendTestEmail | https://app.workato.com/recipes/74650705 | Workflow Testing genie | gmail send_mail outward message | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Ask WSS Advisor | https://app.workato.com/recipes/74966396 | WSS Advisor | assigns task to another genie (triggers execution) | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| FAILED MIGRATION ARTIFACT | action_time_off_request | https://app.workato.com/recipes/78629762 | HR Management genie 1 | acts on time-off requests (approve/deny) | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| FAILED MIGRATION ARTIFACT | cancel_time_off_request | https://app.workato.com/recipes/78629763 | HR Management genie 1 | cancels time-off requests | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| CCE Assistant - Start Ticket Run | https://app.workato.com/recipes/82124424 | CCE Assistant | initiates ticket-run processing, writes ledger | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| sql_query (drift_fix) | https://app.workato.com/recipes/82152185 | Approval Gate NOT IN USE, Drift Check Genie, Drift Investigation Genie, Question Generator +3 more | Snowflake run_custom_sql: arbitrary SQL, could DML/DDL; arbitrary Snowflake SQL, can run DML/DDL | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| store_analysis_report | https://app.workato.com/recipes/82165970 | Session Triage Genie | stores report to files/data tables | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| zip_session_reports | https://app.workato.com/recipes/82231621 | Remediation Genie | creates zip files in file storage | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| propose_remediation_change | https://app.workato.com/recipes/82235060 | Remediation Genie | updates and adds remediation data-table records | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| mark_remediation_reviewed | https://app.workato.com/recipes/82235197 | Remediation Genie | records human approval into data table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| apply_remediation_change | https://app.workato.com/recipes/82235398 | Remediation Genie | writes approved fix to Snowflake semantic layer table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| rollback_remediation_change | https://app.workato.com/recipes/82240792 | Remediation Genie | rolls back changes: updates changelog, adds apply-log rows | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| recompute_batch_status | https://app.workato.com/recipes/82263084 | Remediation Genie | updates batch status rows in REMEDIATION_BATCH_STATUS | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| [AO]CR Signal Ingestion | https://app.workato.com/recipes/82449914 | AO Content & Talking Points Genie, AO Message Personalization Genie, Account Research Genie, Prospect Research Genie +1 more | adds records to a data table (signal ingestion); ingests signals into data table writes | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Log AO System Prompt | https://app.workato.com/recipes/82466340 | AO Content & Talking Points Genie, AO Message Personalization Genie, Account Research Genie, Prospect Research Genie +1 more | saves new row to data table; saves system prompt as new data-table row | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Capture Signal | https://app.workato.com/recipes/82529042 | WOW Product Genie | logs customer signal records via Slack capture flow | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| log_remediation_reasoning | https://app.workato.com/recipes/82604648 | Remediation Genie | inserts reasoning rows into REMEDIATION_REASONING_LOG | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| TEST | HR Genie OAuth Reset Chain UAT | https://app.workato.com/recipes/82795189 | HR Management genie 1 | invokes OAuth reset chain (config change) | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Copy of apply_remediation_change | https://app.workato.com/recipes/82837379 | Remediation Genie | writes approved fix to Snowflake semantic layer table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Invoke tool | https://app.workato.com/recipes/82970513 | Micah 12, Product Support genie 1, System Monitoring genie | invokes arbitrary observability tools via on-prem CLI | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| Invoke tool Prod | https://app.workato.com/recipes/82970514 | Micah 12, Product Support genie 1, System Monitoring genie | invokes arbitrary observability tools via on-prem CLI | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| PR memory skill | https://app.workato.com/recipes/82970516 | Micah 12, Product Support genie 1, System Monitoring genie | updates and adds lookup-table memory entries | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Send Ticket | https://app.workato.com/recipes/82997542 | TPT | sends a ticket outward | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Freshdesk | Create ticket with attachments [Sample] | https://app.workato.com/recipes/83027814 | Sample | Freshdesk Ticket Genie | creates Freshdesk tickets with attachments | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Freshdesk | Add note with attachment [Sample] | https://app.workato.com/recipes/83028202 | Sample | Freshdesk Ticket Genie | adds notes/replies to Freshdesk tickets | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| Invoke tool Prod | https://app.workato.com/recipes/83040830 | Product Support genie 1 | invokes arbitrary observability tools via on-prem CLI | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| PR memory skill | https://app.workato.com/recipes/83040832 | Product Support genie 1 | updates and adds lookup-table memory entries | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| EM Triage | Dev API Executor | https://app.workato.com/recipes/83113395 | EM | Builder, EM | Recipe Triage, EM | Triage Dissenter | generic Workato Dev API executor with arbitrary method/path/body | Recipe trigger (Start workflow flag) + recipe-level allowlist guard; flag alone insufficient — skill is a generic executor |
| [DRIFT FIX] revise_fix | https://app.workato.com/recipes/83234662 | Drift Fix Genie | revises/fixes drift change-log rows in data table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |
| [CX] [RG] 4.2 Log any approved accounts in the G2 staging data table | https://app.workato.com/recipes/83286155 | Review Gen Genie | logs approved accounts into G2 staging data table | Recipe trigger (Start workflow) — flip 'Require user confirmation before executing skill?' to Yes |

## 2. Confirm-flag placement design (per destructive skill)

Three candidate layers; the design picks per class:

- **(A) Skill recipe trigger — the native flag (primary).** Workato's
  `Require user confirmation before executing skill?` input lives on the skill's **Start workflow
  trigger** (the `workato_skill` trigger of the backing recipe). Flip to Yes and, in a supported
  chat conversation, the genie pauses, shows the prepared parameter values, and waits for explicit
  approval before the recipe runs. Docs:
  https://docs.workato.com/en/agentic/skills/user-confirmation.md ,
  https://docs.workato.com/en/agentic/agent-studio/connectors/workato-skill-connector/start-workflow.md
  This is the plan-P2 native flip; it is per-recipe, so the P1 table drives it 1:1. The flip
  itself is a recipe-trigger field change (AIRO `recipe_builder_set_input_field` on the trigger
  step, or one recipe push) — batched over the 57 recipes once Josh approves.
- **(B) Genie instruction — supporting, never sufficient.** A Job-description line ("before any
  destructive skill, collect all inputs and present a summary") improves the confirmation
  quality (docs best practice) but is prompt-level and bypassable; it is never the control.
- **(C) MCP tool layer — covers the non-genie vector.** Skills surfaced through an MCP server
  (and AIRO MCP tools like `data_table_delete`) bypass the Start-workflow flag entirely. The
  plan routes these through the same Jira approval gate as headless genies; enforcement there is
  permission-scoping of the MCP server / connection, not the flag.

Class mapping used in table 2:
- Standard scoped writes (records, tables, messages, tickets): flag (A) alone.
- Generic executors (arbitrary SQL, Dev API executor, on-prem invoke): flag (A) PLUS a
  recipe-level guard — the recipe must validate the requested statement/method against an
  allowlist before executing; flag alone still lets an approved-looking generic call do anything.
- Headless/delegation skills (assign-task-to-genie, recipe-invoked genies): flag (A) is
  documented as inert on that path — user confirmations do not execute without a user present
  (docs "Limitations"). These carry the Jira gate (P2) instead; table 2 marks them.

## 3. Audit-stream watchdog sketch (plan P3)

- **Stream read:** job history per skill recipe — `GET /api/recipes/<id>/jobs` returns job id,
  started/completed timestamps, and a title that carries the invocation context
  (`Workato Skill: start workflow: Genie ID=..., Conversation ID=..., Call ID=...`).
  Verified live against recipe 83074639. Workspace audit-log endpoints
  (`/api/audit_logs`, `/api/activities`) 404 on this token — job polling is the available stream.
- **Detection rule:** a job on a P1-destructive-classified skill recipe (the 57) where the
  execution lacks a confirmation artifact:
  (a) conversation ID is `mcp_mock_*` / absent (MCP-gateway or headless invocation, not a
  confirmed chat), or (b) the calling context is a recipe (assign-task/agent-orchestration
  path — flag cannot fire), or (c) the skill is flag-off AND conversation-invoked.
  Rule (c) is the "flag flipped but not yet verified" case; (a)/(b) are the structural blind
  spots the Jira gate owns.
- **Cadence + pattern:** 15-minute scheduled poll in the Estate Monitor pattern; snapshot
  destructive-skill job counts + genie state/skills_count diffs; alert on any new job of class
  (a)/(b) or any flag-off chat-invoked destructive run. Count-diffing misses a one-for-one skill
  swap (no skill-identity endpoint — `GET /:id/skills` 404s), so P1 re-runs weekly as the deep
  scan. Known API limits inherited from the plan: no skill-identity endpoint, in-place recipe
  hardening invisible.
- **Existing harness fit:** the workato-watchdog agent already autopsies failed jobs; this adds
  a destructive-execution-lacks-confirmation detector to its read-only sweep. It reports only —
  it never stops or edits (watchdog constitution).

## 4. get_fix_proposals remap (plan P4)

- What it is: skill recipe [83074639](https://app.workato.com/recipes/83074639)
  (`get_fix_proposals`), Drift Fix folder 35202337, project 10593549. READ-ONLY skill: reads
  data table DriftFix_Change_Log (157369), joins DriftFix_Apply_Log filtered by change_id,
  optional run_id/change_id/table_name/status filters; returns proposals with review-workflow
  fields and per-fix SQL + rollback SQL.
- Live state verified 2026-10-22: `running=true` but last run 2026-10-14, 6 ok / 17 failed.
  Still hard-wired to the DEAD table **157379** (`DriftFix_Apply_Log` pre-recreation); zero
  references to the recreated **163016**; field name still `query_id` (rename to
  `snowflake_query_id` not applied). Next invocation fails "Data table not found"
  (latest failure j-Ac4arQMK-oXP9BB-CD).
- What remapping involves (dev-side, no genie stop needed): pull the recipe, re-point the
  DriftFix_Apply_Log reference 157379 -> **163016**, remap the changed column field IDs
  (including `query_id` -> `snowflake_query_id`), keep the optional filters intact, push, then
  Test-run once and confirm a clean trace. It is a read-only surface — safe remap, no
  confirmation flag required on it itself. Caveat: because the genie is started, the skill is
  LIVE-served; the push is a hot-swap on a running recipe (workato-hot-swap pattern:
  stop -> push -> start -> verify, all dev-delegated) OR AIRO edit while running. Do this in the
  build phase, not now (out of spike scope).
- Note: MCP tool-description caches do not propagate on push (memory:
  workato-mcp-tool-description-snapshot) — if this skill is served through an MCP server, the
  served description needs an explicit edit after remap.

## BLOCKED ON: Josh-Joel sync re Drift Fix Genie re-stop

**BLOCKED ON: Josh-Joel sync re Drift Fix Genie re-stop.** The build phase (P2 flag flips, P3
watchdog activation, P4 remap execution) is gated on the plan's first DECISION: who restarted
Drift Fix Genie gin-AbWxkCLd-8wRwmG-CD (started again 2026-10-20 23:49 PT), and whether it gets
re-stopped pending attribution. No unilateral re-stop was made in this spike; the genie remains
running and its one skill ([DRIFT FIX] revise_fix, 83234662) is serving. Everything in this doc
is design + evidence; nothing was flipped, stopped, or written.

## Not verified

- Runtime behavior of classified skills: verdicts are static (name/description/connector
  evidence), not job-trace proven per skill. The 57 destructive rows are review targets, not
  final security verdicts.
- Skills whose genies share a home folder are attributed by folder convention (recipe_builder_init_skill
  behavior); the genie->skill attachment list endpoint does not exist (404), so per-genie
  attachment is inferred, not read from an attachment record.
- The 202 non-skill genies (278-76) may have skills attached via non-folder mechanisms — none
  found, none claimed.
- Watchdog rule (a) `mcp_mock_*` conversation IDs were observed in one job title; full
  enumeration of invocation-context patterns across all 57 recipes is build-phase work.
- Raw data: /tmp/p1-spike/merged_results.json (+ results1-5.json, deep/ reads).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - projects/genie-destructive-gate/p1-spike.md — BSYS-29829 P1 spike DONE 2026-10-22 (dev read-only): 278 genies inventoried, 145 unique skill recipes, **57 unique destructive recipes on 55 genies** (Snowflake arbitrary-SQL x3 recipes, Dev API executor 83113395, on-prem Invoke tool, assign-task delegation); flag-placement design (Start-workflow native flag + allowlist guard for generic executors + Jira gate for headless), watchdog sketch (per-recipe job polling; audit-log endpoints 404), get_fix_proposals 83074639 remap spec (still on dead table 157379). **BUILD PHASE BLOCKED ON: Josh-Joel sync re Drift Fix Genie re-stop**