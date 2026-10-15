# Investigation: dual claims-ledger problem (claims/ vs integrity/)

- Investigated: 2026-10-14 (read-only dispatch, session 2026-10-15 window)
- Trigger: brain-gardener bus report 2026-10-15T02:56Z — two claims ledgers, ID-space
  collision (clm-014 in both, renumbered), P1-class claims invisible to drift-gate.
  NOTE: the bus post itself could not be read this session (brain MCP permission-gated);
  its substance is taken from Josh's dispatch and verified against the files on disk.
- Prior art: cortex/investigations/clm-014-duplicate-claims.md (2026-10-12) covers the
  IN-FILE duplicate inside claims/claims.jsonl but PREDATES the second ledger —
  integrity/claims.jsonl was created 2026-10-13, one day after that investigation.
- Read-only throughout. Nothing was changed except this file.

## 1. The two ledgers

| | claims/claims.jsonl (legacy) | integrity/claims.jsonl (integrity mesh) |
|---|---|---|
| Size | 10,501 B | 10,470 B |
| Last modified | 2026-10-11 22:11 | 2026-10-13 18:00 |
| Rows | 16 | 17 |
| Schema | {id, subject, claim, evidence[], confidence, asserted_at, last_verified, status} | {claim_id, ts, agent, statement, tier, proof, legacy_*} |
| ID space | sequential clm-001..clm-015 + ONE duplicate clm-014 | clm-001..clm-015 (backfill) + hash IDs clm-9473e281, clm-7d688215 |
| Writer | none live (frozen since 10-11) | claim-submit.py (only live writer) |

Related but NOT ledgers: `claims/maturations/negative-fixtures.jsonl` (affinity-mature
fixtures, no IDs), `claims/verifications.jsonl` (838 B), `reports/claims-sweep-*.json`
claims-sweep.py reads mission-control/events.jsonl, NOT either ledger — name
collision of terms only, out of scope).

## 2. Reader/writer map

**Read integrity/claims.jsonl:**
- claim-submit.py:34 (LEDGER — writer, append-only)
- reconcile.py:31 (DEFAULT_CLAIMS — flags asserted-tier claims >24h without proof)

**Read claims/claims.jsonl (legacy):**
- drift-gate.py:34 (CLAIMS — the semantic-drift gate; THIS IS THE INVISIBILITY)
- synaptic-strength.py:38 (last_verified signal join)
- brain-dashboard.py:262 (dashboard claim panel)
- dream-mini.sh:97 (dream input)
- affinity-mature.py:43 (read-only; never edits claims per its own docstring)

**Neither:** claims-sweep.py (mission-control events), fdt-gate.py (temp file only),
kb-audit / turn-audit / instruction-miner / em_kb_sync / morning-digest (docstring
mentions only, no ledger path).

**Cross-ledger link:** claim-submit.py `backfill` (line 15-16, 130) re-emits legacy
rows into integrity as tier-"asserted", idempotent by claim_id. Run 2026-10-13.

## 3. The concrete collision set

**clm-014 exists twice in claims/claims.jsonl (lines 14 and 16), with conflicting
subjects:**
- line 14: `deployment-request-convention-enforced` (asserted 2026-10-07, active, high)
- line 16: `drift-prevention-steering-pattern` (asserted 2026-10-11, active, medium)
  — this is the renumbered claim the gardener flagged; it should have been clm-016
  (clm-015 is the max, no gaps). Root cause per the 10-12 investigation: two write
  paths (gardener claim-submit vs librarian procurement) without a shared last-ID counter.

**Integrity ledger collision effect:** the 10-13 backfill deduped by claim_id, so it
ingested only the FIRST clm-014 (deployment-request) and SILENTLY DROPPED
drift-prevention-steering-pattern entirely — integrity has 15 clm-00x rows for 16
legacy rows. clm-001..013 and clm-015 are 1:1 identical subjects across both files
(verified: same statements, legacy_* fields carried). No other numeric conflicts.

**The P1-invisibility mechanism (the part the 10-12 investigation could not see):**
drift-gate.py hardcodes claims/claims.jsonl. Every claim filed after 10-11 through
claim-submit — clm-9473e281 (integrity-mesh scripts live) and clm-7d688215 (Gateway
costUSD is NOT a gateway price, 619-entry measurement, 10-13) — exists ONLY in
integrity/ and NEVER reaches the drift gate, synaptic-strength, brain-dashboard, or
dream-mini. The costUSD correction claim is exactly the P1-class finding going
ungated. Secondary damage: drift-gate.jsonl history already has clm-014 rows carrying
BOTH subjects (10-13/10-14 runs) — same ID, two verdicts, one doc-supported one
weak-support — polluting any per-ID trend query.

## 4. Smallest safe merge order

1. **Fix the in-file duplicate in legacy (per the 10-12 plan, unchanged):** renumber
   claims/claims.jsonl line 16 clm-014 → clm-016 (deployment-request keeps clm-014;
   predictions.jsonl prd-017 and drift-gate rows 12/25/31 cite A). Update INDEX.md
   line 87 and the drift-gate.jsonl line-33 row. This is a WRITE — needs Josh's go.
2. **Re-run `claim-submit.py backfill`** — idempotent, will ingest the renumbered
   clm-016 and close the 16-row gap. Zero code change.
3. **Repoint the legacy readers at integrity, one line each** — drift-gate.py:34,
   synaptic-strength.py:38, brain-dashboard.py:262, dream-mini.sh:97, affinity-mature.py:43
   — with a subject/claim → statement field adapter. drift-gate first (it is the gate
   with the P1 blind spot); the rest can trail.
4. **Declare integrity/claims.jsonl canonical; freeze claims/claims.jsonl as an
   immutable archive** (chmod 444 or a header line) so no writer re-seeds the old
   ID space. Sequential clm-00N = backfilled legacy, hash clm-xxxxxxxx = new claims.
5. **Annotate, do not rewrite:** drift-gate.jsonl clm-014 dual-subject rows and
   librarian bus posts are timestamped history — errata note only.

Why this order: (1) unblocks (2) — backfill would otherwise re-drop the duplicate;
(2) before (3) so the repoint sees a complete ledger; (3) before (4) so no reader is
left on a frozen file. Steps 2-5 fix recurrence, not just the symptom.

## Unverified

- The gardener's bus post verbatim (brain MCP permission-gated this session).
- reconcile.py's exact treatment of the dropped drift-prevention claim (read of
  claim-submit backfill dedup confirmed the drop; reconcile behavior inferred from
  its docstring, not traced).
- Whether any ledger reader outside scripts/ (agents/*.md prompts, hooks) references
  either path — grep covered scripts/*.py|*.sh only.
