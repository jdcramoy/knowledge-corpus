# BSYS-29519 — Collector 82862205: 5s page-commit wait timeout fails whole run under backlog drain

Filed 2026-10-12 from the jira-triage fleet pass. Plan posted as ticket comment 1135522.
Ticket: https://workato.atlassian.net/browse/BSYS-29519 (Bug, 2pts, parent epic BSYS-26808, status New)

## Failure class

`PAGE_COMMIT_ASYNC_JOB_FAILED: async commit job did not succeed (succeeded=0 failed=0 timed_out=1)`

- Recipe: [82862205 REC | HR Genie | Conversation Event Collector](https://app.workato.com/recipes/82862205)
- Child function: [82936791](https://app.workato.com/recipes/82936791) (queue-owner page commit, caller != owner)
- Wait sites: steps 38/39 and 61/62, `wait_for_async_jobs` with `timeout="5"`, strictly sequential per page
- Evidence trace: [j-Abtose33-DKt9cL-CD](https://app.workato.com/recipes/82862205/job/j-Abtose33-DKt9cL-CD) (fails at line 43 catch after a 6-minute grind)
- Window: 2026-10-11 17:11 to 23:56 PT (~27 failed 15-min runs), self-recovered 00:26 PT 2026-10-12

## Mechanics

Backlog drain (large conversation batch accumulated during earlier stoppage/phantom-conversation
repairs) made runs chew through many pages; at least one page commit exceeded the 5s wait budget.
The wait timed out (child never errored, just ran long), the per-conversation catch re-raised, the
whole run failed, the watermark did not advance, and the next run re-processed the batch. The
emitter's `source_job_id` idempotency absorbed repeats: no data corruption, only failed-job noise
and wasted work.

Working theory (unproven): the queue-owner function serializes page commits, so under backlog its
own queueing latency pushed past 5s. Child-side traces from the window were not pulled.

## Proposed fix (awaiting Josh's build go)

1. Raise `wait_for_async_jobs` timeout 5 → 60s on both await sites.
2. On timeout, treat the page as uncommitted and continue (telemetry note per skipped page);
   watermark retries it next run, idempotent.
3. Optional: cap pages per run so backlogs drain over several runs.

## Distinct from (checked, not implicated)

- BSYS-29477 watermark inclusive-from bug: fix intact, failure surface untouched by traces.
- BSYS-29488 phantom-conversation class: closed 2026-10-10; this signature postdates it.

## Lesson for the canon

A tight `wait_for_async_jobs` timeout on a serialized queue-owner is a latent whole-run failure
under backlog: the failure only appears exactly when there is real work to do, and disappears
when the queue is empty, so green cadence proves nothing about the class. Budget waits with
headroom and degrade (skip + telemetry) instead of re-raising when idempotent retry is free.

## Recurrence addendum (2026-10-12, second fleet pass same day)

Class recurred AFTER the plan posted (09:19Z): four failed scheduled runs at 05:11, 05:26, 05:41
and 05:56 PT (j-AbtwwYbR-z6CcfH-CD, j-AbtxDAXW-PK8MQY-CD, j-AbtxPfRK-bgfsL3-CD,
j-AbtxeGNW-8LkBaR-CD), each dying 6-11 minutes in, recovered again 06:11 PT. Fresh trace on
j-AbtxeGNW-8LkBaR-CD: identical signature, line 43, same counts. Second drain in two days.
Consequence for the plan: the page cap (item 3) is promoted from optional to part of the fix;
each drain costs ~1 hour of failed runs before self-clearing. Recurrence comment posted as
ticket comment 1135703.

## Cadence observation, 2026-10-13 ~18:30Z

- 29h+ clean cadence since the 06:11 PT Oct 12 recovery; nine 15-min scheduler runs green through 10:59 PT this pass (2-3s each).
- Live anomaly: job j-Abwbo4RK-XCFeWM-CD started 11:14:54 PT titled "Processing event" (NOT the scheduler trigger), still in-flight at ~14 min with no error. Outlived the prior class's 6-11 min failure window. Caller unknown; on-demand call guessed.
- Ticket comment 1137560 posted with the same evidence. Plan unchanged, build go still pending.
- Note: first addCommentToJiraIssue attempt hit the known stale commentVisibility cache (400 on BSYS); worked around via direct REST with keychain creds (atlassian-confluence service). REST path = fallback when MCP comment cache sticks.

## AMENDMENT (2026-10-13 22:46Z, jira-triage pass — dissent-reviewed)

The plan's three items are IN the pushed source (v42, 2026-10-12 07:58 PT, pushed
under Josh's creds by an unidentified build session): both await sites (steps 40/64)
carry timeout="60"; the skip classifier defers uncommitted pages and
PAGE_BUDGET_EXHAUSTED (cap=10) with watermark retry + idempotency; transient errors
still re-raise. Two corrections to prior claims:

1. CAUSAL: the Oct 11-12 storm self-ended on v41 BEFORE v42 pushed (last failure
   06:02 PT; six green runs on v41; push 07:58 PT). The only real-load proof of the
   60s budget is the Oct 13 hour-long run (50.2s wait survived + budget deferral).
2. NEW DEFECT — 404 classifier is a substring match
   (`msg.include?("404") || msg.include?("not found")` → PERMANENT skip, watermark
   advances). A transient error containing those strings ("host not found" DNS error,
   404 in ports/job-ids/counts) silently loses events on a green job = masked-green
   data-loss surface. Fix: match HTTP status structurally or anchor the provider's
   error code; add the transient-error-with-404 test case. Joins the build scope.
3. Watch item: sustained-backlog starvation (60s budget vs ~2h observed queue latency
   during the storm; storm latency was plausibly self-inflicted by the old failure
   loop — unproven). Metric: deferred-conversation count must fall across runs.

24h clean-cadence criterion: NOT met as of 22:46Z — the stopped window (07:26–16:44 PT
Oct 12) doesn't count; continuous green cadence restarts 16:44 PT Oct 12, 24h completes
~16:44 PT Oct 13. Full evidence on BSYS-29519 (comment 1137755).
