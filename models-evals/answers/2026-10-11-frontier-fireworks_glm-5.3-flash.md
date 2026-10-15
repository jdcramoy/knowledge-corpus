Here are my 10, ordered roughly by how much they unblock the rest.

---

### 1. The Reversibility Ladder (signed autonomy envelopes)
**What:** Classify every write action R0–R3 by blast radius and undo cost, build machine-executable undo for each R1 class, and have Josh sign standing envelopes ("R1 + <$2 + twin-passed = auto-execute"). The harness self-executes inside envelopes, and any FALSE claim or failed undo automatically contracts envelope width — a circuit breaker.
**Why now / compounds:** The pipeline's bottleneck is authority, not ideas (26 filed / 8 built). Envelopes convert accumulated trust into execution *without* violating never_auto — they're Josh-signed pre-authorizations, not constitutional hacks. Each clean month earns wider envelopes; the Actuary (#10) sizes them.
**First step:** One session — pick the 3 most frequent write classes (Jira label/comment, BSYS story filing, config export to staging), write undo scripts, define the R0–R3 taxonomy, run 5 envelope executions in staging.
**Risk:** An undo that itself fails in prod (non-idempotent side effects) — so R1 admission requires the undo to pass a twin run (#3).

### 2. The Decision Compiler (standing orders)
**What:** Treat Josh's decisions as a language to compile: the dreamer mines decision-inbox history and past approvals into recurring patterns, drafts standing-order policies (condition → action → sunset), the dissenter attacks them, Josh approves once, and proposal-decide.py executes them forever after. Every compiled policy permanently shrinks the inbox.
**Why now / compounds:** 11 deferred decisions is the telemetry; the corpus of past decisions is already logged and is pure training data. Decision mass becomes monotonically decreasing — this is the only interface idea where Josh's effort goes down over time.
**First step:** Mine the last ~30 decisions, draft 3 policies (e.g., "UAT-complete + config-only + <$5 → auto-promote"), one session including dissenter review.
**Risk:** Over-broad policy from a small sample — every policy ships with a 90-day sunset and a match-count cap.

### 3. EstateTwin (replay-gym realized, plus chaos pre-mortems)
**What:** Fixture-recorded replicas of Jira/Workato state where promotions, alerts, and proposals run dry-run first — with adversarial perturbation: the twin injects the estate's *historical* failure modes into a proposal's execution path. Prod-gated artifacts must show a twin trace.
**Why now / compounds:** replay-gym is already accepted and sitting unbuilt — highest-leverage asset in the pipeline. Every incident autopsy becomes a new chaos scenario, so the twin's failure library grows with the estate's real history.
**First step:** One session — record live API responses for one promotion flow into fixtures/, replay the manifest dry-run, assert on final state.
**Risk:** Twin drift (fixtures rot, twin diverges from prod) — watchdog refreshes fixtures weekly and a drift-check diffs twin vs. live on 20 sampled calls.

### 4. The Calibration Market (forecast staking)
**What:** Agents file falsifiable forecasts ("scheduler X stalls within 7 days," "ticket Y slips") with reputation stakes; watchdog/evidence auto-resolve them; Brier scores append to models-evals, and calibration rank gates standing — low-calibration agents get fusion cross-checks, high-calibration agents get dissenter fast-pass and wider envelopes.
**Why now / compounds:** Watchdog already emits the ground-truth stream for resolution, and the claim ledger already tracks confidence — this adds the missing temporal axis. Reputation becomes the harness's second currency, earned only by being right about the future.
**First step:** One session — cortex files 5 forecasts at Monday pulse with resolve dates; a Friday script computes Brier scores into models-evals/forecast.jsonl.
**Risk:** Goodharting via safe-bet flooding — mandate a forecast slate with horizon/risk diversity; dissenter audits the slate.

### 5. Treasury & the Spot Swarm (elastic labor market)
**What:** A spend ledger where every run logs tokens/$ from the gateway; cortex acts as central bank allocating a weekly budget across fixed agents *and* an on-demand spot market — bounties posted to the gossip bus, ephemeral subagents pick them up under per-task dollar caps, results merge with dedupe keys. The fixed 11-agent fleet becomes a brokerage over an elastic workforce.
**Why now / compounds:** The gateway already sees usage, and the ~30–40 concurrency cap defines realistic swarm size; census-shaped work (60 tickets, 57 skills, backlog triage) is currently starved. Budgets make "do more" quantitatively decidable and give #1 and #4 real stakes.
**First step:** One session — a run-ID-tagged usage logger writing spend.jsonl, plus one 15-subagent census of the 60 Jira tickets under a hard $3 cap.
**Risk:** Runaway cost/duplication — caps enforced in code, not prompts.

### 6. Double-Entry Estate (reconciliation mesh)
**What:** The estate runs single-entry bookkeeping — internal claims with no external counterpart. Add a nightly reconciler that diffs claims/, build-ledger, and "done" states against live Jira/Workato APIs, flagging orphan claims (internal entry, no external proof) and ghost facts (external state, no internal record) to evidence.
**Why now / compounds:** FALSE-claim grounding incidents are documented; this kills the lying estate at the root rather than via 24h spot-checks. Read-only API lanes also sidestep the sensitive-path write gates strangling headless fleet work. Deltas feed the twin's fixtures (#3).
**First step:** One session — reconciler for one domain: build-ledger vs. actual Jira states, orphan/ghost report into evidence's queue.
**Risk:** API scope/rate limits from headless lanes — request a dedicated read-only scoped credential for the reconciler only.

### 7. Shadow Amendments (regression-tested self-modification)
**What:** Instruction-patches currently land blind. Add promotion machinery: each patch applies to a shadow copy of the affected instructions, runs against replay-fixtures + evals, and auto-promotes only if it beats the incumbent — with a held-out split the nightly miner never sees.
**Why now / compounds:** instruction-patches/ has a nightly miner but zero selection pressure, while evals/ and replay-fixtures/ sit unused as fitness functions. Every patch cycle grows the eval suite — self-improvement gets its own flywheel.
**First step:** One session — take 3 queued patches, build a 10-scenario replay runner, score incumbent vs. patched, file to models-evals/patch.jsonl.
**Risk:** Overfitting to the eval suite — held-out split, and constitutional-class patches always require Josh.

### 8. Skill Natural Selection
**What:** 57 skills with no fitness loop. Instrument invocation, outcome, and latency per skill (same run-ID middleware as #5), compute fitness, and let the dreamer run selection: bottom-quartile skills get deprecation drafts, contested skills get A/B variants, high-fitness skills get promoted into agent frontmatter. Skills evolve under usage pressure instead of accreting.
**Why now / compounds:** The treasury middleware makes this nearly free; skill sprawl is compounding debt today. Months of selection pressure produce a lean, proven toolkit — an evolvable organ, not a junk drawer.
**First step:** One session — invocation telemetry to skills-telemetry.jsonl + a first fitness table over the last 30 days.
**Risk:** Survivorship bias against rarely-invoked skills — require an invocation floor before any skill is cull-eligible.

### 9. Hot Standby (process migration for agents)
**What:** A standard open-loop state schema — active loops, partial artifacts, next action, plus a world fingerprint (git SHA, queue depths, clock) — auto-serialized every N minutes by any long-running lane. Any agent, or a fresh session after a crash, resumes from checkpoint instead of reconstructing from prose. Handoff docs become a protocol.
**Why now / compounds:** Context-reset losses are documented telemetry, and headless launchd lanes are exactly the processes that die mid-flight. Reliable long lanes are a prerequisite for everything else on this list.
**First step:** One session — define the checkpoint schema, add a heartbeat hook to watchdog's lane, then kill a session mid-run and resume it from checkpoint as the acceptance test.
**Risk:** Stale checkpoints resuming against a changed world — fingerprint mismatch forces a re-plan, never a blind resume.

### 10. The Actuary (denominator-aware assurance that sizes autonomy)
**What:** Replace point-checks with statistical assurance: every claim must carry its denominator (58/60, not "done"), and a nightly Monte Carlo sampler deep-audits a random slice of the estate, publishing a confidence interval on estate health to the bus. That number — not vibes — sizes the autonomy envelopes (#1) and swarm budgets (#5).
**Why now / compounds:** "Green jobs + path proofs don't measure population coverage" is the harness's own diagnosis. This creates the first principled feedback loop between *measured* trust and *granted* autonomy: assurance up, leash lengthens; assurance down, it shortens automatically.
**First step:** One session — add a required `denominator` field to the claim schema (enforced by evidence) and run one 20-sample random deep audit of Workato schedulers with a published CI.
**Risk:** Sampling blindness to rare-but-catastrophic failures — watchdog's exhaustive checks stay in parallel, and high-blast-radius classes are exempted from sampling into 100% checks.

---

**Sequencing note:** Treasury middleware (#5) and the reconciler (#6) come first — they generate the data everything else consumes. Envelopes (#1) come last — they're the payoff that consumes it.