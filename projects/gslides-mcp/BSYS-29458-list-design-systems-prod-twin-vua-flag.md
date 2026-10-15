# BSYS-29458: List_Design_Systems VUA flag — prod twin flip plan (dev done, verified holding)

Ticket: [BSYS-29458](https://workato.atlassian.net/browse/BSYS-29458) (Backlog, Medium, labels V2MOM-FY27 / gslides-mcp / security / vua). Parent epic BSYS-29417 GSlides MCP Design System Extractor.

## The ask

The dev-side flag flip is done and verified. What remains is the prod twin, which is a production write and stays Josh-gated. This plan records the live state and the exact prod path.

## Current state (fresh read-backs, 2026-10-11)

- Dev: [Enhanced Google Slides by Workato MCP](https://app.workato.com/ai_hub/mcp/mcps-Ab9w3HK9-CRK-CD/overview) (`mcps-Ab9w3HK9-CRK-CD`, endpoint https://16704.apim.mcp.workato.com, 62 tools): tool 134817 `List_Design_Systems` reads `VUA Required: Yes`. 61/62 tools Yes; the only No is `Host_Asset` (108690), by design. No drift since the 2026-10-10 flip.
- Prod: [mcps-AbEdNLHX-43z-CD](https://app.workato.com/ai_hub/mcp/mcps-AbEdNLHX-43z-CD/overview) (endpoint https://17498.apim.mcp.workato.com, 62 tools): tool 135411 `List_Design_Systems` still reads `VUA Required: No`. 61/62 Yes; 135411 is the only No. As planned, the twin was never touched.
- Dev flip verification basis (2026-10-10 build comment): round-trip re-export (export 42194823, manifest 361034) shows `ref_60` / `vua_required: true` persisted; backing recipe [82059074](https://app.workato.com/recipes/82059074) verified running post-import; dev rollback artifact retained (package 42194803).

## Root cause

The flag was never set at publish, in either environment; it is not drift (dev server last updated 2026-09-12, prod 2026-10-02, and the identical 61/62 split in both predates the dev fix). The documented contract is VUA everywhere for this pipeline; the tool's own description promises caller scope plus a live access check, both unreachable without caller identity.

## Proposed fix (prod, Josh-gated)

Same package round-trip that worked on dev, run against the prod workspace:

1. Export the prod bundle for `mcps-AbEdNLHX-43z-CD` (via manifest create + direct curl to `POST /api/packages/export/{manifest_id}`, since the `wt packages export` arg-name bug is unfixed).
2. Set `vua_required: true` on the tool 135411 config entry in the exported JSON.
3. Import into the prod folder with backing recipes stopped, then restart immediately (expect the 82059074 twin plus its guidance-append sibling in the dep chain, same as dev).
4. Read back with a fresh prod `mcp_server_get` (expect 62/62 Yes, `Host_Asset` twin 116237 the only No, by design) and a served-surface check on https://17498.apim.mcp.workato.com (anonymous initialize must deny, authenticated VUA call must serve).
5. Re-export post-change and confirm the flag persisted in the served config store.

Requires explicit production confirmation before any step runs. Treat any ambiguity about the target workspace as dev and stop.

## Rollback posture and risks

- Retain the pre-change prod package export with its hash; re-import restores prior state; verify with a fresh `mcp_server_get`.
- Import requires the backing recipes stopped: brief prod-server tool downtime, so schedule outside active use.
- clm-001: any later push touching the tool can silently revert the flag, so re-read `mcp_server_get` after every push (standing rule).

## Story points

1 (the dev flip was proven end to end; this is the same path on the twin).

## Acceptance criteria

- [x] Dev tool 134817 reads `VUA Required: Yes` in a fresh `mcp_server_get` (re-verified 2026-10-11)
- [x] Served surface confirmed on dev: gateway auth-enforced, live VUA call green, flag persisted on re-export (2026-10-10)
- [ ] Prod twin 135411 reads `VUA Required: Yes` in a fresh prod `mcp_server_get`
- [ ] Prod served-surface check (anonymous deny, authenticated VUA call green)
- [ ] Pre-change prod package export retained as the rollback artifact

## UAT Evidence

Record: fresh prod `mcp_server_get` read-back showing 61/62 tools VUA Yes with `Host_Asset` (116237) the only No, the prod served-surface citations, and pre/post export hashes. Nothing recorded until Josh authorizes the prod write.
