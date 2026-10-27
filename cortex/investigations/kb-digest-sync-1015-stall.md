# Investigation: KB digest "miss" for 2026-10-15

**Investigated:** 2026-10-15 19:14 EDT (23:14 UTC) — READ-ONLY session, nothing restarted/edited/deleted.

## Verdict: NOT A FAILURE — the run is not due yet (false-alarm observation)

The digest job is alive, loaded, and error-free. The 2026-10-15 digest is written by the
**22:07 PM local (EDT)** run — which is still ~2h53m in the future at time of investigation.
Nothing was missed; the observing pulses ran in UTC and misread the freshness window.

## Sync mechanism found

- **Job:** `com.josh.workato-kb-digest` (launchd, `~/Library/LaunchAgents/com.josh.workato-kb-digest.plist`)
- **Command:** `~/Documents/workato-kb/.venv/bin/python -m kb.digest`, cwd `~/Documents/workato-kb`
- **Schedule:** `StartCalendarInterval` Hour=22 Minute=7 — **local time** (EDT), nightly
- **Logs:** stdout+stderr → `~/.claude/workato-kb/digest.log`
- **Output:** `~/.claude/knowledge/kb-digests/{cortex,harness-dreamer,workato-watchdog,estate-architect,brain-gardener,project-dreamer}.md`

## Last successful run evidence

- `launchctl list`: job loaded, PID `-` (not currently running), **last exit status 0**.
- `digest.log`: contiguous nightly entries **2026-10-08 → 2026-10-14**, every night all six
  digests reported `"written"`, zero errors, zero stderr noise beyond benign HF-token warnings.
  The newest entry (`"date": "2026-10-14"`) is the Oct 14 22:08 run — matching all six digest
  files' mtimes (Oct 14 22:07–22:08) exactly.
- `kb-digests/cortex.md` self-identifies: `# KB digest — cortex — 2026-10-14` — i.e. the file
  on disk is the correct, latest scheduled artifact.

## Failure mode analysis

Not dead (loaded, exit 0), not erroring (no stderr in log since Oct 14 run), not late
(fire time not yet reached today). The "second consecutive pulse observing the miss" is a
**UTC-vs-local timezone artifact**: the digest for date D is written at 22:07 **EDT on date D**,
which is ~02:07 **UTC on date D+1**. A pulse checking "did the 2026-10-15 digest land" during
2026-10-15 UTC (e.g. sweep stamped 2026-10-15T23:08 UTC = 19:08 EDT) can only ever see the
Oct 14-dated file, because tonight's run won't fire until 22:07 EDT — after the UTC day has
already rolled over. Every daily pulse window before 22:07 EDT will produce this false miss;
two consecutive pulses inside that window look like a two-night outage that doesn't exist.

## One-line fix proposal (PROPOSAL ONLY — execution is Josh-gated)

Fix the pulse's digest-freshness check to compare against **local (EDT) dates** — or simply
treat `kb-digests/*.md` as current when mtime < 24h old — so the healthy 22:07-EDT nightly
run stops being flagged as a missed 2026-10-15 digest.
