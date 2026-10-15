# BSYS-28307 plan — Genie Skill: Nudge non-US employees to complete missing payroll-critical data before payroll (Employee)

Ticket: https://workato.atlassian.net/browse/BSYS-28307 (epic BSYS-26808, Backlog, Medium). Plan posted 2026-10-09 (comment 1134658); build executed and verified 2026-10-10 (comment 1134847). This file refreshed 2026-10-11 after a live re-verification pass.

## Current state (live evidence, 2026-10-11)

- [send_payroll_data_nudges_nonus (82959747)](https://app.workato.com/recipes/82959747) read live from dev (folder 30326966, project 15643451): Running=True, daily 07:30. Connections: Workday SOAP 19760790, Slack bot 20369210.
- The classifier code carries the client-side country filter (per-worker country from Name-detail country reference; rows outside the region code are skipped and counted as other_country_skipped, never guessed). This answers the silent-drop defect flagged for this sibling in BSYS-28306 comment 1134853.
- Config table [HR Genie | Payroll Nudge Region Config](https://app.workato.com/data_tables/bdf445b4-60c4-42b0-9891-d96cc0f5ed89) (158555, schema read live) drives required fields, date source, guidance copy, and send_mode per country; the resolver skips incomplete rows and workday-source dates with a reason, never nudges defaults, and hard-skips US rows.
- Ledger [HR Genie | Payroll Data Nudge Log](https://app.workato.com/data_tables/984bba3f-26af-46c8-a90f-2fe3825cd275) (158554), dedupe key worker:region:period; per-run ledger pre-read excludes already-nudged workers BEFORE the 40/region/run cap so the batch advances daily.
- bank_election is declared unresolved for the non-US variant (no bulk scan surface in this build; surfaced in unresolved_fields, not silently dropped).
- Diagnostic counters (diag_birth_seen / diag_nid_seen / diag_email_seen) are in the classifier output for post-grant re-verification.

## Remaining work (the plan from here)

1. Workday Personal Data / National ID / Contact domain grants for the workato2 integration identity (confirmed blocker: 0/999 birth dates, 0/999 national IDs, personal-information present on only 18/999). Every current flag is a false positive until the grant lands. Then re-verify via the diag counters.
2. Truncate the 583 dry-run dev ledger rows before the live period (they would dedupe-block real nudges for the 2026-10-15 GB date). The unfiltered page-1 scan rows from before the client-side filter are in the same truncation.
3. HR-confirmed region config rows (required fields, dates, guidance copy per country/provider) replacing the three dev seeds. Required fields are a policy input; the build does not invent them.
4. Editor Test + test-case authoring on 82959747 (per-country config resolution, no-config skip, rerun dedupe, US exclusion). UI-only via Orca; staged while the browser is contended.
5. Ops-channel digest (channel ID needed) and the per-region send_mode=live flip, then first live run trace verification.

## Acceptance criteria (outstanding)

- [ ] Non-US active employees with country-configured missing fields flagged X days before their payroll date; US excluded by construction and by the resolver's US-row skip.
- [ ] Field set, date source, and copy resolve per country/provider; a country with no config row is skipped and reported.
- [ ] Single DM per employee per period, field names only, provider-appropriate guidance.
- [ ] Every live nudge writes a ledger row; same-period rerun dedupes.
- [ ] Test cases pass on 82959747.

## UAT Evidence

Full-scan job traces with the flagged list grouped by country/provider, per-DM send results, ledger rows with the region column, rerun dedupe trace, and a PII check. Prior dev evidence stands: green end-to-end runs j-AbspEP9s through j-AbspXbEg, the 583-row ledger audit with zero duplicate keys, and GB due / IN skipped-with-reason / US hard-skip trace lines.

## Sequencing note

No nudge asset is in the BSYS-29498 combined prod batch (manifest 361068 v5). Shared surfaces with the in-flight batch: Workday SOAP connection 19760790 and Slack bot 20369210. Whether the GB live window (config date 2026-10-15, now inside the batch deploy window) goes live before or after the Oct 2026 prod batch is Josh's call.

## Points

The ticket carries 5, matching the US twin (BSYS-28306). Build is complete in dev; residual effort is about 1.5 points (grants re-verify, config rows, test authoring, live flip, UAT evidence). Re-verified live 2026-10-11 evening pass: recipe 82959747 still running daily 07:30, classifier filter and ledger wiring unchanged, FUNC/audit assets for BSYS-28314 also re-read green.

**plan ready — awaiting Josh's authorization to kick off the build.**
