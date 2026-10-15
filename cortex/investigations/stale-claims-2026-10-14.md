# Stale / low-confidence claims audit — 2026-10-14

**Verdict first:** the "~16 expected" does not survive contact with the ledger. `claims/claims.jsonl`
has 16 LINES but only 15 unique claims (13 active, 2 superseded), and NO claim carries an explicit
stale flag or numeric confidence. Applying the working definitions actually used by the gardener
(stale = last_verified ≥7d old, or flagged disputed/drifted in garden reports; confidence <0.6 =
drift-gate weak-support score or "medium" categorical), **12 active claims qualify** — that is every
active claim except clm-001. The 16 figure is almost certainly the file's line count being mistaken
for a finding count. Below: all 12, with subject, age, confidence, and load-bearing verdict.
Read-only audit; the ledger itself was not touched.

## Criteria actually available (schema has no stale flag / no numeric confidence)

- Canonical ledger confidence is categorical: 15×"high", 1×"medium". No 0–1 field exists.
- Numeric sub-0.6 scores exist only in the gardener's drift-gate (garden-reports/2026-10-09-brain-audit.md): clm-005 = 0.416, clm-007 = 0.437, clm-014a = 0.425 (all adjudicated "mis-routed class" — internal harness claims no Workato doc could ever support, proposed reclass to live-probe path; still pending).
- "Stale-flagged" exists only in garden-report prose: clm-002 disputed (1 refutation, 2026-10-09; a second supersedes), clm-011 version drift (embedded v0.8.0 vs installed — re-verified v1.0.0 live today), clm-014 ID collision (two distinct claims share one ID; renumber queued, unchanged since 10-12).
- Age reference: today is 2026-10-14. last_verified 2026-10-06 = 8d, 2026-10-07 = 7d, 2026-10-09 = 5d.

## The 12 qualifying active claims

| id | subject | asserted | last_verified (age) | confidence | verdict |
|---|---|---|---|---|---|
| clm-002 | dev-recipe-stop-start-delegation | 2026-10-06 | 2026-10-06 (8d) | high, DISPUTED (1 refutation) | LOAD-BEARING |
| clm-003 | jira-story-points-rule | 2026-10-05 | 2026-10-06 (8d) | high | LOAD-BEARING |
| clm-005 | dependency-tracker-payload | 2026-10-02 | 2026-10-06 (8d) | high; drift-gate 0.416 | LOAD-BEARING |
| clm-006 | local-marketplace-loads-in-place | 2026-10-06 | 2026-10-06 (8d) | high | LOAD-BEARING |
| clm-007 | josh-writing-voice-skill | 2026-10-06 | 2026-10-06 (8d) | high; drift-gate 0.437 | LOAD-BEARING |
| clm-009 | process-run-stdin-param | 2026-10-07 | 2026-10-07 (7d) | high | LOAD-BEARING |
| clm-010 | docs-crawler-dynamic-pages | 2026-10-07 | 2026-10-07 (7d) | high | IGNORABLE |
| clm-011 | prod-cli-wt-instances-and-gate | 2026-10-07 | 2026-10-07 (7d) | high, DRIFTED (v0.8.0→v1.0.0) | LOAD-BEARING |
| clm-012 | dream-loop-and-harness-backup | 2026-10-07 | 2026-10-07 (7d) | high | LOAD-BEARING |
| clm-013 | gossip-bus-maildir | 2026-10-07 | 2026-10-07 (7d) | high | LOAD-BEARING |
| clm-014a | deployment-request-convention-enforced | 2026-10-07 | 2026-10-07 (7d) | high; drift-gate 0.425; ID collision | LOAD-BEARING |
| clm-014b | drift-prevention-steering-pattern | 2026-10-11 | 2026-10-11 (3d) | **medium (<0.6)** | IGNORABLE |

Excluded, with reason: clm-001 (active, high, live-probe CONFIRMED 2026-10-09 — only active claim
that is neither stale nor weak) — clm-004, clm-008 (status superseded, correctly retired at find-time).

