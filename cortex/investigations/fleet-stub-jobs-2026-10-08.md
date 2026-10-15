> Rescued by cortex pulse 2026-10-09T04:31Z from dispatch log dispatch-20261009-042729.log (headless Write denied by sensitive-file gate; findings delivered via stdout fence). Verdict: NO dead jobs - corpus/ops-autopsy enabled and last runs validated; room-sweep real but unscheduled; fleetest/fleetstub synthetic validation probes. Watchdog P2#3 was cadence-blind staleness, not stall.

# Investigation: 5 fleet jobs silent after 2026-10-08T15:08Z

Investigated 2026-10-09 ~00:30 EDT (04:30 UTC), per watchdog report
`garden-reports/watchdog-2026-10-09.md` P2#3 and cortex dispatch at
04:27:29Z. Read-only — nothing was changed.

## Verdict up front

No dead jobs. The "5 silent jobs" are really 3 distinct cases:

1. **corpus, ops-autopsy** — real, wired, enabled, and their last runs
   SUCCEEDED ("done validated" with full real output). They are silent
   only because their schedules haven't come due again. The stub
   rc=1/rc=0 ledger lines were the pre-fix attempts during the Oct 8
   stub-night repair window, and the final retry of each validated.
2. **room-sweep** — a real job definition (kit + deployed) that was
   never given a persistent launchd schedule. It runs manually/one-off;
   its last run also validated. Not broken — unscheduled.
3. **fleetest, fleetstub** — synthetic names with NO definition
   anywhere. They are leftover probes of run-job.sh v2's
   stub→retry→ledger contract and are safe to delete from nothing
   (there is nothing to delete). Their ledger lines are the contract
   working as designed, not a fault.

The watchdog's "silent 12h+" framing was a schedule-arithmetic artifact:
the machine-health check compares last-heartbeat vs now without knowing
each job's cadence.

## Q1 — Do the launchd job definitions exist, and are they enabled?

`~/Library/LaunchAgents/` and `launchctl print gui/501/...`:

| Job | Plist in LaunchAgents | Loaded in launchd | Schedule |
|---|---|---|---|
| corpus | YES `com.josh.fleet.corpus.plist` (Oct 7 05:48) | YES, enabled, state "not running" (normal) | Weekly, Mon 06:07 local (`StartCalendarInterval` Hour 6 Min 7 Weekday 1) |
| ops-autopsy | YES `com.josh.fleet.ops-autopsy.plist` (Oct 8 06:05) | YES, enabled, state "not running" (normal) | Daily 06:07 local |
| room-sweep | **NO plist** | NO — "Could not find service" | none; kit def exists (`bin/fleet/jobs/room-sweep.env` + `.script`) but no schedule anywhere, including kit `schedules/` |
| fleetest | NO plist | NO — "Could not find service" | none; no definition anywhere |
| fleetstub | NO plist | NO — "Could not find service" | none; no definition anywhere |

None of the three existing fleet plists is disabled (no launchd override;
all show exit code 0 and appear in `launchctl list`).

Note: ops-autopsy's plist was created 06:05 Oct 8, two minutes before
its first scheduled fire — it is a NEW job wired during the same
stub-night session.

## Q2 — Last lines of each job's logs: why rc=1?

All five run through `~/.local/bin/fleet/run-job.sh`. Its contract
(run-job.sh v2, deployed Oct 8): an attempt is "valid" only if it
increments the job's heartbeat count OR produces non-empty output;
`stub rc=N` = attempt failed that test with claude's exit code N; the
ledger line is written only after a second failed retry.

- **corpus** (`~/.local/state/fleet/corpus.log`, last line
  `2026-10-08 11:08:21 corpus: done validated`): final attempt produced
  a full, real maintenance report (index drift check, platform-degradation
  note for Oct 8 07:51-08:06 PDT, repo-hygiene proposal). Not a stub.
  The rc=0 stub lines at 15:01:22Z/15:05:51Z UTC were earlier attempts
  in the retry loop before the env repair took effect.
- **ops-autopsy** (`ops-autopsy.log`, last line
  `2026-10-08 11:12:31 ops-autopsy: done validated`): final attempt
  produced a real autopsy report (Drive-carrier 404/403 race diagnosis,
  bounded-retry fix proposal, 2 diagnoses.jsonl writes). Not a stub.
  Its rc=0 stub line at 15:01:22Z was the same earlier-attempt artifact.
- **room-sweep** (`room-sweep.log`, last line
  `2026-10-08 11:08:57 room-sweep: done validated`): the rc=1 at
  14:57:53Z was a real failure of the pre-fix environment — the script
  piped claude's empty output (no gateway env under launchd) into
  `room-sweep.py`, which died on
  `json.decoder.JSONDecodeError: Expecting value: line 1 column 1`
  (exit 1 → `stub rc=1`). The retry validated. So YES, room-sweep's
  rc=1 was exactly the run-job.sh v2 PATH/gateway failure class the v2
  repair targets — and the repair worked on the retry.
