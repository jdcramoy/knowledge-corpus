# Frontify MCP (Workato, AHQ | AI dev)

Project repo: `~/orca/projects/frontify-mcp/` · Research: `docs/research/frontify-api-research.md`
Full introspected schema: `~/orca/projects/frontify-mcp/research/frontify-schema.json` (831 types)

## What this is
Our own Frontify MCP server in the AHQ | AI dev workspace (Josh directive 2026-10-20), covering
the full read surface of the Frontify APIs — brands, libraries, projects, assets (details,
fonts, logos, colors), guidelines, templates, workflow — recipe-backed skills over one shared
GraphQL helper recipe, reusing the existing Frontify connection.

## Verified environment facts (2026-10-20)
- Tenant: `company-181808.frontify.com`; brand "Workato"; "Workato Brand Guidelines" guideline
  id `eyJpZGVudGlmaWVyIjo0ODE2ODAsInR5cGUiOiJndWlkZWxpbmUifQ==` (~24 pages).
- API: Platform GraphQL at `https://company-181808.frontify.com/graphql`, Bearer PAT,
  `X-Frontify-Beta: enabled` header for newer regions (guideline pages, brand essentials).
- Introspection ALLOWED with token on real tenant (anonymous portal blocks it).
- Connection: `Frontify GraphQL (design tokens)` — dev conn id **22276219**, REST-type,
  lives in folder 32268816 ("Automation") under "Enhanced Google Slides by Workato MCP"
  (folder 32205279) inside project **MCP | BT Managed MCP** (project 13683566, root 27328084).
  Build MUST live in this project — connections are project-scoped.
- Token hygiene: token was flagged compromised-on-record on BSYS-29746; Josh rotates in
  console. Build against the CONNECTION, never the keychain token (keychain
  `frontify-api-token` exists, used by legacy helper `orca/projects/google-slides/frontify/fq.py`).
- Official baseline: Frontify's own hosted MCP (mcp.frontify-integrations.com) exposes 47
  tools in packs; admin pack = full catalog. Our tool list mirrors its read surface.
  KB corpus: `webcrawl/frontify--*` (6 docs, ingested 2026-10-20).

## Schema shape (live introspection 2026-10-20)
- 19 root queries: currentUser, account, project, library, workspaceProject, assets, asset,
  creativeTemplate, creativeExport, brand, brands, catalog, catalogSelection,
  guidelinePageBlock, node, guidelineNavigationItem, guidelinePage, serviceApps, webhooks
- 179 mutations (full asset/folder/collection/metadata/comment/workflow/essentials/
  guideline/catalog/brand/webhook CRUD, uploadFile, exportCreative)
- Fonts: BrandEssentialsFontFamily/FontStyle (Adobe/Google/Monotype/Selfhosted variants)
- Colors: BrandEssentialsColorPalette/Color (HEX/RGBA/HSL/CMYK/LAB representations)
- Logos: LogoLibrary type; logos also via asset search + type filter

## State
- 2026-10-20: research + schema introspection done; KB corpus deposit done; build started.

## Built (2026-10-20, dev)

**MCP server: Frontify MCP** — `mcps-Ac4Mrak4-NbK-CD` — https://33238.apim.mcp.workato.com —
https://app.workato.com/ai_hub/mcp/mcps-Ac4Mrak4-NbK-CD/overview — 21 read-only tools, published,
hashed-token auth (verify token created: claude-code-verify-2).
Probe server (1 tool, superseded, safe to delete): mcps-Ac4MM3ET-zzF-CD.

**All 21 tools gateway-verified live** (tools/list 21/21; tools/call with real args):
- PASS with real data (13): Get_Current_User, List_Brands, Get_Targets (honest 0), Get_Brand,
  List_Guidelines, Get_Guideline, Get_Guideline_Page (page id REQUIRED — guideline id rejected
  "Identifier type does not match expected type"), Search_Guideline_Content ("logo" hits),
  List_Brand_Color_Palettes, Get_Brand_Font_Families (Besley/Figtree, provider styles),
  List_Creative_Templates (honest 0), Get_Library_Page_Assets, Search_Brand_Assets (159 assets,
  term filter works), Get_Assets_Data, Read_Asset (real CDN downloadUrl via ...on Image fragment).
