# Wave-3 dissenter pass — 11 proposals attacked before build (2026-10-11)

Scope: the 11 wave-3 proposal cards in `knowledge/dreams/proposals/2026-10-11-wave3-*.md`,
the parent analysis `knowledge/reviews/harness-wave3-science-2026-10-11.md`, and the build
authority `knowledge/scripts/wave3/CONTRACTS.md`. Ground truth: the live substrate
(`scripts/value-ledger.py`, `gossip-read.py`, `dream-mine.py`, `cost-governor.py`,
`replay-gym.py`, `synaptic-strength.py`, `titer-report.py`, `instruction-patch.py`,
`claims/claims.jsonl`, `models-evals/fusion.jsonl`, both predictions ledgers, fleet
launchd plists, `config/model-routing.json`, `dreams/GOSSIP.md`).

Method: steelman each card, then hit the load-bearing assumption. Every objection cites
file:line or a live incident. Verdicts: MATERIAL = spec must change before build;
MINOR = fix during build; CLEAR = survives as written.

---

## Cross-cutting findings (these hit multiple cards)

### X1 — CONTRACTS says "zero-LLM, none should be in wave 3"; three cards have LLM calls at their core
CONTRACTS.md global rules: "Zero-LLM by default; where an LLM call is unavoidable (none
should be in wave 3), stub it and note it." The parenthetical is wrong for this wave:
trials-factor's null miner ("run the dreamer's mining prompt on shuffled transcripts"),
trigger-hierarchy's L1 (cheap-model scoring) and L2 (dreamer/fusion analysis of the
bypass sample), and qd-archive's mutation operator (the dreamer) are all LLM calls.
Only qd's is free (it rides the existing nightly dreamer run). The specs never say which
calls are stubs, which the integrator wires, or where the token budget comes from.
Severity: MATERIAL wherever an acceptance criterion depends on the LLM half
(trials-factor, trigger-hierarchy); noted for qd-archive.

### X2 — Four cards measure with instruments that do not exist
The wave's pattern is "mechanism first, instrument never." Concretely:
- fusion-neff needs per-pair outcome labels; `models-evals/fusion.jsonl` (5 rows, all
  from 2026-10-11) carries ts/model/prompt_sha/tokens/error — **no verdict field**.
  The predictions ledgers (`dreams/predictions.jsonl`, `knowledge/predictions/predictions.jsonl`)
  are keyed by agent, not model.
- affinity-maturation needs per-class fire counts; `titer-report.py`'s own docstring:
  "the canon has NO last_fired... `found` is the DISCOVERY date, not the last occurrence,
  so real fire counts are unknown."
- spore-portfolio needs per-session returns; `cost-governor.py` docstring (lines ~14-16):
  "turn-usage lines carry in/out token counts but NO job/class/model attribution —
  instrumentation gap." The flywheel outcome ledger it searches for is "absent today."
- ratchet-recombination needs per-patch fitness; every available signal (Brier per agent,
  value-ledger hours, skill fitness) is per-agent or per-ticket, never per-prompt-clause.
Severity: MATERIAL on all four. The honest build order is instruments first; several of
these mechanisms become cheap config once the instruments exist.

### X3 — Three cards duplicate mechanisms the fleet already runs
- pleiotropy-gates builds a grep-based consumer/reference graph. `synaptic-strength.py`
  already computes per-file "inbound refs (distinct skills/*.md + INDEX.md files naming
  the basename)" plus reads/corroboration/claims joins, daily at 03:07. The card never
  cites it.
- coincidence-bus attacks the bus corroboration rule as "two agents DISCUSSING counts as
  corroboration." That defect was patched **today**: gossip-read.py lines 12-37 and the
  GOSSIP.md "Citation rule (2026-10-11)" — PATTERN now requires an evidence-bearing
  corroboration from a different agent (kind verify, or a finding with non-empty
  refs/evidence/detail); prose-only agreement renders OBS. The card's premise paragraph
  is attacking a corpse.
- spore-portfolio adds a third routing authority beside `config/model-routing.json`
  ("The cortex proposes table CHANGES; Josh approves them") and cost-governor's routing
  proposals to the cortex attention queue. Precedence between the three is undefined.
Severity: MATERIAL (each spec must state its relationship to the incumbent).

