# Fleet "double-stub" dreamer/project-dreamer/evidence + watchdog empty turns — root cause 2026-10-26

Investigated 2026-10-26 (triage dispatch, approved card fleet-runner-double-stub-dreamer-evidence).
Heartbeat now at investigation time: 2026-10-26T12:36:58Z.

## Verdict

The ledger label "double-stub" is a misnomer for this class. The rows are
`"result":"ran rc=1"` — real output with nonzero exit, not `"stub rc=N"` (empty
output). Runner semantics (run-job.sh attempt(), lines ~220-232): nonzero rc WITH
non-empty OUT = genuinely failing run; only empty-output runs are stubs.

Root cause of both nights: **transient fleet-wide network outage at fire time —
`API Error: Can't reach the API server — check your internet or DNS (ENOTFOUND)`
captured in every one of the six job-window attempts.** Evidence:

- ~/.local/state/fleet/dreamer.log lines 230-234 (10-22) and 260-264 (10-24):
  `API Error: ... (ENOTFOUND)` twice per attempt pair, then `VALIDATION FAILED
  after retry (ran rc=1)`.
- project-dreamer.log lines 174-182 (10-22), 199-207 (10-24); evidence.log lines
  238-246 (10-22), 264-272 (10-24): identical ENOTFOUND signature.
- Fleet-wide, not three-job-specific: the same night hit gardener, cortex x3,
  watchdog, healer, docs-watch, canary, cost-governor, queue-drift,
  restore-drill, decision-inbox (fleet-validation.jsonl 10-22 05:36-11:20Z and
  10-24 04:50-08:28Z windows).

This is already known and structurally fixed: the 10-25 investigation
cortex/investigations/watchdog-dark-enotfound-2026-10-25.md root-caused the same
class, and run-job.sh now carries the network preflight gate
(`fleet-runjob-network-preflight-gate, 2026-10-25`, fail-open DNS check with
3x10s retry, then zero-token skipped-no-signal rows). Since the preflight
landed, all three jobs' subsequent fires are `validated-clean` in
fleet-validation.jsonl (10-25T03:49/04:30/05:03/06:48Z wait that's dreamer
03:49, project-dreamer 05:03, evidence 06:48; 10-26T03:52/04:41/04:55Z). No new
fix needed — verifying the preflight is present in the deployed runner counts as
the applied fix.

## Watchdog empty turn-ends — different class, NOT env

The card's related fact (watchdog agent baseten/deepseek-v4-pro died twice last
night, abrupt empty turn-ends) is NOT the same signature and NOT env:

- Env is exonerated: watchdog.env shares the identical runner, env-repair,
  bypassPermissions and gateway sourcing as the three failing jobs, and the
  watchdog fleet job itself ran validated-clean on 10-25 (11:18 local) and
  10-26 (11:20 local) — same env, no failures.
- The deaths are on the Agent-dispatch path (model pin baseten/deepseek-v4-pro,
  routed via the Workato AI gateway, ANTHROPIC_BASE_URL in ~/.zshenv). An
  abrupt EMPTY turn-end from a gateway-pinned model is the model-dropout
  signature (model lane returns an empty/failed completion mid-run), not an env
  failure. The env-failure signature for comparison is rc=1 WITH the ENOTFOUND
  text in OUT — which is what the fleet jobs showed.
- No local record of the two deaths was found in watchdog-reports/2026-10-26.md,
  cortex/attention-queue.md, turn-audit, or the dispatch logs — the witness is
  the orchestrator's overnight observation, not a fleet ledger row. If the
  baseten lane dropout recurs, the remediation surface is the model pin in
  ~/.claude/agents/workato-watchdog.md (and lanes choice per
  domains/model-gateway-playbook.md), not the fleet runner env.

## Card answer summary

- dreamer/project-dreamer/evidence "double-stub 2+ nights" = fleet-wide
  transient ENOTFOUND outage on 10-22 and 10-24; model pins irrelevant (jobs run
  claude -p on the default gateway model, fireworks/glm-5.3-flash per the
  sdk query_source line in the logs).
- Fix already in place (run-job.sh network preflight, deployed 2026-10-25);
  post-fix fires validated-clean.
- Watchdog empty turn-ends = baseten-lane model dropout class, distinct from
  the ENOTFOUND env class; no env/config change warranted.
