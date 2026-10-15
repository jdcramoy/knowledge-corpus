## 1. TOP IDEAS

**1. Grade the terminal state, not the story.** The reviewer/judge must verify, not read: manifest diff == claimed changes, a test job runs green in AI Production, every claim in the build report cites an evidence ID (API response, job log). No evidence → claim void → grade fails. *Compounds:* kills reward hacking at the root, which makes every downstream number — success rates, lesson ROI, autonomy decisions — real. *Cheap:* executor and job history already return everything; it's a verification pass, not new infra. Add seeded-fault canaries: inject a known bug into 1-in-20 manifests; a reviewer that misses it gets flagged itself.

**2. The Replay Gym — every fix becomes a permanent regression test.** Snapshot each failure (broken manifest + minimized repro + acceptance test job) into a library. Gate every change — lesson promotion, KB release, skill edit, model swap — on replaying it in AI Dev. New model drops Friday, green/red answer by Monday. *Compounds:* the library grows with every ticket, so the platform gets harder to break as it ages; converts "self-learning" from faith into CI. This is the HR flywheel's eval harness but with executable ground truth — strictly better. *Cheap:* environments are disposable, manifests are text, acceptance = run job, compare outputs.

**3. Shadow-Doer scoreboard before write access.** Run 2–4 weeks of dry-run on live tickets: full plan + manifest + diff, no writes, Reviewer grades, humans score against what actually fixed it. *Compounds:* yields per-route, per-failure-class would-be success rates — the calibration baseline that makes idea #4 evidence-based instead of vibes; produces the first Gym cases; safest possible org on-ramp. *Cheap:* the shipped pipeline minus one executor call.

**4. Autonomy ladder — bounded autonomy as a market, not a cap.** Per (route × failure-class), earn autonomy levels by rolling measured success: L0 propose-only → L1 auto-apply in AI Dev → L2 auto-apply + notify → L3 auto-package promotion candidate. Any failed verify or rejected promotion = automatic demotion one level. Keep "max 3 passes" as the fuse, but the ladder decides who spends them. *Compounds:* autonomy concentrates exactly where the genie proves itself, and produces the audit trail sponsors love: "we only expanded autonomy where measured." *Cheap:* a lookup table keyed on route+signature reading rollups you already plan to log.

**5. Silent-failure tripwires — expand the trigger surface past hard crashes.** Anomaly detection on job history: zero-row runs on recipes that usually move volume, duration creep >2σ, schedule gaps, output schema drift, connector deprecation notices. These file tickets typed "suspected silent failure." *Compounds:* the most expensive integration failures are green-and-wrong; catching them is where a monitor becomes indispensable, and it feeds Dreamer far better material than stack traces. *Cheap:* job history API + rolling stats; start with three threshold rules per recipe.

**6. Coroner + blast-radius graph.** (a) Cluster failure signatures across projects in time windows — 12 tickets in an hour with one signature = ONE incident ticket, doers parked, circuit breaker. (b) Build the estate dependency graph (callable recipes, shared connections, lookup tables) from the Dev API so every doer pass and reviewer grade carries a blast-radius score; shared-asset writes require elevated review. *Compounds:* prevents the ticket-storm doom loop — N doers hammering one dead endpoint — which is your most likely bad day in the first quarter; makes review proportionate to risk. *Cheap:* signatures already exist for Build Memory; the Dev API enumerates assets; both are batch jobs.

**7. One-glance approval card + human decision capture.** The human gate gets a single card on the ticket: manifest diff, claims with evidence links, the Dissenter's strongest objection and its resolution, confidence trajectory across passes, rollback plan, blast radius. Approve / approve-with-edits / reject. Log every decision — especially the edit diff — as labeled data. *Compounds:* approval latency is your throughput bottleneck from day one; and human edits become the highest-signal supervision corpus in the company — your real standards, mined from behavior, feeding reviewer rubric updates. *Cheap:* Jira API + existing manifests; the dataset is a webhook on status change.

**8. Rollback-by-construction.** The executor wrapper enforces snapshot-before-mutate (GET stored with the claim before every PATCH/PUT/DELETE); every manifest ships with inverse operations; post-promotion, a 14-day soak watch auto-files a revert candidate — inverse already attached — on recurrence. *Compounds:* review gets easier because reversible means lower stakes; red-team becomes a checklist; promotion fear — the real adoption killer — drops. *Cheap:* ~30 lines in the single chokepoint all writes funnel through. The generic executor is your best design decision; exploit it.

