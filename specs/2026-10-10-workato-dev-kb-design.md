# Workato Dev KB — design spec (2026-10-10)

Status: DRAFT — design presented to Josh, awaiting his approval. Two open calls
flagged in Open Questions. Implementation (repo creation, content promotion,
first push) is Josh-gated.

## Problem

Josh's harness value is more than half content: the mined-and-curated Workato
knowledge (RAG++ corpus + domain playbooks + trap catalogs + verified claims).
The shareable kit repo (`Workato-All/workato-agentic-kit`) ships mechanics
(mods, agents, skills scaffolds) with an EMPTY knowledge layer. Other Workato
employee developers have no path to the experience layer.

Goal: a pre-baked, installable internal Workato development knowledge pack —
public-source corpus via the RAG++ pipeline plus curated generic-form
playbooks — that other Workato developers install in one command, while none
of Josh's private content (people files, estate IDs, BT Confluence, personal
queues) can reach GitHub.

## Decisions locked (Josh, 2026-10-10)

| Call | Decision |
|---|---|
| Distribution vehicle | Separate content repo pulled in by kit installer; content clean by construction (promotion-only, no auto-sync from private tree) |
| BT Confluence corpus (3,352 pages) | OUT for v1 — LOCAL-ONLY rule stays intact; deferred tier pending BT team blessing |
| Experience-layer sharing | Curated promotion, rewritten in generic form at promotion time (no automated sanitize-and-ship) |
| Consumer delivery | Full RAG++ stack — pipeline code + install/verify + first public-source sync (escalated past the markdown-only recommendation) |
| Fractal layer (Josh, mid-review 2026-10-10) | IN — the pack ships the full fractal memory layer wired into the RAG++ stack, not just BM25+dense retrieval |

## The artifact

Two repos, two jobs, one boundary:

- **`Workato-All/workato-dev-kb`** (new, internal-to-Workato): the pack
  consumers install. Contains only content explicitly authored or promoted
  into it.
