# Collector 82862205 — cadence verification log

## 2026-10-13 08:04Z (jira-triage pass)

- Live job_list: 15 most recent scheduled runs all SUCCEEDED, newest j-AbwMxn3K-3n3frE-CD at 2026-10-13 00:59 PT.
- Zero PAGE_COMMIT_ASYNC_JOB_FAILED since the 06:11 PT recovery on Oct 12 → ~19h clean; the ticket's 24h clean-cadence AC is ~19/24 accrued.
- Comment posted on BSYS-29519 (id 1136772) answering the open question from the Oct 12 23:45 note.
- Plan unchanged: 5s→60s wait at both await sites, timeout = uncommitted page (watermark retries), page cap part of the fix. Awaiting build go.
- Open: who stopped the collector Oct 12 ~07:26 PT (still unanswered).
- Stale triage-queue rows noted (statuses belong to triage-decide.py, not hand edits): `82862205-restart-ownership` (restart done Oct 12), `recipe-health-82862205-new-failures` (cadence green), `gslides-vua-prod-twin-go` (prod flip landed Oct 12, tool id 259757).

## 2026-10-13 ~21:00Z (jira-triage pass): fix appears live, provenance unknown

Live job trace j-Abwbo4RK-XCFeWM-CD (11:14-12:14 PT, succeeded, 60 min):
wait_for_async_jobs ran 50.2s and survived (old 5s timeout would have failed) —
timeout was raised. PAGE_BUDGET_EXHAUSTED pages_used=10 cap=10 deferred gracefully
with structured skip telemetry (reason page_budget_exhausted, permanent false) —
degrade-don't-die behavior from the BSYS-29519 plan is present. Long run was a
scheduler tick (corrects the earlier "not the scheduler" guess); scheduler caught
up with a 3-tick burst post-release; 13 green runs since; no PAGE_COMMIT_ASYNC_JOB_FAILED.
711 conversations deferred under the cap in the long run; subsequent 3s runs + advanced
watermark suggest idempotent drain. OPEN: who pushed the change and when — nothing on
BSYS-29519 records the build. 24h clean-cadence clock counts from the change.

## 2026-10-14 02:52Z (jira-triage pass): 24h clean-cadence criterion MET

- Live job_list: 616 succeeded / 62 failed of 680 total. Failed count unchanged from the
  last pass (62 of 570) -> 110 runs since v42 carried zero new PAGE_COMMIT_ASYNC_JOB_FAILED.
- 15 most recent scheduler runs all green in 2-3s, newest j-AbwmzJ8p-EGhEpC-CD 19:44 PT Oct 13.
- Continuous green from 16:44 PT Oct 12 = 27+ hours; the 24h AC is met as of ~16:44 PT Oct 13.
- Second hour-long green run this pass: j-Abwhackk-C386mY-CD, 17:14:56->18:10:09 PT Oct 13
  (55 min), plus the 3-tick catch-up burst. Answers the dissenter objection that the
  morning long run was a one-off; budget deferral held twice.
- Comment posted (id 1137849): criterion met; 404-classifier amendment still open as the
  remaining build scope; v42 author still unverified.

## 2026-10-14 ~13:15 PT (dev build session, Josh's build go recorded): AMENDED FIX SHIPPED as v44 (supersedes the v43 note below)

- Scope executed (only step 45 changed, diff-verified): 404 classifier rebuilt from bare
  substring (`include?("404")||include?("not found")` -> permanent skip + watermark advance,
  the masked-green data-loss surface from comment 1137755) to STRUCTURAL anchors
  (status/response/code-anchored regexes, "HTTP 404" adjacency, stable error_type_id
  err.http.response.client_error.not_found). NEW disposition: 404 on the async-commit poll =
  terminal-success (page committed/gone, reason page_commit_poll_404_terminal) instead of
  retry-forever. Timeout-deferral, budget-deferral, transient re-raise preserved.
- Steps 39/63 timeout=60 and step 31 page cap (pages_used>=10) verified live in the v42 pull
  and left untouched; the amended build scope was classifier-only.
- Evidence: pre-fix snapshot ~/.claude/knowledge/app-snapshots/bsys-29519/recipe-82862205-pre-pagecommit-fix.json;
  15/15 local Ruby classifier cases incl. DNS-"host not found" regression (v42 loses data,
  v43 re-raises); hot swap stop/start verified (running False 12:29 PT, True v43 12:32 PT);
  forced run j-AbxCAJTN-CLgeaa-CD succeeded 12:32:58 PT.
- NEW failure class on v42 this morning, NOT this fix's scope: PAGE_COMMIT_PROGRESS_REVISION_STALE
  expected=6 got=7 (CAS conflict at fail-closed verification), j-AbwramxJ-oDBNEE-CD 00:00 PT,
  j-Abx39wgC-RDtaJW-CD 05:38 PT. v43 re-raises it (visible). Needs its own triage/autopsy.
- 24h clean-cadence clock RESTARTS on v43 as of 12:32 PT Oct 14.
- Residual: poll-404/structural-404 branches are logic-proven, not runtime-proven (no safe
  dev 404 force); if Workato's real poll-404 text carries 404 unanchored, v43 re-raises
  (safe direction) instead of terminal-success - watch first occurrence.

### v44 dissent-review corrections (same build session, ~13:15 PT)

- Dissenter verdict on the v43 draft/code was FAIL with 4 material defects; all addressed:
  (D3) timeout signature now checked BEFORE any permanent branch; (D1) 404-adjacency anchor
  tightened from 20-char window (kills "after 404 ms: host not found" / "read 404 bytes;
  record not found" false permanents); (D2/D4) unproven-poll-404-premise and custom-connector
  anchor-shape caveats recorded IN the shipped code comments; (D7) wording corrected.
- EXACT shipped v44 code executed locally: 11/11 cases incl. all dissenter adversarial inputs.
- v42-window backwards audit: both long backlog-drain traces (j-Abwbo4RK-XCFeWM-CD,
  j-Abwhackk-C386mY-CD) show the ONLY classifier firings were budget deferrals
  (permanent=false, 711 conversations each); zero 404-branch firings; 8-job spread sample
  audit run in parallel.
- v44 live: running=True verified 13:12 PT; forced run j-AbxCkDkG-L9KDfJ-CD succeeded
  13:12:34 PT; failed count unchanged (64). 24h clean-cadence clock restarts on v44 13:12 PT.
- Revision-stale class (PAGE_COMMIT_PROGRESS_REVISION_STALE): NOT folded into this fix
  (correct fail-closed call), but connected: it appeared only after v42 shipped the checkpoint
  machinery (2 occurrences in 12h), so it is plausibly a regression of this fix family.
  Triage finding filed; v43/v44 re-raise it (visible). Filing: queue triage,
  slug page-commit-progress-revision-stale.
