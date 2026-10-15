# BSYS-25528 — Vibe-coded application registry (completion plan)

Ticket: https://workato.atlassian.net/browse/BSYS-25528 (epic BSYS-25523, Backlog, points 3).
Plan posted 2026-10-09 (comment 1134657), built 2026-10-10 (build record comment 1134815). This file holds the 2026-10-11 completion plan for the remaining items. No rebuild of what exists.

## Live evidence (2026-10-11)

- Data tables live in dev, folder 31391241: Vibe-Coded App Registry (158543, https://app.workato.com/data_tables/9a08e8dc-57fa-4ea3-baa8-1a0579d73489) and Vibe-Coded App Registry Snapshots (158544, https://app.workato.com/data_tables/db80ccfb-0b98-4f94-b452-8655e3e7ba2f), 10 and 9 columns.
- Monthly Snapshot recipe 82959477 (https://app.workato.com/recipes/82959477): Running=True on live recipe_get, monthly on the 1st at 6:00 AM.
- Could not re-check row counts: the data-table query route returned HTTP 404 on this server today. Registry assumed to hold the UAT probe row only, per the build record.

## Remaining work (in order)

1. Activate the register-app endpoint in the API platform and grant client access (access profile + token), then one live POST for UAT evidence. UI step, dev workspace.
2. Attach the Search Apps skill (skl-AbsoK8JA-XFHMkA-CD, recipe 82959490) to the Internal AI Directory MCP server (asset 5953). One UI action.
3. Baseline import from BT EA's list, then force-run the snapshot job so the first audit snapshot holds real inventory.
4. One-page self-registration guide, linked wherever EA publishes the endpoint.

## Acceptance criteria (ticket)

- [x] Registry table live with required fields (built 2026-10-10)
- [x] Self-registration path (API endpoint; Workflow Apps not on this plan, form deferred)
- [ ] Registry integrated: MCP read tool attached to the Directory server
- [ ] Baseline inventory imported; snapshot re-run after import

## UAT Evidence

One live registration through the activated endpoint, one MCP query returning the new row through the Directory server, one snapshot export post-import, recorded in the ticket with links.

## Risks

None new. Form-versus-endpoint tradeoff settled in the build record; tier/scope discipline enforced downstream by BSYS-25527's review.

## Points

2 remaining.
