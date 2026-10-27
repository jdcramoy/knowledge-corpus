
## gym-recipe-unreadable 2026-10-22 batch — re-probe 2026-10-22 (two-tool, read-only)

Two read paths per recipe: (1) `wt recipes get <id>` (dev profile, jq-extracted
running state), (2) AIRO MCP `recipe_get` (workato-airo-mcp-server). All wt reads
rc=0; all AIRO reads returned the full recipe. The 20:44Z single-probe clean read
of 82971161 is now superseded by the full six.

| recipe_id | name | wt (dev) | AIRO recipe_get | verdict |
|---|---|---|---|---|
| 82862838 | MON \| HR Genie \| Telemetry Coverage Auditor | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — canon entry closed |
| 82971161 | EM \| Capture Ticket Reaction | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — closed |
| 82997363 | EM \| Capture Triage Request | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — closed |
| 83262538 | search_drive (Company Brain demo) | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — closed |
| 83262540 | search_gmail (Company Brain demo) | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — closed |
| 83262541 | search_slack (Company Brain demo) | rc=0 running=true | full recipe, Running: True | TRANSPORT-CLASS — closed |

### Verdict

- 0 of 6 canon rows confirm "unreadable on dev AND prod (non-404)". All 6 recipes
  read clean on BOTH tools, all running. The gym's 2026-10-22 run hit the known
  wt socket-level rc=1 transport class (canary-alarm-loop.md) and canonized it as
  an asset unreadability regression — same false-alarm class as the 10-09 batch.
- All 6 rows CLOSED in canon.jsonl the same run (append-only closing rows with
  close_evidence; no rewrites, per the canon README convention).
- The two-read-path minimum bar is now ENFORCED in the probe path itself:
  replay-gym.py gained `direct_recipe_get` (raw HTTPS to /api/recipes/<id> with
  the profile's keychain token — independent of wt's transport). A wt non-404
  failure is only canonized if the direct read also fails (None); a clean answer
  (200 or 404) records "transport blip, not canonized" instead. Verified live:
  good ID -> 200 (dev) / clean 404 (wrong-workspace prod), bogus ID 999999999 ->
  404 (int, not None) — recorded as info "deleted", never canonized. Full gym
  run post-patch: 43 recipes probed, 0 unreadable, 0 canon additions.

Probe commands: `wt recipes get <id>`, `mcp__workato-airo-mcp-server__recipe_get`,
`python3 ~/.claude/knowledge/scripts/replay-gym.py` (post-patch live run). Nothing
on the platform was modified.
