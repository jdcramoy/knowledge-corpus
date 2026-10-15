# BSYS-29456 plan — GW discovery sync 82272892 crashes on empty records_json

Ticket: https://workato.atlassian.net/browse/BSYS-29456 (UAT, 2 pts, epic BSYS-29262).
Status: plan posted on the ticket 2026-10-11 (comment 1134987). FIX ALREADY SHIPPED,
so the plan documents verification evidence, not a diff.

## Problem statement

Dev recipe [82272892](https://app.workato.com/recipes/82272892) (GW discovery sync)
crashed with `JSON::ParserError "783: unexpected token at ''"` when the records_json
payload was empty. Canonical regression-canon entry `ruby-eval-empty-records-json`
(21 occurrences before canonization, watchdog 2026-10-07).

## Root cause (evidence-cited)

Two stacked defects:

1. Step 21's `records_json` input pill pointed at
   `invoke_custom_ruby_code_20['output']['records']`, a key the compiler never
   emits (`records_json` is the real key). The step always got an empty string:
   Oct 3 runs died on parse, and after the `flexible_parse` hardening it silently
   yielded `filtered_count=0` every run, keeping the step-27 upsert-if false and
   the step-28 registry upsert permanently skipped.
2. No empty-input guard before the parse evals: blank/nil records_json raised
   instead of meaning "nothing compiled this tick". The second unguarded
   `JSON.parse` (Normalize-pagination step, invoke_custom_ruby_code_a9a3) hid
   behind the first because the original failure died at line 20 before reaching
   it; the empty test case exposed it on 2026-10-11 06:29.

## Fix (shipped, evidence-cited)

- Pill remapped to `invoke_custom_ruby_code_20['output']['records_json']` (2026-10-09).
- Blank/null guard (`records_raw.empty? || records_raw == 'null' ? [] :
  flexible_parse(...)`) on the Preserve-reviewed eval (2026-10-09) and the
  Normalize-pagination eval (2026-10-11, v110, hot-swapped).
- Covering test cases: guard-empty (`citc-AbsPWNeA-QCTfNn-CD`, run
  cirr-AbtJdHxo-4nDd8Q-CD) and upsert-populated (`citc-AbtJF6NX-cpwCJC-CD`,
  run cirr-AbtJdfet-f6ChdF-CD), both green. Canon entry closed as tested;
  pre-fix snapshot at regression-canon/snapshots/recipe-82272892-pre-line21-guard-20261011T064016Z.json.

## Verification evidence (2026-10-11, this pass)

- Fresh recipe pull of dev 82272892: both guards present in code; the step 21
  pill reads `invoke_custom_ruby_code_20['output']['records_json']`.
- Job totals 963 succeeded / 30 failed of 993; the failed count has not moved
  since the fix (all 30 predate it).
- Five most recent scheduler runs (08:39 through 09:40 today) all succeeded,
  including [j-AbtXDPo8-YCENWg-CD](https://app.workato.com/recipes/82272892/job/j-AbtXDPo8-YCENWg-CD).

## Test that catches it

The two covering test cases on the recipe are the guard: empty-records_json
asserts a clean `[]` through both guards with no error; populated asserts
`filtered_count=1` and the upsert path unchanged.

## Risks

Low. Note: real scheduler runs cannot hit the empty case today (step 19 always
emits at least `[]`), so the guard covers the same class, not a live-fire path.
Remaining risk is the generic one: any new Ruby step reading the same pill must
carry the same blank-to-empty guard (canon entry tracks the class).

## Remaining

None to build. Josh's close is the only step.
