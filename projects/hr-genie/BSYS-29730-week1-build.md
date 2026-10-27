# BSYS-29730 — Week-1 build record (2026-10-23)

Epic: https://workato.atlassian.net/browse/BSYS-29730 · Plan: `BSYS-29730-perf-review-cycle-plan.md` · Spikes: `BSYS-29730-day1-spikes.md`
Week-1 progress comment: Jira comment 1147183 on BSYS-29730. All assets in dev ws 3535597, folder `Perf Review Cycle` 35943947 — https://app.workato.com/recipes?fid=35943947

## Built (all verified running)

- `TBL | Perf Cycle | Review Shared Watermark` 164249 / b969ea29-5747-4353-bb96-25bb18ad1388 — inclusive-watermark guard columns (BSYS-29477 pattern), 6 cols — https://app.workato.com/data_tables/b969ea29-5747-4353-bb96-25bb18ad1388
- `TBL | Perf Cycle | Quality Gate Verdicts` 164250 / 2fa74c00-0919-4656-af62-52499cea23f6 — draft_hash, verdict, rubric_scores, nudge_sent, manager_flag_sent, detection_path (Spike A: genie_resubmit | compare_content), 10 cols — https://app.workato.com/data_tables/2fa74c00-0919-4656-af62-52499cea23f6
- `FUNC | Workday Nominee Enrichment` 83296106 — recipe function; WQL allWorkers by name (`contains` on display-format text fields); returns worker id (WID extracted from hash), title, level, continuous-service date, sup org, people partner — https://app.workato.com/recipes/83296106
- `FUNC | Nomination Eligibility Guard` 83296142 — recipe function; three branches: A direct reports (WQL `managementChain_Level01 IN (wid)`, count carried via declare/update variable, default 0), B nominator WID in nominee's chain string (levels 1-8 concat include?), C people-partner descriptor contains nominator legal name; returns status/eligible/branch/reason — https://app.workato.com/recipes/83296142
- `SKILL | Perf Cycle | Nomination Intake` 83296269, handle `skl-Ac6XfaLE-4WEMRH-CD`, attached to HR Genie gin-AYbxpMha-YenKAJ-CD (skills_count 5) — workato_skill trigger; flow: enrich → guard → (not-found early return) → tenure months variable → Workato AI chat_completion pre-eval judge → dedup search on Nomination Log → update (resubmit) / insert (first) → EM | AI Action Log row (mask_data) → return result — https://app.workato.com/recipes/83296269
- Manifest 370603 "BSYS-29730 HR Genie Perf Review Cycle", 10 rows (3 tables + 2 FUNC recipes + agentic_skill 351149 + backing recipe 83296269 + EM | AI Action Log 161960 + connections 19760013/18367190); mirror `~/Documents/workbench/manifests/bsys-29730-hr-genie-perf-review-cycle.manifest.json`
- TEST twins (manifest-exempt): probe 83290934 (spikes + function verify, webhooks suffix `bsys29730-spike`), intake twin 83296279 (webhook twin of the skill, suffix `bsys29730-intake-twin`)

## Verified (live job traces)

- Enrichment: caller job j-Ac6XTEAF-x9Aboa-CD → function job j-Ac6XTFM4-6W6JDw-CD — real IMPL row (Aaron Navarro, Engineering Manager, 2018-06-18 service date, partner [requester] Au Yong, 9 name matches).
- Guard case not-found: function job j-Ac6XbLa4-xeWssK-CD — status nominator_not_found, eligible false, branch none, direct_report_rows 0 (nil-safe path, no WQL crash).
- Guard case no-branch: function job j-Ac6XeHod-4Gx6eb-CD — status ok, nominator_rows 1, eligible false, branch none.
- Guard case management-chain positive: function job j-Ac6Xf8HP-8poxCX-CD — eligible TRUE, branch management_chain (Yogesh Padmanabhan nominating Aaron Navarro).
- Intake e2e run 1 (insert): twin job j-Ac6Xp9Ln-rWTte9-CD — row 0d482049-647e-4de1-8a15-f8d97076f5be landed with policy_flags `{"tenure_months": 100, "tenure_flag_12_24m": false, "rating_vs_exceeds": "pending_leapsome"}`.
- Intake e2e run 2 (idempotency): twin job j-Ac6XpzTW-LXTNFC-CD — IDENTICAL payload, still exactly 1 row, same record id (update path taken).
- EM | AI Action Log 161960: 2 rows (one per intake run), action nomination_ai_preeval, evidence carries the judge verdict.
- All five recipes RUNNING (probe, twin, enrichment, guard, skill) — never left stopped.

## WQL / platform laws learned (2026-10-23)

- WQL `=` on instance-typed fields (preferredName, worker, managementChain_Level01) errors "cannot resolve instance <value>"; instance fields filter with `IN (wid)`. Text `=` only on text fields (email_PrimaryWork works). Name search = `contains` on `preferredNameInGeneralDisplayFormat` / `legalNameInGeneralDisplayFormat`.
- WQL `IN (<nonexistent-wid>)` also errors — cannot sentinel; guard with an if around the query (nominator resolved?) instead.
- ruby() restricted subset: regex-with-capture `v[/re/, 1]` passes VALIDATION but fails at RUNTIME "wrong number of arguments (given 2, expected 1)" — do not use; WQL hash cells arrive as real Ruby hashes (`bindings.v['id']` works; `.split` on them fails "no method 'split'").
- declare_variable: fields are `name`, `type`, then `value` appears only after name+type set (two calls). update_variables: `name` takes the field UUID alias, value maps under the variable NAME path.
- `workato_skill` trigger recipes cannot be invoked via any REST surface found (agentic skill run/invoke/test/execute = 404; force-run = scheduler-only; test-case creation = web_api 404 headlessly) — end-to-end test via a webhook TWIN (copy recipe, swap trigger to workato_webhooks, re-point `start_workflow_1['parameters']` → `new_event_1['payload']`).
- Manifest export bundler resolves connection deps from the RECIPE's live config and CANNOT bundle a cross-project connection (error: "Connection Home/... is not found under Home/<source folder>"); row path rewrites are ignored. Judge step should move to a project-local Workato AI connection at promotion prep.
- IMPL tenant demo emails: pattern `<first>.<last>@workato.com` (e.g. joshua.navarro@workato.com, yogesh.padmanabhan@workato.com).

## Not verified / open

- Branch C (people partner) positively fired in IMPL — logic same include? shape as proven branch B; demo partner data did not produce a positive case.
- The real SKILL trigger (83296269) end-to-end via HR Genie conversation — tested via the webhook twin instead; genie-conversation run is a week-2 UAT item.
- Two-ordering (watermark guard) live test — lands with the R4 detector build per plan phasing.
- Sheet sync — gated on open item E; rows carry sheet_sync_state=pending.
- Judge strict-JSON output — prose today; response_format json_object to pin in the R3 fusion build.
- Red-team verdict — pending, at promotion (never self-run).
- Manifest ZIP verify — blocked on the cross-project connection (see law above); row-level read-back verified in-page 2026-10-23.
