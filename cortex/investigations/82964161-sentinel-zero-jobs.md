# Investigation: 82964161 gw_fleet_schedule_liveness_sentinel — "zero lifetime jobs" (2026-10-13)

Read-only dispatch from cortex session 05:49Z. Verdict up front: **the premise is STALE —
this is an intended, healthy, event-driven sentinel, and it already fired for real.**
Not intended-hourly, not broken, not dead.

## 1. Live config + schedule (wt recipes get / wt jobs list, 2026-10-13)

- Recipe [82964161 gw_fleet_schedule_liveness_sentinel](https://app.workato.com/recipes/82964161), dev, folder 35404884, project 17981834.
- **NOT a scheduler.** Trigger = RecipeOps (`workato_app`) `stop_error` PUSH trigger, dynamic
  scope = All recipes. It is *supposed* to sit idle until Workato auto-stops some recipe
  (trigger_errors_limit silent-death class). Zero jobs between stops is the healthy state.
- running=true, stop_cause=null. Live counts: **1 succeeded / 0 failed, 3 lifetime tasks** —
  not zero.
- The one job: `j-AbwJfLFH-GzHeez-CD`, 2026-10-12 21:34:44 PT, status **succeeded**, title:
  "recipe stopped by workato: Recipe ID=82964017 ... Internal error". That is the real
  auto-stop of canary [82964017 gw_semantic_mutation_chain_canary](https://app.workato.com/recipes/82964017)
  flagged in the owned-asset sweep. **The sentinel fired on the exact event it was built
  for, within its first day of watch.**
- Steps: stop_error → read workspace_health_alert_state (table 156399, mute/cooldown state)
  → Ruby mute check + alert compose → conditional Slack post to C0C6S3VT4KF
  (#gw-semantic-alerts, Slack bot connection 22250688).

## 2. Build ledger + em-squad/bus context: who, when

- `~/.claude/knowledge/projects/google-semantic-mcp.md` (ledger, lines ~2852-2875): built
  2026-10-11 from dream proposal `2026-10-07-gw-semantic-schedule-liveness-sentinel`, Josh
  "build-now" verdict. A parallel session did the build. Design delta (deliberate): the
  accepted draft's 60-min polling loop was replaced by the RecipeOps stop_error push trigger
  — so "intended hourly" was rejected at build time BY DESIGN, not by drift.
- Wiring proven 2026-10-11 via throwaway scheduler clone (82964164, since DELETED):
  force-runs j-AbtKTLMh-Q9bNX8-CD (alert delivered, Slack ts 1791704150.254049) and
  j-AbtKWNPh-HkBFdh-CD (mute suppression path verified). So both branches have live
  evidence. Soak test + forced REAL auto-stop were the declared open items — and the
  2026-10-12 82964017 stop just supplied the real-world soak evidence.
- Sibling, do not confuse: [82951201 gw_fleet_liveness_sentinel](https://app.workato.com/recipes/82951201)
  is the hourly ticking one (90 succ / 3 fail per watchdog 2026-10-12). Two different sentinels.

## 3. Owning Jira ticket

- **BSYS-29478 — "Fleet schedule-liveness sentinel recipe (gw semantic MCP project, dev)"**,
  created 2026-10-09, status UAT. That is the governing ticket.
- Cited transitively in BSYS-29548 ("dead sentinel" in a pre-promotion gap bundle — that
  row carries the same stale zero-jobs claim) and in prod-deployment staging ticket
  BSYS-29583 (2026-10-13). Worth correcting BSYS-29548's "dead sentinel" framing.

## 4. VERDICT

**Intended-idle-by-design, alive, and already proven in production of its duty.**
The "zero lifetime jobs since 10-11" line originated in the watchdog sweep of 2026-10-12
(day 1 of the recipe, before its first real fire) and was repeated in watchdog-2026-10-13
even though the 10-12 21:34 job postdates it. Whoever expects it running: Josh (build-now
verdict) and the google-semantic-mcp project, which stages it in BSYS-29583. Nothing to
start, stop, or fix. The genuinely open item remains the mute-flag semantics in prod
rehearsal windows, per the ledger's soak note.

## Unverified

- Whether the 2026-10-12 21:34 job's Slack alert text actually rendered to
  #gw-semantic-alerts (job succeeded; read of C0C6S3VT4KF not permission-granted this
  session — Slack ts on the delivered message not captured). Mute-row state at fire time
  (last_detail semantics) also unverified for that specific run.
