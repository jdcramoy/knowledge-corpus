# Attention queue rev — pulse 2026-10-14T02:59Z (canonical attention-queue.md overwrite write-gated; harvest into it)

1. **grc-gdpr-emails — CONFIRMED unfinished prod state, still gated on Josh.** Prod 82912295
   untouched since 10-08, running, blank-posts long privacy@ emails to #gdpr-requests (dispatch
   verdict 2026-10-13T14:21Z, grc-gdpr-emails-prod-state.md). Dev truncation fix exists,
   un-promoted, no red-team verdict on record. Josh question filed 19:42Z, unanswered ~7h.
   Registry: in-flight 44.3h stale. The one gated claim PROVEN broken in prod.
2. **needs-josh debt: 37 open rows / 26 non-done workstreams >24h stale (fold 02:59Z).** Inflow
   still outrunning decisions. Oldest: bsys-28296-marketo-history (blocked 54h, Marketo prod
   import red-team FAIL). Sharpest prod-gated: grc-gdpr-emails, healer-fleet (2 HR Genie 401'd
   connections). A batched-verdict pass from Josh retires most of this in one sitting.
3. **82964017 gw_semantic_mutation_chain_canary: defect CYCLE, not a watch item.** Live read
   02:59Z: running=True, last_run 02:33Z, stop_cause=None — but the post-restart investigation
   (82964017-post-restart-cadence.md, 21:50Z) proved the v12 trigger drift is unrepaired
   byte-for-byte: each restart runs ~once then auto-stops on trigger_errors_limit (01:45Z sweep
   caught it stopped again). BSYS-29560 hourly AC unmet; the registry-invariant detection class
   it anchors stays intermittent. Josh owns Fix A (picklist repair + repush).
4. **82862814 canary_sweep_and_promote: failures recur every sweep, pre-declared, root-caused**
   (updateContact resourceName synthesis, dev-only, 16:47Z autopsy). Latest: 02:46Z sweep. Fix
   owner Josh (GWS semantic gateway ledger 147343). Do not re-triage the next tick as fresh.
5. **session-shadow RECOVERED — now-file fresh 02:59Z after ~21h blind (launchd exit 78).**
   Cross-session awareness restored; unregistered-session check ran clean this pulse
   (estate-fusion-audit is registered). Underlying launchd root cause (shared with
   agent-command-watcher) still awaits Josh's go — triage row session-shadow-crash-exit78 open.
   Watch: confirm the recovery holds across pulses.
6. **channels-registry agent bus spam still live** — duplicate "seeded wave-3" lines every read,
   inflating corroboration tallies. Asked 19:42Z, unanswered; triage row filed 21:45Z pulse.
7. **Mission-control escalation tier still missing.** RESOLVED half: non-done staleness now
   computed in fold (mission-control.py:83-89, dreamer fix verified this pulse) and the board
   renders STALE banners. OPEN half: no prod-gated tier, so rows blocking live prod state
   (grc-gdpr 44h+) age in the same list as doc approvals. Two Josh questions filed 20:45Z,
   unanswered.

CLEARED this pulse: fold-staleness-blindspot (fix landed, verified); session-shadow blindness
(recovered); fleet nightly jobs one-class root cause (resolved per 11:15Z dispatch verdict).
