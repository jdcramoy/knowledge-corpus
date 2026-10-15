# Bus-timestamp clock census (read-only sweep)

Date: 2026-10-12. Local timezone: EDT (UTC-4). Method: for each outbox in
`~/.claude/knowledge/dreams/bus/*.jsonl`, grep'd knowledge/scripts/, fleet jobs
(`knowledge/config/fleet/jobs/`), `~/.local/bin/`, and LaunchAgents for the
writer, then compared each file's last-row `ts` against its filesystem mtime
(naive-local rows match mtime exactly; UTC rows read mtime + 4h).

## Root cause (one writer, eight victims)

`knowledge/scripts/bus_post.py:39`:

    "ts": dt.datetime.now().isoformat(timespec="seconds"),   # naive LOCAL

vs the house standard, `mission-control.py:147`:

    "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),  # UTC

## Per-producer census

| Outbox | Writer script | Timestamp source | Sample line (ts vs mtime) | Clock verdict |
|---|---|---|---|---|
| benchmark.jsonl | `bus_post.py post` | naive local (`now()`) | ts 04:07:05 = mtime 04:07:05 EDT | WRONG |
| brain-gardener.jsonl | agent hand-write (gardener session, bash echo) | UTC, Z-suffix (hand-stamped) | ts 03:05:00Z vs mtime 23:01 EDT | OK |
| builder-epistemics.jsonl | `bus_post.py post` | naive local | ts 21:48:42 = mtime 21:48:42 EDT | WRONG |
| channels-registry.jsonl | `coincidence.py` (REGISTRY write, line ~420) | UTC aware — `time.gmtime` + `%...Z` | first_seen 08:07:05Z, measured_at epoch | OK |
| cortex-investigation.jsonl | `bus_post.py post` | naive local | ts 01:39:05 = mtime 01:39:05 EDT | WRONG |
| cortex.jsonl | `bus_post.py post` (112 rows) + agent hand-write (75 rows Z) | MIXED: naive local + UTC | 75 rows end Z, 112 do not | WRONG (dominant path naive) |
| dissenter.jsonl | agent hand-write (bash echo) | UTC, Z-suffix | ts 00:30:00Z vs mtime 20:30 EDT | OK |
| docs-watch.jsonl | `workato-docs-watch.py:60` (`datetime.now(timezone.utc)`) | UTC, Z-suffix (date-only ts) | ts 10:08:17Z vs mtime 06:08 EDT | OK |
| estate-architect.jsonl | agent hand-write | UTC, Z-suffix | ts 11:32:00Z vs mtime 07:11 EDT | OK |
| fix-82862205-family.jsonl | `bus_post.py post` | naive local | ts 04:43:00 = mtime 04:43 EDT | WRONG |
| gym.jsonl | `gym.py:51` (`datetime.now(timezone.utc)`) | UTC aware (+00:00) | ts 19:16:35.914765+00:00 vs mtime 15:16 EDT | OK |
| harness-dreamer.jsonl | agent hand-write (dream loop, dream-nightly.sh spawns) | UTC, Z-suffix | ts 03:49:44Z vs mtime 23:49 EDT | OK |
| librarian.jsonl | `bus_post.py post` | naive local | ts 22:15:56 = mtime 22:15:56 EDT | WRONG |
| main.jsonl | agent hand-write (handoff row) | UTC, Z-suffix | ts 05:00:00Z vs mtime 00:59 EDT | OK |
| orca-main.jsonl | agent hand-write (handoff row) | UTC, Z-suffix | ts 15:39:59Z vs mtime 11:39 EDT | OK |
| prediction-errors.jsonl | `predict.py` `_now()` (line 39-40, `now(timezone.utc)`) for its own rows; PLUS hand-written session rows | MIXED: UTC aware + hand rows naive/null | predict rows +00:00; hand row ts "00:24:16" naive, latest row ts null | PARTIALLY WRONG (hand rows) |
| project-dreamer.jsonl | agent hand-write | UTC, Z-suffix (sloppy: ts off mtime+UTC by ~23 min) | ts 01:05:00Z vs mtime 00:42 EDT | OK (imprecise) |
| promotion-orchestrator.jsonl | — file is 0 bytes, never written | n/a | — | n/a |
| replay-sampler.jsonl | `replay-sample.py:304` → `bus_post.post()` | naive local (inherits bus_post) | ts 03:37:08 = mtime 03:37:08 EDT | WRONG |
| restore-drill.jsonl | `bus_post.py post` (via restore-drill fleet job) | naive local | ts 05:19:37 = mtime 05:19:37 EDT | WRONG |
| session-shadow.jsonl | `~/.local/bin/session-shadow.py:33` | UTC, Z-suffix | ts 13:15:12Z vs mtime 09:15:12 EDT | OK |
| workato-health.jsonl | `workato-health.py:205` (`now(timezone.utc)`) | UTC, Z-suffix | ts 13:28:10Z vs mtime 09:28 EDT | OK |
| workato-kb.jsonl | ad-hoc session hand-write (no script found; `entropy_report` is not a bus_post type) | naive local (hand-stamped) | ts 23:46:09 = mtime 23:46 EDT | WRONG |
| workato-watchdog.jsonl | agent hand-write (echo, date -u) | UTC, Z-suffix | ts 03:17:58Z vs mtime 23:17 EDT | OK |

