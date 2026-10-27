# Investigation: Workato KB nightly-sync doc drop — 2026-10-26

## Verdict (one line)

**Mixed: 14 of 15 removed docs are still live on docs.workato.com — the sync dropped them
because upstream WITHDREW their `.md` markdown-mirror endpoints while the HTML pages remain
200 (sync bug-by-consequence → needs a sync repair). 1 of 15 (`data-orchestration/data-pipeline-recipe.md`)
is a genuine upstream deletion → its removal was correct, no fix.**

## Scope & method

- Diff source: `~/.claude/workato-kb/diffs/2026-10-26.json` — `docs` source, 4,492 toc entries,
  0 changed, 15 removed, `errors: []` (so removals came from the page-inventory step, not failed
  fetches). Note: the run is flagged `"partial": true` — the full delta may be incomplete.
- Probe: `curl -L` against both the corpus-key URL (`.md` mirror, which is how the sync stores
  these docs — corpus layout is `corpus/docs/en/<path>.md`) and the plain HTML page.
- Controls (docs NOT in the removed list): `en/connectors/snowflake.md` → **200**,
  `en/connectors/slack.md` → **200**. The `.md` mirror mechanism is healthy corpus-wide, so the
  `.md` 404s below are page-specific upstream changes, not a mirror-format collapse.

## Per-doc verdicts (probed 2026-10-26)

| Doc (corpus key) | `.md` mirror | HTML page | Verdict |
|---|---|---|---|
| `en/airo/recipe-editor/create-recipes.md` | 404 | **200** | Mirror withdrawn; page live — sync dropped erroneously |
| `en/canvas.md` | 404 | **200** | Mirror withdrawn; page live — sync dropped erroneously |
| `en/connectors/enterprise-context-by-workato.md` | 404 | **200** | Mirror withdrawn; page live — sync dropped erroneously |
| `en/agentic/.../enterprise-context-connector/actions/search-documents.md` | 404 | **200** | Mirror withdrawn; page live — sync dropped erroneously |
| `en/agentic/.../enterprise-context-connector/enterprise-context-connector.md` | 404 | **200** | Mirror withdrawn; page live — sync dropped erroneously |
| `en/data-orchestration/data-pipeline-recipe.md` | 404 | **404** (also `data-pipeline.html` 404; `en/data-orchestration.md` still 200, `en/data-orchestration/` 308) | **Genuine upstream deletion/restructure** — removal was correct |

Unprobed but same-cluster (high-confidence extrapolation — same parent sections as probed peers,
identical pattern): the remaining 9 — `list-documents*.md`, `metadata-filters.md`,
`search-documents-advanced-filters.md`, `upsert-documents.md`, `delete-document.md`
(enterprise-context-connector actions) and `generate-descriptions.md`, `map-fields.md`,
`write-formulas.md` (airo recipe-editor). Confirm opportunistically on the next sync run.

## Root cause

The sync keys docs by their Mintlify `.md` mirror URL and treats a `.md` 404 as "page removed."
Upstream (docs.workato.com) selectively withdrew markdown-mirror serving for these pages
(probably an Agent Studio / AIRO docs restructure — the withdrawals cluster exactly there) but
kept the HTML pages live. The sync never falls back to the HTML URL, so it correctly observed
`404` and incorrectly concluded `removed`.

## Recommended fix

1. **Sync repair (the real fix, covers 14 docs):** before recording a removal, probe the plain
   (non-`.md`) URL. If it returns 200, do NOT remove — fetch the HTML page and re-key (or keep
   the stale `.md` corpus copy and flag `mirror-withdrawn`). Only remove when BOTH the `.md`
   and HTML URLs 404. This makes the sync resilient to Workato withdrawing mirrors piecemeal.
   No redirect map is needed — the pages didn't move, only the mirror format died.
2. **No action for `data-pipeline-recipe.md`:** genuine deletion; the sync's removal was correct.
   If AIRO/data-orchestration content from that page is needed, re-source it from wherever the
   restructure moved it (check `en/data-orchestration.md` children on the next full sync).
3. **Housekeeping:** the 2026-10-26 diff is `partial: true` — treat its `changed/unchanged`
   counts as provisional; re-run the full diff after the sync repair lands.
