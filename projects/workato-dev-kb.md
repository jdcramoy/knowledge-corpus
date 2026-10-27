# Project: workato-dev-kb

The shareable internal knowledge pack for Workato employee developers — Josh's
idea (2026-10-10): package the experience layer (curated playbooks + RAG++ +
fractal) that makes the harness valuable, separate from the mechanics the
`workato-agentic-kit` already ships.

## State (2026-10-15): LIVE on the org + personal-copy staged

- **Pack repo:** `Workato-All/workato-dev-kb` (INTERNAL) —
  https://github.com/Workato-All/workato-dev-kb. Was already on the org
  (first push happened between 10-10 and 10-15, unrecorded); refreshed
  2026-10-15 with the 10-10→10-15 pipeline changes (wave-5 sources,
  camel/atlassian/rss/workday/html, indexer self-heal, Slack docs). Commit
  866c216 pushed, main in sync.
- **Private-repo bridge hardened (2026-10-15):** pack-export.sh now strips
  confluence + stripped-module imports STRUCTURALLY (drop_core_source /
  import_drop — new public sources flow through, no literal-anchor churn),
  excludes `*.bak-*` from the rsync, scrubs the new Josh-mention comments,
  drops the obsolete indexer dict patch (upstream went manifest-driven
  10-10-11), and scrubs the ingest.py→kb.attachments docstring pointer.
  Export gates green: leak-grep clean, py_compile clean.
- **Manual sensitive-string sweep before push (replaces the designed but
  never-installed pre-push hook):** only template `app.workato.com/recipes/<id>`
  placeholders hit. NOTE: the pre-push secret-scan hook is NOT installed in
  the pack repo's .git/hooks — installing it is still open.
- **Personal copies staged (2026-10-15):** mirror clones at
  `~/Documents/workato-dev-kb.git` and `~/Documents/workato-agentic-kit.git`,
  ready for `git push --mirror` to a personal GitHub once Josh runs
  `gh auth login` with the personal account. Drag-and-drop web upload also
  viable for the kit (files only, minus dotfiles).
- **Raw brain + BT Confluence stay OUT** — the pack is the shareable
  artifact; josh-knowledge (the raw brain) is org-internal and must not be
  shared externally without a sanitization pass.

## Decisions locked

- Separate content repo (promotion-only, no auto-sync from `~/.claude`);
  BT Confluence OUT (deferred tier pending BT blessing); full RAG++ + fractal
  in; seed claims ledger v1.1; streamed model-download UX (Josh, rehearsal
  finding).

## Next steps

1. Josh's go → `gh repo create Workato-All/workato-dev-kb --internal` + first
   push (hook will scan it live for the first time).
2. v1.1: seed claims ledger (generic-safe verification pass per claim); kit
   install.sh channel offering the pack; `SOURCES_ENABLED` upstream switch in
   private sync.py to delete the sanitizer patches; consider config-gating the
   consumer's local-memory ingest tier in exported fractal.py.
3. Josh-gated follow-on: BT Confluence tier if BT approves; contribution
   intake if adopted.

## --with-corpus installer flag (2026-10-19, commit 98fda21)

`install.sh --with-corpus` clones Workato-All/knowledge-corpus into
~/.claude/knowledge before the fractal build (step order: ... index, corpus,
fractal, smoke). Never overwrites an existing tree: corpus-origin clones get
git pull --ff-only; personal trees left untouched with a DEGRADED note.
Plain git clone first, gh repo clone fallback (gh keychain auth). No access
(internal-only repo) degrades — public mirror users get the plain install.
Verified: skip/clone/gh-fallback/personal-tree/stray-dir branches tested
against the live repo; both org + mirror repos read back at 98fda21.
Unverified live: the git pull --ff-only update path (needs teammate git auth;
detection logic verified). A teammate's first real `--with-corpus` run is the
final confirmation.
