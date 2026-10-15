# Marketo EventOps MCP — project knowledge

- Handoff: ~/Documents/Claude/HANDOFF-Marketo-EventOps-MCP-App-2026-07-17.md
- Tech spec: ~/Documents/Claude/BSYS-26824-technical-spec.md
- Marketo MCP servers (marketo-app-mcp, marketo-lead-activity-ops-dev) were
  unauthenticated at last check (2026-10-02) — complete OAuth before use.

- Related successor project: [[event-process-mcp]] (Event360, BSYS-28196, Aug 2026+) — canonical repo ~/orca/projects/event-process-mcp/.

## Platform limitation (mined 2026-10-10 from the handoff)

- Workato MCP Apps render in a SANDBOXED IFRAME whose only grantable
  permissions are camera/microphone/location/clipboard — a rendered URL can
  be copied but can NEVER open a new browser tab, by design (confirmed
  against Workato MCP App docs). Design the UI to be upfront about it
  rather than look broken.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [MCP servers - Marketo Program Ops](../../kb-corpus/docs/en/mcp/prebuilt-mcps/marketo-program-ops-mcp-server.md)
- [MCP servers - Marketo Leads and Activity Ops](../../kb-corpus/docs/en/mcp/prebuilt-mcps/marketo-leads-and-activity-ops-mcp-server.md)
<!-- kb-bridges:end -->
