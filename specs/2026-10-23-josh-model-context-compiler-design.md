# Josh Model + Context Compiler — Design Spec

Date: 2026-10-23
Status: approved design (Josh, in-session 2026-10-23), Phase 1 scoped for implementation
Author: Claude (session), Josh direction

## 1. Goal

Close the apply-leg of the self-improvement loop. The harness collects (memory, claims,
ledgers) and reflects (dreamers, cortex, gardener) well. What it cannot do today is answer
"what does Josh want, in THIS kind of session, with evidence" or prove that a learned rule
changed later behavior. This build adds two coupled pieces:

1. **Josh Model** — a structured, evidence-cited store of Josh's preferences, rulings, and
   decision precedents.
2. **Context compiler** — a first-prompt session briefing that retrieves the small set of
   rules relevant to the task at hand, replacing the growing static-rule pile with directed
   retrieval.

## 2. Constitutional boundary (Josh-approved 2026-10-23)

**Scribe + propose only.** The system structures what Josh explicitly says and does.
Anything inferred becomes a `draft` row and is never active until Josh confirms it in a
batched review. No LLM taste-judging anywhere in the loop. Rationale on record: the
decisions-engine UAT (2026-10-14) scored 0.25–0.36 accuracy predicting Josh's verdicts,
worse than an always-reject baseline. Learning from behavioral signal (corrections typed,
approvals given, edits made) is in bounds; inferring taste is not.

## 3. Design gate — existing mechanisms and why this differs

| Existing mechanism | Relationship |
|---|---|
| CLAUDE.md / MEMORY.md | Static, all-or-nothing load, no per-rule scope/confidence/evidence. Josh Model is structured and retrieved, not piled. CLAUDE.md stays the always-on floor; the model is the scoped layer above it. |
| Claims ledger (`brain_claims`) | World-facts ("endpoint X 404s"). Josh Model holds Josh-facts ("verdict-first, always"). Different subject, no merge. |
| Instruction-patch loop (`instruction-patches/`) | Mines corrections nightly, checks instruction-text coverage. Phase 2 makes it a drafts emitter into this store. Compose, never duplicate. |
| Standing Orders (frontier stack) | Estate-governance policies for Workato assets. Josh Model governs session behavior. Separate stores, shared schema ideas. |
| KB RAG++ | Doc retrieval with no notion of scope/status. Phase 3 may mount precedents as a KB source if local retrieval quality is insufficient. |
| Session absorb / reload-session | Undirected "read everything recent." The compiler is directed retrieval against task signals. |

Production contact: none. Local harness only. No Workato assets, no outward surface;
RLM manifest and red-team standing orders do not apply. The one hook ships through the
workato-guardrails plugin in `~/mods` with the plugin test engine, same as hooks 1–15.

## 4. Store

Location: `~/.claude/knowledge/josh-model/`. JSONL throughout (house style: git-diffable,
covered by knowledge-write-stash, consistent with decisions/predictions/mission-control
ledgers). Volumes are hundreds of rows; no database engine.

### 4.1 `preferences.jsonl`

One row per rule:

```json
{
  "id": "pref-001",
  "statement": "Josh's verbatim words where possible",
  "normalized_rule": "machine-checkable phrasing, written once, never paraphrased silently",
  "origin": "stated | proposed",
  "status": "draft | active | superseded | retracted",
  "scope": "global | project:<slug> | task:<type>",
  "tags": ["kebab-case"],
  "evidence": [{"source": "claude-md|memory|transcript|ticket|knowledge-file", "ref": "path or URL", "date": "YYYY-MM-DD"}],
  "created": "YYYY-MM-DD",
  "last_confirmed": "YYYY-MM-DD",
  "supersedes": ["pref-000"],
  "contradicts": ["pref-099"]
}
```

Field rulings (ambiguity fixes from the chat design):

- `origin: stated` = Josh's explicit words (strongest). `origin: proposed` =
  system-inferred, Josh-confirmed at review. There is no separate confidence field;
  origin plus status carry it.
