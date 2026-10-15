# Investigation: List_Design_Systems VUA flag — `mcps-AbEdNLHX-43z-CD`

- **Dispatched:** 2026-10-08, one-job bounded READ-ONLY follow-up to `clm-001-vua-persistence-reverify.md` (its separate follow-up item)
- **Investigator:** cortex subagent
- **VERDICT: FLAG WRONG** — `List_Design_Systems` should read `VUA Required: Yes` per the project's own documented contract and identity model. High confidence on the *should-be*; the *live harm* is unexercised (see Not verified).

## Question

Should `List_Design_Systems` (tool ID 135411) on the Enhanced Google Slides MCP server `mcps-AbEdNLHX-43z-CD` be `VUA Required: Yes` like its identity-adjacent siblings?

## 1. Observed flag state (live read-back, 2026-10-08)

`mcp_server_get` on the prod server (https://app.workato.com/ai_hub/mcp/mcps-AbEdNLHX-43z-CD/overview, endpoint https://17498.apim.mcp.workato.com, auth type `workato_idp`, 62 tools):

- **60/62 tools: `VUA Required: Yes`** — every deck-read, deck-mutate, comment, share, and all four other design-system pipeline tools.
- **2/62 tools: `VUA Required: No`**:
  - `Host_Asset` (ID 116237) — plausible by design: pure Workato-FileStorage staging, "never uploads to Google Drive," needs no Google identity.
  - `List_Design_Systems` (ID 135411) — **the anomaly under investigation.**
- No other tool diverges from its siblings' pattern. In particular the design-system family splits cleanly: `Extract_Design_System` (135408) Yes, `Recommend_Design_Archetypes` (135409) Yes, `Create_Presentation_From_Design_System` (235363) Yes, `Get_Design_System_Guidance` (231823) Yes, **`List_Design_Systems` (135411) No** — the only family member without the flag.
- Dev twin `mcps-Ab9w3HK9-CRK-CD` (https://app.workato.com/ai_hub/mcp/mcps-Ab9w3HK9-CRK-CD/overview, endpoint https://16704.apim.mcp.workato.com, dev workspace): identical split — `Host_Asset` (108690) and `List_Design_Systems` (134817) are the only two VUA-No tools of 62. So the flag is consistent across both environments (not fresh prod drift from the 2026-10-06/07 work; dev server last updated 2026-09-12, prod 2026-10-02, both carrying the flag).

## 2. Intended VUA posture (documented)

Three authoritative sources, all saying the same thing:

1. **Project contract** — `~/.claude/knowledge/projects/google-slides-mcp.md` (§ Environment identities): "Contract: 62 tools, structured envelope (ok/error_code/retryable/...), **VUA everywhere**, idempotency keys (30-day), revision_id guards, destructive-op preconditions." "VUA everywhere" admits no per-tool exceptions, and no other doc declares one for List.
2. **Confluence Deep Dive: Identity, VUA & the Ownership Model** (BTI page 2939650094, https://workato.atlassian.net/wiki/spaces/extbt/pages/2939650094): "Every interactive tool runs under the calling user's own Google identity... VUA is also the isolation boundary: one caller's registry rows, snapshots, and carriers are invisible to another."
3. **Confluence Deep Dive: The Design-System Pipeline** (BTI page 2938732566, https://workato.atlassian.net/wiki/spaces/extbt/pages/2938732566): the pipeline is `List_Design_Systems → Extract → Recommend → Create`; "Registry rows are caller-scoped and environment-local"; and the pipeline's stated access principle: "If the caller cannot access it, that is the answer."

**The contradiction:** `List_Design_Systems` is the pipeline's entry point, and its own tool description promises "only systems in **the caller's own scope** and only after a **live Google Slides access check**." Both promises presuppose caller identity — which on this server is delivered exclusively by VUA (the Identity deep dive: caller identity lives in the first-level recipe's VUA context; nested/platform paths demonstrably lose it — that is the WRF00400 lesson that produced `make_design_carrier`). A VUA-No invocation has no end-user connection to resolve, so "caller's own scope" and a caller-true access check cannot both hold.

**Registry scoping mechanism** (schema read-back): Design System Registry table `Enhanced Google Slides MCP | Design System Registry` (https://app.workato.com/data_tables/5f4cfda7-66b2-4988-8758-54b5e9797ad4, numeric 143563, 28 cols) scopes rows via a **`scope_hash`** column (required) — a hash of caller identity, matching the project doc's note that caller identity surfaces in skill job traces as `context.user_email`. The per-row **`last_access_verified_at`** column backs the live access check. Neither can be computed from a caller that VUA did not deliver.

## 3. Blast radius (what a non-VUA caller could do)

First, the boundary that still holds regardless of this flag: the MCP endpoint requires `workato_idp` authentication and membership in user group `rVXKpZ8ZkAgFZSHGr7jKWw` (both servers). VUA-No removes the per-user Google connection requirement, not endpoint authentication. Anonymous callers get nothing.

For an authenticated group member **without** an established Google end-user connection, a mis-flagged `List_Design_Systems` enables:

| # | Exposure | Severity | Evidence / reasoning |
|---|----------|----------|----------------------|
| 1 | **Cross-caller registry metadata enumeration.** If the recipe falls back to a non-caller `scope_hash` (empty/default identity) instead of failing closed, the listing returns rows outside the caller's scope: registry_key, source_presentation_hash, master/layout/exemplar counts, opaque manifest/catalog/summary FileStorage paths, carrier_presentation_id. | Medium — violates the documented isolation invariant; metadata only | Registry schema (`scope_hash` required, caller-derived); Identity deep dive isolation paragraph; tool description's "caller's own scope" promise |
| 2 | **Identity laundering / service-identity execution.** The tool's "live Google Slides access check" is a real Google call; without caller VUA it can only execute under the recipe's static prod connection (connection 19921568, per `projects/google-slides-mcp.md` § Environment identities) — a caller-triggered Google access probe running as the service identity, consuming its quota, and verifying the *wrong principal's* access. | Medium — anti-invariant ("never runs as the calling user" inverted: runs as nobody / as the service account), and the check's verdict is meaningless for the caller | Identity deep dive (VUA is how caller identity reaches Google calls); connection 19921568 reference in project doc; unexercised live (see Not verified) |
| 3 | **What is NOT exposed:** raw speaker notes / manifest content (private FileStorage, reachable only via `Get_Design_System_Guidance`, VUA Yes, which re-checks caller authorization per call); source decks (carrier decks live in the *original* caller's own Drive — the listing caller cannot open them); and any pipeline escalation. All four actionable siblings are VUA Yes **and** reauthorize the caller against the source deck, so holding someone else's `registry_key` is inert without independent Drive access to that source deck. | Mitigation | Pipeline deep dive (Extract step 2 reauthorize; Guidance per-call reauth; Create "runs under End user's connection"); prod server tool table (all siblings Yes) |
| 4 | **Blast-radius summary:** bounded to (a) metadata disclosure of other callers' design-system entries in the fail-open case, and (b) wrong-principal execution of the access check. No write path, no note content, no deck access, no privilege escalation. | — | Rows 1-3 |

Bounded further by population: only workato_idp users in the one user group can reach the endpoint at all — this is peer-to-peer leakage inside a small authorized group, not an internet-facing hole.

## 4. Verdict reasoning

**FLAG WRONG.** The documented contract says "VUA everywhere"; the ownership model doc declares VUA the isolation boundary for exactly the registry rows this tool lists; the tool's own description promises caller scoping and a caller-true access check that are unreachable without caller identity; all four sibling pipeline tools carry the flag in both environments; and no document anywhere (project knowledge file, both Confluence deep dives, connector repo) declares a deliberate VUA exception for List — the only documented VUA-No rationale in the family applies to `Host_Asset`, whose description explicitly needs no Google identity, unlike List's live access check. The one thing that would flip this to "flag correct" is a deliberate pre-VUA discovery-surface design decision (let agents browse available systems before completing OAuth) — plausible, but it appears in no doc, and it would contradict the tool description's own scoping promise, so it cannot be assumed. A non-VUA call likely fails closed (empty/zero-row result), which would make this a latent mis-configuration rather than a live breach — but that behavior is inferred, not observed (see Not verified).

**Recommended fix (NOT executed — read-only dispatch, and prod write):** flip `List_Design_Systems` to `VUA Required: Yes` on `mcps-AbEdNLHX-43z-CD` (prod) and `mcps-Ab9w3HK9-CRK-CD` (dev) — Josh-gated per the prod-write rule. If the pre-VUA discovery behavior is actually wanted, instead fix the tool description to stop promising caller-scoped access checks, and document the exception in the Identity deep dive. Either way, close the loop per clm-001's standing rule: after any such change, read back `mcp_server_get` for the flag.

## Not verified (explicit)

- **No live invocation.** `List_Design_Systems` was never called — neither as a VUA caller (would be a live prod tool execution) nor as a simulated non-VUA caller (no non-VUA client was available, and exercising the exposure path was out of scope for a read-only dispatch). The fail-open vs fail-closed question is therefore **open**: what the tool actually returns without VUA context (empty list vs cross-caller rows vs error) is inferred from schema and docs, not observed.
- **Recipe internals not read.** `mcp_server_get` does not expose the backing recipe's ID or code; the `scope_hash` computation and the access check's connection resolution under missing VUA context were not traced. (`recipe_get` would require the recipe ID; the List tool recipe was not identified.)
- **Static-connection fallback assumed, not proven.** Row 2 of the blast-radius table assumes the access check runs under prod connection 19921568 when VUA is absent — taken from the project doc's environment table, not from a job trace of a VUA-less call.
- **Deliberate-exception possibility not ruled out** by evidence — only by absence of documentation. If Josh or the build notes say List is intentionally pre-VUA, the verdict flips to "flag correct, description stale."
- **Flag state is point-in-time** (2026-10-08, both `mcp_server_get` read-backs). Per clm-001, any push touching these tools can change flags silently — re-read before acting on this file.
