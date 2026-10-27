# Position: rules settle, context judges, models last

Status: REVISED after dissenter pass (2026-10-25, verdict SHIP-WITH-CHANGES).
Filed on the librarian/2026-10-25 branch; moves to main only after Josh
approves.

## The position

When a house surface has to make judgment calls over Josh-taste text
classification (triage verdicts, routing of verdict-like decisions, quality
grades over written state), the investment order the evidence supports is:
settle what rules can settle FIRST, assemble state and retrieve precedent
SECOND, upgrade the model LAST. On the one surface measured end-to-end, the
biggest model-side accuracy lever ever recorded was retrieval of Josh's own
prior verdicts, and no model swap came close. All measured configurations
still failed the house ship gate, so nothing here licenses automated
filtering.

Scope: this position is measured on ONE domain (Jira triage verdicts, single
rater, residue n=48). It is stated for Josh-taste text-classification
surfaces and should NOT be read as covering perception, novel reasoning, or
deterministic-by-architecture surfaces (the GWS semantic gateway never runs a
taste judge and needs none).

## The evidence (numbers as the ledgers support them)

1. Jev iteration 4 (2026-10-24, `scripts/backtest-jevish4.py`): on a 48-row
   residue (22 accepted, 54.2 percent reject), flash + precedents scored
   0.625 against a 0.542 always-reject baseline; flash alone scored 0.25,
   BELOW the trivial baseline. Kimi, a pricier model (about 14x input price
   by the script's own price table), scored 0.35; CoT 0.38. The equal-model,
   equal-rows 0.25 to 0.62 delta is ledger-verified and is larger than any
   model-swap delta measured on this surface. Honest reading: part of the
   +37 is context helping; part is the flash-alone arm being badly
   miscalibrated on this prompt. Direction survives, magnitude is qualified.
2. Iteration 3 (2026-10-23, `scripts/triage-state.py`): state assembly alone
   lifted the single judge 0.61 to 0.71, crossing the 0.63 majority baseline.
   Mechanism understood: the blindness was CORRELATED across voters (19 of 50
   rejected rows got unanimous true votes in spike 1), which is why the
   ensemble failed (0.49) while state worked.
3. The empirical FIRST lever was a rule, not a model or a retrieval: the
   one-line source rule scored 0.81 (iteration 3), beating every cascade
   (best 0.77). The arc's final architecture encodes the true ordering:
   conservative rules settle where near-certain, the judge with state and
   precedents handles the residue, calibration next, Josh last.
4. Urgency resisted everything: inverted in 8 of 8 configurations across
   three backtests, including every model class tried. A text-level judgment
   ("loud equals urgent") is anchor-level, not information-level. There are
   judgments the model choice CANNOT fix, only the state design can.
5. The decisions engine UAT (2026-10-14): two judge models scored 0.25-0.36
   against Josh's real verdicts; model swapping changed nothing material. The
   dissenter's verdict then (context-blind labels) predicted exactly what
   iterations 3 and 4 proved.

## What this commits the house to (doctrine, not hooks)

These are doctrine commitments pending a Josh decision on enforcement; none
is wired as a hook or gate as of 2026-10-25.

- New judgment surfaces get a state-assembly design review before any model
  selection debate: what settles by rule, what does the judge see, where do
  precedents come from, what is the judgmental residue.
- Model upgrades on EXISTING judgment surfaces require a backtest delta
  against the incumbent at equal context. On NEW surfaces (no verdict ledger
  yet) the arc's own playbook applies: cold-start domains stay order-only by
  design, and judging happens shadow until a ledger exists to gate on.
- Cost comparisons quote the full stack (model plus context assembly), using
  only figures traceable to a script, ledger, or invoice. The house's own
  retrieval machinery (precedent.py, stdlib BM25) costs zero model tokens;
  claims must match that shape of evidence.

## Falsification conditions (one is live, not hypothetical)

- A judgment surface where a model upgrade closed a gap that rules plus state
  could not (a capability gap, not a knowledge gap). Untested here.
- Stale-precedent poisoning is LIVE in the shipped wiring, not hypothetical:
  33 of 48 reason-coded verdicts in `knowledge/triage/verdict-reasons.jsonl`
  are "stale"; `precedent.py` excludes future rows only and applies no
  recency weighting, TTL, or decay, so any past-regime verdict is retrievable;
  doctrine drifted across the arc (severity to decay urgency, reason codes),
  so the 413-row index encodes superseded taste; and the KB digest system
  already had to engineer freshness machinery against this exact mechanism.
  If shadow-judge accuracy degrades as doctrine evolves, this is the prime
  suspect. A freshness guard on precedent retrieval is the follow-up this
  piece recommends.

## Dissent log

Dissenter pass 2026-10-25, verdict SHIP-WITH-CHANGES (attacks also posted to
the bus, thread context-beats-model-class). Strongest objection (attacks 1
and 4 combined): the draft's headline misquoted its own evidence, the residue
is 54.2 percent reject not "79 percent", the +37 point delta partly reflects
flash-alone miscalibration against a 0.542 trivial baseline, every measured
arm failed the 0.8 ship gate, and the empirically first lever was a one-line
RULE (0.81), which the draft's "state first" headline dropped.

Answer: accepted in full and folded in. The ordering is now rules first,
context second, model last; the delta is reported against its trivial
baseline; the ship-gate failure is stated in the headline paragraph; scope is
limited to Josh-taste text surfaces. The core position survives because the
0.25 to 0.62 equal-model delta is ledger-verified and larger than any
model-swap delta measured on this surface, and because the final architecture
the arc actually shipped IS the reframed ordering.

Also folded: 25x price corrected to about 14x input (script price table,
13.6x input / 22.7x output; token counts unpersisted so the realized figure
is unverifiable); the "40 cents of precedent retrieval" figure deleted
(fabricated; precedent.py is stdlib, zero model tokens); 19/51 corrected to
19/50; "stronger model" dropped for kimi (never measured as stronger, only
pricier); commitments labeled doctrine, not hooks; staleness risk marked
live. The same magnitude errors existed in `domains/decisions-judgment.md`
and the Jev memory; the domain file was corrected this pass, the memory is
flagged to the gardener (not librarian-owned).
