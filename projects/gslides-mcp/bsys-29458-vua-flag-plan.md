# BSYS-29458: List_Design_Systems VUA Required flag (dev 134817 / prod 135411)

Ticket: [BSYS-29458](https://workato.atlassian.net/browse/BSYS-29458) (Bug, Backlog, 1 point). Investigation: `knowledge/cortex/investigations/list-design-systems-vua-flag.md` (verdict FLAG WRONG, high confidence). Contract: VUA everywhere for this pipeline (Confluence Identity deep dive 2939650094).

## State as of 2026-10-12 (fresh live read-backs this pass)

- Dev: [Enhanced Google Slides by Workato MCP](https://app.workato.com/ai_hub/mcp/mcps-Ab9w3HK9-CRK-CD/overview) (`mcps-Ab9w3HK9-CRK-CD`, endpoint https://16704.apim.mcp.workato.com, 62 tools): tool 134817 List_Design_Systems reads `VUA Required: Yes`. 61/62 tools Yes; only Host_Asset (108690) is No, by design. No drift since the 2026-10-10 flip.
- Prod: [mcps-AbEdNLHX-43z-CD](https://app.workato.com/ai_hub/mcp/mcps-AbEdNLHX-43z-CD/overview) (endpoint https://17498.apim.mcp.workato.com, 62 tools): tool 135411 still reads `VUA Required: No`. 61/62 Yes; 135411 is the only No. Never touched, as planned.
- Root cause: flag never set at publish in either environment; not drift (dev server updated 2026-09-12, prod 2026-10-02).
- UI path is a dead end for this flag (verified live via Orca 2026-10-09): the Edit tool details dialog exposes only Title/Name/Status/description/annotations.

## Completed dev work (2026-10-10, verified)

Package round-trip on the dev server: exported bundle, set `vua_required: true` on tool 134817 (config key `ref_60`), imported into folder 27328084 with backing recipes 82059074 and 82864228 stopped, restarted both. Verified by fresh `mcp_server_get`, round-trip re-export (export 42194823, manifest 361034, flag persisted), gateway anonymous initialize denied, authenticated VUA call green. Rollback artifact retained: package 42194803, zip sha256 3c21fc5f700989c1b88df0d84e3cffbb9726697bd91d5c9cdf86c59a09aa5581.

## Remaining work: prod twin 135411 (PROPOSE ONLY, Josh-gated production write)

1. Export the prod bundle for `mcps-AbEdNLHX-43z-CD` (manifest create, then direct curl to `POST /api/packages/export/{manifest_id}`; the `wt packages export` arg-name bug is unfixed).
2. Set `vua_required: true` on the tool 135411 config entry in the exported JSON.
3. Import into the prod folder with backing recipes stopped, restart immediately (expect the 82059074 twin plus its guidance-append sibling in the dep chain, same as dev).
4. Read back with a fresh prod `mcp_server_get`: expect 61/62 Yes, Host_Asset twin 116237 the only No.
5. Served-surface check on https://17498.apim.mcp.workato.com: anonymous initialize must deny, authenticated VUA call must serve. Re-export post-change to confirm the flag persisted.

## Risks

- Import requires backing recipes stopped: brief prod-server tool downtime; schedule outside active use.
- clm-001: any later push touching the tool can silently revert the flag; re-read `mcp_server_get` after every push.
- Retain the pre-change prod package export with its hash as the rollback artifact.
