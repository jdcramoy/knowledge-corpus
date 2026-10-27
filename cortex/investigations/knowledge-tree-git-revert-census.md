# Knowledge-tree git revert census — READ-ONLY investigation (2026-10-16)

Dispatched: headless census agent, 2026-10-16 ~03:30 EDT. READ-ONLY — no git state ops run,
nothing deleted. Evidence base: brain-gardener sweep 2026-10-16T03:21Z (bash `cat >>` appends to
jira-triage/runs.jsonl, last-sweep.txt, and FTR memory vanished; Write-tool files and git commits
survived).

## Verdict (one line)

**The reverter is `git filter-repo --force` history rewrites run by an interactive Claude session
(workbench cwd, session b172d420, Oct 15 10:00-23:43) during its two "untrack personal content"
passes — filter-repo finalizes with a working-tree hard reset, which discards uncommitted changes
to TRACKED files while leaving untracked (new/Write-tool) files intact.**

## Candidate table

| # | Candidate | Where | Discard-capable git ops | Verdict |
|---|-----------|-------|--------------------------|---------|
| 1 | Claude session b172d420 (cwd ~/Documents/workbench), "untrack personal identity content" + "untrack slack-posts" | transcript `~/.claude/projects/-Users-<user>-Documents-workbench/b172d420-c6e2-4818-baf5-30f74c32249d.jsonl` | `git filter-repo --force --invert-paths --path people/ --path domains/voice-reps/ --path domains/josh-voice-corpus.md ...` (15:19 untrack) + slack-posts pass (18:07) | **CONFIRMED reverter.** filter-repo refuses a dirty tree unless `--force`; `--force` was used, so it ran OVER uncommitted changes and its finalization hard-resets the working tree to the rewritten HEAD. Tracked-file bash appends reverted; untracked Write-tool files survive; committed content survives. Matches every symptom. |
| 2 | `git filter-repo` runs themselves | `.git/filter-repo/` markers (commit-map 123 commits, already_ran, mtimes Oct 15 18:07) | filter-repo finalization = working-tree hard reset | Mechanism of candidate #1. Also **destroyed the reflog** (see fingerprints) and rewrote all 121 commits, so Oct 14-15 hard-reset fingerprints are unrecoverable locally. |
| 3 | `scripts/state_hasher.py restore` | `~/.claude/knowledge/scripts/state_hasher.py:~97-105` | `git add -A` + `git reset --hard <head>` on knowledge + workato-kb repos | **Latent hazard, NOT the observed reverter.** Only caller that invokes `snap` is the antigen fleet job; `restore` is manual-only, no scheduled or transcript hit for Oct 14-15. One invocation away from the same loss class. |
| 4 | `scripts/harness-backup.sh` (23:33 nightly, `auto_push`) | `~/.claude/knowledge/scripts/harness-backup.sh:101` | `git -C "$repo" reset -q` on token-scan refusal | **SAFE.** Mixed `reset -q` only unstages — working tree untouched. All other paths `add -A` + commit (preserve). Not the reverter; it's the opposite (nightly preservation). |
| 5 | launchd fleet jobs (52 plists) | `~/Library/LaunchAgents/com.josh.*` | none | All job bodies go through `run-job.sh` → claude prompt or zero-LLM script. Grep of all jobs + scripts for checkout/reset/clean/restore/stash/filter: no discarding ops. |
| 6 | `scripts/restore-drill.py` (com.josh.fleet.restore-drill) | scheduled drill | none against the live tree — clones the REMOTE backup into `/tmp/restore-drill/` only | Clean. Named "restore" but never touches the live repo. |
| 7 | Hooks (manifest-guard, redteam-guard, announce-stop-guard, known-broken-tools, jira-comment-guard, lint-changed, session-drop-guard, squad-handoff) | `~/.claude/hooks/` + settings.json PostToolUse `lint-changed.py` | none | lint-changed runs linters only (subprocess on a single file). No git state ops in any hook. |
| 8 | kb-daemon, harness-sync, workato-kb jobs, crontab | plists / `crontab -l` (empty) | none | No git invocations against knowledge. |
| 9 | Interactive sessions of the `git checkout -f` class (prior incident) | `scripts/voices.json:8` — 2026-10-11: 49 decided triage/proposal decisions destroyed by `git checkout -f` over a dirty tree | `checkout -f` | Same loss class, earlier occurrence — establishes this as a RECURRING harness failure mode, not a one-off. |

