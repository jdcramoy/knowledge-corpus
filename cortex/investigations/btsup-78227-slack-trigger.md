# BTSUP-78227 Investigation: Slack app not triggering Genie jobs

**Status:** Biz Sys Review | **Assignee:** Josh Cramoy | **Reporter:** [requester]
**Created:** 2026-10-08 08:35 UTC | **Last update:** 2026-10-09 17:53 UTC
**Investigated by:** cortex agent, 2026-10-09 (read-only)

## Ticket facts (from getJiraIssue, all 19 comments read)

- Customer user [requester]'s Slack app **"Ops Genie - PlanWise (2)"** (App ID **A0C7HLXDUEN**) no
  longer triggers his Workato Genie. DM and @mention both produce: no reply, **no job history
  entry at all**.
- **Workspace:** 3443496 (customer workspace, NOT Josh's dev 3535597 / prod 3535598)
- **Genie:** https://app.workato.com/genies/gin-AbrPR8zH-gf8rGt-CD/overview
- **Workato event receiver URL (verified OK by Slack challenge):**
  https://www.workato.com/workato_genie/slack/689bb888-8f90-4445-8eec-e8e593627105/webhooks/event
- Scopes screenshot reviewed by Marjoe (BT) 2026-10-09 05:35 — "permission looks ok".
- [requester] reinstalled the app recently (scopes added, approved, reinstalled). NOTE: a reinstall
  revokes the previous bot token.
- [requester] states he **cannot view the delivery logs** at the bottom of Slack's Event
  Subscriptions page — so it has NEVER been confirmed whether Slack delivers any events.
- Josh's checklist (2026-10-09 06:26): verify message.im + app_mention bot-event
  subscriptions; verify reinstall went through the genie flow (not api.slack.com); check
  duplicate-app "(2)" suspicion. [requester] says he "did everything in the list" and later
  completed a full trigger+connection reconnect per Josh's 13:40 instructions. Still silent.
- [requester] asked whether to reuse the existing app because "creating a new trigger from genie
  workflow creates a new app" — evidence he was on the duplicate-app path at least once.
- Josh's 17:53 verdict post: taking over, will check genie trigger/callback config directly
  ([requester] granted workspace access), then escalate to platform team with payloads/timestamps.

## Probe results (this session, read-only)

- `genie_get(gin-AbrPR8zH-gf8rGt-CD)` via AIRO dev server → **HTTP 404 Genie not found**.
  Confirms the genie is not in any workspace our MCP tools reach; direct live verification of
  the customer genie is not possible from this harness (our AIRO/dependency-tracker scopes are
  Josh's own workspaces). The dependency-tracker route was permission-gated headless.
- Therefore: no live job trace, no trigger config read, no connection health read for
  workspace 3443496. Everything below is evidence-weighted inference from the ticket.

## Failure-class determination

Candidates evaluated: (a) bot app removed from channel, (b) connection auth expired,
(c) trigger recipe stopped, (d) VUA drift, plus (e) Slack-side event subscription missing /
duplicate app.

**Most likely: (e) Slack-side event delivery failure — bot-event subscriptions
(message.im / app_mention) missing on A0C7HLXDUEN and/or events firing on the duplicate
older app — with (b) stale/revoked bot token as the runner-up.**

Reasoning, per class:

- **(e) event subscriptions / duplicate app — LIKELY PRIMARY.** Verified request URL proves
  only that Slack can reach the endpoint (challenge handshake), not that it sends events.
  Verified scopes are a different page than "Subscribe to bot events"; manifest/scope edits
  commonly drop bot-event subscriptions. The "(2)" suffix implies a duplicate app, and [requester]
  was actively creating new triggers that spawn new apps. Zero job history is exactly what
  this class predicts: Slack never sends anything, Workato never receives anything. Critically,
  the one diagnostic that would falsify it (the delivery log) is the one thing [requester] could
  not access. Workato-side reconnects having no effect is also consistent — they cannot
  restore Slack-side subscriptions.
- **(b) connection auth expired / revoked token — plausible secondary.** Reinstall revokes
  the old bot token; if the reinstall was done from api.slack.com, Workato holds a dead token
  and may drop events at routing (token→workspace mapping) before creating a job. [requester]'s
  full reconnect should have refreshed it, which he says he did — but his last exchange shows
  he may not have completed it through the genie flow (he asked whether to reuse the app, then
  gave up). If the Slack delivery log DOES show deliveries with 4xx, this becomes primary.
- **(a) bot removed from channel — UNLIKELY.** DMs (message.im) do not require channel
  membership, and DMs fail too.
- **(c) trigger recipe stopped — UNLIKELY/NOT APPLICABLE.** This is a genie Slack trigger,
  not a recipe trigger; no recipe is named anywhere in the ticket. A paused genie could
  produce silence, but nothing in the ticket suggests the genie was paused, and the reconnect
  cycle would have surfaced it.
- **(d) VUA drift — RULED OUT as primary.** VUA/end-user-connection drift manifests as jobs
  that fire and error on skill execution. [requester] has zero job history — the trigger never
  fires. VUA drift cannot explain absent jobs.

## Decisive next check (needs Josh — he has workspace access; [requester] apparently lacks api.slack.com access)

1. Get api.slack.com access for A0C7HLXDUEN ([requester] cannot see the settings pages — find the
   Slack workspace admin/owner if he is not it).
2. Check "Subscribe to bot events" includes **message.im** and **app_mention**; and check the
   **delivery log** for events at the test-message timestamps. This single log splits the two
   live hypotheses: no deliveries → (e) subscriptions/duplicate app; deliveries with 4xx/5xx
   → (b) token/routing, fixed by re-saving the Slack app details in the genie build page.
3. Confirm the genie's Slack trigger is bound to A0C7HLXDUEN (not the older duplicate) and
   that the genie itself is active.

## What was NOT verified

- Genie trigger config, connection health, and job history in workspace 3443496 — unreachable
  from this harness (404 on genie_get; dependency tracker not granted headless).
- Slack-side event subscriptions and delivery log for A0C7HLXDUEN — requires api.slack.com
  access [requester] lacks.
- Whether [requester]'s "full reconnect" actually completed through the genie flow.
