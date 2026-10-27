# Investigation: post-restore nightly fleet receipts (2026-10-22)

Investigated 2026-10-22 ~14:50 EDT, read-only. Question: did the 10-21→10-22 nightly
window produce receipts, and where did the watchdog's 10-22 run write?

## Verdict

The nightly chain DID NOT produce its receipts on the 10-21→10-22 window — every launchd
nightly job in the 22:43/23:13/23:33Z window either died pre-work (watchdog: cwd-fail on
corrupt jobfile, rc=1 before any heartbeat/validation) or failed validation after retry
(gardener rc=1, backup rc=2, dreamer rc=1). BUT a morning catch-up run on 10-22
(~07:29–07:36 EDT / 11:29–11:36Z) produced BOTH the watchdog and gardener reports — the
watchdog report simply landed in the WRONG DIRECTORY, which is why watchdog-reports/
looked dark. This is a path deviation by the watchdog agent session, NOT a write-gate
denial: the write succeeded, to `garden-reports/` instead of `watchdog-reports/`.

## Q1 — where the watchdog's 10-22 run wrote, and why

- **It wrote**: `~/.claude/knowledge/garden-reports/2026-10-22-watchdog.md` (mtime Oct 22
  07:36 EDT = 11:36Z; verdict 0 P1 / 2 P2 / 2 P3; heartbeat `{"job":"workato-watchdog"}`
  at 11:38:39Z matches). A companion `garden-reports/2026-10-21-watchdog.md` exists
  (mtime Oct 20 23:47) — the divergence started with the 10-20 23:47 run.
- **The prompt disagrees**: `~/.local/bin/fleet/jobs/watchdog.prompt` line 7 still directs
  the agent to write `~/.claude/knowledge/watchdog-reports/$(date +%F).md`. The manual/
  catch-up sessions since 10-20 have been writing to `garden-reports/` with a
  `-watchdog.md` suffix instead — agent deviation from the jobfile, not a path change in
  config and not a gate denial.
- **NOT the write-gate class**: the 10-22 write to knowledge/ succeeded. The cortex-pulse
  write-gate (memory: pulse sessions get knowledge/ writes denied) did not fire here.
- **Why watchdog-reports/ is dark since 10-19**: the launchd nightly watchdog (23:13 EDT)
  never reached the write stage. Last launchd watchdog heartbeat: 2026-10-20T03:17:45Z
  (the 10-19 23:17 run → `watchdog-reports/2026-10-19.md`). No watchdog heartbeat rows on
  the 10-20 or 10-21 nights. `~/.local/state/fleet/watchdog.launchd.log` contains exactly
  3 lines, all bare bash errors: `run-job.sh: line 79: cd: /Users/YOUR-USER/orca/
  workspaces/workbench/Workday-Development: No such file or directory` — the corrupt
  jobfile had an unreplaced `YOUR-USER` template placeholder in `JOB_CWD`; run-job.sh
  exits rc=1 at the cwd check BEFORE heartbeat and validation, so the failure is invisible
  in fleet-validation.jsonl (no watchdog row at all on those nights). The deployed
  `jobs/watchdog.env` is now restored (JOB_CWD=~/...).

## Q2 — receipts from the 10-21 → 10-22 nightly window

| Receipt | Produced? | Evidence |
|---|---|---|
| Watchdog report (nightly launchd) | **NO** — died at cd, rc=1, pre-heartbeat | watchdog.launchd.log YOUR-USER cwd-fails; no watchdog fleet-validation rows 10-21/10-22; no watchdog-reports/ file since 10-19 |
| Watchdog report (catch-up, 10-22 morning) | **YES** — wrong dir | garden-reports/2026-10-22-watchdog.md, 11:36Z |
| Gardener nightly report (10-21 22:43 run) | **NO** — rc=1 validation failed after retry | fleet-validation.jsonl 2026-10-22T06:37:53Z `gardener ran rc=1`; no 2026-10-21-brain-gardener.md |
| Gardener report (catch-up, 10-22 morning) | **YES** | garden-reports/2026-10-22-brain-gardener.md (delta pass covering 10-21→10-22), 07:29 EDT |
| Backup manifest (10-21 & 10-22 nights) | **NO** — rc=2 both nights | fleet-validation.jsonl 2026-10-21T03:33:54Z and 2026-10-22T05:36:56Z `backup ran rc=2 retry-exhausted`; no restore-drill-2026-10-22.md (last: 2026-10-21). Backup only validated clean at 2026-10-22T12:13:06Z |
| Dreamer report | **NO** — rc=1; missing artifact | fleet-validation 2026-10-22T06:38:27Z rc=1; nightly-gate flag: `missing: dreams/2026-10-21.md`; newest dream file is 2026-10-20.md |
| Nightly gate ledger | **YES** (it observed the gaps) | garden-reports/nightly-receipts.jsonl gate-run 07:07 EDT; nightly-gate-state.json escalations: watchdog/gardener/backup/dreamer escalated 10-21, registry-backup 10-22 |

Side finding: the registry-backup gate check fails with `Operation not permitted` reading
`~/Documents/ChatGPT/Google Workspace MCP/registry-backups/registry-snapshot-latest.json`
— a macOS TCC/sandbox READ denial (same flavor class as the dreams/** write-gate, but a
read denial, and outside knowledge/).

## What was NOT verified

- Exact timestamps of the 3 cwd-fail lines (bash cd errors carry no date in the log);
  attribution to the 10-20/10-21 nights is via the missing heartbeat rows + cortex's
  "watchdog dark 3 nights" observation, not log timestamps.
- Who/what invoked the 10-22 morning catch-up watchdog+gardener runs (agent-level
  heartbeats at 11:38:39Z confirm they ran; the invoking session was not traced).
- Whether backup's rc=2 root cause is the same corruption class (plausible, unconfirmed).

## Recommended fixes (for Josh, not applied)

1. Redirect/copy the watchdog's prompt output spec to match where catch-up runs actually
   write, or rename garden-reports/2026-10-2X-watchdog.md files into watchdog-reports/ —
   one canonical location, else consumers (cortex, morning brief) keep reading a dark dir.
   The 11:15Z morning brief already miscounted "watchdog no report 3 nights" while the
   report was 19 minutes old.
2. Make run-job.sh emit a timestamped "cwd fail" line to the launchd log so silent
   pre-heartbeat deaths are datable (3 bare bash lines cost this investigation).
3. Restore-drill has no 10-22 output because backup itself was down; re-run backup +
   restore-drill now that backup validated clean at 12:13Z to close the gap.
