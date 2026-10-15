# 1. WORKING / NOT WORKING

**Top 5 working:**
- **Context-cost engineering.** Banked, measured: cold start 128.2k→58k in-tokens (-55%, $0.64→$0.29), per-turn 170k→96k. MCP tiering correctly diagnosed (MCP was 81% of tax). This is the best-run workstream in the estate.
- **Grounded retrieval (KB RAG++).** A/B-proven: cost inversion on grounded tasks ($0.34-0.42 harness vs $0.48-1.08 vanilla, 3-6x faster) and eliminates vanilla's signature failure class (confabulated platform economics mispricing designs 5-10x).
- **Governance guard stack.** Manifest-guard, redteam-guard, Josh-only prod gates — snapshot confirms "working as designed." Zero cited incidents of gated-action bypass.
- **Session accountability detection.** Closeout enforcement (script refuses fragments) + SessionEnd hook + 60s dead-man sweep caught session 8985. Detection layer works.
- **Turn telemetry.** 11,029 turns/7d classified (83% productive, 3.1% waste), 794 errors categorized (301 permission-denied, 253 bash-exit). You can't fix what you don't count; this is counted.

**Top 5 broken/straining, classified:**
- **Seismic triage loop (13th stop incident).** **Design flaw.** Read-only agents structurally cannot remediate; the loop produces autopsies, not fixes. 13 repetitions means the loop has no convergence detector and no escalation-with-teeth. Ownership gap secondary (needs-josh rows piling).
- **Cost basis.** **Ownership gap.** Two price books 20-25x apart (gateway ~$5.5/MTok vs Fireworks), never reconciled, plus no cost guard on fleet/headless. Nobody owns the ledger of truth.
- **Fusion ledger / multi-model eval infra.** **Build bug.** 13/32 runs error (5 gateway timeouts, 7 reasoning-exhausted-empty, 1 mapping 400). Compounded by design gap: 2/32 outcome-labeled means even successful runs feed nothing back.
- **promotion-orchestrator.** **Build bug or dead-on-arrival — GUESS: never wired into heartbeat.** 0 gossip posts EVER, in a fleet where heartbeat.jsonl is the liveness contract, proves an agent can be registered and silent indefinitely without tripping anything.
- **needs-josh backlog + stale in-flight claims (79 workstreams, 2+ open loops on several, unreviewed adversarial genie).** **Ownership gap / design flaw hybrid.** The estate generates review work faster than one operator clears it, and nothing ages or escalates the queue. Stale in-flight claim on a gated action = possible unfinished prod state — the most dangerous item on tonight's list.

# 2. MONITORING COVERAGE

**Adequately monitored:** scheduled job liveness (heartbeat contract + dashboard gap display), session closeout (dropped-sessions.jsonl), corpus integrity (source-count floor tripped tonight — gate worked), connection health/stalled schedulers (watchdog 23:13), backup (nightly, sanitized).

**Blind or effectively blind:**
- **Spend.** No statusline/cost guard on fleet or headless sessions. A runaway agent loop tonight burns money until Josh reads a bill. Highest-severity blind spot, and it's compounded by the unresolved price book.
- **Agent silence.** promotion-orchestrator proves registration ≠ liveness. Heartbeat catches jobs that run and fail; it does not catch agents that never post.
- **The 00:37–07:13 window.** Last fleet cron (project-dreamer 00:37) to morning-brief 07:13 is ~6.5h with no recipe-level eyes. Watchdog ran 23:13; a Workato recipe failing at 01:00 is invisible until 07:13. Session-shadow runs every 60s but is session-scoped, not recipe-scoped. KB sync failing again tonight is caught by the gate but (GUESS) only surfaced via digest — up to 8h lag.
- **Non-converging loops.** Nothing counts "same root cause, Nth incident." Seismic hit 13 before it was a named strain. The system detects incidents, not the *failure to fix*.
- **Claims vs live state drift.** Evidence agent exists, but stale in-flight claims on gated actions are listed as a live strain — so reconciliation cadence is insufficient. Failure class: half-applied prod change believed complete.
- **Session content loss.** Dead-man sweep catches the drop, not the payload: 8985 ran 1187 turns, wrote 0 files, and a workday of state is "absorb pending." No checkpoint mechanism.
- **Productivity metric integrity.** GUESS: the 83% productive classification is heuristic/self-reported; nothing cited validates it against outcomes (only 2/32 fusion runs are outcome-labeled — the labeling muscle is weak estate-wide).

# 3. SKILLS/HOOKS/MODS VERDICT

**Earning its keep (evidence-backed):** MCP tiering (-55% cold start), redteam-guard + manifest-guard (standing orders hold), mission-control closeout enforcement (refuses fragments; caught 8985), kb_search/kb_read (measured inversion), airo-error-guide at least *fires* (26KB logged).

