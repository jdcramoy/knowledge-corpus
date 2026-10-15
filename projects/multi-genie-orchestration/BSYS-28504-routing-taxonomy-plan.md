# BSYS-28504 — Routing taxonomy, exclusions, Decision Model rules (technical plan)

Filed 2026-10-12 from the jira-triage pass. Epic: BSYS-28503 (Identity-Safe
Multi-Genie Orchestration POC). Status at planning: Backlog; POC frozen
2026-10-03 pending Product/leadership/BT direction (Confluence banner),
reaffirmed in the 2026-09-16 ticket comment.

## Acceptance-criterion gap map (evidence per row)

| AC | State | Evidence |
|---|---|---|
| Router input fields + allowed enum values documented | DONE | `routing-policy.v1.json` (schema_version 1, routes carry intent/owner/capabilities/precedence) in `~/Documents/ChatGPT/Multi-Genie Orchestration/` |
| Decision outputs limited to specialist/multi-domain/clarify/secure-handoff/unsupported/escalation | PARTIAL | `default_outcome: CLARIFICATION_REQUIRED` exists; the six-outcome enum is not pinned anywhere as the only legal outputs |
| Security-ineligible rules precede domain routing rules | NOT BUILT | No risk-class or security-gate ruleset in policy v1 |
| Default output is clarification, never a specialist | DONE | `default_outcome` + gateway route-registry fail-closed INACTIVE |
| Decision rules stored independently of the Genie job description | DONE | Policy lives in `routing-policy.v1.json`, external to Main Genie's job description |
| 25 clear examples/domain + ambiguous/cross-domain/unsupported/adversarial labeled | PARTIAL | `routing-regression-set.json` v1 = 64 cases total (~5/domain across 12 routes); no adversarial class coverage at the AC bar |
| User text cannot select Genie ID, connection, or routing rule | DONE | Identity invariant (non-negotiable, project.md) + `never_route_from_claimed_identity` + `no_keyword_only_routing` rules |
| Route/reason-code version for telemetry + regression | PARTIAL | `policy_id`/`schema_version` exist; a reason-code taxonomy is not versioned or emitted |

## Drift risk to reconcile first

The 2026-09-16 comment says live routing now runs via direct capability
ownership (Enterprise Data and CSM owned directly; other domains per their
source policies) — which is not what `routing-policy.v1.json` (dev,
environment field) describes. Two routing truths exist: the frozen policy
asset and the live ownership model. Hardening on top of the stale asset
would harden the wrong thing. Step 1 of any build is a reconciliation pass
that either refreshes the policy asset to the live ownership model or
documents that the asset is historical and the build re-baselines from live.

## Proposed build (3 points, gated on the POC freeze lifting)

1. **Reconcile** policy asset with live routing ownership; re-baseline or
   retire `routing-policy.v1.json` (0.5d).
2. **Security-gate ruleset**: risk classes per capability, security-ineligible
   rules ordered ahead of all domain routing rules, pinned six-outcome enum
   (1d).
3. **Reason-code taxonomy v2**: versioned reason codes emitted with every
   route decision, wired to telemetry; regression set keyed on them (0.5d).
4. **Corpus expansion**: regression set to 25+ clear cases per domain plus
   ambiguous, cross-domain, unsupported, and adversarial classes; rerun the
   gateway regression suite green (1d).

## Acceptance criteria for the build

- Security-gate evaluation provably precedes domain routing in the decision
  path (test case where a user-text attempt at a security-ineligible target
  is refused regardless of domain match).
- Outcome enum constrained to the six legal outputs; a violation is a test
  failure.
- Regression set carries versioned reason codes on every case; telemetry
  surfaces route + reason + version.
- Suite green at 25+ cases/domain including all four non-happy classes.

## UAT evidence

To be recorded at build time: policy-reconciliation diff, security-gate test
traces, expanded regression run output, telemetry sample showing versioned
reason codes.

## Verdict

Three of eight acceptance criteria are fully met by existing assets, three
are partial, two unmet. The remaining build is 3 points of policy/corpus
work, not infrastructure — but it is staged behind the POC freeze, so it
waits on direction before anyone kicks it off.
