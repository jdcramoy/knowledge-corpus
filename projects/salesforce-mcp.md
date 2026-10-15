# Project: salesforce-mcp (MCP | BT Managed MCP — SFDC picklist/value options)

Estate assets live in Workato project **MCP | BT Managed MCP** (project_id 13683566,
project folder 27328084), folder *Waterfall Enrichment* (27382500). Local repo
`~/orca/projects/salesforce-mcp` was an empty shell until 2026-10-14 (initial commit,
no docs); the estate is the source of truth, the repo mirrors manifests only.

## Asset map (dev)

- **MCP | Dependency - Find SFDC Picklist values** — recipe 67195423. Function recipe;
  params `object` + `picklist_api_name`; hits SFDC UI-API
  `ui-api/object-info/<object>/picklist-values/012000000000000AAA/<field>` (API v43.0).
  Returns `Results[] {api_name, label}`.
- **MCP | Dependency - Find SFDC options** — recipe 67195424. Caller; hardcodes a
  per-object field list in a step-2 Ruby hash and loops each field through 67195423.
  Branches: `Campaign_Activity__c` (6 fields, all verified green),
  `Contact` (8 unverified fields queried against Contact — latent bug, no current callers),
  `Lead` (pruned 2026-10-14, see below).
- **MCP | Dependency SFDC Value Options** — recipe 67195425; depends on 67195424 +
  lookup table `[LG] SFDC - Values` (3853920).
- Salesforce connection: 13690424 (`integration+btai@workato.com`).

## Incident BSYS-29657 (2026-10-14) — error burst, root cause + fix

- **Symptom:** Estate Monitor error-burst Bug on 67195423 (first seen 2026-10-14 07:06Z).
- **Root cause:** NOT an outage. The Lead field list in 67195424 was copy-pasted from
  Campaign_Activity__c + 2 Cat_ fields; 5 of 8 Lead fields 404 (`NOT_FOUND`) on the
  SFDC UI-API because they are not picklist fields on Lead in the DEV org:
  `Cat_Industry__c`, `Cat_HQ_Country__c`, `Region__c`, `Person_Sub_Region__c`,
  `HQ_Company_Sub_Region__c`. Caller's try/catch swallowed errors, so MCP responses
  still returned (minus those fields) while each failed call landed as a failed job in
  67195423 (1,684 of 4,863 historical, uniform ratio → chronic since build).
- **Fix (DEV):** pruned Lead list to verified picklists `Fit__c`, `Category__c`,
  `Unqualified_Reason__c` (step-2 Ruby hash; step-11 sample doc left stale — sample is
  display-only, runtime loop iterates the Ruby output). Stop→push→start hot-swap,
  `running: true` verified; repeated real Lead job j-AbwsRT4F-TF4tFG-CD → 3/3 function
  calls succeeded, zero 404s.
- **OPEN (needs Josh):** whether Lead *should* expose regional/industry picklists —
  that's an SFDC org change (fields on Lead, or FLS for the integration user), not a
  recipe change. Ticket left In Progress.

## Lessons

- **UI-API 404 semantics:** `NOT_FOUND / The requested resource does not exist` from
  `ui-api/object-info/<obj>/picklist-values/...` = field (or object) not present/not
  visible to the connection user — per-field deterministic, not transient. A "burst"
  of these nightly = a hardcoded list referencing fields that don't exist on that object.
- **Error-burst on a function recipe is a per-caller-iteration event:** when a caller
  loops a dependency function inside a swallowed-error try/catch, the CALLER stays
  green and only the FUNCTION's job history accumulates failures — check the function
  recipe's job list, not just the caller.
- **Same-object success/failure mix means the list, not the code:** when some calls for
  one object 404 and others 200 in the same window, the recipe logic is fine; diff the
  failing field name from the failed line's `path` input against a succeeding one.
- **recipe_builder_set_input_field_v4_mode: object values can't use mode `plaintext`**
  (mode must mirror value shape — dict value needs dict mode); the failure repeats
  identically, so after 2 identical failures switch to writing the literal JSON string.
  Also: sample_document is display-only — don't burn cycles pruning it when the runtime
  loop iterates a Ruby-computed document.
