# BSYS-27657 — Business Approvals button-card for PTO manager approval (research spike plan)

Ticket: https://workato.atlassian.net/browse/BSYS-27657
Parent epic: BSYS-26808 Workday MCP/HR Genie Development. Project file: ../pto-platform.md
Status 2026-10-12 (refreshed): Spike 1 executed 2026-10-10, verdict NO-GO. Spike 2 moot. No build follows. Close-as-NO-GO recommended to Josh; status left untouched for his call.

## The ask

Evaluate whether Workato's beta Business Approvals feature (the workato_genie connector's create_request / create_task actions) can replace the conversational "reply approve/reject in the Genie thread" PTO approval flow with a structured button card. Explicitly decoupled from the PTO notification platform refactor; no-build gate built into the ticket.

## Spike evidence (2026-10-10 dev probes)

- Probe recipe 82959466 (stopped, throwaway, dev): https://app.workato.com/recipes/82959466 plus throwaway table 158538: https://app.workato.com/data_tables/158538
- create_request works from a recipe-only context with no live conversation. Keeper detail: creator_id must be the Workato Identity user ID (from GET /api/iam/users), not the workspace member ID.
- create_task hard-rejects synthetic context: "Unable to determine which chat interface the requester conversation belongs to" (job j-Abso4W8n-zQHWJt-CD). With fully real Genie context it returns a bare platform "Internal error" on both HR Genie chat interface handles, two expiry values, with and without the handle set (jobs j-Abso6GLW-zQHWJt-CD, j-Abso6sQo-FxFWsR-CD, j-Abso8wFD-zWJMeM-CD, j-AbsoACzY-WaEgxY-CD).
- No button card ever reached Slack. The documented blocking/is_approved/is_rejected/is_expired outputs stay unverified in this workspace.

## Verdict per the ticket's own acceptance criteria

NO-GO. Spike 1 disproved the mechanism under test; Spike 2 (service-account Workday attribution sign-off) is moot without a working card. The conversational approval path stays the permanent answer, not a placeholder.

## Production-mechanism check (verified 2026-10-12)

The ticket text says action_time_off_request 71440065 remains the permanent mechanism, but that recipe is titled [Deprecated] and stopped: https://app.workato.com/recipes/71440065. The live prod recipe is action_time_off_request 71538650, confirmed Running in AI Production (folder https://app.workato.com/recipes?fid=32273919, project 15783895) on CON | Workday REST 19234290, VUA skill trigger with the manager's identity in context: https://app.workato.com/recipes/71538650. Dev successor: 78631153. The conversational mechanism lives on under the new recipe IDs; the ticket's reference is stale.

## What remains (Josh calls, no build)

- [ ] Close BSYS-27657 as NO-GO with the reasoning above (status left untouched)
- [ ] Optionally delete probe assets: recipe 82959466 and table 158538
- [ ] Re-probe only if Workato announces Business Approvals GA (beta internal errors may be fixed later)

Points: 3 set on the ticket at creation (spike + writeup). Build points: 0; closure bookkeeping only.

Not verified: no probe was re-run on 2026-10-11/12; the NO-GO rests on the 2026-10-10 job traces cited. App-Event-initiated orchestration was not tested (ruled out of scope by the spec).