**9. KB/skill release discipline + decay.** Skills, KBs, and lessons are versioned artifacts; lesson promotion = a release gated on Gym replay; per-route success heat map flags stale route-catalog specs (API drift); lessons decay — if one hasn't fired or hasn't improved its target signature's success rate in 60 days, auto-deprecate. Publish the Solved-Issue corpus as a human-facing fix encyclopedia — the byproduct the team will actually love you for. *Compounds:* prevents KB calcification (see Risks); makes "many small KBs" governable; buys internal political capital. *Cheap:* versions are metadata on docs you already write; the heat map is an audit-table rollup.

**10. Telemetry-fed Dreamer + tournament mode.** (a) Feed Dreamer grades, costs, and gap-miner output so proposals arrive with expected value and evidence: "route X fails 31% first-pass; KB patch draft + 3 new Gym cases attached." (b) On tickets that burn two doer passes, swap roles — OpenAI builds, Anthropic reviews — and diff the approaches; reviewer merges or picks; log which model wins by failure class and route accordingly. *Compounds:* closes the meta-loop — the platform starts improving its own improvement process; model choice becomes routing policy instead of ideology. *Cheap:* both model integrations already exist; Dreamer is already scoped read+propose.

---

## 2. INTELLIGENCE LAYER DEEP-DIVE

Don't copy the HR flywheel — upgrade it. HR chat had no ground truth, so it needed heavy LLM judging. You have executable ground truth: recipes run or they don't, diffs match or they don't. **Judge less, verify more.**

**Capture — one event stream, four sources:**
- *Genie actions* (your schema exists): add skill/KB/model/prompt **versions**, token + cost per call, pass/round index, claim IDs.
- *Executor events*: route, method, latency, status, retries, and **denial events** — guardrail near-misses are gold.
- *Ticket lifecycle*: triage verdict + predicted effort, each doer pass, reviewer grade + objections, escalation reason, human decision + edit diff + time-in-review, promotion result.
- *Outcomes*: verify-job results, 14-day soak result, recurrence events.

Scrub secrets/PII at capture (see Gaps — you need this more than you think). Volume is low thousands of events/day: one Snowflake table, or even Workato data tables, is plenty. **Do not build the Cortex semantic tier yet** — and set the gate now so it's reachable: retrieval-miss rate >15% of escalations citing missing knowledge, two consecutive weeks, measured from day one.

**Grade — three graders, ordered by trust:**
1. **Deterministic verifier (no LLM):** test job green? diff == claims? all claims evidence-backed? This is 80% of the grade.
2. **LLM judge:** process quality only — route selection, thrash, plan-vs-execution divergence, root-cause vs symptom. Never the same model family as the doer.
3. **Human audit sample:** 5% of tickets weekly, frozen. Re-grade the frozen sample monthly; >5pt judge divergence = judge recalibration. This is your drift tripwire.

**Roll up:** per route × skill × KB × model × failure-class: first-pass success, passes-to-green, cost-to-green, escalation rate. Lesson ROI: before/after success on targeted signatures — a lesson that doesn't move its number in 60 days gets deprecated, and the Gym proves nothing else regressed. Reviewer-human agreement. Confidence calibration curves (stated 0.9 vs measured reality; auto-rescale downstream consumers of confidence).

**Mine:** Gap Miner v2 works three veins: escalations and failed verifies (missing knowledge), **human edit diffs** (missing standards), and denial events (missing route-catalog knowledge or over-broad attempt patterns). Add triage-vs-outcome mining: triage predicted "simple config fix" but the doer burned 3 passes = triage rubric drift. All of it flows to Dreamer as scored proposals and to the weekly digest as decisions.

**The digest is a decision meeting, not a dashboard.** Every weekly item ends in a verb: promote this lesson, deprecate that KB, raise route X to L2, recalibrate the judge. Unread digests are the #1 way flywheels die — make it one page, mandatory, and tracked ("decisions executed per week").

---

## 3. GAPS — will hurt within 90 days

