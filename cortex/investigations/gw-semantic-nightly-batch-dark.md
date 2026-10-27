# gw_semantic nightly batch "dark" — investigation (2026-10-15, cortex, read-only)

## Verdict

**The batch is NOT dark. The "3+ missed nights" evidence is a false alarm: the reported
"last_run 2026-10-11T05:46-06:17Z" timestamps are the recipes' LAST-EDITED (`updated_at`)
values, not job activity.** Live job traces show every sampled scheduler recipe in dev folder
35404884 ([MCP] Google Workspace Semantic MCP/Automation, project 17981834) running on cadence
through 2026-10-14 (~23:2x PT). One REAL defect confirmed: canary 82964017 was auto-stopped
AGAIN with `stop_cause=trigger_errors_limit` — the BSYS-29560 malformed-trigger cycle,
recurrence after the BSYS-29656 fix.

## The timestamp fingerprint (why the evidence was stale)

The evidence window "2026-10-11T05:46-06:17Z" converts to 01:46-02:17 EDT 2026-10-11 — an exact
match to the AIRO `Last updated` (recipe EDIT time) column for precisely the named recipes:

| Recipe | AIRO "Last updated" (EDT) | = UTC |
| --- | --- | --- |
| 82963931 nightly_conformance | 2026-10-11T01:46:25 | 05:46Z |
| 82963934 candidate_triage | 2026-10-11T02:03:08 | 06:03Z |
| 82964024 error_hint_author | 2026-10-11T02:07:22 | 06:07Z |
| 82964058 paraphrase_cluster | 2026-10-11T02:17:52 | 06:17Z |

Digests/rollups show the same 10-11 01:3x-02:3x edit cluster. Whoever/whatever produced the
"last_run" evidence read recipe metadata `updated_at` (or a lagging replica of it), not job
history. Weekly-cadence recipes (paraphrase cluster, error-hint, Monday digest) would ALSO be
legitimately quiet since Sunday 10-11 — a second way the same misread goes undetected.

## Live job traces (all PT, fetched 2026-10-15 via AIRO job_list)

