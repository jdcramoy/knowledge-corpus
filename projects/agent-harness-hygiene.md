---
name: agent-harness-hygiene
description: Harness hygiene work products — first entry BSYS-29457 workato-health.py sweep fixes (mock-probe filter, dedupe-on-append, open-slug check)
metadata:
  type: project
---

# Agent harness hygiene — project file

Home for harness-hygiene technical plans and evidence (workato-health.py,
triage queue mechanics, fleet job hygiene). Cross-refs: domains/workato-platform.md
(sweep + dashboard canon), domains/dream-loop.md (/triage loop), triage/queue.jsonl.

## BSYS-29457 — workato-health.py sweep hygiene (plan filed 2026-10-10, comment 1134768)

Ticket: workato-health.py mock-probe filter + dedupe-on-append + open-slug
check (3 triage findings, parent epic BSYS-29454). Points 2.

**State at plan time: all three findings ALREADY LANDED** (approved patch
session 2026-10-09, file `knowledge/scripts/workato-health.py`). Plan = trace
verification + residue collapse, no code changes:

1. mcp_mock probe filter — `is_probe_job()` lines 85-87 + verdict branch
   lines 150-159 (all-probe failure page → verdict "ok", "(N probe jobs
   excluded)" in detail + sweep line). AC 1 code-verified, NOT yet
   trace-verified (branch never fired live — zero real failures since patch).
2. Dedupe-on-append — `triage_append()` lines 105-113: open row with same
   slug updated in place (ts + evidence refresh) via atomic_write, else
   atomic_append. AC 2 verified live: 16 consecutive hourly sweeps clean
   (09:32Z 2026-10-09 → 00:57Z 2026-10-10, fleet health.log), zero duplicates.
3. Open-slug check in separate helper — NOTHING TO PATCH: triage_append is
   the only queue writer (line 188).

Residue: 5 pre-patch duplicate rows for slug
`recipe-health-82090477-new-failures` in triage/queue.jsonl — collapse via
triage-decide.py / gardener dedupe pass, never a manual hand-edit. Origin
incident: prod recipe 82090477 re-flagged 4x on mcp_mock probe noise;
underlying envelope fix tracked on BSYS-29418 (shipped 2026-10-09).

Load-bearing contract for future edits: triage_append stays the single queue
writer with the open-slug in-place update. Adjacent hygiene (separate pass):
3 `unverifiable` sweep verdicts (wt recipes get errors) in recent runs.

**Evidence addendum, 2026-10-11 pass (comment 1134919):** dedupe held under
live firing. Three hourly sweeps (03:09Z/04:10Z/05:10Z) re-flagged real
fail-count drift on dev recipes 82862205 (HR Genie Conversation Event
Collector, fails 31 to 32) and 82934150 (harness_fire_drill, 12 to 13);
queue holds exactly one open row per slug, zero duplicates. Neither is an
mcp_mock probe, so AC 1's all-probe branch still has not fired live
(code-verified only). Residue confirmed still 5 rows for
recipe-health-82090477-new-failures: a raw `grep -c` of the slug returns 8
because the string also appears inside other rows' evidence fields; count
ROWS, not substring hits. Pending unchanged: synthetic AC 1 check + residue
collapse, Josh's go. Traps for future passes: (1) count rows not grep hits,
(2) AIRO recipe_get on 72856618 reports DatapillInvalidPath warnings that
are DSL-export artifacts, not recipe defects.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [The Agentic Workato Harness: a self-improving development organism](../../kb-corpus/confluence/extbt/2938830860-the-agentic-workato-harness-a-self-improving-development-organism.md)
- [Product Scoop &#8211; November 2025](../../kb-corpus/changelog/product-scoop-november-2025.md)
- [[SA-46] Salesforce System Cleanup and Optimization Initiative Overview](../../kb-corpus/confluence/intbt/2505867370-sa-46-salesforce-system-cleanup-and-optimization-initiative-overview.md)
- [The Workato KB: RAG++ over all documentation, and the dreaming team](../../kb-corpus/confluence/extbt/2938929237-the-workato-kb-rag-over-all-documentation-and-the-dreaming-team.md)
<!-- kb-bridges:end -->

## 2026-10-12 jira-triage pass — two hygiene items landed/found
- FIXED: `atomic_io.py` `_validate_timestamp` rejected the `Z`-suffix timestamps that `mission-control.py add` itself generates (Python 3.9 `fromisoformat` cannot parse `Z`; only 3.11+ can). Every `add` on this machine failed with SchemaViolation. Patched to normalize `Z` -> `+00:00` before parsing (the same normalization `mission-control.py` `fold()` already used). Backup: `atomic_io.py.bak-zfix`. Regression-checked: Z accepted, +00:00 accepted, naive and garbage still rejected.
- FOUND (open finding `heartbeat-jsonl-retention-reset`): garden-reports/heartbeat.jsonl was reset ~2026-10-11 21:00 local (file starts 2026-10-11T21:11:57Z), wiping ~36h of rows incl. both dreamers' most recent. Retention/rotation policy needed; git-committed rows through 2026-10-10T04:46Z (commit 61b8175) survive.
- Pass-level pattern worth keeping: when the morning pass has already planned+commented the whole queue, the evening fleet pass's value is LIVE RE-VERIFICATION (recipe running-states, job counts, flag read-backs) and updating plan files in place — duplicate plan comments under Josh's name are queue noise, not work products.
