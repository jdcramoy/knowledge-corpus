# KB digest — brain-gardener — 2026-10-14

## Change surface (nightly sync)
- no changes since previous sync

## Lens queries (live retrieval)

### platform claims surface
_query: `API behavior limits formulas` (source: docs) — confidence 3.418 bits_
1. [docs] API Access Policies
   https://docs.workato.com/en/api-mgmt/api-access-policies.md
   ## Formula limitations  Workato allows you to [use formulas to transform requests and responses](#transform-data-with-workato-formulas), offering flexibility to dynamically transform data. While most ...
2. [docs] API concurrency
   https://docs.workato.com/en/api-mgmt/api-concurrency.md
   ### Supported formulas  A limited set of Workato formulas is supported when configuring custom authorization expressions. This list is non-exhaustive, and additional Ruby methods may be supported beyo...
3. [docs] Developer API - Endpoints
   https://docs.workato.com/en/workato-api/resources.md
   ## Project properties  | Type | Resource | Description | | --- | --- | --- | | GET | [/api/properties](/en/workato-api/project-properties#list-project-properties) | List project-level properties that ...
4. [docs] Embedded API rate limits
   https://docs.workato.com/en/oem/oem-api/limits.md
   | Collection | Type | Resource | Quota | | --- | --- | --- | --- | | **API clients** | GET | List Developer API Clients: [/api/v2/managed\_users/:managed\_user\_id /developer\_api\_clients](/en/oem/oe...
5. [docs] Manage API clients and applications
   https://docs.workato.com/en/api-mgmt/api-client-mgmt.md
   ## View and manage applications  The **Applications** tab on a client lists every application created for that client, showing the credential type, the configured rules or key, and whether the applica...
6. [docs] Action and fields errors
   https://docs.workato.com/en/recipes/design-time-errors/empty-actions.md
    # Rate limiting  Most APIs have a cap on the number of API calls you can make within a certain period. These limits usually differ by app.  In cases whereby the rate limits may have been reached, the...
7. [docs] Troubleshooting - Formula troubleshooting
   https://docs.workato.com/en/troubleshooting/formula-troubleshooting.md
   ### Solution  Complete the following steps to extract the first value from an array:  1. Go to the recipe step with a field that accepts array input.     2. Activate **Formula** mode in the field wher...
8. [docs] Canvas
   https://docs.workato.com/en/canvas.md
   ### Conditional actions for error handling  IF conditions enable you to control how your recipe responds to different types of errors. You can add them inside an **On error** block or elsewhere in the...
9. [docs] Formulas
   https://docs.workato.com/en/formulas.md
    # Formulas  Users can use formulas to transform data using Workato. Formulas allow users to easily work with and format data. Formulas in Workato are included in allowlists of Ruby methods. Not all R...
10. [docs] Infinite loops
   https://docs.workato.com/en/recipes/infinite-loops.md
   ## Run-time formula errors  Every input field (except for list input fields) can be toggled between text and formula mode. Formulas that didn't throw any design-time errors when the recipe was started...
11. [docs] Common recipe errors
   https://docs.workato.com/en/recipes/design-runtime-error.md
   ## Rate limit revisions  We understand that each business has unique event processing needs. Our goal is to support your objectives by offering flexible rate limits tailored to your specific requireme...

### claude platform changes
_query: `API features limits` (source: claude) — confidence 3.53 bits_
1. [claude] Spend Limits API
   https://platform.claude.com/docs/en/manage-claude/spend-limits-api.md
   ## Overview  The API exposes eight endpoints across two resources:  | Resource                          | Endpoints                                                                                     ...
2. [claude] Rate limits
   https://platform.claude.com/docs/en/api/rate-limits.md
    <Note>   This compatibility layer is primarily intended to test and compare model capabilities, and is not considered a long-term or production-ready solution for most use cases. While it is intended...
3. [claude] Rate Limits API
   https://platform.claude.com/docs/en/manage-claude/rate-limits-api.md
     foreach ($rateLimits->data as $entry) {       $models = $entry->models ? ' (' . implode(', ', $entry->models) . ')' : '';       echo "{$entry->group->type}{$models}\n";       foreach ($entry->limits...
4. [claude] Rate Limits
   https://platform.claude.com/docs/en/api/organization/workspaces/rate_limits.md
   ### Query parameters  - `group_type: optional "batch" or "files" or "model_group" or 3 more`    Filter by group type.    - `"batch"`    - `"files"`    - `"model_group"`    - `"skills"`    - `"token_co...
5. [claude] Rate Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/rate_limits.md
   ### Query parameters  - `limit: optional number`    Number of items to return per page.    Defaults to `20`. Ranges from `1` to `1000`.    default: 20, minimum: 1, maximum: 1000  - `page: optional str...
6. [claude] Permissions
   https://platform.claude.com/docs/en/api/compliance/organizations/roles/permissions.md
   ### List Organization Rate Limits  **GET** `/v1/organizations/rate_limits`  List Messages API rate limits for your organization.  Each entry corresponds to one rate-limit group (either a model family ...
7. [claude] Rate Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/workspaces/rate_limits.md
   ## List Organization Rate Limits  **GET** `/v1/organizations/rate_limits`  List Messages API rate limits for your organization.  Each entry corresponds to one rate-limit group (either a model family o...
8. [claude] Service tiers
   https://platform.claude.com/docs/en/api/service-tiers.md
   ## Rate limits  The rate limits for the Messages API are measured in requests per minute (RPM), input tokens per minute (ITPM), and output tokens per minute (OTPM) for each model class. If you exceed ...
9. [claude] Spend Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/spend_limits.md
   ### Query parameters  - `limit: optional number`    Maximum number of limits per page. Defaults to `20`.    default: 20, minimum: 1, maximum: 1000  - `page: optional string`    Opaque cursor from a pr...
10. [claude] Models (Beta)
   https://platform.claude.com/docs/en/api/beta/models.md
   ### Query parameters  - `limit: optional number`    Number of items to return per page.    Defaults to `20`. Ranges from `1` to `1000`.    default: 20, minimum: 1, maximum: 1000  - `page: optional str...
11. [claude] List Spend Limit Increase Requests (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/spend_limits/increase_requests/list.md
   ## Query parameters  - `limit: optional number`    Maximum number of limits per page. Defaults to `20`.    default: 20, minimum: 1, maximum: 1000  - `page: optional string`    Opaque cursor from a pre...
12. [claude] Permissions (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/rbac_roles/permissions.md
   ### Query parameters  - `limit: optional number`    Maximum results (default: 1000, max: 1000)    default: 1000, minimum: 1, maximum: 1000  - `page: optional string`    Opaque pagination token from a ...

## Your job
Opinion: does anything in the change surface invalidate or strengthen existing claims (clm-*)?
Read the hits, form an OPINION (1-3 lines: how does this relate to ongoing work / your domain?), post it to your gossip-bus outbox. Do NOT file proposals — that is the dreamer's synthesis job.
