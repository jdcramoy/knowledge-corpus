# BSYS-29944 — EM INVENTORY DRIFT attribution (dispatched 2026-10-25 18:14Z)

Investigator: autopsy-investigation (read-only). Date of findings: 2026-10-26.
Governing ticket: https://workato.atlassian.net/browse/BSYS-29944

## Verdict

**NOT-ATTRIBUTED — because the event never happened.** There is no deleter (AIRO session, CLI, recipe, or human) to attribute. The ~180-table "mass delete" is a FALSE POSITIVE of the drift gate itself: reconciler recipe 83326270 (https://app.workato.com/recipes/83326270) diffs a 100-table current fetch (step 8, page 1 only) against a 200-table snapshot (step 10, pages 1+2), so every run that successfully reads its snapshot manufactures ~100+ phantom "deletions". The true diff was deleted=103 / created=3, and every sampled "deleted" table still exists in the dev workspace right now.

This verdict is a re-verification and endorsement of the completed prior investigation `cortex/investigations/bsys-29944-table-delete-attribution.md` (2026-10-25 ~20:00 PT), plus fresh live checks from this session (2026-10-26).

## Evidence

1. **Watchdog report** `~/.claude/knowledge/watchdog-reports/2026-10-25.md` (lines 70-77, 99): the drift gate threw `EM INVENTORY DRIFT (BSYS-29944): created=[] deleted=[~180 data tables...]` on job `j-Ac8DCazx-AmDNtd-CD`; watchdog correctly classified it as "needs Josh attribution", 3 failed / 8 succeeded history.

2. **Prior attribution investigation** `~/.claude/knowledge/cortex/investigations/bsys-29944-table-delete-attribution.md` (written 2026-10-25 20:34Z): full forensic workup already completed —
   - Existence check: full live inventory pull (742 tables on 10-25); 26/26 "deleted" UUIDs visible in the error text still existed, incl. `workspace_learning_candidates`, `HR Genie | Eval Runs`, `[LOG] get_semantic_layer_index v2`, `CLI-TEST-DELETE-ME`, `HR Genie Watchdog | Pipeline Heartbeats`.
   - Smoking gun in reconciler code: step 8 `current_json` = page 1 only (100 tables); step 10 snapshot = pages 1+2 (200 tables) — guaranteed phantom deletes on any successful snapshot read.
   - Exact reconstruction: `/api/data_tables` orders numeric_id DESC; snapshot window (200 newest @ 10-24 02:45 PT) vs current window (100 newest @ 10-25 02:09 PT) predicts deleted=103, created=3; the 3 predicted "created" tables match the error text exactly (`CE Ops Log`, `MG AWS Canary Token Stream`, `workspace_capability_proposals`).
   - Fingerprint: 25/25 sampled "deleted" UUIDs sit in page-2 numeric_id range (154738-160005) — exactly the page step 8 omits; a real workspace-wide delete would mix ranges.
   - Oscillation explained: "successes" (10-24/10-25 02:45) are catch-path re-baselines after FileStorage nil reads, not reconciliations.
   - Local harness ruled out: `garden-reports/usage-ledger.jsonl` shows only 4 `data_table_delete` MCP calls ever (prod 10-09 22:47Z; dev 10-18 14:46/14:47Z; dev 10-22 21:28Z; dev 10-24 09:18Z) — one table per call, none matching the drift list. Consistent with the 10-23 forensic sweep that exonerated harness and EM/drift genies for the 157379 incident (recorded in `projects/drift-fix/bsys-29828-overnight-incident-findings-2026-10-21.md` and on the BSYS-29944 ticket itself).

3. **Build ledger** `~/.claude/knowledge/build-ledger.jsonl`: all BSYS-29944-tagged entries (04:13-12:34Z on 10-25) are investigative reads (wt api GET inventory pages, FileStorage probe, transcript greps) plus the two heredoc appends writing the prior findings file. No delete-class mutations under this ticket. Ledger entries after the prior investigation's completion (20:34Z) mention neither 83326270 nor 29944 — no fix has landed; the buggy gate is presumably still live.

4. **Gossip bus** (`python3 ~/.claude/knowledge/scripts/gossip-read.py`, `dreams/bus/cortex.jsonl`):
   - 2026-10-25T03:20Z workato-watchdog finding `em-inventory-drift-bsys-29944` — "drift gate doing its job; needs attribution not a code fix."
   - 2026-10-25T04:03Z cortex — first attribution dispatch; 12:01Z cortex — that dispatch died on ENOTFOUND, re-dispatched.
   - 2026-10-25T13:04Z cortex finding `bsys-29944-ruled-out-zero-deletes` — "ZERO tables were deleted; the ~180-delete alert was the tripwire reconciler detecting its own pagination bug"; narrative correction + fix filed to triage as `bsys-29944-reconciler-page-asymmetry`.
   - 2026-10-25T18:14Z cortex — the dispatch that produced this report (issued after the 13:04 resolution; duplicate dispatch of already-answered question).

5. **Mission-control registry** `~/.claude/knowledge/mission-control/registry.json`: watchdog closeout row records the "needs Josh: investigate who deleted ~180 data tables unattributed" ask from 10-25; no later registry row records any deletion actor — because there is none.

6. **Fresh live re-verification (this session, 2026-10-26, read-only `wt api GET /api/data_tables` paged)**: dev workspace now holds **745 data tables** (up from 742 on 10-25 — net GROWTH of 3, matching the 10-25 ledger-recorded creates `workato_api_gateway_audit`, `workato_api_lessons`, `workato_api_lessons_index` under BSYS-29894). All 5 spot-checked tables from the "deleted" list (`workspace_learning_candidates`, `CLI-TEST-DELETE-ME`, `HR Genie | Eval Runs`, `[LOG] get_semantic_layer_index v2`, `HR Genie Watchdog | Pipeline Heartbeats`) are present in the live inventory today.

7. **Platform audit stream**: documented gap (BSYS-29944 description, 10-23: "the workspace audit stream does not record the data-table-delete event class at all") — real but never exercised here, since nothing was deleted.

## Open questions

1. The reconciler's pagination asymmetry (and the latent 2-page hardcap watching only the 200 newest of 745 tables) is documented in the prior investigation and filed to triage as `bsys-29944-reconciler-page-asymmetry` — but no build-ledger entry shows a fix landed. Until it does, the gate will keep throwing phantom-drift failures nightly; whether/when to apply the fix is Josh's call (out of scope here — no fix proposed by this report).
2. The 3 genuinely created tables in the diff window (`CE Ops Log` 10-24 04:25 PT, `MG AWS Canary Token Stream` 10-24 18:53 PT, `workspace_capability_proposals` 10-24 20:57 PT) carry no EM Session Log attribution rows; their creators are whoever ran those dev builds. Not a delete investigation, but noted for inventory hygiene.
3. The original 10-19/10-20 deletion of table 157379 (DriftFix_Apply_Log) remains genuinely unattributed at platform level — the audit-stream gap is still open pending Workato-side logs. That is the question BSYS-29944 was created for and is unaffected by this report.
4. Whether the EM Session Log should gain writer rows for table creates/deletes going forward so a future REAL drift event is attributable — design question for the estate-monitor owner, not answered here.
