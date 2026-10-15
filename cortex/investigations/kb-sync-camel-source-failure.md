# Investigation: KB nightly sync — camel source git pull exit 1 (2026-10-13)

Investigator: cortex-session (headless), 2026-10-13 ~04:00–04:20 EDT. Read-only except two
disclosure notes in "Side effects of this investigation" below.

## Symptom

`git -C ~/.claude/workato-kb/corpus/camel/_repo pull --ff-only -q` → exit 1, failing the
source-count floor on the last two nightly syncs (bus alerts 2026-10-12T22:48:45 and
2026-10-13T00:41:51 — NOTE: bus "Z" timestamps are actually local EDT, see timeline).
Both runs logged only `non-zero exit status 1` — **stderr was not captured** by either wrapper
(`kb/camel_source.py` subprocess + `kb/sync.py` error record), so root cause had to be
reconstructed from git reflogs.

## Diagnosis: dirty working tree blocking the merge — NOT divergence, force-push, auth, or disk

Evidence chain (all from reflogs, no writes):

1. `origin/main` fetch reflog (`.git/logs/refs/remotes/origin/main`):
   - Oct 11 21:11:42 EDT — clone (`--depth 1 --filter=blob:none --sparse`) → `3edd6fd6`
   - Oct 12 **21:55:06 EDT** — `pull --ff-only -q: fast-forward` 3edd6fd6 → `a7169d7c`
     (fetch phase SUCCEEDED; the pull still failed → failure was in the merge phase)
   - Oct 13 04:00:59 EDT — my reproduction pull ff `a7169d7c` → `adb6d3bb`, SUCCESS
2. HEAD reflog: between clone and Oct 13 00:42:06 there is NO successful-pull entry — the
   21:55:06 fetch was never followed by a merge. A pull whose fetch succeeds but merge fails
   = classic **"local changes would be overwritten by merge"** refusal (exit 1).
