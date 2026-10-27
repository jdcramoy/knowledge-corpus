---
name: bsys-29828-overnight-incident-findings-2026-10-21
description: RESOLVED 2026-10-21 — overnight actor identified as joel.ang@workato.com (human, UI, via Activity Audit Log); recreated [LOG] DriftFix_Apply_Log (163016), re-pointed 3 of 4 consumers, restarted Drift Fix Genie; get_fix_proposals 83074639 still fails; audit-stream gap found (table delete NOT in stream)
metadata:
  type: project
---

# [DRIFT FIX] overnight incident — verified live state (2026-10-21, read-only)

Parent: [[drift-fix-project]], plan in [[bsys-29829-genie-approval-gate-plan]]. All times PT, dev workspace.

## Timeline as evidenced

- **2026-10-20 ~01:18** — table 157379 (old Apply_Log) deleted. Pinned by job window: 83074639
  success j-Ac46cJN6 01:17:40 → first "Data table not found" 01:18:50; corroborated by
  retrieve_proposal 01:21 success→fail.
- **2026-10-20 19:31** — NEW recipe daily_fix_summary 83232998 (v3, running, green; reads intact
  Change_Log 157369).
- **2026-10-20 20:22–20:30** — `[LOG] DriftFix_Apply_Log` recreated: numeric **163016**, 23 cols,
  UUID ee8cf4cf-9741-4285-a765-78e3d14a35d5, **folder 35701677** (NOT project folder 35202337).
- **2026-10-20 23:49** — Drift Fix Genie gin-AbWxkCLd-8wRwmG-CD STARTED (propose_fixes was failing
  "Genie is not active." at 23:45, green 00:12). Other three drift genies still stopped.
- **2026-10-21 00:11–01:50** — log_proposal (v17) + retrieve_proposal (v17) re-pointed to 163016,
  green since; NEW recipe revise_fix 83234662 (v4, running, references 163016).
- **Zero build-ledger rows** for any of it — full gate bypass, same out-of-band pattern as Oct 8.

## The one still failing

[get_fix_proposals 83074639](https://app.workato.com/recipes/83074639): v2 untouched since 10-14,
6 ok/17 fails, all "Data table not found" — hardcodes dead table 157379 AND old field IDs
(run_order fc6ef31e→ now 043d1197, change_id b2ef3209→ now e02ef6c9). Latest fail
j-Ac4arQMK-oXP9BB-CD 01:30, error at line 5 `workato_db_table get_records`. **Second latent break:**
recreated table renamed `query_id` → `snowflake_query_id` (field 97ee8d01) — 15 code refs. Plain
re-point will NOT fix it; needs field remap + rename = plan P4.

## Verdict (pre-dissenter)

Coherent repair with one incomplete step — full 23-col schema matching consumer reads, 3/4
consumers green, genie restarted, domain-consistent new recipes. NOT evidence of sabotage. Risks:
gate bypass, table in wrong folder, row-data migration status unknown, **attribution UNPROVEN**
(version_author "Joel Ang"/user 3535597 = credential stamp, not a person; job/genie records expose
no actor; only the UI audit log can settle it — see
cortex/investigations/driftfix-external-edit-provenance.md).

## Josh's open decisions (as of 2026-10-21)

1. Was the overnight repair his / an agent session he ran?
2. Re-stop Drift Fix Genie pending attribution, or leave running? (Stopping removes its served MCP
   tool — the stopped-recipe rule.)
3. Authorize BSYS-29829 P4: re-point 83074639 to 163016 + field remap + query_id rename.
4. Old-table rows: migrated, or accepted as lost?
5. Move recreated table into folder 35202337 for manifest coherence?

Evidence: /tmp/driftfix_recipes.json, /tmp/r_83074639.json, /tmp/jobtrace.json, /tmp/dt_applylog.json
(agent scratch, may be gone post-reboot); live wt/AIRO reads 2026-10-21.

## RESOLUTION (2026-10-21 12:45 ET session) — attribution PROVEN via Activity Audit Log

- Pulled workspace **Activity Audit Log** (Operations hub → Activity audit) in-page via the signed-in
  Orca tab: `GET /web_api/activity_logs?created_at_from=<iso>&created_at_to=<iso>&cursor=<cursor>`
  (**`cursor` is the correct pagination param — `next_cursor`/`page_cursor` silently return page 1
  again**; 50/page; ~1,362 events for the 18h window).
- **All 78 drift events 10-20 22:27 ET → 10-21 04:55 ET carry user joel.ang@workato.com** (workspace
  collaborator 8473681), IP 61.13.208.78, Chrome 155 UA — genuine human UI work, not a credential
  stamp and not an agent. Folder context "[GENIE] [DG] DataGenie/V2/Joel Enterprise Data MCP
  Testing/Drift Fix" is his own test project.
- Full timeline confirmed: retrieve_proposal edits from 22:27; daily_fix_summary created 22:31;
  **table 163016 created 23:22:09 + ~20 schema updates through 23:39**; our fleet's genie stops
  (23:25:39–43, wt/1.0) landed MID-rebuild; **genie started 02:46:41 + moved to folder 35202337 +
  updated 02:49:45** (= the 23:49 PT modification); revise_fix created 03:22; old get_drift_report
  moved to NOT IN USE 03:37; **get_fix_proposals REMOVED from Drift Fix MCP server mcps-AbQGAYrF-stw-CD
  at 04:53** (replaced with daily_fix_summary + revise_fix).
- **⚠️ Audit-stream gap (material, affects BSYS-29829 P3):** swept 10-19 00:00 → 10-20 23:00 ET
  (2,215 events): NO `workato_db_table_deleted` for Fix_Apply_Log/157379 anywhere, and no record of
  its original creation either. The plan's premise "the audit stream is the one channel that recorded
  the deletion" is FALSE — P3 watchdog must not rely on the stream for this delete class without a
  spike first. The "Joshua Cramoy (via AIRO)" attribution likely came from the UI banner/trash.
- Posted to Jira: BSYS-29829 comment 1145333 (attribution + correction), BSYS-28296 comment 1145332
  (manifest link fix). Recommendation recorded: leave the genie running, sync with Joel.
