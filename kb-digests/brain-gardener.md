# KB digest — brain-gardener — 2026-10-27

## Change surface (nightly sync)
- docs: 9 docs changed
- blog: 88 docs changed
- changelog: 10 docs changed
- inspiration: 19 docs changed
- eip: 103 docs changed
- claude: 663 docs changed
- temporal: 10 docs changed
- n8n: 1361 docs changed
- prefect: 329 docs changed
- restate: 213 docs changed
- mcp: 357 docs changed
- slack: 3227 docs changed
- snowflake: 9184 docs changed
- dbt: 9 docs changed
- trigger: 30 docs changed
- hf-hub: 3 docs changed
- secondary corpora (non-Workato): 15386 docs changed (excluded from the quiet-night floor)
- DELTA 229 workato-owned changed docs (> 50 floor) — this night is NOT quiet regardless of lens results

## Lens queries (live retrieval)

### platform claims surface
_query: `API behavior limits formulas` (source: docs) — confidence 3.479 bits_
1. [docs] Custom authorization
   https://docs.workato.com/en/api-mgmt/custom-authorization.md
   ## Configure custom authorization  Complete the following steps to configure custom authorization for an API endpoint:  1. Go to **Platform > API platform > API collections**.     2. Select the API co...
2. [docs] Apply API proxy transformations
   https://docs.workato.com/en/api-mgmt/api-proxy-transformation.md
   ### Example formula transformation  You can use formulas to define default values for request parameters. For example, you can define a request parameter with a formula to set a default value if the i...
3. [docs] Embedded API - MCP servers
   https://docs.workato.com/en/oem/oem-api/mcp-servers.md
   ### URL parameters  | Name | Type | Description | | --- | --- | --- | | managed\_user\_id | **string** _required_ | Embedded customer Account ID or External ID. External IDs must have the prefix `E` a...
4. [docs] Rate limiting
   https://docs.workato.com/en/recipes/rate-limiting.md
    # Rate limiting  Most APIs have a cap on the number of API calls you can make within a certain period. These limits usually differ by app.  In cases whereby the rate limits may have been reached, the...
5. [docs] Developer API - Endpoints
   https://docs.workato.com/en/workato-api/resources.md
   ## Project properties  | Type | Resource | Description | | --- | --- | --- | | GET | [/api/properties](/en/workato-api/project-properties#list-project-properties) | List project-level properties that ...
6. [docs] Embedded API rate limits
   https://docs.workato.com/en/oem/oem-api/limits.md
   | Collection | Type | Resource | Quota | | --- | --- | --- | --- | | **API clients** | GET | List Developer API Clients: [/api/v2/managed\_users/:managed\_user\_id /developer\_api\_clients](/en/oem/oe...
7. [docs] Manage API clients and applications
   https://docs.workato.com/en/api-mgmt/api-client-mgmt.md
   ### Create a new application  Complete the following steps to create a new application:  1. Go to **API Platform > Clients**, select the client, and go to the **Applications** tab.     2. Click **\+ C...
8. [docs] RecipeOps - API policy rate limit violation trigger
   https://docs.workato.com/en/connectors/recipeops/triggers/rate-limit-violation.md
    # RecipeOps - API policy rate limit violation trigger  Actively monitors API usage across all access profiles and generates events when an access profile exceeds its assigned rate limits. It creates ...
9. [docs] Troubleshooting - Formula troubleshooting
   https://docs.workato.com/en/troubleshooting/formula-troubleshooting.md
   ### Solution  Complete the following steps to extract the first value from an array:  1. Go to the recipe step with a field that accepts array input.     2. Activate **Formula** mode in the field wher...
10. [docs] Date formulas
   https://docs.workato.com/en/formulas/date-formulas.md
   ### Behavior  The formula behaves differently depending on how you call it:  - **No argument** - Returns Pacific Time: `now.in_time_zone` - **Timezone specified** - Converts to the specified timezone:...
11. [docs] Recipe editor
   https://docs.workato.com/en/recipes/editor.md
   ## Configure a recipe step  Select a step to open its configuration panel, where you set up what the step does. Configuring an app step involves selecting the app, the trigger or action, and the [conn...
12. [docs] Formula mode - Add conditions to formulas
   https://docs.workato.com/en/formulas/conditions.md
   ### Behavior  #### `condition`  A boolean expression that evaluates to `true` or `false`.  #### `expression1`  Returns this expression if `condition` is `true`.  #### `expression2`  Returns this expre...

### claude platform changes
_query: `API features limits` (source: claude) — confidence 3.546 bits_
1. [claude] Rate limits
   https://platform.claude.com/docs/en/api/rate-limits.md
   ## About rate limits  * Limits are designed to prevent API abuse, while minimizing impact on common customer usage patterns. * Limits are defined by **usage tier**. Organizations are placed on a tier ...
2. [claude] Spend Limits API
   https://platform.claude.com/docs/en/manage-claude/spend-limits-api.md
   ## Overview  The API exposes eight endpoints across two resources:  | Resource                          | Endpoints                                                                                     ...
3. [claude] List Organization Rate Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/rate_limits/list.md
    # List Organization Rate Limits  **GET** `/v1/organizations/rate_limits`  List Messages API rate limits for your organization.  Each entry corresponds to one rate-limit group (either a model family o...
4. [claude] Rate Limits
   https://platform.claude.com/docs/en/api/organization/rate_limits.md
    # Rate Limits ...
5. [claude] Structured outputs
   https://platform.claude.com/docs/en/build-with-claude/structured-outputs.md
   ### Schema complexity limits  Structured outputs work by compiling your JSON schemas into a grammar that constrains Claude's output. More complex schemas produce larger grammars that take longer to co...
6. [claude] Rate Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/rate_limits.md
    # Rate Limits ...
7. [claude] Rate Limits
   https://platform.claude.com/docs/en/api/organization/workspaces/rate_limits.md
    # Rate Limits ...
8. [claude] Rate Limits API
   https://platform.claude.com/docs/en/manage-claude/rate-limits-api.md
   ## Filtering by group type  Both endpoints accept an optional `group_type` query parameter that restricts the response to a single category:  <CodeGroup>   ```bash cURL   curl "https://api.anthropic.c...
9. [claude] PDF support
   https://platform.claude.com/docs/en/build-with-claude/pdf-support.md
   ### Check PDF requirements  Claude works with any standard PDF. Ensure your request size meets these requirements:  | Requirement               | Limit                                                 ...
10. [claude] Claude Sonnet 5.5
   https://platform.claude.com/docs/en/models/sonnet-5-5/overview.md
   ## Good to know  * Adaptive thinking is on by default. The lowest thinking setting is `between_tools`, which turns off up-front thinking. It works at `high` effort or below. See [What's new in Claude ...
11. [claude] Rate Limits (Beta)
   https://platform.claude.com/docs/en/api/beta/organization/workspaces/rate_limits.md
    # Rate Limits ...
12. [claude] Usage and Cost API
   https://platform.claude.com/docs/en/manage-claude/usage-cost-api.md
   ## See also  Use the Usage and Cost APIs to deliver a better experience for your users, manage costs, and preserve your rate limit. Learn more about some of these other features:  * [Admin API](https:...

## Your job
Opinion: does anything in the change surface invalidate or strengthen existing claims (clm-*)?
Read the hits, form an OPINION (1-3 lines: how does this relate to ongoing work / your domain?), post it to your gossip-bus outbox. Do NOT file proposals — that is the dreamer's synthesis job.
