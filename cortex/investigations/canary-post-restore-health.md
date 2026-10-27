# em-delivery-canary post-restore health — 2026-10-22 (read-only investigation)

**VERDICT: HEALTHY. Quiet since 16:22Z = success, not silence.** Every run after
16:22Z executed and returned CANARY OK. The fleet jobfile restore was unrelated
to this canary; it never stopped running.

## 1. Cadence + log path
- launchd: `~/Library/LaunchAgents/com.josh.estate-monitor.delivery-canary.plist`
  (Label `com.josh.estate-monitor.delivery-canary`, currently loaded, last exit 0).
- Schedule: `StartInterval 900` (every 15 min), `RunAtLoad true`.
  Invokes `/usr/bin/python3 ~/orca/projects/estate-monitor/harness-hook/em-delivery-canary.py --once` (pinned interpreter).
- NOTE: there is a SECOND, unrelated canary: `com.josh.fleet.canary` (daily 06:05,
  fleet jobfile `~/.local/bin/fleet/jobs/canary.script` -> command-canary.py; its
  launchd log last touched Oct 10). All 82971161 alarms come from the estate-monitor one.
- Logs: `~/.local/state/estate-monitor/canary-launchd.log` (launchd stdout/err),
  `~/.local/state/estate-monitor/canary.log` (script's own), state `canary-state.json`.

## 2. Post-16:22Z run status
Log tail shows an unbroken OK chain — 16:37, 16:52, 17:07, 17:23, 17:38Z — each:
`handler recipe 82971161 running=true` → `POST ... HTTP 200` → `CANARY OK (15–19s)`.
State file: `consecutive_failures: 0`. Recipe verified running=true live.
The canary only posts alarms on FAIL; quiet = healthy probe, exactly as designed.

## 3. Why `wt recipes get` died rc=1 while direct wt succeeded
- The rc=1 is an uncaught Python traceback INSIDE wt at
  `urllib/request.py:1346 do_open` (CLT/Xcode Python 3.9) — a socket-level
  failure (URLError family), NOT an auth/profile/cwd failure. Auth failures die()
  cleanly ("no API token" / "profile not found"), never a traceback.
- NOT env/cwd/PATH/profile: replicated the exact launchd environment
  (`env -i HOME=... PATH=<plist PATH> /usr/bin/python3`) and ran the read-only
  probe today → rc=0, running=true. No proxy configured (`scutil --proxy` all 0).
- NOT the fleet jobfile corruption: wt is self-contained (`~/.workato/profiles`
  + Keychain token); the canary plist/script live outside `~/.local/bin/fleet/`.
  The canary kept succeeding straight through the corruption+restore window
  (fails 16:22Z, OK 16:37Z, restore ~16:45Z).
- Root cause of the 15-min burst (07:20–10:35Z, 14 consecutive) + singles
  (10-21T12:20Z, 10-22T01:22Z, 10-22T16:22Z): the Mac was in clamshell sleep ON
  BATTERY overnight (`pmset -g log`: charge 83–100%, DarkWake maintenance wakes
  every ~15 min). StartInterval fires land on brief DarkWakes where Wi-Fi is not
  yet up → wt's socket connect fails → traceback → alarm. Failure cadence
  (~15 min) matches both StartInterval and the DarkWake cycle. The 16:22Z
  mid-day single was an ordinary transient blip (recovered by 16:37Z).

## Findings / recommendations (no changes made)
1. DIAGNOSTICS GAP: `alarm()` truncates wt's stderr to 200 chars, cutting off
   the actual exception line (we can see WHERE it died, not WHY). Raise the
   `.strip()[:200]` cap in `wt_json` to ~1000 and include the last traceback line.
2. Sleep-correlated alarms are false alarms w.r.t. Workato (the handler was fine
   all night). Consider: only alarm on >=2 consecutive failures, or suppress
   alarms when `pmset -g batt` shows battery power / recent wake, or switch the
   plist to StartCalendarInterval + pmset `sleep prevented` during unattended
   hours. Batteries + 15-min launchd probes will keep re-firing this pattern.
3. No wt commands that mutate were run; launchd untouched; nothing changed.

*Investigator: bounded one-job session, 2026-10-22 ~17:4xZ. Evidence: launchd log
lines 2248–2400, canary-state.json, env-replica probe rc=0, pmset -g log.*