| Recipe | Cadence | Latest job | Result |
| --- | --- | --- | --- |
| 82963934 candidate_triage (https://app.workato.com/recipes/82963934) | daily 06:00 | 2026-10-14 06:00 (j-Abx3obde-EWk9F8-CD) | succeeded; 6/6 green |
| 82963931 nightly_conformance (https://app.workato.com/recipes/82963931) | daily 07:13 | 2026-10-14 07:13 (j-Abx4zts8-AJcWxd-CD) | succeeded; 6/6 green |
| 82889357 usage_metrics_rollup_v2 (https://app.workato.com/recipes/82889357) | hourly | 2026-10-14 22:42 (j-AbxMrwmc-Wz9GDG-CD) | succeeded; 183/183 green |
| 82964024 error_hint_author (https://app.workato.com/recipes/82964024) | weekly+ | 2026-10-14 00:23 (j-AbwsQPDL-bRaYJW-CD) | succeeded; 3/3 green |
| 82964058 paraphrase_cluster (https://app.workato.com/recipes/82964058) | weekly+ | 2026-10-14 00:20 (j-AbwsNeGL-LsCXdm-CD) | succeeded; 6/6 green |
| 82803096 usage_digest (https://app.workato.com/recipes/82803096) | daily 14:00 | 2026-10-14 14:00 (j-AbxDWe9f-dFfbFP-CD) | succeeded (posts to Slack channel) |
| 82862814 canary_sweep_and_promote (https://app.workato.com/recipes/82862814) | 2h | 2026-10-14 23:10 (j-AbxNKXMb-g3xcdX-CD) | succeeded — BSYS-29656 fix holding |
| 82795586 watchdog (https://app.workato.com/recipes/82795586) | 15 min | 2026-10-14 23:23 (j-AbxNXK8X-Qfm6nG-CD) | succeeded; 919/920 green |
| 82951201 fleet_liveness_sentinel (https://app.workato.com/recipes/82951201) | hourly | 2026-10-14 22:54 (j-AbxN6w6P-XxnQe8-CD) | succeeded; detection layer alive |

## The one real finding: canary 82964017 auto-stopped again

- https://app.workato.com/recipes/82964017 — `running=false`, last job 2026-10-14 00:45:45 PT
  (j-AbwsnCR9-JbGgaJ-CD) SUCCEEDED. **Lifetime 14 jobs, 14 succeeded, 0 failed** — no job-level
  failure exists; the silence is at trigger level.
- **stop_cause confirmed via API filter:** `recipe_list(stop_cause="trigger_errors_limit")` over
  folder 35404884 returns EXACTLY ONE recipe — 82964017. Same silent-death class as the
  BSYS-29560 cycle and the 2026-10-07 responder lineage.
- Post-fix timeline: BSYS-29656 restart+force-run green 2026-10-13 19:33 PT → two more green
  runs 00:20 / 00:45 PT Oct 14 → dead before the next hourly tick. Survived <6h after the fix.
- Corroborating signal in the current recipe definition: AIRO read shows **14
  DatapillInvalidPath inconsistencies** (steps 26-32) — pills referencing `compiler_status`,
  `execution_binding_json`, `plan_hash`, `result_json` etc. "don't exist in output schema" of
  the gateway runtime connector actions (`compile_reviewed_operation_abe5`,
  `prepare_confirmable_mutation_15ed`, `commit_confirmed_mutation_0071`). That is connector
  output-schema drift on `google_workspace_semantic_gateway_runtime_connector_3535597_1789196780`
  (connection 22117414) AFTER the last green run — a recipe that fails start-time validation or
  trigger initialization loops into `trigger_errors_limit` without ever creating a failed job.

## Shared connections: healthy

- slack_bot 22250688 (GW Semantic Alerts bot): daily digest 82803096 posted green 2026-10-14
  14:00 PT; canary's own alert path green through its last run.
- gateway runtime connector 22117414: exercised green by canary_sweep_and_promote as recently
  as 2026-10-14 23:10 PT (130 jobs, 115 succeeded, recent all green) and by the canary itself
  at 00:45 PT. The CONNECTION works; the canary's pinned SCHEMA is stale.

## BSYS-29656: no deliberate pause

https://workato.atlassian.net/browse/BSYS-29656 ("Flywheel stall", status Backlog) documents
the Oct 13 stall + fixes, commented FIXED + VERIFIED 2026-10-14T02:39Z with manifest 363068 on
record (sweep v20, canary v12, watchdog v6). It covers the sweep, the canary, and watchdog
alert-suppression ONLY — nothing in it pauses or even touches the nightly batch recipes
(conformance, triage, paraphrase, error-hint, digests, rollups). No deliberate pause exists.

## Recommended next steps (NOT executed — read-only investigation)

1. Restart + force-fire 82964017 per the BSYS-29656 playbook is a dev write — delegated
   stop/start authority exists but THIS dispatch was read-only, so it is left for Josh or a
   writable follow-up session.
2. Root-cause the recurrence instead of just restarting: diff the gateway runtime connector's
   released output schema against what the canary pinned at v12 (something changed after
   2026-10-14 00:45 PT); re-bind pills or pin the connector version, else the
   restart → trigger_errors_limit loop recurs a third time.
3. Fix the evidence pipeline: whatever sweep reported "last_run 2026-10-11T05:46-06:17Z" is
   reading `updated_at` (or a stale replica) as run activity. Point it at job traces
   (job_list / last succeeded job) — the fleet liveness sentinel already does this correctly
   and did NOT report the batch dark.

## Not verified / limitations

- dependency-tracker MCP tools (search_recipe_dependencies, list_connections) were
  permission-blocked in this headless session — could not confirm its store is the stale
  evidence source (hypothesis only) nor read stop_cause from it; stop_cause was instead
  established by the AIRO stop_cause filter matching exactly this recipe.
- Exact trigger-error text and the stop timestamp are not exposed via AIRO read tools.
- What changed the gateway runtime connector schema after 00:45 PT Oct 14 (release? cache?) was
  not established — no connector-release read used.
- Nothing was stopped, started, edited, or written in Workato. Read-only held throughout.
# AUTOPSY: gw_semantic nightly batch dark since 2026-10-11 rebuild wave
# Date: 2026-10-15 | Investigator: cortex probe (read-only) | DEV folder 35404884
# Scope: 9 clock-triggered recipes running=true, last_run_at frozen 10-11T05:46-06:17Z


---

## CONFIRMATION PROBE — second pass, 2026-10-15 ~18:0x PT (fresh live evidence)

The 3-line header block directly above is this probe's file-initialization artifact; this
section is the probe's actual content. It re-pulled ALL 9 named recipes live (AIRO job_list,
recipe_get) and CONFIRMS the first-pass verdict: the batch is alive, every one of the 9 fired
after the 2026-10-11 rebuild wave, and 8 of 9 fired TODAY (10-15).

| Recipe | Cadence (from trigger config / job spacing) | Latest job (PT) | Result |
| --- | --- | --- | --- |
| 82963931 nightly_conformance | daily 07:13 | 2026-10-15 07:13 (j-Abxa6E4g-YcWsRg-CD) | succeeded; also 10-12, 10-13, 10-14 |
| 82963934 candidate_triage | daily 06:00 PT | 2026-10-15 06:00 (j-AbxXrrwr-WDBJMx-CD) | succeeded; also 10-12, 10-13, 10-14 |
| 82964058 paraphrase_cluster | ~nightly 00:2x | 2026-10-15 00:25 (j-AbxPXEKw-pnazGo-CD) | succeeded; also 10-12, 10-14 |
| 82964024 error_hint_author | ~nightly 00:2x | 2026-10-15 00:25 (j-AbxPWxpc-hEkxwA-CD) | succeeded; also 10-12, 10-14 |
| 82893591 responder_stall_watch | hourly | 2026-10-15 17:53 (j-AbxnJWkG-FxLGFe-CD) | succeeded; 198/198 green lifetime |
| 82803096 usage_digest | daily 14:00 PT | 2026-10-15 14:00 (j-AbxgYwFB-CmaeDc-CD) | succeeded (17 ok / 4 failed lifetime, recent all green) |
| 82888690 weekly_intelligence_digest | WEEKLY Monday 08:00 PT | 2026-10-12 08:00 (j-Abw3da9G-FE4dAK-CD) | succeeded — ON CADENCE; next fire Mon 10-19, silence since Mon is expected |
| 82888287 | hourly | 2026-10-15 17:30 (j-AbxmwBnA-QhHEL8-CD) | succeeded; 209/212 green lifetime |
| 82889357 usage_metrics_rollup_v2 | hourly | 2026-10-15 17:42 (j-AbxnAwM9-aap3Qd-CD) | succeeded; 202/202 green lifetime |

### Answers to the 4 investigation questions

1. **Shared stop cause?** None exists to share — zero of the 9 are stopped. All report
   running=true AND have succeeded jobs on/after 10-12. There is no trigger-level failure,
   no scheduler stall, no missed-fire gap beyond 82888690's designed weekly cadence.
2. **Was the 10-11 rebuild wave (BSYS-29656) the mechanism?** Only as an evidence artifact,
   not a runtime one. The wave EDITED these recipes 10-11 01:46-02:17 EDT (= 05:46-06:17Z),
   and the "frozen last_run_at" figures are those edit timestamps (`updated_at`) misread as
   run activity. Scheduler next-fire state was NOT reset: 82963931 fired 10-12 10:43 PT
   (anchor shift from the post-edit restart) then resumed daily 07:13; all others kept their
   cadences unbroken through the wave.
3. **Same failure class as canary 82964017 (BSYS-29560)?** NO. The canary is genuinely
   stopped (`stop_cause=trigger_errors_limit`, trigger-level silent death, 14/14 succeeded
   jobs, connector output-schema drift). The batch has no stop event at all. Two different
   worlds: one real stopped recipe, one stale-timestamp false alarm. Do not merge the cards.
4. **What the watchdog sweep did NOT see:** (a) actual job traces — its "last_run" source is
   recipe metadata, not job history; (b) cadence semantics — weekly 82888690 and ~nightly
   82964024/82964058 legitimately go 24h-7d between fires, so an updated_at-as-last_run
   misread is invisible precisely on the slow-cadence recipes; (c) interval configs and
   version history are not in the sweep's evidence at all (it never pulled recipe_get).

### VERDICT

**Multi-symptom, single-cause — and the cause is in the EVIDENCE PIPELINE, not the fleet.**
The gw_semantic nightly batch is not dark: 9/9 recipes fired after the 10-11 rebuild wave,
8/9 fired today. The "frozen last_run_at 10-11T05:46-06:17Z" is the rebuild wave's edit
timestamps (`updated_at`) being read as run activity by whatever produced the alarm.
Suspected mechanism: sweep/digest source reads recipe metadata instead of job traces.
Minimal live check to confirm: for any one of the 9 (e.g. 82963931), compare
recipe_list/recipe_get `updated_at` against job_list newest job — if the alarm's timestamp
equals `updated_at` while a newer succeeded job exists, the pipeline misreads the field.
(Already true on this pass: alarm said 05:46Z = the recipe's 01:46 EDT edit time; newest
job is 10-15 07:13 PT.) The only REAL defect in the folder remains canary 82964017's
trigger_errors_limit stop-loop (BSYS-29560 / BSYS-29656 recurrence) — tracked separately.

Read-only held: no recipe, lifecycle state, or file other than this findings file was touched.
