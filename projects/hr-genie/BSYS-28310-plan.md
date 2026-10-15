# BSYS-28310 plan — MCP Skill: Show job compensation range within a Job Change BP review (Manager)

Posted to Jira 2026-10-09 (comment 1134666). Status: BUILD COMPLETE in dev (2026-10-10, comment 1134843), functionally verified with live traces; promotion gated on MCP-server attachment + UAT needing a live Job Change event in dev.

## Context

Read-only MCP skill composed onto the existing inbox-review platform:

- FUNC | Resolve Inbox Compensation Context https://app.workato.com/recipes/79410133 — enriches Job Change notifications with the employee's current/proposed comp (event-scoped, fixed backend identity, never authorizes).
- Event scoping: Get Inbox Event Context https://app.workato.com/recipes/74588258, Check Event Still Awaiting Person https://app.workato.com/recipes/74506696.
- VUA read pattern: view_benefit_elections https://app.workato.com/recipes/82759555 (fetch under caller's identity; Workday security decides).

## Business Requirements

- Manager reviewing a direct report's Job Change BP can demand and receive the target job's comp range: min/mid/max + currency when Workday has it.
- Response tied to the exact BP instance, formatted for Slack.
- Nothing for jobs/employees outside the manager's scope; unauthorized callers get a clear non-exposing message.

## Technical Requirements

- New read-only on-demand skill recipe in folder 30326966. Two gates before any comp value returns:
  1. Event-scope gate: caller must be the current awaiting approver on the exact businessProcessEvent (74506696/74588258). No event correlation, no data.
  2. Data-authorization gate: range read runs under the manager's VUA connection (workday_rest 19218617, VUA mode) so Workday domain/role security is the authorization of record. NEVER fetch comp via a fixed integration identity.
- API contract: SOAP Get_Compensation_Grades requires 'Set Up: Compensation Packages' domain (managers don't hold it; fails closed under VUA) so it is NOT primary. Primary = report/WQL compensation-range surface (job profile/grade min/mid/max + currency) under VUA; exact tenant source verified at build. Target grade/profile from BP event context.
- Failure semantics: Workday denial returns a non-exposing error, never a stack trace or existence hint.
- Masking/audit: comp values render in Slack only; nothing with numbers persisted. Audit row: event WID, manager, target job profile, granted/denied, timestamp. mask_data on any step that could echo values into job logs.
- Telemetry: standard MCP skill coverage via the shared emitter.

## Acceptance Criteria

- [ ] Authorized manager invoking conversationally receives min/mid/max + currency tied to the BP instance.
- [ ] Non-approver caller refused before any comp read.
- [ ] Comp-domain-denied manager gets a clear non-exposing error; no leak.
- [ ] No comp values in logs/ledgers/tables; audit carries metadata only.
- [ ] Read-only end to end; no Workday write path.
- [ ] Test cases: authorized manager, non-approver, domain-denied, missing range data.

## UAT Evidence

- Live Job Change event in dev: event-gate traces (authorized + non-approver), VUA comp read trace both sides, Slack response tied to BP instance, audit-ledger rows with metadata only.

## Risks

- Authorization question (is the reviewing manager entitled to the range?): entitlement decided ONLY by Workday domain security under the manager's VUA identity, on top of the event-scope gate; the skill adds no entitlement. Tighter policy later = config change, not redesign.
- A manager-authorized range report may not exist in the tenant (custom report = HRIS-owned Workday config); fallback is a clean "not available" response, flagged to Josh.
- Leak surface is the Slack thread, the accepted BP-review channel.

## Points

5 (2-3 days): two-gate authorization design, VUA report/WQL integration, Slack formatting, audit integration, four-case UAT.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Build status (updated 2026-10-11, fleet re-verification)

Built 2026-10-10 after Josh's kickoff approval. Full report on the ticket (comment 1134843).

- Skill recipe: view_job_compensation_range https://app.workato.com/recipes/82959755 (skill handle skl-Absp3hhd-x6gEfC-CD, folder 30326966). Disposable contract probe PROBE | Comp Range WQL Contracts https://app.workato.com/recipes/82959722 STOPPED after evidence. Reused unchanged: 74588258, 74506696, telemetry emitter 78563374, audit table HR Genie | BP Status Audit Log v2 (table 156371).
- Two gates as planned: event-scope (74588258 CURRENTLY_AWAITING + Job Change type, then 74506696 awaiting-approver check) then the range read on workday_rest 19218617 under the manager's VUA identity (personalization verified true in saved config after flip). workday 19760013 fixed identity carries comp-free event context only. mask_data on comp-bearing steps; audit rows metadata only.
- Tenant finding (per the plan's risk clause): NO manager-readable comp-range surface exists in the dev tenant. WQL allCompensationGrades "DataSource is inaccessible" under fixed identity; 403 under VUA identity; control allWorkers WQL also 403 (denial is Workday domain security, not per-source); SOAP Get_Compensation_Grades "not authorized" under VUA (fail-closed as predicted); staffingBusinessProcess.grade_Proposed is an invalid WQL field. The skill always attempts allCompensationGrades with a sentinel filter (never an unfiltered catalog) and maps denial to a clean non-exposing RANGE_NOT_AVAILABLE/UNAUTHORIZED response; when HRIS ships a manager-authorized range report the swap is one WQL string (step 34) plus a grade pill.
- Verified live: test run against a real awaiting event (a Request Compensation Change) — telemetry fired, caller resolved under VUA, process-type gate refused cleanly WRONG_PROCESS_TYPE (job j-AbspLebd-RLBp6h-CD); audit row 1b763734 read back, metadata only.
- Re-verified 2026-10-11 via recipe_get: recipe 82959755 RUNNING. MCP server check: Workday End-User (mcps-AYbrRaxY-dhF-CD, server id 7435) still lists 27 tools and view_job_compensation_range is NOT among them — attachment still pending.
- Remaining before promotion: attach to MCP server 7435 via the Genie/tool picker (full-replacement-set trap — snapshot the 27-tool list first); UAT four-case set blocked on a live Job Change event in dev (discovery showed only Title Change / Leave / Comp Change / Time Off); re-verify workday_rest personalization true after any further push (wipe-on-push trap). Pre-existing drift noted for a separate look: update_my_contact_info shows vua_required false on the server snapshot.
- Story points: field customfield_10057 = 3 (plan section says 5; field was set lower than the plan's estimate — field stands).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [BTOps Workflow Guide](../../../kb-corpus/confluence/intbt/2557640742-btops-workflow-guide.md)
- [BT Workflow Enablement Guide](../../../kb-corpus/confluence/intbt/2557640730-bt-workflow-enablement-guide.md)
- [Changelog for BSYS-16667: CBP - Automated Provisioning - AHQ BT Assets](../../../kb-corpus/confluence/intbt/1107821504-changelog-for-bsys-16667-cbp---automated-provisioning---ahq-bt-assets.md)
- [[HR-18] Set Up Change Job Business Process in Workday and modify HTR-W recipes for downstream process](../../../kb-corpus/confluence/intbt/2602958962-hr-18-set-up-change-job-business-process-in-workday-and-modify-htr-w-recipes-for.md)
<!-- kb-bridges:end -->
