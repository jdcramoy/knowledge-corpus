
# Stale-registry sweep — READ-ONLY investigation (2026-10-23T18:41Z)

## VERDICT

**45 stale rows (last event >24h before the 18:38Z fold): 14 plausibly STILL-ALIVE, 15 WAITING-ON-JOSH, 16 plausibly DEAD.**

**The 3 dead-class rows most worth closing:**
1. **manifest-review-bsys-29510** (in-flight, 10-12) — BSYS-29510 "Super Happy Friday Fixes" is **Closed** on Jira (verified live 10-23); the "fix 5 blocking items and resubmit" ask blocks a ticket that is already done.
2. **kb-digest-dead-cycles** (10-18) — the only ask was to kill a stuck sync PID 35720 from 10-17; that PID is 6 days dead, and the KB sync path was since reworked (kb-digest fallback fixes landed on the harness-fix bus 10-22T22:50Z). Fully moot.
3. **jira-triage-pass-2026-10-17-2020** (10-17) — duplicate of pass-1213 carrying the same Snowflake grant-intake question, superseded by BSYS-29770 / BTSUP-79061 (the GTM_OPERATIONS grant request for integrations.cx@workato.com was filed into a build row on 10-22T21:43Z).

Method: for each row, grepped the full slug across dreams/bus/*.jsonl, build-ledger.jsonl, garden-reports (heartbeat + recent reports), mission-control/events.jsonl, cortex/dispatches+questions, triage/queue.jsonl, claims/verifications.jsonl; cortex pulse-census mentions were counted as TRACKING, not activity; BSYS-linked rows verified live on Jira (6 tickets pulled 10-23).

## STILL-ALIVE (14) — recent corroborating activity elsewhere

| row | last event | evidence |
|---|---|---|
| estate-review | 10-12 | weekly estate-architect ran TODAY: new closeout 10-23T12:17Z + fresh hygiene findings on the bus |
| regression-registry-hygiene | 10-12 | regression-registry.json actively modified 10-22T23:59 — registry hygiene ongoing (the specific 10-12 verdict ask likely superseded; consider re-asking or closing) |
| btsup-76729-hr-genie-kb | 10-14 | BTSUP-76729 build rows active TODAY (10-23T01:50 v2 sweep build; 10-23T16:30 "prod promotion never filed" escalation) |
| brain-garden | 10-16 | gardener runs daily (bus 10-23); its ask was EXECUTED — clm-014 renumbered 10-22T21:14Z → closeable as done |
| escalation-82959482-btsup76729-dev-assets | 10-18 | BTSUP-76729 promotion escalations active TODAY 10-23T16:31Z |
| ai-directory-rearch | 10-20 | BSYS-29806 updated 10-22T21:57Z (inside 24h of fold) — still Backlog, flip-to-FTR ask stands |
| jira-triage-queue-sweep-1020 | 10-20 | its ask was EXECUTED: manifest 361382 exported at v38 10-22T21:24Z (unzip-verified), BSYS-29905 package work 10-23T03:43Z → closeable as done |
| knowledge-corpus-sync | 10-20 | cortex opinion 10-22T15:06Z continued the sara@acme.com PII/churn discussion (27h pre-fold — borderline) |
| slack-mcp-token-clone | 10-21 | BSYS-29827 live **In Progress**, updated 10-22T02:06Z |
| genie-shutdown-drift | 10-21 | BSYS-29829 updated TODAY 10-23T16:04Z; go/no-go ask still open |
| google-slides-mcp | 10-21 | project very active TODAY: BSYS-29908 layout toolkit + BTSUP-79460 prod hotfix (10-23T16:24Z) |
| jira-autotriage-hr-genie (in-flight) | 10-12 | cortex pulse 10-23T17:45Z judged it explicitly "reads stale but is ALIVE (builds continuing)"; HR Genie/BTSUP-76729 builds active today |
| josh-writing-voice (in-flight) | 10-14 | skill in daily use (Slack-draft voice), census/tracking mentions 10-23; the person-calibration ask itself still unactioned |
| hr-genie-collector (in-flight) | 10-14 | RESOLVED: BSYS-29519 v44 shipped 10-14, "live green per triage 10-23" (closeout 10-23T04:25Z) → closeable as done |

## WAITING-ON-JOSH (15) — only blocker is the unactioned needs sentence

- **corpus-maintenance** (10-12): "Approve the 3 INDEX.md fixes (repoint line 44, add bsys-25529 line, add agent-harness-operations) and the dedup-shortlist artifact-exclusion list"
- **harness-benchmarking** (10-13): "Josh decision on posting the LinkedIn reply, and whether to build the follow-up method/raw-outputs post"
- **seismic-mcp** (10-13): "Nightly registry policy for VUA-bound skills (tag-and-skip vs identity-carrying harness run) — Josh verdict; BSYS-29281 prod-import gate hold stays until nightlies run clean." (seismic-dev still unauthenticated per 10-23 MCP health check)
- **fleet-env-bypasspermissions** (10-14): "Josh decision on whether to execute the walk-back: revert Tier A (cost-governor, cortex) now, fund the census option-A script-lane conversion for Tier B, or accept the governance regression and leave all 18 flagged"
- **alert-channels** (10-16): "Josh: enable Orca + terminal-notifier in System Settings > Notifications when convenient; answer whether he clicked Verify manually on the pre-filled Okta password (settles if keychain value is correct)"
- **regression-autopsy** (10-16): "Josh: (1) UI/Orca red-pill inspection on 82727069 ... (2) decide registry hygiene: empty-shell cases on 82239660/82959480 ... (3) BSYS-25528 endpoint 24083332 activation still pending for the 82959481 fixture." (82727069 was re-pulled on the CLI 10-22T21:36Z — inspection still pending)
- **harness-fix-fleet-run** (10-18): "Josh: pick the durable deploy fix for fleet jobfiles (deploy only from canonical via fleet-deploy.sh, exclude jobfiles from repo redaction, or make parity redaction-aware)"
- **escalation-82872520-gslides-guidance-stopped** (10-18): "Josh decision: fix (stop-guard/auto-restart on prod helper 82872520) or risk-accept manual restarts" (82872520 re-probed by replay-gym 10-22T21:55Z — still failing)
- **fixloop-escalation-82872520-stop** (10-19): "Josh decision on recipe 82872520 failure class 'stop': fix or risk-accept (8 recurrences in 14d)"
- **estate-remediation** (10-20): "Josh: fire a prod session to (1) rotate the Frontify token in the console, (2) pick archive batches, (3) approve the OPS Listener staleness-guard fix, (4) execute the personal-connections plan" — no post-10-20 evidence any of the four fired
- **sfdc-accounts-sync** (10-20): "Josh: decide UAT window and promotion go" — NO red-team verdict on file in ~/.claude/knowledge/redteam/ (checked 10-23), so promotion prep has not started
- **full-fix-day** (10-20): "Josh: Workday grant for the end-user tax-delivery read (or approve ISU re-point) on the tax-elections tool"
- **frontify-mcp** (10-21): "Josh: flip BSYS-29824 to Final Tech Review; later replace Everyone access with the end-user group" — BSYS-29824 parked in Backlog, untouched since the row itself (verified live 10-23)
- **workday-mcp** (10-21): "Josh: decide whether to run the identical-asks head-to-head benchmark (ours vs Workday OOTB MCP) before Friday, and review the brief's voice before it goes out." — zero post-event corroboration
- **gws-semantic-gateway** (in-flight, 10-13): "Jasper review on the five; then merge in order" — otto repo untouched since 10-13 (last commit 64ffa524a 10-13); 10 days stalled, ask stands

## DEAD (16) — no corroborating activity found anywhere (or superseded/moot)

| row | last event | why dead |
|---|---|---|
| manifest-review-bsys-29510 (in-flight) | 10-12 | BSYS-29510 **Closed** on Jira 10-18 (verified live) — ask moot |
| estate-monitor-harness-hook | 10-13 | 10 days, zero non-self hits anywhere in bus/ledger/garden/cortex; no hook artifact found in ~/.claude/hooks |
| agent-gossip-bus | 10-13 | zero non-self hits; the re-scope decision was never taken and the bus simply runs broadcast daily — mooted by status quo |
| sfdc-mcp-picklist-fix | 10-14 | zero non-self hits in 9 days; product picklist question never picked up |
| preso-skills | 10-14 | zero non-self hits in 9 days (delete typo'd Slack draft Dr0C919Q578T + tag contributors) |
| fleet-env-recount | 10-14 | zero non-self hits since row day; memory scope-note correction never picked up |
| hr-genie-intelligence | 10-14 | zero non-self hits in 9 days; the Slack reply draft is long stale |
| btsup-76729-visibility-flip | 10-15 | zero non-self hits; superseded by the LIVE btsup-76729-hr-genie-kb / escalation-82959482 rows carrying BTSUP-76729 today |
| jira-triage-pass-2026-10-17-1213 | 10-17 | superseded — Snowflake grant intake question carried into BSYS-29770/BTSUP-79061 build rows (filed 10-22) |
| night-chain-break-1016 | 10-17 | incident itself repaired + verified same-day (night-chain-repair bus 10-17T22:00Z); the redaction-exclusion ask expired with it |
| jira-triage-pass-2026-10-17-2020 | 10-17 | duplicate of -1213, superseded by BSYS-29770/BTSUP-79061 — **top-3 close candidate** |
| cortex-pulse-2026-10-18-0255z | 10-18 | KB sync on-demand fallback question superseded — kb-digest fallback fixes landed 10-22T22:50Z |
| kb-digest-dead-cycles | 10-18 | kill-PID-35720 ask 6 days moot; sync path since reworked — **top-3 close candidate** |
| kb-sync-rework-closeout-check | 10-19 | the carded memory-cap/single-flight-lock fixes landed via harness-fix entries (kb-digest item 10-22T22:50Z); check ask moot |
| manifest-review (BSYS-29108 draft comment) | 10-14 | BSYS-29108 now status **Deployed** (verified live 10-23, updated 10-23T02:58Z) — the never-posted draft comment is moot |
| cortex-pulse-1019-0237z (in-flight) | 10-19 | one hit = the row itself; pulse closeout with no standing needs; ephemeral |

## Notes / caveats
- Cortex pulse-census bus lines (e.g. 10-23T17:37Z) mention many slugs at once — counted as tracking, NOT corroborating activity.
- Three STILL-ALIVE rows carry asks that were actually EXECUTED (brain-garden, jira-triage-queue-sweep-1020, hr-genie-collector) and one (regression-registry-hygiene) whose ask is likely superseded — all four are closeable-as-done, not alive-and-blocked.
- Read-only: nothing outside this file was touched. Jira reads: BSYS-29806/29824/29827/29829/29108/29510.
