# Panel review: Extraction plan v2

Overall verdict: the architecture is right — one streaming pass, verbatim capture, config-driven taxonomy, parked-pending-canary semantics. But there are **five structural defects** that will silently corrupt output if unaddressed, plus sharpening on each of your listed risks. Ordered by severity.

---

## 1. Phase A session selection is taxonomy-dependent → silent corpus loss (top defect)

`google_tool_calls > 0` was computed by the **ingest-time** tagger. R3 explicitly demands an extensible taxonomy — which means the corpus extractor's taxonomy will be a superset of the ingest tagger's. Any Google-call variant the ingest tagger didn't know (new native server name, renamed Workato instance, community server) produced `google_tool_calls = 0`, and Phase A excludes that session **before your better taxonomy ever sees it**. The sessions most likely to contain novel server variants are exactly the ones you'll never scan.

**Fix:** the pass reads every row's header anyway. For any row where `block_types` contains `tool_use`, read `content_json` and extract only the tool name (cheap parse; tool_use blocks are a minority of corpus bulk). If the name matches a *broad* Google regex (not the classification taxonomy — a superset pattern), increment a per-sid counter. Then:

- Flagged sids → full pair extraction as planned.
- Unflagged sids with broad-match hits → emit to a **drift report** (sid, count, distinct tool names). This simultaneously (a) recovers the lost corpus and (b) audits the ingest tagger — a free compliance-grade validation.

Cost is one extra column read on assistant tool_use rows. Do not skip this; without it, R1's "every distinct user phrase" is unprovable.

## 2. The contiguity assumption is load-bearing and unverified → eliminate it, don't validate it

`pending_user` and `open_calls` as single global buffers only work if each session's messages are contiguous and ordinal-ordered in rowid order. Re-ingests, retries, or backfills break this, and the failure mode is *silent wrong attribution* — the worst kind.

**Fix:** key all state by sid: `state[sid] = {user_window: deque(3), open_calls: {}}`. Memory math: 55K sids × ~2KB cap = ~110 MB worst case; in practice only flagged sids get state, and if contiguity *does* hold the dict stays tiny via eviction on sid change. This makes the design correct under **arbitrary interleaving**, with ordinal sort per sid at emit time if arrival order was scrambled. The assumption becomes an optimization, not a correctness requirement. (Sanity-check contiguity anyway with a per-sid min/max rowid sample — if it holds, you get the small-dict fast path for free.)

## 3. The selective-read predicate misses `tool_result` → R4 dead on arrival

As written: "content_json only when block_types contains tool_use/human." But `tool_result` blocks carry their own block type (`tool_result`), typically in `role='user'` messages, and `human` isn't a block type at all. Concrete predicate:

```
read content_json iff:
  (role='assistant' AND 'tool_use' ∈ block_types)        # calls + drift counting
  OR (role='user' AND block_types ∩ {'text','tool_result'} ≠ ∅)   # phrases + outcomes
```

Assistant text-only rows are skipped — good, they're the long tail of bytes. Verify the block_types vocabulary on a sample first (see §8); don't assume it from the ingest code.

## 4. Aggregation key collapses all semantic-server calls into one row per service

Key is `(normalized phrase × service × tool × server_family)`. For semantic rows, `tool` is literally `mcp__google-workspace-semantic__google_workspace` for *everything* — so "send this email" and "list my labels" both aggregate as `(phrase, gmail, google_workspace, workato-semantic)`. R2 (attribute to the specific tool) is violated for your highest-value server family.

**Fix:** include `capability_id` (nullable) in the aggregate key. Semantic rows discriminate by capability; legacy/native rows by tool name. Also record `call_index_in_chain` (count of tool calls since last user turn) and `turns_since_user` per pair — cheap, and they're the QA downweighting signals you'll want in Phase D.

## 5. Native-row GAP classification is undefined without a tool→capability map

R6's GAP = "phrase with no capability match." Semantic rows carry `capability_id`; native rows carry only `gmail.users.messages.send`. Unless Phase D has a **config-driven tool→capability mapping** (per server family, many-to-one, versioned alongside the server taxonomy), every native-derived candidate is unclassifiable and your GAP report is semantic-rows-only. Build this map as part of the taxonomy config, not as judge-side logic.

---

## 6. Attribution (your risk #1) — endorse the measurement plan, sharpen it

Your calibration idea (semantic `request` vs. preceding turn) is the right move. Three refinements:

