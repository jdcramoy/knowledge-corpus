# BTSUP-78227 — Ops Genie - PlanWise Slack trigger dead: root cause + fix plan

**Status:** root cause found 2026-10-10 (fleet jira-triage pass). Fix is Josh-gated (customer Production workspace writes). Internal note posted as [comment 1134790](https://workato.atlassian.net/browse/BTSUP-78227) (Service Desk Agents visibility).

## Evidence (live, read-only inspection)

- Genie: [Ops Genie - PlanWise](https://app.workato.com/genies/gin-AbrPR8zH-gf8rGt-CD/overview), customer workspace 3443496, project Ops, **Production** env. Reached via Orca browser: Okta SSO → Workato AHQ \| BT Ops → workspace switcher ("[requester]'s team") → env switcher → Production.
- Status banner: **Inactive**. Start genie button present.
- Build page Triggers section ("Chat interfaces and recipes that call this genie"): **native Workato chat + one recipe caller only. No Slack chat interface.**
- Analytics (last 30 days): 2 conversations, 4 end-user messages, 2 unique users — all via the native channel; skills fired (1 KB call failed, 1 feedback call succeeded). The genie itself works; only the Slack path is dead.

## Root cause

The Slack chat interface was removed during the Oct 9 reconnect cycle (Josh's 13:40 instruction: remove trigger + connection, re-add fresh) and the re-add never completed — [requester] hit the trap where creating a new trigger spawns a duplicate Slack app (he asked about this at 13:54, gave up 14:51). The genie was left stopped. Stopped genie + missing Slack interface = zero jobs. Not a platform bug; no platform-team escalation needed.

## Fix path (Josh-gated, customer prod)

1. Genie build page → re-add Slack chat interface → select the EXISTING app **A0C7HLXDUEN** (never create a new trigger).
2. Start the genie.
3. One DM to the bot → confirm a job appears in genie job history.

## Draft customer reply (staged — send only after the fix lands)

> Hi [requester], good news, I found the root cause in your workspace. The genie is currently stopped, and its Slack trigger was removed during the earlier reconnect attempts, so your Slack messages had nothing to reach. The genie itself works fine; it has been answering through the web channel. I am reattaching your existing Slack app and starting the genie now, then I will send one test message and confirm here once it creates a job end to end.

## Not verified

- Whether A0C7HLXDUEN still holds valid event subscriptions post-reconnect (screenshots suggest yes).
- Whether Start genie surfaces a config error on the missing Slack channel (would change the re-add sequence).
