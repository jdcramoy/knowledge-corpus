# BSYS-29744 — genie identity 8789 vs gin-AWWsELCn-DatcpM (cortex dispatch 2026-10-20T09:39Z)

## VERDICT: IDENTITY-CONFIRMED (leak analysis stands)

Numeric genie id **8789 is a PROD-workspace genie** (named "BT Genie GO", workspace 3535598).
It is NOT the dev genie gin-AWWsELCn-DatcpM — but the original leak analysis never claimed it
was. The analysis file (projects/bt-genie/bsys-29744-workspace-id-leak-explained.md, line 29)
already states: "the prod jobs run under **genie 8789** (same name, different id — the genie
is per-workspace)". The dissenter's premise (that the analysis mapped 8789 → dev handle) is
factually wrong about what the analysis said. Nothing inverts.

## Evidence (all read-only, live-verified 2026-10-20)

1. **PROD side — 8789 = prod genie "BT Genie GO".** Recent job titles on prod recipe
   71124238 (workspace 3535598, via `wt api --profile josh-prod get
   /api/recipes/71124238/jobs?per_page=3` and the specific job
   `/api/recipes/71124238/jobs/j-Ac3tFwYb-NMgAwL-CD`):
   "Workato Genie: start workflow: Genie ID=8789, Genie name=BT Genie GO, and Conversation
   ID=conversation-01M5B…". 3,756 succeeded / 1,801 failed jobs on the recipe.
2. **DEV side — dev BT Genie GO ≠ 8789.** The parser sample_document inside prod helper
   71179233 ("[BT Genie] LF | Get Current User Identity", config read via
   `wt api --profile josh-prod get /api/recipes/71179233`) — captured from a DEV
   conversation — shows `genie_id: "6489"`, `genie_name: "BT Genie GO"`,
   `app_user_id: "genie-6489"`, `workspace_id: 3535597` (dev). Dev numeric id is 6489.
3. **Dev handle confirmed via AIRO (dev-scoped MCP):** `genie_list` /
   `genie_get("gin-AWWsELCn-DatcpM")` → BT Genie GO, dev, 23 skills, stopped. Dev
   `genie_get("8789")` → 404 Genie not found.
4. Genie ids are per-workspace: same name "BT Genie GO" exists as dev 6489
   (gin-AWWsELCn-DatcpM) and prod 8789. Matches the analysis's per-workspace claim.

## Dissent disposition

- Objection "8789 was never mapped to gin-AWWsELCn-DatcpM" — TRUE, and correctly so: they
  are different assets in different workspaces. The objection's conclusion ("prod genie →
  env-leak analysis inverts") does NOT follow: the analysis's two-sided observation IS
  dev 6489 → 3535597 vs prod 8789 → 3535597, the same value on both sides of the dev/prod
  split, which is exactly what supports the org-level-constant verdict.
- AC "workspace_id env leak investigated and explained" remains satisfied: explained, no
  fix required, field is an undocumented org constant, not an environment marker.

## Not verified

- Direct prod genie-list read (no wt/api route for genies found: /api/genies,
  /api/v2/genies, /web_api/genies*.json all 404; AI Directory prod MCP tools
  permission-gated this session). Prod identity of 8789 rests on platform-generated prod
  job titles, which are first-party trace evidence.
- Handle ↔ numeric-id binding for 6489 → gin-AWWsELCn-DatcpM inferred (only one dev genie
  named "BT Genie GO" in the AIRO dev list; the fork BT Genie 2.0 carries a different name).
