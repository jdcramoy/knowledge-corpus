# Investigation: session-shadow plist repoint provenance (2026-10-15)

**Verdict:** The repoint was made by session `0084d622-37b8-44ce-9a40-69be15f9264b`
(workbench project) — Josh's overnight "fusion analysis of the whole harness estate" session —
at 2026-10-13 17:59:36 local (21:59:36Z), via cp+sed+launchctl reload. It DID file a
mission-control closeout on `p2-closer-detection-recovery` — but 70 seconds BEFORE the fix,
in state `needs-josh`, and never updated the row. The row is now stale/inaccurate. Fix held:
1,590 continuous heartbeats since 22:00:42Z, max gap 91s.

---

## 1. Who made the repoint

**Session:** `0084d622-37b8-44ce-9a40-69be15f9264b`
Transcript: `~/.claude/projects/-Users-<user>-Documents-workbench/0084d622-37b8-44ce-9a40-69be15f9264b.jsonl` (line 448)

**Origin:** Josh's opening prompt (transcript start, 05:53 local): "While I'm sleeping, I want you
to run a fusion analysis on the whole harness estate, kb, and corpus..." — the session ran the
fusion-estate-audit (artifacts `fusion-audit-2026-10-13.md`, `fusion-estate-audit/`), then Josh
said "Ok yeah, build all of this functionality and verify it end-to-end". The plist fix was part
of that build wave (5 subagents dispatched ~21:53 local; the fix landed from the parent session).

**The exact command** (transcript line 448, timestamp `2026-10-13T21:59:36.868Z` = 17:59:36 local,
one second before both files' mtime 17:59:37):

```
cp ~/Library/LaunchAgents/com.josh.session-shadow.plist \
   ~/Library/LaunchAgents/com.josh.session-shadow.plist.bak-fusion-20261013 \
  && sed -i '' 's|/opt/homebrew/bin/python3|/usr/bin/python3|' \
      ~/Library/LaunchAgents/com.josh.session-shadow.plist \
  && /usr/bin/python3 -m py_compile ~/.local/bin/session-shadow.py \
  && launchctl unload ... 2>/dev/null; launchctl load ... \
  && sleep 70 && tail -3 /tmp/session-shadow.log && launchctl list | grep session-shadow
```

**"fusion-class" confirmed:** the `.bak-fusion-20261013` suffix is the session's own marker —
the fix came out of the fusion-estate-audit build wave. The backup preserves the pre-fix
interpreter (diff: only line 8 changes, `/opt/homebrew/bin/python3` -> `/usr/bin/python3`).

## 2. Mission-control closeout

**YES - but filed BEFORE the fix, and never updated.**
Row at `~/.claude/knowledge/mission-control/registry.json` (also events.jsonl line 352):
- `ts: 2026-10-13T21:58:26Z` (17:58:26 local) - **70 seconds before** the fix command
- workstream `p2-closer-detection-recovery`, project `agent-harness`, state `needs-josh`
- `what`: session-shadow.py auto-absorb + checkpoint journal, --selftest 13/13 PASS,
  63 absorb rows + 303 checkpoint rows from live manual cycles
- `needs`: "Launchd job com.josh.session-shadow is DOWN: plist pins
  /opt/homebrew/bin/python3 which no longer exists (exit 78). Fix the plist interpreter path
  (e.g. /usr/bin/python3) and reload; plist is outside the builder contract"

**Discrepancy:** the session flagged the dead job as needs-josh at 17:58:26, then executed the
fix itself at 17:59:36 and never flipped the row. Registry now shows `age_hours: 27.2, stale: true`
for a row whose named blocker is already resolved. Hygiene note: this is exactly the stale-claim
pattern the queue sweep flags; the row should be closed out (done) - not changed by this
read-only investigation.

## 3. Did the fix hold

**YES.** `~/.claude/knowledge/garden-reports/heartbeat.jsonl`, job=session-shadow:
- Pre-fix gap: last beat 2026-10-12 23:27:58Z -> next 2026-10-13 21:57:40Z (80,982s ~ 22.5h
  dark; the 21:57:40 beat is the session's manual test run during "live manual cycles")
- Post-fix: first beat 2026-10-13 22:00:42Z (~1 min after reload), then **1,590 beats** through
  2026-10-15 01:13:58Z at the 60s StartInterval cadence, max gap 91s
- Live: `launchctl list` -> `com.josh.session-shadow` last exit status **0**;
  `/tmp/session-shadow.log` tail clean (empty tail = no errors written since)

## Timeline (local, 2026-10-13)
- 17:58:26 - closeout filed, needs-josh, plist flagged dead (exit 78)
- 17:59:36 - fix command runs (cp -> sed -> py_compile -> launchctl reload)
- 17:59:37 - both plist and .bak written (mtimes match)
- 18:00:42 - first launchd heartbeat; continuous since

*Investigation read-only; nothing else modified. Session: claude-knowledge project, 2026-10-15.*