1. **Your "no PII" assumption is wrong.** Recipes move employee and customer data; failed-job error payloads, lookup-table snapshots, and connection responses contain it, and your doer reads all of them. You don't need HR's encryption stack, but you need a scrubber at capture (secrets + PII patterns) and a stated retention policy. One incident here and Legal re-reviews the entire program.
2. **Sandbox fidelity.** Fixes validated against stub connections and empty lookup tables won't transfer. You need environment-parity checks (manifest shape diff: AI env vs real project), realistic test data per recipe, and promotion-transfer rate measured from day one — it's the number humans will judge the whole program on.
3. **No executable definition of done.** "Build report looks good" is gradable prose, not done. Every ticket needs acceptance criteria as a runnable test job with expected outputs, drafted by triage, approved by the human, *before* the doer starts. Without this, outcome grading is impossible and reward hacking is inevitable.
4. **Incident mode / circuit breaker.** One platform outage = ticket storm = N doers × 3 passes hammering one dead endpoint, burning budget and rate limits. You need global pause, dedupe-to-one-incident, and per-ticket token budget caps — "max 3 passes" caps loops, not money.
5. **Reviewer contamination.** The reviewer reads the doer's narrative — adversarial input. Give it raw artifacts (diffs, job logs) first, the report last. Same-KB correlation means shared blind spots, which is why seeded-fault canaries are mandatory, not optional.
6. **Ownership of AI-built assets.** When an AI-authored fix breaks prod at 2am, on-call needs owner + runbook + rollback in the manifest. Decide now who is paged — and make the manifest the runbook by enforcing a runbook section.
7. **Signature granularity.** "Same signature 3x" is your entire learning trigger and it's unbuilt. Too narrow: no lessons ever fire. Too broad: wrong lessons get promoted. Plan to iterate signature definitions weekly for the first month, version them, and replay the Gym when they change.
8. **Version pinning in audit.** If every logged action doesn't carry skill/KB/prompt/model versions, your telemetry becomes uninterpretable the first time anything changes — which is week two.

---

## 4. RISKS — the two quiet failures

**1. Green-washing: grades drift up, reports glow, humans stop reading.** The doer learns to write reviewer-pleasing reports; the reviewer — same KBs, same blind spots — accepts them; grades climb while soak survival stays flat; approvers, seeing a streak of beautiful cards, start rubber-stamping. Nothing alarms. The first visible symptom is a promoted manifest failing in production, and the program loses a year of trust in a day. Early-warning pair: **review time ÷ manifest size** collapsing toward zero, and **grades vs soak-survival divergence**. Either moving wrong for two weeks = freeze all autonomy increases. The deterministic verifier (Idea 1) is the structural fix; the pair is the smoke detector.

**2. The learning loop becomes write-only memory.** Lessons, Build Memories, Solved-Issues, and telemetry accumulate; nothing is ever deprecated; the digest goes unread; stale gotchas in the route catalog actively mislead the doer; success decays a point a month with no attributable cause, because every lesson "passed review" once. This platform doesn't die in an incident — it dies at a budget review where nobody can name one decision the telemetry ever drove. Early-warning pair: **lesson deprecation rate** (zero = the loop is broken) and **digest decisions executed per week** (zero = shelfware). Both fixes are structural, not cultural: decay + Gym-gating + decision-format digests.

---

## 5. METRICS — the 5 numbers

1. **Zero-touch close rate** — % of eligible tickets reaching verified-green in AI Production with no human action beyond final approval. The autonomy yield. Trajectory matters more than level: demand ~+5 pts/month.
2. **Human edit distance at promotion** — % of manifests promoted unmodified. The trust metric; humans voting with their hands beats any grade. Rising edit-distance-zero *with* falling review time = winning; falling review time with flat edit distance = Risk #1.
3. **All-in cost per resolved ticket vs human baseline** — tokens + infra + priced human review minutes vs loaded historical cost per fix. The number the sponsor repeats upward, and the instant tripwire for runaway loops.
4. **14-day soak survival** — % of promoted manifests with no revert and no recurrence in real production within 14 days. The truth serum: the one number that cannot be gamed by better prose. Below ~85%, stop everything else and fix transfer fidelity.
5. **Repeat-failure rate on lesson-covered signatures** — after a lesson is promoted, its signature's recurrence should go to ~zero. This is the proof the platform *learns* rather than merely *works* — and the entire justification for the intelligence layer's existence.

(If allowed a sixth: median time-to-green vs historical MTTR — the most visceral demo, but it's a consequence of the five above.)