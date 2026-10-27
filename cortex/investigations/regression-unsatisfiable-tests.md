# Census: unsatisfiable-by-construction tests in the nightly regression registry

**Date**: 2026-10-12 · **Mode**: READ-ONLY census (no runs started, no recipe edits, no deletes, dev CLI reads only) · **Trigger**: 82272814 was proven an unsatisfiable headless test (investigations/82272814-vua-probe-regression.md) — question: how many more exist?
**Sources**: `scripts/regression-nightly.py` + `garden-reports/regression-registry.json` (14 enrolled), nightly reports 2026-10-10/11/12, live `wt api GET /api/recipes/<id>.json` and `wt testcases cases` reads 2026-10-12, autopsies 82272814-vua-probe-regression.md + seismic-vua-probe-regression-1011.md + regression-start-failures-2026-10-09.md.

## Verdict (one line)

82272814 is not alone: of 14 enrolled recipes, 6 are permanent false-alarm producers — 3 fail every nightly run (VUA-identity-dependent skill tests, 82272814 + 82248514 + 82256903) and 3 error every nightly run (unconfigured empty-shell test cases, 82239660 + 82727069 + 82959480) — plus 2 fixture-phase permanent failures (82863111, 82959481); every other enrolled recipe passes and is legitimately satisfiable.

## Enrolled-recipe table (live state 2026-10-12, dev ws 3535597)

