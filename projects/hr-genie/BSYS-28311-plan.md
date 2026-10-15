# BSYS-28311 plan — MCP Skill: Show peer compensation within a Job Change BP review (Manager)

Posted to Jira 2026-10-09 (comment 1134668). Status: BUILD COMPLETE in dev (2026-10-10, comment 1134846), functionally verified with live traces; promotion gated on MCP-server attachment + UAT needing a live Job Change event in dev.

## Context

Twin of BSYS-28310 (https://workato.atlassian.net/browse/BSYS-28310, plan comment 1134666); reuses its two-gate design unchanged. Employee's own comp already event-scoped-resolvable: Resolve Inbox Compensation Context https://app.workato.com/recipes/79410133; event verification https://app.workato.com/recipes/74506696, https://app.workato.com/recipes/74588258; VUA read pattern https://app.workato.com/recipes/82759555.

## Business Requirements

- Peer comp profiles on demand during a Job Change review, scoped to the BP instance, Slack-formatted.
- Peers by configured match criteria (job profile, supervisory org, or both).
- Only Workday-authorized data; never non-direct reports or out-of-scope employees.
- Audit per access: manager, timestamp, BP instance, peers queried.
- Empty peer set: clear message, no names/data.

## Technical Requirements

- Two-gate architecture as BSYS-28310: event-scope gate on the exact businessProcessEvent, then peer comp read strictly under the manager's VUA identity (Workday domain security = authorization of record). No fixed-identity comp fetch, ever.
- Peer resolution: match criteria from BP event context, constrained to the caller's own supervisory org; candidates computed first, each row fetched under VUA; Workday-withheld rows silently absent, never an error or name.
- Surface: report/WQL worker-compensation source under VUA (same tenant verification as BSYS-28310; Get_Compensation_Grades is admin-domain, unusable by managers).
- OPEN POLICY QUESTION (Josh/HR decision, not invented): peer definition entitled to individual-level visibility. Recommended default: peers = the manager's own current direct reports sharing the subject's job profile or grade, visible only where Workday security grants it. Broader views (cross-org, org-wide benchmarks) OUT of scope; if ever wanted, aggregate-only stats (median/range, no names) behind an explicit HR decision — individual cross-org comp is a pay-equity exposure.
- Masking/audit: comp values in Slack thread only; audit row = manager, event WID, BP instance, match criteria, peer Worker IDs, granted/denied, timestamp, no values. mask_data on comp-bearing steps.

## Acceptance Criteria

- [ ] Authorized manager receives matched peer comp profiles tied to the BP instance.
- [ ] Non-approver refused before any comp read; Workday-hidden peers never appear.
- [ ] No cross-org/out-of-scope comp (verified by test case).
- [ ] Audit row per access with peers queried; no comp values persisted anywhere.
- [ ] Empty peer set returns a clear message with no names/data.
- [ ] Test cases: matched-peer return, non-approver refusal, cross-org exclusion, empty peer set, audit-row content.

## UAT Evidence

- Live Job Change event in dev: event-gate traces (authorized/non-approver), VUA peer-comp read trace with per-row Workday decisions, Slack response tied to BP instance, audit rows with peer IDs and no values, empty-peer-set trace.

## Risks

- Authorization question is the core risk: individual peer comp visible only where Workday domain security grants it under VUA, on top of the event gate; the skill grants nothing. Broader peer definition is an open Josh/HR decision; recommended default stated above.
- Match criteria affect result quality; shipped as config (default job profile + supervisory org), tunable without redesign.
- Manager-authorized comp report may need HRIS-owned Workday config; without it, clean not-available response.
- Pay-equity exposure if the peer definition drifts broad; guarded by scope constraint + audit row.

## Points

5 (2-3 days): shares BSYS-28310's gates but adds peer matching, per-row VUA fetching, audit-with-peers record.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Build status (updated 2026-10-11, fleet re-verification)

Built 2026-10-10 after Josh's kickoff approval. Full report on the ticket (comment 1134846).

- Skill recipe: show_peer_compensation https://app.workato.com/recipes/82959783 (skill handle skl-AbsoshYG-49rnMD-CD, folder 30326966). Audit table: HR Genie | Peer Comp Access Audit Log (table 158558, https://app.workato.com/data_tables/3d094eb6-94c7-423c-9f7b-58f00eccccf4) — manager WID/email, event WID, BP type, subject, match criteria, peer WIDs queried, decision, reason, peers-returned count; metadata + WIDs only, NO comp values persisted anywhere. Telemetry via shared emitter 78563374 (tool_name show_peer_compensation).
- Two gates as planned: event-scope (74588258 + 74506696) then per-peer Get_Workers Include_Compensation fetches under the manager's VUA identity (workday_rest 19218617 VUA; workday 19760790 fixed for comp-free context). VUA personalization verified by package re-export after the final push. Withheld peers silently absent — counted arithmetically (matched minus granted) instead of catch-block bookkeeping.
- Deviation from plan (tenant findings, evidenced): peer narrowing ships as the subject's supervisory organization, NOT job profile — WQL proved `manager` is not a valid allWorkers field and `jobProfile` selects empty on this tenant. Org WID comes from the event's staffing context; org filter proven live (9 members of SUP_Infrastructure (CI/CD), job j-AbspGdoL-4wNG6J-CD); each peer's job profile returns from the per-peer fetch for display. Match criteria stay config-tunable.
- Live evidence: per-worker comp shape via Get_Workers Include_Compensation (job j-AbspLaf6-dJobgM-CD); VUA identity proof worker=me resolves Joshua Cramoy (job j-AbspMhcJ-YkQEPF-CD).
- Re-verified 2026-10-11 via recipe_get: recipe 82959783 RUNNING. MCP server check: Workday End-User (mcps-AYbrRaxY-dhF-CD, server id 7435) still lists 27 tools and show_peer_compensation is NOT among them — attachment still pending.
- Remaining before promotion: MCP-server attachment (full-replacement-set trap — snapshot the tool list first); authorized-path live trace + refusal/empty-set UAT cases blocked on a live Job Change event in dev awaiting the VUA caller; delete throwaway probe TEST | BSYS-28311 WQL probe https://app.workato.com/recipes/82959838 after UAT (currently stopped). Cross-org exclusion is by construction (WQL org filter + per-row VUA re-check); dedicated cross-org test case runs at UAT.
- Story points: field customfield_10057 = 3 (plan section says 5; field was set lower than the plan's estimate — field stands).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [HR Genie and Workday MCP - Architecture Overview](../../../kb-corpus/confluence/extbt/2862809419-hr-genie-and-workday-mcp---architecture-overview.md)
- [Workato MCP Server Development Framework](../../../kb-corpus/confluence/extbt/2159444213-workato-mcp-server-development-framework.md)
- [[LEG-4] Nova | MCP Tools](../../../kb-corpus/confluence/intbt/2091548689-leg-4-nova-mcp-tools.md)
- [[WIP] BT Change Management Process — As-Is & Standards](../../../kb-corpus/confluence/extbt/2588114972-wip-bt-change-management-process-as-is-standards.md)
<!-- kb-bridges:end -->
