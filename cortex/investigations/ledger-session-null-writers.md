# Investigation: session:null on orca-browser / workato-cli build-ledger rows

- Date: 2026-10-20 (investigating 2026-10-21T01:1xZ ledger window; wall-clock UTC offset noted)
- Scope: read-only. Nothing else touched.
- Verdict: **workato-guardrails plugin, hook 11 (CLI/ORCA ledger) omits the `session`
  field entirely from its ledger entry.** Hook 10 (AIRO mutations) sets it correctly.

## Symptom (verified in ledger)

Rows at 01:11–01:16Z window in `~/.claude/knowledge/build-ledger.jsonl`:

- `kind:airo-mutation` → `"session":"gslides-carrier-fix"` ✓
- `kind:orca-browser`, `kind:workato-cli` → **no `session` key at all** in the raw JSONL
  (consumers reading `.session` see undefined, rendered as null).

## The writer

`~/.claude/plugins/cache/josh-mods/workato-guardrails/1.0.0/hooks/register.js`
(user-scope plugin, v1.0.0 active per installed_plugins.json). It registers two
independent `tool.call` ledger hooks, both appending via `ledgerAppend()` →
`scripts/atomic_io.py`:

1. **Hook 10 — AIRO mutations** (line ~660): builds entry with
   `session: sid` where `const sid = callingSession(e)`
   (fallback chain: `e.session_id` → `CLAUDE_SESSION_ID` → `ORCA_SESSION_ID` → null).
   ✅ Works — hence real session names on airo-mutation rows.

2. **Hook 11 — CLI/ORCA via Bash sniffing** (line ~889, `on('tool.call', { tool: 'Bash' })`):
   entry is built as `{ kind, command, recipe_id, ticket }` — **no `session` field,
   no `callingSession(e)` call, no tool_use_id.** ❌ THE DEFECT.
   The helper exists in the same file (line ~70) and would work unchanged here;
   the author of hook 11 simply never wired it in. Not an env-var problem, not a
   data-availability problem — a plain omission in the entry literal.

## History

Same omission present in 0.7.2 and 0.7.1 hook copies (`.bak-20261009` identical in
this region) — the field was never there, in any shipped version. The comment at
line ~65–69 (`callingSession` definition) even documents a prior null-session
incident (22:47:02Z prod delete row), so hook 10 was patched; hook 11 was missed.

## Fix (one line, in hook 11's ledgerAppend entry object)

```js
await ledgerAppend($, {
  kind: kind,
  command: cmd.slice(0, 200),
  session: callingSession(e),      // <-- ADD (already defined at top of file)
  recipe_id: ids.length ? Number(ids[0]) : null,
  ticket: currentTicket,
})
```

Optionally add `tool_use_id: e.tool_use_id ?? null` for transcript correlation
parity with hook 10. Read-only session — fix NOT applied; left for a build ticket.
