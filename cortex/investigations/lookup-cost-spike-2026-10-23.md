# Lookup-class cost alarm 2026-10-23 — attribution (READ-ONLY sweep)

**Trigger:** cost-governor-2026-10-23 BUDGET ALARM — lookup cost proxy 148,348 (>2x median 20,800), pass 68% over 74 runs.
**Method:** decoded the governor's scoring (`knowledge/scripts/cost-governor.py`), re-scored all 74 in-window lookup rows in `cortex/dispatches.jsonl` against on-disk logs in `~/.local/state/cortex/`, reconstructed the 10-14→10-23 trend from prior reports. Follow-up to the 2026-10-11 `lookup-cost-spike-attribution.md` investigation (same alarm, same shape).

## Q1 — which dispatches/tasks drove the spike

Nobody did. The 148,348 is Σ dispatch-log bytes, and it is volume, not weight:

- 74 ledger rows = **56 unique dispatches + 18 duplicate double-appends** (77 lifetime duplicate rows in the ledger; deduped byte total 144,820). The dispatcher has been appending the same row twice.
- Largest single dispatch: 4,511 bytes (`fleet-cost-collector-dark` attribution, 10-19) = 3.0% of the total. Top 15 rows ≈ 38%. Long tail of heterogeneous cortex ops lookups at ~1–4 KB each.
- Per-run, lookup stays the cheapest class: ~2.0 KB per row (~2.6 KB per unique dispatch). No runaway job, no single expensive task, no burst cluster — steady 6–9 dispatches/day, flat ~16–32 KB/day.

The >2x-median condition is structural: lookup is the cortex's most-dispatched class and the proxy byte-sums its logs, while the class median is dragged down by near-zero rows (triage-lane 113, judgment 46). Any week lookup is the workhorse, it crosses 2x median by construction.

## Q2 — do failures cluster by query type or time window

**By time, yes — but the cause is an instrumentation change, not the workload or the model.** Raw re-score with the governor's own rule (74 rows): 49 pass, 23 FAIL-NOLOG, 2 GATED → 68%. Decomposed:

- **16 of 23 fails = relative-path false-fails.** Starting ~2026-10-20T00:08Z the dispatcher began writing BARE relative filenames (`dispatch-20261020T000840Z.log`, no directory) into the ledger's `log` field. The governor's `Path(...)` resolves them against its own CWD, misses, and scores FAIL — but all 16 logs sit non-empty on disk in `~/.local/state/cortex/` under the same basename. The 10-11 fix added `expanduser()` (line 178) but not relative-path resolution. This explains the pass-rate dip 77–78% → 68–73% over 10-20→10-23: an instrument change on 10-20, not model degradation. Failure "clustering" is exactly the back half of the window, starting the day the naming convention changed.
- **Every one of those 16 has its findings file persisted** in `cortex/investigations/` (morning-brief-run-missed-1019, scheduled-tasks-wipe-attribution, recipe-83191713-identity, claimed-built-stamps-audit, registry-backup-tcc-denial, bsys-29383-snowflake-upsert-unmapped, nightly-receipts-no-output, recipe-deletions-404-1021, mood-setter-stale-182h, canary-handler-82971161-stopped, dropped-609a5f17-edit-inventory, harness-backup-heartbeat-gap, jobfile-restoration-verify, gym-unreadable-1022-batch-verify, dreamer-heartbeat-writer, canary-alarm-loop).
- **6 truly-missing logs** (deduped: 10-16 kb-uncommitted-edit-ownership, 10-19 05:45z kb-sync + 29519-ftr pair, 10-20 09:45z 29744-genie-identity + build-now-proposals pair, 10-22 em-delivery-canary-loop) — and all six ALSO have their investigation files on disk. The logs were lost/never written; the findings were not.
- **3 GATED** (redteam-dr-moment 10-18, recipe-deletions 10-21, docs-sync verify 10-22): the known write-gate class — the sanctioned bus-persistence credit never fires because `dreams/bus/cortex.jsonl` contains zero `type: investigation` rows, so the exempt-from-denominator path is the only thing saving these from being scored fails.
- **Zero genuine model-quality failures found.** Corrected score: 49 + 16 recovered = 65 pass / 72 scored = **90%** (deduped unique: 47/53 = 89% with 3 gated). No query-type clustering — fails span canary, KB-sync, registry, fleet-cost, recipe-identity, receipts, a cross-section of ordinary ops lookups.

## Q3 — one-off vs trend

**Not one-off; sustained and structural.** The identical alarm has fired in every daily report since 10-14: lookup pass 68/72/73/77/78/78/79%, cost proxy 112,542 → 134,389 → 143,209 → 149,623 → 286,546 → 230,509 → 166,745 → 148,348 — always >2x median, always on glm-5.3-flash. The 10-11 investigation already diagnosed the same shape at 65%/41 KB. The 10-18 spike to 286,546 was the only transient (one heavy day, self-normalized). Within the current window there is no growth loop — the level is flat and benign.

## Verdict

Sustained-but-benign again, now with a second-generation root cause. The alarm is the same defect wearing two new faces: (a) duplicate ledger rows inflating the denominator, (b) a 10-20 dispatcher convention change to relative log paths turning 16 successful lookups into scored fails. The 68% is 100% instrumentation artifact; true corrected pass ≈ 89–90% with all 74→56 unique dispatches' findings persisted somewhere on disk.

**On the proposed kimi-k3 upgrade trial: same answer as 10-11 — it would fix neither the cost nor the pass rate.** Both failure classes are model-independent (path resolution + ledger dedup + write gate). The trial would burn a week confirming a null result.

Fixes (proposals only — Josh approves):
1. `cost-governor.py`: when `log` is not absolute, resolve against `~/.local/state/cortex/` before scoring fail — one line, recovers 16 of 23 false-fails (mirror of the 10-11 `expanduser` fix).
2. Dispatcher: write absolute paths into `dispatches.jsonl` (the 10-11 discipline partially regressed ~10-20 — identify which writer changed).
3. Dedupe the ledger: 77 lifetime duplicate lookup rows (double-appends); upsert on (ts, log, task) at write time, or have the governor dedupe before summing.
4. The bus-persistence credit is dead code (0 `investigation` rows ever) — either fix the bus-posting convention or stop counting GATE_MARKERS logs against the pass rate at all.
