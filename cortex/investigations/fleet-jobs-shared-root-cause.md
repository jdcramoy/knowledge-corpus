# Fleet jobs "shared root cause" investigation — restore-drill / wave3-nightly / frontier-nightly / turn-audit

Investigated: 2026-10-13. Scope: the four 2026-10-12 `fleet-validation.jsonl` rows
(`stub rc=2` / `stub rc=127` / `stub rc=0` / `stub rc=1`, all `retry-exhausted`).
Read-only: plists in `~/Library/LaunchAgents`, wrapper `~/.local/bin/fleet/run-job.sh`,
job definitions `~/.local/bin/fleet/jobs/`, logs in `~/.local/state/fleet/`, ledger
`~/.claude/knowledge/garden-reports/fleet-validation.jsonl` + `heartbeat.jsonl`.

## Verdict

**NOT one shared root cause. No fix is needed for three of the four — they already
self-healed. Only restore-drill is still failing, and for a reason unique to it.**

The four rows LOOK like one cluster (same day, same "double stub; watchdog escalates"
note) but resolve to three distinct mechanisms:

| job | exec path (all identical) | failure | mechanism | still broken? |
|---|---|---|---|---|
| restore-drill | `/bin/bash ~/.local/bin/fleet/run-job.sh restore-drill` | stub rc=2 | NOT a stub — job runs, writes report, script exits 2 by design (viability RED); wrapper mislabels any nonzero rc as "stub" | **YES** |
| wave3-nightly | same wrapper, arg `wave3-nightly` | stub rc=127 | `jobs/wave3-nightly.script` did not exist at fire time (08:17); `bash <missing file>` = 127. File created 08:19. Self-healed | no (validated 10-12 12:19, 10-13 09:07) |
| frontier-nightly | same wrapper, arg `frontier-nightly` | stub rc=0 | same missing/broken-script-at-fire-time class; script landed 08:23, rerun at 08:23:04 validated clean. Self-healed | no (validated 10-12 12:24, 10-13 08:44) |
| turn-audit | same wrapper, arg `turn-audit` | stub rc=1 | `jobs/turn-audit.env` missing at fire time → `source` failed → `JOB_CWD: unbound variable` → fell through to default CLAUDE_JOB=yes mode → `cat turn-audit.prompt` (also absent) → `claude -p` with no input → "Input must be provided…" rc=1. env+script landed 13:39–13:41; run at 13:41:04 validated. Self-healed | no (validated 10-12 17:41, 10-13 11:07) |

## Per-job detail

**Exec path (identical for all four).** Each plist is
`~/Library/LaunchAgents/com.josh.fleet.<name>.plist` →
`ProgramArguments = [/bin/bash, ~/.local/bin/fleet/run-job.sh, <name>]`,
`StartCalendarInterval` at 04:37 / 05:07 / 04:43 / Mon-07:07 respectively, both
stdout+stderr → `~/.local/state/fleet/<name>.launchd.log`. The wrapper exists and is
executable; every per-job file now exists in both the kit copy
(`~/Documents/agentic-workato-kit/bin/fleet/jobs/`) and the live copy
(`~/.local/bin/fleet/jobs/`).

**PATH/env is NOT the cause.** The launchd minimal-PATH problem was root-caused and
fixed inside the wrapper on 2026-10-08 (it exports `$HOME/.local/bin` into PATH and
evals the ANTHROPIC_/WORKATO_/FIREWORKS_ lines out of `~/.zshenv` before spawning).
All four jobs run in `CLAUDE_JOB=no` mode (direct `bash <script>`, zero claude spawn),
so the claude binary/gateway env never even matters for them.

**rc mechanisms, one by one:**
- **rc=127 (wave3):** `run_job()` runs `perl alarm … bash $JOB.script`; when the script
  file doesn't exist bash exits 127 (command not found). `attempt()` → "stub rc=127".
  Log lines 173–178 of `wave3-nightly.log` show three "No such file or directory"
  errors at 08:17:06, then VALIDATION FAILED. Script mtime: Oct 12 08:19 — two minutes
  after the fire.
- **rc=0 (frontier):** rc=0 + no heartbeat delta + empty `$OUT` = the wrapper's literal
  definition of a STUB. Consistent with the script existing in a broken/empty form (or
  a pre-replacement placeholder) during the 08:19–08:22 attempts; replaced at 08:23 and
  the immediate manual rerun at 08:23:04 validated. Same deploy-timing class as wave3.