- `status: draft` rows are never served in briefings and never enforced.
- `superseded`/`retracted` rows stay in the ledger (append-only, like all house ledgers).
- `scope` task types are a controlled vocabulary: `build | plan | review | triage | docs |
  comms | debug | promote | investigate`. New task types require a spec addendum, not ad
  hoc use.
- `statement` is never rewritten after creation. Corrections create a new row that
  supersedes.

### 4.2 `precedents.jsonl`

Decision case law:

```json
{
  "id": "prec-001",
  "date": "YYYY-MM-DD",
  "situation": "one-paragraph sketch of the decision context",
  "options": ["presented options"],
  "chosen": "the option Josh picked",
  "reason": "Josh's stated reason, verbatim where possible",
  "context_tags": ["plan", "workato", "governance"],
  "evidence": [{"source": "...", "ref": "...", "date": "..."}]
}
```

Sources for seeding (Phase 3 backfill; Phase 1 ships the schema and `add` only):
grill-gate answer rounds, plan-mode approvals, red-team overrides, promotion go/no-go
decisions, standing-order rulings.

### 4.3 `drafts.jsonl`

Same shape as preferences with `status: draft` plus `proposed_by` (instruction-miner |
in-session | gardener) and `proposed_at`. Reviewed via the existing /triage queue as
`kind=preference` cards (Phase 2). Phase 1: `josh-model.py review-list` prints them;
`confirm <id>` promotes to active.

### 4.4 `briefings/` log

One JSONL row per served briefing:
`{ts, session_id, task_signal_hash, served_pref_ids: [], served_prec_ids: [], token_estimate}`.
This is the audit trail and the measurement substrate (section 7).

## 5. Compiler and delivery

### 5.1 `josh-model.py` (lives in `~/.claude/knowledge/scripts/`)

Subcommands:

- `add` — interactive/flag-driven preference or precedent creation. Runs the cheap
  contradiction screen (5.3).
- `add-draft` — in-session capture when a correction just happened.
- `brief --task "<first user message>" [--project <slug>] [--cwd <path>]` — prints the
  briefing markdown to stdout. Deterministic, no LLM, target <100ms.
- `review-list` — drafts awaiting confirmation.
- `confirm <id>` / `supersede <id> --by <id>` / `retract <id>` — lifecycle transitions.
- `eval` — runs the recall eval (section 8) and prints recall@8.

### 5.2 Scorer

Deterministic scoring per active row:

```
score = scope_weight            # project match 100 > task match 60 > global 30
      + 10 * tag_overlap_count  # task-signal keywords vs row tags
      + recency_bonus           # last_confirmed within 30d: +10, within 90d: +5
      + violation_boost         # row born from a correction AND tags overlap: +25
      - served_demote           # served in >=3 of last 10 sessions with no violation: -40
```

Weights live in a `CONFIG` dict at the top of the file, tunable without code spelunking.
Briefing = top 8 preferences plus up to 2 precedents when the task signal matches
`plan|build|review`. Output target is ~700 tokens; 800 is the hard cap the hook test
enforces.

### 5.3 Contradiction screen (cheap, zero-LLM)

On `add`: same-scope rows with tag overlap >= 50% are printed as "review candidates."
No polarity claims (keyword polarity is fragile). The deep contradiction lens is a
gardener weekly pass, Phase 3.

### 5.4 Delivery: first-prompt hook

A UserPromptSubmit hook (workato-guardrails plugin, hook 16) that:

- Fires only on the first user prompt of a session (sentinel file
  `/tmp/josh-model-briefed-<session_id>`).
- Calls `josh-model.py brief --task "<prompt>" --cwd "$PWD"`.
- Emits the result as `additionalContext`.
- **Fails open**: any error, missing store, or empty result produces zero output and never
  blocks or annotates the prompt. A broken briefing hook must be invisible, not noisy.
- Task-type classification is keyword-based (`plan|design|architect` -> plan,
  `ticket|triage` -> triage, etc.), documented in CONFIG.

