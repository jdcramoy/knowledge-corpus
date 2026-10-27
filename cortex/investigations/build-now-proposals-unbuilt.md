
## Investigation: 16 accepted-unbuilt / 4 BUILD NOW (gardener bus post 2026-10-20T02:48Z)

- Investigated: 2026-10-20, read-only session (josh, one-shot). Sources: `dreams/bus/brain-gardener.jsonl:59`,
  `garden-reports/2026-10-19-brain-gardener-nightly.md` (P1-P16 build-plan table), frontmatter of all 95 files in
  `dreams/proposals/`, `garden-reports/proposal-outcomes.jsonl`, `triage/queue.jsonl`, live `proposal-pipeline.py --json`.

### VERDICT: claim is STALE - queue drained after the report

`proposal-pipeline.py --json` now reports **0 accepted / 63 built / 8 rejected**. All 16 accepted-not-built
proposals (P1-P16) now carry `status: built` frontmatter. Zero are carded in `triage/queue.jsonl` (0 hits for all
16 slugs). No proposal is currently BUILD NOW / no builder.

### The 4 BUILD-NOW rows (Josh's 2026-10-19 /proposals pass)

| # | Proposal (slug) | Filed | Current status | Evidence check |
|---|-----------------|-------|----------------|----------------|
| P7 | file-gate-heading-fix | 10-15 (5d) | built | REAL - parser fix present in proposal-pipeline.py:76 (Inventions/Proposal queue dual-heading + fallback) |
| P10 | airo-addstep-append-trap | 10-16 (4d) | built | GAP - no dated entry found in workato-sdk-internals.md or airo-mcp-playbook; stamp-only, no outcome row |
| P14 | extend-not-replace | 10-17 (3d) | built | REAL - skill installed at ~/.claude/skills/extend-not-replace/, outcome row logged 10-20 |
| P15 | orca-ledger-self-pollution | 10-17 (3d) | built | GAP - no outcome row, no in-body build evidence; stamp-only |

### The other 12 (were accepted-unbuilt at 02:48Z)

| # | Proposal (slug) | Filed | Current status | Evidence check |
|---|-----------------|-------|----------------|----------------|
| P1 | push-identity-guard | 10-10 (10d) | built | REAL - hook 15 in guardrails register.js, 45/45 tests, outcome row 10-20 |
| P2 | session-shadow-gate-fix | 10-10 (10d) | built | REAL - live-proven 10-20 (61-min spacing, gate holds), outcome row |
| P3 | typed-sweep-findings | 10-12 (8d) | built | REAL - flag map live-proven same hour; outcome row |
| P4 | snapshot-writer-json-guard | 10-13 (7d) | built | GAP - no outcome row, no in-body evidence |
| P5 | em-arch-diagram-refresh | 10-14 (6d) | built | GAP - no outcome row, no in-body evidence |
| P6 | changelog-lens-zero-bits | 10-15 (5d) | built | GAP - no outcome row, no in-body evidence |
| P8 | knowledge-tree-write-durability | 10-15 (5d) | built | GAP - no outcome row, no in-body evidence |
| P9 | mc-defer-expiry-ttl | 10-15 (5d) | built | GAP - no outcome row, no in-body evidence |
| P11 | gws-fleet-receipts | 10-16 (4d) | built | GAP - no outcome row, no in-body evidence |
| P12 | gws-trigger-linter-guard | 10-16 (4d) | built | GAP - no outcome row, no in-body evidence |
| P13 | nightly-sync-receipts | 10-15 (5d) | built | INDIRECT - named as shipped inside nightly-receipts-gate (10-20 outcome row on report-existence-tripwire) but has no direct built row itself |
| P16 | triage-evidence-gate | 10-17 (3d) | built | GAP - no outcome row, no in-body evidence |

### Residual risk (the real open item)

11 of the 16 (P4-P6, P8-P13, P15, P16 minus P13's indirect row) are frontmatter-stamped `built` with NO
proposal-outcomes.jsonl row and no in-body build evidence - the documented pipeline contract requires a built
outcome row with evidence ref. Pattern matches the hand-edit incident noted in the 10-20 outcomes rows. Two
spot-checks: P7 verified real, P10 verified NOT in target doc. Treat the 10 unchecked GAP rows as
"claimed-built, unverified" until the evidence agent or Josh audits them.

### Recommended next owner (one line each)

- P7 file-gate-heading-fix: DONE - no owner.
- P14 extend-not-replace: DONE - no owner.
- P1/P2/P3: DONE - no owner.
- P10 airo-addstep-append-trap: brain-gardener or librarian - actually append the dated gotcha entry (the claimed build is absent from the target doc).
- P15 orca-ledger-self-pollution: builder session - verify checker hit-filter edit; if absent, apply per 10-18 judgment.
- P4 snapshot-writer-json-guard, P8 knowledge-tree-write-durability, P9 mc-defer-expiry-ttl, P12 gws-trigger-linter-guard, P16 triage-evidence-gate: evidence agent - audit claimed-built stamps; restore open status where no artifact exists.
- P5 em-arch-diagram-refresh, P6 changelog-lens-zero-bits, P11 gws-fleet-receipts, P13 nightly-sync-receipts: evidence agent audit, then rebuild from gardener P-table build plans if unverified.
- Fleet-level: whoever stamps frontmatter `built` MUST log the outcome row (proposal-decide.py) - propose a PreToolUse-style rule; see memory `prose-rules-need-tool-layer-enforcement` pattern.
