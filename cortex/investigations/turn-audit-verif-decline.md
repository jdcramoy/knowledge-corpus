# Turn-audit verification-rate decline — investigation (2026-10-22)

**Verdict: the 13%→9% "verif" decline is a metric artifact, not a discipline decline. Real
verification activity is FLAT at 1.71% of turns in both windows. The entire drop comes from one
false-positive class in the `verif` definition, concentrated in one workflow (the workato-kb
corpus-building sessions of Oct 9–14) that left the 7-day mtime window.**

## 1. The script and its definition of 'verif'

- Script: `~/.claude/knowledge/scripts/turn-audit.py` (192 lines, built 2026-10-12, zero-LLM,
  runs in the fleet; also referenced from `~/.local/bin/fleet/jobs/` heartbeat — jobs file
  `turn-audit` posts to gossip bus + heartbeat.jsonl).
- Output: `~/.claude/knowledge/reports/turn-audit-latest.md`, trend rows appended to
  `~/.claude/knowledge/reports/turn-audit-trend.jsonl`, bus post to `dreams/bus/turn-audit.jsonl`.
- **Definition of `verif`** (turn-audit.py:40-41, 55-58): a Bash tool call is VERIFICATION if its
  command matches `VERIFY_SIG = /unittest|pytest|\btest\b|job_get|job handle|trace|verify|
  read.?back|kb_search|kb\b/i`. Anything that isn't Bash (MCP tools, Read/Grep/etc.) is counted
  PRODUCTIVE — only Bash commands can earn verification credit. `verif_rate = verification /
  all classified turns`. Blind retries after errors = WASTE (the 3.3% figure).

## 2. Official trend (turn-audit-trend.jsonl, 7-day windows by file mtime)

| Run (UTC) | sessions | turns | waste% | verif% |
|---|---|---|---|---|
| Oct 12 07:38 | 188 | 11,029 | 3.12 | 12.8 |
| Oct 12 07:41 | 188 | 11,043 | 3.12 | 12.79 |
| Oct 13 01:33 | 232 | 12,587 | 3.34 | 12.6 |
| Oct 20 07:07 | 338 | 14,073 | 3.31 | **9.15** |

## 3. Root cause: `kb\b` false positives dominate the metric

Re-running the script's exact classification (read-only, over the same corpus
`-Users-<user>-Documents-workbench`), splitting verification credit into the `kb\b|kb_search`
class vs every other alternative:

| Window (mtime) | turns | verif% | of which kb-noise | of which real verify |
|---|---|---|---|---|
| Oct 8–15 | 15,257 | 11.40% | **9.69%** (1,479 cmds) | 1.71% (261) |
| Oct 15–22 | 11,308 | 8.14% | **6.44%** (728 cmds) | **1.71% (193)** |

The regex `kb\b` matches ANY command containing the word "kb" — and the dominant match is not
knowledge-base verification at all, it is **`cd ~/Documents/workato-kb`** (616 of 1,740
verification credits = 35% in the prior window), plus `cat ~/.claude/knowledge/kb-digests/...`,
greps inside kb repos, etc. A `cd` into a directory whose name ends in `-kb` earns the same
"verification (PROTECTED)" credit as a pytest run.

### Why it collapsed: one workflow left the window

The prior window contained five KB-corpus mega-sessions (mtimes Oct 9–14) with 38–59% verif
each, led by session `3896e945` — 1,055 turns, 446 verif (42%): Josh's "deep understanding of
Workato architecture" corpus-building session (`d15587bc`, `f38d9d11`, `a39f8b41`, `b3ac18d0`
similar: workato-kb doc ingestion / digest work). Those sessions' hundreds of `cd workato-kb` /
kb-path commands were the majority of the "verification" numerator. In the last 7 days that
workflow did not recur at scale (biggest verif session: `4219edfb`, 152 verif, a genuinely
test-heavy Workato session), so the kb-noise numerator halved (1,479→728) while the turn
denominator stayed large.

Secondary artifact: verification credit is Bash-only — MCP tool calls (AIRO `job_get`,
`workato-kb__kb_search`) count as productive, so any wt-CLI→MCP migration depresses the metric
further. Not the driver this time, but it means the metric is fragile in the same direction.

## 4. Is the decline clustered or broad?

**Clustered — one workflow (KB-corpus maintenance/architecture-docs building), one regex
alternative (`kb\b`).** Per-session breakdown shows the decline is fully explained by the
absence of the Oct 9–14 corpus mega-sessions; the broad population of ordinary sessions did not
get less "verifying" (real-verify share identical at 1.71%). Waste (3.3%) is genuinely flat —
that part of the bus post is real and not part of the decline. Error causes shifted slightly
(bash-exit 570, permission-denied 115, stale-schema 11) but are steady state.

## 5. Recommendations (no changes made — read-only investigation)

1. **Fix the metric** in `turn-audit.py` VERIFY_SIG: drop bare `kb\b` (and probably `\btest\b`
   matching `cd ...workato-kb`-style paths); require action-shaped matches (pytest/unittest/
   `wt ... test`/job trace verification), or require the command to actually run something
   (`kb ` as a command head is fine; `cd .*kb` is not).
2. **Report headline honestly**: true verification discipline is ~1.7% of turns, not 9–13% —
   worth knowing before any conclusion is drawn from the verif line.
3. If KB-session presence legitimately indicates verification-rich behavior, count it as its own
   class (e.g. `kb-work`), not under VERIFICATION.

_Evidence: /tmp re-analysis (deleted-on-reboot scratch, mirrors turn-audit.py logic verbatim),
turn-audit-trend.jsonl, turn-audit-latest.md, transcript sampling of sessions 3896e945/d15587bc/
f38d9d11/a39f8b41/b3ac18d0/4219edfb. Nothing under knowledge/ modified except this file._
