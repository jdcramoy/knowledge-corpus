# Underscore-form field-ref correlation — workato_db_table ApiDocumentFieldRef rejections

Date: 2026-10-23 · Investigator: claude (cortex dispatch) · Mode: read-only (wt CLI profile josh-us, dev workspace 3535597 + AIRO read)
Governing story: BSYS-29894 · Failing recipe: 83290173 devapi_retention_sweep (https://app.workato.com/recipes/83290173)

## (a) VERDICT: REFUTED as stated — CONFIRMED in a narrower, restated form

The blanket claim "underscore-form field-id refs are the trigger" is refuted by evidence inside the
failing job itself. The evidence-supported statement is narrower (see (b)).

### Failing job trace — recipe 83290173, job j-Ac6MonKX-6PYrDK-CD (2026-10-22 13:54 PT, the only job ever run)

Job-level error (from job list `error_parts`):
```
parse request payload error: Expected input type "ApiDocumentFieldRef",
found {"field_id":"f379ea72_d42c_4d1e_b28c_6f45d32ee3a5","type":"document"}.
(while parsing "ApiQueryField") (while parsing "ApiQueryCondition")
(while parsing "list_ApiQueryCondition") (while parsing "DeleteRecordsByConditionsRequest")
error_type: Bad Request · error_id 88fc066f-64c5-4cce-8a95-7ca9d0e237c6
```

Line-by-line (wt jobs get):
- Line 0 clock/scheduled_event — fine.
- Line 1 custom Ruby (cutoff calc) — fine, output cutoff 2026-09-07T20:54:20Z.
  (input renders as report_rendering_failed placeholder in trace; known CLI/AIRO render artifact, not the failure.)
- Line 2 workato_db_table/delete_records_by_condition, table 163963:
  input `{"table_id":"163963","filters":[{"field_id":"c8020ec3_501d_420c_a2ac_5217b5b50031","op_date_time":"lt","value_date_time":"2026-09-07T20:54:20.000000Z"}]}`
  → **SUCCEEDED**, output `{"deleted_count": 0}`. NOTE: this is an UNDERSCORE-form field_id that passed request parsing.
- Line 3 workato_db_table/delete_records_by_condition, table 163958:
  input `{"table_id":"163958","filters":[{"field_id":"56d89755_964a_45f6_a1e3_59cc921f62d2","op_date_time":"lt",...},{"field_id":"f379ea72_d42c_4d1e_b28c_6f45d32ee3a5","op_default":"eq","value_default":"EXPIRED"}]}`
  → **FAILED** at request parse, before execution (400 Bad Request). The rejected field is the
  op_default (string) filter, f379ea72_... — the first (date_time) filter is not the one named in the error.

### Control: sibling 83295770 [BTG 2.0] Genie Feedback Capture — 20/20 jobs green

Green job j-Ac6bk9AG-pAoNA3-CD (2026-10-23 00:13 PT):
- get_records, table 164230, filters `[{"field_id":"f0950acc-b6fd-4b50-b093-1b86faa133c5","op_default":"eq","value_default":"btg20_feedback_capture_wm"}]` — DASHED form, op_default, static value → SUCCESS.
- update_record parameters keyed in UNDERSCORE form (`f0950acc_b6fd_4b50_b093_1b86faa133c5`) → SUCCESS.
  So: underscore is the canonical form for record `parameters`/output keys; dashed is what green filters use.

### Widened control: green filters across the dev estate (all DASHED)

| recipe | jobs | filter shape | result |
|---|---|---|---|
| 83191210 Get_Last_State | 3020 succ | 3 filters, dashed, op_default eq + op_boolean "istrue" | green |
| 83290928 FUNC EM Recovery Evidence | 820 succ | dashed, op_default eq | green |
| 83193467 SFD 03 Collect team replies | 127 succ | dashed, op_date_time gte | green |
| 83295770 Genie Feedback Capture | 20 succ | dashed, op_default eq | green |

No green job anywhere in the sample uses an underscore-form filter field_id.

### Schema membership check (rules out stale-field-ID theory)

`GET /api/data_tables?per_page=100` (dev) — canonical schema field_ids are DASHED; all four relevant
IDs exist in their tables:
- f379ea72-d42c-4d1e-b28c-6f45d32ee3a5 = string "status" in 163958 workato_api_plans ✓
- 56d89755-964a-45f6-a1e3-59cc921f62d2 = date_time "expires_at" in 163958 ✓
- c8020ec3-501d-420c-a2ac-5217b5b50031 = date_time "occurred_at" in 163963 workato_api_learning_events ✓
- f0950acc-b6fd-4b50-b093-1b86faa133c5 = string "name" in 164230 ✓

### The 2×2 that decides it

| field_id form | operator path | observed result |
|---|---|---|
| underscore | op_date_time (typed) | PASSED request parse (83290173 line 2, deleted_count 0) |
| underscore | op_default (untyped/string) | FAILED — ApiDocumentFieldRef rejection (83290173 line 3) |
| dashed | op_default / op_boolean / op_date_time | PASS (4 recipes, ~3000 green jobs) |
| dashed | (any) | no counterexample found |

Caveats, honestly stated:
1. Line 2's success proves the request PARSER accepted an underscore ref on the typed date_time path;
   `deleted_count: 0` is also consistent with a vacuous no-match (table was hours old, cutoff 45 days
   back). It does not prove underscore filter semantics are honored. Do not rely on it either way.
2. The other three flagged recipes (73032777, 73032775, 73032773) have ZERO jobs — never run. Their
   flag is static (underscore refs in code), so they add pattern evidence but no runtime evidence.
3. Table 118176 (target of all three 73032xxx recipes) did not appear in the dev data-table list
   (endpoint returns only the 100 newest tables, no pagination metadata, numeric IDs 159653–164257).
   Field-membership for the 73032xxx fix mappings is therefore unverified — re-verify against the live
   schema at fix time; the table may be gone, which would supersede the ref-form fix for those recipes.
4. Static op-token variants in the never-run recipes differ from observed-green tokens and are
   unverified: 73032777 uses op_boolean "is true" and op_default "equals" (green corpus shows
   "istrue" and "eq"); 73032775 uses op_id "eq". Check picklists at fix time.

## (b) Canon trap entry — YES, but restated precisely

Do NOT canonize "underscore-form field refs rejected by workato_db_table connector" (blanket version
is falsified by line 2). Canonize:

> **TRAP: workato_db_table filter refs must use canonical DASHED field UUIDs.**
> In `filters[].field_id` (and `order_by_field_id`) for get_records / delete_records_by_condition /
> update-style query ops, the connector expects the dashed field UUID exactly as returned by the
> table schema (`GET /api/data_tables`). The UNDERSCORE form — which IS canonical for record
> `parameters` maps and output row keys — is rejected on the untyped/default operator path with
> `400 parse request payload error: Expected input type "ApiDocumentFieldRef", found
> {"field_id":"…","type":"document"}`. Underscore refs on typed op paths (op_date_time) have passed
> request parsing (one observation, 83290173 line 2) — do not treat that as license; normalize ALL
> filter refs to dashed. Root cause of the confusion: the same field appears dashed in schema/filter
> contexts and underscored in record-key contexts, so copying an output key into a filter config
> produces exactly this failure. Evidence: cortex/investigations/underscore-fieldref-correlation.md
> (2026-10-23), job j-Ac6MonKX-6PYrDK-CD.

## (c) Minimal fix shape for the 4 flagged recipes

Mechanical transform, per db_table step, in DEV (all four recipes are dev; zero prod contact):
for every `filters[].field_id` and `order_by_field_id`, replace the underscore UUID with its dashed
form (`_` → `-` between the 5 UUID groups), verified against the live table schema. DO NOT touch
`parameters` maps on add_record/update_record — underscore is correct there (proven green in the
sibling's update_record). Apply via AIRO recipe_builder_pull → set_input_field → push, then re-verify
pill mappings survived (known silent static-text replacement trap), then run one dev Test/job and
read the trace.

- 83290173 devapi_retention_sweep (https://app.workato.com/recipes/83290173):
  step 3 filter[1] `f379ea72_d42c_4d1e_b28c_6f45d32ee3a5` → `f379ea72-d42c-4d1e-b28c-6f45d32ee3a5`
  (this is THE failing input). Also normalize step 2 `c8020ec3_501d_420c_a2ac_5217b5b50031` → dashed
  and step 3 filter[0] `56d89755_...` → dashed (both currently "working"/unproven underscore refs).
- 73032777 Rebuild Confluence Asset Listing Page (https://app.workato.com/recipes/73032777):
  get_records filters `71664bd1_...`, `ec2ed3bd_...` → dashed; `order_by_field_id`
  `34870e1a_fc2a_499e_80a3_e22d2a973026` → dashed. ALSO reconcile op tokens against the picklist
  ("is true" vs observed-green "istrue"; "equals" vs "eq") before first run.
- 73032775 Get AI Asset (https://app.workato.com/recipes/73032775):
  get_records filter `11fbe9a6_a16d_4d7e_86ea_afe42ec03005` → dashed (op_id eq — verify op_id path
  accepts dashed form on first run; no green precedent observed for op_id).
- 73032773 Normalize and Deduplicate Asset Record (https://app.workato.com/recipes/73032773):
  get_records filters `67779606_...`, `bde378c7_...` → dashed. Leave add_record/update_record
  `parameters` keys untouched.

Precondition for the three 73032xxx recipes: confirm table 118176 still exists and the dashed IDs
match live schema (this investigation could not list it — see caveat 3). If the table is gone, the
fix is moot and the recipes need a table-rebinding decision instead.

## Evidence provenance

- wt jobs list/get --profile josh-us (read-only): 83290173 job j-Ac6MonKX-6PYrDK-CD; 83295770 job
  j-Ac6bk9AG-pAoNA3-CD; green corpus jobs j-Ac6RhcNT-EDotfD-CD (83191210), j-Ac6bmdAR-ppW6ow-CD
  (83290928), j-Ac4FptsF-EhcaPK-CD (83193467).
- wt api get /api/recipes/<id> (read-only) for static code of 83290173/73032777/73032775/73032773.
- wt api get /api/data_tables?per_page=100 (read-only) for schema field_id forms.
- Zero writes, zero stop/starts, zero test executions performed.
