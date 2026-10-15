# BSYS-28296 technical plan: Marketo MCP get_lead_activities incomplete/incorrect activity history

Ticket: https://workato.atlassian.net/browse/BSYS-28296
Parent epic: BSYS-25538 (MCP Server Build: Marketo)
Status: BUILD COMPLETE 2026-10-11 (see outcome addendum at the bottom).
Plan posted on the ticket, latest 2026-10-11 refresh = comment 1134952
(prior: 2026-10-09 autopsy 1134563, quota correction 1134608); build
execution and verification = comment 1135001. This edition: 2026-10-11
re-pass, amended same day with the build outcome. Prior edition
(2026-10-09): `~/Documents/../.claude/knowledge/projects/marketo-eventops/BSYS-28296-get-lead-activities-plan.md`

## The ask

Original report (Stefano Mazzalai, filed 2026-08-20 against the pre-rewrite tool):

1. Issue 1, missing endpoint: Data Value Change / New Lead activities live on Marketo's dedicated `Get Lead Changes` endpoint (`/rest/v1/activities/leadchanges.json`, requires a `fields` parameter). The tool only wrapped `/rest/v1/activities.json`, so querying lead 4189925 with activity type 13 returned zero results despite the Marketo UI showing change entries.
2. Issue 2, functional bug: lead 43763092 with `activity_type_ids=["2"]` (Fill Out Form) and `since=2026-08-17` returned zero activities even though the Marketo UI shows a Fill Out Form event on Aug 18 plus Open Email, Email Delivered, Send Email, Add to SFDC Campaign. Wrong type ID, date window, and lead ID were all ruled out in the ticket.
3. Recommendation pending resolution: treat `get_lead_activities` output as non-authoritative; Marketo UI is the reliable source.

## Current state (live evidence, read 2026-10-11)

