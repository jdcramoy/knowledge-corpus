# BTSUP-77184 + BTSUP-72246 investigation — 2026-10-09/10 (jira-autotriage fleet pass, headless)

Complements `btsup-service-desk-triage-2026-10-09.md` (same folder) and
`~/.claude/knowledge/triage/btsup-drafts-2026-10-09.md`. Both tickets are HR
Genie project work. Nothing was posted to any ticket (headless pass).

---

## BTSUP-77184 — HR Self Service Genie cannot reauthenticate (Biz Sys Review since 09-25)

### Ticket state
- Reporter [requester]. (via Slack C25BE01TM, 09-25). [requester] Monica De
  Los Reyes reproduced "auth failed" herself 09-25. [requester]'s
  workaround (disconnect/reconnect Workday inside Claude, twice) failed for
  the reporter 09-28. Ticket silent since 09-28, 12+ days old.
- Same failure class Josh fixed backend-side in BTSUP-76177 (stored
  connection reset + guided reconnect).

### Live evidence (gathered 2026-10-09/10)
- Prod HR Genie healthy: [HR Genie gin-AYcm4fwE-rtsAJC-CD](https://app.workato.com/genies/gin-AYcm4fwE-rtsAJC-CD/overview)
  is `started`, 21 skills, 1 knowledge base (`genie_list`, prod, 2026-10-10).
  No stopped-genie or configuration fault.
- Fleet runtime connection sweep 2026-10-09 (`wt-prod connections list
  --runtime`, recorded in the service-desk triage file): 9,884 runtime
  connections, 827 Workday-named, all sampled `success` with recent activity;
  single true exception is "Workday 98" (stale since Sep 16). Verdict: per-user
  stale-token friction, not a platform outage.
- VUA-revert trap check INCOMPLETE: attempted `mcp_server_get` on the Workday
  End-User MCP server handle `mcps-AYbrRaxY-dhF-CD` against prod → HTTP 404
  (that handle is dev-scoped; the prod end-user server handle is different and
  unknown from this session). The known trap (2x confirmed on BSYS-26815,
  memory `bsys-26815-benefits-skill-state`) is that any recipe push silently
  reverts connection personalization to "This recipe's connection" / `VUA
  Required: No`, which produces exactly this "cannot reauthenticate" symptom
  for end users while the platform looks healthy. NOT ruled out.

### Root cause (best hypothesis, ranked)
1. **Per-user stale VUA token that the client-side reconnect cannot refresh** —
   matches 76177 precedent (backend connection reset fixed it) and the healthy
   fleet-wide connection picture. Most likely.
2. **VUA-required flag reverted on the prod end-user MCP server** after a
   recipe push (BSYS-26815 trap). Plausible; one UI check settles it.
3. Product-side reauth/step-up defect ([requester]'s "working with the product
   team" framing). Unfalsifiable from here without a case timestamp.

### Verified vs not
- Verified: genie running, prod-side config reachable, fleet connection
  health, ticket history.
- Not verified: the prod Workday End-User MCP server's `VUA Required` state
  (404 on the dev handle; check the prod AI Hub page directly), and no
  backend connection reset has been performed for the reporter — that is a
  prod write and stays Josh-gated.

### Next actions (plan only, no build/reset executed)
1. Josh (or Orca) opens the prod Workday End-User MCP server page and confirms
   `VUA Required: Yes` on the Workday tools. If No, re-select end-user
   connection, save, re-verify (BSYS-26815 fix sequence).
2. If Yes, do the backend connection reset for [requester]'s account (same as
   76177), then have him run the guided reconnect once.
3. If both hold, escalate with timestamps to the product team per [requester]'s
   thread.

### DRAFT customer reply — NOT POSTED (confirm before posting)
Headed for the Jira ticket (Slack-synced), addressed to [requester]:

> Hi [requester], sorry this is still blocking you. Where we landed: the genie and
> its integrations are healthy on our side and the wider Workday connection
> pool is clean, so the failure is a stale token on the stored connection that
> the normal disconnect and reconnect is not refreshing. That points at a
> re-authentication issue we are working through with the product team. Two
> ways forward: I can reset the stored connection for your account on our side
> and then you run one guided reconnect, or grab a slot on my calendar and we
> do it live. Verdict: this needs our backend touch, not more retries on your
> side; expect an update here within a day.

Queue row: appended (key did not exist in queue.jsonl before this pass).

---

## BTSUP-72246 — BT-managed Workday time-off status API for Team UI (In Progress)

### Ticket state
- Vlad Sharikov (Engineering Utilities) needs a boolean is-OOO (+ within-7d)
  HTTP endpoint from Workday for PR-reviewer assignment, without Workday
  credentials. Build answered this 10-05 (comment 1129172); dev key handed
  over via Slack 10-06 (comment 1129425). Vlad last active 10-06.

### Live evidence (gathered 2026-10-09/10)
- Dev build alive and running: [REC | Consumer Roster Sync 82823992](https://app.workato.com/recipes/82823992)
  `Running: True`, folder 35712142, project 15643451, connections slack_bot
  22250878 + workday 19760013 (`recipe_get` dev, 2026-10-10). Sibling
  [BSYS-29340](https://workato.atlassian.net/browse/BSYS-29340) carries the
  full asset list: roster sync 82823992, snapshot refresh 82824104, API
  recipe 82824133, tables 156260/156261/156262, API collection 1404598
  (endpoint 24045816), client team-ui-eng-utilities 1285074.
- Promotion path stalled: BSYS-29340 tech review rejected the manifest
  ("invalid manifest... not found in the Workato AHQ | AI Production
  workspace", comment 1130842, 10-07); Josh reverted the deployment request
  10-08 ("Need to hotfix to prod, reverting deployment request", comment
  1133154). No promotion evidence since. **This is the only thing between the
  customer and a working prod endpoint.**

### Root cause of the delay
Not a technical defect in the build; the managed-promotion manifest was
rejected and the re-route to a hotfix promotion has not executed. Ticket
correctly stays In Progress; the actionable item is finishing the prod
promotion per the BSYS-29340 checklist (manifest or direct copy, prod Slack
bot custom OAuth profile for app A0C6Y8E5U3C + one-time Allow, prod crons
`0 6,18` / `7 * * *`, prod key via secrets channel, stop-alert emails on both
scheduled recipes).

### Verified vs not
- Verified live: dev recipe running with correct connections and schedule.
- Not verified: prod state (no Consumer Endpoints assets confirmed in prod —
  promotion has not landed), and Vlad's dev-key testing beyond the ticket's
  own record.

### DRAFT customer reply — NOT POSTED (confirm before posting)
Status update for Vlad on the Jira ticket:

> Hi Vlad, quick status. The endpoint is built and verified in our development
> workspace and the dev key you have already proves the contract: roster
> lookup, the is-OOO and OOO-within-7-days flags, and the out-of-scope guard
> all behaved in testing, including the batch call. The remaining step is
> promotion to production so it serves real Workday data instead of dev-tenant
> data; that runs through our managed promotion process and is the current
> work item. The production URL and a fresh key will reach you through the
> secrets channel once it lands, and you can point your recipes at it then.
> Verdict: development is done and verified, production promotion is the last
> step; I will confirm here the moment it is live.

Queue row: appended (key did not exist in queue.jsonl before this pass).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [BT Workflow Enablement Guide](../../../kb-corpus/confluence/intbt/2557640730-bt-workflow-enablement-guide.md)
- [2024-09-25 | Meeting Notes | BT Support & SecOps Weekly Meeting.](../../../kb-corpus/confluence/intbt/763002944-2024-09-25-meeting-notes-bt-support-secops-weekly-meeting.md)
- [BTSUP: Revised JSM Workflow](../../../kb-corpus/confluence/intbt/1394147536-btsup-revised-jsm-workflow.md)
- [2024-11-27 | Meeting Notes | BT Support & Enterprise Security Weekly Meeting.](../../../kb-corpus/confluence/intbt/834371585-2024-11-27-meeting-notes-bt-support-enterprise-security-weekly-meeting.md)
<!-- kb-bridges:end -->
