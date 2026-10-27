# ops-path-class-sweep — bare-`wt` + minimal-PATH failure-class sweep (2026-10-23)

**Question:** does any OTHER spawned process share the ops-collector failure class
(calls bare `wt`, launched without `~/.local/bin` on PATH → `FileNotFoundError`)?

**Failure class definition:** subprocess argv contains bare `"wt"` (or `["/usr/bin/env","wt"]`,
or a bare-`"wt"` fallback default) AND the launch context is launchd/nohup with the launchd
default PATH (`/usr/bin:/bin:/usr/sbin:/sbin` — no `~/.local/bin`, wt lives at
`~/.local/bin/wt` since the 2026-10-18 move).

**launchd PATH baseline (verified):** `launchctl` user agents without `EnvironmentVariables.PATH`
get the minimal default. Of 71 plists in `~/Library/LaunchAgents`, only 4 set a PATH env:
`co.baseten.switch.{door,router}` (incl. `~/.local/bin`, but no wt use),
`com.josh.estate-monitor.delivery-canary` + `.triage-watcher` (incl. `~/.local/bin`),
`com.josh.kb-receipts-gate` (incl. `~/.local/bin` as last entry).

---

## SITE-BY-SITE VERDICTS

### VULNERABLE

**1. `~/.claude/knowledge/scripts/ops-collector.py:72` — VULNERABLE (the index case, confirmed)**
- Code: `cmd = ["wt"] + args + ["--profile", profile]` (bare `wt`, no WT_BIN override, no which()).
- Launch chain: `com.josh.fleet.ops-visibility.plist` → `/usr/bin/python3 ops-server.py --serve`
  (no PATH env in plist) → `ops-server.py:282` `subprocess.Popen([sys.executable, str(COLLECTOR), "collect"])`
  → collector inherits the minimal launchd PATH → `FileNotFoundError` at subprocess.run.
- PATH hardening: NONE in the plist, NONE in ops-server.py's spawn env, NONE in the collector.
- Failure mode: `except (subprocess.TimeoutExpired, OSError)` at line 76 swallows the
  FileNotFoundError and returns `(False, "", str(exc))` — so the server keeps serving and the
  dashboard goes quietly stale rather than crashing. Silent-staleness, not a crash.
- Note: ops-server.py itself is NOT a wt spawn site — both its spawns (DASHGEN, COLLECTOR) use
  `sys.executable` + absolute script paths, safe invocation, unhardened PATH downstream.

### SAFE (hardened at the call site or by the launcher)

**2. `~/.claude/knowledge/scripts/workato-health.py:74` — SAFE**
- `WT = os.environ.get("WT_BIN", os.path.expanduser("~/.local/bin/wt"))` — absolute fallback.
- Launched DIRECTLY by `com.josh.fleet.health.plist` (`/usr/bin/python3`, no PATH env) — but the
  abs fallback defeats the minimal PATH. The strongest proof this pattern works under launchd:
  this job runs on the same PATH regime as ops-collector and survives it.

**3. `~/.claude/knowledge/scripts/gw_semantic_dashboard_snapshot.py:28` — SAFE**
- `WT = shutil.which("wt") or "~/.local/bin/wt"` + comment "launchd PATH is
  minimal; resolve wt explicitly (broke 2026-10-18 when wt moved to ~/.local/bin)".
- Launched by `com.josh.gw-semantic-dashboard.plist` (`/bin/bash -c /usr/bin/python3 …`, no PATH
  env). Already broke and was fixed — the canonical repair to copy for site #1.

**4. `~/.claude/knowledge/scripts/brier-resolve.py:34` — SAFE**
- `WT = os.path.expanduser("~/.local/bin/wt")`. Launched via fleet `frontier-nightly.script:8`
  (`python3 $HOME/.claude/knowledge/scripts/brier-resolve.py`) inside run-job.sh.

**5. `~/.claude/knowledge/scripts/canonize-failure.py:35` — SAFE** (`WT = os.path.expanduser('~/.local/bin/wt')`; Claude-session invocation only).

**6. `~/.claude/knowledge/scripts/external-edit-sweep.py:46` — SAFE** (`os.environ.get("WT_BIN", expanduser("~/.local/bin/wt"))`; Claude-session invocation only).

