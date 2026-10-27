
# HR Genie Perf Review Cycle dedup inventory — manifests 370467/370603 vs 371545, folder 35943947

Date: 2026-10-26 (cortex lookup dispatch, read-only; sources = local manifest mirrors + gossip bus 96h + knowledge tree; NO Workato API calls)

## VERDICT

**Overlap: YES (directional: the parallel-session manifests are covered BY 371545, not the other way).**

- **370467 vs 370603** (both = parallel BSYS-29730 day-1/week-1 session): overlap on **TBL | Perf Cycle | Nomination Log 164149** — 370467's single asset row IS 164149; 370603 carries it as row 1 of 10.
- **370467/370603 vs 371545** (FY27 squad promotion batch, root-folder anchor on 35943947, rebuilt 10-25 02:31Z, 94 rows claimed): the ENTIRE parallel-session Set B chain was sitting in folder 35943947 at rebuild time and the manifest covers the whole tree, so 371545's coverage includes, at minimum: 164149 Nomination Log, 164249 Review Shared Watermark, 164250 Quality Gate Verdicts, 83296106 FUNC Workday Nominee Enrichment, 83296142 FUNC Nomination Eligibility Guard, 83296269 recipe Nomination Intake, 351149 SKILL Nomination Intake (+ likely dep CON | Workato2 ISU 19760013).
- The FY27 Set A assets (resolve_nominee 83296325, get_competency_evidence 83296336, get_nine_box 83296507, Notification Ledger 164257, etc.) appear in NO parallel-session manifest — overlap only flows one way.
- **Caveat:** 371545's per-row composition is UNVERIFIABLE locally (assets endpoint 404s from CLI; claim-verification 10-25 flagged the 94-row count unverifiable; no local mirror). The inclusion list above is inferred from folder state at rebuild time + the lead's own parallel-session alert, not from reading 371545's rows. Also note timing: 371545 was rebuilt 02:31Z, BEFORE the 03:46Z Set B deprecation moved that chain to zArchive 35969315 — so 371545 as-built still references assets that have since left the live folder tree.

## Evidence

- `~/Documents/workbench/manifests/bsys-29730-hr-genie-perf-review-cycle.manifest.json` — full mirror of **370603** (10 rows, verified in-page 10-23): 164149, 164249, 164250, 83296106, 83296142, 351149 (agentic_skill), 83296269 (backing recipe), + off-folder deps 161960 EM AI Action Log, 18367190 Workato AI conn (Pinecone), 19760013 CON Workato2 ISU. zip_verify PENDING-BLOCKED on cross-project connection 18367190.
- `~/.claude/knowledge/projects/hr-genie/BSYS-29730-day1-spikes.md:72` — manifest **370467** = "1 asset row + folder chain" = Nomination Log 164149; mirror same file (in-page + ZIP verify still pending).
- `~/.claude/knowledge/projects/hr-genie/BSYS-29730-week1-build.md:13` — manifest **370603** row inventory matches mirror.
- Bus thread `hr-genie-fy27-review-cycle`, lead (josh session) 2026-10-25T02:31Z: "manifest rebuilt = 371545 (94 rows, verified, root-folder anchor)" + "PARALLEL SESSION ALERT: the root folder already held overlapping assets from another session (TBL | Perf Cycle | Nomination Log 164149, FUNC | Workday Nominee Enrichment 83296106, etc., manifests 370467/370603) - dedup decision pending with Josh."
- Bus same thread, lead 2026-10-25T03:46Z: "DEPRECATION EXECUTED: Set B chain (83296269 Nomination Intake, 83296106 Nominee Enrichment, 83296142 Eligibility Guard + table 164149 Nomination Log) stopped + moved to zArchive/Perf Review Cycle deprecated 2026-10-24 (35969315)."
- Bus same thread, builder-L: 3 archived (TEST twin 83296279, orphan tables 164249+164250 -> zArchive 35969315); Set A = 9 recipes + 5 tables kept; KEY CORRECTION: live genie was wired to Set B chain (83296269 → 83296106 + 83296142 + 164149), NOT Set A.
- Bus same thread, builder-M: cutover done — 7 Set A skills attached to live genie gin-AYbxpMha-YenKAJ-CD, Nomination Intake (351149/83296269) detached.
- `~/.claude/knowledge/garden-reports/claim-verification-2026-10-25.md:29` — 371545 exists via `wt api get /api/export_manifests/371545`: name "BSYS-29730 FY27 review cycle promotion batch", project_path "Agentic | HR Self Service Genie/Perf Review Cycle", status working; row count 94 UNVERIFIABLE (assets endpoint 404).
- `~/.claude/knowledge/cortex/attention-queue.md:7` — Josh's pending keep-which dedup decision, ref same bus lines.

## Open items for Josh's keep-which decision

- 371545 needs an in-page (UI) row read-back to confirm which of the 7 Set B assets are actually selected vs incidentally tree-covered; the CLI cannot list them.
- Since the Set B chain is now in zArchive 35969315, 371545 (root-anchor, rebuilt pre-deprecation) may carry stale rows into any promotion batch — re-select or rebuild at promotion prep regardless of keep-which.
- 370467 and 370603 are both superseded by 371545's coverage; 370603's own ZIP-verify remains blocked on the cross-project Pinecone connection 18367190.
