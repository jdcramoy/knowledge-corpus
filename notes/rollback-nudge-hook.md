# Rollback-rehearsal nudge hook — SPEC ONLY (not yet wired)

Purpose: make `rollback-rehearsal` fire by default. A `recipe_builder_push`
(dev AIRO server) or a recipe code change that completes without a rehearsal
entry in `~/.claude/knowledge/garden-reports/rollback-rehearsals.jsonl` gets
a one-line nudge appended to the transcript. The mod edit itself is Josh's.

## Matcher

PostToolUse hook, two matchers (either one):

```
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__workato-airo-mcp-server__recipe_builder_push",
        "hooks": [ { "type": "command", "command": "<script>" } ]
      },
      {
        "matcher": "Bash",
        "hooks": [ { "type": "command", "command": "<script>" } ]
      }
    ]
  }
}
```

- Matcher 1 catches the AIRO MCP push directly (dev server
  `workato-airo-mcp-server`; deliberately NOT `workato-airo-mcp-prod` —
  prod pushes are never nudged, they're gated elsewhere).
- Matcher 2 (Bash) inspects the tool_input/command string for recipe-code
  writes (`wt` recipes commands with push semantics, `workato push`,
  `recipe_builder_push` via CLI) before the script's cheap exit.

## Script pseudocode

```
input: read stdin JSON -> { tool_name, tool_input, tool_response, session_id, ... }

1. DETERMINE recipe_id:
   - MCP matcher: parse tool_input (session_id/recipe_id fields of the
     recipe_builder_push payload) and/or tool_response for the recipe id.
   - Bash matcher: regex the command for a recipe id argument; bail if none.
2. BAIL (exit 0, no output) when any of:
   - tool_response indicates error (push failed => nothing to rehearse yet)
   - recipe_id not found
3. CHECK LEDGER:
   now = current epoch
   scan last ~50 lines of rollback-rehearsals.jsonl:
     entry counts iff recipe_id matches AND ts is within THIS TURN
     (turn window: stdin JSON may carry transcript path; practical cheap
     proxy: entry.ts within the last 5 minutes AND entry.current_version
     == current recipe version from `wt recipes versions <id>` fallback —
     the hook may not know turn boundaries, so a recent same-version
     entry counts as rehearsed)
4. IF rehearsed: exit 0 silently.
5. ELSE nudge (single line, stdout, exit 0 — never block):
   "ROLLBACK REHEARSAL MISSING for recipe <id>: run
    python3 ~/.claude/knowledge/scripts/rollback-rehearse.py --recipe <id>
    — a fix without a rehearsal ledger entry is not done."
```

## Constraints

- Read-only + stdout nudge; the hook NEVER runs the rehearsal itself and
  NEVER appends to the ledger (rehearsals must be real, not hook-fabricated).
- Dev-only: if the push profile resolves to prod (workato-prod profile or
  prod MCP server), suppress the nudge.
- Total budget: < 200ms happy path (one file tail, no wt call unless the
  ledger is ambiguous).
- Failure mode is silence: any script error exits 0 with no output — a
  broken nudge hook must not block pushes.
