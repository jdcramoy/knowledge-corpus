# Investigation: Google Docs by Workato MCP — bullet & table deletion failures

- **Date:** 2026-10-14 (headless cortex investigation session)
- **Trigger:** Two independent user reports — (a) [colleague]: deleting bullets via
  `deleteParagraphBullets` errors/wrong behavior; (b) [colleague]: removing a
  table row errors/wrong behavior. Fix session importing package BSYS-29692
  (gdocs-mcp) into Workato folder 35833467 is running concurrently.
- **Scope:** Read-only. This file is the only artifact touched. No Workato assets,
  no Jira writes, no Slack.

---

## 1. Google Docs API `batchUpdate` semantics for the two operations

### Shared batch semantics

- All edits go through `documents.batchUpdate`. Requests are applied **sequentially,
  in order**, and the batch is **atomic all-or-nothing**: "Each `request` is validated
  before being applied. If any request is not valid, then the entire request will fail
  and nothing will be applied." There is no partial application.
  [docs: rest/v1/documents/batchUpdate]
- **Indexes shift after every mutating request in the batch.** "Each insertion
  increments all the higher-numbered indexes by the size of the inserted text. As with
  insertions, deleting text alters the indexes of all the text that follows in the
  segment." Indexes captured from a `get` (or computed from the pre-batch document)
  are stale after the first mutating request. Later requests in the same batch must be
  offset against the post-mutation state. [zapier/connectors google-docs-api-gotchas]
- Optional `requiredRevisionId` / `targetRevisionId` guards return **400** when the
  referenced revision is stale; concurrent collaborator edits can shift indexes
  between read and write even in a single-request batch. [docs: batchUpdate]

### `deleteParagraphBullets`

- Takes a `Range` (startIndex, endIndex, tabId). **Deletes ALL bullets that overlap
  the range, regardless of nesting level** — not "one bullet." A range that grazes
  more paragraphs than the user intended removes more bullets than the user asked
  for, with HTTP 200. [docs: how-tos/lists]
- It removes the **bullet markers, not the text or the paragraphs**. Nesting is
  "visually preserved by adding indent to the start of the corresponding paragraph" —
  that indentation insertion **shifts subsequent indexes** in the segment, exactly
  like `createParagraphBullets`' leading-tab removal "may change the indexes of parts
  of the text." [docs: rest/v1/documents/request#DeleteParagraphBulletsRequest]
- **Error shapes:** 400 bad request when the range would produce an invalid document
  structure (documented classes: deleting the last newline of a Body/Header/Footer/
  Footnote/TableCell/TableOfContents; deleting the start/end of a Table without
  deleting the whole element; deleting the newline before a Table/SectionBreak;
  surrogate-pair splits; **"deleting individual rows or cells of a table"** via
  content-range). No documented 4xx for a range with zero bullets — an overlapping
  range with no list content is a no-op, not an error, per the reference text.
  [docs: rest/v1/documents/request, concepts/rules-behavior]

### `deleteTableRow`

