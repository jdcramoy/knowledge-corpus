# Workato KB (RAG++) — project state

Built 2026-10-08. Repo: `~/Documents/workato-kb` (committed fb3b488). Data root:
`~/.claude/workato-kb/`. Skill: `workato-kb` (~/.claude/skills/workato-kb/SKILL.md).
Nightly launchd `com.josh.workato-kb-sync` 02:07.

## What it is

Josh's requirement: the agent gets deep, always-current Workato platform knowledge
(docs + best practices + Gears + frameworks) referenced during planning/build/test
without flooding context — plus the BT team's internal and external Confluence.

## Sources (all crawled, first-sync totals)

- **docs**: 4,339 pages. KEY DISCOVERY: docs.workato.com ships first-party
  `llms.txt` (4,396 en entries) and every page has a raw-Markdown twin at the same
  path + `.md` (`content-type: text/markdown`, ETagged) — no scraping needed. en +
  ja in sitemap; we sync en only.
- **changelog**: 252 posts. product-hub is WordPress (product2.workato.com);
  changelog = WP category 443 "What's New". The /changelog/ archive HTML renders
  links client-side (useless server-side); RSS feed gives 10 latest.
- **blog**: 1,197 posts. workato.com/blog and /the-connector are ONE WP install
  (blog2workato.wpengine.com) — both wp-json paths serve the same collection;
  /blog/wp-json 301s to /the-connector/wp-json. Crawl the origin host once.
- **confluence-extbt** (BTI, 1,098) + **confluence-intbt** (BTKB, 2,254): BT team
  spaces. Initial backfill via Atlassian MCP getPagesInConfluenceSpace
  (250/call, markdown bodies, cursor pagination — 9 calls + tool-results-file
  ingest). Nightly incremental via REST + API token (keychain service
  `atlassian-confluence`, account <user>@workato.com — **TOKEN NOT YET
  CREATED; step self-skips until then**).

**Privacy wall (Josh ruling):** Confluence corpora are LOCAL-ONLY — never in
git, never in the GitHub backup, never in the org kit repo. Public sources
(docs/changelog/blog/github) may be packaged for the fleet later.

**Josh-added sources (2026-10-08, mid-build):** three architecture-canon GitHub
repos — system-design-primer, awesome-software-architecture,
awesome-system-design-resources — shallow-cloned into corpus/github/,
git-pull incremental, manifest over English md files (320). Source `github`.
The Connector confirmed already covered (it shares the blog WP install).
Plus: `eip` = enterpriseintegrationpatterns.com (103 pages incl. the
eip1_examples_updated rambling), `claude` = Claude platform docs (625 en
pages via llms.txt md-twins — generic crawler kb/llms_source.py ready for
any future llms.txt site), `inspiration` = Automation Inspiration (88,
product-hub WP category 436). Final roster: 9 sources, ~9,400 docs.

**Dreamer mandate (Josh, same night):** harness-dreamer reviews the KB NIGHTLY
via three modes — (1) comprehensive review of the change surface (diff report)
nightly + full-corpus survey on Sunday, (2) targeted RAG queries connecting
last night's session topics to the docs, (3) ongoing meta-mandate: discover
new KB modalities, WoW, architecture designs worth adopting.

## RAG++ stack (all local, MPS)

- Hybrid: FTS5 BM25 + `BAAI/bge-base-en-v1.5` dense (sqlite-vec float[768]) →
  RRF fusion (k=60) → `BAAI/bge-reranker-base` cross-encoder.
- Contextual chunking, deterministic variant: every chunk carries a
  `[source | section | page | url]` header (LLM-generated headers = roadmap).
- Entropy layer (built, staged): per-chunk self-information bits/word under the
  corpus unigram model — `kb.entropy score|top`. Deep-wire into rerank weighting
  during quality tuning (Josh: entropy ranking comes AFTER a working system).
- Agentic loop: search → refine (max 2) → read doc → cite URL. Freshness guard:
  live `.md` re-fetch beats local on disagreement.
- Query expansion: domain synonym table in kb/search.py (datapill/vua/opa/genie...).

## State

- **VISIBILITY RULING (Josh, 2026-10-09): the kit + workato-kb stay INTERNAL.**
  Audit found: config.sh tracked w/ workspace IDs + 114-commit history, AI
  gateway URL + internal hosts/IDs throughout, and airo-mcp-playbook = Workato
  INTERNAL platform-behavior catalog (employee disclosure risk). A public
  edition = sanitizer pass + FRESH git history (old history unredeemable) —
  a deliberate project if ever wanted; the novel IP (fractal/RAG++/dreaming
  team/benchmark) is publishable, the platform internals are not.


- **v0.9.2 (0131ec3 + b4cefce + c57ed3e) — STATE HASHER + ANTIGEN DRILLS LIVE.**
  state_hasher.py (unified snapshot: knowledge-git + 3 DBs + bus + manifests;
  restore = git-atomic + backup-pointed; snap/list/restore tested). Antigen
  pool (4 synthetic failure classes) + CANARY LIVE: recipe 82934208
  ([CANARY] Antigen Drill, dev, folder 32175654) — 6-hourly clock (lowercase
  units), reads kb_antigen_faults table (158128), if antigen_state ==
  virus-active → logs the SIGNATURE line → intentional hard fail (nonexistent
  record). DRILL 1 FULL CYCLE PROVEN: snapshot c3ad75534a77 → inject (AIRO
  set_input_field value='virus-active' constant → push) → force-run → job
  FAILED with the signature in the trace → revert (data-driven conditional) →
  force-run SUCCEEDED. Ledger + case filed. Fleet job `antigen` (Wednesdays
  06:07, headless, AIRO-capable) drills weekly + scores detection.
  AIRO gotchas banked: trigger add accepts `action: scheduled_event` (v1)
  when v2/display forms 404; rb value with quotes stores literal quotes
  (plaintext mode for constants); stop-before-push (running-recipe edit
  block); wt dt create-record envelope = CreateRecordRequest (UNCHARTED —
  all JSON shapes 400'd; fault injection pivoted to AIRO code mutation
  instead of data-row injection; wt dt reads still fine).


- **v0.9.0 (5221a91) — THE FIVE LEARNING MODALITIES.** cases.py (case-based
  reasoning: presentation/diagnosis/treatment/outcome, fused FTS+vec
  retrieval — VERIFIED: filed case retrieved; canon ingest mapping pending),
  apprentice.py (org-recipe pattern mining — VERIFIED: 6 recipes scanned,
  patterns distilled + indexed as apprentice chunks), gym_judgment.py
  (spaced-repetition drills — VERIFIED: first drill graded 0.0 vs known
  cause, resurfaces), curiosity.py (question ledger — VERIFIED end-to-end:
  minted from a benchmark anomaly, investigated, answered, claim-bound),
  competence.py (route by measured track record — learning stage). All
  report into science-state.json (dashboard) + gym A6 invariant (fresh
  <36h, verified). Confluence page v5 + kit synced.


- **v0.8.0 (6c613e5) — THE FIVE BUILDS.** (1) Typed bus: bus_post.py —
  finding/opinion/proposal/vote/question schema, mechanical corroboration
  (1 obs/2 pattern/3+ ACT as arithmetic); GOSSIP.md typed layer. (2) Model
  routing: kb/model_routing.py — per-model acceptance attributed via
  `models:` frontmatter convention (dreamer SOP), kimi token ledger as cost
  side; explore-exploit rule. (3) Skill forge: skill_forge.py — dreamer
  drafts SKILL.md into staging, forge checks (description-as-trigger, length,
  TODOs), Josh's accept = install. (4) Chief of staff: /today skill +
  today_brief.py data stage (heartbeats, pipeline, triage, dream, entropy,
  calibration; calendar/Slack/Jira via MCP at runtime) — ranked agenda, work
  pre-staged, drafts never auto-sent. (5) Benchmark: kb/benchmark.py — 5-task
  set, two arms, TRUE-bare via CLAUDE_CONFIG_DIR isolation (the first bare
  run was contaminated by user-scope config — tied; the isolated rerun: bare
  12.3s vs harness 31.1s, both correct+cited — harness buys depth, bare wins
  simple-task speed; discriminating tasks = diagnosis/UAT/manifests).
  OVERNIGHT AUTONOMOUS CYCLE VERIFIED: full fleet ran (heartbeats 02:32-03:50),
  dreamer filed 5 incubating proposals with math + dissent attachments
  autonomously. NOTE: no 2026-10-09.md dream report despite the 03:46 dreamer
  heartbeat — the gym's file-gate runs 00:15 (before the dreamer); consider a
  post-dreamer gym pass.


