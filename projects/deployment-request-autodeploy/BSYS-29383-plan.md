# BSYS-29383 — Auto-deploy memory failures (recipe 3792733, BT Production workspace 800229)

Filed: 2026-10-15 (jira-triage pass). Status: plan ready, awaiting build authorization.
Ticket: https://workato.atlassian.net/browse/BSYS-29383 (High, In Progress)
Recipe: 3792733 "[DEPLOY] LF | Get Folder ID for Deployment", https://app.workato.com/recipes/3792733
(workspace 800229 "Workato AHQ | BT Production", folder 1839745, project 789886)
Helper: 3792735 (per-file processor, called via recipe-function from step 17; also 3792727 folder
creator at step 33). Wrapper function 3792728. Related main recipe 3383902.

## Evidence (live, 2026-10-15)

- Recipe DSL read in full (100KB cached get_recipe from the dependency tracker; the AIRO dev token
  is permission-denied on workspace 800229, the dependency tracker is not).
- Three Snowflake `search_rows` steps (7, 22, 31) query `DEPLOYMENT.FOLDERS` with server-side
  `where` + `limit: 100` — the lookups are NOT the memory problem (dissenter round 1 falsified the
  draft that blamed them).
- Real memory path: step 1 `file_connector/uncompress_file` inflates the ENTIRE manifest ZIP in
  memory; foreach step 14 base64-encodes every file (+33%) and passes each as a string through a
  recipe-function call to helper 3792735. Lookup-table CSVs and adapter code all live in job memory.
- Recipe last edited 2023-01-03. Failure onset 2026-10-06. 711 jobs/90d, 7-day error rate ~27.7%
  with healthy runs interleaved (healthy job 10-13 15:51 after a 10-13 12:26 failure).
- Most recent failure was WRF00400 recipe-function execution error at step 17, NOT memory:
  at least three failure modes are conflated on the ticket (memory shutdown, transient 502,
  function execution error).
- New comment 2026-10-14 17:45 ([colleague]): Product suggestion in a Slack thread — unreadable
  from the triage session; must be pulled into the ticket as text.

## Open question (gated on traces)

Unchanged recipe failing intermittently since 2026-10-06 = either (a) typical manifest content
grew past the memory cap, or (b) a Workato platform-side change (regression). Date clustering in
the traces decides it. Traces are unreachable from this session (no workspace 800229 access).

## Plan (posted to Jira 2026-10-15)

1. Pull failed 3792733 job traces — named executor required: workspace grant for Josh, or a
   deploy-platform teammate exports them. Find the exact step the memory shutdown fires on;
   cluster failures by manifest size vs by date (date clustering = platform regression signature).
2. Get Product's Slack suggestion into the ticket as text; if it names a known platform
   regression, this plan defers to it.
3. Fix (contingent on traces): restructure manifest handling to stop holding the whole ZIP and
   every file's base64 in memory — batch the files, or pass file-storage references to 3792735
   instead of string contents.
4. Retry envelope on the function call for transient 502/WRF00400 — labeled CONTAINMENT, not the
   fix; retries logged, ticket still commented after final failure.
5. Backfill `DEPLOYMENT.FOLDERS` for manually imported deployments (BSYS-29380's manual import
   created folders with no bookkeeping rows — drift compounds).
6. Interim ops path during diagnosis: failed approved DRs fall back to documented manual import
   WITH the DEPLOYMENT.FOLDERS backfill, so drift stops accumulating.
7. Regression test: synthetic manifest with oversized lookup-table CSV through the deploy
   function, aimed at a THROWAWAY SANDBOX destination workspace/folder, NEVER prod IDs (the test
   path creates real folders and real bookkeeping rows at steps 33-35).
8. Size: 5 points.

## Dissent record

- Round 1: BROKEN. Falsified the Snowflake-lookup diagnosis with live DSL; located the real
  memory path; flagged conflated failure modes and the access problem. (thread
  dissent-bsys-29383-memory-diagnosis, findings in knowledge/dreams/bus/dissenter.jsonl)
- Round 2: REVISE. Two one-clause fixes (sandbox destination for the test; named trace-pull
  executor), points 3 → 5, interim ops path added. All absorbed above.
- Evidence file: ~/.claude/projects/-Users-<user>-Documents-workbench/7fc3d60d-8584-45e6-ad53-afee5ad774f8/tool-results/mcp__workato-dependency-tracker__get_recipe_0_3ee75920.json

## Not verified

Failing job traces, Product Slack thread content, whether Product's suggestion supersedes this plan.
