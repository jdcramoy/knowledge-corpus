# Investigation: mood setter stale ~182h — `dreams/mood.json` last set 2026-10-13T23:48:02

- **Filed:** 2026-10-21 · READ-ONLY diagnosis, nothing changed outside this file
- **Trigger:** live `mood.py` read shows `hours_since_set: 181.9`, `set_by: workato-watchdog`
- **Prior art:** this is a RECURRENCE — `mood-register-stale-baseline.md` (2026-10-12) diagnosed the
  identical gap and proposed Option A (make dreamer decay unconditional) / Option B (deterministic
  nightly `mood.py decay` line in an existing script job). Neither was applied. That is why it recurred.

## 1. Which component is supposed to update the mood register

Exactly one writer script: `~/.claude/knowledge/scripts/mood.py` (set / decay subcommands). The
"mood setter" is not a standalone component — it is **event-driven writes by the workato-watchdog**
(P1 confirm/retract, agents/workato-watchdog.md:109) **plus a conditional nightly decay pass
delegated to the harness-dreamer** (agents/harness-dreamer.md:19). No other script, hook, launchd
plist, or fleet job calls mood.py — re-verified today: zero references in ~/Library/LaunchAgents/,
crontab, and ~/.local/bin/fleet/jobs/. The docstring's "decay … run nightly" is still aspiration, not wiring.

## 2. Is it scheduled, and did the last run succeed?

- **No dedicated mood schedule exists.** Nothing schedules mood.py directly.
- **Watchdog (the writer):** plist `com.josh.fleet.watchdog` nightly 23:13, LOADED. Run log
  `~/.local/state/fleet/watchdog.log`: 10-19 23:17 "done validated" (success); **10-20 23:13 "start"
  → "cwd fail"** — last night's watchdog run FAILED at startup. The nightly-receipts gate confirms:
  `job: watchdog, run_date: 2026-10-20, fresh: false, detail: missing watchdog-reports/2026-10-20.md`.
- **Dreamer (the intended decay runner):** com.josh.fleet.dreamer, nightly ~23:51, SUCCEEDS
  ("done validated" 10-20) but never touches the file. Its instruction fires decay only "if the
  spike is stale" — the predicate is keyed on a stale SPIKE, and decay-on-read masks any spike
  (decayed arousal 0.3 < 0.7 threshold), so the trigger can never fire. It literally sees the
  problem and reports it: dream report 10-19 line 9 reads "**Mood:** arousal 0.3 (calm, stale 143.9h)".
- **Staleness is therefore by design-gap, not run-failure:** even a perfectly running watchdog
  writes mood only on P1 events (none since 10-13), and the dreamer's conditional can never trip.

## 3. Are the 10-13 values still valid posture, or frozen?

**Raw file: frozen stale metadata. Effective read: valid baseline.**

| Field | Raw (frozen 10-13) | Effective (decayed @ 181.9h) | Baseline |
|---|---|---|---|
| arousal | 0.3 | 0.3 | 0.3 |
| exploration | 0.3 | 0.598 | 0.6 |
| risk_tolerance | 0.2 | 0.498 | 0.5 |
| verification_depth | 0.9 | 0.502 | 0.5 |

- Every agent reader goes through mood.py's decay-on-read (`_decayed()`, 24h half-life), so what
  the fleet actually consumes at 181.9h is baseline to within ±0.002. Posture impact today ≈ zero.
- The frozen raw values are ALSO mislabeled, same pattern as the 10-08 write the prior
  investigation flagged: reason says "P1 retracted … No live P1" but exploration 0.3 /
  risk_tolerance 0.2 / verification_depth 0.9 are incident-coupling posture values, not baseline.
  The retraction restored arousal only and left the coupled fields at incident levels.
- Verdict: **frozen, not valid** — as raw state. Valid only via the unmonitored decay-on-read
  dependency. Risks: dead/contradictory metadata for any future raw reader; if decay-on-read were
  ever removed or the file consumed raw, the fleet would inherit incident posture (verif 0.9,
  risk 0.2) with no live incident.

## Secondary anomaly (noted, unexplained)

File mtime is Oct 15 18:07:36 but set_at is Oct 13T23:48:02 — content unchanged (all nine
.stash copies from 2026-10-21 are byte-identical, md5 3e1e338b…). Most likely a stash/restore or
tree-sync rewrote identical bytes on 10-15. No evidence of a third-party mood write.

## Recommendation (PROPOSE-ONLY, not executed — needs Josh's go)

Same as the 10-12 investigation, which was never applied:
1. One-time `python3 ~/.claude/knowledge/scripts/mood.py decay` (idempotent, persists the
   already-decayed near-baseline values with set_by decay-pass).
2. Durable fix Option B (recommended): one deterministic line appending `mood.py decay` to an
   existing reliable nightly .script job (com.josh.fleet.harness-health or decision-inbox) — no new
   unit, decay is idempotent and read-consistent. Option A (make dreamer's decay unconditional)
   alone cannot work: the dreamer's predicate is structurally unable to fire.
3. Bonus (out of scope, flagged): watchdog 10-20 run died "cwd fail" — separate defect, worth its
   own triage row; last night the estate had NO watchdog coverage at all.

## Evidence trail
- Live `mood.py` run 2026-10-21: hours_since_set 181.9, effective values above
- scripts/mood.py:26-32 (BASELINE/HALF_LIFE), :41-54 (decay-on-read), :75-80 (decay, zero callers)
- agents/workato-watchdog.md:109-115 (P1 writer), agents/harness-dreamer.md:19 (conditional decay)
- ~/.local/state/fleet/watchdog.log (10-19 done validated; 10-20 cwd fail), dreamer.log (done validated)
- garden-reports/nightly-receipts.jsonl: watchdog 2026-10-20 fresh:false, missing report
- dreams/2026-10-19.md:9 (dreamer sees "stale 143.9h", does not act)
- launchctl print gui/501/com.josh.fleet.watchdog (loaded, nightly 23:13); grep sweep: no mood refs
  in any plist/crontab/fleet job
- cortex/investigations/mood-register-stale-baseline.md (2026-10-12 prior art, never applied)
