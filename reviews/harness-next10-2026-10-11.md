# Harness next-10 — adversarial panel review, 2026-10-11

6-agent panel (neuroscience/opus, music/sonnet, ecology/fable, psych-socio/sonnet,
cybernetics/fable, resident dissenter/opus) + fable adjudicator cross-examining all 20
proposals against the dissenter's live-evidence attacks. Full reports in session transcript.

## Live incident found by the review (VERIFIED 2026-10-11 ~08:20Z)

- Morning fleet silently dead ~2 days: morning-brief last beat 2026-10-09T07:36,
  decision-inbox 2026-10-09T18:47, cortex 2026-10-09T23:13; cost-governor and loadout
  have NO heartbeat rows under those names. harness-health-2026-10-11 (02:42) marked
  them all "(ok, daily)" — staleness window is 3x interval. Monitoring is inside the
  failure domain (same run-job.sh, same laptop, same heartbeat file).
- Store exposure: 98 uncommitted files in the knowledge tree right now; INDEX.md grew
  39.4KB -> 64.8KB in ~30h with no gate firing; workato-platform.md 1,993 lines vs 300
  budget (6.6x); queue.jsonl corruption already happened (commit 31ac8df, repair file
  dated 2026-10-10); predict.py rewrites its whole store non-atomically per check while
  atomic_io.py sits unused in the same directory; evidence agent built but never armed.

## The ranked 10 (post-adjudication)

1. **Store discipline (Merge C)** — voices.json write ACL + schema-validated atomic
   appends for shared ledgers + queue.jsonl as rebuilt projection over the immutable
   triage-outcomes log. Kills the 49-decision-loss class. BUILD FIRST.
2. **Allostatic fleet + external dead-man (Merge B)** — per-job zero-LLM probes,
   skip-heartbeats distinct from stubs, two-rate hysteresis, PLUS a dead-man switch OFF
   the laptop (healthchecks.io ping / GH Action on backup repo). Fixes the verified
   D1 incident class; health staleness window 3x -> 1.5x.
3. **Arm the unarmed (PSY4 core)** — harness-health flags "pending first tick" beyond
   one interval as a FINDING; arm the evidence agent; commissioning checklist
   (charter/refusal-rights/mentor/dated review) for new agents.
4. **Bus epistemics patch (Merge E)** — gossip-read.py:136 PATTERN requires a
   non-finder verify citing its own evidence (currently flips on 2 agents merely
   discussing); independent/anchored labels; leitmotif registry of canonical slugs.
5. **Salience/decay substrate + INDEX budget gate (Merge A)** — one reinforcement
   pass (reads/writes/inbound-refs/corroboration/last_verified) -> strength per file
   and INDEX line; decay lifecycle with demote-never-delete; amygdala/keystone
   critical exemption; INDEX shrink via librarian branch lane; session-start budget
   gate. Ships only WITH the gate, never as report #54.
6. **Close the prediction loop (CYB2)** — hook auto-open on allowlisted action classes,
   stale-prediction probe, stakes-map forces rehearsal on poorly-calibrated classes,
   atomicity fix to predict.py store.
7. **Germination trials (ECO4)** — restore-drill.py structural verification of the
   never-restore-tested backup (explicit NOT-verified footer for semantic tier);
   dream-mine --days 1 pre-backup nightly so transcript patterns survive machine loss.
8. **Verdict economy (Merge D)** — per-producer rolling precision from outcome ledgers
   -> producer caps + digest lane (P1 bypass), precision x surprise ranking in shadow
   mode. DEPENDENT on #2 (inbox itself was dead when measured).
9. **Salience-weighted interleaved replay (NEU1)** — nightly sampler re-mines ~3 OLD
   sessions weighted by correction density/deviation/spacing; fixes the dreamer's
   recency-window-only consolidation (VUA-revert class recurred 3x across 5 weeks).
   Sequenced after #2 and #8.
10. **Immune tolerance / titer review (folded ECO3)** — last_fired on canon entries;
    retire advisory-tier rules only on docs-watch environment delta, never on
    incident-absence; rides #5's enforcement pass.

## Killed in the kill round

- **Lead-sheet constraints (MUS4)** — prose-vs-YAML drift uncheckable; degenerates to
  a second unread spec per skill.
- **Vector recall over the knowledge tree (NEU3)** — embedding a tree with 98 files
  uncommitted guarantees stale index; substring suffices at ~100 files. Revisit after
  #1 and #5.

## Sequencing law the panel converged on

Fix the STORE first (#1), then LIVENESS with an external judge (#2), then TRUST
surfaces (#3/#4), then METABOLISM (#5-#8), then CONSOLIDATION (#9-#10). Everything
after #1 routes through state that is currently unguarded.
