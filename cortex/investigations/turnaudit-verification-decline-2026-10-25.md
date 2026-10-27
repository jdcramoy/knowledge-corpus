# Turn-audit verification-rate decline — root cause (2026-10-25, read-only investigation)

**VERDICT: detector drift, not behavior drift — with a real, smaller compositional shift underneath.
The headline sequence 13% → 9% → 8% → 3% is two separate artifacts stacked: (A) four KB-corpus
mega-sessions leaving the 7-day window, and (B) the v2 detector change shipped 2026-10-23 11:58,
which alone dropped the same-day same-corpus score from 8.12% to 2.76%. Real verification
discipline (v2-clean rate) has been low-but-flat; waste (~3.4%) and errors are genuinely steady
state and are NOT part of this decline.**

## 1. What 'verification' counts (script + inputs)

- Script: `~/.claude/knowledge/scripts/turn-audit.py` (zero-LLM, runs in the fleet). Scans ONLY
  `~/.claude/projects/-Users-<user>-Documents-workbench/*.jsonl` (mtime within 7d), classifies
  assistant tool calls, writes `~/.claude/knowledge/reports/turn-audit-latest.md`, appends a trend
  row to `reports/turn-audit-trend.jsonl`, posts to `dreams/bus/turn-audit.jsonl`.
- **v1 definition** (until 2026-10-23 11:58, preserved in `turn-audit.py.bak-fix2-20261023`):
  a Bash call is VERIFICATION if the command matches
  `unittest|pytest|\btest\b|job_get|job handle|trace|verify|read.?back|kb_search|kb\b`. Everything
  non-Bash (MCP tools, Read, Grep) = productive; only Bash could earn verification credit.
- **v2 definition** (current, `SIG_VERSION = "v2-no-bare-kb+tool-credit"`): dropped the bare `kb\b`
  alternation; ADDED credit for verification-shaped non-Bash tools (`job_get/job_list/recipe_get/
  get_recipe/kb_search/search_recipe_dependencies/verify/trace` in the tool NAME) and Reads whose
  file_path contains `trace|verif|audit|evidence|report|regression`.
- The prior investigation (`cortex/investigations/turn-audit-verif-decline.md`, 2026-10-22) proved
  the v1 `kb\b` class was 80%+ noise: `cd ~/Documents/workato-kb`, `cat .../kb-digests/...` etc.

## 2. Where the decline concentrates

**Per-window composition (line-timestamp windows, re-scored read-only against live transcripts):**

| Window (report run) | Bash calls | v1 credits | v1 share of Bash |
|---|---|---|---|
| Oct 13 run (the "13%") | 7,508 | 1,449 | 19.3% |
| Oct 20 run (the "9%") | 4,213 | 624 | 14.8% |
| Oct 23+ run (the "8%"/"3%") | 6,799 | 551 | 8.1% |

- **13% → 9%: concentrated in FOUR sessions that left the window.** In the Oct-13 window, four
  KB-corpus mega-sessions carried 853 of 1,449 v1 credits (59%): `3896e945` (446; "deep deep
  understanding of Workato architecture" corpus build), `d15587bc` (159; browser/vision skill),
  `f38d9d11` (155; memory/skill/kb→Obsidian), `b3ac18d0` (93; Confluence KB mining). All are
  `cd workato-kb`-class kb-word noise, not test runs. Current-window top session has 32.
- **9% → 8%: mild further kb-noise runoff** as those sessions aged out; broad population flat.
- **8% → 3%: 100% detector change** (see §3). Same corpus, same day, 2 seconds apart.

**By lane (current window, v2 Bash credits / Bash calls):** cortex-pulse 48/2,730 (1.8%),
sweep/watchdog 39/1,160 (3.4%), other/interactive 84/1,710 (4.9%), jira/triage 16/325 (4.9%),
workato-build 34/638 (5.3%), kb/corpus 12/129 (9.3%). **No lane collapsed; the pulse lane is the
biggest volume (40% of classified calls) at the lowest verification share, so it dominates the
network number — that is lane MIX, not lane decay.** By project: not observable — the script
scans a single corpus (workbench) by design; every classified call has cwd ~/Documents/workbench.

## 3. Detector drift: CONFIRMED (controlled same-corpus A/B)

`trend.jsonl` rows `2026-10-23 11:58:41` and `11:58:43` — 264 sessions / 11,370 turns / 632 errors
IDENTICAL, scored 2 seconds apart across the v1→v2 boundary:

- v1 signature: **verif 8.12%**, waste 3.45%
- v2 signature (`v2-no-bare-kb+tool-credit`): **verif 2.76%**, waste 3.94%

Script mtime 11:58 matches the runs to the minute; the v1 file is preserved as
`turn-audit.py.bak-fix2-20261023`. Decomposition on the current window: v1 credited 551 Bash
matches; dropping `kb\b` removed ~311 (56%); the new MCP/Read credit added back ~92 (recipe_get 27,
kb_search 20, job_list 16, search_recipe_dependencies 12, job_get 6, Read-path 10) → net 314 = the
reported v2 numerator. The v2 tool-credit change is also now CREDITING real verification the old
metric missed (direction opposite to the headline drop).

## 4. Top contributing sessions/agents

- **Decline drivers (v1 numerator that left):** `3896e945` (446 v1 credits), `d15587bc` (159),
  `f38d9d11` (155), `b3ac18d0` (93) — the Oct 9–14 KB-corpus build wave.
- **Current-window top genuine verifiers:** `e3e26529` (32 v2 credits — Workato MCP data-parity
  check), `ef893e1a` (14 — Company Brain build), `4d80970e` (13).
- **Largest drag (volume × lowest verification):** the cortex-pulse lane, 282 sessions,
  40% of all classified calls, 1.8% v2 verification share.
- Error side (unchanged, not part of this decline): bash-exit 492, permission-denied 58,
  other 74, stale-schema 8 of 632 total; worst waste sessions `3df5be5d` (31w/36e) and `fd4279d5`
  (18w/28e).

## 5. Bottom line for Josh

1. The verif line has never been comparable across this sequence — three different things moved:
   window composition (twice) and the detector (once). The only like-for-like comparison is the
   10-23 A/B pair, and it says the last step was pure metric change.
2. Under the v2 definition, true verification share is ~3% and flat, concentrated lowest in the
   pulse lane. If ~3% is too low as a discipline standard, that is a lane-behavior conversation
   (pulse/sweep do few test-shaped actions by design — they mostly read), not a regression.
3. Going forward, only v2 rows are comparable; the v2 note field already marks the break.
   Consider renaming the metric "verification-shaped actions" — pulse lanes will read low forever.

*Method: read-only re-classification of live transcripts with both signatures, line-timestamp
windows; no file under knowledge/ was modified. Unverified: nothing — all numbers above were
recomputed this session from the same corpus the script reads.*
