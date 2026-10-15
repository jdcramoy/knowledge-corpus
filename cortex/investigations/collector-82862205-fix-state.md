# Investigation: recipe 82862205 (REC | HR Genie | Conversation Event Collector) fix state

Investigated: 2026-10-10 ~06:00Z, read-only. Evidence: build-ledger.jsonl lines 5688-5858, live recipe_get (dev AIRO), job traces, regression-canon/canon.jsonl lines 46-47, watchdog-reports/2026-10-09.md item 3, projects/hr-genie.md, BSYS-29488.

Asset: https://app.workato.com/recipes/82862205 (Running=True, dev folder 35712141, project 15643451)

## Q1: Has ANY fix push landed since 2026-10-08?

YES — a full repair session ran this morning. Build ledger (session `hrg-coll-82862205-repair-20261010`, ticket BSYS-29488) shows 21 mutations on 2026-10-10 with THREE `recipe_builder_push` events:
- 04:44:17Z, 05:06:19Z, 05:23:26Z

Live recipe confirms the pushes landed: step 21 empty-batch guard (`if batch_size > 0` wrapping the foreach AND the checkpoint update), step 13 conversation cursor-cycle guard, step 27 event-page overflow guard, step 31 fixed skip breadcrumb (no raise), step 33 empty-transcript short-circuit, step 39 monotonic checkpoint + all-skip guard, BSYS-29477 +1s watermark offset, BSYS-29488 6-hourly 7-day resweep.

## Q2: Is the failing guard test stale, or expecting a never-built fix?

NEITHER stale NOR never-built: the test ran FIRST and the fix followed. Timeline:
- 2026-10-10 00:50Z — guard test `guard-empty-conversation-batch (BSYS-29455)` FAILED (job j-AbshmCmT-JTPhNk-CD, run cirr-AbshmCme-QPxHdL-CD)
- 04:43-05:23Z — repair session pushed 3x (above)
- Test case citc-AbsPGsnb-MALQch-CD has NOT been re-run since the pushes — the fix is built but UNVERIFIED by its own canon test.

Two caveats: (a) canon.jsonl line 47 flags the test job itself died with error "Processed event" and ZERO trace lines — an error string that exists nowhere in recipe code — so the test harness/mock may ALSO be faulty, not just the recipe. (b) The recipe has since regressed into a NEW failure mode (below), so a re-run today would fail on that instead. Verdict: test is valid-but-unre-run; expect a re-run to require both a recipe fix (phantom row) and a test-harness check (trace-less mock).

## Q3: Exact remaining fix gap, per class

- Empty-batch class: ORIGINAL crash ("data must not be empty", line 11, schedulers) is FIXED by the step-21 guard, but the class MORPHED — drain-loop step 14 (`insert_to_list_14`) still inserts a phantom conversation of blank strings when a page returns 0 rows with blank next_cursor; that phantom (batch_size=1, id='', created_iso='1970-01-01T00:00:00Z') fails its event read, trips the step-39 all-skip guard, and crashes with `COLLECTOR_ALL_CONVERSATIONS_SKIPPED: 1/1 conversations failed their event read` — 5 consecutive scheduler failures since 21:24 PDT 10-09 (j-AbshMP9L, j-Abshbxnp, j-AbshpXfk, j-Absk99aB, j-AbskKeQa). Remaining gap: drop blank-id rows from the batch in step 18 (or skip the page-append in step 14 when the page is empty).
- 'Extra keys: log' class: 3x burst 06:51-06:55 PDT 10-09 on Test Automation "Processed event" jobs (j-AbsPREAn / j-AbsPPrMo / j-AbsPN9c9); per projects/hr-genie.md these were stale-snapshot comparisons from editor-Test runs polluting the job list, and the 10-10 rebuild restructured the snippets — every current snippet returns only schema-declared keys, no `log` anywhere. Zero recurrences since. Remaining gap: NONE in recipe code, but unresolved in evidence — no post-repair run has exercised the old logging path; treat as resolved-by-restructure pending one clean regression pass.

## Bottom line

The 10-08 crash class was genuinely fixed this morning (BSYS-29488 repair, 3 pushes), the canon guard test predates the fix and needs a re-run, and the recipe is NOT healthy: it crashes every 15-min scheduler tick on a phantom-row defect one layer upstream of the original bug. Next actions (dev, per standing rules): fix the blank-id batch filter, re-run guard-empty-conversation-batch, then green-light the nightly regression.
