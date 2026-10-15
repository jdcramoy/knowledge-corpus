# Attention queue — pulse 2026-10-13T09:10Z (rev m)

WRITE GATE: canonical cortex/attention-queue.md still permission-gated this pulse (Write tool
and cat-overwrite both denied, second consecutive pulse); queue recorded HERE. Blockage
question stands from 06:58Z.

1. **needs-josh debt: 30 open rows, 12 workstreams >24h stale.** Sharpest: hr-genie-workday-mcp
   (32h — VUA flip + Workday tenant grants block the HR contact-info write path),
   btsup-service-desk (32h — customer-workspace Genie fix go + 4 staged customer replies awaiting
   send), ai-roi-framework (30h — value-thesis approval), sfdc-accounts-sync BSYS-29515 (26h —
   build kickoff + 2 design calls), jira-autotriage 6-gate batch (18h, incl. Marketo
   red-team-FAIL remediation). Ref: mission-control/registry.json (fold 09:01Z).
2. **Canary 82964017 — autopsy LANDED, fix-ready, still down >14h.** Root cause: trigger config
   drift from the v12 push (16:39 PT Oct 12, ZERO build-ledger rows — built outside ledger
   discipline): picklist LABEL "Minutes" stored instead of option ID "minutes", stale
   "Days" dynamicPickListSelection contradicting it, orphaned trigger_at. The 13
   DatapillInvalidPath inconsistencies are runtime-proven innocent (last green job executed chain
   D end-to-end on those pills). Fix = re-set the trigger via builder with option IDs. Dev gate =
   Josh; BSYS-29560 still Backlog/unassigned. Ref:
   cortex/investigations/82964017-trigger-autopsy.md.
3. **KB sync camel failure — diagnosis LANDED, root cause is upstream of camel.** Dirty working
   trees: an unattributed Oct-11 ~03:51 build-window link-rewrite pass rewrote external URLs into
   cross-corpus relative links INSIDE 9 of 20 github source repos; camel's `_repo` pull
   --ff-only wedged on a local-changes-overwritten refusal (fetch fine, merge refused). Azure has
   been failing nightly, silently, since 10-12 (floor only checks CORE). Remedy: find/stop the
   link-rewrite actor, then harden `_update_repo()` to fetch + reset --hard, capture stderr,
   alert on ANY source error. Repair go = Josh; hardening filed to triage. Ref:
   cortex/investigations/kb-sync-camel-source-failure.md.
4. **Mission-control fold computes NO staleness for non-done workstreams** (only
   STALE_DONE_DAYS=14 for done rows); board.html hides the 12-stale cohort. Events-only rule bars
   cortex from fixing the script — Josh proposal stands (triage row
   mission-control-fold-staleness-blindspot).
5. **82272892 canonization: 2 canon-entry candidates awaiting approval** — registry-data
   invariant violations (connector risk/confirmation raise; conflicting-activation-contracts),
   fail-closed and self-clearing, NOT a regression. Un-canonicalized, the health sweep keeps
   re-flagging them as false alarms (again 06:36Z). Ref:
   cortex/investigations/82272892-canon-vs-sweep.md.
6. **Session-shadow DOWN since 2026-10-12T23:27Z** — launchd exit 78 (/opt/homebrew/bin/python3
   moved); now-file frozen, so "no live session" inferences are unreliable. Fix is a one-line
   plist repoint = Josh question open since 06:58Z.
