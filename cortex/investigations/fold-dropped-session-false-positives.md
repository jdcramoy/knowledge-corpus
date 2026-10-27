# Fold / dropped-session deadman gap — root cause + false-positive estimate
Investigated 2026-10-16 (session b6a2031d-441, read-only; only this file written).

## Verdict first
The deadman is broken by TWO anchored-to-the-wrong-clock defects, and the fold
exclusion the absorb note hypothesized is real but NOT the flag's cause.
Estimated false-positive share of the recent dropped backlog: ~70% (21 of 30).

## 1. Why 917cae60's six closeouts are excluded from registry.json (fold logic)
`~/.claude/knowledge/scripts/mission-control.py:118` — `fold()` keeps exactly
ONE event per canonical workstream slug (`reg[canonical_slug(w)] = e`, last
event wins). The registry is a current-state projection with no history and no
session identity (rows carry no session_id). The session's closeouts for
`google-semantic-mcp` (19:28-23:35Z) were superseded by the LAST event for that
slug — another session's closeout at 2026-10-14T02:39:25Z ("Diagnosed the
FLYWHEEL STALLED spam") — so registry.json shows `google-semantic-mcp done`
with none of 917cae60's rows visible. Mechanism: last-event-only collapse.
Not the window, not dedupe, not a field filter.

## 2. The rows still exist (verified)
events.jsonl carries SEVEN closeout rows for `google-semantic-mcp` in the
session window, all `by: josh (session)`: lines 276, 277, 279, 282, 285, 353,
363 — ts 2026-10-13T19:28:19Z through 23:35:32Z. Nothing was lost.

## 3. The flag's real cause (session-shadow deadman, not the fold)
The detector is `~/.local/bin/session-shadow.py` `deadman_sweep()` (launchd
`com.josh.session-shadow`, 60s loop; the SessionEnd hook
`~/.claude/hooks/session-drop-guard.py` is a second writer with the same defect
class). It marks a transcript "closed out" only if a mission-control event
lands in `[mtime - 900s, mtime + 60s]` of the TRANSCRIPT FILE MTIME.
The 917cae60 transcript's mtime is 2026-10-15T02:26:02Z — 26.8 hours after its
last real message (2026-10-13T23:38:48Z) — because Claude Code appends
post-hoc `last-prompt` / `cost-state` records after the conversation ends.
That drift pushes the 15-min closeout window far past the real closeout, so
the flag fires on a cleanly closed session. Verified numerically: the
23:35:32Z closeout is inside the window when anchored to last real message,
outside when anchored to mtime. The same drift re-arms the sweep after every
append — 917cae60 was re-flagged 8 times across 2026-10-14 (also inflating
dropped-sessions.jsonl to 634 rows).

## 4. False-positive share of the dropped backlog (sample of 30 most recent distinct sessions)
- 9 sessions: mtime drift (>15 min) hid a window-valid closeout — FALSE POSITIVE.
- 12 sessions: logged a closeout within +/-15 min of last activity, still flagged
  (SessionEnd-hook path anchors to hook-fire wall clock — same wrong-clock
  defect) — FALSE POSITIVE.
- 9 sessions: genuinely no closeout near activity — TRUE positives.
- Estimated FP share: **70%** (21/30). Registry pollution: 158 of 321
  registry.json rows (49%) are `dropped-*` absorb-note rows — state in-flight,
  never closed, permanent stale noise on the board.
- Corroboration: 917cae60 itself is the documented case (its absorb note
  concluded "NOT actually dropped"); the SessionStart banner's "103 dropped
  sessions" therefore overstates real drops roughly 3x.

## One-line fix
In `deadman_sweep()` (session-shadow.py) anchor the closeout window to the
transcript's last REAL message time — the last line carrying a `timestamp`
field — instead of `os.path.getmtime(f)` (apply the same swap in
session-drop-guard.py, where the anchor is hook-fire time). The deeper fix
worth queueing: add `session_id` to mission-control `add` rows so closeout
attribution stops being a time-proximity guess; today no consumer can answer
"did THIS session close out?"

## Not verified
- Which process appends the post-hoc `last-prompt`/`cost-state` lines (harness
  vs session-shadow itself) — mechanism proven either way; author not pinned.
- The 48h/20min sweep-arm interplay on the 8 re-flags of 917cae60 (row ts
  alignment at :44 suggests an hourly cadence; not traced to the cron owner).
- Nothing was changed except this file (read-only per instruction — including
  no mission-control closeout row for this session; flagging that openly).
