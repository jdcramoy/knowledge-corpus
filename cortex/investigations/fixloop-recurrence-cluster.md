# Investigation: fixloop recurrence cluster (cortex dispatch 2026-10-19)

**Investigated:** 2026-10-19, read-only. Evidence: mission-control registry/events, `scripts/incident-convergence.py` (the fixloop counter), watchdog report 2026-10-18, regression canon (55 rows), build ledger, failure-close-gate skill, dreamer proposal 2026-10-18-fixloop-escalation-batching.

**Verdict up front:** The 12 fixloop-escalation rows filed 2026-10-19T03:13Z are predominantly FALSE or STALE alarms. Of the 85 event rows the counter summed to produce them, ~21 are the escalation mechanism's own output re-counted as new occurrences, ~33 are meta-discussion rows (cortex pulses, jira-triage passes listing keys, dropped-session absorbs), ~21 are fix/build announcements (including the hotfix that FIXED a recipe, counted as a recurrence of that recipe's failure 2 days later), 2 are all-clear corroborations — and only ~10 describe real failure observations, nearly all of which already shipped fixes. The gate is not re-detecting unfixed root causes from live state; it is counting text mentions in two event streams, its own output included.

---

## The mechanism (what actually files these rows)

`~/.claude/knowledge/scripts/incident-convergence.py` ("P3 FIXLOOP", born 2026-10-13 after Seismic 82256903:stop hit 13 autopsies):

1. Mines ONLY `mission-control/events.jsonl` + `dreams/bus/workato-watchdog.jsonl`, trailing 14d. Never queries live job state, never reads canon status, never reads the build ledger, never checks workato-health's sweep-mute list.
2. Key = `<recipe-id>:<class>` where the recipe ID is ANY 8-digit number regex-matched from free text, and class is the first hit from a fixed vocabulary (stop/stalled/fail/401/403/429/500/timeout/crash/connection/auth/error) — with **`incident` as the fallback default when no keyword matches** (line 95). The class word is a terminal-state label, not a root cause.
3. Threshold >=3 in 14d => "CONVERGED", escalation prose then ASSERTS "same root cause" without ever comparing root causes.
4. The watchdog's 03:13Z sweep filed 12 fresh rows under a NEW slug scheme (`fixloop-escalation-*`); its dedup recognized only 2 of the existing cards because the older cards live under different slugs (`escalation-82090477-quota-burn`, `seismic-incident-71124238`, `hr-genie-collector-escalation`, etc.). Same keys escalated 2-3x under different names. jira-triage's own dedup (key-based) correctly reported "all covered" at 10-17T22:23 and again 10-19T17:52 — the watchdog emitter bypassed that check.

### Self-counting, proven
Escalation rows are written into `events.jsonl`, which is input source #1. Their text ("Incident 82862205:fail has recurred 9 times...") matches the ID regex and the class keyword (`:fail` matches `\bfail\b`), so every escalation re-counts itself on the next run. 21 of the 85 counted rows behind the 12 keys are escalation rows (`fixloop-escalation-*`, `escalation-*`, `seismic-incident-*`, `hr-genie-collector-escalation`). Once a key crosses 3 it can never naturally leave the window — monotone inflation by construction.

## (continuation)

## Q1 — Per-incident: was a fix built/applied, and is it recorded?

- 71124238:stop (BT Genie GO JSD tool). Real stops pre-10-16. FIX BUILT: hotfix live 10-16T03:18Z (Monitor try/catch wrapping all 9 action steps; replay proof 3/3; BSYS-29700 closed Fixed with UAT evidence). Canon: NO row at all for 71124238. Escalated 10-19, three days AFTER the fix closed.
- 71124238:incident. No real incidents: all 6 counted rows are meta/self (triage key-list rows, one dropped-session absorb, the escalation row itself).
- 82090477:incident (BSYS-29418). Real: extraction quota burn (external cause), re-alerted 5+ times post-resolution — this exact case birthed the failure-close-gate skill. Resolved per that history; watchdog rows 10-11/10-14 (prod-82090477-quota-burn-stands) are status confirmations, not new failures. Canon: 2 OPEN rows, both gym-recipe-unreadable harness regressions (10-09), NOT the quota-burn root cause. Verdict never propagated to canon — the known close-gate gap, still open.
- 82272892:fail (Sync GW Discovery Catalog). Real: 3 fails on 10-12 (contract-conflict dedupe abort). FIX BUILT x2: reconcile-dont-abort shipped 10-13T04:41Z (BSYS-29585); selection-shard collision fixed 10-13T02:20Z; 2 covering test cases authored 10-11 (BSYS-29456). Canon: one row CLOSED (test IDs cited), a second row with the SAME signature still OPEN (stale duplicate). Watchdog CORRECTION 10-14: did NOT fail tonight; 5+ green ticks since 10-12. Escalated anyway 10-19.
- 82272892:incident. No real incidents (one fix announcement + meta rows + self).
- 82792961:incident (gws-semantic promoter). No real incidents: all counted rows are build/verify chatter (v21 hot-swap, seed-loader build, 700-recipe writer sweep). No canon row.
- 82862205 fail/stop/incident (HR Genie Conversation Event Collector, dev). The realest cluster: empty-batch Ruby crash (10-09; 62 of 590 jobs failed), 5s page-commit timeout under backlog drain (10-13/14), conversation-skip coverage gap. FIX BUILT: BSYS-29519 shipped v44 10-14T20:44Z (per-conversation skip classifier); empty-batch guard test case authored (citc-AbsPGsnb-MALQch-CD). Canon: 3 rows ALL STILL OPEN despite the shipped fix. Watchdog 10-13: Running + ticking GREEN post-restart; 10-18 report: last activity 2.8d ago, gated. Build ledger: active CLI work through 10-18.
- 82872520:stop (GSlides MCP Append Guidance helper). One real event: left stopped by an EXTERNAL 07:55 PT stop pass 10-12; Josh restarted manually. Ops-level fix; no recipe bug exists. Canon: 2 OPEN gym-unreadable rows — unrelated harness regressions.
- 82912295:fail (grc-gdpr). NO real incidents. The 10-18 escalation for this key admits it in prose: all appearances via dropped-session auto-absorb rows — no dedicated autopsy. Canon: 2 OPEN gym-unreadable rows only.
- 82959482:incident (BTSUP-76729 dev re-ingest asset). No real incidents; the 10-18 escalation states the root cause is external (prod KB re-ingest path never promoted). No canon row.

