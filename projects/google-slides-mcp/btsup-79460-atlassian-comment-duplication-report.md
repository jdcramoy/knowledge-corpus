# Bug report for BT Support / Atlassian: duplicate comment rows from one API POST

**Ticket:** BTSUP-79460 (Slack mirror triplication of the 2026-10-23 hotfix comment)
**Reporter:** Josh Cramoy (investigation by Claude Code session, 2026-10-23)
**Destination:** BT Support team (Jira admins) — Atlassian-side defect, nothing wrong with our recipe

## Verdict

One authenticated REST API POST to Jira created **three identical comment rows**.
Jira's 201 response returned only one of them. Our downstream Jira→Slack notifier then
mirrored each comment row 1:1 — so Slack showed the comment three times. Later,
"Atlassian Assist" deleted two of the three rows without us asking it to.

## Evidence (all captured live 2026-10-23)

1. **Our side posted exactly once.** Session transcript: one `POST /rest/api/3/issue/BTSUP-79460/comment`
   → HTTP 201, `comment_id: 1147867`, read-back VERIFIED at 16:24:01.734Z. Our client
   retries only on 429/5xx with 8s+ backoff — it cannot produce sub-second duplicates.
2. **Jira created three rows from that one POST.** The JSM→Slack webhook fired three
   comment-created events at 16:24:04 / :06 / :08 UTC (Workato job trace, recipe 69459301):
   - comment `1147865`, created 16:24:00.657Z
   - comment `1147866`, created 16:24:01.532Z
   - comment `1147867`, created 16:24:02.532Z
   All three: actor Joshua Cramoy (the same authenticated request), identical ADF body,
   spacing 875ms / 1000ms — machine-regular, consistent with a server-side processing
   retry without idempotency. The 201 response carried only id 1147867.
3. **Our mirror behaved correctly.** One webhook in → one Slack post out, three times.
   It is a faithful 1:1 mirror, not the source of duplication.
4. **Atlassian Assist deleted two rows** at 16:26:34.108Z and 16:26:40.532Z (issue
   changelog, field Comment) — including the id our API call returned. One identical
   row (1147865) survives.

## Impact

- Any API-driven comment (bot/integration traffic) can be silently duplicated inside
  Jira; downstream webhook consumers see N duplicate comment-created events for one
  POST and cannot distinguish them from real comments.
- The duplication plus the unrequested Assist deletion makes audit trails unreliable
  (comments appear, vanish, and renumber under integrations' feet).

## Ask

1. Confirm the server-side duplication (one POST → rows 1147865/66/67 on BTSUP-79460
   at 2026-10-23T16:24Z) with Atlassian and raise it upstream if reproducible.
2. Clarify why "Atlassian Assist" deleted two comment rows without a user request, and
   whether that auto-dedupe is sanctioned behavior integrations should expect.
3. If there is an idempotency mechanism for comment creation (client-generated comment
   key), tell us so our integrations can adopt it.

## Disposition of the Slack duplicates

Josh deleted the two duplicate Slack messages manually. No further cleanup pending.
