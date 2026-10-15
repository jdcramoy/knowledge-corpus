# BSYS-29646: CSM Genie "user not authorized" for Firefighter-provisioned user

Filed 2026-10-13. Status: plan posted on ticket (comment 1137682), awaiting Josh's go.
Ticket: https://workato.atlassian.net/browse/BSYS-29646

## Facts

- Susie, provisioned via Firefighter, DMs the CSM Genie and gets the genie's own
  allowlist rejection: "not on the list of authorized users for this bot."
- Workspace per ticket: Workato AHQ | AI prod. Marc Parilla pinged Josh 2026-10-13 20:14.
- KB (Agent Studio FAQ, "Genie works in Test mode but not in production"): the genie's
  End User Access tab governs who can talk to it; users outside the assigned user group
  get no response or an access error.
- Firefighter provisioning grants workspace collaborator access; it does NOT touch a
  genie's end-user access list. The two systems are separate. This separation is the
  likely root cause (labeled as working theory on the ticket).
- NOT verified live: the AHQ | AI prod workspace is not reachable from the AIRO MCP
  bound here (it points at Josh's own workspace; the CSM Genie gin-Aa3wHmsT-KYLn3c-CD
  found there is a different copy). genie_get returned an empty body, so the End User
  Access config was not read for either copy.

## Plan (as posted)

1. CSM Genie > End User Access tab: note assigned user group(s).
2. Check Susie's membership; add her or the covering group.
3. If the group is directory-synced, fix at the source; manual adds get overwritten.
4. Susie re-DMs; complete first-time Confluence auth prompt if it appears.
5. Verify a conversation from her under AI Hub > Conversations.

The change is a config write in a production workspace: Josh's explicit go required.

## Tooling gotcha (2026-10-13)

addCommentToJiraIssue call shape went sticky this session: commentId + role
commentVisibility kept being re-emitted after the first call, 5x 400
"not a member of the project role: Service Desk Agents" on BSYS. Stripping
explicitly (null) did not help from this session. What worked: dispatching a
fresh subagent whose first addCommentToJiraIssue call carried only
cloudId/issueIdOrKey/commentBody/contentFormat. Add to airo-mcp-playbook.
