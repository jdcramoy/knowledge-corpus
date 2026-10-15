# BSYS-27818 — MCP Skill: View my tax documents (Employee) — Technical Plan

Plan posted to Jira 2026-10-09 (comment 1134663). Josh has since approved the Option 1 re-scope and the build was EXECUTED (kickoff 2026-10-10, comments 1134811/1134813: recipe 82959476 saved, live tests deferred; Phase 2 filed as BSYS-29494). Morning triage pass 2026-10-11 (comment 1134955). Second sweep 2026-10-11: re-verified fresh (recipe_get + mcp_server_get), no state change — recipe Running, still zero live tests, still NOT registered on the End-User MCP server (27 tools, no tax-elections tool). Story Points field aligned to the plan estimate (5 → 2). Status: plan ready, awaiting Josh's build authorization.

## Context

Employee-as-Self read skill: view available tax documents (W-2, 1095-C). Epic
BSYS-26808. Story has been BLOCKED since 2026-07-27: research in the ticket proved
`Get_Tax_Document_Deliveries` returns only a delivery-method election per form group
(print consent + override flag), not document instances — no tax year, status, document
ID, or file. The exhaustive SOAP sweep found no worker-scoped operation that returns an
actual tax-document file in this tenant.

Estate check this session: the in-session draft recipe 74379505 is NOT saved on the dev
server (recipe_get returns 404) — the build restarts from scratch when resumed. Siblings:
view_tax_elections https://app.workato.com/recipes/74048992 (SOAP read pattern),
list_worker_documents https://app.workato.com/recipes/71289053 (worker-doc pattern; tax
documents are confirmed NOT stored as Worker Documents in this tenant). Folder:
https://app.workato.com/recipes?fid=30326966

## Business Requirements (recommended re-scope — Option 1 from the ticket)

- Employee can ask whether they are enrolled in electronic delivery of their tax forms
  (W-2, 1095-C, etc.) and see the per-form-group election and any override.
- Employee asking for the actual W-2 file gets an honest "not available through this
  channel yet" answer, routed to the Workday UI — no error, no fake data.
- Phase 2 (document download) is a separate story blocked on Workday RaaS report
  authoring — same dependency class as the BSYS-26819 pivot.

## Technical Requirements

New skill recipe `view_my_tax_document_elections` in project 15643451, folder 30326966,
cloned from the view_tax_elections https://app.workato.com/recipes/74048992 read pattern
(worker=me, read-only, no worker parameter).

API contract:

- Identity: REST `GET /workers/me` on `workday_rest` (19218617, VUA) → WID.
- Read: SOAP `Get_Tax_Document_Deliveries` on `workday` (19760790, VUA), scoped in the
  request via `Request_Criteria/Worker_Reference` (WID type) — already confirmed against
  the live schema in the ticket's research; no broad query + client filter.
- Output shaping: one line per Tax_Document_Printing_Election entry — Form_Group
  descriptor (e.g. "W-2 Print Consent"), Override_Default_Delivery flag, plain-language
  electronic-vs-paper statement. Rename the tool/skill away from "tax documents" to
  "tax document delivery elections" so the Genie never promises files.
- Empty state: "no delivery elections on file" friendly message.
- HR Genie instructions: document-download requests route to a clear unavailability
  message (Workday UI remains the path until Phase 2 lands); never to this tool.
- Telemetry: read-only; no audit table. Wiring: register as a tool on the Workday
  End-User MCP server (mcps-AYbrRaxY-dhF-CD).

Decision still owed by Josh before build (from the ticket's three options): Option 1
re-scope (recommended, this plan), Option 2 pause pending a Workday report-author check
on a Tax Documents RaaS report, Option 3 park. This plan is build-ready under Option 1.

## Acceptance Criteria

- [ ] Josh's scope decision recorded on the ticket before build starts.
- [ ] Employee asking about tax-form delivery gets their per-form-group elections
      (electronic vs paper, override flag) scoped to worker=me.
- [ ] No tool parameter can address another worker; data is caller-only in every trace.
- [ ] Requests for the actual document file return the honest unavailability message
      routed to the Workday UI — never a fabricated list.
- [ ] Empty-state message verified with a worker profile lacking elections.
- [ ] Tool name/description on the End-User MCP server says "delivery elections", not
      "tax documents".
- [ ] Phase 2 (download) filed as a separate blocked-on-RaaS story, not built here.
- [ ] Standard dev test + UAT evidence before promotion request.

## UAT Evidence

- Editor Test + test-case run with job traces showing the election list for the test
  worker (Josh's own account has real elections per the 2026-07-27 research).
- Empty-state fixture run.
- Genie TEST-tab E2E: "show my tax documents" conversation routes correctly (elections
  shown; download ask answered with the unavailability message).
- Tool-description snapshot verified on the MCP server page after wiring.

## Risks

- Expectation gap: the tool delivers much less than the original ask; naming and genie
  instructions carry the mitigation.
- Phase 2 remains blocked on a Workday report author; no SOAP path exists (exhaustively
  swept per the ticket) — do not re-litigate inside this build.
- VUA runtime behavior of Get_Tax_Document_Deliveries under end-user OAuth is
  schema-confirmed but not yet run-proven; the editor Test is the proof point.

## Points

2 — post-decision build is a small single-read skill cloning the view_tax_elections
pattern (the ticket's own research already de-risked the API surface). Phase 2 RaaS
discovery is a separate estimate.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato MCP Server Development Framework](../../../kb-corpus/confluence/extbt/2159444213-workato-mcp-server-development-framework.md)
- [MCP Monday: The Content Creation Stack Gets an Enterprise Brain](../../../kb-corpus/changelog/mcp-monday-the-content-creation-stack-gets-an-enterprise-brain.md)
<!-- kb-bridges:end -->
