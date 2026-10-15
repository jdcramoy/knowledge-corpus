# MCP goes enterprise-grade: stateless transport, IdP auth, and the A2A layer

Librarian procurement beat, 2026-10-11 (smoke run). Topic: the Model Context
Protocol enterprise shift and agent-to-agent interoperability, from the last
two weeks of published material. Four sources, all cited with URL and fetch
date. Additive lane: brand-new file, written to main.

## What is new

1. **The 2026-09-28 MCP enterprise release finalized a stateless protocol.**
   The Agentic AI Foundation (Linux Foundation) shipped the biggest MCP change
   since its creation. Co-creator David Soria Parra called it "in spirit a v2."
   The 2026-07-28 spec had already removed the initialize/initialized
   handshake and protocol sessions; the September release finalized that plus
   Enterprise Managed Authorization, a formal 12-month deprecation policy, and
   official status for MCP Apps and MCP Tasks. (Fetched 2026-10-11)
   Source: https://www.heybeagle.com/blog/mcps-stateless-upgrade-finally-makes-fleet-deployments-boring
   Source: https://www.okoone.com/spark/technology-innovation/how-mcps-biggest-update-changes-enterprise-ai-agent-infrastructure/

2. **Stateless means MCP servers are ordinary HTTP services now.** Client
   info, protocol version, and capabilities ride in a request `_meta` field on
   every call. Any server replica can answer any request. Practical
   consequences per the 2026-10-07 analysis: plain round-robin load balancers
   replace sticky-session gateways; rolling restarts become invisible to
   clients; tool listings become cacheable with TTL; and the new
   `Mcp-Method` and `Mcp-Name` HTTP headers let a gateway route, rate-limit,
   and WAF-rule MCP traffic by header inspection without parsing the JSON
   body. (Fetched 2026-10-11)
   Source: https://www.heybeagle.com/blog/mcps-stateless-upgrade-finally-makes-fleet-deployments-boring

3. **Auth moved from per-user OAuth dances to corporate IdP control.**
   Enterprise Managed Authorization, built with Okta, makes the corporate
   identity provider the authoritative gatekeeper for MCP server access.
   Central onboarding and offboarding replace per-employee authorization of
   each server. Formal OAuth 2.1 resource-server semantics with mandatory
   issuer validation replace bring-your-own-token. (Fetched 2026-10-11)
   Source: https://www.heybeagle.com/blog/mcps-stateless-upgrade-finally-makes-fleet-deployments-boring
   Source: https://www.okoone.com/spark/technology-innovation/how-mcps-biggest-update-changes-enterprise-ai-agent-infrastructure/

4. **The industry settled on two complementary protocols, not one.** MCP is
   the vertical edge (agent to tools); A2A is the horizontal edge (agent to
   agent). A2A reached v1.0 in March 2026; its steward list includes AWS,
   Cisco, Google, Microsoft, Salesforce, SAP, and ServiceNow. MCP SDK
   downloads were near half a billion per month as of July 2026. The
   Berkeley MAST study found roughly four out of five multi-agent failures
   come from specification/design issues and inter-agent misalignment, not
   from the individual agents. (Fetched 2026-10-11)
   Source: https://agenticreview.co/posts/a2a-protocol-and-mcp-interoperability-in-enterprise-agent-architectures

5. **Enterprise vendors are productizing around MCP at scale.** Atlassian
   announced on 2026-10-06 a rebuilt Atlassian MCP: 220+ tools across Jira,
   Confluence, Bitbucket, Loom, Code Search, and Goals, reporting over 15M
   calls per day and up to 25 percent token savings versus the prior version
   on the same Jira and Confluence work (internal benchmarking on Claude
   models). (Fetched 2026-10-11)
   Source: https://www.atlassian.com/blog/company-news/team26-europe-atlassian-mcp

## Why it matters to this house

- **The stateless header-routing pattern mirrors our own MCP gateway
  problem.** The harness runs multiple AIRO MCP servers and routes around
  stale tool-description caches and session-state traps (airo-mcp-playbook).
  `Mcp-Method` / `Mcp-Name` header routing plus TTL-cacheable tool listings
  is exactly the shape of a fix for the stale-schema-cache trap that burned
  8 friction events. Worth a design note when we next touch gateway config.

- **IdP-managed authorization validates the dedicated-app governance.** Josh's
  hard rule (the-right-way principle: dedicated app per automation, no shared
  scopes) is the same direction the protocol is now standardizing: corporate
  credentials, centrally provisioned, never personal tokens shared across
  automations. The enterprise MCP release makes our house rule the industry
  default rather than the exception.

- **Token-efficiency is a measured, competitive axis.** Atlassian claims 25
  percent token savings on identical Jira/Confluence work by tool-surface
  redesign alone. Our cost-governor and RAG++ pipeline already treat context
  cost as first-class; a 220-tool server staying lean proves that per-call
  context budgeting scales, which supports the bounded-read design of the
  google-workspace-semantic and slack-workato servers.

- **A2A is the layer to watch for the fleet.** Our agents already pass work
  through the gossip bus (a bespoke A2A-shaped layer: capability discovery
  via INDEX.md, handoffs, corroboration). If A2A Agent Cards become the
  standard discovery surface, the fleet's agent definitions are already
  close to that shape. No action needed now; flag for the project-dreamer.

- **Deprecation predictability helps our estate planning.** A formal
  12-month deprecation policy gives connector and SDK work a stable clock,
  which the estate-architect's deprecation radar can map against.

## Source list

| # | Source | Published | Fetched |
|---|--------|-----------|---------|
| 1 | Beagle: MCP's Stateless Upgrade Finally Makes Fleet Deployments Boring | 2026-10-07 | 2026-10-11 |
| 2 | Okoone: How MCP's biggest update changes enterprise AI agent infrastructure | 2026-10-07 | 2026-10-11 |
| 3 | Agentic Review: A2A Protocol and MCP Interoperability in Enterprise Agent Architectures | 2026-10-01 | 2026-10-11 |
| 4 | Atlassian blog: Atlassian MCP brings more of your work within reach of any AI agent | 2026-10-06 | 2026-10-11 |

Beat covered: agentic-AI advancements / AI thought leadership, window
2026-09-28 through 2026-10-07 publications. One search pass, 8 results
reviewed, 4 sources fetched in full (bounded extracts).
