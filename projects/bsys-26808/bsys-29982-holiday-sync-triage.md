# BSYS-29982 — Prod Holiday Calendar Sync triage (2026-10-26)

Ticket: https://workato.atlassian.net/browse/BSYS-29982 (dupes: BSYS-29981, BSYS-29983)
Recipe: https://app.workato.com/recipes/83197291 (AHQ | AI Production, folder 35747461, epic BSYS-26808)
Workstream: bsys-26808 / holiday-calendar-sync

## Outcome

- Authorization error FIXED live during the session: 7 consecutive failures 10-20→10-26
  (step 3, Workday Search_business_object Get_Holiday_Calendars, "The task submitted is
  not authorized"), then two green runs this morning — j-Ac9KGJwp-NGFwsH-CD 06:50 PT
  (125 calendars, 138 event upserts, 2 stale prunes) and j-Ac9Kzk3h-zAzQ4Y-CD 07:36 PT.
- Recipe `running: true` at ~14:45Z. Fix window was 06:43–06:50 PT; mechanism UNKNOWN
  (Workday ISU domain grant vs connection 19909763 re-auth — no ledger row, no operator).
- Both greens were MANUAL starts (events 06:21/06:43/07:36 on a once-daily trigger).
  First natural scheduled run: 2026-10-27 07:00 PT. That closes the last AC.
- Restart plan was drafted then withdrawn after the dissenter broke it: the recipe was
  stopped at my first read (twice-verified) and running by the time the comment posted —
  an actor fixed it mid-investigation.

## Lessons

1. **Estate state drifts faster than a triage session.** Verify the LIVE state immediately
   before posting; a state read from 30 minutes ago is stale evidence, not evidence.
2. **Dissenter earned its keep:** caught running=true, the retry-mechanism error
   ("automatic retry" was actually start/stop/start by an unknown actor), the inverted
   stopped_at reading, and the unattributed fix-mechanism guess.
3. **Duplicate filing defect:** the morning triage pass filed BSYS-29983 while BSYS-29982
   was open — dedupe happened on summary+body at POST time only after the fact. Findings
   routed to /triage.

Comment 1149238 on BSYS-29982 carries the full trace-cited plan.
