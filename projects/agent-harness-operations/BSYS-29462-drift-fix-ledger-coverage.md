# BSYS-29462 — Inventory [DRIFT FIX] project 10593549 into external-work ledger coverage

Ticket: https://workato.atlassian.net/browse/BSYS-29462 (epic BSYS-29454, Backlog, points 1).
Plan + build + close evidence posted 2026-10-09/10. This file holds the 2026-10-11 re-verification pass.

## Verdict

Both acceptance criteria are met on live evidence; nothing left to build. Recommendation stands: close on the evidence, and treat the stopped get_drift_report (74717532) as deprecated.

## Live evidence (2026-10-11)

- build-ledger.jsonl carries the 7 externally-managed backfill rows for project 10593549 / folder 35202337: recipes 82928217, 82926620, 82897971, 82896390, 82893519, 81852212, 74717532, all tagged managed=external, tool=external_backfill, plus one additional row referencing the project id (8 ledger matches total on grep).
- knowledge/workato-health/owned-registry.json (updated 2026-10-09T19:29Z) contains all 7 backfill rows in its recipes list with tools=[external_backfill]; coverage chain stays closed (ledger feeds asset-fingerprint.py feeds sweep/promotion-readiness/estate-architect).

## Not verified

- Who or what mutated the DRIFT FIX recipes on 2026-10-08 (no record exists to check).
- Watchdog non-reproduction of the blind-spot finding this pass (rests on the 2026-10-10 close note).
- Disposition of stopped recipe 74717532 is an open call recorded 2026-10-10, still unanswered.
