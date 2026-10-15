# BTSUP-78586: Valkyries Tickets Genie — AHQ | AI project setup

Filed 2026-10-13. Status: plan posted on ticket, awaiting Josh's go. Ticket:
https://workato.atlassian.net/browse/BTSUP-78586

## Ask

Requester (Nathan Calkin) wants an employee-only Genie for Valkyries ticket requests,
entry point Slack channel C096RCPQDSS, broad employee access. Blocked before build:
Firefighter access request can't select a project because none exists in
Workato AHQ | AI. BT asked to create project + collaborator group, dev + prod.

## Data + privacy contract (from the ticket)

- Stored: employee name + email, game dates of interest, tickets requested per game,
  games attended count, most recent game attended.
- Users see ONLY their own requests/status; admins see everything.

## Plan

1. In AHQ | AI workspace, create project "Valkyries Tickets Genie" in both dev and
   prod environments.
2. Create collaborator group (Valkyries Tickets Genie Builders or similar), grant it
   project-scoped privileges in both envs, and confirm it appears in the Firefighter
   provisioning picker.
3. Tell Nathan the project exists so he can re-run the Firefighter request.
4. Build-phase guardrails (design contract for whoever builds the genie):
   - Ticket data in a data table keyed by employee email from the AUTHENTICATED user
     identity (VUA), never from conversation text.
   - Every user lookup scoped to that identity; admin visibility is a separate access
     path, not a loosened user path.
   - Slack entry via C096RCPQDSS is fine with broad access because the genie gates on
     identity, not channel membership.

## Not verified

- AHQ | AI workspace is not reachable from the AIRO MCP bound to this session, so the
  requester's claim that no project exists is unconfirmed; verify when executing.
- Whether AHQ | AI already has a naming convention for projects/groups.
