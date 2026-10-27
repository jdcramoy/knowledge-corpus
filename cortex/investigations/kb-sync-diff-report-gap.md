# kb-corpus-sync / KB-digest SYNC FAILED — investigation 2026-10-16 (read-only)

Verdict: NOT the kb-corpus-sync job. The SYNC FAILED digest header comes from a
scheduling race between two differently-named jobs, plus a stale fleet-timer-health
finding that conflated them. The digest is behaving correctly under its new contract.

## 1. What com.josh.fleet.kb-corpus-sync actually runs
- plist: ~/Library/LaunchAgents/com.josh.fleet.kb-corpus-sync.plist
  → /bin/bash ~/.local/bin/fleet/run-job.sh kb-corpus-sync
- run-job.sh resolves jobs/kb-corpus-sync.{env,prompt}: CLAUDE_JOB=yes, claude -p prompt
  (headless, TIMEOUT=1800). Job files created Oct 16 16:45 — brand new; no .launchd.log
  exists yet; weekly (Mon 07:27), first scheduled run will be Mon 2026-10-19.
- It does: knowledge-export.sh ~/Documents/knowledge-corpus (git add/commit/push).
- The fleet-timer-health claim "wired to a nonexistent run-job.sh job" is STALE —
  both kb-corpus-sync.env and kb-corpus-sync.prompt exist. It has nothing to do with
  the nightly KB digest. Name collision (kb-corpus-sync vs workato-kb-sync), not a fault.

## 2. Where the nightly diff report should come from
- Producer: com.josh.workato-kb-sync launchd job → python -m kb.sync,
  nightly 21:37 (~~/Documents/workato-kb). Writes ~/.claude/workato-kb/diffs/{local-date}.json
  at COMPLETION. Historical completion times: 22:04 (Oct 10), 22:48/22:52/22:53/22:55
  (Oct 11–14). Full reports exist through 2026-10-14.
- 2026-10-15: NO full report — only 2026-10-15.scoped.json (manual scoped run, 16:42).
  Why the 21:37 full sync produced nothing that night could not be determined read-only
  (sync.log was rewritten by tonight's run; sync.py was edited 20:37 that evening).
- 2026-10-16: report not written YET — sync is running right now
  (PID 33614, started 21:37; still fetching hf-transformers at 22:16).

## 3. Why "exit 0" while the digest says SYNC FAILED
Three separate facts, none a bug in the digest:
- The digest job (com.josh.workato-kb-digest, 22:07) runs kb.digest, which since
  digest.py's sync-contract change (UNCOMMITTED, +93 lines, file mtime Oct 16 02:51)
  REQUIRES diffs/{today}.json to exist and stamps "SYNC FAILED (no diff report ...)"
  into the digest body when it's missing. Writing that header IS a successful digest
  run — fail-loud-in-content, exit 0 by design (digest.log shows date 2026-10-16,
  all six digests "written").
- Race: sync completes ~22:48–22:55 most nights; digest reads at 22:07. Under the new
  contract, any night the sync finishes after 22:07 will read as SYNC FAILED. Tonight
  is the first night the contract ran — and the sync (started 21:37) was still running
  at digest time.
- kb-corpus-sync's own exit 0 is run-job.sh's "never die loudly" contract (final
  `exit 0` even after VALIDATION FAILED, ledger row as the alarm) — but it never even
  ran yet (new job). The Oct 15 corpus snapshot digest is green because the diff-report
  check didn't exist until Oct 16 02:51.

## 4. Smallest Josh-gated one-line fix
Move the digest AFTER the sync's completion window — one line in
~/Library/LaunchAgents/com.josh.workato-kb-digest.plist:
  StartCalendarInterval Minute: 7 → 15 (with Hour 22 → i.e. run 23:15, giving
  ~25 min headroom over the 22:48–22:55 completion cluster), then
  `launchctl unload && launchctl load` the plist.
This is a live fleet-timer config flip → Josh's gate. Alternative (not recommended,
two lines and a semantic change): have the digest read the previous day's report.

## Nothing changed
Read-only investigation. Only this findings file was written.
Unverified: why the Oct 15 full sync produced no report (log evidence overwritten);
whether tonight's in-flight sync will complete and self-clear the Oct 16 report.
