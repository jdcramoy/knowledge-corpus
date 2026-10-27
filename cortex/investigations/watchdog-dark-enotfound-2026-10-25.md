# Watchdog dark — ENOTFOUND escalation 2026-10-24 01:58 — findings

Investigated 2026-10-25 ~08:57 SGT (headless dispatch, read-only; wrote only this file).
VERDICT: transient fleet-wide network outage at fire time, NOT network-early-fire, NOT config break. Config is healthy; next scheduled fire has not been missed — no structural fix needed.

## (a) What the job is

- Label `com.josh.fleet.watchdog` — plist `~/Library/LaunchAgents/com.josh.fleet.watchdog.plist`
  (mtime Oct 7 17:48, never edited since). Runs `/bin/bash ~/.local/bin/fleet/run-job.sh watchdog`,
  daily at **23:13 local** (StartCalendarInterval Hour=23 Min=13). launchd stderr/stdout →
  `~/.local/state/fleet/watchdog.launchd.log`. launchctl state: not running, last exit code 0
  (run-job.sh exits 0 even on escalation by design — "never die loudly", the ledger is the alarm).
- Companion alarm: `com.josh.fleet.watchdog-liveness` — `watchdog-liveness.py`, daily **03:43 local**,
  output `/tmp/watchdog-liveness.log`.
- Wrapper `run-job.sh` (deployed copy identical to canonical `~/.claude/knowledge/config/fleet/`
  — diff clean, so the three-copy deploy checklist holds). Env `jobs/watchdog.env` fixed Oct 23
  20:18: `JOB_CWD="$HOME/orca/workspaces/workbench/Workday-Development"` (previously the literal
  template string `/Users/YOUR-USER/...`). TIMEOUT=1800. No probe file.

## (b) Recent run history (watchdog.log + fleet-validation.jsonl + heartbeat.jsonl)

- 10-18 23:19 ✓ done validated · 10-19 23:17 ✓ done validated
- **10-20 and 10-21: dark — `cwd fail` (literal `/Users/YOUR-USER/...` env template bug).** Old
  script died on the cd before claude spawned; 3 bare cd-error lines in watchdog.launchd.log
  (stderr capture; nothing newer than Oct 22 in that file — stderr has been silent since the fix).
- 10-22 17:10 ✓ done validated (manual catch-up) · 10-22 23:13 ✓ done validated → report
  `watchdog-reports/2026-10-22.md` (newest on disk).
- **10-23 23:13 EDT: start → `API Error: Can't reach the API server (ENOTFOUND)` → retry once
  00:32 → ENOTFOUND again → 01:58 `VALIDATION FAILED after retry (ran rc=1)` escalated.**
  Ledger row 2026-10-24T05:58:48Z retry-exhausted. Attempt capture `watchdog.log.run` holds the
  ENOTFOUND text. Heartbeat: last success 10-23T03:17Z.
- No further runs since — see (c): the next fire hasn't arrived yet.

## (c) Signature: transient network outage, not early-fire, not config break

- **Fleet-wide, not watchdog-specific:** the identical ENOTFOUND string appears in **14** fleet
  job logs (antigen, brief, cortex ×7, cost-governor, dreamer, docs-watch, evidence, gardener,
  harness-fix, healer, loadout, ops-autopsy, project-dreamer, watchdog). Whole fleet went dark
  the same night. Cortex's own attention queue already carries "watchdog dark 3 nights" as a
  known item.
- **Everything pre-network worked:** claude spawned, env repair ran, cwd fallback worked
  (env fix Oct 23 20:18 predates the failure). Failure is DNS resolution at the API call only.
- **Split test on time, not assets:** the identical wrapper/binary ran validated-clean on 10-22
  (twice). Network is healthy now (`dscacheutil` resolves api.anthropic.com); cortex ran
  **done validated 2026-10-24 11:38 and again 10-25 08:56** — the outage ended during 10-24
  daytime.
- **Why the night failed (root cause):** the machine was traveling / off-network on battery.
  pmset: Oct 24 night at **Charge:1%**, cycling SleepService dark-wakes, fully asleep
  00:44–08:15, woke on **acattach** (plugged in) 08:15. And the timezone moved: ledger
  (`date -u`) vs log (`date` local) stamps during the failure give **UTC-4**; `/etc/localtime`
  re-linked to **Asia/Singapore** at 08:17:34 today. Josh is in transit US-East → Singapore.
- **No fire has been skipped since the failure.** 23:13 fires in the machine's own local time;
  with the TZ flip the next 23:13 (Singapore) is **tonight ~23:13 SGT** — still in the future.
  The "dark since 10-24" appearance is the TZ travel + the 10-23 failure, not missed fires.
  Liveness re-alarm 10-25 00:20Z (08:20 SGT) = launchd firing the missed 03:43 liveness job
  right after the TZ change; it will re-alarm tomorrow 03:43 SGT unless a report lands tonight.

## (d) Smallest fix

1. **Nothing structural.** The 10-20/21 config bugs are already fixed (env template Oct 23 20:18;
   cwd fallback in run-job.sh); deploy copies identical; escalation + liveness alarm worked exactly
   as designed. Machine is awake, on AC, DNS green.
2. **Optional one-off catch-up (Josh's go — costs tokens):** `launchctl kickstart -k
   gui/$(id -u)/com.josh.fleet.watchdog` to land today's report and clear the alarm before
   tomorrow 03:43 SGT. Otherwise it self-heals at tonight's 23:13 SGT fire.
3. Optional hardening (defer, not needed now): a `watchdog.probe` network gate (exit 7 on DNS
   failure → zero-token `skipped-no-signal` row, liveness stays green on travel nights).
4. Minor/unverified: TIMEOUT=1800 did not bound attempts (79 and 86 min vs the 30-min perl-alarm
   cap — claude's internal API-retry loop outlived the alarm; mechanism not confirmed). Cosmetic —
   validation and escalation still fired correctly. Not investigated further per read-only scope.

Nothing unverified in the verdict itself; the only unverified mechanism is the TIMEOUT item in (d)4.