| Recipe | Trigger | Running (live) | Last 3 nightlies | Classification |
|---|---|---|---|---|
| [82272814](https://app.workato.com/recipes/82272814) workspace_vua_identity_probe | workato_skill | False (stopped diagnostic) | 0/1 FAIL ×3 | **UNSATISFIABLE — stopped diagnostic + VUA-runtime GW connector 1789196780**; headless runner carries no end-user identity ("Missing connection", 0/3 lifetime) |
| [82248514](https://app.workato.com/recipes/82248514) Seismic Search authorized content catalog | workato_skill | True | 0/1 FAIL ×3 | **UNSATISFIABLE — test case exercises get_runtime_actor_scope on VUA Seismic connector 1789094460**; headless 404 RESOURCE_NOT_FOUND (same canon signature vua-skill-headless-test-identity-absent) |
| [82256903](https://app.workato.com/recipes/82256903) Seismic List Intelligence recommenders | workato_skill | True | 0/1 FAIL ×3 | **UNSATISFIABLE — test case exercises list_intelligence_recommenders on the same VUA connector**; headless "Missing connection" (identity absent at platform layer) |
| [82239660](https://app.workato.com/recipes/82239660) POC \| HR Genie Runtime Connection Hygiene Audit | clock | True | ERROR ×3 | **UNSATISFIABLE (probable) — single unconfigured empty-shell case** (citc-AboAHG4Q, "Untitled test case 1", no fixture/assertion); run-request POST cannot start; error body discarded by runner |
| [82727069](https://app.workato.com/recipes/82727069) run_genie_evals | workato_skill | False (stopped, 0 jobs ever) | ERROR ×3 | **UNSATISFIABLE (probable) — single unconfigured empty-shell case** (citc-AbsBKJxC); note: stopped alone is NOT the discriminator (82252949 is stopped and passes) |
| [82959480](https://app.workato.com/recipes/82959480) create_prospect | workato_skill | True | ERROR ×2 (onboarded 10-10) | **UNSATISFIABLE (probable) — single unconfigured empty-shell case** (citc-AbsoNY6e); same signature as the two above |
| [82272066](https://app.workato.com/recipes/82272066) workspace_capabilities | workato_skill | True | 2/2 PASS ×3 | satisfiable |
| [82256904](https://app.workato.com/recipes/82256904) Seismic Recommend next-best content | workato_skill | True | 1/1 PASS ×3 | satisfiable (same connector, identity-independent action path) |
| [82256590](https://app.workato.com/recipes/82256590) Seismic Add authorized content to meeting | workato_skill | True | 1/1 PASS ×3 | satisfiable (same) |
| [82255843](https://app.workato.com/recipes/82255843) Seismic Create a LiveSend | workato_skill | True | 3/3 PASS ×3 | satisfiable (same) |
| [82252165](https://app.workato.com/recipes/82252165) Seismic Save authorized content to my Workspace | workato_skill | True | 2/2 PASS ×3 | satisfiable (same) |
| [82252949](https://app.workato.com/recipes/82252949) zArchive Publish HR Notification Event | recipe_function | False (stopped) | 1/1 PASS ×3 | satisfiable — proves "stopped" alone is not unsatisfiable |
| [82855731](https://app.workato.com/recipes/82855731) audit_conversation_case_file | recipe_function | True | 1/1 PASS ×3 | satisfiable |
| [82862205](https://app.workato.com/recipes/82862205) REC \| HR Genie \| Conversation Event Collector | clock | False | FAIL 10-10/11 → PASS 10-12 | satisfiable — real regression, fixed (BSYS-29455), keep enrolled |

## Fixture-phase permanent false alarms (bonus class, same disease)

- `fixtures/82863111.json` — FAIL ×2 (10-11, 10-12): response lacks `job` key the expect path asserts (`path 'job.status': missing key 'job'`). Fixture asserts a response shape the recipe doesn't produce; can never pass as written.
- `fixtures/82959481.json` — FAIL(timeout) ×2, `job ?`: fixture invokes recipe 82959481 and polls to timeout with no job id returned — invoke never lands.
- 6 other fixtures are unfilled scaffolds (no expects) and are correctly SKIPped, not counted.

## Discriminator, stated generally

A test is unsatisfiable-by-construction when its success depends on something a headless Test-Automation-API run cannot have, by construction:
1. **VUA end-user identity** — the recipe's tested action path resolves actor identity via a `*_runtime_connector` / VUA-required skill connection (82272814, 82248514, 82256903). Recipe running-state is irrelevant; two of the three are running and still fail.
2. **Stopped diagnostic recipes enrolled as regression targets** — a probe kept stopped deliberately (82272814) has no green baseline and no right to be in the nightly run set.
3. **Empty-shell test cases** — an "Untitled test case 1" with no fixture/assertion (82239660, 82727069, 82959480); the run request cannot start and the runner discards the rejection body, so the report shows only "could not start run" forever.

What does NOT discriminate: stopped vs running (82252949 stopped+passes; 82239660/82959480 running+error), trigger type (skill recipes both pass and fail), connector presence (all six Seismic recipes share connector 1789094460; only the two whose tested actions consume actor identity fail).

## Minimal registry-hygiene fix (proposed, NOT applied — read-only census)

1. **Drop or manual-only 82272814** from `garden-reports/regression-registry.json` (already proposed on triage card regression-seismic-pair-vua-probe-1011).
2. **Mark 82248514 + 82256903 manual-only** — their test cases depend on VUA identity; keep the recipes, skip their cases headless. Implement as a tag-and-skip list in `regression-nightly.py` (interim) or an onboarding-time classification gate (proper): when the runner first enrolls a recipe, classify it (VUA-runtime connection binding / empty-shell case) and enroll as manual-only instead of failing nightly.
3. **Delete or re-author the three empty-shell cases** (citc-AboAHG4Q on 82239660, citc-AbsBKJxC on 82727069, citc-AbsoNY6e on 82959480) — the same disposition Josh's accepted 2026-10-08 triage verdict gave 82273581's identical shell.
4. **Report the rejection body**: `run_recipe_cases()` already captures `detail` but `main()` drops it — print it so future "could not start run" errors are self-diagnosing.
5. **Fixtures**: fix 82863111.json's expect path to the real response shape; 82959481.json needs a valid invoke (or both move to manual-only). Recurring-failure circuit breaker: a recipe/fixture failing N consecutive nights with an identical error signature auto-demotes to manual-only pending triage, so permanent false alarms stop consuming nightly attention.
6. **Canon hygiene**: close the auto-seeded open canon entries for the classified-unsatisfiable set once the registry fix lands, so the canon reflects "expected failure, suppressed" rather than open regressions.

## What was NOT verified

- The exact Test-Automation rejection body for the three "could not start run" recipes (runner discards `detail`; replaying the POST is a write — prohibited by this census's read-only scope). "Empty-shell case" is the strongest surviving hypothesis from the 10-09 investigation, applied here as probable, not proven.
- The VUA-required MCP-server-side flag for the Seismic connector was not independently re-read (classification rests on the 10-11/10-12 job-trace autopsies, which are cited above).
- 82272814's connection account 22117414 authorization status was not re-read; prior autopsy evidence relied on.
- No write action of any kind was taken: registry unchanged, no recipes touched, no runs started, no fixtures edited, no Slack.

---

## FIX APPLIED (2026-10-20, Josh-approved verdicts — executed dev-side, live-verified)

**Task 1 — the 6 permanent false-alarm producers:**
- **3 empty-shell test cases DELETED via Orca UI (tag-and-trusted-click; Test Automation API is RUN-only, no delete verb — both REST delete routes 404'd):** citc-AboAHG4Q-dnsQBe-CD on 82239660, citc-AbsBKJxC-JYEz48-CD on 82727069, citc-AbsoNY6e-TcLtdJ-CD on 82959480. Each API-verified via `wt testcases cases` → zero cases. Registry rows removed from `garden-reports/regression-registry.json`; nightly scan now finds no live cases, so nothing runs or counts.
- **3 VUA-identity recipes TAG-AND-SKIPPED, not silently removed (Josh task-2 verdict):** 82272814, 82248514, 82256903 stay enrolled; each registry row carries a `note` field with the reason + re-entry path, and `garden-reports/regression-skip.json` carries the same reason + graduation condition (identity-carrying harness run, or tested path re-authored headless-safe and passing stably — then remove the skip entry to re-enroll). The runner masks them (no FAIL lines, no canon auto-seed). 82272814's note also records the stopped-diagnostic/no-green-baseline fact.

**Harness patch:** `scripts/regression-nightly.py` scan-refresh now merges (`{**old, 'name':…, 'cases':…}`) instead of rebuilding registry rows — the bare rebuild would have wiped the new `note` fields on the very next nightly.

**Fixture-failing items — verdicts kept on record (not fixed this pass, per task):**
- `fixtures/82863111.json` — FAIL ×2 (10-11, 10-12): expect path asserts `job.status` but the response lacks the `job` key; fixture asserts a shape the recipe doesn't produce, can never pass as written. Fix = re-point the expect path at the real response shape.
- `fixtures/82959481.json` — FAIL(timeout) ×2: invokes recipe 82959481 and polls to timeout with no job id returned; the invoke never lands. Fix = a valid invoke, or manual-only.

**Verified live 2026-10-20:** registry read-back 17 rows (3 removed, 3 noted); skip read-back 4 entries with reasons; runner gating simulation shows only MASKED lines for the identity class and no run path for the removed trio; script `py_compile` clean; merge-patch preserves notes on simulated refresh. Note: masked entries still add to the report's error total by design (dependency-unavailable envelope, not a green — 2026-10-16 policy).

**Not done (out of scope, still open):** the two fixture fixes above; census recommendation 4 (render `detail` on start-ERRORs); recommendation 6 (close the auto-seeded open canon entries for this classified set).
