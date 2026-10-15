# BSYS-28306 plan — Genie Skill: Nudge US employees to complete missing payroll-critical data before payroll (Employee)

Ticket: https://workato.atlassian.net/browse/BSYS-28306 (epic BSYS-26808, Backlog, Medium). Plan posted 2026-10-09 (comment 1134655); build executed and corrected 2026-10-10 (comments 1134851, 1134853). This file refreshed 2026-10-11 after a live re-verification pass.

## Current state (live evidence, 2026-10-11)

- [send_payroll_data_nudges_us (82959797)](https://app.workato.com/recipes/82959797) read live from dev (folder 30326966, project 15643451): Running=False (stopped, correct while dry-run/grant-gated). Connections: Workday SOAP 19760790, Slack bot 20369210. Daily 08:00 schedule.
- The client-side US filter is present in the classifier code (the connector silently drops Request_Criteria.Country_Reference on push; per-worker country comes from Name-detail country reference, alpha-3; non-US skipped and counted, never guessed).
- The domain-strip safety guard is present in the classifier (near-universal birth-date absence + zero readable emails = SAFETY_HOLD, send structurally blocked).
- Bank-election scan wired: Cash_Management Get_Payment_Election_Enrollments joins via Role_ID_Reference_WID, US rows by ISO alpha-3.
- Shared tables verified: [HR Genie | Payroll Nudge Region Config](https://app.workato.com/data_tables/bdf445b4-60c4-42b0-9891-d96cc0f5ed89) (numeric 158555, 12-column schema read live) and [HR Genie | Payroll Data Nudge Log](https://app.workato.com/data_tables/984bba3f-26af-46c8-a90f-2fe3825cd275) (numeric 158554, dedupe key US:worker:period).
- Row values not re-read this pass (the AIRO data-table query route 404s on this workspace): US row state per comment 1134851 is send_mode=dry_run, next_payroll_date=2026-10-15 (config source), days_before=10.

## Remaining work (the plan from here)

1. Workday domain grants for the integration identity (Personal Data / National ID / Contact Information) plus the Payroll period-schedules grant or an equivalent RaaS/WQL report. Without them every read is stripped and the guard holds (safe, but no real nudge can fire). Josh/HRIS request; probe recipes stay stopped for re-verification after the grant.
2. Truncate the 999 safety_hold ledger rows before any real-period live run (they only affect the dev test period 2026-10-15).
3. Editor Test runs + test-case authoring on 82959797 (missing each field, complete employee, non-US excluded, rerun dedupe). UI-only via Orca; staged while the browser is contended.
4. Flip the US region row send_mode to live, set the real payroll date, start 82959797, verify the first live run's trace and ops summary.

## Acceptance criteria (outstanding)

- [ ] Only US-based active employees with at least one missing field flagged; non-US excluded (re-verify post-grant via the Non-US skipped counter).
- [ ] Exactly one Slack DM per employee per payroll period; field names only, no values; no third-party data.
- [ ] Complete employees receive nothing.
- [ ] Live run writes ledger rows; same-period rerun dedupes.
- [ ] Editor Test + test cases pass on 82959797.

## UAT Evidence

Job traces for a full live scan (scanned / non-US skipped / flagged / sent counters), ledger rows per nudge, a rerun trace with zero duplicate DMs, and a PII check confirming no government ID or bank values in messages, ledger, or logs. Prior dry-run evidence stands: verification run j-Absr4Gz6-EzAMtD-CD (999 scanned / 669 non-US skipped / 330 flagged / 0 sends) and dedupe run j-AbsphHHF-6Br3Mw-CD.

## Sequencing note

None of the nudge assets are in the BSYS-29498 combined prod batch (manifest 361068 v5 does not list 82959797 or the two nudge tables). Shared surfaces with the in-flight batch: Workday SOAP connection 19760790, Slack bot 20369210, and the ops channel. Whether US live sends wait behind the Oct 2026 prod batch deploy or run independently is Josh's call.

## Points

5 total. Build is complete in dev; residual effort is about 2 points (grants re-verify, test authoring, live flip, UAT evidence).

**plan ready — awaiting Josh's authorization to kick off the build.**
