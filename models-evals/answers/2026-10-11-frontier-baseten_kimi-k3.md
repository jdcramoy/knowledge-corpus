Panel position: the harness's scarcest asset isn't capability, it's *trustworthy signal* — your own telemetry says the estate sometimes lies to itself, and every economy or autonomy layer built on top of that trades counterfeit. So these are ordered as a stack: truth layer first, then trust, simulation, autonomy, prediction, evolution.

---

**1. Proof-Bearing Claims** *(truth layer)*
- **What:** Change the brain bus so an outcome claim is a typed object requiring a re-fetchable proof artifact — Jira transition ID, Workato job-history URL + row-count delta, file hash. Claims without proofs are accepted only as tier "asserted" and rendered second-class everywhere; evidence re-fetches proofs instead of re-reading claims. Today evidence audits after the fact — this makes unproved success *unwritable at the source*.
- **Why it compounds:** Directly attacks the false-success incidents; every proved claim becomes training data for calibration scoring (#3) and twin fixtures (#4).
- **First step:** `submit_claim()` wrapper in the brain MCP requiring a proof pointer, plus two proof adapters (Jira status, Workato job history). Backfill tiers on the existing claims ledger.
- **Risk:** Proof relevance — agents learn to attach *any* artifact. Dissenter must sample-check that the proof semantically matches the claim.

**2. The Denominator Oracle** *(truth layer)*
- **What:** Every job must declare its population — expected N computed independently from source (Workday count, JQL count, manifest). The ledger records numerator/denominator/coverage% per run, and "green" requires coverage ≥ threshold, not exit code 0. "The job ran" stops being a claim and becomes arithmetic.
- **Why it compounds:** Kills the under-collection failure class permanently; coverage% becomes comparable across the estate and shortfalls auto-file to cortex's attention queue with the delta attached.
- **First step:** The 3 jobs that hurt most — write expected-count queries, append coverage lines to watchdog output. Half a session.
- **Risk:** Event-driven flows have no knowable denominator — allow "declared-unbounded" but require sampling audits (re-fetch 20 random events, verify processing).

**3. The Calibration Ledger** *(trust economy)*
- **What:** Agents file falsifiable predictions with confidence and resolution date; a nightly resolver computes Brier scores; each agent's calibration sets its budget, auto-approval ceiling, and fusion-gate bypass rights. Trust stops being *configured* in the trust-ladder and starts being *measured*. Incubating proposals must stake a success prediction to enter the queue — stale ones expire and forfeit the stake.
- **Why it compounds:** Kills two named weaknesses (trust-by-fiat, unbounded incubation); every resolution sharpens scores, and well-calibrated agents earn cheaper fusion gating — an actual inter-agent economy.
- **First step:** `predictions.jsonl` + resolver script; backfill 20 predictions from existing claims and dream reports; run silently two weeks before wiring any gates.
- **Risk:** Gaming via trivial predictions — use proper scoring rules that reward calibrated boldness, and restrict eligible events to consequential, genuinely uncertain ones.

**4. The Twin Gate** *(simulation)*
- **What:** Build the accepted replay-gym into an estate twin — recipe exports, Jira states, scheduler configs as fixtures — and require any prod-touching proposal to ship a *twin-run diff*: before/after behavior on recorded inputs. Dissenter stops arguing rhetoric and attacks empirical diffs.
- **Why it compounds:** Replay-gym is already accepted; the gate is the missing forcing function. Each twin run generates new replay-fixtures, so fidelity compounds with use.
- **First step:** Twin loader for ONE Workato project (export recipes to fixtures); run one stuck incubating proposal through it; attach the diff to its record.
- **Risk:** Twin drift — a stale twin lies with confidence. Enforce snapshot freshness SLAs; every diff stamps its snapshot age.

**5. The Shadow Estate** *(counterfactual execution)*
- **What:** For every decision Josh defers, execute the deferred action in dry-run mode against read-only APIs and track what would have happened — cost avoided, risk accrued, value forgone. Deferral becomes a ranked *regret ledger*: "your 11 deferrals: 3 would have saved ~$X, 2 are now urgent, 6 were correctly deferred."
- **Why it compounds:** Converts the bottleneck itself into training data — the regret ledger is exactly the empirical corpus needed to set delegation-envelope caps (#7) with evidence instead of nerve.
- **First step:** Extend `shadow-state.json` with a counterfactual runner for 3 current deferred items; dry-run paths already exist for most reads.
- **Risk:** Counterfactuals are simulations — count only *verifiable* deltas (a failure that actually occurred while deferred), never present modeled savings as fact.

**6. Reversible Rails** *(autonomy)*
- **What:** Headless agents may write to gated paths if the write carries a journaled inverse patch, sits behind a flag, and passes post-write verification within a TTL — otherwise a revert daemon auto-undoes and files an incident. Changes the safety primitive from *prevention* to *reversibility + observation*, which is what actually unblocks the proposal queue without touching the constitution.
- **Why it compounds:** Every journaled write becomes regression-canon material — the lane gets safer with traffic, inverting the usual risk scaling.
- **First step:** One path class — `instruction-patches/` — with git-backed journal + revert daemon + verification hook. Two weeks, then extend.
- **Risk:** Irreversible actions (prod API writes, sent messages) must never enter this lane. Misclassification is the catastrophic mode — allowlist per-path, never per-agent.

**7. Delegation Envelopes** *(Josh-bottleneck interface)*
- **What:** When Josh resolves a decision, the harness asks for the *rule*, not just the ruling, and distills a policy: scope, dollar cap, expiry, evidence requirements. Future decisions matching an envelope execute autonomously into a delegation ledger with monthly audit digest. The unit of interaction shifts from decisions to policies — Josh legislates once instead of adjudicating forever.
- **Why it compounds:** Structurally shrinks the stated #1 bottleneck; envelope caps get calibrated by the shadow estate's regret data, so autonomy expands at the speed of evidence.
- **First step:** Policy schema + hand-distill 3 envelopes from Josh's last 20 promotion decisions; run the matcher in shadow mode against the 11 deferred decisions and present matches for one-click ratification.
- **Risk:** Over-generalization from single examples — tight scopes, short expiries, and a ratchet: any breach auto-shrinks the envelope.

**8. Precursor Radar** *(predictive)*
- **What:** Mine workato-health/watchdog history for leading indicators — retry-rate creep, connection-error bursts, scheduler drift, queue depth — and file pre-failure tickets 24–72h ahead, each as a scored prediction in the calibration ledger. Watchdog says what broke; this says what's about to, with measured precision.
- **Why it compounds:** The history already exists; every prediction resolved trains the trust economy, and proven precursors become permanent monitors.
- **First step:** One script, three z-score indicators over 90 days of health JSONL. Log predictions silently for a month before alerting.
- **Risk:** False-positive fatigue — run quiet until precision is proven; route only through cortex's attention queue, never direct.

**9. The Skill League** *(learning loop)*
- **What:** A hook logs every skill invocation with session outcome; skills accrue usage, win-rate-vs-baseline, and cost. Nightly pass quarantines bottom performers (rename to `.quarantine` so they stop loading), routes mid performers to dreamer as fix-or-kill targets, cites top performers in morning loadouts. Skills become a managed portfolio instead of 57 unmeasured assets.
- **Why it compounds:** Closes the dreamer's improvement loop — it finally knows which instructions *lose money*, and quarantine is reversible so mistakes are cheap.
- **First step:** Session-end hook writing `skill-stats.jsonl` + one aggregation script; report-only for two weeks before any quarantine.
- **Risk:** Attribution noise — a skill loaded during a failed session isn't the cause. Use per-skill deltas vs. baseline and enforce a minimum-use floor before any demotion.

**10. The Chaos Canary** *(observability red team)*
- **What:** A weekly agent injects known faults into the twin and allow-listed non-prod surfaces — kill a connection, corrupt a fixture, stall a scheduler — and measures whether watchdog/evidence/cortex detect it and how fast. Detection latency becomes a fleet metric; undetected faults auto-file monitoring proposals. Instead of wondering whether the estate can still lie to itself, you continuously prove it can't.
- **Why it compounds:** Each run produces labeled incident data — the scarcest resource for training dissenter and the radar. Monitoring trust becomes earned, not assumed.
- **First step:** Three fault scripts (twin-only) + a detection checker over bus/reports + one weekly plist. First run establishes the detection baseline.
- **Risk:** Blast radius — hard twin/fixture allowlist until the canary itself has a clean record.

---

**Build order if it were my week:** 1 → 2 (stop the lying) → 3 (start scoring) → 6 (unblock the queue) → 7 (shrink Josh). Everything else slots in as the data allows — the twin feeds the canary, the shadow estate feeds the envelopes, and the calibration ledger is the connective tissue the whole stack pays into.