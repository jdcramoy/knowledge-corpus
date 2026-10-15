# BSYS-25527 — Risk-tier classification process + publication gate

Built 2026-10-10 (approved kickoff same day). Dev workspace only — NOT promoted.
Updated plan posted 2026-10-11 (Jira comment 1134966): re-verified recipe stopped, slack_bot connection still None (the one blocker), tables live; remaining points 2.
2026-10-11 evening re-verification (live recipe_get): recipe 82959473 still stopped, slack_bot connection still None — state unchanged, no repost needed.
Jira: BSYS-25527 (build record + UAT evidence in comment 1134814). Epic: vibe-coded app governance; framework approved in BSYS-25524; registry app = BSYS-25528 (not yet built).

## Assets (all NEW, project [AI] [BT] [AIAR] AI Asset Registry, folder 31391241)

- Recipe **Review Risk Tier Classifications Weekly** — id 82959473, https://app.workato.com/recipes/82959473 — clock weekly trigger, Mondays 09:00 America/Los_Angeles. **Currently STOPPED** — start blocked on the slack_bot connection (see below).
- Data table **Vibe App Risk Registry** — id 158539 (UUID e8f88ecc-2a35-4c12-83bd-2e9ea21c9d29). Columns: app_name, app_owner, sharing_scope (personal|team|org|internet), data_sensitivity (public|internal|confidential|restricted), auth_model, external_exposure, declared_tier, risk_tier, publication_gate_status (not_submitted|submitted|approved|rejected), gate_approvers, gate_decision_note, review_status (clear|flagged|escalated), flag_reason, last_reviewed_at.
- Data table **Risk Tier Classification Rules** — id 158541 (8641eb7e-353c-4d46-9c7a-795d3ea8dd66) — 8 rows: sharing_scope personal/team/org/internet → tiers 1-4; data_sensitivity public/internal/confidential/restricted → tiers 1-4. Read live by the recipe every run (rule changes need no recipe edit).
- Data table **Risk Tier Review Event Log** — id 158540 (200d2793-61ed-4020-99f0-51a35ac9321d) — append-only: event_type ∈ tier_bumped | gate_escalated | gate_submitted | gate_decided, old/new value, actor, detail.

## Review semantics

- effective_tier = max(declared_tier, scope-implied, sensitivity-implied), looked up live from the rules table via array `.where` inside one ruby() expression. Under-classified → automatic bump (risk_tier is monotone — never auto-downgrades).
- Internet scope + publication_gate_status != approved → review_status=escalated EVERY week (default deny) until the gate records approved; then the next run clears it automatically.
- Every bump/escalation → event-log row (old/new/actor/reason). Conforming rows → review_status=clear + last_reviewed_at stamped (else-branch update).
- Flag list accumulates in `risk_tier_flags` declare_list; posted to #bt-ea (C08KZFUBGQL) via `slack_bot.post_bot_message` — the recipe's ONLY connection-bearing step.

## Verification (live dev jobs, all succeeded)

- j-AbsoHA8M-LWo9Jf-CD — detection: bumps 1→3 (org), 1→4 (restricted), gate_escalation; conforming rows untouched.
- j-AbsoHtkr-FfFaop-CD — clean path + idempotence: cleared rows get last_reviewed_at; unapproved gate re-escalates weekly.
- j-AbsoJMd8-fYKCnJ-CD — gate closure: recorded submission → approval (approver pair BT EA + Security on the row, decision note) → next run auto-cleared the escalation. 7 event-log rows total = full audit trail.

## Open items (pre-promotion)

1. **Slack bot connection (Josh's hands):** net-new custom OAuth profile + workspace-owned BT-approved Slack app per slack-bot-connection SOP (no personal connections, no borrowed dedicated apps; 0 `slack_bot` connections exist in dev). Then select it on step 13 (post to C08KZFUBGQL), Connect → Allow in a REAL browser (Orca popup trap), then start the recipe.
2. BSYS-25528 registry form: add the classification checklist fields, write to the Vibe App Risk Registry table. Recipe needs no change (reads the table).
3. Reviewer names + escalation path on the epic (Josh/BT EA).
4. Promotion via BT managed process (deployment request from BSYS-25527).

## Traps hit (full detail in airo-mcp-playbook)

- Loop variables are stale to later steps in the SAME iteration (conditions silently never fired — all rows "clear" in a succeeded job). All per-row math now inline; downstream payloads derive from update_record's output record.
- `set_condition` is_true on a boolean pill compiles to a string-vs-boolean compare that never fires. Use ruby 1/0 conversion or a status-string comparison.
- ruby() bindings do NOT renumber on step moves — after any structural edit, re-set every bindings map from fresh `recipe_builder_get_datapills`.
- `[BSYS] BSYS Copilot` project folder (30103591) is grant-locked for AIRO (folder_not_found) — AIAR project folder works.
- Data-table `table_id` in recipe steps wants the NUMERIC id; UUID binding leaves column pills unbound.
- update_record output record nests under `update_record_N['record'][<hash_underscored_field_id>]`.
- `elsif`/`else` parent = the IF block's step number, not the enclosing foreach.
