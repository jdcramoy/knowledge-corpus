# Spec: per-project changelog + env-diff + promotion wiring

Date: 2026-10-10. Status: PLAN — build kickoff gated on Josh.
Fusion-reviewed (baseten/deepseek-v4-pro + fireworks/glm-5.3-flash, 2026-10-10;
ledger: knowledge/models-evals/fusion.jsonl).

## Goal (one sentence)

Know what changed per Workato project and what prod is missing/differing, and
turn that into a governed promotion batch (manifest + Jira story) without
manual tracking.

## Scope

IN: two derived scripts (changelog, env-diff) + promotion-orchestrator prompt
patch. OUT (v1): connection deep-diff (existence only), rename-pairing
heuristic (v1.5), any new authoritative state store, any prod write path,
scheduled new fleet job (reuses estate-architect's Monday pass).

## Prior art (extend, never rebuild — searched INDEX.md, domains/, scripts/, agents/)

- build-ledger.jsonl (8,263 rows, hook-written, ticket-attributed) = WHAT changed
- recipe-history/<env>/<id>/<ts>.json git repo = what the code looked like, both envs
- promotion-orchestrator agent = ledger→manifest→BSYS story→staged execution (~70% of the ask)
- wt (dev 3535597) / wt-prod (3535598) full Developer API, live-verified 2026-10-10
- corpus index (recipes+folders), estate-architect (properties parity only), watchdog Job 4 (external-edit P2 flags)
- MISSING prior art: any asset-level env diff; any per-project changelog view.

## Delta 1 — changelog.py (derive-on-demand, zero new state)

- `changelog.py --project <folder|epic|ticket> --since <date>`
- Resolve ledger recipe_id → folder via corpus index + live reads; group by
  Workato project/folder (= app/service unit); ticket↔folder mismatch FLAGGED.
- MUST include a "changed but no ledger entry" section: assets in scope with
  updated_at > last promotion and zero ledger rows (catches out-of-harness
  edits; the 48h watchdog window is a forgetting window — this is window-wide).
- Output: markdown w/ URLs, tickets, evidence. Rebuildable; parser hard-fails
  on corrupt ledger lines (never skips them silently).

## Delta 2 — env-diff.py (read-only, both profiles)

- Inventory dev vs prod: folders, recipes (+code), connections, lookup tables,
  data tables, properties.
- Join = folder-path + asset NAME (IDs differ across envs — known promotion
  join-key problem).
- Classes: MISSING_IN_PROD, CODE_DIFFERS, NEWER_IN_DEV, ORPHANED_IN_PROD
  (includes intentional deletes — confirm intent, never auto-remediate),
  CONNECTION_MISSING_IN_PROD, PROPERTY_DIVERGENCE.
- CODE_DIFFERS hash: NORMALIZE the DSL first (substitute env-specific IDs →
  name refs via corpus index + dependency data). Raw code hash is WRONG —
  env-ID remapping would flag nearly every correctly promoted recipe.
  Empirical validation gate: on one known-good promoted recipe, normalized
  hash must MATCH before the class is trusted.
- Closure audit: after `wt manifests create`, expand the transitive closure,
  diff against the reviewed batch → "collateral closure members" (closure
  smuggles unreviewed/stale dependencies into the package).
- Cache: derived registry (owned-registry.json pattern) for weekly reports
  ONLY; promotion runs always live-read.

## Delta 3 — promotion-orchestrator prompt patch

- Batch formula (fusion-corrected): **ledger-touched ∪ env-diff-differs-in-scope
  (since last promotion marker)**. The original ∩ formulation was a logic bug —
  out-of-harness edits are by definition not ledger-touched, so intersecting
  with the ledger re-excludes exactly the class it was meant to catch.
- Connection handling (CORRECTED after Josh's evidence + docs, 2026-10-10:
  connections ARE manifest/packageable assets — docs.workato.com
  recipe-development-lifecycle/export — but imported connections do NOT carry
  credentials; they must be re-authorized in the target env). Orchestrator
  stage 0: diff batch connections vs prod — missing ones get INCLUDED in the
  manifest; every connection in the batch gets a "RE-AUTH REQUIRED after
  import" line in the story + the post-deploy-smoke checklist already covers
  post-import verification.
- Promotion marker granularity: VERIFIED per-asset for recipes (guardrails
  register.js:1100 — /promoted writes one {kind: promotion, recipe_id} row per
  id). Caveat for v1.5: non-recipe assets (tables, genies) have no promotion
  marker row class yet — scope "since last promotion" to recipes and treat
  table/genie drift as env-diff-reported only.
- Orchestrator single-instance lock file (cheap race guard).
- Per-project path: "prep the <project> promotion" scopes ledger + env-diff
  to that folder/epic.

## Acceptance criteria (objectively verifiable)

- [x] `changelog.py --project "HR" --since 2026-10-01` — built + live-verified
      2026-10-10: 3 ledger rows hand-matched verbatim; no-ledger section proven
      both directions (reported no-ledger recipes have 0 ledger rows; control
      recipe has 319); corrupt-line hard-fail proven (exit 2 + line number).
- [x] `env-diff.py` full-estate run returns all 7 classes (2026-10-10: missing
      5,773 / code_differs 757 / newer 83 / orphaned 486 / conn-missing 631 /
      conn-reauth 1 / property-divergence 51). Validation gate independently
      reproduced on [CONF] MOD | Confluence (dev 45742351 / prod 48238615):
      raw hashes differ (ID churn), normalized hashes MATCH, exit 0. 18/20
      old-stable pairs pass; the 2 fails investigated = real content diffs.
- [ ] A deliberate out-of-harness edit round-trips through BOTH the changelog
      no-ledger section AND the env-diff union (the components are each proven;
      the combined drill is pending the first real out-of-harness edit).
- [ ] Orchestrator end-to-end on a real batch (scripts + patched agent proven
      separately; first real "prep the <project> promotion" run is the test).
- [x] Zero prod writes: verified by grep on both scripts (GET-only, 0 write
      verbs); env-diff cache masking verified (frontify.token stored redacted).

## First-run estate findings (2026-10-10, actionable)

- CONNECTION_REAUTH x1: `Corporate API (Prod)` prod connection 18689376 is in
  authorization EXCEPTION right now.
- 631 connections exist in dev with no prod counterpart (expected: personal/
  scratch; worth a curation pass).
- 486 prod-only assets flagged confirm-intent (zombie/deletion candidates —
  feeds the estate-architect deprecation radar).
- 51 property divergences dev vs prod.
- Trap discovered: `/api/folders` returns only project ROOTS (263) while
  recipes live in 1,208 distinct dev folders — both scripts resolve
  subfolders by direct GET; the changelog joins on project_id.

## Risks

- Normalization completeness: unknown ID-bearing fields could still hash-differ
  (mitigation: validation gate + report raw-vs-normalized on disagreement).
- Properties import semantics: Workato does not overwrite existing property
  VALUES on import — property drift must be applied manually and listed in the
  story explicitly.
- Ledger ticket misattribution under multi-ticket sessions (accepted: flagged,
  not silently trusted).
