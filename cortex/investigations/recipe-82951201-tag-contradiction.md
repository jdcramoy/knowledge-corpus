# Investigation — recipe 82951201 ticket-tag contradiction

Investigated 2026-10-09T23:1xZ (cortex-dispatched headless read-only probe; dispatch record:
build-ledger.jsonl line 5056). READ-ONLY throughout: wt API reads, file reads, local Jira reads.
Answers both cortex questions from questions.jsonl:53 (18:58:43Z).

## Verdict

1. **The recipe belongs to BSYS-29478.** BSYS-29438's appearance in the ledger is an
   attribution artifact of the guardrails hook's ticket-tagging heuristic, not evidence of
   29438 ownership.
2. **The build was authorized. Josh personally approved it** — a structured
   "Build now (Recommended)" answer at 18:34:54Z, ten minutes before recipe_builder_init
   ran at 18:45:01Z. The build was NOT unauthorized.

## Evidence — ownership: BSYS-29478

- Recipe read (`wt api GET /api/recipes/82951201`): name `gw_fleet_liveness_sentinel`,
  description opens "Fleet schedule-liveness sentinel for the Google Workspace Semantic MCP
  fleet (BSYS-29478)", folder 35404884, created 2026-10-09T11:45:00-07:00 (=18:45Z),
  updated 18:57:34Z, running=True.
- build-ledger.jsonl:4988 — the builder's own substantive entry (appended per its dispatch
  instructions): action "BUILD+VERIFY dev recipe gw_fleet_liveness_sentinel per BSYS-29478
  plan (comment 1134467)", ticket "BSYS-29478", recipe 82951201, 5 job-trace IDs, env
  "dev workspace 3535597 only; NOT promoted".
- Jira BSYS-29478 (workato site, issue 437232): assignee Joshua Cramoy, status UAT; plan
  comment 1134467 (17:48:42Z) describes exactly this build; evidence comment 1134564
  (19:01:55Z) documents recipe 82951201 built, 5 verification jobs, moved to UAT.
- Jira BSYS-29438 (issue 436922): assignee **null**, status **Backlog**, comments are plan
  text only (1134466/1134469/1134482) — no build was ever done or claimed under it. The
  Freshdesk/AE build it describes (SFDC owner-change → Freshdesk ticket) shares no
  functionality with a schedule-liveness sentinel.
- Triage queue.jsonl:42 (`bsys-29478-sentinel-plan-ready`) status "built", decided 19:02:53Z,
  note names recipe 82951201. queue.jsonl:43 (`bsys-29438-ae-freshdesk-plan-ready`) status
  "rejected" at 18:38:42Z — "NOT ASSIGNED TO JOSH".

## Evidence — authorization: Josh's explicit GO

- 17:59Z sweep (jira-triage/runs.jsonl:14) correctly listed "BSYS-29478 sentinel build
  GO/NO-GO (5pts, rec: GO)" in needs_josh; dev was gated.
- Josh opened the interactive /triage pass at 18:16:37Z (workbench transcript
  `~/.claude/projects/-Users-<user>-Documents-workbench/c3a68cb1-f294-492b-97b6-cd7d640336e9.jsonl`).
- 18:17:16Z the session rendered 10 decision cards; card 4 =
  `bsys-29478-sentinel-plan-ready`, rec "Build now".
- **18:34:54Z structured-answer tool result (same transcript): "BSYS-29478 (low):
  schedule-liveness sentinel plan is finished and build-ready (5pts) — authorize the dev
  build now?" = "Build now (Recommended)"** — Josh's explicit authorization. Same batch:
  wt-fix and kb-sync "Build now"; the 18:38:17Z answer carries his BSYS-29438 ruling
  ("This ticket isn't assigned to me… Fix this.").
- 18:39:20Z the triage session dispatched 5 async build agents; the sentinel builder's
  dispatch prompt (subagent transcript
  `c3a68cb1-…/subagents/agent-a4d488db52753d0e2.jsonl`, 18:39:20.785Z) opens "Execute a
  triage-approved 5pt dev build… Josh authorized the build kickoff" and names BSYS-29478 /
  comment 1134467 as the authoritative plan.
- 18:45:01Z recipe_builder_init (build-ledger.jsonl:4878, session gw-sentinel-build-1);
  push 18:57:34Z (:4957); evidence comment 1134564 19:01:55Z; verdict recorded "built"
  19:02:52Z (transcript) / outcomes line garden-reports/triage-outcomes.jsonl:68.

Caveat on attribution tooling: triage-outcomes.jsonl:68 says `"by": "josh (triage-decide)"`,
but triage-decide.py:105 hardcodes that string for every caller, so the outcomes log alone
proves nothing. Here it doesn't matter — Josh's GO is independently proven by the
18:34:54Z transcript. (Flaw worth fixing; see recommendations.)

## Why the ledger says BSYS-29438 (root cause of the contradiction)

The guardrails hook stamps every build-ledger line with the session's `currentTicket`,
defined at plugins/cache/josh-mods/workato-guardrails/1.0.0/hooks/register.js:594-600:
"The last ticket key mentioned in a prompt becomes the session's current ticket;
build-ledger entries carry it for traceability" (first ticket-key match per prompt,
last prompt wins).

The sentinel build ran inside the /triage orchestrator session's process (builder was its
subagent), so its AIRO-mutation and wt-command ledger lines carry the orchestrator's
currentTicket. Josh's last ticket-bearing prompt in that session before the builds was the
18:38:17Z rejection answer, whose question text leads with "BSYS-29438 (low): AE-change to
Freshdesk…" — pinning currentTicket to the REJECTED ticket. Every hook-logged line from
18:43:59Z through 19:02:08Z (build-ledger.jsonl:4874–4991: triage-decide run, wt
start/stop/force-run of 82951201, all recipe_builder_* mutations) therefore carries
ticket "BSYS-29438" even though the work is BSYS-29478's. The tag flip pattern across the
day (29478 → 29477 at :4848 → None 18:39–18:43 → 29438 from 18:43:59) confirms it tracks
prompt-mention, never the work's actual ticket.

The one line the builder agent itself appended per dispatch instructions (:4988) carries
the correct ticket, BSYS-29478.

## Disposition

- No remediation needed on the recipe: correct ticket, authorized, dev-only (workspace
  3535597, not promoted), evidence comment 1134564 posted, 24h UAT soak pending.
- The wrong ticket tags in build-ledger.jsonl:4874–4991 are historical noise; do NOT edit
  the ledger in place (append-only audit trail). The correct ownership is recorded here and
  in the builder's own entry (:4988).

## Recommendations for Josh (not applied — read-only probe)

1. Hook fix: `currentTicket` should be inherited from the dispatch context (the Agent-tool
   prompt / subagent's own prompt) rather than "last ticket key mentioned in any prompt of
   the orchestrator session"; ideally the dispatcher pins the ticket explicitly per
   dispatched build.
2. triage-decide.py: derive `by` from the actual caller (env/`--by` flag) instead of
   hardcoding "josh (triage-decide)" (scripts/triage-decide.py:105), or the outcomes
   audit trail over-credits Josh for agent-recorded decisions.
3. Optional: a one-line cortex note linking this file so future audits of ledger lines
   4874–4991 don't re-derive the mechanism.
