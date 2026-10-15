# BSYS-26816 — MCP Skill: View total compensation (Employee)

Triage pass 2026-10-11. Plan status: build executed (kickoff 2026-10-10, build comment on the ticket). This file captures the re-verified live state and the remaining-work plan.

## The ask

Employee views their total compensation breakdown (base, bonus, allowance, equity, other components) through the HR Genie, scoped strictly to the authenticated employee, with recurring vs one-time labeled so totals are not misread. This is the most sensitive read surface in the epic: employee-own-only, never a manager context.

## Current estate state (re-verified live 2026-10-11, fresh reads)

- Recipe [view_total_compensation 82959479](https://app.workato.com/recipes/82959479), dev project 15643451, folder [30326966](https://app.workato.com/recipes?fid=30326966), Running: true. Contract confirmed by live probe: Get_Workers Include_Compensation on the VUA connection returns real amounts; SOAP is the final contract. Normalizer covers Salary/Allowance/Bonus/Merit/Commission/Stock (Equity)/Future Payment sections plus Workday summary totals; identity assertion fails closed; all sensitive steps mask_data.
- Tool view_total_compensation (254985) on the [Workday End-User MCP server](https://app.workato.com/mcp/mcps-AYbrRaxY-dhF-CD), **VUA Required: Yes** (confirmed in today's read-back — the drift fixed during the build has held).
- Equity question closed: Stock_Plan_Data is in the standard response group; no Phase 2 RaaS story needed.
- Sensitive-data handling: worker resolved server-side from the caller (worker=me), tool description carries the compensation-sensitivity and employee-only wording, no worker parameter exists on the contract.

## Remaining work (in order)

1. Real end-user scoping UAT: a second identity chatting with the Genie, proving the caller sees only their own compensation. The editor Test runs as the connection owner and cannot prove this.
2. Multi-currency case if a suitable test worker exists; otherwise recorded as unverified.
3. Tool-description snapshot check on the MCP server page after wiring (screenshot pending Josh's pass).
4. Promotion via the BT managed process; post-promotion VUA re-check.
5. Wording check (non-blocking): the MCP server description says "Do not use this server for compensation analysis" — that targets manager-context analysis of others; the tool's own description scopes it to the authenticated employee. Confirm the Genie's tool picker is not confused by the server-level line.

## Story points

3 (~1 day skill build, sibling-pattern clone plus contract probe; already set at plan time).

## Acceptance criteria (remaining)

- [ ] End-user scoping UAT: second identity sees only their own data, trace-verified.
- [ ] Multi-currency case run or explicitly recorded unverified.
- [ ] Tool-description snapshot verified on the MCP server page.
- [ ] Promotion request staged with evidence.

## UAT Evidence

Not gated on new Workday security grants (the read path is proven under the connection owner). The gating item is a second human identity in the HR Genie dev surface. Evidence to collect: Genie transcript, recipe job trace for the second identity, scoping assertion line from the trace.
