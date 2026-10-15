# Investigation: prod recipe 82090477 "Extract Design System" — Running=True, "zero jobs since 10-09"

Read-only investigation, 2026-10-12 (~09:00 PT). Sources: `wt` CLI prod reads (recipes get,
jobs list, jobs get, api recipes list). No writes, no stops, no tests. Dependency-tracker MCP
unavailable (permission not granted in headless session) — noted where it limits the answer.

## Headline: the watchdog premise is now FALSE, and there is a NEW real problem

1. "Zero new jobs since 10-09" was true only at watchdog verify time (2026-10-12T03:47Z =
   2026-10-11 20:47 PT). The recipe is on-demand (skill trigger), the 10-09→10-12 gap was demand
   silence, not a stall. Traffic resumed TODAY: 11 jobs on 10-12 (02:20 through 08:36 PT).
2. The real live issue: **helper recipe function 82872520 "GSlidesMCP | Append Guidance" is
   STOPPED (since 2026-10-12 07:55:55 PT) while its parent tool recipes run.** Two jobs today
   (08:24, 08:36 PT) failed with `Can't call a stopped recipe (id: 82872520)`. This is a partial
   restart after a stop window: 82090477 stopped_at 07:45:47, 82090474/82090475 stopped_at
   07:48:30, 82872520 stopped_at 07:55:55 — all four were stopped during a ~07:45–07:56 PT
   maintenance window, and 82090477/82090474/82090475 came back Running but 82872520 did not.

## (1) What the recipe is

- 82090477 "Extract Design System", folder 32312723, project 13755171 (PROD, workspace 3535598):
  https://app.workato.com/recipes/82090477
- Description: "Extract and cache a native-fidelity Google Slides design system without mutating
  the source."
- Trigger: `workato_skill` (MCP "start workflow" tool — NOT a scheduler, NOT a webhook;
  webhook_url=null). Invoked on demand by MCP clients/Genies calling the `Extract_Design_System`
  tool (job titles show MCP invocation frames). No cadence exists to stall.
- Flow (42 steps): guarded presentation-revision read (Google Slides custom connector, account
  19921568) → registry lookup via helper 82090475 "Get Design System Registry" → early-return
  path (revision unchanged) with catalog upsert + guidance append (step 8 → 82872520) → native
  design-system extraction → file-store artifacts (3 files) → catalog data-table upserts
  ("Enhanced Google Slides MCP | Design System Catalog") → final guidance append (step 41 →
  82872520) → return result.
- Helpers: 82090475 registry lookup (Running), 82090474 "Build Theme Carrier" (Running),
  82872520 "Append Guidance" (STOPPED), 82090475-referenced registry keyed by project property
  "GSlidesMCP Environment".

## (2) Why Running=True with zero new jobs since 10-09

Not a stalled scheduler — there is no scheduler. Skill-trigger recipes show Running=True
indefinitely; they run only when an MCP client invokes them. Between 2026-10-09 16:21 PT and
2026-10-12 02:20 PT nobody called the tool (demand silence — usage peaked 33 jobs on 10-05 and
decayed after). Running=True + no jobs is the healthy idle state for this trigger type.
The stopped-then-restarted race IS present, but today and in the OPPOSITE direction: parents
restarted, the shared guidance helper was left stopped, so post-07:55 invocations now fail.

## (3) Quota / task consumption

- Idle consumption: ZERO. No polling trigger exists; a Running skill recipe with no invocations
  consumes nothing. The exposure was never "burning while idle".
- Per-invocation consumption: every invocation consumes runtime tasks even when it fails.
  lifetime_task_count for 82090477 is 5,699 (87 succeeded / 67 failed of 154 jobs lifetime).
  Today's failed jobs each consumed ~7 tasks (trigger, try, Slides read, registry call, upsert,
  failing guidance call) before erroring — work done, result discarded.
- Failure-path burn pattern: a "revision unchanged" invocation dies at step 8 (~13–15s, cheap);
  a full extraction invocation would do ALL extraction work, upsert catalog rows, and THEN die
  at step 41 — maximum waste per call. If tool traffic ramps back to 10-05 levels (33/day), a
  stopped 82872520 converts every call into wasted tasks plus a broken tool response.

## (4) Blast radius of a stop (and of the CURRENT state)

Stopping 82090477 would:
- Affect: MCP clients calling `Extract_Design_System` — they'd get "Can't call a stopped
  recipe". No other recipe lists 82090477 as a dependency; it is a leaf tool (it calls helpers;
  nothing calls it). No scheduled downstream process depends on its output; artifacts land in
  file storage + catalog data table on demand.
- NOT affect: the shared helpers (82090474/82090475/82872520) or sibling tool recipes; the
  Google Slides connection; stored design-system artifacts or catalog rows already written.
- Verdict: stopping is LOW risk (on-demand tool, no dependents) — but stopping does not fix
  anything while the root cause is the stopped helper.
Current state blast radius (82872520 stopped): confirmed consumer 82090477 fails on both guidance
paths (steps 8 and 41). The helper is parameterized by tool_name ("one MCP tool" per call) and is
architecturally shared across the GSlidesMCP tool family — sibling consumers almost certainly
exist but could not be enumerated (dependency-tracker MCP permission denied; two-strike rule
applied). Its family folder 32312724: https://app.workato.com/recipes?fid=32312724 also contains
"Sync Guidance from Confluence" (82873160, clock, Running) which publishes the guidance 82872520
serves — guidance content will silently go stale for any tool still managing to run.

## PROPOSAL (for Josh — no action taken)

1. Start 82872520 "GSlidesMCP | Append Guidance":
   https://app.workato.com/recipes/82872520 — this is the fix. It was stopped in the
   07:45–07:56 PT window today and not restarted; every GSlidesMCP tool call that reaches a
   guidance step fails until it runs. One command: `wt recipes start 82872520 --profile josh-prod`.
2. After start, verify with the next real invocation (no forced test on prod without sign-off):
   confirm a job reaches its return step and the guidance delta lands.
3. Watchdog rule improvement: treat "Running=True with zero jobs" as NORMAL for skill/webhook
   triggers (demand silence), and add a family-level check instead: all recipe functions called
   by a Running tool recipe must themselves be Running (this exact failure — partial restart —
   is what the check should catch).
4. Audit this morning's 07:45–07:56 PT stop/start window: find what stopped the family
   (deploy session?) and why 82872520 was excluded from the restart — that gap is the defect.

## Not verified

- Sibling consumers of 82872520 beyond 82090477 (tracker unavailable) — stated as unknown, not low.
- What process performed the 07:45–07:56 stop window (no audit read attempted).
- Whether the 08:24/08:36 failures came from a human or agent MCP client (mock invocation IDs).
