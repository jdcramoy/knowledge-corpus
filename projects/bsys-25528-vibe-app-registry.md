# BSYS-25528 — Vibe-coded application registry

Epic: BT EA central registry of vibe-coded apps (name, owner, platform, risk tier, sharing scope, dates, gate status, source links). Sibling of BSYS-25527 (risk-tier classification, same AIAR project). Plan = Josh's technical-plan comment on the ticket (2026-10-09). Built in dev 2026-10-10 via AIRO MCP (session `bsys-25528`), promotion handoff posted as Jira comment 1134815.
Updated plan posted 2026-10-11 (Jira comment 1134965): last mile only, points 2 remaining. Data-table query route 404'd that day, so registry row count and endpoint activation state remain unverified.

## Assets (dev, AIAR project 16361491 / folder 31391241)

- Data table `Vibe-Coded App Registry` — numeric 158543, UUID 9a08e8dc-57fa-4ea3-baa8-1a0579d73489. 10 string/date columns; record-ID field: 11fbe9a6_a16d_4d7e_86ea_afe42ec03005.
- Data table `Vibe-Coded App Registry Snapshots` — numeric 158544, UUID db80ccfb-0b98-4f94-b452-8655e3e7ba2f.
- API recipe `Vibe-Coded App Registry | Register App` — 82959481, running. API collection 1409691 "Vibe-Coded App Registry API" v1, endpoint 24083332 `POST /v1/register-app` (INACTIVE — activation + client access are UI-only, still pending).
- Workflow recipe `Vibe-Coded App Registry | Monthly Snapshot` — 82959477, running, monthly 1st 6:00 AM, force-run verified.
- Skill `Vibe-Coded App Registry | Search Apps` — skl-AbsoK8JA-XFHMkA-CD (recipe 82959490). Returns count + all rows; caller filters. Attach-ready for MCP server 5953 "Internal AI Directory by Workato MCP" (attach is UI-only — AIRO mcp_server surface is create/get, no update).

## Verified (live, dev)

- Job j-AbsoFREM-xL4TWp-CD: snapshot force-run, empty registry, succeeded.
- Job j-AbsoJ3pk-XxFTHB-CD: snapshot force-run copied seeded UAT row (registry record 98db7936-9c6f-482f-8010-26189f611d5a) → snapshot record e6508935-b8b2-4743-a0d6-37b105ba83f3; durable readback via records API.

## Remaining before promotion

1. UI: activate `register-app` endpoint + grant client access (access profile + token) → one live POST for UAT evidence.
2. UI: attach skl-AbsoK8JA-XFHMkA-CD to MCP server 5953.
3. Baseline inventory import from BT EA's list (registry holds only the UAT probe row).
4. One-page self-registration guide; re-run snapshot after baseline import.

## Lessons (durable, platform-level)

- **Workflow Apps is NOT on the AHQ|AI dev plan** (Tools → "Upgrade your plan"; project Create menu has no App entry). The "data table form with no-auth self-serve URL" pattern is unavailable there — plan accordingly; fallback = API-recipe REST registration endpoint.
- **API platform fully scriptable via `wt api`**: `POST /api/api_collections` ({"name","version","project_id" as STRING}); `POST /api/api_collections/<id>/api_endpoints` ({"name","method","path","flow_id"=recipe id}) creates endpoints; but endpoint **activation** (active:true) is ignored via PUT/PATCH and `POST /api/api_endpoints/enable` 404s — activation is UI-only. `POST /api/api_access_profiles` 404s on every payload shape — access profiles UI-only.
- **`wt recipes force-run` only supports scheduler triggers** (API/webhook triggers 422 "On-demand runs are only supported for recipes with the Workato Scheduler trigger"). API-recipe verification without gateway access = fixture/test-case route (UI) or gateway activation.
- `wt fixture` (~/.claude/knowledge/fixtures/<recipe>.json) is the browser-free verification harness: kinds webhook/api/force-run, --expect assertions, catches the new job and asserts its output.
- Data-table picklists: `table_id` accepts the numeric id directly; record fields materialize as `parameters.<hash_underscored>` only after table_id is set.
- Orca browser session was heavily contested during this build (stale tab redirects, "Session expired", eval reading wrong tab) — UI-only steps were deferred to handoff rather than fought; time-box browser work and prefer `wt` paths first.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - projects/bsys-25528-vibe-app-registry.md — BSYS-25528 BUILT in dev 2026-10-10 (registry + snapshots tables, Register App API recipe + collection/endpoint, Monthly Snapshot recipe 82959477 running, Search Apps skill skl-AbsoK8JA-XFHMkA-CD attach-ready for MCP server 5953; snapshot verified live j-AbsoJ3pk-XxFTHB-CD; remaining: UI endpoint activation + MCP attach + BT EA baseline import; Workflow Apps NOT on AHQ|AI plan — API-recipe registration is the fallback)