# BSYS-29519 v42 exposure audit — independent re-verification (2026-10-25)

**VERDICT: THEORETICAL EXPOSURE ONLY — zero evidence of actual data loss.** Every number from the 2026-10-15 full audit (verdict CLEAN) independently reproduced from live reads on 2026-10-25. Additionally: **the v42 classifier never ran in production at all** — recipe 82862205 does not exist in the prod workspace.

- **Date:** 2026-10-25
- **Auditor:** read-only investigation session (kimi-k3), dispatched by Josh
- **Recipe:** [82862205 REC | HR Genie | Conversation Event Collector](https://app.workato.com/recipes/82862205) — DEV workspace "Workato AHQ | AI" (3535597)
- **Scope honored:** investigation-only, zero writes to any platform asset; only artifact written is this file (Bash append, per headless constraint)

## Profile correction (task said josh-prod; the recipe is dev-only)

- `wt recipes get 82862205 --profile josh-prod` → **HTTP 404** (prod workspace 3535598). Full paginated sweep of the prod recipe list finds **no "Conversation Event Collector" counterpart** — nearest prod HR Genie assets are different systems ([82178945 Conversation Tool Event Collector](https://app.workato.com/recipes/82178945), [82197695 Conversation Telemetry Classifier](https://app.workato.com/recipes/82197695), [82120590 Conversation Outcome Collector](https://app.workato.com/recipes/82120590)).
- Consequence: the v42 window (2026-10-12 07:58 PT → 2026-10-14 12:29 PT) ran entirely in DEV. There is no prod job history to audit and no prod exposure surface. The job-listing audit below was therefore run read-only against the dev profile, where the recipe actually lives.

## Window job census (dev profile, live re-fetch 2026-10-25)

- **177 scheduled runs in-window** — exact reproduction of the prior audit: first `j-AbwE68kA-AxAgFQ-CD` 2026-10-12 16:44:44 PT, last `j-AbxBoo9t-YopgnY-CD` 2026-10-14 12:15:15 PT. Status: **175 succeeded + 2 failed** (`j-AbwramxJ-oDBNEE-CD` 10-14 00:00:55, `j-Abx39wgC-RDtaJW-CD` 10-14 05:38:56 — both PAGE_COMMIT_PROGRESS_REVISION_STALE, both with green successors minutes later).
- Boundary check: the job before the window is `j-Abw39dzz-whRcTc-CD` 2026-10-12 07:26:10 PT — confirming the 07:26–16:44 PT stop-never-restart dead window (recipe stopped, so v42 code only *executed* 16:44 Oct 12 → 12:15 Oct 14, ~43.7h of the ~52.5h deployed window).

## Signature scan — all 177 traces re-fetched and full-text scanned (0 fetch failures)

| Signature | Jobs with hits | Disposition |
|---|---|---|
| `conversation_gone_404` (the loss-branch reason) | **0** | loss branch never fired |
| `"permanent": "true"` | **0** | no permanent skip emitted |
| `not found` / `not_found` (any case) | **0** | clean |
| `PAGE_COMMIT_ASYNC_JOB_FAILED`, `timed_out` | **0** | poll-404/timeout paths never fired |
| bare `404` substring | 11 | **all benign** — every match is a timing float (`0.4043`, `0.0404`, `40.8404`) or a timestamp millisecond (`10:29:53.404`); zero HTTP-404 content |
| `PAGE_BUDGET_EXHAUSTED` | 11 | all line-45 outputs `{"skipped": true, "permanent": "false", "reason": "page_budget_exhausted"}` — non-permanent deferrals, re-swept by later runs |
| `PAGE_COMMIT_PROGRESS_REVISION_STALE` | 2 | the 2 failed jobs; died before checkpoint, watermark held |

Every one of the 13 catch firings is accounted for: 11 non-permanent budget deferrals + 2 visible revision-stale re-raises. **No masked-green permanent-skip signature anywhere.**

## Corroboration channels (all re-verified live)

- **Child page-commit function** [82936791](https://app.workato.com/recipes/82936791): **137/137 jobs succeeded in-window**. All observed child failures predate the window (latest `j-AbtxeLgJ-LQd48a-CD` 2026-10-12 07:13:48 PT — the v41 storm). The poll-404 precondition (child job record vanishing mid-poll) never materialized. (This sweep saw 17 pre-window failures on the boundary page; the prior audit's full-lifetime count was 26 — all pre-window either way.)
- **Sinks stayed fed:** table 158099 (event_revisions) = **77 rows / 21 distinct conversations created in-window** (exact reproduction); table 158100 (capture_observations) = **509 rows in-window** (exact reproduction; note: 158100 has no `conversation_hmac` column — distinct count used `genie_hmac`=1, the row count is the corroboration).

## Conclusion

The dissenter's concern — that v42's substring classifier (snapshot step 45: any error containing "404"/"not found" → permanent skip + watermark advance = masked-green loss) *could* silently drop pages on poll-404 inputs — describes a **real latent defect that was live for ~43.7h of execution but fired zero times**. No 404-class error reached the classifier in any of the 177 runs, no permanent skip was emitted, the watermark never advanced over a skipped conversation, every child commit succeeded, and both sinks received continuous in-window data. This matches both prior audits (2026-10-15 full audit CLEAN; 2026-10-23 sweep "zero actual damage").

**Residual (inherited, platform-structural):** Workato job reports show only the last execution of a looped step, so a transient-404 masquerade in a non-last loop iteration cannot be excluded from traces alone. It remains implausible for the four reasons in the 2026-10-15 audit (watermark arithmetic, TOCTOU race needed, 137/137 child jobs present, any non-404 transient would have re-raised visibly). No new evidence changes that assessment.

**Note on canon:** the earlier finding stands that `regression-canon/canon.jsonl` has no row for the v42 substring-classifier bug class — a fix-forward gap, separate from the (negative) exposure answer.

## Evidence

- Window job list: `/tmp/bsys29519-window-jobs.json`; traces: `/tmp/bsys29519-v42-traces/` (177/177, ephemeral — re-fetch to re-verify)
- Prior audits: `cortex/investigations/82862205-v42-exposure-audit.md` (2026-10-15, CLEAN), `cortex/investigations/bsys-29519-v42-exposure-window.md` (2026-10-23 sweep)
- v42 code snapshot: `app-snapshots/bsys-29519/recipe-82862205-pre-pagecommit-fix.json`
- Ticket: [BSYS-29519](https://workato.atlassian.net/browse/BSYS-29519)
