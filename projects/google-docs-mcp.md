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

## Open state (closeout 2026-10-14)

- Live end-to-end UAT run pending — blocked on Josh SSO in Orca browser (test doc prepped:
  https://docs.google.com/document/d/1OQM8nEUmTngbyTEuCxtln59sG9Axfnj5dXoyeoLjpr0/edit,
  fixture at ~/.claude/knowledge/fixtures/83074320.json). Then deployment-request for promotion.
- Promotion manifest (dev, id 364020): 4 recipes — 83074320, 83074561, 83074563, 83074564.


## CORRECTIONS (Josh, 2026-10-15 — after I flailed through the wrong surfaces)

- **Enterprise MCP servers live in the "MCP | BT Managed MCP" project** (prod folder 27436344:
  https://app.workato.com/recipes?fid=27436344#assets). They are NOT created from the Enterprise MCP
  UI section, NOT from a project Create menu, and AIRO `mcp_server_create` wants a folder_id in that
  managed project — "Invalid Folder" from AIRO means wrong folder, not an ACL problem.
- **Recipe → skill conversion IS an API call:** `POST /api/agentic/skills` with `{"recipe_id": <id>}`
  returns the `skl-*` handle (this is what UI "convert to skill" does). No UI needed.
- **Test-automation API is run/list ONLY** (POST /api/test_cases/run_requests,
  GET /api/test_cases/run_requests/:id, GET /api/recipes/:id/test_cases). There is NO create-test-case
  API — `POST /api/recipes/:id/test_cases` 404s (verified). First test case for a recipe = UI.
- **`wt recipes force-run` is scheduler-trigger-only** and the trigger type check follows the recipe's
  stored trigger; raw-PUT trigger swaps are IGNORED (platform keeps workato_genie). Do not attempt
  trigger-swap workarounds to fake an invocation.
- **The folders dev-API returns a BARE ARRAY** (not {items: []}) — my "no dev Managed MCP folder"
  conclusion came from a broken one-page parse. Paginate and parse defensively.
- Lesson Josh enforced: before ANY browser/UI automation for something that might be an API surface,
  CHECK THE KB + grep the API index first. The KB exists so sessions don't re-derive platform facts
  by trial and error.


## FINAL CORRECTION (Josh, 2026-10-15 — the dev twins existed all along)

- **Dev twins of all 11 MCP tools DO exist: recipes 70572934–70572944** in dev folder 29891061
  ("Google Docs by Workato MCP", project 18274956) — one id off the prod series (705728xx).
  My "no dev twin exists" conclusion was WRONG (name-search across an incompletely parsed folder list).
- **The DEV Enterprise MCP server is `mcps-AYEBCFWr-3FB-CD`** (https://4319.apim.mcp.workato.com,
  auth workato_idp, published:false) with tools bound flow_id → 70572934..70572944, vua_required true.
  Dev "MCP | BT Managed MCP" folder = 27328084. Reading tools: in-page
  `GET /web_api/mcp/servers/<handle>/tools.json` (session cookies).
- **The fix is applied to the REAL twins** (70572944 main; 70572935 create_document;
  70572940 list_mentions; 70572941 list_suggestions) — recipe must be STOPPED for PUT
  ("can't modify running recipe"), restart after. Verified live in stored code.
- My imported duplicates (83074320, 83074561/563/564) are superseded — deleted; living manifest
  now carries the real ids. Duplicate-dev-twin creation was wasted motion caused by the wrong
  "no twin" conclusion — ALWAYS check the MCP server's own tools.json flow_ids first.
- Rule Josh enforced twice this session: check the KB before UI improvisation; MCP servers live in
  the MCP | BT Managed MCP home (dev folder 27328084 / prod 27436344).
- Live verification still pending: needs one MCP-tool invocation of update_document_content against
  the test doc (Workato IDP auth on 4319.apim blocks headless session calls; any connected MCP client
  — or Josh's manual Test run — completes it).