- **ADOPTION COMPLETENESS + SPEED MEASUREMENT (894c872).** Kit now carries the
  FULL system: 5 harness scripts (predict/mood/calibration/dissent_ledger/
  rehearsal) in knowledge/scripts/, refreshed workato-kb + kb skills, fractal
  authoring rules + interaction contract in INSTALL.md Part 2. Measured: CLI
  search pays ~6.4s model-load tax per call (search itself is ms) -> MCP server
  is the speed path (resident process amortizes load); queue the skill-default
  flip to MCP.


- **v0.7.2 (COVERAGE PASS AIRTIGHT).** Coverage auditor (kb fractal coverage):
  268 memory files across 12 surfaces (knowledge tree, claims, agents, skills,
  CLAUDE.md tiers, ALL project memory dirs incl. the 13 non-workbench ones, repo
  CLAUDE/AGENTS files, fleet prompts, loose docs) — 0 gaps; KB pages 10,288/
  10,288. Funnel at full coarse coverage (10,284) — SIMPLIFIED: the coarse
  distance distribution (0.72-0.84 for everything relevant) makes a distance-
  gated shortlist a recall risk; final design = unrestricted fine search +
  rank-based page-affinity boost. Zoom eval 9/10 content-scored. Criticality
  alpha 1.8 (critical zone, small-n). First real incubation re-looks: GLM
  DECAYS'd the managed-agents mapping (unverified one-to-one claim), STEEL'd
  the failure flywheel. Sync pipeline verified clean end-to-end.


- **v0.7.1 (e78067a) — VERIFICATION ROUND: everything on the not-verified list
  exercised.** (1) Full drain DONE (8,601, pending 0); funnel coarse rebuilt at
  FULL coverage — shortlist path live. (2) Co-evolution ledger has REAL data:
  first cold re-looks via GLM-contrarian on both incubating proposals —
  managed-agents mapping got DECAYS (one-to-one claim unverified; porting guide
  = fossilized false equivalence; keep the watch, kill the guide) — the
  incubation lane caught its first overreach; failure-flywheel got SURVIVES
  (steel, provenance caveat). GLM thinking-budget fix (4500 for glm). (3)
  Sync pipeline verified CLEAN end-to-end (the confluence days-arg bug found
  and fixed BEFORE tonight's first launchd run would have hit it). (4)
  Criticality: alpha 1.8, critical zone (n still small; meter maturing). (5)
  Fractal zoom: 9/10 content-scored on 10 diverse queries; three real bugs
  found and fixed by the eval (first-non-empty-level ranking inverted the
  zoom — now global bm25 + 8x title weight; factlet ID collisions — chunk_id
  in ids, page-level parents created; vec0 upsert = delete+insert). Fractal
  store now covers ALL harness memory: knowledge tree, claims, agent SOPs,
  skills, CLAUDE.md tiers, auto-memory, dreams, calibration (112 level-1
  factlets); incremental builds + freshen-on-read.


- **v0.7.0 (fa315cc) — THE FIVE LEAPS, BUILT OVERNIGHT (Josh: 'build it all').**
  (1) Calibration science: knowledge/scripts/calibration.py — per-agent
  prediction accuracy + overconfidence gap from predict.py ledger + outcomes;
  weekly calibration cards in dreams/calibration/. (2) Dissenter triad +
  adversarial co-evolution: knowledge/scripts/dissent_ledger.py — 3 critics
  (kimi-lawyer / deepseek-engineer / glm-contrarian), learning rule = severity
  that predicts real rejections earns weight; attack-classes = the dreamer's
  pre-empt list; wired into both dreamer SOPs + proposals-skill resolve hook.
  (3) Rehearsal cortex: knowledge/scripts/rehearsal.py — counterfactual replay
  orchestration; fixture extraction PROVEN (rejection miner 82863662, 3/3 jobs,
  trigger input in lines[0].input); counterfactual stage activates with the
  liveness-sentinel build. (4) Fractal memory: kb/fractal.py — 64,238 factlets
  (1 topic/25 files/294 sections/63,918 chunks), one schema at every scale,
  zoom retrieval (coarse-first, drill on decision); ADDITIVE over existing
  stores (nothing migrated); pre-fractal-cutover tags + DB backup taken.
  (5) MRL funnel: kb/funnel.py — LLM situating lines as coarse page layer
  (1,683 coarse-embedded), chunks as fine; coverage guard (coarse dist > 0.65 →
  plain fine search) until the contextualize backlog drains; three vec0 gotchas
  fixed (MATCH must be in WHERE not select-list; k must be inline literal, not
  param; MATCH-joins must live in one inner select). Plus: kb.criticality (bus
  cascade power-law fit, honestly anecdote-status at n=8), kb.mcp_server (stdio
  MCP: kb_search/kb_read/kb_zoom for any client), event-driven dreamer wakeup
  on P1 (launchctl kickstart), full contextualize drain running (~14h).


- **v0.5.2 (479a7eb) — THE MECHANISM + CROSS-DOMAIN DREAMS.** (1) `kb` CLI shim
  at ~/.local/bin/kb — zero-friction query/read/passthrough from anywhere
  (kills the cd+venv dance that would let the habit die). (2) Global CLAUDE.md
  KB mandate: query-before-plan with explicit trigger points + anti-pattern
  guard (phase boundaries, not per tool call). (3) Lateral graph went
  cross-domain: concepts = BURSTY technical terms only (burstiness >=2.5 mean
  occurrences per containing chunk — the filter that finally killed prose
  filler after df-window and stopword approaches both failed), knowledge tree
  (56 files) joins as EDGE EVIDENCE so hidden pairs span platform x practice;
  current output: deny+permission_policy, permission_policy+judgement pairs.
  (4) Sunday cross-domain dream mandate in harness-dreamer B2: lateral top-15
  + mechanism-or-considered-null requirement.


- **INCUBATION LANE (2026-10-08, from the DeepSeek contrarian critique).** The
  cross-model probe returned a real internal critique: same-night proposals are
  the least-stable version of an idea — automation deleted the "sleep on it"
  filter humans use. Fix: ideas file as `status: incubating` (NOT into Josh's
  queue); nightly re-judgment COLD by a DIFFERENT model (kb.lens_call, model
  ≠ conceiving model); promotion after surviving 2 re-looks or evidence
  strengthening; drops logged (the 4-in-5 the human filter would kill); fast
  lane only for stated-deadline windows. Both dreamer SOPs + proposal-pipeline
  (incubating display) + FILE-GATE status vocabulary updated. /proposals shows
  only proposal-status files.


- **v0.5.1 (5caad46) — CROSS-MODEL DREAMING ON JOSH'S FLEET.** Real models (Josh
  provisioned): kimi-k3 (FRONTIER, expensive), glm-5.3-flash, deepseek-4.1-flash,
  all through the Workato AI gateway (ANTHROPIC_BASE_URL/Auth token — Anthropic-
  compatible messages API). kb/lens_call.py: persona opinions direct from any of
  the three. GOTCHAS: gateway models emit thinking blocks that eat max_tokens
  before text (budget 2000 + thinking disabled); Agent-tool model mapping is
  opus/fable→kimi, sonnet/haiku→glm, deepseek only via direct call. Cost
  governance ENFORCED in script: Kimi = 1 rotating lens/night (artist→contrarian→
  musician→doctor→ceo→analogist→cto), Sunday = full board on Kimi, off-rotation
  calls self-skip, kimi-ledger.jsonl tracks usage. All three probed live with
  sharp opinions back.


- **v0.5.0 (ab1e3bc) — THE FOUR, BUILT.** (1) Board minutes: kb/board_minutes.py
  renders weekly from dream reports + bus (sanitizer: intbt/EDW/josh.cramoy
  markers, dry-run 0 findings); fleet job `minutes` Mondays 06:27 publishes a
  DRAFT Confluence page under 2938830860 in BTI — Josh publishes on review
  (Josh-gated per harness-docs policy). (2) Cross-model dreaming: dreamer SOP
  mandates Agent-tool model override per lens (sonnet/opus/haiku/fable), never
  two lenses on one model, model attribution in reports. (3) Empirical dreams:
  auto-dev section 4c — 2 experiments/30min/night budget, probe recipe ->
  measurement -> teardown -> (hypothesis, measurement, verdict) on bus;
  proposals marked empirical vs speculative; null results are results. (4)
  Outcomes flywheel: dream_math now reads the REAL ledger
  (garden-reports/proposal-outcomes.jsonl — 11 records); posterior P(accept)
  0.887; `flywheel` subcommand shown at the top of every /proposals session;
  logistic fit unlocks at 20 decisions.


