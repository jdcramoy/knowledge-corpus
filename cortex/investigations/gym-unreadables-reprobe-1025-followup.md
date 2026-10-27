# Replay-gym unreadables re-probe — followup for the remaining 3 (2026-10-26, read-only investigation)

**Verdict: 83326118 and 83326123 are TRANSIENT (readable now, full 200 JSON). 83326117 is PERSISTENT-unreadable — but the error class CHANGED: it now returns a clean HTTP 404 on both read surfaces (get + versions), where the 2026-10-25 gym finding was non-404. That 404 pattern (both surfaces, both profiles on 10-25) is consistent with the recipe having been DELETED or removed from token visibility, not a transient gateway failure.**

Method: `wt recipes get <id>` via wt CLI, dev profile josh-us, workspace 3535597 ("Workato AHQ | AI" — /api/users/me id 3535597, same token basis as the 2026-10-25 reprobe). Read-only; nothing mutated. 83326117 additionally probed once via `wt recipes versions 83326117` as a second read surface to classify the 404.

| Recipe | Name | Result | Running | Notes |
|---|---|---|---|---|
| 83326117 | (unknown — unreadable) | UNREADABLE — HTTP 404, body `{"message": "Not found"}` (get); HTTP 404, body `{"errors":[{"code":404,"title":"Not found"}]}` (versions) | unknown (unobtainable via 404) | PERSISTENT — but class changed from non-404 to clean 404; likely deleted/withdrawn since 2026-10-25, not a readability failure |
| 83326118 | TEST BSYS-29944 session-audit probe | READABLE (200, full JSON incl. code) | stopped (`running: false`, last ran 2026-10-24 17:50 PDT) | manifest-exempt TEST probe; 24 jobs, 0 failed |
| 83326123 | lookup_career_framework | READABLE (200, full JSON incl. code) | running (`running: true`, last run 2026-10-24 19:30 PDT) | career-framework lookup skill; 18 succeeded / 3 failed jobs |

## Canon coverage

All three covered by open canon rows in regression-canon/canon.jsonl (lines 115-117, found 2026-10-25, status open, test_case_id null):

- gym-recipe-unreadable-83326117
- gym-recipe-unreadable-83326118
- gym-recipe-unreadable-83326123

## Suggested disposition (for Josh / canon owner — NOT applied)

- 83326118, 83326123 — resolve-transient (no repro, full 200 evidence 2026-10-26), same basis as the five closed in the prior reprobe. failure-close-gate requires the canon row update in the same run that closes them; this read-only session deliberately did not touch canon.jsonl.
- 83326117 — do NOT close as transient. Recommend one manual check whether the recipe was intentionally deleted (e.g. a TEST-probe cleanup); if deleted, close the canon row as "asset withdrawn — no longer probeable" rather than resolved-transient. If it was NOT deliberately deleted, the 404 across both surfaces on both profiles is itself the finding and the row stays open.