**Suspect / probable dead weight:**
- **47 active skills with zero cited usage telemetry.** 13 were parked in the diet and nothing broke — evidence the long tail is load-bearing only as context tax. GUESS: 10-15 more parkable.
- **28 gossip outboxes vs 16 named agents.** 12 outboxes map to nothing named — GUESS: stale/duplicate registrations. Corroboration model ("3+ = act") is meaningless if outboxes outlive their agents.
- **cortex hourly pulse + hourly 14-section dashboard + 60s session-shadow.** Three attention surfaces, one human reader. No cited instance of a cortex pulse causing an action. Prime theater candidate.
- **Dreamer pipeline.** 45 proposals "lifecycle-managed" — adoption count not cited. Idea generation with a trust ladder is only value if proposals land; if adoption ≈ 0, it's a proposal museum.

**Missing (each maps to a tonight-failure):** fleet/headless cost-cap hook; session checkpoint/journal hook (8985); agent-silence detector (promotion-orchestrator); loop-convergence counter (Seismic); needs-josh aging escalator; hook outcome-logging.

**What to measure:** per-skill invocations/7d (park bottom quartile); per-hook fire→behavior-change rate (airo-error-guide: do AIRO errors recur post-fire?); per-agent posts + downstream actions; dreamer proposal adoption rate; gossip outbox↔agent registry diff. Any skill/hook that can't produce a number in this pass is dead weight by definition.

# 4. VALUE PROOF VS THEATER

**Proven with numbers:** deep battery 6.0/6 vs 4.5/6 (same model); eliminated failure class is named and economically material (platform-economics confabulation, 5-10x design mispricing); grounded-task cost inversion with latency win (3-6x); -55% cold start; per-turn 2.2-4.4x cheaper than trailing week.

**Theater or unproven:** the fleet's *business* mission is tonight's failure list — Seismic stop #13, recipe 82272892 failing, canary stopped, KB sync failed. The harness is measurably better at *answering questions about Workato* while the *Workato estate it operates* degrades. Simple lookups: 7-9x token tax for +1/12 correctness (and vanilla's miss was a fabricated citation — real, but one doc lookup). The 16-agent/28-outbox/11-cron apparatus has no cited measure connecting it to recipe uptime. Fusion eval infra (13/32 errors) currently can't even grade itself.

**Single most defensible value claim:** elimination of the confident-confabulation failure class on platform economics — A/B measured, same-model controlled, with a direct dollar mechanism (mispriced designs). This survives scrutiny.

**Single most damaging weakness:** the unresolved cost basis. Every savings claim above ($0.64→$0.29, inversion dollars) is denominated in a currency the estate itself cannot define — two price books 20-25x apart, no fleet cost guard. It doesn't just weaken ROI claims; it means the estate's largest unmeasured risk (headless spend) is unpriced. Runner-up: Josh-as-bottleneck (gates + 79 workstreams + aging needs-josh) caps total system throughput at one human's attention.

# 5. NEXT EVOLUTION PHASES (ranked by leverage per Josh-hour)

**P1 — "One Price Book" (cost truth).** Goal: single canonical cost basis + spend guards. First build: adjudication script over 30d of gateway costUSD vs Fireworks line items, pick canonical, log verdict to claims ledger; add per-session cost-cap hook for headless/fleet. Done when: one verified price book; every session (incl. fleet) emits cost; >$X/session alert fires in digest. Highest leverage: cheapest build, unblocks every other ROI claim.

**P2 — "Converge or Escalate" (remediation loops).** Goal: no 14th read-only autopsy. First build: per-root-cause incident counter; at N=3, auto-escalate to needs-josh with a proposed *write* fix (bounded auto-remediation for the known Seismic class, red-team verdict first since prod). Done when: next recurrence is auto-fixed or lands with a fix proposal, not an autopsy.

**P3 — "Josh-Queue Burn-down."** Goal: needs-josh aging < 72h; zero stale in-flight claims on gated actions. First build: aging column + escalation in 07:13 digest; pre-digested approve/reject packets (dissenter pre-votes) so review is minutes not hours; claims-vs-live-state sweep for gated actions. Done when: no item with 2+ open loops older than a week; stale gated claims = 0. Directly raises total system throughput.

**P4 — "Never Lose a Workday."** Goal: zero unabsorbed sessions. First build: checkpoint hook journaling state every N turns + on idle; dead-man sweep auto-absorbs. Done when: kill-test a 100-turn session and absorb reconstructs it; every dropped-sessions row has an absorb artifact.

**P5 — "Fleet Headcount Review."** Goal: every agent/skill/outbox proves use or parks. First build: telemetry pass (Q3 metrics), auto-generated park list — promotion-orchestrator first, orphaned outboxes second. Done when: registry↔heartbeat coverage is 100%, silence alarms on, park list executed.

# 6. NEXT TOKEN/COST TRANCHE

