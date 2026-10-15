# BSYS-29456 — GW discovery sync 82272892 empty records_json guard

Status: fixed-awaiting-UAT (Josh's close pending). Fixed and verified 2026-10-11.

## Root cause

Recipe [82272892](https://app.workato.com/recipes/82272892) crashed on empty upstream
payloads: the `records_json` input pill read a nonexistent `['output']['records']`
key (step 20 always got an empty string, `filtered_count` permanently 0, registry
upsert never ran), and the "Preserve reviewed rows" eval had no empty-input guard.
A bounded burst 2026-10-10 23:17-23:27 PDT self-recovered; cortex filed the guard
finding, which turned out to duplicate this ticket.

## Fix

- Step 20 (Preserve reviewed rows): blank/null -> [] guard. Pushed 2026-10-09.
- Step 21 (Normalize pagination limit defaults): same unguarded `JSON.parse` found
  by the empty test case 2026-10-11 06:29, guard applied 06:44 (v110, hot-swapped).
- Covering test cases: guard-empty (cirr-AbtJdHxo-4nDd8Q-CD) and upsert-populated
  (cirr-AbtJdfet-f6ChdF-CD), both green.
- Canon entry `ruby-eval-empty-payload` stamped tested/CLOSED.

## Post-fix verification (2026-10-11)

6 most recent scheduler runs (13:09-14:24 UTC) all succeeded, zero errors.
Totals 954 succeeded / 30 failed (all pre-fix).

## Residual

Ticket sits in UAT awaiting Josh's close. Nothing else open.