Rationale for first-prompt over SessionStart: SessionStart fires before the task exists;
the first message IS the task signal. Mid-session task switches are served by manual
`josh-model.py brief` (documented, no hook).

## 6. Seed pass (Phase 1 includes this)

Scribe existing written rulings into `preferences.jsonl`, one batch, Josh reviews before
hook activation:

1. Global CLAUDE.md standing orders and global rules (verbatim statements, evidence =
   file + section).
2. Project CLAUDE.md rules (`~/Documents/CLAUDE.md`, workbench CLAUDE.md).
3. MEMORY.md memory files of type `feedback` and `user`.
4. Knowledge-tree standing rulings (THE RIGHT WAY, micro-target discipline, manifest
   algorithm, red-team gate, dev-free/prod-gated, etc.), one row each with evidence link.

Estimated 40–80 rows. Every row: `origin: stated`, `status: active`, evidence required or
the row is dropped. Transcript backfill is explicitly OUT of Phase 1 (the nightly miner
already owns transcript correction discovery going forward).

Josh reviews the seed file in one batched pass before the hook is enabled. The review
verdict is recorded as a mission-control event on the workstream row.

## 7. Measurement (the prove-it leg)

- **Hit-rate join (Phase 2):** when instruction-miner records a correction event for a
  session, join against `briefings/`: was a rule with the violated rule's tags served?
  `served-but-violated` high = briefings are wallpaper (fix ranking/length).
  `not-served` high = retrieval gap (fix tags/scorer). Zero-LLM, reported in weekly
  gardener output.
- **Spaced-repetition demote** (5.2) keeps briefing novelty high; demote behavior itself
  is logged in the briefing row so the metric can separate "not served by design" from
  "retrieval miss."
- **Row churn report:** active/draft/superseded counts over time, appended to gardener
  weekly output (Phase 2).

## 8. Testing and verification

1. **Unit tests** for scorer (scope precedence, tag ranking, cap enforcement, demote
   logic) with fixture rows. Plugin test engine, same harness as hooks 1–15.
2. **Hook tests:** fires once per session (sentinel), fail-open on missing store, fail-open
   on malformed JSONL row (skip row, log, continue), output under token cap.
3. **The money test — correction-episode recall eval.**
   `~/.claude/knowledge/josh-model/eval/correction-episodes.jsonl`:
   `{episode_id, task_signal, expected_pref_ids: []}`. Built from real past correction
   episodes (the ones already mined in dream reports and instruction-patch coverage
   files). `josh-model.py eval` computes recall@8: fraction of episodes where the
   preventing rule appears in the briefing. Baseline number recorded in this spec as an
   addendum before the hook is enabled. The eval is the permanent regression suite for
   every scorer/weight change.
