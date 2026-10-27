
## Lookup sweep: Workato deleted enterprise-context-connector doc pages (dream 2026-10-22)

Run: 2026-10-23, cortex lookup dispatch (read-only sweep; nothing edited, synced, or re-synced).

### 1. Citation hit list — knowledge tree (`~/.claude/knowledge`, grep -ri 'enterprise.context.connector')

| File : line | Class of citation |
|---|---|
| `INDEX.md:66` | HR Genie BTSUP-76729 note: "Enterprise-context connector replaces deprecated Store knowledge" — historical narrative, not a runtime truth-anchor |
| `mission-control/registry.json:204` (+ `.bak-reconcile-20261016T025055:588`, `.bak-20261022-deadman-fix:380`) | BTSUP-76729 closeout: re-ingest mechanism = "Enterprise context connector recipe actions"; no prod recipe carries it |
| `mission-control/events.jsonl:469` (+ `.bak-20261022-deadman-fix:469`, `.bak-reconcile-20261016T025055:469`) | same closeout event |
| `mission-control/board.html:80` | rendered closeout text |
| `cortex/attention-queue.md:7`, `cortex/questions.jsonl:920`, `cortex/dispatches.jsonl:281` | this sweep's own dispatch trail |
| `dreams/2026-10-22.md:102,131`, `dreams/bus/cortex.jsonl:758` | dream report origin |

No Genie/KB **description** in the estate cites the connector (AIRO reads: genie_list p1 50/259, knowledge_base_list p1 50/234 — descriptions clean). The dependency lives in recipes, not Genie instructions.

### 2. Local workato-kb corpus (`~/Documents/workato-kb`, data root `~/.claude/workato-kb/`)

8 deleted-upstream pages retained in `corpus/docs/en/agentic/agent-studio/connectors/enterprise-context-connector/` (hub + actions: search-documents, search-documents-advanced-filters, list-documents, list-documents-advanced-filters, metadata-filters, upsert-documents, delete-document), plus connector overview `corpus/docs/en/connectors/enterprise-context-by-workato.md`. All 8 have `manifest/docs.jsonl` rows (ETag + sha256, section Agent Studio → Connectors).

Sync semantics (`kb/docs_source.py:144`): removed pages are **reported** under `removed` in the sync summary but manifest rows and corpus files are **not deleted** — so the local RAG++ KB keeps a FROZEN snapshot: retrieval still serves the content but will cite dead docs.workato.com URLs and the pages will never update. Next sync should log all 8 URLs in its removal report.

### 3. Live estate dependency (verified read-only)

- Dev recipe [82959474 — BTSUP-76729 HR Genie KB FTO Re-ingest](https://app.workato.com/recipes/82959474) confirmed using `enterprise_context.upsert_documents` ("Enterprise context by Workato" connector) against KB kb-AYc8DXFF-rzGerR-CD. Same connector family behind collector 71498060 and freshness sentinel 82959482 (per knowledge tree; sentinel is dev-only, never promoted).
- Production: carries NO connector-based recipe (re-verified in the BTSUP-76729 closeout 2026-10-14) — nothing in prod depends on the deleted docs.

### Verdict

**No live build lost its docs truth-anchor in a breaking sense.** The Enterprise-context-connector builds are dev-only (HR Genie KB pipeline); prod is clean. Residual exposure is two-tier: (a) the local RAG++ KB now serves a frozen snapshot of 8 dead URLs — citations will 404 upstream and content silently stops evolving; (b) dev recipe 82959474 + sentinel 82959482 are built on connector actions whose only remaining documentation is that local snapshot. Knowledge-tree hits are historical narrative, not runtime anchors.

### Recommended follow-up owner

- **workato-kb sync owner (librarian / KB sync job)**: on the next docs sync, confirm the 8 URLs appear under `removed`; decide whether to pin the corpus snapshot with a dead-URL flag or let it rot silently. No action taken this run per dispatch scope.
- **Josh (decision only)**: whether the dev-only HR Genie KB pipeline needs a BTSUP-76729 follow-on note that its build-time docs are gone upstream — not a build change, just a ledger note.
