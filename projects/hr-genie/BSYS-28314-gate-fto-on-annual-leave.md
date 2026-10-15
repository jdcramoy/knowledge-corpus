# BSYS-28314 — MCP Skill: Gate FTO time-off option on Annual Leave balance (Employee)

Triage pass 2026-10-11. Plan status: build complete in dev (Phase 1 steering 2026-10-06, Option 2 hard block 2026-10-07, remaining-work plan 2026-10-09, UAT staged 2026-10-10). This pass re-verified the estate with fresh reads and confirms the plan is unchanged: what remains is the non-US UAT session and promotion.

## The ask

The Genie only offers FTO when the employee's Annual Leave balance is used up, for all countries except the USA. Built as a generalized steering skill (preferred/allowed/blocked classification) plus a fail-closed hard block at the submit chokepoint.

## Current estate state (re-verified live 2026-10-11, fresh reads)

- [get_my_time_off_options 82839617](https://app.workato.com/recipes/82839617), Running: true. Serialization confirmed today: worker=me, country from get_staffing_worker (ISO 3166-1 alpha-3, never user input), eligible absence types, absence balances, classification delegated to the shared FUNC, telemetry via 78563374.
- [FUNC | Time Off Policy Classify 82862012](https://app.workato.com/recipes/82862012) — shared classifier, single source of truth for recommendation and enforcement.
- [submit_time_off_request 78622059](https://app.workato.com/recipes/78622059) — hard-block guard before any Workday write, fail-closed, audit row per decision.
- [HR Genie | Time Off Policy Audit Log (table 156829)](https://app.workato.com/data_tables/d33e94ae-2798-4713-b405-bfe756fe218b).
- Properties: HR Genie Depletable Plans = Annual Leave; HR Genie FTO Gate Exempt Countries = USA; No-Balance Plans = Flexible Time Off, Contractor Planned Unavailability, Intern Planned Unavailability.
- [Workday End-User MCP server](https://app.workato.com/mcp/mcps-AYbrRaxY-dhF-CD) read-back today: get_my_time_off_options (239379) and submit_time_off_request (130660) both active, VUA Required: Yes. Registration intact.

Evidence on file: US-caller E2E green (jobs j-Abphb6Kz-XsQAxH-CD, j-AbpkBxCa-oEBmok-CD, j-AbrAKWKc-d9xkGw-CD), classifier fixtures PASS, post-refactor steering trace j-Abs3ta44-FXxPXk-CD (also live proof the VUA connection survived the pushes). Workday-native tenant-side enforcement is out of scope per Josh.

## Remaining work (unchanged from the 2026-10-09 plan, re-confirmed today)

1. Non-US steering UAT: Canada-ideal volunteer in the HR Genie dev surface. AL balance > 0: Annual Leave preferred, FTO blocked, Genie steers to AL. AL = 0 (or a second worker): FTO allowed. Transcripts plus traces.
2. Non-US enforcement UAT: first live exercise of the submit BLOCKED branch under that caller; policy message, no Workday request, audit row BLOCKED in table 156829.
3. US regression smoke in the TEST tab (belt and braces; evidence already on file).
4. Promotion of 78622059, 82839617, 82862012, table 156829, and the two properties via the BT managed process; post-promotion VUA mode re-check and smoke.

Rollback posture: property-driven. Removing Annual Leave from HR Genie Depletable Plans restores pre-gate behavior with no code change; the audit table is additive.

## Story points

3 (already set; remaining work is UAT execution plus promotion, about a day once a non-US caller is available).

## Acceptance criteria (remaining)

- [ ] Non-US caller with AL balance: FTO blocked, Genie steers to AL (transcript + trace).
- [ ] Non-US caller with AL exhausted: FTO offered (trace).
- [ ] Submit BLOCKED branch under a real non-US caller: no Workday request, policy message, audit row BLOCKED.
- [ ] US regression smoke green.
- [ ] Promotion completed with post-promotion VUA re-check and smoke.

## UAT Evidence

The only gate is a non-US person in the HR Genie dev surface (Canada ideal, since it holds Annual Leave); it has blocked this Story since August and is the one thing only Josh/HR can supply. Evidence to collect: Genie transcripts, job traces per scenario, ALLOWED and BLOCKED audit rows, post-promotion smoke job IDs.
