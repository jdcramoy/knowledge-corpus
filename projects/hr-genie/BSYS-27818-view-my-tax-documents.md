# BSYS-27818 — MCP Skill: View my tax documents (Employee)

Triage pass 2026-10-11. Plan status: build executed under the approved Option 1 re-scope (kickoff 2026-10-10, build comments on the ticket). This file captures the re-verified live state, the WSDL-index confirmation from today, and the remaining-work plan.

## The ask (as re-scoped, Option 1)

Employee asks whether they are enrolled in electronic delivery of their year-end tax forms (W-2, 1095-C). The skill returns per-form-group delivery elections (print consent plus override flag), worker=me scoped. It never returns the documents or files; download requests route to the Workday UI. Phase 2 (document download) is filed as BSYS-29494, blocked on Workday RaaS report authoring.

## WSDL index re-check (2026-10-11, fresh query of the pre-built JSON index, never raw WSDL)

Searched the v46.2 index for tax-document operations. The Payroll service exposes exactly three: Put_Tax_Document_Delivery, Get_Tax_Document_Deliveries, Import_Tax_Document_Delivery — all delivery-method election operations. No operation on the exposed surface returns a tax-document file for a worker. This re-confirms the ticket's exhaustive 2026-07-27 sweep; the re-scope stands and Phase 2 stays RaaS-blocked.

## Current estate state (re-verified live 2026-10-11, fresh reads)

- Recipe [view_my_tax_document_elections 82959476](https://app.workato.com/recipes/82959476), dev project 15643451, folder [30326966](https://app.workato.com/recipes?fid=30326966), Running: true, saved v1. Serialization confirmed today: get_worker(me) identity with 32-char WID guard, SOAP Get_Tax_Document_Deliveries scoped in-request via Request_Criteria/Worker_Reference (WID), two-level empty state (noElections), catch returning a clean wrapped error, all steps mask_data, no worker parameter on the contract. Tool description says DELIVERY ELECTIONS ONLY and routes download asks to the Workday UI.
- Not yet registered as a tool on the [Workday End-User MCP server](https://app.workato.com/mcp/mcps-AYbrRaxY-dhF-CD) — today's 27-tool read-back has no tax-document-elections tool.
- Zero jobs run so far: the live tests were deferred on 2026-10-10 when the shared Orca browser was contended by a parallel session. This is the largest remaining gap.
- Open serialization question from the build: Response_Group="Include_Reference" drops after push; descriptors ride on include_descriptors_in_response=true. First test trace must confirm Form_Group descriptors still arrive.

## Remaining work (in order)

1. Editor Test (recipe page caret dropdown or a test case + `wt testcases run --recipe 82959476`): elections path on Josh's account, confirm Form_Group descriptors present in the trace.
2. Empty-state test-case run.
3. Register the tool on the End-User MCP server; read-back the served description says "delivery elections", not "tax documents" (tool descriptions do not track recipe-description edits; re-save the tool if the recipe description changes). Set VUA Required: Yes and verify it holds.
4. Genie TEST-tab E2E routing check (Josh's UAT): "show my tax documents" shows elections; download ask gets the honest unavailability message.
5. Promotion via the BT managed process with the standard VUA post-push re-check.

## Story points

2 (post-decision build is a small single-read skill cloning the view_tax_elections pattern; the API surface was de-risked by the ticket's own research; already set at plan time).

## Acceptance criteria (remaining)

- [ ] Live editor Test with trace: elections list plus Form_Group descriptors for Josh's account.
- [ ] Empty-state run returns the friendly noElections message.
- [ ] Tool registered with the delivery-elections description and VUA Required: Yes, verified on read-back.
- [ ] Genie E2E routing: elections shown, download ask refused honestly.
- [ ] Promotion request staged with evidence.

## UAT Evidence

Not gated on new Workday security grants beyond what the read path already uses. Evidence to collect: job traces for the elections path and empty state, the tool-description screenshot, the Genie transcript for the routing check. What gates nothing but should be noted: Josh's own account has real elections per the 2026-07-27 research, so the elections path has a live fixture.
