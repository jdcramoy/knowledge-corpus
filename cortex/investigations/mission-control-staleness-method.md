# Mission-control staleness methodology — fold/board vs flat-ts (investigation 2026-10-13T05:0xZ)

Read-only investigation. Evidence: `scripts/mission-control.py` (170 lines, read end to end),
`mission-control/registry.json` (77 rows, folded_at 2026-10-13T04:48:05Z), `events.jsonl`
(209 events, 77 distinct workstreams), `cortex/questions.jsonl:130`.

## Verdict in one line

**The fold script computes NO staleness for non-done workstreams at all** — the only age logic in
the codebase is `STALE_DONE_DAYS = 14` (mission-control.py:42), applied exclusively to
`state == "done"` rows (lines 69-76, drops them off the board). Neither "staleness stable at 2"
nor "flat-ts 11 stale" is canonical, because neither is implemented in the script; both are
cortex-layer overlays using the same ad-hoc rule (max-ts per workstream, state != done, > 24h).

## Exact code path in fold()

`fold()` (mission-control.py:58-82):
1. Replays events.jsonl; `reg[w] = e` — last event per workstream wins (line 64). No age filter here.
2. Done-drop window only: for `state == "done"` rows, parse `ts` and `continue` (drop) when
   `(now - ts).days > STALE_DONE_DAYS` (lines 68-76). Non-parseable ts silently keeps the row.
3. Sort key `(STATES.index(state), ts)` (lines 77-79) — ts is a **sort tie-break within a state
   group**, not a staleness computation. The oldest row merely sorts to the top of its state group.
4. Writes registry.json with `folded_at`. Nothing anywhere thresholds non-done age.

`board(rows)` (lines 89-119) renders **every** row, grouped by state in fixed order
(needs-josh, blocked, in-flight, done), each card's meta line carrying the raw `ts`. It contains
zero staleness logic — no 24h line, no stale marker, no age highlight. The 27 occurrences of
"stale" and 2 of "24h" in the current board.html are all **row content** (workstream names like
`stale-jira-review`, prose in what/why/needs fields, one pulse-closeout note quoting
">24h") — none from the renderer.

## Why 2 and 11 disagree: same method, different clock times

The "stable at 2" figure traces to the cortex pulse at **2026-10-12T21:25:48Z**
(questions.jsonl:130): "bsys-28296-marketo-history (blocked 24.4h) and kb-wave3-sources
(in-flight 24.4h) are the only two workstreams past the 24h staleness line", computed over a
55-workstream fold. Reproduced exactly:

| Measured at            | stale (>24h, non-done, last-event-per-workstream) | count |
|------------------------|----------------------------------------------------|-------|
| 2026-10-12T21:25:48Z   | kb-wave3-sources, bsys-28296-marketo-history       | **2** |
| 2026-10-13T01:00:00Z   | same two                                            | **2** |
| 2026-10-13T04:50:00Z   | the 11 listed below                                 | **11**|

The two numbers are **both correct snapshots of the identical rule**. The 9 extra rows were all
last touched 2026-10-12T01:02–04:42Z (the evening closeout batch: hr-genie-workday-mcp,
btsup-service-desk, ai-roi-framework, stale-jira-review, jira-stale-review, workato-watchdog,
jira-autotriage-hr-genie, bsys-28296-marketo-mcp, hr-genie-monitoring-401) and crossed the 24h
line between ~01:02Z and 04:50Z on Oct 13. No tie-break or grouping difference exists; both
computations use max-ts-per-workstream and exclude done. "Stable at 2" was stable only until the
batch aged — the word "stable" was the error, not the count.

The 11 at 04:50Z: kb-wave3-sources (in-flight, 31.9h), bsys-28296-marketo-history (blocked,
31.9h), jira-autotriage-hr-genie (in-flight, 27.8h), hr-genie-workday-mcp (needs-josh, 27.8h),
btsup-service-desk (needs-josh, 27.8h), ai-roi-framework (needs-josh, 26.2h), stale-jira-review
(needs-josh, 26.1h), jira-stale-review (needs-josh, 26.1h), workato-watchdog (needs-josh, 25.4h),
bsys-28296-marketo-mcp (in-flight, 24.4h), hr-genie-monitoring-401 (needs-josh, 24.1h).

## Which is canonical

As built: **neither** — the script defines no non-done staleness, so there is nothing canonical to
disagree with. The flat-ts 24h line is the de facto convention because it is the only consistent
definition any consumer applies, but it lives in pulse prompts, not in code, so it can drift per
session. If Josh wants a canonical number, the threshold belongs in `fold()` (e.g. a
`STALE_OPEN_HOURS` constant emitting a `stale: true` flag into registry rows that board.html and
`needs` can render). Definitional caveat worth settling when that happens: **needs-josh rows are
7 of the 11** — under the current rule, staleness flags Josh's own unanswered items as if they
were agent drift. The pulse may want needs-josh excluded, or labeled separately ("waiting on Josh
26h"), before this number routes attention.

## Does board.html display the stale cohort?

**Yes, fully — but unlabeled.** All 77 workstreams render (needs-josh 25, blocked 2, in-flight 11,
done 39), so all 11 stale rows appear inside their normal state groups with their raw ts in the
meta line. Nothing marks them stale, sorts them by age across groups, or summarizes the count;
a reader must eyeball timestamps. The board's only age-driven behavior is inherited from fold:
done rows vanish past 14 days, and stale non-done rows persist indefinitely.

## Method note

Flat-ts reproduction used the same fold semantics as the script (last event per workstream by
string ts comparison — safe here because all ts are same-format UTC Z strings). All measurements
cited above were run live against events.jsonl this session.

Nothing unverified beyond: the pulse's "55-workstream fold" figure was taken at its word (the
event log has since grown to 77 workstreams; 55 was plausible at 21:25Z and immaterial to the
conclusion). No files were modified other than this report.