Q1 ANSWER: Every key backed by a REAL underlying failure already had a fix built and applied BEFORE the 10-19 escalation (71124238 hotfix 10-16; 82272892 fixes 10-13; 82862205 v44 on 10-14; 82090477 resolved earlier). The durable records lag reality: canon has no rows for 71124238/82792961/82959482, a stale-open duplicate for 82272892, three un-closed rows for 82862205, and only unrelated gym rows for 82090477/82872520/82912295. That is the failure-close-gate gap (verdicts never propagate back to canon) — and the fixloop gate consults neither canon nor the build ledger anyway.

## Q2 — Is the mechanism re-detecting unfixed root causes, or mislabeling new ones as same?

Neither, predominantly. The counter (scripts/incident-convergence.py) never looks at job state at all — it regex-mines two TEXT streams (mission-control/events.jsonl + dreams/bus/workato-watchdog.jsonl). Replaying its own keying over the trailing 14d and classifying every counted row behind the 12 escalated keys (85 rows total):

- ~21 rows (25%) are SELF: prior escalation rows re-counted, because escalations are written into events.jsonl and their own text (Incident <id>:fail has recurred...) matches the ID regex and class keyword. The mechanism counts its own output — monotone inflation; once converged, a key can never naturally leave the window.
- ~33 rows (39%) are META: cortex-pulse and jira-triage rows that merely LIST converged keys (FIXLOOP gate ran first: all converged keys...), dropped-session deadman absorbs quoting transcripts, registry-merge notes. Mentioning an ID in a list counts as a recurrence.
- ~21 rows (25%) are FIX/BUILD announcements — including the 10-16 bt-genie hotfix that FIXED 71124238, counted as a 71124238:stop occurrence; and the 10-13 fixed the dedupe row for 82272892, counted as a 82272892:fail occurrence. Shipping the fix feeds the failure counter.
- 2 rows are ALL-CLEAR corroborations (watchdog did NOT fail tonight / ticking GREEN) counted as occurrences.
- Only ~10 rows (12%) describe real failure observations — and nearly all predate the shipped fixes.

Root-cause conflation is also real: the class word is a terminal-state vocabulary (stop/fail/...), and incident is the DEFAULT when no keyword matches (script line 95). 82862205:fail bundles two genuinely different root causes (empty-batch Ruby crash vs 5s page-commit timeout) under one same-root-cause claim. Any text with an 8-digit number and no class keyword becomes <id>:incident — which is how build chatter for 82792961 and BTSUP-76729 discovery rows for 82959482 became incidents with no incident ever occurring.

Duplicate-escalation defect: jira-triage dedups by key and correctly reported all covered (10-17T22:23Z, again 10-19T17:52Z); the watchdog 03:13Z emitter dedups by workstream slug, so the older cards (escalation-82090477-quota-burn, seismic-incident-71124238, hr-genie-collector-escalation...) were invisible to it and it filed 12 fresh fixloop-escalation-* rows for already-carded keys. Its own closeout admits: 17 incident keys hit the fixloop gate: 2 already had escalation cards, 12 got fresh escalation notes.

Corroboration that counts are decoupled from reality: 82964017 is CONVERGED at count 21 while the 10-18 watchdog report itself says it is Now green (0 fails, 15 succ, restarted 2026-10-18).

## Q3 — The ONE root cause that would stop the most recurrences

