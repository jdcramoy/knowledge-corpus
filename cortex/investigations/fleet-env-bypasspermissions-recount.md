# Investigation: fleet bypassPermissions recount (2026-10-14)

Read-only recount from primary sources; nothing changed. Resolves the scope
contradiction between the gardener bus post (2026-10-14 03:15Z, thread
harness-dreamer-2026-10-13: "18 agent environments with bypassPermissions,
including report-class agents") and the memory scope note
(cortex-pulse-write-gate.md, gardener F2: "15 writer-class environments").

## 1. Verdict first

**18 is the correct COUNT of fleet env files carrying bypassPermissions —
but it is NOT a count of writer-class environments.** Only 4 of the 18 are
writer-class by charter; 14 are advisory/report/sweep-class. The "15
writer-class" phrasing in the memory scope note conflated "15 files flipped
on 2026-10-12" with "15 writer-class". Both counts refer to the same 18
files; the class label was wrong, not the number. Separately, ONE
non-fleet carrier exists outside every prior count: the interactive root
`settings.json` `permissions.defaultMode` is `bypassPermissions`, so every
interactive session inherits bypass by default. Total distinct carriers:
18 fleet + 1 interactive root = 19.

## 2. Primary-source sweep (what was enumerated)

| Source | Files checked | Carriers |
|---|---|---|
| Fleet job env files `~/.claude/knowledge/config/fleet/jobs/*.env` | 40 | **18** (`--permission-mode bypassPermissions` in EXTRA_ARGS) |
| Agent frontmatter `~/.claude/agents/*.md` | 12 | 0 (no agent .md sets a permission mode; only prose mention in cortex.md) |
| `~/.claude/settings.json` | 1 | **1** (`"defaultMode": "bypassPermissions"` at line 143, permissions block) |
| `~/.claude/settings.local.json` | 1 | 0 (allow-list only, no defaultMode) |
| Project settings (Documents, workbench, knowledge) | 5 checked | 0 (files absent or no defaultMode) |
| MCP configs `~/.claude/mcp-*.json` (5) | 5 | 0 |
| Launchd plists `~/Library/LaunchAgents/*.plist` (~60) | all | 0 directly — plists delegate to `~/.local/bin/fleet/run-job.sh`, which sources the env files above; the flag lives only in the env files |

## 3. Exact per-env list (fleet, 18 carriers of 40)

Classification is charter-based (prompt file text), consistent with
fleet-env-bypasspermissions.md (2026-10-14).

| # | Env file | Class | Basis |
|---|---|---|---|
| 1 | antigen.env | WRITER | mutates dev canary recipe 82934208 via AIRO |
| 2 | architect.env | REPORT | estate review, writes report file only |
| 3 | brief.env | REPORT | morning brief file |
| 4 | corpus.env | SWEEP | "Proposal-only; never auto-mutates" |
| 5 | cortex.env | REPORT | "reports and routes; applies nothing" |
| 6 | cost-governor.env | SCRIPT-RUNNER | "Zero-LLM-script day job; you only run the scripts" |
| 7 | dreamer.env | REPORT | mode-gated never_auto |
| 8 | evidence.env | REPORT | "Never mutes, never edits the things it audits" |
| 9 | gardener.env | REPORT | "never mutates without approval" |
| 10 | healer.env | WRITER (pre-existing) | dev-scoped repairs via allowlist |
| 11 | harness-fix.env | WRITER (pre-existing) | harness scripts/queues/hooks |
| 12 | loadout.env | REPORT | one loadout file + heartbeat append |
| 13 | minutes.env | WRITER-outward (flipped) | publishes DRAFT Confluence page |
| 14 | ops-autopsy.env | REPORT | autopsy reports + mission-control rows |
| 15 | project-dreamer.env | REPORT | "NEVER edits project repos — advisory-only" |
| 16 | roi-weekly.env | REPORT | ROI report file |
| 17 | uat-sweep.env | SWEEP (pre-existing) | "READ-ONLY verification sweep... never modify, save, push, stop, or start" |
| 18 | watchdog.env | REPORT | "Reports only; never stops, starts, or edits recipes" |

**Class totals: 4 writer (incl. 1 outward), 12 report, 2 sweep,
1 script-runner.** "Writer-class": 4. "Flipped on 2026-10-12": 15 (rows
without "(pre-existing)"). Neither equals the other; both sum with the 3
pre-existing to 18.

## 4. The 22 non-carriers (fleet)

backup, benchmark, bus-actuate, canary, decision-inbox, docs-watch,
frontier-nightly, gym, harness-health, index-budget, instruction-miner,
jira-triage, kb-audit, queue-drift, replay-sample, restore-drill,
room-sweep, synaptic-strength, titer-report, turn-audit, value-ledger,
wave3-nightly.

## 5. The extra carrier the fleet census misses

`~/.claude/settings.json` → `permissions.defaultMode: "bypassPermissions"`.
Backup forensics: `settings.json.bak-bypass` (mtime Oct 8 03:19) has
`"defaultMode": "auto"`; `settings.json.bak` (Oct 9 12:56) already has
`bypassPermissions`. So the interactive root has run bypass-by-default since
~Oct 8-9 — it PREDATES the 2026-10-12 fleet flip and is independent of it.
Any classification of "the fleet is uniform in bypass" understates the real
surface: interactive sessions run bypass by default too.

## 6. Reconciliation

- Gardener bus post ("18 agent environments... including report-class"):
  **correct on both count and framing.**
- Memory scope note ("final count is 18... All writer-class fleet jobs now
  uniform" + earlier "15 writer-class"): count correct, label wrong. 18 is
  15 flipped + 3 pre-existing; writer-class is 4, not 15 or 18. The word
  "writer" was doing no work in that sentence — what is actually uniform is
  "all fleet jobs that write reports headless", which is why 14 advisory
  jobs carry the flag: the sensitive-path write-gate workaround, not a
  mutation grant.

Nothing was modified. Sources re-read 2026-10-14; per-file grep evidence in
transcript.