- **Cost basis first, non-negotiable.** 20-25x divergence means all dollar figures below are provisional. GUESS at root cause: gateway costUSD is blended/list across routed models while Fireworks is per-model actual — or one includes cache-read/write at full price. Until adjudicated, report tokens, not dollars.
- **Simple-lookup tax: biggest remaining tranche.** 7-9x tokens on simple tasks (correctness 12/12 vs 11/12 — a ~1-point gain). Build a task-class gate at session start: lookup-class skips fleet context + KB preamble. If lookups are (GUESS) 30-40% of the 188 sessions/wk, cutting their multiplier to ~2x saves roughly 25-35% of total weekly in-tokens off the 96k/turn baseline.
- **Residual cold-start.** 58k remains: GUESS 8-15k more via lazy-loading INDEX.md's 27 domain files on route-match only (router is 91 lines; the domains behind it shouldn't all be hot), plus hook system-reminder residue diet.
- **Error-turn conversion.** 554/wk permission-denied + bash-exit errors (~5% of 11,029 turns). Fix allowlists for the top denied patterns; measure airo-error-guide's post-fire recurrence. Each error turn costs the error + retry: GUESS 3-5% turn reduction.
- **kb_search latency, 13.6s median.** Slow retrieval → more verification turns (13% of turns ≈ 1,434/wk). Tune reranker depth/top-k; target <5s. Savings are turn-count, not per-turn tokens.
- **Fleet job budgets.** Dreamer/librarian/corpus jobs over a 200k-chunk corpus have no cited token caps. Set per-cron budgets; alert on overrun (dovetails with cost guard).
- **Turn budgets + checkpointing.** 8985 ran 1,187 turns — sessions that long are context-cost time bombs regardless of the loss issue. Soft cap with forced compaction/checkpoint at N turns.

# 7. KNOWLEDGE GAPS

**Strong:** external corpus (34k docs/200k chunks, hybrid BM25+dense+rerank, retrieval quality A/B-proven), Workato platform economics (the exact domain where vanilla confabulates), curation machinery (gardener, librarian, corpus-indexer), claims ledger with confidence levels.

**Thin — and these are the gaps that matter:**
- **Failure-derived knowledge.** 13 Seismic autopsies and the root cause is still unfixed *and* apparently not encoded where retrieval would surface it. Autopsies should auto-distill into claims-ledger "gotcha" entries that kb_search returns *before* similar work. Tonight's loop is proof incident knowledge isn't compounding.
- **Josh's own operational knowledge.** 491 internal md files vs 34k external docs — the estate knows Workato's docs far better than it knows Josh's estate. Recipe 82272892's coupling to a stopped canary surprised someone; a cross-recipe dependency/blast-radius map is internal knowledge that doesn't exist in the KB. Same for runbooks, env quirks, historical incident fixes.
- **Transcript → knowledge pipeline.** 8985: 1,187 turns, 0 files, absorb pending — a full day of reasoning existed only as transcript. spec-distiller exists but no cited transcript-mining flow. 188 sessions/wk is the richest untapped corpus in the estate.
- **Decision provenance / Josh-preference model.** 79 workstreams with stale claims means decision state lives in Josh's head. Mining Josh's gate decisions (approves/rejects/edits) into a preference corpus would let agents pre-align proposals and shrink the needs-josh queue — the single smartest-making addition available.
- **Self-knowledge.** The estate doesn't know its own economics (price books) or its own fleet liveness (silent orchestrator). Introspective knowledge is the thinnest layer.

# 8. DISSENTER ATTACKS

**Attack 1: "Self-licking ice cream."** The plurality of the fleet exists to observe and improve the harness itself (cortex, dreamer, brain-gardener, estate-architect, librarian, evidence, dissenter) while the paying mission — Workato ops — fails tonight on four fronts (Seismic #13, 82272892, canary, KB sync). **Lands, partially (~70%).** The A/B gains are real, but the build-vs-operate balance is visibly off; several meta-agents would not survive the Q3 usage audit.

**Attack 2: "Unauditable ROI."** Every value claim rests on an unresolved 20-25x price-book divergence; fleet spend is unguarded and unpriced; the eval infra that should arbitrate claims has a 41% error rate (13/32) and 6% outcome-labeling (2/32); the headline "83% productive" has no cited outcome validation. **Lands fully.** This is the strongest attack because it poisons the defense's best evidence, and it is fixable in a week, which makes not having fixed it worse.

**Attack 3: "Governance theater masking a bus factor of one."** Josh-only gates + 79 workstreams + aging needs-josh rows + an unreviewed adversarial genie + 13 unanswered autopsies = the system's true throughput ceiling is one human's attention, and the fleet manufactures oversight debt faster than it clears. A stale in-flight claim on a gated action means the guard stack can *say* "gated" while prod sits half-finished. **Lands fully — tonight's own evidence (strains 3, 8, 9) is the indictment.**

Weaker attacks that miss: "over-monitoring" (heartbeats and the integrity floor genuinely caught things tonight) and "skills bloat" (real, but the diet mechanism already proves self-correction).

**Grade: B-.** A-grade measurement craft and governance design (A/B bench, -55% cost work, guard stack); D-grade showing tonight on cost truth, production reliability, and queue throughput. The harness is excellent at knowing things and measurably worse at finishing them.