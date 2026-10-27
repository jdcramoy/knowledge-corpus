# BSYS-29944 table-delete attribution

## Context (assembled 2026-10-25)

- Watchdog 2026-10-25: EM reconciler 83326270 threw `EM INVENTORY DRIFT (BSYS-29944): created=[] deleted=[~180 data tables...]` — no `EM | Session Log` attribution rows. Fail-closed gate working as designed; the ask is ATTRIBUTION (who/what deleted ~180 dev data tables, via which path).
- Premise to test FIRST: "Workato audit stream drops data-table delete events (proven 10-23)".
- Prior proof located: `projects/drift-fix/bsys-29828-overnight-incident-findings-2026-10-21.md` (RESOLUTION section) — swept `/web_api/activity_logs` 10-19 00:00 → 10-20 23:00 ET (2,215 events): NO `workato_db_table_deleted` for table 157379 that was definitely deleted, and no creation row either. Conclusion then: "the audit stream is the one channel that recorded the deletion" is FALSE. Note: table 163016's creation + ~20 schema updates DID appear in the stream — so coverage is event/class-dependent, not UI-vs-API-simple.
- Same file notes: "The 'Joshua Cramoy (via AIRO)' attribution likely came from the UI banner/trash" — i.e. the UI trash/banner carries actor attribution even when the audit stream does not.
- Local attribution surfaces available: garden-reports/usage-ledger.jsonl (every MCP call, with timestamps), guardrails build-ledger (destructive AIRO mutations carry asset_id since 2026-10-10 fix), EM Session Log data table (estate-monitor's own attribution), reconciler job traces (error text names the deleted tables).
- usage-ledger grep already shows only FOUR data_table_delete MCP calls ever: prod 2026-10-09 22:47Z; dev 2026-10-18 14:46/14:47Z; dev 2026-10-22 21:28Z; dev 2026-10-24 09:18Z. data_table_delete deletes ONE table per call → 4 calls cannot account for ~180 tables via Josh's AIRO MCP sessions unless calls are missing from the ledger.

## Premise check #1 — audit-stream drop is DOCUMENTED on the governing ticket

BSYS-29944 (https://workato.atlassian.net/browse/BSYS-29944), created 2026-10-23T23:35Z, description states verbatim:
- "the workspace audit stream does not record the data-table-delete event class at all. The DriftFix_Apply_Log (157379) deletion on Oct 19-20 left no claiming record anywhere."
- "Exhaustive forensic sweep (2026-10-23 session) exonerated both the local harness and the EM/drift genies for the 157379 deletion; the actual AIRO client is unidentified pending Workato-side logs."

=> The "proven 10-23" claim = the BSYS-29828/29944 forensic sweep. The story EXISTS to close this surveillance gap (Session Log + reconciler tripwire). The reconciler firing on 10-25 with ~180 unclaimed deletes is the tripwire catching its first real event — meaning the deletes happened in an attribution blind spot BY CONSTRUCTION (no claiming rows in EM Session Log / AI Action Log, and no audit-stream coverage for this event class).

## VERDICT: NO DELETIONS OCCURRED — attribution question is moot; the drift alert is a reconciler code bug (false positive by construction)

**~180 is also a misestimate: the true diff was deleted=103, created=3, and all 103 "deleted" tables still exist in the dev workspace right now.**

### Decisive evidence (all read-only, 2026-10-25 ~20:00 PT)

1. **Existence check:** fetched the full live inventory via `wt api GET /api/data_tables?per_page=100&page=N` — workspace has **742 data tables**. All **26/26** "deleted" UUIDs visible in the 10-25 02:09 PT failure's (truncated 2048-char) error text **still exist**. Sample: `workspace_learning_candidates`, `HR Genie | Eval Runs`, `[LOG] get_semantic_layer_index v2`, `CLI-TEST-DELETE-ME`, `HR Genie Watchdog | Pipeline Heartbeats` — all live.

2. **Smoking gun in the reconciler code** ([recipe 83326270](https://app.workato.com/recipes/83326270), pulled via AIRO `recipe_get`):
   - **Step 8 (drift gate) `current_json`**: `(bindings.adhoc_http_action_2['data'] || ...)` — **page 1 ONLY (100 tables)**.
   - **Step 10 (snapshot write) `content`**: `(action_2['data'] || []) + (action_3['data'] || [])` — **pages 1+2 (200 tables)**.
   - Any run that successfully reads its 200-table snapshot diffs it against a 100-table current → **~100+ phantom "deletes" guaranteed**. The gate can only pass when the FileStorage read fails and the catch path re-baselines (prior_json empty → "baseline" no-op).

3. **Exact reconstruction:** `/api/data_tables` orders numeric_id DESC (newest first; verified page boundaries: p1 = 164783..160006, p2 = 160005..154738). Reconstructing snapshot window (200 newest as of 10-24 02:45:15 PT snapshot write) vs current window (100 newest as of 10-25 02:09:09 PT job) from `created_at` values predicts **deleted=103, created=3** — and the 3 predicted created tables are EXACTLY the 3 named in the error text (`CE Ops Log` created 10-24 04:25 PT, `MG AWS Canary Token Stream` 10-24 18:53 PT, `workspace_capability_proposals` 10-24 20:57 PT). The error text's visible deleted UUIDs are all inside the predicted deleted set. 0 tables were created after the 02:09 job, so the reconstruction is exact.

4. **Fingerprint check:** 25/25 valid visible "deleted" samples sit in today's **page-2 numeric_id range** (154738–160005) — precisely the page step 8 forgets. A real workspace-wide mass delete would mix page-1 and page-2 IDs.

5. **Both failures are the same false positive:** 10-24 02:41 PT (j-Ac8DCazx, vs 02:20:39 snapshot) and 10-25 02:09 PT (j-Ac8ffw9Y, vs 02:45:15 snapshot) — both snapshots 379,663 bytes (identical content; no table changes between), both live fetches healthy (100+100 per trace line outputs), both threw the same phantom diff. The 10-24 02:41 throw was even cited in the estate-monitor notes as "drift-throw PROVEN" — the proof itself was this bug.

### Why runs sometimes "succeed" (the oscillation)

- Snapshot read OK → step 8 throws false drift (the two FAILED drift jobs).
- Snapshot read fails nil (known FileStorage content-pill flakiness, cf. 10-24 02:09 `no method '[]' for nil` failures) → catch path → "first-run baseline" → step 10 writes fresh 200-table snapshot → SUCCESS. The 10-24 02:45 and 10-25 02:45 "successes" are re-baselines, not reconciliations. ("Gate-before-snapshot ordering" never gets to protect anything — the gate IS the bug.)

### Latent second bug (post-fix preview)

Even with symmetric pages, the hardcoded 2-page cap watches only the **200 newest of 742** tables. Every table creation pushes a real table out of the window → spurious `created=N, deleted=N` drift. The 10-25 diff's real signal (3 genuinely new tables) would still throw. Fix needs paginate-until-empty (or a scoped inventory), not just the page-2 patch.

### Attribution surfaces — disposition of each

| Surface | Result |
|---|---|
| Workato activity audit stream | Confirmed documented gap (BSYS-29944 description, created 10-23: "the workspace audit stream does not record the data-table-delete event class at all"; BSYS-29828 findings: 2,215-event sweep 10-19→10-20 had NO `workato_db_table_deleted` for a table definitely deleted). **Real but never exercised here — nothing was deleted.** |
| Local harness ledgers (usage-ledger.jsonl, guardrails build-ledger) | Only 4 `data_table_delete` MCP calls ever: prod 10-09 22:47Z; dev 10-18 14:46/14:47Z; dev 10-22 21:28Z; dev 10-24 09:18Z. One table per call; none temporally or nominally match the drift list (all drift-listed tables still exist). Local harness RULED OUT — consistent with the 10-23 forensic sweep that exonerated it for the 157379 incident. |
| EM Session Log / AI Action Log | No claiming rows — correct, because there was nothing to claim. |
| Folder/project cascade delete | Moot — no deletes. |
| Reconciler trace (83326270 jobs) | The actual evidence source; contains the full story above. |

### Answer to the dispatched question

**Attribution is structurally RULED OUT because the event never happened.** There is no deleter — human, genie, AIRO client, or otherwise. The "deleted-by-via-AIRO class" alert fired on a page-asymmetry bug in the tripwire itself (built 10-24, BSYS-29944 scope). The 3 "created" tables are genuine and unattributed in the EM logs (their creator is whoever ran those dev builds 10-24 afternoon/evening PT) — out of scope for a delete investigation but noted for the record.

### Recommended follow-ups (NO changes made — read-only investigation)

1. Fix step 8 `current_json` to include page 2: `((bindings.adhoc_http_action_2['data']||[]) + (bindings.adhoc_http_action_3['data']||[])).to_a.to_json` (mirror step 10).
2. Replace the 2-page hardcap with paginate-until-empty (742 tables and growing; 8 pages today) — otherwise the fixed gate still throws on every table creation.
3. Re-baseline after the fix, then re-prove the drift-throw with an INJECTED test table create/delete (the 10-24 "proof" validated the bug, not the gate).
4. Correct the "~180" figure to 103 in the watchdog/ticket narrative.
5. Bigger design note for BSYS-29944: the reconciler currently detects its own bugs as drift. Consider a sanity ceiling (e.g., |deleted| > 20% of inventory → suspect the measurement, log differently) so future instrumentation bugs don't page as mass deletes.
6. The 10-23 premise stands untested-and-true for real deletes: audit stream still drops the class; UI trash/banner remains the only platform-side attribution for genuine table deletes until Workato-side logs answer the 157379 question.

_Evidence anchor jobs: j-Ac8ffw9Y-QexppR-CD (10-25 02:09 PT fail), j-Ac8DCazx-AmDNtd-CD (10-24 02:41 PT fail), j-Ac8DF6dK-fM6srf-CD (10-24 02:45 PT "success" = catch-path re-baseline). Snapshot: /em-audit-reconciler-inventory-latest.json (379,663 B, created 10-24 02:45:15 PT)._
