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
# 82178793 new-failures investigation (workato-health 07:27Z flag)

_Investigated 2026-10-17, read-only. Predecessor report: [82178793-new-failures-1520z.md](82178793-new-failures-1520z.md) (10-14, pre-canonization)._

## Verdict: RECURRENCE #4 of the canonized `line24-next-cursor-gate-abort` class (platform-side-abort). NOT Group B, NOT novel.

The failure the 07:27Z workato-health flag caught is a fourth occurrence of the
already-canonized class - same signature, same line, same masked error, no recipe
defect surfaced. Canon row is already open (canonized 2026-10-14T20:20Z, status open).

**The flagged failure** - [j-AbzRaXPR-rQnHJr-CD](https://app.workato.com/recipes/82178793/job/j-AbzRaXPR-rQnHJr-CD)
- Started 2026-10-17 00:22:23 PT (07:22Z) - 5 minutes before the 07:27Z flag
- **Failed in 9.2 s** (healthy ticks run 2-3.5 min); failed line **24** = `misc/if`
  next_cursor pagination gate, output `{'condition': False}`, gate completed, then
  the trace **stops** - lines 26+ (rounds budget, checkpoint, heartbeat to fn 82959725) never run
- Error field carries only the trigger title (AIRO masking, as at canonization); no
  error record on any line. Workload light (loop 1.6 s, events HTTP 0.58 s) -
  workload-independence reconfirmed
- Self-healed next tick: 00:37 PT and every tick since green (job_list verified 10-17)

**Failure distribution (failed-only job_list, 26 lifetime / 3,674 total = 0.7%)**
- Class occurrences on the current recipe shape: **4** - j-AbwMpA6r (10-13 00:51),
  j-Abx4seMz (10-14 07:07, canonized), **j-AbxDcXPN (10-14 14:07, UNCANONIZED 3rd
  instance, ran ~47 min after the 20:20Z canonization)**, j-AbzRaXPR (10-17 00:22)
- j-AbxDcXPN verified live this session: identical shape (line 24, `{'condition': False}`,
  no error record) on a HEAVY tick (loop 72.5 s, HTTP 67.6 s, died 79 s in) - further
  workload-independence evidence
- Pre-rebuild 10-09 burst (line-36 `while_condition`) is the old version's separate
  class - not part of this count

**Classification vs the candidate classes**
- **Group B shared-dispatch-gate (82059061 + 82202341) - NO.** Group B is the
  regression-nightly auto-seeded "Untitled test case 1" failure class on OTHER
  recipes (test-harness fixtures, run/job pairs cirr-Abxr*); this is a live
  scheduler job abort on 82178793's own line-24 gate. Different recipes, different
  mechanism, different surface.
- **Regression-canon - MATCH, already on record.** canon.jsonl
  `line24-next-cursor-gate-abort` (recipe_id 82178793, class platform-side-abort,
  open), spec at `regression-canon/line24-next-cursor-gate-abort.md`. New failure
  is a textbook instance of it.
- **Novel - NO.** Same signature, same boundary, same masking.

**What's new since canonization**
- Frequency: canon recorded 2 in ~31 h. Now 4 total, spread 10-13 -> 10-17 - roughly
  1 per ~24 h of scheduler uptime, consistent with the >1/week tripwire that tripped.
  The canon row stays open and this does NOT change its disposition (self-heal +
  watermark coverage still hold; zero data loss indicated).
- j-AbxDcXPN (10-14 14:07) postdates the canon row and isn't cited in it - the canon
  entry's jobs list should arguably include it (cosmetic; row is open either way).

**Recommendation (nothing executed - read-only investigation)**
- Leave the canon row OPEN; no hotfix (self-heals next tick, watermark covers the
  gap, 0.7% lifetime rate unchanged in character).
- The open question is still the platform-side abort at the line-24->26 boundary;
  recovering the masked exception requires an Orca UI trace read (AIRO masks it) -
  candidate for the next autopsy pass rather than a new dispatch.
- If a 5th occurrence lands within another ~24 h, consider escalating the platform-
  side-abort pattern to Workato support with the 4 job URLs as evidence.
