# Harness wave 3 — physics × evolutionary science fusion (2026-10-11)

Panels: deepseek-v4-pro (full answer), baseten/glm-5.3-flash (full answer at 20k tokens
after a 12k reasoning exhaustion — worth the rerun), fireworks/kimi-k3 (truncated at 6k,
but its visible brainstorm independently hit the LHC trigger hierarchy + minimum-bias
sample), baseten/kimi-k3 (empty). Plus main-model adjudicator + live research
(AlphaEvolve arXiv:2506.13131, CycleQD, GAVEL, Mix-ME, Renormalizing Generative Models,
Keep-CALM-and-CRDT-On VLDB).

Raw answers: knowledge/models-evals/answers/run-baseten_deepseek-v4-pro.md,
run-baseten_glm-5.3-flash.md. Ledger: models-evals/fusion.jsonl.

Filter: banned = all of wave-1 frontier stack + next-10 review. Convergence count is
noted per idea — independent arrival across model families is the strongest signal here.

**Convergence map:** LHC trigger hierarchy hit by 4 sources (deepseek, glm, kimi,
adjudicator). Muller's ratchet ×3 (deepseek, glm, adjudicator). RG coarse-graining ×3.
Bet-hedging portfolio ×2. MAP-Elites/QD ×2 + research. Affinity maturation ×2.
Stabilizer/syndrome checks ×2. glm contributed 4 ideas nobody else had (trials factor,
multimessenger coincidence, N_eff for panels, fluctuation–dissipation gate) — all four
survived adjudication into the top tier.

---

## Tier 1 — build candidates

### 1. Trials factor / look-elsewhere effect for the dreamer (glm, unique)
**Concept.** Particle physics: scanning many windows and reporting the most significant
bump overstates significance — the Higgs's 3σ local bumps were ~2σ global. The cure is
not counting trials (fuzzy for LLMs) but a *permutation null*: run the identical
analysis on simulated background, calibrate against the max-statistic distribution.
**Mapping.** harness-dreamer nightly mining + claims promotion. The dreamer must report
a pattern every night; best-of-N selection guarantees "discoveries."
**Mechanism.** Miner emits `candidates_examined` where enumerable. Monthly
`null_miner.py` runs the SAME mining prompt on time-shuffled transcripts; the max-score
distribution becomes the calibration curve. Promotion rule: best-of-N patterns get
prior odds shrunk accordingly before a claim can tier up. Some nights the honest output
is "nothing survived the trials factor."
**Kills.** Dreamer confabulation; PATTERN-flips-on-discussion at the source.
**Failure mode.** N is fuzzy for LLM search — hence calibrate on the permutation null,
not counted N. Cost: one logged field + one monthly script. **Highest leverage/cost of
the entire run.**

### 2. Fluctuation–dissipation gate on improvement claims (glm, unique)
**Concept.** Fluctuation–dissipation theorem: response to perturbation is bounded by
spontaneous equilibrium fluctuations. Translation: **you cannot claim a causal
improvement smaller than the metric's noise floor.**
**Mapping.** Outcome ledger, value ledger, harness-fix improvement claims, promotion
readiness.
**Mechanism.** `fdt_gate.py`: any "change X improved metric M by δ" claim computes M's
stationary σ from pre-change history (MAD, detrended); accepted only if δ > 2σ with
adequate samples; else the value ledger books ZERO with "within noise floor." Metrics
whose σ exceeds typical claimed effects get flagged as bad instruments.
**Kills.** Improvement theater; makes the denominator of cost-per-verified-value
trustworthy; noisy proxies become un-gameable (no visible wins → incentive collapses).
**Failure mode.** Nonstationary history breaks σ. Guard: rolling detrend; the gate logs
its σ assumptions and the evidence agent audits the gate itself monthly.

