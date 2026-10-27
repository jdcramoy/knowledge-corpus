# Harness fusion audit — three-model panel + ops sweep (2026-10-12)

Charter: audit and validate everything built (wave-1 frontier stack, next-10 builds,
wave-3 science stack + integration) plus harness health and operations. Three
independent auditors (fable/sonnet/haiku), identical read-only charter, reports at
/tmp/audit-{a,b,c}-2026-10-12.md. Adjudication below; disagreements resolved by
evidence, not averaging.

## Headline

**The stacks are real.** ~41 scripts + 2 nightly jobs + integration wiring across three
waves: every claimed script exists, all 12 wave-3 selftests pass, and every spot-checked
headline number reproduces exactly (15 orphans, 0.90 coverage, Brier 0.1267, 3/3 chaos
detections, 21/0/19 regret, trigger 1194→332→4776, 24 channels, 164/168 cells,
141/103/25/13 pleiotropy, brain-mcp archive glob serves the bank). Verdicts: 33+/36
VERIFIED, 3-5 DEGRADED, 0 BROKEN, 0 UNBUILT. Secrets scan clean across 44 scripts.

## The audit's own catches (what it was for)

### P0 — heartbeat.jsonl was REPLACED mid-day Oct 11 (triple convergence)
1,402 rows (Oct 7 → Oct 11 03:32Z) vanished; current file started fresh at
21:11:57Z Oct 11. This manufactured 7-10 of harness-health's "never writes
heartbeats" findings (job logs prove those jobs ran) — the evidence ladder ranks
heartbeat above log mtime, so the wipe poisoned the health view. **No alarm fired on a
ledger shrinking.** RESOLVED: recovery disagreement between auditors adjudicated by
evidence — blob 25ba9d1 (commit 61b8175, Oct 10 backup) holds the full 1,402-row file;
all 1,402 recovered + merged with dedup (file now 2,005 rows, verified live). The
Oct-10 23:33 → Oct-11 wipe window rows exist in no commit (genuinely lost).
Root-cause class: run-job.sh bare `>>` writers racing atomic_io replace (inode swap
orphans open fds). QUEUED: heartbeat-ledger-wipe-recovery (runner adopts atomic_io +
ledger-shrink alarm).

### P1 — wave3-nightly spore row was a silent no-op (triple convergence — MY bug)
The job called `spore_router.atomic_append_row()` behind `hasattr` — the function
never existed — and printed success nightly while `spore-returns.jsonl` never did;
plus config-key mismatch (`returns_series_path` vs `series_path`). FIXED THROUGH TWO
LAYERS live: real `atomic_append_validated` with RETURNS_SCHEMA + fail-loud
existence check, then the second layer the first fix exposed — config stores the
series path in tilde-form, which wrote into a literal `~` directory under CWD
(row recovered from the stray dir, dir removed, `expanduser` added). Verified: row
lands at the real path. The ε-routing decision would have silently waited on a series
that never filled — the exact class this harness exists to kill.

### P1 — gossip-read.py timezone handling (auditor-1 unique)
`_ts` strips tz suffixes (`ts[:19]`) and mktime-assumes local: Z-suffixed bus rows
shift +4h (caught live: 05:12:48Z shown as 09:12:48Z). Corrupts epistemics TTL/cutoff
math and coincidence windows; likely root cause of the channels-registry
future-dating (auditor-2: last_seen ~3.8h ahead of measured_at — double conversion
in the seeder). QUEUED: gossip-read-tz-strip.

### P1 — live jira-triage runs a stale prompt (auditor-1 unique, fleet-drift class)
The deployed copy is missing Josh's 2026-10-10 voice correction (Oct-10 18:40 partial
redeploy overwrote it; canonical never re-synced) and TIMEOUT drifted 1800 vs
canonical 3600. Second recurrence of the fleet dual-copy drift class. QUEUED:
jira-triage-stale-deployed-prompt.

### P1 — mixed-writer race + wave-1 never adopted atomic_io
atomic_io's os.replace design races bare `>>` writers on the same file; the wave-1
frontier stack (including hash-chained saga.py) predates atomic_io and never migrated.
The in-tree fix (atomic append CLI) exists, unused. QUEUED: wave1-atomic-io-adoption.

### P2s
- **--help executes real jobs** in 4 scripts — auditors' probes fired 2 REAL Slack
  canary posts and freshened liveness state during the audit. QUEUED:
  help-executes-real-jobs.
- **fusion.jsonl selftest pollution** — my integration selftest rows + pre-wave3 rows
  with unjoinable process-randomized prompt_sha. QUEUED (fix landed tonight makes new
  rows joinable; old rows are identifiable waste).
- **Doc overclaims corrected in place**: fdt-gate's retroactive verdict was
  console-only (now marked); "first fire green" was a manual run (now marked);
  standing-orders "3 drafts awaiting Josh" persists nowhere (QUEUED:
  standing-orders-drafts-false-claim).
- Store discipline gate proved itself during the audit: it REFUSED my first
  schema-less queue append (SchemaViolation) — the protection built this week
  blocked its own auditor.

## Ops answers

- 10 "no heartbeat" findings = wipe artifacts (recovered); gym self-cleared at its
  01:07 fire during the audit. The 2 no-runner findings (frontier-nightly,
  wave3-nightly bypass run-job.sh validation contract) are REAL and persist —
  wave-3 propagated wave-1's deviation; queue them for runner adoption.
- 60 uncommitted knowledge files = post-23:33-backup churn; the backup works
  (git add -A); residual risk is only the 24h window.
- Both nightly jobs loaded, exit 0; tonight's 04:43/05:07 fires were still pending at
  audit time (expected — it was 00:57).

## Audit-method notes (for the fusion playbook)

- Three models × identical charter converged on the two biggest bugs independently —
  cross-model agreement remains the strongest truth signal.
- Divergence resolved by evidence: the heartbeat-recoverability question was settled
  by `git cat-file`, not by voting.
- Auditor side effects are real: read-only charters still fired Slack canaries via
  --help. Audit charters should say "run NO script that can post/write externally".


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Harness fusion audit 2026-10-12](reviews/harness-audit-2026-10-12.md) — 3-model panel (fable/sonnet/haiku, identical charter) over all 3 waves + ops: ~41 scripts 33+/36 VERIFIED, 0 BROKEN/UNBUILT, headline numbers reproduce to the digit; **P0 heartbeat.jsonl REPLACED mid-day Oct 11 (1402 rows; manufactured 7-10 false "never" health findings; no shrink alarm fired; 1402 recovered from blob 25ba9d1 → 2005 rows; Oct10 23:33→wipe window lost in no commit; root cause = run-job.sh bare >> racing atomic_io replace)**; spore-row no-op caught x3 (fixed live, 2 layers); gossip-read _ts tz-strip (+4h on Z rows — likely registry future-dating root cause); jira-triage deployed prompt STALE (missing Josh Oct-10 voice correction, TIMEOUT drift — dual-copy drift 2nd recurrence); --help fires real jobs (2 real Slack canary posts during audit); wave-1 stack never adopted atomic_io; 7 findings QUEUED to triage (13 pts); store gate REFUSED the auditor's schema-less append (worked as designed)