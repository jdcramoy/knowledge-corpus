# Attention queue — pulse 2026-10-13T07:50Z

NOTE: attention-queue.md is permission-gated this session (Write/overwrite/append all
denied); the rebuilt queue is recorded HERE and the blockage filed as a question.

1. **needs-josh debt: 27 open rows, 12 workstreams >24h stale (cohort grew 10→12 in 2h).**
   Sharpest: hr-genie-workday-mcp (30.9h — VUA flip + Workday tenant grants block the HR
   contact-info write path), btsup-service-desk (30.9h — customer-workspace Genie fix go +
   FOUR staged customer replies awaiting send), ai-roi-framework (29.3h — value-thesis
   approval), sfdc-accounts-sync BSYS-29515 (25.3h — build kickoff + 2 design calls).
   Newer gates: jira-autotriage 6-gate batch (16.9h), gws-semantic-catalog-sync BSYS-29585
   (4.6h). Ref: mission-control/registry.json (fold 07:50Z).
2. **Canary 82964017 gw_semantic_mutation_chain_canary — DEFECT confirmed, still down 4h+.**
   Workato auto-stopped it (trigger_errors_limit, 03:35–04:35Z); health sweeps still red at
   06:36Z and 07:36Z. BSYS-29560 is Backlog/unassigned while its AC demands 24h of hourly
   runs. Root cause unpinned (lead: 13 DatapillInvalidPath inconsistencies, steps 26–32) —
   autopsy-investigation dispatched this pulse (kimi-k3). Fix-forward gate = Josh. Ref:
   cortex/investigations/gws-mutation-chain-canary-82964017.md, triage row
   recipe-health-82964017-stopped.
3. **KB sync failing its source-count floor 2 consecutive nights — camel source.**
   `git pull --ff-only` on corpus/camel/_repo exits 1 (sync_alerts 10-12 22:48Z, 10-13
   00:41Z); camel is ~2 days stale for every fleet RAG query that needs it. Lookup
   dispatched this pulse (flash); repair authorization = Josh (Q2). Triage row
   kb-sync-camel-source-failing filed.
4. **Mission-control fold has NO staleness pass for non-done workstreams — confirmed by
   investigation.** Only age logic is STALE_DONE_DAYS=14 for done rows; board.html shows no
   stale cohort (the 12-row >24h list above is a cortex overlay). Events-only rule bars the
   cortex from editing the script — triage row mission-control-fold-staleness-blindspot
   open, Josh proposal stands.
5. **82272892 canon-vs-sweep: 2 NEW canon-entry candidates awaiting approval.** The 3
   post-FIXED failures are registry-data invariant violations (connector risk/confirmation
   raise; conflicting-activation-contracts in Derive-unique-operation-contracts), fail-closed
   and self-clearing — not a regression, closed fix verifiably intact. Un-canonicalized, the
   health sweep re-flags them as false alarms (it did again 06:36Z). Q3 to Josh.
6. **kb-wave3-sources: closeout written by cortex this pulse per recorded default.** Build
   landed and live-verifies (camel 812, snowflake 8,922 rows; eval n=275 R@10 0.8945).
   Row moved in-flight→needs-josh: two tails (uncommitted code in ~/Documents/workato-kb;
   fix never proven by a live post-fix sync) are now explicit Josh decisions. Ref:
   cortex/investigations/kb-wave3-sources-aliveness.md.
7. **Session-shadow DOWN — cross-session awareness blind.** launchd exit 78
   (/opt/homebrew/bin/python3 moved); now-file frozen at 2026-10-12T23:27Z, so "no live
   session" inferences are unreliable until repointed. Josh question open since 06:58Z;
   fix is a one-line plist repoint only Josh can authorize.
