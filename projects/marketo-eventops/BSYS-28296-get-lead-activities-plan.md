# BSYS-28296 technical plan: Marketo MCP get_lead_activities incomplete history

Posted as ticket comment 1134563 on 2026-10-09 by the jira-autotriage pass.
Status: plan ready, awaiting Josh's build authorization + Marketo connection re-auth.

## TL;DR

- Two tool generations exist; the repro was filed against the pre-rewrite tool.
- Issue 1 (missing Get Lead Changes endpoint): already remediated on paper by
  tool recipe get_lead_changes 75492294 (2026-09-05, project 13683566, folder
  32282299). Never linked back to the ticket.
- Issue 2 (empty standard activity results): the current get_lead_activities
  72856618 is a hardened rewrite (lead-exists precheck, token encoding, type-id
  validation, empty-intermediate-page note) but has ZERO real-caller jobs
  (74/74 history entries are mcp_mock probes from 2026-08-25, pre-rewrite).
- Best remaining root-cause candidate for Issue 2: Marketo's documented
  empty-intermediate-page behavior (position-based paging tokens, moreResult
  true with empty pages, Adobe KCS ka-28493); single-page tool + cursor-chase
  contract makes callers see empty results. Static request construction is
  doc-exact (leadIds param name verified against the OpenAPI; activityTypeIds
  is now required).
- LIVE STATE 2026-10-09: recipe 72856618 STOPPED (this pass stopped it for a
  verification probe); restart FAILS, Marketo connection 19479258 is
  unconnected (config_unconnected). Josh re-auth unblocks.

## Build plan (2 points)

1. Re-auth connection 19479258, restart 72856618, verify Running read-back.
2. Live repro: editor Test on 72856618 (lead 43763092, activity_type_ids=["2"],
   since 2026-08-17) and on 75492294 (lead 4189925, type 13). Record traces.
3. If empty + has_more=true: add server-side auto-pagination loop (bounded) to
   72856618. If data returns: Issue 2 is resolved by the rewrite; close.
4. Author 2 test cases (populated; empty-intermediate fixture), close canon entry.
5. Read back served MCP tools list to confirm get_lead_changes registration.

## Verification evidence (2026-10-09 pass)

- recipe_get live on 72856618 and 73537373 (both generations).
- job_list 72856618: 74 jobs, all succeeded, all mcp_mock, all 2026-08-25.
- Marketo docs: experienceleague activities page, paging-tokens page, KCS
  ka-28493, api-evangelist OpenAPI (leadIds, activityTypeIds required).
- wt recipes start 72856618 -> success:false, config_unconnected (account
  19479258). Connection re-auth is the unblock.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [MCP servers - Marketo Program Ops](../../../kb-corpus/docs/en/mcp/prebuilt-mcps/marketo-program-ops-mcp-server.md)
- [MCP Monday: Two New Marketo MCP Servers Are Live](../../../kb-corpus/changelog/mcp-monday-two-new-marketo-mcp-servers-are-live.md)
- [[MK-13] Agentic - Lead Genie MCP](../../../kb-corpus/confluence/intbt/2138046540-mk-13-agentic---lead-genie-mcp.md)
<!-- kb-bridges:end -->
