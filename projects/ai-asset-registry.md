# AI-Asset-Registry (Workato-All/AI-Asset-Registry)

Workato's internal marketplace for Claude and Codex plugins — source of truth, install source, and discovery layer in one repo. Private org repo: https://github.com/Workato-All/AI-Asset-Registry (workato org family; clone via `gh repo clone Workato-All/AI-Asset-Registry`).

## Convention (verified 2026-10-20, PR #13)

- Paired org assets: `org/<name>-claude` and `org/<name>-chatgpt` under `org/`; team-scoped plugins under `plugins/<team>/<name>`.
- **Claude package**: `.claude-plugin/plugin.json` (schemastore claude-code manifest) + `skills/<skill-name>/` + `metadata.yaml` (`platform: claude`) + README.
- **ChatGPT/Codex package**: `.codex-plugin/plugin.json` (with `interface` block: displayName, capabilities, defaultPrompt, brandColor) + `skills/<skill-name>/` + optional `agents/openai.yaml` inside the skill (interface + `allow_implicit_invocation`) + `metadata.yaml` (`platform: chatgpt`, `support_email`, `status: production-ready`).
- `.app.json` only when the plugin binds an Apps SDK MCP app (by `asdk_app_...` id). Pure-content plugins omit it and omit `.mcp.json` (not the org-wide ChatGPT distribution path).
- **Both marketplaces must be updated**: `.claude-plugin/marketplace.json` (Claude) and `.agents/plugins/marketplace.json` (Codex, uses `source: {source: "local", path: ...}` + policy blocks).
- Install (Claude): `/plugin marketplace add Workato-All/AI-Asset-Registry` → `/plugin install <name>@ai-plugins-workato`.
- Managed rollout via `extraKnownMarketplaces` + `enabledPlugins` in org managed settings; ChatGPT rollout via Admin > Plugins > Import marketplace (policy fields from the marketplace file are NOT applied — set in ChatGPT after import).
- Commits go through PRs to main (squash, `#N` in title). Author field: Workato Business Technology, bt@workato.com.

## First asset added this pattern

`official-workato-brand-guidelines-claude` / `-chatgpt` (2026-10-20, PR #13): 2026 Workato brand skill (tokens.css/tokens.json/wk- component CSS/design-system.json), triggers on decks, HTML, PDFs, docs, keynotes, PPTX, slides, dashboards, emails, components. Source bundle: ~/Downloads/workato-brand-2026.skill.
