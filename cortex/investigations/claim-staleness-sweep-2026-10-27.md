# Claim staleness sweep: 5 oldest active claims
Date: 2026-10-27. Scope: clm-003, clm-005, clm-006, clm-007, clm-009 in ~/.claude/knowledge/claims/claims.jsonl (20 rows, all ids unique). Read-only sweep; nothing outside this report was written.

## Verdict summary

| Claim | Subject | Verdict |
|---|---|---|
| clm-003 | jira-story-points-rule | CONFIRMED |
| clm-005 | dependency-tracker-payload | CONFIRMED (guidance) / bytes not re-measured |
| clm-006 | local-marketplace-loads-in-place | STALE |
| clm-007 | josh-writing-voice-skill | CONFIRMED (substance) / size detail stale |
| clm-009 | process-run-stdin-param | CONFIRMED |

## clm-003: jira-story-points-rule: CONFIRMED
Claim: every Jira ticket gets Story Points (customfield_10057) at creation; BTSUP/HROPS/PSM/MCP exempt (field not on screens).
Evidence:
- Rule present verbatim in ~/Documents/CLAUDE.md ("Jira story pointing" section, customfield_10057, same exempt list).
- jira-story-standards skill is installed and loadable (appears in this session's skill registry).
- Live JQL probe (read-only, BSYS created >= -7d, first 8): Josh-side build tickets all carry points: BSYS-30012=8, BSYS-30008=1, BSYS-30007=2, BSYS-30006=3. Inbound auto-filed tickets (BSYS-30014, BSYS-30013, BSYS-30011, BSYS-30010) have null points, consistent with the convention (points land on Josh-created work, not inbound error/permission tickets).
- Exempt-project half (BTSUP/HROPS/PSM/MCP lacking the field) not probed this run; no contradicting signal.
Not verified: the four exempt projects' screens; older tickets.

## clm-005: dependency-tracker-payload: CONFIRMED (guidance), byte sizes not re-measured
Claim: dependency-tracker get_recipe returns full raw recipe JSON (~226KB, 2.8x AIRO recipe_get); prefer AIRO recipe_get for reading recipe logic.
Evidence:
- workato-dependency-tracker MCP server is attached and healthy (session-start health check: Connected).
- Memory index (workato-dependency-tracker-mcp.md) independently reiterates: blast-radius tools valuable; get_recipe floods context. Corroborates the operative guidance.
- Deliberately did NOT re-call get_recipe to re-measure bytes: the call itself floods context (that is the claim), and the tool call was permission-blocked in this headless run anyway. Re-measurement would only reproduce a known flood.
Not verified: current exact payload sizes (226KB / 2.8x figures are 2026-10-02 measurements).

## clm-006: local-marketplace-loads-in-place: STALE
Claim: plugins installed from a LOCAL directory marketplace load in place from source (edits live at next session start); cache-by-version only applies to git/remote marketplaces.
Evidence (filesystem contradicts the claim):
- josh-mods IS registered as a directory marketplace (known_marketplaces.json: source "directory", path ~/mods).
- But installed plugins point at versioned cache copies: ~/.claude/plugins/cache/josh-mods/workato-guardrails/1.1.0 and .../brain-guard/0.4.1. readlink confirms these are real directories, NOT symlinks into ~/mods.
- Versioned cache for a local marketplace is exactly the behavior the claim says applies only to git/remote.
- Drift proof: ~/mods/workato-guardrails/tests/josh-model-driver.mjs (mtime 2026-10-23) is NEWER than the cache copy (2026-10-21) and differs (source adds an env stub line). A post-update source edit did not propagate to the loaded copy. hooks/register.js is currently identical (last plugin update 2026-10-23T04:34), so runtime hooks are in sync today, but only via explicit update, not in-place loading.
- Stale leftover: cache/josh-mods/workato-guardrails/1.0.0 still on disk next to 1.1.0.
Implication: the correct mental model now is cache-by-version for ALL marketplaces; source edits reach the loaded plugin only via `claude plugin update` (clm-011 already carries the "re-check after any mod edit" habit, which matches this reality).
Not verified: whether /reload-plugins reads from source or cache.

## clm-007: josh-writing-voice-skill: CONFIRMED (substance); frozen size detail stale
Claim: installed user-scope at ~/.claude/skills/josh-writing-voice/SKILL.md; governs all Josh prose; hard rules: no em/en dashes, minimal bold, no emoji, peer register, close on a verdict.
Evidence:
- File exists at the claimed path, user scope. All claimed hard rules present in the live file: no em/en dashes ("Josh does not use em dashes or en dashes. Ever."), minimal bold (lines 23, 234), emoji rules (25, 28, 236), peer-to-peer register (42), verdict closers (116, 147).
- The 7 em/en dash grep hits are inside quoted example text and rule statements, not violations.
- STALE DETAIL: the claim freezes the file at 3,671 bytes (2026-10-06); live file is 19,867 bytes, mtime 2026-10-20. The skill has grown ~5.4x since. Claim substance holds; the byte-size evidence is outdated and should not be cited as current.
Not verified: byte-identity with any .skill bundle (bundle path not probed).

## clm-009: process-run-stdin-param: CONFIRMED
Claim: $.process.run's stdin key is `stdin` (ProcessRunInit), not `input`; types win; {input:...} silently no-ops.
Evidence:
- Current bundled types: ~/mods/workato-guardrails/.claude-plugin/types/claude-code/index.d.ts, ProcessRunInit at line 7667 (exactly the line the claim cites), defines `stdin?: string` ("Text written to the child's standard input, then closed"). No `input` key exists.
- Every live hook call site uses the correct key: { stdin: line } at brain-guard/hooks/register.js:54 and workato-guardrails/hooks/register.js:43, 59, 435, 804-805.
- Behavioral proof the path works today: the build-ledger and verifications jsonl files are actively growing (claims.jsonl, verifications.jsonl, error-events.jsonl all present and populated).
Not verified: nothing beyond the above; claim fully re-checked at type and behavior level.

## Recommended ledger actions (for Josh, not applied here)
- clm-006: mark stale/superseded; the local-marketplace loader now caches by version; edits reach the plugin via claude plugin update.
- clm-007: update the evidence snapshot (file is now 19,867 bytes, mtime 2026-10-20); claim substance unchanged.
- clm-003, clm-005, clm-009: no change needed.
Nothing unverified beyond the per-claim "Not verified" lines above. No platform writes, no file changes outside this report.
