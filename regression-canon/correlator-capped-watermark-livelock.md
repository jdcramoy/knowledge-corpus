# Failure canon: correlator-capped-watermark-livelock

- **recipe:** [82863111](https://app.workato.com/recipes/82863111)
- **job:** j-AbsnnXWa-ckoYrK-CD (dev)
- **canonized:** 2026-10-10T08:24:34Z
- **failure class (final):** code-bug
- **error signature:** `fail-correlator-source-truncated-correlator-handled-hit`
- **status:** closed (fix landed v6, live-verified 2026-10-10, session fix-82862205-family)

## Error signature

`fail-correlator-source-truncated-correlator-handled-hit` — CORRELATOR_SOURCE_TRUNCATED: correlator_handled hit the 500-row read cap; watermark held back, work stays replayable. Backfill or widen the window.
(error_type: Eval custom ruby code error)

## Autopsy (final — supersedes the trace-heuristic map below)

- **ORIGIN step:** step 6, Ruby snippet "Correlate sources to emit payloads" — the three watermark assignments `wms["correlator_*"] = (capped || max_t.nil?) ? old_wm : max_t` hold the watermark back whenever the source read hits the 500-row cap. Because the emit path already consumed the window (emitter dedupes on source_event_id), holding the wm back is a pure livelock: the next cycle re-reads the SAME 500 rows, re-emits (ALREADY_PERSISTED), and the truncation raise re-fires — forever. Evidence: wm `correlator_handled` frozen at 2026-09-01T12:20:19Z across 11 consecutive failures (j-AbshDxcW..j-AbsnnXWa, Oct 9 21:15 → Oct 10 01:06) while usage/outcomes wms stayed current.
- **victim step:** step 13, Ruby snippet "Surface source truncation" — where the livelock surfaces (job dies AFTER emits and AFTER the wm update, so the design was one edit away from correct).
- **classification:** code-bug (watermark hold-back on capped reads contradicts the dedup-safe replay design).
- **diff (v5→v6, minimal):** drop `capped || ` from the three wms assignments; truncation raise message updated to state the advancing-watermark semantics. Rollback snapshot: /tmp/fix-82862205-family/snapshot-82863111.json.

## Live verification

- Force-run j-Abso6DPK-K4nE84-CD: wm advanced 2026-09-01T12:20:19Z → 2026-09-02T02:19:38Z (~14h of backlog per cycle), truncation raise still fires (fail-visible preserved).
- Scheduled j-AbsoHdxQ-m8GJAs-CD: wm now 2026-09-02T16:05:29Z. Backlog (Sep 1 → Oct 10) drains at ~500 rows/cycle, ~66 cycles ≈ 33h at the 30-min cadence. Drain-phase cycles keep failing CORRELATOR_SOURCE_TRUNCATED **with advancing wm** — expected until ~Oct 11 21:00 PT, not a regression.

## Trace map (original trace heuristic, kept for the record)

- **origin candidate (superseded):** line 1 (workato_db_table/get_records)
- **victim step:** line 12/13 (workato_custom_code/invoke_custom_ruby_code)
- **top-level error:** Scheduler by Workato: new recurring event

## Fixture status

scaffolded ~/.claude/knowledge/fixtures/82863111.json (empty) — NEEDS INPUT+EXPECTS before it enters the nightly fixture phase (wt fixture run --recipe 82863111)

The scaffold is intentionally EMPTY — do not guess input. Fill `input` and
`expect` from the autopsy's "test case that would have caught it", then
`wt fixture run --recipe 82863111`. A non-empty expect list is what the
nightly regression fixture phase runs; filling it IS the nightly slot.

## Canon entry

appended to ~/.claude/knowledge/regression-canon/canon.jsonl (signature fail-correlator-source-truncated-correlator-handled-hit)

## Close-out

1. workato-autopsy on [j-AbsnnXWa-ckoYrK-CD](https://app.workato.com/recipes/82863111) — refine class + diff.
2. Fill the fixture input + expects (testcase-authoring skill).
3. Fix, prove with a live job trace, `wt fixture run` green.
4. Set the canon entry status to closed (class verified, fixture guarding).
