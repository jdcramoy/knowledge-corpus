# Fleet jobfile drift — clustering investigation (2026-10-14)

Investigator: read-only cortex dispatch. Source run: harness-health 2026-10-14T03:20:05Z
(21 jobfile-drift rows filed to harness-fix/queue.jsonl). Report:
`garden-reports/harness-health-2026-10-14.md`. Nothing was changed except this file.

## Verdict first

**21 rows are really 2 root causes, not 21.** 18 rows are scanner noise from the
2026-10-13 fusion-event backup files; 3 rows are one real partial-deploy of the
FIXLOOP GATE prompt edit. Two single repair passes close the class; zero per-row fixes needed.

## Evidence base (all verified live, read-only)

- Queue rows match report 1:1 (21 jobfile-drift slugs, all `kind: hygiene`, all open, ts 03:20:05Z).
- Canonical: `~/.claude/knowledge/config/fleet/jobs/` — contains 18 `*.bak-fusion-20261013`
  files (mtime 2026-10-13 17:54–19:14). Kit repo `~/Documents/agentic-workato-kit/bin/fleet/jobs/`
  contains zero of them.
- `harness-health.py` `check_jobfile_parity()` (~line 463) walks both dirs with raw
  `iterdir()` and no `.bak-*` exclusion — every backup file is scanned as a first-class artifact.
- Diff of the 3 diverged prompts (jira-triage/ops-autopsy/watchdog `.prompt`): canonical has a
  6-line `## FIXLOOP GATE (2026-10-13, fusion audit)` block prepended; kit copies lack it.
- The matching `.bak-fusion` prompt copies hold the pre-gate version — the gate was an in-place
  canonical edit with a backup left behind, never deployed kit-ward.
- Counter-evidence that env files DID sync: kit `antigen.env` already carries the post-fusion
  `EXTRA_ARGS="--permission-mode bypassPermissions"` (the .bak holds the pre-fusion
  `acceptEdits`). So the fusion deploy ran env-ward but never prompt-ward — a partial deploy.
- Stray sibling artifact: `~/Documents/agentic-workato-kit/bin/session-shadow.py.bak-fusion-20261013`
  (same fusion-event backup class, outside the scanned jobs dirs so uncounted by the 21 rows).

## Clusters

### Cluster A — backup artifacts polluting the parity scan (18 rows, noise)
One canonical event (2026-10-13 fusion audit) left 18 `.bak-fusion-20261013` files in the
canonical jobs dir. Backups were never meant to ship to the kit repo, but the scanner treats
any canonical-only file as drift. Root cause: **scan-surface gap** — the parity check has no
backup-file exclusion, so every future backup/edit event re-files this whole row class.

### Cluster B — partial fusion deploy: prompt edit never went kit-ward (3 rows, real)
The FIXLOOP GATE block was edited into 3 canonical prompts but the kit copies never got it,
while the same event's `.env` changes DID reach the kit. Root cause: **sync-mechanism gap** —
the fusion pass had no completeness check for prompt files, repeating the partial-deploy class
that already bit 2026-10-10 (named in the scanner's own comment, harness-health.py ~line 454).

## Proposed repair (2 passes, class-level)

1. **Cluster A — scanner patch (not file moves):** in `check_jobfile_parity()`, filter both
   `canon_files` and `dep_files` to skip `.bak-*` (and `.bak` generally), e.g.
   `if p.name.split('.bak')[0] == p.name` gating inclusion. This permanently closes all 18
   rows and every future backup event. Alternative (weaker): relocate the 18 backups to
   `config/fleet/jobs-archive/` — but that alone leaves the gap open for the next backup.
   Do both only if Josh wants the jobs dir clean; the filter is the class-closer.
   Also sweep the stray `bin/session-shadow.py.bak-fusion-20261013` in the kit repo on the same pass.
2. **Cluster B — one kit-ward deploy of the 3 prompts:** copy canonical
   `jira-triage.prompt`, `ops-autopsy.prompt`, `watchdog.prompt` over their kit copies
   (canonical is the corrected side — it carries the gate the fusion audit intended). Then
   close the 3 queue rows. Optionally: add a post-edit deploy checklist line to the fusion/
   audit flow — "env AND prompt AND script files all copied kit-ward" — since this is the
   second partial-deploy in 4 days.

Recommended order: pass 2 first (real drift, the running jobs' canonical prompts already have
the gate so fleet behavior is correct either way, but the kit repo is declared source of truth
via the `~/.local/bin/fleet` symlink), then pass 1 (silences the noise permanently).

## Not verified

- Whether `~/.local/bin/fleet` is indeed the symlink the scanner comment claims (not re-checked).
- Whether run-job.sh reads prompts from canonical or kit at runtime (canonical assumed live per
  the DEPLOY CHECKLIST comment; fleet behavior is unaffected by the kit-side lag either way).
- The 2026-10-13 fusion session's own deploy log was not located; the env-vs-prompt asymmetry is
  inferred from file mtimes + diffs, not from that session's transcript.
