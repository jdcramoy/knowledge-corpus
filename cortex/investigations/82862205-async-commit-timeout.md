
---

# Autopsy: 82862205 PAGE_COMMIT_ASYNC_JOB_FAILED (async commit timeout) — 2026-10-11

**Investigator:** claude (cortex-dispatched autopsy, read-only)
**Date:** 2026-10-11 ~18:35 PT
**Scope:** read-only. Nothing edited, stopped, started, or posted.
**Assets:** REC | HR Genie | Conversation Event Collector — https://app.workato.com/recipes/82862205 (dev) ; FUNC | HR Genie | Commit Collector Page (queue owner) — https://app.workato.com/recipes/82936791 (dev)
**Reported against:** BSYS-29477 comment 1135099; distinct from the closed BSYS-29488 phantom-conversation class.

## TL;DR

The parent collector is a VICTIM. The origin is the commit-owner function 82936791: its "Complete POST observation readback before durable ACK" repeat loop (trace lines 61-67) never terminates when the readback set spans more than one data-table page. The loop spins until the platform's 50,000-iteration repeat limit kills the job ~1h42m later ("Reached repeat limit of 50,000. Check condition" / Iteration limit exceeded). While one owner job spins, every later async commit call queues behind it; each parent collector tick that finds work waits its 5-minute `wait_for_async_jobs` timeout, gets `succeeded=0 failed=0 timed_out=1`, and its own fail-closed verifier raises PAGE_COMMIT_ASYNC_JOB_FAILED by design. Both failure bursts today (11:11-11:56 PT and 17:11-17:56 PT) started one tick after the 6-hourly resweep ticks (18:00 and 00:00 UTC) — the resweep's 7-day window is what produces event pages big enough to trip the multi-page readback. The parent's failure handling worked exactly as designed (fail closed, watermark held). The bug is in the child.

## Failure class

**Classification: code bug (child recipe loop non-termination), with a platform-behavior contributor.** New canon class. Not the BSYS-29488 phantom-conversation class: that class was under-collection upstream; this one is the new page-commit lane's owner deadlocking itself on readback pagination.

## Evidence (all live pulls, dev workspace, 2026-10-11)

### Parent 82862205 — 4 failures in the evening burst (one more than the 3 in the dispatch note)

| Job | Started PT | Duration | Failed line |
|---|---|---|---|
| https://app.workato.com/recipes/82862205/job/j-AbtfPLpk-cTJM8z-CD | 17:11:04 | 11m38s | 50 (insert_to_list; same window, downstream victim) |
| https://app.workato.com/recipes/82862205/job/j-Abtfdtme-wA4BHr-CD | 17:26:04 | 5m58s | 43 (catch-handler Ruby re-raise) |
| https://app.workato.com/recipes/82862205/job/j-AbtfsTgD-NHBXXH-CD | 17:41:04 | 5m58s | 43 (same) |
| https://app.workato.com/recipes/82862205/job/j-AbtgB6d8-cLJRot-CD | 17:56:04 | 5m58s | (same class, 4th in burst) |

Traces of j-Abtfdtme / j-AbtfsTgD: line 37 `call_recipe_async` (flow_id=82936791) fires, line 38 `wait_for_async_jobs` returns with `timed_out=1`, the catch (42) routes to line 43 "Note skipped conversation" Ruby whose input literally carries `error_message: 'PAGE_COMMIT_ASYNC_JOB_FAILED: async commit job did not succeed (succeeded=0 failed=0 timed_out=1)'`. That label is authored in this recipe's own step 41 "PC V1 Verify commit ack envelope" — the fail-closed verifier built this morning under BSYS-29498. So the collector detected a commit-timeout and raised on purpose. Design worked; the timeout is real.

Morning twin burst: parent jobs 11:11 / 11:26 / 11:41 / 11:56 PT failed the same way (first ~12 min, then ~6 min each), green from 12:11 through 16:56 PT.

### Child 82936791 — the actual origin

