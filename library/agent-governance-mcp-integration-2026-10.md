# Agent governance and MCP integration patterns (October 2026 procurement)

Librarian procurement pass, 2026-10-19. Beats this pass: AI advancements
(MCP roadmap and spec direction) and integration development patterns
(agent data-access architectures). Fetch tooling note: the fireworks
web-search server returned 401 earlier on 2026-10-19; this pass used the
duckduckgo-search MCP server (stdio binary driven over JSON-RPC, config
in `~/.claude/mcp-on-demand.json`). All URLs fetched 2026-10-19.

Standing beat (checked first, 2026-10-19): the Managed Agents permission
policies page (https://platform.claude.com/docs/en/managed-agents/
permission-policies) is UNCHANGED on both trigger conditions in
`domains/managed-agents-policy-watch.md`: the page still carries the
beta banner and beta header `managed-agents-2026-04-01` (condition 1,
beta exit, NOT flipped), and it still states "Custom tools are executed
by your application and controlled by you, so they are not governed by
permission policies" (condition 2, MCP-tool carve-out, NOT flipped).
No claim row filed; client-side hooks remain the enforcement layer.

## 1. MCP 2026 roadmap: four priority areas

Source: "The 2026 MCP Roadmap", MCP official blog,
https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/
(fetched 2026-10-19). Context: the last spec release shipped November
2025; the roadmap is now organized around priority areas instead of
release dates, with Working Groups as the primary vehicle. Top four:

1. **Transport evolution and scalability.** Streamable HTTP unlocked
   remote MCP servers, but stateful sessions fight load balancers and
   horizontal scaling needs workarounds. Work: evolve the existing
   transport (no new official transports this cycle, deliberate) plus
   a standard `.well-known` metadata format so a server's capabilities
   are discoverable WITHOUT connecting to it.
2. **Agent communication.** The Tasks primitive (SEP-1686) shipped
   experimental; production feedback surfaced lifecycle gaps: retry
   semantics for transient task failure and expiry policies for
   completed-task results.
3. **Governance maturation.** Of the PROCESS, not permissions: every
   SEP currently needs full core-maintainer review; a contributor
   ladder and Working-Group delegation model are coming.
4. **Enterprise readiness.** Audit trails, SSO-integrated auth,
   gateway behavior, configuration portability. Explicitly the least
   defined area; expected to land as EXTENSIONS rather than core spec
   changes; no Enterprise Working Group exists yet as of the post.

House tie: the `.well-known` server-metadata direction matters for the
MCP Registry surface (registry entries would be discoverable without a
live connection, which changes what a fleet catalog like
`harness-graph` could read instead of scraping configs). The gateway
priority validates the house decision to treat MCP gateways as their
own governed surface rather than an API detail (the gateway
header-routing trap, `library/mcp-enterprise-shift-2026.md`).

## 2. Enterprise agent governance is consolidating on a known shape

Sources (all fetched 2026-10-19, second-tier blog corroboration, treat
specifics as unverified until primary-sourced):

- https://aigovernance.com/news/ai-governance-weekly-october-15-2026
- https://www.strac.io/blog/enterprise-ai-agent-governance
- https://www.ruh.ai/blogs/ai-governance-enterprise-ai-agents-2026-compliance-playbook

Convergent recommendations across these: named ownership per deployed
agent, pre-authorized permission scopes per agent, action-level
behavioral logging, predefined human-intervention thresholds, and an
enterprise agent registry. One source's 90-day rollout ends in a
governance review with legal and security stakeholders.

House tie: the fleet already runs most of this shape end to end:
people-filed ownership, `never_auto` scopes, heartbeat + bus behavioral
logs, and the registry row pattern in mission-control. The gap an
external auditor would still find: ownership for one-off script jobs
(the "ephemeral bus identity" problem the gardener flagged 2026-10-18,
finding L5: unregistered one-shot outboxes). If an Enterprise WG forms
upstream, watch it; the shape is converging on what this house already
practices, which is mildly reassuring and worth citing when the
managed-agents GA decision comes.

## 3. Integration patterns: the direct-API to gateway arc is settled wisdom now

Source: "AI Agent Data Integration: 5 Patterns Compared (2026 Guide)",
Promethium, https://promethium.ai/guides/ai-agent-data-integration-
patterns-compared/ (fetched 2026-10-19; vendor blog, marketing-adjacent
figures, direction sound). Five patterns compared: direct API calls
with function calling, MCP gateways, data warehouses, virtualization,
AI-native fabric.

The load-bearing claims for this house:

- Direct function-calling integration deploys fastest (days) but
  breaks past roughly 10 to 15 APIs: per-integration auth, retry, rate
  limit, and versioning code becomes the dominant cost, and audit
  logging scatters across target systems so no one can reconstruct an
  agent's full call chain. Corroborates the house governance rule
  (2026-10-08 hard correction): dedicated app, custom OAuth profile,
  scoped connection BEATS the fast path, because the governed path is
  the one that keeps credentials and audit in one place.
- Gateway-mediated access (MCP as the integration layer) is now a
  named pattern in mainstream guidance, not an experiment: the value
  claim is central enforcement of access control and audit at one
  layer. This is the same argument the fleet's MCP Registry and
  workato-guardrails already implement client-side.
- Cost figure to treat skeptically: integration custom code claimed at
  25 to 40 percent of total AI project cost. Cite as "vendor estimate,
  2026-03" if ever used.

## 4. What this changes for the house

Nothing operational this pass. The managed-agents watch did not fire;
the roadmap items that touch us (`.well-known` metadata, Tasks
lifecycle, enterprise extensions) are upstream directions, not
spec changes to adopt. Carried observations for future passes:

- Watch the MCP Enterprise WG's formation (roadmap post invites
  founders); its output will define the audit/auth extension surface
  our prod-write gate would eventually port to.
- The one-off-identity hygiene finding (gardener L5, 2026-10-18) is
  the same weakness external governance frameworks call "agent
  inventory completeness"; the existing channels-registry is the fix,
  the gap is emitter discipline.
- Fireworks web-search 401 (2026-10-19) is an availability gap in the
  procurement stack; duckduckgo stdio fallback proven workable this
  pass via manual JSON-RPC.

## Source list (URL + fetch date, all 2026-10-19)

- https://platform.claude.com/docs/en/managed-agents/permission-policies (standing beat)
- https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/ (fetched in full)
- https://aigovernance.com/news/ai-governance-weekly-october-15-2026 (search result only)
- https://www.strac.io/blog/enterprise-ai-agent-governance (search result only)
- https://www.ruh.ai/blogs/ai-governance-enterprise-ai-agents-2026-compliance-playbook (search result only)
- https://promethium.ai/guides/ai-agent-data-integration-patterns-compared/ (fetched in part)


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Agent governance + MCP integration patterns, 2026-10](library/agent-governance-mcp-integration-2026-10.md) — procured 2026-10-19: MCP 2026 roadmap four priorities (.well-known metadata, Tasks lifecycle, enterprise extensions); governance frameworks converge on house shape; direct-API-to-gateway arc corroborates dedicated-app rule; fireworks 401 noted, duckduckgo stdio fallback proven; standing beat unchanged both conditions