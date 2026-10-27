# SPEC — DevAPI Semantic MCP Phase 6: Self-Learning (audit → shape → lessons → verifier/stats → benchmark)

- **Spec author:** spec-distiller (advisory only — builds nothing)
- **Date:** 2026-10-25
- **Governing story:** [BSYS-29894](https://workato.atlassian.net/browse/BSYS-29894)
- **Source of truth:** Josh's approved Phase 6 design (2026-10-25 — all recommendations stand): 6a/6b NOW, 6c/6d/6e FAST FOLLOW
- **Builds on:** repo [SPEC.md](~/orca/projects/dev-api-mcp/SPEC.md) (Phases 0–5 complete, suite 41/41), [HANDOFF.md](~/orca/projects/dev-api-mcp/HANDOFF.md), kb-corpus `00-architecture-and-contracts.md` + `03-promotion-pipeline.md`
- **Builder rule:** cite this file's path in the build report; post-build scoring via `~/.claude/knowledge/scripts/spec-score.py`. Criteria carry the exact table names, recipe IDs, envelope classes, and error codes the scorer must match.

## Goal

Make the dev-only 3-tool Workato Developer API gateway (`mcps-Ac6JB4fW-H9T-CD`) self-learning: full per-call audit, Ruby-inspect response normalization, jury-adjudicated auto-applied lessons, daily lesson re-verification with evidence-weighted stats, and a 3-arm benchmark against the 100+-tool AIRO MCP and the raw API — with no LLM ever on the hot path.

## Scope

### Phase 6a (NOW) — sessions + full audit

**IN:**
- New insert-only data table `workato_api_gateway_audit` in the Data Tables folder (35937038): one row per `workato_api` action carrying event_id, session_id, caller identity, request, family/capability/intent, resolution_class (`exact/scored/fuzzy/ambiguous/unresolved`), outcome_class, http_status, error_class, error_signature, response_bytes, plan_id, created_at.
- **Spec addition to Josh's column list (flagged, not smuggled):** the audit schema ALSO carries `response_shape` and `duration_ms` AT CREATION. Reason: `data_table_update(columns)` on a populated table silently wipes rows (airo-mcp-playbook trap), and 6b needs response_shape while 6d's p50 stat needs duration_ms — both must exist before the first row lands.
- Optional `session_id` input on the `workato_api` tool schema so agents correlate calls; every response envelope echoes session_id.
- Caller identity captured from the VUA/skill context WHERE BINDING-SAFE (see Risk 1 — the banked context-pill trap); MCP token name is the guaranteed floor.
- Learning events stay exactly as they are — the curator feed. Audit is the rich log, not a replacement.

**OUT (6a):**
- Auditing `workato_api_capabilities` / `workato_api_policy_lookup` calls — they are content-free introspection with no resolution semantics; add later only if Josh asks.
- Any change to learning_events emitters, the plan/confirm flow, or the envelope vocabulary (session_id echo is additive only).
- Any UI/reporting over the audit table (6d materializes stats; raw browsing is Josh's).

### Phase 6b (NOW) — shape classification + structured error events + the flagship lesson

**IN:**
- Deterministic response-shape classifier on the gateway read/execute path: `response_shape ∈ {json, ruby_inspect, empty, other}`, recorded on the audit row. Motivation: the Workato management API returns Ruby-inspect strings (`id=>...`) on many endpoints.
- The flagship lesson: a Ruby-inspect normalizer parsing those strings to real JSON inside the response envelope — silent correctness, no caller-visible error, no caller change.
- Structured error events on every failure path: `error_class` + `error_signature` = MD5 of the normalized error detail.
- Parser fixture suite committed to the repo covering the banked Ruby-inspect edge cases.

**OUT (6b):**
- Fixing upstream API behavior — the normalizer is gateway-side only.
- LLM-assisted parsing of any kind, at any point.
- Changes to `response_contract_json` projections (normalization precedes projection; contracts unchanged).
- Retroactive classification of pre-6b traffic (the audit table starts empty).

### Phase 6c (FAST FOLLOW) — lessons table + jury + hot-path auto-apply

**IN:**
- New data table `workato_api_lessons`: signature → remedy_json (three remedy classes: `response_parser`, slot-format hints, endpoint quirks) plus lifecycle fields (status active/stale/retired, stale_count, last_verified_at, verdict_json as audit).
- Curator extension mining lesson candidates from error_signature clusters in `workato_api_gateway_audit`.
- Adjudication by the SAME 3-model jury (Claude judge / GPT dissenter / Gemini resolver via Workato AI) behind promoter 83286359; machine gate per PR-002 — humans audit after, never gate.
- Sync 83284865 materializes confirmed lessons into a hot-path index table `workato_api_lessons_index`; the gateway consults it at compile: normalization-class remedies auto-apply silently, strategy hints surface as advisory notes on the envelope, risk-bearing remedies stay plan/confirm.

**OUT (6c):**
- Human-in-the-loop per-lesson approval (machine gate per PR-002; humans audit after).
- Auto-apply of risk-bearing remedies under any circumstances.
- Any change to the phrase-promotion flywheel (separate pipeline, untouched).
- Lessons that alter a capability's contract (slot names, risk class, activation) — contract changes stay registry edits through the existing promoter/discovery path.

### Phase 6d (FAST FOLLOW) — lesson verifier + efficiency stats

**IN:**
- Daily lesson-verifier recipe re-probing every active lesson against the live API: re-affirm with evidence (last_verified_at + probe reference) or mark stale; 2 stale = retired; retired lessons leave `workato_api_lessons_index` within one sync tick — tended memory that never goes stale.
- Hourly materialization of per-capability efficiency stats into new table `workato_api_capability_stats` (success rate, p50 duration_ms, response_bytes stats) computed FROM `workato_api_gateway_audit`.
- `workato_api_capabilities` (83280134) `mode=summary` gains per-family efficiency hints.
- Resolution tie-breaks gain an evidence term (stats-informed), falling back to the existing rank rule when stats are empty.

**OUT (6d):**
- Real-time or inline stats on the hot path — materialization is offline hourly, period.
- Retiring capabilities or intents (the verifier retires LESSONS only).
- Alerting/digest wiring from stats (a separate Josh decision).

### Phase 6e (FAST FOLLOW) — the AIRO-killer benchmark study

**IN:**
- In-repo benchmark harness modeled on the GWS benchmark-harness (`~/orca/workspaces/workbench/Google-Semantic-MCP/docs/slack-mcp/benchmark-harness/`): runner + fixtures + summarize/evaluate scripts; read-only task suite.
- Frozen task list sampled from the mined intent corpus (`~/orca/databases/claude-intents-raw.db` — 200,944 user_ask phrases).
- Three arms: (1) this 3-tool gateway `mcps-Ac6JB4fW-H9T-CD`; (2) the purpose-built 100+-tool AIRO MCP server (`workato-airo-mcp-server`) — the "AIRO-killer" comparison arm, an existing asset, NOT a new build; (3) raw Developer API over HTTP with the same dev token.
- Metrics per arm: token cost, task completion, p50 latency, failure recovery.
- Written study committed to the repo.

**OUT (6e):**
- Building a new 100+-tool comparison server (AIRO IS the arm).
- Mutation tasks in the suite (read-only, per the GWS harness safety pattern).
- Production or marketing claims from a dev-workspace study.
- Subjective/LLM-judged quality scoring — completion is checked by objective per-task fixtures only.

## Acceptance criteria

### Phase 6a — sessions + full audit

- [ ] Table `workato_api_gateway_audit` exists in folder 35937038 with columns event_id, session_id, caller_identity, request, family, capability_id, intent_key, resolution_class, outcome_class, http_status, error_class, error_signature, response_bytes, response_shape, duration_ms, plan_id, created_at — created via `data_table_create`; `data_table_update` columns never called on it once populated.
- [ ] Insert-only proven: the gateway recipe's write path performs create-record only against `workato_api_gateway_audit`; a job-trace inspection shows zero update/delete steps targeting the audit table.
- [ ] A probe set of N calls through `workato_api` covering READ_EXECUTED, READ_FAILED, MUTATION_PLAN_READY, MUTATION_COMMITTED, RESOLUTION_SUGGESTED, and SEMANTIC_CONTEXT_INVALID produces exactly N new `workato_api_gateway_audit` rows, each with outcome_class matching its envelope and plan_id correlating where applicable.
- [ ] resolution_class values observed across the probe set are confined to exact / scored / fuzzy / ambiguous / unresolved.
- [ ] A call with session_id `phase6-probe` echoes session_id `phase6-probe` in the response envelope AND writes it on the audit row; a call WITHOUT session_id succeeds and its audit row records session_id null.
- [ ] Every probe audit row carries a non-empty caller_identity field (MCP token name minimum; richer skill-context identity if binding-safe).
- [ ] After the schema-change push, gateway-level tools/list on `mcps-Ac6JB4fW-H9T-CD` still serves exactly 3 tools (workato_api, workato_api_capabilities, workato_api_policy_lookup) AND `GET /api/mcp/mcp_servers/mcps-Ac6JB4fW-H9T-CD/tools` reports empty `incompatibility_reasons` for all three (context-pill binding trap check — run after EVERY push, not once).

### Phase 6b — shape classification + structured error events

- [ ] Every 6b probe call's `workato_api_gateway_audit` row carries response_shape ∈ json / ruby_inspect / empty / other.
- [ ] A live READ_EXECUTED against an endpoint observed returning a Ruby-inspect string returns valid parsed JSON in the response envelope with response_shape=ruby_inspect on its audit row and no error surfaced to the caller (silent correctness proven end to end).
- [ ] Parser fixtures committed to the repo covering the banked Ruby-inspect edge cases: unquoted date values, string "nil" literals, nested `=>` hashes, AND a JSON payload containing "=>" inside a string value that MUST stay classified json.
- [ ] Fail-safe proven: a seeded unparseable payload passes through UNMODIFIED with response_shape=other — no payload corruption, no caller error (silent correctness never means silent corruption).
- [ ] A forced 4xx and a forced transport failure each write an audit row with error_class + error_signature (MD5 of normalized detail); two repetitions of the SAME failure produce byte-identical error_signature values, and two DIFFERENT failures produce different signatures.

### Phase 6c — lessons + jury + hot-path auto-apply

- [ ] Table `workato_api_lessons` exists keyed by signature, with remedy_json covering the three remedy classes (response_parser, slot-format hints, endpoint quirks) plus status (active/stale/retired), stale_count, last_verified_at, verdict_json.
- [ ] The curator mines lesson candidates from error_signature clusters in `workato_api_gateway_audit`; a seeded sub-threshold cluster is observed HELD, not promoted (machine gate per PR-002).
- [ ] A gate-passing lesson candidate receives verdicts from all three jury models (Claude judge / GPT dissenter / Gemini resolver via Workato AI); a seeded malformed verdict PARKs the candidate with all three outputs attached (fail-closed, never promotes on error).
- [ ] Sync materializes a confirmed normalization-class lesson into `workato_api_lessons_index`, and a re-run of the originally failing call then SUCCEEDS with no caller change (silent auto-apply proven end to end).
- [ ] A seeded strategy-hint lesson surfaces as an advisory note on the response envelope and does NOT alter execution.
- [ ] A seeded risk-bearing remedy does NOT auto-apply: the mutation path still returns MUTATION_PLAN_READY and commits only via the one-time challenge.
- [ ] Job traces of lesson-applied calls show zero model-connector steps (no LLM on the hot path — deterministic index read only).

### Phase 6d — lesson verifier + efficiency stats

- [ ] A daily-scheduled lesson-verifier recipe exists; a job trace shows an active lesson re-probed against the live API with last_verified_at updated and an evidence reference recorded on the lesson row.
- [ ] A lesson whose probe fails flips stale_count 0→1; a second failed probe flips status to retired; `workato_api_lessons_index` stops serving it within one sync tick (re-run of the call shows the remedy no longer applied).
- [ ] Hourly materialization writes per-capability_id rows to `workato_api_capability_stats` carrying success rate, p50 duration_ms, and response_bytes statistics computed from `workato_api_gateway_audit` via filtered, continuation-token-paged reads (no unfiltered 1000-row scans — the GWS dedupe-boundary bug class).
- [ ] `workato_api_capabilities` mode=summary response includes per-family efficiency hints sourced from `workato_api_capability_stats`; the stale-checksum fail-closed gate is re-proven unregressed after the change.
- [ ] With a seeded stats history favoring candidate B, a resolution tie between A and B resolves to B (evidence term proven); with `workato_api_capability_stats` empty, the same request falls back to the existing rank rule / INTENT_AMBIGUOUS behavior.

### Phase 6e — the AIRO-killer benchmark study

- [ ] Benchmark harness committed under `~/orca/projects/dev-api-mcp/` (runner + fixtures + summarize/evaluate scripts) following the GWS benchmark-harness pattern: warmups, sequential measurements, read-only suite, no tokens in committed fixtures.
- [ ] The frozen task list is sampled from `~/orca/databases/claude-intents-raw.db` (200,944 user_ask phrases) with the sampling query, stratification method, and task count recorded in the study doc BEFORE any arm runs.
- [ ] All three arms executed against the frozen task list: the 3-tool gateway `mcps-Ac6JB4fW-H9T-CD`, the AIRO MCP server (`workato-airo-mcp-server`, 100+ tools), and raw Developer API HTTP calls using the same dev token.
- [ ] Per-arm results JSON committed with token cost (chars/4 estimate minimum), task completion rate, p50 latency, and failure-recovery outcomes; no live secrets or raw request payloads in committed results.
- [ ] The written study (repo doc) states the measured winner per metric class and its limitations (dev workspace, sample size, single-driver caveat).

### Governance (cross-phase)

- [ ] [BSYS-29894](https://workato.atlassian.net/browse/BSYS-29894) carries the Phase 6 scope at build start (comment or linked sub-tasks); any new ticket gets Story Points on `customfield_10057`.
- [ ] Manifest 371191 is updated via the `manifest-creation` skill (the ONLY sanctioned path — UI-built via RLM per the 2026-10-24 algorithm, which supersedes hand-built/API rows) in the SAME TURN the first Phase 6 asset is created — new tables and recipes selected, dependencies crawled — with read-back (`/export_manifests/371191.json`) AND ZIP-level verification (a 200 response alone proves nothing).
- [ ] Every recipe stopped during the build is restarted in the same turn; a post-restart tools/list re-verifies all 3 tools present (stopped recipe = missing tool).
- [ ] No API token or secret appears in any Phase 6 job trace, audit row, or repo file (`mask_data` on connection-touching steps; 10-row audit spot-check recorded in the build report).
- [ ] A red-team delta review covering the audit table, the normalizer, and the lesson auto-apply surface is dispatched at build completion, verdict recorded under `~/.claude/knowledge/redteam/` before ANY promotion discussion (standing order; the prior BSYS-29894 verdict predates this surface).
- [ ] A mission-control closeout row exists for the build session (`python3 ~/.claude/knowledge/scripts/mission-control.py add --event closeout`).

## Design gate (what already exists; what was checked)

Checked before writing this spec:

- **Claim ledger** (`~/.claude/knowledge/claims/claims.jsonl`, 20 rows): no claim covers the Phase 6 mechanisms (gateway audit store, lessons store, shape classification) — nothing reusable as a mechanism. clm-001 (recipe_builder_push can silently revert VUA personalization) reinforces the verify-after-every-push criterion in 6a. Checked, ruled out.
- **`bin/fleet/` job defs and retry caps:** no local fleet job defs govern this build. All Phase 6 cadences (curator extension, sync materialization, daily verifier, hourly stats) are Workato-side recipe schedules inside project 18341380, joining the existing fleet — sync 83284865, curator 83285929, promoter 83286359, discovery 83284655, retention 83290173, feeder 83290345. `launchctl list | grep com.josh` checked: harness-side jobs only; no local schedule changes needed.
- **Global skills:** `manifest-creation` (the ONLY manifest path — governance criterion), `airo-mcp-playbook` (the `data_table_update` columns trap drives the schema-complete-at-creation rule), `workato-skill-builder`, `verify-recipe` (trace-based proof standard), `red-team-review` (delta review), `mcp-optimization-playbook` (bounded modes for mode=summary hints), `efficient-airo-delivery`. All reused; no new skill needed.
- **Workato KB + project knowledge:** data-table read caps (1000-row page, continuation_token paging), record API `{"document": …}` envelope; Ruby-inspect edge cases banked in `google-semantic-mcp.md` (unquoted date columns, string "nil" literals, array-pill poisoning of re-parsed tables — the reason parser fixtures are a hard criterion); the `context.call_id` binding trap banked in `dev-api-mcp-build-state.md` (drives Risk 1 and the 6a incompatibility_reasons criterion).
- **GWS-canon patterns reused (named per the approved design):**
  - *Flywheel-writes / gateway-reads* — lessons follow the same split as phrases: curator/jury/sync write the store; the gateway hot path only reads `workato_api_lessons_index`. No LLM on the hot path, ever.
  - *Fail-closed adjudication* — the SAME 3-model jury (Claude judge / GPT dissenter / Gemini resolver via Workato AI) with PARK-on-malformed; machine gate per PR-002, humans audit after.
  - *Evidence-weighted tie-breaks* — the GWS BSYS-29356 pattern; 6d adds the evidence term to this gateway's existing rank tie-break (the 2026-10-23 INTENT_AMBIGUOUS fix) with empty-stats fallback.
  - *Observability-v2 hourly materialization* — the GWS intelligence-metrics pattern (metrics table + hourly computer, HR-Genie slice reads) is the direct precedent for `workato_api_capability_stats`.
  - *GWS benchmark-harness* (run.mjs / fixtures / evaluate-gates.mjs, chars/4 token estimate, read-only main suite) is the 6e pattern source.
- **Existing assets reused, never rebuilt:** gateway 83281584, capabilities 83280134, policy 83281173, registry `a8bbb135` (163957, 332 intents / 33 families), vectors `cff4db7c` (163968), sync 83284865, curator 83285929, promoter 83286359, manifest 371191, MCP server `mcps-Ac6JB4fW-H9T-CD`, local install token `local-claude-code`, corpus DB `~/orca/databases/claude-intents-raw.db`.

Standing invariants confirmed by this spec (unchanged from Phases 0–5): no LLM on the hot path; ALL mutations plan-confirm gated with byte-exact commit; fail-closed on any incompatible change; review queue is evidence, not a gate (except capability/functionality-class promotions, which remain Josh's).

## Risks (each with early-warning signal)

1. **Context-pill binding incompatibility (6a).** Banked trap from this very build: the `context.call_id` pill made MCP tool bindings INCOMPATIBLE — the tool was silently dropped from tools/list, no error anywhere. Caller-identity-from-skill-context is exactly this risk class. *Early warning:* after any gateway push, tools/list shows fewer than 3 tools or `incompatibility_reasons` is non-empty on `GET /api/mcp/mcp_servers/mcps-Ac6JB4fW-H9T-CD/tools`. *Rule:* check after EVERY push; on the first failure fall back to token-name identity + the optional session_id input and record the constraint on BSYS-29894.
2. **`data_table_update(columns)` on populated tables silently wipes rows** (airo-mcp-playbook: cells nulled, field_ids regenerated). *Early warning:* any plan phrased as "add a column later." *Rule:* both new tables' schemas are COMPLETE AT CREATION (the audit table carries response_shape and duration_ms from day one precisely so 6b/6d never alter a populated table); a missed column means a NEW table plus backfill, never an in-place column update.
3. **Ruby-inspect parser false positives.** A naive `=>` detector misclassifies legitimate JSON containing "=>" in string values, and nested hashes/unquoted dates break naive parsers. *Early warning:* fixture failures, or a live json response classified ruby_inspect. *Rule:* fixture-driven parser using the banked GWS edge cases; parse failure = pass-through UNMODIFIED with response_shape=other (silent correctness never means silent corruption).
4. **Hot-path cost of audit writes.** One extra create-record per call lands on a gateway already carrying ~2s fixed overhead. *Early warning:* read-happy-path job p50 regresses >20% versus the ~1–2s job-time baseline from 2026-10-23. *Rule:* exactly one audit write per call and ZERO audit-table reads on the hot path; stats materialization is offline only.
5. **LLM creep via lessons.** A remedy that requires interpretation is an LLM on the hot path in disguise. *Early warning:* any design note proposing per-call judgment. *Rule:* remedies are compiled data (parser selection, slot-format hints) applied by deterministic code; advisory notes are static strings from the lesson row; risk-bearing stays plan/confirm.
6. **Young-data threshold miscalibration (6c).** Sparse early audit rows plus probe/debris traffic can hold everything forever or promote debris. *Early warning:* candidates table empty after a week of traffic, or candidates whose request text matches the debris regex (thanks/probe/uat/bench/regression). *Rule:* debris-lint the audit feed with the curator's existing regex class; thresholds recorded on BSYS-29894; Josh spot-audits the first promotions (humans audit after).
7. **Benchmark arm contamination (6e).** The gateway arm can improve mid-study from its own lessons, and arms run on different days see different fleet load. *Early warning:* task-list edits after arm 1 starts; arms spread across days. *Rule:* freeze the task list and harness BEFORE arm 1; same machine, same day, interleaved arm order; raw-API arm uses the same dev token.
8. **1000-row read-cap row loss in stats materialization (6d).** Unfiltered scans of a growing audit table silently drop rows (the GWS alphabetical-tail bug class). *Early warning:* per-capability stat counts stop growing while audit rows keep growing. *Rule:* time-windowed filtered reads with continuation_token paging only — the HR-Genie slice pattern.

## Open questions (true judgment calls for Josh — batched)

1. **Caller-identity mechanism.** Skill-context pills risk the binding-incompatibility trap; MCP token name is safe but coarse. *Recommendation: attempt context-based identity; at the first non-empty incompatibility_reasons, fall back to token name + session_id and record the outcome on BSYS-29894 either way.*
2. **Lesson machine-gate thresholds.** Cluster size and recency window for promotion eligibility are unstated in the design. *Recommendation: ≥3 distinct sessions sharing one error_signature within 7 days, plus the remedy proven by re-probe before any auto-apply class activates; tighten if the first audit week is noisier than expected.*
3. **Benchmark scale and driver.** Task count and the model driving all three arms are unstated. *Recommendation: 40–60 tasks stratified across the top corpus families by frequency, a 5-task pilot first for real cost, and the same harness model across all three arms.*
4. **Efficiency-hint exposure.** Raw success rates versus bucketed hints in mode=summary. *Recommendation: bucketed hints (healthy/degraded) to callers; raw stats stay in `workato_api_capability_stats` for operators.*

---

*Advisory only. If the builder discovers facts that invalidate a criterion, revise this spec with a `## Revision` note — never silently ignore a criterion.*
