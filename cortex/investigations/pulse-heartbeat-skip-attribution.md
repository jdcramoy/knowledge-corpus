# Pulse heartbeat-skip attribution (investigation 2026-10-18, read-only session)

## Verdict (2026-10-18 ~21:45Z, read-only session)

**The heartbeat was never skipped.** Every hourly pulse on 2026-10-18 wrote a cortex heartbeat.
The "last entry 02:57:24Z" reading is a DETECTION ARTIFACT: the monitor greps the spaced literal
`"job": "cortex"` but the canonical heartbeat command produces the no-space form `"job":"cortex"`.
Last spaced entry: 02:57:24Z. No-space entries exist for every pulse hour after it.

## Evidence

1. **Two JSON formats coexist in `garden-reports/heartbeat.jsonl`:**
   - Spaced (json.dumps style): `{"ts": "2026-10-18T02:57:24Z", "job": "cortex"}` — last cortex entry 02:57:24Z.
   - No-space (echo style): `{"ts":"2026-10-18T14:19:32Z","job":"cortex"}` — matches every pulse hour.
2. **Full hourly coverage 2026-10-18 (no-space cortex entries):** 03:59/04:00, 05:00/05:01,
   06:03/06:13, 07:06(x2), 08:08/08:12, 09:09/09:10, 10:10/10:11, 11:13/11:16, 12:15/12:16,
   13:17(x2), 14:19(x2), 15:21/15:22, 16:22(x2), 17:24(x2), 18:25/18:37, 19:27/19:30,
   20:28(x2), 21:31/21:36Z — one pair per hour, continuous. No gap after 02:57:24Z.
3. **Transcript proof, 3 post-03:00Z sessions** (all `~/Documents/workbench` project, model
   fireworks/glm-5p3-flash, all launched by `com.josh.fleet.cortex` with the
   `[cortex-coordinator-pulse]` prompt):
   - 50d2e37b (17:22–17:24Z): final tool call `echo '{"ts":"'"$(date -u ...)"'","job":"cortex"}'
     | python3 ~/.claude/knowledge/scripts/atomic_io.py .../heartbeat.jsonl && tail -1` at
     17:24:10Z → entry 17:24:10Z present in file. Clean end ("Pulse complete"), no compaction.
   - fd0c329b (19:25–19:27Z): ended 19:27:02Z; entry 19:27:02Z present (plus slot-stamped
     19:30:00Z). Clean end.
   - ee80fc9e (21:29–21:31Z): heartbeat at 21:31:01Z (hardcoded ts 21:36:00Z) → present; clean
     end. Notably this session itself ran the spaced grep `'"job": "cortex"'` mid-pulse, found
     "last = 02:57:24Z", and dispatched this very investigation — the false alarm is self-propagating.
   - Control: 09e58f18 (02:55–02:59Z) improvised a python json.dumps heredoc → spaced entry
     02:57:24Z. That was the LAST improvised writer; later sessions followed the canonical echo.
4. **No context exhaustion:** zero compaction/summary markers in all four transcripts; all end
   with a final "Pulse complete…" assistant text + normal attachment/system/last-prompt/cost-state
   close. Sessions did not die early — they finished, including the heartbeat.
5. **15:00–20:00Z "visible activity gap" partially real but benign:** dispatch logs
   (`~/.local/state/cortex/dispatch-*.log`) jump from dispatch-20261018T141923Z to
   dispatch-20261018T213500Z, i.e. no SUBAGENT dispatches for ~7h. Pulse transcripts and
   heartbeats continued hourly throughout — those were attend-only pulses (quiet estate, nothing
   to dispatch). The launcher (launchd `com.josh.fleet.cortex`) never stopped firing.

## Root-cause hypothesis — CONFIRMED (confidence: ~95%)

The pulse prompt's LAST STEP mandates: `echo '{"ts":"<now ISO>","job":"cortex"}' | python3
~/.claude/knowledge/scripts/atomic_io.py .../heartbeat.jsonl` — which serializes with NO spaces.
Any monitor (or self-check) that greps the spaced literal `"job": "cortex"` sees only entries from
sessions that improvised a json.dumps writer instead. The 02:55Z pulse was the last to improvise;
from 03:59Z on, all sessions used the canonical command, so the spaced pattern went dark while the
heartbeat stream itself continued uninterrupted. Detection-fragility (whitespace-sensitive grep on
JSON), not behavior change. Secondary (low-severity) defect found: some sessions hardcode the
launcher slot time instead of `<now ISO>` (e.g. 21:36:00Z written at 21:31:01Z real, 18:37:00Z,
19:30:00Z) — future-stamped pollution in the heartbeat timeline.

## Recommended fix

1. **Fix the detector (the actual bug):** stop grepping a serialized literal. Parse, e.g.
   `jq -r 'select(.job=="cortex") | .ts' heartbeat.jsonl | tail -1` (jq tolerates whitespace), or
   grep -E '"job":[ ]*"cortex"'. Any staleness alarm on this file must use format-agnostic parsing.
2. **Keep the canonical echo command as the single writer shape** — it is already correct; add a
   one-line note in the pulse prompt that the entry is no-space by design, so future pulses
   self-checking with a spaced grep don't re-dispatch this investigation.
3. **Kill the hardcoded-slot-timestamp habit:** the prompt already says `<now ISO>`; sessions
   substituting the launcher slot time (21:36:00Z etc.) should use `$(date -u +%Y-%m-%dT%H:%M:%SZ)`
   always. Optional follow-up: a one-line atomic_io.py guard rejecting ts > now+2min.
4. No backfill needed — data is complete; only the reading of it was wrong.

*Investigation method: read-only. Transcript survey of 4 pulse sessions (1 pre-, 3 post-03:00Z),
heartbeat.jsonl format census, dispatch-log mtime sweep, launchd job identification. Note: stat
mtime display in this session initially rendered LOCAL time (UTC-4) with a literal Z suffix —
cross-checked against epoch before trusting; transcript-internal timestamps are authoritative UTC.*
