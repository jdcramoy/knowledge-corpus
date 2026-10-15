# BSYS-29488 — HR Genie telemetry completeness and outcomes reporting hardening (technical plan)

Posted to Jira 2026-10-10. Development only; no Production change in this story.

## Summary

Finish the unproven Development telemetry work: repair and prove the four Development collectors (pagination, cursor/late-arrival handling, idempotent checkpointing, masking, durable-ack-before-watermark), reconcile retained-window source data into the privacy-minimized fact model, and add only defensible business metrics to the aggregate-only v2 reporting layer. Live evidence shows two collectors are actively failing today (a stuck 500-row correlator backfill and a malformed-page failure class), so this is repair-plus-proof, not greenfield.

## Current state (verified 2026-10-10)

- [REC | HR Genie | Conversation Tool Event Collector 82178793](https://app.workato.com/recipes/82178793) (Running, 15-min): watermark in [HR Genie | Telemetry Collector State 156849](https://app.workato.com/data_tables/156849), 7-day re-drain horizon, 60s overlap, bounded budgets (10 conv pages x 100, 5 event pages per conv), cursor-cycle guards, idempotent upsert by event_id into legacy table 145706, checkpoint holds watermark on truncation. Job history: 2,982 jobs, 19 failed. Live failure [j-Absk4hA3-ksYxRb-CD](https://app.workato.com/recipes/82178793/job/j-Absk4hA3-ksYxRb-CD) 2026-10-10 01:06Z: `CONV_PAGE_MALFORMED: conversation page is not a JSON object` — a transient malformed provider page kills the cycle (fail-closed worked; no checkpoint advanced; but there is no bounded retry). Job [j-AbskAABx-AzfWTe-CD](https://app.workato.com/recipes/82178793/job/j-AbskAABx-AzfWTe-CD) has been `pending` since 01:11 EDT with no completion (hung/queued overlap — no leader election, known estate issue).
- [REC | HR Genie | Conversation Event Collector 82862205](https://app.workato.com/recipes/82862205) (Running, 15-min): already carries the BSYS-29477 inclusive-window +1s offset and a 6-hourly 7-day late-activity resweep; durable emitter ack (PERSISTED/ALREADY_PERSISTED) gates the monotonic checkpoint; all-skip guard fails visibly. Open gap in code: the per-conversation event fetch reads ONE 100-row page and raises `EVENT_PAGE_OVERFLOW_UNHANDLED` on any conversation with more events — coverage fails visibly and replays forever rather than draining multi-page conversations.
- [MON | HR Genie | MCP Tool Usage Collector 78545249](https://app.workato.com/recipes/78545249) (Running, 15-min): RecipeOps job-history based, per-tool watermarks in table 141250 with a 1-hour rewind overlap, idempotent upsert by job id into legacy table 141249, inventory cap guard (100 recipes) and job-history cap guard (1,000 jobs) both fail loud, failures route to the shared alert publisher [76234914](https://app.workato.com/recipes/76234914). Post-containment it no longer writes caller email/name/user id/error_summary; it still upserts into restricted legacy table 141249.
- [REC | HR Genie | Ledger Correlator 82863111](https://app.workato.com/recipes/82863111) (Running, 30-min): folds three legacy sources (141249 usage, 142899 outcomes, 140219 handled errors) into the App Event Ledger via the shared emitter [FUNC | Emit App Event 82862028](https://app.workato.com/recipes/82862028), durable-ack-gated watermarks, 500-row read caps. Live failures [j-Abshthhp-LJmBK3-CD](https://app.workato.com/recipes/82863111/job/j-Abshthhp-LJmBK3-CD) and [j-AbshQbx3-DwCgRF-CD](https://app.workato.com/recipes/82863111/job/j-AbshQbx3-DwCgRF-CD): `CORRELATOR_SOURCE_TRUNCATED: correlator_handled hit the 500-row read cap` — the handled-error backlog above the watermark exceeds 500 rows, so each run re-reads the same 500 rows (emitter dedup keeps it safe), holds the watermark, and fails. The backlog cannot drain at the current shape; 5 of 150 jobs failed. Late-arrival gap: any row timestamped below the watermark is dropped (`next if st < wm_t`) — no bounded resweep.
- Reporting layer: [REC | HR Genie | Intelligence Rollup 82863448](https://app.workato.com/recipes/82863448) (Running, hourly) publishes only the aggregate-only path into [HR Genie | Product Metrics Daily v2 158393](https://app.workato.com/data_tables/158393) (fixed all-up metrics, literal `all` dimension, k>=10, fail-closed completeness guards); legacy dynamic-dimension steps are skipped and masked (comment 1134741). Recent hourly ticks green (84/93 succeeded; zero-source suppressed path verified in [j-AbshoxWr-Nm9Cwp-CD](https://app.workato.com/recipes/82863448/job/j-AbshoxWr-Nm9Cwp-CD)). The v2 dashboard [idb-Abse8QCG-GLWTT9-CD](https://app.workato.com/insights/dashboards/idb-Abse8QCG-GLWTT9-CD/preview) renders four k>=10 all-up facts; the legacy Product Analytics board [idb-Abrntmt9-RYgtWH-CD](https://app.workato.com/insights/dashboards/idb-Abrntmt9-RYgtWH-CD) is restricted-legacy and per the pause handoff (comment 1134780) still has a miswired KPI card, hard-coded rolling windows, and sub-ten breakouts.
- Test infrastructure (TEST-only, stopped, excluded from promotion): fixture table [158407](https://app.workato.com/data_tables/6f8284e3-06b2-4321-815a-adc04319c3fc), seeder [82956985](https://app.workato.com/recipes/82956985), continuation verifier [82956990](https://app.workato.com/recipes/82956990) (job j-AbsdQPka-TCWXzm-CD), multi-page verifier [82957144](https://app.workato.com/recipes/82957144) (job j-AbsdxxXb-EDCnCY-CD). Data-tables continuation mechanics are proven; live-population rollup testing is not.
- Not verified in this pass: Coverage State (156843) row-level contents, the legacy table row counts (141249/145706/142899/140219), and the dependency tracker returned no rows for this workspace, so blast radius below is derived from recipe code reads, not the tracker index.

## Technical design

All work in the HR Genie Development project 15643451 (Intelligence Platform folder 35712141 and Operational Monitoring folder 32985204). Every change follows the hot-swap discipline: read persisted asset, stop, edit via AIRO push, independently read back, restore Running, masked trace.

### A. Collector repairs (each ends with the full test matrix)

1. **82178793** — (a) bounded single retry on a malformed/empty provider conversation page (the 7-day re-drain horizon already guarantees a retry next cycle; the retry only removes avoidable red failures); (b) replace remaining raw `conversation_id`/`genie_id`/`tool_call_id` producer mappings into legacy 145706 with salted-HMAC session/call keys (project property `HR Genie Telemetry Pseudonym Salt`), completing audit requirement 3 (comment 1134721) for this writer; (c) add a hung-job guard: a run that starts while a previous run is still pending logs a skip-count to Collector State instead of overlapping (no leader election exists on the platform). Test matrix: normal, empty, multi-page (>10 conv pages and >5 event pages), late-or-equal watermark boundary, replay (re-run same window; assert zero duplicate upserts).
2. **82862205** — replace the single-page event fetch with a bounded multi-page cursor drain per conversation (page budget + truncation flag folded into the existing checkpoint-hold logic, same shape as 82178793); keep `EVENT_PAGE_OVERFLOW_UNHANDLED` as the fail-visible backstop above the budget. Test matrix adds a synthetic multi-page conversation via the existing fixture pattern.
3. **78545249** — no logic change expected; prove idempotent replay (job-id dedupe), the 1-hour rewind overlap (late-or-equal), cap guards, and masking with masked traces. If the 1,000-job cap guard has fired in practice, add cursor paging to the job-history drain.
4. **82863111** — (a) replace the 500-row capped reads with continuation/cursor paging per source so the correlator_handled backlog actually drains (read cap becomes a budget, not a ceiling; `CORRELATOR_SOURCE_TRUNCATED` remains the fail-visible guard for budget overrun); (b) add a bounded late-arrival resweep (same 7-day re-drain horizon already used by 82178793/82862205) so rows backfilled below the watermark are folded instead of dropped; (c) keep durable-ack-before-watermark exactly as is. Then observe one run that drains the backlog and advances the watermark.

### B. Completeness and coverage model

- Collectors and correlator record per-run source-coverage outcomes (rows seen / persisted / skipped / truncated, sweep status) in [HR Genie | Telemetry Coverage State 156843](https://app.workato.com/data_tables/156843) (schema already exists, 10 columns).
- Reconcile the retained-window source data into [HR Genie | Source Event Facts v2 157686](https://app.workato.com/data_tables/91ea98ad-033b-4a67-bfb3-e3ea08664705) with its `sanitized_payload` field governed by an explicit field allowlist registered in [HR Genie | Telemetry Schema Registry 156841](https://app.workato.com/data_tables/40d6e33c-75b8-4480-bf15-2fa3f3a5e6cd) plus a persisted readback proof (per audit requirement on 157686).
- Validate dashboard source coverage: every v2 dashboard claim must map to a completed source-coverage row; uncovered or unknown inputs stay visibly labelled in the dashboard (existing pattern: `COMPLETE_CURSOR_PAGED` / coverage metadata).

### C. Outcomes reporting (only defensible metrics)

- All new metrics publish exclusively through the aggregate-only v2 path (Rollup 82863448 -> Product Metrics Daily v2 158393 -> the v2 dashboard [idb-Abse8QCG-GLWTT9-CD](https://app.workato.com/insights/dashboards/idb-Abse8QCG-GLWTT9-CD/preview)), fixed all-up taxonomy, literal `all` dimension, k>=10, no identity/HMAC/raw-id/text fields.
- Raw MCP vs Genie attribution: derive origin provenance (`raw-authenticated` / `Genie-linked` / `unattributed`) per canonical event in Source Event Facts v2 from collector-recorded origin (direct MCP caller vs Genie-mediated actor). Publish the raw-MCP-only aggregate ONLY when provenance covers 100% of the source window's rows and the same-environment dedup rule is proven; until then the metric stays unpublished (comment 1134762 boundary preserved).
- Outcome cohorts: notification -> matching-skill -> provider-verified linkage emitted only when the three-way linkage is unique per notification; response-time measures only for cohorts whose denominators are mature; cohort maturity definition is an open decision (below).
- Knowledge/ticket signals: published only as candidates labelled as such unless ticket-lifecycle evidence proves resolution/avoidance. No metric infers adoption, savings, deflection, or uptime from missing data.
- Legacy restricted sources (141249, 145706, 142899, [156842](https://app.workato.com/data_tables/24acb62d-70a4-463b-ac14-ce80814035f3)) are never dashboard sources; the restricted-legacy board stays labelled and unaltered.

### D. Failure posture (unchanged invariants, now proven per collector)

Durable-ack-before-watermark everywhere; watermark holds on truncation/budget exhaustion and advances only after all writes of a cycle are durably acked; fail-visible raises with actionable fingerprints; masked traces on every data-bearing step; fail-closed on unknown environment; k>=10 suppression on every published cell. Testing discipline per the fixture-testing rule: `wt fixture run`-style on-demand runs and synthetic fixtures, never waiting for scheduled ticks.

## Risks and blast radius

- Shared emitter [82862028](https://app.workato.com/recipes/82862028) is the single coupling point for all four collectors, the feedback consumers ([82863906](https://app.workato.com/recipes/82863906)), and the correlator — no change to its ack contract is in scope; every collector change must preserve the PERSISTED/ALREADY_PERSISTED gate.
- Collector State [156849](https://app.workato.com/data_tables/a43835e8-ce80-46d7-81f2-a98b4f93b0bd) is the shared checkpoint store (conversation_tool_events, conversation_events, correlator_* keys). A bad watermark write would corrupt every consumer's window; the readback-and-restore discipline plus the monotonic watermark logic are the mitigations.
- 82862205 and 82178793 both poll the same Agent Studio API every 15 minutes; adding multi-page drains increases API load — budgets stay bounded and staggered.
- De-identifying 145706 producer mappings changes existing row keys; downstream consumers of 145706 beyond the correlator must be enumerated at build time (correlator confirmed as reader; re-check during build before switching keys).
- Dependency tracker returned no index rows for this workspace; blast radius above is derived from code reads of the four collectors, the rollup, and the table list. Re-run the tracker check at build kickoff.
- Non-goals (per ticket and pause handoff): no Production change or promotion; no access-control work (the P0 least-privilege finding, comment 1134742, is separately gated); no destructive table/schema operation; no historical-row deletion (retention/legal decision is separate).

## Acceptance Criteria

- [ ] Each of the four collectors has a persisted exact asset readback after its change, and a normal / empty / multi-page / late-or-equal / replay test (as applicable) with job IDs recorded, all data-bearing trace lines masked.
- [ ] 82862205 drains multi-page conversations up to its budget and holds the watermark with a visible truncation flag beyond it; no `EVENT_PAGE_OVERFLOW_UNHANDLED` on conversations within budget.
- [ ] 82178793 survives a transient malformed page with a bounded retry and no checkpoint regression; overlapping runs no longer produce pending-job overlap (skip-count evidence).
- [ ] 82863111 drains the correlator_handled backlog to zero above-watermark rows, advances its watermark (job evidence of a run with `CORRELATOR_SOURCE_TRUNCATED` absent and checkpoint advanced), and folds late-arriving rows inside the resweep horizon.
- [ ] 145706 receives no new raw conversation/genie/tool-call identifiers (readback of persisted mappings + masked trace).
- [ ] Source Event Facts v2 `sanitized_payload` has a registered field allowlist and a persisted readback proof.
- [ ] Dashboard source coverage is validated: every published v2 claim maps to a completed coverage row in 156843; uncovered/unknown inputs remain labelled.
- [ ] Raw-MCP-only metric is published only if provenance covers 100% of a source window; otherwise it stays unpublished with the decision recorded.
- [ ] Outcome-cohort and response-time metrics appear only with unique linkage and mature denominators; knowledge/ticket signals appear only labelled as candidates.
- [ ] No Production change or promotion performed in this Story.

## UAT Evidence

- Evidence file: `artifacts/hr-genie-response-2026-10-08/bsys-29488-uat-evidence.md` (same tree as the privacy audit evidence), with per-collector sections: recipe version readback, test matrix results, job IDs (normal/empty/multi-page/late-or-equal/replay), masked-trace confirmation, downstream fact/checkpoint readback.
- Job IDs to be recorded: one per matrix cell per collector, plus the correlator backlog-drain run and the Source Event Facts v2 reconciliation run.
- Dashboard coverage: v2 dashboard screenshots plus the 156843 coverage rows backing each claim.

## Open decisions for Josh

1. Cohort maturity definition for response-time measures — the ticket requires "mature cohort response-time measures" but does not define maturity. Recommendation: a cohort is mature N days after its last notification, N=7 proposed but unspecified in the ticket — needs his number.
2. Correlator late-arrival resweep horizon — recommendation: reuse the 7-day re-drain horizon already established in 82178793/82862205 rather than inventing a new window.
3. Historical raw-row disposition in the four legacy tables — ticket says not automatically deleted by this work item; needs the approved retention/legal policy source before anything touches historical rows.

## Story points

8 — four collector repairs each with a five-cell test matrix and hot-swap discipline, a stuck correlator backfill to redesign around cursor paging, a fact-model reconciliation with allowlist proof, provenance-gated metric design, and dashboard coverage validation; comparable in surface count to BSYS-28420's 8.

---

What was NOT verified:
- Row-level contents of Telemetry Coverage State (156843), Collector State (156849), and the legacy tables (141249/145706/142899/140219) — data-table reads were not performed in this pass (data_table_query 404s on this server per estate knowledge; row counts and contents need UI/wt at build time).
- The root cause of the pending/hung job j-AbskAABx-AzfWTe-CD on 82178793 (status observed pending; not diagnosed).
- Dependency-tracker blast radius (index returned empty for this workspace) — derived from code reads instead.
- Whether any consumer of legacy table 145706 exists beyond the correlator (to be enumerated at build time before de-identifying producer keys).

plan ready — awaiting Josh's authorization to kick off the build

## Addendum (2026-10-10 05:40Z)

Jira comment 1134787 (autopsy, posted 05:35Z) shows collector [82862205](https://app.workato.com/recipes/82862205) is ALREADY mid-repair by another session (`hrg-coll-82862205-repair-20261010`, pushes 04:21-05:23 UTC) with a live phantom-conversation regression: a terminal empty page (`data: []`, blank cursor) passes the cursor guard and materializes a blank-id row that defeats the empty-batch guard. The build session must (a) coordinate with or supersede that in-flight repair session (one session per recipe; session holds ONE recipe), and (b) fold in the autopsy's fix direction: empty-page-terminates-regardless-of-cursor in the guard, blank-id rejection in batch prep, plus the two regression fixtures (empty page with blank cursor; blank row). Checkpoint watermark should be reset to canonical `%Y-%m-%dT%H:%M:%SZ` format during the proof pass (a non-canonical Ruby `Time#to_s` watermark was observed).
