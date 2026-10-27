# Investigation: recipe 83074320 (gdocs-mcp-fix / BSYS-29692) returns 404

**Date:** 2026-10-19 · **Investigator:** cortex read-only probe (headless dispatch) · **Scope:** read-only, no assets touched

## VERDICT: DELETED — deliberately, by the fix session itself (not misrecorded, not renamed, not never-deployed)

Recipe 83074320 was real, was the gdocs-mcp fix's first dev twin, and was **deleted on 2026-10-15
(~09:41Z) by session 9b617349 itself** after it discovered it had built duplicate dev twins on top of
pre-existing ones. The fix is NOT lost — it lives on the pre-existing dev twin **70572944**
(`update_document_content (Google Docs by Workato MCP)`), which I live-verified today:
`wt recipes get 70572944` → EXISTS, running: true. The deletion is documented in the session's own
transcript (`~/.claude/projects/-Users-<user>-orca-projects-google-docs-mcp/9b617349-f422-4980-be64-f3633aa1d6cf.jsonl`):

- "wt recipes stop $id; wt recipes delete $id" for `83074320 83074561 83074563 83074564` (the duplicate twins)
- "83074320 (now DELETED) — that handle is now orphaned/broken"
- twins "(are) superseded — deleted; living manifest now carries the real ids. Duplicate-dev-twin
  creation was wasted motion caused by the wrong [id map]"
- build-ledger line 17040 (2026-10-15T09:41Z) records the id_map applied: `{'83074320':'70572944',
  '83074561':'70572935', ...}` — deleted twins remapped to the real dev recipes
- fix confirmed applied to the survivor: "Test recipe 70572944 (running, fixed ✓)"

## Timeline

1. **Oct 15 ~02:05Z** — session 9b617349 starts. Exports prod package (manifest 364013), imports into
   dev folder 35833467 (import op 42230891, completed 02:13Z), landing dev twin 83074320 (+ siblings
   83074561/563/564). Applies the structural-delete fix to the twin, PUTs via wt api.
2. **Oct 15 02:34Z** — Jira comment posted on BSYS-29692 citing 83074320 + the 3 siblings (stale
   ~7h later; Jira was never corrected).
3. **Oct 15 ~06:24–09:39Z** — session discovers pre-existing dev twins (70572944/35/40/41) already
   exist; realizes its imports were duplicates; re-applies the fix to 70572944, regenerates the skill
   handle (skl-AbxJXTnh), and **deletes its own duplicate twins** (83074320, 83074561, 83074563, 83074564),
   remapping the living manifest to the real IDs (`google-docs-mcp/manifests/BSYS-29692.manifest.json`).
4. **Oct 16 15:01Z** — mission-control claim registered citing 83074320 (kept the pre-cleanup ID).
5. **Oct 19** — claims sweep live-verify: 83074320 MISSING (flagged POSSIBLE UNFINISHED PROD STATE);
   dev AIRO recipe_get also 404. Both 404s are CORRECT — the recipe no longer exists by design.

## Why the claim text misled (secondary finding: misrecorded claim)

The claims sweep extracted three "recipe_ids" from the claim: 83074320 (real, deleted), 35833467 and
42230891 (context "bare-8digit"). Both are NOT recipes — **35833467 is the dev FOLDER** (Google Docs
by Workato MCP; `recipes?fid=35833467`) and **42230891 is the package IMPORT OP id**. The sweep's
8-digit regex over-extracted. Only one of the three was ever a recipe.

## What Jira says (BSYS-29692, read via Atlassian MCP)

The single comment (2026-10-15 02:34Z, Josh) still cites the **deleted** twin 83074320 and siblings
83074561/563/564, and links manifest 364020. It does NOT record the real surviving recipe IDs
(70572944 et al.). Ticket is In Progress; promotion never happened. So Jira points at a dead ID.

## Current true state

- **Survivor (real fix):** dev recipe 70572944 — EXISTS, running, fix applied and unit-tested; skill
  handle skl-AbxJXTnh. Sibling fixes: 70572935 (create_document), 70572940 (list_mentions),
  70572941 (list_suggestions).
- **Prod:** still unfixed — prod generator is 70572893; no deployment request was ever filed, so the
  prod-side work of BSYS-29692 remains open.
- **Deleted (correctly):** 83074320, 83074561, 83074563, 83074564 (duplicate dev twins).

## Recommended closeout actions (not executed — read-only session)

1. Update the mission-control claim (and optionally the Jira comment) to cite 70572944 instead of
   83074320 — the claim's flag_prod_state flag should clear once the recipe_ids reference a live asset.
2. Fix the claims-sweep extractor so folder/import-op ids aren't harvested as recipe_ids.
3. BSYS-29692's open item is unchanged: live UAT on 70572944, then deployment request.

## Sources

- build-ledger.jsonl lines 16506–17426 (Oct 15 build), line 17040 (id_map + deletion), line 21430/21486 (Oct 19 404 probes)
- transcript 9b617349-f422-4980-be64-f3633aa1d6cf.jsonl (deletion commands, "fixed ✓" on 70572944)
- mission-control/registry.json gdocs-mcp-fix row (ts 2026-10-16T15:01:16Z)
- reports/claims-sweep-latest.json (flag_prod_state entry, verify MISSING)
- Jira BSYS-29692 (description + 2026-10-15 comment) via Atlassian MCP
- Live: wt recipes get 70572944 → EXISTS, running: true (2026-10-19)

**Not verified:** nothing material outstanding. The prod recipe 70572893's current content was not
inspected (out of scope); prod promotion status inferred from absence of a deployment request in
ledger/Jira rather than a positive check of the DR queue.

## RESOLVED (2026-10-22, triage)

The POSSIBLE UNFINISHED PROD STATE flag from this claim is resolved and must not re-fire:
Josh confirmed BSYS-29692 done/closed on 2026-10-19 (mission-control closeout row, same ts).
The fix lives in the google-docs-mcp repo, not the deleted recipe. Surviving dev twins for
reference: 83074320 -> 70572944, 83074561 -> 70572935 (build-ledger 17040 id_map). Corrective
comment posted on BSYS-29692 pointing readers at the twins. claims-sweep should treat any
future 83074320/83074561 citation as a stale registration reference, not MISSING prod state.
