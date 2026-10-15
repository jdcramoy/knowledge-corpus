# Failure canon: resolver-v2-catalog-snapshot

- **recipe:** [82794233](https://app.workato.com/recipes/82794233)
- **job:** j-AbrfmCLn-cFCLFM-CD (dev)
- **canonized:** 2026-10-09T08:31:39Z
- **failure class (provisional):** regression-failure
- **error signature:** `regression-fail-output-check-failed-data-wasn-t-equal-to`
- **status:** open

## Error signature

`regression-fail-output-check-failed-data-wasn-t-equal-to` — Output check failed: data wasn't equal to expected value
(error_type: Test Automation error)

## Trace map (trace-derived; autopsy names the true origin)

- **origin candidate:** line 1 (workato_api_connector_748504_1684743862/__adhoc_http_action) — first step with an error record
- **victim step:** line 6 (workato_api_connector_748504_1684743862/__adhoc_http_action) — last step with an error record (where the job died)
- **top-level error:** Recipe function by Workato: new call for function: Calling job ID=TEST_JOB_NO_DELETE, Calling recipe ID=82210315, and Verified end user ID=TEST_MCP_OWNER

## Classification

Provisional: **regression-failure** (trace heuristic). Refine with the workato-autopsy
skill on this job — it maps trace to recipe code, correlates the green→red
window, and produces the proposed diff. Update this file and the canon entry
class when it does.

## Fixture status

existing fixture ~/.claude/knowledge/fixtures/82794233.json but 0 expects — fill input + expects, then wt fixture run --recipe 82794233

The scaffold is intentionally EMPTY — do not guess input. Fill `input` and
`expect` from the autopsy's "test case that would have caught it", then
`wt fixture run --recipe 82794233`. A non-empty expect list is what the
nightly regression fixture phase runs; filling it IS the nightly slot.

## Canon entry

entry already exists for this job (signature regression-fail-output-check-failed-data-wasn-t-equal-to) — not appended

## Close-out

1. workato-autopsy on [j-AbrfmCLn-cFCLFM-CD](https://app.workato.com/recipes/82794233) — refine class + diff.
2. Fill the fixture input + expects (testcase-authoring skill).
3. Fix, prove with a live job trace, `wt fixture run` green.
4. Set the canon entry status to closed (class verified, fixture guarding).
