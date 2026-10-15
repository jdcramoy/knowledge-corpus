# Autopsy: unattributed PROD data_table_delete at 2026-10-09T22:47:02.861Z

**Date of autopsy:** 2026-10-09 (same evening, read-only)
**Trigger:** build-ledger.jsonl row with `tool=data_table_delete server=prod` and `asset_name/ticket/session` all null.

## VERDICT

**ATTRIBUTED, EXPLICITLY AUTHORIZED, BENIGN.** The delete was ordered by Josh in-message ("Delete the table and close/resolved the ticket.") and executed 76 seconds later by the ai-directory session. The deleted table was a same-day, session-created scratch cache table (`MCP Tool Call Stats (cache)`, numeric 158060) that had just been superseded by a Snowflake table. The GWS-semantic migration session was NOT the caller, and the GWS semantic registry table (b64781ad) was NOT touched. Blast radius: zero.

## 1. Which table was deleted

**`MCP Tool Call Stats (cache)`** — UUID `b362248a-2477-4d3d-9c2a-74e85b7ef20f`, numeric ID 158060, folder 30138416, prod workspace 3535598.

Evidence:
- The delete call with full arguments is in the session transcript `~/.claude/projects/-Users-<user>-orca-projects-ai-directory/971ed45e-9da7-44b6-9216-fe92a0f7f1bf.jsonl` line 5497: `TOOL_USE mcp__workato-airo-mcp-prod__data_table_delete {"data_table_id": "b362248a-2477-4d3d-9c2a-74e85b7ef20f"}` at 2026-10-09T22:47:01.975Z — matches the audit log entry `~/.claude/workato-audit/prod-writes.log:991` (`2026-10-09T22:47:01.997Z PROD-WRITE mcp__workato-airo-mcp-prod__data_table_delete`) and build-ledger.jsonl:5055 to within a second.
- Table identity from its creation earlier in the same transcript, line 3618 (2026-10-09T05:54:17Z): `Data Table Created — ID (UUID): b362248a-..., Numeric ID: 158060, Name: MCP Tool Call Stats (cache), Folder ID: 30138416`. Created and deleted by the same session, ~17 hours apart.
- Deletion confirmed by tool result, transcript line 5500: `Data Table Deleted — Data Table ID: b362248a-...`.
- Independently re-verified during this autopsy (read-only): `wt-prod dt get b362248a-2477-4d3d-9c2a-74e85b7ef20f` → HTTP 404 `table_not_found`.

## 2. Attribution — who called it, and was it authorized

**Caller:** Claude session `971ed45e-9da7-44b6-9216-fe92a0f7f1bf` in project `~/orca/projects/ai-directory` (session title "func-list-mcp-tools Snowflake timeout"), working ticket BSYS-29443.

**Authorization:** explicit and direct. Transcript line 5493, user message 2026-10-09T22:45:45.556Z: **"Delete the table and close/resolved the ticket."** The delete followed at 22:47:01.975Z. After the delete the session closed BSYS-29443 (line 5513: `transitionJiraIssue` id 251 with `resolution: Fixed`; line 5526 closing summary: "Data table deleted — MCP Tool Call Stats (cache) (158060) is gone; the Snowflake table EDW_DB.WORKATO_USAGE.MCP_TOOL_CALL_STATS is the single source of truth. BSYS-29443 closed — resolution Fixed, verified on read-back").

The `workato-guardrails` PreToolUse hook DID fire and log the write (transcript lines 5498-5499: `workato-guardrails: PROD WRITE · mcp__workato-airo-mcp-prod__data_table_delete`, hook_success) — the audit trail worked as designed. It is informational only; it does not block.

## 3. Consistency with the migration work — initial hypothesis REFUTED

The prompt's hypothesis (caller = GWS-semantic migration session) is **disproven**:

- The 22:22-22:47Z GWS activity in the build ledger is a different session doing different work: rows at 22:22-22:23 are `orca-browser` reads of `~/orca/projects/gws-semantic-export/` plus a `generate_migration_connector.py` run; rows at 22:41:33 and 22:45:38 (build-ledger.jsonl:5053-5054) are read-only `wt dt query` calls against the registry table `b64781ad` from cwd `~/Documents/ChatGPT/Google Workspace MCP`. All reads. That session issued no delete.
- The delete came from the ai-directory session and was the planned final cleanup step of the BSYS-29443 work: migrate MCP tool-call stats off the Workato data table onto Snowflake (`EDW_DB.WORKATO_USAGE.MCP_TOOL_CALL_STATS`), backfill dev, then drop the superseded cache table. It was consistent with THAT migration, not the GWS-semantic one.
- The GWS semantic registry is intact: `wt dt get b64781ad-06b6-44db-bfde-09daeba8e801` (dev/default profile) returns `workspace_semantic_registry`, numeric 147343, schema present. (`wt-prod dt get b64781ad` returns 404, which is expected — PROD_PROMOTION_RUNBOOK.md line 26 lists b64781ad in the "Dev UUID" column; it was never a prod table.)

## 4. Blast radius

**Zero residual references, zero live consumers.**

