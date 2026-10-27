# Red-team DR-moment gap — BSYS-29519 coverage check (read-only investigation)

## 2026-10-19 — session: does BSYS-29778 cover BSYS-29519's collector assets?

**Question.** Evidence row 5 (garden-reports/claim-verification-2026-10-19.md:18) records
"Red-team DR-moment gap 29383/29519 VERIFIED-CLOSED (DR BSYS-29778 cites verdict, verdict
precedes DR)" citing `redteam/BSYS-29383-build-recipes-table-code-strip.md` — which does not
mention 29519. Does DR BSYS-29778 cover 29519's collector assets, or only 29383's?

**Evidence gathered (all live reads, 2026-10-19):**

1. **BSYS-29778** (Story, In Progress, created 2026-10-18T06:15:17Z, reporter/assignee Josh)
   — summary: "Deploy memory fix to prod: strip code field from [DEPLOY] LF | Build recipes
   table (3792740)". Scope per description: prod recipe **3792740 only**; manifest **367065**
   (prod, folder 1839746, 5 rows); red-team cited = `BSYS-29383-build-recipes-table-code-strip.md`
   (Tier 2); labels `BSYS-29383`, `auto-deploy`. Zero mention of BSYS-29519, collector
   82862205, function 82936791, or any HR Genie asset. Remote issue links: **empty ([]** —
   no manifest link or linked assets beyond the in-description references).
2. **BSYS-29519** (Bug, **Backlog**, updated 2026-10-14) — HR Genie Conversation Event
   Collector **82862205** PAGE_COMMIT_ASYNC_JOB_FAILED; fix touches collector 82862205 +
   commit function 82936791. UAT evidence: "to be recorded at build time" — nothing recorded.
3. **~/.claude/knowledge/redteam/ listing (14 files):** BSYS-25540, BSYS-28296 (×3),
   **BSYS-29383-build-recipes-table-code-strip.md**, BSYS-29498, BSYS-29514, BSYS-29584,
   BSYS-29587, BSYS-29680, BSYS-29698, BSYS-29700, BSYS-29727, BSYS-29757.
   Grep for `29519|82862205|82936791` hits **only** `BSYS-29498-hr-genie-oct-prod-batch.md`
   — the BSYS-29383 verdict contains **no** reference to 29519 or the collector recipes.
4. **The 29383 verdict itself** (read in full): scope is explicitly prod twin 3792740 /
   dev twin 3383902, Tier 2. Its closure evidence (probe 83152838, code_rows=3944) concerns
   the Snowflake upsert question. Nothing about the HR Genie collector.
5. **The only red-team coverage of 29519's assets** is `BSYS-29498-hr-genie-oct-prod-batch.md`
   (Tier 1 FULL, dated 2026-10-12, 44-asset HR Genie prod batch; deep review of collector
   82862205 v42, function 82936791, emitter, judge, digest). Its verdict: **FAIL** —
   two material findings open (F1 package drift: package 42198163 ships collector at v40
   while dev is v41/v42). A FAIL verdict blocks promotion; it does not authorize one. No
   closure addendum for F1/F2 appears in the file.
6. **Garden row 5** (claim-verification-2026-10-19.md:18): the verifier's evidence confirms
   only that (a) the 29383 verdict file exists at PASS-WITH-NOTES effective and (b) BSYS-29778
   was created 2026-10-18T06:15:17Z. It never checked whether the DR's scope includes 29519 —
   and it does not.

**Resolution of the contradiction.** BSYS-29778 is exclusively the BSYS-29383 code-strip
deployment (recipe 3792740, manifest 367065). BSYS-29519's collector assets (82862205,
82936791) are outside its scope by description, labels, and links. The evidence row's
"VERIFIED-CLOSED" is therefore supported for the 29383 half only; the 29519 half is a
mis-citation — the cited verdict does not mention 29519, and the DR does not cover its assets.

**Verdict: UNCOVERED.** BSYS-29778 covers only BSYS-29383's assets. BSYS-29519's collector
assets have no DR at all and no valid pre-DR red-team verdict on record: the only verdict
touching them is BSYS-29498's Tier-1 **FAIL** (2026-10-12), which blocks rather than
authorizes promotion, and no closure addendum closes its material findings. Today nothing is
actually being promoted (BSYS-29519 sits in Backlog; no 29519 DR exists), so no live
standing-order violation is in progress — but the garden ledger's "29383/29519
VERIFIED-CLOSED" claim is wrong as written and should be corrected: any future promotion of
the collector assets requires its own DR, fresh manifest, and a red-team pass that closes the
BSYS-29498 FAIL findings (or a Josh override by name).
