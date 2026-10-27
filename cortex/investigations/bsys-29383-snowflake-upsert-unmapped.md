# Investigation: Snowflake `upsert_rows_batch` — update branch vs. unmapped optional columns

**Question (single, read-only):** When Workato's Snowflake `upsert_rows_batch` UPDATE branch fires on an
existing row (keyed `ID + WORKSPACE_USER_ID`), does it overwrite columns that are mapped
optional-but-UNMAPPED in the rows mapping (specifically `CODE` and `CLEAN_CODE`, unmapped after the
BSYS-29383 schema change) with NULL, or does it preserve their existing values?

**Investigated:** 2026-10-20, read-only session. Verdict up front: **PRESERVES — existing values of
unmapped columns are NOT nulled**, proven empirically by the closure probe already on record; the
official docs are silent on the semantics (absence confirmed and is itself material for the verdict file).

## 1. What the docs say (and do NOT say)

Fetched in full: https://docs.workato.com/en/connectors/snowflake/upsert.md (the batch upsert action doc).

- Columns section: *"you will need to map the required fields from the output datatree here to upsert
  rows with data from preceding trigger or actions"* — describes mapping mechanics only.
- Only conditional statement: *"primary key values provided will be used to determine an update or
  create for each row."*
- **NOT stated anywhere:** whether the update branch writes the full row or only mapped columns;
  whether optional/unmapped columns are preserved, overwritten, or set to NULL. Zero occurrences of
  "null", "preserve", "unmapped", "optional" in a column-semantics sense.
- Sibling docs checked for completeness — https://docs.workato.com/en/connectors/snowflake/update.md and
  https://docs.workato.com/en/connectors/snowflake/insert.md (both HTTP 200, short pages): zero mentions
  of null/preserve/unmapped/overwrite semantics.
- Local KB (~/Documents/workato-kb, 5 query variants: 'snowflake upsert unmapped columns update branch
  preserve null', 'snowflake upsert update branch optional unmapped columns', 'upsert rows batch
  optional fields', 'snowflake write row null semantics unmapped', 'MERGE INTO update set only mapped
  columns database connector'): the only Workato-doc hits were the upsert doc itself and the analogous
  Db2/Redshift/SQL Server upsert docs — none of which state column-preservation semantics either. No
  changelog or Confluence hit addresses it.
- **The absence is material and CONFIRMED:** nothing in Workato's official docs answers this question.
  Any verdict resting on doc language alone would rest on nothing.
- Suggestive-but-not-evidence: generic SQL `MERGE ... WHEN MATCHED THEN UPDATE SET <listed columns>`
  convention only sets listed columns, but Workato does not document what SQL it generates.

## 2. Empirical evidence (decisive) — already on record

`~/.claude/knowledge/redteam/BSYS-29383-build-recipes-table-code-strip.md`, closure appendix
(2026-10-18):

- **MATERIAL-1 CLOSED — refuted by direct probe.** Throwaway probe recipe 83152838
  (manifest-exempt test probe) ran `SELECT COUNT(*) FROM DEPLOYMENT.RECIPES WHERE
  WORKSPACE_USER_ID = 800219 AND CODE IS NOT NULL` via the same Snowflake connection
  (job `j-AbzxXeda-cbabBE-CD`, succeeded): **code_rows = 3,944**.
- Context: the dev twin (recipe 3383902 — https://app.workato.com/recipes/3383902) ran the full
  code-free rebuild on 2026-10-15, upserting all 5,379 rows WITHOUT the code mapping, over a table
  whose rows previously held CODE. 3,944 of them (73%) still hold non-NULL CODE after being
  re-upserted unmapped.
- This is exactly the refutation test MATERIAL-1 itself defined in advance: *"count > 0 proves
  mapped-only update and this finding closes to cosmetic."* The count was 3,944.
- Corroboration: the build plan (`projects/deployment-request-autodeploy/BSYS-29383-plan.md`) records
  the dev test job (j-Abxw4fn9-cktKQo-CD, succeeded, ~6m) trace-verified code-free upserts.

## 3. Proven vs. assumed

**Proven:**
- On the dev twin's real full-volume run (5,379 rows, keys ID + WORKSPACE_USER_ID), rows re-upserted
  without the CODE mapping retained non-NULL CODE (3,944 rows). The update branch does NOT overwrite
  unmapped columns with NULL on that run. The "silent erasure of CODE history" scenario in
  MATERIAL-1 cannot occur as feared.
- The docs' silence is verified as of 2026-10-20 (live fetch + KB sweep) — the redteam file's claim
  "no column-preservation statement in the doc" remains accurate.

**Assumed / residual uncertainty:**
- The count probe is population-level, not row-level: it cannot list WHICH rows were match-updated vs
  insert-created. A critic could argue the 3,944 non-NULL rows were somehow never re-matched. Implausible
  (73% retention across a full-table rebuild keyed on the same ID + WORKSPACE_USER_ID), but not
  row-level proof.
- Behavior is undocumented, so Workato could change it in a connector release without notice — the
  empirical result is a point-in-time fact (2026-10-15/18 dev data), not a contract.
- CLEAN_CODE was never explicitly probed (it was dropped alongside CODE and rides the same unmapped-
  column mechanism; no evidence suggests different treatment, but it was not separately counted).

## 4. Recommended cheap probe (if row-level proof is wanted; ~2 min, dev Snowflake only)

Dev-twin single-row A/B: in the dev workspace, upsert one row into a TEST table with CODE='marker-1'
via upsert_rows_batch; then re-upsert the SAME key with CODE unmapped (and CLEAN_CODE also exercised);
then `SELECT CODE, CLEAN_CODE` for that key. CODE='marker-1' after round 2 = row-level proof of
preservation; NULL = docs-silence bites and the redteam finding reopens. Uses the existing Snowflake
connection, no prod touch, manifest-exempt under the TEST-naming exemption. Given the 3,944-row
evidence already on record, this is optional belt-and-braces, not a gate.

## 5. Note for the verdict file

The closure appendix in the redteam file is complete and correct on MATERIAL-1. One stale surface:
`cortex/attention-queue.md` (entry from 2026-10-18) still describes the verdict as "FAIL, blocks on
MATERIAL-1" — the file's own appendix supersedes that to effective PASS-WITH-NOTES. Flagged here,
not edited (read-only session).
