# Investigation: BSYS-29757 prod stop — recipe 82121168 left stopped, edit PUT unverified

**Investigator:** cortex (read-only), 2026-10-16T19:58Z
**Sources:** transcript tail (last 120 of 786 entries) of session 3d4d4b1a-6560-4078-9948-fe37c9785b81 ("HR Genie PTO approval bug", final prompt "Hotfix to production please. This needs to fixed asap.", bypassPermissions) + live read of the local manifest mirror.

## Verdict (one paragraph)

The hotfix session's last COMPLETED action was stopping prod recipe 82121168 via the Workato CLI stop command (prod profile) at 19:35:13Z — response success:true, immediately re-read running:False. At 19:35:16Z it fired the prod edit — a PUT of /tmp/ait_patched.json to /api/recipes/82121168.json ("Push patched recipe code to prod") — and the transcript ENDS on that tool_use: no tool_result, no assistant text, no closeout. Whether that PUT reached Workato and completed is UNKNOWABLE from the transcript; combined with the 19:56Z live check (still running:False), recipe 82121168 is in POSSIBLE UNFINISHED PROD STATE: definitively stopped, possibly edited (the patched trigger description may or may not have landed), definitively NOT restarted. The next action by anyone must be a live read of the recipe (wt recipes get 82121168 on the prod profile, comparing version/code against /tmp/ait_patched.json) — not a restart, not another edit.

## (1) Last completed action

19:35:13Z — wt recipes stop 82121168 (prod profile) returned {"success": true} and the follow-up get confirmed running: False. Immediately before (19:35:05Z) it wrote the red-team verdict file ~/.claude/knowledge/redteam/BSYS-29757-action-inbox-task-trigger-description.md (brain-guard linted, 1 issue). Sequence: staged patched code to /tmp/ait_patched.json (19:34:58, "patched. desc len: 1743" — trigger-description-only change to the action_inbox_task skill) → red-team verdict → stop recipe → PUT patched code (interrupted).

## (2) Was the prod EDIT completed?

UNKNOWN — fired but unconfirmed. The PUT tool_use exists at 19:35:16Z; there is NO tool_result for it anywhere (last 12 entries checked in full; the file terminates on that tool_use). No evidence of success (no version bump, no response body) and none of failure. Per the POSSIBLE UNFINISHED PROD STATE rule, a live read must settle it. Anchor: the manifest row shows the recipe at version 6; a live get will show whether the version advanced.

## (3) Documented next step

The session's narrated plan: patch the trigger description of the action_inbox_task skill (Time Off routing fix) → red-team (done) → stop recipe (done) → PUT patched code (fired, unconfirmed) → restart recipe and verify a live run. The manifest/export verification branch was explicitly TIME-BOXED AND ABANDONED at 19:34:57: "Manifest rows are accurate but the export engine keeps refusing placement of connection deps on agentic_skill rows — 3 strikes, time-boxing that per the sunk-cost rule and proceeding with the hotfix." So the recorded path forward: confirm/complete the PUT, then START the recipe and verify. Restart was never reached.

## (4) Manifest — created, hand-edited in /tmp only, NEVER verified

- Platform export manifest 366666 created 19:32:26Z, 25 rows, folder chains crawled top-down; action_inbox_task correctly present BOTH as agentic_skill (provider_id 82121168, handle skl-AbTFaPJf-kh4wnh-CD) and as its recipe row with 9 deps.
- Export/ZIP verification FAILED 3 times (export ops 42249022, 42249046, 42249061 — all status:failed). The Workato export engine rejected connection-dep placement, e.g. "Connection Home/* Connections/Workato API is not found under Home/Agentic | HR Self Service Genie/Core/HR Skills/Workday MCP" and the same for "CON | ISU Prod". No ZIP was ever downloaded — the standing order's ZIP-verify step never happened.
- The hand-edits the build ledger shows are real but went to a TEMP payload, not the mirror: 19:33:44 python heredoc dropped the duplicate recipe row (25→23 rows, "payload written"); 19:34:24 another stripped deps to [] on all 23 rows — both writing /tmp/manifest-fix-payload.json. Neither fixed the export; neither was written back to the local mirror.
- Local mirror file …/manifests/bsys-29757-hotfix-action-inbox-task-trigger-description-time.manifest.json, read live 19:58Z: 25 rows, deps intact, verified: false, mtime 19:32:22Z (set at creation, never touched since). The mirror reflects the UNVERIFIED 25-row state; the 23-row dep-stripped variant lives only in /tmp, and the export it fed still failed.

## Proposals (NOT executed — read-only investigation)

1. PROPOSED (prod write, needs Josh's explicit go): live-read 82121168 to settle (2) — compare running flag, version (manifest says 6), and trigger description against /tmp/ait_patched.json. If the PUT landed, only start + live-run verification remains; if not, decide whether to re-fire it per the hotfix plan.
2. PROPOSED: restart 82121168 ONLY after (1) resolves — it is an MCP-tool recipe for a live Genie and has been down since 19:35:13Z (confirmed still down 19:56Z).
3. PROPOSED: manifest 366666 must not be cited as verified anywhere (mirror verified:false, zero ZIP evidence). Fix the connection-placement rows via the manifest-creation script path, not more hand-edits, before any DR ticket.
4. The red-team verdict exists and predates the stop, so the red-team gate is satisfied on record; the manifest gate is not.

Nothing was changed, restarted, edited, posted, or deleted during this investigation beyond writing this findings file.
