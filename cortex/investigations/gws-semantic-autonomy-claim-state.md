# Investigation: stale gated claim `gws-semantic-autonomy` (BSYS-29569)

Investigated 2026-10-19 ~20:15Z (cortex lookup dispatch 2026-10-19T20:05:30Z). Read-only -
registry.json, events.jsonl, claims-sweep-latest.json, projects/google-semantic-mcp.md, garden
reports, live AIRO recipe/job reads, read-only Jira read of BSYS-29569. Nothing modified except
this file.

**VERDICT: the claim is stale BOOKKEEPING, not unfinished prod state. The build shipped, was
UATd, and is still running green today. A `done` closeout already exists under a twin workstream
name; the in-flight claim row was simply never closed.**


## 1. What the jury build actually delivered (before it went quiet)

BSYS-29569 (judge/dissenter/resolver jury) is BUILT and UATd, per two independent records:

- **Jira comment 1136332** on BSYS-29569 (Joshua Cramoy, 2026-10-13T00:12Z, "BUILT AND UATd
  (dev)"): promoter promote_google_workspace_learning_aid 82792961 at v22, steps 20-38 carry
  the full jury - docket builder (error hints review_pending + parked phrase_seed backlog +
  parked coverage_gap proposals), pre-jury lint, cost guard 25 rounds/run hints-first, three
  AI roles (JUDGE gpt-4o-mini / DISSENTER gpt-4.1-mini on the OpenAI connector - documented
  substitution because AI Gateway Anthropic connection 19937586 is Genie-only, zero in-recipe
  actions / RESOLVER gpt-4o-mini), verdicts PROMOTE/RETIRE/PARK_FOR_EVIDENCE recorded per row
  (reviewer=jury-v1, full audit in review_notes), fail-closed (juror error -> PARK, never
  promote; rows stay re-judgeable). Strict traffic-earned mechanical gate byte-identical v21
  and deliberately NOT juried.
- **Live recipe description on 82792961 today** (AIRO read, 2026-10-19) carries the identical
  BSYS-29569 jury-lane spec - the code on the platform matches the comment.

UAT evidence in the comment: real 3-role verdicts with both arguments (3 RETIRE examples),
fail-closed proof (judge model swapped to nonexistent -> 2 force-runs GREEN, all 25 docket rows
parked with reason=juror_error_monitor_caught, zero promotions, then model reverted and the same
rows got real verdicts), backlog drain: jury-backlog-ingest.mjs inserted all 497 parked clusters
idempotently, 100 phrase_seed clusters RETIRED + 10/10 error hints adjudicated after 4 green
jury runs, ~4h projected to full drain, ~1,113 tokens/round.

## 2. Are the artifacts live? YES - verified 2026-10-19 via AIRO (dev)

- **82792961 promote_google_workspace_learning_aid**: Running=True AND fresh green jobs TODAY -
  j-Ac3mffWL-WdWeBQ-CD started 2026-10-19T12:52:52-07:00, succeeded in 1.7s; 15-min cadence
  confirmed (12:22 / 12:37 / 12:52 PT same day). 1,624 lifetime jobs, 1,620 succeeded / 4
  failed. (Per the 2026-10-18 serving-truth-audit lesson, job recency - not the running flag -
  is the liveness proof; both checked.)
- **82993457 gw_semantic_promoted_phrase_health** (BSYS-29570 sibling build, same claim body):
  Running=True, hourly green jobs today (j-Ac3mEa6s-gfdkgB-CD, 12:22 PT), 183/183 succeeded.
  Its dissenting-juror step is live; the BSYS-29569 full jury replacing it is a documented
  ENHANCEMENT, not delivered scope.
- Sister artifacts from the same claim: strikes table 159653, mode row promoted_phrase_health_mode
  in 156399, metric row in 157186, jury backlog ingest script scripts/jury-backlog-ingest.mjs.

## 3. Alive, abandoned, or waiting on a Josh verdict?

**ALIVE and running autonomously - not abandoned, and NOT waiting on any Josh verdict.**

- The work went quiet because it FINISHED: a closeout row with state=done exists at
  events.jsonl:153 (2026-10-13T00:13:02Z) - but under workstream name **gws-semantic-mcp**,
  while the claim at events.jsonl:141 was filed 41 minutes earlier under **gws-semantic-autonomy**.
  Two workstream names, one body of work. The closeout closed the twin row; the
  gws-semantic-autonomy claim was never matched/closed and has aged 164h as a ghost.
- Nothing gated is pending. The ticket itself (BSYS-29569, status Backlog, unassigned, High,
  labels autonomy/flywheel/gws-semantic-mcp) was never transitioned after the build comment -
  the ONLY residual Josh-side item on it is a status flip, not a verdict on the build.
- Both remaining follow-ups in the record are explicitly non-blocking design notes (hint SERVE
  path attachment; 3 throwaway jurytest-* fixture rows in 155485 "harmless, delete at leisure").

## 4. Single most useful next step + owner

**Step: close the ghost claim row.** File a closeout for workstream `gws-semantic-autonomy`
(BSYS-29569) citing this investigation + the existing done-closeout at events.jsonl:153 - the
work shipped, artifacts verified live 2026-10-19, no POSSIBLE UNFINISHED PROD STATE. That
clears the last prod-adjacent stale claim on the ledger and empties the claims-sweep flag.

**Owner: the next mission-control session (any harness session running mission-control.py) -
mechanical registry closeout, no Josh gate needed.**

Secondary (Josh-only, whenever convenient): flip BSYS-29569 out of Backlog to Done/Delivered -
it is 7 days stale in status only. This investigation touched nothing on the ticket (no Jira
writes). Optional cleanup, not urgent: 3 jurytest-* fixture rows in 155485.

## Evidence index

- mission-control/events.jsonl:141 (claim, 2026-10-12T23:31:56Z, in-flight) and :153 (closeout
  done, 2026-10-13T00:13:02Z, workstream gws-semantic-mcp)
- reports/claims-sweep-latest.json (2026-10-19T19:30:44Z): the one gated stale claim, 164h,
  recipe_ids empty, flag_prod_state false
- Jira BSYS-29569 comment 1136332 (build+UAT record, 2026-10-13T00:12Z) - read-only
- AIRO live reads 2026-10-19: recipe 82792961 (Running=True, description = BSYS-29569 jury
  spec) + job_list (green jobs 12:52 PT today); recipe 82993457 (Running=True, hourly green)
- projects/google-semantic-mcp.md lines ~3135-3145 (BSYS-29570 SHIPPED section; residual
  noting the full-jury upgrade path)
- garden-reports/garden-2026-10-16.md (already classified BSYS-29569 as "Josh-gated state",
  no prod-state flag)
