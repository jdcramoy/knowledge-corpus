# Stale in-flight closure sweep — mission-control registry
**Run:** 2026-10-26T04:30Z (cortex dispatch `stale-inflight-closure-sweep`, read-only)
**Source:** `~/.claude/knowledge/mission-control/registry.json`, fold `folded_at=2026-10-26T04:30:20Z`, 457 workstreams.

## Reconciliation of the dispatch's numbers (133 / 21)
- Live fold: **138 in-flight** + 25 needs-josh (the brief's "133" was a pre-refold snapshot; the registry refolded at 04:30:20Z, 40s after the brief was generated at 04:29:40Z).
- **Stale >=24h among in-flight only: 6.** The brief's **21** matches exactly when needs-josh rows are included: 6 stale in-flight + 15 stale needs-josh = **21 stale OPEN rows**. All 21 are covered below, state-flagged. Only the 6 in-flight rows are registry-strict matches for the brief's wording.

## Evidence methods
Fold = latest event per workstream. Recency probes: build-ledger.jsonl timestamps, file mtimes (excluding mission-control/cortex machinery — the dispatch echo in dreams/bus/cortex.jsonl and triage/queue.jsonl re-listings are NOT activity), events.jsonl max-ts per workstream, and 3 read-only Jira ticket reads (BSYS-29510, BSYS-28309, BSYS-29657).

---

## A. Stale IN-FLIGHT rows (6)

| # | Workstream | Age | Was doing | Classification |
|---|---|---|---|---|
| 1 | jira-autotriage-hr-genie | 339.5h (10-12) | Fleet triage of BSYS-28309/28310/28311 — plans+builds verified done in dev; work should have flipped to needs-josh | **(a) silently-dead as in-flight** — the pass finished; remaining item is Josh's (UAT with live Job Change events; attach 2 comp skills to End-User MCP server). [BSYS-28309](https://workato.atlassian.net/browse/BSYS-28309) still In Progress (updated 10-22) — re-open as needs-josh, don't drop |
| 2 | manifest-review-bsys-29510 | 316.9h (10-12) | Manifest review: verdict delivered (comment 1136008); 5 blocking items pending builder resubmit | **(a) silently-dead — PROVEN** — [BSYS-29510](https://workato.atlassian.net/browse/BSYS-29510) is **Closed/Done** since 2026-10-18. Row can close outright |
| 3 | gws-semantic-gateway | 314.5h (10-13) | PR #5020 split into 5-PR stack (#5033-#5037), awaiting Jasper review | **(b) genuinely-active** — build-ledger shows live filesystem probes on ~/orca/projects/otto/services/gws-semantic-gateway/ at 2026-10-25T01:42Z. Row stale, work is not |
| 4 | josh-writing-voice | 282.9h (10-14) | Next calibration pass planned; needs Josh to name 2-3 people/threads to calibrate against | **(a) silently-dead as in-flight** — waiting-on-Josh ask that never flipped to needs-josh; zero activity since |
| 5 | hr-genie-collector | 271.8h (10-14) | BSYS-29519 v44 fix shipped + verified on [recipe 82862205](https://app.workato.com/recipes/82862205); 24h clean-cadence clock accruing | **(a) silently-dead** — the observation clock elapsed days ago unobserved; no events, no failures filed since. Fix itself was verified; only bookkeeping closure remains |
| 6 | cortex-pulse-1019-0237z | 169.9h (10-19) | One-shot hourly pulse closeout (fold census, attention queue) | **(a) silently-dead** — ephemeral per-pulse artifact; pulse workstreams are snapshots and should auto-close, not linger in-flight |

## B. Stale NEEDS-JOSH rows (15) — included because the "21" only reconciles with these

| # | Workstream | Age | Class | Gated-action wording (verbatim) |
|---|---|---|---|---|
| 7 | sfdc-mcp-picklist-fix | 285.0h | **(a)** | — [BSYS-29657](https://workato.atlassian.net/browse/BSYS-29657) **Closed/Done 10-21**; the picklist question is superseded; row closable |
| 8 | alert-channels | 244.4h | **(a)** | — waiting on Josh System Settings toggles; re-listed in 10-25 decision inbox, no movement |
| 9 | jira-triage-pass-2026-10-17-1213 | 208.3h | **(c) gated-contact** | needs: "his go on the AHQ \| AI Production connection build **(prod write)**" |
| 10 | estate-remediation | 139.9h | **(c) gated-contact** | needs: "Josh: **fire a prod session** to (1) **rotate the Frontify token** in the console ... (4) **execute the personal-connections plan**" (prod rotation + prod connections) |
| 11 | sfdc-accounts-sync | 139.9h | **(c) gated-contact** | needs: "Josh: decide UAT window and **promotion go**"; what: recipe left RUNNING in dev, "red-team verdict will be dispatched at promotion prep" (promotion = prod write) |
| 12 | slack-mcp-token-clone | 121.8h | **(c) gated-contact** | needs: "Josh flips BSYS-29827 to Final Tech Review; team deploys via **Workato UI import** ... start 29 recipes, set Limits ..., **mint alexey-token-prod**" (prod import + prod token mint) |
| 13 | google-slides-mcp | 103.7h | **(a)** | — ask is Josh's (generate 4 ChatGPT images); note the PROJECT is alive: project doc appended 2026-10-26T01:27Z, so the workstream isn't dead, only this ask |
| 14 | invisible-jira-tickets | 79.3h | **(a)** (borderline gated) | needs: "request **Jira admin cleanup** of TEST ticket 29861" — admin-facing but not a Workato prod write/VUA/Slack/connection |
| 15 | bsys-29744-item4-build | 73.3h | **(c) gated-contact — POSSIBLE UNFINISHED PROD STATE candidate** | needs: "Josh confirms the **prod hot-swap: replace trigger description on 71124238** (12,079 -> 15,549 chars, prompt text only, steps untouched)". A staged-but-unexecuted prod hot-swap on a prod-running recipe |
| 16 | super-bt-genie-2-0 | 72.5h | **(c) gated-contact** + **(a) partially superseded** | needs: "**Slack admin approval** of the workspace install request ... then Josh: api.slack.com **Install App > Allow (mints bot token)**, then **Workato connection 22364458 > Connect > Allow**". Superseded in part by row 20 (app created in the right workspace via Slack CLI on 10-24) |
| 17 | btgenie20-p0-rtfix | 71.8h | **(c) gated-contact AND (b) genuinely-active** | needs: "Josh: (1) **authorize Slack connection 22364458** [BTG 2.0] Pilot Slack — both recipes are bound to it and start-validation (config_unconnected) blocks start until authorized; then **wt recipes start 831135...**". Build-ledger shows AIRO mutations (recipe_builder_push on 83113544) **today 2026-10-26T01:35Z** — dual-classified, treat as live |
| 18 | btgenie20-rt-rereview | 71.7h | **(c) gated-contact** | needs: "Josh: **authorize connection 22364458** (one Allow click); pilot channel C0CCC23RH7S added to Approved channels property" |
| 19 | btgenie20-slack-app-move | 71.2h | **(a) superseded** by row 20 | was gated-flavored ("create the app from the prepared manifest... hand me the new app ID") — resolved 10-24 by row 20 |
| 20 | ops-visibility | 66.4h | **(a)** (remediation-gated, not prod-write) | needs: "Josh to approve **restarting ops-server.py (PID 2131)** after the one-line PATH hardening" — local monitoring daemon restart, Josh's remediation gate per policy; [BSYS-29929](https://workato.atlassian.net/browse/BSYS-29929) filed |
| 21 | btg-sweeper-envelope | 43.0h | **(c) gated-contact** | needs: "Three credentials (client id, client secret, signing secret) ... need a **human Show-button click**, then I build the **Workato OAuth profile, re-point the connection**" (Slack connection credential + OAuth re-point) |

---

## Verdict tally
- **(a) silently-dead / superseded / closable-as-bookkeeping:** 10 — rows 1, 2 (proven via BSYS-29510), 4, 5, 6, 7 (proven via BSYS-29657), 8, 13*, 14, 19 (*13's ask is dead but its project is active)
- **(b) genuinely-active elsewhere:** 2 — rows 3 (orca filesystem, 10-25) and 17 (AIRO mutations, 10-26); row 13's project arguably a third
- **(c) gated-contact:** 8 rows — 9, 10, 11, 12, 15, 16, 18, 21 (row 17 dual (b)+(c); row 16 dual (a)+(c))

## POSSIBLE UNFINISHED PROD STATE — highest-risk rows
Per the claim-lifecycle rule, three stale rows carry staged-but-unexecuted prod-side work that must be verified LIVE before any closure sweep touches them:
1. **bsys-29744-item4-build** — a prod hot-swap on prod recipe 71124238 is staged awaiting Josh's confirm. Verify live whether the trigger description was already replaced (a prior session may have executed it without logging).
2. **slack-mcp-token-clone** — prod import of the 29-recipe token-MCP clone was pending Final Tech Review; verify BSYS-29827's actual deploy state before assuming it never landed.
3. **btgenie20-* cluster + btg-sweeper-envelope** — two dev recipes (83113544, 83291436) were re-bound to pilot connection 22364458; start-blocking on Josh's authorization. Dev-scope, but the enqueue path could fire real Slack messages once authorized.

## Recommended closures (Josh-gated, none executed — read-only sweep)
- Safe to close now, evidence in hand: rows 2, 7 (tickets Closed), 5, 6, 19 (superseded), 4, 8, 1 (flip to needs-josh), 14 (close with the admin ask recorded), 13 (close ask, keep project alive).
- Do NOT close without live verification: rows 15, 12, 10, 9, 11, 16, 17, 18, 21.
