# Slack by Workato MCP — project notes

## 2026-10-26 — BSYS-30009: Slack Lists/To-Dos scopes + tools (plan posted, comment 1149459)
- Ask: lists:read/lists:write scopes + slackLists.* tools on the Slack by Workato MCP.
- Verified: slackLists.* methods live (docs.slack.dev); scopes exist for bot AND user
  tokens; Lists is paid-plan gated.
- Plan (3 pts): (1) confirm token type FIRST — our MCP connections are user-token
  (Workato Identity) OAuth, bot scopes buy nothing if so; (2) locate connector SDK
  source — NOT findable from CLI this pass (knowledge/tracker/custom_connectors API all
  empty — needs workspace eyes); (3) Slack app scopes (BT app-admin gate); (4) SDK
  actions; (5) re-auth = planned TOKEN SWAP, reinstall revokes the old token → the
  WHOLE MCP loses its tooling between reinstall and re-auth, not just lists tools;
  (6) tool bindings don't auto-appear + descriptions need push; (7) scratch-List tests.
- Dissent materially fixed the plan 3x (downtime scope, token-type fork, estimate).
- Status: plan ready, awaiting Josh's build go.
