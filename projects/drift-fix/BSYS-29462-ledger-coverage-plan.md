# BSYS-29462 plan: inventory [DRIFT FIX] project 10593549 into ledger coverage

Posted as ticket comment 1134567 on 2026-10-09 (jira-autotriage pass).
Status: plan ready, awaiting Josh's build authorization. 1 point.

## Inventory (live recipe_list 2026-10-09, folder 35202337, dev)

| Recipe | Running | Last updated | URL |
|---|---|---|---|
| [DRIFT FIX] retrieve_proposal (82928217) | yes | 2026-10-08 | https://app.workato.com/recipes/82928217 |
| Copy of [DRIFT FIX] get_drift_report (82926620) | yes | 2026-10-08 | https://app.workato.com/recipes/82926620 |
| [DRIFT FIX] validate_proposal (82897971) | yes | 2026-10-08 | https://app.workato.com/recipes/82897971 |
| [DRIFT FIX] log_proposal (82896390) | yes | 2026-10-08 | https://app.workato.com/recipes/82896390 |
| [DRIFT FIX] propose_fixes (82893519) | yes | 2026-10-08 | https://app.workato.com/recipes/82893519 |
| [DRIFT FIX] list_drift_reports (81852212) | yes | 2026-10-08 | https://app.workato.com/recipes/81852212 |
| [DRIFT FIX] get_drift_report (74717532) | no (superseded by 82926620; deprecation candidate) | 2026-10-08 | https://app.workato.com/recipes/74717532 |

No knowledge-tree record ties the project to any harness build; Copy-of pattern
+ zero ledger rows point to out-of-band mutation.

## AC 2 design: seed the ledger, no new config surface

Coverage chain: guardrails ledgerAppend hook -> build-ledger.jsonl ->
asset-fingerprint.py -> workato-health/owned-registry.json -> health sweep /
promotion-readiness / estate-architect. Fix = backfill one externally-managed
inventory row per recipe (7 rows, project 10593549 / folder 35202337), rebuild
the registry, read back. Non-goals: never tag these rows as harness-owned;
74717532 gets an inventory row only.

Build-phase caution: seed rows must match register.js's writer schema before
inserting hand rows.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [2024/05 May Lookback](../../../kb-corpus/confluence/intbt/540639287-202405-may-lookback.md)
- [2026/05 May Lookback](../../../kb-corpus/confluence/intbt/2579726560-202605-may-lookback.md)
- [The Workato KB: RAG++ over all documentation, and the dreaming team](../../../kb-corpus/confluence/extbt/2938929237-the-workato-kb-rag-over-all-documentation-and-the-dreaming-team.md)
- [2026/08 August Lookback](../../../kb-corpus/confluence/intbt/2826666060-202608-august-lookback.md)
<!-- kb-bridges:end -->
