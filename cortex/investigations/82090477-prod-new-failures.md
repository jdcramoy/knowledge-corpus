# Investigation: prod 82090477 (Extract Design System) new-failures — 2026-10-08

- **Dispatch:** cortex autopsy-investigation, read-only (prod READ tools + file reads only)
- **Target:** [Extract Design System (prod recipe 82090477)](https://app.workato.com/recipes/82090477), project 13755171, folder 32312723
- **Trigger:** workato-health flagged new-failures at 08:17Z / 13:20Z / 15:25Z; triage item `recipe-health-82090477-new-failures` marked **built** 15:32:42Z; harness-dreamer deep-pass 23:59Z claims **unworked**. Contradiction resolution requested.

## TL;DR

The failures are **real job failures but not real user impact**: every failed (and every successful) job in the window carries `Genie ID=mcp_mock_genie_id` mock context — these are test/probe invocations, not production caller traffic. All sampled failures are the **same Google 403** from the custom Slides connector's `get_presentation_revision_guarded_v19`, at one of two unguarded steps. **No fix was deployed to prod after the 15:25Z triage mark — by design**: the triage verdict was dev-scoped, the autopsy was completed, and the fix was filed as **BSYS-29418** (not yet built). The dreamer's "unworked" claim is wrong about the triage item (it WAS worked: autopsy + ticket) but accidentally right about prod code (recipe is unchanged and will keep failing on mock probes until BSYS-29418 ships).

## (1) Are the failures real? Exact error per job trace

Yes — real failed jobs, single error signature across days:

```
Google denied access (403) — the connected account lacks permission for this operation.
at line: 100, called from: 143 → 193 → 1813
Adapter: google_slides_custom__connector_3535598_1786643879 (connection acct 19921568)
Operation: get_presentation_revision_guarded_v19
Error type: Forbidden by API server
```

Two failure modes, both the same 403 at an unguarded revision-guard step:

| Mode | Trace line | DSL step | What 403s | Sample job |
|---|---|---|---|---|
| A — source guard | line 1 (masked) | step 2 | The SOURCE presentation revision check; mock probe passes a presentation ID the connected account cannot read. Job dies in ~1–3s, nothing written. | j-AbrtLYrR-pperbF-CD, j-AbramJEa-9n3mgp-CD, j-AbrkJaeh-4Gp6zd-CD |
| B — carrier re-check | line 24 (unmasked) | step 25 | The CARRIER revision re-check after the idempotency claim returns `decision=replay`; the ledger's `resource_id` carrier (`1IPdoTXs-o96mCyTtRkctNbFgQ2M_1UvcOKQ3Nx6_kEE`) is not readable under this caller context. Extract + FileStorage writes (steps 8–14) already ran; job dies before Registry upsert (step 31). | j-Abrpzhox-WDNNKN-CD, j-Abrpzrh3-CThNH4-CD |

Job URLs: https://app.workato.com/recipes/82090477/job/j-AbrtLYrR-pperbF-CD , https://app.workato.com/recipes/82090477/job/j-Abrpzhox-WDNNKN-CD , https://app.workato.com/recipes/82090477/job/j-Abrpzrh3-CThNH4-CD , https://app.workato.com/recipes/82090477/job/j-AbramJEa-9n3mgp-CD

Critical context: **all 20 most recent jobs — successes included — are mock-context invocations** (`Genie ID=mcp_mock_genie_id, Conversation ID=mcp_mock_converation_id, Call ID=mcp_mock_call_id`). This matches the known "Surprise 1" finding in the project file: Workato Test-button / registry "try it" probes generate mock-titled jobs that count as failures, inflating health-sweep counts. No genuine end-user failure was observed in the window.

## (2) Most recent failure timestamp

**2026-10-08T14:54:37Z** — job j-AbrtLYrR-pperbF-CD (https://app.workato.com/recipes/82090477/job/j-AbrtLYrR-pperbF-CD), mode A, source-guard 403, ~3s fail.

Day's failure cadence: 07:34Z (A), 12:27Z ×2 (B, retry pair 11s apart), 14:54Z (A). Lifetime totals at read time: 124 jobs, 66 succeeded / **58 failed** — exactly matching the 15:25Z triage count, i.e. **zero new failures since the triage decision**. Jobs after the last failure succeeded: 14:55Z and 18:43Z (j-Abs34Apb-p4tTRQ-CD, https://app.workato.com/recipes/82090477/job/j-Abs34Apb-p4tTRQ-CD). The three workato-health flags (08:17/13:20/15:25Z) were the same cluster re-counted as it grew 55 → 57 → 58.

## (3) Was any fix deployed to prod after the 15:25Z "built" mark?

**No — and none was supposed to be.** Evidence:

- Current prod recipe code (fresh `recipe_get` pull this investigation) still shows steps 2 and 25 **with no error-handling wrapper** — the exact defect the autopsy identified. The recipe is structurally identical to the 2026-10-06/07 claim/carrier restructure (dev connector 1332342 v40 / prod connector 1335212 v5, prod Claim 74736296 / Finalize 74736297), which predates the triage.
- The triage decision (queue.jsonl, 15:32:42Z) reads: *"autopsy of prod Extract Design System failures approved dev-scoped"* — the work field was always "dev-scoped unless prod hotfix, which needs Josh."
- What "built" actually produced that afternoon (recorded in `knowledge/projects/google-slides-mcp.md`, section "Extract Design System failure cluster — autopsied 2026-10-08 (/triage)"): the autopsy itself, the real-defect writeup, and **BSYS-29418** (Bug, 3 pts, Josh) under new epic **BSYS-29417** "GSlides MCP: Design System Extractor Reliability" (parent BSYS-21305 FY27 VMT), explicitly "sized as its own session."

**Contradiction resolved:** triage "built" = the triage unit of work (autopsy + ticket) was completed. Dreamer "unworked" = it read the unchanged prod fail-count signal and missed the autopsy/ticket record. Both are consistent once you see "built" referred to the ticket, not a prod deploy.

## (4) Root-cause hypothesis and proposed fix

**Root cause (structural):** steps 2 and 25 call `get_presentation_revision_guarded_v19` outside any error-handling block. When Google returns 403 — an *expected* outcome for a source deck the caller can't authorize (mode A) or a replayed carrier resource not readable by the current context (mode B) — the connector raises and the job fails raw, instead of returning the tool's promised fail-closed `{ok, error_code, upstream_status, retryable}` envelope. Mock/probe traffic (Test button, registry try-it) supplies unresolvable presentation IDs at a steady trickle, so the failed-job counter climbs and workato-health re-flags the recipe every sweep.

**Contributing factor (mode B):** since the 2026-10-06/07 restructure, carriers are caller-owned (built in the caller's own Drive). A replay against a ledger row whose carrier was created under a different/deleted context can 403 on the step-25 re-check. The claim/replay ledger has no stale-resource eviction path.

**Why this is not a regression:** the failures are inherent to the interaction of fail-closed authz + unguarded steps + mock probes; the prod code is unchanged since 10-06/07 and the failure signature is identical across 10-07 and 10-08.

**Proposed fix (already filed as BSYS-29418, dev-scoped):**
1. Wrap step 2 (source revision guard) in error handling → return `{ok:false, error_code:"SOURCE_ACCESS_DENIED", upstream_status:403, retryable:false}` envelope.
2. Wrap step 25 (carrier revision re-check) → on 403, return `{ok:false, error_code:"CARRIER_ACCESS_DENIED", retryable:true}` (source unchanged; a fresh claim may rebuild), and consider tombstoning the replayed ledger row so the next call re-claims instead of replaying a dead carrier.
3. Keep idempotency/registry semantics untouched; tests for 403/404/mock/happy paths (dev recipe 78677477 first, promote with Josh sign-off).
4. Telemetry hygiene (separate, already noted in project file): health/watchdog sweeps should filter `mcp_mock` job titles so probe noise stops counting as prod failures — this is what actually stops the re-flagging.

## Not verified

- Only 4 of 58 failed jobs were trace-inspected (2 per mode, across 10-07/10-08) — the remaining 54 are assumed same-signature from identical titles/error summaries, not individually proven.
- Origin of the mock invocations (Workato Test button vs MCP registry "try it" vs internal health harness) inferred from job titles only.
- Dev recipe 78677477 state and BSYS-29418 ticket contents not re-fetched (dev tools and Jira writes were out of dispatch scope).
- Ownership/ACL of carrier `1IPdoTXs-o96mCyTtRkctNbFgQ2M_1UvcOKQ3Nx6_kEE` not checked (would need Drive-side read).
