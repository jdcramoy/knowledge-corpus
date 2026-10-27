# BSYS-29646 — CSM Genie access path verified live (2026-10-16)

Ticket: [BSYS-29646](https://workato.atlassian.net/browse/BSYS-29646) (also BTSUP-78406). Prior plan in this folder: `bsys-29646-susie-access-plan.md`.

## What changed this pass

Nicholas Chiodo confirmed the go from the requester side (comment 12:58Z). The pass verified the
remaining unknowns that were flagged unverified in the 10-13 plan.

## Live-verified facts (prod workspace 3535598, `wt --profile josh-prod`)

- CSM Genie = `gin-AaTBfBon-TNoQgC-CD`, state active, Slack trigger `ginct-Ab9LJnC6-xrNerg-CD`,
  channel_scope `all_invited`, response_mode `on_mention`.
- **Gate = exactly one End User Group: `[TEAM] T32 | CSM`** (id `fv1Cic8dCSZcEf8hZnc9Ec`,
  104 members, membership last updated 2026-09-30 — predates Susie's 10-09 grant).
- Affected user: Susie Shaver (`U0B69PB17TN`, Embedded CSM) — resolved from the Slack thread.
- Genie answering other CSMs in Slack same-day → failure is user-specific, not genie-wide.
- No wrong-bot risk: the only other CSM genie ("CSM Genie Go", `gin-AWkP69ah-FTRD8z`) is
  Workato-GO-only.

## Runbook corrections to the 10-13 plan (dissenter-driven, runbook verified)

- Runbook: [Workato Genies | End User Groups Management](https://workato.atlassian.net/wiki/spaces/intbt/pages/1689976864)
  - Provisioning path = Okta group add, named `[WORKATO-ID-3535597] {end_user_group_name}`
    (uses the DEV workspace ID; memberships sync across both environments).
  - A manual UI path exists (Workspace Admin > End User Groups > Add Users, plus
    `Invite End User` if no end-user record) but the runbook heads it "(Not Applicable today)".
    The 10-13 claim that UI adds are always clobbered was too absolute — soften to "runbook
    marks it not-applicable".
  - Membership CHECK needs no Okta admin: Workspace Admin > End User Groups in the UI.
- Slack-side sync risk (dissenter find, ASEE page 2118942766 — NOT independently verifiable,
  login-walled): a user added to groups after first genie login may not sync into Slack;
  cheap reset = `logout` command then re-message. Treated as a guess in the posted comment.

## Fix sequence posted to the ticket (comment 1141196, 13:57Z)

1. Check Susie's membership in `[TEAM] T32 | CSM` (Workspace Admin > End User Groups).
2. If missing: add to Okta group `[WORKATO-ID-3535597] [TEAM] T32 | CSM`.
3. `logout` + re-message (Slack session refresh).
4. Escalate to Invite End User record / SAML claims if still blocked.

## Open question

Firefighter provisioning is supposed to be automated for genies on it. If Susie's grant never
reached the gate group, either the automation targets a different group or the sync broke.
Settle this before closing so the next CSM doesn't hit the same wall.

## Gate status

Requester go received. The prod access change itself still needs Josh's per-action
confirmation (blanket-delegation rule). Dissenter verdict: SHIP-WITH-CHANGES; all three
corrections incorporated before posting.

## STAGED FOR EXECUTION (Josh go 2026-10-16, triage pass)

Josh's go recorded in triage 2026-10-16. Execute in a firing session with first-hand
per-action confirmation before each prod step:

1. Check Susie Shaver's membership in end-user group [TEAM] T32 | CSM.
2. If missing: add via Okta group [WORKATO-ID-3535597] [TEAM] T32 | CSM (per-action go).
3. Have her run the Slack `logout` command against any genie she's logged into, then re-login.
4. Retest the CSM Genie DM; capture evidence; update BSYS-29646.

Ticket: https://workato.atlassian.net/browse/BSYS-29646
