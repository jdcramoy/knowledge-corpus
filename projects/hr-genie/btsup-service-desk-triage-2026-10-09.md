# BTSUP service-desk triage — 2026-10-09 (jira-triage fleet pass, headless)

Headless pass: customer replies below are DRAFTS in Josh's voice, awaiting his
confirmation. Nothing was posted to any BTSUP ticket. Evidence gathered live.

## Fleet-wide evidence (one check covers the Workday reauth cluster)

`wt-prod connections list --runtime` (2026-10-09): 9,884 runtime connections,
827 Workday-named. All sampled Workday runtime connections `success`, most
active Oct 5-9. Only one true `exception` ("Workday 98", stale since Sep 16)
plus a handful of never-authorized `none` rows. Verdict: per-user stale-token
friction, not a platform outage. The reauth-step-up pattern (disconnect the
Workday connection on the Workato VUA screen before reconnecting) remains the
correct guidance.

## BTSUP-76177 — Workday OAuth blocking approvals ([requester], Sep 10)

- State: Josh posted the full reconnect steps Sep 11. No reply since (only the
  Sep 17 auto-nudge). Ball in customer's court.
- Verdict: aging follow-up needed, nothing technical left on our side.

Draft reply (confirm before posting):

> Hi [requester], following up on the Workday connection issue from last month.
> Did the reconnect steps work for you? The most common miss is not clicking
> Disconnect next to the Workday connection on the Workato login screen before
> reconnecting, so the old token never actually refreshes. If you are still
> blocked, grab 15 minutes on my calendar and we will fix it live. Either way,
> let me know and I will close this out or keep digging.

## BTSUP-71439 — Claude Workday MCP connected-but-invalid ([requester], Aug 3)

- State: same class as 76177. Josh posted reconnect steps Sep 11; no reply
  since (Sep 17 auto-nudge only).
- Verdict: aging follow-up, same draft pattern.

Draft reply (confirm before posting):

> Hi [requester], following up on the Workday MCP connection. Did the reconnect
> steps from my earlier message get you working? The step people usually miss
> is clicking Disconnect next to the Workday connection on the Workato login
> screen before connecting again. If it still fails after that, book time on
> my calendar and we will troubleshoot it together.

## BTSUP-77184 — HR Self Service Genie cannot reauthenticate (Sep 25, Biz Sys Review)

- State: genuinely unresolved. [requester] Monica confirmed auth failed on her own
  try; [requester] still failing after the Claude-side disconnect/reconnect.
  [requester] flagged it as an issue being worked with the product team.
- Evidence: fleet runtime connections healthy (above), so the failure is
  specific users/tokens, consistent with the product-side VUA reauth issue.
- Verdict: needs a status update to the requester + escalation trail kept on
  the ticket. No fix exists on our side to ship.

Draft reply (confirm before posting):

> Hi [requester], thanks for the patience on this. What we are seeing: the Workday
> re-authentication flow has a known issue we are working through with the
> product team, so for some users the normal disconnect and reconnect does not
> refresh the token even though everything looks connected. Most users get
> through with the reset-and-reconnect steps shared earlier (disconnect the
> Workday connection on the Workato login screen, then connect again). For
> anyone still stuck after that, I am happy to jump on a quick screen share.
> I will post an update here as soon as product confirms a fix.

## BTSUP-75746 — Read large Google Slides decks (Pragya, via Ivan, Sep 7, aging)

- Triage: the three blocked paths in the ask (Drive raw fetch 401, export
  >10MB cap, 250KB chunk cap) are all export-path limits. The Google Slides
  MCP we operate reads decks through the Slides API instead: text, speaker
  notes, and structure per slide, no export, so the 10MB export cap does not
  apply. Embedded media binaries are still not retrievable, and the Drive 401
  means the specific deck is not shared with the integration account.
- Verdict: answerable today with existing tooling; no build needed. Reply
  should ask her to share the deck with the integration account and point her
  workflow at the GSlides MCP read path.

Draft reply (confirm before posting):

