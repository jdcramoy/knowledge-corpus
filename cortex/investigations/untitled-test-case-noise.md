# Investigation: `regression-fail-untitled-test-case-1` — seeded-junk, not recipe regressions

**Date**: 2026-10-16 · **Mode**: READ-ONLY (dev MCP job_get reads + local files; single permitted write = this file) · **Resolves triage card** `untitled-test-case-regression-noise` (open, cortex, 2026-10-16T05:27Z).

## Verdict (one line)

All 6 open canon rows are seeded noise — **zero are real recipe regressions**: 2 are the nightly's own is_test invocations failing on recipe functions that are 128k-jobs-green in real traffic, 2 are the already-classified VUA-identity unsatisfiable pair, 1 passed clean on 10-16 (stale row), and 1's test case was deliberately deleted on 10-09 (row should have closed then).

## (1) What auto-seeds these, and why "Untitled test case 1"

**Seeder**: `scripts/regression-nightly.py`, "canon auto-seed" block (lines ~259-283, comment: *"a failure with no canon entry becomes one ... the canon grows itself instead of waiting for the watchdog to rediscover failures"*). On each nightly run, for every recipe with failed cases and no existing canon entry keyed by recipe_id, it appends a row with:

- `signature: 'regression-fail-' + slugified test-case name` — since every enrolled case is literally named **"Untitled test case 1"**, all of them collapse into the single shared signature `regression-fail-untitled-test-case-1`. Distinct failure classes (missing connection, connector 404, unrunnable function) are colliding under one signature.
- `line: "Auto-seeded: test case '<name>' failing (run ..., job ...)"` — the exact phrasing in all 6 rows.

**Why the name is untitled**: the harness never creates test cases (`wt testcases` in `~/.local/bin/wt` only runs/statuses/lists — no create verb; `canonize-failure.py` doesn't create either). The cases were created 2026-09-12 era via UI/API and **never renamed or configured** — "Untitled test case 1" is Workato's default case name. The accepted 2026-10-08 triage verdict on 82273581's twin confirms it: *"Case was created 2026-09-12 and never configured - no fixture, no assertion, covers no failure class."* Some (Seismic pair) do exercise real action paths but were still authored without a name.

## (2) Real regressions or seeded junk? — per-row evidence

All job traces read live via dev AIRO MCP `job_get`, 2026-10-16. Compare with the 2026-10-12 census (`cortex/investigations/regression-unsatisfiable-tests.md`), which already classified three of these.

| Recipe | Case | Failing job evidence | Verdict |
|---|---|---|---|
| 82059061 FUNC \| Dispatch Inbox Notification | citc-AbRGm4EB | Job j-AbxrPAtf fails in 0.2 s, error "Processed event", **no recipe lines**. Job history: **128,326 total, 128,296 succeeded, 29 failed — the nightly's test job is the only recurring failure.** | **Junk — harness-shape artifact.** A recipe function can't be driven by a bare test-run invocation (no calling event); it dies instantly. Not a regression. |
| 82202341 FUNC \| Dispatch PTO Notification | citc-AbXpQ8nJ | Job j-AbxrPgDE: identical shape — 0.15 s, "Processed event", no lines. | **Junk — same artifact class as 82059061.** |
| 82248514 Seismic \| Search authorized content catalog | citc-AbYakm9F | Job j-AbshhGmt: Seismic connector 404 `RESOURCE_NOT_FOUND` on `get_runtime_actor_scope` — headless test run carries no VUA end-user identity. | **Junk — unsatisfiable-by-construction**, already classified in the 10-12 census (VUA-identity class). |
| 82272814 workspace_vua_identity_probe | citc-Aba8tpTz | Job j-AbxrRcCG: "Missing connection. Please establish connection manually" on the GWS semantic-gateway runtime connector. | **Junk — unsatisfiable-by-construction**, census row 1 (stopped diagnostic + VUA identity). |
| 82256903 Seismic \| List Intelligence recommenders | citc-AbYgrxMC | Failed 10-10 ("Missing connection", job j-AbshkEQW) but the **10-16 nightly passes 1/1** (run cirr-AbxrR64t) — connection was established since. | **Stale row — failure no longer reproduces.** Also downgrades the census's "permanent x3" classification: the VUA-identity class is connection-state-dependent, not strictly permanent. |
| 82273581 execute_google_workspace_operation | citc-AbaAmBxM | Case **deliberately deleted 2026-10-09** (sibling closed row on the same recipe documents it); recipe has dropped out of the live registry (no entry in `garden-reports/regression-registry.json`). | **Stale row — should have been closed with its sibling on 10-09.** |

Fixtures/config cross-check: no fixture under `~/.claude/knowledge/fixtures/` references any of the 6 recipes (fixture phase is a separate, already-audited class). Registry confirms 5 enrolled with 1 case each; 82273581 correctly absent.

**Answer: seeded junk / stale canon rows, 6 for 6. No recipe behavior is wrong.**

## (3) Smallest fix to stop the class recurring

Options weighed: **rename-at-seed** (impossible — the script copies the platform's case name; the junk is the case itself, not the label), **dedupe-at-canon** (already exists — `if fails and rid not in canon_now`; the problem was never dupes, it's that unsatisfiable/unrunnable cases get enrolled and seeded at all), or **exclude**.

**Recommended: exclude-at-runner, two edits in `regression-nightly.py`** (smallest change that kills both the nightly noise and the canon re-seeding):

1. A skip-list constant keyed by `test_case_id` (the 6 `citc-...` ids, or better: the 5 recipe ids + a "manual-only" tag per the census's proposed fix #2) checked in both the run loop and the auto-seed loop — one `continue` each. This stops tonight's run from re-failing/re-seeding the class.
2. In the auto-seed block, skip failures whose job produced **no recipe lines** (the "Processed event", 0-line shape of the FUNC class) — those are the runner failing to invoke the recipe, not the recipe failing. This future-proofs against new FUNC recipes getting enrolled.

Plus the one-time canon hygiene (census fix #6, still pending): close the 6 open rows as `expected-failure-suppressed` / `stale` with this file as evidence, so drift-gate stops reading false-open noise. The 10-12 census rows 1-6 remain the fuller fix (classification gate at enrollment time); this is the minimal stop-the-bleeding subset.

**Not done here** (read-only scope): no canon edits, no registry/nightly edits, no case deletions, no triage-card status change. Josh's gate: approve the skip-list + canon close-out.

## Related

- `cortex/investigations/regression-unsatisfiable-tests.md` (2026-10-12 census — the umbrella class; this file is the signature-level disposition Josh's triage card asked for)
- `cortex/investigations/regression-start-failures-2026-10-09.md`, `investigations/82272814-vua-probe-regression.md`
- Accepted triage verdict on 82273581's case (2026-09-12 creation, never configured -> delete)
