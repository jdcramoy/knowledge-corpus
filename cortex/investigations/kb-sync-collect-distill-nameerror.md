# KB sync webcrawl NameError root cause — `_collect_distill` (read-only investigation, 2026-10-12)

## What failed

Two full KB syncs on 2026-10-11 failed the source-count floor with webcrawl as the
missing core source:
- Run 1: launchd `com.josh.workato-kb-sync` (21:37 local start), report written
  22:47:44 (bus 22:47:46Z-style ts). Errors: `webcrawl: name '_collect_distill' is
  not defined` PLUS `fractal: database is locked` and `lateral: database is locked`.
- Run 2: manual re-run, report at `~/.claude/workato-kb/diffs/2026-10-11.json`
  (mtime 22:55). Errors: webcrawl NameError ONLY — no locks.

Run 1's report survives only in `~/.claude/workato-kb/sync.log` (~line 3382/3537);
run 2 overwrote the on-disk report file. Evidence: bus log
`~/.claude/knowledge/dreams/bus/workato-kb.jsonl` (last two sync_alert entries).

## (a) Where it's called vs defined

Single file: `~/Documents/workato-kb/kb/html_source.py`.
- Call: line 217, inside `_collect()` — `if cfg.get("distill_repos"): return
  _collect_distill(cfg["max_pages"])`. Reached only for the `distill` SITES entry
  (`"distill": {"distill_repos": True, "max_pages": 90}`), added in wave 3 2026-10-11.
- Def: line 258, `_collect_distill(max_pages)` — walks the distillpub org's
  post--* repos via the GitHub API.
- Exactly one call site, exactly one def; nothing else in the repo references the
  name (grep across kb/*.py, scripts/). Chain: `sync()` (line ~286, dispatched by
  `kb/sync.py:108 try_step("webcrawl", html_source.sync)`) → `_collect()` →
  `_collect_distill()`.

## (b) The fix and its state

NameError at runtime means the executing module had the call but NOT the def — a
wave-3 edit landed the call in `_collect` before the helper def existed. The file
is git-untracked (no `git log` entries, no committed version to diff against), so
the exact pre-fix text is unrecoverable, but the timeline pins it:
- Both failing runs predate the current file: `html_source.py` mtime is
  2026-10-11 23:02:40 local, seven minutes after run 2's 22:55 report.
- The `__pycache__/html_source.cpython-312/-314.pyc` files regenerated at
  23:02:46/41 — an import immediately followed the edit (a verification import).
- Current file verified sound by AST parse: both `_collect` and `_collect_distill`
  defined, `import json` present (the helper needs `json.load` — a second latent
  NameError if missing — it is present).

Conclusion: the fix (adding the def, and the json import) was already applied at
23:02:40 on 2026-10-11, post-failures, in the working tree. It is uncommitted and
UNVERIFIED by a live sync — no run has executed since the fix. Triage card
kb-sync-webcrawl-nameerror-floor stays open until a live webcrawl step passes:
`cd ~/Documents/workato-kb && .venv/bin/python -m kb.sync --sources webcrawl`
(read-only investigation; NOT run per scope).

## (c) Entrypoint coverage

Three entrypoints, one code path — the single def fixes all of them:
1. `python -m kb.sync` full (launchd, nightly 21:37 local).
2. `python -m kb.sync --sources webcrawl` (scoped; `sync.py` filters try_step).
3. `python -m kb.html_source` (the module's own `__main__` block).
All import the same `kb.html_source` module; no duplicate copy of the file exists
anywhere on the runtime path (find over the repo + venv: only one html_source.py;
launchd WorkingDirectory is the repo, venv python resolves `kb` from it).

## (d) Relationship between the locks and the NameError

Independent of the NameError; partly transient.
- `fractal: database is locked`: `fractal.py:_connect()` uses bare
  `sqlite3.connect(FACTLET_DB)` — default 5 s busy timeout, no WAL mode — against
  `DATA_ROOT/index/fractal.db`. The ALWAYS-RUNNING `kb.daemon` (`-m kb.daemon`,
  up since Friday per ps) calls `kb.fractal.zoom`, which opens the same DB. Any
  daemon-side zoom holding fractal.db >5 s during the sync's fractal step (which
  runs after ~70 min of index building, ~22:45) produces exactly this error.
- `lateral: database is locked`: `lateral.py` uses `indexer.get_db` — the same
  index sqlite the indexer step just wrote in the same sync; contention with an
  uncommitted/held write txn or a concurrent reader.
- Run 2 (8 min later, fast — everything etag-cached) had NO lock errors, so the
  locks were transient contention, not a broken DB. Possible overlap of run 2's
  start with run 1's tail cannot be confirmed (no shell-history trail; run 2's
  stdout went to no log), so the two runs racing each other can't be ruled out —
  but either way the locks did not recur and share no cause with the NameError.
- Structural risk worth a fix ticket (not done — read-only): bump
  `sqlite3.connect(..., timeout=30)` + `PRAGMA journal_mode=WAL` in
  `fractal.py:_connect()` and confirm indexer/lateral connections commit+close
  before downstream steps; and consider a daemon-side read-only URI connect.
  Related open card: drift-gate-kb-lock.

## Answers to the four questions, compressed

(a) Called at `kb/html_source.py:217` in `_collect`, defined at :258 same file;
    wave-3 runtime had the call without the def.
(b) Missing def (plus json import) — already added in the working tree at
    23:02:40 2026-10-11, after both failures; uncommitted; unverified by live run.
(c) Three entrypoints (full sync, --sources webcrawl, module __main__), all share
    the one module — no second copy, one fix covers all.
(d) Independent causes. Locks = sqlite contention (daemon holds fractal.db with a
    5 s-timeout connect; lateral contends on the index DB), transient, absent in
    run 2, unrelated to the NameError.

Not verified: (1) the fix has never run live — the proposed verification is the
scoped `--sources webcrawl` run; (2) run 2's exact start time / trigger (manual,
unlogged); (3) the pre-fix file content (git-untracked, unrecoverable).
