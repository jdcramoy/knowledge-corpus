# Guard-built contradiction — investigated 2026-10-17 (read-only)

## VERDICT: fixes ARE live in the tested recipes. The regression runner is NOT testing stale recipe versions. The STALE thing is the test cases — their mocks are bound to older recipe versions and were orphaned by later recipe edits (82272892 on 10-12, 82862205 on 10-16). The registry-cache-bug suspect does NOT match these failures.

## Evidence

1. Build ledger (~/.claude/knowledge/build-ledger.jsonl L4406-4407, 2026-10-09T09:49Z):
   - 82862205: empty-batch guard pushed (step 9 if batch_size>0 wraps loop+watermark), BSYS-29455, verified j-AbsJwzXC-W6X8sD-CD.
   - 82272892: records_json pill remap + step-21 empty-input guard pushed, BSYS-29456, verified j-AbsJxNLD-rzEErH-CD.

2. Live recipes (wt recipes get, 2026-10-17):
   - 82272892 "Sync Google Workspace Discovery Catalog": running=true, updated 2026-10-12T21:40 — AFTER the 10-09 fix. Guard code present verbatim: "# Empty-input guard: a blank or null records_json payload..." with `records_raw = input['records_json'].to_s.strip; records = (records_raw.empty? || records_raw == 'null') ? [] : flexible_parse(...)`. Two guard copies exist (second annotated BSYS-29456 / "the 2026-10-11").
   - 82862205 "REC | HR Genie | Conversation Event Collector": running=true, updated 2026-10-16T00:08 — AFTER the 10-09 fix. Guard present verbatim: if-condition on `invoke_custom_ruby_code_c524 output.batch_size` rhs "0" with comment "Empty-batch guard: when no non-test conversations exist since...".

3. The 10-17 failing jobs never executed recipe logic (executed lines: [] in all three traces). They died in test-case validation, pre-execution:
   - 82272892 j-AbzNLERd-LeKFdo-CD and j-AbzNLERd-RWzEwW-CD: "Test case contains an error: Some steps with mocks or checks were deleted from the recipe. Please update the test case or revert the recipe to the version that the test case was built for."
   - 82862205 j-AbzNLbQE-enhPec-CD: "Test case contains an error: Step can't be executed, it requires sample data. Please fix it in the test case editor."

4. Test case bindings (wt testcases cases):
   - 82272892 cases mock "step 19 compiler output" / check "step 20" (citc-AbsPWNeA-QCTfNn-CD, citc-AbtJF6NX-cpwCJC-CD; last updated 10-09/10-10). The 10-12 recipe edit shifted/deleted mocked steps → orphaned mocks.
   - 82862205 case (citc-AbsPGsnb-MALQch-CD) was already re-recorded 2026-10-11 for the EXACT same drift class ("event-drain v4 rebuild orphaned the original mocks"). The 10-16 recipe rebuild orphaned it AGAIN, this time as missing-sample-data.

5. Registry-cache-bug ruled out for THESE failures: that bug's signature is "could not start run" errors on case-less recipes kept in the run set (see investigations/regression-start-failures-2026-10-09.md) — tonight that signature appears on 82239660 / 82727069 / 82959480, which are separate error-class rows in the same report, NOT the guard FAILs.

## Root cause (the real defect)
Guard test cases bind mocks/checks to recipe step identity. Every recipe rebuild or edit re-orphans them → the guard tests go red even though the fix is intact. This is a RECURRING class: the 82862205 guard has been broken by drift twice in eight days (10-10/11 rebuild, 10-16 rebuild). "Built" triage rows are accurate; nightly red is a false alarm on fix integrity.

## Recommended (not applied — read-only)
1. Re-record/re-bind the three test cases against current recipe versions (same fixture shapes; the 82862205 case's own description documents the re-record procedure).
2. Structural fix worth a triage card: after ANY recipe push to a guard-tested recipe, auto-re-record mocks or surface "drift vs fix" distinctly in the regression report so a drift failure is never read as "fix missing/regressed".
3. Optionally have the regression report classify pre-execution validation errors ("steps with mocks deleted", "requires sample data") as DRIFT, not FAIL, to stop the built-vs-failing contradiction from re-firing nightly.

## Not verified
- Whether the 10-12 edit to 82272892 or the 10-16 edit to 82862205 actually preserved guard BEHAVIOR (code text present ≠ re-run proof); the guards' own verifying jobs are from 10-09. A live Test run would close that — not fired, read-only mandate.
- Exact step-number mapping between the test cases' mocked steps and the current recipes (drift confirmed by error message; per-step mapping not reconstructed).