- **v0.4.0 (82d3cc4) — THE DREAMING TEAM.** Josh: dreamer matters most to him;
  dreams must be lateral-thinking connections across ALL professional domains,
  with math self-evaluation. Built: (1) kb/lateral.py — hidden-connection engine,
  concept co-occurrence graph from TECHNICAL sources only (blog prose = filler;
  blog rejoins as bridge evidence), PMI-chance-corrected edges, binary-adjacency
  vectorized Adamic-Adar (numpy; pure-python was 15+ min CPU, vectorized 2-5s),
  hub filter MAX_DF 3% + hard MAX_DIRECT co-occurrence filter — output = concept
  pairs the corpus never states together; (2) kb/dream_math.py — proposal math:
  Beta(2.2,1.3) posterior P(accept) updated from outcomes ledger (logistic
  regression at n>=20 — outcomes ledger was EMPTY at build: first outcomes start
  the data flywheel), EV + break-even sensitivity, assumption registry with
  nightly re-check (assumption-regression on standing proposals); (3)
  kb/dream_entropy.py — memory-state entropy report (claims redundancy/
  contradiction/staleness + knowledge-file gini/size-entropy) = the Complexity
  term of Surprise ~= Complexity - Accuracy; first run: claims healthy, gini
  0.71 (knowledge concentrating — gardener signal); (4) dreamer SOP: the Board
  (Doctor/Lawyer/Artist/Musician/CEO/Engineer/Accountant/PM/CTO, 2-3 rotating
  nightly, full tour weekly), math block mandatory on every proposal card,
  lateral top as input feedstock, entropy-exploitation framing (gardener
  minimizes memory entropy, dreamer exploits it).


- **v0.3.0 (9a59581) — ROADMAP COMPLETE + FAN-OUT LIVE.** LLM contextual headers
  (ollama qwen2.5:3b-instruct local, incremental 400/night, contextualize zeroes
  sha to force re-chunk), Confluence attachments machinery (v2 API, extraction
  proven; corpus turned out to be ~all images — fine), nightly digest fan-out
  (kb/digest.py: 6 agents, lens queries + change surface -> knowledge/kb-digests/),
  sync pipeline order sources→attachments→contextualize→index→pmi→entropy,
  launchd sync moved 21:37 + digest 22:07 (both BEFORE the 22:15+ agent fleet),
  5 agent SOPs wired (opinions to bus, proposals stay dreamer's), dreamer
  creativity protocol (multi-lens fan-out: Architect/Contrarian/Analogist;
  forced-variation frames; rejection mining; draft-attack-revise; monthly
  hit-rate), /kb slash command (skills/kb), kit packaging pushed (baf6863:
  kb-pipeline/ code-only + both skills + schedule; data gitignored).


- **v0.2.0 (5b6e6fc) — PHASE 2 LIVE.** Final score = rerank × (1 + 0.15·entropy_norm)
  × (1 + 0.10·pmi_norm). Retrieval-distribution confidence gate: expand to a second
  round ONLY when distribution entropy > 0.9 bits AND top rerank < 0.5 (flat-among-
  strong is confidence, not uncertainty — that guard was probed and matters). PMI =
  Σ log2(P(t|chunk)/P(t|corpus)) normalized per query term; term stats persisted
  (53K terms / 5.7M words, `index/terms.json.gz`), auto-built if missing.
- Integrity verified: 10,274 docs / 63,952 chunks / vec rows == chunks / entropy on
  all chunks / all 9 sources present.
- Confluence sync LIVE with Josh's token (v2 pagination + storage→markdown; v1 CQL
  search broken on this tenant — cql arrives EMPTY server-side, don't retry that
  path). Keychain account = **josh.cramoy@workato.com** (dot — <user>@ 403s).
  Sync proven idempotent (second pass 0 changed).
- Manifest keying rule (bit hard): manifests are keyed by URL everywhere — mixing
  id-keys and url-keys doubles counts and defeats sha change-detection.
- docs_source gotcha: manifest paths must carry the "docs/" prefix AT SOURCE
  (local_path_for); a resync rewrites path fields, so the fix must live in the
  module, not a one-off manifest patch (bit twice in one night).
- v0.1.1 committed (ab90e87): 9 sources smoke tests PASSED live (null-datapill →
  0.99 rerank; EIP Aggregator correct; kb.read citation path verified).
- Known entropy edge (probed): raw unigram entropy over-favors proper-noun lists;
  handled by rerank gating, phase-3 candidate = IDF-style doc-frequency scoring.
- Dreamer mandate LIVE: nightly KB review (change-surface diff + targeted RAG
  queries + modality discovery), Sunday full-corpus pass.
- Wiring: grill-gate (KB self-answering), workato-development-playbook, platform-
  onboarding (llms.txt ingestion tip), harness-dreamer Mandate B2.
- Remaining roadmap: LLM-generated contextual chunk headers, Confluence
  attachments (PDF), fleet packaging of public sources into the org kit repo.
- BOSS-FACING RATIONALE (for the local-advantages question, 2026-10-08):
  cacheable (one-time fetch, zero per-question web calls), indexable (FTS5 +
  embeddings + entropy over the whole corpus in milliseconds), RAG++-supportive
  (hybrid retrieval, contextual chunking, rerank, agentic loop — none possible
  against live web pages), cheap etag/diff sync keeps it current, private
  (Confluence never leaves the machine), and it compounds (dreamer mines it
  nightly; every session reuses the same indexed corpus).

## Gotchas found building it

- urllib in sync_wp needs query-separator logic when the API base already has
  `?` params (categories=443&per_page=...) — 400 Bad Request if naively appended.
- blog2workato WP install: category IDs 443 (What's New) vs 444 (Monthly Product
  Scoop) both look like changelogs; 443 is the real one.
- Atlassian MCP getPagesInConfluenceSpace overflows the MCP token window at
  250 pages/call → auto-saves to a tool-results file; ingest from the file, never
  read it into context (kb/confluence_ingest.py does exactly that).
- python3.14 (homebrew default) has no torch wheels — venv pinned to python3.12.

## 2026-10-09: sync.py overwrite incident + restore (dev fix, triage-approved)

- Commit `fa0447a` replaced the ENTIRE 152-line kb/sync.py orchestrator with the 65-line
  jira_bulk_pull body (Jira-only nightly). Restored same day from `2a1713e^:kb/sync.py`
  with the jira-cases step re-wired (Sunday-only or `--sources jira-cases`). Uncommitted
  working-tree loss is why sync.py must NEVER be regenerated by pasting a step's body
  over the file — a scoped run of a new step ships as a diff, not a whole-file rewrite.
- sync.py now carries two guards (from cortex investigation kb-sync-source-shrink.md):
  (1) `"scope": "full"|"scoped"` in the diff report + bus summary line — the 03:22
  "1 of 15 sources" report was a scoped run indistinguishable from a nightly full run;
  (2) source-count floor on full runs: any of the 8 CORE_SOURCES missing/failed, or
  0 total changed vs nonzero previous report, -> floor_failures in report, sync_alert
  bus post, exit 1 (report still written first). Scoped runs never trip the floor.
- Live-verified: scoped docs run (2808 changed, scope flag present), venv python clean
  (system python3 lacks sqlite_vec — always test with .venv/bin/python, that is what
  launchd runs), floor test cases A/B/C via stubbed steps + temp DATA_ROOT.
- Bus recovery gotcha: workato-kb.jsonl is git-tracked in the knowledge tree — after
  accidental truncation, `git checkout -- dreams/bus/workato-kb.jsonl` then re-append
  post-commit lines from session context.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [The Workato KB: RAG++ over all documentation, and the dreaming team](../../kb-corpus/confluence/extbt/2938929237-the-workato-kb-rag-over-all-documentation-and-the-dreaming-team.md)
