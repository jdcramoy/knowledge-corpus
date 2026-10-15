# Investigation: actor of the unattributed link-rewrite pass (9/20 KB github repos)

Dispatched: 2026-10-13 (cortex, read-only). Window: Oct 11 2026, 03:37-03:51 EDT.

## Verdict

**The actor is NOT a Claude session. It is the nightly KB sync pipeline itself: launchd job
`com.josh.workato-kb-sync` running `python -m kb.sync` (~/Documents/workato-kb), whose mandatory
`links` post-processing step — `kb/links.py`, `links.normalize` — rewrote resolvable website-style
links into cross-corpus relative `.md` links, in place, in the source repos.**

No session, human, or agent hand-edited anything. The working-tree "dirt" is a designed,
uncommitted side effect of sync writing into the git checkouts without committing. This is a
design gap (sync should not dirty source checkouts, or should commit/checkout after), not a rogue
actor.

## Evidence chain

1. **No session was live in the window.** Grepped every transcript in `~/.claude/projects/` for
   timestamps `2026-10-11T03:33`–`T03:59`: exactly one match,
   `-Users-<user>-Documents-workbench/2679658d-9120-4d94-8f6e-085c7f112304.jsonl` — the nightly
   cron-host session (docs-watch at 03:01, brain-gardener heartbeat 03:04, watchdog spawn 03:43,
   watchdog heartbeat 03:47). It never touched the corpus, `kb.links`, or `kb.sync`. The two
   transcripts with 03:31 mtimes (`22ac26b6`, `b3ac18d0`) contain only Oct 10 entries — mtime was a
   later index write, a red herring.

2. **The build ledger rows 03:37-03:51** (`~/.claude/knowledge/build-ledger.jsonl`) are Workato
   recipe diagnostics (`wt recipes get 82727069/82862205`), the orca-ledger check, and dream-report
   writes — from the same cron-host session. Nothing corpus-related.

3. **The rewrite mechanism is a shipped KB tool.** `~/Documents/workato-kb/kb/links.py`:
   "Corpus link normalization: turn website-style links into vault-resolvable ones... rewritten to
   RELATIVE .md links when (and only when) the target actually exists in the corpus."
   `_rel()` at links.py:49 is `os.path.relpath(dst, src.parent)` — which produces exactly the
   observed cross-corpus patterns. `kb/bridges.py:65-71` computes the same `../` depth for vault
   placement.

4. **The pipeline invokes it automatically.** `kb/sync.py:115-118`: "link normalization: website-
   style .html / absolute docs links -> relative .md links... MUST run after every source step or
   sources re-emit raw links; runs before index build" → `try_step("links", links.normalize)`.
   Also `kb/ingest.py:48` (`try_step("links", links.normalize)`).

5. **The dirty repos and window match one sync run exactly.** `~/.claude/workato-kb/sync.log`
   records a full-scope run (source list starting at log line 2918, ending in the summary JSON
   dated `2026-10-11`): sources claude → temporal → n8n → prefect → restate → mcp → rss →
   webcrawl → camel → confluence → harness → attachments → **`[sync] links` (line 2996)** →
   jira-cases → hubs → contextualize → index → funnel → edges → pmi → entropy → fractal.
   Corpus directory mtimes (Oct 11 03:37 claude/mcp/prefect/restate, 03:39 dbt, 03:51 jira-bugs)
   match the source sweep order and window.
   
6. **Dirty repos sampled — content and mtime confirm.** 9 of 20 `corpus/github/*` checkouts have
   dirty trees: asyncapi-spec (1), awesome-software-architecture (19), azure-architecture-center
   (30), cs231n-notes (4), d2l-en (9), duckdb-web (92), noc-book-2 (19), openai-cookbook (6),
   system-design-primer (4). Sampled diffs contain exactly `](../../../../../eip/index.md)`,
   `](../../../../azure-architecture-center/docs/patterns/idempotent-consumer.md)`,
   `](../../../../../docs/en/connectors/oracle/introduction.md)` — pure `os.path.relpath` outputs
   to sibling-corpus targets. Dirty-file mtimes: Oct 11 03:51:13, the window tail.

7. **Why 03:37 and not 21:37.** The launchd job `com.josh.workato-kb-sync`
   (`~/Library/LaunchAgents/com.josh.workato-kb-sync.plist`) is scheduled `StartCalendarInterval`
   Hour 21, Minute 37 — same :37 as the observed mtimes, 6 hours earlier. macOS launchd fires a
   missed StartCalendarInterval once at next wake. `pmset -g log` (rotated past Oct 11) shows a
   wake request scheduled for `wakeAt=2026-10-11 01:31:29`, confirming the machine was asleep
   overnight. Best-supported reconstruction: the Mac missed the 21:37 slot; launchd coalesced and
   ran sync at the machine's ~03:37 wake. (Alternative: a manual `python -m kb.sync` at 03:37 —
   but no shell/session trace of one was found, and the :37 alignment favors the scheduled job.)

## What would fully confirm the wake hypothesis

- `pmset -g log | grep "2026-10-11 03:3"` for `Wake from` (log has rotated — check Time Machine
  backup or `log show --predicate 'process == "powerd"'` if the unified log retains Oct 11).
- Or a corroboration: any other 21:37-scheduled side effect that also ran at 03:37 that night.

## Bottom line for remediation (NOT done — read-only dispatch)

Nothing needs hunting or rolling back. The decision for Josh: KB sync should either commit its
rewrites in the source checkouts (e.g. `git commit -m "kb links normalize <date>"`), or copy
sources into the corpus rather than rewriting checkouts in place. Until then, every sync after an
upstream change will re-dirty these trees by design.

*Nothing was modified during this investigation — reads, grep, `git status`/`git diff` only. No
repos cleaned.*
