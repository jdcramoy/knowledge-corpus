# BSYS-26816 — MCP Skill: View total compensation (Employee) — Technical Plan

Plan posted to Jira 2026-10-09 (comment 1134661). Build has since been EXECUTED (kickoff 2026-10-10, build comment 1134822: recipe 82959479, SOAP contract probe-proven, UAT in progress pending second-identity scoping proof). Morning triage pass 2026-10-11 (comment 1134954). Second sweep 2026-10-11: re-verified fresh (recipe_get + mcp_server_get), no state change — recipe Running, tool 254985 VUA Required: Yes held, equity answer stands. Story Points field aligned to the plan estimate (5 → 3). Status: plan ready, awaiting Josh's build authorization.

## Context

Employee-as-Self read skill: view total compensation breakdown (base, bonus, other
components) through the HR Genie. Epic BSYS-26808. Ticket's feasibility notes name REST
worker GET or SOAP Get_Compensation plus a Total Rewards RaaS report. Estate check this
session: no compensation skill exists in dev project 15643451 (32-recipe inventory
verified). Closest siblings: get_my_profile https://app.workato.com/recipes/78626397
(staffing read, no comp amounts) and get_my_payslips https://app.workato.com/recipes/73618136
(paid amounts, not comp plan). Folder: https://app.workato.com/recipes?fid=30326966

## Business Requirements

- Employee asks for their total compensation or specific components (base, bonus, equity)
  and gets current Workday data scoped to themselves.
- Response shows components in a clear readable format, labeled recurring vs one-time.
- Sensitive data only ever returned to the authenticated employee.

## Technical Requirements

New skill recipe `view_total_compensation` in project 15643451, folder 30326966, cloned
from the view_benefit_elections https://app.workato.com/recipes/82759555 read pattern
(worker=me, read-only, no worker parameter, sensitivity wording in the tool description).

API contract:

- Primary: SOAP `Get_Workers` (Staffing) with the `Include_Compensation` response group
  on `workday` (19760790, VUA end-user connection). Verified in the local WSDL index
  (v46.2): Compensation_Data carries Compensation_Package/Grade/Grade_Profile/Step
  references and `Compensation_Element_*` values for Base Pay, Bonus Plan, Commission
  Plan, Allowance Plan, and Calculated Plan — i.e. the component breakdown the ticket
  asks for, worker-scoped, on a connection we already run.
- Scope: `Request_Criteria` worker-scoped to the resolved WID (same scoping style the
  tax-deliveries research confirmed for sibling SOAP ops).
- Identity: worker resolved via REST `GET /workers/me` on `workday_rest` (19218617) —
  never from prompt text.
- The ticket's REST suggestion is downgraded: community/third-party evidence indicates
  the REST worker and compensation/v2 endpoints return profile summaries without
  pay amounts. First build step is a schema probe of both surfaces; SOAP is the default
  contract unless the probe proves otherwise.
- Output shaping: one row per component (name, amount, currency, frequency, recurring/
  one-time label, effective date) plus a plain-language total. Currency from the element
  data; multi-currency workers get per-currency lines, no FX conversion invented.
- Equity/stock: likely absent from the standard Compensation_Data elements. Do not fake
  it. If the schema probe confirms absence, ship Phase 1 without equity and file the
  Total Rewards RaaS report (needs a Workday report author) as a named Phase 2 story —
  same pivot pattern as BSYS-26819/27818.
- Telemetry: read-only; no audit table needed. MCP tool-call logging is inherent.
- Wiring: register as a tool on the Workday End-User MCP server (mcps-AYbrRaxY-dhF-CD);
  tool description states compensation sensitivity and employee-only scoping.

## Acceptance Criteria

- [ ] First build step is a live schema probe proving whether Get_Workers
      Include_Compensation (and the REST alternative) return amounts under the VUA
      connection; contract choice recorded before shaping work.
- [ ] Employee can ask for total compensation or a specific component and receives
      per-component lines (amount, currency, frequency, recurring/one-time label).
- [ ] Results scoped to the calling employee via worker=me; no worker parameter on the tool.
- [ ] Equity/stock components: returned if the probe shows them in the data, otherwise
      explicitly excluded with a Phase 2 story filed — never silently missing.
- [ ] No-balance/no-comp-data case returns a clear friendly message, not an error or blank.
- [ ] Tool registered on the End-User MCP server with sensitivity wording; HR Genie never
      surfaces compensation to a manager context.
- [ ] Standard dev test + UAT evidence before promotion request.

## UAT Evidence

- Editor Test + test-case run with job traces for the total-comp question and a
  single-component question.
- Read-back proving masking/scoping: only the caller's own data in the trace.
- Multi-currency case if a test worker exists; otherwise noted as unverified.
- Tool-description snapshot verified on the MCP server page after wiring.

## Risks

- Equity/stock components likely need a RaaS report (Workday report-author dependency).
- Compensation is the most sensitive read surface yet; VUA scoping must be verified with
  a real end-user call, not the Test panel.
- REST/SOAP contract ambiguity in the ticket — resolved by the mandatory schema probe.
- Amount rounding/frequency confusion (monthly vs annual) — output must carry frequency
  to avoid misreading.

## Points

3 — ~1 day skill build: single read op, sibling pattern clone, plus the contract probe
and output shaping. Phase 2 (RaaS total rewards) is a separate estimate.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato Genie & MCP Development Guide](../../../kb-corpus/confluence/intbt/2423914526-workato-genie-mcp-development-guide.md)
- [Genie usage](../../../kb-corpus/docs/en/pricing/usage-metrics/agent-studio.md)
- [HR Self Service Genie & MCP Server End User Guide](../../../kb-corpus/confluence/extbt/2439020753-hr-self-service-genie-mcp-server-end-user-guide.md)
- [Workato MCP Server Development Framework](../../../kb-corpus/confluence/extbt/2159444213-workato-mcp-server-development-framework.md)
<!-- kb-bridges:end -->
