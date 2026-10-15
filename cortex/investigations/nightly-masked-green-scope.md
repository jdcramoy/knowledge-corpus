# Investigation: nightly masked-green blast radius (2026-10-11)

**Mode**: READ-ONLY sweep (no tests executed, nothing modified). Evidence base: `cortex/investigations/seismic-vua-probe-regression-1011.md` (proved connection acct 22111194 dead while sibling 82256904 reported green via DEPENDENCY_UNAVAILABLE fallback envelope, trace j-AbtGmke4-rYM8Kp-CD).
**Staging note**: intended destination `~/.claude/knowledge/cortex/investigations/nightly-masked-green-scope.md` was permission-blocked for ALL write mechanisms (echo >, cat >>, touch, tee), as was garden-reports/ — the whole knowledge tree is write-gated in this session. Filed here; move with `mv` once approved.
**Method**: registry from `garden-reports/regression-registry.json` (14 recipes, matches regression-nightly.py's live re-verify scan); per-recipe classification from read-only `recipe_get` DSL; live confirmation from `regression-latest.md` (2026-10-11 run) and read-only job traces.

## The mask mechanism (generalized — not VUA-specific)

The hole is: **a monitor/catch block that returns a structured envelope (ok:false / DEPENDENCY_UNAVAILABLE / failed idempotencyStatus) instead of re-raising, combined with a test case that asserts the envelope shape rather than the success path.** The job then `succeeds`, the case counts green, and a dead dependency is invisible. VUA-runtime custom connectors (`*_runtime_connector_*`, `seismic_by_workato_connector_*`) are the worst instance because their connections are caller-scoped and provably dead in headless test jobs — but ANY connector behind a catch-to-envelope gets the same mask.

Secondary mask found at job-trace level: **ledger short-circuit**. 82252165's nightly job (j-AbtGkoLf-Rpopk9-CD) exited at step 12 via the replay/in-flight ledger path — the live Seismic mutation was never called at all, yet the case passed.

## Per-recipe findings (all 14 registry entries)

1. **82855731 audit_conversation_case_file** — No VUA connector (recipe function + Ruby + data tables). Green 1/1 is genuine headless (table reads + code work without caller identity). Risk: none from this hole.
2. **82727069 run_genie_evals** — No VUA connector (Genie connector, data tables, JS). Nightly: ERROR "could not start run" (recipe stopped) — honest red, not masked.
3. **82272814 workspace_vua_identity_probe** — VUA-runtime connector (gw `..._runtime_connector_..._1789196780`), first call at step 2, UNCONTAINED. Fails openly every night (0/3 lifetime; recipe stopped). Honest red, zero green signal. Low mask risk; should be dropped from the registry per the 10-11 autopsy.
4. **82272066 workspace_capabilities** — No VUA connector anywhere (skill + data tables only; pure catalog reader). Green 2/2 genuine. Caveat: the test never exercises the VUA runtime execution path at all — the registry has no coverage of the actual `google_workspace` execution skill.
5. **82256904 Seismic | Recommend next-best content** — VUA connector step 3, CONTAINED (monitor step 2 → DEPENDENCY_UNAVAILABLE envelope). **PROVEN masked-green** (10-11 autopsy trace). HIGH.
6. **82256903 Seismic | List Intelligence recommenders** — VUA connector step 2, UNCONTAINED. Honest red nightly; real defect is the missing containment its description promises. Low mask risk (currently), but the moment the fallback monitor is added per follow-up #3 it becomes a masked-green.
7. **82256590 Seismic | Add authorized content to meeting** — VUA connector steps 3 + 18, CONTAINED (monitors at 2 and 16). Trace of nightly green job j-AbtGmNCG-txdF9z-CD: prepare succeeded locally, then the ledger `add_record` failed (`required field not set: 'tenant_key'`), catch fired, job returned the failed envelope and **succeeded** → 1/1 green while the mutation path errored. HIGH.
8. **82255843 Seismic | Create a LiveSend** — VUA connector steps 3 + 18, CONTAINED (monitors 2 and 16 → canonical failed envelope). 3/3 green in the same window the shared connection 22111194 is proven dead. HIGH.
9. **82252949 zArchive | Publish HR Notification Event** — No VUA connector (Event Streams pub/sub). Green genuine headless. (Stopped/archived recipe, but green honestly.)
10. **82252165 Seismic | Save authorized content to my Workspace** — VUA connector steps 6 + 18. First call (step 6 `prepare_mutation_context`) is UNCONTAINED but is a local connector action (succeeds headless, 0.016s in trace). The live mutation (step 18) is CONTAINED by monitor 16. Nightly green via **ledger short-circuit** (job j-AbtGkoLf-Rpopk9-CD exited at the replay/in-flight return; the save was never attempted). HIGH.
11. **82248514 Seismic | Search authorized content catalog** — VUA connector step 2 (`get_runtime_actor_scope`) OUTSIDE the monitor that begins at step 6. Honest red (404 actor-scope). Low mask risk; latent gap already flagged in the 10-11 autopsy.
12. **82239660 POC | HR Genie Runtime Connection Hygiene Audit** — No VUA connector (Workato API platform connector `workato_api_connector_748504`, account 13685697 — token auth, not caller-scoped). Nightly: ERROR could not start run. Low.
13. **82862205 REC | HR Genie | Conversation Event Collector** — No VUA connector (same platform API connector). Honest red on a real assertion failure (guard-empty-conversation-batch). Low.
14. **82959480 create_prospect** — Not VUA-runtime, but SAME structural shape: Outreach custom connector behind monitor step 2 with classify-catch → error envelope. If the shared Outreach service connection dies, tests would go green on the error envelope. MEDIUM (structurally vulnerable; shared service identity is currently stable). Nightly: ERROR could not start run.

## Verdict table

| Recipe ID | Name | VUA-runtime connector in first 2 steps | Contained (catch -> fallback envelope) | Masked-green risk | Nightly status |
|---|---|---|---|---|---|
| 82855731 | audit_conversation_case_file | no | n/a | low | green (genuine) |
| 82727069 | run_genie_evals | no | n/a | low | ERROR (stopped) |
| 82272814 | workspace_vua_identity_probe | **yes** (step 2) | no | low (honest red) | FAIL 0/1 |
| 82272066 | workspace_capabilities | no | n/a | low | green (genuine; no VUA coverage) |
| 82256904 | Seismic Recommend next-best | **yes** (step 3) | **yes** | **HIGH — proven masked** | green 1/1 (masked) |
| 82256903 | Seismic List recommenders | **yes** (step 2) | no | low (honest red) | FAIL 0/1 |
| 82256590 | Seismic Add content to meeting | **yes** (steps 3, 18) | **yes** | **HIGH** | green 1/1 (masked) |
| 82255843 | Seismic Create a LiveSend | **yes** (steps 3, 18) | **yes** | **HIGH** | green 3/3 (masked) |
| 82252949 | zArchive Publish HR Notification | no | n/a | low | green (genuine) |
| 82252165 | Seismic Save to Workspace | **yes** (steps 6, 18) | partial (mutation only) + ledger short-circuit | **HIGH** | green 2/2 (masked) |
| 82248514 | Seismic Search catalog | **yes** (step 2) | no (monitor starts step 6) | low (honest red) | FAIL 0/1 |
| 82239660 | POC HR Genie Hygiene Audit | no | n/a | low | ERROR |
| 82862205 | REC Conversation Event Collector | no | n/a | low | FAIL (real defect, honest) |
| 82959480 | create_prospect | no (Outreach custom) | yes (same shape) | medium | ERROR |

**Totals: 7/14 recipes run a VUA-runtime connector in their first 2 steps; 4 of those 7 (82256904, 82256590, 82255843, 82252165 — 7 of the 11 green case-passes) are masked-green. 3 of 7 VUA recipes fail honestly.**

## How many nightly greens are trustworthy — one-line verdict

**Of 11 green case-passes, 4 recipes / 7 cases (all four Seismic VUA skills) are NOT trustworthy — every green on a VUA-runtime skill is a fallback-envelope or ledger-replay green; only the 3 non-VUA greens (82272066, 82252949, 82855731) reflect real dependency health, so the nightly's green count overstates true health by ~2/3 on the skills it was added to cover.**

## Recommended follow-ups (for Josh; nothing executed)

1. Tag-and-skip VUA-bound skills in regression-nightly.py (interim, per 10-11 autopsy), OR make the harness parse the returned envelope: a case whose result carries `ok:false` / `sourceMode:unavailable` / `idempotencyStatus:failed` must count as masked-FAIL, not pass.
2. Add a connection-health precheck to the harness: for each registered recipe, resolve its custom-connector accounts and verify authorization status before crediting a green.
3. Fix test assertions on the four HIGH recipes so cases assert the success envelope (ok:true + real counts), which converts a dead connection back into an honest red.
4. 82252165: clear or rotate the test fixture's request_id so cases exercise the live path instead of short-circuiting on the ledger replay.
5. Generalize the canon signature: `monitor-catch-envelope-masks-dependency-failure` (applies to 82959480 too), distinct from but linked to `vua-skill-headless-test-identity-absent`.
