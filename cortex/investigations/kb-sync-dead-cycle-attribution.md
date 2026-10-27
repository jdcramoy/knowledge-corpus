# KB sync dead digest cycles — attribution (2026-10-18, read-only investigation)

Triage card `kb-digest-timer-skew` hypothesized: the 22:07 digest launchd timer fires
BEFORE the corpus sync completes. **Verdict: the timer ordering is real but SECONDARY.
The sync does not merely finish late — since the night of 2026-10-15 it DIES mid-run
(SIGKILL during `hubs.build` hdbscan clustering) and never writes a diff report at all.
The digest is faithfully reporting a sync that never completed.**

## (1) Does the digest read a per-day diff report from a separate sync stage? YES

- `~/Library/LaunchAgents/com.josh.workato-kb-sync.plist` → `python -m kb.sync`, daily 21:37.
- `~/Library/LaunchAgents/com.josh.workato-kb-digest.plist` → `python -m kb.digest`, daily 22:07.
- `kb/sync.py` (nightly orchestrator, ~30 steps) writes `~/.claude/workato-kb/diffs/<TODAY>.json`
  **only at the very END of `main()`**, after all sources, index build, hubs, fractal, lateral.
- `kb/digest.py` → `sync_status(today)` reads `diffs/{today}.json` for the digest's own run
  date; a missing file → `{"ok": False, "failed_sources": ["no diff report for <today>"]}` →
  the exact `SYNC FAILED (...) - digest unreliable` header seen in all 6 per-agent digests.
- This contract came from proposal `2026-10-12-kb-digest-sync-contract` (digest must never
  claim quiet without a report). Working as designed — the input never arrives.

## (2) RC/log evidence for 10-17 (and 10-15/16)

- **No diff report exists for 10-15, 10-16, or 10-17.** `~/.claude/workato-kb/diffs/` ends at
  `2026-10-14.json` (mtime Oct 14 22:53). Nothing in `kb/*.py` deletes reports.
- `launchctl list`: `com.josh.workato-kb-sync` → **PID 35720 still running, last exit -9 (SIGKILL)**.
- `ps`: PID 35720 = `python -m kb.sync`, started 21:37 Oct 17, **4h29m elapsed, ~99% CPU,
  1.8 GB RSS** — a full sync took **~75 min** on 10-14 (report 22:53).
- `sync.log` shows the last three runs (10-15, 10-16, 10-17) all collapsing at the same point:
  each reaches `[sync] hubs ...`, loads doc vectors, prints the sklearn
  `hdbscan.py:722 FutureWarning`, then the process ends — the multiprocessing
  resource_tracker prints `leaked semaphore objects to clean up at shutdown`
  (log lines 6422 and 6684 for the 10-15 and 10-16 runs) and **no report is written**.
  No traceback, no crash report in `~/Library/DiagnosticReports/`.
- 10-17's run: last output 23:33 (hdbscan warning), silent ~5h+ while burning CPU — deep in
  clustering under extreme swap. `vm_stat`/`sysctl` at investigation time: **33.4 GB of 33.8 GB
  swap used** on a 36 GB Mac.
- `digest.log`: a run for every date 10-08 → 10-17; all six digests "written" each night —
  the 22:07 writer itself never failed. On-disk + git-committed digests:
  `SYNC FAILED (no diff report for 2026-10-16)` (session-shadow 8bdefa6, 10-16 22:16) and
  `... for 2026-10-17` (7b1e713, 10-17 22:15).

### What changed on 10-15
`kb/sync.py` commits 404743f (08:23, "Wave 5 ingest: HF docs, PwC dumps, API catalogs"),
10bb410 (20:34, confluence all-spaces), 4dc9301 (22:01, snowflake/dbt/trigger + FTS).
Corpus went to **7.1 GB / index 8.0 GB**. The first nightly with the full expanded corpus was
the 10-15 21:37 run — and it is the first run that never finished. `hubs.build` runs
hdbscan (min_cluster_size=5) over the now-much-larger doc-vector matrix; O(n²)-ish memory
in the mutual-reachability step is the most plausible kill site, under severe memory
pressure (SIGKILL; no jetsam entry found in `log show` — kernel kill is the best-supported
hypothesis, not proven).

