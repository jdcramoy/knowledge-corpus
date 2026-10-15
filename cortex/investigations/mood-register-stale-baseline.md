# Investigation: stale mood register — `dreams/mood.json` frozen since 2026-10-08T06:38

- **Filed:** 2026-10-12 ~21:00Z · one-job bounded brief, READ-ONLY (nothing changed outside this file)
- **Trigger:** triage slug `mood-register-stale-baseline` (queue line 202, filed 20:23Z); decision-inbox "mood register is ~100h stale" open since rev h
- **Verified state of file:** arousal 0.3, exploration 0.3, risk_tolerance 0.2, verification_depth 0.9, reason "restore baseline after test", set_by "me", set_at 2026-10-08T06:38:55. File mtime = set_at (confirmed via `stat`) — not a single write since.

## 1. Who writes mood.json, and who was supposed to run the restore

**Writers:** exactly one script — `~/.claude/knowledge/scripts/mood.py`, via its two subcommands (`set`, `decay`). No other script, hook, launchd plist (checked all 40+ in `~/Library/LaunchAgents/`), crontab entry, or fleet job prompt (`~/.local/bin/fleet/jobs/*.prompt|script`) references mood.json or mood.py. Raw-file readers that bypass mood.py: none.

**Writers by role (per mood.py docstring + agent definitions):**
- `workato-watchdog` — P1 spikes (`mood.py set arousal …`, agents/workato-watchdog.md:103)
- `harness-dreamer` — **the intended restorer**: agents/harness-dreamer.md:19 instructs it to "run the decay pass `mood.py decay` at report time **if the spike is stale**"
- anyone Josh directs

**Supposed restorer = the harness-dreamer's nightly conditional decay pass.** The mood.py docstring's "decay … run nightly" was never given its own job.

## 2. Why the restore never happened

Three compounding gaps (verdict: **never scheduled + delegated-but-never-fired**; no evidence of a failed run):

1. **No job exists.** `mood.py decay` has zero callers anywhere — the docstring's "run nightly" is aspiration, not wiring. The 06:38 session's "restore baseline after test" was the last write itself, not a scheduled follow-up.
2. **The delegated restorer never fired.** The dreamer's decay instruction is *conditional* ("if the spike is stale") and the dreamer ran 2026-10-08 → 10-10 without executing it, then **skipped 10-11 entirely** (second mechanism-dependent skip — attention-queue.md rev l, line 19).
3. **The 06:38 write doesn't match its own label.** Values written (exploration 0.3, risk_tolerance 0.2, verification_depth 0.9) are *not* mood.py's BASELINE (0.6 / 0.5 / 0.5). The write put a verification-heavy test posture into the file under a "restore baseline" reason — i.e., the restore was mislabeled or the follow-through step was never executed.

**Mitigating finding — the pulse is not actually reading frozen values.** Every reader (cortex, brain-gardener, estate-architect, project-dreamer, harness-dreamer — all per `~/.claude/agents/*.md`) reads through `mood.py`'s **decay-on-read** path (`_decayed()`, 24h half-life toward BASELINE), never the raw file. Verified read-only run of `mood.py` at 105.8h elapsed: arousal 0.3, exploration 0.586, risk_tolerance 0.486, verification_depth 0.519 — effectively baseline. Corroborated by gardener workbench reports 10-09/10-10 reading exploration 0.51/0.55 and reporting "baseline restored." So today's posture impact ≈ zero; the real damage is (a) dead/contradictory metadata (`reason`, `set_by`, stale raw values) for any future raw reader, (b) an unmonitored silent dependency on decay-on-read, (c) a standing false alarm in the attention queue.

## 3. Correct post-test baseline values (per repo evidence)

`scripts/mood.py:26-31` — the code's own `BASELINE` dict, which every decay computation targets:

| Field | Correct baseline | Currently in file | Effective (decayed) @ 105.8h |
|---|---|---|---|
| arousal | 0.3 | 0.3 | 0.300 |
| exploration | 0.6 | 0.3 | 0.586 |
| risk_tolerance | 0.5 | 0.2 | 0.486 |
| verification_depth | 0.5 | 0.9 | 0.519 |

Corroboration: gardener passes 10-09/10-10 read via decayed path converging toward these; no other baseline definition exists anywhere in the repo.

## 4. Proposed minimal fix (PROPOSE-ONLY — not executed)

**One-time remediation (clears the stale flag):** run `python3 ~/.claude/knowledge/scripts/mood.py decay` once. It persists the already-decayed near-baseline values with `set_by: "decay-pass"` and a fresh `set_at` — semantics preserved, no raw-file edit. Effort: one command, zero risk (values are already what readers see).

**Durable owner + mechanism (pick one; both tiny):**
- **Option A — make the existing delegation real:** in `agents/harness-dreamer.md`, change "run the decay pass … **if the spike is stale**" to an unconditional report-time step. Owner: harness-dreamer, as its agent file already claims. Weakness: the dreamer just skipped 10-11 (mechanism-dependent), so the restorer inherits that flakiness.
- **Option B (recommended) — deterministic backup line:** add one line (`python3 ~/.claude/knowledge/scripts/mood.py decay`) to an existing nightly `.script` job that already runs reliably — `com.josh.fleet.harness-health` or `decision-inbox.script`. No new launchd unit, no new infra; decay is idempotent and read-consistent.

**Rejected as non-minimal:** persisting decay-on-read automatically inside `mood.py` (behavior change touching every reader), and a dedicated launchd unit for one idempotent command.

**Needs Josh:** (1) go/no-go on the one-time `mood.py decay` run, (2) pick Option A vs B for the durable owner. Note "mood-register owner" is already an open question in attention-queue rev l — this proposal answers it.

## Evidence trail
- `scripts/mood.py:26-32` (BASELINE, half-life), `:41-54` (decay-on-read), `:75-80` (decay — zero callers)
- `grep` across `~/Library/LaunchAgents/*.plist`, crontab, `~/.local/bin/fleet/jobs/` → no mood references
- `agents/harness-dreamer.md:19` (conditional decay), `agents/{cortex,brain-gardener,estate-architect,project-dreamer}.md` (decayed-read consumers), `agents/workato-watchdog.md:103-109` (P1 writer)
- `garden-reports/2026-10-08-brain-gardener-full-pass.md:8` (verification-heavy posture day-of), `2026-10-09-workbench.md:16`, `2026-10-10-workbench.md:14` (baseline-restored readings)
- `now/decision-inbox.json:213` (open question), `triage/queue.jsonl:202` (this investigation's row), `cortex/attention-queue.md:19` (dreamer 10-11 skip; owner question open)
- Live read-only `mood.py` run 2026-10-12 ~21:00Z: hours_since_set 105.8, effective values above
