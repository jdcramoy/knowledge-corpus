# Investigation: 82862205 — 10-10 "RESOLVED" claim vs 10-12 new-failures sweeps

**Investigator:** collector (cortex-dispatched, read-only)
**Date:** 2026-10-12
**Question:** Is the failure flagged by workato-health (10-12 12:27Z / 13:28Z) the SAME class the 2026-10-10 fix-82862205-family post closed (a regression), or a different defect?

## Verdict

**DIFFERENT DEFECT — not a regression.** The 10-12 failures are the BSYS-29477 async-commit class
(`PAGE_COMMIT_ASYNC_JOB_FAILED`), which did not exist when the 10-10 post was written. Nothing the
10-10 fix closed has returned.

## The two claims, side by side

**The 10-10 RESOLVED post** (bus/fix-82862205-family.jsonl, 2026-10-10T04:43Z) closed exactly two
things, neither of which is what is failing now:

1. **82863111 Ledger Correlator** capped-watermark livelock (`CORRELATOR_SOURCE_TRUNCATED`,
   wm frozen at 2026-09-01T12:20:19Z) — fixed in v6, drain-phase TRUNCATED failures explicitly
   flagged "expected, not a regression." Different recipe; those failures carry an ADVANCING
   watermark by design.
2. **82862205's 'Extra keys: log' burst** (10-09 06:51-06:55) — declared a test-case CHECK
   artifact, no code defect. Distinct from the orphaned guard-test class, which was separately
   re-recorded and closed 10-11 (cirr-AbtKg9Ma / j-AbtKg9MQ GREEN on v40).

**The 10-12 sweeps** flag 82862205 — and the failure underneath is the async-commit class first
seen 10-11 (one day AFTER the 10-10 post): the page-commit lane was built 10-11 under BSYS-29498,
so the 10-10 claim chronologically could not have covered it. Autopsied 10-11
(investigations/82862205-async-commit-timeout.md): origin is the commit-owner function 82936791,
whose POST-readback repeat loop never exits on multi-page reads (H1: update_variables loop state
does not persist across iterations), spins to the 50k-iteration platform kill ~1h42m later; the
parent's fail-closed verifier then raises `PAGE_COMMIT_ASYNC_JOB_FAILED` by design.

## Live job evidence (pulled read-only, 2026-10-12)

- Parent 82862205 failure burst 10-12: 4 scheduler jobs 05:11 / 05:26 / 05:41 / 05:56 PT
  (12:11-12:56 UTC), right after the 12:00 UTC resweep tick — the class's exact trigger signature.
- **j-AbtxeGNW-8LkBaR-CD** (05:56 PT) verified at trace level: failed line 43,
  `PAGE_COMMIT_ASYNC_JOB_FAILED: async commit job did not succeed (succeeded=0 failed=0
  timed_out=1)`; line 37 `call_recipe_async` (82936791) → line 38 `wait_for_async_jobs` → catch
  42 → raise 43. Byte-identical signature to the 10-11 evening burst jobs.
- Child 82936791: **j-Abtx646P** started 05:17:30 PT, ran 1h56m, failed 07:13:43 PT — the owner
  hang; two backlog-flush failures 07:13:47/48 follow it, matching the autopsy's queue-drain
  pattern.
- Parent green 06:11-07:26 PT (~2-3s no-work ticks); totals at pull: 506 ok / 62 failed (the
  "fails=62" the sweep counted).
- The 12:27Z / 13:28Z sweep flags were LIVE and accurate (fired during/immediately after the
  burst) — unlike the test-run noise class closed 10-11 22:14Z, these were real runtime failures.

## Current live state (flag for follow-up)

Recipe 82862205 is **Running: False** right now (read from the live recipe). bsys-29519-builder
stopped it 14:39Z and pushed the fix 14:57-14:58Z (prediction pred-20261012-105756-29 matched:
timeout=60 at both await sites, page_budget list, patched classifier/snapshot/residual/checkpoint
codes). No scheduler jobs since 07:26 PT — **the recipe has not been restarted / fix not yet
live-verified post-push.** Per the blanket-delegation rule this is possible unfinished state:
someone (bsys-29519-builder or Josh's go) needs to restart 82862205 and prove the next resweep
tick green, including the >100-event fixture from the autopsy before calling the class closed.

## Failure-class ledger for the 82862205 family (for the sweep's dedup)

| Class | First seen | Status |
|---|---|---|
| store_file dir-not-found | ~10-08 | gone (superseded) |
| empty-batch crash (BSYS-29488 precursor) | 10-08 | fixed+verified 10-09 |
| 'Extra keys: log' check artifact | 10-09 | closed 10-10 (test artifact) |
| orphaned guard-test mocks | 10-10 | closed 10-11 (re-recorded) |
| EVENT_PAGE_OVERFLOW_UNHANDLED | 10-10 | closed by BSYS-29488 repair 10-10 22:32Z |
| **PAGE_COMMIT_ASYNC_JOB_FAILED (BSYS-29477)** | **10-11** | **open — fix pushed 10-12 14:58Z, restart + live verify outstanding** |
| trace-less test-harness aborts | 10-10 | harness class, recipe exonerated |

## Bottom line

The 10-10 post was truthful and narrow: it closed the correlator livelock and the log-key
artifact. The 10-12 sweep is also truthful: a different, newer defect (BSYS-29477 async-commit)
was failing. No contradiction in substance — only in labeling: the sweep flags per-recipe, while
the fix claims are per-failure-class, so one recipe accumulating a fourth distinct class reads as
"the fix didn't hold." It didn't; a new class was born after the fix.

**Nothing unverified beyond:** the child hang's exact death error (j-Abtx646P trace not opened —
duration + timing signature only), and the durability of the poison page's fact rows (carried
unverified from the 10-11 autopsy).
