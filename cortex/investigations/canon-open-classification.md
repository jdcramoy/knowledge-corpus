# Canon open-entry classification — read-only sweep
Swept: 2026-10-09 (cortex, read-only). Source: `~/.claude/knowledge/regression-canon/canon.jsonl` (42 lines, 2 closed, 40 open).
NOTE: task brief said 39 open; actual count is 40. All 40 classified below — no entry skipped.

Cross-checks used: `build-ledger.jsonl` (4,768 rows), `garden-reports/gym-2026-10-09.md`, `garden-reports/regression-2026-10-09.md`, plus two live read-only probes (`wt recipes get <id> --raw` on dev and `wt-prod` on prod profiles for the 10 flagged recipes). Nothing was modified except this file.

## Counts per bucket

| Bucket | Definition | Count | Canon line indexes (0-based) |
|---|---|---|---|
| (a) | recipe deleted / 404 pollution | 10 | 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 |
| (b) | duplicate signature of another entry | 21 | 1, 3, 5, 16-22, 31-40, 41 |
| (c) | fix landed but status never closed | 9 | 0, 23, 24, 25, 26, 27, 28, 29, 30 |
| (d) | genuinely open | 0 | — |
| | **Total** | **40** | |

Headline: the canon's 40 "open" entries contain ZERO genuinely open regressions. 31 of 40 are pure hygiene debt (dupes + 404 pollution), 9 are real findings whose resolution never got written back.

## Bucket (a) — 404 pollution (10)

Live probe evidence (2026-10-09, this sweep):
- 82919741, 82920816, 82928684 — 404 on dev AND prod. Genuinely deleted; gym-2026-10-09.md confirms: "recipe 82919741 deleted since yesterday (404 both profiles)" (likewise 82920816, 82928684). Pure deletion pollution.
- 71768712, 74736304, 82090477, 82872520, 82873160, 82912295, 82929351 — 404 on dev profile, but READABLE-ON-PROD just now. These are prod-workspace recipes; the gym probed them with the dev profile (`wt` instead of `wt-prod`) and recorded the wrong-profile 404 as a harness regression. 82090477 is the known prod twin of dev 78677477 (BSYS-29396 envelope work). Wrong-profile 404 pollution, not a real failure.
- Recommendation (not applied — read-only): gym should route per-workspace (recipe-id → profile map or try wt-prod on 404) before seeding a `gym-recipe-unreadable` entry; the "dev AND prod" wording on the second batch (idx 31-40) was never actually verified and is false for 7 of 10.

## Bucket (c) — fix landed, status never closed (9), with evidence lines

| Canon idx | Signature | Recipe | Evidence the fix/finding landed (exact source) |
|---|---|---|---|
| 0 | `ruby-eval-empty-payload` | 82272892 | build-ledger.jsonl:4407 — 2026-10-09T09:49:54Z, kind "fix", ticket BSYS-29456: "records_json pill remapped (nonexistent 'records' key -> 'records_json') + empty-input guard in step 21; pushed, wire-verified, force-run j-AbsJxNLD-rzEErH-CD succeeded with previously-dead upsert path executing" |
| 23 | `gym-replay-miss-wt-recipes-list-raw-2-dev-null-python3` | — | gym-2026-10-09.md: "ledger rows in window: 2570; recipes checked: 38 — misses: 0" — the same-day gym replay ran clean; rc=2 usage errors were the stale wt binary in the gym's launchd PATH (usage string lacks the wt-v2 `testcases` subcommand), the same PATH root cause repaired in run-job.sh v2 (2026-10-08) |
| 24 | `gym-replay-miss-wt-recipes-list-raw-2-1-head-5-echo-no` | — | same evidence as idx 23 (same gym run, misses: 0) |
| 25 | `gym-replay-miss-wt-jobs-list-82090477-status-failed-ra` | — | same evidence as idx 23 |
| 26 | `gym-replay-miss-wt-recipes-get-82090477-raw-profile-jo` | — | same evidence as idx 23; additionally build-ledger.jsonl:4252 (2026-10-09T09:04) shows `wt recipes get 82090477 --raw` succeeding on prod |
| 27 | `gym-replay-miss-wt-jobs-list-82090477-status-succeeded` | — | same evidence as idx 23 |
| 28 | `gym-replay-miss-wt-testcases-cases-82794233-2-1-head-6` | — | same evidence as idx 23; regression-2026-10-09.md proves `wt testcases` works that day (run cirr-AbsJKthc-9kXhKP-CD produced results) |
| 29 | `gym-replay-miss-wt-testcases-cases-recipe-82273581-raw` | — | same evidence as idx 23/28 |
| 30 | `gym-canary-fail-command-loop-canary-failed-at-2026-10-` | — | the 10:20:28 canary failure was a controlled chaos-drill artifact, not a regression: build-ledger.jsonl:4476 (10:28) creates drill antigen drill-2026-10-09-01 noted "chaos drill: controlled canary failure"; build-ledger.jsonl:4574 (10:45) records "Replay gym + fire drill + command canary (built 2026-10-09, all LIVE)"; gym-2026-10-09.md firedrill-ok line confirms green after flip-back |

## Bucket (b) — duplicates (21)

- idx 1 → duplicate of CLOSED idx 2 (same signature `regression-fail-untitled-test-case-1`, recipe 82273581; the closed twin already records "case deliberately deleted; entry closed 2026-10-09"; regression-2026-10-09.md's remaining "could not start run" is the stale-registry-cache symptom the closed entry explains).
- idx 3 → duplicate of CLOSED idx 4 (same for resolver-v2, recipe 82794233).
- idx 5 → canonization of job j-AbrfmCLn-cFCLFM-CD, the exact job cited in idx 3/4 — third entry for the same resolver-v2 failure, already covered by the closed twin.
- idx 16-22 → free-text copies of idx 23-29 (same 7 commands, one pair each); idx 23-29 kept as canonical because they carry the rc=2 usage detail.
- idx 31-40 → second batch of the 10 `gym-recipe-unreadable` signatures, verbatim dupes of idx 6-15 with the unverified "dev AND prod" claim added.
- idx 41 → verbatim dupe of idx 30 (same canary signature, same 10:20:28 timestamp).

## Nothing unverified

Every bucket assignment above cites a ledger line, garden-report line, or a live read-only probe run during this sweep (both profiles, all 10 flagged recipe IDs). No recipe, canon entry, ledger row, or report was modified; the only write was this file. Recommended (out of scope here, needs a write): close the 9 (c) entries with their evidence lines, delete/merge the 21 (b) dupes, and fix the replay-gym profile routing so (a)-class pollution stops regenerating.
