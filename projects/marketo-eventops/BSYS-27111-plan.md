# BSYS-27111 — Outreach MCP: `create_prospect` tool

Ticket: https://workato.atlassian.net/browse/BSYS-27111 (parent epic BSYS-25535 "MCP Server Build: Outreach", Closed; sibling pattern epic BSYS-25538 Marketo). Status at planning: Backlog. Plan posted to Jira 2026-10-09.

## Context

The Outreach MCP server is live in the Workato MCP Registry as "Outreach by Workato MCP" (registry entry id 12288) serving sequence search/creation, prospect and account lookup, prospect update, call logging, and sequence enrollment — but has no prospect-create tool, which is the gap this story fills. The epic is Closed, so this tool lands on an existing production server. Connections: prod "Outreach | SDK" (integration@workato.com), connection 16364432 in workspace 3535598 (folder 18336632). The AI Development workspace (3535597) has no Outreach connection today, so the dev build starts with connection setup. Prior art: a legacy "Create Outreach prospect" recipe exists in the BT estate (recipe 4076990, BT Development) using the same SDK connector, confirming the JSON:API shape in-house.

## Business Requirements

- A sales rep or RevOps user working through an AI agent can create a new Outreach prospect by providing core identifying fields, without hand-writing API calls.
- Data-quality gate: firstName, lastName, and at least one email are required at the tool layer, before any API call.
- No duplicate prospects from agent calls: the prospect email is the unique key, so dedupe runs before create.

## Technical Requirements

- New recipe function `create_prospect` on the existing Outreach MCP server, following the same tool pattern as the server's current tools (recipe function exposed as an MCP tool with an explicit input schema).
- Contract (per the ticket's Outreach API v2 spec): POST https://api.outreach.io/api/v2/prospects, Content-Type and Accept `application/vnd.api+json`, OAuth bearer auth. Payload is JSON:API under `data` with `type: "prospect"` and no `id`; `emails` is an array of strings; optional `title`, `company`, and additional attributes as needed.
- `accountId` (optional integer) nests under `relationships.account.data` as `{ "type": "account", "id": <n> }` — the relationship-nesting gotcha called out in the ticket; the input schema must wrap it correctly or the API rejects the payload.
- Required-field gate: validate firstName + lastName + at least one RFC822-format email before any HTTP call; return a descriptive validation error naming the missing field.
- Dedupe behavior: Outreach keys prospects on email. Pre-check with `GET /api/v2/prospects?filter[email]=<email>` for each submitted email; on a match, return the existing prospect `id` with `created=false` and a duplicate notice instead of a blind POST. If a POST still returns 422 for a duplicate/race, surface the Outreach `errors[]` title/detail verbatim. This makes behavior deterministic regardless of any server-side upsert semantics.
- Response contract: on HTTP 201 return prospect `id`, `firstName`, `lastName`, `emails`, `createdAt`, `created=true`. Do not use `?include=` on create (deprecated by Outreach, Oct 2023); if related account data is needed, make a follow-up `GET /prospects/{id}?include=account`.
- Error classes returned by the tool: `validation_error` (tool-layer gate), `duplicate` (existing prospect returned), `outreach_4xx` (errors[] passthrough), `auth_error` (401), `transient` (5xx/timeout, one retry).
- Ownership note: the created prospect is owned by the user tied to the OAuth credential. The connection is a shared service identity (integration@workato.com), so tool-created prospects are owned by that identity. Per-user delegation is a future decision, explicitly out of scope here.
- Dev prerequisite: create an Outreach connection in the AI Development workspace (sandbox if available) before build; reuse prod connection 16364432 only at promotion.

## Acceptance Criteria

- [ ] Tool exposed as `create_prospect` on the Outreach MCP server with a clear input schema (required + optional fields).
- [ ] Missing required fields returns a descriptive error with no API call made.
- [ ] Valid create returns 201 with prospect id and key attributes.
- [ ] Duplicate email returns the existing prospect id with `created=false`; no second prospect is created.
- [ ] Optional `accountId` nests correctly under `relationships.account.data`.
- [ ] HTTP 422 surfaces the Outreach `errors[]` title/detail to the caller.
- [ ] Verified end-to-end against the Outreach sandbox.

## UAT Evidence

- Sandbox create with the full payload: job trace plus returned prospect id.
- Duplicate-email rerun: trace showing the existing-id return and no new prospect.
- Validation-failure trace (missing email) and a forced 422 passthrough trace.
- Agent-session round trip: tool invoked through the MCP server, not just the recipe Test panel.

## Risks

- Sandbox availability: if no Outreach sandbox is provisioned for the dev connection, UAT runs against the prod instance with a clearly-marked test prospect and immediate cleanup; Josh's call at kickoff.
- Write path on a Closed epic's production MCP server: adding a tool re-touches a served server, so promotion needs the standard post-push verification (tool description propagation is not automatic — the served description may need an explicit edit after push).
- Shared service identity ownership: prospects created by the tool are owned by integration@workato.com; document this in the tool description so agents do not promise per-rep ownership.
- Dedupe pre-check adds one GET per create; rate limits are generous but the pre-check should filter on email, not list-scan.

## Points

3 — about a day: one recipe function with contract validation, dedupe pre-check, error classes, sandbox E2E, and server wiring.

**plan ready — awaiting Josh's authorization to kick off the build.**

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato connectors - Outreach actions](../../../kb-corpus/docs/en/connectors/outreach/action.md)
- [MCP servers - Outlook Contacts](../../../kb-corpus/docs/en/mcp/prebuilt-mcps/outlook-contacts-mcp-server.md)
- [MCP Monday: Outreach Sales Engagement Is Live](../../../kb-corpus/changelog/mcp-monday-outreach-sales-engagement-is-live.md)
- [[MK-13] Agentic - Lead Genie MCP](../../../kb-corpus/confluence/intbt/2138046540-mk-13-agentic---lead-genie-mcp.md)
<!-- kb-bridges:end -->
