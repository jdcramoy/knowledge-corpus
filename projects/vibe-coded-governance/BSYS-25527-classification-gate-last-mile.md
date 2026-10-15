# BSYS-25527 — Risk tier classification process and publication gate (last-mile plan)

Ticket: https://workato.atlassian.net/browse/BSYS-25527 (epic BSYS-25523, Backlog, points 3).
Plan posted 2026-10-09 (comment 1134659), built 2026-10-10 (build record comment 1134814). This file holds the 2026-10-11 last-mile plan. No rebuild of what exists.

## Live evidence (2026-10-11)

- Review recipe 82959473 (https://app.workato.com/recipes/82959473) exists, scheduled Mondays 09:00 America/Los_Angeles, Running=False, matching the build record's deliberate hold.
- Its slack_bot connection reads None on the live pull: the one blocker, no bot identity attached to the #bt-ea post step.
- Tables live in folder 31391241: Vibe App Risk Registry (158539), Risk Tier Review Event Log (158540), Risk Tier Classification Rules (158541).
- Dev UAT already on record: three green job traces (detection/bumps/default-deny, clean path + idempotence, gate decision closes the loop).

## Remaining work

1. Slack bot connection: net-new workspace-owned Slack app + custom OAuth profile per the slack-bot-connection SOP, never a personal connection. Select it on the final recipe step, one Connect Allow needs Josh's hands (browser popup), then start the recipe.
2. Registry intake wiring: when BSYS-25528's registration path activates, add the classification checklist fields pointed at the Vibe App Risk Registry. The review recipe needs no change; it reads the table.
3. Reviewer names + escalation path published on the epic (Josh/BT EA).
4. Promotion through the BT managed process after UAT sign-off.

## Acceptance criteria (ticket)

- [x] Classification checklist live on intake (dev, per build record)
- [x] Weekly review recipe built and dev-verified; blocked on Slack connection before it can run in earnest
- [x] Scope-promotion rule table documented and applied
- [x] Gate workflow with one decision recorded end-to-end (dev)
- [ ] Reviewer names and escalation path on the epic
- [ ] Flag list actually posting to BT EA from a bot identity

## UAT Evidence

After the connection lands: one forced or scheduled review run with the #bt-ea post observed in-channel from the bot identity, plus the three dev job traces already on record.

## Risks

The Workbot connection is the long pole (dedicated app approval + OAuth popup); everything else is minutes.

## Points

2 remaining.