## Reflog fingerprint evidence

- `git -C ~/.claude/knowledge reflog -30` → **exactly 1 entry**: `82d6867 commit: knowledge deposit: … history-rewrite record` (2026-10-15 18:08:40 EDT). A repo with 121 commits should have a long reflog.
- `.git/logs/HEAD` and `.git/logs/refs/heads/main` are each 253 bytes, mtime Oct 15 18:08 — reflog was truncated/rebuilt by the filter-repo run(s).
- `.git/filter-repo/` present (already_ran, changed-refs, commit-map [123 entries], first-changed-commits, ref-map, suboptimal-issues), all mtimes **Oct 15 18:07**.
- `.git/ORIG_HEAD` = `d8173e8` (pre-"history-rewrite record" HEAD).
- Consequence: **the Oct 14-15 reset fingerprints are destroyed locally** — the rewriter erased the very evidence trail. The single-entry reflog is itself the fingerprint of the history rewrite.
- RECOVERY PATH (not exercised — read-only): the vanished Oct 14 rows were committed by the nightly `auto_push` ("nightly auto-backup 2026-10-14 23:33") and pushed to `origin` (github.com/Workato-All/josh-knowledge) BEFORE the rewrites. The pre-rewrite `runs.jsonl` / `last-sweep.txt` blobs are likely recoverable from that remote's history.

## Mechanism (why the symptom pattern matches exactly)

`git filter-repo --force` on a non-bare repo: rewrites all commits → resets refs → **hard-resets the working tree** to the rewritten HEAD.
- Tracked files with uncommitted bash appends (`cat >>` into jira-triage/runs.jsonl, last-sweep.txt, FTR memory): content reverted to the rewritten HEAD → **appends vanish**. ✓
- New files created by the Write tool (typically untracked): `reset --hard` does not remove untracked files → **survive**. ✓
- Committed content: survives (and filter-repo only removed the explicitly untracked personal paths). ✓
- Working tree was DIRTY at rewrite time (filter-repo refuses without `--force`; `--force` was used) → the dirt was exactly what got discarded. ✓

## Ranked conclusion

1. **Most likely reverter (high confidence): the Oct 15 `git filter-repo --force` untrack rewrites** run by session b172d420 (workbench cwd). Two passes (15:19 identity, 18:07 slack-posts) over a dirty tree, each ending in a working-tree hard reset. The gardener's "Oct 14-15" loss window is partially explained; if Oct 14 rows vanished too, suspect an additional earlier rewrite or a same-class `checkout -f` from a session (the 2026-10-11 precedent) — pre-rewrite remote history can settle it.
2. **Second: state_hasher.py restore** — capable of the identical loss, no evidence of Oct 14-15 invocation, but one manual run away from recurrence.
3. All launchd/cron/hook/backup automation is CLEAN — the reverter is a session-driven history rewrite, not scheduled automation.

## Gating fix (recommended)

1. **PreToolUse guard (tool-layer, per the known-broken-tools.py pattern):** deny `git filter-repo`, `git filter-branch`, `git reset --hard`, `git checkout -- .`/`-f`, `git clean -f`, `git restore .` when the target repo is `~/.claude/knowledge` unless the command carries an explicit Josh-approval marker. Sessions cannot be trusted to self-police this (proven twice now).
2. **Dirty-tree pre-flight for ANY history rewrite:** mandatory `git add -A && git commit -m "pre-rewrite snapshot"` (or `state_hasher.py snap`) immediately before filter-repo/filter-branch — script the untrack operation so `--force` over a dirty tree is structurally impossible.
3. **Never run history rewrites during active write windows:** knowledge tree has ~30 fleet jobs + parallel sessions appending all day; rewrites belong in a quiet window with the tree verified clean.
4. **Recovery:** pull the pre-rewrite `runs.jsonl`/`last-sweep.txt` from `origin/main` history (github.com/Workato-All/josh-knowledge, commit "nightly auto-backup 2026-10-14 23:33") and reconcile against the live files to restore the lost rows.

## Unverified

- Whether an ADDITIONAL rewrite/reset ran on Oct 14 (local evidence destroyed by the Oct 15 rewrites; remote history would settle it — not fetched, read-only scope).
- Live confirmation that the vanished rows exist on the remote backup (recovery step 4 not executed).
- Session b172d420's authorship context (Josh-directed task vs autonomous privacy pass) — transcript exists but was not read in full.
