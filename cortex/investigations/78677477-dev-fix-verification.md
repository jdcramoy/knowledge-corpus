# Investigation findings — BSYS-29418 dev fix, recipe 78677477

Rescued from dispatch log ~/.local/state/cortex/dispatch-20261008-201934-78677477verify.log
(headless run's Write/mkdir into this directory was refused by the sensitive-path gate;
parent cortex session wrote this file on its behalf, 2026-10-09T01:24Z).

Verdict: NOT VERIFIABLE FROM LIVE EVIDENCE - no post-fix job exists. The fix code is
present and structurally correct in the DSL, but the newest job on the recipe is from
2026-10-07, over a day before the 2026-10-08T23:55Z cutoff. Nothing was executed or
edited; pure recipe_get + job_list read on the DEV server
([recipe 78677477](https://app.workato.com/recipes/78677477)).

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Source-probe guard (steps 2-5) present in DSL | PASS (structure only) | recipe_get 78677477: WorkatoMonitor + except WorkatoError wraps step 3; step 5 returns {ok:false, error_code: SOURCE_ACCESS_DENIED/SOURCE_NOT_FOUND/SOURCE_ACCESS_FAILED, upstream_status: 403/404/502} classified from catch_4_message |
| 2 | Carrier-probe guard (steps 28-31) present in DSL | PASS (structure only) | Same pull: step 31 returns the same envelope shape from catch_30_message, message prefix "Carrier access failed at revision probe:" |
| 3 | Post-fix job after 2026-10-08T23:55Z exists | FAIL - none exists | job_list (newest-first, 58 total): newest is j-AbrGtxEB-9Trzxz-CD, started 2026-10-07T02:19:03-07:00 |
| 4 | 403 SOURCE_ACCESS_DENIED envelope in a trace | NOT OBSERVED | No post-fix job to inspect |
| 5 | CARRIER_ACCESS_DENIED envelope in a trace | NOT OBSERVED | Deployed code emits SOURCE_ACCESS_DENIED on the carrier path too (step 31 reuses the same classifier) - if the ticket requires a distinct CARRIER_ACCESS_DENIED code, that is a spec/code mismatch to raise |
| 6 | Happy-path regression in a post-fix trace | NOT OBSERVED / NOT EXCLUDED | Newest execution (j-AbrGtxEB-9Trzxz-CD, succeeded) ran pre-fix code |

Not verified: all runtime behavior - the 403 envelope against a real Google Slides error
message, the classifier's regex matching, and the happy path unchanged post-fix. Closing
it requires one Test on [78677477](https://app.workato.com/recipes/78677477) with an
inaccessible presentation_id (expect the 403 envelope) and one with an accessible one
(expect ok:true unchanged), then re-check traces.

Harness defect note: headless dispatches briefed to write findings into
knowledge/cortex/investigations/ can be denied by the sensitive-path gate, stranding
output in ~/.local/state/cortex/*.log. First occurrence: this dispatch. Fix options
belong to the dreamer/gardener, not the cortex.
