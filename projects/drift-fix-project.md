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


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Drift-fix project](projects/drift-fix-project.md) — [DRIFT FIX] Workato project 10593549 inventory (7 recipes, externally maintained, zero ledger history); Job 4 scope amended (BSYS-29462); **+ 2026-10-21 overnight incident verified live: table 157379 deleted ~01:18, [LOG] DriftFix_Apply_Log recreated as 163016 (folder 35701677), 3/4 consumers re-pointed + 2 new recipes + Drift Fix Genie restarted 23:49 — all zero-ledger; get_fix_proposals 83074639 still fails (dead 157379 + query_id→snowflake_query_id rename = plain re-point insufficient); attribution UNPROVEN; findings projects/drift-fix/bsys-29828-overnight-incident-findings-2026-10-21.md**