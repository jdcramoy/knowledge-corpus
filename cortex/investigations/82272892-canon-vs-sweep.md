# Autopsy: 82272892 canon-vs-sweep (2026-10-12, read-only)

Recipe: Sync Google Workspace Discovery Catalog — https://app.workato.com/recipes/82272892 (dev workspace 3535597)
Trigger: owned-asset health sweep 2026-10-13T01:34Z flagged 82272892 as new-failures, against canon.jsonl entry `ruby-eval-empty-payload` marked FIXED/CLOSED 2026-10-11.

## (1) Job history since the fix

Fix-verification anchor re-pulled live: j-AbtJdHxf-BgFEXs-CD (guard-empty-records-json) Status: succeeded, ran 2026-10-10T23:43:13 PDT (https://app.workato.com/recipes/82272892/job/j-AbtJdHxf-BgFEXs-CD). Full failed-job inventory via AIRO job_list status=failed (33 lifetime): after the fix jobs there are exactly THREE failures, all real scheduled runs on 2026-10-12 (PDT), each surrounded by green 15-minute cadence runs:

- j-AbwDFzAT-JYdJbm-CD — failed 2026-10-12T15:54:54 (https://app.workato.com/recipes/82272892/job/j-AbwDFzAT-JYdJbm-CD)
- j-AbwDG6JL-mrp9wg-CD — failed 2026-10-12T15:55:07 (https://app.workato.com/recipes/82272892/job/j-AbwDG6JL-mrp9wg-CD); green run 15:57:13 immediately after
- j-AbwFbQAo-TrkPQ4-CD — failed 2026-10-12T18:21:46 (https://app.workato.com/recipes/82272892/job/j-AbwFbQAo-TrkPQ4-CD); green runs 18:20:31 before and 18:23:08 after

The other recent failures in history (j-AbtJNHaT, j-AbtJMA44-RLKxec, j-AbtJKsJR, j-AbtJJs6a x2, j-AbtJHJN9, j-AbtJFEgm x2, all 2026-10-10 23:17–23:27 PDT) are the PRE-fix test/reproduction jobs already cited in the canon entry — not post-fix.

## (2) Signature classification of the 3 post-fix failures

NONE match the closed '783: unexpected token' empty-payload class. Zero occurrences of '783: unexpected token' in either full 4.9MB trace; guarded steps (trace lines 19/20/21 invoke_custom_ruby_code: Preserve-reviewed, Normalize-pagination guards) executed cleanly in all three traces, and the live recipe code still carries both guards + flexible_parse (recipe_get, 2 occurrences). Two NEW error classes instead:

- Class A (15:54:54 + 15:55:07 pair): failed line 41, adapter `google_workspace_semantic_gateway_runtime_connector_3535597_1789196780` (custom Connector SDK), operation materialize_semantic_retrieval_index. Error: "Registry tuple violates the risk/confirmation invariant: docs.documents.batchUpdate@v1/batch update documents is risk=external_side_effect with confirmation=intent_scoped; external_side_effect/destructive rows require confirmation=always. at line: 1412" (error ids 0b56a77b-07c8-4a44-80d0-c23bba57a79a, 8c33a048-b666-4469-9498-4c78424930d0). The raise lives in the connector's Ruby (line 1412, called from 1398/223) — the string does not exist in the recipe code. Data-driven fail-closed: a registry row carries confirmation=intent_scoped against risk=external_side_effect. The pair fired 13s apart on the same bad tuple; next run green.
- Class B (18:21:46): failed line 28, workato_custom_code 'Derive unique operation contracts'. Error: "Conflicting generated operation contracts for people.people.deleteContactPhoto@v1: activation." (code.rb:54:in `block in bind`, error id 1b56abde-0bb9-46a9-9e99-a506a9f809b4). Recipe-side intentional conflict detector (raise string confirmed present in live recipe code) firing on two registry rows for the same capability with different activation values; input records_json was fully POPULATED (fresh rows updated_at 2026-10-13T01:21:54Z) — the empty-payload guard path was not even exercised. Next run green 2 min later.

Classification per autopsy buckets: upstream data change / data-contract violation in the semantic registry pipeline (registry rows momentarily violating connector/recipe invariants), NOT a code bug in the guarded steps, NOT test-run artifacts (full scheduler trigger payloads, real 15-min cadence), NOT platform.

## (3) Verdict

The sweep flag is REAL but the canon entry is NOT stale: the closed ruby-eval-empty-payload fix (blank/null->[] guard + flexible_parse, dev v110) is verifiably intact — its covering job j-AbtJdHxf-BgFEXs-CD re-pulls as succeeded, the guarded steps ran clean through all three post-fix failures, and no '783: unexpected token' appears anywhere in the post-fix traces. What the sweep caught is a NEW DEFECT (two sibling classes) in the downstream semantic-registry consistency layer: Class A = the semantic-gateway runtime connector fail-closing on a docs.documents.batchUpdate@v1 row whose confirmation=intent_scoped violates its risk/confirmation invariant (jobs j-AbwDFzAT-JYdJbm-CD, j-AbwDG6JL-mrp9wg-CD); Class B = the recipe's own Derive-unique-operation-contracts step raising on conflicting activation values for people.people.deleteContactPhoto@v1 (job j-AbwFbQAo-TrkPQ4-CD). Both are transient registry-data states that self-cleared within minutes, but they are genuine fail-closed events the canon does not cover — candidates for new canon entries (registry-invariant-violation / conflicting-activation-contracts) and possibly a BSYS investigation into which writer produced the offending rows. Read-only scope honored: no recipe edits, stops/starts, tests, canon writes, or ticket writes; only this file was appended. Not verified: which upstream writer/data-table row produced the intent_scoped tuple and the duplicate-activation pair (would require data-table reads beyond the requested scope), and why extra trigger events clustered at 15:54–15:57 and 18:20–18:23.
