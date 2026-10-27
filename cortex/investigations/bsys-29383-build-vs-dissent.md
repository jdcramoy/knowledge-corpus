# BSYS-29383 build-vs-dissent investigation — does the 3383902 fix answer the dissenter?

Written: 2026-10-17 ~11:00Z by cortex investigation session (read-only; nothing changed).
Question: does the built code-strip fix on dev twin 3383902 answer dissent findings 1-5, and do
manifest + red-team artifacts now exist for a promotion batch?

## Evidence base

- Mission-control closeout row `bsys-29383-autodeploy-memory` (2026-10-17T07:14Z, needs-josh).
- Dissenter thread `dissent-bsys-29383-deploy-memory-fix` (+ `dissent-bsys-29383-class2-autopsy`)
  in knowledge/dreams/bus/dissenter.jsonl.
- Plan file: knowledge/projects/deployment-request-autodeploy/BSYS-29383-plan.md (updated 10-17).
- Live recipe DSL reads (today, read-only): dev 3383902 (bt-dev, RUNNING, 7 top steps) and prod
  3792740 (bt-prod, RUNNING) — /tmp/3383902-dsl.json, /tmp/3792740-dsl.json.
- Manifest mirror on disk: ~/orca/projects/bt-auto-deploy/manifests/BSYS-29383.manifest.json.
- redteam dir listing; build-ledger.jsonl tail.

## Finding-by-finding verdict

1. STEP-0 CODE CHECK — ANSWERED. Done post-dissent, as measurement not estimate: live trace of
   prod 3792740 job j-AbxnoEYM-tm6xXX-CD shows connector page = 59 recipes / 167KB with
   code = 43.2% of every page (SR's ~90% corrected downward). Fix is not a no-op.

2. STEP-OUTPUT RETENTION / clear_scope — PARTIALLY ANSWERED; mechanism risk still live.
   - Outcome evidence: dev test v43 job j-Abxw4fn9-cktKQo-CD, 5,379 recipes (2x prod stress),
     SUCCEEDED in 6m01s, trace-verified code-free upserts, 2.2x faster per recipe.
   - Mechanism evidence ABSENT: today's live DSL read shows BOTH dev foreach loops carry
     clear_scope="false" — step 17 (simple loop, publish_to_topic) and step 19 (batch-100 loop
     wrapping the Snowflake upsert at step 21). The dissenter's exact demand — "dev test must
     measure peak memory before/after, not just pass/fail" — was never met: no peak-memory
     number exists in the plan, the closeout row, or any ledger entry.
   - Structural mitigation: the upsert now runs inside a batch-100 loop (bounded batches) rather
     than accumulate-then-upsert, which bounds per-batch memory; but raw List-Recipes page
     responses retained as step output for the job's life is exactly the unverified mechanism the
     dissenter flagged. 2x-stress pass without OOM is real but circumstantial.

3. ~95 MISSES/DAY → HARD FAILURES — REFUTED WITH DATA. Caller attribution on the 100-job sample:
   979 calls from daily setup vs only 21 from deploy-path lookup misses. Misses are rare, not the
   norm; the dissent's premise (949 runs/10 days ⇒ misses are the norm) conflated daily
   maintenance with misses. Fix does not convert a frequent self-healing path; no failure-class
   change at scale.

4. THREE RESOLVERS (3792734/3792732/56324388) — REAL, CORRECTLY DE-SCOPED. Two-pass reconciled
   autopsy (Jira comments 1140960 + 1141773) root-caused the function-execution-error class to a
   duplicate-name data collision (two 'New Critical Ticket CSM Notification' recipes, ids
   66937514 + 66835227, same folder 26978285, workspace 3535597): 24/3/2 split across the three
   resolvers. The memory fix never claims to cure this class; resolver hardening is a separate
   ticket, data cleanup (a delete) awaits Josh's go. Minor unresolved drift: dissenter's recount
   says 59 failed = 28 memory + 31 non-memory; the closeout says 31 memory + 29 duplicate-name.
   Cosmetic, but the two records disagree.

5. DEV/PROD SNOWFLAKE TABLE SHARING — STILL UNVERIFIED; DISCLOSURE NEVER MADE.
   - Today's live read: dev 3383902 Snowflake step uses connection account_id=1260266; prod
     3792740 uses account_id=1260601 — different connection records.
   - Whether both target the same physical DEPLOYMENT.RECIPES table could NOT be established:
     connection detail reads 404 on both /api/connections/:id and /api/v2/connections/:id
     (token scope absent — plan already noted missing data-table scopes).
   - The dissenter asked "verify before testing; disclose to Josh." The test ran; no disclosure
     on record. Dissenter itself rated shared-table impact benign (dev-slice rows, nullable
     code), so this is a process/disclosure gap, not a demonstrated hazard. Still open.

6. GOVERNANCE ARTIFACTS — MANIFEST YES, RED-TEAM NO.
   - Manifest: EXISTS. Dev manifest id 366061 ("BSYS-29383 — auto-deploy memory fix (dev)"),
     anchored folder 1604941, created at build start 10-16, read-back verified, 5 rows (recipe
     3383902 + topic 16251 + custom_adapter 186326 + 2 connections incl. Snowflake Recipe
     Usage). Mirror verified on disk (2,910 bytes, 5 rows).
   - Red-team: DOES NOT EXIST. No BSYS-29383 file in ~/.claude/knowledge/redteam/ (29 verdict
     files, none for this ticket). The closeout's own ask sequences red-team Tier 2 AFTER Josh's
     authorization. Per the standing order the verdict must be on record BEFORE the push —
     so it must be produced between Josh's "go" and any DR execution, not after.

## Bottom line

The build answers findings 1, 3, 4 cleanly. Finding 2 is HALF-answered: the outcome evidence is
strong (2x stress, no OOM, 2.2x faster) but the dissenter's specified mechanism check
(clear_scope, peak-memory measurement) was skipped — clear_scope is "false" on both loops and no
memory number was recorded. Finding 5 remains open as an unmade disclosure; connection-detail
reads are scope-blocked, so closing it needs either Orca connection inspection or the data team.

The promotion batch is NOT ready today:
- Red-team Tier 2 verdict: missing (required pre-push).
- Finding-5 disclosure to Josh: missing (one sentence in the DR ticket closes it).
- Recommendation on finding 2: either accept the 2x-stress pass as sufficient outcome evidence
  (defensible — the mechanism concern predicts exactly the OOM the 2x test failed to produce, at
  2x volume), or require a peak-memory reading from the existing v43 job's trace before push.
  Do not silently carry it as "tested."
- The closeout row's "TESTING COMPLETE" framing overstates finding-2 closure and omits the
  finding-5 disclosure the dissenter demanded; Josh's authorization should be requested with
  those two caveats stated, not flat.

Nothing was changed anywhere except this file.