**7. `~/.claude/knowledge/scripts/fleet-config-receipts.py:50` — SAFE** (`WT_BIN` env override with `~/.local/bin/wt` fallback).

**8. `~/.claude/knowledge/scripts/incident-convergence.py:66,311,316` — SAFE**
- `WT_BIN = os.path.join(HOME, ".local/bin/wt")`, plus an explicit `os.path.exists` guard that
  degrades to a "wt CLI not found" note instead of a raise.

**9. `~/orca/projects/estate-monitor/harness-hook/em-delivery-canary.py:89` — SAFE**
- `WT = "~/.local/bin/wt"` hard-coded; AND its plist sets
  `PATH=~/.local/bin:…`. Double-hardened.

**10. `~/orca/projects/estate-monitor/harness-hook/em-triage-watcher.py:40` — SAFE**
- `WT = "~/.local/bin/wt"` hard-coded; plist sets PATH. Double-hardened.

**11. All ~30 fleet claude jobs via `~/.local/bin/fleet/run-job.sh:94` — SAFE**
- Line 94: `export PATH="$HOME/.local/bin:$PATH"`, line 96 sources ANTHROPIC_/WORKATO_ export
  lines from `~/.zshenv`. Every `com.josh.fleet.*` plist that runs a claude session goes through
  this, so any wt call inside those sessions resolves. This is the launcher-level fix.

**12. `~/.local/bin/agent-command-watcher.py:146` — SAFE (non-exec path)**
- Does not exec wt; it loads the wt source file directly via SourceFileLoader with the absolute
  path `~/.local/bin/wt`. Its python3.14 binary path is absolute in the plist.

**13. `~/Documents/ChatGPT/Google Workspace MCP/scripts/registry-backup-daily.sh:15` — SAFE (not wt)**
- No wt use; hardens PATH for node (`/opt/homebrew/bin`) with its own launchd-PATH comment.

### SAFE-BY-LAUNCH-CONTEXT (bare `wt` at the call site, but every current launch path has hardened PATH — LATENT RISK if ever launchd-launched directly)

**14. `~/.claude/knowledge/scripts/claims-sweep.py:128` — SAFE-BY-LAUNCH-CONTEXT (latent)**
- `subprocess.run(["/usr/bin/env", "wt", "recipes", "get", rid, "--raw"])` — PATH-dependent.
- Only scripted caller found: `morning-digest.py:51` (`subprocess.run([sys.executable, …claims-sweep.py, "--json"])`),
  which itself runs inside fleet claude sessions (run-job.sh PATH). Interactive/Claude Bash
  invocations also carry the login PATH. No launchd/cron launcher found.
- Latent: `/usr/bin/env wt` dies under bare launchd PATH. Catches the failure (degrades row to
  UNVERIFIED) rather than crashing.

**15. `~/.claude/knowledge/scripts/changelog.py:49` — SAFE-BY-LAUNCH-CONTEXT (latent)**
- `WT = os.environ.get("WT_BIN", "wt")` — bare fallback when WT_BIN unset.
- No scripted launcher found anywhere (fleet configs, hooks, plists, crontab) — Claude-session
  invocations only. Dies with a clear `wt not found` message (line 90) if ever launchd-run bare.

**16. `~/.claude/knowledge/scripts/env-diff.py:54` — SAFE-BY-LAUNCH-CONTEXT (latent)**
- `PROFILES = {"dev": ["wt"], "prod": ["wt-prod"]}` — bare binaries.
- No scripted launcher found; Claude-session/interactive only. Same latent exposure.

**17. `~/.claude/knowledge/scripts/evidence_ref_check.py:43` — SAFE-BY-LAUNCH-CONTEXT (latent)**
- `WT = "wt"` bare; catches FileNotFoundError explicitly (line 112) and returns a degraded
  verdict instead of raising. No scripted launcher found.

**18. `~/.claude/knowledge/scripts/import-remap.py:57-58` — SAFE-BY-LAUNCH-CONTEXT (latent)**
- `cmd = ["wt-prod" if profile == "wt-prod" else profile] + args` — bare, and no
  FileNotFoundError handler seen. Interactive/claude-session use only (Josh-run remediation tool).

