# BSYS-29462 plan: Inventory [DRIFT FIX] project 10593549 into external-work ledger coverage

Parent epic: BSYS-29454 (Agent Harness Operations — Watcher, Registry & Fleet Hygiene).
Status: DELIVERED — plan posted as ticket comment 1134567, build posted as comment 1134604
(2026-10-09, 1pt). This file is the finished technical plan with live-verified state as of
2026-10-09 (jira-autotriage planning pass). Remaining step: Josh's review / transition.

## Background

Workato-watchdog triage finding `drift-fix-project-unledgered` (2026-10-09, P2): the
[DRIFT FIX] Workato project 10593549 / folder 35202337 in the DEV workspace had ZERO
build-ledger entries, despite all 7 recipes being touched 2026-10-08 — including a fresh
unparented "Copy of get_drift_report". The guardrails ledgerAppend hook only records
AIRO-driven mutations; out-of-band edits (Josh UI, Codex, Orca) never produce ledger rows,
so /promotion-ready, the ops-visibility scan, and ticket reconciliation were blind to this
project. Same failure class as the BTSUP-72246 prod fleet cluster (watchdog P2#5).

## Business Requirements

- Every Workato project with active mutations is visible to the build ledger and the
  promotion-readiness scan.
- Externally-maintained work is inventoried honestly: flagged as externally managed,
  never claimed as harness-built.

## Technical Requirements

### AC 1 — Inventory (delivered)

Seven recipes in folder 35202337, dev workspace, all last updated 2026-10-08:

| Recipe | ID | Running | URL |
|---|---|---|---|
| [DRIFT FIX] retrieve_proposal | 82928217 | yes | https://app.workato.com/recipes/82928217 |
| Copy of [DRIFT FIX] get_drift_report | 82926620 | yes | https://app.workato.com/recipes/82926620 |
| [DRIFT FIX] validate_proposal | 82897971 | yes | https://app.workato.com/recipes/82897971 |
| [DRIFT FIX] log_proposal | 82896390 | yes | https://app.workato.com/recipes/82896390 |
| [DRIFT FIX] propose_fixes | 82893519 | yes | https://app.workato.com/recipes/82893519 |
| [DRIFT FIX] list_drift_reports | 81852212 | yes | https://app.workato.com/recipes/81852212 |
| [DRIFT FIX] get_drift_report | 74717532 | no (superseded by 82926620; deprecation candidate) | https://app.workato.com/recipes/74717532 |

Ownership finding: no knowledge-tree record ties this project to any harness build. The
Copy-of pattern plus zero ledger history points to manual/out-of-band mutation — the exact
blind spot this ticket closes.

### AC 2 — Close the scan blind spot by seeding the ledger, no new config surface (delivered)

Coverage chain (how enforcement actually works): guardrails `ledgerAppend` hook →
`~/.claude/knowledge/build-ledger.jsonl` → `asset-fingerprint.py` self-discovery →
`~/.claude/knowledge/workato-health/owned-registry.json` → health sweep /
promotion-readiness scoring / estate-architect, which all read that registry.

Fix: backfill one externally-managed inventory row per recipe (7 rows) into
build-ledger.jsonl, then rebuild the registry. Row schema mirrors the ledgerAppend hook's
airo-mutation shape (kind, tool, server, session, recipe_id, asset_name, folder_id, ticket)
plus the inventory tags: `managed=external`, `project_id=10593549`, `folder_id=35202337`,
`last_updated=2026-10-08`, `tool=external_backfill`, `session=bsys-29462-backfill`. Rows
were appended atomically via scripts/atomic_io.py (flock + temp + os.replace).

Deliberate non-goals (honored):
- No ledger row claims harness ownership — all 7 are `managed=external`.
- The stopped 74717532 gets only the inventory row; no active monitoring.
- No new scan config surface — self-discovery from ledger rows keeps the project
  visible to promotion-readiness and the sweep going forward.

## Acceptance Criteria

- [x] Project 10593549 inventoried with current asset states (7 recipes, live recipe_list,
      comment 1134567)
- [x] Promotion-readiness scan includes the project going forward (7 externally-managed
      ledger rows; owned-registry rebuilt to 97 recipes with all 7 present; sweep ran clean)

## Risks

- Attribution unknown: who/what mutated these recipes on 2026-10-08 has no record to check.
  The inventory records the fact, not the actor.
- Knowledge-tree drift (found this pass, not fixed — out of this file's scope): INDEX.md
  line 32 points at `projects/drift-fix-project.md`, which does not exist on disk; the
  inventory lives in `projects/drift-fix/` instead, and a heredoc transcript fragment of
  the would-be file sits inside `projects/google-slides-mcp.md` (~line 1090). Next
  gardener pass should repair the INDEX pointer and relocate the fragment.
- 74717532 deprecation is undecided — Josh to call delete vs keep as historical.
- Seed rows for any FUTURE external project must match register.js/hook writer schema
  before hand-insertion (was a build-phase check here; it passed).

## Points

1 (Fibonacci; mechanical backfill + one registry rebuild + read-back). Actuals matched.

## What was verified (live, this pass, 2026-10-09)

- Ticket read fully incl. both comments (1134567 plan, 1134604 build) and epic BSYS-29454
  description.
- `build-ledger.jsonl`: exactly 7 rows carrying project 10593549, all `managed=external`,
  `tool=external_backfill`, ticket BSYS-29462 (grep + sampled row shown above).
- `workato-health/owned-registry.json`: 7 matching recipe rows present (keys: updated,
  recipes, genies; recipe 82928217 row confirmed by grep).
- Watchdog corroboration: watchdog-reports/2026-10-09.md states the finding "no longer
  reproduces"; gossip bus verify post (2026-10-10T03:17Z) confirms closure with 2
  corroborations.

Not verified this pass: who/what mutated the recipes on 2026-10-08 (no record exists);
a fresh AIRO recipe_list re-pull of folder 35202337 (inventory rests on the 2026-10-09
live listing; nothing suggested drift since — watchdog would have flagged it).
