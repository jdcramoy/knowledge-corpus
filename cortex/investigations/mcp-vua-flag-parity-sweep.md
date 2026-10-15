# Investigation: MCP VUA-flag parity sweep — is the List_Design_Systems divergence a class?

**Date:** 2026-10-09
**Dispatch:** one-job bounded READ-ONLY sweep (cortex dispatch log `dispatch-20261008-201939-vuaparity.log`)
**Question:** the `List_Design_Systems` VUA-Required=No divergence on the Enhanced Google Slides server (prior investigation: `list-design-systems-vua-flag.md`) — is it a one-off or a class across the estate?
**Method:** all reads via the DEV AIRO MCP server (`mcp__workato-airo-mcp-server`), `mcp_server_get` per handle, live 2026-10-09. No browser, no prod servers, no mutations.
**Enumeration path:** no `mcp_server_list` exists on AIRO and the Developer API has no MCP-server list endpoint (`GET /api/mcp_servers` variants -> 404). Enumerated via `mcps-` handles recorded in `~/.claude/knowledge/` (6 unique handles found) plus the connected-server port map from the session's MCP health check.

## Per-server verdicts

| Server (handle) | Project / role | Tool count | Divergent tools | Verdict |
|---|---|---|---|---|
| `mcps-AYbrRaxY-dhF-CD` — Workday End-User, [overview](https://app.workato.com/ai_hub/mcp/mcps-AYbrRaxY-dhF-CD/overview) | Workday self-service (identity-adjacent: elections, timesheet, inbox, PTO) | 25 | **None** — 25/25 VUA Yes (incl. inactive `get_my_time_off_balances` 130656, still Yes) | Clean — no divergence |
| `mcps-AbYzPeKh-QHG-CD` — Google Workspace Semantic, [overview](https://app.workato.com/ai_hub/mcp/mcps-AbYzPeKh-QHG-CD/overview) | Caller-scoped Gmail/Drive/Calendar/Docs/Sheets/Slides semantic layer | 3 | `workspace_capabilities` (157771) + `workspace_policy_lookup` (157776) = No vs `google_workspace` (160862) Yes — **documented as by-design** (content-free metadata, never touch caller data; clm-001 reverify §2) | Clean — intentional split, not a defect |
| `mcps-AbrGbzWN-3Af-CD` — HR Genie Intelligence (Dev), [overview](https://app.workato.com/ai_hub/mcp/mcps-AbrGbzWN-3Af-CD/overview) | Pseudonymous telemetry aggregates (not caller-scoped) | 3 | **None** — 3/3 VUA No, uniform; auth type is `hashed_token`, not `workato_idp`, so VUA is not this server's transport at all | Clean — uniform, appropriate |
| `mcps-Ab9w3HK9-CRK-CD` — Enhanced Google Slides (dev), [overview](https://app.workato.com/ai_hub/mcp/mcps-Ab9w3HK9-CRK-CD/overview) | Google Slides authoring incl. design-system pipeline | 62 | **`List_Design_Systems` (134817) = No** vs its family siblings all Yes (`Extract_Design_System` 130667, `Recommend_Design_Archetypes` 130668, `Create_Presentation_From_Design_System` 130669, `Get_Design_System_Guidance` 160762). `Host_Asset` (108690) = No is the other flag, but it is FileStorage staging — no caller Google identity involved — and matches the same "no-identity-needed staging/metadata" pattern the Semantic server documents as intentional | **The divergence exists, and it is a one-off** |
| `mcps-AbR6YwoM-JX8-CD` — Event Process MCP | Event-process pipeline (recorded with prod property work in `projects/event-process-mcp.md`) | n/a | n/a | **Insufficient access** — HTTP 404 from the DEV server (prod-resident handle; consistent with clm-001's workspace-routing note). Out of bounds for this no-prod dispatch |
| `mcps-AbEdNLHX-43z-CD` — Enhanced Google Slides (prod twin) | prod | n/a | n/a | **Out of scope by constraint** (no prod servers). Prior investigation already covered it live from prod: identical split, 60/62 Yes |

## Answer: one-off, not a class

Across every dev-resolvable Workato MCP server asset (4 of 6 known handles read live this session):

1. **The only sibling-against-family VUA divergence in the estate is `List_Design_Systems` itself.** Its design-system family is otherwise uniformly VUA-Yes, and no other server shows a family member splitting against siblings on an identity-sensitive tool.
2. **Every other VUA-No flag observed is either (a) whole-server uniform** (HR Genie telemetry, `hashed_token` auth — VUA isn't in play) **or (b) a documented by-design metadata/staging exception** (`workspace_capabilities`/`workspace_policy_lookup`; `Host_Asset`). That is the recurring *intentional* pattern: tools that never resolve caller-scoped data ride VUA-No.
3. Which sharpens the original finding rather than softening it: `List_Design_Systems` does not fit the estate's intentional-No pattern (its own description promises caller-scoped registry rows + a live caller access check), while `Host_Asset` does. One tool, one wrong flag — a typo-class defect, not a systemic flagging failure.

## Coverage gaps (not verified live)

- **No enumeration API**: discovery relied on handles recorded in knowledge files; a dev-workspace MCP server with no recorded `mcps-` handle would be missed. The connected-server health check names two more Workato-hosted MCP endpoints with no recorded handle: `gmail-mcp-v3-custom` (18764.apim, recipe-backed workspace server per `projects/otto.md`) and `slack-workato` (17731.apim) — their VUA flag parity is **unverified** (no handle -> no `mcp_server_get` possible from available tools).
- `mcps-AbR6YwoM-JX8-CD` (event-process) and the prod Slides twin: prod-resident, deliberately not read.
- No tool was invoked; this is config-surface evidence only (consistent with the prior investigation's "harm unexercised" caveat).

**Recommendation unchanged from the prior investigation:** flip `List_Design_Systems` to VUA Required: Yes on dev `mcps-Ab9w3HK9-CRK-CD` (and prod twin, Josh-gated), or — if pre-VUA discovery is intended — rewrite the tool description to stop promising caller-scoped access and document the exception. Sweep confirms this is the sole instance needing that decision.
