# wave3-nightly "stub rc=0" after the fix landed — validator keying investigation
Date: 2026-10-18 (read-only investigation, nothing modified)

## Verdict
The validator classified CORRECTLY. The 21:59:10Z "stub rc=0" row was produced by a
run of the PRE-FIX script copy at ~/.local/bin/fleet/jobs/wave3-nightly.script — the
copy the launchd plist actually executes. The fixed script (stdout echo + atomic_io
heartbeat) was only fanned out to the executed copy ~40s later; the very next run
(21:59:50Z) validated cleanly. Root cause is a partial-deploy / stale-copy race, not
validator logic, and NOT the run-job-sh-rc-misclassification class.

## The validator
- File: ~/.claude/knowledge/config/fleet/run-job.sh (canonical). Executed copy:
  ~/.local/bin/fleet/run-job.sh via ~/Library/LaunchAgents/com.josh.fleet.wave3-nightly.plist
  (ProgramArguments: /bin/bash ~/.local/bin/fleet/run-job.sh wave3-nightly;
  schedule 05:07 local — the 21:59Z runs were manual verification runs, not the schedule).
  Third copy: ~/Documents/agentic-workato-kit/bin/fleet/run-job.sh. All three currently
  byte-identical (diffed 2026-10-18).
- Ledger written at run-job.sh:206 -> garden-reports/fleet-validation.jsonl.

## Exact keying condition for "stub rc=0"
- validated() (run-job.sh:167-173): an attempt is valid iff
  (a) heartbeat.jsonl rows matching "job":"$NAME" increased during the attempt, OR
  (b) the per-attempt capture $OUT ("$LOG.run") is non-empty: [ -s "$OUT" ].
- attempt() (run-job.sh:175-190): rc==0 && validated -> "valid";
  rc!=0 && [ -s "$OUT" ] -> "ran rc=N"; ELSE -> "stub rc=N".
- Therefore "stub rc=0" keys on the CONJUNCTION of three facts:
  spawn exit code exactly 0 AND zero new heartbeat rows AND empty stdout/stderr capture.
  It is not stdout-timing vs heartbeat-ordering: the two evidence channels are OR-ed,
  so EITHER one landing before the attempt returns prevents the stub. Script-name
  matching is not involved (job name comes from argv[1]; heartbeat grep is a plain
  substring match on "job":"wave3-nightly"). rc handling is exact ($? of the perl
  alarm-wrapped spawn, run-job.sh:162).

## Timeline (evidence: ~/.local/state/fleet/wave3-nightly.log lines 467-556)
- 21:59:08Z run-job.sh invocation #1, attempt 1 (21:59:09): script ran ALL stages
  (trigger/coincidence/ratchet/spore row appended) but produced NO stdout summary
  line and NO heartbeat -> "no work evidence (stub rc=0) — retrying once".
- Attempt 2 (21:59:09-10): identical -> "VALIDATION FAILED after retry (stub rc=0)"
  -> ledger row {"ts":"2026-10-17T21:59:10Z","result":"stub rc=0"}.
- Between 21:59:10Z and 21:59:50Z the fixed script was copied to ~/.local/bin/fleet
  and the kit (all three script copies carry mtime Oct 17 17:59 local; diffs today:
  identical).
- 21:59:50Z invocation #2: fixed script echoed "wave3-nightly: rc=0 ... stages done"
  to stdout (non-empty $OUT) AND wrote the heartbeat -> "done validated" 21:59:51Z.
- The TWO heartbeat rows at 21:59:51Z are the script's own atomic_io write plus
  run-job.sh's mechanical write_heartbeat on success (run-job.sh:199) — benign
  duplication, not a second run.

## Root cause
Partial deploy, exactly the failure mode run-job.sh's own DEPLOY CHECKLIST header
(lines 27-32) warns about: the fix was edited and verified in the knowledge tree
(~/.claude/knowledge/config/fleet/jobs/wave3-nightly.script) while the plist-executed
copy under ~/.local/bin/fleet/jobs/ still held the pre-fix script when verification
run #1 fired. The log shows the older, severer symptom of the same class two days
earlier: "bash: ~/.local/bin/fleet/jobs/wave3-nightly.script: No such
file or directory" (log lines 405-406, Oct 16 — copy missing entirely).

## Relation to run-job-sh-rc-misclassification (prior finding)
NOT the same root cause. That class was: nonzero rc (2/3, e.g. restore-drill RED
verdicts, heartbeat atomic_io rc=2) with non-empty/empty OUT mislabeled "stub rc=N",
hiding real failures — fixed 2026-10-16 by the "ran rc=N" branch (run-job.sh:182-186).
Here rc was genuinely 0 and BOTH evidence channels were genuinely empty because the
old script had no stdout echo and no heartbeat write: a true positive, correct
classification of a stale-deploy run. That bug was validator logic; this is deploy
ordering. (Note: triage row canon-gap-night-chain-redacted-paths, 2026-10-18T03:58Z,
already flags that this wave3 false-stub class has no canon regression row.)

## One-line fix proposal
Make deploy atomic and verified — a scripts/fleet-deploy.sh that copies any edited
jobs/* file to BOTH ~/.local/bin/fleet/jobs/ and the kit and shasum-verifies all three
copies in the same breath (or symlink the two deployed copies at the knowledge tree),
so no verification run can ever fire against a stale executed copy.