- **fleetest / fleetstub**: no log files, no state files, no heartbeats
  — they only ever appear in the ledger (rc=0 stubs at 14:58:38Z /
  15:00:15Z). Mechanism: `run-job.sh fleetest` with no
  `jobs/fleetest.prompt` runs `claude -p ""` under the broken env,
  exits 0 with empty output → stub → retry → ledger line. That is the
  v2 validation contract recording a deliberate empty-shell invocation,
  i.e. someone (the Oct 8 repair session) tested the ledger path with
  fake job names.

Timeline correlation: every ledger line falls in 14:57:53-15:05:51Z
(10:57-11:05 EDT Oct 8) and every successful "done validated" lands
15:08-15:12Z (11:08-11:12 EDT). That is a single manual
verify-the-v2-runner session run from the terminal, not scheduled
execution (corpus's 06:07 Monday schedule and ops-autopsy's 06:07 daily
schedule do not produce 11:00 EDT runs). The v2 repair was deployed
mid-session; post-repair attempts validated, pre-repair attempts stubbed.

## Q3 — Is fleetstub a synthetic test to delete, or a real job?

Synthetic, and there is nothing to delete. Evidence:

- Zero references to `fleetest` or `fleetstub` anywhere in the kit repo
  (`~/Documents/agentic-workato-kit`, git history grep on commit 4adf0d5
  "bin/fleet: the fleet runner + job definitions"): no
  `jobs/fleetest.*`, no `jobs/fleetstub.*`, no schedules, no plists.
- Zero references in `~/.local/bin/fleet/jobs/` (16 deployed defs;
  `fleetest`/`fleetstub` absent).
- No log or state files in `~/.local/state/fleet/` for either name.
- No shell-history traces found (history file not flushed at the time).
- The names themselves read as throwaway probe names ("fleetest" =
  fleet + test, "fleetstub" = the stub contract itself).

Both names appear ONLY as two lines in
`garden-reports/fleet-validation.jsonl` — which is exactly the artifact
you'd expect from pointing the new runner at nonexistent job names once
each to prove the stub→retry→ledger→watchdog escalation path end to end.
The contract behaved correctly. The watchdog's "verify intent" ask is
answered: test artifacts, no cleanup needed, no schedule to remove.

## Q4 — Are these visible to the machine-health heartbeat check?

Unlike the dreamer jobs (P2#4, zero heartbeats ever), **all three real
jobs DID write heartbeats** and are fully visible to the check:
`room-sweep` 15:02:53Z and 15:08:57Z, `corpus` 15:05:22Z and 15:08:21Z,
`ops-autopsy` 15:12:31Z — all Oct 8. `heartbeat.jsonl` itself is healthy
(15 entries through 04:15Z today from gym, dreamer, watchdog, etc.).

Two nuances:

- `fleetest`/`fleetstub` never wrote heartbeats because the validation
  contract correctly withholds a heartbeat from a stubbed run — they
  are invisible to the heartbeat check by design, and the validation
  ledger is the catch-net that surfaced them.
- The real gap is not heartbeat invisibility but **cadence-blindness in
  the watchdog's "silent 12h+" check**: it flagged corpus (weekly, next
  due Mon Oct 12 06:07) and ops-autopsy (daily, next due Oct 9 06:07 —
  about 5.5 hours after this investigation) as anomalous. A
  cadence-aware staleness test (compare last heartbeat against the
  plist's `StartCalendarInterval` + one-period grace) would have
  produced zero findings here. Worth a follow-up: ops-autopsy's 06:07
  run THIS morning is the true health test for the two real jobs — if
  it heartbeats at ~06:07 EDT Oct 9, this whole P2 closes as
  false-alarm-with-a-lesson.

## Recommended actions (none taken — read-only)

1. Nothing to fix on the 3 real jobs; let ops-autopsy's 06:07 run today
   and corpus's Monday 06:07 run prove liveness.
2. Optional ledger annotation on the two `fleetest`/`fleetstub` lines
   marking them verified-synthetic, so future watchdog runs stop
   re-flagging them (they re-derive from the jsonl each run).
3. Decide room-sweep's intent: it has a kit + deployed definition but no
   schedule. If it should run, wire a plist (it currently runs only when
   invoked by hand); if it's superseded, say so in the kit README.
4. Watchdog improvement (cadence-aware staleness) — file as a triage
   card rather than treating this P2 as an incident.

## What was NOT verified

- Who exactly invoked the 15:00-15:12Z Oct 8 manual runs (shell history
  unavailable); inferred from timing + output, not from a session record.
- Whether `claude -p ""` under a broken gateway returns rc=0/empty
  (mechanism for fleetest/fleetstub's rc=0) — inferred from runner
  source, not reproduced.
- ops-autopsy's 06:07 EDT Oct 9 run had not fired yet at write time —
  liveness of the scheduled path remains unproven until then.
- The brain bus MCP was permission-gated this session; the fleet-stub
  threads were read directly from `knowledge/dreams/bus/*.jsonl`
  instead.
