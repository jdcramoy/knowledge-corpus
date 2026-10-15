# DriftFix external-edit provenance — 83074639 + 83074329 (2026-10-15)

Investigation of workato-watchdog 2026-10-15 P2 finding `driftfix-external-edit-83074639-83074329`.
Dispatched by cortex-coordinator-pulse 04:20Z (dispatches.jsonl). READ-ONLY pass — nothing mutated.
Method: AIRO read tools (recipe_get, job_list, job_get, recipe_list, genie_list, collaborator_list),
build-ledger subtraction, full Claude-transcript sweep, harness tooling fingerprint match.

## Verdict (one line)

Both assets are READ-ONLY drift-observability tools built interactively on the evening of 2026-10-14
by a NON-FLEET editor (not Josh's Claude harness — proven, not just ledger-subtracted); most likely a
human workspace member working UI-side, possibly Copilot-assisted, with Data Genie Builders affiliation
the tightest (circumstantial) correlation. Behavioral risk: LOW. The two recipes do NOT consume or
duplicate each other's data; the real overlap is with the EXISTING [DRIFT FIX] skills.

## (1) What each recipe does / what is new

### 83074639 `get_fix_proposals` — NEW Workato skill (not an edit to an existing asset)
- URL: https://app.workato.com/recipes/83074639 — project 10593549, folder 35202337 (the established
  [DRIFT FIX] folder). Created 2026-10-14 22:47:39 EDT, last saved 22:51:18 EDT, Running=True.
- Reads data table DriftFix_Change_Log (table 157369, newest 1000) and, per matching finding, joins
  DriftFix_Apply_Log (table 157379) filtered by change_id. Optional filters: run_id, change_id,
  table_name, status (all blank-match-all, case-insensitive on table/status).
- Returns proposals with review-workflow fields: review_status, reviewed_by, resolution, plus
  per-record fix SQL (proposed_query), rollback SQL (rollback_query), run_order, depends_on,
  apply_status, query_id. `requires_user_confirmation=false`; description explicitly states
  "this tool never modifies data." Skill jobs confirm read-only (2/2 succeeded, <1s).
- Relationship to existing estate: functional SUPERSET of `[DRIFT FIX] retrieve_proposal`
  (82928217, https://app.workato.com/recipes/82928217) — same two tables, same change_id join, but
  retrieve_proposal requires run_id and returns F01/query-shaped output WITHOUT the review/rollback
  fields. Raw API pull shows 83074639 has `copy_count: 1`; combined with the schema superset, this
  looks like a clone-and-extend of retrieve_proposal adding an approve/reject/apply review workflow
  (statuses proposed/approved/rejected/applied are new vocabulary for the project).
- Test traffic: 2 jobs, both titled "Workato Skill: start workflow: Genie ID=mcp_mock_genie_id,
  Conversation ID=mcp_mock_converation_id, Call ID=mcp_mock_call_id" at 22:53:17 and 23:29:51 EDT —
  the mcp_mock signature (see editor section).

### 83074329 `Get Drift Tables Data` — NEW recipe function
- URL: https://app.workato.com/recipes/83074329 — project 10593549, folder **35664342** (a DIFFERENT
  folder than the established 35202337; sole recipe in that folder). Created+saved 2026-10-14
  22:27:11 EDT (single version), Running=True.
- Reads ALL rows (limit 1000) from [LOG] TABLE_DRIFT_STATUS (table 154870 — 30 rows at read time)
  and [LOG] Drift Reports (table 140856 — 450+ rows), returns both arrays with counts. No filters,
  no writes. Live job j-AbxKkBBY-8E9L4a-CD confirms: two get_records calls, 0.1–0.2s each, succeeded.