### 3. Trigger hierarchy with prescales + minimum-bias + novel stream (4-way convergence)
**Concept.** LHC: L1 hardware (dead-time-bounded, ~1000× reduction) → HLT → offline.
Load-bearing details both panelists caught independently: (a) the **prescale column** —
accept 1/N of boring classes, record the factor, statistically unfold rates downstream;
(b) the **minimum-bias sample** — a random bypass so trigger efficiency (false-negative
rate) is measurable at all; (c) prescale-1 "streaming" paths so genuinely novel event
classes can never be filtered to death.
**Mapping.** dreamer/project-dreamer mining; cortex attention; eventually bus → evidence
routing.
**Mechanism.** L0: stdlib metadata scanner (unknown error class, conflicts > 1, cost
> 2σ, failed verifications). L1: cheap model scores survivors. L2: full dreamer/fusion
on top-N. Prescales recorded per class in a versioned trigger menu; counts unfolded
(raw × prescale, Poisson uncertainty). 0.1–1% random bypass to L2. Unclassifiable events
→ `novel_stream.jsonl` at prescale 1, rate-bounded; the dreamer mines that stream to
fill empty MAP-Elites cells (#8). Never prescale prod-touching or P0-citing events.
**Kills.** Cost per verified value; the unmeasurable-false-negative hole (today we only
inspect what triage already surfaced).
**Failure mode.** Trigger bias against slow diffuse anomalies. Guard: minimum-bias
sample + monthly no-trigger audit; the dreamer mutates the trigger menu from leakage
estimates.

### 4. Muller's ratchet + forced recombination (3-way convergence)
**Concept.** Asexual lineages accumulate irreversible deleterious mutations; only
recombination recreates the clean genotype. The harness is deliberately Lamarckian
(session lessons are inherited via knowledge writes) — so it needs this guard more than
biology does. glm's sharpening: canonized failures currently add rules FOREVER; prompts
grow monotonically.
**Mapping.** instruction-patch queue, harness-fix lane, all prompt/routing edits.
**Mechanism.** `patch_genome.jsonl` lineage per patch. Fitness window = Brier delta +
P(accept) + skill fitness + value ledger. `ratchet_watch.py`: patches-added with no
measured benefit increments the ratchet counter. On trip (or quarterly): recombination —
branch from last-known-good, each clause must re-earn its place against the regression
fixture suite; survivors merge, the rest drop to a dormant branch (never deleted).
Makes failure-canonization **reversible**.
**Kills.** Monotonic prompt cruft; the quiet death of a self-modifying system.
**Failure mode.** LLM crossover subtly changes clause meaning; purges rare-regime
patches. Guards: full fixture suite + evidence diff review pre-merge; purge needs
harm-evidence or 7-day window; dormant alleles immortal.

### 5. Multimessenger coincidence with systematics vetting (glm, unique) + Ising coupling detector (deepseek, unique)
**Concept.** GW170817 was confirmed by *independent* channels (gravitational waves +
gamma rays) with joint significance from each channel's separately-measured background
rate. The discipline: **channels sharing an upstream systematic are not independent and
count once.** (Ising companion: magnetization high + evidence field low + coupling
rising = social alignment, not evidence alignment.)
**Mapping.** The gossip bus corroboration rule (1 obs / 2 pattern / 3+ act) — currently
two agents *discussing* counts as corroboration even when both read the same upstream
source.
**Mechanism.** `coincidence.py`: per-channel background rates λᵢ from history; same-class
signals within ±10 min score Σ log pᵢ. A **dependency registry** (same MCP server, same
host, same upstream job, same source doc) groups channels; each systematic group
contributes ONCE. Multi-group coincidences auto-escalate one trust rung. Side benefit:
two independent groups flagging a dead sensor catches the "fleet dead 2 days" class from
a different angle than the dead-man switch.
**Kills.** Consensus-without-evidence (the named bus weakness), false corroboration.
**Failure mode.** Coincidence starvation. Guard: median time-to-confirm as a health
metric; a visible "interesting but unconfirmed" tier.

### 6. QEC threshold → effective N for fusion panels (glm, unique)
**Concept.** Quantum error correction works only below an error-rate threshold and only
for *independent* errors. For N correlated majority voters, effective panel size
N_eff = N / (1 + (N−1)ρ̄). Two kimi-family panelists agreeing is secretly a 1.3-model
panel.
**Mapping.** Fusion panels (this very run), prediction ledger, claims weighting.
**Mechanism.** Pairwise co-failure rates (Cohen's κ) per model pair from prediction
history. `fusion_policy.py`: fuse only if N_eff ≥ 2; else prefer one model + the
evidence agent (a mechanistically disjoint channel). Fusion-promoted claims carry
evidentiary weight N_eff, not N. Invariant: no two models with measured co-failure
κ > 0.5 sit on the same panel.
**Kills.** Paying for redundancy that buys nothing; unanimous-but-wrong confidence
(the exact live example in the fusion skill).
**Failure mode.** Small-sample ρ is noise. Guard: ≥30 joint predictions per pair;
default ρ = 0.5 (pessimistic) until measured.

### 7. Pleiotropy-gated change control (glm, unique)
**Concept.** Evo-devo: high-pleiotropy genes (one gene, many traits) are strongly
conserved because mutating them breaks everything; evolution keeps modularity to
localize the damage.
**Mapping.** The trust ladder — currently trust classes are assigned by hand.
**Mechanism.** `pleiotropy.py`: consumer graph over the fleet's prompts/configs/scripts
(grep counts per instruction/claim/INDEX line/skill clause). Degree ≤ 2 → auto-safe;
3–9 → propose; ≥ 10 or INDEX-consumed → Josh gate + mandatory regression fixture. A
change touching ≥ 5 consumers must instead be proposed as a **module split** (localize
the pleiotropy).
**Kills.** "Small edit broke 7 agents"; Goodhart events whose blast radius nobody
measured. Turns the trust ladder from vibes into graph theory.
**Failure mode.** Runtime-constructed consumers are ungreppable. Guard: prompt-embedded
knowledge must reference INDEX paths; unknown consumers count as maximal pleiotropy
(conserved until shown otherwise — the evo-devo default).

### 8. AlphaEvolve loop + MAP-Elites archive + novelty circuit breaker (merged: deepseek + glm + research + adjudicator)
**Concept.** AlphaEvolve (DeepMind 2025): LLM mutation operator + real evaluator +
evolutionary archive → discovered better data-center scheduling and novel math.
MAP-Elites: best-per-cell over a behavior grid, not one elite — the stepping stones are
the value. Novelty search (Lehman/Stanley): when proxies get gamed, search for novelty
under minimal criteria.
**Mapping.** dreamer (mutation operator) × replay gym + canon fixtures (the mechanical
evaluator — the hard part, and the harness already HAS it) × `elites.jsonl` archive.
**Mechanism.** Descriptor axes: failure-class × loop-touched × blast-radius. Best-per-
cell retained even if globally outperformed; dreamer prompt gets the empty-cell list +
3 distant elites as cross-breeding context. **Circuit breaker:** when the outcome ledger
shows proxy/value divergence (Goodhart signature), harness-fix switches the objective to
novelty (maximize nearest-neighbor distance) subject to passing fixtures.
**Kills.** Self-improvement local optima; dreamer re-proposing the same patch class
nightly; recency-window learning (old ideas stay alive and recombinable).
**Failure mode.** Junk-drawer archive. Guard: per-cell quality floor; 90-day-unvisited
cells decay; axes reviewed quarterly.

---

## Tier 2 — strong, cheap, specific

9. **RG coarse-graining with decision-relevance + integration regret + cryptic variation
   bank** (3-way convergence, merged). Gardener's compaction test per item: *which
   next-level decision does this detail change?* None → integrated out to archive/ with
   a `micro: archive/x@commit` pointer (git keeps the microphysics). Repeatedly
   decision-changing items earn edit protection. New diagnostic: **integration regret** —
   when a failure needed a detail that was integrated out, count it; it tunes compaction
   aggressiveness. Composition with neutral theory (Kimura): banked detail is cryptic
   variation — on a novel failure class, search the bank FIRST, before fresh dreaming.
10. **Bet-hedging spore portfolio** (deepseek + glm merged). Geometric-mean objective
    per config; ε ≈ 10% of each agent's runs on off-policy models/prompt variants — the
    spore population. Spore-vs-dominant divergence is an early detector of
    dominant-config failure; when the dominant config fails, a live candidate exists.
    Guard: quarterly rotation, ε capped by cost-governor.
11. **Noether conservation audits** (adjudicator, unique). Every stated invariant → a
    nightly mechanical conservation check between two ledgers ("every prod write has a
    confirmation" → |prod mutations| − |confirmations| = 0). Generative: state a new
    symmetry, get a new audit for free. A symmetry check that can't run is itself a
    violation. Kills the VUA-revert class of invariant drift.
12. **Stabilizer syndrome checks** (deepseek + adjudicator). Per action-class, invariant
    questions with known answers run alongside fusion/knowledge jobs; a model's
    violation pattern = an error syndrome → per-class quarantine. Stabilizers rotate
    from evidence-verified claims; agreement is never ground truth.
13. **Affinity maturation** (deepseek + adjudicator, merged targets). Somatic
    hypermutation + selection applied to (a) high-usage claims (constrained grammar —
    scope/quantifiers only, never predicates) and (b) catching probes — when a failure
    class is caught, N probe variants are generated; variants that catch more of the
    class survive, autoreactive (false-positive) ones die. Canonize-failure becomes a
    maturation loop, not a single fixture.
14. **Quorum decay + quenching** (adjudicator, unique). Corroboration counts are
    autoinducers: add time-decay (old consensus shouldn't rule forever) and let a
    dissenter evidence-backed objection RESET the count to zero, not merely veto.
15. **VoI/EIG cortex scheduling** (glm + deepseek merged; glm's honesty flag stands —
    it's VoI in a Friston costume, and the docs should say so). Closed-form EIG over the
    claims ledger's Beta posteriors × consumer count from #7's graph − cost. Attention
    flows to load-bearing uncertainty by construction. Cap EIG-only actions per hour.
16. **Percolation audit** (deepseek). Weekly node-removal impact on the knowledge
    graph; enforced redundancy only for top-5% critical nodes; the rest rely on git.

## Tier 3 — named and flagged

- **CRDT/LWW merge for shared structured ledgers** (glm): per-field {value, lamport,
  agent} registers on JSONL/JSON shared files; prose stays on git + Josh. Conditional:
  build only if the race is observed — note the queue.jsonl whole-file-write race IS
  filed as latent, so the condition may already hold for that class.
- **QND two-of-three probes** (deepseek): no-two-hashes-agree = actuator noise, not
  drift. Folds mostly into next-10 #2. Corollary worth keeping: probe jobs count as load
  (the 65 mock-probe jobs estate-wide were the observer polluting the observed).
- **Zeno-cadence monitoring**: per-asset sweep rates from measured hazard rates. Blocked
  on Precursor Radar's 14-day history gate; revisit when hazards exist.
- **Seed-bank substrate diversity**: dormant fallbacks must live on DIFFERENT infra than
  the primary (the fleet-dead-2-days lesson). The viability drill exists (germination);
  the new rule is substrate diversity per critical loop.

## Killed in adjudication

- **Zeno checkpoints for long agents** (self-flagged by glm): "frequent cheap assertions
  + respawn" is fine engineering but not a physics import; next-10's probes cover it.
- **Tunneling/annealer for the launchd schedule**: real collision cluster (22:07–01:07)
  but cron jitter solves it for free; annealing is theater here.
- **Holographic INDEX / entanglement parity / criticality tuning**: fold into RG (#9),
  stabilizers (#12), or dropped as metaphor.
- **Evo-devo selector/enhancer YAML** (deepseek's #12, self-flagged): superseded by
  pleiotropy gating (#7), which is the same instinct with a measurable mechanism.

## Cross-pollination (physics × evolution, composed)

1. **RG × neutral theory → the cryptic variation bank** (glm): integrated-out detail is
   banked, not discarded; novel failure classes search the bank first; integration
   regret measures the payout rate.
2. **QEC × ratchet → recombination as decorrelation** (glm): before scaling fusion,
   decorrelate the panel — swap in a spore-pool model from a different training lineage;
   invariant: no κ > 0.5 pairs on one panel.
3. **Prescales × bet-hedging → the novel stream** (glm): the ε bandwidth premium keeps
   the unknown sampleable; the dreamer mines it to fill empty MAP-Elites cells.
4. **Ising/coincidence × affinity maturation** (deepseek): a social-alignment flag
   triggers evidence-only variant generation — replacing a social population with an
   evidence-selected one.
5. **Weismann barrier made explicit** (adjudicator): transcripts = soma (die with the
   session), playbooks/claims = germline. The auto-save rule is the barrier crossing —
   which makes the harness Lamarckian, which is exactly why #4 (ratchet guard) is
   load-bearing.

## Adjudicated ranking (leverage/cost)

1. **Trials factor** — one logged field + a monthly permutation script; honest epistemic
   pricing on everything the dreamer produces, forever.
2. **Fluctuation–dissipation gate** — ~50 lines; upgrades the entire measure→learn loop,
   not one component.
3. **Trigger hierarchy + prescales + minimum-bias + novel stream** — 4-way convergence;
   biggest cost win; the only top-tier item needing real plumbing.
4. **Ratchet + recombination** — the existential guard for a self-modifying system.
5. **N_eff + multimessenger independence** — the trust-measurement pair: fusion
   weighting and bus corroboration get honest independence accounting.
6. **Pleiotropy gating** — the trust ladder becomes measured blast radius.
7. **AlphaEvolve/QD archive** — highest ceiling; uniquely feasible here because the
   mechanical evaluator (replay gym + canon fixtures) already exists.

## Panel performance notes (for the fusion playbook)

- glm-5.3-flash needed 20k tokens on this prompt shape (12k exhausted on reasoning).
  When it lands, it lands — 4 unique top-tier ideas. Budget accordingly.
- deepseek-v4-pro answered fully at 12k in ~2 min; best speed/depth ratio again.
- kimi-k3 burned its whole budget on visible brainstorming at 6k (fireworks) and silent
  reasoning (baseten). For dense analytical prompts, kimi needs a hard "answer-first"
  instruction or a much bigger cap — its brainstorm did independently converge on the
  LHC trigger, so the capability is there behind the verbosity.

Nothing here is queued or filed — Josh picks; picks become proposals through the normal
/proposals path.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Harness wave-3 science review](reviews/harness-wave3-science-2026-10-11.md) — 2026-10-11 fusion (deepseek+glm+kimi-signal+adjudicator) for physics/QM/evolution ideas beyond waves 1-2: top tier = trials-factor null calibration for the dreamer, fluctuation-dissipation noise-floor gate on improvement claims, LHC trigger hierarchy w/ prescales+minimum-bias+novel stream, Muller's-ratchet recombination for the patch genome, multimessenger coincidence w/ systematics vetting for the bus, N_eff correlated-error accounting for fusion panels, pleiotropy-gated trust ladder, AlphaEvolve/QD archive; cross-pollinations (RG×neutral-theory cryptic-variation bank, QEC×ratchet panel decorrelation κ>0.5 rule, prescale×bet-hedging novel stream)