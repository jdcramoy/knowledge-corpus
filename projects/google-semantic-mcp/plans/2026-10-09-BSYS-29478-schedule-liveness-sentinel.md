# BSYS-29478: Fleet schedule-liveness sentinel — plan ready (2026-10-09)

Status: plan posted on the ticket (comment 1134467), awaiting Josh's build authorization.
Source design: dreams/proposals/2026-10-07-gw-semantic-schedule-liveness-sentinel.md (accepted, dissent-answered).

Build: one dev recipe gw_fleet_liveness_sentinel, hourly lowercase minutes:60 no anchor;
dynamic folder enumeration of running schedule-trigger recipes; per-recipe alert when
now - last_success > 3x interval AND stop_cause=trigger_errors_limit; Slack dashboard
digest (healthy) / immediate DM (anomaly); 82795586 postmortem prerequisites mandatory
(desc reads, refusal exclusion, self-heartbeat into gateway-silence, sentinel_muted row).

Pinned at kickoff: exact recipe ID hosting the Slack dashboard digest line.
UAT: 24h soak + forced canary anomaly. Rollback: delete recipe + event rows.

Loop pass note: 2026-10-09 jira-autotriage pass reviewed the design for build-readiness,
no design changes; ticket already carried 5 points.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [The Workato KB: RAG++ over all documentation, and the dreaming team](../../../../kb-corpus/confluence/extbt/2938929237-the-workato-kb-rag-over-all-documentation-and-the-dreaming-team.md)
- [2024/05 May Lookback](../../../../kb-corpus/confluence/intbt/540639287-202405-may-lookback.md)
- [Schedule Update for Product Usage Recipes](../../../../kb-corpus/confluence/extbt/340526773-schedule-update-for-product-usage-recipes.md)
- [2023/12 December Lookback](../../../../kb-corpus/confluence/intbt/388268205-202312-december-lookback.md)
<!-- kb-bridges:end -->
