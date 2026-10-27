# BTSUP-78586: Valkyries Tickets Genie — AHQ | AI project setup

Filed 2026-10-13. Status: Workato side DONE + verified (2026-10-23); open item is the
Okta/Firefighter group mapping (BT Apps) + a Slack nudge Josh promised. Ticket:
https://workato.atlassian.net/browse/BTSUP-78586

## Ask

Requester (Nathan Calkin) wants an employee-only Genie for Valkyries ticket requests,
entry point Slack channel C096RCPQDSS, broad employee access. Was blocked before build:
Firefighter access request couldn't select a project because none existed in
Workato AHQ | AI. BT asked to create project + collaborator group, dev + prod.

## Data + privacy contract (from the ticket)

- Stored: employee name + email, game dates of interest, tickets requested per game,
  games attended count, most recent game attended.
- Users see ONLY their own requests/status; admins see everything.

## Done (2026-10-23, verified)

- Dev project "Valkyries Tickets Genie" — AHQ | AI dev folder 35947365
  (https://app.workato.com/recipes?fid=35947365). Builders group = Builder role there.
- Prod project same name — AHQ | AI prod folder 35947366
  (https://app.workato.com/recipes?fid=35947366). Builders group = Operator role there.
  Re-verified live 2026-10-24 via `wt folders get 35947366 --profile josh-prod`.
- Collaborator group "Valkyries Tickets Genie Builders" (org-level, both envs).
- Nathan told to re-run his Firefighter request (2026-10-23 08:03Z comment).

## Open

1. Okta/Firefighter mapping of the Builders group — owned by BT Apps team. The explicit
   3-step ask is posted on the ticket (2026-10-23 05:34Z comment). Josh committed to a
   Slack nudge ("I'm nudging the mapping today") that has NOT gone out — no entry in
   slack-posts.jsonl. Nudge needs Josh's confirm (outward message).
2. Nathan's Firefighter picker retry ("try tomorrow" = 2026-10-24). His result is the
   end-to-end test of item 1.

## Build-phase guardrails (design contract for whoever builds the genie)

- Ticket data in a data table keyed by the immutable IdP subject/employee ID from
  AUTHENTICATED identity (VUA), never email from conversation text.
- Every user lookup scoped to that identity; admin visibility is a separate access
  path, not a loosened user path.
- Slack entry via C096RCPQDSS is fine with broad access because the genie gates on
  identity, not channel membership.
