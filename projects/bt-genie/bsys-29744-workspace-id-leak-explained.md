# BSYS-29744 — the workspace_id "env leak" investigated and explained (2026-10-20)

Ticket: https://workato.atlassian.net/browse/BSYS-29744 (AC item: "workspace_id env leak
investigated and fixed or explained"). Comment posted under Josh's name 2026-10-20T02:47Z,
dissent-reviewed (first hypothesis died, corrected version shipped).

## The flag

Prod job traces on [Create Customer Request 71124238](https://app.workato.com/recipes/71124238)
carried `context.workspace_id: 3535597` — the DEV workspace id (josh-us profile target,
BT US dev) — inside Production jobs (recipe lives in workspace 3535598, AHQ | AI Production).

## What was verified (all read-only)

1. **Source = the Genie trigger's Context, platform-generated.** Prod job
   `j-Ac3tFwYb-NMgAwL-CD`: trigger output context opens `{"genie_id": "8789", …,
   "workspace_id": 3535597, …}`; forwarded verbatim as `data_string` to identity helper
   [71179233](https://app.workato.com/recipes/71179233) ("[BT Genie] LF | Get Current User
   Identity").
2. **No recipe sets it.** Full source walk of 71124238 (90KB): zero hardcoded workspace ids;
   only literal `workspace_id` is doc text inside the tool description. Metadata writes
   (step 8 → table 93782 "Agentic Conversation External IDs"; step 12 → table 66783
   "Conversation metadata") store conversation_id / user_email / issueKey / genie name /
   request type — **no workspace_id column**, zero workspace_id pill references.
3. **Semantics settled by a two-sided observation.** Workato docs
   (https://docs.workato.com/en/agentic/agent-studio/connectors/workato-skill-connector/start-workflow.md)
   enumerate the Context fields — `workspace_id` is NOT documented. The helper's parser
   sample (captured from a dev conversation) shows **genie 6489** "BT Genie GO" stamping
   3535597; the prod jobs run under **genie 8789** (same name, different id — the genie is
   per-workspace) also stamping 3535597. Same value on both sides of the dev/prod split →
   the field is an **org-level constant (likely the org's origin workspace)**, NOT an
   environment marker and NOT the genie's home workspace.
4. **Nothing consumes it.** 71124238 maps only `result.user_email` / `result.user_name`
   from the helper. Helper exposes workspace_id as a parsed field but no caller reads it.

## Verdict

Explained, no fix required. The "leak" is an undocumented platform-generated Context field
carrying the same org constant in dev and prod. Serving prod from a prod-registered genie
would NOT change the value (first hypothesis — dead).

## Reusable rule

> **Never treat `context.workspace_id` from a Workato skill-trigger Context as an
> environment discriminator.** It is undocumented, environment-invariant across this org's
> dev (3535597) / prod (3535598) workspaces, and platform-stamped. Use the workspace
> binding of the recipe itself (recipe `user_id`) for environment context.

## Not verified

Platform-internal semantics of the constant (which workspace exactly it names);
whether genie families outside the BT Genie path show the same value (expected yes).
