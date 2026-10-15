# Blast radius: Oct-12 19:29 Homebrew unlink of /opt/homebrew/bin/python3

Investigated: 2026-10-13, read-only sweep. Verdict first:

**VERDICT: contained. Exactly 2 hard-broken consumers (the 2 known ones), everything else
either never resolved through the dead path or falls back to a working interpreter. One
systemic silent risk: bare `python3` in login-shell contexts quietly downgraded to Apple
3.9.6.**

## The unlink event

- `/opt/homebrew/bin/python3` — gone (confirmed `No such file or directory`).
- Cause signature: `/opt/homebrew/bin/python3.14` relinked **Oct 12 19:28** (Cellar
  python@3.14/3.14.8_2) — brew moved the unversioned `python3` symlink ownership at
  install time and did not re-link it. `python3.11`, `python3.12`, `python3.14` versioned
  symlinks all still exist and work.
- Working resolution today (login shell): `python3` → `/usr/bin/python3` = **3.9.6**
  (Xcode shim, confirmed runs).

## DEAD — references the missing absolute path (live-confirmed)

Both load fine but exit status **78 on every run** (`launchctl list`):

| # | Consumer | Detail |
|---|----------|--------|
| 1 | `com.josh.session-shadow` | ProgramArguments: `/opt/homebrew/bin/python3 ~/.local/bin/session-shadow.py` |
| 2 | `com.josh.agent-command-watcher` | ProgramArguments: `/opt/homebrew/bin/python3 ~/.local/bin/agent-command-watcher.py` |

Impact: cross-session awareness file `~/.claude/knowledge/now/josh-now.md` is not being
maintained; agent command watching is down. Fix = repoint both plists to a versioned
interpreter (`/opt/homebrew/bin/python3.14` or `/usr/bin/python3`) + `launchctl unload/load`.
(NOT done — this investigation was read-only.)

## AT-RISK — resolution silently changed, currently alive

The systemic class: bare `python3` / `#!/usr/bin/env python3`. Login PATH (`.zprofile`
`brew shellenv`) puts `/opt/homebrew/bin` first, so these resolved to brew python before
the unlink and to Apple 3.9.6 after. All script corpus is stdlib-only (import survey: json/
sys/os/argparse/pathlib/datetime/re/subprocess — zero third-party imports) and **0 files
fail 3.9 syntax** (in-memory compile check, all 102 knowledge/scripts .py + 2 hook .py +
2 local/bin .py). So they run, but on a python 3 major-versions older than intended.
Known 3.9-vs-3.11+ runtime traps that apply silently: `datetime.fromisoformat` not parsing
`Z`-suffixed timestamps (pre-3.11), no `datetime.UTC` alias, no `zoneinfo`-bundled tzdata
guarantees. Josh's standing rule "target the system Python version (no datetime.UTC)"
already encodes this trap class — scripts comply, but anything new written against a
modern interpreter will not.

| # | Consumer | Resolution context |
|---|----------|-------------------|
| 3 | Login/interactive shells | bare `python3` → now 3.9.6 (was brew) |
| 4 | `~/.claude/settings.json` hook commands (4): `airo-error-guide.py`, `session-drop-guard.py`, `lint-changed.py`, `morning-digest.py` | bare `python3`, resolved via Claude session env (login PATH) |
| 5 | MCP server wrappers launched from login shell: `~/.local/bin/brain-mcp` (`env python3` shebang), `~/.local/bin/kb` (kb-mcp-server.sh chain) | both reported Connected at session start — alive on 3.9.6 |
| 6 | CLI wrappers with bare `python3`: `wt`, `wt-route`, `brain-dashboard`, `dream-mini`, `harness-backup`, `prod-bypass`, `gwsemantic/*.sh` | login-shell invocations now 3.9.6 |
| 7 | `com.josh.estate-monitor.triage-watcher` + `delivery-canary` plists | main script pinned to `/usr/bin/python3` (safe) but their `EnvironmentVariables` PATH includes `/opt/homebrew/bin` — any bare-`python3` subprocess inside `em-*.py` flipped to 3.9.6 |
| 8 | `#!/usr/bin/env python3` shebangs, ~106 scripts total (`knowledge/scripts/*.py` ×98, hooks ×2, local/bin ×2, plus `fleet/run-job.sh` bare `python3` ×2 → `atomic_io.py`) | direct execution (`./x.py`) or PATH-carrying contexts resolve per caller env; launchd-context ones see launchd default PATH (see unaffected note) |

## UNAFFECTED

| # | Consumer | Why |
|---|----------|-----|
| 9 | 7 plists invoking `/usr/bin/python3` absolutely: `com.josh.brain-dashboard`, `com.josh.fleet.health`, `com.josh.fleet.ops-visibility`, `com.josh.workato-docs-watch`, `com.josh.estate-monitor.{triage-watcher,delivery-canary}` (main scripts) | never touched brew python; `/usr/bin/python3` works (3.9.6) |
| 10 | 4 venv-based plists: `com.harness.sync`, `com.josh.kb-daemon`, `com.josh.workato-kb-sync`, `com.josh.kb-benchmark`, `com.josh.workato-kb-digest` | venv interpreters symlink to the **versioned** `/opt/homebrew/opt/python@3.12` chain — intact; live-confirmed (`kb-daemon` running pid 1049; both venvs executed 3.12.14 during sweep) |
| 11 | Fleet plists without a PATH env dict (majority of `com.josh.fleet.*`) | launchd default PATH (`/usr/bin:/bin:/usr/sbin:/sbin`) never contained brew — their bare `python3` resolved to `/usr/bin/python3` before AND after the unlink |
| 12 | `co.baseten.switch.{door,router}` | versioned brew path (`/opt/homebrew/opt/baseten-switch/bin/...`), running (pids 1035/1040) |
| 13 | crontab | empty — zero cron consumers |
| 14 | `/Library/LaunchAgents` | no hits |
| 15 | `~/.claude/*.json` configs, agents, skills | no references to the dead path |

## Coverage notes / unverified

- `/Library/LaunchDaemons`: grep produced no output but the directory may be
  permission-limited to this session — treat system-daemon coverage as **unverified**.
- Runtime (not syntax) 3.9 compatibility of the ~106-script corpus was inferred from
  import survey + compile check + Josh's existing system-python rule; individual scripts
  were not executed (read-only constraint).
- Nothing was modified: no plist edits, no relink, no cache writes (syntax check was
  in-memory; venv probes ran with `-c` only).

## Recommended fix (NOT applied)

1. Repoint both dead plists to a versioned interpreter — `/opt/homebrew/bin/python3.14`
   (or pin `python3.12` for consistency with the venvs) — then `launchctl unload/load` both.
2. Optional hardening: replace bare `python3` with `python3.12` (or absolute versioned
   paths) in settings.json hook commands and the login-shell-facing wrappers, so the next
   brew symlink shuffle cannot silently downgrade the fleet to 3.9.6.
3. `brew link --overwrite python@3.14` would restore the unversioned symlink — but that is
   a prod-write-class change and was not tested.
