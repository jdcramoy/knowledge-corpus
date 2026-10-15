# Autopsy 2026-10-10 — Collector 82862205 new-failure sweep (flagged on BSYS-29477)

Dev workspace, dev AIRO MCP only. Autopsy + propose; no recipe edited, no status transition, no prod touch.

## Verdict

The six new failed jobs (2026-10-10 04:24-05:24 UTC) are NOT a recurrence of the BSYS-29477 watermark bug and NOT a fault in the BSYS-29455 fix. They are a **new phantom-conversation regression introduced inside the edit window of the in-flight BSYS-29488 repair session** (`hrg-coll-82862205-repair-20261010`), plus its downstream crash-surface re-exposures. Full evidence posted as [BSYS-29488 comment 1134787](https://workato.atlassian.net/browse/BSYS-29488); cross-reference on BSYS-29477 comment 1134788.

## Job classification (all traces walked to origin)

| Job (UTC 2026-10-10) | Failure at origin | Class |
| --- | --- | --- |
| j-AbshMP9L (04:24) | drain-loop while_condition → None, mid-edit churn (set_condition pushes 04:24:17-25) | (c) regression, repair churn |
| j-Abshbxnp (04:39) | same while_condition signature, event drain loop | (c) regression, mid-edit artifact |
| j-AbshmCmT (04:49) | trace-less "Processed event" — regression test case guard-empty-conversation-batch (BSYS-29455) | (a) known test artifact, already canonized open |
| j-AbshpXfk (04:54) | 404 Conversation not found at per-conversation event fetch, untolerated revision | (c) regression |
| j-Absk99aB (05:09) | `data must not be empty` at watermark update | (a) BSYS-29455 crash class recurrence via phantom batch |
| j-AbskKeQa (05:24) | COLLECTOR_ALL_CONVERSATIONS_SKIPPED 1/1 at Compute checkpoint; batch_size=1, conv_id='', max_created_iso=1970-01-01T00:00:00Z | (d) new failure mode |

## Root cause

The conversation-list drain loop's page-accumulate step (step 14, `insert_to_list` on `conv_pages`) inserts `data[0]` fields unconditionally. The cursor-cycle guard (step 13) only raises on `page_rows == 0` WITH a non-blank `next_cursor`. A terminal empty page (`data: []`, blank cursor) passes the guard and materializes a phantom conversation with blank id/created_at. batch_size becomes 1, defeating the empty-batch guard (`batch_size > 0`); the blank-id event read 404s; revision-dependent outcomes: raw 404 → empty-data update crash → tolerated skip + all-skip guard raise. The all-skip guard itself worked as designed (visible stop, no silent coverage loss).

Attribution evidence: last green scheduler run 04:02 UTC; first failure 04:24 UTC; build-ledger pushes at 04:21:58 / 04:25 / 04:29 / 04:44 / 05:06 / 05:23 UTC. Pre-refactor empty-page runs at 03:02-04:02 UTC were green.

## Proposed fix (awaiting BSYS-29488 repair session / Josh's authorization — not built)

1. Cursor guard treats `page_rows == 0` as terminal regardless of next_cursor, or skip the accumulate insert when `data` empty / `data[0]['id']` blank.
2. Defense in depth in "Prepare conversation batch" (step 18): reject rows with blank id before batch prep.
3. Keep the all-skip guard.
4. Finish the collector's normal/empty/multi-page/late-or-equal/replay proof pass per the BSYS-29488 handoff comment.

Regression fixtures: (1) List-conversations returns `data: []` + blank cursor → expect batch_size=0, guard False, watermark untouched; (2) `data: [{}]` blank row → expect row rejected, batch_size=0.

## Side observations

- Watermark `last_wm` is in Ruby `Time#to_s` format (`2026-10-09T23:12:03.000000+00:00`), not the recipe's canonical `%Y-%m-%dT%H:%M:%SZ` — written outside the recipe's normal path; reset during the proof pass.
- No jobs after 05:24 UTC as of 05:34 UTC despite Running=True; next scheduler tick 05:39 UTC is the first read on the 05:23 push.

## What was NOT verified

- The exact revision of the recipe that ran at each failure timestamp (Workato exposes only the current definition; version attribution is inferred from build-ledger push timestamps vs job start times).
- Whether the empty page returned `data: []` or a literal blank row — both are covered by the same proposed guard; the response body is masked in the trace.
- Whether the 05:39 UTC scheduler tick ran green on the final 05:23 push (after this autopsy's observation window).
- The 04:49 test-case failure is accepted from the existing canon entry (cirr-AbshmCme-QPxHdL-CD) rather than re-pulled fresh.
