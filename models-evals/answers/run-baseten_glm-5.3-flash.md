# Wave 3: Physics, Particle Physics, Quantum, Frontier CS, Evolution

---

## 1. Trigger Hierarchy with Prescales (LHC detector design)

**Concept:** LHC events pass two trigger stages: Level-1 (coarse, µs, 40 MHz → ~100 kHz) then High-Level Trigger (full reconstruction → ~1 kHz). The load-bearing subtlety is the **prescale column**: for abundant uninteresting event classes, accept 1/N randomly, and *record the prescale factor* so downstream rates can be statistically unfolded. Rare/interesting classes get prescale = 1.

**Mapping:** The gossip bus → evidence agent → claims ledger. Right now every observation and PATTERN flows to consumers at full rate and corroboration is cheap, so the bus drowns and evidence-agent attention is diluted.

**Mechanism:** New `trigger.py` between agent outboxes and consumers. L1: per-agent local filter with a per-event-class prescale table (`prescales.json`); accepted items carry their prescale factor. L2: evidence agent sees only L1-accepted items; corroboration counts are computed on **unfolded** counts (raw count × prescale, with Poisson uncertainty). Weekly gardener pass adjusts prescales using cost-governor posteriors.

**Kills/Enables:** Kills bus drowning and cost-per-verified-value bloat (evidence stops reading everything). Kills the "rare event never verified because it's 1 of 10,000" class — prescale=1 classes for prod-touching and never_auto-adjacent items guarantee they always reach L2.

**Failure mode:** Prescale drops the one observation that mattered. Guard: never prescale anything citing a P0 incident or touching prod; an "express line" bypasses L1 entirely; record the prescale-column version with each count so rate comparisons survive prescale changes (LHC does exactly this).

---

## 2. The Trials Factor / Look-Elsewhere Effect (particle physics statistics)

**Concept:** When you scan many possible windows/regions and report the *most significant* fluctuation found, its significance must be corrected for the number of trials. The Higgs 3σ local bumps became ~2σ globally because someone scanned the whole mass range. LHC handles this with background-only pseudo-experiments: run the full analysis chain on simulated background, record the max-statistic distribution, and calibrate against *that*, not the naive p-value.

**Mapping:** harness-dreamer's nightly pattern mining + claims ledger confidence. The dreamer must report a pattern every night; scanning hundreds of candidate patterns across transcripts and reporting the best one guarantees "discoveries."

**Mechanism:** Dreamer's miner emits `candidates_examined: N`. Claims ledger promotion rule: a PATTERN selected as best-of-N gets prior odds shrunk by 1/N before promotion to verified. Plus empirical null: monthly, `null_miner.py` runs the *same* mining prompt on time-shuffled/permuted transcripts and records the max-score distribution — that becomes the calibration curve for "is this pattern real, or just the best of N?"

**Kills/Enables:** Directly kills the observed weakness: PATTERN flipping on two agents merely discussing, and dreamer confabulating a nightly discovery. Makes dreamer's output rate *honest* — some nights the correct output is "nothing survived the trials factor."

