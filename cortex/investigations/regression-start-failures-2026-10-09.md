> Rescued verbatim by cortex pulse 2026-10-09T08:45Z from dispatch log (headless Write was gate-denied; see triage slug cortex-dispatch-add-dir-fix).
# Investigation: regression-nightly "could not start run" ×3 — 2026-10-09

**Date:** 2026-10-09 · **Mode:** READ-ONLY (no runs started, no recipe edits, dev workspace only, no prod access)
**Trigger:** `~/.claude/knowledge/garden-reports/regression-2026-10-09.md` — 1 passed, 0 failed, **3 errors: "could not start run"** (82273581, 82727069, 82794233); 82855731 passed (run `cirr-AbsEfNBe-kQYmWc-CD`).

## Verdict (one line)

Not an auth/session failure and not an API change: two recipes' test cases were **deleted on 2026-10-08 under Josh's own accepted triage verdicts** (nothing left to run → the run-request POST returns no `data.id`), the third (82727069) has a different, still-ambiguous cause, and a **runner registry-cache bug** keeps case-less recipes in the run set so the error will repeat nightly until fixed.

## Evidence

### 1. Recipes all still exist in dev (ws 3535597) — `recipe_get` 2026-10-09

| Recipe | Name | Exists | State |
|---|---|---|---|
| 82273581 (https://app.workato.com/recipes/82273581) | execute_google_workspace_operation | yes | **stopped** |
| 82727069 (https://app.workato.com/recipes/82727069) | run_genie_evals (workato_skill trigger) | yes | **stopped**, **zero jobs ever** (`job_list` total 0) |
| 82794233 (https://app.workato.com/recipes/82794233) | FUNC \| Resolve Active HR Genie MCP Runtime Child V2 | yes | **running** |
| 82855731 (https://app.workato.com/recipes/82855731) | audit_conversation_case_file (control) | yes | running |

Deleted-recipe hypothesis: **ruled out** — all four resolve.

### 2. Test cases today — `wt testcases cases` (read-only GET /api/recipes/:id/test_cases)

| Recipe | Cases now | Detail |
|---|---|---|
| 82273581 | **0** | canon's `citc-AbaAmBxM-aWc4HC-CD` is gone |
| 82794233 | **0** | all 4 cases gone, incl. canon's `citc-Abo3G9Ew-sTkNQt-CD` |
| 82727069 | 1 | `citc-AbsBKJxC-JYEz48-CD` "Untitled test case 1", created 2026-10-08 18:17 PDT (3.5 h before the nightly) |
| 82855731 | 1 | `citc-AbpxcLar-hohBHJ-CD` (created 10-06) — passes |

### 3. API session is healthy — expired-session hypothesis ruled out

- All four `cases` calls returned HTTP 200.
- `wt testcases status` on three historical run requests returned 200 with full payloads: `cirr-AbsEfNBe-kQYmWc-CD` (10-09, completed, 100% coverage), `cirr-Abrfkxwo-oHGY9X-CD` and `cirr-AbrfmCM3-tNfNaJ-CD` (10-08, completed).
- The failing nightly itself **did** start a run for 82855731 minutes after the three failures. An expired Test Automation API token would fail all four uniformly.

### 4. API change hypothesis — no supporting evidence

Same endpoints behaved identically 10-07 → 10-08 → 10-09 for the control recipe; the public surface is only the 3 documented endpoints (`POST /api/test_cases/run_requests`, `GET .../run_requests/:id`, `GET /api/recipes/:id/test_cases` — per https://docs.workato.com/en/workato-api/test-automation.md). Probes for undocumented detail/list endpoints 404'd (`/api/test_cases/:id`, `/api/test_cases/run_requests?recipe_id=`) — same as ever, not a regression.

### 5. Root cause per recipe

**82273581 — deleted test case (orphaned canon entry).**
`garden-reports/triage-outcomes.jsonl`, 2026-10-08, by josh (triage-decide), action=accepted:
> "Dev recipe 82273581: unconfigured 'Untitled test case 1' fails every run… VERDICT: delete. Case was created 2026-09-12 and never configured — no fixture, no assertion, covers no failure class… Delete the artifact, no recipe edit."
The deletion was executed; the recipe now has zero test cases, so `POST /api/test_cases/run_requests {recipe_id}` has nothing to run and returns no `data.id` → runner reports "could not start run". Canon entry `regression-fail-untitled-test-case-1` (found 10-08, status open) now points at a deleted case — **stale, should be closed**.

**82794233 — deleted test cases (orphaned canon entry), re-author half-landed.**
Same triage file, 2026-10-08, accepted:
> "Resolver V2 test asserts whole MCP tool catalog, breaks on every catalog change… VERDICT: approve re-author to stable facts (count>0 + named tool present, not catalog equality). 1 point, dev-scoped test-case edit only."
All 4 old cases (which ran and 3/4-passed on 10-07 and 10-08) are gone; **no replacement cases exist yet**. Zero cases → same start failure. Canon entry `regression-fail-resolver-v2-unique-caller-owned-mcp-child` is likewise stale-open against a deleted case. Open follow-up: the approved re-authoring (stable-facts assertions) has not landed.

**82727069 — cause genuinely different; NOT orphaned cases (1 case exists).** Correlational evidence only, because disambiguating would require a POST (prohibited by the read-only scope):
- Only failing recipe whose case exists → case-deletion does not explain it.
- Only registry recipe with a `workato_skill` trigger (the 3 others are `workato_recipe_function`) and the only one with **zero jobs of any kind, ever**.
- It is stopped, but so is 82273581 — while 82794233 failed despite running — so "stopped" alone is not a proven discriminator; the cleanest correlates of the one success (82855731) are: running + recipe_function trigger + configured case.
- Live hypotheses, unranked: (a) Test Automation run requests reject skill-triggered recipes; (b) run requests require the recipe started; (c) the case is an empty shell (untitled, no description, created 18:17 PDT 10-08) and fails validation. Docs page states no constraints. **Next diagnostic (needs Josh's go-ahead since it writes): `wt testcases run --recipe 82727069 --ids citc-AbsBKJxC-JYEz48-CD` and read the error body.**

### 6. Contributing harness defects (the error will recur nightly)

1. **Registry cache never re-verifies cases** — `regression-nightly.py` `scan_for_test_cases()`: `if cached: found[rid] = …; continue` skips the cases call for any registered recipe, so a recipe whose cases were deleted stays in the run set forever and errors every night. Fix: refresh the case count for cached entries (or treat 0-case as prune).
2. **The report discards the actual error** — `run_recipe_cases()` captures `detail: str(r)[:150]` but `main()` only prints `res['error']`; the API's rejection body is lost, which is why this investigation could not quote it. Fix: include `detail` in the report line.
3. **Canon hygiene gap** — canon auto-seeds failures but nothing closes an entry when its test case is deliberately deleted via triage. The two 10-08 entries are open pointers to deleted `citc-` IDs.

## Correlation with canon.jsonl (as requested)

| Canon signature | Recipe | Found | Canon status | Reality 10-09 |
|---|---|---|---|---|
| regression-fail-untitled-test-case-1 | 82273581 | 10-08 | open | test case `citc-AbaAmBxM-aWc4HC-CD` **deleted per accepted triage verdict** — close canon entry |
| regression-fail-resolver-v2-unique-caller-owned-mcp-child | 82794233 | 10-08 | open | all 4 cases deleted for the accepted re-author; replacements not yet created — close/mark superseded |

The 10-09 "errors" are the mechanical echo of executing Josh's own 10-08 triage verdicts, amplified by the registry-cache bug — **not a new platform failure, not expired credentials, not deleted recipes.**

## What was NOT verified

- The exact rejection body of the 10-09 POSTs (runner discarded `detail`; replaying requires a write).
- 82727069's root cause among the three live hypotheses (needs one write-capable run request or UI Test click to disambiguate).
- Who/when exactly deleted the 82273581/82794233 cases (no audit API probed; triage-outcomes timestamps are the evidence of intent, not of the delete act itself).
- No prod workspace was touched; no runs were started; no recipes edited.
```

**Note:** the Write to `~/.claude/knowledge/cortex/investigations/regression-start-failures-2026-10-09.md` was blocked by the sensitive-file gate — if you approve that path, say the word and I'll persist it verbatim. Nothing else was changed: no runs started, no recipe edits, dev-only reads, zero prod calls.
