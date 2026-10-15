# BTSUP-73287 — Deel time-off approvals via HR Genie: feasibility + build plan

Filed 2026-10-12 from the jira-triage pass. The Workday half of this ask is
shipped (HR Genie approves/rejects Workday time off for direct reports). The
open item Josh parked on 2026-10-10: build vs decline the Deel half. This
plan is the input to that call — it is not a commitment to build.

## The ask (from the customer thread)

Deel-hired employees cannot submit time off in Workday (they are employed by
Deel), so their approvers juggle two platforms: Workday requests for
Workday-hired reports, Deel for Deel-hired ones. Alexey asked for vacation
approvals to work inside HR Bot/HR Genie.

## Feasibility — the API half is a non-problem

Deel's public API has a complete time-off surface (developer.deel.com,
Time Off endpoints): list time-off requests for the organization with
`status=REQUESTED` filters, a dedicated approve/reject review endpoint,
validation, create, cancel. Token scopes `time-off:read` and `time-off:write`.
Verified live this pass from the published docs.

Workato-side: no Deel connector exists in the workspace (checked the
connector catalog 2026-10-12), so the build uses the HTTP connector with a
Deel API token — the standard pattern, nothing exotic.

## The real design problem: manager-to-Deel-report mapping

HR Genie resolves a manager's identity from the Workato VUA context and
looks up their direct reports in Workday. Deel-hired workers are not Workday
workers, so the Workday lookup returns nothing for them. The build's core
problem is bridging "this manager" to "their Deel-hired reports". Three
options:

1. **Deel-side org data** (preferred if the fields are populated): Deel
   profiles carry team/department/manager fields; a scheduled sync maps
   manager email → Deel profile IDs into a Workato data table.
2. **Email-join sync**: nightly pull of Deel workers, join on email against
   the manager's report list from Workday, store the pair table.
   Tolerable but breaks where Deel emails differ from corporate email.
3. **Manual lookup table**: fastest to ship, slowest to rot — only acceptable
   for a small pilot population.

## Proposed build (5 points, only if Josh says build)

1. Deel connection: HTTP connector + API token, read + write scopes,
   dev first (0.5d)
2. Mapping bridge: option 1 sync recipe + data table, fallback to option 2
   (1d)
3. Two MCP skills on HR Genie: view pending Deel time-off requests for my
   reports; approve/reject a Deel request by ID with confirmation
   (1.5d)
4. Guardrails: VUA everywhere (identity from context, never user text),
   approve/reject requires an explicit confirm step in the genie contract,
   audit log of every Deel decision to a data table (0.5d)
5. UAT: pilot with Alexey as the first approver, real approve + reject
   traces, evidence block (1.5d)

## Risks

* **Scope creep**: "time off" in Deel covers 40+ policy types (sick,
  parental, regional). V1 should scope to vacation-type policies only and
  say so in the skill description.
* **Audit/compliance**: approving employment actions in Deel through an AI
  surface is a policy question, not just a technical one — HR owns whether
  that is acceptable; the audit log is the minimum answer.
* **Token custody**: a Deel API token can approve/reject org-wide; scope it
  to a service account with least privilege and never surface it through a
  personal connection (governance rule).
* **Volume**: if only a handful of managers have Deel reports, this is a
  lot of build for small reach — the decline case Josh is weighing.

## Verdict

Technically buildable in about a week of build time; the deciding inputs are
product reach (how many managers have Deel-hired reports) and HR's tolerance
for AI-mediated employment actions. If the reach number is small, decline
and close this as answered-with-Workday-only.
