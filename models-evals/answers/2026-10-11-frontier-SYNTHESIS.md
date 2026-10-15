# Fusion synthesis — 10 frontier ideas for the harness (2026-10-11)

Panel: baseten/kimi-k3 (11.3k tok), fireworks/glm-5.3-flash (10.4k tok), main session.
Full panel answers: same dir, `2026-10-11-frontier-*.md`. Pairwise similarity low (0.01-0.4) = genuinely divergent framings; convergence on twin/calibration/envelopes/denominators/skill-fitness across all three lists raises confidence.

## The 10 (ordered as a dependency stack: truth → simulation → trust → autonomy → prediction → steady-state)

1. **Estate Twin** (kimi#4 + glm#3 + main; replay-gym already accepted) — nightly versioned snapshot of recipes/connections/schedulers/Jira into a queryable twin; prod-touching proposals must attach a twin-run diff; twin age stamped on every answer, fail closed >24h.
2. **Integrity Mesh** (kimi#1 Proof-Bearing Claims + glm#6 Double-Entry Estate) — write-time: claims require re-fetchable receipts (job id, row-count delta, digest); nightly: reconciler diffs claims/build-ledger vs live Jira/Workato, flagging orphans (claim, no proof) and ghosts (state, no claim). Kills "the estate that lies to itself" at both ends.
3. **Denominator Oracle / Actuary** (kimi#2 + glm#10) — every job declares expected N from an independent count; "green" = coverage ≥ threshold, not exit 0; nightly Monte Carlo deep-audit publishes a CI on estate health that sizes autonomy (see 5).
4. **Calibration Ledger** (kimi#3 + glm#4) — falsifiable predictions with confidence + resolve dates; nightly Brier scoring; calibration gates autonomy tiers, dissenter fast-pass, fusion routing. Trust becomes measured, not configured.
5. **Standing Orders** (glm#2 Decision Compiler + kimi#7 Delegation Envelopes + glm#1 Reversibility Ladder) — Josh legislates once: mined from decision-inbox history, dissenter-attacked, one-approval policies (scope, dollar cap, expiry, auto-shrink ratchet). The 11-deferral queue becomes the training corpus; autonomy expands at the speed of evidence (3 feeds it).
6. **Saga Protocol / Hot Standby** (kimi#3 + glm#9) — hash-chained mission journals with compensating actions; any crashed lane resumes from checkpoint; fingerprint mismatch forces re-plan. Prerequisite for all autonomy; kills context-loss + ledger-corruption bug classes.
7. **Skill League** (kimi#9 + glm#8) — per-skill invocation/outcome/cost telemetry; quarantine reversibly; dreamer runs fix-or-kill; portfolio of 57 skills instead of a junk drawer.
8. **Precursor Radar** (kimi#8) — z-score leading indicators over workato-health history; pre-failure tickets filed 24-72h ahead as scored predictions; quiet until precision proven.
9. **Chaos Canary** (kimi#10) — weekly fault injection into the twin (kill connection, corrupt fixture, stall scheduler); detection latency becomes a fleet metric; undetected faults auto-file monitoring proposals.
10. **Shadow Estate** (kimi#5) — deferred decisions execute as dry-run counterfactuals; a regret ledger ("3 of your 11 deferrals would have saved ~$X") converts the bottleneck itself into evidence for sizing 5's envelopes.

Cut, with reasons: **Treasury & Spot Swarm** (glm#5 — strongest Goodhart exposure; revisit after 4/5 prove out) and **Shadow Amendments** (glm#7 — valuable but narrow; rides the twin's fixture library later).

**Build order if it were our week:** 2 → 3 (stop the lying, cheap) → 1 (foundation) → 6 (safe long lanes) → 4 → 5 (the autonomy payoff) → 7/8/9 steady-state → 10 feeds 5.
