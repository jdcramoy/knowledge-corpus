# Investigation: 82272892 'Sync Google Workspace Discovery Catalog' failure burst

**Date**: 2026-10-11 · **Mode**: read-only autopsy (job_list + job_get x3, AIRO dev server) · **Dispatched by**: Josh
**Asset**: https://app.workato.com/recipes/82272892
**Connector**: google_workspace_semantic_gateway_runtime_connector_3535597_1789196780 (connection acct 22117414)
**Write note**: intended destination ~/.claude/knowledge/cortex/investigations/82272892-discovery-sync-failure-burst.md was permission-DENIED (cortex-pulse write-gate: all direct knowledge/ writes denied in dispatch sessions). Report parked at /tmp/82272892-discovery-sync-failure-burst.md — move into place with: cp /tmp/82272892-discovery-sync-failure-burst.md ~/.claude/knowledge/cortex/investigations/

## Verdict up front

The "30 failed jobs" is the recipe's LIFETIME failed count, not the burst. The Oct 10-11 burst is 8 jobs over 10 minutes, self-recovered, and the failure class is NEW: an empty-upstream-payload / data-shape failure in the catalog's Ruby normalization steps — NOT connector missing-connection, NOT VUA identity, NOT gateway outage. Cost exposure trivial.

## 1. Exact time span (job_list, dev ws 3535597, status=failed, all 30 on one page)

- **Burst window**: 2026-10-10T23:17:33.581-07:00 → 2026-10-10T23:27:35.445-07:00 PDT (06:17:33Z → 06:27:35Z Oct 11). **8 failures in 10m02s.**
- Burst cadence: irregular, ~85-180s between jobs (23:17:33, 23:17:34, 23:20:31, 23:22:45, 23:22:47, 23:24:11, 23:25:55, 23:27:35), with two 1-2s-apart pairs suggesting immediate retries. Off the recipe's normal 15-min grid (:09/:24/:39/:54).
- **The other 22 lifetime failures are NOT part of the burst**: scattered 2026-09-13 through 2026-10-08 (Sep 13 x2, Sep 14 x4, Sep 25 x9, Oct 1 x2, Oct 2 x2, Oct 3 x2, Oct 8 x1). Older failures run 5-10s; the burst jobs die sub-second (0.5-1.0s).
- First lifetime failure: 2026-09-13T02:00:09-07:00 (j-AbafN66f-rkT4Ag-CD). Last: the burst end above.

## 2. Failure class — NEW CLASS (empty payload, not connection/identity/gateway)

Three traces pulled. The two burst traces fail at DIFFERENT lines with DIFFERENT errors, both downstream of an upstream fetch that returned nothing:

