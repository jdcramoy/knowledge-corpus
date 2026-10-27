# Snowflake read-grant request — draft for Josh to file (BTSUP-79061)

**Status:** draft staged 2026-10-17. Filing is Josh's call (cross-team ask,
beyond the standing BTSUP reply). Drop this text into whichever queue the
Snowflake/data team actually takes requests through.

---

**Request:** Read grants for a service account on schema `GTM_OPERATIONS`.

**Identity:** `integrations.cx@workato.com` — the CX team's shared identity.
If no service account exists for that identity yet, creating one is part of
this request.

**Grant shape:** read-only on the `GTM_OPERATIONS` schema (SELECT on all
tables in the schema, and USAGE on the schema and its containing database).
Read-only is confirmed sufficient — the Genie only queries.

**Tables (all in GTM_OPERATIONS, per Nikki Salvie Clarin on BTSUP-79061):**
DIM_CALENDAR, PUD_ACCOUNT_INVENTORY, PUD_API_ENDPOINT_DAILY_AGG,
PUD_API_ENDPOINT_INVENTORY, PUD_CONNECTION_DAILY_AGG, PUD_CONNECTION_INVENTORY,
PUD_CREDIT_USAGE_DAILY, PUD_OPA_INVENTORY, PUD_PROXY_TASK_DAILY_AGG,
PUD_RECIPE_CONNECTION_DAILY_AGG, PUD_RECIPE_DAILY_AGG, PUD_RECIPE_INVENTORY,
PUD_TASK_DAILY_AGG, PUD_WORKSPACE_INVENTORY.

(14 tables; Nikki's message ran the last two together —
PUD_TASK_DAILY_AGGPUD_WORKSPACE_INVENTORY is two table names run together in
the paste, so confirm PUD_TASK_DAILY_AGG and PUD_WORKSPACE_INVENTORY both
exist as separate tables when the grant is cut.)

**Why:** the Review Gen Genie (CX team) needs to query the PUD tables as part
of its skills. Schema-scoped read-only beats mirroring a personal role: it
can't silently widen later and doesn't drift as personal access changes.

**Tracked on:** BTSUP-79061 (the scoping is locked there; the G2 side already
rides an existing G2-schema connection, no change needed for it).