### X4 — The two-predictions-ledger trap
`knowledge/dreams/predictions.jsonl` (predict.py, the predict-then-check protocol) and
`knowledge/predictions/predictions.jsonl` (brier-resolve.py's calibration ledger) are
different stores with different schemas. Cards that say "prediction ledger" (fusion-neff,
ratchet) without naming which one will be built against the wrong one or both.
Severity: MINOR globally; MATERIAL where the data itself is missing (fusion-neff).

---

## Card 1 — trials-factor

**Steelman.** The dreamer must surface something nightly; best-of-N over hundreds of
candidate patterns guarantees confabulation at a calculable rate. A permutation null is
the correct cure — calibrate the max-statistic on data where no real pattern exists.
Ranked #1 leverage/cost by the adjudicator. I agree with the science completely.

**Objections.**

1. MATERIAL — **The dreamer has no score to calibrate.** The mechanism requires a
   max-statistic: "record the max-score distribution," "if nothing beats the null." Dream
   reports are prose (see dreams/2026-10-10.md: "What Josh worked on," "Corrections,"
   "Repeats") — there is no per-pattern numeric score field anywhere in the dreamer
   pipeline. Acceptance criterion ">=1 real dreamer pattern retroactively fails the null
   bar" is unexecutable: no real pattern carries a score to compare against a null
   distribution. The builder will invent a scoring interface ad hoc.
2. MATERIAL — **The specced null runner violates the build contract and is unbudgeted.**
   "Run the dreamer's mining prompt on time-shuffled transcripts" is an LLM call — five
   of them, monthly, at dreamer scale (the wave-3 fusion run shows glm needing 20k
   tokens per dense answer; the dreamer reads a 3-day, 30MB/file corpus). CONTRACTS says
   zero-LLM "none should be in wave 3." No cost line exists for this anywhere.
3. MATERIAL (with a cheap fix that makes the card stronger) — **The enumerable layer
   already exists and the card doesn't use it.** `dream-mine.py` is the dreamer's
   mechanical mining core: stdlib, read-only, emits corrections, error strings (top 25
   with counts), and 4-gram tool sequences (>= 3 occurrences) — every one an ENUMERABLE
   candidate with a count, which is exactly what "candidates_examined: N where the search
   genuinely enumerates" asks for. A permutation null over shuffled transcripts through
   dream-mine.py is fully stdlib, contract-clean, and retro-runnable against history
   (acceptance criterion 2 becomes executable tonight). The LLM-layer null (prose
   patterns) can be a later phase with an explicit budget.
4. MINOR — **Permutation granularity is unspecified and changes the answer.** Turn-level
   shuffle destroys conversational coherence (the null corpus becomes semantic garbage
   the miner finds little in — biasing the null LOW and making real patterns look more
   significant); session-intact day-swap preserves everything except cross-day
   repetition. The card says "time-shuffled" without picking. The permutation must
   destroy only the structure the statistic is sensitive to.

**Exact spec changes:** (a) define the statistic — dream-mine digest counts (max ngram
frequency, top error-string count) as the wave-3 null target; LLM-prose null deferred
with an explicit monthly token budget if wanted; (b) pin permutation to session-intact
day-swap; (c) acceptance 2 becomes "re-mine >=5 historical shuffled corpora through
dream-mine.py; >=1 real historical digest statistic fails the null bar."

**Verdict: MATERIAL.** The #1 ranking survives the respec — arguably improves, because
the mechanical version is cheaper than the card's own 2h estimate and contract-legal.

---

## Card 2 — fdt-gate

**Steelman.** You cannot claim a causal improvement smaller than the metric's noise
floor; booking those claims as value is improvement theater. A ~50-line MAD-based gate
is the best leverage/cost ratio in the wave after trials-factor. The self-audit clause
(evidence agent audits the gate monthly) is exactly right.

**Objections.**

1. MATERIAL — **The contracted insertion point contains no claims the gate can evaluate.**
   The card: "the value ledger books ZERO with 'within noise floor.'" CONTRACTS integrator:
   "fdt-gate (hook into value-ledger derive)." But value-ledger.py `derive()` (lines
   146-232) never processes a "change X improved metric M by δ" claim — it appends rows
   with CONSTANT heuristic hours per outcome class (lines 53-62: ticket_fixed=2.0h,
   capability_built=4.0h). There is no δ, no pre-change history, no metric series. A gate
   on the derive path gates nothing. The harness's actual δ-claims live in dream reports
   and proposal EV math ("+8h/quarter," "p_accept est 0.8") — prose estimates with no
   measured M. So the gate's real first job is DEFINING the claim format (improvement
   claims must name metric, pre-window, post-window) and the metric series it reads
   (Brier calibration reports in knowledge/predictions/, skill-fitness invocations,
   heartbeat pass rates — all real, all stationary enough to σ). The spec must name them.
