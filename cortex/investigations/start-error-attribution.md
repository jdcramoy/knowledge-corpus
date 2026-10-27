# Start-ERROR attribution — regression "could not start run" trio (read-only, 2026-10-17)

Investigator: cortex read-only session. Method: wt recipes get / jobs / connections list +
testcases cases (all read-only GETs), runner source analysis, nightly history 10-07→10-17.
No test run was fired (POST run_requests is a write — out of charter).

## VERDICT FIRST

- The prior Group C guess "common connection/auth drift on all three" is **KILLED** — one of the
  three has no connections at all, and the other two's connections are authorized/healthy.
- The "runner-side harness failure" guess is **KILLED** — same runner, same token, same night:
  ~18 recipes start test runs fine while these fail with 100% fidelity across 5+ nights.
- **BSYS-29383 attribution: KILL.** BSYS-29383's verified root cause is the AHQ workspaces'
  deployment-tables memory pattern — different workspace, different mechanism. Decisive
  counter-evidence: 82239660's own scheduler jobs succeeded at 00:05/00:10/00:15/00:20 on
  2026-10-17 while the 00:14 nightly failed to start its test run. A workspace-wide
  OOM/502 pattern cannot coexist with a provably healthy recipe failing only at test-run start.
- Actual cause class: **chronic per-asset Test-Automation-API run-start rejection**, bound to the
  recipe's TEST CASE (not the recipe's health, connections, or running state). Most probable
  mechanism: the scaffolded cases fail server-side validation at POST /api/test_cases/run_requests
  (mock trigger input / mocked-step references that don't match the current recipe), so the run
  request is refused before any job is created. Exact API error body unrecoverable (see gap below).

## Per-recipe findings (live, 2026-10-17 ~03:20 PT)

### 82239660 — POC | HR Genie Runtime Connection Hygiene Audit
https://app.workato.com/recipes/82239660
- running: true; 10,431 succeeded / 27 failed lifetime; scheduler jobs succeeding every 5 min
  RIGHT NOW (j-AbzRYQT9-Xg8efr-CD 2026-10-17 00:20:51, status succeeded).
- Connection 13685697 (Workato API, workato_api_connector): authorization_status=success,
  connection_lost_at=null. db_table/custom_code/recipe_function are connectionless.
- Test case citc-AboAHG4Q-dnsQBe-CD ("Untitled test case 1", created 2026-10-02 23:46) exists.
- Verdict: recipe healthy, connection healthy → **test-case-bound run-start rejection**.
  Case predates the recipe's 10-04 20:25 edit — stale case references plausible.

### 82727069 — run_genie_evals
https://app.workato.com/recipes/82727069
- running: false; job_count = 0 — NO job of any kind, test or live, has EVER been created.
- Recipe has ZERO connections (workato_skill + workato_db_table + workato_genie + js_eval —
  all connectionless). Connection/auth drift is structurally impossible here.
- Test case citc-AbsBKJxC-JYEz48-CD (created 2026-10-08 18:17) exists.
- Erroring every nightly since its first scan (10-09). Verdict: **test-case-bound run-start
  rejection**; case has never once validated.

### 82959480 — create_prospect (Outreach MCP tool recipe)
https://app.workato.com/recipes/82959480
- running: true; job_count = 0 — never run, test or live (confirms BSYS-27111 re-verification).
- Connection 15862972 (Outreach | SDK, integration@workato.com): authorization_status=success,
  connection_lost_at=null.
- Test case citc-AbsoNY6e-TcLtdJ-CD (created 2026-10-10 01:36, 13 min after last recipe edit) exists.
- Erroring every nightly since first scan (10-11). Verdict: **test-case-bound run-start
  rejection**; scaffold case born invalid (mocks/checks never matched), not rotted by a later edit.

## The class-level evidence (nightly history 10-07 → 10-17)

- Current trio errored on 10-10, 10-11, 10-12, 10-16, 10-17 — every appearance, never a pass.
- 82727069 errors since 10-09. 82239660 first scanned 10-10 → error. 82959480 first scanned
  10-11 → error. Pattern: error begins with the recipe's FIRST nightly scan and never recovers.
- 10-09's error trio was DIFFERENT: {82273581 execute_google_workspace_operation, 82727069,
  82794233 FUNC | Resolve Active HR Genie MCP Runtime Child V2}. Live check today:
  82273581 and 82794233 both now have ZERO test cases (verified via wt testcases cases).
  **The only observed exit from this error class is test-case deletion** — they were never repaired.
- Passing controls disprove every simple discriminator: 82252165 (workato_skill trigger,
  running=true, 30 jobs) and 82855731 (running=true) start test runs fine. Running-state,
  trigger type, and project are all ruled out.

## Runner mechanics (why the report says only "could not start run")

- regression-nightly.py `run_recipe_cases()`: POST /api/test_cases/run_requests via
  `wt testcases run --recipe <id>`; "could not start run" = response has no `data.id`.
- On any HTTP error, wt prints `HTTP <status>` + body to STDERR and exits 1; the runner wrapper
  captures stderr into a `detail` field (150 chars) — **but the report renderer drops it**.
  launchd log /tmp/fleet-regression.out is truncated at each run start; the error body is lost.
- One-line harness fix: render `detail` on start-ERROR lines. That would have answered this
  attribution in one night.

## What was NOT verified

- The exact API error message/status for the run-start POST (needs one POST run_requests — a
  write; deferred to a Josh-approved probe, or will surface once the runner renders `detail`).
- Test-case internals (mock config / check step references) — no read API for case detail
  (/api/test_cases/<id> 404s); would need the in-page web_api route via Orca browser.
- Whether the invalid-case mechanism is stale step references vs invalid mock-trigger input —
  both fit the evidence; indistinguishable without case detail.

## Recommended next steps (for Josh / triage)

1. Fix the runner to render `detail` on start-ERRORs (one line) — permanent diagnosis.
2. One-shot probe (Josh-approved, dev-side): POST run_requests for 82959480 alone, capture the
   error body, then delete + re-record its test case with valid mocks and confirm the class exits.
3. Stop citing BSYS-29383 for this class; re-point the triage card at test-case validation.
4. If the scaffold that creates "Untitled test case 1" cases never validates them, fix the
   scaffold — every future auto-scaffolded case would otherwise join this error class forever.