- Correct-behavior-on-missing-tenant-objects (4): Get_Library, Get_Project, Get_Templates_Data,
  Get_Creative_Export — clean "Invalid identifier" on fake ids; tenant has no libraries/projects/
  templates. When they exist, the tools are ready.
- Blocked by token scope (1): Get_Asset_Comments — Frontify API token has NO comments scope
  (trace x_oauth_scopes: account:read, basic:read, blocks:read, finder:read, webhook:read).
  Fix = new PAT with comment scopes + connection re-auth. NOT a code defect.

**Recipes (21, all in folder 35910254, all RUNNING):** 83230036 Get_Current_User · 83230141
Get_Brand · 83230175 List_Brands · 83230177 Get_Targets · 83230181 List_Guidelines · 83230317
Get_Guideline · 83230373 Get_Guideline_Page · 83230403 Search_Guideline_Content · 83230176
Get_Library · 83230183 Get_Project · 83230316 Search_Brand_Assets · 83230336 Get_Assets_Data ·
83230368 Read_Asset · 83230372 Get_Asset_Comments · 83230174 List_Creative_Templates · 83230310
Get_Templates_Data · 83230320 Get_Creative_Export · 83230335 Get_Library_Page_Assets · 83230354
List_Brand_Color_Palettes · 83230359 Get_Brand_Color_Palette · 83230369 Get_Brand_Font_Families.

**Manifest:** 368734 (project-level folder 27328084) — 22 rows read-back verified
(1 connection + 21 agentic_skill). Mirror: ~/orca/projects/frontify-mcp/manifests/.

## Deployment submitted (2026-10-20)

- UAT: gateway sweep 21/21 + headless client UAT 9/9 PASS (frontify-mcp-dev added to Josh's local
  Claude config for this project, hashed-token auth).
- Server published to MCP registry (was Private → Published "Visible to all users" per Josh —
  access-group Everyone for testing; proper end-user group to replace it later).
  NOTE: server UI page is at /mcp/<handle> — the /ai_hub/mcp/<handle>/overview URL from
  asset_url_get 404s in the SPA for API-created servers.
- Red-team: PASS (no fatal/material; cosmetics: step masking off, high-side limit clamps).
  Verdict: ~/.claude/knowledge/redteam/BSYS-29815-frontify-mcp.md, commented on both tickets.
- Deployment Story: BSYS-29824 (parent Epic BSYS-29823 "Frontify by Workato MCP", created —
  per jira-story-standards DRs file as STORY, never the Deployment Request type).
  Fields verified by re-read: Manifest Link 10494 = export_manifests/368734; Source 10588 =
  AI Development [3535597] / Home/MCP | BT Managed MCP (option 31161/51485); Destination 10446 =
  AI Production [3535598] / Home/MCP | BT Managed MCP (option 31164/57015). Attachments: package
  ZIP (export 42284540, 46 files, 21 recipe.json) + manifest JSON.
- Manifest fix discovered at packaging: agentic_skill rows need the SKILL platform id (348898+)
  as row id with provider_id=recipe id; the backing RECIPES ride as their own recipe rows —
  skill-only manifests export bindings without recipes (0 recipe.json in first ZIP).
- Awaiting: Josh flips BSYS-29824 to Final Tech Review (not in my transition set — reviewer gate).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Frontify MCP](projects/frontify-mcp.md) — build our own Frontify MCP in AHQ | AI dev (Josh 2026-10-20): full-surface read MCP over Platform GraphQL (tenant company-181808.frontify.com), recipe-backed skills + shared GraphQL helper, reusing conn 22276219 in project MCP | BT Managed MCP; repo ~/orca/projects/frontify-mcp/ (research + full introspected schema 831 types); official 47-tool MCP catalog mirrored in KB corpus webcrawl/frontify--*
## Full UAT complete (2026-10-26, authenticated server)

- Five phases via real MCP clients after Workato Identity auth: chained UAT 15/16, adversarial
  24-case battery (21 CLEAN, 0 hangs/crashes), fix-verify 4/4, stress w/ 2 concurrent clients
  (no 429s, repeat-identical), pagination regression 4/4.
- FIXED during testing: (1) Frontify edge WAF 403 on code-shaped search terms surfaced as opaque
  "Tool execution failed" — both search tools now have error_handling monitors returning structured
  upstream_rejected/search_failed JSON; (2) MY OWN always-truthy Ruby modifier
  `p = 1 if p > 1000 ? 1000 : p` (0 is truthy in Ruby; ternary always truthy → p always 1) silently
  killed pagination on 83230316 — corrected + regression-proven. NEVER write modifier-if with a
  ternary condition; it is not a clamp, it is an unconditional assignment.
