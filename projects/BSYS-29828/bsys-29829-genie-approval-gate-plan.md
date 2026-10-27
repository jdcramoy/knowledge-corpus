# BSYS-29829 — Technical plan: Genie destructive-capability approval gate

Status: plan ready — awaiting Josh's authorization to kick off the build.
Parent: BSYS-29828 (Genie Governance — Autonomous-Action Approval Gates)
Dissenter: CONTEST on first draft (7 material defects, all incorporated); re-run pending —
see ~/.claude/knowledge/dreams/bus/dissenter.jsonl thread `bsys-29829-plan`.
Posted: (pending)

## Current state verified live 2026-10-21 (read-only)

- **Drift Fix Genie (gin-AbWxkCLd-8wRwmG-CD) is STARTED again** — restarted 2026-10-20 23:49 PT.
  The other three drift genies (Check, Investigation, Remediation) are still stopped. WHO restarted
  it is the most important open question on the ticket. No unilateral re-stop — may be Josh's own
  overnight work; stopping could destroy state.
- **Attribution UNPROVEN.** "Joshua Cramoy (via AIRO)" is equally consistent with any local agent
  session using the ungated AIRO MCP `data_table_delete` tool. Genie theory weakened by Drift Fix
  Genie's own instructions ("Never run a mutating statement"). The gate covers BOTH vectors.
- **Deleted table already recreated by an overnight actor:** `[LOG] DriftFix_Apply_Log` (numeric
  163016, folder 35701677) exists again; `log_proposal` (82896390) re-pointed to it 03:11 PT today;
  `revise_fix`/`retrieve_proposal` updated 04:15/04:50 PT. Only `get_fix_proposals` (83074639)
  still points at dead table 157379 — failing "Data table not found", latest failing job
  j-Ac4arQMK-oXP9BB-CD.

## P1 — Automated destructive-capability inventory (~3 pts)

All 257 genies (one paged API call), started and stopped. Script the sweep: pull each genie's
skills + backing recipe code, grep-classify destructive verbs (delete/update/overwrite on recipes,
data tables, connections, files, KB docs, MCP servers), human-review only destructive-classified
hits. Findings table on the ticket: genie, skill, recipe, class, state, confirmation-flag.

## P2 — The gate: native confirmation flag + Jira approval (~1.5 pts)

Native per-skill `requires_user_confirmation` flipped to true on every destructive-classified skill
(P1 output drives it) — hardest, cheapest enforcement first. On top: requester files a BSYS
submission naming genie/capability/scope/rollback; approval = Jira transition; execution after,
evidence posted. Headless (recipe-invoked) genies blunt the confirmation flag — the Jira gate
carries that class. MCP-agent destructive tool use (data_table_delete-class) comes under the same
Jira gate.

## P3 — Watchdog (~2 pts, blind spots stated)

15-min scheduled poll (Estate Monitor pattern): genie states + skills_count/active_recipes_count,
diff vs snapshot table, alert on transitions. Known API limits: no skill-identity endpoint
(GET /:id/skills → 404), so count-diffing misses a one-for-one skill swap and in-place recipe
hardening is invisible. Mitigation: P1 re-runs weekly as the deep scan.

## P4 — Finish the in-flight repair (~0.5 pts)

Re-point get_fix_proposals (83074639) from dead 157379 to recreated 163016, remap field IDs
including the schema rename query_id → snowflake_query_id, verify a clean run.

## Sequence + points

Josh decides first: re-stop Drift Fix Genie now or leave running pending attribution. Then
P1 → P2, P4 anytime, P3 last. Estimate 7-8 points as revised vs the 3.0 on the ticket (delta
flagged to Josh; field left untouched).
