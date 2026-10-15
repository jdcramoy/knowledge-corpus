# BSYS-27724 — Manager PTO Reminders: Consolidate Pending Requests into a Single Digest

Ticket: https://workato.atlassian.net/browse/BSYS-27724 (epic BSYS-26808). Status at planning: Backlog. Plan posted to Jira 2026-10-09.

## Context

The Phase 1 PTO notification platform is live in dev (folder https://app.workato.com/recipes?fid=31025335, project 15643451; prod project 15783895). [REC | Time-Off Event Hub](https://app.workato.com/recipes/74094662) runs every 5 minutes over a Workday WQL snapshot and runs three per-row detectors ([Process New Request](https://app.workato.com/recipes/74247462), [Process Decision](https://app.workato.com/recipes/74247862), [Process Reminder](https://app.workato.com/recipes/74248295)). Every send passes the idempotency gate [FUNC | Dispatch PTO Notification](https://app.workato.com/recipes/82202341) and the single messenger choke point [FUNC | Send Genie Event](https://app.workato.com/recipes/74094657). [REC | Approval Escalator](https://app.workato.com/recipes/74248506) re-notifies unactioned NEW_REQUESTs hourly, capped at 2 nudges per request. Today each event is one Slack message per request, addressed conversationally ("reply approve or reject").

## Business Requirements

- A manager with multiple pending time-off requests receives one consolidated digest message instead of one ping per request.
- Each request in the digest stays individually actionable, with no ambiguity about which request an action applies to.
- Existing single-request behavior (immediate NEW_REQUEST ping for a single pending request, DECISION, REMINDER, escalator nudges) is unchanged.
- Digest cadence and grouping window are configurable project properties, finalized at build time.

## Technical Requirements

Recommendation: build the digest as a parallel scheduled job, not as an extension of the hub or the detectors. Why:

- The hub pipeline is per-row by design (BSYS-27656 deliberately extracted single-responsibility detectors), and Dispatch PTO Notification's idempotency is keyed per exact occurrence (event + recipient). A digest is a recipient-level aggregation with its own cadence and its own dedup identity, which is a different contract, not a modification of the per-row one.
- Extending Process New Request to batch would break the occurrence-claim semantics and put the shipped, UAT-gated Phase 1 behavior at risk. The AC explicitly requires that behavior unchanged.
- A parallel job is independently testable, stoppable, and revertable, and can ship to dev without touching any running Phase 1 recipe.

Build:

- New REC | Manager PTO Digest, scheduled per a project property (default: same-run batching at the hub cadence; supporting a daily rollup window as the alternative the ticket names).
- Grouping rule: within the grouping window, a manager with exactly one pending NEW_REQUEST keeps today's immediate single message (conversational approve/reject still works). A manager with 2+ pending unactioned NEW_REQUEST rows gets one digest listing all of them.
- Source of truth is Workday via the ledger plus Always Validate: read PTO Notification Log NEW_REQUEST rows with no recorded Outcome, group by manager, re-verify each is still pending (the same re-verify pattern the escalator uses) before listing. Actioned or cancelled requests are dropped from the digest.
- Delivery reuses the messenger choke point [FUNC | Send Genie Event](https://app.workato.com/recipes/74094657) in notify mode, one call per manager, so enrollment/suppression handling comes for free. Digest sends claim one DIGEST occurrence row per manager per window in the same claim pattern, so a re-run never double-sends.
- Actionability, two paths:
  - If [BSYS-27657](https://workato.atlassian.net/browse/BSYS-27657) (Business Approvals spike, currently Backlog) lands GO: each digest line carries its own approve/reject button card. That is the target state and the only fully unambiguous per-line action.
  - If BSYS-27657 is NO-GO or undecided: ship the digest as an informational rollup that names each pending request (employee, dates, days pending) and points the manager to the HR Genie conversation to action them one at a time via the existing action_time_off_request flow. Do not build multi-request natural-language reply parsing as a stopgap; that ambiguity is exactly what the ticket calls out as fragile.
- Dependency note: BSYS-27657 blocks only the button-card variant. The rollup digest is buildable now and does not conflict with either spike outcome.

## Acceptance Criteria

- [ ] A manager with 2+ pending unactioned requests receives exactly one digest per window listing all of them.
- [ ] A manager with a single pending request is unaffected; the existing conversational message stands.
- [ ] Each digest line names the employee, dates, and days pending, and the action path per line is unambiguous.
- [ ] DECISION, REMINDER, and escalator nudge messages are unchanged (diff-verified before/after).
- [ ] Digest sends are idempotent: a re-run in the same window claims SUPPRESSED and sends nothing.
- [ ] Requests actioned or cancelled before the digest run are excluded (Workday re-verified).
- [ ] Failed digest sends return real FAILED status with the messenger error_class contract (RECIPIENT_SUPPRESSED / RECIPIENT_NO_GENIE_ACCESS / DELIVERY_ERROR) so rows can be parked/retried by the reconciler, never silently dropped.
- [ ] Cadence and grouping window are project properties, changed without a code edit.

## UAT Evidence

- Controlled dev scenario: seed 3 pending requests for one manager, capture the digest job trace and the single delivered Slack message listing all 3.
- Idempotency: second digest run in-window returns claim SUPPRESSED with no second Slack message.
- Exclusion: action one request in Workday, re-run, confirm the digest drops it.
- Regression: DECISION and nudge job traces before/after, diff-verified unchanged.
- Single-request path: a manager with one pending request still gets the immediate individual message.

## Risks

- Actionability is gated: without button cards the digest is informational; if a manager replies "approve" against a list, the Genie must refuse and ask for one request at a time. Mitigation: explicit wording in the digest message.
- Threshold choice (2+) needs Josh's product sign-off at kickoff; it is a judgment call, not derivable from the ticket.
- Ledger growth of one row per manager per window is trivial but should follow the existing log-hygiene purge pattern.
- Time-to-first-notice: with same-run batching there is no added delay; a daily-rollup window would delay first notice, so ship same-run batching as the default and treat daily rollup as an opt-in knob.

## Points

5 — a new scheduled digest job plus ledger grouping, Workday re-verify, claim idempotency, and a controlled multi-manager UAT; about 2-3 days.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Proactive Notifications and Lifecycle Tracking](../../../kb-corpus/confluence/extbt/2939650050-proactive-notifications-and-lifecycle-tracking.md)
- [[HR-2] Reminders for Employees with Terminated Managers](../../../kb-corpus/confluence/intbt/533659746-hr-2-reminders-for-employees-with-terminated-managers.md)
- [New Workato Features: HTTP - Send Request and wait for response | APIM log replication | Audit log replication V2 | On-prem groups & agents | RLCM repeatable recipes start | Require base URL for HTTP connections | Provided realtime tasks usage data](../../../kb-corpus/confluence/intbt/265060513-new-workato-features-http---send-request-and-wait-for-response-apim-log-replicat.md)
- [[HR-14] Rework recipes in Workato AHQ | BT and HR (Sensitive) to switch from Namely to Workday](../../../kb-corpus/confluence/intbt/2295332873-hr-14-rework-recipes-in-workato-ahq-bt-and-hr-sensitive-to-switch-from-namely-to.md)
<!-- kb-bridges:end -->
