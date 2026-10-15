# Google Calendar MCP — project knowledge

Created 2026-10-10 by the legacy-tree mining pass (archive:
`~/Documents/ChatGPT/Google Calendar MCP/` — a benchmark/improvement
workspace for "Google Calendar by Workato MCP").

## State (as recorded in the archive)

- Dev server `mcps-AY4EfgAW-XCJ-CD`, recipes 70265533–70265546 plus
  82241450/82241584, 17 tools. Epic BSYS-28798 / story BSYS-28799.
- Error-handling contract rolled out to all 16 audited catch branches;
  promotion scorecard GO 2026-09-12; prod smoke checklist includes the
  8,000-char description cap and `attendeesOmitted`/`descriptionTruncated`
  signals.

## Durable lessons (generalizable; details in domains/workato-platform.md)

- MCP isError gap → mandatory structured error envelope
  `{success:false, error, errorCode, retryable:false}` with per-class
  retryability and per-item fail-open for batch partials (source:
  `planning/error-handling-contract-2026-09-10.md`).
- Published schema default vs action fallback drift — schema-aware clients
  bypass a recipe's action fallback when the published trigger schema still
  declares an old default; audit both after any default change.
- Empty-string padding tax: 69% of scalars in default `list_events` output
  were empty strings; `skip` semantics on optional scalars (booleans/arrays/
  IDs directly mapped so valid `false` survives) + compact default
  projection = 10.24× cut.

## Gmail/Calendar Workato-MCP parity gaps (upstream product bugs, worth knowing)

- `trash_messages` does not remove drafts (drafts survive; no draft-delete
  on the purpose-built arm); `list_drafts` returns stubbed payloads;
  `unarchive_threads` silently no-ops on trashed threads; gmail-workato-3781
  `create_filter` advertised but unregistered ("No such tool available").
- Gmail mutations with `confirmation: intent_scoped` commit on the FIRST
  call when the caller supplies the full semantic tuple — plan/confirm
  round trips materialize only for `always`-confirm caps.

## Related (KB bridges)
