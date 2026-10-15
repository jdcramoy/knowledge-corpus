## 1. TOP IDEAS

**1. Replay Farm — a regression harness built from solved incidents.**
*What:* Every episode ending in a verified fix is frozen as a replay case: failing job payload + pre-state manifest + expected post-state. Nightly, N closed cases replay against the current genie stack (skills, KBs, prompts) in AI Dev; pass-rate delta gates any change to the genie. *Why it compounds:* It converts the red-team's human-gate findings and every solved ticket into permanent tests. Today, changing a prompt or KB doc is a leap of faith; with the Farm it's a CI check. It's also the honest measurement gate for the Cortex Search tier: build retrieval only if it lifts replay pass-rate. *Why cheap:* Manifests, build reports, and the generic executor already exist — replay is the Doer loop run against a fixture.

**2. Verify-before-grade — a deterministic backbone under the Reviewer.**
*What:* Before the reviewer LLM opines, run mechanical checks: replay the fixed recipe against the captured failing payload, schema-lint the manifest, assert the diff touches only manifest-listed assets. The Reviewer's job becomes "argue with the harness," not "imagine correctness." *Why it compounds:* Kills grading theater. An AI grade anchored to a reproducible event is a measurement; an unanchored grade is vibes — and vibes can't be calibrated later. *Why cheap:* update-and-verify + the executor + captured payloads.

**3. Earned Autonomy Tiers — the intelligence layer's real product.**
*What:* Structure the human promotion gate as a rubric (correctness, blast radius, idempotency, observability, rollback), log scores, then monthly compute reviewer-vs-human agreement and post-promotion survival per failure class. Classes with clean calibration auto-promote to AI Production; humans see exceptions only. *Why it compounds:* Human review is the throughput ceiling of the entire design. This converts the flywheel into falling human cost per fix — the only route to "go nuts" scale. Autonomy expands on evidence, contracts on incident. *Why cheap:* A Jira form plus rollups you're building anyway.

**4. KB report cards — telemetry on the knowledge estate itself.**
*What:* Log every KB retrieval (doc ID, version, score) beside episode outcome. Per doc: times-retrieved, win-rate-in-context, escalation-rate-when-present. The distillation job consumes this: high-retrieval/low-win docs get rewritten, never-retrieved docs get archived, and new lessons are validated by whether the *next* episode's outcome actually improves. *Why it compounds:* Most KBs rot invisibly; this makes the knowledge estate self-pruning and gives distillation an objective function instead of vibes. *Why cheap:* A join between audit rows and Build Memory docs, both already committed.

**5. Plan-first dry run + plan-adherence scoring.**
*What:* Pass 0 is plan-only: routes to call, assets to touch, expected diff, risk — posted to the ticket. The executor refuses writes outside the approved plan unless the Reviewer co-signs a delta. The judge scores adherence every pass. *Why it compounds:* The cheapest guardrail that exists (a plan is free), and intent-vs-action drift is the single best early predictor of rogue behavior — you catch it before it's expensive. *Why cheap:* An operating-instruction change plus one allow-list check in the existing route guard.

**6. Provenance pins — every manifest carries a knowledge fingerprint.**
*What:* Hash the KB docs and skill/prompt versions used per build; write them into the manifest and report; flag monitoring events on genie-built prod assets with that fingerprint. *Why it compounds:* When a genie-built asset breaks in February, you can diff what the genie *knew* in September — separating knowledge rot from code rot, and making "self-learning" a scientific loop instead of a slogan. *Why cheap:* A hash and a data-table column.

**7. Cost-per-fix ledger with fleet circuit breaker.**
*What:* Tokens + passes + rounds + judge cost per episode, rolled into cost-per-outcome (auto-fixed / escalated / abandoned). Per-ticket spend cap triggers STOP-and-escalate; a fleet-level daily cap handles storms; trivial failure classes route to a cheaper model pair. *Why it compounds:* Without unit economics the sponsor can't defend expansion; with them you can show exactly where genies print money and where humans are cheaper. *Why cheap:* Audit rows plus provider usage logs.

**8. Fire drills — the Monitor monitors itself.**
*What:* Scheduled chaos recipes that fail on purpose across each monitored project type; assert detection → ticket → triage within SLA; measure false-positive rate against Jira outcomes. *Why it compounds:* Everything downstream is capped by detection quality, and monitor recall is currently unmeasured — a silently degrading monitor makes every other metric lie. *Why cheap:* You own the estate; a drill recipe is 20 minutes.

**9. Give the Dreamer a day job: estate-wide automation ranking.**
*What:* Dreamer v1 does one concrete thing — cluster all-time Jira bug history plus Build Memory signatures into failure classes, score by frequency × human-minutes × similarity to solved issues, and output "top 10 automatable failure classes" with evidence links. *Why it compounds:* Replaces "thinks associatively" with a deliverable that directly shapes KB investment and proves value beyond incident response. *Why cheap:* Queries over data tables you've already committed to.

## 2. INTELLIGENCE LAYER DEEP-DIVE

One reframe first: the HR flywheel's "capture is urgent because content purges in 90 days" translates here as **Workato job-history retention is your 90-day clock.** The raw evidence — the failing recipe's job logs and payloads — rots on Workato's side. Capture at event time or lose the training data. And the "no privacy machinery" call is half right: the threat model isn't PII, it's **secrets in payloads** and **poisoned memory**. So the one piece you cannot skip is a sanitizer at ingest.

