# Investigation: recipe 82178793 — new-failures flag (workato-health sweep 2026-10-13)

**Investigated:** 2026-10-13, read-only via workato-airo-mcp-server (dev) + local sweep records. Nothing changed.

## What it is
- **Name:** `REC | HR Genie | Conversation Tool Event Collector` (https://app.workato.com/recipes/82178793)
- **Project/folder:** HR Genie project (project_id 15643451), folder "Operational Monitoring" (folder_id 32985204)
- **Purpose:** Privacy-minimized HR Genie telemetry collector. Runs every 15 min (Scheduler); reads the Collector State watermark row (data table 156849), sweeps Agent Studio Genie conversations + terminal `tool_execution_completed` events via the Workato agentic API (custom HTTP connector acct 13685697), validates each page (shape/ownership/blank-id guards), idempotently upserts event rows into data table 145706, then advances the watermark only after all upserts succeed. Reads only tool *metadata* (name, type, status, time, IDs) — no conversation/tool-argument/response content. Fail-closed Ruby guards throughout (GENIE_HANDLE_UNSET, CONV_PAGE_MALFORMED, EVT_OWNERSHIP_MISMATCH, etc.). Ends with a best-effort async heartbeat to recipe function 82959725.
- **Status at investigation:** Running=true. Lifetime: 3,297 jobs — 3,274 succeeded, 23 failed (~0.7%).

## Why it was flagged
- Sweep 2026-10-13T08:37:23Z: `sweep: 2 failing owned asset(s): 82964017 stopped [dev]; 82178793 new-failures [dev]`
- **Correction to the premise:** the 10:38:17Z sweep did NOT re-flag it — that line reads `1 failing owned asset(s): 82964017 stopped [dev]` only. 82178793 had already self-cleared off the failing list by 10:38Z.

## Newest failed job
- **Job:** `j-AbwMpA6r-pCtYoB-CD` — https://app.workato.com/recipes/82178793/job/j-AbwMpA6r-pCtYoB-CD
- Ran 2026-10-13 00:51:45→00:54:04 PT (07:51Z, ~2m20s) — the failure that produced the 08:37Z flag. Prior failure was Oct 11 (23 failures total, mostly an Oct 9 build/testing cluster).
- **Failed step (trace line 24):** the step-25 `if next_cursor` conditional — output `{'condition': False}` — **no step error raised**.
- **Error message:** the Error field echoes only the trigger title ("Scheduler by Workato: new recurring event: Scheduled time=2026-10-13T00:51:44.937431-07:00 …") — no exception text. Trace simply STOPS after line 24; steps 27–47 (rounds budget, checkpoint compute, watermark update) never executed.
- Notable: trace line 19 (step-20 "List HR Genie terminal tool events" HTTP call) took **120.99 s** in this run (healthy full runs take 3.5–4 min total).

## Failure class
**Transient abnormal job termination (platform-side mid-run abort) — NOT a logic/validation failure.**
Signature: no named guard exception fired, error field echoes the trigger title, trace truncated mid-recipe. Consistent with a worker kill / timeout / transient infra abort ~2m20s in, right after a 121 s upstream API call. Distinguishable from the recipe's own fail-closed class, which always raises a named `*_` error from a Ruby guard.

## Triage vs noise: **NOISE — self-resolved, no action needed**
- Every subsequent 15-min scheduled run succeeded, starting with the very next tick (02:21, 02:36, 02:51, 03:06, 03:21, 03:36, 03:51, 04:06 PT all green).
- No watermark corruption: the job died *before* the checkpoint steps (40–44), and the design only advances the watermark after all upserts succeed — plus a 60 s overlap and 7-day re-drain horizon guarantee the next run re-scanned the window. The 03:51 run confirmed green.
- The 10:38Z sweep already dropped it from the failing list.
- If it recurs (>1 unexplained mid-run abort/week on this recipe), worth a watchdog autopsy on the 121 s event-page HTTP call (candidate: pagination size / latency on `events?include_event_types[]=tool_execution_completed`), but one instance is not a pattern.
