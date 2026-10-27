# v42 exposure-window audit — HR Genie Conversation Event Collector (82862205)

- **Date:** 2026-10-15 (audit run ~21:10–21:45 UTC)
- **Auditor:** claude session (cortex investigation, read-only)
- **Recipe:** [82862205 REC | HR Genie | Conversation Event Collector](https://app.workato.com/recipes/82862205) — dev workspace "Workato AHQ | AI" (user id 3535597)
- **Trigger:** dissenter finding `dissent-bsys-29519-v43-classifier` (material #5: "v42 exposure window unaudited") on the gossip bus; triage plan `~/.claude/knowledge/projects/hr-genie/bsys-29519-collector-pagewait-timeout-plan.md`; ticket BSYS-29519
- **Method:** read-only `wt api` GETs against the dev profile (job list + full job detail for every window job), full-text signal scans over all fetched traces, v42 source-of-truth code review from the pre-fix snapshot, data-table state/sink reads. Zero writes to any platform asset.
- **Trace cache (ephemeral):** `/tmp/v42traces/*.json` (177 job payloads, 7.0 MB) + `/tmp/v42-window-jobs.json`

## Window refinement (correction to the task statement)

v42 code was **deployed** 2026-10-12 07:58:01 PT (verified: snapshot `updated_at` = `2026-10-12T07:58:01.097-07:00` in `~/.claude/knowledge/app-snapshots/bsys-29519/recipe-82862205-pre-pagecommit-fix.json`; snapshot carries all three v42 markers — `timeout="60"` at both wait sites (steps 39/63), page cap `pages_used >= 10` at step 31, substring 404 classifier at step 45).

But the collector was **stopped 07:26–16:44 PT Oct 12**, so the *executing* exposure window is:

- **First v42 run:** `j-AbwE68kA-AxAgFQ-CD` 2026-10-12 16:44:44 PT
- **Last v42 run:** `j-AbxBoo9t-YopgnY-CD` 2026-10-14 12:15:15 PT (recipe stopped 12:29 PT for the v43 hot-swap)
- **177 scheduled runs** (43.7 h executing; 52.5 h deployed). All 175 green + 2 failed were clock-triggered ("Scheduler by Workato" ×175, "Processed event" ×2, both green idle ticks); **zero manual runs, zero repeats, zero test jobs** in the window.

## The v42 loss mode (code-verified, snapshot step 45)

```ruby
msg = input["error_message"].to_s.downcase
if msg.include?("404") || msg.include?("not found")
  { "skipped" => true, "permanent" => "true", "reason" => "conversation_gone_404" }
elsif msg.include?("page_commit_async_job_failed") && msg.include?("failed=0") && msg =~ /timed_out=[1-9]/
  { "skipped" => true, "permanent" => "false", "reason" => "page_commit_wait_timeout_uncommitted" }
elsif msg.include?("page_budget_exhausted")
  { "skipped" => true, "permanent" => "false", "reason" => "page_budget_exhausted" }
else
  raise input["error_message"].to_s
end
```

Any caught error containing "404"/"not found" (any case, anywhere — including "host not found" DNS errors or a poll-404 on the async page-commit job) → **permanent skip**. Snapshot step 78 then feeds `permanent == "true"` skips into `safe_iso`, so the watermark advances over them; snapshot step 46 is the ONLY insert into the skip_flags list (`30cc2b62…declare_list_30cc`) and the only carrier of the `permanent` flag (verified: all 10 insert_to_list steps enumerated; only step 46 has a permanent field).

## Q1 — Did any run hit the poll-404 / 404-classifier path? **ZERO hits found.**

Full-text scans over every byte of all 177 fetched job payloads (unmasked portions):

| Signal | Jobs with hits |
|---|---|
| `conversation_gone_404` (the loss-branch reason) | **0 / 177** |
| `"permanent": "true"` (any quoting/spacing variant) | **0 / 177** |
| `404` / `not found` / `not_found` (any case) | **0 / 177** |
| `err.http.response.client_error.not_found` | **0 / 177** |
| `PAGE_COMMIT_ASYNC_JOB_FAILED` (wait-failure signature) | **0 / 177** |
| `timed_out` | **0 / 177** |
| `PAGE_BUDGET_EXHAUSTED` | 11 (the budget-drain runs) |
| `PAGE_COMMIT_PROGRESS_REVISION_STALE` | 2 (the failed runs) |

The catch (line 44) fired in exactly **13 jobs**. Every visible classifier (line 45) output:

- **11 budget-drain runs** — all `{"skipped": true, "permanent": "false", "reason": "page_budget_exhausted"}`:
  `j-AbwEXEbf-JKgwxx-CD` (10-12 17:14), `j-AbwLHoQH-9AP4Gw-CD` (10-12 23:14), `j-AbwT6Psc-gPXYHK-CD` (10-13 05:14), `j-Abwbo4RK-XCFeWM-CD` (10-13 11:14), `j-Abwhackk-C386mY-CD` (10-13 17:14), `j-Abwr9e9c-48BXzH-CD` (10-13 22:59), `j-AbwrLF4K-obCGfH-CD` (10-13 23:58), `j-AbwzrMmd-tneg4T-CD` (10-14 05:00), `j-Abx3LWco-CrRPWr-CD` (10-14 05:39), `j-AbxAczRr-GHhCC3-CD` (10-14 11:00), `j-AbxArYNP-4BX8kK-CD` (10-14 11:33).
  Example catch input (j-AbwEXEbf, line 45 input): `PAGE_BUDGET_EXHAUSTED: pages_used=10 cap=10 - deferring conversation conversation-01M47QS63JZ3Q2Z5J9XFD03XZP to the next run` — no 404 content.
- **2 failed runs** — classifier re-raised (else branch), error text contains no 404:
  - `j-AbwramxJ-oDBNEE-CD` 10-14 00:00:55 PT — line 45 error_details: `PAGE_COMMIT_PROGRESS_REVISION_STALE expected=2 got=3`
  - `j-Abx39wgC-RDtaJW-CD` 10-14 05:38:56 PT — line 45 error_details: `PAGE_COMMIT_PROGRESS_REVISION_STALE expected=6 got=7`

Corroboration from the child page-commit function [82936791](https://app.workato.com/recipes/82936791): **137 child jobs ran inside the window, 0 failures.** All 26 lifetime child failures are ≤ 2026-10-12 07:13:48 PT — pre-window, belonging to the known v41 storm parents (j-Abtose33, j-AbtwwYbR, j-AbtxDAXW/j-AbtxPfRK/j-AbtxeGNW family). A poll-404 requires the child job record to vanish mid-poll; Workato retains job records (749 visible in history), every dispatched child exists and succeeded, and no child failure surfaced into the window.

Note: the v42 **timeout-deferral branch also never fired** (zero `timed_out` strings) — the 60s wait budget absorbed everything (max observed wait 50.2s, j-Abwbo4RK, per cadence log).

## Q2 — Were affected pages retried, or lost? **No 404-path hits exist to retry. All deferrals were retried.**

- Budget deferrals (`permanent=false`) never enter `safe_iso` (step-78 code), so the watermark holds below them and later runs re-sweep. Observed: deferral counts draining 910 → 902 → 709 → 711 → 711 → 709 → 662 → 467 → 467 → 467 → 468 across the 11 drain runs while the watermark advanced monotonically:
  `15:00:24Z(10-12) → 07:02:18Z → 09:57:03Z → 15:00:33Z → 19:44:25Z(10-13) → 06:55:31Z → 07:01:30Z → 07:01:39Z → 15:00:28Z → 18:02:23Z(10-14)` (line-78 `new_wm` per checkpoint run; 20 checkpoint runs total, 9 with skips=0).
- The 2 revision-stale failures **died before the checkpoint** (no line-78 in either trace) → watermark held → immediate successor runs succeeded (`j-AbwroLsM-JG6m6m-CD` 00:01:11 PT and `j-Abws6to9-tDJf3D-CD` 00:01:29 PT after the 00:00 failure; `j-Abx3LWco-CrRPWr-CD` 05:39:30 PT after the 05:38 failure).
- Downstream sinks received continuous in-window emissions (proves the retry machinery delivered, not just held): table 158099 (event_revisions, UUID f4b166af-11fc-4f61-96e3-cab30987916d) = **77 rows created in-window across 21 distinct conversations** (30 LIVE-scope, 47 UNKNOWN-scope); table 158100 (capture_observations, UUID 409c41f9-ba4f-459f-b763-98aaaf62bb65) = **509 rows in-window across 22 distinct conversations**. Per-day coverage unbroken (Oct 12/13/14).
- Post-window continuity (state table 156849, row `conversation_events`): watermark now `2026-10-15T15:00:30Z` and advancing, `conversations_processed_total` 547, `events_emitted_total` 148, status `active`, last_run 2026-10-15 21:33Z. No stick, no regression.

## Q3 — Blast radius had loss occurred

One permanent skip = one conversation's entire event history silently absent from the facts pipeline: no rows in **158099 event_revisions** or **158100 capture_observations** (HMAC-pseudonymized; no plaintext PII path — transcripts are AES-256-GCM blobs, identifiers HMAC'd), and nothing for the downstream correlator lanes (state rows `correlator_usage/outcomes/handled/notif_pto/notif_inbox/notif_bp`) and HR Genie analytics reading those tables. Bounded population: the Oct 6–14 backlog (~910 conversations max in a single batch; only 21–22 distinct conversations actually emitted events in-window). Because the job stays green, the loss would be invisible to ops without this kind of audit — exactly the masked-green surface BSYS-29519's amendment closed in v44.

## Q4 — Verdict: **CLEAN** (with one stated residual)

No 404-branch firing, no permanent skip, and no data loss is visible on any evidence surface the platform exposes: zero loss-signature strings in 177/177 traces, all 13 catch firings explained (11 budget deferrals + 2 visible revision-stale re-raises), zero child-commit failures in-window, watermark arithmetic consistent with deferral-only behavior, sinks continuously fed, and post-window state healthy.

**Residual (stated honestly):** Workato job reports display only the **last execution** of a repeated step ([docs](https://docs.workato.com/en/features/account-properties.md) — "Steps that are repeated in a loop are not fully visible from the job reports, as only the last execution of that step is displayed") and truncate long values (~5 KB; observed: line-78 input cut mid-JSON at 5,647 chars). Loop-iteration classifier outputs other than the last are therefore unrecoverable from the job API, and `line_stat.map_input` counts proved non-authoritative (j-AbwT6Psc: line-46 count 530 vs the same line's reported `list_size` 709). A transient-404 masquerade in a non-last iteration cannot be excluded from traces alone. It is nonetheless implausible because all four independent channels are quiet: (1) the watermark never advanced during pure-deferral runs, though any permanent skip of a post-`2026-10-12T15:00:24Z` conversation would have lifted it (step-78 code); (2) the legit-gone case needs a list→fetch TOCTOU deletion race against the source conversation listing; (3) poll-404 needs Workato to lose a child job record mid-poll — contradicted by 137/137 child jobs present and green; (4) any non-404 transient error would have re-raised and failed the job visibly — only 2 failures, both revision-stale.

**Optional full-closure follow-up (not done):** source-vs-sink reconciliation — enumerate HR Genie conversations with window-era activity from the source API and diff against the 21–22 `conversation_hmac` values emitted in-window. Requires source-side read access scoping; out of this audit's read path.

**Side observation (not this audit's class):** `events_emitted_total` dipped 86 → 73 between `j-AbwrLF4K-obCGfH-CD` (23:58 Oct 13, still in flight ~55 min) and `j-AbwroLsM-JG6m6m-CD` (00:01:11 Oct 14) — a stale state-record read under overlapping runs, the same overlap that produced the revision-stale CAS conflicts (expected=2 got=3 at 00:00:55). Bookkeeping-only; events themselves are idempotent at the emitter (`source_job_id`). The revision-stale class is tracked separately (triage slug `page-commit-progress-revision-stale`).

## Evidence index

- v42 snapshot: `~/.claude/knowledge/app-snapshots/bsys-29519/recipe-82862205-pre-pagecommit-fix.json` (updated_at = 2026-10-12T07:58:01.097-07:00; classifier step 45, waits 39/63 timeout=60, cap step 31)
- Window job set: `/tmp/v42-window-jobs.json`; traces `/tmp/v42traces/` (177/177 fetched, 0 fetch failures)
- Key trace lines cited: line 45 outputs (11 budget runs), line 45 error_details (2 failed runs), line 78 outputs (20 checkpoint runs), line 44 catch summary (j-AbwT6Psc: last error from `workato_custom_code` at 06:15:50 PT)
- Data tables: 156849 `a43835e8-ce80-46d7-81f2-a98b4f93b0bd` (state), 158099 `f4b166af-11fc-4f61-96e3-cab30987916d`, 158100 `409c41f9-ba4f-459f-b763-98aaaf62bb65`, 156850 `8d46382a-6b9d-42e5-9b35-6c06a140f0b8` (topic taxonomy — not checkpoint state)
- Dissenter thread: `~/.claude/knowledge/dreams/bus/dissenter.jsonl` subject `dissent-bsys-29519-v43-classifier` (material finding #5 discharged by this audit)
- Cadence log: `~/.claude/knowledge/projects/hr-genie/BSYS-29519-collector-cadence-log.md`

## What was NOT verified

- Non-last loop-iteration trace content (platform-hidden; see Residual).
- Source-side conversation inventory (no HR Genie source-API enumeration performed).
- Table 158155 (page-commit progress rows) not cross-read for window-era coverage states.
- Child recipe traces were counted, not line-inspected (137 jobs, status-level only).
- The `/tmp/v42traces` cache is ephemeral; re-fetch from the API to re-verify.
- Per task constraints, no mission-control registry row and no INDEX.md update were written (findings-file-only scope); dispatcher should file the closeout row for workstream `bsys-29519` / project hr-genie: "v42 exposure audit complete — verdict CLEAN, residual noted."