2. MATERIAL — **Acceptance criterion 1 is impossible as written.** "One real historical
   improvement claim retroactively books zero" presumes historical δ-claims exist in a
   machine-readable form. They do not (objection 1). Also, "retroactively books zero" in
   an append-only JSONL regime (CONTRACTS: append-only, atomic) means appending a
   compensating verdict row, not rewriting — the spec should say so.
3. MINOR — The evidence agent's monthly audit needs a schedule; memory notes the
   evidence plist landed (00:53 daily), so wire the audit into it explicitly or the
   self-audit clause is dead text.
4. Goodhart note (in the card's favor): flagging high-σ metrics as bad instruments makes
   noisy proxies unrewarding — this is the rare metric that gets MORE honest when gamed.
   Approved as designed.

**Exact spec changes:** retarget from "value-ledger derive" to (a) a claim-format
contract on dream/proposal improvement claims + (b) a scorer over named series
(predictions calibration, skill-fitness, heartbeat); acceptance 1 becomes "one real
historical EV claim from a dream report or proposal re-scored against the named series
and correctly flagged within-noise or supported"; add compensating-row semantics.

**Verdict: MATERIAL.** Mechanism sound; the spec aims it at a stream that doesn't exist.

---

## Card 3 — trigger-hierarchy

**Steelman.** Prescales with recorded factors, a minimum-bias sample, and a prescale-1
novel stream are the correct import — the 4-way convergence is deserved. The
false-negative hole is real: nobody measures what the attention layer misses.

**Objections.**

1. MATERIAL — **The card never names the stream, and under both readings something
   breaks.** Read one: the trigger prescales the dreamer's input ("L2: full
   dreamer/fusion on top-N L1 survivors"). The dreamer's "Repeats and skill candidates"
   section (dreams/2026-10-10.md: "Bash>Bash>Bash>job_get x36") IS an unfolded-rate
   analysis over full-corpus transcripts; prescaling "boring classes" 1/N before the
   miner sees them degrades the repeats signal proportionally — and you cannot unfold
   prose. Read two: the trigger sits only on the bus/cortex attention path and the
   dreamer keeps mining raw transcripts via dream-mine.py — then the trigger saves
   nothing, because the dreamer run IS the frontier spend on repetitive events and it
   still runs full-corpus. The card's EV ("largest cost win of the set") names no spend
   it cuts: fusion is already P0-gated (rare), the dreamer is one bounded nightly run,
   cortex pulses read digests. Pick the stream, then re-derive the EV.
2. MATERIAL — **L1 and L2 are LLM calls; CONTRACTS assumes none.** Acceptance criteria 2
   ("trigger-efficiency report from the bypass sample") and 3 (">=1 novel-stream event
   reached L2") both require L2 wired — that's a dreamer prompt change, which CONTRACTS
   reserves to the integrator and the card doesn't budget. In wave 3 as contracted, only
   L0 + the novel stream + the bypass ledger are buildable; say so.
3. MATERIAL — **The minimum-bias sample is empty at fleet event volumes.** "0.1–1%
   random bypass" — the bus sees tens of events/day, so 1% is ZERO events most days. At
   the LHC, 1% is millions. The bypass needs a count floor (e.g., >= 3 events/day chosen
   uniformly), not a percentage, or acceptance criterion 2 has no sample to estimate
   leakage from.
4. MINOR — Cold start: "events matching no known L0 class → novel stream." On day one
   every class is unknown, so the novel stream is the entire firehose and the rate bound
   silently drops genuinely novel events. Ship with permissive seed classes.
5. MINOR — "Never prescale prod-touching or P0-citing events" needs the express line
   implemented as a deny-list checked BEFORE class assignment, not after — otherwise a
   misclassified P0 event gets prescaled out and the failure mode the card kills
   (invisible blind spots) recurs in the worst place.

**Exact spec changes:** name the input stream (bus events + cortex attention candidates;
dreamer transcript mining explicitly out of scope, full-corpus forever); wave-3 scope =
L0 + novel stream + bypass ledger with a >=3/day floor; L1/L2 stubbed with an integrator
wiring note; drop or re-derive the cost-win EV against a named spend line.

**Verdict: MATERIAL.** Build the L0/novel/bypass third now; the rest after the stream
question is answered.

---

## Card 4 — ratchet-recombination

**Steelman.** A Lamarckian self-modifying system with additive-only canonization will
accumulate cruft irreversibly; recombination-with-re-earning is the correct guard, and
"dormant, never deleted" plus "purge needs harm-evidence or 7-day window" makes the
worst case reversible. The Weismann framing is earned, not decorative.

**Objections.**

1. MATERIAL — **No oracle exists that can tell whether a prompt clause "re-earns its
   place."** The mechanism: "each clause must re-earn its place against the regression
   fixture suite." The fixture suites that exist test RECIPES (wt testcases, canon
   fixtures like the ruby-eval entry in canon.jsonl) and HARNESS INVARIANTS
   (replay-gym.py, read-only replays). Neither evaluates a prompt clause. The guards
   that matter most behaviorally ("never end a turn announcing intent," voice rules) are
   only observable in live sessions; replay-gym cannot see them. Acceptance criterion 2
   ("a clause fails the fixture suite and is dropped to dormant") is unfalsifiable as
   written — the builder must invent a clause→check mapping the spec should have
   provided. Some clauses ARE mechanically checkable (grep-lints, hook-enforced rules),
   so the fix is an explicit per-clause-class oracle registry: lint-checked,
   replay-checked, human-reviewed. Without it, recombination systematically purges
   exactly the rare-regime behavioral guards it claims to protect (dormancy mitigates,
   and most constitutional guards are hook/config-backed — never_auto in
   dreams/config.json is enforced, not prompt-resident — so this is MATERIAL, not
   fatal).
2. MATERIAL — **"Fitness window per patch" attributes signals that don't exist at patch
   granularity.** Brier is per-agent (brier-resolve over knowledge/predictions/), value
   is per-ticket heuristics (value-ledger.py), skill fitness is per-skill
   (skill-fitness.py). None resolves to a clause or patch. The genome can record lineage
   honestly (instruction-patch.py already logs applied.jsonl; the queue exists), but the
   fitness join must be per-target-file over a window, not per-patch — or the ratchet
   counter fires on measurement absence, not on harm. Goodhart corollary: insurance
   patches (guards against rare catastrophes) always show "no measured benefit" and
   march to the front of the recombination queue. Dormant-not-deleted is the only thing
   standing between this metric and a slow-motion purge of the fleet's immune system;
   the spec should add a never-recombine class (never_auto, hook-backed guards).
3. MINOR — "Captures 100% of instruction-patch queue writes" is honest (the queue is
   real), but the wider claim "every patch to prompts/routing/agent configs" overreaches:
   most prompt edits bypass the queue entirely (direct edits, kit syncs, mods-deploy).
   Scope the genome to queue writes + git-observable diffs and say so.

**Exact spec changes:** ship items 1-2 (genome ledger + ratchet counter, report-only) as
specced; gate item 3 (recombination) behind an oracle registry mapping each clause class
to lint / replay-gym invariant / human review; fitness join per-target-file; add
never-recombine class for config/hook-enforced guards.

**Verdict: MATERIAL.** Items 1-2 buildable today; the recombination half needs the
oracle registry written first.

---

## Card 5 — coincidence-bus

**Steelman.** Independence accounting for corroboration — channels sharing an upstream
systematic count once, joint significance from per-channel background rates — is the
right import and the dependency registry is genuinely new capability.

**Objections.**

1. MATERIAL — **The ±10-minute window never fires for the fleet's actual channels.**
   Cadences from launchd: watchdog daily 23:13, gardener daily 22:43, docs-watch daily
   22:31, evidence daily 00:53, dreamer daily 23:43, kb-audit 3x/day, cortex hourly.
   Two independent channels observing the same condition post HOURS apart (watchdog →
   evidence is 100 minutes; gardener → evidence 130). A ±10-min coincidence window
   structurally cannot produce a multi-group coincidence between the daily channels —
   the mechanism is dead for exactly the incident class the card cites (fleet-dead-2-days,
   caught by channels on different schedules). In GW terms: the coincidence window must
   be set by the slower channel's time resolution. Make the window per-channel-cadence-aware
   (e.g., max(±10min, channel period)) with λ computed on the same window, or the joint
   significance is calibrated for a streaming system this fleet is not.
2. MATERIAL — **Internal contradiction: read-only vs auto-escalate.** "Multi-GROUP
   coincidences auto-escalate one rung on the trust ladder" is a write into Josh's
   trust governance; "Rollback: matcher is read-only over existing bus JSONL; off =
   current behavior" and CONTRACTS ("FORBIDDEN: editing gossip-read.py — emit a patch
   note") say it can't. The builder cannot satisfy both. Pick: advisory scorer emitting
   a patch note (my read of the contract's intent), with auto-escalation as a separate
   Josh-gated follow-up.
3. MINOR — **Stale premise.** "Bus corroboration counts two agents DISCUSSING as
   corroboration" was patched today (gossip-read.py:12-37; GOSSIP.md citation rule
   2026-10-11: PATTERN requires evidence-bearing corroboration from a different agent).
   The card's remaining delta — the dependency registry and λ joint significance — is
   real, but the spec should be re-grounded so the builder doesn't "fix" a rule that
   was already fixed and possibly re-open it.
4. MINOR — Goodhart/cold-start: the registry is hand-curated; new agents (librarian
   joined today) default to no upstream edges = counted independent = free corroboration.
   Default unregistered channels to "unvetted — cannot escalate" until registered.
   λ from 4 days of sparse bus history will be noise for weeks; scoring is advisory, so
   tolerable — log the confidence interval with the score.

**Exact spec changes:** cadence-aware window; advisory-only in wave 3 (escalation as a
patch note to Josh); re-ground the premise paragraph on the post-2026-10-11 tally;
unregistered-channel default.

**Verdict: MATERIAL.**

---

## Card 6 — fusion-neff

**Steelman.** N_eff = N/(1+(N−1)ρ̄) is the correct accounting; the kimi-family
unanimous-wrong incident is the exact failure; defaulting to pessimism (ρ=0.5 until
measured) is the right posture for weights.

**Objections.**

1. MATERIAL — **The data source does not exist and cannot accumulate on the cited
   timescale.** "Pairwise co-failure rates from prediction history": fusion.jsonl (5
   rows, all today) has no outcome/verdict field — it logs ts, model, prompt_sha,
   tokens, errors. The predictions ledgers are agent-keyed, not model-keyed. So there
   are ZERO labeled joint predictions today, and fusion is P0-gated (the fusion skill:
   invoked only for hard-to-reverse + costly-wrong + subtle) — call it a handful of
   panels per month. ">=30 joint predictions per pair" is many months away per pair.
   Acceptance criterion 1 is unachievable in any reviewable window.
2. MATERIAL — **The pessimistic default + invariant make every panel illegal, including
   Josh's explicit invocations.** Unknown pairs default ρ=0.5 → a 3-model panel has
   N_eff = 1.5 < 2 → policy refuses fusion; "no two models with κ > 0.5 on one panel"
   with unmeasured κ treated as 0.5 → every unmeasured pair violates the invariant. The
   fusion skill is Josh's tool with his invocation policy (P0 gate +
   domains/model-gateway-playbook.md). A policy script that silently downgrades his
   explicit fusion call to "one model + evidence agent" inverts authority. Explicit
   invocation must override the policy (log the N_eff, never block).
