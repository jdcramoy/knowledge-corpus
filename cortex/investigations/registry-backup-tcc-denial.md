# Investigation: registry-backup nightly-receipts-gate ESCALATION — TCC Documents denial
Run-date: 2026-10-20 · Read-only investigation · Nothing changed outside this file.

## VERDICT
macOS TCC Documents-folder denial against the **`/usr/bin/python3`-rooted launchd context**.
The snapshot is fresh, unlocked, and readable from a terminal. The backup job itself
(bash-rooted) wrote it successfully at 04:23. Every failing job is one whose launchd
process tree is rooted in `/usr/bin/python3` (→ Xcode's python3) and touches `~/Documents`.

## Evidence trail
1. **Plist** (`~/Library/LaunchAgents/com.gwsemantic.registry-backup.plist`): `/bin/bash
   .../scripts/registry-backup-daily.sh`, fires 04:23, stdout+stderr → `/tmp/gws-registry-backup.log`.
   Comment shows a same-morning 02:51 edit adding RunAtLoad catch-up (unrelated to this failure).
2. **Backup job SUCCEEDED**: log shows 08:23:05Z run — "1073 rows exported", "snapshot changed,
   committed", `backup_seeded batch nightly-2026-10-20`. File mtime Oct 20 04:23:10 local. The
   writer has Documents access.
3. **Snapshot is healthy**: 4,653,959 bytes, fresh `exported_at: 2026-10-20T08:23:10Z`, no ACLs
   (`ls -leO` clean), no restricted flags, only `com.apple.provenance` xattr — not locked,
   not quarantined, not overwritten. `head -c 500` from terminal: exit 0.
4. **The reporter is `com.josh.kb-receipts-gate`** (`~/.claude/knowledge/scripts/nightly-receipts-gate.py`,
   /usr/bin/python3, fires 07:07, log `/tmp/kb-receipts-gate.log`). Its reads of the snapshot
   fail `[Errno 1] Operation not permitted` on run-dates 2026-10-19 AND 2026-10-20.
5. **Same denial class confirmed in sibling jobs (pattern is TCC-wide, not one-off)**:
   - `com.josh.kb-receipts-gate` also fails the `backup` check: `git -C ~/Documents/josh-orca
     log -1` → exit 128 from its launchd context; the IDENTICAL command from a terminal → exit 0.
   - `com.josh.gw-semantic-dashboard` (exit 1): `PermissionError: [Errno 1] Operation not
     permitted` WRITING `~/Documents/gw-semantic-dashboard/index.html`; dashboard HTML stale
     since Oct 18 22:13 while the 07:42 runs fail.
6. **Control case**: `com.josh.kb-stash` runs every 15 min, `errors=0` all day — it writes only
   `~/.claude/knowledge/`, OUTSIDE TCC scope. Only ~/Documents touchers fail.
7. **TCC attribution asymmetry**: the backup job's python3 export runs as a CHILD of /bin/bash
   (the plist program) and succeeds; the gate runs /usr/bin/python3 as the ROOT of its job tree
   and fails, and its git child fails with it. `/usr/bin/python3` resolves to
   `/Applications/Xcode.app/.../python3`. Bash-rooted job trees have a Documents grant;
   python3-rooted job trees do not. (TCC.db itself unreadable even from this terminal —
   `Operation not permitted` on the copy — consistent with no Full Disk Access here; grant
   inventory could not be enumerated directly.)
8. Ruled out: file lock/ACL (step 3), changed script path (plist path correct, script exists),
   stale/missing snapshot (fresh 04:23 write), job miss (receipt line proves the 04:23 fire).

## Recommended smallest fix (RECOMMENDATION ONLY — nothing applied)
**Wrap the failing jobs' program in `/bin/bash -c`, making bash the root of the job tree:**
- `com.josh.kb-receipts-gate.plist`: `/bin/bash -c '/usr/bin/python3
  ~/.claude/knowledge/scripts/nightly-receipts-gate.py'`
- `com.josh.gw-semantic-dashboard.plist`: same wrapper for its python script.
This is the evidence-proven path: python-under-bash already writes to Documents daily in the
backup job. No new TCC surface, no plist re-approval churn, `launchctl unload/load` per job.

**Alternative (wider grant, not preferred):** grant Full Disk Access (or Documents) to
Xcode's python3 binary in System Settings — works, but grants EVERY python3 script Documents
reach and can silently break when Xcode updates the interpreter.

**Do NOT:** chase path/lock theories (ruled out), or add another manifest/copy of the snapshot
outside ~/Documents as a workaround — fixes the symptom, leaves the dashboard write broken.

## Follow-ups for Josh (after fix, verify live)
- `launchctl kickstart gui/$(id -u)/com.josh.kb-receipts-gate` → log should show registry-backup GREEN.
- Same for `com.josh.gw-semantic-dashboard` → index.html mtime updates.
- The gate's other REDs on 2026-10-19 (`backup` git inspect, `kb-sync` missing diff) are the
  same TCC class for `backup`; `kb-sync` missing `~/.claude/workato-kb/diffs/`
  is a separate check to re-verify after the fix.
- Gate log holds only the two most recent runs (/tmp cleared per boot) — first-failure date
  before 2026-10-19 could not be established; dashboard staleness bounds it to ≤ Oct 19.