- **j-AbtJKsJR-QnxxfB-CD** (23:24:11, https://app.workato.com/recipes/82272892/job/j-AbtJKsJR-QnxxfB-CD): failed line 20 'Preserve reviewed rows from re-upsert' — `Output check failed: data wasn't equal to expected value at 'output.filtered_records'. Expected to find 1 items but found 0` (error type "Test Automation error"). Input `registry_rows_json` carried 3 records; `filtered_records` came back empty.
- **j-AbtJNHaT-9m89YY-CD** (23:27:35, https://app.workato.com/recipes/82272892/job/j-AbtJNHaT-9m89YY-CD): failed line 21 'Normalize pagination limit defaults in compiled registry records' — Ruby eval `783: unexpected token at ''` — a JSON parse of EMPTY `records_json` (`code_input.data.records_json: ''`).
- **j-Abs3x34H-w6kDtH-CD** (Oct 8, https://app.workato.com/recipes/82272892/job/j-Abs3x34H-w6kDtH-CD, contrast case): failed line 28 — `Conflicting generated operation contracts for people.people.createContact@v1: activation.` That is a DIFFERENT, older class: conflicting capability rows in the catalog data itself.

Classification against the four candidates:
- **Connector missing-connection: NO.** Every line executed; the rest call (line 5) ran, DB steps ran. No "Missing connection" anywhere.
- **VUA identity: NO.** No identity/actor-scope/404 errors; the connector executed and returned data-shaped (empty) output.
- **Gateway outage: NO.** No 5xx/timeout. Telling detail: in the burst traces the `rest make_request_v2` (line 5) completes in 0.0011-0.0017s — effectively an instant empty/non-call — versus 1.05s in the healthy Oct 8 run. Something upstream returned an empty payload instantly; the recipe has no guard for that and the Ruby steps then die on the emptiness (assertion on `filtered_records`, then `JSON.parse('')`).
- **NEW CLASS: YES** — `discovery-sync-empty-upstream-payload-unguarded`: the GW discovery catalog sync received an empty/changed upstream dataset for ~10 min, and both its "Preserve reviewed rows" and "Normalize pagination limit defaults" steps fail unguarded on empty input. Distinct from the Oct 8 contract-conflict class (`catalog-contract-conflict`, 22 lifetime occurrences) which is a data-content conflict, not an emptiness failure.

## 3. Still failing? NO — bounded burst, self-recovered

- Last failure 23:27:35.445-07:00 Oct 10; **first success after the burst 23:54:38-07:00 (j-AbtJoKnN-GEMTwA-CD, https://app.workato.com/recipes/82272892/job/j-AbtJoKnN-GEMTwA-CD)** — back on the 15-min grid.
- Every scheduler run since 23:54 succeeded: continuous greens 23:54 → 05:39 PDT Oct 11 (page 1 + page 2 of succeeded, 25 consecutive). 947/977 lifetime success rate; the recipe is currently green on schedule.
- Note: no succeeded run exists between 23:27 and 23:54 — the ~23:39 grid slot either did not fire or the recipe was briefly stopped; one grid slot is unaccounted for.

## 4. Correlation with the 82862205 trace-less class and the VUA-headless signature

- **vs 82862205 'Processed event' trace-less class** (canon line 47, per 82862205-1011-guard-verdict.md): NOT correlated — that class is sub-250ms with ZERO trace lines, dying at harness dispatch before step 1. The 82272892 burst jobs have full 20-22 line traces and real step-level errors. Opposite signature.
- **vs `vua-skill-headless-test-identity-absent`** (seismic-vua-probe-regression-1011.md): NOT correlated — that signature is "Missing connection" or a connector 404 at step 1/2 in headless test jobs on the same connector family. The 82272892 jobs are SCHEDULED (not test) runs whose connection resolves fine; they die later, in Ruby data-handling steps, on empty input.
- Shared context only: same connector runtime family (GW semantic gateway runtime, acct 22117414) and overlapping night. Timing does not overlap the nightlies (seismic trio ~00:50Z, 82862205 nightly 04:48Z, burst 06:17-06:27Z). One plausible common thread worth a follow-up: the burst's instantly-empty rest response and the VUA probe's identity 404 could both be symptoms of the semantic gateway runtime having a bad window late Oct 10 — but the evidence here does not prove that, and this recipe's failure is reproducible as a plain unguarded-empty-input bug.

## 5. Cost exposure at observed cadence

- Burst as observed: 8 jobs x ~15-20s of runtime equivalent, billable steps ~6-8 per job (1 rest, 3-5 Ruby, 2 DB; variable/if/foreach logic steps don't bill) ≈ **50-60 task units total. Trivial.**
- If the burst cadence (~90s) had sustained: ~40 jobs/hr x ~7 billable ≈ 280 tasks/hr — an order of magnitude below the 320-tasks/hr Slack incident class, and it self-bounded in 10 minutes anyway.
- Steady state (15-min grid): ~4 jobs/hr x ~7 ≈ 28 tasks/hr. The 22 lifetime older-class failures add nothing material.

## Follow-ups for Josh (no action taken, read-only)

1. The real defect is the recipe's missing empty-payload guard: an empty upstream fetch should return a safe envelope (skip + alert), not die on `filtered_records` assertion and `JSON.parse('')`. Cheap fix in the two Ruby steps + the line-13 if.
2. The off-grid ~90s burst pattern with 1-2s pairs is worth one look in the recipe's error/retry config — something replayed the schedule off-grid that night.
3. Optional: check gateway runtime logs for an Oct 10 ~06:17-06:27Z empty-response window; if confirmed, this graduates from "recipe bug" to "gateway incident with a recipe symptom".

**Nothing unverified except**: the cause of the instant-empty rest response (gateway-side logs not accessible from here) and the unaccounted ~23:39 grid slot.

**VERDICT**: Bounded 8-job/10-min burst (23:17:33-23:27:35 PDT Oct 10), NEW empty-payload class (not VUA/connection/gateway), self-recovered by 23:54, ~60 tasks exposure, real fix is an empty-input guard.