4. **Live smoke:** one real session (this project's) first-prompt briefing inspected by
   Josh before the hook is left enabled.

## 9. Acceptance criteria (Phase 1)

1. `josh-model.py` add / add-draft / brief / review-list / confirm / supersede / retract /
   eval all work on fixture data, unit-tested.
2. Seed file exists; every row has statement, scope, and at least one evidence ref; Josh
   sign-off recorded.
3. Hook fires on first prompt only, emits <=800-token briefing, fail-open proven by test.
4. Briefing log row written per served session.
5. Recall eval runs; baseline recall@8 recorded as spec addendum.
6. Plugin test suite green (existing 42 + new).
7. INDEX.md line + MEMORY.md pointer added; mission-control closeout row filed.

Explicitly NOT Phase 1: instruction-miner drafts emitter, /triage preference lane,
hit-rate join, precedent backfill, KB mount, gardener contradiction lens. Each becomes a
dreamer/triage proposal through the existing pipeline.

## 10. Risks

- **Briefing fatigue / wallpaper.** Mitigated by the 700-token cap, top-8 cut, and the
  served-demote rule; measured by the hit-rate join. If served-but-violated stays high,
  the fix is fewer, sharper rows, not more context.
- **Seed drift.** `statement` verbatim + `normalized_rule` as a separate field + Josh
  review gate before activation.
- **Keyword-dumb retrieval.** Accepted for Phase 1; the recall eval quantifies exactly how
  dumb, and KB mounting is the staged upgrade path.
- **Store rot.** Drafts that sit unreviewed >30 days are surfaced by gardener weekly as
  stale; rows supersede instead of being edited, so history is always auditable.

## 11. Open items

None blocking. Phase 2/3 sequencing is deliberately left to the proposal pipeline.

## 12. Build addendum (2026-10-23, Phase 1 built)

**Baseline recall eval: 1.000 (10/10 episodes).** Interpretation guardrails: the
set is small, episodes were authored with knowledge of the tags (two seed rows
gained faithful tags during construction: pref-008 +slack, pref-021 +scheduler,
wait), and recall@8 is lenient. This number is a regression floor for future
scorer changes, not proof of retrieval quality. Precision noise exists (some
briefings carry marginal rows); the Phase 2 hit-rate join is the real quality
signal.

**Scorer refinement shipped during build (within spec §5.2's spirit, recorded
here for the record):**

1. Classification is multi-type. "Post an update to the BSYS ticket" is comms
   AND triage; the spec's single-winner classifier starved the losing side's
   task-scoped rules (proven by a failing eval episode during construction).
   `classify_task` returns all types with >=1 keyword hit, best-first.
2. Untyped prompts no longer exclude task-scoped rows: they become eligible at
   a weak weight (20, below global's 30), so task rows surface on untyped asks
   only when tag overlap earns it. Motivating case: "flip the vua_required
   flag" contains no debug keyword but must serve the micro-target rule.

**Engine constraints discovered (deposited in domains/claude-code-mods.md):**

- The plugin validator forbids two bare `on('prompt.submit', ...)` registrations
  per module; hook 16 lives inside hook 5's existing handler.
- A test's stubbed prompt.submit answer may not carry both `drop` and
  `context`; capture context via closure instead.

**Activation state: LIVE since 2026-10-26.** The cache was first refreshed
2026-10-24 (v1.1.0), but hook 16 silently never fired — `process.env.HOME`
throws `process is not defined` in the hook runtime, and the fail-open catch
made the dead hook invisible for 3 days. Diagnosed 2026-10-26 via a
temporary diag file + headless `claude -p` probe (fires the real engine);
fixed with `$.env.get('HOME')`; five other latent `process.env` sites in the
plugin swept the same day (/builds, /cockpit, ledgerChurn, etc. had been
silently degrading). Live-verified twice: briefing rows land in
josh-model/briefings/briefings.jsonl and probe sessions visibly answer with
the served rules. Full trap writeup in domains/claude-code-mods.md.
Note for the record: the §6 seed-review gate was overtaken by the 10-24
activation; the seed remains open to Josh's review at any time (rows are
data, editable without redeploying the hook).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Josh Model + context compiler](specs/2026-10-23-josh-model-context-compiler-design.md) — structured preference/precedent store (~/.claude/knowledge/josh-model/, preferences/precedents/drafts JSONL + briefings log) + `josh-model.py` (add/brief/confirm/supersede/retract/eval; deterministic scorer: scope > tag overlap > recency + violation boost, served-demote, 800-token cap) + hook 16 first-prompt briefing (inside hook 5's prompt.submit — ONE bare registration per module); constitution: scribe+propose only, no LLM taste-judging (decisions-engine lesson); seed = 83 stated rows from CLAUDE.mds + feedback memories; baseline recall@8 = 1.000 on 10 correction episodes (eval/correction-episodes.jsonl = the permanent scorer regression suite); unit tests 20/20 + plugin 48/48 + driver 4/4; **ACTIVATION HELD pending Josh's seed review, then cp ~/mods → plugin cache**; Phase 2: instruction-miner drafts emitter, /triage kind=preference lane, hit-rate join