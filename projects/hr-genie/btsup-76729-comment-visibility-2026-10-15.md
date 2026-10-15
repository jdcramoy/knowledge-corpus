# BTSUP-76729 — comment visibility state + JSM MCP gotcha (2026-10-15)

## Ticket state (verified live 2026-10-15 ~12:49Z)

The 05:52Z note (comment 1139318) claiming the evidence comment was "flipped to
internal-only in the Jira UI" is **false against live state**. Customer-visible
(jsdPublic, no visibility marker) with internal IDs:

- **1134812** (2026-10-10) build-complete evidence: recipe IDs 82959474/82959482,
  collector 71498060, job handles, KB kb-AYc8DXFF-rzGerR-CD, incident UUID
- **1138909** (2026-10-14) prod-blocked evidence: prod KB kb-AYcm4ggH-L9o6zm-CD,
  prod collector 71538649, recipe/job IDs
- **1139318** (2026-10-15) the flip note itself

Internal (role "Service Desk Agents", safe): 1134796, 1135182. Public-safe:
1139779 (rewritten to a customer-neutral housekeeping note after an initial
awkward version).

## Josh-only remaining step

JSM has no post-hoc visibility toggle, so: delete the three public comments in
the Jira UI and repost the two evidence comments internal from the compose box.

## Gotcha (general, hit while executing)

The Atlassian MCP **cannot** make a JSM comment internal on this instance:
- `commentVisibility` param is hook-blocked (documented 400), and update/create
  with it never reaches the API — the guard is static, not a live check.
- MCP-posted comments default to **jsdPublic: true (customer-visible)** — there
  is NO way to post internal via MCP. Verify with the `jsdPublic` field on the
  response before assuming a post is internal.
- Orca browser cannot pass Atlassian SSO (Google→Okta wall, FastPass no network
  permission — orca-browser traps ledger 2026-10-13). No local REST token.
- Net: any internal-only JSM content must be posted by Josh in the UI. Plan
  comment strategy around that — do not promise internal posts via automation.

## Open authority items (Josh's call, filed in triage queue)

1. DR promotion of dev recipes 82959474 (FTO re-ingest) + 82959482 (KB Source
   Freshness sentinel) to prod — unblocks the prod fix; publisher 82120576
   already in prod.
2. Manual deletion of the three public comments above.
