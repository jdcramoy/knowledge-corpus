# Google Docs by Workato MCP

Legacy MCP (11 recipe-backed tools) serving Google Docs editing from Claude. Lives ONLY in PROD
(folder 29890954, project "MCP | BT Managed MCP") — no dev twin existed before BSYS-29692.
To be deprecated when the GWS Semantic MCP covers Docs.

## Architecture

- Prod folder: https://app.workato.com/recipes?fid=29890954#assets (11 recipes, all running).
- Tools: update_document_content (the write path), get_document_content, get_document_info,
  find_blocks, create_document, add/reply/resolve_comment, list_comments/mentions/suggestions.
- Pattern per tool: `workato_genie` skill trigger → connector steps + `workato_custom_code` Ruby →
  adhoc HTTP `POST /v1/documents/{id}:batchUpdate` on the google_docs connection.
- The write tool's whole surface = the Ruby generator in its step-3 custom code
  (`GoogleDocsUpdateGenerator` + `GoogleDocsPayloadGenerator`). Block ids: `body/b:N/e:N` and
  `body/b:N/r:R/c:C/p:P/e:E` for table cells.

## BSYS-29692 (2026-10-14): structural deletes — root cause + fix

- **Root cause:** generator emitted only `deleteContentRange`/`insertText`/`insertTable`/
  `insertTableRow`/`createParagraphBullets`/`updateParagraphStyle`. No `deleteTableRow`,
  `deleteParagraphBullets`, `deleteTableColumn` → table rows undeletable (Richy's "Done-row"
  lifecycle), bullets unremovable (Jon's report), trailing empty bullet permanently errors on the
  document-final-newline guard.
- **Fix (dev twin 83074320, folder 35833467):** ops `delete_row`, `delete_column`, `delete_table`,
  `remove_bullets`; replace/delete on a bulleted block auto-prepends `deleteParagraphBullets`
  (bullets survive text deletion otherwise); doc-final empty bullet → bullet-strip instead of
  `NothingToDeleteError`. Guards: last row/column of a table refuses delete (use delete_table).
- API semantics verified against docs: `deleteParagraphBullets` removes bullets overlapping a range
  (nesting visually preserved via indent, no index shift); `deleteTableRow`/`deleteTableColumn` take
  `tableCellLocation{tableStartLocation{index,tabId},rowIndex,columnIndex}`.

## Audit findings (2026-10-14, subagent pass over all 11 recipes)

Shipped in BSYS-29692: create_document echo-trim (83074561), list_suggestions pagination
(83074564 — also fix key-style: options arrive string-keyed via `input.except`), list_mentions
"user"→person alias + page_no schema-name reaching Ruby (83074563 — the schema said `page_no`, the
Ruby read `input["page_number"]`: pagination silently pinned to page 1).

Deferred: add_comment + get_document_info full-doc fetch → field-masked adhoc GET (needs live-
verified pill rewiring); list_mentions entity filter originally accepted user/person/file/unknown;
new tools (search_documents, trash document) need MCP server wiring (prod import of mcp_server
members fails via API → Josh UI import).

## Environment quirks (learned 2026-10-14)

- **AIRO MCP identity lacks ACL to NEW dev projects** — `recipe_builder_pull` fails
  "Permission denied: you do not have access to the target folder or its project" for the fresh
  project while raw `wt` (Dev CLI keychain token) works. Fallback: full-recipe raw
  `PUT /api/recipes/:id` via wt — payload needs `config` and `folder_id` (stringified!) as JSON
  STRINGS; a prod-sourced folder_id 404s the PUT.
- Raw recipe create via `POST /api/recipes` 500s (shape not battle-tested) — clone+PUT of an
  existing recipe is the proven raw path.
- `wt recipes force-run` is **scheduler-trigger-only**; workato_genie skill recipes can't be
  force-run or webhook-invoked. Live test paths: Orca browser "Test recipe" (needs Josh SSO when
  session expired) or an MCP server binding (needs skl-* handle; `workato_genie` rejected at
  mcp_server_create).
- Semantic MCP `docs.documents.batchUpdate@v1` op-list caps at insert_text / delete_content_range /
  replace_all_text — can't create tables or bullets; useless for building Docs test fixtures.
- Test-probe recipe creation via the API failed; the working alternative was dogfooding the tool
  under test to build its own fixture (replace op supports heading/table/list_item blocks).

## ⚠️ GOTCHA (Josh-confirmed, 2026-10-17): STOPPED RECIPE = TOOL DISAPPEARS FROM THE MCP SERVER

- The MCP gateway serves a tool ONLY while its backing recipe is RUNNING. Stopping a twin recipe
  for any reason (Test-dialog flows, hot-swaps, maintenance) silently REMOVES that tool from the
  served tools/list — clients see a shrunken tool set with NO error anywhere.
- This caused a 90-minute false diagnosis (2026-10-16→17): three write tools "missing" → theories
  about broken bindings, stale registries, ACL quarantine — all wrong. The recipes were simply
  stopped (by me, for the Test-dialog flow) and never restarted.
- **RULE: if an MCP tool is missing from a served list, FIRST check `running` on its backing
  recipe (`wt recipes get <id>`), before any binding/server theory. And ALWAYS restart any recipe
  you stopped, same turn.**
- Restarting changes nothing else — the served tool set comes back as soon as the recipe runs.

## BSYS-29727 (2026-10-15): hyperlink fix BUILT in dev, UAT pending

- [colleague] asked Claude to insert a doc link at first mention of a feature; the MCP fell back to
  asking him to do it manually. Root cause: the generator emitted NO `updateTextStyle`/`link` —
  `insertText` is plain-text only. Ticket: https://workato.atlassian.net/browse/BSYS-29727 (3pts).
- **Fix (2026-10-15, dev twin 70572944 in folder 29891061):** ops `link_text` / `unlink_text` —
  substring+occurrence matching (occurrence 1 = first mention), emits `updateTextStyle` with
  `textStyle.link.url` + `fields: "link"`; unlink = fields "link" with link unset (verified against
  the official format-text guide). UTF-16 code-unit conversion for astral chars; http(s)-only URL
  guard; updateTextStyle shifts no indices so batch ordering is unaffected. Trigger description now
  documents link ops. 20/20 local unit tests (build/BSYS-29727/test_link_ops.rb in the repo).
- ⚠️ The REAL dev twin is **70572944** (folder 29891061, project "MCP | BT Managed MCP") — it
  carried the BSYS-29692 fixes as of 2026-10-15 02:36 even though the BSYS-29692 closeout named
  twins 83074320/83074561/83074563/83074564, which are now DELETED (404). Folder 35833467 (project
  "Google Docs by Workato MCP") is an EMPTY newer folder — don't rebuild twins there. A duplicate
  twin (83110574) was accidentally cloned from PROD code into it this session and deleted.
- Raw `POST /api/recipes` with `{name, description, code: <json-string>, config: <json-string>,
  folder_id: "<string>"}` WORKED this time (the "500s, not battle-tested" note is stale — the
  stringified config+folder_id shape is the battle test).
- Manifest 365931 (3 rows: agentic_skill 68138 + recipe 70572944 + connection 19022500), verified.
- **Red-team (independent agent): round-1 FAIL → delta PASS-WITH-NOTES** (2026-10-15, verdict file
  redteam/BSYS-29727-google-docs-mcp-link-ops.md). Round 1 caught: (1) trigger
  `parameters_schema_json` missing link fields — would have broken the feature on promotion (the
  schema, not just the description, is the calling agent's contract); (2) downcase-based
  case-insensitive matching misaligns offsets when chars expand on downcase (İ U+0130) — fixed with
  regex scan over the original string. Both fixed, delta-verified against a fresh live pull.
  LESSON: when adding ops to a genie tool recipe, update parameters_schema_json too, not just the
  description.
- **Follow-up (2026-10-16, same ticket): heading-style loss + unrepairable next to tables** (Jon
  Dart). Root causes: (1) replace on a heading block with typeless content degraded it to
  NORMAL_TEXT — fixed with `preserve_block_types!` (content blocks without "type" inherit the
  target's named style; string keys "level" — symbol keys silently no-op through process_heading's
  dig); (2) the only repair path was replace (index-shifting, feared next to tables) — fixed with
  an index-neutral `apply_style` op (updateParagraphStyle namedStyleType only, http(s)-style guard
  on values, range excludes trailing newline). Suite 34/34. PUT-4 verified. NOTE: para_element
  mocks MUST use UTF-16 endIndex (char-based mocks mask off-by-emoji bugs).
- **LIVE UAT PASSED (2026-10-17) — all via the gdocs-dev MCP gateway, zero test-dialog clicks**
  (the dialog path is retired; tools/call is the test surface). Doc 1p8TdLvO-TF1BhjnzdUAI3pgJQgmoNmcOrgqImeos9v4
  (created via MCP create_document — MCP VUA identity, self-consistent account). Verified live:
  link_text occurrence 1/2 + case-insensitive + İ-offsets + whole-block (trailing newline
  excluded), unlink, apply_style heading repair AFTER a table, replace typeless-content heading
  preservation (empty-string type — MCP schema forces type present, so "" = inherit), delete_row
  (Richy done-row) + last-row guard + batch atomicity. Visual: doc screenshot (linked second
  mention, unlinked first, one-row table, repaired heading in outline). Suite 36/36. Unit-test
  mocks must use UTF-16 endIndex.
- Minor open item: tab_id "" errors instead of defaulting to primary tab (hint promises default);
  workaround = pass t.0. Fix candidate.
- Leftover zombie: MCP server mcps-AbzMMJbD-M3Q-CD ("BSYS-29727 UAT") + 2 DCR OAuth clients
  (oaoPY3jj, gos3JdWt) from the auth experiments — UI-delete candidates, no tokens issued.
- **PROD HOTFIXED (2026-10-17, Josh: "just hotfix it"):** prod 70572893 v5→v6 via stop→PUT→start
  (10s window), read-back verified (8/8 code checks). Post-deploy smoke PASSED through the PROD
  gateway (5492.apim.mcp.workato.com, workato_idp OAuth — flow: DCR → authorize → consent →
  **"Complete connection" button** (the missing redirect hop — click it!) → token): 11 tools,
  served schema has link_url/occurrence/style, live create+link+apply_style on prod doc
  1cfKIQJFP514_PtThmtmCAAZn4nHS8mV0pnPUxzlIl78, job j-AbzMxxMC-mxNzpt-CD green. DR record: BSYS-29765.
- Open cosmetic: prod-served tool DESCRIPTION snapshot is stale (795 chars, no link ops) — served
  inputSchema is correct so calls work; refresh via the Edit-description dialog per tool.
- Zombie cleanup candidates: uat MCP server mcps-AbzMMJbD-M3Q-CD (dev), 3 DCR OAuth clients
  (oaoPY3jj/gos3JdWt/TmBh1JDp), dev UAT docs 1ZAHpHJw + 1p8TdLvO, prod smoke doc 1cfKIQJF.
- BROWSER LESSONS (2026-10-16 UAT session): the Test-recipe caret works ~once per session-state
  then dies to ALL input channels (refs, OS mouse, keyboard) — after a page RELOAD the first
  interaction usually works again. Workato enforces ONE workspace per session cookie: a second tab
  in another workspace flips the session and "Session expired — switched workspaces" popups
  ping-pong; fix = close extra tabs, click Reload, verify env switcher (env can ALSO flip to
  Production — red banner, 404s all dev assets; switch back via the top-left dropdown, items are
  button.app-menu-item needing the full pointerdown/mousedown/pointerup/mouseup/click dispatch).
  Raw-JSON view of the Test dialog is display-only (Angular model never syncs — "can't be blank" on
  submit even with valid JSON): fill the FORM view; short single-line orca type works (≤~100
  chars), ≥700-char type calls die with runtime_unavailable.

## Open state (closeout 2026-10-14)

- Live end-to-end UAT run pending — blocked on Josh SSO in Orca browser (test doc prepped:
  https://docs.google.com/document/d/1OQM8nEUmTngbyTEuCxtln59sG9Axfnj5dXoyeoLjpr0/edit,
  fixture at ~/.claude/knowledge/fixtures/83074320.json). Then deployment-request for promotion.
- Promotion manifest (dev, id 364020): 4 recipes — 83074320, 83074561, 83074563, 83074564.
