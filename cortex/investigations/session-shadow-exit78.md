# session-shadow exit 78 — diagnosis (2026-10-13, read-only)

**Verdict: CONFIG DRIFT — dead interpreter path. Launch job itself is fine; script is fine.**

## Evidence chain

1. **Plist** (`~/Library/LaunchAgents/com.josh.session-shadow.plist`): structurally valid —
   `ProgramArguments` present: `/opt/homebrew/bin/python3` + `~/.local/bin/session-shadow.py`.
   `StartInterval` 60s, `RunAtLoad` true, logs → `/tmp/session-shadow.log`.
2. **launchctl list**: `-  78  com.josh.session-shadow` (PID `-` = not running, last exit 78).
3. **Interpreter missing**: `ls /opt/homebrew/bin/python3` → **No such file or directory**.
   Only versioned binaries exist: `python3.12`, `python3.14` (+ config symlinks).
   `/opt/homebrew/bin` mtime **Oct 12 19:29:01 2026** — a Homebrew operation (upgrade/cleanup
   unlinking the unversioned `python3` symlink) removed it right at the outage window
   (now-file froze 2026-10-12T23:27:58Z).
4. **No log file at all**: `/tmp/session-shadow.log` does not exist → the process never
   launched even once; launchd fails at spawn. Exit 78 = launchd's "configuration error"
   (unexecutable/missing program), consistent.
5. **Script is healthy**: `python3 -m py_compile ~/.local/bin/session-shadow.py` →
   **SYNTAX OK** (checked with `/usr/bin/python3`). Not a code bug.

## Classification

**Config drift / transient env** — Homebrew dropped the unversioned `python3` symlink during
an Oct 12 ~19:29 operation; the plist hardcodes `/opt/homebrew/bin/python3`. The script itself
is unchanged (mtime Oct 12 17:44) and compiles clean.

## Minimal repair (one sentence)

Point `ProgramArguments[0]` at an existing interpreter — `/opt/homebrew/bin/python3.12` — then
`launchctl unload && launchctl load ~/Library/LaunchAgents/com.josh.session-shadow.plist` and
confirm a fresh `/tmp/session-shadow.log` and a now-file mtime newer than 2026-10-12T23:27:58Z.
(Alternative equally valid: `brew link python@3.12` to restore the unversioned symlink — no
plist edit — but the versioned pin is more drift-resistant against future brew upgrades.)

## Not verified

- Did not apply the repair (read-only mandate) — plist unchanged, job still down.
- Did not check whether OTHER launchd jobs reference `/opt/homebrew/bin/python3` (likely
  blast radius: any launch agent pinned to the unversioned path is also dead — worth one
  `grep -l 'opt/homebrew/bin/python3<' ~/Library/LaunchAgents/*.plist` sweep).

## Blast radius addendum (checked live)

`com.josh.agent-command-watcher` is the ONLY other launch agent pinned to
`/opt/homebrew/bin/python3` — launchctl shows it also at last exit 78, not running. Same root
cause, same one-line fix. Both jobs are down and neither has written logs.
