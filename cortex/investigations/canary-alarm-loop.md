# Investigation: em-delivery-canary false-alarm loop

Date: 2026-10-22 (written 16:5xZ) · Investigator: cortex-pulse session (read-only)
Subject: 20+ `canary-alarm` gossip-bus posts in 24h while handler recipe
82971161 (`EM | Capture Ticket Reaction`) was live-verified `running=true`.

## Verdict

**False alarms confirmed. 18 of the last 24h's ~19 posts were probe-infrastructure
failures (wt could not reach the Workato API), not delivery failures.** The recipe
was running and delivering throughout. Root cause is a canary design gap: a single
failed `wt recipes get` is treated as a delivery alarm and posted to the bus
unconditionally, every 15-minute cycle, with no retry, corroboration, rate limit,
or recovery post.

## 1. What produces the posts (producer located)

- launchd job **`com.josh.estate-monitor.delivery-canary`**
  (`~/Library/LaunchAgents/com.josh.estate-monitor.delivery-canary.plist`):
  `/usr/bin/python3 ~/orca/projects/estate-monitor/harness-hook/em-delivery-canary.py --once`
  on **StartInterval 900s + RunAtLoad** (4 cycles/hour, 96/day).
- Script: `~/orca/projects/estate-monitor/harness-hook/em-delivery-canary.py`
  (BSYS-29566, Builder B). Every failing cycle calls `alarm()`, which
  **unconditionally** posts via `bus_post.py` to thread `squad-estate-monitor-phase2`,
  subject `canary-alarm`, then exits 2. No dedup, no backoff, no recovery/"clear"
  post ever.
- NOT the producer: `com.josh.fleet.canary` (daily 06:05, `command-canary.py` via
  `~/.local/bin/fleet/jobs/canary.script`) — a different canary entirely, and its
  launchd log shows a dead `run-job.sh` path anyway. The monitored recipe's trigger
  itself posts nothing; it is purely the probe target.
- Post count reconciles exactly: 21 canary-alarm rows in
  `~/.claude/knowledge/dreams/bus/em-delivery-canary.jsonl`; ~19 fall inside the
  trailing-24h window (17-streak + 10-21T19:22Z + 10-22T16:22Z).

## 2. Where the rc=1 tracebacks originate (broken state identified)

Alarm path: `wt_json(["recipes","get","82971161"])` in the canary script raises
`RuntimeError("wt recipes get 82971161 rc=1: ...")` when the `wt` CLI exits nonzero;
the alarm body embeds the first 200 chars of wt's stderr.

The embedded traceback is from **wt's own urllib stack**
(`wt` line 123: `urllib.request.urlopen(req, timeout=120)` → Python 3.9
`urllib/request.py:1346 do_open`) — i.e. **wt could not complete a TCP/TLS request
to www.workato.com**. This is a network-layer URLError inside the probe tool, NOT:

- a stale running-flag — the `running=false` alarm fired only twice in the log
  (10-13T05:12Z, 10-21T19:22Z; the latter was a real stop, recovered);
- a wrong-profile invocation — default profile is `josh-us` (workspace 3535597),
  recipe 82971161 lives there and a live `wt recipes get 82971161` succeeds now;
- a 404/auth error — the only 404 was the deliberate 10-13 selftest with bogus id.

Failure timeline (`~/.local/state/estate-monitor/canary.log`, 2393 lines):

- 2026-10-22T01:22Z → 10:35Z: **17 consecutive FAILs**, one per 900s cycle, all
  identical `wt recipes get ... rc=1: Traceback ... do_open`.
- 2026-10-22T10:50Z: CANARY OK resumes, self-recovered, no config change
  (overnight window ≈ 18:22–03:35 PDT — consistent with an overnight
  network/sleep/wake condition on the Mac; exact cause unverified, see below).
- Isolated singles: 10-21T12:20Z, 10-22T16:22Z — same signature.
- Every OK cycle shows the full happy path: webhook HTTP 200, job seen in 15–19s.

Aggravating bug: `wt_json` truncates stderr with `.strip()[:200]` — the traceback's
**final line, which names the actual exception, is cut off**. The single most useful
character of the whole error is the one character past the truncation.

## 3. Minimal fix shape (proposal — nothing changed)

Probe correction (in `em-delivery-canary.py`):

1. Classify failures. `recipes get` rc≠0 = **PROBE_UNAVAILABLE**, not delivery
   failure. Retry once in-run after ~20s; if the retry also fails, log
   `PROBE DOWN` and exit non-zero **without** a bus post. Keep `STOPPED` and
   `job NOT seen in 120s` as genuine delivery alarms (the 10-21T19:22Z STOPPED
   post was a real event and correct behavior).
2. Capture the tail, not the head: `.strip()[-300:]` so the exception line
   survives, making the next occurrence diagnosable.

Rate-limit / corroboration before repeat-posting:

3. Gate the bus post on the state file it already keeps
   (`~/.local/state/estate-monitor/canary.json` → `consecutive_failures`):
   post only on the transition into `consecutive_failures == 3` (~45 min of
   sustained failure), then re-mind at most every N cycles (e.g. `n % 8 == 0`,
   2h) instead of every cycle.
4. Post a one-line **CANARY RECOVERED** on return to OK after any alarm, so the
   thread self-closes instead of staying red — and readers can distinguish a
   15-min blip from an ongoing outage at a glance.

Effort: ~30 lines in one script; no plist changes; no Workato-side change.

## Not verified

- The exact network exception behind the overnight streak (URLError subclass,
  DNS vs TCP vs TLS) — unprovable retroactively because stderr was truncated to
  200 chars before the exception line.
- Whether the Mac slept during part of the window (launchd fired on schedule the
  whole time, so it was awake at least at cycle boundaries).
- Whether other network consumers failed in the same window (checked 3 fleet
  launchd logs; they are broken in unrelated ways and not timestamp-correlatable).
