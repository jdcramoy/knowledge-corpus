# BSYS-29461 — Wire harness-dreamer and project-dreamer fleet jobs into the heartbeat contract

Ticket: https://workato.atlassian.net/browse/BSYS-29461 (epic BSYS-29454, Backlog, points 1).
Finding premise was stale on the 2026-10-09, 2026-10-10, and 2026-10-11 passes. Jira status comments: 1134566 (10-09), 1134777 (10-10), 1134959 (10-11). Points 1 set. Deduped on the 2026-10-11 evening pass: re-verified live (heartbeat rows dreamer 2026-10-11T03:48:03Z, project-dreamer 2026-10-11T04:48:19Z; both fleet logs "done validated"), no repost.

## Verdict

The wiring has existed end to end since the run-job.sh v2 fleet runner (2026-10-08). Both dreamers heartbeated on their most recent scheduled runs. No build needed; close on evidence.

## Live evidence (2026-10-11)

- knowledge/garden-reports/heartbeat.jsonl: dreamer row 2026-10-11T03:48:03Z, project-dreamer row 2026-10-11T04:48:19Z (last night's scheduled runs). Note: newer rows use the job key dreamer; the 2026-10-09 row reads harness-dreamer. Anything grepping the old name will miss recent rows.
- Fleet job defs carry both jobs through run-job.sh: kit repo bin/fleet/jobs/dreamer.prompt and project-dreamer.prompt, mirrored in ~/.local/bin/fleet/jobs.
- knowledge/dashboard.html renders fleet-dreamer and fleet-project-dreamer machine-health tiles.

## Not verified

- Tonight's 23:43 and 00:37 runs had not fired at time of writing; next-run heartbeat appends are inferred from mechanism plus observed runs through 2026-10-11.