> Hi Pragya, good news: this is doable today. The export errors you hit are
> limits of the Drive export path, not of deck reading in general. Our
> Google Slides MCP reads decks directly through the Slides API, which
> returns slide text, speaker notes, and structure without any export, so
> large decks that fail the 10MB export work fine. Two things to set up:
> share the deck with the integration account (the 401 you saw means it is
> not shared), and point the workflow at the Google Slides MCP read calls
> rather than Drive export. One honest limit: embedded videos and image
> binaries are not retrievable as bytes, only their placement. If you share
> the deck and it still will not read, I will take it from there.

## BTSUP-76729 — HR Genie answering from stale FTO policy (Sep 17, In Triage)

- Triage: real product defect in the HR Genie knowledge layer. The prod HR
  Genie Knowledge Base (kb-AYcm4ggH-L9o6zm-CD, folder 34162532) ingests live
  Confluence HRKB pages via the single recipe [HR Genie Confluence
  71538649](https://app.workato.com/recipes/71538649) (running). The Genie
  citing a PDF from an earlier page version means a stale source (most likely
  a PDF attachment or an old document snapshot) is retained in the KB and wins
  retrieval over the live page.
- Fix plan (dev work, needs Josh's authorization like any build):
  1. Inspect 71538649's ingestion scope: does it ingest attachments in
     addition to page bodies, and does it delete-then-recreate or upsert?
  2. Find the stale FTO document in the KB document list; delete it
     (knowledge_base_delete_documents).
  3. Re-ingest the FTO page fresh; verify the Genie cites the current version.
  4. Add a freshness assertion to the HR Genie monitoring (BSYS-28420's
     watchdog scope): newest-ingested version per page must match Confluence.
- Customer reply deferred until the fix lands, then confirm with [requester]'s
  original question.

## BTSUP-75909 — Workday 2 (workatoinc2) access for Vivek (Sep 9)

- State: Josh took it Sep 9 ("adding Vivek to Workday 2 via okta group"). No
  follow-up comment since; the Sep 15 auto-nudge went unanswered.
- Verdict: not verifiable with available tools (Okta group membership needs
  the Okta console). Needs Josh to confirm the add happened, then update or
  close. Recorded here so it surfaces in the morning brief.

## Queue findings filed this pass

- BSYS-29283 deployment-failure remediation plan ready (prod writes, Josh gate).
- BTSUP-76729 stale-KB fix plan ready (dev work, Josh gate).

## BTSUP-67187 — Confluence tool registry / MCP standardization (Jun 22, Biz Sys Review)

- Triage: the coordination answer already exists — the Internal AI Directory
  MCP server is the tool registry, and standard MCP servers (Confluence SDK,
  Gmail V3, GSlides, GW Semantic) replaced per-team duplicates through 2026.
  The specific complaint (duplicate Confluence tools in AI AHQ Dev) is a
  cleanup pass on that server's tool list, not a new program.
- Verdict: reply should point at the directory + offer a consolidation pass.

Draft reply (confirm before posting):

> Hi Abhishek, the short answer: yes, this is being coordinated. The Internal
> AI Directory MCP server is the shared tool registry, and the standard MCP
> servers (Confluence SDK, Gmail, Google Slides, Google Workspace Semantic)
> are the sanctioned surfaces teams should build on rather than minting
> duplicate tools. The duplication you saw in AI AHQ Dev is on the cleanup
> list for that consolidation. If you send me the specific duplicate tools
> you found, I will fold them into the next cleanup pass.

## BTSUP-73287 / BTSUP-73121 — HRBot for vacation approvals (Aug 17, twins)

- Triage: the Workday half is answered and shipped — HR Genie approves/rejects
  Workday time-off requests conversationally (action_time_off_request recipe
  71440065, whole-company access, Josh pointed Alexey at it Aug 19). The open
  item is Danielle's Aug 19 question to Josh: Deel-employed people are not in
  Workday, so HR Genie cannot reach them; a Deel integration is a new-platform
  build (Deel API onboarding) and a scope decision, not a fix.
- 73121 is the same ask filed separately; recommend closing one as duplicate
  (Josh's call — the loop never transitions to Done).
- Verdict: needs Josh's scope decision on Deel; customer-facing answer is
  already on the ticket. No loop build.

## Pass summary

Worked this pass: BSYS-29283 (deployment-failure plan), BSYS-29477 (→UAT),
BSYS-29456 (→In Progress), BSYS-27450 (→UAT), BSYS-26815 (→UAT), BSYS-27477
(plan), BSYS-25528 (plan), BSYS-25527 (plan), BSYS-27657 (spike readiness),
BSYS-29443 (verified complete, no action), BTSUP-76177/71439/77184/75746/
76729/75909/67187/73287/73121 (triaged, drafts above). Subagent plan lanes
covered the Workday/HR Genie skill batches and misc backlog stories.

## SECOND PASS (2026-10-10 01:21 UTC, worker agent, disjoint ownership 76177/71439/75909/75746/73121/73287/67187)

Re-verified every ticket fresh from Jira; states below hold as of this pass.
Queue rows for these keys did not exist (grep-confirmed 0) and are now filed.

### Fresh live evidence this pass

- Prod Workday runtime connection health re-pulled (wt-prod connections list
  --runtime, 01:15 UTC): 1,658 Workday-named runtime connections, ZERO with
  exception status right now. The single "Workday 98" exception this morning's
  pass saw is gone (reauthorized or dropped off). Confirms the morning
  verdict with sharper data: per-user stale-token friction, never a platform
  outage. Reconnect playbook remains the right guidance for both tickets.
- BTSUP-75746 upgraded from hypothesis to PROVEN against Pragya's actual
  deck: Google Slides by Workato MCP Get_Presentation on deck
  1taAHmzYZqO3kqKLb7B1AVe6WVQtY3JF2-agJTYUWHoM returned upstream 200, 139
  slides, title "[Pragya's] Workato AI Control & Execution Plane", full slide
  ID map. Get_Slide on slide 64 (g3f975eadfbb_0_25281) returned 120 elements
  with real text extracted. No export path touched, so the 10MB export cap
  and 250KB chunk cap do not apply. The ask is solved by shipped tooling;
  the only open question is her access to the MCP server (VUA connection).
  The morning draft needs one edit: her deck IS readable as-is (the 401 she
  saw was the Drive-export path, not the Slides read path), so the "share
  the deck with the integration account" step may be unnecessary for read;
  keep it only if her workspace blocks external API reads.

### Per-ticket re-verification (no comment traffic since Sep 11 Josh replies / Sep 17 auto-nags)

- 76177: unchanged, ball on [requester]. Aging 3+ weeks. Draft above stands.
- 71439: unchanged, ball on [requester]. Aging 8+ weeks. Draft above stands.
- 75909: unchanged, ball on JOSH ONLY (Okta group add, never confirmed).
  This is the oldest Josh-owned action item in the cluster.
- 75746: needs customer reply, now with live proof (above). Draft above
  stands with the one edit noted.
- 73121: unchanged, needs Josh's Deel scope decision; close-as-duplicate
  rec (keep 73287, close 73121) since 73287 carries the fuller thread and
  Alexey's access answer.
- 73287: unchanged, customer answer already on ticket (Danielle's HR Genie
  pointer); only open item is the same Deel question.
- 67187: unchanged, zero substantive reply since June 22. Draft above
  stands. Waiting only on Josh sending the reply or formally closing.

## BTSUP-78227 — Slack app not triggering Genie jobs (Oct 8, Biz Sys Review) — evening fleet pass 2026-10-10

Grouping note: this is a customer Agent Studio genie (workspace 3443496), not
the BT HR Genie, but it files here as BTSUP service-desk lane work alongside
the 77184 reauth cluster. Full customer draft lives in
`~/.claude/knowledge/triage/btsup-drafts-2026-10-09.md`.

- Ticket state: [requester] Ferreira's genie
  [gin-AbrPR8zH-gf8rGt-CD](https://app.workato.com/genies/gin-AbrPR8zH-gf8rGt-CD/overview)
  stopped creating jobs on Slack DM and @mention; Slack app A0C7HLXDUEN;
  request URL verified. Marjoe confirmed OAuth scopes look right (10-09).
  Josh gave the events-list + re-install-token checklist (06:26Z), then the
  full genie-side trigger+connection reconnect instructions (13:40Z); [requester]
  ran it all and reported blocked (14:51Z). Josh took over 17:53Z: reuse the
  existing app, edit the existing trigger (a fresh trigger spawns a duplicate
  app), Josh checks the genie trigger and callback directly with his invited
  workspace access and escalates to the platform team if clean.
- DRAFT WAS POSTED: the 17:53:41Z Jira comment matches the draft in
  btsup-drafts-2026-10-09.md verbatim. No further customer draft is needed;
  the open action is Josh's direct inspection, which needs his invited access
  (customer workspace, not reachable from the fleet's own dev/prod
  connections).
- Ranked hypotheses remaining (from ticket evidence + KB):
  1. Duplicate app "(2)" — the bot being DM'd is not A0C7HLXDUEN, or a second
     copy holds the event subscription against the same request URL.
  2. Bot token revoked by an api.slack.com-side reinstall; Workato holds the
     dead token, so the receiver 4xx's silently (no job, no user-visible
     error).
  3. `message.im` / `app_mention` missing from "Subscribe to bot events" —
     the scopes screenshot Marjoe checked covers OAuth scopes, not the events
     list; manifest edits commonly drop them.
- Platform semantics citations:
  https://docs.workato.com/en/agentic/agent-studio/app-events.md
  (troubleshooting: genie not responding checklist) and
  https://docs.workato.com/en/agentic/agent-studio/chat-interface/channel-support.md
  (required bot scopes for Slack).
- Verified vs not: verified from the ticket record and KB docs; NOT verified:
  anything inside workspace 3443496 (no cross-workspace AIRO access) or their
  api.slack.com app config. Josh's inspection is the unblocking step.
- Queue: no new row. Existing row line 41 of triage/queue.jsonl
  (btsup-78227-genie-slack-customer-blocked, status deferred, decided 10-09
  18:38Z) covers this key; Josh deferred it to his own timing, and the
  takeover reply landed 5 minutes before that deferral was recorded.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [2023-01-25 Meeting notes: BT Support & SecOps Weekly Meeting.](../../../kb-corpus/confluence/intbt/156368897-2023-01-25-meeting-notes-bt-support-secops-weekly-meeting.md)
- [2022-08-24 Meeting notes: BT Support & SecOps Weekly Meeting](../../../kb-corpus/confluence/intbt/59605009-2022-08-24-meeting-notes-bt-support-secops-weekly-meeting.md)
- [2022-11-23 Meeting notes: BT Support & SecOps Weekly Meeting](../../../kb-corpus/confluence/intbt/109314726-2022-11-23-meeting-notes-bt-support-secops-weekly-meeting.md)
- [2022-08-11 Meeting notes: BT Support & SecOps Weekly Meeting](../../../kb-corpus/confluence/intbt/53575681-2022-08-11-meeting-notes-bt-support-secops-weekly-meeting.md)
<!-- kb-bridges:end -->

## BTSUP-78227 addendum (2026-10-10 03:30Z pass, jira-triage fleet job)

Re-verified the unblocking step live, no change to the plan above:

- Cross-workspace confirmed from THIS side too: AIRO prod genie_get on
  gin-AbrPR8zH-gf8rGt-CD returns HTTP 404 "Genie not found" (workspace-scoped
  IDs, token-bound to Josh's own workspaces). No API path into 3443496.
- Orca browser probe: app.workato.com bounces to /users/sign_in and the Okta
  re-route (workato.okta.com/app/UserHome) also lands on the Okta sign-in —
  the browser session is expired. Josh's one-action unblock for his promised
  direct genie inspection: sign into the Orca browser (Okta dashboard), then
  the genie build page is one goto away.
- Also confirmed this pass: `orca tab create --url <url>` is the correct
  subcommand (tab new / tab open do not exist).
- No new customer draft (17:53Z takeover reply already posted and still
  current); no new queue row (btsup-78227-genie-slack-customer-blocked,
  status deferred, still covers it).
