# error-sensor.py phantom-rate investigation
**2026-10-27 · read-only audit · corpus: `~/.claude/knowledge/error-events.jsonl` (818 events, 2026-10-26 21:13 → 10-27 01:07, ~4h window — file rotates fast)**

## Verdict
**~40% of captured "errors" are phantom.** Refined classifier over all 818 events: 364 true errors
(44.5%), 149 confirmed phantom (18.2%), 305 ambiguous (37.3%); a 20-row hand-audit of the ambiguous
bucket found ~65% phantom → **estimated phantom rate 38–45% (call it 4 in 10)**. True-error share is
~44–50%. The sensor roughly doubles its log size with misclassified success output.

## The cited evidence — all four verified clean
| sig_hash | rows | signature | actual payload |
|---|---|---|---|
| 181bb101b61c | 4 | `Read\|<q> <q> <q> <q>...` | Successful Read of `~/.claude/agents/cortex.md` |
| 3fee36af9d84 | 1 | `Bash\|<q> cortex constitution...` | `cat` of a markdown doc (clean stdout) |
| faad9715520b | 1 | `Bash\|<q> <n> <n> <n>t<n>...` | Watchdog report stdout, clean |
| e942bc622aba | 4 | `Bash\|<q> <q>ts <q><n>...` | grep/JSON analysis stdout, clean |

## Why the predicate fails (error-sensor.py `is_error_payload`)
1. **Substring scan over success payloads.** The structured branches (`is_error`/`error`/`stderr`)
   only run when `tool_response` is a dict. List/str payloads (every MCP text-array success, every
   Read result) fall straight through to the `ERROR_MARKERS` scan — 'not found', 'failed', 'invalid',
   'http 4', 'permission denied' — over the first 4,000 chars of output. Clean content trips it
   constantly: recipe DSL echoes contain "invalid", Jira issue text contains "failed", docs contain
   "not found", grep results quote the error ledger itself.
2. **Self-referential capture (proven live this session).** `cat error-sensor.py` was logged as an
   error — the file's own marker list matches itself. Reads of agents/*.md, error-canon files, and
   analyses of error-events.jsonl are guaranteed phantoms.
3. **Success-shape payloads captured wholesale.** Cluster `584ab34f5c81` is 23 events of
   "Recipe retrieved successfully" (AIRO recipe_get) — the marker sat inside the echoed recipe DSL.
   Write-success payloads (`{"type":"create",...}`), addCommentToJiraIssue successes, and the
   harness notice "Shell cwd was reset to..." (top cluster `38767f0a1162`, 29×) are all logged.
4. **Bash stdout with exit 0 still scanned.** Genuinely useful for `HTTP 404` payloads surfacing on
   stdout, but the same scan catches any grep/analysis output mentioning "failed".
5. **Signature collapse amplifies it.** `normalize()` reduces every quoted string to `<q>` then
   truncates to 40 chars, so unrelated clean outputs share a hash (`Bash|<q>` cluster, 15×; the four
   cited hashes are `Read|<q>...` buckets). Clusters then feed the promoter, and
   **`canon_match`'s 0.7 overlap-coefficient on tiny token sets fires phantom CANON ERROR injections**
   into live sessions — observed twice during this investigation (sig 08344cb53c2a, "seen 15x across
   12 sessions", no lesson).

## Marker frequency among pure-prose phantoms
`failed` 124 · `http 4` 100 · `not found` 98 · `invalid` 50 · `permission denied` 22 · `rejected` 15.

## Blast radius
error-canon.jsonl and fired.jsonl accumulate phantom signatures with 3+ counts → future sessions
receive bogus "CANON ERROR — do not blind-retry" injections for clean outputs, polluting attention
and burning context. The promoter's `--record` loop then invites "lessons" for non-errors.

## Recommended fixes (not applied — read-only)
1. Drop the bare substring scan for non-dict payloads, or restrict markers to unambiguous ones
   (Traceback, `Exit code [1-9]`, `command not found`, `zsh:`/`bash:` prefixes, `is_error: true`).
2. For dict payloads with exit 0 + empty stderr, never scan stdout.
3. Whitelist harness notices ("Shell cwd was reset", wt PROD banners).
4. Signature: extract the error LINE first, then normalize; never emit bare `<q>`-only signatures.
5. `canon_match`: require exact sig_hash (or overlap ≥ 0.7 AND ≥ 3 shared tokens, min sig length 5).
