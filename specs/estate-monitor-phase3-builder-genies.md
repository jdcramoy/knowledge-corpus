# Phase 3 — Builder/Remediator Genies (the Doers) — design + phasing

Status: DESIGNED 2026-10-14 (rev 2 — Josh corrections applied same day).
Build kickoff pending Josh's go. Zero live assets exist for phase 3 yet.
Parent platform: Estate Monitor (BSYS-29554). Epic: BSYS-29666.

## Mission

Close the loop end to end:

> Incident → Reaction → Jira ticket → Genie triage (SHIPPED) → **Human
> review** → build label → **Doer genie executes** → **Reviewer genie
> checks + grades** → manifest on the Jira ticket → build report on the
> ticket → report ingested back into the KB → human sees everything.

Two genies, doer/dissenter style (the house pattern): one FIXES/BUILDS, the
other REVIEWS, GRADES, and picks up slack. Different models, same KBs, same
skills, different operating instructions.

## Architecture principles

1. **Native Workato.** Genies live in Agent Studio. Their hands =
   recipe-backed skills (the proven phase-2 pattern).
2. **One generic executor + a compiled route catalog (the GWS answer).**
   We will NOT spec every Dev API endpoint as a skill. The core hand = ONE
   generic Workato Dev API executor skill: {method, path, body} in →
   response out, with guardrails (allowed-route patterns, deny-list, rate
   caps, mandatory audit). Route MECHANICS are deterministic: a **route
   catalog** — per-route docs (path, method, params, payload schema,
   gotchas, pinned lessons) COMPILED at build/KB-Sync time from the Dev API
   reference + wt-route + the trap ledger. No live-discovery pipeline to
   maintain: the Workato API is finite and we already own the corpus; the
   catalog regenerates with the distillation job. The genie consults the
   catalog BEFORE calling (route existence, param names, known traps), the
   executor validates against it, and the KB prose supplies semantics.
   **Self-improving:** every failed call writes a memory; 3-strike lessons
   get PINNED to their route's catalog entry — the catalog improves weekly,
   exactly like wt/AIRO gotcha catalogs do locally. In phase 3.4 the
   catalog also goes semantic (Cortex): "update a recipe's code" → finds
   PUT /api/recipes/:id.
3. **Auth = a secret + the Dev API.** The executor skill's token is stored
   as a SECRET (not a project property) and talks to the Workato DEV API.
4. **Containment.** The genies work in the **AHQ | AI Development**
   environment (**AHQ | AI Production** as their named output environment).
   No staging-to-prod process exists and none will be built — the manifest
   + Jira ticket IS the deliverable record. If a human later wants a real
   promotion, the standing DR/red-team/Josh process applies unchanged.
5. **Bounded autonomy.** Max 3 doer passes, 2 review rounds; every action
   claim-first audited; STOP-and-escalate always available; the genie can
   never widen its scope.
6. **KB: many KBs, domain-partitioned — feed it everything.** Not one huge
   KB: knowledge spread across MULTIPLE Enterprise Context KBs by domain/
   functional area (mirroring the knowledge-tree INDEX.md structure:
   domains, projects, specs, gotchas, decisions, triage memory, build
   memory, Jira bugs...). The corpus we already have — integration, AI,
   engineering best practices, lessons, efficiency playbooks — all of it
   goes in. The genie skills declare which KBs they need; retrieval stays
   sharp because each KB is small and focused.
7. **Self-learning with an immune system.** Every error = a Build Memory doc
   (error signature + context + attempt + outcome). Same signature 3x = a
   lesson draft — promoted into the distilled corpus ONLY after Dissenter
   review (no self-poisoning). Completed build reports ON THE JIRA TICKET
   are ingested back into the KBs and strengthen the genies. Solved fixes
   are logged as Solved-Issue docs; the doer pre-queries them at build
   start ("have we seen this before?").
8. **Total audit + grading.** Every genie action inside Workato logs to the
   **EM | AI Action Log** data table: what, WHY (the reason), a confidence
   score, the actor genie, the ticket, and evidence links. On completion
   the solution is GRADED against the best-practices corpus + documentation
   (rubric-scored; the grade feeds the Dreamer).

## The Dreamer genie

A third genie with a full-time job (the harness dreamer, ported):
- **Primary:** wakes periodically and thinks associatively ACROSS
  everything — Jira tickets, knowledge docs, internal + external best
  practices, the AI Action Log, grades, triage/build comments, the recipes
  themselves — and makes suggestions for improving the system overall.