- **Morning:** job https://app.workato.com/recipes/82936791/job/j-AbtYkDXa-a3PBNt-CD started 11:17:19 PT, ran **1h41m55s**, failed 12:59:14 PT at trace line 67 (`while_condition`) with **"Reached repeat limit of 50,000. Check condition" — Iteration limit exceeded**. Trace lines 61-67 = the POST-observation readback loop: `get_records` on table 158100 (3349s cumulative = ~50k x 67ms — the table was answering the whole time), Ruby canonicalizer (1319s), smart-list append (424s), update_variables (36s). The while_condition evaluated `{'condition': True}` on every one of the 50,000 iterations. The exit predicate never became false.
- **Evening:** job https://app.workato.com/recipes/82936791/job/j-AbtfX3nz-fzWNMW-CD started 17:17:41 PT and was **STILL PENDING at 18:26+ PT** (>1h09m, no trace lines yet — same signature in flight; expected to die ~18:59 PT at the 50k limit like its morning twin).
- Around both hangs, the child was otherwise healthy: ~26 commit jobs 17:11:12-17:17:29 PT, each green in 1-2s (small/replay pages). Zero child jobs were created after 17:17:41 — commit calls from the 17:26/17:41/17:56 parents **queued behind the hung job and never became jobs**; they are still queued and will flush when the hung job dies (morning proof: 3 backlog jobs flushed 12:59:15-19 within 4s of the hang dying, 1 green / 2 failed).
- Correlation with the resweep: the collector widens its window to 7 days at 00/06/12/18 UTC (BSYS-29488 late-event resweep). 11:11 PT = 18:11 UTC. 17:11 PT = 00:11 UTC. Both bursts begin on the first tick after a resweep tick; every non-resweep tick today was green. Normal-window ticks produce small pages; resweep ticks produce big multi-page event reads.

### Mechanism (from the recipe code, both pulled live)

Parent lane (built today, BSYS-29498, v40): N1 identity/HMAC → G1 predecessor read (158155) → N2 signed proposal → A1 `call_recipe_async` 82936791 → W1 `wait_for_async_jobs timeout=5` (raised from 1 to 5 this morning ~07:56 PT, session "cutover-timeout-fix-82862205") → G2 durable readback → V1 fail-closed verify. Strictly sequential per page: each page's commit must be ACKed before the next page is proposed.

Child loop (82936791 trace lines 61-67): `while True` repeat → `get_records` table 158100 filtered by (capture_job_hmac, capture_cycle_hmac, page_ordinal), order_by asc, **limit=100** → Ruby "Canonical POST observation page" computes `private_next_cursor` / `has_more` / `seen_cursor_hashes` → conditional smart-list append → `update_variables_67` writes lookup_cursor / lookup_pages / matched_rows / seen_cursor_hashes_json / sql_bytes.

## Root-cause hypothesis (ranked)

**H1 (leading): loop-carried state does not advance across repeat iterations, so any readback needing page 2 spins forever.** The collector's own spec (`projects/hr-genie/page-commit-cutover-spec-20261011.md` §1) documents the proven platform law: "Variables-in-loop updates do not persist" — which is why the collector carries loop state in declare_list slots. The child's readback loop carries its cursor via `update_variables` (step 67) instead of the list-slot idiom. If the update does not persist, iteration 2 re-fetches page 1 with the same (empty) cursor, gets the same 100 rows and the same continuation token, forever: condition True 50,000 times, byte-cap guards never trip (sql_bytes also resets), exactly as observed. Consistent with every green commit being a single-page (<=100-row) readback and both hangs arriving with the first >100-row readbacks (resweep traffic).

**H2 (alternative, same trigger): the data table returns a non-clearing continuation token at/above the 100-row boundary** under this filter+order_by, and the `seen_cursor_hashes` cycle guard (also carried via the same non-persisting variables) never gets a chance to break it. H1 and H2 share the same discriminating test and the same fix region; H1 is favored because the non-persistence law is already project-canon and the loop's state-carry idiom is demonstrably the non-proven one.

**Contributing design factor (not a bug, but it amplifies):** queue-owner serialization is caller-side AND platform-side — one stuck owner job blocks all later async commit calls, and the parent's 5-minute wait is 20x shorter than the ~1h42m platform kill-switch, so every tick in the window fails deterministically. Also note: the poison commit's fact inserts (step 51 `create_records_batch`) DID run before the readback loop — facts are likely durable; what never lands is the progress-row ACK, so replays re-enter the same spin. The condition is self-rearming, not self-healing.

