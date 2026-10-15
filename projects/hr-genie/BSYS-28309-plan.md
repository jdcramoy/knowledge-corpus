# BSYS-28309 plan — Genie Skill: Make Leave of Absence notifiable and approvable (Manager)

Posted to Jira 2026-10-09 (comment 1134665). Status: BUILD COMPLETE in dev (2026-10-10, comment 1134841), functionally verified with live traces; promotion gated on UAT items needing real identities.

## Context

Extend-and-verify on the existing notification/approval platform, not a new stack:

- Discovery: REC | Inbox Task Discovery Hub https://app.workato.com/recipes/74482795 — tenant-wide WQL over allBusinessProcessTransactionsAwaitingPersons, NO BP-type filter; only exclusion is Time Off (TYPE == 'Request Time Off'). LoA tasks already flow.
- Ledger/dispatch/reconcile: Inbox Task Notification Log https://app.workato.com/data_tables/614f89f8-0225-41b9-b7b2-80d14c9331d7, Dispatch gate https://app.workato.com/recipes/82059061, Reconciler https://app.workato.com/recipes/74506733.
- Recipient routing incl. delegation: Resolve Business Process Assignee https://app.workato.com/recipes/74437245 (Workday awaitingPersons already reflects active delegations).
- Approval: action_inbox_task https://app.workato.com/recipes/74380076 (VUA-write, preflight ownership re-read, refuse-list covers Time Off), list_my_pending_tasks https://app.workato.com/recipes/74324952.
- Context enrichment siblings: Resolve Inbox Compensation Context https://app.workato.com/recipes/79410133, Get Inbox Event Context https://app.workato.com/recipes/74588258.

## Business Requirements

- Manager Slack notification on direct-report LoA submission: name, leave type (FMLA/disability/parental/other), start/end dates, act-from-Slack guidance.
- Approve/deny written back to Workday under the manager's VUA identity, confirm gate, deny requires reason.
- Routing follows Workday awaiting-person assignment incl. delegations; no unauthorized visibility.
- Ledger every notification/decision with timestamps, request IDs, BP instance.
- Surface only what Workday returns for the approval step; no medical details beyond that, no cross-manager leakage.

## Technical Requirements

1. Verify LoA flow-through (Discovery Hub row processor, recipient resolution) and fix any LoA type mishandling.
2. New FUNC | Resolve Inbox Leave Context in folder https://app.workato.com/recipes?fid=32175654, sibling of 79410133: event-scoped WQL/Get_Inbox_Event_Context returning leave type, dates, current step for one businessProcessEvent WID; read-only, fixed backend identity.
3. Leave-type-aware message template; approval deep-links into the HR Genie conversation; decision executes via action_inbox_task pattern (ordinary vs Consolidated per stepType, preflight re-read, deny reason, confirm gate).
4. Verify action_inbox_task accepts LoA Approval/Consolidated Approval steps; extend allowlist explicitly if refused.
- Identity: service-identity reads (74588258 model); write is VUA under the approving manager; delegation authorization delegated to Workday.
- Telemetry: reuse ledger chain incl. Ledger Correlator 2 - Notifications https://app.workato.com/recipes/82863630.

## Acceptance Criteria

- [ ] Direct-report LoA submission produces a manager notification with name, leave type, dates, act-from-Slack guidance.
- [ ] Decision writes back to Workday under manager VUA identity; confirm step + deny reason; Workday shows the decision.
- [ ] Active delegation routes to the delegate as notified, authorized approver.
- [ ] Every notification/decision ledgered (event WID, step WID, timestamps, outcome).
- [ ] No data beyond the approval-step return; cross-manager requests never visible.
- [ ] Leave-type rendering verified for FMLA, disability, parental, generic.

## UAT Evidence

- Live LoA request in dev: Discovery Hub trace, ledger row, Slack message, action_inbox_task trace with Workday write-back, post-decision Workday state, delegated-approver case, rerun dedupe from the Dispatch gate.

## Risks

- LoA approval step may be a Consolidated Approval variant; step type confirmed against a real LoA event at build time.
- Leave type/dates may not be in approval-step context; fallback to event-scoped WQL; Workday-withheld medical details stay hidden by design.
- Discovery Hub's pre-cutoff exclusion question applies to LoA too; unchanged.

## Points

3 (~1 day): one new context function, a message template, end-to-end LoA verification pass.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Build status (updated 2026-10-11, fleet re-verification)

Built 2026-10-10 after Josh's kickoff approval. Full report on the ticket (comment 1134841).

- New asset: FUNC | Resolve Inbox Leave Context https://app.workato.com/recipes/82959603 (folder 32175654) — read-only, fixed backend identity. Returns context_state, leave_type (Workday's own leaveType only, never inferred), leave_type_source, leave_reason, pending_steps, on_leave_now, leave_start_date, leave_end_date_estimated. Dedicated LOA WQL sources are ISU-inaccessible in the tenant; allWorkers is the validated leave-date path.
- Wired into FUNC | Process Inbox Task Row https://app.workato.com/recipes/74482074: fail-open enrichment block (gated on BP descriptor containing "Leave of Absence", LEAVE_ENRICHMENT_FAIL_OPEN on error) between comp enrichment and summary build; Detail Summary gained leave type / leave start / estimated end / on-leave-now lines, so the Slack message and ledger row stay in lockstep. Non-LoA rows skip the extra reads.
- Approval path verified needing no change: action_inbox_task https://app.workato.com/recipes/74380076 refuses only Request Time Off, accepts Approval and Consolidated Approval steps, requires deny reason, re-reads the live inbox, delegates authorization to Workday's awaiting-person assignment.
- Live evidence: ledger rows for both live LoA events; rebuild job j-Absp9HPd-49LBrP-CD + function job j-AbspEDgm-kmdX9B-CD (ledger row f75983a3, SENT); fail-open proven for real when the function call hit WRF00409 (stopped-recipe-function) on the first post-push cycle — notification still sent, error logged.
- Honest findings: Workday returns leaveType EMPTY in the awaiting-persons projection for the live events, and a pending LoA has no leave dates yet (by design, message shows only what Workday returns). Telemetry: QUIET coverage entry for the read-only function.
- Re-verified 2026-10-11 via recipe_get: recipe 82959603 RUNNING.
- Remaining before promotion: a live LoA approve/deny from Slack by a real awaiting manager; one APPROVED LoA case to see typed leave-type/date lines render; one delegated-approver LoA case.
- Story points: field customfield_10057 = 5 (plan section says 3; the field was set higher than the plan's estimate — field stands).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Proactive Notifications and Lifecycle Tracking](../../../kb-corpus/confluence/extbt/2939650050-proactive-notifications-and-lifecycle-tracking.md)
- [[HR-19] Recruiting Genie](../../../kb-corpus/confluence/intbt/2567209028-hr-19-recruiting-genie.md)
- [PRD - RunIt Genie](../../../kb-corpus/confluence/intbt/2468840430-prd---runit-genie.md)
- [Workato Genie Workspace (Deal Closing, Provisioning, Billing, Revenue Recognition)](../../../kb-corpus/confluence/extbt/711754189-workato-genie-workspace-deal-closing-provisioning-billing-revenue-recognition.md)
<!-- kb-bridges:end -->