The fixloop counter/emitter itself: it keys on free-text regex over event streams that include its own output, and never consults ground truth (live job state, canon status, build ledger, workato-health sweep-mute list). No single RECIPE root cause comes close — the recipe with the most real recurrences (82862205) is already fixed and green, and every other real failure class in the cluster has a shipped fix. Fixing the mechanism kills all 12 current false/stale escalations at once, stops the self-inflation loop permanently, and prevents the needs-josh flood (70 to 84 rows in one hour on 10-18, per cortex pulse) from recurring.

Concrete minimal changes (for Josh decision, in priority order):

1. Exclude the mechanism own exhaust from its sources: skip rows whose workstream matches fixloop-escalation-*, escalation-*, *-incident, *-recurrence, cortex-pulse, jira-triage*, dropped-*, harness-dreamer — or stronger: only count rows that cite a live job ID (the watchdog already enforces job-ID evidence for stall verdicts; same standard).
2. Dedup escalations by KEY, not workstream slug — one open fix-or-risk-accept card per recipe-id:class across all of mission-control.
3. Before filing, check canon + live state: skip keys whose canon rows are all closed, whose recipe is currently green on live job_list evidence, or that appear on workato-health sweep-mute list (the 10-18 dreamer proposal 2026-10-18-fixloop-escalation-batching already covers batching + the upstream mute gap).
4. Key on canon root-cause SIGNATURES, not (id, class-word) — or at minimum stop asserting same root cause when the key carries no root-cause information.
5. Close the close-gate backlog feeding this: propagate the four known resolutions into canon (82272892 duplicate open row, 82862205 x3 open rows post-v44, 82090477 gym rows unrelated to quota-burn, and add the missing 71124238 row) so any future state-aware gate reads the truth.

Note for the record: the fixloop gate DID succeed at its original job — the 10-18 watchdog report shows zero fourth autopsies and the gated section correctly suppressed re-diagnosis of 82862205/82964017. The defect is purely in the escalation-accounting layer above it, which now manufactures Josh-decision debt faster than real incidents do.

---

## Prod row — BSYS-29905: FUNC | Send Genie Event 82120574 (verdict card, 2026-10-22)

**Verdict: NO-LIVE-BUG / RISK-ACCEPT.** The 2026-10-19T17:51Z health-sweep "new failures" flag on prod [recipe 82120574](https://app.workato.com/recipes/82120574) was a broken TEST CASE, not a production failure. The recipe never executed a step in the flagged job; zero production failures exist, lifetime or current. No hotfix, no prod write. Governing ticket: BSYS-29905.

**Origin walk (workato-autopsy method, job j-Ac3hPtgG-np4Emc-CD):**
- Reported surface: job "failed" at 2026-10-19T17:31:14Z (10:31:14 PT) — 20 minutes BEFORE the 17:51Z sweep flag, duration 136ms.
- `is_test_case_job: true`; `lines: []` — ZERO recipe steps executed. The job never entered the recipe.
- Error: "Test case contains an error: Step can't be executed, it requires sample data. Please fix it in the test case editor" — error_type "Test Automation error", adapter "Workato Automation", `calling_recipe_id: null`.
- ORIGIN step: there is none inside the recipe. The origin is Workato's Test Automation pre-flight validating stub test case `citc-Abcb8Fgp-T9mEN6-CD` ("Untitled test case 1", created 2026-09-16T17:07:53Z, never renamed, empty description) which has NO sample data captured for its step. The framework refused to execute before step 1. No READ-ONLY guard, no RUN-SKILL guard, no caller recipe, no upstream system was reached.

**Classification:** test-fixture defect (harness-side). Explicitly ruled out: upstream outage (no upstream call occurred), guard rejection (neither the READ-ONLY nor RUN-SKILL guard fired — no step executed), caller misuse (no caller; `calling_recipe_id: null`), genuine code defect (recipe code never ran and production is green).

**Still active? NO — the production class has zero occurrences ever.** Live counts 2026-10-22 (wt jobs list, prod): 64,115 jobs lifetime = 64,108 succeeded / 1 failed (the test artifact above). Recent prod calls all green through 2026-10-22T20:34 PT (j-Ac6XFhQb-PJeRPs-CD succeeded; steady "new call for function" traffic). Residual: the empty stub test case still exists and would fail again if someone re-runs it — cosmetic, zero pipeline impact. Optional dev-scope hygiene: rename/fix or delete `citc-Abcb8Fgp-T9mEN6-CD` and capture sample data for the notify/invoke_skill paths; not urgent, no prod gate.

**Why the sweep flagged it:** the health sweep counted a terminal "failed" state without walking to origin — the same class-vs-root-cause conflation the Q2 section above documents for the fixloop counter. A test-case pre-flight rejection is not a recipe failure class.

*Autopsy 2026-10-22, read-only on prod (wt --profile josh-prod). Evidence: wt jobs list/get, wt testcases cases. Ticket BSYS-29905.*

---
Method note: all evidence gathered read-only (registry/events/canon/ledger reads, incident-convergence.py --report replay, per-key row replay via the script own extract_key). One file written: this report. No recipes, prod assets, Slack, or canon touched.
