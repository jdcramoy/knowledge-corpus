# BTSUP-78227: Ops Genie - PlanWise (2) Slack app not triggering Genie jobs

Ticket: https://workato.atlassian.net/browse/BTSUP-78227 (Biz Sys Review, medium)
Customer: [requester], workspace 3443496
Genie: https://app.workato.com/genies/gin-AbrPR8zH-gf8rGt-CD/overview

## State as of 2026-10-13 (this pass)

- Diagnosis stands from Josh's 2026-10-10 internal comment: genie Inactive in
  customer Production + Slack chat interface missing (the Oct 9 reconnect
  removed it; the re-add hit the duplicate-app trap). Only the Slack path is
  dead; the genie works through native chat.
- NOT re-verified this pass: the AIRO MCP binding in this session reaches only
  Josh's own workspace, so the customer genie returns 404 from here. The
  genie's current state is unchanged-since-Oct-10 by absence of evidence, not
  by observation. Before executing the fix, re-pull the genie live.
- Last customer-visible contact: Josh 2026-10-09 17:53 UTC ("I will take over
  from here"). Customer has been waiting on that promise since; the fix is the
  blocker, not the reply.

## The fix (Josh-gated, prod write in customer workspace)

1. Re-add the Slack chat interface on the genie build page, picking the
   EXISTING app A0C7HLXDUEN when prompted. Never create a new trigger; that
   spawns the duplicate "(2)" app.
2. Start the genie (watch for a config error on the missing Slack channel; if
   it errors, step 1 first, then start).
3. DM the bot once; confirm a job appears in the genie's job history.

Unverified from Oct 10: whether A0C7HLXDUEN still holds valid event
subscriptions after the reconnect cycle (screenshots suggest yes).

## Customer reply (DRAFT, posts only after the fix verifies green)

**Superseded 2026-10-14:** the postable-now draft is now
`draft-customer-reply-2026-10-14-consent-ask.md` (consent-ask variant, revised after
independent adversarial review broke the original framing; the Oct 10 diagnosis
survived that review). The variant below posts only AFTER the fix verifies green, as
the working-end-state confirmation. Old 10-12 draft kept in
`draft-customer-reply-2026-10-12.md` for the record.

Hi [requester],

Update, and this one has an end in sight. I pulled your genie up directly and found two things: it was sitting stopped in Production, and the Slack connection from the reconnect we did on the 9th never made it back on. Either one alone means silence from the bot; together they fully explain it. That reconnect advice was mine, so sorry it led into a trap in our UI: creating a new Slack trigger from the genie spawns a duplicate app instead of reusing yours, which matches the "(2)" you have been seeing.

I have re-added the Slack chat interface pointing at your existing app and started the genie. Could you send it one DM now? If it replies, we are done. If it stays quiet, send me the exact time of that message and I will take it to the platform team with the event payloads.

## Follow-up obligation

Posts to https://workato.atlassian.net/browse/BTSUP-78227 under Josh's name.
Track replies in ~/.claude/knowledge/slack-posts.jsonl? No: Jira ticket, the
comment itself is the thread; the nightly watchdog covers ticket replies.

## STAGED FOR EXECUTION (Josh go 2026-10-16, triage pass)

Josh's go recorded in triage 2026-10-16. Execute in a firing session with per-action
confirmation before each prod step:

1. Re-add the Slack chat interface on the genie build page, reusing app A0C7HLXDUEN
   (never create a new trigger).
2. Start the genie; verify running flag.
3. DM test; capture the job trace line.
4. Post the drafted customer reply (josh-writing-voice pass first).

Ticket: https://workato.atlassian.net/browse/BTSUP-78227
