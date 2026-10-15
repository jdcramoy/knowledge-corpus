# kb-wave3-sources aliveness census (read-only, 2026-10-12 ~23:40 PT)

Dispatched by cortex pulse 23:34Z (registry row in-flight 26.6h, needs EMPTY, no
events since). Verdict up front: **quietly complete-but-unrecorded** — the wave-3
build landed and its numbers verify live, but the session that did it never posted
a mission-control closeout, and two real tails remain (uncommitted code, fix never
proven by a live sync).

## 1. What it set out to do

KB corpus scout-expansion wave 3 (RAG++ pipeline, repo ~/Documents/workato-kb,
data ~/.claude/workato-kb). Registry row opened 2026-10-11T20:57:27Z by "josh
(parallel kb session)": "KB wave 2 landed (24.6k docs / 165k chunks, eval held);
wave 3 queued: JS-rendered distill and NoC slices, Camel, Postgres, eval-set
regen". The wave-3 queue (README Roadmap + projects/workato-kb.md): distill +
Nature of Code via git routes (both had become JS-rendered Gatsby apps invisible
to the wave-2 crawler), Camel .adoc→md, selective Postgres chapters, AWS WAF,
trigger.dev parser, Snowflake depth, and eval-set regeneration (the old eval could
not measure the expansion's gains — expectations were Workato-only).

Note: distinct from harness-wave3-science (the physics-fusion harness build),
which closed done the same night — the two share the "wave3" name only.

## 2. What state it actually reached (live-verified this session)

The build ran the SAME NIGHT, 2026-10-11 ~21:08–23:02 local. All of it is on disk:

- `kb/camel_source.py` exists (mtime 21:12) — Camel via sparse clone + Pydowndoc.
  Manifest `camel.jsonl` = **812 rows** (matches doc claim exactly).
- `snowflake.jsonl` = **8,922** rows; `trigger.jsonl` = **15**; `webcrawl.jsonl` =
  **3,249** (holds distill 52, Nature of Code 19, Postgres 72, AWS WAF 48).
  Corpus dirs: camel 369M, snowflake 92M, webcrawl 64M.
- Eval regenerated: `~/.claude/workato-kb/eval/results-baseline-postexp.json` —
  n=275, R@10 **0.8945**, MRR **0.8312** — matches the project doc's claimed new
  regression reference digit for digit.
- Index rebuilt Oct 11 22:51–22:53 (kb.db 1.87G, fractal.db 1.91G).
- README Roadmap line 161: "[x] Scout wave 3: DONE 2026-10-11" with the full
  per-source breakdown.
- projects/workato-kb.md "Wave 3 + outstanding-fix sweep" section records the
  whole night including paid gotchas.
- Bonus: the `_collect_distill` NameError that broke two syncs that night was
  root-caused and fixed in `kb/html_source.py` (def added 23:02:40, seven minutes
  after the last failing report) — see
  cortex/investigations/kb-sync-collect-distill-nameerror.md.

## 3. Verdict + the two real tails

**Complete in substance, unrecorded in mission control.** The build session
wrote the project doc, README, and code but never closed the registry row. The
row should move to done-with-caveats — but NOT before the two tails below,
because "done" currently rests on the builders' own numbers plus my disk checks,
not on a proven live sync.

TAIL 1 — all wave-3 code is UNCOMMITTED. Last commit in ~/Documents/workato-kb is
2026-10-10 (f02cad2). Working tree: 10 modified files + 3 untracked sources
(camel/html/rss_source.py). One careless checkout loses the whole wave. The
NameError investigation itself flags the fix as "uncommitted; unverified by live
run". Commit is the single highest-value 5-minute action on this workstream.

TAIL 2 — no successful sync since the fix. sync.log's last entry is the failing
run 2026-10-11T22:47:44 (webcrawl floor failure); no diffs report newer than
22:55 Oct 11; cortex reported 10-12 digests missing at 19:33Z and 21:25Z Oct 12
("if tonight's sync failed the webcrawl floor again that is three nights"). The
investigation's own proposed verification — a scoped `--sources webcrawl` run —
has not happened. The fix is on disk and AST-sound but has never run live.

Parked small items (per project doc, correctly open): Snowflake IncompleteRead
pages retry on next etag sync; optional hand-authored cross-source eval slice;
source-affinity weighting for Workato-slice queries (proposed, not built).

## Recommended disposition for the registry row

Not "close as done" flat-out. The honest closeout: run the scoped webcrawl sync
live (proves the NameError fix and regenerates the missing digest), commit the
working tree, THEN post the kb-wave3-sources closeout citing this file and the
project doc. Both actions are dev-scope and unblocked; the closeout needs either
a gated session or Josh's go for the commit (repo hygiene only, no platform
writes).

Nothing unverified is claimed above as verified: every number in section 2 was
read live from manifests/eval/corpus this session; the one thing this census did
NOT do is execute the verification sync (read-only mandate).
