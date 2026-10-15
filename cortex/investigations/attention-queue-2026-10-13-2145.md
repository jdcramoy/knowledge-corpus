# Attention queue rev — pulse 2026-10-13T21:45Z (attention-queue.md overwrite write-gated; full queue here)

1. **needs-josh debt: 41 open rows, 20 workstreams >24h stale — inflow still outrunning decisions.**
   Oldest: bsys-28296-marketo-history (blocked 48.8h, Marketo prod import). Sharpest prod-gated:
   grc-gdpr-emails, healer-fleet (2 HR Genie 401'd connections), jira-triage batched gates (2 plans
   awaiting go/no-go, 21:28Z). Fold staleness computed externally — the fold script still has no
   non-done staleness pass (item 7). Ref: mission-control/registry.json (fold 21:45Z).
2. **grc-gdpr-emails — CONFIRMED unfinished prod state, live-verified 19:36Z.** Prod 82912295
   blank-posts long privacy@ emails; dev truncation fix exists, un-promoted, no red-team verdict on
   record (deploy predates the standing order). Triage row open (grc-gdpr-prod-blank-email-fix);
   Josh question filed 19:42Z, unanswered. The one gated claim PROVEN broken in prod.
3. **82964017 gw_semantic_mutation_chain_canary: RESTARTED — downgraded to watch.** Health sweep
   21:43Z: running=True, fails=0. But last_run=13:29Z is 8.2h before the sweep vs the hourly cadence
   BSYS-29560 wants — confirm the fix held AND the schedule cadence. Old "canary is blind" items
   closed. Ref: workato-health/sweeps (21:43Z line).
4. **82862814 canary_sweep_and_promote: failure will re-fire ~22:10Z — pre-declared, not new.**
   Autopsy (16:47Z): root cause is updateContact resourceName synthesis; dev-only blast radius;
   deterministic, unchanged row state. Fix owner Josh (GWS semantic gateway ledger 147343). Do not
   re-triage the next tick as a fresh incident. Ref: canary-sweep-82862814-new-failure.md.
5. **Monitor-the-monitors: cross-session awareness is BLIND.** session-shadow + agent-command-watcher
   dead ~21h (launchd exit 78); now-file last updated 2026-10-12T23:27Z (22h stale), so this pulse
   could NOT verify live sessions against the registry. Root cause shared with harness-machine-health
   (python plist re-point, Josh's go unblocks both). Triage row open (session-shadow-crash-exit78).
6. **channels-registry agent bus spam still live.** Every 2h bus read returns dozens of duplicate
   "seeded 2026-10-11 wave-3 builder C" lines — pollutes merged reads and inflates corroboration
   tallies for its claims. Asked 19:42Z, unanswered; triage row filed this pulse. Ref: gossip-read
   --since 2h (21:45Z).
7. **Mission-control fold: staleness + escalation gaps still open (two Josh questions filed 20:45Z).**
   No non-done staleness pass in fold (only STALE_DONE_DAYS=14); no prod-gated tier so rows blocking
   live prod state (grc-gdpr 39h+) age in the same list as doc approvals. Board hides the real
   20-stale cohort. Ref: cortex/questions.jsonl 20:45:09Z.

Cost governor: unchanged from 2026-10-13 report (no alarms; 3 kimi-k3 downgrade trials pending
Josh; brain-guard instrumentation gap open).

Delta vs 11:15Z rev: 82964017 restarted/green (old items closed, watch cadence), needs-josh
29->41 rows, stale 14->20, grc-gdpr prod state live-CONFIRMED broken, channels-registry spam
still unanswered, full queue rebuilt here.
