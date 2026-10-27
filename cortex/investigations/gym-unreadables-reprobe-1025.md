# Replay-gym unreadables re-probe (2026-10-25, read-only investigation)

**Verdict: TRANSIENT — all five recipes re-probed as fully READABLE on dev (josh-us) today. Zero persistent-unreadables.**

Method: `wt recipes get <id>` via wt CLI, env token verified against workspace 3535597 ("Workato AHQ | AI", dev — /api/users/me id 3535597) before probing. Read-only; nothing mutated.

| Recipe | Name | Result | Running | Notes |
|---|---|---|---|---|
| 83326270 | EM \| Data Table Inventory Reconciler | READABLE (200, full JSON) | — | BSYS-29944 reconciler |
| 83326303 | TEST BSYS-29944 re-baseline | READABLE (200, full JSON) | stopped | manifest-exempt TEST probe |
| 83330363 | Route to HR Genie — Streaming Gateway (AWS) | READABLE (200, full JSON) | running | BSYS-29946 canary |
| 83330387 | MG AWS Token Stream Poller (dev) | READABLE (200, full JSON) | running | BSYS-29946 SQS poller |
| 83331083 | TEST AWS e2e probe runner | READABLE (200, full JSON) | stopped | manifest-exempt TEST probe |

## Error class

The original replay-gym finding was "unreadable on dev AND prod (non-404)" — an error that was NOT 404. Today every probe returned clean 200s with full recipe JSON, so the failure did NOT reproduce. No error class observable in this session. Plausible classes for a transient non-404 across two profiles simultaneously: upstream gateway 5xx, rate-limit, or a gym-side client/token/session issue at probe time. A same-instant failure on both dev and prod tokens points more toward a shared client/network layer than workspace-side state. Recommend the gym capture HTTP status + body on next occurrence so the class is classifiable.

## Canon coverage

All five ALREADY covered by open canon rows in regression-canon/canon.jsonl (lines 118-122, found 2026-10-25, status open, test_case_id null):

- gym-recipe-unreadable-83326270
- gym-recipe-unreadable-83326303
- gym-recipe-unreadable-83330363
- gym-recipe-unreadable-83330387
- gym-recipe-unreadable-83331083

## Triage cards (per-recipe, not about unreadability itself)

- 83330363 — open card `uat-sweep-83330363` (different failure: 400 invalid_request on skill calls).
- 83326270 — open card `bsys-29944-reconciler-page-asymmetry` (different failure: pagination bug).
- 83326303, 83330387, 83331083 — no open triage cards.

## Suggested disposition (for Josh / canon owner — NOT applied)

The five canon rows can be marked resolved-transient (no repro on re-probe, full 200 evidence 2026-10-25) per the failure-close-gate rule — which requires the canon row update in the same run that closes them; this read-only session deliberately did not touch canon.jsonl.
