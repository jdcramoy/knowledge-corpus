# BSYS-26810 — MCP Skill: Update or add personal information (Employee) — Technical Plan

Plan posted to Jira 2026-10-09 (comment 1134660). Build has since been EXECUTED (kickoff 2026-10-10, build comment 1134839: recipe 82959472, REST 403-probed, SOAP fallback built, blocked on Workday tenant security grants). Morning triage pass 2026-10-11 (comment 1134953). Second sweep 2026-10-11 (comment 1135096): re-verified fresh, all findings held, one NEW item — the served tool description still says "REST staged flow" while the executing contract is the SOAP fallback (Change_Home_Contact_Information); fix wording in the same edit as the VUA flip on tool 254984 (still VUA Required: No as of the second sweep). Status: plan ready, awaiting Josh's build authorization.

## Context

Employee-as-Self write skill: update or add personal information (address, phone,
email, and potentially emergency contacts) via HR Genie natural language. Epic
BSYS-26808. The ticket's 2026-07-01 research flipped the contact-info portion to
REST person/v4 but left two open items; investigation on 2026-10-09 closed the
big one (change-event initiation) and confirmed the emergency-contact SOAP leg.

Existing estate (dev project 15643451, folder 30326966):
- Read sibling: get_my_profile https://app.workato.com/recipes/78626397 (worker=me REST)
- Write sibling to clone: update_payment_elections https://app.workato.com/recipes/74912047
  (confirmation-gated write, read-modify-write, friendly error surfacing)
- Folder: https://app.workato.com/recipes?fid=30326966
- No existing recipe covers personal-info writes (32-recipe inventory verified).

## Business Requirements

- Employee updates/adds address, phone number, email via natural language through the HR Genie.
- HR Genie calls the MCP write tool; Workday validation errors surface as friendly messages.
- Confirmation of the update is returned; changes route through the Workday Home Contact
  Change business process (so "pending approval" vs "completed" must be distinguished).
- Emergency contacts either handled as a separate SOAP sub-flow or explicitly descoped to
  a follow-on story (recommendation below).

## Technical Requirements

New skill recipe `update_my_contact_info` in project 15643451, folder 30326966, cloned
from the update_payment_elections 74912047 pattern (worker=me identity, explicit
confirm-before-write gate, validation errors surfaced, no raw faults to the user).

API contract (REST staged flow — primary):

1. Identity: `GET /workers/me` on `workday_rest` (19218617, VUA end-user connection) —
   same resolution as get_my_profile 78626397. Never from free text.
2. Initiate: `POST /workers/{ID}/homeContactInformationChanges` (Staffing service) with
   an effective date. This CLOSES the ticket's open item — confirmed against Workday's
   Contact Information Changes REST API docs (developer.workday.com): the initiation
   endpoint exists on the Staffing service; save the returned event ID.
3. Stage: POST/PUT/PATCH/DELETE on person/v4
   `/homeContactInformationChanges/{ID}/addresses|phoneNumbers|emailAddresses`
   (+ `POST /phoneValidation` helper for phone format checks).
4. Submit: `POST /homeContactInformationChanges/{ID}/submit` (Person service) — launches
   the Home Contact Change BP.
5. Response shaping: report "submitted / pending approval" with the event ID; never claim
   immediate completion (the BP may route approvals).

Fallback if REST scopes are not granted on the VUA connection: single-call SOAP
`Change_Home_Contact_Information` (Human_Resources) — one business-process call covers
address/phone/email/IM/web under the same BP, on `workday` (19760790, VUA).

Emergency contacts: REST person/v4 does not cover them (ticket research, unchanged).
SOAP `Change_Emergency_Contacts` (Human_Resources) is verified in the local WSDL index
v46.2: takes Person_Reference + Emergency_Contacts_Reference_Data (add/delete/Replace_All)
and returns an Emergency_Contact_Event_Reference. Plan it as a second tool/skill or a
separate sub-flow — do not bolt it into the REST flow.

Identity/VUA model: worker=me only; no worker parameter accepted; all calls under the
caller's VUA connection pair (workday_rest 19218617, workday 19760790).

Telemetry hook: audit data table row per write (occurred_at, caller, fields changed,
change event ID, outcome) — same pattern as the HR Genie Time Off Policy Audit Log
(table 156829).

Wiring: register as a tool on the Workday End-User MCP server (mcps-AYbrRaxY-dhF-CD);
HR Genie instructions updated for write-tool confirmation behavior.

## Acceptance Criteria

- [ ] Employee can update home address, home phone, and home email via natural language;
      each lands as a submitted Home Contact Change event in Workday.
- [ ] First build step is a live scope probe: confirm the REST initiation/staging/submit
      endpoints are authorized for the VUA connection 19218617; if not, switch to the SOAP
      fallback before any other work.
- [ ] The skill asks for explicit confirmation and echoes the exact changes before the
      submit call (update_payment_elections confirm-gate pattern).
- [ ] Workday validation errors (conflicting pending change events, invalid effective
      date, country-specific address field requirements) surface as friendly messages.
- [ ] Response distinguishes "submitted, pending approval" from "completed" and never
      claims immediate reflection in Workday.
- [ ] worker=me only; no worker/employee parameter exists on the tool; no cross-worker data.
- [ ] Audit table row written per execution with change event ID and outcome.
- [ ] Emergency contacts: either shipped as the SOAP sub-flow (verified schema) or
      descoped to a named follow-on story — decision recorded before build.
- [ ] Standard dev test + UAT evidence collected before promotion request.

## UAT Evidence

- Editor Test + test-case run with job traces for update-address, add-phone, add-email.
- One confirmation-declined run proving the write does not fire without consent.
- One validation-error run (e.g. conflicting pending change event) proving friendly surfacing.
- Workday UI read-back showing the change event submitted/pending for the test worker.
- Audit table rows verified for each run.

## Risks

- REST scope grants on the VUA connection are unverified — the scope probe is a gate.
- Business-process routing means approval latency; expectation-setting in AC wording is
  required (original AC "reflected immediately" is not achievable as written).
- Conflicting pending contact change events block initiation — needs friendly handling.
- Emergency contacts via SOAP run as a business process under VUA identity; initiation
  behavior under end-user OAuth needs a probe (same class of question as the old
  BSYS-26817 SOAP grant issue).
- Write path: masking/consent discipline is mandatory (this is the estate's first
  personal-info write skill).

## Points

5 — 2-3 day build with UAT: multi-endpoint staged REST flow with a SOAP fallback,
confirm-before-write discipline, audit table, and a scope-probe gate.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [HR Self Service Genie & MCP Server End User Guide](../../../kb-corpus/confluence/extbt/2439020753-hr-self-service-genie-mcp-server-end-user-guide.md)
- [Workato Genie & MCP Development Guide](../../../kb-corpus/confluence/intbt/2423914526-workato-genie-mcp-development-guide.md)
- [HR Genie and Workday MCP - Architecture Overview](../../../kb-corpus/confluence/extbt/2862809419-hr-genie-and-workday-mcp---architecture-overview.md)
- [[Draft] Product Requirement Document](../../../kb-corpus/confluence/extbt/2622619668-draft-product-requirement-document.md)
<!-- kb-bridges:end -->