- **rc=1 (turn-audit):** `turn-audit.launchd.log` is the smoking gun, verbatim:
  `run-job.sh: line 66: …/turn-audit.env: No such file or directory`,
  `line 69: JOB_CWD: unbound variable`,
  `cat: …/turn-audit.prompt: No such file or directory`,
  `Error: Input must be provided either through stdin or as a prompt argument when using --print`.
  Missing .env → wrapper kept default `CLAUDE_JOB=yes` → missing .prompt → empty claude
  prompt → claude exits 1.
- **rc=2 (restore-drill):** the ONLY real defect still live. `jobs/restore-drill.script`
  is one line: `python3 ~/.claude/knowledge/scripts/restore-drill.py`. That script
  documents its own contract: "exit 0 = viable-enough, nonzero = red". The 10-13 run
  did REAL work (full report at `garden-reports/restore-drill-2026-10-13.md`, viability
  67% 4/6 — RED on md-frontmatter check and a corrupt JSON snapshot) and exited 2.
  The wrapper's `attempt()` (`run-job.sh`: `if [ "$rc" -eq 0 ] && validated`) treats any
  nonzero rc as a stub regardless of evidence, so a legitimately-RED drill is recorded
  as "stub rc=2, retry-exhausted" and re-fires daily (10-12 08:37 **and** 10-13 08:37).
  It also has NO heartbeat rows — it can never earn one while the report is RED.

## One fix or four?

**Four separate findings, two of which are already closed:**

1. **No shared fix.** The tempting single fix — "PATH/env in launchd context" — is
   already in place (wrapper lines under the `launchd environment repair` comment) and
   provably not implicated: three of the four failures happened in zero-LLM mode where
   PATH/gateway env is irrelevant, and the missing files, not the environment, are what
   failed.
2. **Closed (wave3, frontier, turn-audit):** the 2026-10-12 cluster was the same CLASS —
   job-definition files (`<job>.script` / `<job>.env`) landed in
   `~/.local/bin/fleet/jobs/` minutes AFTER the plists first fired them (a small replay
   of the 2026-10-10 partial-deploy incident). Each self-healed on its next fire or
   manual rerun; all three have fresh validated heartbeats on 2026-10-13. Fix for the
   class, if desired: after deploying new job files, `launchctl kickstart` once or
   accept the first-night escalation — the wrapper's validation did exactly what it was
   designed to do.
3. **Open (restore-drill) — wrapper contract bug:** `attempt()` conflates "script
   failed" with "stub". Suggested fix (one line in `run-job.sh`): treat a run as valid
   when evidence exists even on nonzero rc — e.g. record `result: "ran rc=2"` instead of
   `stub rc=2` when `$OUT` is non-empty — so a RED restore-drill reads as a real,
   failing drill, not a stub. Separately, the drill being RED is genuine signal (47
   files missing from the 10-12 backup, `projects/event-process-mcp.md` frontmatter, a
   corrupt `regression-canon/snapshots/recipe-82272892-*.json`) and needs its own
   triage — that is the drill WORKING, not the drill being broken.

## Evidence pointers

- Ledger rows: `garden-reports/fleet-validation.jsonl` ts 2026-10-12T08:37:11Z /
  12:17:06Z / 12:22:33Z / 17:40:15Z, plus recurrence 2026-10-13T08:37:13Z (restore-drill only).
- Recovery heartbeats: `garden-reports/heartbeat.jsonl` 2026-10-12T12:19:24Z (wave3),
  12:24:50Z (frontier), 17:41:08Z (turn-audit); 2026-10-13 rows for all three; none for restore-drill.
- Logs: `~/.local/state/fleet/{wave3-nightly,frontier-nightly,turn-audit}.log` (start/
  VALIDATION lines at the timestamps above), `~/.local/state/fleet/turn-audit.launchd.log`
  (the .env-missing chain), `~/.local/state/fleet/restore-drill.log` (full drill output
  + "VALIDATION FAILED after retry (stub rc=2)").
- Files now present: `~/.local/bin/fleet/jobs/{restore-drill,wave3-nightly,frontier-nightly,turn-audit}.{env,script}`
  (mtimes Oct 11 05:26 / Oct 12 08:19 / Oct 12 08:23 / Oct 12 13:39–13:41 respectively).
