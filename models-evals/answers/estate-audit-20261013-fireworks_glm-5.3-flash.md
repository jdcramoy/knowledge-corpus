# 1. WORKING / NOT WORKING

**Working (top 5):**
- **Context economics** — measured, mechanism-attributed: cold start 128.2k→58k in-tokens (-55%, $0.64→$0.29), MCP tiering (9 servers, MCP was 81% of tax), per-turn 170k→96k. This is real, same-model, reproduced across task classes.
- **Guard stack** — manifest-guard Stop hook, redteam-guard, `never_auto` constitution on skills/hooks/settings. Zero counter-evidence of gate bypass tonight despite 5+ live failures.
- **Detection layer** — heartbeat contract, dropped-sessions.jsonl, KB source-count floor, watchdog autopsies all *fired correctly tonight*: KB sync failure tripped its gate; session 8985's death was captured; seismic stops detected. Detection is not the problem.
- **Turn telemetry** — 188 sessions/7d = 11,029 turns classified (83% productive / 13% verification / 3.1% waste); 794 tool errors decomposed by type (301 permission-denied, 253 bash-exit).
- **KB retrieval economics** — grounded tasks $0.34–0.42 vs vanilla $0.48–1.08 web-crawling, 3–6x faster; correctness 12/12 vs 11/12. The corpus pays for itself on grounded work.

**Broken/straining (top 5, classified):**
- **Session persistence** — 8985: 1187 turns, 0 files, no closeout. **Build bug + design flaw**: dead-man sweep detects death; nothing recovers the corpse. Absorb exists but "pending" = unreliably wired.
- **Triage-without-action** — seismic 13TH stop: repeated read-only autopsies, root cause unfixed, needs-josh rows piling. **Design flaw**: the loop has no act/verify stage and no escalation dedup — same root cause → N rows instead of 1 decision request.
- **promotion-orchestrator** — 0 gossip posts EVER. **Build bug** (likely dead process) **+ ownership gap**: the heartbeat gap was apparently never escalated to an alarm, only noticed by audit.
- **Cost basis** — two price books 20–25x apart, no statusline guard on fleet/headless. **Ownership gap**: nobody owns reconciliation; **design flaw**: no cost metering hook exists in a harness that measured everything else.
- **Fusion eval infra** — 13 errors/32 runs, only 2/32 outcome-labeled. **Build bug**: the harness's own measurement instrument is its flakiest surface.

