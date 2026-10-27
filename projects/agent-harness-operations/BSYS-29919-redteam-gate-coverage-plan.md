# BSYS-29919 technical plan: extend red-team gate enforcement beyond the promotion push surface

Parent epic: BSYS-29454 (Agent Harness Operations — Watcher, Registry & Fleet Hygiene).
Drafted 2026-10-23 by the jira-triage pass. Revised after dissent review (v2).
Grounded in a full read of `~/.claude/hooks/redteam-guard.sh` (131 lines).

## Current state (read from the hook, not from the ticket)

`redteam-guard.sh` is a **Stop** hook: it reads ONE transcript (the main session's
`transcript_path`), scans tool_use records for (a) prod MCP write tools
(`mcp__workato-airo-mcp-prod__*` mutation allowlist) and (b) prod CLI writes
(`wt-prod`/`workato-prod` mutation verbs; plain `wt` only matches
`manifests import`). If prod writes happened and no verdict text
(`knowledge/redteam/` or verdict language) appears anywhere in the transcript,
it blocks the stop once.

Blind spots, verified:

1. **CLI matcher gap (the real one).** `is_prod_cli_write` matches plain `wt`
   ONLY for `manifests import`. `wt --profile josh-prod packages import`,
   `wt --profile josh-prod api PUT/POST/DELETE`, and
   `wt --profile josh-prod recipes push/start/stop` all evade the gate — and
   the ahq-prod-recipes skill prescribes exactly that invocation style.
   (Note: `manifests create` is deliberately NOT a gate surface — the standing
   order mandates creating the manifest AT BUILD START, before any verdict can
   exist; gating creation would invert the mandated workflow. Same for
   `packages export`: staging, not promotion.)
2. **Transcript gap.** Subagent transcripts live at
   `<project-dir>/<session-uuid>/subagents/agent-*.jsonl` (confirmed on disk)
   and are never scanned. A dispatched subagent doing the prod push escapes
   the gate entirely.
3. **Jira-surface gap.** Filing the promotion package comment on a deployment
   ticket (`addCommentToJiraIssue`) is invisible to the Stop hook's detection,
   so a promotion can be announced end to end without a verdict anywhere in
   the loop.

## Design (Stop-hook extension only; no PreToolUse deny)

The first draft proposed a PreToolUse deny gate. Dissent review killed it:
the mid-flight deny creates ordering traps (it can block the verdict's own
publication comment; its key-lookup mismatches the governing-ticket verdict
naming) and duplicates the Stop hook's job in a hot path. v2 extends the Stop
hook instead — detection surfaces widen, the block semantics stay exactly as
today (block the stop once, demand the verdict):

1. **Matcher fix in `is_prod_cli_write`:** resolve the effective profile from
   `~/.workato/profiles` (`environment: production` — covers `josh-prod`,
   `bt-prod`, `hr-prod`; do NOT hardcode one profile string), also honor the
   `WORKATO_PROFILE` env var (stripped by the env-prefix sanitizer today), and
   add `PATCH` to the `api` verbs in MUT_VERBS (PUT|POST|DELETE misses the
   config-flip surface the micro-target doctrine names). Closes the packages
   import / api write / recipes push evasion across ALL prod profiles.
   `manifests create` and `packages export` remain deliberately outside the
   matcher (staging surfaces, mandated before any verdict exists).
2. **Subagent scan:** after the main transcript loop, glob
   `Path(transcript_path).with_suffix('') / 'subagents' / 'agent-*.jsonl'` and
   run the same detection over each. Verdict evidence may come from the main
   OR a subagent transcript (a dispatched red-team agent's verdict file, once
   reported, counts).
3. **Jira-comment detection:** add `mcp__atlassian__addCommentToJiraIssue`
   tool_use records to the Stop hook's scan — a comment counts as prod-bound
   only when BOTH (a) the comment targets an issue that is a deployment/
   promotion record (Deployment Request type, or a Story/Bug whose summary or
   the comment body carries a manifest ID AND a package/promotion verb) and
   (b) no `knowledge/redteam/` verdict exists for the governing ticket. The
   `manifest-review` skill's routine Blocking/Non-Blocking review comments
   MUST NOT trip this — the negative pass case is a required fixture, not a
   nice-to-have (pattern-over-content matching is the exact failure class the
   2026-10-12 hook fix deleted; a live misfire of that class was caught by the
   dissent reviewer during this very review). Composes with the existing
   `jira-comment-guard.py` PreToolUse hook (formatting/voice domain) without
   overlapping it. Known residual (accepted, noted): cross-subagent
   `verdict_seen` is global — a prod write in subagent A plus an unrelated
   verdict in subagent B passes; tightening that is follow-up, not launch
   scope.
4. **Fixtures (new):** `~/.claude/hooks/tests/` does not exist today — the
   fixture harness is created here: `test-redteam-guard.sh` runs the hook
   against synthetic transcripts, block and pass per surface (prod-profile
   packages import via each of the three prod profiles and via
   `WORKATO_PROFILE=`, `--profile <name>` AND `--profile=<name>` spellings,
   subagent prod write, promotion comment, manifest-review comment NEGATIVE
   pass case, prod-profile READ pass case, clean dev session).

## Risks

- **Prod-profile detection false positives:** a `--profile josh-prod` READ
  (`wt recipes get ... --profile josh-prod`) must not count. Mitigation:
  MUT_VERBS already requires a mutation verb in the segment; fixtures cover a
  prod-profile read as a pass case.
- **Stop-hook latency** from the subagent glob: bounded (scan only files
  touched in the session window; the hook already streams line-by-line).

## Acceptance criteria mapping

- AC1 (Jira promotion-comment gate) → design item 3, fixture case C.
- AC2 (`manifests create` gate) → REVISED: the story's AC2 as written would
  gate the mandated build-start operation. The corrected criterion: prod-bound
  `packages import` (any profile spelling) is gated, `manifests create` is
  explicitly exempt. Fixture case A.
- AC3 (subagent transcripts) → design item 2, fixture case B.
- AC4 (fixtures) → the new test harness, block/pass per surface.

## Estimate

2 points (revised from 3): matcher fix + subagent glob + detection extension
plus fixture harness, ~2 dev-days.

## Where I could be wrong

The first draft proposed a PreToolUse deny gate and was broken in dissent
review (gating `manifests create` inverts the mandated build-start manifest
order; `wt manifests export` does not exist as a subcommand; the real evasion
was the plain-`wt` profile gap). v2 above is the post-review design, re-reviewed
STANDS with amendments folded in. The residual judgment calls: whether
Josh wants hard prevention (PreToolUse deny) rather than stop-blocking, and
whether `jira-comment-guard.py` should host the promotion-comment check instead
of the Stop hook. Both are kickoff decisions, not blockers.
