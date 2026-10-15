# BSYS-27111 — Outreach MCP: create_prospect tool

Ticket: https://workato.atlassian.net/browse/BSYS-27111
Parent epic: BSYS-25535 MCP Server Build: Outreach (Closed). Project file: ../outreach-mcp.md
Status 2026-10-11 re-triage: build complete in dev (2026-10-10), zero live jobs, UAT evidence is the only remaining work.
Jira: plan comment 1134669 (2026-10-09), build update 1134819 (2026-10-10), re-triage 1134964 (2026-10-11). Points 3 set. Deduped on 2026-10-11 evening pass, no repost.
2026-10-11 evening re-verification (live job_list): recipe 82959480 still at zero jobs — UAT evidence remains the whole remaining gap. State unchanged.

## The ask

A `create_prospect` tool on the Outreach MCP server wrapping POST https://api.outreach.io/api/v2/prospects (JSON:API, `application/vnd.api+json`, OAuth bearer). Required at the tool layer: firstName, lastName, at least one email. Optional: title, company, accountId (nested under `relationships.account.data`), plus occupation/address/tags.

## Current estate state (live, re-pulled 2026-10-11)

- Tool recipe create_prospect 82959480 (handle skl-AbsnzRFK-fnpnPf-CD), RUNNING in dev, folder 30934805 (project MCP | MOPs/Outreach - Sales Engagement): https://app.workato.com/recipes/82959480
  - Trigger: workato_skill.start_workflow (workato_genie.start_workflow is deprecated and cannot be added to new recipes).
  - Validation gate: Ruby snippet before any HTTP call, names each missing/invalid field, returns error_class=validation_error.
  - Dedupe: per-email GET /api/v2/prospects?filter[email]=...; match returns the existing id with created=false and a duplicate notice.
  - Payload: data.type=prospect, no id, emails as array, optional accountId under relationships.account.data as {type: "account", id: <n>}.
  - POST with Content-Type and Accept application/vnd.api+json; error classifier: auth_error (401), transient (5xx/timeout, one retry via monitor), outreach_4xx (Outreach errors[] passed through verbatim).
- Connection: dev Outreach | SDK (integration@workato.com) 15862972. The 2026-10-10 blocker (CON | Outreach MCP 19327220 connection-lost) no longer appears on the recipe's connection list; it now binds 15862972, same custom SDK connector family as prod connection 16364432 (folder https://app.workato.com/recipes?fid=18336632).
- Dev MCP server Outreach MCP | Dev Verification mcps-AbsoJko8-hrL-CD with create_prospect attached: https://app.workato.com/ai_hub/mcp/mcps-AbsoJko8-hrL-CD/overview
- Job history on 82959480: zero jobs. No create, no duplicate rerun, no validation-gate trace has ever run. That is the whole remaining gap.
- KB citation: Workato's Outreach connector made First Name/Last Name/Emails optional in Create Prospect in May 2025 (https://product2.workato.com/platform-connector-releases-in-may-2025/), aligning with Outreach's API. The tool keeps the stricter tool-layer gate on purpose; that is a data-quality choice, not an API constraint.
- Ownership: shared service identity (integration@workato.com) owns tool-created prospects; documented in the tool description. Per-user delegation explicitly out of scope.

## Remaining plan (the only build work left)

- [ ] Run the three UAT scenarios as editor Test jobs on 82959480: validation gate (missing email), clean create (clearly-marked test prospect), duplicate rerun (existing id returned, created=false, no second prospect)
- [ ] MCP round trip through the dev verification server (tool invoked as an MCP tool, not just the Test panel)
- [ ] Post-promotion check on the served tool description (propagation is not automatic; may need an explicit edit on the MCP server page)
- [ ] Delete the stray empty dev server mcps-AbsoJYmY-h6B-CD

## Risks

- Sandbox availability: if no Outreach sandbox is provisioned for the dev connection, UAT runs against the prod instance with a clearly-marked test prospect and immediate cleanup; Josh's call at kickoff.
- Write path on a Closed epic's production MCP server: promotion re-touches a served server; standard post-push description verification applies.

## UAT Evidence

Pending. Expected: sandbox create trace with returned prospect id; duplicate-email rerun trace (existing-id return, no new prospect); validation-failure trace; forced 422 passthrough trace; agent-session MCP round trip.

Points: 3 (build done; remaining is about a half day of evidence work).

Not verified: no live Outreach call has been made by this tool (zero jobs); dedupe behavior and payload shape are verified by DSL read-back and in-house prior art (legacy Create Outreach prospect recipe 4076990, BT Development), not by a trace.
