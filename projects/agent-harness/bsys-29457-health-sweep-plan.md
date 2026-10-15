# BSYS-29457: workato-health.py sweep hygiene (3 findings) — plan and verification state

Ticket: [BSYS-29457](https://workato.atlassian.net/browse/BSYS-29457) (Bug, Backlog, 2 points). Parent epic BSYS-29454 Agent Harness Operations.

## The three findings

1. mcp_mock registry-probe jobs counted as prod failures in the hourly sweep.
2. No dedupe-on-append: triage queue got a fresh row per sweep for the same open slug.
3. Possible second triage_append helper with the same gap.

All three landed 2026-10-09; a race-fix rewrite of triage_append landed overnight 2026-10-11. See also `BSYS-29457-workato-health-sweep-verification.md` in this directory (prior pass's close-out doc, includes the in-session hardening-push false-alarm class).

## Verification state (live re-check 2026-10-12)

- Script: `~/.claude/knowledge/scripts/workato-health.py` (mtime Oct 11 03:26 local), read-only against Workato by design.
- Finding 1: CONFIRMED in code. `is_probe_job()` lines 87-89; verdict branch lines 233-246 excludes probes (and red test-case jobs) from `real` failures; excluded-probe count surfaces in the sweep line. Live trace: health.log `2026-10-11T07:11:43Z` reads "(136 probe jobs excluded)". Also earlier firing: 2026-10-09T09:10:41Z "(65 probe jobs excluded)".
- Finding 2: CONFIRMED in code. `triage_append()` lines 129-191: read inside the queue flock, unmatched lines copied byte-for-byte, original ts preserved, only `evidence` refreshes. Live queue check 2026-10-12: 157 rows, 39 open, zero open-slug duplicates.
- Finding 3: NOTHING TO PATCH. `triage_append` is the only queue writer in the sweep (called at line 276). No second helper exists.
- 82090477: zero re-flags since 2026-10-09. Its 5 queue rows are all terminal (1 built, 4 rejected via triage-decide). Underlying envelope fix tracked on BSYS-29418.
- Sweeps clean through 2026-10-12T00:19Z (health.log).

## Delta since the 2026-10-11 pass

The script gained two more noise exclusions on the same axis: `is_test_case_job()` (red test-case runs, lines 92-101) and `FIRE_DRILL_RECIPES` (harness fire drill 82934150 excluded by identity, line 111). Neither touches the three findings; both narrow false alarms further.

## What remains

Nothing to build on the three findings. Adjacent, separate scope: 3 unverifiable verdicts per sweep (wt recipes get errors), and 82862205's fail-count climb (its own open queue row; BSYS-29418 tracks the class).

## Constraints for any future edit

- Keep `triage_append` as the single queue writer with the open-slug in-place update; losing it re-opens the duplicate-row incident class.
- Never hand-edit queue.jsonl; status changes belong to triage-decide.py.
- Knowledge tree is git-backed: revert to the prior commit if the flock rewrite ever misbehaves.