3. MATERIAL — **Acceptance criterion 2 contradicts the rollback posture.** "One panel
   configuration rejected or reweighted by the κ > 0.5 rule" requires enforcement ON;
   "Rollback: advisory at first (log-only); enforcement flag off = current behavior"
   requires it OFF. With no data (objection 1), enforcement-on means rejecting panels on
   defaulted, unmeasured κ — enforcement of a guess.
4. MINOR — Goodhart/identity-laundering: κ history keyed on display names resets when a
   provider renames or fine-tunes a model. Pin the family registry to provider+checkpoint,
   curated, not self-declared. And state the cheaper-first rule the incident actually
   justifies: never put two same-family models on one panel — that rule needs NO
   measurement and would have caught the kimi incident; the κ table refines it later.

**Exact spec changes:** wave-3 scope = instrument (add outcome + panel-composition
fields to fusion.jsonl going forward) + fusion_policy.py log-only with the static
family-diversity check live; explicit-invocation override; acceptance 2 resequenced
behind ">=30 labeled joints per pair," criterion rewritten as "one panel's N_eff
computed and logged with the family-diversity check firing on a synthetic pair."

**Verdict: MATERIAL.** Build the instrument and the static rule now; the κ machinery
earns enforcement only after data exists.

---

## Card 7 — pleiotropy-gates

