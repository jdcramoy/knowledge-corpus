# BSYS-29457: workato-health.py sweep hygiene (3 findings) — verification and close-out plan

Ticket: [BSYS-29457](https://workato.atlassian.net/browse/BSYS-29457) (Backlog, Medium, labels V2MOM-FY27 / agent-harness / hygiene). Parent epic BSYS-29454 Agent Harness Operations.

## The ask

Confirm the three sweep-hygiene findings are fully resolved in current code and live behavior, and state what (if anything) still needs a build. The patch landed 2026-10-09; a race-fix rewrite landed overnight 2026-10-11; this pass is the final verification on top of both.

## Current state (live evidence, 2026-10-11)

- Script: `~/.claude/knowledge/scripts/workato-health.py` (mtime Oct 11 03:26 local), still read-only against Workato by design. Sweep outputs in `~/.claude/knowledge/workato-health/`, log at `~/.local/state/fleet/health.log`.
- Finding 1, mock-probe filter: `is_probe_job()` (lines 87-89) plus the verdict branch (lines 233-246). The branch has now FIRED in a live sweep: the `2026-10-11T07:11:43Z` health.log line reads "(136 probe jobs excluded)". The earlier plan's trace-verification gap for AC 1 is closed.
- Finding 2, dedupe-on-append: `triage_append()` (lines 129-191), rewritten overnight with the read inside the queue flock, byte-for-byte copy of unmatched lines, and original ts preserved (only `evidence` refreshes). Live test this pass: I ran a fresh sweep at 2026-10-11T08:12:18Z; it flagged [82862205](https://app.workato.com/recipes/82862205) (fails 42, was 32) and [82951201](https://app.workato.com/recipes/82951201) (fails 3, was 2), and `knowledge/triage/queue.jsonl` holds exactly ONE open row per slug (116 to 118 rows, no open duplicates). New open rows only appeared where the prior row was already built, which is the contract working as designed.
- Finding 3, open-slug check in a second helper: nothing to patch. `triage_append` is the only queue writer in the sweep (called at line 276).
- Recipe [82090477](https://app.workato.com/recipes/82090477): not re-flagged since 2026-10-09. The 5 residue rows for slug `recipe-health-82090477-new-failures` all carry terminal statuses now (1 built, 4 rejected via triage-decide), so no open residue remains.

## Root cause

Root-caused and fixed 2026-10-09: the sweep counted mcp_mock registry probe jobs as prod failures and re-appended a fresh queue row per run for the same open slug. The overnight 2026-10-11 rewrite additionally fixed a read-modify-write race against triage-decide.py that could clobber concurrent rows and restamp ts (seen 03:09:59 Oct 11).

## Proposed fix

Nothing left to build on the three findings. The only open items are adjacent, not this ticket:

- Every sweep still reports 3 "unverifiable" verdicts (wt recipes get errors); worth a separate hygiene look.
- 82862205's fail count climbed 32 to 42 today; it has its own open queue row and existing ticket coverage (BSYS-29418 tracks the collector envelope class).

## Rollback posture and risks

- Local-only script; the knowledge tree is git-backed, so revert the file to the prior commit if the flock rewrite ever misbehaves.
- Any future edit must keep `triage_append` as the single queue writer with the open-slug in-place update; losing it re-opens the duplicate-row incident class.
- No Workato-side writes anywhere in this scope.

## Story points

1 (verification-only; the original patch was a 2-point hygiene build).

## Acceptance criteria

- [x] mcp_mock jobs never counted as new failures (code in place; live trace 2026-10-11T07:11:43Z, 136 probe jobs excluded)
- [x] Two consecutive sweeps produce zero duplicate queue rows for an open slug (full-day evidence plus fresh 08:12:18Z sweep)
- [x] 82090477 stops re-flagging (zero re-flags since 2026-10-09; residue rows terminal)

## UAT Evidence

Record: the 07:11:43Z health.log line with the probe-exclusion count, the back-to-back sweep evidence for dedupe, and the 82090477 row status check. All three captured this pass; nothing further to record at build time since no build remains.

## Sweep false-alarm class: in-session hardening pushes (2026-10-11)

The `recipe-health-82951201-new-failures` alarm (gw_fleet_liveness_sentinel, fails 2->3) was a
false alarm by construction: the three failed jobs (07:05-07:13Z Oct 11, `GET /api/folders?parent_id=`
empty string -> 400 "Must be a number") were intermediate pushes DURING the BSYS-29478 hardening
session itself. The final push fixed it; zero failures after 07:18Z. Trap for the sweep: an hourly
failure-count delta will flag any recipe mid-hardening, because pushes increment fail counts before
the fix lands. Practical rule: before working a `new-failures` row on a recipe with an active open
ticket, check whether the last failures predate that ticket's most recent verified fix job — if so,
close the row via triage-decide instead of planning duplicate work. Row closed `built` 2026-10-11
with job j-AbtKAKPw-L4EgRF-CD as the trace citation.
