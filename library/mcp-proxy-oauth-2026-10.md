# MCP proxy servers and OAuth: the 2026-10 state

Librarian synthesis, 2026-10-25. Procurement note: the fireworks web-search
key was revoked 2026-10-18 and no duckduckgo MCP was attached to this run, so
this pass is KB-internal (RAG++ corpus, nightly-synced, last delta 2026-10-25).
The standing beat (platform.claude.com managed-agents permission policies) was
fetched directly over HTTPS; see the verdict at the end.

## What is new (from the KB corpus)

- Workato Proxy MCP servers support both API-token and OAuth authentication,
  including multiple header parameters (client ID plus client secret). Docs:
  https://docs.workato.com/en/mcp/mcp-authentication.md (KB corpus, synced
  2026-10-25). Docs-watch flagged the "MCP Proxy with OAuth" release to the
  digest on 2026-10-20; the docs surface now carries the full auth section.
- The Verified User Access authentication flow for MCP servers got a
  streamlined OAuth experience (Product Scoop June 2026:
  https://product2.workato.com/product-scoop-june-2026/): fewer clicks for
  end users connecting to MCP tools with their own credentials.
- The MCP Gateway model separates authentication (end user identity) from
  authorization (what the user may do, server level and backend level):
  https://docs.workato.com/en/mcp/mcp-gateway.md.
- Genies can act as MCP CLIENTS (Product Scoop January 2026,
  https://product2.workato.com/product-scoop-january-2026/), consuming
  external remote MCP servers and Workato-hosted ones without custom skill
  development.
- Workato's own CISO-facing content names the ecosystem's structural gap: no
  cryptographic mechanism verifies a server is who it claims to be, so
  name-squatting works (https://product2.workato.com/ten-mcp-security-gaps-cisos-should-know/).

## Why it matters to this house

1. VUA is load-bearing here. Every end-user-facing skill we ship (HR Genie,
   GSlides MCP, AI Directory) keys on vua_required, and the house law is
   read-back-verify after every push (motif vua-revert-on-push). A
   streamlined OAuth flow reduces the friction side of that trade without
   changing the verify side. Keep the read-back law unchanged.
2. Proxy OAuth gives a sanctioned answer to a recurring question: when a
   downstream system needs per-client credentials in headers, the proxy MCP
   server path now supports it natively (docs, above) instead of a
   custom-connector shim. Relevant to the Dev API MCP (BSYS-29894), which
   currently waits on a dedicated Developer API client token.
3. The name-squatting gap is the security argument for the house's
   server-allowlist instincts: we attach MCP servers by explicit config and
   deny by default (deniedMcpServers, mcp-on-demand patterns), which is the
   right posture in a world with no publisher attestation. The red-team gate
   should keep treating "new MCP server attached" as a trust event.
4. Genies-as-MCP-clients is the platform-native version of what the fleet
   does with skills; worth a probe when a Genie needs a tool family we have
   not skill-built. Not urgent, no house surface touched as of 2026-10-25.

## Standing beat verdict (managed-agents permission policies)

Fetched 2026-10-25, https://platform.claude.com/docs/en/managed-agents/permission-policies
(HTTP 200). Trigger condition 1 NOT fired: the surface is still labeled
Managed Agents Beta with beta header managed-agents-2026-04-01. Trigger
condition 2 unchanged in text: policies govern server-executed tools (the
pre-built agent toolset and the MCP toolset), while "custom tools are run by
your application and controlled by you, so they are not governed." Since both
conditions must hold, no migration trigger; client-side hooks remain the
enforcement layer. No claim row filed (unchanged watch, per the watch doc's
own rule).

## Sources

- https://docs.workato.com/en/mcp/mcp-authentication.md (KB corpus, sync 2026-10-25)
- https://docs.workato.com/en/mcp/mcp-gateway.md (KB corpus, sync 2026-10-25)
- https://docs.workato.com/en/mcp/verified-user-access.md (KB corpus, sync 2026-10-25)
- https://product2.workato.com/product-scoop-june-2026/ (changelog corpus)
- https://product2.workato.com/product-scoop-january-2026/ (changelog corpus)
- https://product2.workato.com/ten-mcp-security-gaps-cisos-should-know/ (changelog corpus)
- https://platform.claude.com/docs/en/managed-agents/permission-policies (fetched 2026-10-25)
