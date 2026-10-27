# Investigation: dev-workspace recipe deletions — 83154015 / 83185818 / 83197138 (404 on both profiles)

**Investigated:** 2026-10-21 (cortex investigation dispatch, read-only)
**Trigger:** evidence agent replay gym flagged all three recipes returning HTTP 404 on BOTH
profiles (dev + bt-prod) since 2026-10-20 — expected cleanup or drift?
**Verdict up front: ALL THREE ARE INTENTIONAL DELETIONS, documented in the build ledger with
same-day context. Zero unexplained drift. Live-verified 2026-10-21: all three 404 on dev AND
bt-prod (matches the evidence agent's report exactly).**

---

## Recipe 83154015 — INTENTIONAL-CLEANUP (documented)

- **What it was:** the `ai_directory_get_asset` MCP tool recipe (AI Directory project,
  BSYS-25832; tool recipes 83153991/83154015/83154017 were built 2026-10-18).
- **Deleted:** 2026-10-20T05:18:22Z, `wt api DELETE /api/recipes/83154015` (ledger line 22715),
  after repeated `recipes start` code_errors that morning.
- **Why (documented in `~/.claude/knowledge/projects/ai-directory.md` lines 21/54):**
  "get_asset wrapper DELETED (redundant — list_assets(asset_id=...) does exact lookup; also its
  start-validation was blocked by the stale function-registry schema)." MCP server tool count
  went 16→15; manifest 367175 (15 rows, read-back verified) reflects the removal. The project doc
  was updated in the same session (05:21Z).
- **Classification: intentional-cleanup.** Ledger + project doc + manifest all agree.

## Recipe 83185818 — INTENTIONAL-CLEANUP (delete-and-rebuild as v2)

- **What it was:** Estate Watchtower v1 Watcher recipe (BSYS-29667, built 2026-10-19 19:47–19:54,
  session `watchtower-watcher-build-20261019`), heartbeat monitor on EM Ops Audit Log.
- **Why it died:** project-dreamer/dissenter round (2026-10-20 04:48–04:49, gossip bus
  `estate-monitor-2026-10-20`): v1 read the EMPTY AI Builder copy table 161961 instead of the
  live EM original c4019066 / 158784 (~100 rows/hour, live-pagination proven). One-field
  table_id fix, not an architecture flaw.
- **Deleted:** 2026-10-20T05:36:13Z, `wt api DELETE /api/recipes/83185818` (ledger line 22740,
  ticket BSYS-29477), session `watchtower-fix`. Fourteen seconds later (05:36:27Z) session
  `watchtower-v2` ran `recipe_builder_init` for "Estate Watchtower | Watcher" in folder 35890140.
- **Replacement live-verified:** recipe 83196679 "Estate Watchtower | Watcher" exists in dev
  (created 2026-10-19T22:36:27-07:00 = 05:36:27Z), currently STOPPED, 0 jobs. The v1→v2 rebuild
  happened as designed; the doc at `projects/estate-monitor.md` lines 352-353 still describes the
  pre-rebuild v1 state (STOPPED, awaiting Josh's signal pick) — **that project doc is now stale
  relative to the v2 rebuild and should be refreshed by the estate-monitor owner.**
- **Caveat:** v2 is built but stopped with zero jobs — the "watchtower replaced" claim holds for
  the DELETE, not for a working replacement. Nothing unverified beyond that.

## Recipe 83197138 — INTENTIONAL-CLEANUP (ephemeral test probe)

- **What it was:** probe recipe built 2026-10-20T07:25 (session `push-identity-guard-build`,
  BSYS-29315), alongside sibling 83197137, to exercise the push-identity-guard hook during the
  build: recipe_builder_add_step → 3× push → start → stop → **delete both 07:28:07Z** (ledger
  line 22986) → immediately followed by the "Push identity guard (hook 15)" knowledge entry in
  `domains/claude-code-mods.md` (closeout 07:28:38Z, workato-guardrails).
- **Lifecycle:** built → pushed (hook under test fires on recipe_builder_push) → started →
  stopped → deleted, all within ~3 minutes. Ephemeral validation fixture, not a build.
- **Classification: intentional-cleanup** (test-probe pattern; note the probe names were not
  TEST/TEMP/Probe-styled, so the 2026-10-13 manifest exemption did not formally apply — no
  manifest row existed for them and none appears to have been owed, since neither survived the
  session. Flagging for Josh only if he wants probe-asset naming discipline tightened).

---

## Cross-checks performed (all read-only)

1. **Live 404 confirmation** — `wt recipes get` on both profiles, all three: HTTP 404 on dev AND
   bt-prod. Evidence agent's flag is accurate; nothing further 404s.
2. **Build ledger** (`~/.claude/knowledge/build-ledger.jsonl`, 25,554 lines): explicit delete
   commands found for all three IDs, each with same-session context; no orphaned deletions.
3. **Gossip bus archive** (`knowledge/dreams/bus/project-dreamer.jsonl`, `dissenter.jsonl`):
   watchtower wrong-table finding + dissent verdict recorded 2026-10-20 04:48Z.
4. **Mission-control** (`mission-control/events.jsonl`): estate-watchtower closeout 2026-10-19
   (v1 build), workato-guardrails hook-15 closeout 2026-10-20 07:28. No row references the
   deletions as incidents — consistent with intentional ops.
5. **gslides-brand-voice / drift-fix angle:** NO prior gslides-brand-voice session exists — the
   only hits in now/josh-now.md + shadow-state.json are echoes of THIS investigation's own
   prompt (self-referential artifacts). drift-fix project docs (BSYS-29462/29828) cover ledger
   coverage gaps, not these recipes; no linkage found.

## Residual actions (for owners, not this investigation)

- `projects/estate-monitor.md` watcher section (lines 352-353) predates the v2 rebuild — stale.
- Replay gym: add these three IDs to its known-deleted baseline so they stop flagging.
- Nothing unverified beyond: v2 watcher (83196679) correctness/stopped-by-design state — its
  config was not inspected beyond existence, name, timestamps, and job counts.
