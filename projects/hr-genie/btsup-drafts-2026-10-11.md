# BTSUP customer reply drafts + triage findings — 2026-10-11

Headless jira-autotriage pass. Both drafts below are DRAFTS ONLY, awaiting
Josh confirmation, NOT POSTED to any ticket. No status transitions performed.
Investigation findings are in the second half, per ticket.

Related: `btsup-77184-and-72246-investigation-2026-10-09.md` (prior pass),
`btsup-service-desk-triage-2026-10-09.md`.

---

## DRAFT REPLY — BTSUP-77184 (HR Self Service Genie cannot reauthenticate)

To: [requester]. (ticket is Awaiting information; he has not replied
since the reconnect instructions went up). Two variants depending on which
way he responds.

### Variant A: follow-up nudge (he stays silent)

> Hi [requester], following up on this. I've already reset your connection on our
> side, so the stored one that was blocking you is gone. The reconnect only
> works if the steps run in the order listed in my earlier note, so please
> start from step 1 and take them one at a time. If any step looks different
> from what I described, tell me which step number and what you see and we'll
> pick it up from there. Verdict: the reset is done on our side, and the
> reconnect just needs to run end to end once.

### Variant B: closing note (he confirms it worked)

> Hi [requester], glad that landed. I'll close this out. If the login prompt ever
> shows up again, start with the reconnect steps from my earlier note, and if
> it still fails we'll reset the connection on our side and run it once more.
> Verdict: resolved.

---

## DRAFT REPLY — BTSUP-76729 (HR Genie referencing an outdated version of the Confluence page)

To: [requester] (reporter; [requester] hit the behavior). IMPORTANT: this is a
status update, not a "fixed" message, because the fix is verified in the
development workspace only; the production knowledge base still holds the
stale copy as of this morning (evidence in the findings section). The draft
deliberately avoids internal IDs, job traces, and blame.

> Hi [requester] Yen, thanks for the report, and apologies for the slow turnaround.
> Where things stand: we reproduced what [requester] saw and found the cause. The
> Confluence page itself was always current; the genie's knowledge layer was
> holding an older snapshot of the Flexible Time Off page from an early
> ingest, and that snapshot was outranking the live page in search results.
> That's the "pdf from an earlier version" you saw.
>
> The fix is built and verified in our build workspace: the stale copy is
> removed, the current page is re-ingested, and a check now compares the
> knowledge base against the live Confluence page on a weekly schedule so
> drift gets caught on its own instead of waiting on a report. The last step
> is rolling that out to the live genie, which runs through our standard
> release process. I'll confirm here the moment it's live.
>
> Verdict: this was a stale snapshot in the genie's knowledge layer, not a
> problem with the Confluence page or the policy itself, and once the rollout
> lands the genie will only ever cite the current version.

---

# INVESTIGATION FINDINGS (internal, for Josh)

## BTSUP-77184 — HR Self Service Genie cannot reauthenticate

Ticket: https://workato.atlassian.net/browse/BTSUP-77184
Status: Awaiting information, Medium, created 2026-09-25.

What the ticket says: reporter [requester]. (via Slack C25BE01TM
2026-09-25) says the genie "can't reauthenticate". [requester]
reproduced "auth failed" herself 09-25. [requester]'s workaround
(disconnect/reconnect Workday inside Claude, twice) failed 09-28. Josh posted
the backend-reset + 11-step guided reconnect 2026-10-10 09:08. No reply from
the user since; the Slack thread (read this pass) also shows no visible reply
after the reset, only the ticket's move to Awaiting information on 10-10.

Estate evidence (gathered 2026-10-11, read-only):