- **`workato-kb`** (Josh's private upstream, unchanged in behavior): gains a
  `pack-export` step that strips Confluence + harness sources and copies the
  generic pipeline code into the dev-kb repo.

## Repo layout

```
workato-dev-kb/
├── README.md              # what this is + 3-command quickstart
├── install.sh             # clone → venv → deps + models → first public-source sync →
│                          #   build fractal projection → verify
├── verify.sh              # post-install self-check: index built, kb search returns hits,
│                          #   `kb fractal coverage` reads AIRTIGHT, skill loads
├── kb/                    # RAG++ pipeline — pack-exported, confluence/harness sources REMOVED
│                          #   includes fractal.py: factlet schema at every scale,
│                          #   zoom retrieval, coverage auditor
├── knowledge/
│   ├── INDEX.md           # router (knowledge-tree pattern)
│   ├── domains/           # generic-form playbooks (promotion-rewritten) —
│   │                      #   fractal-compliant: one file one topic, ## sections
│   │                      #   written AS queries, INDEX line per file
│   ├── memory-rules.md    # the fractal memory-authoring rulebook (from kit kb-pipeline INSTALL.md)
│   └── claims.jsonl       # seed claim ledger — verified platform-behavior claims only
├── skills/                # sanitized skill pack: airo-mcp-playbook, workato-kb, verify, diff-reading
└── sources/               # sync config: PUBLIC sources only
                           # (docs / changelog / blog / inspiration / github / eip / claude)
```

## Privacy guarantee — structural, not procedural

1. **No inbound sync.** Content enters only by promotion (authored in-repo, or
   a private file rewritten once at promotion). No script copies from
   `~/.claude` into this repo, ever.
2. **The export filter.** The only automated path (`pack-export`, living in
   the private KB repo) copies code and strips the two sensitive sources.
   Code cannot carry estate data.
3. **Allowlist review.** Every promotion is a PR Josh eyeballs before push —
   same read-back discipline as harness-docs publishing.
4. **Pre-push secret-scan hook** in dev-kb, tuned to leak classes: workspace /
   recipe / table IDs, `*.workato.com` URLs carrying IDs, personal names,
   Jira keys.

Never-ship list: people files, workspace/recipe/table IDs, BT Confluence
content, triage queues, slack-posts.jsonl, personal claims, estate topology,
Josh's schedules/agent fleet.

## Consumer experience

```bash
git clone git@github.com:Workato-All/workato-dev-kb.git && cd workato-dev-kb
./install.sh     # venv, deps, bge models, first sync of public sources (~10 min)
kb "how do I handle pagination in a custom connector"   # cited RAG answers
```

Consumers get: cited RAG answers over public Workato docs + curated playbooks,
trap-catalog skills loading in Claude sessions, INDEX.md router for direct
reads, seed claims so their agents inherit verified platform behavior. The
fractal layer gives them self-similar memory over the whole corpus: `kb zoom`
drills topic → file → section → chunk, the coverage auditor proves nothing is
unindexed, and the promoted content is authored to the factlet rules so zoom
actually lands on it. Their nightly sync hits public endpoints only — no BT
access, nothing of Josh's involved.

Privacy note on fractal: the factlet projection (like the vector index) is
built consumer-side from THEIR corpus and the pack's knowledge tree at
install/sync time. Nothing ships prebuilt, so the pack carries no Josh-derived
index state at all.

The five dreaming-team science scripts (predict.py, mood.py, calibration.py,
dissent_ledger.py, rehearsal.py) stay in the kit repo's knowledge/scripts
distribution as today — the dev-kb pack depends on the kit for them rather
than duplicating; fractal.py itself ships in the pack's kb/ because zoom
retrieval is part of the core read path.

## Out of scope for v1

Plugin/marketplace packaging, auto-update channel beyond `git pull`,
Confluence tier, Obsidian layer, contribution/intake pipeline from other
developers. One-way publishing first; add intake only if adopted.

## Build shape (swarmable, disjoint file ownership)

- (a) `pack-export` script + private-repo side (owner: workato-kb repo)
- (b) dev-kb repo scaffold + install.sh + verify.sh + secret-scan hook
- (c) content promotion: ~6-8 domain files + ~4 skills rewritten generic
- (d) seed claims extraction (platform-behavior claims, verified, de-identified)

## Open questions (Josh's calls)

1. **Repo name** — APPROVED: `workato-dev-kb` (Josh, 2026-10-10).
2. **Seed claims** — DEFERRED TO v1.1 (Josh approved my recommendation):
   content promotion (a)-(c) ships v1; claims get their own generic-safe
   verification pass and land in v1.1.
3. **Design approval** — APPROVED 2026-10-10. Remaining gates: final content
   list before promotion starts, and the first push.

## Install hardening (Josh requirement, 2026-10-10)

Same level as the kit's install.sh (461-line hardened installer) — a smooth,
dynamic onboarding that sticks with the user through errors and friction:

**Carried over from the kit (the patterns to reuse):**
- `set -euo pipefail`; tee'd timestamped log (echoed up front + on failure)
- Step pipeline tracking: STEPS / CURRENT_STEP / COMPLETED / DEGRADED; EXIT
  trap reports the failed step, what completed, what did not, degraded items
  each with the exact fix command, log path, and "safe to re-run" resume line
- ERR trap with line number + current step
- `with_retry` bounded retries + `classify_failure` (network / permissions /
  auth / tool-version hints grepped from captured output)
- `with_retry_stream` for interactive fixers (things that prompt)
- `fix_or_fail`: interactive offers the one-command fix [Y/n] and RE-VERIFIES
  after; headless fails fast printing the exact command to run
- brew as the fix engine; `ensure` re-checks post-fix
- Idempotency contract: re-run is always safe, no rollback needed

**KB-specific additions the kit didn't need:**
- `python3.12` venv creation with existing-venv repair (stale/wrong-python
  venvs are the top KB-onboarding failure; delete-and-recreate offer)
- Model download step (bge-base + bge-reranker-base) with resume-on-retry and
  a disk-space preflight before the ~2GB fetch
- First sync as its own resilient step: per-source progress, per-source
  failure is DEGRADED (not fatal) as long as ≥1 source succeeds — a source
  being down must not kill an otherwise-good install
- Index + fractal projection build with the coverage auditor as the gate:
  `kb fractal coverage` must read AIRTIGHT or the run ends DEGRADED with the
  specific audit line printed
- `kb` smoke query at the end: one real search that must return hits, so the
  user's first command is proven working before the installer claims success
- Onboarding shim like the kit's: no config → interactive questions (install
  dir, which sources to enable); headless → example config + clear note

## Build shape (swarmable, disjoint file ownership) — FINAL

- (a) `pack-export` script + private-repo side (owner: workato-kb repo)
- (b) dev-kb repo scaffold + hardened install.sh + verify.sh + secret-scan hook
- (c) content promotion: ~6-8 domain files + ~4 skills rewritten generic
      (final list is Josh's gate before this starts)
- (d) seed claims extraction — **v1.1, not v1**
