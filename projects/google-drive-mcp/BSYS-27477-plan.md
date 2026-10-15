# BSYS-27477 — Native-file content refresh (Drive MCP)

Ticket: https://workato.atlassian.net/browse/BSYS-27477
Parent epic: BSYS-27191 Google Drive by Workato MCP Enhancements (Closed).
Status 2026-10-11 re-triage: built in the canonical connector repo (2026-10-10), nothing saved to Workato, awaiting Josh's release decision.
Jira: plan comment 1134654 (2026-10-09), build update 1134810 (2026-10-10), re-triage 1134968 (2026-10-11). Points 5 set (raised from the plan's 3, already on the ticket). Deduped on 2026-10-11 evening pass, no repost.

## The ask

Refresh a Google-native Doc/Sheet/Slide's content in place from a convertible source, preserving fileId, link, name, location, and shares. The ticket proposed convert-on-import via `files.update`; that mechanism is dead.

## Key finding (verdict stands)

Drive API v3 does not support convert-on-update. `files.update` with a media body stores a blob; there is no conversion parameter. Workato connector's Feb 2025 conversion feature is Upload/Export-side only (KB: product2.workato.com/platform-connector-releases-in-february-2025). Create-side conversion confirmed live in upload_file recipe 74060461 (convert_to -> targetMimeType): https://app.workato.com/recipes/74060461

## Current estate state (live, 2026-10-11)

- Sibling action `update_native_file_content` exists in the canonical connector source: `~/Documents/ChatGPT/Google Workspace MCP/connector/google_drive_mcp/connector.rb` (line 105). Docs -> `documents.batchUpdate` (clear + re-insert), Sheets -> `values.clear` + `values.update`, Slides documented as covered by the GSlides MCP.
- Guards kept: `NO_CONTENT_PROVIDED`, `NOT_A_NATIVE_FILE` (routes blobs back to `update_file_content`), `UNROUTABLE_NATIVE_TYPE` (e.g. Drawings) with the v1-style clear error.
- 12/12 connector specs green (WebMock-stubbed request-stream assertions); sibling gateway suite 48/48.
- Live media-PUT spike script staged: `scripts/spike-bsys-27477-convert-on-update.sh` (throwaway self-trashing Doc); blocked on an interactive Google consent (keychain VUA token rotated; needs `gcloud auth login` for the drive scope). Documentary verdict holds meanwhile.
- No Workato asset touched. Nothing saved or released.

## Remaining plan

- [ ] Josh's release decision: save the connector as a custom connector in dev, then wire via the MCP recipe layer (path documented in the connector README)
- [ ] Optional: run the convert-on-update spike once consent is available, converting the documentary verdict into a live one
- [ ] UAT: editor test jobs against a real Doc and a real Sheet (before/after content read-back, fileId and permissions unchanged, guard error on an unsupported type)

## Risks

- Docs API batchUpdate payloads are structured, so the HTML -> Docs-request conversion is the main build cost (already sunk in the repo); v1 scope is simple documents (headings, paragraphs, lists).
- Per-file rate limits on Docs/Sheets APIs; a regeneration loop needs backoff.

## UAT Evidence

Pending release. Expected: editor test job traces on the new action against a real Doc and a real Sheet, before/after content read-back, fileId/permissions unchanged, guard error for an unsupported type.

Points: 3 (build done in repo; remaining is release wiring plus UAT).

Not verified: nothing has run against a real Google Doc or Sheet; batchUpdate behavior is proven by specs against stubbed HTTP only.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato connectors - Google Drive - Export file action](../../../kb-corpus/docs/en/connectors/google-drive/action-export-file.md)
- [Workato connectors - Google Drive - Search files or folders action](../../../kb-corpus/docs/en/connectors/google-drive/action-search-files.md)
- [Workato connectors - Box - Upload file using file URL](../../../kb-corpus/docs/en/box/action-upload-file-url.md)
- [Platform Connectors – May 2026](../../../kb-corpus/changelog/platform-connectors-may-2026.md)
<!-- kb-bridges:end -->