## One-line verdicts

- **clm-002** — LOAD-BEARING: governs the delegated dev stop/start used in nearly every build session; carry the dispute flag (CLI-start no-op observed once, 2026-10-09) and verify with a job trace before citing.
- **clm-003** — LOAD-BEARING: creation-time story-point rule fires on every Jira ticket; 8d unverified but rule-level, low decay risk.
- **clm-005** — LOAD-BEARING: steers recipe-read tool choice away from a ~2.8x payload blowout; the 0.416 is a mis-routed-class artifact (internal tool claim), not doubts about the measurement.
- **clm-006** — LOAD-BEARING: grounds the whole mods in-place-edit workflow (guardrails, skills); if it ever broke, every mod edit would silently stop loading.
- **clm-007** — LOAD-BEARING: governs all outward prose as Josh; the 0.437 is mis-routed-class (a personal voice skill has no Workato doc source). SKILL.md existence spot-checked in gardener run 10-09.
- **clm-009** — LOAD-BEARING: silent zero-byte-ledger data-loss class (the bug ate a day of jsonl writes); cheap to re-probe and worth keeping fresh.
- **clm-010** — IGNORABLE: crawler-specific hash-hygiene rule with one consumer (docs-watch); matters only when crawler work resumes, and the crawler already carries the fix.
- **clm-011** — LOAD-BEARING — and the most dangerous row in the ledger: it is the dev/prod topology + prod-write-gate claim, and its embedded version is now TWO releases behind (text says v0.8.0/hook 13; installed is v1.0.0, verified live today; gardener proposed supersede 10-08, still not done). The topology itself shows no sign of drift; the version citation does.
- **clm-012** — LOAD-BEARING: nightly backup + dreamer trust ladder; the never_auto list is constitutional, so staleness here is low-decay.
- **clm-013** — LOAD-BEARING: bus protocol every agent brief references; note the 10-14 bus audit found the corroboration-tally promise overscoped vs real traffic — protocol exists, its stated corroboration discipline is aspirational.
- **clm-014a** — LOAD-BEARING: hook-enforced (dual path: SKILL.md + fallback digest) deployment-convention claim; the 0.425 is again mis-routed-class; the ID collision is a hygiene defect, not a content doubt.
- **clm-014b** — IGNORABLE: medium-confidence research-futures claim (AgentGUI paper, 34pp drift-prevention headline) explicitly marked "not independently reproduced" — advisory input to the cortex steering idea, never load-bearing.

## Cross-ledger note

`integrity/claims.jsonl` (17 rows) is a backfill mirror of the canonical 15 plus 2 `proved` rows
(clm-9473e281 integrity-mesh scripts, clm-7d688215 gateway-costUSD verdict). No numeric confidence
there either — the tier field (asserted/proved) replaces it. The dual-ledger split is already a
queued P1 (garden-2026-10-13, "claims-ledger-split" thread, needs Josh on canonical home).

## Queue for whoever acts on this (in order)

1. Supersede clm-011 with a v1.0.0 restatement (drift is 6 days old and compounding — two releases behind now).
2. Renumber the clm-014 collision (queued since 10-12, still two rows sharing one ID).
3. File the clm-002 second-refutation watch: one more CLI-start no-op observation supersedes it.
4. Reclassify clm-005/007/014a to the live-probe/no-source class per the pending 10-09 adjudication — kills the fake sub-0.6 scores at the root.

*Method: read-only. Sources: claims/claims.jsonl, integrity/claims.jsonl, garden-reports (10-08 nightly, 10-09 audit, 10-12 drift-conflict-rot, 10-13 weekly), claims-sweep-latest.json, drift-gate scores, live version check of ~/mods/workato-guardrails (v1.0.0). Nothing edited, superseded, or muted in the ledger; the only write is this report. Not verified: no live re-probe of any platform-behavior claim (clm-001/002/005/009) — verdicts rest on the gardener's recorded verifications plus today's one version spot-check.*