**Steelman.** Trust rungs assigned by hand is true; blast radius measured as consumer
degree is the right axis; read-only scoring first with enforcement behind a flag is the
right posture; "uncountable consumers = maximal pleiotropy" is the honest default.

**Objections.**

1. MATERIAL — **Rule 3 (module-split mandate) blocks shared-library bugfixes.** "A
   change touching >= 5 consumers must be proposed as a module split instead." CONTRACTS
   orders every wave-3 script to import `atomic_io.py`; it is already imported across
   the scripts/ tree (value-ledger, instruction-patch, titer-report, synaptic-strength…
   20+ consumers). By rule 3, a bugfix to atomic_io — the exact file whose absence cost
   queue.jsonl 49 decisions — cannot be proposed as a bugfix; it must be proposed as a
   "module split," which is incoherent for fixing a shared primitive. The rule confuses
   change-in-interface (dangerous at high degree, gate hard) with
   change-in-implementation-behind-a-stable-interface (the whole point of a library).
   Exempt interface-stable bugfixes; trigger the module-split mandate only when the
   change alters the consumed contract.
2. MATERIAL — **Unstated relationship to synaptic-strength.py.** A per-file
   inbound-reference graph over the knowledge tree already exists and runs daily
   (03:07): synaptic-strength.py joins inbound refs from skills/*.md + INDEX.md with
   reads, bus corroboration, and claims. pleiotropy.py would be a second, finer-grained
   (per-line) reference graph. Fine if deliberate — but the spec must say "extends
   synaptic-strength to per-clause granularity" or "replaces," or the fleet ends up with
   two graphs that disagree about the same tree with no arbiter.
3. MINOR — Grep counts text mentions, not consumers: paraphrased embeddings of a rule
   (agents' .md files are hand-edited prose) under-count; comments over-count. The
   card's own acceptance (spot-check 5 high-fanout items against intuition) is the right
   calibration step — keep it, and publish the false-positive/negative rate from the
   spot check in the report.
4. MINOR — Goodhart: consumer-count as blast radius is gameable by inlining shared code
   (reduces counted degree while increasing real coupling). The count is a floor for
   risk, not a ceiling — say so in the report header.

**Exact spec changes:** amend rule 3 with the interface-stability exemption; add a
paragraph stating the synaptic-strength relationship; publish spot-check error rates.

**Verdict: MATERIAL** (narrow — the graph itself is buildable as specced; rule 3 must
be fixed before the enforcement flag ever flips, and the duplication must be
acknowledged in the spec).

---

## Card 8 — qd-archive

**Steelman.** MAP-Elites over (failure-class × loop-touched × blast-radius), best-per-cell,
mutation operator riding the existing nightly dreamer (no new LLM spend), novelty
circuit breaker on Goodhart divergence — the highest-ceiling card, and the ONLY one whose
framing correctly identifies the evaluator as the hard part.

**Objections.**

1. MATERIAL — **"The mechanical evaluator already exists" is false at the granularity
   the mechanism needs.** replay-gym.py is a read-only INVARIANT checker (replays
   yesterday's activity as assertions) plus a fire drill; canon fixtures are pass/fail
   per failure class; wt testcases test recipes. These answer "did this variant BREAK
   something?" — one bit. MAP-Elites needs comparative FITNESS per cell to select
   best-per-cell, and the card's fitness = "Brier improvement + value-ledger impact +
   P(accept)" is three lagging signals none of which attributes to a variant: Brier is
   per-agent, value-ledger hours are per-ticket heuristic constants, P(accept) is the
   dreamer's SELF-ESTIMATE (every wave-3 card carries "p_accept est 0.75-0.85" — a
   compressed range). Selecting on self-estimated accept probability breeds
   high-self-esteem variants — the archive fills with confident junk, which is the
   card's own named failure mode ("junk-drawer archive") arriving through the fitness
   function instead of the door.
2. MATERIAL — **The variant artifact class is never pinned.** "Propose → fixture
   evaluation → cell update" — a variant of WHAT? If variants are prompt/patch text, no
   fixture evaluates them (see ratchet objection 1). If variants are machine-benchmarkable
   artifacts (miner thresholds, trigger-menu classes, lint rules, spore configs), the
   replay gym + labeled corpora CAN score them and the whole card works. The spec must
   pin the artifact class, or builders will file dreamer prose proposals into the grid
   and call them elites.
3. MINOR — Cross-card dependency: item 5 (dreamer mines novel_stream.jsonl) depends on
   Agent C's trigger card shipping the stream — soft (acceptance doesn't require it),
   but the integrator should wire it only after both land.
4. MINOR — "Cells unvisited 90 days decay out" interacts badly with the archive's own
   purpose (stepping stones for rare regimes): the most valuable cell is the one for the
   failure class that hasn't happened yet. Decay on visit-count punishes foresight.
   Decay on re-evaluation-failure instead.

**Exact spec changes:** pin variants to machine-benchmarkable artifact classes (list
them); redefine fitness as (fixtures pass) × (cost delta) × (novelty distance) with
Brier/value as long-horizon CONFIRMATION signals, not selection signals; drop P(accept)
from fitness entirely; decay on re-eval failure.

**Verdict: MATERIAL.**

---

## Card 9 — cryptic-variation-bank

**Steelman.** Coarse-graining alone says discard; neutral theory says most variation is
regime-neutral; the composition justifies banking. Integration regret as the tuning
signal is honest. The CONTRACTS already defused the dangerous half: "the bank COPIES,
never moves; coarse-graining runs in dry-run report mode only on first build" and
"FORBIDDEN: editing any domain file."

**Objections.**

1. MINOR — **Spec/contract mismatch on acceptance.** "One full coarse-graining pass with
   >=3 details integrated out, pointers verified resolvable" requires actual moves; the
   contract forbids them in build 1 (dry-run + copy-only). Reword to "dry-run report
   names >=3 integration candidates over one domain file; copy-path + pointer format
   demonstrated on one synthetic item."
2. MINOR — **The bank must stay inside the search surface or banking = burial.**
   brain_search covers domains/projects/claims/dream-reports; a new knowledge/archive/
   tree may fall outside the indexed surface, and the RAG KB doesn't index the knowledge
   tree at all. "On a novel failure class, FIRST search the bank" fails silently if the
   bank is invisible to the searchers. Add an acceptance line: the bank path is in
   brain_search's indexed surface and in the dreamer/gardener read lists.
3. MINOR — Degenerate equilibrium: banking everything drives integration regret to zero,
   which tunes compaction aggressiveness to zero, which bloats. The compaction test is
   the only brake; the regret tuner needs a floor (aggressiveness never drops below the
   current rate) or a regret-rate denominator (regrets per integrated item, not absolute).
4. Note (not an objection): the fattest real target — workato-platform.md at 6.6x size
   budget — is untouchable in build 1 by the contract's domain-file edit ban. Correct
   staging, but the report should name it as the first real candidate for build 2.

**Verdict: MINOR.** The card survives; build as contracted with the three annotations.

---

## Card 10 — spore-portfolio

**Steelman.** Monoculture fragility is real (one gateway regression degrades the whole
fleet identically); a small ε of off-policy runs is cheap insurance; spore-vs-dominant
divergence as an early-warning signal is a genuinely good detector idea.

**Objections.**

1. MATERIAL — **Item 2 (geometric-mean objective) targets a data series that does not
   exist.** "Geometric mean of per-session returns (value − cost)." cost-governor.py's
   own docstring: turn-usage lines carry token counts "but NO job/class/model
   attribution — instrumentation gap"; the flywheel outcome ledger it searches for is
   "absent today." There is no per-session return series to take a mean of. And
   "floored so logs exist" breaks the economics: flooring negative returns at ε makes a
   catastrophic session equal to a negligible one, and GM over floored values prefers
   consistently-mediocre over occasionally-brilliant — punishing exactly the variance
   bet-hedging exists to protect. Delete item 2 from wave 3; revisit when per-session
   attribution lands (it's already on cost-governor's own proposal list).
2. MATERIAL — **Third routing authority with undefined precedence and no owner for the
   enforcement point.** Routing today: config/model-routing.json ("The cortex proposes
   table CHANGES; Josh approves them") plus cost-governor's proposals. spores.json would
   be a third. Worse, the contracts give Agent D spore-router.py + spores.json and a
   patch note — but the enforcement point is the job-invocation path (run-job.sh /
   agent frontmatter model pins), which NO wave-3 agent owns and the integrator's plist
   wiring doesn't cover. As contracted, the ε router is a wrapper nothing calls.
3. MINOR — "ε ≈ 10% of non-prod runs" needs the spore rows distinguishable in the
   outcome ledger — feasible and the acceptance criterion is honest — but at fleet
   volumes (~30 jobs/day), 10% is ~3 runs/day spread across agent classes; divergence
   detection on n≈3/day will cry wolf weekly. Set the divergence alarm on a trailing
   window (>= 30 spore runs) and say so.

**Exact spec changes:** delete item 2; name the enforcement point (spore-router as a
run-job.sh wrapper, integrator wires one plist pair as proof) and precedence
(spores.json may only select among configs already present in model-routing.json);
divergence alarm on trailing >=30 spore runs.

**Verdict: MATERIAL.**

---

## Card 11 — affinity-maturation

**Steelman.** Detectors that caught something should get sharper, not just kept; a
constrained mutation grammar (scope/quantifiers only, never the predicate) is the right
safety shape; never_auto claims stay Josh-gated. The cross-pollination hook
(social-alignment flag → evidence-only variant generation) is the best idea in the card.

**Objections.**

1. MATERIAL — **The "constrained grammar" has nothing to bind to.** Claims in
   claims.jsonl are prose: {id, subject, claim (prose), evidence, confidence,
   asserted_at, last_verified, status}. There are no structured scope/quantifier/
   threshold/time-window fields to mutate. Mechanical mutation of prose ("30 days" →
   "14 days" by regex) is fragile parody of the grammar the card describes. And
   "high-usage claims" — no usage counter exists on claims (synaptic-strength tracks
   FILE reads, not claim usage). The spec must first add structured fields to the claim
   schema (scope, quantifiers, thresholds, windows — opt-in per claim) or the mutator
   generates garbage variants of free text.
2. MATERIAL — **"Keep variants that catch MORE of the class" is unmeasurable: one
   fixture per class, and fire counts unknown.** The card itself states the cause:
   "Canonize-failure adds ONE fixture per failure class." Selection on n=1 means any
   variant that relaxes the parent "catches more" by construction until the
   autoreactive screen — and the autoreactive (false-positive) screen needs NEGATIVE
   fixtures per class, which also don't exist. titer-report.py's docstring confirms the
   deeper gap: "the canon has NO last_fired... real fire counts are unknown." Acceptance
   criterion 2 ("variant catches a fixture sub-case the parent missed") presumes
   sub-case corpora that nobody is scoped to build. The instrument comes first: per-class
   occurrence logging + sub-case/negative fixture corpora; the maturation loop is wave-4
   work on top of it.
3. MINOR — Cheaper alternative that captures most of the value now: when a failure class
   recurs with a new instance, canonize-failure already appends the instance; making the
   class's fixture SET the selection corpus (grow sub-cases per class, track which
   fixture variant catches which sub-case) is 80% of maturation with zero new machinery.

**Exact spec changes:** wave-3 scope = (a) claim-schema extension with structured
scope/quantifier fields for NEW claims, (b) per-class occurrence/fire-count logging in
the canon, (c) sub-case + negative fixture corpora conventions; defer the mutation/
selection loop to wave 4, or restrict it to probe thresholds (numeric, mechanically
mutable) over classes that have >= 3 sub-cases.

**Verdict: MATERIAL.**

---

## Overall verdict

**No card is fatal.** The science imports are mostly excellent — trials-factor, fdt-gate,
and N_eff are genuinely the right physics, and cryptic-variation-bank survives nearly
clean. The wave's systemic defect is interface-level: specs written against an idealized
substrate (per-pattern scores, outcome-labeled fusion history, per-class fire counts,
per-session returns, per-clause fitness oracles) that the real substrate doesn't have.
X2 is the meta-lesson: four of eleven cards are mechanisms waiting on instruments, and
in every case the instrument is cheap and the mechanism becomes config once it exists.

**Safe to build in parallel exactly as contracted:** cryptic-variation-bank (MINOR
annotations only).

**Safe to build in parallel AFTER the one-paragraph spec amendments above** (none
requires re-dreaming; each is a targeted edit):
- trials-factor — rescope null to dream-mine.py digests (gets cheaper AND contract-legal)
- fdt-gate — retarget insertion point + define the claim format
- trigger-hierarchy — name the stream; L0 + novel stream + bypass floor only
- ratchet-recombination — items 1-2 now; oracle registry before recombination
- coincidence-bus — cadence-aware window + advisory-only + re-grounded premise
- fusion-neff — instrument + static family-diversity rule now; κ enforcement after data
- pleiotropy-gates — rule-3 interface-stability exemption + synaptic-strength paragraph
- qd-archive — pin variant artifact class; honest fitness (drop P(accept))
- spore-portfolio — delete item 2; name enforcement point + precedence
- affinity-maturation — instruments first (schema fields, fire counts, sub-case corpora)

**Contract-level notes for the integrator (no ownership collisions found):** file
ownership is disjoint across Agents A-D. Two naming nits: `knowledge/dreams/calibration/`
already exists (contains 2026-10-08-calibration.md — Agent A adds to it, doesn't create
it); `knowledge/bus/` (motifs) vs `knowledge/dreams/bus/` (maildirs) — Agent C's
channels-registry.jsonl lands in the former; fine, but say so in the build report.
Cross-card soft dependencies (qd←trigger novel stream; affinity←coincidence social flag;
fusion←spore decorrelation pool) are all integrator-wiring, no build-order constraint.

**What I could not break:** cryptic-variation-bank's core mechanism — banked detail with
regret tuning under a copy-only, dry-run-first contract is honest, reversible, and
correctly scoped. Steel manned; only annotations survive.

Nothing unverified in this review: every substrate claim above was read from the live
file today (value-ledger.py, gossip-read.py, dream-mine.py, cost-governor.py,
replay-gym.py, synaptic-strength.py, titer-report.py, claims.jsonl, fusion.jsonl, both
predictions ledgers, model-routing.json, GOSSIP.md, launchd plists). What I did NOT do:
run any of the proposed scripts (they don't exist), or verify the wave-1 CONTRACTS
precedent beyond the wave-3 contract's own text.
