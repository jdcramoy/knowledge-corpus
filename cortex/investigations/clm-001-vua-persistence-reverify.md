# Investigation: clm-001 `vua-persistence-after-push` — re-verify

- **Dispatched:** 2026-10-08, READ-ONLY cortex lookup (flagged 7x in the dreamer re-verify queue since 2026-10-07 12:57, never re-verified)
- **Investigator:** cortex subagent
- **VERDICT: CONFIRMED** (current-state integrity verified on live read-back; the revert hazard itself was NOT re-exercised — see Scope limits)

## The claim

`~/.claude/knowledge/claims/claims.jsonl` line 1:

```json
{"id": "clm-001", "subject": "vua-persistence-after-push",
 "claim": "recipe_builder_push can silently revert VUA personalization to the base identity — verify connection mode after every push on VUA skills; re-select only on observed drift",
 "evidence": [rule ~/Documents/CLAUDE.md (Josh ruling 2026-10-06), memory bsys-26815-benefits-skill-state.md (2 regressions 2026-10-01), airo-mcp-playbook trap table (2026-09-11)],
 "confidence": "high", "asserted_at": "2026-10-06", "last_verified": "2026-10-06", "status": "active"}
```

Note: the claim is a **standing hazard rule** ("push CAN revert — verify after EVERY push"), not a claim that VUA always persists. Memory `bsys-26815-benefits-skill-state.md` documents the hazard being **hit twice on 2026-10-01** — every `recipe_builder_push` on recipe 82759555 reverted the Workday steps' connection to "This recipe's connection", flipping the served tool to `VUA Required: No`. The 2026-10-06 Josh ruling in `~/Documents/CLAUDE.md` (and the 2026-09-11 airo-mcp-playbook trap table) codifies the fix sequence: stop -> UI re-select End user's connection on both Workday steps (REST 4 + SOAP 7) -> save -> start -> re-read `mcp_server_get` to confirm `VUA Required: Yes`. Do after **every** future push.

## Live read-back evidence (2026-10-08)

All reads were `mcp_server_get` — read-only, no mutations, no recipe edits, no Slack.

### 1. Workday End-User server `mcps-AYbrRaxY-dhF-CD` (dev workspace, 25 tools)
https://app.workato.com/ai_hub/mcp/mcps-AYbrRaxY-dhF-CD/overview — this is the claim's subject server (benefits skill tool 231372, wired per the memory file).