## (3) Does timer ordering explain the miss?

Partly historical, not the current cause:
- Scheduled gap is only **30 min** (21:37 sync → 22:07 digest), but healthy-era reports were
  written at **22:48–23:52** (10-09: 23:52; 10-11: 22:55; 10-12: 22:48; 10-13: 22:52;
  10-14: 22:53) — i.e. the 22:07 digest has been structurally ahead of the sync end for days.
- Healthy digests on 10-12/13/14 (nightly-backup snapshots at 23:33) imply the digest
  effectively ran after the report on those nights (launchd sleep-coalescing or same-evening
  re-runs) — or that a same-day manual full-sync report was present. One evidence gap: the
  10-15 23:33 backup digest is healthy ("no changes since previous sync"), which requires
  `diffs/2026-10-15.json` to have existed at ~22:07 — that file is now absent and no code
  path deletes reports. Doesn't affect the 10-16/17 mechanism, which is fully evidenced.
- **Reordering timers alone fixes nothing**: a digest that waits longer still has no report,
  because the sync is killed before it ever writes one.
- Additional latent bug: `sync.py` computes `today = dt.date.today()` at END of run. Any
  run finishing after midnight stamps the report with the NEXT day's date — the 10-17 run,
  if it completes, will write `2026-10-18.json` (next digest then reports 10-18 "healthy"
  off a stale night, and 10-17 is lost forever).

## (4) Smallest fix (recommendation)

1. **Out of the critical path: `hubs.build` (hdbscan)** — the actual killer. Make hubs
   weekly, subsampled, or incremental/cached, or move it after the report write. Without
   this, no digest-side fix matters — there will never be a report.
2. **Write the diff report earlier in `sync.py`** (immediately after the source steps +
   index build, before hubs/fractal/lateral/memory-entropy) — the heavy tail can no longer
   take the report hostage; update the report at the end with floor-failure status.
3. **Fallback-to-last-good in `digest.py`** (smallest digest-side change; `latest_diff()`
   already exists there): if `sync_status(today)` has no report, fall back to the most
   recent report and label the digest with the report's actual date + "stale" warning.
4. **Date the report at run START** in `sync.py` (pass the start date to the write), fixing
   the post-midnight misdating.
5. Timer reorder / retry-at-00:30: optional polish, insufficient by itself.

## Josh decisions needed
- The 10-17 sync (PID 35720) is STILL RUNNING (~5h+ CPU in hdbscan). Kill it and re-run a
  scoped/`--no-embed` full sync off-peak, or let it finish (report will be misdated 10-18)?
- Approve the fix shape (1+2+3+4 recommended) — triage card `kb-digest-timer-skew` verdict
  should be updated to "timer ordering real but secondary; root cause = sync killed at
  hubs/hdbscan since 10-15 wave-5 corpus expansion under severe memory pressure (33 GB swap)".
- Side observation: "re-embedding 464 docs missing first-chunk vectors" appears EVERY
  night — the same 464 docs never get vectors (separate small bug, worth a follow-up).

## Evidence files
- `~/Library/LaunchAgents/com.josh.workato-kb-sync.plist`, `...kb-digest.plist`
- `~/Documents/workato-kb/kb/sync.py`, `kb/digest.py`, `kb/hubs.py`
- `~/.claude/workato-kb/sync.log` (lines 6163→6422, 6424→6684, 6686→in-flight)
- `~/.claude/workato-kb/digest.log`, `~/.claude/workato-kb/diffs/` (ends 2026-10-14.json)
- `~/.claude/knowledge/kb-digests/*.md` + git snapshots 1f43fd8/80e14da/8bdefa6/7b1e713
