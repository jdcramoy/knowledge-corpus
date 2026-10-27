# BSYS-29646 EXECUTED — Susie added to gate group (2026-10-22)

Firing session with Josh's per-action go ("Go + send reply", triage round 2026-10-22).
All steps done same day. Ticket: https://workato.atlassian.net/browse/BSYS-29646

## What was checked first (the two open items from the membership check)

1. End-user record: CONFIRMED EXISTS. The group's "Add end users" dialog user
   search for "shaver" returned Susie Shaver (susie.shaver@workato.com) as a
   candidate — that search lists existing end users only, so her Workato
   Identity record is real and no Invite End User was needed.
   Screenshot: `bsys29646-susie-enduser-record-exists-2026-10-22.png`.
2. Sync-surviving path: Okta admin is NOT reachable. Okta session was expired;
   restored via the staged keychain+push protocol (worked), but /admin/dashboard
   404s twice with a live session and no Admin button exists on the end-user
   dashboard — the account has no Okta admin on workato.okta.com. KB
   (docs.workato.com manual-provisioning / SCIM pages) confirms manual changes
   on IdP-synced groups can be overwritten at sync/login. So: MANUAL Workato add,
   revert risk noted on the ticket.

## What was added

- Manual Add end users on
  https://app.workato.com/members/access_control/environments/3535598/groups/fv1Cic8dCSZcEf8hZnc9Ec
  ([TEAM] T32 | CSM, Production env 3535598). Selected Susie Shaver, clicked Add.
- Group member count 105 → 106 at add time.
- Verified: fresh page load, member search "shaver" → "Showing 1 member",
  Susie Shaver / susie.shaver@workato.com. Screenshot:
  `bsys29646-susie-added-2026-10-22.png`.
- Note: the morning check found 104 members; the pre-add dialog showed 105.
  One other member joined between the check and the add. Not caused by us.

## Reply posted

- Jira comment 1146963 on BSYS-29646, 2026-10-22 21:46Z, via the minimal
  addCommentToJiraIssue shape (cloudId, issueIdOrKey, commentBody,
  contentFormat markdown) — the sticky-400 gotcha from the 10-13 plan did NOT
  reproduce this session; first call landed clean. Re-read back: real bold,
  list items render correctly.
- Draft updated to past tense before posting
  (`bsys-29646-nicholas-timeline-reply.txt`): add done today, record exists,
  Okta admin unreachable, revert risk on record, re-login instruction for Susie
  (Slack `logout` against the genie, then re-message).

## Records

- Build ledger row appended (kind prod-access-change, ticket BSYS-29646).
- Mission-control closeout: workstream bsys-29646-csm-genie, state done
  (needed --force: slug-guard flagged the earlier triage rows on the same
  Jira key; distinct phase, execution vs triage).

## Open item (hers, not ours)

Susie's re-login + first CSM Genie conversation. Watch AI Hub > Conversations
for her first conversation, then close the ticket. If her group membership
reverts at a sync, the durable fix is the Okta group add
([WORKATO-ID-3535597] [TEAM] T32 | CSM) via someone with Okta admin.

## Not verified

- Whether the manual add survives the next IdP sync (unknowable until it happens).
- Why the Firefighter automation missed her (the open question on the ticket).
- Her re-login/first conversation has not happened yet.
