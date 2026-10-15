# Closure-gap inventory — the harness's detect-well-persist-poorly pattern

- **Dispatch:** cortex fleet pulse, class `sweep`, read-only, 2026-10-09
- **Sources read:** `knowledge/triage/queue.jsonl`, `knowledge/regression-canon/canon.jsonl`,
  `knowledge/garden-reports/fleet-validation.jsonl`, `knowledge/garden-reports/triage-outcomes.jsonl`,
  `knowledge/garden-reports/regression-2026-10-08.md`, `knowledge/garden-reports/regression-registry.json`,
  `knowledge/claims/claims.jsonl`, `knowledge/cortex/investigations/*.md` (5 files),
  `knowledge/dreams/bus/*.jsonl` (all outboxes, recent lines)
- **Question:** where did a detection signal exist but never propagate to the state that should have closed it?
- **Verdict: the pattern is real, systemic, and has at least 10 distinct instances across 5 failure shapes.**
  The harness's detectors fire reliably; the write-backs to closure state (canon flips, claim `last_verified`
  lifts, sweep suppressions, ledger closure rows) have no owner, no mechanism, or a broken mechanism. This
  inventory is the fourth independent witness of the pattern (dreamer deep-pass 23:59Z, gardener full-pass
  14:55Z, cortex corroboration 01:25Z, this sweep).
- **RESCUE NOTE:** the Write of this file to `knowledge/cortex/investigations/closure-gap-inventory.md` was
  DENIED by the permission gate (sensitive-file path) — the same gate that stranded the 78677477 findings in
  dispatch logs on 2026-10-08. Full document printed to stdout for parent-session rescue.

## The gap table