Side note: `kb-audit.py:197` uses the same naive `dt.datetime.now()` but writes
the audit JSON under `~/.claude/workato-kb/audit/`, not the bus — adjacent bug,
out of scope here. `bus_post.py:75` computes its 24h cutoff from naive-local
`now()` too, so bus_post's own `threads` window is internally consistent with
its naive stamps but shifts 4h against every UTC writer in the same merged
timeline.

## (a) Which existing outbox lines are in the wrong clock

Every row written through `bus_post.py post` — i.e. ALL rows in:
benchmark, builder-epistemics, cortex-investigation, fix-82862205-family,
librarian, replay-sampler, restore-drill, plus the 112 non-Z rows inside
cortex.jsonl — carry naive EDT stamps that read 4 hours behind UTC. They sit in
the same files as correctly-UTC hand-written/scripted rows (cortex.jsonl is the
worst: 112 naive vs 75 UTC rows interleaved). Also wrong: the hand-stamped
`workato-kb.jsonl` entropy rows (naive EDT), and the hand-written rows in
prediction-errors.jsonl (naive or ts:null). Effect: `gossip-read.py` merged
timeline and any UTC-aware 24h cutoff mis-sorts/mis-windows these rows by 4h;
corroboration counts grouped by recency windows under-count bus_post producers.

## (b) The one-line fix per non-UTC producer

ALL eight naive producers share ONE root cause — a single line fixes them all:

`knowledge/scripts/bus_post.py:39`:
    "ts": dt.datetime.now().isoformat(timespec="seconds"),
→  "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),

(matchs the mission-control.py:147 house format; also update the cutoff at
bus_post.py:75 to `dt.datetime.now(dt.timezone.utc)` so the 24h window compares
UTC to UTC).

Remaining two are PROCEDURAL, not code:
- workato-kb.jsonl: the writer is whichever Claude session posts the row by
  hand — the fix is to stop hand-stamping and post via
  `bus_post.py post --agent workato-kb --type finding ...` (after the line-39
  fix) or stamp with `date -u +%Y-%m-%dT%H:%M:%SZ`.
- prediction-errors.jsonl hand rows: sessions should leave error spikes to
  `predict.py` (already UTC-aware) rather than echoing rows with their own ts.

Existing wrong-clock rows are history — leave them (they're append-only
evidence); the fix governs future writes. Optionally backfill by +4h if any
downstream windowing must be re-run over old data.

Not verified: no writer found for promotion-orchestrator.jsonl (file empty —
plausibly its fleet job has never completed a post); brain-gardener/dissenter/
watchdog/dreamer/main/orca-main writers are inferred from row shape (hand
echo with Z) since no script targets those paths — the Z + UTC arithmetic
against mtime makes the clock verdict solid regardless of which session
stamped them.
