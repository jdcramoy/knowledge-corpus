# Investigation: duplicate claim ID clm-014 (claims.jsonl)

- Investigated: 2026-10-12 (read-only cortex dispatch)
- Ledger: `~/.claude/knowledge/claims/claims.jsonl` (16 rows, clm-001..clm-015, no other gaps or duplicates)
- Verdict: TWO distinct claims share `clm-014` — lines 14 and 16. Recommended fix: line 16 (the newer librarian claim) renumbers to `clm-016`; line 14 keeps `clm-014`. Do NOT edit in this investigation.

## The two colliding rows (verbatim)

### A. Line 14 — `deployment-request-convention-enforced` (the EARLIER claim; should keep clm-014)

```json
{"id": "clm-014", "subject": "deployment-request-convention-enforced", "claim": "Deployments are filed as Story/Bug under the governing epic, NEVER the 'Deployment Request' issue type — enforced at BOTH paths: jira-story-standards SKILL.md (Prompt-time injection via guardrails hook 6) AND the hook's embedded fallback digest (works when the SKILL.md is unreadable). The 2026-10-06 miss predated the fallback digest.", "evidence": [{"type": "skill", "ref": "jira-story-standards SKILL.md deployment section"}, {"type": "skill", "ref": "workato-guardrails register.js STANDARDS_FALLBACK lines 68-69"}, {"type": "doc", "ref": "dream 2026-10-07 proposal #1"}], "confidence": "high", "asserted_at": "2026-10-07", "last_verified": "2026-10-07", "status": "active"}
```

### B. Line 16 — `drift-prevention-steering-pattern` (the LATER claim; should become clm-016)

```json
{"id": "clm-014", "subject": "drift-prevention-steering-pattern", "claim": "AgentGUI (arXiv 2607.26300) demonstrates automated drift prevention raising small-agent task completion up to 34pp and 38% faster trace triage; a credible future harness capability is drift-prevention steering for the cortex (currently flag-only)", "evidence": [{"type": "url", "ref": "https://arxiv.org/html/2607.26300 (fetched 2026-10-11)"}, {"type": "doc", "ref": "library/attention-bottleneck-mission-control.md"}], "confidence": "medium", "asserted_at": "2026-10-11", "last_verified": "2026-10-11", "status": "active", "verified_result": "paper claims read 2026-10-11; not independently reproduced"}
```

## Why the earlier claim keeps the ID

- Minimizes churn: claim A (asserted 2026-10-07) carries ~10 historical references; claim B (2026-10-11) carries ~6.
- Claim A is the one external resolvers already key on: predictions.jsonl `prd-017` explicitly cites "clm-014 double-path enforcement holds", and drift-gate rows from 2026-10-09 predate claim B's existence.
- ID ordering matches assertion order — the ledger's only duplicate is a write-path failure, not an intent to displace A.

## Exact renumber mapping

| Row | Line | Old ID | New ID |
|---|---|---|---|
| deployment-request-convention-enforced | 14 | clm-014 | clm-014 (unchanged) |
| drift-prevention-steering-pattern | 16 | clm-014 | **clm-016** (next free; max existing is clm-015, no gaps) |

## References that would need updating (claim B's cluster only)

Must edit (live join surfaces):
1. `claims.jsonl` line 16 — the ID field itself.
2. `INDEX.md` line 87 — attention-bottleneck line cites "(clm-014)" → clm-016.
3. `garden-reports/drift-gate.jsonl` line 33 — the 2026-10-11 row with subject drift-prevention-steering-pattern → clm-016. (Rows 12/25/31 have subject deployment-request-convention-enforced and stay clm-014 — note this is why drift-gate output was ambiguous: same ID, two subjects.)

Historical records — annotate, do NOT rewrite (they are timestamped logs; a retroactive rewrite falsifies history):
4. `garden-reports/2026-10-11-librarian.md` lines 58, 87 — cites clm-014 for the steering claim; correct ID at write time was the collision, leave as-is or add a one-line errata note.
5. `dreams/bus/librarian.jsonl` line 5 — bus posts are immutable history; no edit.
6. `garden-reports/garden-2026-10-11.md` line 36 — refers to clm-014 by subject alongside; fine as-is.
7. `events/novel-stream.jsonl` — derived event stream, no edit.

Claim A's cluster needs NO changes: dreams/2026-10-07.md, morning-brief/2026-10-07.md, drift-gate rows 12/25/31, integrity/reconcile-report-*.md (3 files), predictions.jsonl prd-017, garden 2026-10-09 audit — all reference the deployment-convention subject.

## Root-cause pointer (for the claims owner)

cortex/questions.jsonl line 98 already asks how two writers produced the same ID. Both colliding claims were filed via different paths (gardener's claim-submit on 2026-10-07 vs librarian's procurement flow on 2026-10-11); a shared last-ID counter that a writer didn't consult (or a race) is the likely mechanism. Renumber fixes the symptom; the write path decides whether it recurs. Also corroborated independently by brain-gardener bus post 2026-10-12T03:05Z and garden-2026-10-11.md finding 2 — this investigation confirms with verbatim row capture and the reference map.

## Unverified

- Nothing unverified. Both rows quoted verbatim from the live file this session; reference sweep covered .md/.jsonl/.py/.sh across the knowledge tree.