| # | Signal (detection) | Detected at | Should have closed where | Actual state (live read 2026-10-09) | Gap shape |
|---|---|---|---|---|---|
| 1 | clm-001 re-verify investigation verdict CONFIRMED; cortex bus post explicitly says "gardener can lift last_verified 10-06 -> 10-08 citing the investigation file" | 2026-10-08T23:16Z (bus) / investigation earlier same day | `claims/claims.jsonl` clm-001 `last_verified` lifted 2026-10-06 → 2026-10-08 | Still `"last_verified": "2026-10-06"` in claims.jsonl | **A — no write-back actor.** The recommendation is on the bus; nobody owns mutating claims.jsonl from it. Gardener flagged the same channel as unwired ("verifications.jsonl does not exist") at 14:55Z |
| 2 | Dreamer workshop re-verify queue flagging clm-001 hourly | 2026-10-07T13:27Z through 2026-10-08T23:31Z (11+ fires) | Queue item dropped once the re-verify landed (23:16Z) | The 23:31:42Z workshop line — 15 minutes AFTER the resolution — still reads "clm-001 last verified 2026-10-06" | **C — closed-state-blind detector.** The queue regenerates from the static claim field, so gap #1 multiplies one unapplied write-back into a dozen duplicate detections. One mutation clears both gaps |
| 3 | Regression failures 82273581 (0/1) + 82794233 (3/4) auto-seeded into canon, then triage-ACCEPTED at 15:15:52Z with explicit verdicts (delete the artifact / re-author to stable facts) | canon seed 2026-10-08T00:56Z; triage accept 15:15:52Z | `regression-canon/canon.jsonl` entries `regression-fail-untitled-test-case-1` and `regression-fail-resolver-v2-unique-caller-owned-mcp-child` flipped `open` → closed/decided with a verdict pointer | Both entries still `"status": "open"`; canon.jsonl untouched since the auto-seed (mtime 00:56Z) | **A — no write-back actor.** triage-decide.py writes queue.jsonl + triage-outcomes.jsonl but has no canon write-back; the only canon writer is the nightly auto-seeder, which appends and never flips |
| 4 | Triage verdict for 82273581: "Delete the artifact, no recipe edit" (test case citc-AbaAmBxM-aWc4HC-CD) | 2026-10-08T15:15:52Z | The test case actually deleted; disposition recorded | No execution record anywhere — no bus row, no outcome note beyond the verdict prose. (orca-main separately archived the whole orphan recipe at 05:10Z, but that was an independent discovery, not this verdict executing) | **D — verdict without executor.** Accepted non-build actions (delete/re-author test cases) are recorded as prose and dispatched to nothing |
| 5 | orca-main handoff: "Watchdog/regression sweeps can ignore this signature on 82273581 going forward" (stale orphan executor archived to zArchive) | 2026-10-08T05:10Z | Sweep configs / regression registry suppress the signature; canon entry superseded | Nightly regression and canon still carry the signature as an open failure; no suppression mechanism exists | **C — closed-state-blind detector.** Instructions to future sweeps are posted to the bus; no sweep reads its own disposition state before flagging |
| 6 | workato-health re-flagging prod 82090477 as new-failures 3× in one day (08:17Z / 13:20Z / 15:25Z, fail-count 55→57→58), all the same mock-probe 403 cluster | 2026-10-08, three fires | Dedup at detection time + the `mcp_mock` title filter so probe jobs stop counting | Three separate triage rows existed for one finding (dedup happened only at triage-decision: rejected×2 superseded, built×1, filed×1); the filter item `health-sweep-mock-probe-filter` filed by cortex at 23:16Z is still `open` | **C + A.** The sweep has no memory of its own open triage items — each fire re-enters the queue as a fresh row — and the root-cause filter has no owner yet |
| 7 | Fleet-validation stubs: 6 jobs returned stub rc, "watchdog escalates to bus + brief" | 2026-10-08T14:57–15:05Z | fleet-validation.jsonl gains clean re-run rows after run-job.sh v2 root-cause fix (launchd PATH + `~/.zshenv` gateway env repair, same day) | ZERO rows after 15:05Z — nothing between the last stub and now | **B — detection-only ledger.** fleet-validation.jsonl records failures and never recovery. Closure of an escalated incident is unobservable: "fixed and not logged" and "silently recovered" are indistinguishable. The stub-night root cause is documented in dream-loop.md but the ledger cannot show the incident closed |
| 8 | Headless dispatch findings stranded by the sensitive-path write gate (78677477 dev-fix verification completed but Write refused) | Dispatch ~2026-10-08T20:19Z; rescued by parent session 2026-10-09T01:24Z | Findings file lands in `knowledge/cortex/investigations/` at moment of discovery | Stranded ~5h in `~/.local/state/cortex/dispatch-*.log`; worse, the cortex bus post at 00:20Z cited the investigations file as a ref BEFORE it existed on disk | **E — infra gate strands output.** The gate denies with no fallback path, and the dispatch runner has no post-run artifact check, so downstream consumers cited a file that wasn't there yet |
| 9 | Dreamer deep-pass verdict: "82090477 prod new-failures unworked since 08:17Z" | 2026-10-08T23:59Z | Nothing to close — this is the inverse: the detector should have read the closure state that ALREADY existed (triage built 15:32Z: autopsy + BSYS-29418) | False "unworked" claim published to the bus; consumed a cortex dispatch (the 22:45Z autopsy investigation) to resolve the contradiction | **C — closed-state-blind detector, inverted.** Detectors flag without consulting triage-outcomes/Jira, so already-worked items re-enter attention. Cortex's autopsy file calls this out: dreamer "read the unchanged prod fail-count signal and missed the autopsy/ticket record" |
| 10 | Cortex finding: first regression live run's 2 FAILs had no canon entries ("FAIL rows are not flowing into the canon") | 2026-10-07T22:30Z | Canon auto-seed covers regression FAIL rows | CLOSED — both entries seeded by the 2026-10-08 00:56Z nightly run | **Contrast case: the one that closed.** It closed via the next scheduled run doing the right thing, not via anyone acting on the finding. That is why it worked: the seeder's appender design couldn't drift. Every gap above involves a state change the writer was never built to perform |

## The five failure shapes