- [Workato Labs: What&#8217;s New](../../kb-corpus/blog/workato-labs-whats-new.md)
- [2024/12 + 2025/01 December/Jan Lookback](../../kb-corpus/confluence/intbt/542703625-202412-202501-decemberjan-lookback.md)
<!-- kb-bridges:end -->

## Graph layers ablation (2026-10-10 night, Josh-approved build 1-4, swarm of 3 + integration)

Built and MEASURED against a 235-query eval set (200 in-source + 35 cross-source; seed-42 stable):
- Baseline: Recall@10 0.9000 overall / 0.9625 in-source / 0.5429 cross-source; MRR@10 0.6518.
- Entity edges (kb/edges.py, 13,214 cross-source edges, per-source IDF, provenance cols) + 1-hop
  expansion (search.py `_edge_neighbors`, KB_EXPAND=1 gate): Recall@10 +0.0000 EVERY slice.
  Structural cause: of 15 zero-recall failures, ZERO have the expected doc 1-hop edge-adjacent
  to a top-10 hit. Failures are RANKING failures (sibling-doc hard negatives, cross-source
  crowding), not reachability failures. Expansion fires on 43% of queries, recruits never crack
  top-10 (first-chunk intros rerank low). KB_EXPAND left default-off.
- Hub notes (kb/hubs.py, AgglomerativeClustering dist 0.85 after sweep; HDBSCAN degenerates to
  one blob on dense bge space; 110 hubs, 1,553 member links all resolving, self-pollution guard)
  ingested as `hubs` source: Recall@10 +0.0000; hubs reached top-10 on 13/235 queries; 4 MRR
  movers, net -0.0007. Recall-neutral.
- KILLED BY MEASUREMENT: entity-edge retrieval expansion, hubs-as-recall-lever. Both were the
  predicted survivors (mine AND Kimi's) - the eval killed both predictions. Calibration event.
- SURVIVED: eval harness (permanent, exposed real failure modes); links.py normalization (28k
  real graph edges - the Obsidian value); hubs as browsing constellations + coarse zoom layer
  (fractal topic nodes; token-cost dimension UNMEASURED - that was hubs' real claim all along).
- Real next lever (evidence-backed): ranking quality, not graph structure. Recall 0.90 with MRR
  0.65 = docs present but ranked wrong; sibling disambiguation + cross-source crowding are the
  failure classes. Graph edges cannot fix this; reranker enrichment might.
- Swarm pattern worked: 3 builders on disjoint files (edges.py/hubs.py/eval.py), integration
  (search.py/indexer.py/sync.py) held by the session; zero collisions; guarded imports so the
  nightly sync survives missing modules.
- Obsidian stub trap (from bridges): clicking unresolved links creates 0-byte stub notes;
  corpus dead .html links were the cause; new-note default location -> zz-stubs folder.

## Rung repair + ranking wins (2026-10-10 early morning, swarm of 5 + integration)

- RANKING FIXED (the night's real retrieval win): sibling title-overlap tiebreak
  default-ON in search.py. MRR@10 0.6469 -> 0.8675 overall (+0.22), hard-sibling
  slice 0.635 -> 0.97, cross-source recall +1.4pt, ZERO recall losses. Torn-pass
  (KB_TORN) available; KB_CAPS ablated DEAD (-0.04 recall every slice); KB_EXPAND
  dead (previous entry); KB_POOL stays default 4 (pool8: 3 recall wins vs 1 loss,
  not default).
- FRACTAL RUNGS REPAIRED: sections 392 -> 58,464 factlets (81.3% file coverage),
  topics 1 stub -> 110 hubs, chunks healed to 66,428, orphans 15+10,839 -> 0.
  kb.fractal_audit OVERALL PASS (bars: sections>=80%, chunks>=95% of chunkable,
  topics>=20 no stubs, orphans 0). Root causes fixed at emitter level: claims
  emitter invented nonexistent parent ids; kt/agent/skill/memory emitters
  parented to the deleted root stub; single-chunk docs skipped chunk emission.
- ZOOM CLAIM FIRST MEASURED (kb/zoom_eval.py): cheap-path answers 64% -> 92%,
  section answers 242 tokens median, zoom-vs-file ratio 10.4x (in the claimed
  10-30x band). Answer-QUALITY not yet scored (cost only).
- AUDITOR GOTCHAS (paid for): by_level rows are (fid,tlen,parent,source) 4-tuples
  - r[4] indexing silently emptied a set; corpus L1 sources are URLs but L2/L3
  conventions mix URLs/paths - coverage must resolve via PARENT CHAINS not
  source strings; 'hubs://' is not caught by startswith('hubs/'); chunks_pct
  must divide by the CHUNKABLE denominator not the sections one.
- BOTH REPOS PUSHED: workato-kb 273d396, workato-agentic-kit 7aca928 (package
  copy synced identical).

## Scout expansion wave 1 (2026-10-11, Josh mandate: "mine the best AI-eng/systems/integration/automation/CS sources")

8 parallel scout agents (5 domains + 3 follow-on: AI-eng, systems-arch, integration, automation, CS-foundations, databases, NN, neuro/psych/bio-applied), each live-verifying ingest paths. 16 sources landed through the EXISTING chain (design-gate win: no new pipeline code paths, adapters only):

- **llms.txt sites** (`kb/llms_source.py` SITES): temporal (86p), n8n (1364p, 0 errors), prefect (332p), restate (221p), mcp (362p), snowflake (59p, top index only), dbt (1309p). `parse_llms` now tolerates `##`-section files (Temporal shape); relative TOC URLs absolutized; slugs strip `.md`.
- **git repos** (`kb/github_source.py` REPOS, +14): azure-architecture-center (503), google-aip (131), hacker-laws, standard-webhooks, asyncapi-spec, cloudevents-spec, openai-cookbook (159), anthropic-cookbook (77), d2l-en (3718!), cs231n-notes (66), nn-zero-to-hero, build-nanogpt, spinningup, duckdb-web.
- **RSS/Atom** (NEW `kb/rss_source.py`, 16 feeds): Morning Paper (**1,086-post backfill** via WP `?paged=` — the whole evergreen archive), danluu, jvns, simon-willison, latent-space, chip-huyen, eugene-yan, hf-blog, anthropic-eng (community feed), aws-arch-blog, cloudflare, netflix, fowler-bliki, lilian-weng, hamel, cynefin. BACKFILL_CAPABLE walks WP archives; thin (<500 char) entries recorded-but-skipped.

All new steps are CORE_SOURCES (nightly floor fails loudly if any die). **Regression gate for ANY corpus change: `kb.eval --run --tag X` before + after, `--compare` for the delta** (pre-scout baseline: overall R@10 .909, MRR .863, n=275; cross-source slice is the weak one at .514 — watch it). Scout reports preserved in session; wave-2 (static-HTML: SRE books, MIT 6.824, use-the-index-luke, Jepsen, Kimball, Nielsen, distill, jalammar, Gregg, microservices.io, Neuroscience Online, Nature of Code, AskNature, Camel .adoc) queued in README Roadmap. Licensing: cookbooks/Azure/AIP/AsyncAPI/CloudEvents/webhooks/d2l MIT/Apache/CC-BY (clean); blogs are all-rights internal-RAG-only — never republish.

Gotchas paid for: llms.txt sites disagree on heading level (`##` vs `###`) and emit relative URLs; progress prints break `| python3 -c json.load` pipes (tail first); acolyer wp-json REST is disabled (use feed `?paged=`); trigger.dev llms.txt is prose-shaped (needs custom parser, deferred); HashiCorp docs explicitly forbid bulk ingest (cite-by-link only).

## Scout-expansion build details (2026-10-11 night, continued)

**Indexer discovery made fully dynamic (the important fix).** `_doc_iter`'s hardcoded source dict silently excluded every scout source (temporal/n8n/prefect/restate/mcp/snowflake/dbt/rss) — the EXACT bug class as the 2026-10-10 confluence fix, and it recurred because the fix special-cased confluence instead of generalizing. Now: sources = every `manifest/*.jsonl` stem; a newly-wired source syncs+manifests+indexes with zero code. Index after build: 21,553 docs / 138,267 chunks (was 16,504/103,322).

**One corrupt row killed two nightly steps** (`temporal` + `links` both KeyError 'url'): a single url-less row in temporal.jsonl. `common.load_manifest` now skips url-less rows instead of failing the nightly — corrupt-row isolation is the loader's job, not every caller's.

**Eval (the regression gate) — honest numbers:** pre→post overall R@10 .9091→.8945 (−1.5pp), MRR .8629→.8505 (−1.2pp), cross-source .5143→.4714 (−4.3pp), in-source MRR UP (+0.5pp at .888). Named winners (xs-023/024, in-070/104/122 flipped 0→1) and losers (xs-005/022/029, in-107/110 halved). Interpretation: the eval's expect_urls are Workato-only, so adding 5k external docs can only displace, never score — the cross-source dip is dilution physics, in-source quality held. **Follow-up worth doing: regenerate the eval set with new-source slices (it cannot measure the expansion's gains today) + consider source-affinity weighting for Workato-slice queries.**

**Fractal audit FAIL is an accounting artifact, not retrieval damage:** sections 75.67% vs 80% gate. Direct store query: only 22/11,919 level-1 factlets (0.2%) truly lack level-2 children. The audit's 2,801 uncredited files are 2,553 URL-source level-1 factlets (emitted by the section-pass heal path with source=url instead of relative path) + 189 unlabeled. Chunks 99.78% PASS, topics PASS, 0 orphans. **Wave-2 fix: normalize the heal-path source convention OR extend the audit's crediting to URL-source files; do NOT lower the gate.**

Live retrieval proven on new sources: Temporal deterministic-replay pages, Azure Center outbox/saga/compensating-transaction canon, CS231n+d2l attention math — all cited. Resident daemon needs NO restart (search opens a fresh DB connection per query via get_db()).

## Scout wave 2 (2026-10-11 day, Josh: "do the second pass")

**`kb/html_source.py`** — generic static-HTML crawler (eip_source idiom): per-site config (starts, include/exclude regex, hops, max_pages, sitemap option), shared html_to_markdown, one shared "webcrawl" manifest/corpus dir with per-site rows. **3,090 docs crawled** across 14 sites: SRE books (143 chapters — all four books), MIT 6.5840 (23 lecture notes), Use The Index Luke (289), Jepsen analyses (33), Kimball (130), Nielsen NN (7), distill (4), jalammar (30), Brendan Gregg (289), microservices.io (135), Neuroscience Online (63), AskNature (~1,900 strategy cards), Numenta, Hermans, FEP essays. Registered as CORE_SOURCES step "webcrawl". Post-build: **24,643 docs / 165,005 chunks**; fractal OVERALL PASS on the full corpus (sections 96.59% of non-flat, chunks 99.9%, 216 topics, 0 orphans); eval post-wave2 == post-scout overall (R@10 .8945, MRR −0.2pp — wave 2 added ZERO displacement; wave 1 took the dip).

**Fractal audit sections-gate fixed properly (OVERALL was FAIL at 78.68%):** root cause chain — (1) fractal.db was a day stale (nothing in kb.sync rebuilds the projection — watch this, projection drift is now a known risk); (2) section pass by-design skips headingless docs (chunks hang straight off the file rung — "nothing to section here"); (3) audit counted those as failures. Fix: `_flat_headingless_docs()` excludes docs whose kb.db chunks have zero ##/###-initial chunks (same spirit as hubs exclusion); `norm_src` maps URL-source level-1 factlets onto doc paths via kb.db url↔path. **Paid gotchas: `re` wasn't imported in fractal_audit (NameError → silent except → exclusions silently empty — the degrade path ate its own bug); `kb.fractal` requires the `build` subcommand; nature-of-code + distill are now JS-rendered apps (crawler can't see links — wave-3 needs git/sitemap routes).**

Wave-3 queue (README Roadmap): distill + Nature of Code via git/sitemap, Camel .adoc→md, selective Postgres slices, AWS WAF, trigger.dev parser, Snowflake depth, **eval-set regeneration with new-source slices** (still can't measure the expansion's gains).

## Wave 3 + outstanding-fix sweep (2026-10-11/12 night, Josh: "fix all of these")

ALL wave-3 sources landed and indexed: distill (52, via distillpub per-article git repos — `public/index.html`, branch varies master/main, resolved via GitHub API — `html_source.py` `_collect_distill`), Nature of Code (19, via noc-book-2 content html→md at ingest — `github_source` HTML_REPOS set + sync-loop conversion), Apache Camel (812 via sparse clone + Pydowndoc + drop-templated-includes preprocessor — NEW `kb/camel_source.py`; pydowndoc needs the venv bin ON PATH — patched at module import), PostgreSQL core chapters (72, selective 5-chapter crawl), AWS WAF framework (48), trigger.dev (.md twins, 15), Snowflake FULL manual (8,922 — recursive section-llms walk in `llms_source.sync`, depth 1).

**Final state: ~34k docs / ~200k+ chunks. Gates: fractal OVERALL PASS on the full 35.5k-file corpus (sections 97.57% of non-flat, chunks 99.93%, 258 topics, 0 orphans); eval R@10 held .8945 through the doubling; in-source recall UP .9475→.9525.** MRR drift (.849→.833) = the Workato-only-expectations dilution artifact — the eval set was REGENERATED (275 queries now sampled corpus-wide) and `results-baseline-postexp.json` (R@10 .8945 / MRR .8312) is the NEW regression reference.

Paid gotchas: my dead-block deletion ate `_collect_distill` (NameError → webcrawl floor failure — the loud floor WORKED as designed); `_collect` must return {page_url: fetch_url} in ALL branches; TocEntry kwargs collide on `section` when merging nested-llms entries (build kwargs dict + update); camel INCLUDE_DIRS glob dirs not files (rglob under each); Postgres `perform.html` 404s (slug is `performance-tips.html`); natureofcode.com + distill.pub archive are now JS-rendered Gatsby apps.

Open (small): Snowflake IncompleteRead pages retry on next etag sync; optional hand-authored new-topic cross-source eval slice; source-affinity weighting for Workato-slice queries (proposed, not built).

## Wave 4: Slack developer docs (2026-10-14, Josh: "we do so much work in Slack")

**Source `slack` = docs.slack.dev** — first-party llms.txt PLUS `llms-sitemap.md`
(full machine-readable page list). Rationale: recipes post to Slack, bots get
built, the slack-workato MCP is wired — platform canon belongs in the corpus.
Committed 69d823b (also consolidates uncommitted wave-2/3 fixes).

- **New generic adapter** in `kb/llms_source.py`: `SITEMAPS` dict — llms.txt is
  curated (top pages only), the sitemap has EVERY page. Sitemap bullets are
  bare URLs (no titles) → `parse_llms` regex misses them; `_sitemap_entries`
  merges the full list, section = first URL path segment, title backfilled
  from the page's first `# ` heading at fetch time (slug as fallback). Tail
  TOC-refresh loop only updates titles when the TOC entry HAS one.
- **3,274 en-only pages** final (88 ja-jp locale twins + 6 llms-full*.txt
  whole-site dumps filtered — en-only rule as with Workato docs). Sections:
  tools 2,192 (Bolt/CLI/SDK), reference 756 (API methods/events/scopes),
  changelog 243, ai 29. Corpus: 38,787 docs / 250,875 chunks.
- Gates: fractal OVERALL PASS full corpus (sections 97.58% / chunks 99.92% /
  366 topics / 0 orphans). Eval vs baseline-postexp: in-source −0.5pp (1 of
  200 queries), hard-sibling 1.0 flat, cross-source −4.3pp (n=35, dilution
  physics per wave-1 precedent), cross-source MRR UP (+4pp). Live probes:
  chat.postMessage + Bolt-Python button handling → exact Slack pages top.
- Registered: CORE_SOURCES + the scout llms-site loop in sync.py (own step, so
  the nightly floor fails loudly if the site dies).
- Gotchas paid: Slack's server 304s inconsistently and drops connections
  (Remote end closed) — flakes self-heal on next etag sync; distinct pages
  can collide in slug space (rtm/v2.md vs rtm/rtm_v2.md) → short-URL-hash
  suffix, deterministic; a 304 on a URL with no stored record persisted a
  PATHLESS manifest row (the corrupt-row class again) → 304 branch now
  refuses pathless records; llms.txt also links llms-full*.txt single-file
  dumps that duplicate every page — sitemap sites filter to .md entries.
- **Integrity sweep findings (same night, from Josh's end-to-end question):**
  a build KILLED mid-embed strands committed chunks vectorless FOREVER (only
  chunks inserted in a run are embedded; later runs skip unchanged docs) —
  4,535 slack chunks had no vec rows. Fixed in indexer (20e297f): build()
  backfills any chunk missing a vec row, every build. Also purged 31 orphan
  vec rows; wiped + clean-rebuilt fractal.db (934 duplicate file factlets
  from the interrupted build; now 3,274 file factlets = 3,274 docs, 0 dupes,
  audit OVERALL PASS, chunks rung 250,875 == corpus chunks exactly). Rule of
  thumb: after ANY killed kb process, run the integrity probe (vec==chunks
  per source) — gates can pass on a damaged projection.
- **Watchdog hardened (same night, commit 0d82d68 in knowledge repo):** the
  kb-audit fleet job (3x daily 07:37/14:07/19:37, 9 checks, bus findings) had
  TWO defects — (1) no missing-vec check (blind to the stranded-chunk bug —
  now checked, FAIL if any chunk lacks a vector; vec0 rowids-table rowid IS
  the chunk_id, the chunk_id column is a partition id, never join on it);
  (2) hardcoded manifest list → drift read 133% forever (now glob +
  thin:true rows excluded, drift 0.01%). File checks now age-aware: fresh
  unindexed (<48h) = WARN "not yet", stale = FAIL. Live-reorg race caught
  same-day: root-cause-2026-10-10.md flagged stale-unindexed — real cause =
  another session moving it into a renamed project dir; heals at 21:37.


## Wave 6: Atlassian developer docs (2026-10-15, Josh: "ingest JIRA developer docs — JSM Cloud, Jira Cloud Platform, Jira Software Cloud, Confluence Cloud, maybe Build with AI")

**Source `atlassian` = developer.atlassian.com/cloud** — no llms.txt, but two
better DAC-specific discoveries. New adapter `kb/atlassian_source.py`, commit
9e891de. Nightly wiring (sync.py try_step + CORE_SOURCES) rides the in-flight
wave-5 commit — sync.py is entangled with uncommitted wave-5 work, did not
commit it from this session.

- **KEY DISCOVERY 1 — every DAC doc page embeds RAW MARKDOWN** in
  `window.__DATA__.page.document` (a list of `{type: markdown|shortcode,
  content}` blocks; page title in `page.metadata.title`). No HTML conversion —
  parse the JSON blob with a string-aware brace scanner, join blocks
  (shortcodes → blockquotes). 380 guide pages across 6 trees.
- **KEY DISCOVERY 2 — REST reference pages embed the full OpenAPI spec**
  (`window.__DATA__.swaggerUrl`, e.g. `/cloud/jira/service-desk/swagger.v3.json`).
  Expanded ONE DOC PER API TAG (~222 group docs: jira-cloud 102, confluence
  96, jira-software 14, jsm 10) with method/path/summary/scopes/params/
  request-body-ref/responses per operation. The sitemap's api-group-* pages
  are renderings of the same spec — NOT fetched; unmatched tags get a
  synthesized api-group-<tag>/ URL key. Intro doc carries info.description +
  x-atlassian-narrative + servers.
- Trees: jira-cloud 251, jira-software 108, jsm-cloud 107, confluence-cloud
  121, rovo-mcp 7, rovo-a2a 10 sitemap pages. "Build with AI" is a NAV
  CATEGORY, not a tree — its content lives in rovo-mcp/rovo-a2a. Corpus +
  652 files (7.5MB), source `atlassian`, section = product slug
  (`--source atlassian --section jsm-cloud`).
- **Traps canonized:** (1) DAC's CDN sheds load — at the shared pool's 12
  workers ~1/3 of pages return status 0 with rotating victims; source runs
  its own 4-worker pool + 3 backoff retries, and transient stragglers are
  swept on re-run (never treat one run's `skipped` as final). (2) 304s hide
  the payload: a root page or swagger JSON fetched with a stored ETag returns
  304 + EMPTY BODY, which silently skips the whole REST expansion — REST
  roots and swagger JSON always refetch fresh (few files; sha-skip
  downstream). (3) `site_urls` rstrips trailing slashes, so
  `.../service-desk/rest/` became `.../rest` and fell through BOTH handlers —
  normalize the path to a trailing slash inside `_rest_root_of` and match
  fetched-dict lookups on both forms. (4) `u.rstrip("/")` + per-tag URL keys
  mean manifest URLs for REST docs carry the trailing slash; sitemap URLs
  don't.
- Ingest chain ran full (links→index→edges→pmi→entropy; 43,411 chunks
  embedded, index now ~41k docs) + `kb fractal build` (81,330 factlets,
  coverage AIRTIGHT). Live probes: JSM customer-create REST → exact
  api-group-customer top; ADF structure → exact page; Rovo MCP zoom →
  Getting-started/Overview chunk+section+file levels all from `atlassian`.

## Wave 5: Josh's external-source crawl mandate (2026-10-15, commit 404743f)

Josh dropped 14 sources ("crawl, extract, bend the rules, set up pipelines so
nothing gets stale"). Three parallel builder agents + session integration; the
commit ALSO carried wave 6's uncommitted workday/atlassian wiring (same repo
dirty — check `git status` BEFORE building on it; both sessions landed).

- **Landed, all CORE_SOURCES (nightly floor covers them):**
  `hf-datasets/hub/transformers/diffusers/peft/accelerate` (1,604 pages via
  llms.txt + .md twins, version segment STRIPPED for stable URLs — a release
  updates in place, never duplicates); `pwc` (Papers-with-Code dumps from
  pwc-archive parquet on HF: 15,008 dataset cards + 8,725 method cards + 8,000
  SOTA benchmark tables, cap from 11,778); `apis-guru` (2,519 API cards, specs
  LINK-only); `terraform-registry` (5,560 namespace catalogs over 7,437
  providers, metadata-only per HashiCorp's no-bulk-ingest rule); `figshare`
  (budgeted firehose-verify: 8 verified first tranche, 120-detail/5-min budget
  per sync); `developer-roadmap` (11,046 pages via NEW sparse blobless clone —
  the nilbuild fork's content lives in `roadmaps/` not `content/`); 8
  webcrawl single-article sites (NECI universality, Red Hat self-healing, Azure
  WAF self-preservation +reliability cluster, GfG self-healing, Confluent +
  IBM EDA, zcking Medium EDA, arXiv 2504.21048) via NEW `self_start` option.
- **llms-scout pipeline (NEW, report step — never core):** mines
  SecretiveShell/Awesome-llms-txt + thedaviddias/llms-txt-hub into
  `scout/llms-site-queue.jsonl` — 2,849 sites (2,849 queued / 2 already
  ingested / 9 spam rejected). THIS is the "keep mining" pipeline: Josh or a
  future wave picks from the queue; auto-ingest deliberately out of scope.
- **Corpus 38.8k → ~95k docs / 355,516 chunks. Gates: fractal OVERALL PASS
  (sections 98.26%, chunks 99.48%, 0 orphans, 31 orphan vec rows purged);
  eval vs results-baseline-postexp: overall R@10 .8945→.8782 (−1.6pp),
  cross-source MRR +6.5pp, hard-sibling 1.00 flat — the dilution-physics
  signature again (corpus +141%; verified the biggest loser query's expected
  doc exists, crowded out by its own siblings: ranking artifact, not loss).**
- **Live probes all hit new sources**: ImageNet SOTA → pwc SOTA tables; ReAct
  → developer-roadmap ai-agents; self-healing playbook → Azure+GfG; RAG
  chunking → roadmap ai-engineering; EDA → Confluent page.
- **Paid gotchas (wave 5):** (1) HF rate-limits bulk fetches HARD (429 +
  retry-after: 60) — fixed with a process-wide 429 circuit-breaker in
  common.py honoring Retry-After; a retrying worker pool re-trips the limit
  in synchronized bursts. (2) figshare `/v2/articles/search` IGNORES category
  filters (category_id and categories both verified ignored) and offset caps
  at 1000; OAI-PMH is a dead end (202 forever). (3) apis.guru catalog =
  `api.apis.guru/v2/list.json` (2.5k keys, top-level). (4) Terraform
  `/v1/providers` clamps offset at 100 — `/v2/providers` (JSON:API) is the
  walkable one. (5) links.normalize rewrites corpus files IN PLACE → github
  clones go dirty → ff-only pulls fail silently until upstream touches those
  files; `_update_repo` now resets dirty trees before pulling (9 clones were
  blocked). (6) Red Hat architect pages are JS-rendered (crawler sees a nav
  shell) — one-off ingest via rendered fetch (fireworks web_fetch renders).
  (7) The audit's flat-doc exclusion + needs_chunks denominator silently
  ignored pseudo-URL sources (pwc://, workday://) — fixed in fractal_audit
  (norm_src resolves ANY docs.url key, not just http). (8) PwC methods dump
  carries ~5-8% call-center-spam rows (467 flagged, `spam_likely_methods` in
  the summary) — pre-emission filter is a follow-up if Josh wants.
- **LangChain Hub (smith.langchain.com/hub): probed, NOT ingested** — the
  public list API 404s everywhere; only per-prompt
  `api.hub.langchain.com/repos/<owner>/<repo>` works. The hub index page
  renders via fireworks fetch (top prompts: hwchase17/react, rlm/rag-prompt…).
  Ingest as a wave if Josh wants prompt canon — needs the directory listing
  scraped per-page, not an API.
- **Josh follow-ups surfaced by builders:** pwc methods spam filter (above);
  figshare backlog pacing (nightly 120-detail budget vs ~70-170/hour churn).

### Wave 5b collision note (2026-10-15, this session vs wave-5b session)

- This session committed `langchain_hub_source.py` + sync wiring (33946bf) with
  the scoped-prune fix (a `--pages N` run must never prune what it didn't
  walk — a 1-page pilot pruned 5,885 rows/files). The wave-5b session then
  hardened the same module on disk with the complementary fix: a `complete`
  flag so 429'd LISTING pages never trigger prunes + a serial retry sweep.
  LEFT UNCOMMITTED for that session to land (active file ownership).
- **New trap: concurrent syncs on one source.** Two full langchain-hub syncs
  ran at once (both sessions reacting to the prune) → manifest 9,730 rows vs
  4,033 files on disk (save_manifest is whole-file last-writer-wins; 429
  breaker also tripped mid-restore). **Second trap inside it: a manifest row
  whose corpus file is missing is sha-skipped as unchanged** — the sig check
  never looks at the file. Repair recipe for the wave-5b session: delete
  manifest rows whose `path` file is gone, then one full sync after the Hub
  rate-limit cools, then `kb.ingest --quick` + `kb fractal build`.
- Sync registry verified COMPLETE this session: 30 core sources, every one
  wired (hf-* and llms.txt sites via loops), imports clean under venv 3.12.
  (Ad-hoc multi-import test scripts hit a weird `inspect`-patching side
  effect + semantic-gateway EVENTS dump — startup hook artifact, not a repo
  defect; test source modules with `python3 -m kb.<mod>` in fresh processes.)

## FULL-CORPUS SEARCHABILITY AUDIT (2026-10-16, after the ASEE gap made Josh ask "what else?")

Two silent gaps found and fixed, both the same class: ingested but never wired.

- **GAP 1 — BM25 leg dead since inception.** `chunks_fts` is external-content
  fts5 with NO populate path anywhere in indexer.py — the index had 0 rows
  even in the 2026-10-08 backup. Every search ever ran dense-only; the
  "hybrid" was a lie. Fix: `build()` now runs the fts 'rebuild' command
  after every build (~11-20s for 386k chunks — cheap, exact). Eval
  before/after (275 queries): overall recall .8945→.9055, MRR .8312→.8510,
  cross-source MRR +5.5pp; hard-sibling −2.5pp (sibling tiebreak was tuned
  dense-only — retune candidate). results-fts-restored.json is the new
  regression reference. Lesson: the eval measured the system as-built, so it
  never noticed a whole dead leg — an eval can't test for components that
  contribute nothing.
- **GAP 2 — snowflake/dbt/trigger had no nightly step** (ingested waves 1/3,
  never wired into sync.py or CORE_SOURCES). Wired into the llms loop +
  CORE_SOURCES; scoped sync ran (dbt 912 changed, trigger 28, snowflake 1).
- 31 orphan vec rows purged (chunks deleted after embed; indexer purge SQL is
  keyed right, the rows predate it). Integrity now: vec 386,586 == chunks,
  0 vectorless, 0 orphans. Fractal audit OVERALL PASS.
- Vestigial: `morning-paper.jsonl` empty (content lives under rss) — harmless.
- All 40 sources live-probed; per-source availability OK (the crude
  generic-term probe is a weak discriminator — github floods generic queries
  at 16k docs; the eval is the real gate).

## Workato org code ingest (2026-10-16, commit be7e99b, Josh: "ALL of the workato code")

- The two vendor-canon SDK repos were cloned 2026-10-13 but the md/html rule
  ingested only 4 files — the knowledge IS the Ruby source. New
  `CODE_EXTENSIONS` in github_source ingests .rb/.gemspec (SDK: 173 docs),
  .rb connector examples (custom-connector-docs: 95), .java/.yaml
  (opa-extensions: 3), .yaml/.tpl (edge-gateway-helm-charts: 10). +302 docs.
- Org survey: the rest of github.com/workato is Ruby OSS forks (internal
  infra); the dev-relevant set is now complete. Embed samples
  (full-embed-sample, connection-embed-sample) noted, not yet ingested —
  Vue apps, low doc value.
- Synthesis docs dispatched (sibling agents): domains/workato-sdk-internals.md
  (SDK ground truth from code) + domains/workato-dev-apis.md (full dev-API
  inventory with citations) — both end with product-feedback sections.

## Confluence spaces nightly-gap fix (2026-10-16, commit 10bb410)

ASEE (Forward Deployed Engineering) was backfilled 2026-10-10 (commit 57c50ee)
but the nightly `_confluence_best_effort` loop only covered ("extbt", "intbt")
— asee/gears/cssup went stale. Fixed: loop iterates `confluence_sync.SPACES`
so future spaces are nightly by default. Scoped sync ran live (asee 180 seen /
1 changed, gears 176 changed, cssup 380 changed) + index rebuild (722 docs
updated, 2 added, 2,924 chunks embedded, 0 vectorless). KB probe verified:
"Customer 360 process MCP user guide" → exact ASEE page (`confluence/asee`).

## Wave 5b: LangChain Hub prompt catalog (2026-10-15, Josh: "go nuts", commit 32453f1)

Correction to the wave-5 line: the public list API DOES exist — the morning
probe hit the wrong paths. `GET api.hub.langchain.com/repos?limit=100&offset=N`
→ `{repos: [...], total}` (10,322 public prompt repos: tags, likes, downloads,
views, num_commits, last_commit_hash); `GET /commits/<owner>/<repo>` →
serialized prompt manifests. New `kb/langchain_hub_source.py`:

- **Template extraction = recursive walk** of the manifest — `template` sits
  at `kwargs.template` (PromptTemplate) or nests under
  `kwargs.messages[i].kwargs.prompt.kwargs.template` (ChatPromptTemplate);
  collect every {template, template_format, input_variables} node (14,838
  templates total, multiple per repo).
- **Change-sig skip**: nightly fetches only repos whose
  updated_at/num_commits/last_commit_hash changed.
- **9,961/10,321 repos landed (96.5%)** — ~47 rotating 429 stragglers per
  pass (DAC-style rotating victims), self-heal on the nightly; chunked
  fetch+write with per-chunk manifest saves (crash-safe).
- **TWO prune bugs, same-day, both guarded:** (1) a scoped `--pages 1` pilot
  run with the unscoped prune deleted 5,885 manifest rows + files (rows
  survived with files gone = silent refetch-skip landmine — repair: drop
  file-less rows, refetch); (2) failed LISTING pages read as upstream
  deletions and pruned fresh docs. Law: PRUNE ONLY ON A COMPLETE UNSCOPED
  WALK; rows-without-files are a corruption class worth auditing anywhere a
  prune exists.
- Corpus ~105k docs / ~383k chunks. Fractal OVERALL PASS (98.55/99.53/0
  orphans); eval recall FLAT vs wave 5 (zero displacement from +27k prompt
  chunks), MRR −0.6pp vs baseline (dilution). Live probes: RAG prompt queries
  land exact hub prompts; "system prompt generator" lands the superb_system_
  instruction_prompt family.

### Wave 5b restore COMPLETE + full-feature audit (2026-10-16, this session took over)

- Josh handed the langchain-hub restore to this session. Overnight the wave-5b
  session had landed its commits (incl. the complete-flag prune hardening +
  daemon-first MCP work) and healed most of the corpus. This session ran one
  more full sweep (sha-skipped the healthy 9,96x, fetched stragglers; a
  handful of upstream-dead repos 404 and are recorded as errors, not pruned),
  then `kb.ingest --quick` (126 docs added / 6,860 re-embedded / 51,124
  chunks) and `kb fractal build` + coverage (AIRTIGHT, 0 gaps).
- **Full-feature audit (cross-layer, /tmp/feature_audit.py pattern):**
  - **atlassian:** 656 manifest rows (652 docs + 4 pathless swagger-etag rows
    the indexer correctly skips) → 652 files → 652 docs indexed → 5,485
    chunks, 0 missing vecs → 652 file / 5,342 section / 5,485 chunk
    factlets. 0 orphans, 0 missing files. EXACTLY 1:1 file:doc:file-factlet.
  - **langchain-hub:** 9,966 rows = 9,966 files = 9,966 indexed docs →
    27,289 chunks, 0 missing vecs → 9,966 file-level factlets (1:1), ~24k
    section / ~27k chunk. Note: `source LIKE 'hub://%'` ALSO matches the HF
    wave-5 sources — count with `level=1` + `COUNT(DISTINCT source)` for the
    1:1 check (61k raw rows ≈ 10k docs × 3 levels is the expected shape).
- **Live probes:** hub SQL-chain query → exact text-to-sql prompt docs top-5;
  zoom on both sources returns correct factlets with drill pointers.
- **Myestery root-caught: `/tmp/inspect.py`** (leftover data-tables debug
  probe from Oct 12) shadowed stdlib `inspect` for ANY script run with
  sys.path[0]=/tmp — dataclasses import crashed with a gateway EVENTS dump.
  Renamed to /tmp/dt_inspect_probe.py. Repo and daemon were never affected.

## Harness re-ingest: tech-review lessons (2026-10-21)

Scoped `kb.sync --sources harness` (459 written) → `kb.ingest --quick` (FTS rebuild 18.8s) → `kb fractal build` → `kb fractal_audit` OVERALL PASS (sections 98.17%, chunks 99.52%, 263 topics, 0 orphans). New files indexed: domains/tech-review-lessons-learned.md (12 chunks, doc 243378) + workato-development-playbook SKILL.md update (25 chunks, doc 243385). Live probes: search ranks both #1/#2 above the intbt Recipe Deployment Process page; zoom returns the file + chunk factlets with drill pointers. Integrity: 392,856 chunks, 0 vectorless; 31 orphan vec rows = the known vestigial set, left untouched. Corpus state note: index/kb.db is the live DB (DATA_ROOT/kb.db is a 0-byte stub — probe the index dir).

## Honest zero: lens-degraded headers in the digest (2026-10-19, proposal 2026-10-15-changelog-lens-zero-bits)

- **Change:** `kb/digest.py` now tracks per-lens retrieval health. When a lens
  query's `confidence_bits` metric is 0.0 for `ZERO_BITS_PASSES` (2) consecutive
  passes, its digest section header renders
  `### <topic> — LENS DEGRADED (0.0 bits xN, last fresh hit <date>)` and the
  stale hits are suppressed (count shown). A lens that reads nothing can no
  longer present months-old posts as "no news".
- **State:** `~/.claude/workato-kb/digest-lens-state.json` (beside the other
  digest state in DATA_ROOT): per `agent/label` lens → `zero_streak` +
  `last_fresh`. Last-fresh = last pass a current-year hit appeared in the
  oversampled top-K for recency sources (changelog/blog); for evergreen
  sources, last pass with bits > 0 and hits at all. `KB_LENS_STATE` env
  override for dry runs, mirroring `KB_DIGEST_DIR`.
- **Verified live 2026-10-19:** real digest run (clean state, /tmp digest dir)
  + simulated 0.0-bit dry run through the real `build_digests` path — degraded
  header rendered with streak 1→2 crossing, non-degraded sections unchanged,
  streak resets on bits > 0. Changelog lens TODAY: 3.46-3.58 bits, top hits
  still "Product Scoop – April 2026" (nonzero bits but months old — the
  staleness pathology persists; metric-based trigger did not fire today).
- **Unrelated live finding:** no full nightly sync diff report since
  `diffs/2026-10-14.json` — every digest since 10-15 renders SYNC FAILED. The
  sync job needs investigation (out of scope here).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Workato KB (RAG++)](projects/workato-kb.md) — **2026-10-16 AUDIT: BM25 LEG WAS DEAD SINCE INCEPTION (chunks_fts never populated — every search ran dense-only; now rebuilt in indexer every build, eval recall +1.1pp/MRR +2pp, cross-source MRR +5.5pp); snowflake/dbt/trigger never had nightly steps (wired); confluence nightly covers all SPACES (asee/gears/cssup were stale); Workato org code INGESTED (SDK Ruby source 173 docs, 96 canonical connector examples, opa-extensions, edge-gateway charts — CODE_EXTENSIONS in github_source); synthesis docs: domains/workato-sdk-internals.md + domains/workato-dev-apis.md**; **WAVE 5b LANGCHAIN HUB IN 2026-10-15 (10,322 public prompt repos listed, 9,961 docs landed w/ 14.8k extracted templates incl. input vars + format; recursive manifest walk; change-sig nightly skip; TWO prune bugs guarded — prune ONLY on complete unscoped walk; corpus ~105k docs/383k chunks, fractal PASS, eval flat, commit 32453f1)**; **WAVE 5 CRAWL MANDATE 2026-10-15 (corpus ~95k docs / 355k chunks, commit 404743f — also carried wave 6's uncommitted workday/atlassian wiring): HF library docs (6 sites, 1,604p, version-stripped URLs), pwc dumps (31.7k docs: dataset/method cards + 8k SOTA tables from pwc-archive parquet), apis-guru (2.5k API cards), terraform-registry (5.6k namespace catalogs, metadata-only per HashiCorp rule), figshare (budgeted firehose-verify — search API ignores category filters, verified), developer-roadmap (11k pages, sparse blobless clone of roadmaps/), 8 self-healing/EDA/universality webcrawl sites (self_start option); NEW llms-scout pipeline = 2,849-site candidate queue at scout/llms-site-queue.jsonl (report step, never core); 429 circuit-breaker in common.py (Retry-After aware); fractal_audit pseudo-URL fix (pwc:// etc. now credit); fractal PASS 98.26/99.48/0 orphans; eval −1.6pp = dilution artifact (corpus +141%, sibling-crowding verified); LangChain Hub probed NOT ingested (no public list API)**; **ATLASSIAN DEV DOCS INGESTED 2026-10-15 (developer.atlassian.com cloud: Jira Cloud 251p, Jira Software 108p, JSM 107p, Confluence Cloud 121p, Rovo MCP/A2A 17p = source `atlassian`, 652 corpus files incl. ~222 OpenAPI-exploded REST API-group docs; window.__DATA__ raw-markdown extraction adapter, commit 9e891de; fractal AIRTIGHT, live-probed)**; **SLACK DOCS INGESTED 2026-10-14 (docs.slack.dev, 3,274 en-only pages incl. 756 API-reference pages, source `slack`, llms.txt+sitemap adapter in llms_source.py, CORE_SOURCES floor, commit 69d823b; corpus 38.8k docs/250.9k chunks, fractal PASS, eval in-source −0.5pp)**; **ASEE+GEARS+CSSUP spaces INGESTED 2026-10-10 (797 pages, 179 GOLD, 20-agent scored; standard space-ingest process in the file + curation report; indexer confluence-manifest discovery fixed dynamic)**; **PIPELINE AUDIT 2026-10-10 eve: auto-memory-ingest bug FIXED+live-proven (harness 116→281 docs), scoped-report clobber fixed, funnel wired into nightly, kb-audit monitor fleet 3x daily (9 checks incl. live retrieval probe) PASS 9/9, fleet runner symlink restored**; **v0.7.0 THE FIVE LEAPS** 2026-10-08 overnight (calibration cards; dissenter triad w/ learned critic weights; rehearsal cortex w/ proven fixture extraction; fractal factlets 64,238 + zoom retrieval; MRL coarse-fine funnel w/ coverage guard; criticality meter; KB MCP server; event-driven dreamer wakeup; (`kb` CLI shim everywhere + CLAUDE.md query mandate; lateral graph cross-domain via burstiness concept filter — docs x practice hidden pairs; Sunday full-KB dream mandate; (dreamer lens calls across kimi-k3/glm-5.3-flash/deepseek-4.1-flash via AI gateway, Kimi cost-governed to 1 rotating lens/night + Sunday full board; (board minutes -> draft Confluence Mondays 06:27 via fleet `minutes` job; cross-model lens mandate; empirical-dream budget 2/night in auto-dev; outcomes flywheel LIVE on the real ledger — posterior P(accept) 0.887 from 11 records, flywheel opens /proposals; (Board of 9 professional lenses, lateral hidden-connection engine [vectorized Adamic-Adar], dream_math [Beta P(accept) + EV + assumption regression], memory-entropy report; roadmap + fan-out complete: (LLM contextual headers via local ollama, attachments machinery, /kb slash command, 6-agent nightly digest fan-out w/ opinions-to-bus, dreamer multi-lens creativity protocol, kit baf6863; sync 21:37 + digest 22:07 ahead of the fleet): 9 sources / 10,274 docs / 63,952 chunks; docs.workato.com (4,342 via llms.txt md-twins) + changelog (252) + blog/The Connector (1,197) + Automation Inspiration (88) + GitHub arch-canon (320) + EIP (103) + Claude docs (625) + BT Confluence (3,352, LOCAL-ONLY, token sync LIVE v2-pagination — v1 CQL broken on tenant); stack: BM25+bge-base+RRF+reranker × entropy × PMI + confidence-gated round 2; integrity verified vec==chunks; repo ~/Documents/workato-kb (5b6e6fc), skill workato-kb, launchd 02:07; dreamer nightly 3-mode KB review + grill-gate/onboarding/playbook wired; remaining: LLM chunk headers, PDF attachments, fleet packaging