3. Ancestry proof: `git merge-base --is-ancestor 3edd6fd6 a7169d7c` = YES (57 commits behind);
   reverse = NO. Local main NEVER had unique commits → **divergence and upstream force-push
   ruled out**. A clean tree at 21:55 would have fast-forwarded trivially (proven by my own
   pull ff'ing cleanly in the same shallow repo at 04:00).
4. Auth ruled out: public https remote, no credentials involved. Disk ruled out: 585 GiB free.
5. The dirty tree is no longer visible in camel's repo — see side effects below — but the
   mechanism is proven live in a sibling repo (next section).

### Where the dirt came from: a cross-repo link-rewrite pass dirtied the source repos

Sweeping all 20 `github_source` repos: **9 have dirty working trees right now**, and the diffs
are all the same signature — external URLs rewritten into cross-corpus relative links INSIDE
the upstream working trees, e.g.:
- `asyncapi-spec`: YAML 1.2 spec URL → `../../cloudevents-spec/cloudevents/spec.md`
- `system-design-primer`: Consul docs URL → `../../eip/index.md`

File mtimes cluster at Oct 11 03:51 EDT — the same window as the big corpus build that night
(github/mcp/jira sources stamped 03:37–03:51). An unattributed process (agent session or script
from that build window) rewrote links in the SOURCE repos instead of (or in addition to) the
extracted corpus copies. Camel's `_repo` was almost certainly dirtied the same way; the reset
below destroyed the evidence, so this specific link is inference, flagged as such.

### Unattributed recovery write at 00:42:06 EDT Oct 13

`HEAD@{2026-10-13 00:42:06}: reset: moving to origin/main` (3edd6fd6 → a7169d7c). This was NOT
the sync script (no reset logic in `kb/sync.py` or `kb/camel_source.py`) and no bus post claims
it. It came 66s after the second failed run closed and cleaned camel's tree — which is why my
04:00 pull then succeeded. A git write on KB infra with no audit trail: whoever did it should
record it (bus discipline).

## Side effects of this investigation (full disclosure)

1. My reproduction `pull --ff-only` at 04:00:59 EDT was NOT a no-op: it fast-forwarded camel
   `a7169d7c` → `adb6d3bb` (57 upstream commits, Oct 11→13). This was the single most useful
   diagnostic step (proved merge path healthy) but it did update the repo. No other git writes
   made by this session.
2. Camel's pre-reset dirty state is UNRECOVERABLE (reset discarded it) — the dirty-tree cause
   for run 1 is proven by mechanism + the azure twin, not by camel's own remaining evidence.

## Is the camel corpus (812 rows, built Oct 11) materially stale? No — marginally

- 812 manifest rows confirmed (`~/.claude/workato-kb/manifest/camel.jsonl`, 812 lines).
- Drift across the 42h gap: `git diff 3edd6fd6..a7169d7c` = 323 files changed repo-wide, but
  only **13 of 812 (1.6%) ingestable .adoc pages** changed (filtered to the INCLUDE_DIRS globs).
- Baseline: the "good" Oct 11 run itself indexed 812/841 with 29 thin/failed-conversion errors —
  the corpus was never 100% of the docs tree.
- Verdict: not material. The repo is now current; the next successful sync will fold in those
  13 pages. No urgent re-ingestion needed.

## Other sources at risk — YES, one actively failing and eight loaded springs

- **azure-architecture-center: actively failing BOTH nights with the same signature**
  (`"git failed: 1"` in both diffs JSONs), still dirty now (3 modified files) and
  **69,256 commits behind**. It is NOT in `CORE_SOURCES`, so it fails SILENTLY — the floor only
  counts core sources. Its corpus data IS materially stale (upstream churn is enormous).
- 8 more repos dirty but currently passing (their modified files haven't collided with upstream
  changes yet — collision luck, not health): asyncapi-spec, awesome-software-architecture,
  cs231n-notes, d2l-en, duckdb-web, openai-cookbook, system-design-primer (modified files) and
  noc-book-2 (untracked files variant). Any upstream commit touching a modified file = next
  nightly failure for that repo.
- webcrawl has a separate known issue (NameError, in the decision-inbox since 10-11) — out of
  scope here.

## REMEDY — PROPOSAL ONLY (no git writes, no sync triggers were made for this)

1. **Camel itself needs no fix**: repo is current and the merge path is proven working. The next
   nightly sync (or a manual re-run, Josh's call) should pass and fold in the 13 drifted pages.
2. **Clean the dirt in the 9 dirty github-source repos** — for each: `git checkout -- .`
   (modified files) and `git clean -fd` where untracked files block (noc-book-2); then for
   azure-architecture-center run its pull (it will then fast-forward the 69k backlog). These are
   discards of rewrites that never belonged in the working trees — but they ARE writes on KB
   infrastructure, so they wait for Josh's go.
3. **Find and stop the link-rewrite actor** (Oct 11 ~03:51 build window) before cleaning,
   otherwise the dirt regenerates. Rewrites belong in the extracted corpus .md copies, never in
   `_repo`/source working trees. Unattributed so far — needs the source of that build pass.
4. **Harden `_update_repo()` in `kb/camel_source.py` + `kb/github_source.py`**: these are
   disposable caches, not working repos — replace `pull --ff-only` with
   `git fetch origin && git reset --hard origin/<default>` (or pre-pull `git status --porcelain`
   + auto-discard), so a dirty tree can never wedge a nightly sync again. Also `capture_output`
   and LOG THE STDERR on failure — tonight's diagnosis cost an hour because two wrappers logged
   only an exit code.
5. **Alert on ANY source error, not just the CORE floor** — azure has been failing nightly,
   silently, since at least Oct 12 while the floor stayed green on its behalf.
6. **Record the 00:42:06 reset** — if it was your session, post the claim to the bus.

## Not verified (honest gaps)

- Camel's exact dirty-tree contents at run 1 (destroyed by the 00:42 reset) — cause inferred
  from mechanism + azure twin, not camel's own evidence.
- The identity of the 00:42:06 reset actor and of the Oct 11 link-rewrite process.
- That the next nightly sync passes — predicted from a live successful pull, not observed.
- Whether the link-rewrite pass also touched other non-git corpus sources.

## Key artifacts

- Sync driver: `~/Library/LaunchAgents/com.josh.workato-kb-sync.plist` (21:37 nightly) →
  `python -m kb.sync` in `~/Documents/workato-kb`
- Pull call sites: `kb/camel_source.py:61`, `kb/github_source.py:61` (both `check=True`, stderr lost)
- Floor logic: `kb/sync.py:31` (CORE_SOURCES) and `kb/sync.py:171-198`
- Run records: `~/.claude/workato-kb/diffs/2026-10-12.json`, `2026-10-13.json` (errors),
  `2026-10-11.json` (last clean camel run); bus: `~/.claude/knowledge/dreams/bus/workato-kb.jsonl`
