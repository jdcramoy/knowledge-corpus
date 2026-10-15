# Workday Org Chart MCP

One public MCP tool, `Get_Employee_Org_Chart`, serving an allowlisted org-chart
view from a version-pinned materialized Workday snapshot. Zero request-time
Workday access (Workday conn 19760013 is refresh-only). Dev/UAT validated
2026-08-17: 22/22 UAT, 9/9 adversarial, 237/237 stress, zero-error concurrency
ceiling 320, 1,473-descendant full-org in 3.7s. **Standing instruction: do not
promote to Production** (Aug 17 report is readiness evidence, not authorization).

## Canonical locations

- **Canonical repo: `~/orca/projects/org-chart/`** (absorbed 2026-10-08,
  committed 5afb1d9). Read `AGENTS.md` (policy) then
  `ORCA-CLAUDE-CODE-HANDOFF.md` (master handoff) before any work.
- Archive of original: `~/Documents/ChatGPT/Workday Org Chart MCP/`
  (untracked git, no baseline — do not rely on it for rollback).
- `Vijay_Tella_Full_Org_2026-08-15.md` = restricted employee PII. In orca repo
  it is on disk but .gitignored; never copy into tickets, prompts, or handoffs.

## Asset register (live-verified 2026-10-08, all read-only via dev AIRO/wt)

| Role | Asset | ID | Live state |
| --- | --- | --- | --- |
| Public MCP skill | Get Employee Org Chart | recipe 74594114 | Running; folder 32272162, project 13683566; last updated 2026-09-05 |
| Snapshot reader (function) | Build Org Chart From Snapshot | 74597697 | Running; folder 32272170 |
| Scheduled refresh | Refresh Workday Org Chart Snapshot | 74597493 | Running; folder 32272163 (4h cadence) |
| Index builder (function) | Build Org Chart Snapshot Indexes | 74766125 | Running; folder 32272170 |
| Search table | Org Chart Employee Search Index | 22f8a2b1-a7f4-4dba-b7b1-7676f8efed3b (num 137030) | Live; folder 32272171; 15 cols incl. Snapshot Version, Search Text, allowlisted person fields, Active |
| Closure table | Org Chart Relationship Closure Index | 7a27b5ae-d7a9-482e-b8ad-f02bd7dc026f (num 137031) | Live; folder 32272171; 16 cols incl. Relationship Type, Depth, Order Key |
| **DRIFT: telemetry emitter** | async caller-identity call to HR Genie shared func `FUNC \| HR Genie \| Record MCP Tool Usage Identity` | **78563374** (folder 32985204, project 15643451) | Added to skill step 2 post-Aug-17 (last skill update 2026-09-05) — NOT in the handoff asset register |

Drift notes: (1) the skill now emits async masked caller-identity telemetry to
the shared HR Genie recorder 78563374 — shared dependency; any HR Genie change
to that function affects this skill's step 2 (fail-open by design). (2) The
handoff recorded no project/folder IDs; now durable: project 13683566, folders
32272162 (skill) / 32272163 (refresh) / 32272170 (reader+builder) /
32272171 (tables). Not yet verified live: active-snapshot pointer value,
snapshot invariants (count parity, non-empty closure, zero manager/cycle
errors), whether the Sep 5 skill update changed anything else.

## Fixed invariants (do not violate)

- Version-pinned reads from the shared active-snapshot pointer; never mix
  snapshot generations; previous generation stays rollback-usable until a
  validated replacement promotes.
- Views: manager | direct_reports | reporting_chain | full |
  full_organization (whole-org intent routes to full_organization). Formats:
  table | indented | diagram. Cursor-driven while loops, no fixed caps;
  truthful truncation; never substitute page limits for dataset limits.
- Allowlisted fields only (employee_id, full_name, work_email, business_title,
  manager_employee_id, organizations_json, hire_date,
  continuous_service_date, years_of_service; +depth on descendants).
- source_preference auto|live never authorizes request-time Workday access.
- MCP topology: Development = local org-chart-mcp mcp-remote server
  (https://16902.apim.mcp.workato.com/, Codex `mcp__org_chart_mcp__*`; in
  Claude Code map via /mcp — not currently configured in this session's MCP
  list). Live = connected "Org Chart by Workato MCP" app. Dev-vs-live
  benchmark: one identical call per case per surface, never a second
  mcp-remote process as a live substitute.

## Operating rules

- Workato playbooks: efficient-airo-delivery, workato-development-playbook,
  airo-mcp-playbook; build/test via workato-skill-builder; verify via
  verify-recipe. Browser only for genuine UI-only ops.
- Mutations: read live source first, fresh builder session after stop, one
  bounded change, re-read persisted state, restore lifecycle, prove the
  downstream contract (not just a green parent job). Structural UAT gate +
  test order in handoff (`uat/local_npx_orgchart_check.mjs` →
  `official_uat.mjs` → `mcp_stress_matrix.mjs`). Forced-pagination test
  mutates page size — preserve/restore state, isolated Dev context.
- Rollback = validated pointer move to prior known-good snapshot generation;
  never while a candidate is building/unvalidated.
- Update Jira BSYS-27479 only at milestones; query Jira before trusting its
  status as current.

## Open items / future work

- Full live reconciliation of reader/builder/refresh source vs documented
  design (only the public skill was read in full on 2026-10-08).
- Literal >3,000-worker certification still requires a disposable 5,001-row
  fixture (tenant was below 3,000).
- End-to-end chat latency unproven; 640 concurrency = observed overload, not
  capacity.
- Optional: version-aware cache, incremental refresh (needs full
  reconciliation proof), persistent SLO observability.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [MCP Monday: Workday End User, Databricks Data Explorer, and Twitter/X Are Live](../../kb-corpus/changelog/mcp-monday-workday-end-user-databricks-data-explorer-and-twitter-x-are-live.md)
- [MCP Monday: Outlook Calendar and Zoom Meetings Are Live](../../kb-corpus/changelog/mcp-monday-outlook-calendar-and-zoom-meetings.md)
- [MCP Monday: Scheduling, Reporting, and Data, Handled](../../kb-corpus/changelog/mcp-monday-scheduling-reporting-and-data-handled.md)
<!-- kb-bridges:end -->
