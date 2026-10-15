# channels-registry bus "spam" — read-only diagnosis (2026-10-13)

Verdict first: NOT a stuck retry loop and NOT live spam. One single write of a static
24-row registry file on 2026-10-11 21:47 local (2026-10-12T01:47:43Z) is being re-read
as bus events on every gossip-read pass, because the registry lives inside the bus
directory and its rows carry no `ts` field, so they bypass both the TTL filter and the
`--since` cutoff forever.

## 1. Writer identification

- The note string `seeded 2026-10-11 wave-3 builder C` exists in exactly ONE script:
  `~/.claude/knowledge/scripts/coincidence.py` (lines 415/418, inside
  `bootstrap_registry()`; REGISTRY path at line 79 = `knowledge/dreams/bus/channels-registry.jsonl`).
- No launchd plist or cron calls it with the write flag: the nightly
  `com.josh.fleet.wave3-nightly` plist runs `run-job.sh wave3-nightly`, whose script
  (`~/.local/bin/fleet/jobs/wave3-nightly.script:12`) invokes
  `coincidence.py --since 24h` WITHOUT `--bootstrap-registry`. Repo-wide grep found
  zero invokers of `--bootstrap-registry` outside coincidence.py itself. Crontab is empty.
- File evidence confirms a single write, not a loop:
  - `channels-registry.jsonl` mtime = Oct 11 21:47, never touched since.
  - All 24 rows share one identical `measured_at` = 1791769663.56 (2026-10-12T01:47Z).
  - 24 rows = exactly one row per channel discovered at bootstrap (atomic_write
    whole-file rewrite — an append loop would show staggered timestamps).

## 2. Why it duplicates on every read

`gossip-read.py:113-140` (`load_events`) globs EVERY `*.jsonl` in
`knowledge/dreams/bus/` — including `channels-registry.jsonl`, a metadata file that
happens to live in the bus directory. For each row it does
`ev.setdefault("agent", agent_file)` -> agent becomes `channels-registry`. Two
aggravating bugs:

1. Rows have NO `ts` field (they carry `first_seen`/`last_seen`/`measured_at`
   instead). In the TTL loop, no-ts events are appended to `fresh` unconditionally
   (never expire), and the final `--since` filter also keeps no-ts events
   unconditionally. Net effect: all 24 rows appear in EVERY read, even `--since 2h`,
   forever.
2. All 24 rows carry the same builder-C note, so the merged read renders as ~24
   near-identical "channel-census" lines from one agent — matching the cortex pulse
   complaint (attention-queue-2026-10-13-2145.md item 6). Side effect: they can
   inflate corroboration/thread tallies and coincidence.py's own channel list
   (coincidence.py imports gossip-read's loader).

So: not idempotence failure on `measured_at`, not a retry loop — a placement bug
(registry inside the bus glob) + a schema mismatch (no `ts`) making a one-time static
file look like an ongoing firehose.

## 3. Minimal safe fix

ONE file to change: `~/.claude/knowledge/scripts/gossip-read.py`, in `load_events`
(line ~117). Skip the registry filename in the glob loop:

    for path in sorted(glob.glob(os.path.join(bus_dir, "*.jsonl"))):
        if os.path.basename(path) == "channels-registry.jsonl":
            continue   # registry metadata, not bus events

Options considered:

- RECOMMENDED: the filename skip above. One line, zero downstream effects — every
  consumer that needs the registry reads it via `coincidence.py --registry` / direct
  path, never via `load_events`. Fixes both gossip-read AND coincidence.py's polluted
  channel list in one stroke (coincidence imports this loader).
- Alternative (more robust, slightly larger): filter rows by schema inside the loop —
  skip events lacking `ts` AND carrying `interval_min`/`upstreams` keys. Covers any
  future metadata file dropped in the bus dir.
- NOT recommended: moving the registry out of `dreams/bus/` — breaks the wave-3
  CONTRACTS.md-documented location and requires editing coincidence.py line 79 plus
  re-pointing consumers.
- Do NOT "fix" coincidence.py by adding a `ts` to registry rows — they would still be
  misread as events and would genuinely age into the bus for ttl_days.

No stop/restart needed: nothing is running; the file is static. After the one-line
fix, a `gossip-read.py --since 2h` re-run should show zero channels-registry lines —
that is the verification step.

## What was NOT verified
- Nothing unverified beyond the fix itself (not applied — read-only mandate). All
  writer, timestamp, and loader-behavior claims above are from direct file reads.
