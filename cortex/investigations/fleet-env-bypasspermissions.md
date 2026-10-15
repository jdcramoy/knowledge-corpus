# Investigation: bypassPermissions flip across fleet job env files
Date: 2026-10-14. Read-only audit, nothing changed. Method: grep over
~/.claude/knowledge/config/fleet/jobs/*.env, prompt-file charter review,
.bak-fusion-20261013 forensics.

## 1. Census

40 env files total; **18** contain `--permission-mode bypassPermissions` (22 do not).

Per-file record (job → agent/persona → class → flip provenance):

| # | Job (env file) | Agent / persona | Charter class | Flip |
|---|---|---|---|---|
| 1 | antigen.env | antigen-drill (canary chaosome) | WRITER — mutates dev canary recipe 82934208 via AIRO (pull/push/stop/start/force-run) | flipped 10-12 |
| 2 | architect.env | estate-architect | ADVISORY — read-only estate review, writes report file only | flipped 10-12 |
| 3 | brief.env | morning brief | ADVISORY — reads all surfaces, writes brief file | flipped 10-12 |
| 4 | corpus.env | corpus maintenance (gardener sub-sweep) | ADVISORY — prompt says "Proposal-only; never auto-mutates" | flipped 10-12 |
| 5 | cortex.env | cortex pulse | ADVISORY — "reports and routes; applies nothing" (knowledge writes via bus_post.py lane) | flipped 10-12 |
| 6 | cost-governor.env | cost-governor | ADVISORY — "Zero-LLM-script day job; you only run the scripts" (scripts do the writes) | flipped 10-12 |
| 7 | dreamer.env | harness-dreamer | ADVISORY — reports/proposes, mode-gated never_auto | flipped 10-12 |
| 8 | gardener.env | brain-gardener | ADVISORY — "never mutates without approval" | flipped 10-12 |
| 9 | evidence.env | evidence (claim hunter) | ADVISORY — "Never mutes, never edits the things it audits"; writes verdict reports | flipped 10-12 |
| 10 | healer.env | healer (watchdog repair phase) | WRITER — dev-scoped (3535597) repairs via allowlist; never prod | PRE-EXISTING |
| 11 | harness-fix.env | harness-fix auto-lane | WRITER — edits harness scripts/queues/hooks (harness-only scope) | PRE-EXISTING |
| 12 | project-dreamer.env | project-dreamer | ADVISORY — "NEVER edits project repos — advisory-only is constitutional" | flipped 10-12 |
| 13 | minutes.env | board-minutes weekly | WRITER (outward, draft-gated) — publishes DRAFT Confluence page via Atlassian MCP | flipped 10-12 |
| 14 | loadout.env | morning load-out assembler | ADVISORY — writes one loadout file + heartbeat append | flipped 10-12 |
| 15 | roi-weekly.env | ROI weekly report | ADVISORY — report writer | flipped 10-12 |
| 16 | ops-autopsy.env | ops autopsy (watchdog sibling) | ADVISORY — autopsy reports + mission-control rows only | flipped 10-12 |
| 17 | uat-sweep.env | UAT sweep (dev 3535597) | ADVISORY — prompt: "READ-ONLY verification sweep... never modify, save, push, stop, or start" | PRE-EXISTING |
| 18 | watchdog.env | workato-watchdog | ADVISORY — "Reports only; never stops, starts, or edits recipes" | flipped 10-12 |

Backup forensics: the 15 files with a clean `.bak-fusion-20261013` were flipped in the
2026-10-12 change; healer/harness-fix/uat-sweep have no bak (carried the flag before it) —
matches the memory's scope note exactly ("15 flipped tonight + 3 pre-existing").

## 2. Comparison against the recorded claim

Memory `cortex-pulse-write-gate.md` (scope note 2026-10-13, gardener F2) says:
"the final count is 18 env files carrying bypassPermissions — 15 flipped tonight +
3 pre-existing (healer/harness-fix/uat-sweep). **All writer-class fleet jobs now uniform.**"

- The **count of 18 is verified live**: 18/40 env files carry the flag today. The 15/3 split
  is verified by backup forensics. INDEX.md carries NO "15 writer-class" claim (grepped —
  the claim exists only in the memory file).
- The **"all writer-class" label is WRONG for at least 8 files, arguably 14.** By Josh's own
  advisory list (watchdog, architect, gardener, evidence, brief, minutes, roi-weekly, uat-sweep),
  **8 of the 18 are advisory-class**: architect, brief, gardener, evidence, minutes, roi-weekly,
  watchdog, uat-sweep. (minutes is on the advisory list but its Confluence draft post makes it
  the most writer-like of the eight — classified writer-outward above.)
- Broadening to charter text, an additional 6 are explicitly proposal-only/read-only
  (corpus "never auto-mutates", cortex "applies nothing", cost-governor "only runs the scripts",
  dreamer never_auto, project-dreamer "never edits project repos", ops-autopsy reports-only,
  loadout single-file). On charter, only **4 of 18 are genuinely writer-class against a live
  system**: antigen (dev recipe mutations), healer (dev repairs), harness-fix (harness tooling),
  minutes (outward Confluence draft).
- **Why advisory jobs got the flag anyway:** the 2026-10-12 change was fixing the
  sensitive-path write-gate (knowledge/** writes auto-denied headless), not granting mutation
  rights. Report-writing agents (dreamer, evidence) were blocked for 2 nights writing their
  own reports. The flip silenced the gate for everyone rather than routing each job through
  script lanes — census option C, which the same census explicitly marked "(Not recommended)...
  governance regression."

**Verdict on the recorded claim:** count accurate (18 = 15+3, live-verified); classification
inaccurate — "all writer-class" is true for ~4 of 18, false for 8 by Josh's list and 14 by
charter. The flag on advisory jobs is a write-gate workaround, not a write requirement.

## 3. Walk-back plan (DRAFT — nothing executed)

Root blocker for any revert: the built-in sensitive-path screen denies headless writes to
`~/.claude/knowledge/**` (no prompter in launchd context). A job that must land a file in
knowledge/ under default mode fails silently unless its writes go through a sanctioned
allowlisted script lane (bus_post.py, run-job.sh write_heartbeat) or move out of the dot-dir.

### Tier A — could revert to `--permission-mode default` NOW (low risk)
- **cost-governor** — the session "only runs the scripts"; all file writes happen inside
  cost-governor.py/roi-report.py (direct file I/O, no Write-tool screen). Re-run risk: near
  zero. Verify one run lands the report after flip.
- **cortex** — write-gate doctrine already mandates the bus_post.py lane; pulse prompt should
  be amended (census option A) to forbid raw `cat >>`/Write to knowledge/** and route the
  attention-queue rebuild + heartbeat through scripts. This is the job whose write-gate
  history started the whole investigation — reverting it re-closes the loop.

### Tier B — revert ONLY after a script-lane (census option A) or path-migration (option B)
These write report files directly to knowledge/** headless; under default mode they'd hit the
exact denials that caused the 2-night dreamer/evidence outage. Nothing breaks at the Workato
layer — what breaks is the artifact not landing:
- architect, brief, corpus, dreamer, evidence, gardener, loadout, ops-autopsy, project-dreamer,
  roi-weekly, uat-sweep, watchdog.
Per-job breakage if flipped without a lane: architect → no estate review file; brief → no
morning brief (Josh's primary orientation surface); corpus → no index-drift deltas; dreamer →
no dream report/proposals (the original casualty); evidence → no claim-verification verdicts;
gardener → no garden report; loadout → no loadout file + heartbeat gap; ops-autopsy → no
autopsy + no escalation-card mission-control row; project-dreamer → no architecture proposal;
roi-weekly → no ROI report; uat-sweep → sweep results files not written (proposed-fix text
lost); watchdog → P1 report not written (downstream healer loses its input, since healer reads
watchdog-$(date +%F).md first).
- **uat-sweep note:** its prompt is explicit read-only-forever; it needs the flag solely for
  results-file writes — a strong candidate for the first option-A conversion (writes could go
  through a small allowlisted sweep-writer script).

### Tier C — genuinely need elevated writes; keep bypassPermissions (or scope it)
- **antigen** — mutates + stops/starts/force-runs dev canary recipe 82934208 through AIRO MCP.
  Under default mode every AIRO mutation prompts → drill silently can't infect. (Its own
  prompt turns a non-failing canary into a finding, but an un-run drill is just a dead job.)
- **healer** — dev-scoped auto-repairs via repair-allowlist.json; the whole point is unattended
  writes. Reverting breaks the watchdog repair phase entirely. (Prod is separately protected —
  prompt forbids it, and prod MCP isn't attached to these jobs.)
- **harness-fix** — edits harness scripts/ledgers/hooks; same unattended-write rationale.
- **minutes** — creates a DRAFT Confluence page via Atlassian MCP (external write). Could
  arguably run under default mode since MCP create prompts... but headless prompt = auto-deny =
  no minutes. Keep until an unattended-safe draft path exists; the DRAFT-only rule is the
  real gate, not the permission mode.

### Recommended sequencing
1. Revert Tier A (cost-governor, cortex) with one verified run each.
2. Build the option-A script-lane conversion, then migrate Tier B one job per night with
   next-morning artifact checks (heartbeat.jsonl is the canary for "did it land").
3. Leave Tier C as-is; revisit minutes if a draft-writer script becomes available.
4. Correct the memory's "all writer-class" sentence to the 4-writer/14-advisory reality so the
   next audit doesn't inherit the mislabel.

## What was NOT verified
- That run-job.sh passes EXTRA_ARGS straight through to `claude` (read the comment header
  only, not the exec line) — if EXTRA_ARGS is dropped somewhere, the census overcounts real
  permission behavior.
- Whether any of the 22 non-bypass env jobs write to knowledge/ and are silently degraded
  today (not audited).
- That MCP tool calls (AIRO/Atlassian) inside these headless sessions actually prompt under
  default mode rather than being allowlisted by project settings — Tier B/C breakage claims
  rest on the write-gate memory's observed denials plus prompt-mode semantics, not a fresh
  controlled test.