- **A — No write-back actor.** A detection produces a recommendation or verdict that names the exact
  mutation needed (lift a `last_verified`, flip a canon status), and that mutation simply has no owner.
  Evidence lands on the bus; the target ledger waits for an agent that never comes.
- **B — Detection-only ledgers.** fleet-validation.jsonl (and the pattern it embodies) records failures
  and escalations but has no success/closure row type, so incident recovery is invisible. You cannot prove
  an incident closed from a ledger that only writes when things break.
- **C — Closed-state-blind detectors.** Sweeps, dreamers, and re-verify queues regenerate their findings
  from raw signal (fail counts, static claim fields, unfiltered job titles) without consulting the closure
  ledgers (triage-outcomes, canon status, Jira tickets) that already adjudicated them. Produces both
  duplicate flags (#2, #6) and false "unworked" verdicts (#5, #9).
- **D — Verdicts without executors.** Triage decisions on non-build actions (delete a test case, re-author
  an assertion) are recorded as prose and dispatched to nothing. A "built" verdict has a natural executor
  (a dev session); a "delete" verdict has none.
- **E — Gates that strand output.** The sensitive-path write gate refuses headless dispatch writes with no
  fallback, leaving completed findings stranded in dispatch logs, sometimes cited by the bus before they
  exist on disk.

## Cross-cutting observations

1. **Detection-to-closure is a one-way valve.** Signals flow into the bus freely (13 outboxes,
   corroboration tallies working as designed — the detect-well-persist-poorly thread already has 2
   witnesses). Nothing flows back out to the ledgers the signals were about. The bus is an excellent
   sensory system attached to no motor system.
2. **The only ledger that self-closes is the one with an appender-only writer.** Canon's auto-seeder
   worked (#10) precisely because it does one thing on a schedule. Every closure that requires *flipping*
   state (canon open→closed, last_verified lift, queue item retirement, suppression list update) has no
   writer.
3. **The dreamer's filed proposal already names the treatment.**
   `knowledge/dreams/proposals/2026-10-08-failure-flywheel-writeback.md` ("mandatory write-back at moment
   of discovery", filed incubating off the 23:59Z deep-pass). This inventory is the concrete instance list
   that proposal lacked — 10 instances across 5 shapes, every one with file-and-timestamp evidence.
4. **Highest-leverage fixes, in order:** (a) give triage-decide.py a canon write-back (closes #3, #4
   mechanically); (b) wire the gardener's claim-verification run so bus-verified claims actually lift
   `last_verified` (closes #1, which collapses #2's duplicate stream); (c) add a closure/pass row type to
   fleet-validation.jsonl (closes #7); (d) make workato-health read its own open triage items before
   flagging + ship the mcp_mock filter (closes #6); (e) give the write-gate denial a rescue path and the
   dispatch runner a post-run artifact check (closes #8).
5. **One small verification from this sweep:** the dreamer's 23:59Z pipeline defect "glm-5.3-flash lens
   route hard-400s" appears stale — this investigation ran on `fireworks/glm-5.3-flash` end-to-end without
   a 400 — but no closure record exists anywhere, so the defect row persists on the bus with a `ttl_days`
   clock still running. Same class, minor instance.

## Not verified

- Live Workato-side state was not re-read this dispatch (read-only sweep over knowledge files only):
  whether the 82273581 test case `citc-AbaAmBxM-aWc4HC-CD` still exists on the recipe is inferred from the
  stale registry snapshot (00:56Z) and the absence of any disposition record, not a live Test Automation
  API call.
- `regression-registry.json` and `canon.jsonl` mtimes are the evidence for "untouched since" claims — a
  write that preserves mtime is theoretically possible but no such mechanism is known.
- Whether workato-health's 2026-10-09T00:28:55Z sweep (heartbeat.jsonl) produced a finding suppressed from
  the bus, or stayed quiet because the fail-count stopped moving, is indistinguishable from available
  evidence.
- The proposal file `2026-10-08-failure-flywheel-writeback.md` was cited from bus/dreamer references, not
  read directly.
