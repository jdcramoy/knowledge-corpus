

# KB digest lens degradation — root-cause investigation (cortex lookup, 2026-10-09 11:05Z dispatch)

Investigator: cortex lookup (flash), read-only, sources limited to ~/.claude/knowledge per dispatch scope.
Dispatch: cortex/dispatches.jsonl 2026-10-09T11:05:52Z, class=lookup.

## Sources read (all inside the allowed tree)
- kb-digests/*.md (all 6 agent files)
- dreams/bus/workato-kb.jsonl (all sync + entropy lines)
- dreams/bus/cortex.jsonl, harness-dreamer.jsonl, brain-gardener.jsonl, project-dreamer.jsonl, workato-watchdog.jsonl, orca-main.jsonl (digest/lens/2018 mentions)
- garden-reports/2026-10-08-brain-gardener-full-pass.md and -nightly.md (KB digest opinion sections, pipeline-defects echo)
- projects/workato-kb.md (full version history: v0.2.0 through v0.9.2, v0.7.0 record)
- INDEX.md line 30 (v0.7.0 record), morning-brief/2026-10-08.md
- triage/queue.jsonl line 33 (kb-digest-degraded-lens card, open)
- cortex/attention-queue.md + attention-queue-2026-10-09-1003.md

## Q1: The date lens hits stopped being current

**Bounded, not pinned: no later than the 2026-10-08 22:07 digest run.**
- The only surviving digest files are the 6 agent files in kb-digests/, all headered
  2026-10-08, and ALL already show 2018-era changelog lens hits (harness-dreamer's
  "new platform launches" lens returns June/May/August 2018 Product Release posts;
  cortex's changelog lens returns "On-prem file major update 2018"). kb/digest.py
  overwrites these files per run — no dated archive exists anywhere in the tree
  (find confirmed: kb-digests/, scripts/morning-digest.py, dreams/data/2026-10-08-lens-digest.md
  which is the dreamer's deep-pass report, not a digest archive). So no pre-degradation
  digest survives to compare against.
- Earliest bus observation of 2018-era lens hits: cortex.jsonl 2026-10-09T00:20Z
  ("the changelog lens returned a 2018 on-prem retro at 0.0 bits"). Two further
  independent cycles: 04:28Z (watchdog-corroborated) and 06:40Z. The "3rd day"
  arithmetic in the 10:05Z finding counts observation cycles across the digest's
  short life, not calendar days of a previously-healthy lens.
- Critically: there was likely never a healthy baseline. The digest fan-out itself
  (kb/digest.py) shipped in v0.3.0, which landed in the SAME 2026-10-08 overnight
  build as v0.7.0 (projects/workato-kb.md records the whole v0.2.0→v0.7.0 arc in one
  night). The first digest run was already post-v0.7.0. The gardener's 14:55Z Oct-8
  opinion describes the change surface only (docs/changelog counts), not lens-hit
  dates, so it neither confirms nor refutes an earlier healthy lens.

## Q2: Does onset coincide with kb-pipeline v0.7.0?

**Yes within hours, but the correlation is unprovable by artifact — there is no
pre-v0.7.0 digest to exonerate or indict it.**
- v0.7.0 (fa315cc, "THE FIVE LEAPS", built overnight 2026-10-08, Josh: "build it all")
  rewired the retrieval stack: (4) fractal memory — 64,238 factlets, zoom retrieval,
  explicitly ADDITIVE over existing stores; (5) MRL funnel — LLM situating lines as a
  coarse PAGE layer (1,683 coarse-embedded) with a coverage guard (coarse dist > 0.65
  → plain fine search).
- v0.7.1 (e78067a, same day) then found the v0.7.0 funnel design was itself a recall
  risk — "the coarse distance distribution (0.72-0.84 for everything relevant) makes a
  distance-gated shortlist a recall risk; final design = unrestricted fine search +
  rank-based page-affinity boost" — i.e. the v0.7.0-era coarse path was demonstrably
  degrading fine recall within hours of landing, and was simplified in response.
  Whether digest.py's lens-call path picked up the v0.7.1 simplification is
  NOT verifiable from the knowledge tree (repo read blocked, see below).
- Two zero-confidence lens results in the surviving digest (project-dreamer docs lens
  0.0 bits, watchdog changelog lens 0.0 bits) plus 1.4-1.6-bit 2018-dominated hits
  elsewhere are consistent with either (a) the digest path still routing through a
  coarse/title-dominated layer, or (b) generic keyword lens queries with no recency
  weighting over a corpus that legitimately contains 2018 "Product Release" posts
  whose titles exactly match terms like "release"/"launch"/"update". Cortex's 04:28Z
  read independently favors (b): "digest lens queries could use a freshness filter
  rather than raw relevance." Both mechanisms produce the same symptom; (a) is a
  v0.7.0 regression, (b) is a design gap that v0.3.0's digest inherited and v0.7.0's
  rerank/funnel changes may have surfaced. The two are distinguishable only by
  reading kb/digest.py and probing live retrieval — both blocked in this scope.

## Q3: Corpus or retrieval layer?

**Retrieval layer. The corpus ingestion chain is demonstrably current.**
Evidence for corpus currency:
- Sync reports on the bus are healthy and show CURRENT deltas reaching the digest:
  workato-kb.jsonl 2026-10-08 02:19 (3,368 docs changed, 1 error — the confluence
  days-arg bug, found and fixed before v0.7.1's first launchd run), 10:32 (3,078
  changed, 0 errors), 21:52 (3,327 changed, 0 errors).
- The digest change surfaces show Oct-2026 content flowing: gardener 14:55Z read
  "the Oct 7 2026 changelog delta (Community Connectors release) is the only product
  delta touching active work" — a 2026 changelog post was seen by the same pipeline.
- v0.7.2 integrity: "KB pages 10,288/10,288" coverage, sync pipeline verified clean
  end-to-end.
Evidence against retrieval:
- The changelog lens returns 2018-dated pages as top hits for "new launch" intent at
  ~1.4-1.6 bits — ranking failure, not absence of current content.
- The digest's own index line disagrees with the verified index: all six digests say
  "index: +0 docs, 25,800 chunks, 25800 embedded" while v0.2.0's live-verified
  integrity line (projects/workato-kb.md:287) says 10,274 docs / 63,952 chunks and
  v0.7.0 says 63,918 chunk factlets. 25,800 matches NO recorded index state. The
  digest's index-stats read is pointing at the wrong store (or a partial one) —
  the same class of error as a lens query reading the wrong layer. Note "+0 docs"
  alone would be normal for sha-based incremental re-chunking (changed docs re-chunk
  in place, count unchanged); the 25,800 number is the real anomaly.

## Q4: Minimal fix shape and owner

**Fix shape (minimal, 3 parts, all in the kb repo ~/Documents/workato-kb):**
1. kb/digest.py lens retrieval: add recency weighting for time-sensitive sources
   (changelog especially) — a date-aware rank multiplier or a last-N-days window on
   lens queries. This is the fix cortex itself recommended at 04:28Z.
2. Resolve the index-stats read: find where digest.py gets "25,800 chunks" and point
   it at the real index (63,952) — cheap, and it converts the digest's own header
   into a freshness canary.
3. Add a digest self-assertion: top changelog lens hits must include a post within
   N days of the sync date; failure posts to the bus instead of silently degrading.
   (Absent assertion is why this ran 3 cycles before anyone measured it.)

**Owner: dreamer-proposal class, not gardener hygiene.** Reasons:
- The fix is a code change to retrieval ranking in the kb repo. The gardener has no
  repo-write authority and reports/branches only (garden-reports nightly: "no branch
  created... on approval"); the gardener already correctly dispositioned the
  dreamer's pipeline-defects thread as "KB-owner work items; echoed to the bus as
  corroboration, not re-filed".
- Cortex's own routing note at 06:40Z: "digest lens needs a recency filter or better
  query set (gardener/dreamer class, not cortex-editable)."
- A triage card is ALREADY OPEN: triage/queue.jsonl line 33, slug
  kb-digest-degraded-lens, kind=hygiene, 1pt, status=open, filed by cortex 10:05Z.
  Recommended path: resolve that card into a dreamer proposal (spec: the 3-part fix
  above; dissenter pass per constitution), then build on Josh's approval. The
  gardener's only action is recording this finding and keeping the claims/index
  line for workato-kb accurate — no index surgery needed.

## Separate defect found en route (forward-looking corpus risk, NOT the lens bug)

- workato-kb.jsonl 2026-10-09T03:22:32: "KB sync 2026-10-09: 0 docs changed across
  **1 sources**; errors: 0" — previous runs reported 15 sources. One source scanned
  is not a healthy no-op; if it persists, the corpus WILL go stale within days and
  the lens question becomes moot. Different failure mode than the lens degradation
  (this one is genuinely stale-corpus). Needs eyes on the sync runner config in the
  repo — blocked in this scope, flag to the same proposal/triage card.

## Blocked-unverified (sources outside the allowed tree)

1. kb/digest.py and kb/funnel.py source — repo ~/Documents/workato-kb. Cannot confirm
   which search path the digest lens calls (fine search vs funnel/zoom coarse layer)
   or where the 25,800 number originates. THE key unverified link.
2. Live retrieval probe (kb_search / kb CLI against the live index at
   ~/.claude/workato-kb) — would distinguish digest-path-only degradation from a
   global retrieval regression in one call. Not run: outside the read-scope.
3. Pre-2026-10-08 digest runs — none archived anywhere in the tree (overwrite-per-run
   design). Onset before 22:07 Oct 8 cannot be established from artifacts.
4. sync runner config explaining "1 sources" on the Oct-9 run (same repo).

## Verdict

Retrieval-layer degradation, onset no later than the first v0.7.0-era digest run
(2026-10-08 22:07), same-night as the v0.7.0 retrieval rewiring but without a
pre-v0.7.0 baseline to prove causation; corpus is current. Minimal fix is recency-
weighted lens retrieval plus an index-stats read repair and a freshness assertion,
owned as a dreamer proposal resolved from the already-open triage card; a separate
sync-shrink (1 of 15 sources on Oct 9) is the more urgent of the two defects for
corpus health and should ride the same card.
