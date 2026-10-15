# BTSUP-78227 draft customer reply (staged 2026-10-12, NOT posted)

Why staged: Josh's public promise "I will follow up here as soon as I have the root cause"
(2026-10-09 17:53) is now 3 days unanswered; the 10-10 findings comment is Service-Desk-Agents
only, so the customer has seen none of it. Headless pass: confirm-gated, never auto-posted.
Fire from the morning brief or on Josh's confirm.

## Underlying facts (evidence)

- Customer workspace 3443496, Slack app "Ops Genie - PlanWise (2)" (A0C7HLXDUEN).
- Josh's 2026-10-10 workspace read: genie Inactive in Production AND no Slack chat interface
  attached; either alone accounts for zero jobs. Root cause of HOW it got that way is still a
  guess (misregistered Slack trigger / duplicate Slack apps).
- Fix touches the customer's PRODUCTION workspace: needs per-action confirmation, not just a
  reply confirm. Our dev Slack-event path verified healthy today (recipe 82971161, 4 green
  events 15:01-15:47 PDT), so platform delivery is not the suspect.

## Draft (Josh voice, no internal IDs)

Hi [requester],

Following up as promised. I got into the workspace and found what's going on: the Ops Genie
assistant had been switched to inactive, and its Slack chat interface had come detached, so
Slack messages had nothing to land on. That combination explains the silence on both DMs and
mentions.

The fix is to reactivate the genie and re-attach the Slack interface, then send a couple of
test messages to confirm jobs fire again. Since this is your production workspace, I want your
go-ahead before I change anything: can you confirm I should proceed? If it's easier to walk
through live, happy to hop on a quick screenshare.

Thanks!

## Not verified

- Current genie state in workspace 3443496 (last read 2026-10-10; it may have changed).
- Whether [requester]'s original token/event-subscription checklist work is still in place.
