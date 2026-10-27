# Blast-radius sweep: workato_db_table trap (`$created_at` orderby / type-tagged filter refs)

Date: 2026-10-23 | Sweep: bounded read-only, wt CLI (`--profile josh-us`) raw API GETs only.
Origin: connector started rejecting `get_records`/`delete_records_by_condition` calls with
'Expected input type ApiDocumentFieldRef' (broke [BTG 2.0] Pending Message Sweeper 83291436 on
2026-10-22, since fixed; [MCP] devapi_retention_sweep 83290173 still failing, BSYS-29894).

## Scope and method
- Population: recipes in the josh-us dev workspace (3535573 / AHQ AI Development) using the
  `workato_db_table` adapter — API reports **1817** (`adapter_names_all=workato_db_table`), all
  1817 fetched across 18 list pages (19 GETs total incl. smoke tests; zero writes, zero stops).
- Bound note: candidate list exceeded the ~60 sample threshold. The list response already carried
  each recipe's full DSL `code`, so the grep/classification ran over ALL 1817 locally at no
  incremental API cost — full coverage instead of a 60-sample. The most-recently-updated-60 slice
  is also reported below.
- Method: parsed each recipe DSL as JSON (0 parse failures), walked every step, kept steps with
  `provider == workato_db_table`, inspected `input.order_by_field_id` and `input.filters[]`.

## Signature tiers (what was searched)
1. `order_by_field_id` set to `$created_at` (sort pseudo-field): **0 hits** fleet-wide. No recipe
   passes the literal pseudo-field today (83291436's fix removed it from `input`; it survives only
   in that recipe's `visible_config_fields`, which is inert UI metadata, not payload).
2. `order_by_field_id` set at all (live sort config): **244 recipes**. All are dashed-UUID field
   literals (accepted shape) except one underscore-form ref (below).
3. **Underscore-form field refs** (`field_id`/`order_by_field_id` shaped `c8020ec3_501d_...`
   instead of dashed `c8020ec3-501d-...`): **4 recipes, 5 steps** — the high-confidence correlate.
   The working fixed recipe (83291436) uses dashed UUIDs + `op_default`/`value_default`; the still-
   failing recipe (83290173) uses underscore UUIDs. Correlation with the ApiDocumentFieldRef error
   is inferred from code shape — confirm against the BSYS-29894 job trace before treating as canon.
4. Type-tagged filter keys (`op_date_time`/`value_date_time`, `op_boolean`, `op_id`, ... rather
   than `op_default`): 415 recipes — a common, apparently benign shape when paired with dashed
   refs; not treated as a trap on its own.

## Hit list (underscore-form refs — recipes to fix or watch)
| Recipe | Name | Step | Signature | State |
|---|---|---|---|---|
| 83290173 | devapi_retention_sweep ([MCP] Workato Developer API Semantic MCP, proj 18341380) | delete_records_by_condition_12f9 (2 flagged steps) | 3 filter refs underscore-form (`c8020ec3_501d_420c_a2ac_5217b5b50031`, `56d89755_964a_45f6_a1e3_59cc921f62d2` op_date_time; `f379ea72_d42c_4d1e_b28c_6f45d32ee3a5` op_default) | **RUNNING — known failing, BSYS-29894** |
| 73032777 | Rebuild Confluence Asset Listing Page ([AI] [BT] [AIAR] AI Asset Registry, proj 16361491) | get_records_74dd | `order_by_field_id` underscore-form `34870e1a_fc2a_499e_80a3_e22d2a973026` + 2 underscore filter refs | stopped, last upd 2026-06-12 |
| 73032775 | Get AI Asset (same project) | get_records | 1 underscore filter ref (`op_id`) | stopped, last upd 2026-06-12 |
| 73032773 | Normalize and Deduplicate Asset Record (same project) | get_records | 2 underscore filter refs (op_default) | stopped, last upd 2026-06-12 |

## Recent-60 slice (as bounded by the sweep instruction)
Of the 60 most recently updated adapter candidates, 21 carry signature tier-2/4 usage, but only
**83290173** carries the underscore-form (high-confidence trap) signature. The other 20 use
dashed-UUID refs and are presumably running clean.

## Unreadable / skipped
None. 1817/1817 recipes parsed and classified; 0 parse failures, 0 skipped, no permissions errors.

## Blast-radius verdict
The `$created_at`-orderby variant of the trap is absent from the dev fleet; the live blast radius
is the underscore-form field-ref variant, held by exactly 4 recipes — the known-failing
devapi_retention_sweep (running, BSYS-29894) plus three dormant June-2026 AI Asset Registry
recipes (stopped, low risk unless restarted) — so the fleet-wide exposure beyond the known incident
is minimal.

## Not verified
- That underscore-form refs are the precise trigger of 'Expected input type ApiDocumentFieldRef'
  (inferred from the working-vs-failing code contrast; needs the BSYS-29894 trace to confirm).
- Whether the 244 dashed-UUID `order_by_field_id` refs all resolve against their target tables
  (stale field IDs would fail differently); not in scope.
- Runtime behavior of the three stopped AIAR recipes (not executed — read-only sweep).
