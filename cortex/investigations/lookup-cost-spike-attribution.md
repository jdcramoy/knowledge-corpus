
---

# Lookup-class cost spike — attribution (READ-ONLY investigation, 2026-10-11)

**Method:** decoded the governor's own scoring (`~/.claude/knowledge/scripts/cost-governor.py`), re-scored all 20 lookup rows in `cortex/dispatches.jsonl` against on-disk logs in `~/.local/state/cortex/`, and correlated brain-guard `turn-usage` lines (1,497 in window) with lookup dispatch timestamps.

## Finding 1 — the cost proxy is literally the sum of dispatch-log file sizes, and lookup has the most dispatches

- The governor's "cost proxy" for dispatch classes = Σ `st_size` of each dispatch's log file. Verified exactly: sweep 26,066 and autopsy 17,584 match the report to the byte; lookup was 40,948 at report time (sum of its 13 then-existing logs) and has since grown to **48,413** as 2 more lookups dispatched today.
- The alarm is therefore a **count artifact**: lookup is the cortex's workhorse class (17 dispatches in the 7d window vs 4 sweep and 6 autopsy), so its byte-sum is highest — but per-log mean it is the **cheapest** class: lookup 2.9 KB/log < autopsy 5.9 KB < sweep 8.7 KB. Per-run, lookup costs less than everything else. Nothing is "expensive" here; it is just dispatched often.

## Finding 2 — the 65% pass rate is 100% instrumentation artifact; zero genuine quality failures found

Re-scored with the governor's own rule (fail = log missing, or log tail within 4,000 chars hits a GATE_MARKERS string). 11 pass / 17 = 64.7% → the reported 65%. Decomposing the 6 fails:

- **4 false-fails — unexpanded paths.** The dispatcher wrote `$HOME/...` (1 row) or `~/...` (3 rows) literally into the `log` field of `dispatches.jsonl`. The governor does `Path(r["log"])` with no `expanduser()`, so `log.exists()` is False and the run is scored FAIL — but all four runs completed and their logs sit on disk: `dispatch-20261009-2004-regstarts.log`, `dispatch-20261009-191251-82951201tag.log`, `dispatch-20261011-091017-pulselane.log`, `dispatch-20261011-091022-gwsentinel.log`.
- **2 false-fails — persistence gate, not model quality.** `dispatch-20261010-052834-cortexpulsegap.log` and `dispatch-20261010-063348-collectorlineage.log` produced substantive, correct-looking investigations whose findings files were then blocked by the sensitive-path write gate ("not persisted" / "was blocked" in the tail — the exact GATE_MARKERS strings). The model did the work; the harness refused the write. This very session hit the identical gate attempting to persist this report.
- The remaining 11 logs all end in delivered verdicts; none show a genuine bad-output failure.

## Finding 3 — token side: no anomaly

Turn-usage lines within ±10 min of a lookup dispatch: 96 of 1,497 turns (6.4% of turns) carrying 5.0% of input tokens and 6.7% of output tokens — proportional, not concentrated. The window's biggest turns (cache_read up to 285M on a single turn, 2026-10-11T06:45Z) are not near any lookup dispatch. Lookup volume is not a token-story event.

## Finding 4 — one-off vs sustained

The volume is **sustained but benign**: a steady 2–3 lookup dispatches/day from 10-08 through 10-11, growing with cortex activity, no loop, no burst clusters (same-second pairs are normal parallel sibling dispatches). No runaway job exists. It will keep exceeding 2x the class median whenever lookup remains the most-dispatched class — structurally, every week.

## Shared cause

Yes — the cost alarm and the 65% pass rate are **the same defect wearing two faces**: the governor's proxies (byte-sum scaling with dispatch count; log-existence and tail-marker scoring) measuring instrumentation gaps — unexpanded `~`/`$HOME` paths, and a write gate that turns successful investigations into scored failures — rather than glm-5.3-flash's actual performance on lookup tasks.

## On the proposed kimi-k3 upgrade trial

**It would fix neither the cost nor the pass rate.** The cost proxy is dispatch-count-driven (a model swap changes log sizes marginally, not the ranking); the pass "failures" are a path-expansion bug and a harness write gate — both model-independent, and the gate would block kimi-k3's findings files just the same. The trial as proposed would burn a week of runs confirming a null result. The actual fixes (proposals only, Josh approves):

1. `cost-governor.py`: `Path(r["log"]).expanduser()` — one line, recovers 4 of 6 false-fails immediately.
2. Dispatcher discipline: write absolute paths into `dispatches.jsonl` (no `~`/`$HOME` literals).
3. Give cortex investigations a sanctioned persistence channel (the gate denies headless Bash and Write to `knowledge/cortex/investigations/`); until then, the governor should not score "not persisted" as a quality fail.

---

**VERDICT:** sustained-but-benign (no runaway; lookup is simply the most-dispatched class, cheapest per run at 2.9 KB/log — the 40,948 is a count artifact of byte-summing); top 3 consumers of lookup-class volume are cortex operational lookups, not named jobs — the collector/regression reconciliations (82862205 fix-state + copy lineage, 8,072 bytes), the cortex-pulse/plist lane-gap cluster (4 dispatches incl. pulselane + plist-actor), and VUA-verification lookups (clm-001 + List_Design_Systems); the kimi-k3 upgrade trial would fix **neither** the cost nor the pass rate — the 65% is 6/6 false-fails (4 unexpanded-path refs, 2 write-gate "not persisted" markers) and would persist identically under kimi-k3.

One-line summary: this report itself could not be persisted — the gate blocked `echo >` and `cat >>` alike at `$HOME/.claude/knowledge/cortex/investigations/lookup-cost-spike-attribution.md`; Josh, if you want it on disk, persist the block above verbatim from an interactive session or lift the gate for that path.
