# Dropped-session fallout sweep (48h cohort, read-only)

Swept 2026-10-18 by read-only investigation session. Cohort: every session flagged in
`mission-control/dropped-sessions.jsonl` within 48h (86 rows, the live hook reports 76 after
dedup) — each transcript under `~/.claude/projects/` parsed in full, final tool call classified.
Changed nothing except this file.

## Verdict first

The 48h "dropped" cohort is mostly NOT unfinished work. Classifying each session by its final
tool call: 48 ended on their normal heartbeat append (a completed fleet pulse), 6 recorded a
mission-control closeout, 11 ended on a benign read Bash call, 7 on other non-mutating calls.
The durable-state fallout is real but lives in the DETECTOR and the REGISTRY, not in the dead
sessions. Only 3 sessions in the cohort died with an unverified write to a shared knowledge
file as their literal last action, and spot-checks found all 3 files complete. No Workato
asset mutation appears in any session tail. No Jira/Slack mutation was left unaccounted. Zero
sessions in the cohort meet the POSSIBLE UNFINISHED PROD STATE bar.

## Top 3 fallout classes by blast radius

### 1. Mission-control registry pollution — 191 never-closing auto-absorb rows
Every flagged session gets an auto-absorb row `dropped-<session-id>` written as in-flight into
`~/.claude/knowledge/mission-control/registry.json`. Nothing ever closes those rows: 191 exist,
158 older than 48h, 0 resolved. The registry now holds 207 in-flight rows of which only 16 are
real work — ~92% noise. Everything that reads the registry (board.html, /today, hourly cortex,
morning brief) drowns. Example: `registry.json:1271` (`"workstream": "dropped-6085a963-eaf"`)
and the 190 rows like it; by contrast the real rows (`hr-genie`, `google-semantic-mcp`,
`gws-semantic-autonomy`) are buried under them. This is the meta-fallout: the gap-recording
mechanism became the largest durable-state corruption in the file.

### 2. Deadman false positives — clean sessions flagged, feeding class 1
Root cause already diagnosed (cite:
`cortex/investigations/fold-dropped-session-false-positives.md`): the detector anchored the
quiet window on transcript FILE mtime, which Claude Code inflates with post-hoc
`last-prompt`/`cost-state` appends, so ~70% of flags were clean sessions. The fix IS deployed
(`~/.local/bin/session-shadow.py:370-401`, `_last_transcript_ts()` now anchors on the last
timestamped line) but detections continue post-fix — 25 on 10-18 alone. Residual defect: the
sweep treats any quiet transcript as dead, including sessions that COMPLETED cleanly and are
merely still open in a terminal (evidence: in this cohort 48 sessions ended on their heartbeat
append and 6 recorded closeouts, yet all 86 were flagged). Cost: Josh's attention plus 86
phantom absorb-rows in 48h. Example: session 5526b97a-4a3 — recorded a closeout for
`hr-genie-cutover` mid-session, ended on its watchdog heartbeat, still flagged as dropped.

### 3. Unverified final writes to shared knowledge files
Three cohort sessions whose literal last action was a write into `~/.claude/knowledge/` with no
read-back before death — the exact shape that produces half-written durable files:
- f2206864-3a8 — final action: Edit to `knowledge/projects/google-slides-mcp.md` (91KB file;
  spot-check tail ends mid-word on a coherent code-comment, likely intact but unverified by
  the writer)
- 21cd94ae-e0a — final action: heredoc write to
  `knowledge/cortex/investigations/bsys-29757-82121168-hotfix-landing.md` (6.4KB, tail verified
  complete — ends with the Fix-B-staged note)
- b1b19500-ef2 — final action: heredoc write to
  `knowledge/cortex/investigations/wave3-validator-stub-keying.md` (4.8KB, tail verified
  complete)
Blast radius is capped today because the files spot-check clean, but the class is the only one
in the cohort that can silently truncate shared knowledge, and the heredoc-via-Bash write path
has no Write-tool failure surface to catch it.

## Other findings

- **scheduled_tasks.json duplicate drift (concrete, fix-worthy):** FOUR identical
  `[harness-docs-sync-nightly]` tasks share cron `57 6 * * *` —
  `scheduled_tasks.json:63` (017afeef), `:111` (cca9ad06), `:123` (a1c65627), `:134`
  (504715c9). The task's own prompt says "self-rearm — re-create this scheduled task"
  (recurring tasks expire after 7 days), so every re-arm pass that dies between CronCreate and
  CronDelete — or simply runs before the old one expires — leaves a duplicate. Four copies now
  run the same Confluence publish nightly; four concurrent `updateConfluencePage` flows are a
  clobber risk on the same pages.
- **Jira/Slack/Workato mutations: clean.** 11 cohort sessions touched Jira mutations; the
  sampled tails (db615126-d58: BSYS-29727/29765 edits + transitions + Slack announcement) show
  completed, outcome-tracked actions. 4 sessions posted Slack; `slack-posts.jsonl` shows 0
  pending/draft-waiting. Zero Workato mutation tools (recipe_builder_*, data_table_*,
  blueprint_*) appear in any of the 86 tails; zero `wt recipes` lifecycle Bash calls.
- **attention-queue.md churn:** 31 cohort sessions rewrote
  `knowledge/cortex/attention-queue.md`, but each pulse rewrites it wholesale by design —
  self-healing, no clobber fallout.
- **No orphaned background dispatches:** no cohort session's final action was an Agent launch
  or `nohup claude` dispatch; the three dispatchers (b6a2031d, 90ed4349, 5526b97a) all logged
  after dispatching. The dispatch chain b6a2031d -> 07519f8a (the deadman-gap investigation)
  actually completed and wrote its report.

## Safe to ignore vs Josh-verify

SAFE TO IGNORE (~83 of 86): the 48 heartbeat-enders, the 6 closeout-recorded sessions, the
benign-read tails, and all cortex-pulse rewrites of attention-queue.md. Their work landed;
only the flag is wrong.

JOSH-VERIFY (3 items):
1. `knowledge/projects/google-slides-mcp.md` — f2206864's final Edit was never read back by
   the writer. Skim the last trap entries for truncation.
2. scheduled_tasks.json — delete 3 of the 4 duplicate `harness-docs-sync-nightly` tasks (keep
   017afeef or the newest), otherwise tonight runs 4x.
3. registry.json — bulk-close the 191 `dropped-*` rows (a one-line reconcile pass), or /today
   and the board stay ~92% noise.

## Unverified
- Pre-10-16 flag cohorts (the 634-row backlog) not re-audited here; scope was the 48h cohort.
- The deadman's post-fix residual FP rate not quantified — mechanism inferred from the
  post-fix detection counts plus the clean-tail evidence, not from re-running the sweep.
