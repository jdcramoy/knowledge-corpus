# Attention queue — rebuilt 2026-10-27T05:50Z (cortex pulse)

1. **PROD P1 83197291 (BSYS-29982): verdict tick 14:00Z today.** Attribution investigation
   landed; fix was NOT fleet-made (code untouched since 10-20, stop→start in the 06:43-06:50 PT
   window); surviving candidates are Josh manual or a Workday-side ISU grant. Josh calls
   pending: force-run for freshness evidence vs let the 07:00 PT tick cover it; re-export
   manifest 361068 (triage rows 9-11h old).
   Refs: investigations/bsys-29982-fix-actor-attribution.md; https://app.workato.com/recipes/83197291;
   https://workato.atlassian.net/browse/BSYS-29982.
2. **Needs-josh rot: 19 open rows, oldest 98.5h (bsys-29744-item4 prod hot-swap go); /needs-josh
   still never run since approval 10-26.** Sharpest live asks: bsys-29744-item4 prod hot-swap go
   (98.5h); btgenie20 remediation re-review + Slack app move (96-97h); ops-visibility
   ops-server.py restart approval (91.6h); btg-sweeper envelope (68h); pilot live + multi-genie
   AWS cutover confirm (40h).
   Refs: mission-control fold 2026-10-27T05:50Z.
3. **FY27 review-cycle squad cutover landed (hr-genie-fy27-review-cycle).** Recipes
   83296324 / 83296325 live-verified Running=True; 7 skills attached; TEST twin archived.
   Remaining: calibration-sheet row config + prod-promotion decision (Josh). The
   convert_to_skill-stops-backing-recipe gotcha fired twice in one build; regression-test
   canon candidate filed to triage.
   Refs: https://app.workato.com/recipes/83296324; registry hr-genie-fy27-review-cycle.
4. **Error-canon sensor: phantom-fire loop, Josh's fix-or-disable decision pending (8.4h in
   needs-josh).** Dream 2026-10-27 corroborates with the same verdict (fix the sensor, not the
   symptoms); this pulse again emitted phantom fingerprints on clean calls. No more --record
   calls until fixed.
   Refs: dreams/2026-10-27.md; investigations/error-sensor-phantom-rate.md.
5. **Claim ledger: gardener must retire or update clm-006** (local marketplace plugins load
   in place, verdict STALE) per the claim-staleness sweep that landed 01:43Z. A stale
   load-bearing claim is worse than none.
   Refs: investigations/claim-staleness-sweep-2026-10-27.md; claims/claims.jsonl; triage
   claim-clm-006-stale-retire (open).
6. **Estate remediation pair, both parked on Josh 15+ days:** personal prod Slack connection
   19182094 still live after flag (BSYS-29986); Frontify prod token rotation owed 157h+
   (BSYS-29746, compromised-on-record; dev side done, prod rotate is Josh's fire).
   Refs: garden-reports/estate-2026-10-26.md; registry estate-remediation.
7. **Decision-fatigue queue in /proposals:** canary recovery-clear (accept/reject), corpus
   proposals A-D, roadmap-gap-jury (now 3 witnesses per dream 10-27). First /needs-josh run
   should sweep these with it.
   Refs: registry harness-dreamer; dreams/2026-10-27.md.

Notes this pulse: dispatched ONE sweep (flash) live-classifying the 6 zombie in-flight
registry rows (195-365h stale); findings → investigations/zombie-inflight-registry-rows-2026-10-27.md;
triage hygiene row zombie-inflight-registry-closeout filed for the closeout events. Killed:
gardener-nightly-dark-1025 (verified-hold TERMINATED 04:20Z, surface changed, no escalation
needed). gws-semantic-gateway re-wake condition unchanged (mtime).

Killed this pulse: SYNC Platform P3 83362376 (live-verified recovered: newest job 20:35 PT
succeeded, 1 failure total, watchdog 2+ threshold not met). Estate zombie heat (noise).
mcp-backing 83154018 (closed).
