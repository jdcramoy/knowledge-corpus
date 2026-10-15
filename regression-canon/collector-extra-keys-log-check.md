# Failure canon: collector-extra-keys-log-check

- **recipe:** [82862205](https://app.workato.com/recipes/82862205)
- **job:** j-AbsPREAn-Cz3Mba-CD (dev)
- **canonized:** 2026-10-10T08:29:45Z
- **failure class (provisional):** regression-failure
- **error signature:** `regression-fail-output-check-failed-data-wasn-t-equal-to`
- **status:** open

## Error signature

`regression-fail-output-check-failed-data-wasn-t-equal-to` — Output check failed: data wasn't equal to expected value at 'output'. Extra keys: log
(error_type: Test Automation error)

## Trace map (trace-derived; autopsy names the true origin)

- **origin candidate:** line 0 (clock/scheduled_event) — first step with an error record
- **victim step:** line 5 (workato_custom_code/invoke_custom_ruby_code) — last step with an error record (where the job died)
- **top-level error:** Processed event

## Classification

Provisional: **regression-failure** (trace heuristic). Refine with the workato-autopsy
skill on this job — it maps trace to recipe code, correlates the green→red
window, and produces the proposed diff. Update this file and the canon entry
class when it does.

## Fixture status

existing fixture ~/.claude/knowledge/fixtures/82862205.json but 0 expects — fill input + expects, then wt fixture run --recipe 82862205

The scaffold is intentionally EMPTY — do not guess input. Fill `input` and
`expect` from the autopsy's "test case that would have caught it", then
`wt fixture run --recipe 82862205`. A non-empty expect list is what the
nightly regression fixture phase runs; filling it IS the nightly slot.

## Canon entry

appended to ~/.claude/knowledge/regression-canon/canon.jsonl (signature regression-fail-output-check-failed-data-wasn-t-equal-to)

## Close-out

1. workato-autopsy on [j-AbsPREAn-Cz3Mba-CD](https://app.workato.com/recipes/82862205) — refine class + diff.
2. Fill the fixture input + expects (testcase-authoring skill).
3. Fix, prove with a live job trace, `wt fixture run` green.
4. Set the canon entry status to closed (class verified, fixture guarding).
