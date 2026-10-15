# workato-dev-kb — promotion readiness (2026-10-10)

## What shipped (all local, nothing on GitHub)

11 commits on `main` at `~/Documents/workato-dev-kb`:

| Commit | Content |
|---|---|
| `2bdc3ee` | Scaffold: README, config, sources/public.json (7 public sources; confluence/attachments/harness excluded by design), INDEX, memory-rules |
| `237e879` + `832773c` | Pre-push secret-scan hook (patterns + names blocklist, self-scan exclusion) |
| `c2fc0de`→`173c632` | Hardened install.sh (372 lines): kit-grade framework (tee'd logs, step tracking, EXIT-trap report, retry + failure classification, interactive fix_or_fail) + prereqs/vm/models/sync/index/fractal/smoke steps |
| `95d0823` (private repo) | pack-export.sh: 21 sensitive modules stripped, sanitizer pass, guard + idempotency verified |
| `72d325f` | verify.sh doctor (109 lines) + exported kb/ pipeline (25 modules) |
| `ca5c433`, `a5a0086`, `3af3117` | Content promotion: 6 domain playbooks (~1,400 lines) + 5 skills (~2,000 lines) + INDEX |

## Verification state

- Secret scan: whole-tree `git grep` across all 34 tracked files with every leak pattern (estate IDs, ticket keys, personal names, wiki spaces, people paths) — zero matches outside the blocklist files themselves.
- Installer entrypoints cross-checked against the real exported CLI: `sync --sources`, `indexer --force`, `fractal build`/`coverage`, `entropy score`, `search` — all exist in the exported modules; both scripts `bash -n` clean.
- Hook behavior live-proven: 5 push scenarios against a throwaway bare remote (clean allowed; recipe-URL / name / Jira-key pushes blocked).
- pack-export: two consecutive exports byte-identical; non-pack target refused; all 25 modules parse.

## End-to-end rehearsal — PASSED (exit 0, zero degraded)

Full consumer path in a sandbox HOME (clone → install.sh headless): prereqs ✓,
venv + torch ✓, models ✓, all 7 sources synced first-try (5,489 docs /
39,076 chunks embedded, entropy-scored mean 11.22 bits/word), fractal
projection 75,882 factlets, coverage audit 5,489/5,489 **AIRTIGHT**, smoke
query returned results. Sandbox cleaned (3.2GB). Note: rehearsal ran the
pre-streaming install.sh (`766711a` streaming fix landed during the run —
same command, output plumbing only).

## Remaining unverified

- The streamed model-download UX (`with_retry_stream` change) was not itself rehearsed end-to-end (low-risk: output routing only).
- `verify.sh` has not been run inside a completed sandbox install (its checks mirror rehearsed facts: AIRTIGHT seen, smoke query passed).
- First-push flow (`gh repo create` + push through the pre-push hook) unexercised — Josh-gated.

## Deliberately absent (by design)

BT Confluence corpus, harness-source mirroring, people files, all estate IDs, Jira keys, personal names. Seed claims ledger deferred to v1.1. Science scripts (predict/mood/calibration/dissent/rehearsal) stay in the agentic-kit distribution.

## Judgment calls made (Josh's review)

1. pack-export strips 21 modules (plan listed 4) — the extra 17 hardcode estate paths/credentials discovered in the live tree.
2. "Workato's otto platform" precedent references kept in 2 skills — internal platform design behavior, appropriate for an employee audience.
3. Installer sync uses per-source degraded semantics: one down source warns; all-down fails.
