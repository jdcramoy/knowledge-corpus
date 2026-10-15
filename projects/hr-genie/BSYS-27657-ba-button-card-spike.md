# BSYS-27657 — Business Approvals button-card spike for PTO manager approval

Ticket: https://workato.atlassian.net/browse/BSYS-27657
Parent epic: BSYS-26808 Workday MCP/HR Genie Development. Project file: ../pto-platform.md
Status 2026-10-11 re-triage: Spike 1 executed 2026-10-10, verdict NO-GO. No build follows from this ticket.

## The ask

Evaluate whether Workato's beta Business Approvals feature (the workato_genie connector's create_request / create_task actions) can replace the conversational "reply approve/reject in the Genie thread" PTO approval flow with a structured button card. Explicitly decoupled from the PTO notification platform refactor; no-build gate built into the ticket.

## Current estate state (live, re-pulled 2026-10-11)

- Probe recipe 82959466 (stopped, throwaway, folder 30378861): https://app.workato.com/recipes/82959466 - Scheduler -> workato_genie create_request -> create_task, first with synthetic then with real call_id/requester_conversation_id.
- Throwaway table "HR Genie | Spike Approval Requests (throwaway)" 158538: https://app.workato.com/data_tables/158538
- Spike 1 results (2026-10-10 job traces):
  - create_request works fine from a recipe-only context with no live conversation; creator_id must be the Workato Identity user ID, not the workspace member ID.
  - Synthetic conversation context is hard-validated and rejected: "Unable to determine which chat interface the requester conversation belongs to" (job j-Abso4W8n-zQHWJt-CD).
  - Fully real context also fails: create_task returns a bare platform "Internal error" on both HR Genie chat interface handles, two expiry values, with and without the handle set (jobs j-Abso6GLW-zQHWJt-CD, j-Abso6sQo-FxFWsR-CD, j-Abso8wFD-zWJMeM-CD, j-AbsoACzY-WaEgxY-CD).
  - No button card ever reached Slack; the documented blocking/approval/rejection/expiry outputs stay unverified in this workspace.
- Production mechanism check today: the ticket text says action_time_off_request (71440065) "remains the permanent production mechanism", but that recipe is now titled [Deprecated] and stopped: https://app.workato.com/recipes/71440065. Dependency tracker shows the current prod recipe is action_time_off_request 71538650 in AI Production (folder https://app.workato.com/recipes?fid=32273919) on CON | Workday REST 19234290, with dev successor 78631153. The conversational mechanism lives on under the new recipe IDs; the ticket's reference is stale.

## Verdict per the ticket's own acceptance criteria

NO-GO. Spike 1 disproved the mechanism under test; Spike 2 (service-account Workday attribution sign-off) is moot without a working card. The conversational approval path stays the permanent answer, not a placeholder.

## What remains (Josh calls, no build)

- [ ] Close BSYS-27657 as NO-GO with the reasoning above (status left untouched for Josh)
- [ ] Optionally delete probe assets: recipe 82959466 and table 158538
- [ ] Re-probe only if Workato announces Business Approvals GA (beta internal errors may be fixed later)

Points: 0 build (spike executed); 1 if counting closure bookkeeping.

Not verified: no probe was re-run today; the NO-GO rests on the 2026-10-10 job traces cited. App-Event-initiated orchestration was not tested (ruled out of scope by the spec). Prod recipe 71538650's running state was pulled 2026-10-12 (Running in AI Production, project 15783895) and recorded in ticket comment 1135095; see the pto-platform copy of this plan for the full record.