- **25/25 tools read `VUA Required: Yes`** — including every identity-sensitive tool:
  - `view_benefit_elections` (ID 231372) — Yes (the claim's original skill)
  - `update_payment_elections` (ID 182158) — Yes
  - `enter_timesheet` (ID 202731, BSYS-26812) — Yes
  - `view_payment_elections` (123586), `view_tax_elections` (94080), `action_inbox_task` (109082), `get_my_payslips` (231412) — all Yes
- Auth Type: `workato_idp` (correct VUA transport). Tools Count 25 matches the knowledge-tree note "All 25 tools on mcps-AYbrRaxY-dhF-CD verified VUA after fix" (`domains/workato-platform.md:1149`).
- One tool is **Active: No** (`get_my_time_off_balances`, ID 130656, shadowed by the newer `get_my_time_off_options` 239379) — its `VUA Required` flag is still Yes, so no drift there either.

### 2. Google Workspace Semantic server `mcps-AbYzPeKh-QHG-CD` (dev workspace, 3 tools)
https://app.workato.com/ai_hub/mcp/mcps-AbYzPeKh-QHG-CD/overview — the flagship VUA tool per `projects/google-semantic-mcp.md:903`.

- `google_workspace` (ID 160862) — **`VUA Required: Yes`**, Active. This is the tool whose execution rides the caller's Verified User Access connection; correct.
- `workspace_capabilities` (157771) and `workspace_policy_lookup` (157776) — `VUA Required: No`, **by design** (content-free metadata lookups that never touch user content). Not drift.

### 3. Enhanced Google Slides (PROD) server `mcps-AbEdNLHX-43z-CD` (prod workspace, 62 tools)
https://app.workato.com/ai_hub/mcp/mcps-AbEdNLHX-43z-CD/overview — prod read via `mcp__workato-airo-mcp-prod__mcp_server_get`.

- 60/62 tools `VUA Required: Yes`, including all deck-mutating and sharing tools (`Create_Deck`, `Share_Presentation` — which correctly notes it stays VUA-gated).
- Two exceptions, both plausibly intentional staging/metadata tools: `Host_Asset` (116237) and `List_Design_Systems` (135411) read `VUA Required: No`. `Host_Asset` is storage staging (no end-user identity needed) — fine. **`List_Design_Systems` is an observation, not a claim verdict:** its description says it returns "only systems in the caller's own scope" after a "live Google Slides access check", which sounds caller-scoped; if design-system scoping is expected to ride the caller's identity, this tool may want VUA on. Flagging for a follow-up look (design choice belongs to the google-semantic-mcp project, not this claim).

### Workspace-routing note
The dispatch pointed at the prod read tool; prod resolves only prod-workspace handles. `mcps-AYbrRaxY-dhF-CD` and `mcps-AbYzPeKh-QHG-CD` returned HTTP 404 from prod (they are dev-workspace assets), so their read-backs went through the dev AIRO server's identical read-only `mcp_server_get`. `mcps-AbEdNLHX-43z-CD` was read from prod directly. All three reads are the same live API surface the claim's fix sequence prescribes.

## Verdict reasoning

**CONFIRMED.** Today's live read-back shows VUA personalization intact on every identity-sensitive tool across all three servers checked — the exact flag (`VUA Required: Yes`) the claim's verify-after-every-push rule requires to be present. The operational rule ("verify connection mode after every push; re-select only on observed drift") remains correct, current, and load-bearing.

**Scope limits (what this did NOT verify):**
- The **hazard itself was not re-exercised**. Proving "push can revert" would require an actual `recipe_builder_push` on a VUA skill followed by read-back — a write, excluded by this read-only dispatch. So today's evidence proves *current-state integrity*, not *renewed vulnerability*. Two readings are consistent with the data: (a) no push has hit these skills since the last verified re-selection, or (b) the revert bug was fixed platform-side. The claim's evidence (2 observed regressions, 2026-10-01) still stands as the most recent direct observation of the hazard, so the standing rule stays active either way — the rule is cheap (one read-back per push) and the cost of missing a revert is a silent identity downgrade on live HR tools.
- No live VUA invocation was made (e.g., a real `view_benefit_elections` call) — flag-level read-back only, which is what the claim's fix sequence prescribes.
- `mcp_server_get` does not expose per-step recipe connection settings (the deeper "End user's connection vs This recipe's connection" selection inside recipe 82759555's steps 4/7); the served-tool flag is the observable the claim and the playbook both specify, and that is what was read.

## Recommendation for the ledger

- clm-001 can stay **active, confidence high** — this investigation is a current-state confirmation, and the hazard evidence is unchanged. Suggested `last_verified: 2026-10-08` with this file as the verification pointer.
- The dreamer re-verify loop should stop flagging clm-001 on recency alone: the claim is re-verifiable read-only (this exact procedure), and this file is that procedure's output. Future re-verifies can re-run the three `mcp_server_get` calls in minutes.
- Separate follow-up (not clm-001): confirm whether `List_Design_Systems` on `mcps-AbEdNLHX-43z-CD` should be `VUA Required: Yes`.

*Investigator's own unverified-item disclosure, per house rules: the only unverified thread is the re-exercise limit explained above — no live push was run to re-trigger the hazard, and no live VUA invocation was made (flag-level read-back only, which is what the claim's fix sequence prescribes).*
