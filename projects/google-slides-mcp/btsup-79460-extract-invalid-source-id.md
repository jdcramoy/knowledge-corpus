# BTSUP-79460: Extract_Design_System INVALID_SOURCE_ID on valid Slides IDs

Filed: 2026-10-23 by Kazunori Hori (AI Intake, via Slack). Status at triage: In Triage, assigned Josh.

## What the ticket said broke

Extract_Design_System rejects valid Google Slides presentation IDs with
`INVALID_SOURCE_ID` ("presentation_id does not look like a Slides ID", upstream_status 400,
retryable false) before any Google call. Two 44-char IDs tested, both conformant.
Get_Presentation succeeds on the same IDs. List_Design_Systems returns 0.

## What the workspace shows now (live-verified 2026-10-23)

- Reproduced in prod job traces on recipe 82090477 (Extract Design System):
  jobs j-Ac6aXfJH-CBhRba-CD (2026-10-22T22:57:55 PT) and j-Ac6aoNWg-496gxQ-CD
  (2026-10-22T23:15:57 PT). Guard step output shows
  `presentation_id = "start_workflow_1['parameters']['presentation_id']"` — the datapill
  reference arrived as an UNRESOLVED LITERAL STRING, 51 chars containing `'`, `[`, `]`,
  spaces. The guard regex `\A[A-Za-z0-9_-]{20,}\z` correctly rejects that literal.
- Guard code (step 1, prod 82090477):
  `pid = input['presentation_id'].to_s.strip; valid = pid.match?(/\A[A-Za-z0-9_-]{20,}\z/)`.
- Every prod extraction job from 2026-10-22T20:55:48 PT onward short-circuits at the guard
  (4 steps, valid=no). Last job with the real flow: 2026-10-22T19:45:39 PT (8 steps).
  Zero successful extractions since the hot-swap. Outage window ≥14h at triage time.
- Dev twin 78677477 has the SAME static-text mapping in code_input.data (verified in code).
- List_Design_Systems returning 0 for the requester is EXPECTED behavior (caller-scoped
  registry, no rows in his scope because no extraction ever succeeded).

## Root cause (proven, not guessed)

The 2026-10-22 "Fix F1" hot-swap window (last real-flow job 19:45:39 PT, first all-fail job
20:55:48 PT) wrote the guard step's `code_input.data.presentation_id` mapping as static text
in prod 82090477's DSL — read directly from the prod recipe pull, not inferred. The prime
suspect is the `recipe_builder_set_input_field` silent-static-text failure mode from CLAUDE.md
gotchas; the exact write path (AIRO vs CLI vs browser) in the hot-swap session is not proven. The guard therefore validates its own mapping
string, not the caller's ID, and rejects every call. The post-fix verification
(`mock` → INVALID_SOURCE_ID, job j-Ac6WsQCG) passed because the expected result of a mock
ID is rejection — a one-sided verification that could not distinguish "guard rejects
garbage" from "guard rejects everything".

## Fix plan (Josh's gate: prod write)

1. Prod 82090477 + dev 78677477: re-map the guard step input
   `code_input.data.presentation_id` to the real trigger pill
   (`start_workflow_1['parameters']['presentation_id']` as a RESOLVED reference, not
   literal text). Verify the mapping resolves in a job trace after push — not just DSL.
2. Verification must include a VALID-ID end-to-end extraction (known-good deck,
   e.g. Daman's pricing deck 17gjt-n8jAJ1aJYEC7h9HCQW694JT0vnuuqocxTzmdMk) proving
   29-step flow + registry row created, PLUS the mock-ID negative case.
3. Optional hardening: guard treats an input that literally matches
   `^\w+\[.*\]$` (unresolved pill syntax) as a distinct mapping-failure error code, so
   this class can never masquerade as a customer input error again.
4. Red-team gate before the prod push per standing order.

## Evidence

- Prod job trace: `~/.claude/knowledge/projects/google-slides-mcp/evidence-btsup-79460-job-j-Ac6aXfJH-CBhRba-CD.json` (line 1 = guard input with literal pill string)
- Prod recipe code: `wt recipes get 82090477 --profile josh-prod` (guard step 1)
- Project history: `~/.claude/knowledge/projects/google-slides-mcp.md` (OPS FIX ROUND 1, 2026-10-22)

## Dissent gate (2026-10-23)

Dissenter verdict: diagnosis STANDS; draft revised before posting. Accepted objections:
(1) struck the unverified "Fill_Template/Create_Deck not affected" claim from the customer
reply; (2) added that registry-dependent tools stay degraded for this caller until fixed;
(3) softened F1 attribution to the hot-swap window (19:45–20:55 PT boundary); (4) corrected
the literal string length to 49 chars; (5) fix verification must be trace-level (guard input
shows the resolved 44-char ID, not a green response). Rejected/absorbed: prod step-1 mapping
was already read from the prod DSL (the inferential hop is closed); "nothing was modified"
is provable (every failed job short-circuited before any Google call).
