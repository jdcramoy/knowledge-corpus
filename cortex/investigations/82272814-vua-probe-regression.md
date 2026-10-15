# Autopsy: regression-nightly 2026-10-12 04:50Z — workspace_vua_identity_probe 82272814, job j-AbtmpY6g-d3ccQH-CD

**Date**: 2026-10-12 · **Mode**: read-only (no edits, no stop/start, no prod calls) · **Recipe**: https://app.workato.com/recipes/82272814 · **Job**: https://app.workato.com/recipes/82272814/job/j-AbtmpY6g-d3ccQH-CD

## (a) What exactly failed

Job j-AbtmpY6g-d3ccQH-CD (started 2026-10-12T00:48:11-04:00, duration 0.5s, trigger context `Genie ID=, Genie name=, Conversation ID=test-vua-probe`):

- **Step**: line 1 (first action after `start_workflow`), operation `get_connection_identity` on `google_workspace_semantic_gateway_runtime_connector_3535597_1789196780` (connection account 22117414). Mask data: False. Line time 0.1229s.
- **Error**: `Missing connection. Please establish connection manually` — platform-level refusal BEFORE any HTTP left the connector. **No HTTP status code** (contrast with the Seismic sibling's 404, below).
- Error type: `Missing connection`; error id `cb63a73e-74eb-4848-9784-99b4a1fe29a4`; adapter reported as Workato; actionable: true.
- Lines table: line 0 `workato_skill.start_workflow` OK (0.0053s); line 1 failed; the recipe's return step (line 2/3) never ran.
- Recipe state at read time: Running: False (stopped diagnostic skill). Code = 3 steps, no monitor/error-handling block, so the step-1 failure crashes the job (by design for a probe).

## (b) Same root cause as the seismic pair? YES — one cause, two surface signatures

Tonight's seismic failures pulled live and compared:

- 82248514 (https://app.workato.com/recipes/82248514/job/j-Abtmo4kR-QcHAsw-CD): line 1 `get_runtime_actor_scope` on `seismic_by_workato_connector_3535597_1789094460` — HTTP **404** `RESOURCE_NOT_FOUND` ("Seismic request failed for get_runtime_actor_scope", retryable false, connector line 3156, call stack 2406/2411/533).
- 82256903 (https://app.workato.com/recipes/82256903/job/j-AbtmozEz-tDX3Np-CD): line 1 `list_intelligence_recommenders`, same connector — `Missing connection. Please establish connection manually` (error id 13afa0b7-a84f-43f5-baf1-564120d0519a), no HTTP code.

All three are Workato Skills whose first connector action runs on a **VUA-runtime custom connector** (Seismic 1789094460 / GW Semantic 1789196780). The nightly runner executes test cases via the API under the CLI token — headless, no browser session, no end-user OAuth identity — so VUA identity resolution is unsatisfiable. Where identity resolves at the platform connection layer the failure is "Missing connection" (82272814, 82256903); where it resolves inside the connector's actor-scope bootstrap it surfaces as the connector's own 404 (82248514). Same class, different depth in the stack. This matches the 2026-10-11 autopsy verdict (investigations/seismic-vua-probe-regression-1011.md, signature `vua-skill-headless-test-identity-absent`) and cortex bus finding seismic-vua-trio-verdict (2026-10-11T08:45:41).

Byte-identical recurrence: 82272814 failed with the same step/adapter/message on 10-10 (j-AbshkmLx-twPdhc-CD) and 10-11 (j-AbtGnBBa-W4krE6-CD, error id ed976003-e36c-4b00-8855-ae2b25f2fc0a); the seismic pair likewise repeated their 10-10/10-11 errors verbatim tonight. Canon line 45 already carries 82272814's auto-seeded open entry (signature regression-fail-untitled-test-case-1, test case citc-Aba8tpTz-wLLoPe-CD).

## (c) recipe_builder_push-reverts-VUA trap? NO — known headless class, not a new class and not the revert

Evidence against the VUA-revert trap:
1. The failure is identical across three consecutive nightlies and across a connector rebuild (the 2026-09-12 job failed the same way on the OLD gateway connector 1789177389; current failures are on runtime connector 1789196780). A push-revert would show a before/after discontinuity tied to a push event; there is none.
2. 82272814 has never passed anywhere — 3 lifetime jobs, 3 failures, all "Missing connection" in headless context. There is no green baseline to have regressed FROM.
3. The connection binding itself is intact: recipe_get shows the step bound to account 22117414 on the runtime connector; the platform does not report a broken/lost connection (no 401, no re-auth prompt) — it reports the ABSENCE of an end-user identity, which is exactly the headless-test condition. The revert trap would manifest as the connection reverting to a shared/app connection (identity present but wrong), not "Missing connection".
4. Prior autopsy (1011) established no recipe edits between the seismic pair's 2026-10-01 green runs and their failures — the only variable that changed was execution context (nightly headless runner, onboarded to the registry 2026-10-10, commit 2bc6260).

Classification: recurrence of the known canon signature `vua-skill-headless-test-identity-absent` (filed 2026-10-11). Not a new class; not the push-reverts-VUA trap.

## (d) Minimal fix proposal + the test that would have caught it

This is a harness/registry defect, not a recipe defect — no recipe edit is the correct fix.

1. **Registry fix (minimal, already proposed on triage card regression-seismic-pair-vua-probe-1011)**: remove 82272814 from the nightly registry (stopped diagnostic probe, 0/3 lifetime, unsatisfiable headless by construction) or reclassify its test case as manual-only. Interim general fix: tag-and-skip list in scripts/regression-nightly.py for VUA-bound skills; proper fix: a headless-context capability flag so VUA skills only run in a context carrying an end-user identity.
2. **The test that would have caught it**: a registry-onboarding gate, not a recipe test — when regression-nightly.py onboards a recipe, classify it (connection account bound to a `*_runtime_connector` / VUA-required Workato Skill) and refuse or mark manual-only. A single fixture asserting "headless run of a VUA-bound skill MUST fail with Missing connection" would also work as a sentinel proving the harness still detects the class, but the probe's own nightly FAIL was never signal — it is the expected output of an unsatisfiable test.
3. If a genuine VUA-revert regression guard is wanted for identity-sensitive skills (the 82272814 class of concern): the existing standing rule already covers it — post-push read-back of the connection mode (mcp_server_get / recipe UI, "VUA Required: Yes"). Tonight's failure does NOT indicate that guard is needed here; nothing was pushed.

## Not verified

- The 3 could-not-start recipes (82239660, 82727069, 82959480) and fixture fails 82863111/82959481 were not investigated here (out of scope; separate signatures per the morning brief).
- Connection 22117414's authorization status was not independently re-read via a connections-list call; the job trace's "Missing connection" (not a 401/exception) plus intact recipe binding is the evidence relied on.
- No write action taken; triage card regression-seismic-pair-vua-probe-1011 remains the remediation vehicle.

Sources: job_get j-AbtmpY6g-d3ccQH-CD / j-Abtmo4kR-QcHAsw-CD / j-AbtmozEz-tDX3Np-CD; job_list 82248514 + 82256903; recipe_get 82272814; morning-brief/2026-10-12.md REGRESSION; regression-canon/canon.jsonl:45; cortex bus (seismic-vua-trio-verdict 2026-10-11T08:45:41, attention-queue rev k/l); investigations/seismic-vua-probe-regression-1011.md; investigations/hr-genie-auth-cluster.md (unrelated 401 missing_privilege cluster — different class: key-scope, not VUA-identity-absent).
