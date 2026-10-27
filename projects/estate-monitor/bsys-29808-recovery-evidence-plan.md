# BSYS-29808 containment — Recovery Evidence plan (v2, post-dissent)

Ticket: [BSYS-29808](https://workato.atlassian.net/browse/BSYS-29808) · Status: plan ready — awaiting Josh's authorization to kick off the build · Points: 3

## Live evidence this pass (2026-10-20)

- Recipe [82863630](https://app.workato.com/recipes/82863630) running=true (AIRO recipe_get).
- EM | Incident State (c212d9f8, record c95830ca): Status=resolved, Resolved at + Recovery notified at 2026-10-20T10:05:41.060Z, notification sent.
- Registrar EM | Register Started Recipe 82966985 job 03:05:40.101 PT succeeded, trigger "recipe started … Recipe ID=82863630, Started at=03:05:37.117864" → recipe was stopped **21 seconds**; registrar did the resolve + 🟢 ping.
- EM | Ops Audit Log (c4019066) for this incident key: opened → ticketed (14:18:22Z, **4h07m AFTER the resolve**) → triage-in-progress → triage_failed. **No `recovered` transition row.**
- The ticket description still claims the recipe is "no longer running" — auto-recovery never surfaced.
- BSYS-29797 note: separate item, blocked on Patricia's workspace-admin access; no-action this pass.

## Root gap

Recovery resolves resolve Incident State + green ping, but write no audit transition and never surface on a ticketed incident. Dissent round 1 added the material constraint: tickets are filed by human reaction (hours late) while auto-recovery is machine-speed (seconds), so a resolve-time-only comment leg misses exactly the fast-recovery cases that motivated the containment.

## Plan v2

**Leg A — audit row at resolve time.** New shared recipe function `FUNC | EM | Recovery Evidence` (FUNC-library precedent: 83115345). Inputs: incident key, recipe id, resolved_at. Writes Ops Audit Log row, Audit key `<incident key>|recovered` (search-then-create gate; a rare double-resolve race may double-write cosmetically — accepted). Fail-open: error monitor, retries 0, empty catch; can never block or fake a resolve.
Call sites (never re-inlined): registrar 82966985 resolve step; EM | Evaluate Service Health 82966998 stop-incident safety net + degraded/connection recovery branches.

**Leg B — ticket surfacing, both orderings.**
- B1 resolve-time (in the FUNC): look up `<incident key>|ticketed`; if present, parse ticket key via `/browse/([A-Z]+-\d+)` from Detail (anchor the URL, not the message prefix), post a one-line recovery comment via Jira connection 18702724. Covers ticket-first.
- B2 filing-time (in reaction handler EM | Capture Ticket Reaction 82971161, after the `ticketed` row): read incident Status in Incident State; if resolved, post recovery facts (resolved-at, ping sent) with the filing flow so the ticket never ships stale. Covers recovery-first — the proven BSYS-29808 case.

**Test choreography (both orderings; missing comment/row = FAIL, fail-open may not green the run).**
1. Ticket-before-start: stop TEST probe → file fixture ticket → start probe → assert resolved + exactly one `recovered` row + B1 comment.
2. Recovery-before-ticket: stop → start a second probe → file ticket via handler → assert B2 recovery facts posted.
Assertions read the audit table + ticket comments, never the resolve job's status.

## Dissent record

- Round 1: CONTEST — resolve-time-only comment leg can't cover ticket-after-resolve; led to Leg B2. Findings: `~/.claude/knowledge/dreams/bus/dissenter.jsonl` thread `bsys-29808-recovery-evidence-plan`.
- Round 2 (on v2): CONCUR. Surviving objection cosmetic: seconds-wide seam when a resolve lands mid-filing-flow (sub-second double-post or miss on the comment; the `recovered` audit row always lands). Build notes: B2 in the robot_face branch (steps 14-23; the ticket-emoji branch is gated Status=open and can never see a resolved incident) and inside the handler's existing try(30)/catch(48); manifest at build start (FUNC exports as plain `recipe` row; connection rows non-portable, Jira 18702724 needs re-auth at import per BSYS-29667 precedent); red-team before promotion; probe must live in a MONITORED scope or no incident opens; test runs file real BSYS bugs; B2 should also correct the stale description, not only comment. Live-verified: incident keys are per-occurrence (timestamp suffix → no cross-cycle B1/B2 overlap); handler steps 5/15 already fetch full Incident State (Status + Resolved at present); registrar's existing audit row keyspace `recipe_started|<recipe_id>|<job_id>` does not collide with `<key>|recovered`; ESH branches 9-16/22-32/33-43 match the plan.

## Related

[[estate-monitor]] · epic [BSYS-29554](https://workato.atlassian.net/browse/BSYS-29554)
