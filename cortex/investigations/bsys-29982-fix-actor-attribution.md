# BSYS-29982 — fix-actor attribution, prod recipe 83197291 (REC | Holiday Calendar Sync)

- **Date:** 2026-10-27 (investigation run ~02:15 +08)
- **Scope:** READ-ONLY. One batched prod probe (josh-prod profile, GETs only). No stop/start/modify, no Slack/Jira posts.
- **Recipe:** https://app.workato.com/recipes/83197291 — ticket https://workato.atlassian.net/browse/BSYS-29982 (dupes BSYS-29981/29983 marked)

## VERDICT

**The fix actor cannot be positively identified from reachable evidence.** What is proven: the fix
was NOT made by any Claude/fleet session (excluded with high confidence), it involved NO recipe-code
or connection-binding change, and it included a Workato-side stop→start inside the 7-minute window
06:43:33–06:50:24 PT on 2026-10-26. The surviving candidates are (a) a human operator — most plausibly
Josh — acting manually in the Workato prod UI, and/or (b) a Workday tenant admin activating the
missing ISU security grant in the same window (invisible to Workato observability). Both are
inference, not attribution.

## 1. Latest job state (live prod probe, read-only, 2026-10-27)

| Field | Value |
|---|---|
| running | **true** |
| last_run_at | 2026-10-26T07:36:27-07:00 |
| job_succeeded / job_failed | 2 / 7 |
| recipe updated_at | **2026-10-20T01:08:02-07:00 (untouched since deploy)** |
| bound Workday connection | 19909763 "ISU Prod" (NOT rebound to 22340993 "Workato2 ISU") |

Job list (newest first): `j-Ac9Kzk3h` **succeeded** 07:36:27 PT; `j-Ac9KGJwp` **succeeded**
06:50:24 PT; `j-Ac9KBEnK` **failed** 06:43:10 PT; then daily 07:00 PT failures 10-25, 10-24,
10-23, 10-22, 10-21, 10-20 — matching the brief's Fri/Sat/Sun failure pattern.
Next natural tick (~07:00 PT 2026-10-27) had not yet fired at probe time.

**Key forensic detail:** `stopped_at = 2026-10-26T06:43:33-07:00` with `stop_cause = None`, and
`running = true` with a success at 06:50:24 — i.e., someone/something **stopped the recipe 23
seconds after the failed 06:43 tick and restarted it before 06:50**. That stop→start is the only
Workato-side action in the fix window. The two successes (06:50, 07:36) are off the 07:00 schedule
and read as manual catch-up/rerun runs.

## 2. Attribution evidence sweep (all negative for a fleet actor)

- **Build-ledger (`build-ledger.jsonl`):** zero wt/API calls between 2026-10-26T03:15Z and 13:55Z.
  The fix window is 13:43–13:50Z — squarely inside the dead zone. All 10-26 ledger rows for
  83197291 are read-only GETs (tickets BSYS-29503, BTSUP-78227, BSYS-29982).
- **Session transcripts:** the only sessions adjacent to the window are strictly read-only —
  `0bb1a376` (06:54 PT, read prod recipe + filed BSYS-29983 AFTER the fix landed), `e587d9d4`
  (07:29 PT, wt api GETs only), cortex pulse `4151f393` (attention-queue writes only, prod reads
  only). Grep for any mutating command (update/put/post/patch/authorize/start/stop/edit/create)
  in both investigator transcripts: **zero hits**. AIRO-MCP prod writes would have left
  permission-prompt + tool_use records; none exist anywhere in the window.
- **Gossip bus:** every 83197291 post (cortex, watchdog, harness-dreamer, 10-24→10-26) says the
  fix is Josh-gated ("Josh owns the re-auth", "Josh's Workday ISU grant decision is the only
  unblock"). No agent claims the fix.
- **Redteam / error-canon:** no records for 83197291 (recipe never went through a promotion
  red-team; only related file is BSYS-29799 OOO calendar layer).
- **Mission-control registry:** the pre-fix row lists "prod restart of holiday-calendar recipe
  83197291 (BSYS-29982)" as a **pending Josh decision**; the post-fix closeout (10-26 14:45Z)
  explicitly records "Authorization error resolved by an **unidentified actor** mid-investigation"
  and leaves an open need: "Whoever made the Workday-side change (ISU grant or connection re-auth)
  to note it on BSYS-29982 so the fix mechanism is on record."
- **Weak/inconclusive signal:** the Workday-Development workspace projects dir shows an mtime of
  06:29 PT on 10-26 (14 min before the failed tick) with no contained transcript file in that
  window — consistent with a transient session file, not usable as attribution.

## 3. What the evidence supports about the MECHANISM

Ranked by fit:

1. **Workday-side grant + manual Workato restart (most plausible).** The 10-24 autopsy proved the
   failure was Workday's per-task authorization ("task submitted is not authorized" at
   `Get_Holiday_Calendars` via connection 19909763, which authenticated fine — sibling recipe
   82917289 green on the same connection). A Workato-side fix alone shouldn't clear that. The
   observed pattern — last failure 06:43, stop at 06:43:33, success 06:50 — fits an operator
   restarting the recipe immediately after a Workday admin granted the ISU the task and activated
   pending security policy changes (a known Workday gotcha).
2. **Connection re-auth on 19909763 during the stop window.** Possible but contradicts the
   autopsy's proof that auth was healthy; would also be invisible in the fields probed.
3. **Restart alone cleared a stale session.** Weakest — the 06:43 failure was a fresh scheduled
   job, so a stale-session theory has to explain why fresh sessions kept failing for 7 days.

Note what is EXCLUDED by the probe: no recipe edit (`updated_at` = 10-20 deploy), no rebind to
the never-authorized connection 22340993 (still bound to 19909763).

## 4. Why exact attribution is impossible from here

- **Workato audit log unreachable by API:** `GET /api/audit_logs` → HTTP 404 on the prod
  workspace's developer API. The workspace Activity Log (UI) and any audit-log streaming
  destination are the remaining Workato-side surfaces and would name the user who stopped/started
  the recipe at 06:43:33 PT.
- **Workday tenant side is entirely unreachable** from this environment; the ISU grant/activation
  (the likely substantive fix) lives in Workday's own audit, owned by the HRIS/Workday admin team.
- Bounded to one prod probe per the brief; the UI Activity Log (Orca browser, read-only) is the
  single highest-value follow-up.

## 5. Recommended next step (for Josh, no action taken)

Ask in the BSYS-29982 thread whether Josh himself stop/started the recipe ~06:43 PT Monday. If
not, the Activity Log in the Workato prod UI (or audit-log stream) names the operator, and the
Workday admin team can confirm the ISU grant/activation timestamp — then the open mission-control
need ("fix mechanism on record") can close.

## Evidence index

- Live probe (this run): recipe get + jobs + connection GETs, josh-prod profile, 2026-10-27 ~02:10 +08.
- Prior autopsy: `~/.claude/knowledge/cortex/investigations/prod-holiday-calendar-p1-autopsy-83197291.md` (2026-10-24).
- Ledger rows: `build-ledger.jsonl` 2026-10-26T13:55–14:43Z (read-only investigations, tickets BSYS-29503 / BTSUP-78227 / BSYS-29982).
- Bus threads: `prod-p1-holiday-calendar-83197291-confirmed-live`, `p1-83197291-*`, `watchtower` (3-strike termination 2026-10-26T03:27Z).
- Registry: `mission-control/registry.json` BSYS-29982 closeout row (2026-10-26T14:45:43Z).
- Session transcripts: workbench `0bb1a376`, `e587d9d4`, `4151f393` (all read-only in window).
