# Failure canon: phantom-conversation-row-empty-page

- **recipe:** [82862205](https://app.workato.com/recipes/82862205)
- **job:** j-AbskKeQa-ENdmaF-CD (dev)
- **canonized:** 2026-10-10T05:36:16Z
- **failure class (provisional):** code-bug
- **error signature:** `fail-collector-all-conversations-skipped-1-1-conversatio`
- **status:** open

## Error signature

`fail-collector-all-conversations-skipped-1-1-conversatio` — COLLECTOR_ALL_CONVERSATIONS_SKIPPED: 1/1 conversations failed their event read; coverage incomplete
(error_type: Eval custom ruby code error)

## Trace map (autopsy-refined 2026-10-10 — full report: projects/hr-genie/bsys-29477-collector-newfailure-autopsy-2026-10-10.md + BSYS-29488 comment 1134787)

- **origin step:** conversation-list drain loop's page-accumulate step (step 14, `insert_to_list` on `conv_pages`) — inserts `data[0]` fields unconditionally; a terminal empty page (`data: []`, blank cursor) materializes a phantom conversation with blank id/created_at
- **victim step:** Compute checkpoint (step 39) — all-skip guard raised `COLLECTOR_ALL_CONVERSATIONS_SKIPPED: 1/1 conversations failed their event read` (by design; the guard worked)
- **chain:** empty page → phantom row (batch_size=1, conv_id='', max_created_iso=1970-01-01T00:00:00Z) → defeats empty-batch guard (`batch_size > 0`) → blank-id event read 404s → revision-dependent outcome (raw 404 j-AbshpXfk / empty-data watermark-update crash j-Absk99aB / tolerated skip + guard raise j-AbskKeQa)
- **attribution:** introduced inside the BSYS-29488 repair session's push window (04:21-05:23 UTC 2026-10-10); last green scheduler run 04:02 UTC, first failure 04:24 UTC; cursor guard (step 13) only protects the empty-page-WITH-cursor case

## Classification

**code-bug (confirmed by autopsy).** Regression introduced by the drain-loop refactor in the BSYS-29488 repair churn. Not a recurrence of BSYS-29477 (watermark offset intact, not the failure surface) — but it re-exposed the BSYS-29455 empty-data crash class via the phantom batch.

## Proposed fix (NOT built — awaits BSYS-29488 repair session / Josh authorization)

1. Cursor guard (step 13): treat `page_rows == 0` as terminal regardless of next_cursor, or skip the step-14 insert when `data` empty / `data[0]['id']` blank.
2. Defense in depth in "Prepare conversation batch" (step 18): `convs = convs.reject { |c| c["id"].to_s.strip.empty? }`.
3. Keep the all-skip guard as is.

## Fixture status

SPEC-ONLY — the scaffold at ~/.claude/knowledge/fixtures/82862205.json was left EMPTY deliberately. The recipe is scheduler-triggered (no webhook, no test-case scaffolding — same finding as BSYS-29455's verification), so a webhook-kind fixture cannot invoke it; registering a non-empty expect list on an unrunnable fixture would break the nightly phase. The regression guard is this specification:

- **Fixture A (empty page):** List-conversations returns `data: []` with blank `next_cursor` → expect: no `conv_pages` insert, `batch_size = 0`, empty-batch guard condition False, job SUCCEEDED, watermark row untouched.
- **Fixture B (blank row):** List-conversations returns `data: [{}]` → expect: row rejected before batch prep, `batch_size = 0`, same clean idle.
- **Repeatable live procedure (no code change needed to run):** force-run the collector on an empty window (watermark past all conversations) → job must SUCCEED with the guard condition False. Under the bug it fails with COLLECTOR_ALL_CONVERSATIONS_SKIPPED.

## Canon entry

appended to ~/.claude/knowledge/regression-canon/canon.jsonl (signature fail-collector-all-conversations-skipped-1-1-conversatio — auto-generated from the error string, truncated; the failure-class fingerprint is the empty-page-phantom-row chain documented above)

## Close-out

1. Autopsy complete 2026-10-10 (this file + BSYS-29488 comment 1134787).
2. Fix belongs to the BSYS-29488 repair session's in-flight work — do not duplicate it.
3. Prove with the live empty-window force-run procedure above on the final revision; then the canon entry can move to fixed/tested.
4. Reset the checkpoint watermark to the canonical `%Y-%m-%dT%H:%M:%SZ` format during the proof pass (it was left in Ruby `Time#to_s` format).
