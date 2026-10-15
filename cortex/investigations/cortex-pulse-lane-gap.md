# Cortex pulse lane gap — 2026-10-10T07:37Z → 2026-10-11T09:08Z (~25.5h)

Investigated 2026-10-11 ~09:15Z, read-only. STAGED COPY — the primary write to
~/.claude/knowledge/cortex/investigations/cortex-pulse-lane-gap.md was DENIED by the
sensitive-path gate (5th occurrence of the cortex-pulse-write-gate class). Promote with:
  cp /tmp/cortex-investigation-staging/cortex-pulse-lane-gap.md \
     ~/.claude/knowledge/cortex/investigations/cortex-pulse-lane-gap.md

## Verdict

The machine never slept. The gap was a two-stage breakage of the fleet runner itself
(~/.local/bin/fleet/), not sleep, not launchd unloading, and not the model gateway:

- Era 1 — runner missing (2026-10-10 ~09:29Z → ~22:29Z, 14 hourly fires): the launchd job
  fired hourly but run-job.sh did not exist. Bash printed "run-job.sh: No such file or
  directory" to launchd's stderr and died before any script logic. Zero trace in
  cortex.log — this is why the gap reads as "did not fire" when it actually fired 14 times.
- Era 2 — jobs/ env missing (2026-10-10 23:29Z → 2026-10-11 08:29Z, 10 hourly fires):
  run-job.sh restored, but jobs/cortex.env absent. Every fire wrote "cortex: start" to
  cortex.log, then died at line 46 (cd "$JOB_CWD" → JOB_CWD: unbound variable, exit 1)
  because line 43's `source "$JOB.env"` no-ops on a missing file and set -u kills at the
  first reference. Claude was never launched. 10 start lines with no done in between.
- Recovery (2026-10-11 09:07–09:08Z): the full jobs/ dir was redeployed (all jobs/*.env
  and *.script restamped 05:07 local = 09:07Z) and a run started at 05:08:00 local
  (09:08Z) — a non-anchor minute, i.e. a manual kick right after the repair, not the
  hourly scheduler. Heartbeat resumed 09:10:27Z.

## (a) launchd job state

- launchctl list: "-  1  com.josh.fleet.cortex" — loaded, last exit code 1.
- launchctl print gui/501/com.josh.fleet.cortex: state = not running, runs = 24,
  last exit code = 1, run interval = 3600 seconds, plist at
  ~/Library/LaunchAgents/com.josh.fleet.cortex.plist.
- runs = 24 lines up exactly with the post-reload fire count (14 + 10); the last exit
  code 1 is the 08:29Z 10-11 env-era fire. The heartbeat ledger confirms the 09:08Z run
  succeeded (09:10:27Z model check-in + 09:10:33Z mechanical line).

## (b) Schedule and anchor evidence

- StartInterval = 3600, RunAtLoad = false, no StartCalendarInterval. launchctl print
  exposes no KnownPastFires/System state — launchd does not keep that surface for
  interval jobs (calendar jobs only).
- The plist mtime is 2026-10-10 08:29:15Z (04:29:15 EDT) — 52 minutes after the last
  good pulse (07:37:22Z). Pre-gap fires anchored around :15–:37 past the hour (heartbeat
  ts pattern); every post-edit fire anchored at :29 (cortex.log start lines at :29:16–
  :29:18). The rewrite+reload moved the fire anchor and coincides with the breakage
  window opening. The plist content itself is fine; whatever did the maintenance at
  08:29Z also (staged) removed the runner files the job points at.

## (c) Sleep/wake — ruled out

- pmset -g log: zero Entering Sleep / Wake from / SleepService events on 2026-10-10 and
  2026-10-11. Most recent machine sleep in the log: 2026-10-07 13:34 EDT.
- Display-off inside the window (10:28Z → 21:24Z on 10-10) is not sleep — the 14 hourly
  era-1 fires landed on cadence straight through that display-off period, which launchd
  could not do on a sleeping machine.
- The Mac was running the entire gap. The wake-boundary hypothesis does not hold; nothing
  in the power timeline lines up with 07:37Z or 09:08Z.

## (d) Process stderr/stdout and crash logs

- /tmp/fleet-cortex.launchd.log (birthtime 2026-10-09 13:54 local, mtime 2026-10-11
  04:29 local) contains exactly the failure eras and nothing else: 14x "run-job.sh: No
  such file or directory", then 11x the pair "line 43: .../jobs/cortex.env: No such file
  or directory" + "line 46: JOB_CWD: unbound variable". (11 env pairs vs 10 accounted
  fires — off by one, likely a duplicate/counter quirk; not load-bearing.)
- No crash reports: ~/Library/Logs/DiagnosticReports/ holds only 1Password and
  SkyComputerUseService reports from 2026-10-05. No claude or bash crashes — the process
  never got that far.

## (e) The 07:35Z 10-10 autopsy dispatch with no artifact

The dispatch completed — its findings exist in full.
dispatch-20261010-073537-82862205-postfix-autopsy.log (4.3KB) opens with:
  "The write was denied by the sensitive-path gate — per the dispatch instructions, here
   are the full findings inline: BEGIN_FINDINGS ..."
The subagent finished the 82862205 post-fix-failure autopsy (verdict: trace-less
test-harness aborts, canon line 47, not a recipe regression) but its Write to
investigations/ was denied by the sensitive-path gate — 4th occurrence of the
cortex-pulse-write-gate class — and it dumped the complete findings inline into the
dispatch log instead. Nothing promoted them afterward, so no artifact landed. The
findings are recoverable verbatim from that log (precedent: the 07:37Z pulse rescued
stranded lineage findings into collectorlineage.md the same way). The 09:08Z pulse
filed triage card "cortex-dispatch-no-artifact" for exactly this.

Related lane note: the sibling 09:10Z dispatches (pulselane, gwsentinel) both first died
with "[claude-code:unrecognized_model] fireworks/glm-5.3-flash" (transient gateway/SDK
error at 09:10Z); the gwsentinel re-run recovered and wrote its artifact; this
investigation is the pulselane retry.

## Contract holes this exposed

1. Pre-launch bash failures bypass run-job v2's validation contract entirely. The
   stub-detection code never runs when the script dies at line 43/46, so 10 consecutive
   dead fires wrote nothing to garden-reports/fleet-validation.jsonl (verified: zero
   cortex entries in that ledger for the gap). The watchdog never escalated.
2. Heartbeat absence is not monitored. Nothing consumes heartbeat.jsonl staleness
   hourly; the pulse lane can go dark for a day with no mechanical alarm. (The 09:08Z
   pulse flagged its own 26.5h-stale queue; no local monitor did.)
3. The deploy that removed the runner was two-stage and unlogged: run-job.sh restored
   10-10 18:40 local without jobs/, jobs/ restored 10-11 05:07 local. Who/what ran it
   is unverified — no zsh-history or log trace found for either step.

## Not verified

- Who or what performed the 08:29Z 10-10 plist rewrite + reload and the two-stage runner
  deploy (no log or history trace found).
- The exact cause of the 11th env-error pair in the launchd log vs 10 accounted fires.
- Whether the 09:08Z run was a launchctl kickstart or a direct run-job.sh invocation
  (timing says manual kick; method unknown).
