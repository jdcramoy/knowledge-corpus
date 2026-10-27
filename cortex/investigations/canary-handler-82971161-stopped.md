# Investigation: recipe 82971161 (EM | Capture Ticket Reaction) "stopped" canary alarm

Investigated: 2026-10-21T19:50Z (read-only cortex dispatch, thread squad-estate-monitor-phase2)
Alarm: canary 2026-10-21T19:22Z, running flag false, consecutive_failures=1

## VERDICT UP FRONT

**FALSE ALARM — the recipe is RUNNING now.** The canary fired inside a ~53-second
deliberate stop window during a hot-swap push by session `em-triage-consolidate-20261021`.
The recipe was stopped deliberately, pushed, restarted, and verified running by the same
session at 19:23:07Z. No restart is needed; nothing is down.

## Evidence

- Live state (`wt recipes get 82971161`, 19:51Z): `running: true`, `stop_cause: null`,
  `stopped_at: 2026-10-21T12:21:56 PDT (=19:21:56Z)`, `last_run_at: 12:23:03 PDT`,
  `job_succeeded_count: 770`, `job_failed_count: 1` (lifetime total: ONE failure).
- Build ledger (`~/.claude/knowledge/build-ledger.jsonl` lines 25633-25638):
  - 19:18:14Z — session pulls version history for 82997363 + 82971161
  - 19:21:59Z — `wt api PUT /api/recipes/82971161/stop` (explicit, session em-triage-consolidate-20261021)
  - 19:22:44Z — `recipe_builder_set_input_field` (same session)
  - 19:22:55Z — `recipe_builder_push` (same session)
  - 19:23:07Z — verification read: `running: true`
- Post-restart job trace: `j-Ac4oYQMz-43dGbr-CD` — Slack new_event EvEMCANARY1792611451
  (the canary delivery itself) **succeeded** at 12:37:33 PDT; also EvEMCANARY1792609633
  succeeded at 12:07:14 PDT. Event delivery is flowing end-to-end.
- Timing match: alarm timestamp 19:22Z falls exactly inside the 19:21:56→19:22:49 stop window.

## Stop cause (deliberate vs self-stop)

**Deliberate.** Explicit REST stop call in the ledger by session
`em-triage-consolidate-20261021` (a triage-consolidation/drift-fix pass), followed 56s
later by a recipe_builder push — the standard stop → edit → push → restart hot-swap
sequence. Not a self-stop:
- `stop_cause: null` (error-limit stops populate this field)
- `consecutive_failures=1` reflects the canary's own probe count, and the recipe has only
  1 failed job in 771 lifetime jobs — nowhere near an error limit
- a self-stopped recipe would still be stopped; this one is running with post-restart jobs

## Is a restart safe/needed (owner: main session, not me)

**Not needed — restart already happened and is verified live.** The restarting session
completed its own loop: running=true at 19:23:07Z, successful jobs at 19:23:03Z and
19:37:33Z after the restart. Starting it again would be a no-op at best and a stop-start
churn risk at worst. Main session may optionally re-arm/confirm the canary goes green on
its next tick.

## MCP tool backing (stopped-backing-recipe gotcha)

**Not applicable.** Recipe 82971161 is a Slack Events API `new_event` trigger handler
(event-delivery path for the estate monitor), not a recipe function/skill backing an MCP
tool. No MCP server in the workspace serves a tool with provider_id 82971161. Even if it
did, the recipe is running, so the tool would be served.

## Confidence

**High (~97%)** on: deliberate stop, hot-swap sequence, current running state, and event
delivery (all directly evidenced by ledger command lines + live API state + successful
canary job trace). Residual uncertainty (~3%): the restart command itself is not visible as
a discrete ledger line (command fields truncate at ~200 chars and no `PUT /start` line
appears) — but running=true plus two post-restart successful jobs makes the restart a
verified fact regardless of which call performed it. The only real follow-up is canary
hardening: it should suppress or re-check before alerting when `stopped_at` is seconds
old and a same-session push is in flight.