- **The semantic `request` field is not just ground truth for measurement — it's the better candidate phrase.** The model already performed coreference resolution ("now send that to the team" → "Send the Q3 summary email to the platform team"). Emit semantic-derived candidates with `phrase_source=request` as **tier-A**, raw-user-turn candidates as tier-B, and native rows with `turns_since_user > 1` or `call_index_in_chain > 3` as tier-C. The judge should see the tier.
- Calibration metrics to actually compute on semantic rows: (a) distribution of *which* preceding turn best matches `request` (t-1 vs t-2 vs t-3) → sets window W empirically instead of defaulting to 3; (b) near-match rate (embedding sim ≥ threshold) → the native-row attribution error rate; (c) rewrite-rate → how often `request` is anaphora-resolved, which tells you what fraction of native tier-B phrases are garbage without context.
- Keep the full preceding window in the pair record (you do), because the judge needs it to reconstruct intent for tier-B/C candidates. Aggregation keys on the trigger turn only.

## 7. IO mechanics (your risk #2) — one pass is correct; verify the layout assumptions that make it cheap

- Selective column reads only avoid the 110 GB if `content_json`'s payload lives in **overflow pages** and sits late in the record. Run `dbstat`/`sqlite3_analyzer` first: what fraction of pages are overflow? If content_json is mostly inline (small rows), the "selective read" saves little and you should just plan for a full 110 GB read (~20–40 min — still fine, but know it).
- Open with `file:...?mode=ro&immutable=1` (compliance corpus — no journal, no mutation risk), large `mmap_size`, big page cache. Rowid-range resume (`rowid > checkpoint`) is indexed-by-definition; snapshot the sid-state map every ~2M rows.
- **On the slim-view question: do both.** The main pass emits a slim sidecar (SQLite or parquet: flagged sids only, relevant block types only, fields capped) as a byproduct. Cost ≈ zero during the pass; all taxonomy/attribution iteration then runs against a ~1–5 GB artifact and you never touch the 110 GB again. A *separate* pre-extraction pass would be wrong; a *free byproduct* is right.

## 8. Privacy — bigger than flagged

`user_email` in aggregates is the least of it. The phrase text itself contains PII ("email sara@acme.com about the Acme-Corp merger"), and `semantic_facts_json` is *resolved* PII — names, addresses, file IDs. Your judge is an external model API. That's PII egress from a Compliance-API corpus to a third party, and "internal tool" doesn't cover it.

Concrete boundary (consistent with R9 — capture verbatim, clean downstream):

- Extractor + pair store: verbatim, restricted. `facts_json` retained **only** here (the canary needs resolved entities to build replayable templates; see §9).
- Phase D / learning-event creation: PII scrub (emails, phones, obvious names) before anything judge-facing. `user_email` → salted hash in aggregates; you only need distinct-user *counts* anyway.
- Note the tension honestly: scrubbed phrases are worse canary inputs. The canary should reconstruct from the restricted pair store, not from the learning event.

## 9. Judge handoff shape (your risk #5) — plus one thing you didn't list

Verify against the live schema, and add:

- **Provenance + idempotency**: `run_id`, `extractor_version`, `taxonomy_version` on every row; pair_id = `sha1(sid, ordinal, tool_use_id)`; learning-event key = `hash(norm_phrase, capability_candidate)` with dedupe against *existing* learning events (re-runs must not duplicate parked rows).
- **Evidence payload**: `success_rate` (resolver will weigh it), counts per R5, ≤3 example sids (bounded row size).
- **Replayability**: parked-pending-canary implies the canary can execute the candidate on your path. Verbatim phrases with embedded dates/names/IDs aren't replayable as-is — the canary needs slot-filled templates. That's promotion-pipeline work, but the extractor's job is to *retain the raw material* (facts_json, verbatim window) that makes template generation possible. Flag this dependency now or parked rows will pile up unprovable.

## 10. Pre-flight gates (the highest-value process change)

Do not run the full pass against assumed schemas:

1. **Gate 0** — 500-sid sample pass. Hand-inspect 50 pair records: block_types vocabulary, semantic input field names (`request` vs `semantic_capability_id` — verify, don't assume), tool_result location and `is_error` shape, taxonomy miss rate.
2. **Gate 1** — full pass; reconcile pair counts against `sum(google_tool_calls)` per sid; investigate variance > a few % (dangling calls in `complete=0` sessions will explain some — keep `outcome=missing` pairs, don't drop).
3. **Gate 2** — attribution-quality report on the semantic subset (§6 metrics) → set W and tier thresholds.
4. **Gate 3** — manual spot-check of 100 ADDs + 50 GAPs before *anything* writes to learning-events.

---

## What's already right (briefly)

Verbatim-at-capture with downstream cleanup (R9); config-not-code taxonomy — add an explicit `unknown` bucket with a rejects/audit log of every unmatched `mcp__*` name so the taxonomy evolves from evidence; parked-pending-canary for foreign-path evidence (R7) is exactly the right epistemics; capped phrase length — add a `truncated` flag so QA doesn't mistake a cut phrase for verbatim; `outcome=missing` as a first-class value.

**Bottom line:** fix the session-selection bias (§1) and per-sid state (§2) before anything else — those two determine whether the corpus is complete and correct. Everything else is calibration.