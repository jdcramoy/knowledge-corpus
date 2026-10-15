# BSYS-28314 plan — MCP skill: gate FTO on Annual Leave balance (remaining work: non-US UAT + promotion)

Ticket: https://workato.atlassian.net/browse/BSYS-28314 (epic BSYS-26808, Backlog, points 3). Plan posted to Jira 2026-10-09 (comment 1134772). The build is DONE in dev (comments 2026-10-06 Phase 1, 2026-10-07 hard block); this plan covers only what remains. UAT staged 2026-10-10 (comment 1134826). Latest triage pass 2026-10-11 (comment 1134956). Status: plan ready, awaiting Josh's build authorization.

## Context

Built assets (Development, project 15643451), all verified in the ticket's own build comments:

- [get_my_time_off_options 82839617](https://app.workato.com/recipes/82839617) (skl-AbphJwLz-EY3t6D-CD) — steering skill, tool #25 on the [Workday End-User MCP server](https://app.workato.com/mcp/mcps-AYbrRaxY-dhF-CD); VUA end-user connection; worker=me, country from staffing profile (never user input).
- [FUNC | Time Off Policy Classify 82862012](https://app.workato.com/recipes/82862012) — shared classifier (depletable-first + USA exception), single source of truth.
- [submit_time_off_request 78622059](https://app.workato.com/recipes/78622059) — hard-block guard before any Workday write; fail-closed.
- [HR Genie | Time Off Policy Audit Log (table 156829)](https://app.workato.com/data_tables/d33e94ae-2798-4713-b405-bfe756fe218b) — one row per enforcement decision.
- Properties: `HR Genie Depletable Plans` = Annual Leave; `HR Genie FTO Gate Exempt Countries` = USA.
- E2E green: US caller steered/offered correctly (jobs j-Abphb6Kz-XsQAxH-CD, j-AbpkBxCa-oEBmok-CD, j-AbrAKWKc-d9xkGw-CD). Classifier fixtures PASS (US-exempt, Canada AL 3d preferred, UK blocked, Canada AL 0 allowed).

What remains, per the 2026-10-07 comment: non-US UAT fixtures and promotion. Workday-native (tenant-side) enforcement is out of scope per Josh.

## Business Requirements (remaining)

- Prove the policy gate for a real non-US employee: Annual Leave balance steers to AL, FTO refused; exhausted AL unlocks FTO.
- Prove the submit BLOCKED branch under a real non-US caller with an audit row.
- Promote the five in-scope assets via the BT managed process.

## Technical Requirements (remaining)

1. **Non-US steering UAT.** A non-US test caller (Canada ideal: has Annual Leave) in the HR Genie dev surface: (a) with AL balance > 0 — options call returns Annual Leave preferred, FTO blocked, Genie refuses to offer FTO and steers to AL; (b) with AL = 0 — FTO allowed. Capture Genie transcripts + recipe job traces.
2. **Non-US enforcement UAT.** First live exercise of 78622059's BLOCKED branch under that caller: policy message shown, no Workday request created, audit row BLOCKED in table 156829 with country/ISO3 + depletable balance. (Dev-proven with temporary test properties in October; this is the real-caller confirmation.)
3. **Regression re-run.** US caller path unchanged (VTO ALLOWED E2E), cancel flow green, non-FTO types unaffected.
4. **Promotion.** Assets 78622059, 82839617, 82862012, table 156829, and the two properties via the BT managed promotion process — this Story is the deployment-request source. Post-promotion: verify VUA/connection mode survived the push (revert recurrence class), re-run the US E2E smoke.
5. **Rollback posture.** Property-driven: removing Annual Leave from `HR Genie Depletable Plans` restores pre-gate behavior for steering and enforcement without code changes; table 156829 is additive and never blocks.

## Acceptance Criteria

- [ ] Non-US caller with AL balance: options call marks FTO blocked; Genie refuses and steers to AL (transcript + trace).
- [ ] Non-US caller with AL exhausted: FTO offered (trace).
- [ ] Submit BLOCKED branch executes under a real non-US caller: no Workday request, policy message, audit row BLOCKED.
- [ ] Audit row fields populated (caller, country/ISO3, requested type, balance, decision, reason, job id).
- [ ] US regression: ALLOWED path + cancel flow green post-refactor.
- [ ] Promotion completed and post-promotion smoke verified (VUA mode re-checked).

## UAT Evidence

- Genie transcripts (fresh conversations), job traces per scenario, audit-table rows for ALLOWED and BLOCKED, post-promotion smoke job IDs.

## Risks

- Non-US test caller availability in the HR Genie dev surface is the long pole (blocked this since August); a Canada-based volunteer or test worker is needed.
- recipe_builder_push VUA revert recurrence — verify connection mode on read-back after any push, per the standing rule.

## Points

3 (already set): remaining work is UAT execution + promotion, roughly a day once a non-US caller is available.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato MCP Server Development Framework](../../../kb-corpus/confluence/extbt/2159444213-workato-mcp-server-development-framework.md)
- [2026/05 May Lookback](../../../kb-corpus/confluence/intbt/2579726560-202605-may-lookback.md)
- [2026/02 February Lookback](../../../kb-corpus/confluence/intbt/2358247562-202602-february-lookback.md)
- [MCP Monday: Workday End User, Databricks Data Explorer, and Twitter/X Are Live](../../../kb-corpus/changelog/mcp-monday-workday-end-user-databricks-data-explorer-and-twitter-x-are-live.md)
<!-- kb-bridges:end -->
