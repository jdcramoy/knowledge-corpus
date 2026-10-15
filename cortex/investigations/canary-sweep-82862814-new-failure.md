# Investigation: canary_sweep_and_promote — new failure 2026-10-13

**Job:** [j-AbwdecWb-F9kKRK-CD](https://app.workato.com/recipes/82862814/job/j-AbwdecWb-F9kKRK-CD) · [Recipe 82862814 canary_sweep_and_promote](https://app.workato.com/recipes/82862814) · 2026-10-13 13:10:44 PT (2h scheduler tick)
**Swept by:** workato-health 20:43Z — `new-failures` (10 prior failures all cluster 2026-10-07; this is the first since, 6 quiet days).
**Read-only investigation.** Nothing changed on the workspace.

## Verdict

**DEFECT (two-layer), not canary-by-design, not transient.**

- By-design contract: a red replay that RECORDS ITS STRIKE is success for this recipe. Here the strike was NOT recorded — the job died on the recording step. That is a failure by the recipe's own definition.
- Layer 1 (upstream, fully root-caused): the sandbox replay of a mutating capability (`people.people.updateContact@v1`) hard-failed in the gateway runtime instead of returning a structured red outcome. A new candidate registered TODAY by the hourly observation miner reached the canary for the first time — which is exactly why this fired today after 6 quiet days (the 10-07 cluster was build-iteration era, different failure signature: line 16 `insert_to_list` on an older recipe revision, e.g. job j-AbrYNfQf).
- Layer 2 (the job failure itself): the parent's strike-write then also failed. Red verdict never landed on the candidate row.

## Origin step

Parent: **line 31 — `workato_db_table.update_record`** (masked) on candidates data table [156859 workspace_organic_workflow_candidates](https://app.workato.com/data_tables/a1d50b08-df15-4388-82cb-f1b2b652c5c6), reject/else branch (line 22 if → 30 else). Failed 0.22s after entry — server-side write rejection, not a timeout.
Upstream trigger: child [82862817 j-AbwdepdX-RGazbn-CD](https://app.workato.com/recipes/82862817/job/j-AbwdepdX-RGazbn-CD) **line 11 — `commit_confirmed_mutation`** (Google Workspace semantic gateway runtime connector) → `Exception: resourceName contains an invalid reserved path identifier.` (gateway lines 1966/1959/1990/2048/512). All other children in that tick (slides.presentations.getStructure ×3, create) succeeded.

## Root cause

1. **Invalid resourceName synthesis (deterministic).** The updateContact replay's synthesized resourceName hit a reserved-path guard in the gateway runtime. Most likely an unsubstituted placeholder (`{{resource_id}}`-style facts template, cf. the 156865 overlay's `drive.files.delete` template shape) or a sandbox fixture ID colliding with a reserved path segment. Deterministic → will reproduce on every replay of this candidate.
2. **Strike-write failure on line 31 (the actual job failure).** Exact API error is masked (step has Mask data: true; failed-job detail returns no per-line I/O). The identical code path SUCCEEDED at 11:10 PT on candidate wf-3cc127579943 (record 6746d7f9-…, strike 0→1), so this is data/row-state dependent, not code. Leading hypotheses, in order: (a) stale Record ID — the hourly observation miner re-registered/deduped the new candidate row between `get_records` (13:10:44) and the write, or re-created it after 11:10; (b) the red payload for an EXCEPTION-errored child (vs the clean-UNSUPPORTED red the recipe handles at lines 12–13) carries a value the data-table write rejects (nil/oversized/mis-typed into strike_count or reviewed_at). **Unmasked UI job log (Orca) is the decisive next probe — not done here (read-only MCP scope).**

## State consistency: data table 156859

- Schema intact and reachable (data_table_get OK; 12 columns, created 2026-10-06, unmodified since).
- Row-level state is the inconsistency: candidate row for the updateContact candidate is frozen — `review_status` still `pending_canary`, strike NOT incremented, `reviewed_at`/`review_notes` stale from the last successful write (11:10 PT tick). The red verdict evidenced by child job j-AbwdepdX exists nowhere in the ledger.
- Caveat: row-level verification was NOT possible via MCP — `data_table_query` on 156859 returns HTTP 404 (deployed WorkAI service missing the query route; doc `guides:workspace-query` says don't retry). Consistency conclusion is inferred from job traces: 11:10 succeeded (strike recorded), 13:10 failed at the same step (strike not recorded).

## Blast radius

- Dev-only canary loop; no UAT/prod contact. Sandbox Slides deck created per replay; ~400-token gpt-4o-mini judge call per tick. Failure mode is loop-with-strike-frozen: the candidate will be re-swept and re-replayed every 2h tick indefinitely.
- Child replay (82862817) will keep hard-failing its own job each tick for the same candidate (7 child failures now; this adds a recurring one) — pollutes job history and any failure-based alerting on the gateway recipe.
- No data loss: the only skipped write is the strike itself.

## Recommended owner

**Josh, Google Semantic Gateway project** (dev estate; live ledger 147343). Fix sequence when picked up:
1. Read the unmasked line-31 error in the [parent job log](https://app.workato.com/recipes/82862814/job/j-AbwdecWb-F9kKRK-CD) (Orca) to pin layer 2 between hypotheses (a)/(b).
2. Fix the updateContact overlay/synthesis so resourceName is a valid sandbox path (layer 1) — and/or make the gateway return a structured `UNSUPPORTED`/red outcome instead of raising, matching the fail-closed pattern the parent already handles.
3. Harden parent line 31: wrap the strike-write in monitor/error-handling so a failed strike degrades to a logged warning, never kills the sweep.

## Repeat likelihood — next tick 2026-10-13 15:10 PT

**HIGH.** The candidate remains `pending_canary` (strike un-recorded), so line 1 `get_records` re-selects it; the same overlay template regenerates the same invalid resourceName (deterministic layer-1 failure), and whatever row-state/payload condition broke line 31 is unchanged. Expect both the child failure and a parent failure at 15:10 and every tick after until fixed.

## Evidence & what was NOT verified

- Cited: parent job trace (failed line 31 + full line table), successful twin trace 11:10 PT ([j-Abwbk9Pc](https://app.workato.com/recipes/82862814/job/j-Abwbk9Pc-MaCNkN-CD)) proving the strike path works, child trace (gateway exception verbatim), 110-job history (11 failures; 10-07 cluster = different signature), [table 156859](https://app.workato.com/data_tables/a1d50b08-df15-4388-82cb-f1b2b652c5c6) schema.
- NOT verified: the exact line-31 API error (masked; needs UI job log), row-level contents of 156859 (data_table_query route 404s), and which candidate_id the 13:10 tick processed (masked line-1/line-2 output; inferred from child capability ID `people.people.updateContact@v1`).
