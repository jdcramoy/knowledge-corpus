# Investigation: replay-gym "gym-recipe-unreadable" canon entries — live re-probe

- Investigator: cortex session (headless), 2026-10-22, probe window 20:44–20:47Z
- Scope: read-only. One `wt recipes get <id>` probe per recipe ID. Nothing else changed.
- Prior signal: canon.jsonl carries 6 entries found 2026-10-22, signature
  `gym-recipe-unreadable-*`, claiming recipes unreadable on dev AND prod (non-404):
  82862838, 82971161, 82997363, 83262538, 83262540, 83262541.

## Live probe evidence (dev workspace, wt CLI)

Reference probe (not run by this session): 82971161 at 20:44Z — read clean, running:true.

This session, 2026-10-22 ~20:46Z, one probe each, rc + jq parse check:

| recipe id | rc | valid recipe JSON | name (from response) | running |
|---|---|---|---|---|
| 82862838 | 0 | YES (jq parsed) | MON \| HR Genie \| Telemetry Coverage Auditor | true |
| 82997363 | 0 | YES (jq parsed) | EM \| Capture Triage Request | true |
| 83262538 | 0 | YES (jq parsed) | search_drive | true |
| 83262540 | 0 | YES (jq parsed) | search_gmail | true |
| 83262541 | 0 | YES (jq parsed) | search_slack | true |

Exact command per ID: `wt recipes get <id>` — stdout captured, stderr EMPTY on all five.
Sample stdout head (82862838), verbatim:
```
{
  "id": 82862838,
  "user_id": 3535597,
  "name": "MON | HR Genie | Telemetry Coverage Auditor",
  "created_at": "2026-10-06T20:43:57.279-07:00",
  "updated_at": "2026-10-21T09:57:57.129-07:00",
  "copy_count": 1,
  "trigger_application": "clock",
```
jq verdict line for each (parse proof): e.g. 82862838 →
`valid-recipe-json name=MON | HR Genie | Telemetry Coverage Auditor id=82862838 running=true`.
No error shapes to note — zero non-zero rc, zero stderr bytes, zero jq parse failures
across all 5 probes. Raw probe outputs retained at /tmp/gym-verify/<id>.out.

## Verdict

- **All 6 of 6 canon entries are CONTRADICTED by live evidence.** The 5 probed here
  read clean as valid recipe JSON with rc=0 and running:true; the 6th (82971161) was
  already read clean at 20:44Z the same evening. The "unreadable on dev AND prod
  (non-404)" claim is a transport-class false alarm for the entire batch — most
  plausibly a transient wt/gateway blip or rate-limit during the gym run at
  canonization time, not a recipe-side defect. None remain suspect.
- **Recommendation (one line):** yes — the replay-gym probe path should retry each
  "unreadable" read via a second tool (e.g. AIRO `recipe_get` MCP, or a single retry
  of `wt recipes get` after a short backoff) and only canonize if BOTH paths fail,
  because a single-tool transient read failure currently pollutes the canon with
  false harness-regression rows (this is the second such all-false batch after the
  2026-10-09 entries).
- Note: the 2026-10-09 sibling entries (71768712, 74736304, 82090477, 82872520,
  82873160, 82912295, 82919741, 82920816, 82928684, 82929351, …) were NOT re-probed
  here (out of scope) but share the same signature and same failure mechanism
  suspicion; they warrant the same two-tool retry policy before any is treated as real.
- Read-only confirmed: no canon row, recipe, or other asset was modified in this session.
