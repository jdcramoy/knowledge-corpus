# BSYS-28420 plan — HR Genie: Add independent watchdog for monitoring pipeline self-health

Ticket: https://workato.atlassian.net/browse/BSYS-28420 (epic BSYS-26808, Backlog, Medium). Plan posted 2026-10-09 (comment 1134670); build executed and verified in dev 2026-10-10 (comment 1134845). This file refreshed 2026-10-11 after a live re-verification pass, re-confirmed the same evening.

## Current state (live evidence, 2026-10-11)

- [REC | Pipeline Watchdog (82959774)](https://app.workato.com/recipes/82959774) read live from dev: Running=True, every 5 minutes, own folder [Pipeline Watchdog (35769475)](https://app.workato.com/recipes?fid=35769475) in project 15643451. Checks verified in code: heartbeat freshness per component (table 158559), running state of every project recipe via the Workato API, read-only health probe of the primary Slack bot connection 20369210 (never sends through the probe), and delivery-claims checks (FAILED rows in the last 15 minutes in the inbox ledger 132894 and PTO ledger 127804). Incident lifecycle with one-alert dedup and exactly-one-recovery is implemented against [HR Genie Watchdog | Incidents](https://app.workato.com/data_tables/51365c22-2207-4ef8-b261-276a77a7981b) (158560).
- Design gate satisfied: the existing monitoring already covered recipe stops (RecipeOps + the stopped-by-user listeners, P1 severity work on this ticket 2026-08-27); the watchdog adds the missing separate failure domain rather than duplicating RecipeOps. Its own death is caught by RecipeOps externally, no recursion by construction.
- Controlled-failure evidence stands (comment 1134845): detection + first alert j-AbspKPwF-MRN3ob-CD, dedup j-AbspL9JW-HTPBEm-CD (zero sends), single recovery j-AbspLkXs-CrKhKL-CD, no second recovery j-AbspMNAe-3efWLC-CD, RecipeOps caught the watchdog's own stop (j-AbspNBfA-FHF9Mb-CD), monitored recipes' heartbeat calls verified non-behavioral.

## Honest gap vs the plan

The plan's alternate route was to share nothing with the primary bot path. Live today, the watchdog's first alerts post through the SAME Operations Workbot 20369210 the primary route uses; only the retry-cycle email fallback (Email by Workato, no connection) is truly independent. That matches the build comment's "email route is the proven interim," and the dedicated Slack app for the watchdog's Slack leg is the remaining load-bearing work, not a nice-to-have.

## Remaining work (the plan from here)

1. Dedicated workspace-owned Slack app + Workbot connection + OAuth for the watchdog's Slack leg (per the dedicated-app rule, no shared scopes). Browser/OAuth work via Orca; staged.
2. Swap the watchdog's Workato API read from the shared monitoring connection [13685697] to a watchdog-owned scoped API token (the project-local token 22080724 lacks recipes:read; flagged, not worked around).
3. AC1 10-minute-bound controlled stop of publisher/listener with alternate-route timestamps, plus the AC2 primary-Slack-failure canary drill, once the dedicated app is connected.
4. Add the discovery-hub components to the heartbeat registry when the hub recipes exist in dev (registry is data-driven; no recipe change needed).
5. Re-validate freshness thresholds against prod cadences at promotion.

## Acceptance criteria (outstanding)

- [ ] Stopping the publisher or a monitored listener alerts through the independent route within 10 minutes, with timestamps.
- [ ] A primary Slack delivery failure is visible through the alternate route (canary drill).
- [ ] Recovery closes the incident with exactly one message; dedup holds across repeated unhealthy cycles.
- [ ] Watchdog failure cannot loop; RecipeOps catches it (evidence already captured, re-verify post-app-swap).
- [ ] Monitored recipe behavior unchanged (heartbeat calls only, diff-verified).

## UAT Evidence

Controlled stops with alert timestamps proving the 10-minute bound, forced primary-route failure with alternate-route delivery evidence, single-recovery and dedup traces, a before/after diff of one monitored recipe showing only the heartbeat call, and the watchdog-kill RecipeOps trace. Dev controlled-test evidence cited above covers dedup, recovery, no-recursion, and non-behavioral wiring.

## Sequencing note

BSYS-29498 (Final Tech Review) deliberately EXCLUDES the watchdog recipe 82959774 and Incidents table 158560 from the prod batch, while the heartbeat function 82959725 and Heartbeats table 158559 travel with it. That split is correct and I would not fight it: prod gets heartbeat plumbing now, the watchdog follows once the dedicated Slack app exists. Nothing in my remaining work touches the batch's 44 assets; the token swap on 82959774 should wait until the batch import finishes so the shared connection 13685697's prod re-point (to 22284446) is not disturbed mid-flight. Sequencing relative to the Oct 2026 combined prod batch is Josh's call.

## Points

8 total. Build and dev verification are done; residual effort is about 3 points (dedicated app, token swap, controlled AC1/AC2 tests, registry additions, prod threshold re-validation). Note: the ticket's Story Points field holds 5 (the creation-time estimate); the plan's own arithmetic is 8 total / about 3 residual. Left the field alone since it is set; flagging the variance here.

## Evening re-check, 2026-10-11

Recipe 82959774 re-read live the evening of 2026-10-11: still Running every 5 minutes, still on the shared monitoring connection 13685697 for the API read and the Operations Workbot 20369210 for first-alert posts, so the honest gap above is unchanged and the dedicated Slack app remains the load-bearing remaining work. No state change; the morning ticket comment (1134970) stands as the current plan and no new comment was posted.

**plan ready — awaiting Josh's authorization to kick off the build.**
