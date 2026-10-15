# Investigation: 2026-10-11 00:50Z nightly regression trio (Seismic x2 + VUA probe)
**Date**: 2026-10-11 · **Mode**: read-only autopsy · **Investigator**: cortex dispatch (dispatches.jsonl 2026-10-11T11:39:40Z)

## Canon classification vs line 47

Line 47 signature = `test-fail-error-processed-event-no-trace-lines` (job fails with 'Processed event' and NO trace lines = canonize-failure gap / mock-or-assertion mismatch). **None of the three match it** — all three jobs have full traces (lines 0 and 1 present) and carry real connector-layer errors. This trio is a NEW signature: `vua-skill-headless-test-identity-absent` (VUA-bound Workato Skill fails at its first connector action in a headless test-run job).

## Verdicts (per recipe)

### 1. 82248514 Seismic | Search authorized content catalog — job j-AbtGkdAK-d8aQFT-CD
**Verdict: harness/test-context failure (NOT a recipe regression).**
- Trace evidence, failed line 1 (`get_runtime_actor_scope`, mask=True, 0.501s): `{"code":"RESOURCE_NOT_FOUND","message":"Seismic request failed for get_runtime_actor_scope","httpStatus":404,"retryable":false} at line: 3156, called from: 2406/2411/533` — the connector executed and its identity-bootstrap call 404'd. The connection itself was reachable; the runtime actor-scope resolution has no end-user identity in a headless test job.
- Counter-evidence to regression: identical recipe code passed 7 consecutive runs on 2026-10-01 (e.g. job j-AbnQEdow-NKYfHA-CD, 19:28Z: step 1 `get_runtime_actor_scope` succeeded in 0.094s, full pipeline through search_content -> cursor persist -> 82247580 envelope -> return). Same code, same connection; only the execution context changed.
- Latent hardening gap (worth a follow-up, not the cause): step 2 `get_runtime_actor_scope` sits OUTSIDE the WorkatoMonitor that begins at step 6 (which wraps only `search_content`), so an identity-layer failure crashes the job instead of returning the canonical safe envelope the recipe's own schema advertises. Also note AIRO validation flags stale datapill refs to `search_content_2188` schema (`internalContinuationToken`) — connector schema drift after a re-release; cosmetic tonight but should be refreshed.
- Recipe changed recently? No evidence of an edit between the 10-01 green runs and the 10-09/10-10 failures; failure is byte-identical across both nights (job j-AbshhGmt-6x3MLg-CD on 10-10: same 404, same line 3156 call stack).

### 2. 82256903 Seismic | List Intelligence recommenders — job j-AbtGmaNX-hYfpRQ-CD
**Verdict: harness/test-context failure (NOT a recipe regression); genuine recipe defect in missing fallback containment.**
- Trace evidence, failed line 1 (`list_intelligence_recommenders`, mask=True, 0.3289s): `Missing connection. Please establish connection manually` (error id 325033c8-9d27-4896-9b29-d44bb6b0ebf6, type "Missing connection") — the platform refused the call before any HTTP left the connector.
- The recipe calls the live connector unconditionally at step 2 with NO monitor block, despite its own description promising a documented-fallback catalog ("on this development tenant it transparently returns Seismic's public documented catalog"). Sibling 82256904 has exactly that containment and therefore "passed" (see shared root cause). The defect is real but the nightly FAIL's cause is environmental.
- History: last green 2026-10-01 16:28Z; identical "Missing connection" failure on 10-10 nightly (j-AbshkEQW-zkQ8cm-CD). No recipe edit evidence in the gap.

### 3. 82272814 workspace_vua_identity_probe — job j-AbtGnBBa-W4krE6-CD
**Verdict: test-case drift / invalid test (the test asserts something a headless run can never provide). Never passed anywhere.**
- Trace evidence, failed line 1 (`get_connection_identity`, mask=False, 0.1116s): `Missing connection. Please establish connection manually` (error id ed976003-e36c-4b00-8855-ae2b25f2fc0a), trigger context `Genie ID=, Genie name=, Conversation ID=test-vua-probe`.
- This skill's entire purpose is to prove a CALLER-SCOPED Google Workspace VUA identity. A headless API-driven test job has no caller identity by construction, so the probe is unsatisfiable in the nightly harness. Job history: 3 jobs total, 3 failures — 2026-09-12 (j-Aba8wFzg-9PPMYf-CD, OLD connector `..._gateway_connector_..._1789177389`), 10-10 and 10-11 nightlies (current `..._runtime_connector_..._1789196780`) — the identical failure persists across a connector rebuild, proving it is not code- or version-caused.
- Additional flag: the recipe is STOPPED (Running: False) — a stopped, never-green diagnostic skill should arguably be removed from the nightly registry rather than remediated.

## Shared root cause — YES, one cause

All three are Workato Skills whose step-2 action runs on a VUA-runtime custom connector (Seismic `seismic_by_workato_connector_3535597_1789094460` / connection acct 22111194; GW Semantic `..._runtime_connector_3535597_1789196780` / acct 22117414). The nightly runner (`scripts/regression-nightly.py`: scans workspace for recipes with test cases, executes them via the Workato API under the CLI token — no browser session, no end-user OAuth identity) cannot satisfy VUA runtime identity resolution. Depending on where the connector resolves identity, the failure surfaces as either platform-level "Missing connection" (82256903, 82272814) or a 404 from the connector's actor-scope bootstrap (82248514).

Corroborating control: sibling skill 82256904 (SAME Seismic connection 22111194) ran 16 seconds after 82256903's failure in the same nightly window and "passed" — but its trace (j-AbtGmke4-rYM8Kp-CD) shows line 1 try -> `{'error': True}`, line 3 catch output `{'type': 'Missing connection', 'message': 'Missing connection. Please establish connection manually', 'adapter': 'seismic_by_workato_connector_3535597_1789094460', 'action': 'get_content_recommendations'}`, line 4 returned the DEPENDENCY_UNAVAILABLE fallback envelope. The connection fails identically for the "green" recipes; their monitor blocks mask it as a pass. The red trio are simply the skills whose failing first call is uncontained (or, for 82272814, whose assertion is definitionally unsatisfiable headless).

Timeline note: the trio entered the nightly registry on 2026-10-10 (registry grew from ~4 to 14 recipes; commit 2bc6260). They have failed every nightly run since onboarding — this is day-1-of-coverage environment exposure, not a behavior change in the recipes.

## Recommended follow-ups (for Josh; no action taken)
1. Registry/harness fix: either exclude VUA-bound skills from headless nightly runs, or run their cases through a context that carries a VUA identity. Cheapest interim: tag-and-skip list in regression-nightly.py.
2. 82248514: extend the WorkatoMonitor to cover step 2 (actor-scope) so identity failures return the canonical safe envelope; refresh stale `search_content_2188` datapill refs.
3. 82256903: add the documented-fallback containment its description already promises (mirror 82256904's monitor block).
4. 82272814: remove from nightly registry (stopped diagnostic probe, 0/3 lifetime, unsatisfiable headless) or reclassify its test as manual-only.
5. Canon: seed new signature `vua-skill-headless-test-identity-absent` (distinct from line 47's trace-less signature).
