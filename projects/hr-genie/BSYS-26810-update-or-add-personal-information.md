# BSYS-26810 — MCP Skill: Update or add personal information (Employee)

Triage pass 2026-10-11. Plan status: build already executed (kickoff 2026-10-10, see build comment on the ticket). This file captures the re-verified live state and the remaining-work plan.

## The ask

Employee updates or adds home contact information (address, phone, email) via HR Genie natural language, routed through the Workday Home Contact Change business process, with confirmation before write, friendly validation errors, and submitted/pending vs completed distinguished. Emergency contacts were descoped to a follow-on story.

## Current estate state (re-verified live 2026-10-11, fresh reads)

- Recipe [update_my_contact_info 82959472](https://app.workato.com/recipes/82959472), dev project 15643451, folder [30326966](https://app.workato.com/recipes?fid=30326966), Running: true. Built on the SOAP fallback (Change_Home_Contact_Information, Human_Resources v46.2) after the live probe 403'd the REST staged flow on the VUA connection. Serialization confirmed today: Get_Change_Home_Contact_Information pre-read, harvest + envelope builder, write-path monitor that cancels the open change event on failure (no dangling pending change), audit rows on success and failure paths, confirm gate (requires_user_confirmation=true), worker=me only.
- Audit table [HR Genie | Contact Info Write Audit Log](https://app.workato.com/data_tables/b8870e04-3fe9-4608-a54b-9338aeaab422) (numeric id 158542), 10 columns.
- Tool update_my_contact_info (254984) registered on the [Workday End-User MCP server](https://app.workato.com/mcp/mcps-AYbrRaxY-dhF-CD), now 27 tools; requires confirmation: yes.

## Finding this pass (2026-10-11)

Tool 254984 still shows **VUA Required: No** on the MCP server read-back; every sibling shows Yes. The build comment flagged this on 2026-10-10 and it is still drifted. This is the identity-sensitive class: with VUA off the tool can serve the connection owner's identity to a caller. Fix is a tool-config flip plus read-back, before any UAT.

## Remaining work (in order)

1. Flip VUA Required on tool 254984 in the tool config, then read-back verify (VUA revert-after-push trap class).
2. Workday tenant security grants (HR/Workday admin): enable the Change Home Contact Information (REST Service) and (SOAP Service) initiating actions on the Home Contact Change business process for the employee security group; grant the API-gateway access; self-service domains for Home Address/Phone/Email.
3. UAT: update-address, add-phone, add-email runs with job traces; declined-confirmation run; validation-error run; Workday read-back; audit rows on the success path (failure-path rows already proven).
4. Promotion via the BT managed process; post-promotion VUA mode re-check and smoke.

## Story points

5 (set at plan time: staged multi-endpoint flow, confirm gate, audit table, scope-probe gate, UAT coordination).

## Acceptance criteria (remaining)

- [ ] Tool 254984 shows VUA Required: Yes on read-back and stays Yes after any subsequent push.
- [ ] Workday tenant grants land; the write path is authorized for a real end-user identity.
- [ ] Update-address, add-phone, add-email runs succeed with traces and Workday read-back.
- [ ] Declined confirmation produces no write.
- [ ] Success-path audit row verified in table 158542.
- [ ] Promotion request staged with evidence.

## UAT Evidence

Gated on the Workday tenant security grants above (same admin-grant dependency class as BSYS-26815 and BSYS-26817). Evidence to collect: job traces per scenario, declined-consent run, Workday UI read-back of the change event, audit-table rows.
