# Investigation: REC | Pipeline Watchdog (82959774) STOPPED 2026-10-13 17:11:03 PT

**Verdict: MANUAL STOP — INTENTIONAL. Executed by a Claude session under BSYS-29653 as part of
the "hr-genie-ops notification pause" (pause ALL dev HR Genie ops notifications to #hr-genie-ops).
NOT an error-limit stop, NOT a malfunction, NOT a stray write. No action needed; rollback path exists.**

## Timeline (evidence: build-ledger.jsonl, BSYS-29653)

- 00:09:35Z–00:11:00Z — session sets project property `HR Genie Monitoring Mode` = `SHADOW`
  (project 15643451) via several paths; several scoping attempts needed before readback confirmed.
- 2026-10-14T00:11:03.984Z = 2026-10-13 17:11:03 PT — `wt recipes stop 82959774 --raw`
  (build-ledger.jsonl line 15651). Timestamp matches the sweep's stop time EXACTLY.
- 00:11:30Z — `wt recipes stop 82863670 --raw` (Weekly Intelligence Digest, second sender).
- 00:12:37Z — Jira ticket **BSYS-29653** "Pause dev HR Genie Operations notifications to
  #hr-genie-ops (watchdog + publisher + weekly digest)" created, documenting this exact stop.
- 00:12:46Z — living export manifest "BSYS-29653 hr-genie-ops-notification-pause" created
  (id 363005, folder 30275122); assets 82959774, 82863670, 76234914 verified in it at 00:14:10Z;
  package 42219152 ZIP-verified at 00:14:28–00:15Z.

## Why the sweep missed it

uat-sweep-2026-10-14 flag 1 treated the stop as an anomaly; BSYS-29653 was created minutes after
the stop but the sweep did not correlate it. Recipe id 82959774 has ZERO gossip-bus mentions in
the 24h window — the pause session posted no claim/finding line, so the sweeper had nothing to
correlate against. Process gap, not a lost asset.

## Check details

1. **Gossip bus (24h):** 0 hits for 82959774; 0 hits for BSYS-29653/82863670/pause. Nearby
   stopped-recipe traffic was all the separate 82964017 canary case (trigger config drift,
   trigger_errors_limit, Oct 12, BSYS-29560, gated on Josh).
2. **build-ledger.jsonl:** stop row at line 15651 (00:11:03Z), immediately preceded by SHADOW-mode
   property writes to project 15643451, immediately followed by the 82863670 stop, ticket creation,
   and manifest build. Prior 82959774 rows are the Oct-10 build session (hrg-watchdog-slack-20261010,
   BSYS-29488) which started it — none in between.
3. **watchdog-reports/2026-10-13.md:** no mention of 82959774 / BSYS-29653 / pause — the watchdog
   did not flag anything about this recipe before the stop.
4. **recipe-health sweep lines:** every sweep in the window names only 82964017 stopped and
   82272892/82178793 new-failures (82178793 already verdict-noise at 11:15Z). No other recipe
   stopped unexpectedly in the window; the only other stop was 82863670, same pause, same session.

## Classification

- **manual-stop** (human/agent-initiated via `wt recipes stop`), stop_cause=None is consistent —
  no trigger errors accumulated; compare 82964017 which auto-stopped with trigger_errors_limit.
- Companion stopped asset: 82863670 (Weekly Intelligence Digest), same intentional pause.
- Publisher 76234914 kept running (mode-gated to SHADOW — records incidents, sends no Slack).

## Rollback (from BSYS-29653)

Start 82959774 + Start 82863670, flip `HR Genie Monitoring Mode` back to `ACTIVE`.
Ticket status: Backlog, unassigned. Nothing unverified beyond the two wt-CLI stop commands'
output not being captured verbatim in the ledger (their effects are confirmed by BSYS-29653
UAT-evidence readbacks: property = SHADOW, both recipes Running: False).
