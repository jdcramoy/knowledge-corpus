# Investigation: night-chain break 2026-10-16→17 (backup/dreamer/regression "skipped" 23:33–00:53)

- **Filed:** 2026-10-17 ~14:50 EDT, read-only investigation (nothing changed outside this file)
- **Verdict: ROOT CAUSE = (c) a deploy-pipeline regression, NOT launchd and NOT the rc-classifier.**
  The 2026-10-16 16:45 EDT "fleet-job sync" deployed **pre-commit-redacted job scripts** to the live
  runner: the kit's personal-path redaction rule rewrote `~` -> `/Users/YOUR-USER`
  inside the job `.script` files, and those exact redacted bytes landed in `~/.local/bin/fleet/jobs/`.
  Every `.script` job whose last line is the atomic_io heartbeat check-in died with
  `python3: can't open file '/Users/YOUR-USER/.claude/knowledge/scripts/atomic_io.py'` -> exit 2 ->
  run-job.sh correctly classified "ran rc=2" -> VALIDATION FAILED -> no heartbeat -> recorded as skipped.
  The dreamer and regression jobs actually RAN and validated that night; the morning brief misread
  them via stale heartbeat names. The perceived "chain break" = 1 real failure cohort (backup + 4
  sibling script jobs) + 2 phantom skips (name-matching artifact).

## 1. What launchd did (hypothesis a — RULED OUT)

- Schedules: com.josh.fleet.backup 23:33, com.josh.fleet.dreamer 23:43, com.josh.fleet.regression 23:50 local.
- Every job FIRED on time: backup.log "2026-10-16 23:33:05 backup: start", dreamer.log
  "2026-10-16 23:43:05 dreamer: start", regression ran to "done validated 2026-10-17 00:02:59".
- Plists intact (read-only check), StandardError logs clean, no spawn errors. The scheduler did its job.

## 2. What actually failed, minute by minute (all times EDT, Z rows are +4h)

Deploy contamination Oct 16 16:45:12 (kit commits 4a2fc1d + 9cf00ef/c42b3a2/2a5f62e "content-audit"):
- 4a2fc1d diff on bin/fleet/jobs/backup.script line 4 is the smoking gun: heartbeat write changed from
  a plain `>> "$HOME/.../heartbeat.jsonl"` append (old) to
  `| python3 /Users/YOUR-USER/.../atomic_io.py /Users/YOUR-USER/...` (redacted).
  Same sync touched live: run-job.sh + job mtimes 16:45:12 == commit timestamps.
- Live got the kit's redacted working-tree bytes, NOT the canonical real-path copies from
  knowledge/config/fleet (canonical mtime 01:31 Oct 16, never mutated, md5 matches the fixed live copy).

