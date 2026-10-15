# BTSUP-73287 — draft requester reply + internal feasibility plan

- Ticket: BTSUP-73287, https://workato.atlassian.net/browse/BTSUP-73287
- Requester: [colleague]. Status: In Progress (master ticket for HRBot
  vacation approvals per Josh's 10-10 comment). Draft saved 2026-10-11,
  NOT posted. Confirm with Josh before sending.

Capability correction versus the original brief: the second-pass evidence
(2026-10-11) shows manager time-off approvals through HR Genie are ALREADY
LIVE for the Workday population, not a roadmap item. The Workday End-User MCP
surface carries get_direct_report_time_off_requests, action_time_off_request
(approve/reject), and get_direct_report_time_off_balances, and the genie was
probed 10-10 with real stuck business processes approved through the real
Workday inbox. So the honest draft says "live for Workday", and the only open
item is Deel. The draft below reflects that.

---

## Draft customer reply (Josh voice, no internal IDs)

Hi Alexey,

Quick update on this. The piece you asked about for Workday is already live:
HR Genie, the Slack app assigned to the whole company, lets you approve or
reject time-off requests from your direct reports right in Slack, and the
result lands in Workday with a full audit trail. Try searching Slack global
search for "HR Genie" and ask it to show your pending time-off requests.

The Deel piece is different: people employed through Deel are not in Workday,
so their requests never reach either Workday or HR Genie. Whether we build a
Deel integration for approvals is a separate decision that is still with us,
and I'll update this ticket as soon as that call is made. Consider the Deel
approval flow taken as a feature request either way.

## Internal feasibility plan (NOT a build; Josh's call)

**Already shipped, nothing to build.** A manager gets the pending time-off
request notification in Slack, replies through HR Genie, and the approval
lands in Workday under the manager's own verified connection. Covered end to
end: the PTO notification platform (BSYS-26808 epic) routes pending-request
notifications, with the FTO policy gate (BSYS-28314) and reconciliation on
top. Live-probed 2026-10-10 with real approvals.

**Gap 1, the real one: Deel.** Deel-employed teammates do not exist as
workers in Workday, so no Workday-side skill can ever see their requests.
Covering them needs a Deel connection (dedicated app per governance, no
shared scopes) plus a small skill set against Deel's time-off API: list
pending requests, approve, reject. Rough size: 3 to 5 points for connection
plus skills plus manager gating. No Deel connection exists anywhere in the
estate today. Approvals for Deel workers can only land back in Deel; there is
no Workday record to mirror into.

**Gap 2, manager identity on any new surface.** Whatever surface serves
approvals must run the approval tools under the approving manager's own
end-user connection (VUA Required: Yes on the tools), not a service account.
Known trap: any recipe push touching that wiring can silently revert the
connection personalization (BSYS-26815, confirmed twice), so every push needs
the verify-and-reselect check.

**Decision owner:** Josh, build versus decline on Deel. Until that call,
this ticket stays open as the master ticket and the Workday half is answered.

## Not verified

Nothing here was tested end to end by an actual Deel-employed user (there is
nothing to test); the "no Deel connections" check ran against our own
workspaces via the dependency tracker, not the customer's.