- Dev HR Genie [gin-AYbxpMha-YenKAJ-CD](https://app.workato.com/genies/gin-AYbxpMha-YenKAJ-CD/overview)
  is `started`, 26 skills, 1 KB. The old [DEPRECATED] HR Self Service Genie
  [gin-AYT8CXX3-AJPWeA-CD](https://app.workato.com/genies/gin-AYT8CXX3-AJPWeA-CD/overview)
  is `stopped` (retired as designed, not an incident).
- Prod HR Genie [gin-AYcm4fwE-rtsAJC-CD](https://app.workato.com/genies/gin-AYcm4fwE-rtsAJC-CD/overview)
  reachable via prod AIRO read (call succeeded 2026-10-11); the read-back
  returned no state payload this time, so "started" for prod is carried from
  the 10-09 pass rather than re-proven today.
- Shared prod Workday connection is healthy: CON | Workday REST, workspace
  3535598, authorized 2026-04-05, no connection-lost flag
  (workato-dependency-tracker, 2026-10-11). Per-user VUA connections do not
  appear in the tracker inventory, so [requester]'s individual connection state
  is not directly observable from here.
- Prior pass's top hypothesis (per-user stale VUA token that the client-side
  reconnect cannot refresh) was already acted on: Josh did the backend reset
  10-10. The ticket is now simply waiting on the user's guided reconnect.
- The v2 residual risk from the 10-09 pass (VUA-required flag reverted on the
  prod end-user MCP server after a push, BSYS-26815 trap) was NOT rechecked
  this pass; the prod end-user server handle was still unknown from this
  session. Worth one UI look on the prod MCP server page when Josh is there.

Working theory (unchanged, and now in execution): stale per-user VUA token
fixed backend-side; outcome hinges on [requester] running the reconnect in order.

Draft status: Variant A (nudge) and Variant B (close-out) written above,
NOT posted. Awaiting Josh's pick and confirmation.

Not verified: [requester]'s own connection state post-reset (no read path to
personal VUA connections); whether he has attempted the reconnect since
10-10; prod genie running state today (read-back was empty); the prod
end-user MCP server's VUA Required flag.

## BTSUP-76729 — HR Genie referencing an outdated version of the Confluence page

Ticket: https://workato.atlassian.net/browse/BTSUP-76729
Status: In Triage, Low, created 2026-09-17. Internal comments only since
Josh's 10-10 root-cause and fix-complete notes; nothing customer-facing
beyond the support auto-ack.

What the ticket says: [requester] asked the HR Genie about the FTO policy and got
an answer sourced from an early version of the Confluence page (page updated
since May). Josh's 10-10 comments confirm root cause (stale KB doc) and a
fix completed in the dev workspace, explicitly "nothing promoted".

Estate evidence (gathered 2026-10-11, read-only):

- DEV fix verified live. HR Genie Knowledge Base
  [kb-AYc8DXFF-rzGerR-CD](https://app.workato.com/knowledge/kb-AYc8DXFF-rzGerR-CD)
  doc 242843660 "Flexible Time Off Program": INDEXED, 3,924 bytes, updated
  2026-09-17T12:28:21-04:00 (matches the source page's current version),
  re-ingested 2026-10-10T08:23Z. The stale copy is gone from dev retrieval.
- Freshness sentinel running. [MON | HR Genie | KB Source Freshness
  82959482](https://app.workato.com/recipes/82959482) is Running: True,
  compares the KB doc against the live Confluence page version weekly and
  raises a P3 through the shared publisher on drift. Latest job
  j-AbtKHYE9-JhxAFK-CD 2026-10-11 succeeded, no alert fired (condition false,
  fresh). Job totals 9: 6 succeeded, 3 failed (the 10-10 negative test batch).
- Confluence collector [HR Genie Confluence
  71498060](https://app.workato.com/recipes/71498060): 764 jobs, 0 failures;
  latest activity 2026-10-06. Polling quiet since; the known gap is the two
  silently missed page-update events on the FTO page (from the 10-10
  comment), which the sentinel now covers for the FTO page only.
- CRITICAL GAP: the PROD knowledge base is still stale. The employee-facing
  prod genie attaches prod HR Genie Knowledge Base
  [kb-AYcm4ggH-L9o6zm-CD](https://app.workato.com/knowledge/kb-AYcm4ggH-L9o6zm-CD),
  and its doc 242843660 "Flexible Time Off" is a 1,003-byte snapshot ingested
  2026-04-03 and never refreshed. The live page is ~3.9 KB after the May and
  Sep 18 updates. So the exact failure mode [requester] reported is still live in
  production. Josh's dev fix (delete + re-ingest + sentinel) exists only in
  the dev workspace; the sentinel has no prod counterpart yet.

Working theory: no longer a theory, confirmed on both sides. Original cause:
the collector's polling trigger silently missed both page-update events on
page 242843660, so the April snapshot in each KB kept winning retrieval.
Current state: dev clean and monitored, prod still serving the stale doc.

Draft status: status-update draft written above (cause confirmed, fix built,
rollout pending), NOT posted. Deliberately not worded as "fixed" because
production still shows the bug.

Not verified: which recipe feeds the prod KB (prod has an active recipe on
the KB but its identity and health were not pulled this pass); whether a prod
promotion of the re-ingest + sentinel is already queued (nothing seen in this
pass); [requester]-irrelevant but worth noting: the full-KB sweep (v2 sentinel
covering all HRKB pages) remains unbuilt, and a prod sentinel does not exist.

## Recommended next actions (Josh's call, no writes performed)

1. Approve the prod-side fix for 76729: re-ingest page 242843660 into
   kb-AYcm4ggH-L9o6zm-CD (or promote the dev re-ingest + sentinel pattern),
   then confirm with a retrieval check on the prod KB. This is the only
   thing between the customer and the corrected answer.
2. Pick 77184 Variant A or B when [requester] responds (or Variant A if he stays
   silent past the nudge window).
3. When in the prod AI Hub, eyeball the HR Self Service end-user MCP server's
   VUA Required flag (the 77184 v2 residual risk, one check).
# BTSUP drafts 2026-10-11 (jira-autotriage pass)

Both drafts below are DRAFTS awaiting Josh confirmation. Nothing was posted, nothing transitioned, no recipe or genie was touched. Estate checks were read-only.

---

## BTSUP-73287 - HRBot for vacation approvals (In Progress, created 2026-08-17)

### Ticket record
- Requester: [colleague]. Original ask: approve vacations inside HRBot instead of jumping between Deel and Workday.
- HR (Danielle De Vera) answered 2026-08-19: HRBot cannot do approvals; HR Genie (Slack app) can approve or reject time-off requests from direct reports submitted in Workday. Deel-employed people are employed by Deel, not Workato, so they cannot submit time off in Workday at all. Ticket moved to BT for the Deel integration question.
- Josh's 2026-10-10 comment: Workday half is shipped through HR Genie; the one open item is the Deel HR integration scope decision (build vs decline), which sits with him.

### What exists today (verified)
- HR Genie in production, started, 21 skills, JSM escalation built in: https://app.workato.com/genies/gin-AYcm4fwE-rtsAJC-CD/overview
- Manager time-off approval coverage is real and shipped: the Workday End-User MCP surface carries get_direct_report_time_off_requests, action_time_off_request (approve/reject), and get_direct_report_time_off_balances; the PTO notification platform (BSYS-26808 epic) routes pending-request notifications end to end, with policy gates (BSYS-28314 FTO gate) and reconciliation.
- The genie was probed live on 2026-10-10 with real stuck business processes (Libby Alden comp change, David Martinez promotion) approved through the real Workday inbox, and the full BP-completion pipeline fired.

### Assessment
This is already covered for the Workday population. A manager can get a pending time-off request notification in Slack, reply through HR Genie, and the approval lands in Workday with an audit trail. Telling Alexey to use HR Genie for Workday-employed direct reports is a correct answer today, not a promise.

The genuine gap is Deel only. Deel-employed teammates do not exist as workers in Workday, so no Workday-side skill can ever see their requests. Covering them needs a Deel integration (connection plus skill set), which does not exist anywhere in the estate today (no Deel connections found). That is a build-vs-decline scope decision that belongs to Josh, and it is the only thing keeping this ticket open. Everything else in Alexey's ask is answered.

### DRAFT customer reply (NOT posted, awaiting Josh)
> Hi Alexey,
>
> Quick update on this. The piece you asked about for Workday is already live: HR Genie, the Slack app assigned to the whole company, lets you approve or reject time-off requests from your direct reports right in Slack, and the result lands in Workday with a full audit trail. Try searching Slack global search for "HR Genie" and ask it to show your pending time-off requests.
>
> The Deel piece is different: people employed through Deel are not in Workday, so their requests never reach either Workday or HR Genie. Whether we build a Deel integration for approvals is a separate decision that is still with us, and I will update this ticket as soon as that call is made.

Not verified: nothing here was tested end to end by an actual Deel-employed user (there is nothing to test); the "no Deel connections" check ran against our own workspaces via the dependency tracker, not the customer's.

---

## BTSUP-78227 - Slack app not triggering Genie jobs (Biz Sys Review, customer workspace 3443496)

### Voice-trap separation (per 2026-10-10 comment rewrite)
- What the ticket originally said broke: the customer's Slack app "Ops Genie - PlanWise (2)" stopped producing any genie response or job history from DMs and @mentions, after scopes were added and the app reinstalled.
- What the workspace shows now (re-verified live today, 2026-10-11, read-only through the customer Production env): the genie is still Inactive, the build page still lists only the native Workato chat interface and one recipe caller, there is still no Slack chat interface, and the 30-day analytics are unchanged (2 conversations, 4 end-user messages, all native channel). No jobs are flowing. Nothing was fixed since yesterday's inspection.
- The guess at original cause, stated as a guess: the genie had multiple Slack apps and at some point two connected, so the original break was most likely a misregistered Slack trigger pointing at the wrong app. The current missing-interface state is aftermath of the Oct 9 reconnect attempt, not the original break. These three layers are kept separate on purpose.

### Current wiring state
- Trigger wiring today: no Slack connection, no Slack trigger, no Slack chat interface on the genie. The only channels are native Workato chat and one recipe caller. The genie itself works on the native channel.
- The Slack app A0C7HLXDUEN is the customer's own dedicated app (correct pattern; the fix path reuses it rather than spawning a duplicate). The dedicated-app re-add path was NOT completed: [requester] hit the create-new-trigger-spawns-duplicate-app trap and stopped.
- Prior live record: ~/.claude/knowledge/projects/btsup-78227-genie-slack-trigger/root-cause-2026-10-10.md

### Verdict
The original problem is NOT resolved in the current workspace. The fix is small, fully mapped, and sits in the customer's Production workspace, so it stays Josh-gated: re-add the Slack chat interface selecting the existing app A0C7HLXDUEN (never create a new trigger), start the genie, send one DM, confirm a job in history. The one open sequencing question from yesterday stands: whether starting the genie throws a config error on the missing Slack channel, which would reorder the steps.

### DRAFT customer reply (NOT posted, awaiting Josh; send only after the fix lands)
> Hi [requester],
>
> Good news, I found the root cause in your workspace. The genie is currently stopped, and its Slack connection was removed during the earlier reconnect attempts, so your messages had nothing to reach. The genie itself works fine; it has been answering through the web channel the whole time.
>
> I am reattaching your existing Slack app to the genie and starting it now. Then I will send one test message and confirm here once it shows a job end to end. You do not need to try anything else on your end.

Not verified: whether A0C7HLXDUEN still holds valid event subscriptions after the reconnect cycle (screenshots suggest yes); whether Start genie surfaces a config error on the missing Slack channel; whether the fix was applied between yesterday's inspection and today (the live check today says it was not).

---

# Second pass addendum (jira-autotriage fleet run, 2026-10-11 ~14:30Z)

Independent re-triage of all four tickets, full threads re-read, one live fact
re-checked. Verdicts unchanged, drafts unchanged. New evidence:

- BTSUP-76729: sentinel [82959482](https://app.workato.com/recipes/82959482)
  re-verified live — latest scheduled run j-AbtKHYE9-JhxAFK-CD (2026-10-11
  00:23 PT) completed clean, no alert. Dev KB still fresh; the prod-KB gap in
  the findings above remains the only customer-visible item.
- BTSUP-73287: confirmed BSYS-27657 (Business Approvals button-card) is a NO-GO
  with its finding still open pending Josh's closure. It does NOT gate this
  ticket; the only open item stays Josh's Deel build-vs-decline call.
- BTSUP-77184 and BTSUP-78227: no estate change since the morning pass. 78227's
  genie still Inactive, no Slack interface, analytics unchanged. Parked states
  are correct.
- Queue hygiene: triage finding `82272892-discovery-sync-empty-payload-guard`
  flipped to built via triage-decide.py (it duplicated BSYS-29456, fixed 06:44 UTC).

Nothing posted to any ticket this pass either. All four replies stay staged,
awaiting Josh's confirmation.

---

# Third pass addendum (BTSUP service-desk agent, 2026-10-11 ~20:00Z)

## AGING FLAG - BTSUP-78227 leads the morning brief

**40+ hours cold.** The last customer-visible word on the ticket is Josh's
2026-10-09 17:53Z comment telling [requester] "I will take over from here" and
"this is on our side to fix". The root cause was found and recorded
internally 2026-10-10 05:47Z (comment 1134790, Service Desk Agents
visibility), but [requester] has never seen it. He is waiting on a promised
follow-up that already exists but has not been delivered, and the actual fix
(reattach Slack chat interface on the existing app A0C7HLXDUEN, start the
genie, one test DM) is a customer Production workspace write that stays
Josh-gated. Every hour this sits, the gap between [requester]'s expectation and
the real state grows. This is the first item on the morning brief.

Root cause re-check this pass: the customer workspace was last verified live
by the second pass at ~14:30Z today (genie still Inactive, no Slack
interface, analytics unchanged) and the root-cause file
`btsup-78227-genie-slack-trigger/root-cause-2026-10-10.md` is unchanged. This
pass did not re-open the customer workspace; the 14:30Z check stands as the
most recent live evidence and the root cause holds per it. The staged
customer reply (above) should only go out once the fix lands, so the fastest
way to unstick both the ticket and the reply is the fix itself.

## BTSUP-76729 fresh state check (live, read-only, ~20:00Z)

- PROD KB [kb-AYcm4ggH-L9o6zm-CD](https://app.workato.com/knowledge/kb-AYcm4ggH-L9o6zm-CD)
  doc 242843660: STILL STALE. 1,003 bytes, updated 2026-04-03, never
  refreshed. The employee-facing genie is still answering FTO questions from
  the pre-May policy right now.
- DEV KB doc 242843660: fresh and holding (3,924 bytes, page version
  2026-09-17, re-ingested 10-10).
- Sentinel [82959482](https://app.workato.com/recipes/82959482): Running
  True, weekly Mondays 13:00 UTC, dev-side only.
- Verdict: the 76729 draft
  (`btsup-drafts/btsup-76729-reply.md`) stands unchanged as a status
  update. The only customer-visible blocker remains the prod re-ingest /
  promotion, which is Josh's call.

## BTSUP-77184 and BTSUP-73287

No state change since the second pass. Drafts now saved as standalone files:

- `btsup-drafts/btsup-77184-reply.md` (nudge + close-out variants; asks which
  surface, Slack or MCP, and gives both reconnect paths)
- `btsup-drafts/btsup-73287-reply.md` (customer draft corrected to "live for
  Workday via HR Genie, Deel is the feature request" + internal feasibility
  plan: no build, Deel connection + skills ~3-5 points if approved, manager
  identity VUA trap flagged)

All four replies remain staged, nothing posted, nothing transitioned, no
writes to any Workato workspace this pass.

---

# Fourth pass addendum (jira-triage fleet job, 2026-10-11 ~22:15 PT)

## BTSUP-76729: collector-miss mechanism found (new evidence)

Full 764-job walk of collector 71498060 + trigger config + Confluence space
enumeration. The May FTO edit was lost to the Apr 29 - Jul 21 stop window;
the Jul 21 restart rescan skipped page 242843660 mid-walk even though the
Confluence API enumerates it fine (position 142/250); the trigger also
double-delivers pages within minutes. Full writeup:
`btsup-76729-collector-miss-mechanism-2026-10-11.md`. Posted as internal
comment 1135182 on the ticket (this is the first ticket comment this pass;
prior passes only staged drafts). Proposal unchanged from the drafts: prod
re-ingest/promotion + sentinel v2 full-KB sweep (2 pts), both Josh's call.

## BTSUP-73287: Deel API surface confirmed (backs the 3-5 pt estimate)

No native Deel connector in the Workato library (recipe_builder search
confirmed; Deputy/Concur are near-matches only). Deel's public API covers the
full approval surface at api.letsdeel.com (bearer OAuth, scopes time-off:read
+ time-off:write): GET /rest/time_offs (list, status filter REQUESTED),
POST /time_offs/review and HRIS POST /time-off/requests/{id}/review
(approve/decline), plus create/validate/cancel and policies/entitlements.
So the "Deel connection + manager approval skills" plan in
`btsup-drafts/btsup-73287-reply.md` is buildable as scoped; identity mapping
(Deel person_id to Slack/manager identity) stays the real cost driver.
No ticket comment added; the decision package was already staged.

## Queue verdict this pass

All four BTSUP tickets remain in their parked states with drafts staged;
78227 stays the aging lead (last customer-visible word Oct 9 17:53Z). The
only NEW ticket content this pass is the 76729 mechanism comment. Nothing
customer-facing posted, nothing transitioned, no writes to any workspace.
