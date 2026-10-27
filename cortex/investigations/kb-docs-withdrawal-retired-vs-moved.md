# Investigation: 2026-10-26 KB corpus sync — 15 removed docs: retired vs moved

Verdict date: 2026-10-27. Method: local KB corpus queries (`~/Documents/workato-kb/.venv/bin/python -m kb.search`),
corpus grep for distinctive phrases, manifest/TOC diff vs the LIVE `docs.workato.com/llms.txt`
(fetched read-only), and content diffs old-path vs successor-path. Complements
`cortex/investigations/kb-docs-drop-2026-10-26.md` — that note's "mirror withdrawn, page live"
framing is refined here: the removed paths are ALSO gone from the LIVE llms.txt TOC (delisted
upstream), and the content moved to successor pages. See the ADDENDUM at the bottom for how
this reconciles with the earlier note.

## Per-doc verdict table (15/15 resolved)

| # | Removed corpus key | Verdict | New path (live TOC, cited docs.workato.com URL) |
|---|---|---|---|
| 1 | `en/airo/recipe-editor/create-recipes.md` | **moved** | `https://docs.workato.com/en/airo/build/recipes` — heading-for-heading identical to the old page (only H1 "Create recipes with AIRO" → "Build recipes with AIRO"); listed in live llms.txt |
| 2 | `en/airo/recipe-editor/map-fields.md` | **moved** | `https://docs.workato.com/en/recipes/copilot-in-text-mode` — "Mapper Copilot"; three unique old phrases ("compose text that incorporates datapills", "regular inputs and manipulate English text", "search and select from thousands of datapills") appear verbatim in the new doc |
| 3 | `en/airo/recipe-editor/write-formulas.md` | **moved** | `https://docs.workato.com/en/recipes/copilot-in-formula-mode` — "Formula Copilot"; "formula requirements", "tailored suggestions", "directly prompting" verbatim overlaps |
| 4 | `en/airo/recipe-editor/generate-descriptions.md` | **moved (rebranded)** | `https://docs.workato.com/en/recipes/recipe-description` — "Docs Copilot"; identical section skeleton (Prerequisites / Generate your recipe descriptions / No description present / Description present), AIRO → Docs Copilot rename |
| 5 | `en/canvas.md` | **delisted — no successor found (unresolved, retired-leaning)** | No Canvas-titled entry in the live llms.txt; HTML still serves 200 but nothing links to it; no corpus doc carries its content (When to use Canvas / Get started / Start from a template / BPMN modeling / Workato asset nodes / Canvas pages). The recipe-editor-update overhaul is the plausible reason Canvas was wound down, but no page declares itself the successor |
| 6 | `en/connectors/enterprise-context-by-workato.md` | **moved (renamed)** | `https://docs.workato.com/en/connectors/knowledge-base-by-workato` — "Knowledge base by Workato"; same-doc rename |
| 7-14 | `en/agentic/agent-studio/connectors/enterprise-context-connector/{enterprise-context-connector,actions/search-documents,actions/search-documents-advanced-filters,actions/list-documents,actions/list-documents-advanced-filters,actions/metadata-filters,actions/upsert-documents,actions/delete-document}.md` (8 docs) | **moved (renamed)** | `https://docs.workato.com/en/agentic/agent-studio/connectors/knowledge-base-connector/...` — same connector under its new name; action slugs identical (search-documents, upsert-documents, metadata-filters, …). Proof: `diff` of old vs new `search-documents.md` = 12 lines, all of them the canonical-URL header + the term substitution "enterprise context" → "knowledge base". All 8 new action docs are in the live llms.txt (8 TOC entries) |
| 15 | `en/data-orchestration/data-pipeline-recipe.md` | **moved (split into a section)** | `https://docs.workato.com/en/data-orchestration/data-pipeline-recipe/create-data-pipeline-recipe` ("Data pipelines" overview) + 78-entry child section in the live llms.txt (`concepts.md`, `configure-pipeline-sources.md`, `monitor.md`, `troubleshoot.md`, …). Old single page is gone from the TOC AND its live HTML now 404s |

## How the evidence lines up

- **Live llms.txt (2026-10-27):** all removed `.md` paths absent (0 matches), EXCEPT the
  data-pipeline children which now form the `data-pipeline-recipe/` section. Successor paths
  (`airo/build/recipes`, `recipes/copilot-in-text-mode`, `recipes/copilot-in-formula-mode`,
  `recipes/recipe-description`, `connectors/knowledge-base-by-workato`,
  `agentic/agent-studio/connectors/knowledge-base-connector/*`, `mcp/enterprise-context-mcp`,
  `recipe-editor-update/overview`) all present in the live TOC.
- **Corpus state nuance:** the 10-26 diff flagged the 15 as removed, but the local manifest
  (`~/.claude/workato-kb/manifest/docs.jsonl`) still lists all 15 URLs and the corpus files
  remain on disk (fetched 2026-10-15/20) — the removal was recorded in the diff but the 10-26
  run was `partial: true` and did not purge manifest/corpus, so the old chunks are still
  queryable locally. The "moved" successor docs listed above are present in corpus/manifest
  already (they arrived in an earlier sync).
- **Also new in the live TOC** (cluster context, not replacements per se):
  `en/mcp/enterprise-context-mcp` ("Enterprise Context MCP" — the native-MCP-server product
  surface, different structure, NOT the connector docs' new home — the connector docs' home is
  knowledge-base-connector) and `en/recipe-editor-update/overview` ("Workato recipe editor
  update" — new learning section for the recipe editor overhaul).

## Bottom line

**14 of 15 removed docs MOVED** to successor paths, via two upstream renames/restructures:
(1) AIRO-editor features → "Copilot" pages (`recipes/copilot-in-text-mode`,
`recipes/copilot-in-formula-mode`, `recipes/recipe-description`, plus `airo/build/recipes`
for the create-recipes flow), and (2) enterprise-context-connector → knowledge-base-connector
(9 docs total: 8 action/connector pages + the connectors/ landing page).
**1 of 15 (`en/canvas.md`) is delisted upstream with no declared successor — unresolved
(retired-leaning)**: the page still serves 200 but no TOC entry, no redirect, and no corpus
doc carries its content. The lone page whose live HTML is really gone is
data-pipeline-recipe.md — which is also the one that provably SPLIT into a section, so its
removal was correct behavior.

## Addendum (2026-10-27) — reconciling with kb-docs-drop-2026-10-26.md

The 10-26 note concluded "14 live pages dropped by a mirror-withdrawal sync bug" based on
curl probes on 2026-10-26. This investigation's live llms.txt diff (2026-10-27) shows the
same 14 paths are ALSO absent from upstream's TOC — so the corpus removal matched a genuine
upstream delisting, not a sync bug. The two notes are compatible: the HTML pages still serving
200 are orphaned pages upstream has not yet taken down, while the TOC and mirror `.md` URLs
were both withdrawn. The sync behaved correctly; the "recommended sync repair" in the 10-26
note (HTML-fallback on `.md` 404) remains a reasonable robustness improvement, but the
removal itself was not erroneous.