Failure wave (garden-reports/fleet-validation.jsonl):
- 23:20:05 harness-health ran rc=2  (first of the wave)
- 23:33:26 backup     ran rc=2  (the brief's "skipped" backup; two attempts, identical YOUR-USER error)
- 23:50:05 value-ledger ran rc=2
- 00:47:05 instruction-miner ran rc=2
- 03:47:06 queue-drift ran rc=2
- 05:07:06 wave3-nightly "stub rc=0" (separate, pre-existing issue)
- 07:20:05 decision-inbox ran rc=2  (last failure row of the wave)

backup.log proof (the job's real work SUCCEEDED before the heartbeat line died):
  2026-10-16 23:33:05 backup: start
  harness-backup: dream-mine --days 1 -> sessions=114 turns=20255 ...
  harness-backup: committed + pushed (2026-10-16 23:33:05)
  /Applications/Xcode.../python3: can't open file '/Users/YOUR-USER/.../atomic_io.py': [Errno 2]
  2026-10-16 23:33:26 backup: VALIDATION FAILED after retry (ran rc=2) — job did not run; escalated

Why rc=2 exactly: the atomic_io heartbeat check-in is the LAST line of each affected .script job;
python exits 2 on "can't open file", so the whole script exits 2. run-job.sh attempt() then
correctly echoes "ran rc=2" per the 2026-10-16 rc-classification fix — the classifier worked.

## 3. The two phantom skips (brief-side amplifiers, run-job.sh name-identity family)

- dreamer: ran 23:43, filed dreams/2026-10-16.md, "done validated 23:47:26". Mechanical heartbeat
  row {"job":"dreamer"} landed 03:47:26Z. Validated clean.
- regression: ran 23:50, "done validated 2026-10-17 00:02:59". Heartbeat {"job":"regression"} 04:02:59Z.
- The morning brief (today_brief.py passes raw beats to the brief writer) reported skips against the
  STALE model-written names: "harness-dreamer" (last beat 06:52Z Oct 16; the dreamer prompt now
  instructs job name "dreamer") and "regression-nightly" (dead name since 2026-10-10). Fresh rows
  under "dreamer"/"regression" were sitting in heartbeat.jsonl in the 24h window.
- Brief's "no 2026-10-17 dream report — dreamer itself skipped": dream reports are named by the local
  EVENING date (date +%F at 23:43 Oct 16 -> 2026-10-16.md). A 10-17 file only appears after tonight's
  run. Expected behavior misread as a skip.
- Name duality (backup/harness-backup, dreamer/harness-dreamer, regression/regression-nightly) is a
  known nuisance — see harness-health.py:36 comment and brain-dashboard.py:96 mapping.

## 4. Self-heal (already landed, verified)

- Oct 17 08:11:23 EDT: live job scripts re-deployed with REAL paths (all affected .script mtimes
  08:11:23; md5 identical to canonical across all three locations).
- Oct 17 08:11:26 EDT: harness-health ran clean, heartbeat landed — live proof the fleet healed.
- No fleet-validation failure rows after 11:20Z (07:20 EDT).

## 5. Hypothesis scorecard

- (a) launchd job failures: RULED OUT — all jobs fired on schedule; plists/logs clean.
- (b) run-job.sh rc=2 misclassification family: the CLASSIFIER is exonerated ("ran rc=2" was an
  accurate label of a genuinely failing job). But two family members DID contribute:
  (i) the brief's stale-name matching turned 1 real failure into 3 reported skips;
  (ii) "regression-nightly" has been a dead heartbeat name since Oct 10 — same family.
- (c) distinct scheduler regression: CONFIRMED — the redaction-contaminated deploy is the root cause.
  Category: deploy-pipeline regression (kit pre-commit redaction mutated deployable bytes; sync then
  copied kit-tree -> live, violating run-job.sh's own DEPLOY CHECKLIST which says deploy from
  knowledge/config/fleet to BOTH the kit and live).

## 6. Residual risks + recommended fixes (NOT applied — read-only mandate)

1. Redaction is not deploy-safe: the pre-commit personal-path rule still fires on fleet job scripts.
   The next canonical->kit->live sync will re-break the whole script-job fleet. Exclude
   ~/.claude/ internal paths from redaction (precedent: c775fa9's --no-verify
   self-exclusion for sanitizer scripts), or make the sync deploy canonical->live only.
2. Kit working tree currently holds the real-path restore UNCOMMITTED (git status dirty on
   bin/fleet/jobs/); commit it or the next audit will re-flag it.
3. Fix brief/dashboard name matching: dedupe backup=harness-backup, dreamer=harness-dreamer,
   regression=regression-nightly (reuse the identity logic sketched at harness-health.py:36).
4. "regression-nightly" heartbeat name dead since 2026-10-10 — retire or re-point.
5. wave3-nightly "stub rc=0" at 05:07Z is a separate open item (empty-output spawn, not this wave).
6. Minor: 2026-10-15 23:33 backup push hit "src refspec master does not match any" (transient; the
   run still validated) — worth a glance in harness-backup.sh's branch handling.

## Evidence trail
- ~/.claude/knowledge/garden-reports/fleet-validation.jsonl (failure wave rows, 03:20Z-11:20Z Oct 17)
- ~/.claude/knowledge/garden-reports/heartbeat.jsonl (last-beat per job; dreamer/regression fresh)
- ~/.local/state/fleet/backup.log (YOUR-USER error + validated work before it), dreamer.log,
  regression.log (both "done validated" that night), deploys.log (16:45 triage-bundle deploy line)
- ~/Documents/agentic-workato-kit git: 4a2fc1d diff (YOUR-USER in backup.script line 4), 9866ad9,
  c775fa9; live-vs-canonical md5 equality post-fix
- ~/Library/LaunchAgents/com.josh.fleet.{backup,dreamer,regression}.plist (schedules, read-only)
- ~/.claude/knowledge/scripts/today_brief.py:56-72 (brief heartbeat ingestion)
- mood.json reason + mood-register-stale-baseline.md (prior rc=2 misclassification history)
