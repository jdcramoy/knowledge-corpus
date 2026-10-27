# Investigation: nightly regression runner 'Untitled test case 1' auto-seed question

Date: 2026-10-17 (read-only session; nothing changed anywhere but this file)

## Evidence base
- canon.jsonl rows: signature `regression-fail-untitled-test-case-1` on 82059061,
  82202341 (found 2026-10-16), 82133030 (found 2026-10-17), plus earlier
  82248514 / 82256903 / 82272814 (10-10) and 82273581 (10-08, closed 10-09).
- Runner: `~/.claude/knowledge/scripts/regression-nightly.py` (launchd
  `com.josh.fleet.regression.plist`).
- CLI: `wt testcases` in `~/.local/bin/wt` (`cmd_testcases`, line 581).

## Q1 — Does the runner auto-seed/create a failing test case named 'Untitled test case 1'?
**NO.** The runner never creates test cases. Its only write surfaces are
(a) the registry JSON, (b) the garden report, (c) canon ROWS.
- `scan_for_test_cases()` (regression-nightly.py:76) only **GETs**
  `/api/recipes/{id}/test_cases` — lists existing cases.
- `run_recipe_cases()` → `wt testcases run` → `POST /api/test_cases/run_requests`
  (wt:628) — executes existing cases; `cases` and `status` subcommands are pure GET.
- The "auto-seeded" wording in the canon `line` field refers to the **canon
  auto-seed block** (regression-nightly.py:280-308): a failed case with no canon
  entry gets a canon row whose signature is `regression-fail-` + slugified
  case name (line 294). A case literally named "Untitled test case 1" →
  `regression-fail-untitled-test-case-1`. The name is read from the test case
  object returned in the run results — it originated in the case itself.

Where the case DID come from: live API shows a real test case named
"Untitled test case 1" on each flagged recipe, **created 2026-09-02 /
09-06 / 09-09** — weeks before any canon row, with empty descriptions and
Workato's default UI name. These are leftover scaffolding cases (created in the
test-case editor / API and never named or configured), not runner artifacts.

## Q2 — Self-generated noise vs real drift?
**Neither recipe drift nor runner-created — a third thing: unconfigured
scaffolding cases failing pre-execution, which the runner converts into canon
FAIL rows.** Two failure classes observed:
- **82059061 / 82202341** — job j-AbxrPAtf-oQAxfJ-CD: `error_type: "Test
  Automation error"`, message: *"Test case contains an error: Step can't be
  executed, it requires sample data. Please fix it in the test case editor."*
  The case never executed — a pre-execution validation error against an empty
  scaffold case. Zero information about recipe health.
- **82133030** — job j-AbzNJesP-gRtKDs-CD: the case DID run, and failed on
  `workday` adapter `get_wql_report` → **"Service unavailable"** — a
  dependency/environment failure on a `TEST |` probe recipe, not logic drift.
Verdict: the canon rows are **noise in kind** (not regression failures of the
recipes) but **runner-amplified in volume** — the auto-seed block files
pre-execution validation and dependency blips under a regression-failure
signature, and the default name collapses all of them into one colliding
signature across unrelated recipes.

## Q3 — Minimal fix
**Recommended: classify pre-execution validation errors as a non-FAIL class
(plus a one-time scaffold cleanup). Not skip-auto-seed, not renaming alone.**
1. **Classify (the real fix, ~5 lines in regression-nightly.py:286-308):** when
   the run result's `error_parts.error_type == 'Test Automation error'`
   (message matches "requires sample data"), seed the canon row with
   `kind: 'testcase-unconfigured'` (status open but NOT counted in report FAIL
   totals) instead of `kind: 'regression-failure'`. The case never ran, so
   there is no regression to record — same logic as the existing skip-headless
   MASKED envelope (regression-nightly.py:51-55), which already treats
   dependency-unavailable as "not a green, not a FAIL".
2. **One-time cleanup (needs a write session; not done here):** the five
   existing "Untitled test case 1" scaffold cases (82059061, 82202341,
   82133030, 82248514, 82256903/82272814 per 10-10 rows) should be filled or
   deleted — they are empty September scaffolding that will re-fail nightly
   forever. Deleting them drops the recipes from the registry automatically
   (the re-verify walk handles deleted-case recipes — canon row 2 documents
   exactly this path for 82273581).
3. **Rejected — skip auto-seed:** loses genuine failure capture (the intake-lag
   closer was deliberate); the noise is a classification problem, not a capture
   problem.
4. **Rejected — renaming alone:** treats the symptom; the next default-named
   case re-collides into the same signature. Fine as hygiene, insufficient as
   the fix.
5. Optional hardening: name the signature from recipe id + case name
   (`regression-fail-82059061-untitled-test-case-1`) so unrelated recipes stop
   sharing one signature even before case names are fixed.

## Bottom line
The runner is innocent of creating cases; it faithfully runs old empty scaffold
cases, and its canon auto-seed mislabels unconfigured-case and dependency
failures as regression failures under one colliding signature. Fix the
classification (step 1), clean the five scaffold cases (step 2), keep auto-seed.