- Documented upstream: Frontify caps brand.search limit at 50; brand.search term relevance narrow;
  contentSearch backend nulls results for some terms (color, brand).
- Red-team r2: PASS-WITH-NOTES (the pagination bug, fixed same hour, re-verified per its gate).
- Evidence comment on BSYS-29824 (id 1148496). Ready for Final Tech Review.

## Outstanding-items sweep (2026-10-26, "fix everything outstanding")

- Probe server mcps-Ac4MM3ET-zzF-CD: DELETED (web_api DELETE 200 + read-back verified, 0 found).
- Fleet: 21/21 recipes running; server published, workato_identity, Everyone group (1) bound.
- Get_Asset_Comments: still scope-blocked (retested live — "policy 'assets' not fulfilled" on
  asset.comments; asset resolves fine). ONLY fix: Josh creates a comments-scoped PAT in the
  Frontify console + re-auths connection 22276219. Tool/connection are proven healthy otherwise.
- Deliberately NOT done (reasons on record): per-tool description hardening (server-level
  instruction already carries the untrusted-content line; 19 stop/start cycles for a snapshot
  that refreshes only on tool re-save is churn), limit-hint text alignment (hints still accurate
  in practice; clamps bounded at 100), upstream Frontify bugs (their side).
- Remaining Josh-only: comments-scoped PAT; flip BSYS-29824 to Final Tech Review.
- ACCESS = EVERYONE, PERMANENT (Josh 2026-10-26): public brand content, not sensitive. Do not
  re-recommend restriction anywhere — red-team treats content exposure as a non-finding.

## Josh ruling 2026-10-26: NO token rotation for the Frontify API token
Frontify is a read-only, non-sensitive system (design guidance only) — the token never needs rotating, and rotation asks are permanently closed. Any future estate-review/rotation pass must skip it.

## Get Asset Comments DROPPED (2026-10-26, Josh verdict)

- The comment-read block is our FRONTIFY ACCOUNT TIER (no comment scopes available to us at all) —
  not a PAT rotation item. Josh: drop the tool entirely, zArchive it, no resurfacing until he says
  so or we go to a paid Frontify account.
- Done: binding 277912 deleted from server (20 tools served, client-verified); recipe 83230372
  STOPPED + moved to zArchive folder 35980951; manifest 368734 = 41 rows (1 conn + 20 skills +
  20 recipes), package export 42325972 ZIP-verified (20/20, zero comment assets).
- GOTCHA: presigned package download URLs expire in 10 SECONDS — chain get→curl in one command.
- GOTCHA: filtering manifest rows by recipe id misses agentic_skill rows (their id is the skill
  platform id; recipe id is in provider_id). Filter both.
- Server final: 20 read-only tools, Everyone access (permanent), Workato Identity.

## Manifest REBUILT the sanctioned way (2026-10-26, after Josh called out the missing mcp_server)

- Manifest of record is now **372158** (368734 destroyed — it was hand-built rows, missing the
  mcp_server asset entirely: "the one asset that defines what this project is").
- 372158: 41 rows — **1 mcp_server CHECKED (include_mcp_apps, auto-attaches bindings on import)** +
  20 agentic_skill + 20 recipe, zero Not-found rows, anchor 35910254, anchor-relative paths
  (root rows folder: ""), NO connection row (connections are deploy-time wiring — ticket text only;
  packager rejects cross-anchor connection rows).
- Export 42326966 FAILED on the connection row ("Connection ... is not found under <anchor>") —
  export 42326975 COMPLETED; ZIP: 20 recipe.json + 20 agentic_skill + frontify_mcp.mcp_server.json.
- Ticket 10494 now = export_manifests/372158; fresh package attached; description says 20 tools.
- ENFORCEMENT ADDED: manifest-guard.sh now content-checks — session created an MCP server → the
  manifest MUST carry a checked mcp_server row (in-page read-back via Orca; blocks with the
  rebuild demand). Verified both ways (block on throwaway 372159, pass on 372158).
- The presigned-URL 10s expiry + provider_id filtering gotchas are in the knowledge file above.