**CAPTURE** (event-time, into your own data tables):
- Episode envelope: trigger recipe ID, job ID, error text, full job-log snapshot, sanitized source payload, ticket, environment.
- Per doer pass: executor traces (method, path, sanitized body/response, status, latency), approved plan, KB docs retrieved (ID + version + score), model + prompt/skill versions, token counts.
- Review rounds: verdict, findings, delta from previous round, attached harness output.
- Human gate: rubric scores, decision, reviewer, time-to-decision.
- **Outcome loop:** promotion event, then monitoring events on genie-built prod assets for 90 days post-promotion via the provenance pin. This is ground truth most AI systems never wire up — and the Doer writes to a monitored estate, so you *can*.
- Sanitizer at ingest: strip credentials, connection configs, and payload secrets before anything lands in a table that re-feeds prompts.

**JUDGE** — two layers:
- Layer 0, deterministic: harness verdict (replay success, blast-radius assertion, schema lint). Cheap, ungameable.
- Layer 1, LLM: the Reviewer grades the episode on a rubric — outcome correctness, plan adherence, pass efficiency vs. cap, route-guardrail hits, report quality, evidence sufficiency. Grade review quality too: did the review round surface real defects? Run a periodic independent judge on a different model to detect reviewer drift.

**ROLLUP** — five cubes: per-episode (outcome class, passes, rounds, cost, human minutes); per-failure-signature (recurrence, fix rate, time-to-lesson); per-KB-doc (retrieval → win rate); per-route (error-rate drift, gotcha hit rate — this is your route-catalog rot detector); per-genie-version (eval pass rate + grade distribution, so you can tell "the world changed" from "the genie changed").

**MINE** — four miners: Knowledge Gap Miner (STOPs, escalations, and retrieval-misses → ranked KB backlog); Signature Miner (Build Memory clusters → the Dreamer's input); Calibration Miner (AI grade vs. human rubric vs. post-promotion outcome); Cost Archetype Miner (failure classes that are money pits vs. money printers).

**EVAL + DIGEST** — Replay Farm as the regression suite; hard gate: no prompt/skill/KB promotion without replay non-regression. Define the Cortex Search measurement gate now: logged retrieval-miss rate is the demand signal, replay-set lift is the proof. Weekly digest: fixes shipped vs. escalated, survival rate, novelty rate, cost per fix, KB report-card top/bottom, calibration drift. The Analyst Genie gets one read-only query skill over the rollup tables — nothing more.

## 3. GAPS (hurts within 90 days)

1. **No reproduction reality.** The Doer can't verify a fix without the failing job's payload and working test connections in the sandbox. Provisioning sandbox creds for real downstream systems and building a capture-and-replay-payload skill is the long pole — without it the Doer grades on "it compiles," not "it works." Start this first.
2. **No rollback/restore.** A corrupted sandbox contaminates every subsequent episode. Per-episode manifest snapshot + restore skill, non-negotiable.
3. **No storm circuit breaker.** One bad deploy = 50 failing recipes = 150 doer passes and 50 tickets. Root-cause dedup at the trigger layer plus a fleet-level spend cap, or the first real incident bankrupts the token budget.
4. **Concurrency collisions.** Two episodes touching the same project will corrupt manifest-fold. Lock per project or serialize.
5. **Genie version control.** Prompts, operating instructions, and skills need a repo and a release process. Without it, grade shifts are unexplainable and the per-genie-version rollup is fiction.
6. **Ingest sanitizer.** As above — re-ingesting unsanitized build reports into KBs puts credentials in future prompts and hands injectors a persistence mechanism.
7. **Jira bug-history KB.** All-time tickets contain pasted credentials and customer data. Scrub before ingest, same rule as #6.

## 4. RISKS — the two quiet failures

1. **The rubber-stamp loop.** The Reviewer learns what humans wave through; humans learn to wave through what the Reviewer grades highly; no outcome feedback ever arrives. Every dashboard stays green while genie-built fixes quietly fail in prod. The tell is a promotion rate near 100% with unknown post-promotion survival. Countermeasure: survival metric, monthly calibration report, occasional blind human re-review of AI-approved builds.
2. **The echo chamber.** Self-learning with unverified write access to its own memory: confident-but-wrong build reports re-ingest into KBs, coincidental fixes get recorded as lessons, distillation compacts the wrongness into fewer, more authoritative docs, and future episodes retrieve them as gospel. The tell: lesson count grows while novel-failure rate flatlines. Countermeasure: lessons promote only with replay-verified evidence, and KB report cards demote docs with bad win rates.

## 5. METRICS — the five numbers

1. **Human minutes per resolved failure** (vs. pre-genie baseline) — the attention-leverage thesis in one number.
2. **Auto-resolution rate with 30-day survival** — % of failures fully closed by genies that don't re-open. Throughput with the honesty term built in; without survival, it's gameable.
3. **Novel-failure rate** — % of incidents with a never-before-seen signature. Should trend down as Build Memory works; a flatline means self-learning is decoration.
4. **Cost per auto-fixed failure** — tokens + infra + human gate minutes, against the loaded engineer cost of the manual fix.
5. **Reviewer calibration error** — disagreement rate between AI grades and (human rubric + post-promotion outcomes). This is the trust number, and it gates everything: if it doesn't improve, autonomy can't expand and humans must read every report — which kills the value proposition.

All five fall out of the capture layer in section 2. If the team builds nothing else from this review, build capture first — the flywheel can't spin on data you didn't catch before it aged out.