- Takes a `TableCellLocation`: `{tableStartLocation: Location(index, tabId),
  rowIndex (zero-based), columnIndex (zero-based)}`. Deletes the row that the
  referenced cell spans.
  [docs: rest/v1/documents/request#DeleteTableRowRequest, #TableCellLocation]
- **Merged cells:** "If this is a merged cell that spans multiple rows, ALL rows that
  the cell spans will be deleted" — one request can legally delete several rows.
  [same]
- **Empty-table rule:** "If no rows remain in the table after this deletion, the
  whole table is deleted." Deleting the last remaining row silently destroys the
  table with HTTP 200.
- **Error shapes:** the classic 400 is
  `Invalid requests[0].deleteTableRow: Invalid table start location. Must specify the
  start index of the table.` — thrown when `tableStartLocation` does not exactly match
  the table's `startIndex` in the CURRENT revision. Stale reads, index drift from
  earlier batch requests, or multi-tab documents without `tabId` all produce this.
  [SO 61493437; issuetracker 158124540]
- A row index past the table's bounds or an out-of-document `tableStartLocation`
  yields a 400 validation error before anything is applied (batch is atomic).

## 2. Do the reported failures match Docs-API semantics or a connector defect?

Raw error traces for the two reports were NOT available to this session (read-only
scope; no job traces or request bodies pulled). So this is a hypothesis ranking, not
an adjudication — **the fix session must capture the actual `batchUpdate` request JSON
and response from a failed job trace before finalizing the fix.**

The two API-semantics behaviors that most plausibly LOOK like connector bugs to end
users, with HTTP 200 and no error:

- Bullets ([colleague]): (a) range overlap deletes MORE bullets than intended (all
  nesting levels in range); (b) post-delete indentation shifts indexes; (c) bullets
  removed but text retained — a user expecting the line to disappear calls it wrong.
- Table row ([colleague]): (a) merged-cell span deletes multiple rows; (b) deleting
  the last content row deletes the ENTIRE table; (c) zero-based `rowIndex` vs a human
  counting from one — passing "row 2" as index 2 deletes the third row, silently.

The failure modes that indicate a genuine CONNECTOR defect in gdocs-mcp (what the
BSYS-29692 session should grep the connector code for):

1. **Stale single-read index model** — one `get` at the start, then multiple
   delete/insert requests built from pre-batch indexes without recomputing offsets.
   Classic symptom: the FIRST request in a batch succeeds, later ones 400 with
   "Invalid table start location" or hit a different element.
2. **Missing revision/staleness guard** — the Slides MCP equivalent carries
   `expected_revision_id` + dry-run + re-read-and-rebuild-on-conflict (see §3). If the
   Docs MCP has no revision guard, concurrent edits produce wrong-target deletes.
3. **Row-removal emulated via `deleteContentRange`** — the API hard-400s content-range
   deletions of individual rows/cells ("Deleting individual rows or cells of a table"
   is an explicitly invalid delete class). If any code path tries to remove a row by
   deleting its content range, every attempt fails. [concepts/rules-behavior]
4. **Missing/incorrect `tabId` propagation** — multi-tab docs default to the first
   tab; an index valid on tab 1 but applied to tab 1 while the user meant tab N gives
   400 or wrong-target edits. [rest/v1/documents/request#Location]
5. **No guard on the whole-table-deletion boundary** — silently nuking a table when
   the last row is removed may be "correct" per API but needs surfacing to the caller.

**Verdict:** both reports are consistent with EITHER semantics or defect; the
discriminating signal is status code. A 200 with too-large/wrong scope of deletion
points at semantics (overlap rule, merged spans, whole-table rule, zero-based
indexing) or an off-by-one/stale-index defect. A 400 — especially "Invalid table
start location" — points at stale-index or tab-handling defects. Without traces the
leading connector-defect hypotheses are (1) and (3).

## 3. Known traps in google-slides-mcp-playbook / local KB corpora

- `~/.claude/skills/google-slides-mcp-playbook/SKILL.md` (Slides
  server, but the deletion doctrine transfers directly):
  - "Bulk-delete slides with Batch_Update, not one-at-a-time Delete_Slide": fresh
    `Get_Presentation` for revision_id + element ids immediately before the delete;
    build requests from THAT read; **dry_run first**; call for real with
    `allow_destructive=true` and `expected_revision_id`; **on revision conflict,
    re-read and rebuild the batch — don't blindly resubmit the stale request.**
  - Deletion ordered LAST: replacement content built and visually verified before any
    destructive action, so there's never a half-deleted window.
  - "Google Slides API 429 rate limiting under bulk calls": rapid-fire mutation calls
    trip write-quota 429s; back off 60-90s wall clock, don't tight-loop retry.
  - The Slides MCP's revision-guard + dry-run pattern is the explicit mitigation for
    the index-shift/stale-read class. **If gdocs-mcp lacks an equivalent, that is the
    gap BSYS-29692 should close** (fresh-read-before-delete, offset recompute across
    batch requests, revision conflict → rebuild, not retry).
- Local KB corpus gap: `workato-kb/corpus/docs/en/mcp/prebuilt-mcps/google-docs-mcp-server.md`
  exists but its frontmatter URL and body are actually the Google **Drive** MCP doc
  (trash_item/restore_item semantics only) — the corpus carries **no documented
  semantics for Docs MCP paragraph-bullet or table-row deletion tools**, and grep for
  `deleteTableRow`/`deleteParagraphBullets` across the corpus hits only irrelevant
  Camel/Slack/duckdb files. No local prior art beyond the slides playbook.
- (Two queries to mcp__workato-kb__kb_search and brain_search were permission-denied
  in this session; local-corpus reads were used instead. No gap in coverage expected,
  but the KB RAG index itself wasn't re-queried.)

## 4. One test case for the BSYS-29692 fix session (proves BOTH reports closed)

**Test: `delete-both-in-one-batch`** — one test doc, one connector flow, assertions
cover both reports:

- **Setup:** create a test doc containing (a) a 4-item bulleted list with one nested
  (level-2) item, and (b) a 4-row table (header + 3 data rows), positioned AFTER the
  list so the table's startIndex is affected by bullet-marker removal.
- **Act:** in ONE `batchUpdate` through the gdocs-mcp connector: (1)
  `deleteParagraphBullets` on a range covering ONLY bullet item 2; (2) `deleteTableRow`
  for data row 2, with `tableStartLocation` recomputed AFTER request (1)'s index shift
  and a correct zero-based `rowIndex`.
- **Pass criteria (all must hold, verified by a FRESH `get` + visual/doc readback):**
  1. Bullet item 2's marker gone; its text retained; indentation visually preserved;
     the other three bullets intact — proves the [colleague] report closed (no
     over-deletion, no error).
  2. Exactly one table row removed — the SECOND data row; header and other rows'
     content unchanged; table still present — proves the [colleague] report closed
     (correct target, no whole-table deletion, no 400).
  3. Request (2) succeeded inside the same batch despite request (1) shifting indexes
     — proves the connector recomputes offsets mid-batch rather than using a stale
     single-read index model (the leading defect hypothesis).
  4. No retry masked a first failure: single call, single response, 200.
- **Negative probe (same test, second run):** attempt `deleteTableRow` on a table
  with only one content row → assert the connector either surfaces a clean error or
  explicitly reports the whole-table consequence — never a silent wrong result.

## What was NOT verified

- The actual error text/traces from [colleague]'s and [colleague]'s sessions (not
  available in this read-only scope) — §2 attribution is hypothesis-ranked, not
  adjudicated.
- The BSYS-29692 package contents and the gdocs-mcp connector source (not read).
- The current import state of BSYS-29692 into folder 35833467 (concurrent session).
- mcp__workato-kb__kb_search / brain_search were permission-denied here; KB RAG
  coverage beyond the local corpus files was not re-checked.

### Citations

- https://developers.google.com/workspace/docs/api/how-tos/lists
- https://developers.google.com/workspace/docs/api/how-tos/tables
- https://developers.google.com/workspace/docs/api/concepts/rules-behavior
- https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate
- https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/request
  (#DeleteParagraphBulletsRequest, #DeleteTableRowRequest, #TableCellLocation, #Location)
- https://stackoverflow.com/questions/61493437/cannot-delete-row-in-table-by-google-docs-api
- https://issuetracker.google.com/issues/158124540 (via SO 61493437)
- https://github.com/zapier/connectors/blob/main/apps/google-docs/references/google-docs-api-gotchas.md
- Local: ~/.claude/skills/google-slides-mcp-playbook/SKILL.md
- Local: ~/.claude/workato-kb/corpus/docs/en/mcp/prebuilt-mcps/google-docs-mcp-server.md
