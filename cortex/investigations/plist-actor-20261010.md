# Plist rewrite + fleet runner gutting — actor attribution (2026-10-10/11)

Investigated 2026-10-11, read-only. Companion to cortex-pulse-lane-gap.md, which established
the mechanics and left the actor as "unverified". This closes that hole.

## Verdict — one Claude session, one design flaw, three stages

**The actor was Claude Code main session `fcd2fc76-cfdd-4492-bf69-66706904fc8d`**
(workbench cwd, ~/.claude/projects/-Users-<user>-Documents-workbench/). Not launchd, not a
subagent, not Josh's shell (zsh history ends 2026-10-09 12:53 with zero fleet commands).

Timeline (all times Z; local = EDT):

1. **2026-10-10 06:03:35** — Josh opens session fcd2fc76 with the workato-dev-kb pack idea:
   "provide a pre-baked internal workato development kb... keep private files private and not
   pushed to github." This is the kit de-identification mandate (memory: workato-dev-kb
   SHIPPED 2026-10-10).
2. **08:29:10** — session runs `cp -R ~/Documents/agentic-workato-kit/bin/fleet
   ~/.claude/knowledge/config/fleet` (new private source of truth).
3. **08:29:15** — THE PLIST REWRITE: session runs a 5-iteration sed loop (cortex,
   decision-inbox, harness-fix, harness-health, value-ledger) repointing each
   ~/Library/LaunchAgents/com.josh.fleet.*.plist from the kit path to
   ~/.local/bin/fleet/run-job.sh, with launchctl unload/load per plist. This is the shared
   04:29:15-local mtime on all five plists. Intended as a path repoint, not a schedule change —
   but the unload/load shifted the fire anchor from :15-:37 to :29 (per lane-gap report (b)).
4. **08:30:18** — THE CASUALTY: same session runs `git rm -rq bin/fleet schedules
   bin/agent-command-watcher.py && git commit` in the kit (commit 724c0da, pushed).
   ~/.local/bin/fleet was a SYMLINK into the kit (created Oct 10 00:01 by consolidation commit
   9c974fd "kit repo is canonical, ~/.local/bin/fleet symlinked"). git rm deleted the live
   runner THROUGH THE SYMLINK. Era 1 (every hourly job exit 127) begins at the next fire,
   ~09:29Z — one hour after the session closed.
5. **2026-10-10 22:40:42** — PARTIAL RESTORE by session `b3ac18d0-fd3d-4dda-aaa2-752a4c5f159c`
   (Josh-interactive; Josh was feeding it ASEE/GEARS Confluence-mining asks at 09:47Z). It hit
   the broken runner while debugging kb-audit, discovered the breakage (22:39-22:40 invoke
   tests), and restored the kit's bin/fleet from the `~/.local/bin/fleet.pre-consolidation-2026-10-10`
   snapshot. That snapshot dated Oct 9 05:00 and predates 9+ job families — cortex.env/prompt,
   cost-governor, decision-inbox, evidence, harness-fix/health, index-budget, instruction-miner,
   kb-audit, replay-sample, restore-drill were NOT in it. Era 2 (cortex.env missing) begins at
   the 23:29Z fire.
6. **2026-10-11 09:07-09:26Z** — FULL RECOVERY by session `ce9493c9-ff4d-433b-ba46-68498956d1ce`
   (the next-10 build-wave session, subagents 05:15-05:33 local): full jobs/ redeploy (05:07
   local restamps), run-job.sh v2 with probe gate (05:14/05:26), 5 new zero-LLM-job plists
   (05:25), kit commit f2ded3b "full job-file deploy set" (09:26:25Z), and the dream-loop.md
   Morning-fleet outage RCA appended 09:26:44Z, which self-reports "all 10 approved by Josh".

## Was it Josh-approved?

- The session itself: YES — Josh opened it with the de-identification directive, and was live
  in the window (commit 69e4539 04:27:41 carries "(Josh 2026-10-10)" feedback).
- The plist repoint: a reasonable execution of that directive; no explicit per-step approval,
  none sought. Within the standing dev-autonomy grant.
- The runner deletion: NOT an approved action and not an intended one — an unanticipated side
  effect of git rm through a symlink the session did not know existed (it had repointed plists
  to ~/.local/bin/fleet believing the copy at knowledge/config/fleet was now the backing store;
  it never re-pointed the symlink or copied files into it).
- The 22:40 partial restore: restorative self-repair in a Josh-interactive session; not flagged
  to Josh as an incident.
- The 10-11 full redeploy: inside the Josh-approved next-10 build wave ("all 10 approved by
  Josh", dream-loop.md 2026-10-11 entry, ticket BSYS-28296).

## Why it was unlogged

- build-ledger.jsonl records wt/AIRO/orca-browser mutations only; plain Bash git/file ops in
  main sessions are not captured. The ledger has ZERO entries between 2026-10-10T08:11Z and
  2026-10-11T01:47Z — covering both the 08:29Z plist rewrite and the 22:40Z restore.
- Neither actor session appended a ledger line: fcd2fc76 treated the repoint+git-rm as repo
  hygiene inside a doc task (its own commit message claims "21+5 plists verified" — it verified
  the plist text, not a live job run through the new path); b3ac18d0 logged its KB findings to
  projects/workato-kb.md but did not file the fleet breakage it incidentally fixed.
- The failure surfaced an hour AFTER fcd2fc76 closed (next hourly fire), so nothing connected
  the plist mtime to the outage until the cortex pulse investigation at 09:15Z on 10-11.

## Contract gaps (beyond the three in the lane-gap report)

4. Symlinked runtime + git rm = remote-control deletion of live infrastructure. The
   consolidation made the kit repo a loaded gun: any session cleaning the shareable repo
   silently kills the fleet. knowledge/config/fleet is the source of truth now; the symlink is
   gone (current ~/.local/bin/fleet is a real dir) — keep it that way.
5. Path-repoint verifications must end with a LIVE job execution through the new path, not a
   grep of plist text. fcd2fc76's verification grep passed while the backing files were one
   minute from deletion.
6. Session-authored plists/runtime changes should append to build-ledger.jsonl (kind:
   host-config) — the ledger's current scope is Workato-only, so the entire fleet/launchd
   surface is invisible to evidence/claim verification.

## Not verified

- Whether session ce9493c9's "all 10 approved by Josh" covers the fleet-file redeploy itself
  or only the 10 build-wave items (approval framing taken from its own dream-loop entry).
- The exact mechanism that restamped jobs/*.env at 05:07 local vs run-job.sh at 05:14/05:26
  within session ce9493c9 (single continuous run assumed from commit + append timing).
- The 11th env-error pair anomaly from the lane-gap report remains unexplained.
