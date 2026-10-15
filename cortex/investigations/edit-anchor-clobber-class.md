# Edit-anchor-clobber failure class — investigation findings

Investigated 2026-10-12 (cortex sweep, read-only). Source: harness-dreamer 03:49Z finding, thread
`edit-anchor-clobber-class`. Scope: 783 session transcripts under ~/.claude/projects/ (mtime >= 2026-10-05),
2,990 Edit tool calls parsed, plus full transcript replay of both flagged sessions.

## The two instances (confirmed, both repaired in-session)

**1. `f38d9d11` (session f38d9d11-3323-4bba-a003-d5db84cb056e), 2026-10-10 04:11:22 — `kb/search.py`**
- Intent: insert `_chunk_cosine` and `_title_overlap` helper defs before `def search(`.
- Edit used `old_string` = the single line `def _edge_neighbors(db: sqlite3.Connection, seed_urls: ...) -> list[Hit]:` and `new_string` = the two new helpers ending in `def search(`. The `_edge_neighbors` header was consumed entirely; its body (docstring, try-block, ~40 lines, none of it in old_string) was left orphaned and attached to the trailing `def search(`. Syntactically plausible file, functionally broken.
- Repair: 13 seconds later, a second Edit whose old_string was exactly the mangled state (`def search(` + the neighbor body head) restored the `def _edge_neighbors` header. Caught by model self-review, not by tooling.

**2. `f7acbe35` (session f7acbe35-edc5-44dd-96fd-5fd69a8e3a80), 2026-10-08 02:56:47 — `knowledge/scripts/brain-dashboard.py`**
- Intent: insert timer-counting lines before the `stat = lambda label, value, sub="": ...` definition.
- Edit used `old_string` = the 2-line lambda definition, `new_string` = the new counting code with no re-inclusion of the lambda. The `stat` helper was silently deleted (file stayed syntactically valid).
- Detection chain (transcript L679-L759): edit succeeded -> grep verify showed a duplicated `agents_speaking` line (first anomaly) -> 3 runtime tracebacks (launchctl bootstrap, 2x direct python3 run, NameError on the deleted lambda) -> model states "My earlier edit replaced the `stat` lambda definition instead of following it" -> repair edit 40 seconds later. Caught by runtime failure only.

Current file state verified today: `def _edge_neighbors` present (1 occurrence) in search.py; `stat = lambda` present (1 occurrence) in brain-dashboard.py. Zero persistent damage from either instance.

## Trigger pattern (what state makes the anchor go stale)

Both instances share one anatomy:

1. The model intends an INSERTION adjacent to an existing short definition and uses that definition line as `old_string`, planning to re-include it at the end of `new_string` (the correct insert-before-anchor form).
2. The staleness is in the MODEL'S mental file image, not in the file. The Edit tool's match is unique and valid; nothing is wrong from the tool's side. Two failure sub-modes observed:
   - Wrong-neighborhood anchor: an earlier correct insertion (04:19 -> search.py L1187, 4 min prior) had already placed `_edge_neighbors` directly above `def search(`. On the next insertion the model anchored for "before search" but grabbed the `_edge_neighbors` def line as old_string, so the replacement consumed the wrong header and orphaned its body onto the trailing `def search(`.
   - Replace-instead-of-follow: the model wrote the insertion content as new_string and simply never re-included the anchor (stat lambda). Its own later wording confirms the intent was to follow the anchor, not replace it.
3. The Edit tool cannot intercept this: old_string matched uniquely, the file was freshly read, the operation is legal. The failure is a generation error (anchor omitted from new_string), not a tool mismatch.
4. Clobber shape depends on what follows the anchor: if the body below the anchor was NOT part of old_string, the body gets re-parented to whatever the new_string ends with (orphaned-body variant, worse because syntax stays valid); if the anchor was a self-contained helper, the def just disappears (valid file, NameError at runtime).

## Frequency and detection rate (7-day quantitative sweep)

- 2,990 Edit calls across 783 recent transcripts (all projects, main sessions + subagents).
- Definition-anchored short old_strings (<=3 lines, first line is def/class/name=lambda): 73.
  - 71 correctly re-included the anchor in new_string (the correct form).
  - 2 consumed it: the two instances above. Per-attempt error rate ~2.7%; fleet-wide that is ~0.4 instances/week at current edit volume.
- 62 additional "String to replace not found" / "old_string and new_string are the same" tool errors = near-misses where anchor staleness WAS caught by the tool (non-silent, retries followed).
- Tight signature sweep (anchor's defining token fully vanishes from new_string, no repair): exactly 1 candidate beyond the two known instances, and manual check shows it is a deliberate function replacement (`recipes_by_folder` -> `recipes_in_scope` in changelog.py, def gone, zero remaining references, replacement present). False positive. So the observed undetected count in 7 days is ZERO, and the signature has ~1 FP/week as a guard predicate.

## Undetected-occurrence risk

Both observed instances were caught within the same session (13s and 40s), but detection came from downstream signals, never from the Edit itself:
- The orphaned-body variant survives `py_compile`-style checks only by luck (it happened to break NameError-level at runtime here; it can also parse cleanly if the trailing anchor accepts the body).
- The deleted-helper variant is syntactically invisible; only execution of the deleted symbol catches it.
- Blind spot: helpers/branches edited late in a session with no runtime probe (no test, no py_compile, no script run) would persist silently. At ~0.4 instances/week and both instances caught only because a runtime probe happened to run, an estimated meaningful fraction of future instances in probe-less sessions will go undetected. The class is real but low-frequency; cost when undetected is a broken file handed off as done.

## Guard recommendation (validates dreamer proposal 2026-10-11-edit-anchor-readback)

Two layers, both warn-only:
1. Edit-time predicate (hook): warn when `old_string` first line defines a token (def/class/name=lambda), that token is absent from `new_string`, and `new_string` is longer than `old_string` (insertion-shaped). On the 7-day corpus this fires on exactly the 2 true instances and 1 deliberate replacement (~1 FP/week). Message: "anchor <token> is consumed by this edit; if inserting, re-include the anchor line at the end of new_string."
2. Post-edit runtime probe: the existing lint-changed.py CHECKERS path (py_compile) after Python edits catches the orphaned-body variant; it cannot catch deleted helpers, which need execution (or an AST diff comparing defined names before/after the edit).

Dreamer's warn-only hook proposal (never_auto) is confirmed valid by this data. Josh's call on wiring it.