### NOT-A-SPAWN (checked, no wt execution)

- `~/.claude/knowledge/scripts/brain-dashboard.py` — wt appears only in a docstring (line 922);
  subprocess calls are `["python3", …abs…]` (line 392), `["git", …]` (line 445), `["open", OUT]`
  (line 978). git/python3 resolve fine under launchd PATH (/usr/bin). Launched by
  `com.josh.brain-dashboard.plist` directly — safe on those specifics.
- `~/.claude/knowledge/scripts/efficiency-dash.py:173,286` — PARSES wt command text out of
  transcripts; never executes wt. (`effdash-daily.sh` wrapper has no wt either.)
- `~/.claude/knowledge/scripts/watchdog-liveness.py:86,105` — spawns `sys.executable` + abs
  paths (BUS_POST, ATOMIC_IO) only. No wt.
- `~/.local/bin/session-shadow.py:773-790` — git subprocesses only.
- `~/.claude/knowledge/scripts/knowledge-write-stash.py`, `workato-docs-watch.py`,
  `nightly-receipts-gate.py`, `spend-refresh.py`, `spend-ingest.py` — no wt references at all.
- `dream-mini.sh`, `effdash-daily.sh`, `harness-graph/refresh-pages.sh`,
  `benchmark-smoke-daily.sh` — no wt.

### Launch surfaces with NO jobs

- **crontab: EMPTY** (`crontab -l` returns nothing). No `/etc/periodic` jobs.
- `/Library/LaunchDaemons` + `/Library/LaunchAgents` are all vendor/IT (Docker, Jamf,
  SentinelOne, Zscaler, Google, Ollama) — none reference wt or Josh scripts.

---

## SUMMARY

| Verdict | Count | Sites |
|---|---|---|
| VULNERABLE | 1 | ops-collector.py:72 (via ops-server.py spawn, launchd minimal PATH) |
| SAFE (hardened) | 12 | workato-health, gw_semantic_dashboard_snapshot, brier-resolve, canonize-failure, external-edit-sweep, fleet-config-receipts, incident-convergence, em-delivery-canary, em-triage-watcher, run-job.sh (fleet-wide), agent-command-watcher, registry-backup-daily |
| SAFE-BY-LAUNCH-CONTEXT (latent) | 5 | claims-sweep.py:128, changelog.py:49, env-diff.py:54, evidence_ref_check.py:43, import-remap.py:58 |
| NOT-A-SPAWN | 13 | brain-dashboard, efficiency-dash, watchdog-liveness, session-shadow, knowledge-write-stash, workato-docs-watch, nightly-receipts-gate, spend-refresh, spend-ingest, dream-mini.sh, effdash-daily.sh, refresh-pages.sh, benchmark-smoke-daily.sh |

## CONCLUSION

**Exactly ONE live site in the failure class: `ops-collector.py:72`.** It is the only bare-`wt`
spawn that actually executes under an unhardened launchd PATH today (ops-server.py →
`com.josh.fleet.ops-visibility.plist`, no EnvironmentVariables.PATH). Its OSError handler masks
the failure as silent dashboard staleness, which is why it presented as "missing data" rather
than an error.

The rest of the estate is either (a) call-site-hardened with an `expanduser("~/.local/bin/wt")`
fallback — the pattern gw_semantic_dashboard_snapshot.py adopted after the 2026-10-18 wt move,
and workato-health.py uses under the exact same launchd regime — or (b) shielded by
run-job.sh:94's PATH export at the fleet-launcher level. Five scripts keep bare-`wt` defaults
but have no launchd launcher; they are latent-only.

**Fix pattern to copy (read-only sweep — not applied):**
`WT = shutil.which("wt") or os.path.expanduser("~/.local/bin/wt")` at ops-collector.py:72, or
add `EnvironmentVariables.PATH` including `~/.local/bin` to com.josh.fleet.ops-visibility.plist
(then `launchctl unload/load`), or both (belt and suspenders). The 5 latent sites can be
normalized to the same one-liner opportunistically.

*Scope: read-only. Nothing modified except this report file.*
