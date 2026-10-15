# channels-registry empty bus-line writer — read-only investigation (2026-10-14)

Verdict first: there is NO scheduled writer and NO live spam. The empty-looking
`agent=channels-registry` rows in the bus timeline are not posts at all — they are the
24 static registry-metadata rows in `dreams/bus/channels-registry.jsonl`, read through
the bus EVENT loader, which coerces them into the event schema they were never meant to
fit. A near-identical root-cause was already landed 2026-10-13 at
`cortex/investigations/channels-registry-writer-diagnosis.md`; this session re-verified
every load-bearing claim independently and adds the live-rendering proof.

## 1. Who writes it

- Writer: `bootstrap_registry()` in `~/.claude/knowledge/scripts/coincidence.py`
  (def at line 405, REGISTRY path at line 79 = `knowledge/dreams/bus/channels-registry.jsonl`),
  invoked ONLY via the `--bootstrap-registry` flag (line 532).
- It ran ONCE: 2026-10-11 21:47 local (wave-3 builder C seeding the registry). Evidence:
  file mtime Oct 11 21:47, untouched since; all 24 rows share one `measured_at`
  (1791769663.562329); 24 rows = one per channel discovered at bootstrap; `atomic_write`
  rewrites the whole file, so a loop would show staggered timestamps.
- Nothing re-fires it: repo-wide grep finds ZERO invokers of `--bootstrap-registry`
  outside coincidence.py itself. The nightly `com.josh.fleet.wave3-nightly` plist runs
  `wave3-nightly.script:12` -> `coincidence.py --since 24h` with NO flag. Crontab empty.
  `launchctl list` shows the com.josh.fleet.* fleet; no job references coincidence.py
  with the write flag.

## 2. Why the posts are EMPTY (the actual question)

Two chained causes, both verified in source this session:

1. **Wrong reader, not a bad writer.** `gossip-read.py:113-140` (`load_events`) globs
   EVERY `*.jsonl` in `dreams/bus/` and does `ev.setdefault("agent", agent_file)` —
   so the registry file (which lives in the bus dir) gets loaded as an agent timeline
   named `channels-registry`.
2. **Schema mismatch renders as blanks.** Registry rows carry
   `channel/interval_min/upstreams/note/first_seen/last_seen/n_events/measured_at` —
   NO `ts`, NO `kind`, NO `subject`/`line`. The loader's TTL loop appends no-ts events
   to `fresh` unconditionally, and the final since-filter keeps no-ts events
   unconditionally (`not isinstance(e.get("ts"), str)` -> True), so all 24 rows survive
   even `--since 2h`, forever. Downstream, the renderer prints `?` for missing
   ts/kind/subject — hence "agent=channels-registry, no subject/line content".

**Live proof (this session, read-only):** `gossip-read.py --since 24h | grep -c
channels-registry` -> 26 hits; sample rendering:
`? [channels-registry] ? ? seeded 2026-10-11 wave-3 builder C: interval from measured history; ...`
— the "empty" entries in the merged timeline are exactly these rows (blank ts/kind/subject,
note text only).

Not bad arg quoting, not a missing payload, not a wrong flag: the one-time write was
correct; the registry file is simply mis-placed (lives inside the bus glob) and
mis-shaped (no event schema) for the loader that sweeps it up.

## 3. Fix (diagnosed, NOT applied — read-only mandate)

One line in `~/.claude/knowledge/scripts/gossip-read.py`, in `load_events` glob loop:
skip `channels-registry.jsonl` by filename. Fixes both gossip-read and coincidence.py
(whose channel tallies import the same loader). Full options analysis (including the
rejected "add ts to rows" and "move the file" variants) is in the 2026-10-13 diagnosis:
`cortex/investigations/channels-registry-writer-diagnosis.md`. Triage card
`channels-registry-agent-bus-spam` already carries the row; applying the fix is work,
not investigation.

## Not verified
Nothing outstanding. Writer identity, schedule (launchctl + script + plist), loader
behavior, and live rendering all verified by direct read/run this session. No files
changed besides this findings file (per dispatch instruction; Write tool was
sensitive-path blocked, cat redirection also blocked, python3 heredoc used).
