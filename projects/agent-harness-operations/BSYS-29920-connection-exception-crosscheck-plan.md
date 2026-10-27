# BSYS-29920 technical plan: cross-check dependency-tracker inventory against wt before declaring zero exceptions

Parent epic: BSYS-29454 (Agent Harness Operations — Watcher, Registry & Fleet Hygiene).
Drafted 2026-10-23 by the jira-triage pass.

## Current state

The workato-watchdog agent's connection-health job (step 1 of its procedure,
`~/.claude/agents/workato-watchdog.md` line 45) reads exceptions exclusively
from the dependency tracker (`list_connections` with
`authorization_status: "exception"`). The tracker returns an empty exception
list for the AI Development workspace while `wt connections list` showed 31
dev exceptions on the same night, stable across 3+ nights. Any "zero dev
exceptions" claim sourced from the tracker alone is underreporting by
definition.

## Design (documentation + one procedural line; no code)

Re-verified live 2026-10-23 during dissent review: `wt connections list` (dev,
workspace 3535597) returns 948 connections, 31 exceptions; the tracker's
`list_connections(authorization_status=exception)` returns 0 rows scoped to AI
Development (27 rows unscoped in other workspaces, some with
`loaded_at: 2025-11-25`, eleven months stale). The gap is workspace-specific:
the tracker sees AI Production's 4 exceptions fine and is blind to AI
Development. The story's numbers reproduce.

1. **Watchdog agent file (`~/.claude/agents/workato-watchdog.md`), connection-
   health job:** after the `list_connections` step, add a mandatory cross-check
   step: count wt exceptions COUNT-VIA-SHELL
   (`wt connections list --profile <p> --raw | python3 -c "import json,sys; …"`)
   — never paste the raw 948-row dump into context (documented context-flood
   trap). The report must cite BOTH numbers, tracker count and wt count, and
   when they diverge, the wt count is the reported number and the tracker
   count goes in the report as a known-gap footnote. Run for both profiles;
   the prod comparison matters too while the tracker still sees prod.
2. **Known-gap note** in the same section: the dependency tracker's exception
   filter returns an empty list for the AI Development workspace (workspace
   3535597; observed 2026-10-20 through 10-23, re-verified 2026-10-23 with
   counts above); until the tracker is fixed, it is never the sole source for
   exception counts.
3. **Escalation (root cause, not footnote):** file the tracker sync bug as a
   distinct acceptance criterion — tracker inventory blind to workspace
   3535597 with the repro evidence above (two calls to reproduce). The
   cross-check line is the interim guard; the ticket closes the gap so the
   footnote does not become permanent.

## Acceptance criteria mapping

- AC1 (SOP carries the rule and gap note) → edits 1 and 2 above.
- AC2 (next watchdog report cites both sources) → the cross-check line makes
  the omission impossible; verified on the next scheduled run.
- AC3 (added in plan): tracker sync bug for workspace 3535597 filed with repro
  evidence; closed when tracker counts match wt.

## Estimate

1 point: two doc edits plus the escalation note, well under half a day.