- **Secondary:** per-recipe review — for every recipe in Estate Monitor
  scope: logs, job histories, shape/architecture — how could it be better?
- **Output discipline:** ideas are CLUSTERED and SCORED (a scoring math
  with a threshold: SUGGEST above it, DEFER/DEMOTE below). Suggestions
  queue in a proposals DATA TABLE and a daily digest posts to a Slack
  channel. The Dreamer proposes; it never applies.

## The loop (end to end)

1. **Trigger.** Handler gains a `send-to-build` branch: gate = the ticket
   has a triage verdict (the human reviewed it) + claim-first audit row
   `build-requested|<ticket>` → invoke the Doer with ticket + plan +
   metadata (ticket key, incident key, build scope).
2. **Doer pass.** Pattern pre-query (solved issues + bug corpus) →
   plan-step selection → execute via the generic executor + composite
   skills → verify (real job traces, never green-job status) → ACTION LOG
   row (action, reason, confidence) + memory write-back → structured
   result (status, changes, evidence, manifest rows).
3. **Review.** Reviewer genie re-verifies with read-only skills + diff
   reading + blast-radius check → verdict APPROVE / FIX-REQUIRED (with
   defects) → FIX-REQUIRED loops the doer (max 2 rounds). At APPROVE the
   Reviewer GRADES the solution against the best-practices corpus (rubric
   score, stored).
4. **Wrap-up.** Manifest assembled from touched assets as they go (real UI
   names) → manifest + a complete build REPORT written to the Jira ticket
   (Manifest Link field + report comment) → labels/status updated.
5. **Ingestion.** The build report + graded outcome are ingested into the
   KBs (Build Memory / Solved-Issues) — the loop strengthens itself.
6. **Dreamer.** Periodically thinks across all of it; proposals queue →
   daily Slack digest; humans pick.

## Component inventory

- **Doer genie** "EM | Builder" — generic Dev API executor skill + composite
  skills + KBs + structured output contract (anthropic).
- **Reviewer genie** "EM | Build Reviewer" — read skills + diff/verify
  methodology + grading rubric + same executor (openai).
- **Dreamer genie** "EM | Dreamer" — creative association across all
  surfaces + recipe architecture review + clustering/scoring + proposal
  queue + daily digest.
- **EM | AI Action Log** data table — action, reason, confidence, actor,
  ticket, evidence. Total audit for every genie action.
- **Write surface:** generic Dev API executor skill (secret-token auth,
  route guardrails) + composite skills (update-and-verify, manifest-fold).
- **KB estate:** domain-partitioned Enterprise Context KBs (full corpus) +
  Build Memory + Solved-Issues + BSYS all-time bug corpus + distillation
  job feeding KB Sync.
- **Proposal queue** data table + daily Slack digest (Dreamer output).

## Phasing (each phase = shippable)

| Phase | Scope | Pts |
| --- | --- | --- |
| 3.0 Foundation | AHQ AI environments; generic Dev API executor skill (secret auth + route guardrails) + composite skills; EM | AI Action Log table; Build Memory KB + signature convention; manifest-field wiring; Enterprise Context cap measurement | 5 |
| 3.1 Doer v1 | Fixer genie + handler `send-to-build` branch + bounded passes; v1 scope = single-recipe fixes with approved plans (canonized bug classes first) | 5 |
| 3.2 Reviewer + grading | Reviewer genie + doer/reviewer loop + pickup-slack + best-practices grading | 3 |
| 3.3 Self-learning | Build Memory write-back, 3-strike lesson promotion (dissenter-reviewed), Solved-Issues pre-query, distillation job, BSYS bug corpus ingest, Jira-report ingestion | 3 |
| 3.4 Semantic scale-out | Multi-KB domain partitioning of the FULL corpus (integration/AI/engineering docs); measurement gate; Snowflake Cortex Search tier + hybrid retrieval; pattern pre-query upgrade | 5 |
| 3.5 Builder mode | Net-new builds from distilled specs (squad-build decomposition); same bounded+review loop | 5 |
| 3.6 Dreamer | Dreamer genie: cross-surface association, per-recipe architecture review, clustering/scoring math, proposal queue + daily Slack digest | 8 |

## Fusion-adopted ideas (3-model brainstorm 2026-10-14: kimi-k3 + deepseek-v4-pro + glm-5.3-flash)

