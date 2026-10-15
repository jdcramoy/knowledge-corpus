
## KB sync source-shrink — root cause (read-only investigation, 2026-10-09 09:15 EDT)

**Verdict: the "1 of 15 sources" report was not a crawl failure. It was a deliberate single-source verify run whose summary line is indistinguishable from a full nightly run. But the same night's commit `fa0447a` then clobbered `kb/sync.py` itself — the nightly launchd now runs a Jira-only script, and the multi-source orchestrator exists only in git history. The shrink is currently PERMANENT until restored.**

### Timeline (all times local EDT = Z-4)

- 2026-10-08 21:52:03 (01:52Z) — LAST healthy full sync: bus `workato-kb.jsonl` reports "3327 docs changed across 15 sources; errors: 0"; diff report `~/.claude/workato-kb/diffs/2026-10-08.json` (89KB, all steps).
- 2026-10-09 02:41–03:20 — v0.9.0 / cases-seeding commits in `~/Documents/workato-kb` (`5221a91`, `311dda0`).
- 2026-10-09 03:22:32Z — bus post "KB sync 2026-10-09: 0 docs changed across 1 sources; errors: 0" (`~/.claude/knowledge/dreams/bus/workato-kb.jsonl` line 9).
- 2026-10-09 03:22:39 EDT — commit `2a1713e` "sync: weekly (Sunday) Jira case-base refresh wired; **verified run**". Diff: +14 lines to `kb/sync.py` (adds a `jira-cases` step; orchestrator content otherwise unchanged).
- 2026-10-09 03:39:25 EDT — commit `fa0447a` "nightly jira-case refresh: skip-existing…" — **replaces the ENTIRE 152-line `kb/sync.py` orchestrator with the 65-line `jira_bulk_pull` body** (diff is `-152/+65`: full deletion of `main()`, `try_step`, all source steps, the diff-report writer, and the bus poster).
- After 03:39 — no further `sync_report` on the bus; `diffs/` still ends at `2026-10-09.json`. Working tree today: `git status` shows only `kb/digest.py` modified (the separate lens fix, uncommitted — do not lose it).

### Q1: Which loop or early-exit reduced the source list to 1?

Not a per-source exception and not crawler index state. The old orchestrator's `--sources` filter (`if wanted and name not in wanted: return` in `try_step`) skipped all steps except the newly wired `jira-cases`. Evidence:

- `~/.claude/workato-kb/diffs/2026-10-09.json` (226 bytes, written 03:22): `"results"` contains exactly one key, `"jira-cases"`; `errors: []`. A crawl failure would leave the other 14 keys present with `{"error": ...}` values.
- The bus summary computes `len(results)` — i.e. **"sources" actually means "pipeline steps executed in that invocation"** (a full run is 15 steps, but only ~8 are true sources; attachments/contextualize/index/pmi/entropy/lateral/memory-entropy are post-processing). A scoped run legitimately reports 1. `2a1713e`'s commit message calls the run a "verified run" — this was the targeted `--sources jira-cases` smoke test of the new step, posted to the shared bus in the same format as a full nightly report.
- Config (`docs-watch-sources.json`, crawler index state) is NOT involved — that belongs to the separate fleet docs-watch job (3 sources, different pipeline); the 15-source count is the step list hardcoded in the old `kb/sync.py`.

### Q2: Did a later run scan all 15?

No. The only sync_report entry on the bus after 21:52 10-08 is the single 03:22 scoped run. `diffs/` has no report after `2026-10-09.json`. Worse: none is coming — the nightly `com.josh.workato-kb-sync` launchd (21:37) runs `python -m kb.sync`, which since `fa0447a` executes ONLY the Jira-case refresh (fetches closed bugs, prints "refreshed: …", exits). It writes no diff report, no bus post, and re-indexes nothing. Corpus and index go stale silently from tonight onward.

### Q3: Does ANY script assert a healthy source count?

No. Verified:

- The old `kb/sync.py` bus block (recoverable via `git show 2a1713e^:kb/sync.py`, lines ~103-127) posts `len(results)` with no floor and no scoped/full distinction; `changed=0` + `errors=0` reads as a healthy no-op.
- The digest staleness self-assertion added 2026-10-09 (uncommitted `kb/digest.py`) checks retrieval freshness, not sync coverage — it would only fire days later, after retrieval degrades.
- No launchd agent, watchdog job, or fleet validation rule checks `sync_report` source counts or diff-report presence. The cortex caught this manually; nothing automated would have.

### Recovery pointer (NOT applied — investigation was read-only)

Restore the orchestrator from git history: `cd ~/Documents/workato-kb && git show 2a1713e^:kb/sync.py > kb/sync.py` (or `5221a91:kb/sync.py`), then re-add the `jira-cases` step from `2a1713e` so both behaviors coexist. The Jira-only body already lives correctly at `kb/jira_bulk_pull.py`. Preserve the uncommitted `kb/digest.py` lens fix when doing so. Recommend: (a) bus summary gains `"scope": "full"|"scoped"` + a step-count floor on unscoped runs (e.g. `< 8 steps` = alert), (b) the nightly job should hard-fail (nonzero exit + bus error) when `results` has fewer than the 15 expected step names.

— Investigation by cortex-dispatched agent, session 2026-10-09. Sources: bus `knowledge/dreams/bus/workato-kb.jsonl`, `~/.claude/workato-kb/diffs/2026-10-0{8,9}.json`, git log/diffs of `~/Documents/workato-kb` (commits `2a1713e`, `fa0447a`, `65e0264`), launchd plists `com.josh.workato-kb-sync` / `com.josh.fleet.docs-watch`.
