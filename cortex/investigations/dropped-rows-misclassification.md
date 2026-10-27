# dropped-* mission-control rows: misclassification audit
Investigated 2026-10-17 (read-only session; only this file written).

## Verdict first
181 `dropped-*` rows in registry.json (all `event: absorb-note`, `state: in-flight`,
`by: deadman-sweep`, one per session). **62 of 181 (34%) are misclassified-LIVE** —
the session kept working after the row declared it dropped. 11 of those 62 were
still active within the last 24h: live sessions wearing a "dropped" badge right now.
The deadman never re-checks: once an absorb-note lands it is idempotent
(`absorb_note_exists` → return) and nothing ever resolves it, so it stays
in-flight forever. Confirmed this is the dominant remaining defect — it produces
staleness AFTER the row is written, not just bad rows at write time.

## Counts per class
Classification basis: row's last registry event ts vs transcript evidence
(`~/.claude/projects/*/<session-id>.jsonl`), cross-referenced against
`garden-reports/session-catalog.json` (930 sessions, generated 2026-10-17T10:23Z).

| class | rows | evidence |
|---|---|---|
| TRULY-DEAD (no transcript activity after row ts) | 119 (66%) | mtime ≤ row ts |
| MISCLASSIFIED-LIVE (mtime after row ts) | 62 (34%) | mtime > row ts |
| ↳ of which CONFIRMED-LIVE (timestamped JSONL line appended after row ts) | 36 | last-line ts > row ts |
| ↳ of which TOUCHED-NOT-LIVE (mtime bumped, no timestamped append after row ts — post-hoc record writes) | 26 | last-line ts ≤ row ts |
| Catalog cross-ref | 62/62 LIVE rows in catalog; 67/119 dead in catalog (52 predate/absent) | id match |
| dropped-* rows stale >24h | 164 of 181 | registry `age_hours` |

Fix-date split: 26/36 confirmed-live rows were written BEFORE the 2026-10-16
deadman FP fix (wrong-clock anchor); 10 AFTER it. So the 10-16 fix (anchor on
last timestamped line instead of mtime / hook wall-clock) reduced but did not
eliminate the class — because the surviving defect is no-resolution, not bad anchoring.

## Top 10 MISCLASSIFIED-LIVE rows (by last real session event)
All `by: deadman-sweep`, `state: in-flight`. last_event = last timestamped
transcript line; catalog = present in session-catalog.json.

| workstream | session id | row written (UTC) | last transcript event (UTC) | catalog |
|---|---|---|---|---|
| dropped-3df5be5d-65f | 3df5be5d-65fd-4735-871d-0d16dd1a578e | 2026-10-17T00:39:55Z | 2026-10-17T11:48:27Z | yes |
| dropped-cef234e4-773 | cef234e4-7739-4814-baa2-ac05df6fe0db | 2026-10-17T00:40:56Z | 2026-10-17T08:01:38Z | yes |
| dropped-1ba896c0-a28 | 1ba896c0-a282-4a38-adf0-608bdebf1df8 | 2026-10-16T22:47:54Z | 2026-10-17T07:40:00Z | yes |
| dropped-769cfc96-50e | 769cfc96-50ee-4d18-a03d-7a1302e95a4b | 2026-10-16T07:49:47Z | 2026-10-17T07:32:16Z | yes |
| dropped-3d4d4b1a-656 | 3d4d4b1a-6560-4078-9948-fe37c9785b81 | 2026-10-16T18:24:47Z | 2026-10-17T07:14:03Z | yes |
| dropped-db615126-d58 | db615126-d58e-4d56-a18a-5c79425a21e1 | 2026-10-16T00:19:26Z | 2026-10-17T05:39:04Z | yes |
| dropped-c9205027-746 | c9205027-7467-4a65-8d9d-f2edecc0903a | 2026-10-17T01:31:46Z | 2026-10-17T03:57:46Z | yes |
| dropped-5526b97a-4a3 | 5526b97a-4a3f-4611-88fa-68323fd05e1a | 2026-10-16T09:13:01Z | 2026-10-17T03:51:52Z | yes |
| dropped-7ad54b2c-6ed | 7ad54b2c-6ed6-4ed6-af43-a168cc22170b | 2026-10-15T22:07:51Z | 2026-10-16T22:54:24Z | yes |
| dropped-e93dad91-008 | e93dad91-0089-4f73-b4a2-e212a1c97be6 | 2026-10-14T14:35:01Z | 2026-10-16T22:42:16Z | yes |

Still-live within 24h (the board's worst offenders): the first five rows above.
Largest lag overall: dropped-e93dad91-008, transcript ran 78.3h past its row ts.

## Root cause (code-cited)
The absorb-note row is written ONCE by `maybe_absorb_drop()`
(`~/.local/bin/session-shadow.py:279`) via `deadman_sweep()`
(`session-shadow.py:395`): `if absorb_note_exists(sid): return` — idempotent,
never re-evaluated. `mission-control.py` folds one event per workstream slug,
and the slug is `dropped-<sid[:12]>` (`session-shadow.py:295`) — a resumed
session's closeouts land under its real workstream slug, so **no closeout can
ever fold the `dropped-*` row away**. Result: correct-at-write-time rows go
stale the instant the session revives, and they accumulate (49% of the registry
was already dropped-noise at the 2026-10-16 audit; 181/365 now).

## Minimal deadman-detector rule change
One condition + one append in `maybe_absorb_drop()` (session-shadow.py:284).
Today:

    if absorb_note_exists(sid):
        return

Change to: if an absorb-note exists **and** the transcript's last timestamped
line is newer than that note's ts, append a resolving row to the SAME slug
instead of returning silently:

    event: absorb-resolved, workstream: dropped-<sid[:12]>,
    state: done, needs: "", what: "session resumed/finished — deadman row superseded
    by transcript activity at <last-line-ts>"

The registry fold keeps the LAST event per slug, so the done row instantly
replaces the stale in-flight absorb-note — no other consumer changes.
One-line statement of the rule: **resolve a deadman row on session activity,
not on registry events — when the transcript outlives the note, fold the note.**
Secondary (same shape, apply for symmetry): session-drop-guard.py writes rows
keyed to hook-fire time with no resolution path at all; the same
resolve-on-activity check covers it.

## Related
- Prior audit: cortex/investigations/fold-dropped-session-false-positives.md
  (2026-10-16, ~70% FP share sample-30, wrong-clock anchor → fixed same day).
  This audit covers the RESIDUAL defect that fix left behind: never-resolved rows.
