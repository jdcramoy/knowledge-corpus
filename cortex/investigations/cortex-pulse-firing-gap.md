# Investigation: cortex pulse firing gap (dispatched 05:28Z, persisted 06:32Z by the 06:31Z pulse)

Source: dispatch log ~/.local/state/cortex/dispatch-20261010-052834-cortexpulsegap.log (the headless lane could not write through the sensitive-path gate; persisted verbatim here by a permitted writer).

## Verdict (one line)

**There is no firing gap — the job is loaded and fired every hour through the claimed window; the "5h no-pulse gap" is an evidence-collection artifact (filtering heartbeat.jsonl by the UTC date substring `2026-10-09` hides every pulse written on `2026-10-10`), and the smallest fix is to stop date-string-filtering the heartbeat when compiling pulse evidence.**

### (1) Plist and launchd state

- `~/Library/LaunchAgents/com.josh.fleet.cortex.plist`: **`StartInterval` = 3600** (not `StartCalendarInterval`), `RunAtLoad` false, stdout/stderr → `/tmp/fleet-cortex.launchd.log` (0 bytes since creation — launchd has logged nothing, ever).
- `launchctl list`: `79231  0  com.josh.fleet.cortex` — **loaded, exit status 0, currently running** (PID 79231 started 01:27:05 local = 05:27:05Z, matching the observed 05:27Z fire). A running PID at an odd minute is normal for StartInterval jobs.
- Schedule is genuinely hourly, but with **drift** (~62–64 min spacing: 00:14 → 01:17 → 02:21 → 03:23Z) because launchd re-arms StartInterval after each run completes.

### (2) What happened between 00:15Z and 05:25Z — nothing is missing

- `~/.claude/knowledge/garden-reports/heartbeat.jsonl` has a cortex pulse for **every hour in the window**: 00:14:41, 00:15:24, 01:17:49, 02:21:20, 03:23:43, 04:27:04, 04:37:00 (all 2026-10-10Z). All of Oct 9 is likewise uninterrupted hourly.
- `~/.local/state/fleet/cortex.log`: zero `already running` skips, zero `VALIDATION FAILED`, zero `no work evidence`; last line `2026-10-10 01:29:14 cortex: done validated`.
- Coordinator work products exist in-window: attention-queue rebuilt 05:28Z (`.bak-0015` rotated 00:15Z), two dispatches launched 05:28:34Z.

**The artifact, reproduced:**
```
grep '"job":"cortex"' heartbeat.jsonl | grep '2026-10-09' | tail -1
→ {"ts":"2026-10-09T23:13:11Z","job":"cortex"}
```
That is exactly the reported "last seen" pulse. Any pulse after UTC midnight carries `2026-10-10` and vanishes from a date-substring filter; the "until 05:28Z" endpoint is the observing pulse's own launch/mtime, misread as a heartbeat. The earlier questioning at 23:24Z (claimed 00:14Z–03:21Z gap) is the same failure — those heartbeats were in the file the whole time. Both "gaps" were misread evidence, not missed fires. So: launchd did not skip, the job did not fail silently, and the schedule is hourly.

### Secondary observations (real, minor — not the cause)

1. **Paired heartbeats** (two lines 6–50s apart most hours) = the model's own check-in + run-job.sh's mechanical `write_heartbeat`. Several pulses' model check-in is missing because the sensitive-path write-gate denies the append (the 05:28Z pulse's own check-in was denied — noted in its log). Validation still passes via non-empty output.
2. **Out-of-order lines** (04:37:00 appended before 04:27:04) — `tail -1` is unsafe for "last pulse"; use a max-ts scan.
3. **StartInterval drift** — if on-the-hour pulses are wanted, switch to `StartCalendarInterval` with a pinned Minute; not required to fix this incident.

### Recommended fixes

1. Smallest: correct the evidence compile — never filter heartbeat.jsonl by date substring; filter by relative timestamp comparison (jq/awk on `ts` vs now−6h) or grep the whole label.
2. Optional: `StartCalendarInterval` for wall-clock alignment; resolve the pulse write-gate so the model check-in lands reliably (separate known issue).
