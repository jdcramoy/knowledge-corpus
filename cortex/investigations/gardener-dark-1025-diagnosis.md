# Gardener dark 10-25 diagnosis

**Investigated:** 2026-10-25 (bounded read-only session). **Verdict: BOTH — a real dark night (the scheduled 10-24 run-date nightly failed and produced nothing) AND a filename-convention mismatch that makes the escalation overstate the gap.**

## Q1: Did com.josh.fleet.gardener fire on 10-24, and did it run or fail?

**Two nights, two different outcomes.**

**Night A — fire at 22:43 local on 2026-10-23 (this is the run the gate grades as run-date 2026-10-24).** It fired and it FAILED:

- `gardener.log`: `2026-10-23 22:44:02 gardener: start` → two claude invocations, each dying with `API Error: Can't reach the API server — check your internet or DNS (ENOTFOUND)` plus an `unrecognized_model` warning (fireworks/glm-5.3-flash).
- `run-job.sh` retry logic fired: `2026-10-23 23:56:49 gardener: no work evidence (ran rc=1) — retrying once`, then `2026-10-24 00:50:12 gardener: VALIDATION FAILED after retry (ran rc=1) — job did not run; escalated`.
- Validation ledger (`garden-reports/fleet-validation.jsonl`) row `{"ts":"2026-10-24T04:50:12Z","job":"gardener","result":"ran rc=1","action":"retry-exhausted","note":"validation failed after retry; watchdog escalates to bus + brief"}`.
- **No artifact was produced.** rc=1 both attempts, zero bytes of report.

**Night B — fire at 22:43 local on 2026-10-24: NO TRACE.** `gardener.log` jumps from the 00:50 VALIDATION FAILED line straight to `2026-10-25 10:43:01 gardener: start`. There is no 10-24 22:43 start line, no probe line, no validation-ledger row between `2026-10-24T04:50:12Z` and `2026-10-25T02:51:54Z`. `launchctl list` shows the job loaded with last exit 0. StartCalendarInterval fires are coalesced-on-wake / skipped when the Mac is asleep or off — the 10-24 22:43 schedule was never honored (or died pre-log, which run-job.sh's design makes near-impossible given the start bookend). Most consistent explanation: machine not in a state to run at that hour; the fire was coalesced into the **10-25 10:43 start** (exactly 12h after the 22:43 slot — machine woke ~10:43 and launchd fired the missed interval; the `gardener.log.probe-out` mtime of 10:43 supports this).

## Q2: Where did its output go, if anywhere?

Three artifacts exist in `garden-reports/` for the 10-24/10-25 window — **none named `2026-10-24-brain-gardener-nightly.md`**:

| Artifact | mtime | What it is |
|---|---|---|
| `garden-reports/2026-10-24-nightly-garden.md` | Oct 24 16:04:54 | A brain-gardener **incremental nightly pass for run-date 10-24** (signed "— brain-gardener, nightly incremental", workbench/Jev-arc delta scope). Real gardening output for the gate's run-date, under a non-canonical filename. |
| `garden-reports/2026-10-25-weekly-full-pass.md` | Oct 25 10:51 | Output of the coalesced 10-25 10:43 run — a **weekly full pass** (Saturday cadence: full estate audit, 21 build plans), named for 10-25. |
| `garden-reports/heartbeat.jsonl` | — | `2026-10-25T02:51:38Z` brain-gardener heartbeat matching the 10:51 done-validated; plus an entry noting a "duplicate fire into active session; nightly pass already complete (2026-10-24-nightly-garden.md)". |

So the run-date 10-24 window has genuine gardener output (`2026-10-24-nightly-garden.md`), and the coalesced run produced substantial output — but nothing the gate can see, because the gate checks exactly one canonical filename per run-date.

## Q3: Dark night, convention mismatch, or suppressed output?

**All three mechanisms, ranked:**

1. **Real dark night (primary, for the scheduled nightly).** The 10-23 22:43 fire — the run the gate grades as run-date 2026-10-24 — failed hard: two attempts, both `API Error … ENOTFOUND` (no network/DNS at that hour), rc=1, escalated correctly by run-job.sh to the validation ledger. This is not suppressed output; it never ran.
2. **Filename-convention mismatch (compounding).** The gate grades run-date 2026-10-24 against exactly `garden-reports/2026-10-24-brain-gardener-nightly.md` and accepts no aliases. `2026-10-24-nightly-garden.md` — a real 10-24 gardening pass — is invisible to it. The identical pattern hit the watchdog (gate wants `watchdog-reports/2026-10-24.md`; the 23:13 fire stamped the artifact `2026-10-25.md` — off-by-one on run-date vs artifact-date naming, while a `2026-10-24-watchdog.md` sits in `garden-reports/`, the wrong directory entirely).
3. **A fully successful run invisible to the gate.** The coalesced 10-25 10:43 run completed and validated (`2026-10-25T02:51:54Z valid` in the validation ledger) and wrote a comprehensive weekly full pass — and the gate still escalates, because the run-date-10-24 canonical file doesn't exist. The gate has no notion of "validated-clean ledger row + differently-named artifact = coverage".

## What actually needs Josh (or a triage decision)

- **Nothing is operationally dark right now.** The gardener is healthy as of the 10-25 10:51 validated run; the heartbeat is current (`2026-10-25T02:51:38Z`); the estate-audit content (INDEX.md tax, failing prod recipe 83197291, cron-overwrite guard, 4 unbuilt accepted proposals) is all in `2026-10-25-weekly-full-pass.md`.
- **Real gap to close:** the 10-24 scheduled nightly genuinely didn't happen (network down at 22:43 on 10-23; 10-24 22:43 fire missed). Fix options: add a morning catch-up trigger (or rely on launchd wake-coalescing, which worked 10-25), and/or have run-job.sh treat `API ENOTFOUND` nights as retry-next-wake.
- **Gate fix:** nightly-receipts-gate should accept (a) the validation-ledger `validated-clean` row as proof-of-run, and (b) alternate report filenames per run-date (watchdog and gardener both burned by exact-name grading). Filed context: cortex finding `receipts-gate run-date wrinkle` (2026-10-25T12:01:51Z), triage item `gardener-nightly-dark-1025`.

## Evidence index

- `~/.local/state/fleet/gardener.log` lines: `2026-10-23 22:44:02 start` / `23:56:49 no work evidence (ran rc=1)` / `2026-10-24 00:50:12 VALIDATION FAILED after retry — escalated` / `2026-10-25 10:43:01 start` / `10:51:54 done validated`
- `~/.claude/knowledge/garden-reports/fleet-validation.jsonl` rows 10-22→10-25 (`ran rc=1 retry-exhausted` at `2026-10-24T04:50:12Z`; `valid` at `2026-10-25T02:51:54Z`)
- `~/Library/LaunchAgents/com.josh.fleet.gardener.plist` — StartCalendarInterval 22:43 daily; `launchctl list` → loaded, last exit 0
- `~/.claude/knowledge/config/fleet/run-job.sh` — retry-once + validation + ledger + "never die loudly" escalation semantics (lines ~183-221)
- `garden-reports/2026-10-24-nightly-garden.md` (10-24 incremental, 16:04), `garden-reports/2026-10-25-weekly-full-pass.md` (weekly full pass, 10:51 10-25)
- `garden-reports/nightly-gate-state.json` (`"gardener": "2026-10-24"` escalated), `garden-reports/nightly-receipts.jsonl` gate rows
- `dreams/bus/cortex.jsonl` finding `receipts-gate run-date wrinkle` (2026-10-25T12:01:51Z)
