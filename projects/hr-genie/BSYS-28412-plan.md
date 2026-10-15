# BSYS-28412 plan — Phase 3: optimize HR Genie discovery hub throughput without changing behavior

Ticket: https://workato.atlassian.net/browse/BSYS-28412 (epic BSYS-26808, Backlog, Medium). Plan posted 2026-10-10 (comment 1134770); build kickoff executed with baseline and shadow instrumentation 2026-10-10 (comment 1134842). This file refreshed 2026-10-11 after a live re-verification pass, re-confirmed the same evening.

## Current state (live evidence, 2026-10-11)

- [Inbox Task Discovery Hub 74482795](https://app.workato.com/recipes/74482795) and [Time-Off Event Hub 74094662](https://app.workato.com/recipes/74094662) both confirmed Running with green 5-min scheduler ticks: inbox j-AbtL4QBs-bAtx4p-CD (118s wall) and j-AbtKwtHE-Hgf6YE-CD; PTO j-AbtL4QCt-o9Q8CC-CD (36s wall). Job totals: inbox 13782 succeeded / 1048 failed lifetime; PTO 20568 / 1111.
- Build state per comment 1134842, unchanged since: 24h baseline collected (inbox p50 141s / p95 175s / max 296s, 53535 processor calls; PTO p50 40s / p95 47s; BP Completion hub p50 7s); approved target documented (p95 hub runtime < 4 min, 20% headroom); HUB_METRICS structured logging, in-memory identity dedup, and ledger pre-screen with re-action-safe skip keys deployed on all three hubs behind property gates that are OFF; rolling lookback wired into the inbox WQL predicate, value BLANK pending the older-than-window fixture test; rollback = property flip per hub plus pre-change package snapshot 42194959 (manifest 361043).
- Shadow numbers from the gate-OFF verification runs: inbox 40/215 calls (19%) would be ledger-skipped at cutover; PTO 94/94 REMINDER calls (98%); BP 6/6. Traces cited in comment 1134842.

## Remaining work (the plan from here)

1. Collect the >= 24h shadow diff across the six behavior classes (normal approvals, consolidated approvals, PTO events, Deny/Reject, Send Back, re-actioned tasks) from live traffic: HUB_METRICS shadow skip counts vs actual processor calls per cycle. The diff must be empty.
2. Older-than-window Send Back / re-action fixture test, then set the inbox lookback property to 7 days.
3. Pressure test at 2x the observed UAT row volume, no sustained job accumulation.
4. Flip the three Optimized Path gates, verify optimized-path traces, re-check the step-9 >1000-row truncation guard interaction.
5. UAT evidence collection and cutover approval. Prod promotion stays a separate approved batch.

## Acceptance criteria (outstanding)

- [ ] Shadow comparison produces identical notification identities across all six behavior classes.
- [ ] No missed and no duplicate notifications in the regression suite.
- [ ] Re-actioned tasks (new step ID) remain discoverable within the latency requirement.
- [ ] Lookback reduction property-controlled, reversible, tested against older-than-window fixtures.
- [ ] Pressure test at 2x volume completes without accumulation.
- [ ] Optimized-path failure fails open or supports immediate documented rollback.
- [ ] Baseline AC1 and the documented target are met (baseline done; post-change metrics continue via HUB_METRICS).

## UAT Evidence

Post-cutover HUB_METRICS tables vs the 2026-10-09/10 baseline, pressure-test job traces, the shadow-diff report per behavior class, a property-flip rollback rehearsal trace, and a notification-format read-back.

## Sequencing note

The hub recipes are not in the BSYS-29498 combined prod batch (manifest 361068 v5), so there is no file collision. The shared window is real though: the batch deploys the collector, monitors, and the full Intelligence Platform to prod, and the hub cutover would land nearby in the same project. I would not cut the gates over during the batch deploy window; whether Phase 3 cutover waits until the batch is green in prod is Josh's call.

## Points

5 total. Baseline and instrumentation are done; residual effort is about 2 points (shadow window, fixture test, pressure test, cutover, evidence). Story Points field on the ticket holds 5, matching the plan.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Evening re-check, 2026-10-11

Both hubs re-verified live the evening of 2026-10-11: green 5-minute scheduler ticks all day, recent inbox walls 137 to 154 seconds and PTO walls 36 to 46 seconds (inbox recent traces j-AbtgAJnK-DCrpwk-CD, j-Abtg4mwd-8YCETH-CD, j-AbtfxHBr-fFJMfA-CD; PTO j-AbtgDsMQ-QAbTpb-CD). Lifetime totals moved from 13782/1048 and 20568/1111 this morning to 13983/1048 and 20770/1111 by evening: about 200 new successes per hub with zero new failures, so the transient Workday window behind the 40-failure cluster did not recur. Runtimes still track the baseline and sit under the 4-minute target, consistent with gates still OFF. No state change; the morning ticket comment (1134969) stands as the current plan and no new comment was posted.
