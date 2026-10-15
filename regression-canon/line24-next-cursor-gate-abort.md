# Failure canon: line24-next-cursor-gate-abort

- **recipe:** [82178793](https://app.workato.com/recipes/82178793) (events collector, dev)
- **jobs:** j-Abx4seMz-XoYM8t-CD (2026-10-14 07:06 PT, primary) and j-AbwMpA6r (2026-10-13 00:51 PT, first occurrence)
- **canonized:** 2026-10-14 (harness-fix triage batch)
- **failure class (provisional):** platform-side-abort (workload-independent; exception text AIRO-masked)
- **error signature:** `line24-next-cursor-gate-abort`
- **status:** open

## Failure class

The collector's tail region dies at the line-24/26 boundary — the `if next_cursor`
pagination gate evaluates and COMPLETES (`output: {'condition': False}`, no error
record, no runtime), then the trace stops. Lines 26-45 never run: no rounds budget,
no checkpoint write, no self-heartbeat to recipe function 82959725. The job-level
error carries only the trigger title (AIRO masking) — no exception text exists at
the API level either (verified via job_get 2026-10-14).

Workload-independence points away from time-based infra kills toward the
gate→rounds-budget transition: the 10-14 occurrence died in 9.2 s (heavy loop
1.6 s, events HTTP 1.3 s) while healthy ticks run 2-3.5 min (142 s loops, 131 s
HTTP). Both occurrences are on the CURRENT recipe shape (post-rebuild); the 10-09
`while_condition` line-36 burst is the old version's separate class.

## Evidence (live-verified 2026-10-14)

- job_get j-Abx4seMz-XoYM8t-CD: failed line 24 `misc/if`, output `{'condition': False}`,
  no error record on any line; finalize `insert_to_list` (line 23) succeeded 0.0041 s
- self-heals next tick: 07:21 PT ran 2m22s green; every tick since green (verified
  job_list 2026-10-14 12:37 PT — 8/8 green, 2.5 min each); watermark design
  (advance-only-after-upserts, 60 s overlap, 7-day re-drain) covers the aborted window
- tripwire: 2 occurrences in ~31 h tripped the 10-13 report's >1/week tripwire
- 0.7% lifetime failure rate (24/3,427)

## Fixture shape (SPEC-ONLY — deliberately no runnable fixture)

The recipe is scheduler-triggered; a webhook-kind fixture cannot invoke it (same
finding as the phantom-conversation canon), so the fixture scaffold is left empty
and the spec here is the guard. The abort cannot be reproduced from recipe INPUT —
it is input-independent (light workload, gate evaluated False and completed):

- **Fixture A (healthy tail):** next_cursor blank after a full drain → expect: line-24
  condition False, lines 26+ RUN (rounds budget, checkpoint, heartbeat), job SUCCEEDED.
  This is the exact path that aborts — a green trace through it is the regression proof.
- **Fixture B (recurrence detector):** watchdog greps canon for
  `line24-next-cursor-gate-abort`; a third occurrence = canon violation, P1.

## Covering test (the honest gap)

No Workato test case can express this class: the failure is a platform-side abort
AFTER a step completed, not a raise in recipe logic — nothing in the input schema
or step code can force it. The covering artifacts are (1) Fixture A's expectation,
runnable live at any time via `wt recipes force-run 82178793` + trace read (lines
26-45 present), and (2) this canon row, which turns the next occurrence into a
canon violation. Remaining refinement: Orca UI trace read of j-Abx4seMz to recover
the masked exception text; escalate to a formal platform-side pattern if the trace
is genuinely cut (recommendation from cortex/investigations/82178793-new-failures-1520z.md).

## Disposition

No hotfix — self-heals next tick, watermark covers the gap, fail rate 0.7%. Recipe
NOT edited (canonization is the deliverable, per the 2026-10-14 Josh-go'd batch).