**Ruled out:** connection/auth (all adapters green throughout, sub-second), upstream API outage (parent's event fetches green in the same jobs), the morning timeout=1→5 change as a cause (it only bounds the wait; the child hang is 20x the bound), BSYS-29488 class (that was collection-scope; this is commit-lane).

## Current live state (as of ~18:35 PT, verified by fresh job lists)

- Parent: green ticks 18:11 and 18:26 PT (2-3s, no-work ticks — normal window has nothing new; the poison page only re-enters via resweep or a big live page).
- Child: hung job j-AbtfX3nz still pending; ~3 evening commit calls queued behind it. Expect it to die ~18:59 PT with the iteration-limit error, then the queued retries will flush and — if H1/H2 is right — re-spin on the same poison page. **Next resweep tick is 06:00 UTC = 23:11 PT tonight: high probability of another failure burst without intervention.** This is an active, recurring condition, currently latent.

## What test/fixture would catch it

1. **Owner-recipe test case (the direct guard):** call 82936791 (via the existing acceptance harness pattern in test 82939872) with a synthetic `facts_json` page of **>100 events (e.g. 250)** under one (capture_job, cycle, page_ordinal), forcing the POST readback of 158100 to paginate. Assert: job completes green and the progress row reaches rev+1 COMPLETE. Today every test and force-run used <=15-event pages — the boundary was never exercised. This fixture fails red on the current code in ~the 50k-limit or any watchdog cap, and goes green on the fix.
2. **Loop-invariant assertion (cheap, catches the spin early):** a page-count/iteration bound inside the loop (or on the test) — readback of a committed page must terminate within ceil(rows/100)+1 iterations; anything past that is a spin by definition. A runtime cap of, say, 50 iterations turns a 1h42m silent blockage into a 3-second loud failure with a distinct error.
3. **Parent-side regression fixture:** a collector test whose commit-lane stub returns `timed_out=1` (the existing fail-closed path) — already effectively covered by the natural j-AbtKGxrm evidence from the build; keep as a canon fixture so the parent's behavior (raise + watermark hold) stays pinned while the child is fixed.

## Proposed fix direction (NOT applied — read-only autopsy; dev-gate belongs to Josh)

1. In 82936791, re-home the readback loop's carried state (lookup_cursor, lookup_pages, matched_rows, seen_cursor_hashes_json, sql_bytes) from `update_variables` to the declare_list/list-slot idiom the collector already proves in production (spec §1.3), OR drive the loop from the get_records continuation token directly with the seen-hash guard evaluated on values actually carried across iterations. Same diff region either way: steps 61-67 (trace numbering).
2. Add the hard iteration bound with a distinct raise (e.g. `PAGE_COMMIT_READBACK_NOT_CONVERGING`) so a recurrence fails in seconds with its own signature instead of spinning 50k times.
3. Re-run fixture (1) above, then a live force-run of the collector at a resweep-wide window to watch the poison conversation's commit go green; confirm 158155 progress row advances and the queued evening calls drain green.
4. Canonize this class (`page-commit-owner-readback-spin` / parent signature `PAGE_COMMIT_ASYNC_JOB_FAILED timed_out=1`) via canonize-failure.py — deliberately not run here (read-only dispatch).
5. Operational note for whoever takes the fix: when the hung owner job dies (~18:59 PT) the queued evening retries flush automatically; if they re-spin, the child is effectively down again until ~20:40 PT, and the 23:11 PT resweep tick will burst-fail the parent again. Mitigation options (Josh's call): stop 82936791 before the resweep tick (parent then fails fast/queues), or ship the fix before 23:11 PT.

## Not verified (explicit)

- The exact value semantics of `wait_for_async_jobs timeout` (minutes assumed per this morning's empirical note; irrelevant to the root cause).
- Whether the poison page's fact rows are fully durable in 158099/158100 (insert step ran green; no readback ACK exists by definition of the hang). Data-table query tool returned 404 from this environment, so table-level confirmation is outstanding.
- The while_condition's exact configured expression (the DSL export renders the block as `while True:`; the trace shows the condition output True 50,000 times — the config itself was not independently re-read from the raw recipe JSON).
- H1 vs H2 discrimination (needs the >100-event fixture run).
- Whether the 18:11/18:26 green ticks imply the watermark advanced despite the failed commits (expected behavior is hold; not independently confirmed because the failed-job inputs are masked).

## Pointers

- Design spec + build record: `~/.claude/knowledge/projects/hr-genie/page-commit-cutover-spec-20261011.md` (§1.3 the list-slot law, §8.6 timeout note, §10 build record)
- Project state: `~/.claude/knowledge/projects/hr-genie.md` (BSYS-29498 section)
- Tickets: BSYS-29477 (comment 1135099, this failure report), BSYS-29498 (cutover), BSYS-29488 (closed phantom class)
- Case base: no prior case for this signature (checked `kb.cases similar` — no match; this autopsy is the candidate entry)
