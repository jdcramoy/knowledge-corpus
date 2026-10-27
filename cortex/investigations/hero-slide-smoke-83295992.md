# Investigation: hero slide smoke — recipe 83295992 (Measure Slide)

**Date:** 2026-10-23
**Canon entry:** `regression-canon/canon.jsonl` line 72 — `regression-fail-hero-slide-smoke`, status `open`, found 2026-10-23 by regression-nightly
**Recipe:** Measure Slide — https://app.workato.com/recipes/83295992 (running: true, folder 32269258)
**Test case:** `citc-Ac6XFTpc-9XYRAD-CD` "hero slide smoke" (created 2026-10-22T23:34:15-04:00)
**Failing run:** `cirr-Ac6XfhkN-Hb9B8e-CD` — job `j-Ac6XfhkH-hm9kYY-CD` — https://app.workato.com/recipes/83295992/job/j-Ac6XfhkH-hm9kYY-CD

## Verdict: test-artifact (NOT a real asset regression)

The recipe asset is healthy. The failure is a malformed test case: Workato Test Automation requires the trigger step to be mocked in the test case editor, and this test case has no trigger mock. Every test run dies at trigger dispatch before a single recipe step executes.

## Origin evidence

1. **Exact error (raw job API, `wt api GET /api/recipes/83295992/jobs/j-Ac6XfhkH-hm9kYY-CD`):**
   `error_parts.message = "Test case contains an error: Trigger should be mocked. Please fix it in the test case editor"` — error_type `Test Automation error`, adapter `Workato Automation`. `lines: []` (zero steps executed), job duration 64ms, `is_test_case_job: true`.

2. **All 5 test-case jobs fail identically.** Full job history for the recipe: 5 failed jobs (20:35:11, 20:35:49, 20:43:21, 20:53:16, 21:03:00 -07:00) — every one has the same `Trigger should be mocked` error and 0 lines. The nightly run is simply the latest instance, not a new regression.

3. **A direct skill invocation succeeds end-to-end.** Job `j-Ac6XaQhC-QKbDBt-CD` (2026-10-22T23:55:28-04:00, "Workato Skill: start workflow") ran the full happy path in 4.3s and succeeded: permit acquire (recipe function 74622357) → Google get_slide (875ms, upstream OK) → custom Ruby metrics → permit release (74622358) → guidance call (82864228) → `workflow_return_result` with the ok envelope. Recipe logic, connections, custom connector, and downstream recipe functions all work.

4. **Test-run coverage confirms dispatch-level failure:** run `cirr-Ac6XfhkN-Hb9B8e-CD` reports "Actions: None/None visited" and coverage error `tests_failed` — consistent with zero steps executing.

5. Timeline fits: the test case was created 2026-10-22T23:34:15-04:00 and has never passed; there is no earlier passing baseline that regressed.

## Minimal fix shape

- In the **test case editor** for `citc-Ac6XFTpc-9XYRAD-CD`, add a mock for the `workato_skill` trigger step supplying the input parameters (`presentation_id`, `slide_id`, `include_unfilled_placeholders`) matching the trigger's parameters schema. Do not edit the recipe itself.
- If the Test Automation framework cannot mock a `workato_skill` trigger (possible platform limitation — the successful run came from a real skill call, not the test harness), then either (a) wrap the logic in a recipe function and point the test case at that, or (b) delete/replace this test case, since in its current shape it can never pass.
- After fixing, close canon line 72 (`regression-fail-hero-slide-smoke`) per the failure-close-gate (update the durable record in the same run that marks it resolved).

## Scope note

Read-only investigation. Nothing was edited, stopped, started, or re-run.
