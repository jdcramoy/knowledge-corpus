# Investigation: BSYS-29757 — did the hotfix edit land on PROD 82121168 before its 20:27Z restart?

**Investigator:** read-only session, 2026-10-16T21:00Z. All reads via wt with the josh-prod profile (GET only),
build-ledger.jsonl, mission-control registry.json, /tmp artifacts. Nothing written to Workato; no lifecycle ops.

## Verdict

**YES — the hotfix edit landed BEFORE the restart, and the recipe is now running it.** Live code (read 21:00Z)
is byte-identical to `/tmp/ait_patched.json` (the Fix A payload) and to `/tmp/ait_live.json` (the 20:27:45Z
post-start GET). Diff vs pre-hotfix `/tmp/ait_fresh.json` (19:31Z GET, pre-PUT) is exactly ONE change: the
trigger description of the `action_inbox_task` trigger — "...exact internal task correlation" → "...exact
internal task correlation **for a Workday inbox task (Approval, Consolidated Approval, or Send Back)**..." —
the BSYS-29757 Fix A (Time Off routing exclusion). No step, connector, or dependency changed.

Version history (live read): **v7** (id 154561672) created **2026-10-16T20:27:16Z** by the federated
"Workato AHQ | AI" service account (the wt CLI path); pre-hotfix is **v6** (Josh, Oct 2). The 20:27:34Z
restart ran v7. Recipe running: True.

## Timeline (ledger + live evidence)

- 19:31:21Z — GET recipe → /tmp/ait_fresh.json (pre-hotfix state, v6 code)
- 19:32:22Z — manifest mirror created (25 rows, deps intact, verified: false); platform manifest 366666 created 19:32:26Z
- 19:33:44Z / 19:34:24Z — hand-edits (dedup 25→23 rows; strip all deps to []) written to **/tmp/manifest-fix-payload.json only** — never the mirror
- 19:34:15–19:34:51Z — export attempts against manifest 366666; ops 42249022/42249046/42249061 ALL status:failed ("Connection ... CON | ISU Prod is not found under Home/Agentic | HR Self Service Genie/Core/HR Skills/Workday MCP"); op 42249061 re-read live: failed, download_url null. **No ZIP ever produced.**
- 19:34:57Z — manifest branch time-boxed and abandoned per sunk-cost rule (prior investigation, bsys-29757-prod-stop-state.md)
- 19:34:58Z — Fix A payload staged → /tmp/ait_patched.json (description-only change)
- 19:35:05Z — red-team verdict on record (redteam/BSYS-29757-action-inbox-task-trigger-description.md) — gate satisfied pre-stop
- 19:35:13Z — recipe STOPPED (success:true, running:False confirmed)
- 19:35:16Z — deadman session 3d4d4b1a fired its PUT; transcript ends on the tool_use, NO result — that PUT is UNPROVEN
- **20:14:41Z — follow-up session re-fired the PUT: wt api PUT /api/recipes/82121168.json --data /tmp/ait_patched.json (josh-prod profile)** (ledger line 18625) ← the edit that landed
- 20:27:16Z — payload rebuilt from fresh+patched and PUT (ledger 18674); **v7 born 20:27:16.7Z**
- 20:27:34Z — wt recipes start 82121168 (ledger 18680); post-start GET running check
- 20:27:45Z — live GET → /tmp/ait_live.json, code == patched (ledger 18684); re-verified 20:32:15Z (ledger 18720)

## Q2: Does the hand-edited manifest change (dependency rows stripped) match what is live?

**NO — it never landed in any verified form, and it is irrelevant to what runs.**

- The dep-stripping edits lived only in /tmp/manifest-fix-payload.json. The local mirror
  (`~/orca/workspaces/workbench/Workday-Development/manifests/bsys-29757-hotfix-action-inbox-task-trigger-description-time.manifest.json`)
  was never touched: 25 rows, deps intact on every row, `verified: false`, mtime 19:32:22Z (untracked in git, no baseline diff possible).
- Platform manifest 366666 ("BSYS-29757 hotfix — action_inbox_task trigger description (Time Off routing
  exclusion)", project Agentic | HR Self Service Genie/Core/HR Skills/Workday MCP) exists, status "working",
  updated_at = last_exported_at = 19:34:25Z — that timestamp is the export-attempt bump, not a verified export.
  Rows are not readable via the REST routes available to wt; no ledger entry shows the stripped payload being
  pushed to the platform before the session died.
- Decisive: every export op failed with the connection-placement 422 and download_url null — the manifest never
  produced a ZIP, so no import from it could ever reach any environment. The recipe's runtime dependency
  footprint is unchanged by construction (code diff is description-only).
- Staleness: the mirror's recipe row pins **version 6**; live is **v7**. Manifest 366666 must NOT be cited as
  verified anywhere (no ZIP, no read-back, stale version pin) — consistent with proposal 3 of the prior stop-state investigation.

## Q3: Does any registry row or ledger line attribute the restart?

- **Ledger: YES, but anonymously.** build-ledger.jsonl lines 18625 (20:14:41Z PUT), 18674 (20:27:16Z payload/PUT),
  18680 (20:27:34Z start), 18684 (20:27:45Z verify), 18720 (20:32:15Z running/version check) — all workato-cli
  on the josh-prod profile. The ledger records kind + command + recipe_id but NO session ID, so the restarting
  session is identifiable only as "a workato-cli session active 20:14–20:32Z", not by name.
- **Registry: NO.** mission-control registry.json has exactly two BSYS-29757 rows: the 18:24:47Z deadman absorb
  note (dropped-3d4d4b1a-656) and the 20:48:02Z closeout — which describes Fix B phase 1 / recipe 82201417 ONLY.
  Zero rows mention 82121168. The 20:28:51Z mission-control closeout command (ledger 18704, --jira BSYS-29757)
  produced no registry row naming 82121168.
- Corroboration the restart was deliberate, not stray: bus post 20:59:12Z "prod-82121168-stopped-RESOLVED"
  (ledger 18760) and the attention-queue 20:00Z entry tracking the stopped state.

## Bottom line

The POSSIBLE UNFINISHED PROD STATE from the 19:35Z deadman death was resolved by a follow-up session:
edit re-fired at 20:14Z (final PUT 20:27:16Z creating v7), restart 20:27:34Z, verified 20:27:45Z.
Hotfix Fix A is live and running. Residual gaps, in priority order:
1. **No named attribution** for the restart anywhere (ledger line is anonymous; registry row missing). A
   closeout row naming 82121168 should be added by whoever owns that session — or absorbed as dropped work.
2. **Manifest gate unmet**: manifest 366666 unverified (3 failed exports, no ZIP), mirror stale at v6 with
   verified:false. Fix connection-placement via the manifest-creation script path before any DR ticket cites it.
3. BSYS-29757 remains open overall: Fix B (dedup lock rewire) is staged and waiting on Josh's go (20:48Z row).
