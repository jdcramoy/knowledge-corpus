# BTSUP-78827 — Data extract: Claude Projects shared org-wide for CS org

Triaged 2026-10-15. Status: UNBLOCKED — key stashed and live-verified (see
correction below); extract can run on Josh's word.

## The ask

Export of Claude Projects shared to "Everyone at Workato", filtered to
creators in Dan Kennedy's Customer Success org (direct + indirect reports).
Fields: project name, claude.ai project URL, creator name/email. Requester:
Mercer Moore, CS AI CoE inventory. Paras Bhavnani confirmed the data is not
in Snowflake and asked if it can come from Claude.

## Finding (dissent-checked 2026-10-15)

The Anthropic **Compliance API** is the right surface:
`GET https://api.anthropic.com/v1/compliance/apps/projects`
(docs: platform.claude.com/docs/en/api/compliance/apps/projects).

- Returns per project: id (tagged `claude_proj_...`), name, created_at,
  updated_at, deleted_at, `is_private` (false = visible to all org members),
  organization_uuid, `user: {id, email_address}` (null if creator departed).
- Paginated (limit max 100, `next_page` token).
- Companion endpoints: `GET /v1/compliance/organizations`,
  `GET /v1/compliance/organizations/{org_uuid}/users`; the projects endpoint
  accepts `user_ids` and `organization_ids` filters.

## Dissenter corrections that changed the plan

1. **Project URL is NOT documented as constructible from the tagged ID.**
   claude.ai project URLs take a UUID; the API returns a tagged ID. Reply
   promises to confirm the mapping before the extract ships, does not promise
   the column.
2. **Key path:** Compliance Access Keys are created in **claude.ai >
   Organization settings > API** by the primary owner or an org owner (NOT
   the Claude Console; Enterprise parent orgs don't appear there at all).
   The Compliance API must also be **enabled at parent-org level by the
   primary owner**. Auth is `x-api-key` + `anthropic-version` headers, NOT
   `Authorization: Bearer` (the docs example's Bearer form was wrong in the
   first evidence packet).
3. **Org scoping:** if Workato has more than one linked claude.ai org,
   `is_private=false` must be filtered by the Workato org's
   `organization_uuid` (`organization_ids` filter), not taken across the
   whole readable tree. Enumerate orgs first.
4. `user` is null for departed creators — those rows ship with empty creator
   fields, disclosed in the reply.
5. Verdict downgraded from "we can pull it" to "the path exists, one
   prerequisite" — nothing has been run.

## CORRECTION (Josh, 2026-10-15): this was proven territory — reply overstated gaps

The original triage reply told Mercer a key needed issuing by an org owner and
that enablement state was unknown. Both were already settled:

- The key has existed since 2026-10-11, stashed in the macOS keychain
  ([redacted: keychain pointer]), originally
  used to mine claude conversations for the Google Semantic MCP project
  (`~/orca/workspaces/workbench/Google-Semantic-MCP/scripts/phrase-miner/mine.mjs`).
- Live-probed 2026-10-15: `GET /v1/compliance/organizations` → 200 (single org
  "Workato, Inc.", uuid `89dcd16e…` — no multi-org scoping ambiguity) and
  `GET /v1/compliance/apps/projects?limit=1` → 200 with the exact schema below.
- So "Open items" above are resolved: enablement confirmed, no owner-seat
  routing needed. Remaining work is just the paginated pull + Workday joins.

Process lesson filed: search knowledge + memory BEFORE triaging
(memory: kb-search-before-triage). Canonical platform doc now lives at
`~/.claude/knowledge/domains/anthropic-compliance-api.md`.

## EXTRACT RUN (2026-10-15 ~15:50Z) — done, deliverables staged

- Full paginated pull: **8,362 projects** total; **550 live + shared
  org-wide** (`is_private=false`, not deleted). Raw:
  `~/Documents/workbench/btsup-78827-extract/projects-raw.json`
  (a parallel session's pull at 15:17 got 8,360 — estate drift of 2 in the
  interval; this run is the fresher source).
- Workday joins via the org-chart closure table (`7a27b5ae…`, snapshot
  `org-j-AbxXT3BF-ge4dzp-CD`, refreshed 16:36Z same day): **217/217 creator
  emails resolved to active employees** with names + business titles; 78
  projects created by a now-departed member carry empty creator fields
  (disclosed limitation).
- Dan Kennedy (employee 348) reporting tree from closure table: **320 active
  direct+indirect reports**. **153 of the 550 org-wide projects** are inside
  his CS org.
- Deliverables in `projects/btsup-78827-claude-projects-extract/`:
  `org-wide-projects-joined-20261015.csv` (all 550, joined),
  `cs-org-dan-kennedy-20261015.csv` (the 153-row CS view — the ask),
  `dan-org-emails.json` (the membership set used for the filter).
- Workday join gotcha (paid once): data-tables REST is
  `POST https://data-tables.workato.com/api/v1/tables/<uuid>/query` with
  where = bare `{column: value}` (operator wrappers 400), and it 429s above
  ~3 rps — 2 threads with backoff held.

## Crosscheck (2026-10-16) — PASS

Two independent derivations of Dan Kennedy's tree, both on the current
snapshot generation (`org-j-Abz6XHaz-33MYKw-CD`, materialized 12:36Z):

- Closure-table descendants of employee 348: 320 people.
- Fresh BFS over the search table's `Manager Employee ID` links: 320 people.
- Set diff: zero delta in both directions, and zero change vs the generation
  the original 153-row CSV was cut on. The shipped CS CSV is confirmed
  correct as-is.

Snapshot-generation note for the org-chart project: both tables carry TWO
generations (current + previous, 1,550 employees / 12,488 closure rows
each); a 4h refresh replaces the older one, and generation version strings
change per cycle — never hardcode a version string across sessions, always
pin by max materialization timestamp. (The original pull's version
`org-j-AbxXT3BF-ge4dzp-CD` was purged overnight.)

Still open: the claude.ai URL column. The Compliance API returns the tagged
`claude_proj_…` id only; the claude.ai URL format uses a UUID the API does
not expose. Flagged in the customer reply rather than promised — if links
are wanted, options are a browser-side mapping pass or asking creators.

## Extract plan (superseded by run above)

1. Enumerate orgs → pin Workato's claude.ai org UUID.
2. Page through `/compliance/apps/projects` filtered to that org.
3. Keep `is_private=false`, `deleted_at=null` rows.
4. Join creator email → Workday for display name.
5. Join to Dan Kennedy's Workday reporting tree (direct + indirect).
6. Deliver CSV to Mercer; confirm the ID→URL mapping first and flag any
   field that needs the admin console instead.

## Open items

- Compliance API enablement state at Workato: unknown (guessing enabled,
  not verified).
- Who holds the primary-owner/org-owner seat: unknown, routing through Josh.