Strong independent convergence (all three models landed these separately):

1. **Verify-before-grade** — a deterministic backbone under the Reviewer:
   replay the fix against the captured failing payload, schema-lint the
   manifest, assert the diff touches only manifest-listed assets, every
   claim cites an evidence id. The LLM reviewer ARGUES WITH THE HARNESS
   instead of imagining correctness. Kills grading theater; makes every
   downstream number real. (kimi #1, glm #2)
2. **Replay Gym / Farm** — every solved incident frozen as a replay case
   (failing payload + pre-state manifest + acceptance job). ALL changes to
   the genie stack (lessons, KB releases, prompt/skill edits, model swaps)
   gate on replaying the farm. Self-learning becomes CI, not faith. Also
   the honest measurement gate for the Cortex tier. (kimi #2, glm #1)
3. **Shadow-Doer on-ramp** — before writes: 2-4 weeks of dry-run mode on
   real tickets (full plan + diff, no mutation), Reviewer grades, humans
   score. Yields per-route/per-class would-be success rates = the
   calibration baseline for the autonomy ladder. (kimi #3, deepseek #3)
   **DROPPED by Josh 2026-10-14:** it's dev — changes are rollback-able;
   success scores come live during ramp-up. No propose-only period.
4. **Earned-autonomy ladder** — autonomy as a market, not a cap: per
   (route × failure class), L0 propose-only → L1 auto-apply in AI Dev →
   L2 auto + notify → L3 package promotion candidate; any failed verify or
   rejected promotion demotes one level. The pass cap stays as the fuse.
   THE intelligence layer's real product: falling human cost per fix.
   (kimi #4, deepseek #2, glm #3)
5. **Silent-failure tripwires / Estate Watchtower** — trigger surface past
   hard crashes: zero-row runs on high-volume recipes, duration creep >2σ,
   schedule gaps, output schema drift, connector deprecations → pre-failure
   tickets. (kimi #5, deepseek #6)
6. **KB report cards / Knowledge Debt Ledger** — log every KB retrieval
   (doc, version, score) beside episode outcome; per-doc win-rate; the
   distillation job gets an objective function (rewrite high-read/low-win
   docs, archive never-read) — the knowledge estate self-prunes. Also:
   provenance pins — hash the KB/skill/prompt versions into each manifest
   so a February failure can be diffed against what the genie KNEW in
   September (knowledge rot vs code rot). (deepseek #7, glm #4 + #6)
7. **Coroner + blast-radius graph + circuit breaker** — cluster failure
   signatures across projects in time windows (12 tickets/hour with one
   signature = ONE incident, doers parked); the estate dependency graph
   from the Dev API so every pass/grade carries a blast-radius score;
   shared-asset writes need elevated review. (kimi #6)
8. **Value Receipts** — machine-readable receipt per fix: failure
   signature, recurrence frequency, business impact, diff hash, risk,
   token cost → "AI avoided $X/month in repeat failures" becomes a query.
   (deepseek #1)
9. **Plan-first pass 0** — plan-only pass posted to the ticket; the
   executor refuses writes outside the approved plan unless the Reviewer
   co-signs a delta; plan-adherence scored every pass — the cheapest
   rogue-behavior predictor there is. (glm #5)
10. **Live approval cards + revert memory** — one-glance Slack/Jira card
    (diff, confidence trajectory, dissenter's strongest objection, rollback
    plan, blast radius) with Approve/Request-Changes buttons; every human
    revert/edit of an AI change captured as high-priority memory that can
    force propose-only mode. (deepseek #5 + #8)

Landing map: 3.0 += plan-first pass 0, provenance pins; 3.1 += shadow-mode
on-ramp; 3.2 += verify-before-grade + approval cards; 3.3 += Replay Gym +
KB report cards + revert memory + value receipts; NEW 3.7 = tripwires +
coroner + blast-radius graph.

## Open items (decided-by-default, Josh can override)

- Trigger = label `send-to-build` (consistent with `send-to-triage`,
  re-triggerable, no workflow change). A status can wrap it later.
- v1 fix scope = canonized bug classes on single recipes; general fixes
  unlock after the reviewer loop proves out.
- Doer model: anthropic; Reviewer: openai (house pattern). Dreamer: TBD at
  build (creative association may favor a different model again).
- Executor route guardrails v1: deny-list destructive/non-dev routes + the
  AHQ AI environment containment; the deny-list grows from the audit log.
