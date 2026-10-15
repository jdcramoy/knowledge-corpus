# BSYS-29700 / prod recipe 71124238 — provenance investigation (2026-10-15, ~11:45Z)

**Verdict: POSSIBLE UNFINISHED PROD STATE — CONFIRMED.** Prod recipe 71124238 "Create Customer
Request" is STOPPED on the OLD code (v11). The fix never landed. The owning session died
mid-push at 10:28:21.901Z, ~5 seconds after the stop succeeded, while issuing the combined
transform+PUT+start command. No tool result for that command exists; prod `updated_at` is
still 2026-10-07, proving the PUT never persisted.

## Sources
- Owning session transcript: `~/.claude/projects/-Users-<user>-orca-projects-bt-genie/41c00d3d-9bfd-49dc-b408-927f759554e2.jsonl` (08:52:27Z → 10:28:21.901Z, 1523 lines — ends mid-command)
- Build ledger: `~/.claude/knowledge/build-ledger.jsonl` lines ~16850–17096 (08:57–10:32Z)
- Red-team verdict: `~/.claude/knowledge/redteam/BSYS-29700-create-customer-request-hotfix.md` (PASS-WITH-NOTES)
- Jira BSYS-29700 (read-only via Atlassian MCP, cloud 99bd32a1): status Backlog; exactly 2 comments (red-team FAIL 09:53:51Z, red-team PASS-WITH-NOTES 09:57:43Z); NO push-outcome comment
- Live read-only GET of /api/recipes/71124238.json on the prod profile at ~11:40Z
- Cortex bus findings 10:30:56Z + 11:33:04Z; cortex question 10:32Z; NO mission-control row exists for this work

## (1) What fix was in flight
Hotfix for BSYS-29700: "Create Customer Request" (prod 71124238), the Genie skill behind BT
Genie GO (Genie 8789), with a **44% JSD call failure rate** (3,708 succeeded / 1,806 failed).
Root cause: Genie-supplied JSON fragments (`form`, `requestFieldValues`) interpolated raw into
an adhoc JSD create-POST body → 400 "error parsing JSON" when user text carries unescaped
quotes; 422 "Field is required" when the Genie omits required Proforma questions. Fix (built +
verified on dev twin 70911663 v42, running): wrap steps 2–9 in a **Monitor try/catch**; catch
step 12 `workflow_return_result` returns blank issue ids + a static guidance `error` string;
optional `error` property added to the trigger result schema and step 13 input schema. The job
then SUCCEEDS and hands the Genie recoverable guidance instead of hard-failing. Red-team FAIL
(09:53:51Z — empty catch return F1, no pre/post-creation discrimination F2, schema drift F4)
was remediated and re-verdicted **PASS-WITH-NOTES** (09:57:43Z) with a conditioned post-push
replay proof (repeat 2–3 failed jobs whose failure line = create-POST, 422/400 class only).
Root-cause body rebuild (F3) deferred to a separate ticket by agreement.

## (2) Did it complete before the session ended? — NO
Timeline (all UTC):
- 09:52:16Z — session reports "everything staged", holding only for the red-team verdict. Prod payload staged from a fresh fetch; manifests 364230 (8 rows) + 364232 created and verified; knowledge deposited in domains/workato-platform.md.
- 09:57:43Z — PASS-WITH-NOTES lands on the ticket.
- 09:57:58Z — session fires the combined block: stop → fresh GET → `/tmp/hotfix_transform.py` → `/tmp/fix_catch.py` → PUT.
- 10:27:59Z — that command **hung the full 1800s** (interactive prod-write confirmation prompt; `| tail -2` held stdin) and was auto-backgrounded (task beeqdla9g). `/tmp/prod_push.log` is 0 bytes — nothing in the block had run.
- 10:28:13Z — session kills the hung task, diagnoses the confirmation prompt.
- 10:28:16–17Z — re-issues the stop with a piped `y` → `{"success": true}`. Prod stopped (API `stopped_at` 2026-10-15T03:28:16.931-07:00 = 10:28:16.931Z).
- 10:28:21.901Z — session issues the final one-liner: fresh GET → transform → fix_catch → `PUT /api/recipes/71124238.json` → start. **The transcript ends here. No tool result. The session died.**

Live GET ~11:40Z: `running: false`, `version_no: 11`, `updated_at: 2026-10-07T23:55:31-07:00`,
`last_run_at: 2026-10-07`. The PUT **never landed** — prod is down on the pre-fix code.
Staging artifacts `/tmp/prod_fresh2.json`, `/tmp/prod_final.json`, `/tmp/prod_put_final.json`
do not exist (never created); only `/tmp/hotfix_transform.py` and `/tmp/fix_catch.py` survive
(both were validated against dev twin v42). Cortex confirmed running=False at 10:31Z and again
at 11:35Z.

## (3) Was a restart planned or intentionally deferred? — PLANNED, IMMEDIATE, NOT DEFERRED
Stated twice verbatim (09:52:16Z and 09:57:12Z): "stop 71124238 → PUT → start → verify running
flag → repeat failed jobs as live proof of the catch path → comment BSYS-29700 → closeout."
Josh's own opening instruction to the session: "hotfix it in production, with as little
downtime as possible." The restart was chained in the SAME shell command as the PUT. The
downtime was unintentional — a session crash ~5s after the stop succeeded.

## (4) Exact restart command the session intended
```
printf 'y\n' | wt recipes --profile josh-prod start 71124238
```
**DO NOT run this alone.** The PUT never persisted; a bare start resurrects the OLD v11 code
with the 44% failure mode (arguably worse than a clean stop: silent failures resume). The
correct completion of the session's plan, in order:
1. `wt api --profile josh-prod GET /api/recipes/71124238.json > /tmp/prod_fresh2.json`
2. `python3 /tmp/hotfix_transform.py /tmp/prod_fresh2.json prod /tmp/prod_new_code2.json`
3. Wrap in a `{"code": ...}` envelope, then `python3 /tmp/fix_catch.py /tmp/prod_env.json /tmp/prod_final.json`
4. `printf 'y\n' | wt api --profile josh-prod PUT /api/recipes/71124238.json --data "$(cat /tmp/prod_put_final.json)"`
5. `printf 'y\n' | wt recipes --profile josh-prod start 71124238` + verify the running flag
6. Conditioned replay proof per the red-team ruling: repeat 2–3 FAILED jobs whose error line =
   the create-POST step and whose class is 422/400 ONLY — never a succeeded or post-creation job
7. Comment BSYS-29700 with the outcome; mission-control closeout (no row exists today)

Alternative equally-valid path: rebuild the same catch structure from dev twin 70911663 v42
(which HAS the fix and is running in dev) — diff first; the dev twin carries an extra
`.gsub(/[[:cntrl:]]/, ' ')` hardening prod never got.

## Loose ends the dead session never reported
- Unexplained `context.workspace_id: 3535597` (the DEV workspace id) inside a PROD job trace —
  the session believed it was dev-scoped metadata written by the conversation-logging
  prerequisite skill, outside this hotfix's blast radius, and meant to flag it to Josh.
- BSYS-29700 sits in Backlog with no record that the push was attempted and is incomplete.
- Dev twin 70911663 carries the shipped-intent fix (v42) and is running in dev.
- First stop attempt hung 30 minutes on the prod-write confirmation prompt; any rerun should
  always pipe `y` (or use a non-interactive flag) on wt prod writes.

Investigator: cortex-dispatched provenance session, 2026-10-15 ~11:33–11:45Z. Read-only;
no wt/AIRO writes performed. Only artifact created: this file.
