# Spec: BSYS-29418 — Extract Design System 403-envelope fix, in-place prod push

Distilled 2026-10-09 by spec-distiller from BSYS-29418, the autopsy
(`cortex/investigations/82090477-prod-new-failures.md`), and the dev-fix
verification (`cortex/investigations/78677477-dev-fix-verification.md`).
Status: awaiting Josh's stop-push-start confirmation on the in-place prod
push. This spec is the contract the prod-push builder follows.

## Goal

Ship the dev-verified 403-envelope fix from dev recipe 78677477 to prod
recipe [82090477](https://app.workato.com/recipes/82090477) in place (stop →
push → start), so Google 403s from inaccessible presentations surface as the
fail-closed SOURCE_ACCESS_DENIED / CARRIER_ACCESS_DENIED envelope instead of
raw job failures.

## Scope

**IN:**
- In-place prod push of the already-pushed dev fix (source/carrier probe
  guards, steps 2–5 and 28–31 envelope paths) to prod 82090477.
- Post-push verification against the acceptance criteria below.
- MCP tool description integrity check for the served tool backed by 82090477.

**OUT:**
- No new fix code, no dev rework (dev fix already pushed 2026-10-08T23:58Z).
- No promotion-manifest/package flow — this is the in-place hotfix path.
- No changes to the Slides custom connector or connection acct 19921568.
- No changes to the mock-probe harness (probe noise is the trigger, not the
  defect; its source is a separate open question).

## Acceptance criteria

- [ ] Prod recipe 82090477 runs after the push: a post-push job completes with status succeeded on https://app.workato.com/recipes/82090477
- [ ] 403 probe returns the envelope: a post-push trace on 82090477 shows the fail-closed envelope (error_code SOURCE_ACCESS_DENIED with upstream_status 403) instead of a raw Forbidden-by-API-server failure
- [ ] Failure count flat: the daily failed-job count for 82090477 does not increase in the 24h after the push (workato-health sweep / wt-prod jobs list)
- [ ] MCP tool intact: the served MCP tool backed by 82090477 still lists correctly (mcp_server_get / tool resolver count unchanged) and no VUA personalization drift is observed after the push

## Design gate

Existing mechanisms checked, 2026-10-09:

- **workato-hot-swap skill** — this push is exactly its stop → edit/push →
  start → verify loop; the builder must follow it (includes the
  verify-the-running-flag trap: starts can silently no-op).
- **post-deploy-smoke skill** — covers the post-push first-green-job +
  connection + schedule verification; use its checklist for the criteria
  above.
- **prod-write gate (guardrails hook 13)** — the stop-push-start on prod
  82090477 is gated on Josh's explicit confirmation; that confirmation is
  this spec's pending input, not a step to route around.
- **Recipe snapshots (/snapdiff)** — pre-push snapshot of 82090477 must be
  captured so the push is revertable (rollback-rehearsal standard).
- **VUA revert trap (airo-mcp-playbook)** — post-push verify the
  "End user's connection" mode on 82090477; re-select only on observed drift
  (Josh ruling 2026-10-06: verify, don't assume).
- **workato-health.py hourly sweep** — already monitors 82090477; it is the
  failure-count-flat signal source. No new monitor needed.

## Risks

- **Start no-ops silently** — verify the running flag after start (workato-hot-swap trap); early warning: zero jobs seen post-push despite healthy status.
- **VUA/personalization revert on push** — identity-sensitive recipe; early warning: mcp_server_get shows connection mode flipped to base identity.
- **Probe noise returns** — mock probes will still hit prod until the probe-source question is answered; a post-push failure spike from mock context (Genie ID=mcp_mock_genie_id) is NOT a fix failure — check job context before alarming.
- **Fix not runtime-proven even in dev** — the dev fix has structure-only verification (no post-fix job existed as of 2026-10-09T01:25Z); if the 403 envelope shape differs from the classifier regex in prod traces, the push must stop and the dev fix be re-tested first.

## Open questions

- None blocking the push itself. (Separate track: where do the mock-probe
  invocations come from — cortex question 2026-10-08T23:16Z; and the dev
  check noting step 31 reuses SOURCE_ACCESS_DENIED for the carrier path —
  if the ticket requires a distinct CARRIER_ACCESS_DENIED code, raise it
  with Josh before shipping.)
