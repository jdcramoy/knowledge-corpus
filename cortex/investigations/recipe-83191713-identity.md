# Recipe 83191713 — Identity Investigation (read-only lookup)

Dispatched by cortex quiet-pulse 2026-10-20 ~02:25Z. Scope: wt CLI reads + file reads only.
All times UTC unless noted.

## (1) What the recipe is

- **Name:** `delete_table_of_contents (Google Docs by Workato MCP)`
- **URL:** https://app.workato.com/recipes/83191713
- **Folder:** `Google Docs by Workato MCP` (29891061), inside project **MCP | BT Managed MCP**
  (27328084), project_id 13683566.
- **Type:** `workato_skill` trigger (MCP tool recipe → an `agentic_skill` row in manifests;
  skill handle **skl-Ac3pTon4-rseLGa-CD**).
- **Purpose:** Deletes table-of-contents (`tableOfContents` structural elements) from a Google
  Doc via exact-boundary `deleteContentRange`. Flow: `get_document` → Ruby builder
  (TocDeleteRequestBuilder: scans all tabs, resolves missing indices by structural tiling,
  revision-mismatch guard, highest-index-first ordering) → adhoc HTTP `batchUpdate` on the
  google_docs connector → re-fetch for new revision → returns deleted_count / ranges /
  revision / doc URL. Params: document_id (req), required_revision_id, tab_id, occurrence (opt).
- **Origin:** BSYS-29800 ([colleague] TOC report 2026-10-19) — stated in the recipe description.

## (2) Ticket / ledger linkage

- **Ticket: BSYS-29800** — "Google Docs MCP: add delete_table_of_contents tool ([colleague] TOC
  report)". In recipe description + registry closeout row. No ticket id in ledger rows
  (`ticket: null`) — linkage is via the registry + description.
- **Build ledger** (`~/.claude/knowledge/build-ledger.jsonl`): session **`gdocs-toc-delete-build`**.
  Built 2026-10-19 22:46Z (recipe_builder_init as 70572944, immediately re-created via
  recipe_builder_init_skill as **83191713** at 22:47:42Z). Iterated 22:46Z→02:03Z
  (push at 02:03:38Z), then a late `set_input_field` + `recipe_builder_push` at 02:21–02:22Z,
  `wt recipes start` at 02:25:13Z. The 02:09–02:16Z "probing" flagged by the pulse is that
  SAME session's verify loop (wt recipes get @ 02:09, wt jobs list @ 02:13,
  wt jobs get j-Ac3tk8A8-MzJpR8-CD @ 02:16) — read-only verification, not a mystery session.

## (3) Current state (live wt reads, 2026-10-20 ~02:26Z)

- **running: true** (started 02:25Z after version-7 push at 02:22Z).
- **Jobs: 1 succeeded / 6 failed.** Latest job **j-Ac3w3zX8-FtehW3-CD SUCCEEDED**
  (started 2026-10-19 19:27:58-07:00 = 02:27:58Z) — the tool works on a live run post-fix.
- Failure history (chronological): 4×403 Forbidden (17:03-07:00, connection perms), then
  "tableOfContents #1 has no indices" (18:42-07:00 — the exact bug the Ruby resolver now
  handles), then **j-Ac3tk8A8-MzJpR8-CD** (19:11-07:00) — 400 "Invalid requests[1]
  .deleteContentRange: Invalid deletion range", the failure the probed job-trace was checking.
  That 400 appears fixed: push at 02:22Z → successful run at 02:27Z.
- Note: recipe-get showed 0 succeeded at first read; jobs list shows 1 — the success landed
  between reads (02:27Z run).

## (4) Mission-control coverage — **YES, covered** (the pulse's "unregistered" flag is stale)

- `~/.claude/knowledge/mission-control/registry.json` line ~1355 + `events.jsonl` line 856:
  **closeout row, workstream `google-docs-mcp`, Jira BSYS-29800, state `needs-josh`,
  ts 2026-10-19T23:08:42Z** — explicitly names recipe 83191713, skill skl-Ac3pTon4-rseLGa-CD,
  manifest 367967, unit harness 8/8 green.
- `needs` sentence: Josh to re-SSO the Orca browser session so the skill can be attached to
  the dev MCP server, manifest in-page+ZIP verified, live UAT run.
- The 02:09–02:16Z probing predates no registry gap — the row landed BEFORE it (23:08Z).
  The gw-semantic dashboard linkage in session-shadow is adjacent workstream context, not
  the owner; owner is `google-docs-mcp`.
- Attention-queue item #6 ("recipe 83191713 unregistered / session owes a claim row") can be
  resolved as a false positive: the closeout row covers it.

## Verdict

Recipe 83191713 is the known, ticketed, registry-covered `delete_table_of_contents` MCP tool
for the Google Docs by Workato MCP (dev), built by session gdocs-toc-delete-build under
BSYS-29800. No orphaned session, no unregistered work. Remaining open items live in the
registry row's `needs`: skill attachment to the dev MCP server + live UAT.

*Investigation artifact only — nothing else modified.*
