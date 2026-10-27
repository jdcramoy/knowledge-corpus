
---

# Re-investigation: gw-semantic nightly batch "dark 4 days" — watchdog P2 recurrence (2026-10-16)

Investigator: cortex probe (read-only, no Workato tools called) | Trigger: watchdog 2026-10-16 P2
"running=true but last-run dark 4 days" on folder 35404884; canary 82964017 stopped pending Josh;
dream report 2026-10-16 triage item 1 ("read the 10-11 rebuild session before touching a single recipe").

## VERDICT: NOT RETIRED-BY-DESIGN and NOT BROKEN — the dark signal is a false alarm (stale evidence pipeline)

Does not fit the offered trichotomy cleanly. If one token is required: the darkness claim is
FALSE-ALARM; only the post-10-15 state is UNDETERMINED (this dispatch was read-only, no live probe today).

## Evidence chain (3 independent sources)

### 1. The 10-11 rebuild wave CREATED and STARTED the batch — it cannot have retired it (build-ledger.jsonl)

The nightly batch recipes were not pre-existing recipes edited on 10-11 — they were born in the wave:

- ledger 11510: 2026-10-11T05:40:54Z `recipe_builder_init` gw_semantic_nightly_conformance (82963931), folder 35404884, session nightly-conformance-29504, ticket BSYS-29397
- ledger 11526: 2026-10-11T05:41:26Z `recipe_builder_init` gw_semantic_candidate_triage (82963934), folder 35404884, session bsys29505-triage, ticket BSYS-29397
- ledger 11991/12033: same-day inits for gw_semantic_error_hint_author (82964024) and gw_semantic_paraphrase_cluster (82964058), tickets BSYS-29504

Then the wave explicitly STARTED and VERIFIED them green:

- ledger 11657/11663/11709: `wt recipes start 82963931` (05:45:04Z, 05:45:11Z, 05:46:36Z) each followed by running:true check
- ledger 11711/11731: `wt recipes force-run 82963931` (05:46:40Z) and `force-run 82963934` (05:48:17Z)
- ledger 11753/11819: force-run jobs j-AbtHkbQb-oBNrds-CD and j-AbtHncgM-CE4GLG-CD awaited and status-checked
- ledger 11863: `wt recipes reset-trigger 82963931` and `reset-trigger 82964017` (05:56:00Z)

There is no stop, retire, pause, or deprecation entry anywhere in the ledger for any batch
recipe. Session transcripts (9f2bd9b7 + subagent a64b90a1, Google-Semantic-MCP workbench,
covering the 05:40–06:20Z build window) contain zero lifecycle stop/retire statements for
82963931/82963934. The wave's intent was the opposite of retirement: greenfield build, start,
force-run, verify.

### 2. Prior two-pass LIVE investigation (gw-semantic-nightly-batch-dark.md, 2026-10-15)

Two independent live passes (AIRO job_list + recipe_get, fetched 10-15) showed:

- 9/9 batch recipes fired AFTER the 10-11 wave; 8/9 fired on 10-15 itself
  (82963931 daily 07:13 green 10-12→10-15; 82963934 daily 06:00 green same; hourly rollups/
  stall-watch green through 17:5x PT; weekly_intelligence_digest 82888690 legitimately quiet
  since Monday — weekly cadence)
- The "frozen last_run_at 2026-10-11T05:46–06:17Z" is EXACTLY the wave's recipe EDIT times
  (AIRO "Last updated" column: 01:46–02:17 EDT = 05:46–06:17Z). The evidence source read
  recipe metadata `updated_at` as run activity.
- The batch recipes have NO stop cause: `stop_cause=trigger_errors_limit` filter over folder
  35404884 returns EXACTLY ONE recipe — canary 82964017 — the batch is a different world.
- BSYS-29656 (the wave's governing ticket family) contains no deliberate pause of the batch.

### 3. Today's P2 carries the same fingerprint

Watchdog 2026-10-16 P2 "dark 4 days" from 10-16 lands on the same 10-11/10-12 anchor — i.e. the
same `updated_at`-as-last_run misread the 10-15 investigation already root-caused. The fleet
liveness sentinel (82951201, which reads job traces correctly) did NOT report the batch dark —
only the metadata-reading sweep did, on both 10-15 and 10-16.

## The one REAL finding in the family (unchanged, do not merge)

Canary 82964017 is genuinely stopped (`trigger_errors_limit`, 14/14 lifetime jobs succeeded,
connector output-schema drift on the gateway runtime connector after 2026-10-14 00:45 PT) —
tracked in gw-semantic-nightly-batch-dark.md and 82964017 investigations, pending Josh per the
BSYS-29656 recurrence. It is NOT evidence about the batch.

## Limitations

- No live Workato probe today (read-only dispatch, pulse lane folder-denied): "batch green" is
  verified live through 2026-10-15 ~18:00 PT only. Post-10-15 darkness cannot be excluded from
  here — but no NEW defect evidence exists, and the only alarm is the one already root-caused
  as a metadata misread.
- No mission-control closeout row exists for BSYS-29397/29504/29502 (the 10-11 wave sessions
  are among the dropped-session population) — the ledger's start/force-run/verify entries are
  the surviving intent record, and they are unambiguous.

## Recommended Josh decision (one line)

Kill the alarm, not the batch: point the watchdog sweep's last_run source at job history
(job_list newest succeeded job) instead of recipe `updated_at` — the fleet liveness sentinel
82951201 already does this correctly and can be the source of truth — then separately decide
the canary 82964017 restart-vs-rebind call (real defect, still pending).
