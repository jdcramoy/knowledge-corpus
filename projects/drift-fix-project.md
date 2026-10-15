---
name: drift-fix-project
description: Inventory + ledger coverage for the [DRIFT FIX] Workato project 10593549 (folder 35202337) — externally-maintained, zero build-ledger history
metadata:
  type: project
---

# [DRIFT FIX] project 10593549 — inventory (2026-10-09, /triage)

Watchdog finding `drift-fix-project-unledgered`: all 7 recipes updated 2026-10-08
with ZERO build-ledger entries — external work (Josh UI / Codex / Orca), invisible
to the multi-agent ledger. Inventory (dev workspace):

| ID | Name | Running | Last updated |
|---|---|---|---|
| [82928217](https://app.workato.com/recipes/82928217) | [DRIFT FIX] retrieve_proposal | yes | 2026-10-08T23:53-04 |
| [82926620](https://app.workato.com/recipes/82926620) | Copy of [DRIFT FIX] get_drift_report | yes | 2026-10-08T21:34-04 |
| [82897971](https://app.workato.com/recipes/82897971) | [DRIFT FIX] validate_proposal | yes | 2026-10-08T05:55-04 |
| [82896390](https://app.workato.com/recipes/82896390) | [DRIFT FIX] log_proposal | yes | 2026-10-08T22:58-04 |
| [82893519](https://app.workato.com/recipes/82893519) | [DRIFT FIX] propose_fixes | yes | 2026-10-08T22:59-04 |
| [81852212](https://app.workato.com/recipes/81852212) | [DRIFT FIX] list_drift_reports | yes | 2026-10-08T21:38-04 |
| [74717532](https://app.workato.com/recipes/74717532) | [DRIFT FIX] get_drift_report | NO | 2026-10-08T03:04-04 |

Note the fresh unparented `Copy of get_drift_report` (82926620) — likely a
scratch copy; ask Josh whether it should be deleted or promoted over 74717532.
Ledger coverage: Job 4 of [[workato-watchdog]] now names this project in scope
explicitly (agent def amended 2026-10-09), BSYS-29462 tracks it.
