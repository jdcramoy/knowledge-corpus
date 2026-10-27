# harness-backup heartbeat gap — read-only investigation (2026-10-22)

## Verdict

**The heartbeat check-in EXISTS and is not broken today.** The "never checks in"
premise is false as a permanent state — `harness-backup` has 13 rows in
`garden-reports/heartbeat.jsonl` (2026-10-08 → 2026-10-22). What actually
happened: a **deploy-divergence incident** in the window **2026-10-20 → 2026-10-22**
broke the check-in line (and the job's exit code) by deploying a copy of the
script whose personal paths had been redacted to a `/Users/YOUR-USER/` placeholder.
Fixed 2026-10-22 08:11; the 08:12 run validated clean. **The recurrence trap is
still armed** (details in Root cause).

## Chain of custody (script path)

1. `~/Library/LaunchAgents/com.josh.fleet.backup.plist` → `/bin/bash ~/.local/bin/fleet/run-job.sh backup`, nightly 23:33 local. (There is **no** `com.josh.harness-backup` plist — the header comment inside `harness-backup.sh` referencing one is stale.)
2. `~/.local/bin/fleet/run-job.sh backup` → sources `jobs/backup.env` (`CLAUDE_JOB=no`, TIMEOUT 600) → executes `jobs/backup.script`.
3. `~/.local/bin/fleet/jobs/backup.script` →
   a. runs `~/.local/bin/harness-backup` (symlink → `~/.claude/knowledge/scripts/harness-backup.sh`, the actual rsync+git backup), piped to `tail -5`;
   b. **the heartbeat check-in lives HERE, in the wrapper** — `printf '{"ts":"%s","job":"harness-backup"}\n' … | python3 …/atomic_io.py …/garden-reports/heartbeat.jsonl` (the "dream-nightly.sh pattern").
4. `harness-backup.sh` itself contains **no** heartbeat call. On-demand manual `harness-backup` runs never check in by design-as-built.

## Root cause of the outage window (evidence-cited)

- `~/.local/state/fleet/backup.log`, runs of 10-20 23:33 and 10-21 23:41 local:
  `python3: can't open file '/Users/YOUR-USER/.claude/knowledge/scripts/atomic_io.py': [Errno 2] No such file or directory`
- Kit repo commit `4a2fc1d` (2026-10-16 16:45, "fleet-job sync: 28 files"): the
  sync committed `bin/fleet/jobs/backup.script` with paths redacted
  `~` → `/Users/YOUR-USER` **"per pre-commit rule"** — to satisfy
  the kit's pre-commit hook (`.githooks/pre-commit`: `<user>|<user>` in
  added lines ⇒ "personal-identifier" COMMIT BLOCKED, dated 2026-10-15).
- The redacted copy was then synced back OUT to the runtime copy
  (`~/.local/bin/fleet/jobs/backup.script`) — poison flowed kit → runtime. First
  failing nightly run: 10-20 23:33 local (the 10-19 23:33 run was still clean).
- Fix deployed 2026-10-22 08:11:33 (all three copies re-stamped: runtime, kit,
  `~/.claude/knowledge/config/fleet`); the 08:12 run shows `committed + pushed`,
  `done validated`, and heartbeat rows for BOTH names at 2026-10-22T12:13:05Z.

### Blast radius of the broken line — bigger than a missing heartbeat

The bad line exits **rc=2** (python "can't open file"), and being the last
command in `backup.script` it became the script's exit code. Consequences:
1. The **backup itself succeeded** ("committed + pushed" in the log) but the
   runner classified it `ran rc=2` → retried the whole backup →
   `VALIDATION FAILED after retry` → false "job did not run" escalation in
   `fleet-validation.jsonl` (rows 10-17?, 10-21T03:33, 10-22T05:36Z).
2. Because validation never passed, the runner's mechanical success heartbeat
   (job `backup`) also never fired — so BOTH names went dark in the window
   (no rows at all on 10-21 / 10-22T03:xxZ).
3. Each retry re-ran dream-mine + a full second rsync/commit cycle.

## Comparison with a working job (docs-watch)

`docs-watch` is a **prompt job** (CLAUDE_JOB default yes): it has NO inline
check-in — `run-job.sh` writes the heartbeat **mechanically** on validated
success (`write_heartbeat`, job name = fleet job name). `backup` gets that same
mechanical `backup` row when it validates. The inline `harness-backup` check-in
in backup.script is a redundant THIRD identity that only makes sense because
`harness-health.py:64` maps `"backup": ["backup", "harness-backup"]`. The
runner-level contract (2026-10-08: "Success writes the heartbeat MECHANICALLY")
already covers liveness; the inline line adds a second failure surface and, as
seen, can poison the exit code of an otherwise-successful run. jobs with inline
check-ins: backup, decision-inbox, harness-health, queue-drift, regression,
instruction-miner, value-ledger, wave3-nightly — all share this pattern-risk.

## Recurrence risk (LIVE, read-only — not remediated)

- Kit working copy currently has an **uncommitted** modification restoring
  `~` in `backup.script` (`git status: M bin/fleet/jobs/backup.script`).
- The kit pre-commit hook that motivated the redaction is still active
  (`core.hooksPath=.githooks`). The next commit of that file either BLOCKS
  ("personal-identifier" — same as the `COMMIT BLOCKED: personal-identifier`
  lines already visible in backup.log from the auto_push path) or, if an agent
  "fixes" it the same way again, re-deploys YOUR-USER on the next sync.
- Structural conflict: fleet job scripts legitimately contain personal paths,
  but the kit repo forbids them → every fleet-job sync through the kit can
  reproduce this. The canonical copy in `~/.claude/knowledge/config/fleet/`
  (per the run-job.sh DEPLOY CHECKLIST) is correct and never carried YOUR-USER.

## Secondary observations

- `harness-backup.sh` push fallback `git push origin main || git push origin
  master` prints `error: src refspec master does not match any` on josh-orca
  (no master branch) — noise on every main-push failure.
- Heartbeat gap 2026-10-15 (no row that day) predates this incident; log was
  truncated and unexplained — separate minor item, not investigated further.

## Recommended fixes (for Josh to approve; nothing was changed)

1. Best: drop the inline check-in from `backup.script` and let the runner's
   mechanical heartbeat be the only liveness signal (docs-watch pattern), with
   harness-health already accepting `backup`. Simplest and removes the rc=2 trap.
2. If the inline check-in stays: end the script with an unconditional
   `exit 0` after it (or `|| true` the check-in) so a broken check-in can never
   flip a successful backup's exit code.
3. Fix the systemic hook/sync conflict: keep personal-path-free *templates* in
   the kit, or have the sync deploy only from `~/.claude/knowledge/config/fleet/`
   (the declared canonical source), never from the kit repo.