- These are the drift DETECTOR's log tables (DATA_GENIE.WORKATO_ANALYTICS scope; Drift Reports rows
  carry File Path into /DataGenie/DriftReports/...). The existing `[DRIFT FIX] list_drift_reports`
  (81852212, https://app.workato.com/recipes/81852212) discovers the same reports by RECURSIVE
  FileStorage search; 83074329 is the cheap table-backed index over the same domain. Overlap of
  PURPOSE, different SOURCE — not a byte-level duplicate.
- Test traffic: 4 jobs, all "Processed event" (recipe-function calls, no genie context visible):
  22:28:12, 22:32:11, 22:37:13 EDT (build-test loop right after creation), then 23:29:46 EDT.

### What changed on 83074639 between 22:47 and 22:51
Not recoverable line-level (no snapshot of the 22:47 version exists locally; env-diff-state.json is
class-level and carries neither ID). Four minutes between create and final save = minor
post-create adjustment, typical of UI editing.

## (2) Editor identity

### Ruled OUT: Josh's Claude fleet (stronger than the watchdog's ledger subtraction)
- Build ledger: 0 rows for either ID (watchdog's original signal — confirmed).
- Exhaustive transcript sweep (`rg "83074639|83074329"` over ALL ~/.claude/projects/**/*.jsonl):
  the only sessions touching these IDs are (a) the watchdog's own 10-15 run (63766773 + subagent,
  03:13–03:21Z), (b) the fusion-analysis session's watchdog digest (0084d622), (c) the cortex pulse
  that dispatched this investigation (8c42297d), (d) this session. NO builder session exists.
- No manifest in ~/Documents/workbench/manifests/, no mission-control rows, no dispatch records.

### Ruled OUT: scheduled job / API-token automation
Recipes do not self-create; no estate automation writes recipe code; the cadence (create → 3 test
jobs in 10 min → save → skill test) is an interactive human/agent build-test loop, not automation.

### The mcp_mock fingerprint (explains the skill's jobs, not the builder)
`Genie ID=mcp_mock_genie_id` (incl. the "converation" typo) is the known signature of MCP-surface
probe/test invocations — canonized in workato-health.py ("mcp_mock registry probe jobs … noise by
design") and watchdog 10-09/10-11 (82090477 mock-probe quota burn). So 83074639 was invoked THROUGH
an MCP surface with mock context at 22:53 and 23:29 EDT — either Josh's own registry health probes
hitting a newly-registered skill (implies the builder attached it to a probed MCP server same-night)
or builder-side MCP testing. The 23:29:46 (83074329) / 23:29:51 (83074639) pairing, 5s apart, reads
as ONE sweep or test event touching both tools.

### Circumstantial collaborator-activity correlations (EDT, 2026-10-14; weak evidence, any-activity stamps)
- Joel Ang (Data Genie Builders) — last activity 22:58:30 — 7 min after the final 83074639 save,
  inside the test window. Tightest hit; group affiliation matches the DATA_GENIE table scope.
- anna.delosreyes (Workspace Admin) 23:11:59; [colleague] (Sales Genie Builders) 23:15:20 —
  inside the window, weaker.
- james.soh (Data Genie Builders) 00:09:50 (10-15) — just after the window.
- Josh's own account: 23:53:42 — UNRELIABLE signal; the harness (incl. the watchdog itself,
  23:20–23:47 EDT) generates API traffic as Josh continuously.

### Style evidence
- 83074329's Title-Case name + description ("Reads all rows from … and returns them to the user")
  is characteristic of Workato Copilot/AI-assisted generation, unlike the hand-crafted,
  prompt-engineered skill descriptions of the original 7 [DRIFT FIX] recipes.
- BOTH new assets drop the established `[DRIFT FIX]` naming prefix; 83074329 sits outside the
  established folder. Consistent with a different author or a Copilot flow, not the original
  maintainer's hand.

### Ranked hypotheses
1. MOST LIKELY: a human workspace member building UI-side (possibly Copilot-assisted), Data Genie
   Builders affiliation plausible (Joel Ang correlation). Evidence: interactive cadence, Copilot
   style, convention break, collaborator timing.
2. POSSIBLE: Josh hands-on in the UI (BSYS-29462 lists "Josh UI / Codex / Orca" as the historical
   external editors). No positive evidence either way; his activity stamp is contaminated by harness
   traffic.
3. UNPROVEN: another AI client outside the fleet (Codex/Orca). No session artifact found.
Definitive attribution is not possible from available surfaces — Workato recipe metadata does not
expose last-editor; the workspace audit log (UI-only, not pulled — read-only scope) is the surface
that would settle it.

## (3) Behavioral risk

- DIRECT RISK: LOW. Both recipes are strictly read-only (data-table get_records; no writes, no SQL
  execution — fix/rollback SQL is returned as inert TEXT). All 6 observed jobs succeeded in <1s.
- CROSS-CONSUMPTION: NONE. 83074329 reads tables 154870/140856; 83074639 reads 157369/157379 —
  disjoint sets. 83074329 neither consumes nor duplicates 83074639's data. Both only READ tables
  written by the drift-detector/proposal pipelines; no write contention with anything.
- REAL OVERLAP is with the EXISTING skills: get_fix_proposals ⊇ retrieve_proposal (same sources,
  superset output); Get Drift Tables Data ~ list_drift_reports in purpose (table-backed vs
  file-walking). If old and new are attached to the same Genie (three exist: Drift Fix Genie
  gin-AbWxkCLd-8wRwmG-CD, Drift Check Genie gin-AbJ4d8Pr-FMbXpn-CD [10 skills], Drift
  Investigation Genie gin-AbQpfH8c-wafcsH-CD), the LLM faces tool-selection ambiguity between
  near-equivalent tools returning different shapes — the main coherence risk to watch.
- DATA EXPOSURE: outputs are internal metadata (Snowflake table names, drift types, file paths) and
  raw proposed/rollback SQL text. Low sensitivity in dev; flag if anything here is ever promoted —
  the red-team gate would apply then (none applies now; project is dev-only, externally managed).
- GOVERNANCE: no manifest, no red-team verdict, no ledger rows — EXPECTED for this project:
  BSYS-29462 designated it externally-managed, and watchdog Job 4's subtraction scan is the
  standing control. It worked as designed (detected <5h after the edits).

## Not verified (explicit)

- Which Genie(s)/MCP server(s) the new assets are attached to (genie_get returned empty detail;
  no mcp_server list tool exists). The mcp_mock jobs imply an MCP-surface registration for
  83074639 but do not prove which server.
- Editor identity (ranked hypotheses only; needs the UI audit log or Josh's memory of the evening).
- Folder 35664342's name (folder_list under project root returned 0; not pursued — two-strike rule).
- What changed between 83074639's 22:47 create and 22:51 save (no pre-image exists locally).
- Whether table 157369/157379 actually contain the new review-status columns the skill reads
  (schema read not taken; job success at 22:53 implies yes).

## Evidence index

- Recipes: https://app.workato.com/recipes/83074639 · https://app.workato.com/recipes/83074329 ·
  https://app.workato.com/recipes/82928217 · https://app.workato.com/recipes/81852212 ·
  https://app.workato.com/recipes/82926620
- Jobs: https://app.workato.com/recipes/83074329/job/j-AbxKkBBY-8E9L4a-CD (full trace, read-only
  proof) · 83074639 jobs j-AbxKCQYT-soK4bk-CD (22:53 EDT), j-AbxKkDno-pHWnT4-CD (23:29 EDT)
- Watchdog report: ~/.claude/knowledge/garden-reports/watchdog-2026-10-15.md (P2 #1)
- Bus: dreams/bus/workato-watchdog.jsonl (03:20:46Z + 03:47:05Z findings)
- Project doctrine: ~/.claude/knowledge/projects/drift-fix-project.md,
  projects/drift-fix/BSYS-29462-plan.md (external-maintenance designation)
- mcp_mock canon: ~/.claude/knowledge/scripts/workato-health.py (is_probe_job),
  garden-reports/watchdog-2026-10-09.md / 2026-10-11.md
- Transcript sweep: rg over ~/.claude/projects/**/*.jsonl — 6 files, all watchdog/cortex/this
  session; no builder session.
