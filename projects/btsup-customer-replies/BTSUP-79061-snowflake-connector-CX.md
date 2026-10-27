# BTSUP-79061 — Snowflake connector for the CX Review Gen Genie

Requester: Nikki Salvie Clarin (CX). Routed by Marc Parilla to Josh 2026-10-16 15:59Z.
Reply posted 2026-10-16 18:07Z as comment 1141491 (public, Josh voice), dissent-checked
two rounds (verdict: stands; bus subject `dissent-btsup-79061-snowflake-conn`).

## The ask

A Snowflake connection usable by integrations.cx@workato.com so the Review Gen Genie
skills can query the PUD (Product Usage Dashboard) and G2 Review tables. Requested as
"mirror my access."

## What the estate shows (live, 2026-10-16)

- Recipe 72454426 "Tool 5 - Search Snowflake for G2 Reviews" already exists in
  AHQ | AI Production (project 15244250), running on connection 19439471
  "Snowflake | Recipe Usage | Schema: G2 (CS_CUSTOMER_EXPERIENCE)" — the exact
  G2-search capability, already built as a Genie tool. The prepared path is
  clone-and-extend of this pattern.
- The Review Gen Genie project lives in AHQ | AI **Development** (project 17453007,
  folder 33900037, 7 recipes) with ZERO Snowflake connections there — dev+prod
  connection pair is needed (connections are workspace-local).
- CX team's own workspace (AHQ | Customer Experience Prod) has its own G2-schema
  connection (13983896) — if the Genie ships there, half the ask already exists.
- All existing Snowflake connections in AHQ | AI are shared service accounts scoped
  by schema (PRISM_GENIE@, DATA_GENIE@, BT_OPS_GENIE@ ...). Personal-mirror is not
  the house pattern.

## Position in the reply

Scoped service connection beats personal mirror (drift argument). Proposed one CX
connection scoped to PUD + G2 schemas (per-schema split offered as alternative).
Named the Snowflake-side dependency: service account + schema grants may not exist
yet; filing for it is step one if so.

## Open (waiting on Nikki)

1. Schema/table names the Genie queries (PUD schema untraceable with available
   tooling — dependency tracker has no recipe-usage rows for the PRISM_GENIE
   Product-DB connection; asking the requester is correct).
2. Which workspace the Genie ships in (AI vs CX).
3. Read-only confirmation.

## Not verified

Whether integrations.cx@workato.com exists as a Snowflake user today; where the
Genie asset itself (vs its recipes) is registered. Connection creation when scoped
is a prod write — Josh's gate.

## Round 2 — Nikki's scoping answers (2026-10-16 19:32Z) + reply 20:12Z

Nikki confirmed: workspace is AHQ | AI, team- or schema-scoped both fine, only PUD
needs a new connection ("we just need one other connection for the PUD tables in
AHQ | AI if doesn't already exist"). Table list came as a screenshot (attachment
277406) that this session could NOT open — no Atlassian API token locally, MCP has
no attachment-download tool; asked her to paste schema/table names as text.

Fresh estate read this round (live, `wt --profile josh-prod`, 20:05Z):

- Re-enumerated all 19 Snowflake connections in prod: none scoped/named for PUD.
  The one broad "Schema: ALL" connection (16138378, GO_GTM_ANALYTICS_AND_INSIGHTS_API_USER,
  healthy) might technically reach PUD tables but rides the wrong identity with far
  too much scope — rejected in the reply as the answer.
- **NEW SIGNAL: connection 22321876 "Snowflake | Data Loading | XS Warehouse |
  Database: Product (pe_product_led_growth@workato.com)" created 2026-10-15 sits in
  authorization_status exception / "400 Bad Request".** Someone's Product-DB
  connection attempt is failing auth — Snowflake-side grants against that database
  are the demonstrated friction, so the CX grant is the long pole, not a formality.
  Not customer-named in the reply (cited as "a Product-database connection stood up
  yesterday").

Dissent: two rounds (round 1 BROKEN — voice break "goes out on Josh's go", "none
reaches PUD" overclaim, Product-DB placement stated as fact, unconditional G2
coverage, "ready to go"; round 2 stands after line-1 swap to "nothing is scoped for
it yet"). Bus thread BTSUP-79061, dissent-btsup-79061-snowflake-conn.

Reply posted 2026-10-16 20:12Z as comment 1141595 (public, jsdPublic=true, verified
rendering). Next: on Nikki's text reply with schema/table names → confirm the CX
Snowflake grant exists (file for it if not) → Josh's go → create the scoped
connection in prod and wire it into the Review Gen Genie skills.

## Status reply 2026-10-27 01:42Z (comment 1149855, public, status-only, dissent-gate skipped)

Nikki asked how long schema grants usually take. Replied honestly: no solid
baseline, request went in 10-23 (4 days), committed to chase the data team and
come back with a real ETA if nothing moves by early next week. NOTE: the chase
is Josh's action (cross-team ask, same class as the original filing). Grant
request draft still at grant-request-draft.md for the record.