**Failure mode:** N is fuzzy for LLM-mined patterns (the model doesn't enumerate its search). Guard: don't count N directly — calibrate against the permutation null (which is what LHC actually does); use countable N only where the miner genuinely enumerates candidates.

---

## 3. Multimessenger Coincidence Detection with Systematics Vetting

**Concept:** GW170817 was confirmed because *independent* channels (gravitational waves + gamma-ray burst) registered coincident events within a window, with joint significance computed from each channel's separately-measured background rate. The crucial discipline: channels sharing an instrumental systematic (common upstream dependency) are **not independent** and must not be double-counted.

**Mapping:** watchdog + estate sensors. Currently each sensor alerts alone (flapping noise), and "corroborated" alerts may secretly share one root cause sensor.

**Mechanism:** `coincidence.py` over timestamped JSONL from all channels (recipe run logs, cost-governor anomalies, watchdog probes, evidence-agent findings). Each channel's background rate λᵢ is measured from its own history. Candidate event = signals of the same class within ±10 min; joint score = Σ log pᵢ. A channel registry records dependency edges (same MCP server, same host, same upstream job); channels sharing a dependency form one "systematic group" and contribute **once**. Confirmed multi-*group* events auto-escalate one rung on the trust ladder; single-channel events stay at report level.

**Kills/Enables:** Kills monitoring-inside-the-failure-domain: a dead sensor can't corroborate itself, but two independent groups can flag the *sensor* as failed (the "fleet dead 2 days unnoticed" class). Kills false corroboration through shared upstream — the exact failure mode of two agents discussing.

**Failure mode:** Coincidence starvation — over-aggressive grouping means nothing ever confirms. Guard: track median time-to-confirm as a health metric; if it grows, gardener relaxes windows/grouping; keep a visible "interesting but unconfirmed" tier so single-channel signals aren't lost.

---

## 4. Quantum Error-Correction Threshold → Effective N for Fusion Panels

**Concept:** The QEC threshold theorem: below a physical error rate threshold, adding redundant qubits suppresses logical error *exponentially*; above it, adding redundancy makes things **worse**. And it holds only for independent errors — one correlated error source poisons the whole code. For a majority vote of N correlated voters with pairwise error correlation ρ, the effective panel size is N_eff = N / (1 + (N−1)ρ).

**Mapping:** The fusion panel (same prompt to N models + cross-check) and the prediction ledger.

**Mechanism:** From prediction-ledger history, compute pairwise co-failure rates (or Cohen's κ) between model pairs. Compute ρ̄. A `fusion_policy.py` rule: invoke N-way fusion only if N_eff ≥ 2; otherwise prefer one model + evidence agent (a mechanistically *disjoint* channel, which is true independence). Claims promoted via fusion carry evidentiary weight N_eff, not N, in the claims ledger. Recompute monthly.

**Kills/Enables:** Kills the false confidence class where kimi/glm/deepseek all agree on the same wrong fact because they share web-training lineage — correlated error means your 5-way fusion is secretly a 2-way fusion. Directly cuts cost per unit of *verified* value: don't pay for redundancy that buys nothing.

**Failure mode:** ρ estimated from small samples is noise. Guard: require ≥30 joint predictions per pair before trusting ρ; default to ρ = 0.5 (pessimistic) when unknown, so fusion is never over-trusted by default.

---

## 5. Quantum Zeno Checkpoints for Long-Running Agents

**Concept:** The quantum Zeno effect: a system that is *frequently measured* cannot evolve — observation freezes the state. Transitions require unobserved intervals to accumulate amplitude.

**Mapping:** Fleet scheduler / launchd long jobs (dreamer, harness-fix, estate-architect) — agents that run 40 minutes and drift far off-policy before anyone notices.

**Mechanism:** Any agent run >10 steps appends to `zeno.jsonl` every K actions: {goal, claimed file ownership, 2-3 invariant assertions ("no writes outside claimed paths", "cost so far < X")}. `zeno_watch.py` (stdlib) reads heartbeats: missing heartbeat or violated invariant → SIGTERM + respawn from last checkpoint. The design intent: without frequent cheap measurement, the trajectory diffuses into off-policy states; frequent trivial assertions collapse it back onto intent, and checkpoints make partial work resumable.

**Kills/Enables:** Kills the runaway-agent class (long undetected wrong-path runs burning cost and touching wrong files); kills "fleet job silently wedged." Enables cheap partial-work recovery.

**Failure mode:** The measurement itself becomes the burden (Zeno's own cost). Guard: K adapts to measured check overhead; checks are JSON appends verified by grep-level scripts, so cost per collapse is microseconds.

⚠️ **Honesty flag:** the physics here is framing. The mechanism is "frequent cheap assertions + checkpoint/respawn," which is valuable but is essentially watchdogging. Kept because the *interval design principle* (collapse early, cheaply, often — rather than one big final review) is a real design delta over current practice.

---

## 6. Renormalization-Group Coarse-Graining of the Knowledge Tree

**Concept:** RG: integrate out short-distance degrees of freedom level by level; only **relevant operators** — couplings that grow under coarse-graining — survive at long distance scales; irrelevant details flow away but the microscopic theory is preserved.

**Mapping:** Gardener + knowledge tree + INDEX.md bloat.

**Mechanism:** Define explicit levels: L0 raw transcript evidence → L1 observations → L2 patterns → L3 principles/procedures. Gardener's compaction pass must answer, per item: *"which decision at the next-coarser level does this detail change?"* If none in the review window, the item is **integrated out**: detail moves to `archive/` (git retains the microphysics), the parent file gains a one-line "relevant coupling" summary with a pointer (`micro: archive/x@commit`). INDEX.md carries only L2+ relevant items. Items that repeatedly change decisions get tagged "relevant" and earn stricter edit protection.

**Kills/Enables:** Kills knowledge rot *and* recency-window learning simultaneously — old knowledge is compressed, not deleted, so its influence persists at the scale where it matters. Kills INDEX.md/session-prompt bloat. Enables a diagnostic you don't have: **integration regret** — when a failure occurs, check whether the needed micro-detail existed but was integrated out; track that count as gardener's tuning signal.

**Failure mode:** Coarse-graining away detail that later becomes load-bearing (rare edge cases are, by definition, irrelevant under normal coarse-graining). Guard: the archive pointer + git history guarantee recoverability; the integration-regret metric sets the aggressiveness of the compaction pass.

---

## 7. Pleiotropy-Gated Change Control (evo-devo gene regulatory networks)

**Concept:** Evo-devo result: genes deep in the developmental network — high **pleiotropy** (one gene affecting many traits) — are strongly conserved because mutating them breaks everything; low-pleiotropic genes mutate freely. Evolution keeps modularity to *localize* pleiotropic damage.

**Mapping:** Trust ladder + instruction-patch queue + knowledge-tree write gates. This is the missing principled basis for *which* items deserve which trust rung — currently trust class is assigned by hand.

**Mechanism:** `pleiotropy.py` builds a consumer graph: for every instruction, claim, INDEX line, skill, and prompt clause, grep the fleet's prompt files, configs, and scripts to count consumers. Write-gate policy: degree ≤ 2 → auto-safe allowed; 3–9 → propose; ≥10 or anything INDEX.md consumes → Josh gate + mandatory regression fixture. Additionally: when a proposed change touches ≥5 consumers, gardener is required to propose a **module split** instead (localize the pleiotropy, like HOX-cluster modularity).

**Kills/Enables:** Kills Goodhart drift on proxies — the canonical Goodhart event is a "small" proxy tweak whose blast radius nobody measured. Kills "small edit broke 7 agents." Turns the trust ladder from vibes into graph theory.

**Failure mode:** Degree undercounted when consumers are constructed by LLMs at runtime rather than statically greppable. Guard: lint rule that any prompt-embedded knowledge must be referenced via an INDEX path; treat unknown consumers as maximal pleiotropy (the evo-devo default — conserved until shown otherwise).

---

## 8. MAP-Elites Archive + Novelty Search for Self-Improvement (quality-diversity / open-endedness)

**Concept:** MAP-Elites (Mouret & Clune): maintain an archive holding the best solution per cell of a behavior-descriptor grid, preserving diversity regardless of global fitness. Lehman & Stanley's novelty search: when objectives are deceptive (proxies get gamed), search for *novel behavior* under minimal criteria instead of maximizing the objective.

**Mapping:** harness-dreamer's nightly invention mandate + harness-fix lane + outcome ledger.

**Mechanism:** `elites.jsonl`: descriptor axes fixed at design time (e.g., failure-class-addressed × harness-loop-touched × blast-radius). Spec-distiller classifies every dreamer proposal into a cell; best-per-cell is retained even if globally outperformed. The dreamer prompt is augmented with: (a) the currently-empty cell list, (b) 3 elites from the most *distant* cells as cross-inbreeding context. When the outcome ledger shows the value proxy diverging from actual value (Goodhart signature), harness-fix **switches objective to novelty** (maximize nearest-neighbor distance in descriptor space) subject to minimal criteria: must pass regression fixtures. All implementable with a dict of cells and k-NN in stdlib.

**Kills/Enables:** Kills the self-improvement local optimum — dreamer re-proposing the same class of patch every night; directly addresses recency-window-only learning (the archive keeps good old ideas alive and re-combinable). Novelty-mode is a *circuit breaker* against Goodhart rather than another proxy.

**Failure mode:** Archive becomes a junk drawer of mediocre diversity. Guard: per-cell quality floor; cells unvisited for 90 days decay out; descriptor axes reviewed quarterly for decision-relevance.

---

## 9. Muller's Ratchet → Forced Recombination for the Instruction-Patch Queue

**Concept:** Muller's ratchet: in an asexual population, deleterious mutations accumulate **irreversibly** — with no recombination, the clean genotype can never be recreated, and drift load ratchets monotonically. Sex exists largely to break this ratchet.

**Mapping:** The instruction-patch queue, which appends patches and never merges them; plus canonized failures that add rules forever.

**Mechanism:** Maintain a "wild-type" reference: the constitutional core + the regression fixture suite = the ancestral genome. Track a **ratchet counter**: patches that (a) added a rule and (b) whose benefit no later measurement detected. When the counter trips (or quarterly), harness-fix runs a recombination pass: take the current accumulated instruction set plus 2–3 top historical variants from git history of prompt files, and generate a *merged* prompt where each clause must earn its place against the fixtures; clauses surviving neither selection nor recombination are dropped.

**Kills/Enables:** Kills monotonic prompt cruft — the current regime guarantees prompts grow forever, agents over-constrain, and every canonized failure is permanent. Makes failure-canonization **reversible**, which is the property the canonize-failure loop is missing.

**Failure mode:** LLM-mediated crossover hallucinates a merge that subtly changes a clause's meaning. Guard: every merged prompt must pass the full regression fixture suite plus an evidence-agent diff review; pre-merge prompt kept in git for instant rollback.

---

## 10. Bet-Hedging + Ergodic Geometric Mean for Fleet Configuration

**Concept:** Evolutionary bet-hedging: in unpredictable environments, the genotype maximizing the **geometric mean** of fitness wins, even at lower arithmetic mean — stochastic phenotype switching at small rate ε maintains viable variants for regime shifts. Ergodicity economics (Ole Peters) makes this precise: for multiplicative processes, time-average growth ≠ ensemble average, and variance drag punishes volatile configs.

**Mapping:** Per-agent model pins + cost-governor + outcome ledger.

**Mechanism:** Outcome ledger changes its objective from mean score per config to **geometric mean of per-session returns** (value−cost, floored so logs exist). Cost-governor reserves ε ≈ 10% of each agent's runs on off-policy configs (second-best model, alternate prompt variant) — the spore population. Function: (a) divergence between spore and dominant runs is an early detector of novel dominant-config failure; (b) when the dominant config fails, a live candidate exists for promotion, selected on geometric mean rather than average.

**Kills/Enables:** Kills monoculture fragility — today, if all pins drift to one "best" model and that model or gateway regresses, the whole fleet degrades in the same way at the same time. Enables discovery of configs whose value only appears on rare task classes (the arithmetic mean can't see them).

**Failure mode:** ε spend is a pure insurance premium that gets squeezed in cost pressure. Guard: quarterly review — an off-policy config must show geometric-mean value or be rotated out; ε capped by cost-governor.

---

## 11. Fluctuation–Dissipation Gate on Improvement Claims

**Concept:** Fluctuation–dissipation theorem: a system's response to a perturbation is bounded by its spontaneous equilibrium fluctuations. Practical translation: **you cannot claim a causal improvement smaller than the metric's noise floor.**

**Mapping:** Outcome ledger + value ledger + harness-fix improvement claims + promotion-orchestrator.

**Mechanism:** `fdt_gate.py`: any claim of the form "change X improved metric M by δ" must compute M's stationary distribution from pre-change history (robust σ via MAD after detrending). The claim is accepted only if δ > 2σ_stat with adequate post-change sample size; otherwise the value ledger books **zero** and records "within noise floor." Metrics whose natural σ exceeds typical claimed effects get flagged as bad instruments for improvement measurement at all.

**Kills/Enables:** Kills improvement theater — harness-fix and dreamer claiming wins that are noise. Kills Goodhart pressure structurally: a noisy proxy *cannot be gamed into visible wins*, so the incentive to game it collapses. Makes the value ledger — the denominator of your cost-per-verified-value — actually trustworthy.

**Failure mode:** Nonstationary history (estate grows, metrics drift) breaks the σ estimate. Guard: rolling-baseline detrending; the gate logs its σ assumptions and the evidence agent audits the σ computation monthly (the gate itself is subject to the claims regime it enforces — deliberately).

---

## 12. CRDT Merge Semantics for Concurrent Knowledge Edits

**Concept:** CRDT theory: state that merges commutatively, associatively, and idempotently provably converges without coordination. Per-key last-writer-wins with Lamport clocks is the simplest such structure.

**Mapping:** Knowledge tree (git-backed) where cortex-spawned agents plus Josh edit concurrently; currently resolved by luck and manual conflict resolution.

**Mechanism:** Restructure shared domain files as JSON with per-field records `{value, lamport, agent_id}`. `merge.py` resolves per-field by (lamport, agent_id) tiebreak — deterministic and order-independent. Agents write via read-modify-merge, never direct writes, on shared files. Deletions are tombstones. Gardener periodically compacts LWW records back into prose.

**Kills/Enables:** Kills the lost-update race class (two agents concurrently editing one domain file); removes a real coordination tax on Josh; enables fearless parallel fan-out on *shared* files, which the disjoint-file-ownership convention currently forbids — so it widens what swarms can do.

**Failure mode:** LWW silently drops one agent's semantic intent (field-level wins ≠ intent-level resolution). Guard: CRDT only for structured registers; prose files stay on git merge + Josh review; deletion requires tombstone + gardener ratification. *Note the boundary with the banned atomic-store item:* that was single-writer atomicity; this is multi-writer **convergence semantics** — a different problem, but adjacent enough that you should build only if the race is actually observed.

---

## 13. Cortex as Expected-Information-Gain Scheduler (active inference, stripped to the bone)

**Concept:** Active inference: agents act to minimize expected free energy ≈ epistemic value (expected information gain) + pragmatic value. The usable core is **Value of Information** ranking — and its key theorem-backed property: observations of near-certain beliefs have ~zero EIG, so uncertainty-seeking provably redistributes attention away from the well-observed.

**Mapping:** cortex (hourly attention coordinator) + claims ledger Beta posteriors.

**Mechanism:** Each candidate attention action scores: EIG of one Bernoulli observation against the least-certain **load-bearing** claim it would touch (closed-form for Beta posteriors — no sampling needed), plus pragmatic term from the value ledger, minus cost from cost-governor. Load-bearing = consumer count from idea #7's graph. Near-certain claims contribute ~0 EIG, so cortex stops re-verifying the obvious; high-variance × high-consumer claims float to the top.

**Kills/Enables:** Kills agents converging on the same blind spots *and* on the same comfortable certainties — attention flows to load-bearing uncertainty by construction, not by nagging. Cheap: the EIG formula is a few lines over existing ledger data.

**Failure mode:** Pure EIG forages into weird low-value corners. Guard: pragmatic term anchored by the value ledger; cap on EIG-only actions per hour.

⚠️ **Honesty flag:** the free-energy language is decoration; this is VoI scheduling, a standard decision-theory mechanism wearing a Friston costume. Kept because the mechanism stands alone and is implementable this afternoon.

---

# Ranking (leverage / cost)

1. **#2 Trials factor** — near-zero cost (one logged field + a permutation script you run monthly), and it attacks the single most-observed weakness in your description: PATTERN flips and dreamer confabulation. It changes the *epistemic pricing* of everything the dreamer produces, forever.
2. **#11 Fluctuation–dissipation gate** — a ~50-line script that makes the value ledger honest. Its leverage is multiplicative: every other improvement claim in the system now passes through it, so it upgrades the entire measure→learn loop, not one component.
3. **#7 Pleiotropy gating** — a grep-based degree counter coupled to the trust ladder you already have. It converts the trust ladder from hand-tuned classes into measured blast radius, and is the only idea here that structurally kills silent-blast-radius Goodhart drift.

(#1 trigger hierarchy is the runner-up: it's the biggest cost win, but it needs more plumbing than the top three.)

# Honesty Pass (self-rejection)

- **#5 Zeno checkpoints** — metaphor-heavy. The physics adds framing, not mechanism; what remains ("frequent cheap assertions + checkpoint") is solid engineering but not a physics import. Kept at reduced confidence.
- **#13 Free-energy cortex** — the FEP language is a costume; the actual content is standard VoI scheduling. Kept because the mechanism is independently strong, but if you implement it, strip the philosophy from the docs.
- **#12 CRDT** — real computer science, not a metaphor, but risks over-engineering: if concurrent-edit races are rare in practice, this degenerates into "we wrote a merge script." Build only if the race class is observed. Flagged as conditionally valuable.
- **#10's ergodicity math** — the geometric-mean objective is defensible, but fleet "returns" aren't strictly multiplicative; part of the justification is aesthetic. The bet-hedging (ε spore population) half is the load-bearing part.

# Cross-Pollination (physics × evolution compositions)

1. **RG coarse-graining (#6) × Neutral theory (Kimura) → "banked cryptic variation."** RG alone says discard irrelevant detail; neutral theory says most variation is neutral *under the current regime* — and cryptic variation is exactly what evolvability draws on when the regime shifts. Composition: gardener integrates out neutral detail from the *active path* but banks it in the archive as standing variation; when a novel failure class appears, the first search is the archive, not a fresh dream. Neither concept alone justifies *keeping* the micro detail — the composition does, and the integration-regret metric from #6 measures how often the bank pays out.

2. **QEC threshold (#4) × Muller's ratchet (#9) → recombination as decorrelation.** Correlated model errors are to a fusion panel what accumulated deleterious mutations are to an asexual genome: they make added redundancy useless or harmful. Composition rule: before scaling fusion capacity, run a recombination pass on the panel — swap one member for a model from the ε spore pool (#10) or a different training lineage — because decorrelating the panel raises the effective threshold. Concrete invariant: no two models with measured co-failure κ > 0.5 sit on the same panel.

3. **Trigger prescales (#1) × Bet-hedging → the parking stream.** A prescale table tuned to known event classes means genuinely novel failures are systematically never recorded — the exact reason LHC keeps prescale-1 "streaming" paths for new physics. Composition: trigger.py routes unclassifiable events (those matching no known L1 class) to a `novel_stream.jsonl` at prescale 1 unconditionally, bounded by rate; harness-dreamer mines that stream to fill empty MAP-Elites cells (#8). The prescale design alone would let novel events die; the bet-hedging logic is what mandates paying the ε bandwidth premium to keep the unknown sampleable.