- The ticket's two-tool-family picture still holds. Current family: project 13683566, folder 32282299, 12 tool recipes, all last touched 2026-09-05. Legacy family: project 14570285, recipes 735373xx, untouched since 2026-06-18.
- [get_lead_activities 72856618](https://app.workato.com/recipes/72856618): Running=False. It is the only stopped recipe in the family; the Oct 9 pass stopped it for a verification probe and the restart failed on the dead connection. Job history: 74 jobs, all mcp_mock probes from 2026-08-25, none since.
- [get_lead_changes 75492294](https://app.workato.com/recipes/75492294): Running=True. It wraps `v1/activities/leadchanges.json`, requires `fields`, accepts 1 to 30 `lead_ids`. Issue 1 is remediated on paper. Job history: 33 jobs, all mcp_mock probes from 2026-08-25, none since. Never linked back to this ticket.
- Connection 19479258 "CON | Marketo MCP" (used by both recipes): read live today as status inactive, authorization_error `Daily quota '100000' reached`. This matches Josh's Oct 9 correction, the limit is a daily API CALL quota, and Marketing Ops is analyzing what consumes the calls.
- Second Marketo connection found in dev: 19655486 "My Marketo account", status active, authorization success. Whether it points at the same Marketo instance the MCP tools serve is unverified, and the name reads as a personal connection, so using it for anything needs Josh's ruling first.
- 72856618's code matches the documented Marketo contract: input validation, lead-exists precheck, paging token via `v1/activities/pagingtoken.json` with URL-encoded sinceDatetime, `activityTypeIds` as a comma list capped at 10, batchSize 1 to 300, cursor passthrough, and a `has_more` plus `cursor` result contract that documents the empty-intermediate-page behavior in the tool description.

## Root cause / working theory

- Issue 1 is not a bug, it was an API surface gap. `leadchanges.json` is now wrapped by 75492294. Remaining work is verification and MCP registration confirmation only.
- Issue 2, best remaining theory: Marketo's activities endpoint can return an empty page while `moreResult=true` (position-based paging tokens, Adobe KCS ka-28493). The tool returns one page per call and hands the cursor back, so a caller that does not chase the cursor sees zero activities even though data exists. A malformed-request cause now looks unlikely, the query construction matches Adobe's documented contract exactly.
- Guess, labeled as such: the reason the repro also fails is that every job on the tool predates the rewrite, so the repro may already be fixed by the hardened code and nobody has been able to run it because the connection has been quota-blocked since at least Oct 9. Only the live repro settles this.
- Watch item: the AIRO recipe read-back flagged binding-path warnings on steps 9 and 12 of 72856618 (the recipe_builder DSL export shows datapill paths that don't resolve). Playbook history says these exports can be misleading, so treat it as a thing to check against the live job trace during the repro, not as a confirmed second bug.

## Proposed fix

Step 0, unblock: confirm Marketing Ops has restored daily call headroom on connection 19479258 (their analysis was in flight as of Oct 9). Then restart [72856618](https://app.workato.com/recipes/72856618) and verify Running by read-back. Fallback if headroom is not restored and Josh wants the verification now: temporarily point the repro at active connection 19655486, only after confirming it serves the same Marketo instance, and only with Josh's explicit OK since it is a personal connection.

Step 1, live repro: editor Test on 72856618 with the ticket's exact inputs (lead 43763092, activity_type_ids ["2"], since 2026-08-17), and on 75492294 for lead 4189925 / fields covering the changed values. Capture both job traces.

Step 2, branch on the repro result:
- If the repro returns data: the rewrite already resolves Issue 2. Close the ticket on that evidence, note the empty-page contract in the tool description, done.
- If the repro returns empty while `moreResult=true`: add an internal auto-pagination loop to 72856618 that chases the cursor server-side until `limit` records, `moreResult=false`, or a bounded page cap (suggest 10 pages), so the tool returns authoritative results without caller cursor-chasing. Rollback posture: single-recipe push, snapshot before push via the build ledger, revert is a snapshot restore of 72856618.

Step 3, regression coverage: author two test cases on 72856618 (populated result; empty-intermediate-page fixture with cursor continuation) and close the canon entry for the empty-page bug class.

Step 4, reconciliation: read back the served tools list on both Marketo MCP servers to confirm `get_lead_changes` is registered alongside `get_lead_activities`. The server handles were not resolvable in this pass, that check happens during the build.

## Story points

2 points. Verification plus conditional auto-pagination patch plus test authoring plus registration read-back, roughly two dev days. If Marketing Ops headroom takes longer than a day to arrange, the wall-clock slips but the effort does not.

## Acceptance criteria

- [ ] Restart of 72856618 verified by read-back, Running=True
- [ ] Live repro on 72856618 with the ticket's exact inputs captured as a job trace, outcome recorded either way
- [ ] Live repro on 75492294 captured as a job trace
- [ ] If empty-with-moreResult reproduces: auto-pagination loop shipped, repro returns the Aug 18 Fill Out Form event in one call, trace cited
- [ ] Two covering test cases authored and passing on 72856618
- [ ] Served tools list on both Marketo MCP servers confirms get_lead_activities and get_lead_changes
- [ ] Ticket comment links the evidence traces before closure

## UAT Evidence

Plan-time evidence (this pass): connection 19479258 read as inactive with `Daily quota '100000' reached`; both recipes' job histories pulled, zero runs after 2026-08-25; recipe code for both tools read live and matched against Adobe's activities contract; family inventory of 12 recipes pulled from folder 32282299.

UAT will add: the two repro job traces with IDs and output summaries, the two passing test case runs, the MCP tools-list read-back, and before/after snapshots of 72856618 if the pagination patch ships.

Not verified in this pass: whether the rewrite fixes the repro (blocked on quota headroom); whether get_lead_changes is registered on the served MCP tools list (server handles not resolvable read-only); whether connection 19655486 serves the same Marketo instance; whether the binding-path warnings on 72856618 steps 9 and 12 are export artifacts or real.

plan ready — awaiting Josh's authorization to kick off the build.

## Outcome addendum (2026-10-11 evening, verify pass)

The build this plan proposed was authorized and executed the same day. Per
ticket comment 1135001, with the plan's steps mapped to what landed:

- Issue 2 root cause proven live: repro job [j-Abtcnkka-HFnNzn-CD](https://app.workato.com/recipes/72856618/job/j-Abtcnkka-HFnNzn-CD) confirmed the empty-page-while-moreResult theory. Fix shipped to [get_lead_activities 72856618](https://app.workato.com/recipes/72856618): server-side cursor chase (bounded 10 pages) returning up to `limit` activities in one call. Verification run [j-AbtdWawL-XWsMhR-CD](https://app.workato.com/recipes/72856618/job/j-AbtdWawL-XWsMhR-CD) returned the ticket's exact Fill Out Form event (2026-08-18 19:41 UTC) on the ticket's exact inputs.
- Issue 1 reconciled: [get_lead_changes 75492294](https://app.workato.com/recipes/75492294) confirmed registered on the served tools list of "Marketo by Workato MCP" (mcps-AaECTcQF-McD-CD). Nothing to build.
- Connection 19479258 cleared via UI Connect after the quota outage left it stuck "Not authorized"; recipe restarted, running.
- Regression: test case `citc-AbtcfET9-tQH6Ba-CD` authored (repro fixture). Still open per the build comment: assertion rows and a second caller-cursor-continuation case (test-case web API rejects non-UI writes), and `cursor`/`has_more` behavior under a real MCP call (nil under the test sandbox).
- Rollback point: pre-fix v9 snapshot at `app-snapshots/bsys-28296/recipe-72856618-pre-pagination-rollback.json`. Recipe at v37, Running per comment 1135001.

Ticket is In Progress with the build complete; remaining items above are the only open work.
