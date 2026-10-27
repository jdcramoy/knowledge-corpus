# Regression autopsy batch — 2026-10-16 (read-only investigation, cortex)

Source: `~/.claude/knowledge/garden-reports/regression-2026-10-16.md` (identical to `regression-latest.md`, run 2026-10-16 00:14Z).
Headline: **16 passed / 6 failed / 3 errors** (test-run phase) + fixture phase 1 pass / 2 fail / 7 skip. Canon auto-seeded 2 (82059061, 82202341). Triage card: `triage/queue.jsonl` slug `regression-failures-2026-10-16`, status open, high, 3 pts.

## FAILs — 6 failing test cases across 5 recipes

1. **82059061** FUNC | Dispatch Inbox Notification — case "Untitled test case 1" (citc-AbRGm4EB-NWDHbe-CD) — job j-AbxrPAtf-oQAxfJ-CD, run cirr-AbxrPAto-Atfpd3-CD. Class: test-case failure, unautopsied. https://app.workato.com/recipes/82059061
2. **82202341** FUNC | Dispatch PTO Notification — case "Untitled test case 1" (citc-AbXpQ8nJ-hHCfcA-CD) — job j-AbxrPgDE-Yng3p8-CD, run cirr-AbxrPgDL-wQd8NY-CD. Class: test-case failure, unautopsied; identical shape to 82059061 (both HR Genie dispatch gates). https://app.workato.com/recipes/82202341
3. **82248514** Seismic | Search authorized content catalog — case "Untitled test case 1" — job j-AbxrQ9E3-PsHeB8-CD, run cirr-AbxrQ9EC-Y6reeC-CD. Class: test-case failure, unautopsied. https://app.workato.com/recipes/82248514
4. **82272814** workspace_vua_identity_probe — case "Untitled test case 1" — job j-AbxrRcCG-J8dGfe-CD, run cirr-AbxrRcCP-gGCHoT-CD. Class: test-case failure, unautopsied (GW Semantic MCP). https://app.workato.com/recipes/82272814
5. **82272892** Sync Google Workspace Discovery Catalog — case guard-empty-records-json (BSYS-29456) — job j-AbxrRnTc-m9Lhg9-CD. https://app.workato.com/recipes/82272892
6. **82272892** — case upsert-populated-records-json (BSYS-29456) — job j-AbxrRnTc-Drt86M-CD, run cirr-AbxrRnTk-JwEbeW-CD. Class (per UAT sweep 2026-10-16, draft 2): test-case rot — "steps with mocks or checks were deleted from the recipe"; recipe live health green (latest live job succeeded). Guards are dark, pipeline is not.

## start-ERRORs — 3 recipes, "could not start run" (no job IDs)

7. **82239660** POC | HR Genie Runtime Connection Hygiene Audit. https://app.workato.com/recipes/82239660
8. **82727069** run_genie_evals. https://app.workato.com/recipes/82727069
9. **82959480** create_prospect (Outreach MCP tool, skl-AbsnzRFK-fnpnPf-CD). Note: ZERO lifetime jobs per BSYS-27111 re-verification 2026-10-11 — a start failure on a never-run asset may be asset-local, not platform. https://app.workato.com/recipes/82959480

Triage-card hypothesis: BSYS-29383 OOM/502 family, one root cause / one autopsy. **Caveat:** BSYS-29383's verified root cause (full-stack trace completed 2026-10-16) is the AHQ workspaces' deployment-tables memory pattern (`[DEPLOY] LF | Build recipes table` accumulating full recipe DSL) — different workspace, different mechanism. The attribution for this dev-workspace "could not start run" class is unproven until one real autopsy.

## Fixture phase (outside the headline 6+3)

- **FAIL 82863111** REC | HR Genie | Ledger Correlator — job j-AbxrTPEf-DEp6Tx-CD — class: fixture scorer assertion `path 'job.status': missing key 'job'` — fixture/scorer shape mismatch. Canon doc `regression-canon/correlator-capped-watermark-livelock.md` flagged this fixture as scaffolded-empty on 10-10; it now has expects but the scorer path does not match the job output shape.
- **FAIL 82959481** Vibe-Coded App Registry | Register App (API recipe) — timeout, no job ID.

## 82862205 collector-family flag

- **CORE family:** 82863111 (Ledger Correlator — one of the BSYS-29488 four-collector set: 78545249 / 82863111 / 82862205 / 82178793; Intelligence Platform stack per hr-genie asset-graph L15).
- **Family-adjacent (HR Genie notification/dispatch layer, downstream of the collector):** 82059061, 82202341 (dispatch gates feeding messenger 74094657); 82239660 only by project (audit POC).
- **The collector itself 82862205 PASSED 1/1** (run cirr-AbxrTDP3-xYkNNQ-CD, per triage note on v44). This batch is NOT a collector regression.
- **Outside the family:** 82248514 (Seismic), 82272814 + 82272892 (GW Semantic MCP), 82727069 (genie evals), 82959480 (Outreach MCP), 82959481 (Vibe registry).

## Suspected root-cause groups

- **Group A — test-harness rot, recipe health green (fix = re-record/repair tests, no recipe logic change expected):** 82272892 x2 (deleted-mock rot), 82863111 (fixture scorer missing-key).
- **Group B — shared dispatch-gate failure (one autopsy covers both):** 82059061 + 82202341 — identical single-case shape, auto-seeded same night; suspect a common upstream change in the HR Genie dispatch/messenger path or shared test fixture.
- **Group C — could-not-start-run class (one autopsy; verify or kill the BSYS-29383 attribution):** 82239660, 82727069, 82959480.
- **Group D — singletons needing individual autopsy:** 82248514 (Seismic search), 82272814 (VUA probe), 82959481 (fixture timeout).

## Count reconciliation

Headline "6 failed / 3 errors" = 6 failing test cases across **5** recipes + 3 start-error recipes = **8 distinct recipes**; the triage card's "9 recipes" presumably folds in one fixture FAIL. Both fixture FAILs counted = 10 distinct recipes touched. Canon auto-seeded exactly 2 (82059061, 82202341) — the other failures have no canon rows yet.

Not verified (read-only charter): no job traces opened, no recipes inspected live; error classes for items 1-4 and the start-ERROR attribution are inferred from the report + triage card, not from traces.