(Honorable mention: KB nightly sync failed its floor — detection worked; automated repair and downstream staleness-flagging didn't.)

# 2. MONITORING COVERAGE

**Adequately monitored:** job heartbeats, dropped sessions, recipe failure detection + autopsies, KB integrity gates, morning digest aggregation (07:13), turn audit.

**Blind — failure classes that can happen TONIGHT with no surface firing:**
- **Stale in-flight claims on gated actions** (79 workstreams, explicitly flagged) → possible unfinished prod state sitting overnight. The evidence agent exists but is not on the cron list — GUESS it runs on-demand only, so nothing sweeps claims against live state. This is the most dangerous gap.
- **Silent agent death.** promotion-orchestrator proves an agent can be dead its entire life with no alarm. The class applies to any of the 16+.
- **KB staleness downstream.** Sync failed tonight; tomorrow's grounded sessions will cite a stale corpus. GUESS kb_search results carry no as-of/freshness stamp, so nothing flags it — a correctness failure invisible until a wrong design ships.
- **Cost runaway.** No cost guard on fleet/headless. A recurring nightly job (dreamer, corpus-indexer) melting down burns money visible only at invoice.
- **State loss repeat.** Any session killed tonight before absorb runs = 8985 again.
- **Closed-loop fix verification.** Nothing answers "did the fix fix it" — the exact class behind the seismic recurrence.

# 3. SKILLS/HOOKS/MODS VERDICT

**Earning keep:**
- Hooks as a class — deterministic, cheap, invariant-shaped: manifest-guard, redteam-guard, closeout-refusing script, airo-error-guide (26KB of fires = it's live), hook output dieting + MCP tiering (measured savings). The `never_auto` constitution on skills/hooks/settings is the best governance decision in the estate.
- The measurement hooks (turn-audit, heartbeat, dead-man sweep) — they caught everything tonight.

**Dead weight / unverifiable:**
- promotion-orchestrator: dead.
- 47 active skills: zero per-skill fire/cost/outcome attribution anywhere in the evidence. Breadth without telemetry = unverifiable.
- cortex hourly pulse: 24 fires/day; no cited decision it changed.
- Dreamer pipeline: 45 proposals "lifecycle-managed," zero cited graduations to auto-safe.
- Gossip corroboration tiers (1/2/3+ witnesses): no cited action ever keyed to the 3-witness rule. Elegant on paper, unexercised in evidence.

**Missing:** cost-accumulator hook; scheduled claim-freshness sweep; post-fix verification hook.

**What to measure:** per-skill fires/30d, tokens-per-fire, downstream acceptance rate; hook-fire → repeat-error delta for airo-error-guide; actions-per-week per agent. Kill rule: no fires in 30d and no guard role → park (13 already parked; expect more).

**Verdict:** hooks earn their keep; skills are the least-measured and most likely over-built layer; the missing guards are cost and closure, not more capability.

# 4. STRENGTHS / WEAKNESSES + VALUE PROOF

**Proven with numbers:** -55% cold start (mechanism-attributed); grounded-task cost + latency win; 6.0 vs 4.5 on deep design with a specific plausible mechanism (vanilla confabulates platform economics, mispricing designs 5–10x — exactly what a domain KB fixes); 83/13/3.1 turn discipline at n=11,029.

**Theater:** promotion-orchestrator (dead weight wearing a title); fusion eval (2/32 outcome-labeled — the proof machine cannot prove); 45 dreamer proposals with no cited adoption; corroboration tiers with no cited trigger; a 14-section dashboard (zero-token regen is good engineering; 14 sections is a firewall of glass — GUESS on readership).

**Most defensible value claim:** the same-model A/B token economics — cold start -55% with named mechanism, plus grounded tasks cheaper AND faster. Token counts are price-book-independent, so this claim survives problem #7 intact.

**Most damaging weakness:** **detection-without-closure.** Tonight's evidence shows the harness noticing everything — 8985's death, the KB floor breach, the seismic recurrence, the dead agent — and closing none of it without Josh. It is a world-class sensor rig bolted to a one-human actuator.

# 5. NEXT EVOLUTION PHASES (ranked by leverage per Josh-hour)

1. **REAPER** — claim & fleet hygiene. Goal: no stale claims, no silent agents. First build: nightly evidence-agent sweep — re-verify in-flight claims vs live state, flag gossip-silent agents >N days, archive dead workstreams. Done = promotion-orchestrator revived or removed; 79 workstreams pruned with fresh claim timestamps. ~1 Josh-hour (approve).
2. **CLOSER** — detection → recovery. Goal: never lose a workday again. First build: dead-man sweep triggers auto-absorb of killed-session transcripts into a closeout row + claims snapshot. Done = next dropped session absorbed <15 min, zero lost work. ~0.5 Josh-hours.
3. **PRICEBOOK** — one canonical cost table + guard. First build: reconcile gateway vs Fireworks into a single claims-ledger entry (the ledger exists for exactly this); per-session USD in statusline; hard budget abort on nightly fleet jobs. Done = one source of truth, every fleet session costed, test alert fired. ~1–2 Josh-hours (adjudicate the two books).
4. **FIXLOOP** — autopsies that terminate. First build: watchdog output gains an action field + root-cause dedup key; autonomous-safe fixes (dev-test scope) apply + verify; one needs-josh row per distinct root cause. Done = seismic root cause fixed, or exactly one decision request. ~2–3 Josh-hours.
5. **SKILLCULL** — evidence-based surface area. First build: skill fire/cost telemetry → 30-day report → park the bottom N. Done = 47 → a measured count, every survivor with a fire rate. ~2 Josh-hours (review).

# 6. TOKEN/COST NEXT TRANCHE

- **Light-mode profile for simple tasks.** The 7–9x simple-lookup tax is the fixed estate (guards-only profile for trivial sessions: skip gossip/digest injection, minimal skills). Est: 58k cold → ~35–40k. GUESS on the simple/complex session mix — measure it first.
- **Retrieval payload diet.** kb_search 13.6s median (vs kb_read 0.11s) suggests chunk sets land in context. Server-side rerank → return top-k IDs + ~200-token abstracts, expand on demand. Est 5–15k per grounded turn. GUESS on payload size.
- **Error-tax removal.** 794 tool errors/wk; 301 permission-denied = config/agent mismatch. A preflight allowlist for repeat offenders removes ~300 retry round-trips/wk, each carrying context reload. bash-exit 253: airo-error-guide fire→repeat delta is unmeasured — measure before assuming it works.
- **Verification-turn diet.** 13% verification = ~1,434 turns/7d; convert mechanical verification to Stop-hook assertions. Est 3–6% turn reduction. GUESS.
- **Resume compaction.** 1187-turn sessions imply monster transcripts; checkpoint summaries cut resume cost after every kill.
- **Cost basis is a precondition, not an optimization.** Until PRICEBOOK lands, optimize to tokens (the honest currency) not USD. After: per-session USD, hard budget caps on nightly jobs, and likely a routing policy — GUESS the 20–25x spread is route-mix (cheap Fireworks routes for mechanical jobs, gateway for judgment), not a bookkeeping error, but nobody knows because nobody owns it. That itself is the finding.

# 7. KNOWLEDGE GAPS

**Strong:** external Workato corpus + platform economics (the A/B proves it — vanilla misprices 5–10x, harness doesn't); curated 91-line INDEX router; the claims-ledger *pattern*; redteam verdicts.

**Thin:**
- **Josh's own operational knowledge.** 491 own-KB files vs 34k external docs. Session 8985 — a full workday living only in a transcript, 0 files written, absorb pending — is the emblem. Much of what the estate "knows" about itself lives in transcripts and mission-control rows, not the KB.
- **Postmortem distillation.** Watchdog autopsies show no evidence of flowing into domain files or the claims ledger; the seismic recurrence proves lessons aren't closure-bound.
- **Per-recipe runbooks** (82272892 state, canary history, known failure modes). GUESS thin.
- **Cost knowledge.** Two price books violate the estate's own claims-ledger standard (evidence + confidence). The ledger exists; the entry doesn't.
- **Corpus freshness.** The floor gate detects failure; retrieval results carry no as-of stamp. GUESS.

**What would make the whole system smarter (not just more complete):** (a) transcript-absorption as a first-class pipeline — every session's durable facts → claims ledger; (b) a captured model of Josh's adjudication patterns (what he actually does with needs-josh rows: approve/defer/kill frequencies) so the trust ladder can graduate more loops to auto-safe. That converts Josh-only head-knowledge into fleet-usable knowledge — the highest-leverage capture available.

# 8. HONEST VERDICT

**Attack 1 — "This is an instrumentation rig, not an operator."** It detects everything and closes almost nothing: 8985 captured but the workday lost; seismic autopsied repeatedly, never fixed; promotion-orchestrator dead for life; needs-josh rows piling; 2/32 eval runs labeled. The harness exhibits the exact pathology it diagnoses in vanilla Claude Code — confident output without verified grounding, except its output is signals. **Lands hardest. Four independent evidence items corroborate it tonight.**

**Attack 2 — "The value math is self-graded."** Owner-designed rubric, battery run count undisclosed (GUESS n small), eval infra erroring 13/32, and the USD headline unauditable while two price books sit 20–25x apart. **Lands partially**: token-count claims are same-model, mechanism-attributed, and price-independent — the -55% survives. The USD narrative and eval rigor are the soft tissue.

**Attack 3 — "Over-built relative to one operator."** 16+ agents, 28 outboxes, 11 crons, 47 skills, 14-section dashboards — and the fleet's net effect on Josh's queue is *positive needs-josh rows* (item 8, item 9: 79 workstreams). Elaborate supervision machinery funneling into one human. **Lands largely**, with the concession that Josh-only gates are deliberate governance and the 07:13 digest is the aggregation answer — but the queue grew anyway, and at least one agent produced nothing, ever.

**Which lands: Attack 1.** The closure gap is the harness's defining failure, and it's the one the evidence set was literally structured to reveal.

**Grade: B-.** Justification: genuinely measured economics, working guard stack, and a detection layer that caught every failure tonight — undercut by zero-closure automation, one dead agent nobody alarmed on, an unauditable cost basis beneath the flagship metric, and an eval instrument too flaky to trust. Not lower because the measurement culture is real and every failure was *seen*; not higher because nothing finishes without Josh, which is the one thing this harness was supposedly built to change.