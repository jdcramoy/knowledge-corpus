# BSYS-29462 — Inventory [DRIFT FIX] project 10593549 into external-work ledger coverage

Epic: BSYS-29454 (Agent Harness Operations). Status: Backlog. Points: 2 (set).
Prior artifacts: `drift-fix/BSYS-29462-plan.md`, `drift-fix/BSYS-29462-ledger-coverage-plan.md`, `agent-harness-operations/BSYS-29462-drift-fix-ledger-coverage.md`.

## Background

Workato-watchdog finding `drift-fix-project-unledgered` (2026-10-09): project 10593549 / folder 35202337 (the [DRIFT FIX] recipe family) had zero build-ledger entries, so its mutations were invisible to the ledger, promotion-readiness scoring, and ticket reconciliation. The 2026-10-09 pass inventoried the project and seeded 7 externally-managed ledger rows; the build completed same day.

## 2026-10-11 evening re-verification (this pass)

Verdict: both acceptance criteria hold, nothing left to build. Live evidence:

- AC 1, inventoried: `knowledge/build-ledger.jsonl` carries all 7 `managed=external` / `tool=external_backfill` rows, parsed from the live file this pass: 82928217 retrieve_proposal, 82926620 Copy of get_drift_report, 82897971 validate_proposal, 82896390 log_proposal, 82893519 propose_fixes, 81852212 list_drift_reports, 74717532 get_drift_report (stopped).
- AC 2, scan coverage: `workato-health/owned-registry.json` (97 recipes, last rebuilt 2026-10-09) contains all 7 recipe IDs (grep, 1 hit each). Self-discovery chain closed: ledger rows feed `asset-fingerprint.py`; the health sweep, promotion-readiness scoring, and estate-architect read the registry.

Cosmetic noise: an 8th ledger row dated `2026-10-11T03:02:26Z` (kind `workato-cli`) carries `recipe_id: 10593549`, grabbed from an INDEX.md patch heredoc in the logged command string. Not a DRIFT FIX mutation; no action needed.

## Business Requirements

- Every Workato project with active mutations is visible to the build ledger and promotion-readiness scan.

## Technical Requirements (as built)

- One backfill row per recipe in `build-ledger.jsonl`, mirroring the ledgerAppend hook's airo-mutation schema plus `managed=external`, `project_id=10593549`, `folder_id=35202337`, `tool=external_backfill`.
- No new scan config surface: coverage rides the existing self-discovery chain.
- Non-goals honored: no rows claim harness ownership; stopped 74717532 holds only its inventory row.

## Acceptance Criteria

- [x] Project 10593549 inventoried with current asset states
- [x] Promotion-readiness scan includes the project going forward

## UAT Evidence

Inventory output (7-row table, ledger-verified) and the registry read-back; both re-verified 2026-10-11 from the live files.

## Risks

- No record exists of who or what mutated the DRIFT FIX recipes on 2026-10-08; uncheckable by design.
- Open disposition call: stopped get_drift_report (74717532) treated as deprecated unless someone objects (flagged 2026-10-10).

## Story points

2 (already set; verification-only close recommended, no build).