- Disk sweep for `b362248a-2477-4d3d-9c2a-74e85b7ef20f` across `~/.claude` (excluding session transcripts), `~/orca/projects/ai-directory`, and `~/Documents`: **no matches**. No ledger, doc, script, or knowledge file references the deleted table. It appears only in the transcript of the session that created and deleted it.
- The table lived < 24h as a write-cache for the stats pipeline; the pipeline's recipes now read Snowflake. Final estate per the closure entry in `~/.claude/knowledge/domains/workato-platform.md:1649-1653`: "prod 71768712 + dev 71099839 (both running, cache-read) + filler 82929351 (6h, one CREATE OR REPLACE statement) + Snowflake cache table EDW_DB.WORKATO_USAGE.MCP_TOOL_CALL_STATS. **Data table 158060 DELETED (superseded).** Scratch probe 82928794 still in dev harness folder."
- Ticket BSYS-29443 transitioned to Closed/Fixed at 22:47:38Z, verified on read-back by the session.
- The GWS-semantic registry and its MCP server were never in the blast radius (different table, different workspace env, verified intact above).

## 5. Governance findings (process gaps this autopsy surfaced — not defects in the delete itself)

1. **CLAUDE.md overstates the prod-write gate.** The global instructions say prod write tools "are gated by the `permissions.ask` rule and ALWAYS prompt Josh." In fact `~/.claude/settings.json` has `ask: []` (empty) and `mcp__workato-airo-mcp-prod__data_table_delete` sits in the **allow** list alongside every other prod write tool. In this instance Josh directly ordered the delete, so nothing bypassed him — and the session was in `bypassPermissions` mode anyway (transcript line 5505) — but in a normal-mode session this delete would also have run without a prompt. The only enforced control is the informational `workato-guardrails` hook that logs to `prod-writes.log`. Recommend: move prod write tools (at minimum `data_table_delete`, `data_table_truncate`, `data_table_update`, recipe_builder mutations, blueprint writes, genie/knowledge_base writes, `mcp_server_create`, connector save/release) from `allow` to `ask`, or correct the CLAUDE.md text.
2. **Ledger attribution gap.** build-ledger.jsonl:5055 records the mutation with `session/asset_name/folder_id/ticket` all null, and the guardrails log records only the tool name — not the `data_table_id` argument. The table ID was recoverable only from the session transcript. Recommend the airo-mutation ledger writer capture `session_id` and the primary asset identifier from tool input (`data_table_id`, `recipe_id`, etc.).
3. **The mandated pre-write restatement was skipped.** CLAUDE.md requires the bold `⚠️ LIVE PRODUCTION EDIT` warning + explicit confirmation before any prod write; the assistant turn preceding the delete (transcript line 5496) contained no such restatement. Josh's same-minute direct instruction functioned as confirmation, so intent was unambiguous, but the procedure was not followed verbatim. Worth one line in the ai-directory session's lessons, not an incident.

## Evidence index (every claim above)

| # | Source | Line/loc | Content |
|---|--------|----------|---------|
| 1 | ~/.claude/knowledge/build-ledger.jsonl | 5055 | the unattributed delete row, 22:47:02.861Z |
| 2 | ~/.claude/workato-audit/prod-writes.log | 991 | `2026-10-09T22:47:01.997Z PROD-WRITE mcp__workato-airo-mcp-prod__data_table_delete` |
| 3 | transcript 971ed45e (ai-directory) | 5497 | tool_use with `data_table_id: b362248a-...`, 22:47:01.975Z |
| 4 | transcript 971ed45e | 5493 | Josh: "Delete the table and close/resolved the ticket.", 22:45:45Z |
| 5 | transcript 971ed45e | 3618 | table creation 05:54:17Z: name "MCP Tool Call Stats (cache)", numeric 158060, folder 30138416 |
| 6 | transcript 971ed45e | 5500 | tool result "Data Table Deleted" |
| 7 | transcript 971ed45e | 5498-5499 | workato-guardrails PreToolUse hook fired + logged |
| 8 | transcript 971ed45e | 5505 | permissionMode: bypassPermissions |
| 9 | transcript 971ed45e | 5513-5514, 5526 | BSYS-29443 → Closed/Fixed; closing summary naming Snowflake as single source of truth |
| 10 | ~/.claude/knowledge/domains/workato-platform.md | 1649-1653 | closure entry: "Data table 158060 DELETED (superseded)" |
| 11 | `wt-prod dt get b362248a-...` | live, this autopsy | HTTP 404 table_not_found (deletion confirmed) |
| 12 | `wt dt get b64781ad-...` | live, this autopsy | workspace_semantic_registry intact in dev |
| 13 | build-ledger.jsonl | 5053-5054 + 22:22 rows | GWS-semantic session activity was read-only queries + migration-connector codegen; no delete |
| 14 | grep b362248a over ~/.claude (excl. transcripts), ~/orca/projects/ai-directory, ~/Documents | this autopsy | zero on-disk references |
| 15 | ~/.claude/settings.json | permissions | `ask: []`; `mcp__workato-airo-mcp-prod__data_table_delete` present in `allow` |
| 16 | "Google Workspace MCP"/docs/PROD_PROMOTION_RUNBOOK.md | 24-28 | b64781ad = dev UUID of workspace_semantic_registry; explains prod 404 for that id |

**Actions taken by this autopsy:** none beyond reads (file reads, greps, transcript parsing, `wt/wt-prod dt get` read-only lookups). No writes to Workato dev or prod, no Jira/Slack posts. Only file written: this report.
