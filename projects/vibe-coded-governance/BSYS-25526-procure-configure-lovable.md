# BSYS-25526 — Procure and configure the third-party AI builder platform (Lovable)

Ticket: https://workato.atlassian.net/browse/BSYS-25526 (BSYS, assigned Josh, created
2026-05-06, In Progress, ZERO prior comments — the only never-triaged ticket in the May
governance cluster). Epic: BSYS-25523 (vibe-coded governance). Plan posted as Jira
comment 1141874 (2026-10-18), 5 points set. Grouping: vibe-coded-governance.

## Key finding

The ticket was unblocked for three months and nobody noticed: BSYS-25525 (vendor
selection) closed 2026-07-14 with Lovable selected after a successful POC and initial
security review. The May cluster (25526/25528/25529) got triaged 2026-10-09/10 except
this one.

## Established facts

- Vendor = Lovable (BSYS-25525 Closed; selection 2026-06-23, POC + security review
  passed 2026-07-14).
- The Confluence policy page (extbt 2553184311, "Vibe-Coded App Governance Policy",
  last modified Sep 2026) already carries a Lovable row: "Rapid prototyping,
  team-level apps", managed by BT Shared Services = the tier restriction is Tier 1-2,
  team-level internal apps. Workato AWS keeps Tier 2-4; external-facing promotes to
  Tier 4 = never Lovable.
- The same page is internally stale: it also says "the third-party AI builder is under
  evaluation. Candidates: Replit, Lovable, Vercel" and shows Status: Draft, Last
  Updated May 2026. Phase 4 of the plan reconciles it.
- Sibling dependency chain: BSYS-25529 Phase B is gated on THIS ticket; BSYS-29701
  (Lovable × Wiz CNAPP) shares the step-zero workspace inventory.

## Plan (7 phases, dependency line: 0 feeds 1; 2-3 wait on contract; 4 + 5-prereqs run during the wait)

0. Lovable workspace inventory (exists from POC? owners? count?) — shared with 29701.
1. Ironclad contract (long pole, months per Zoom precedent). Re-validate current
   enterprise SKU vs the July evaluation (Lovable Cloud postdates the POC; teams
   already use Lovable outside governance per 29701). SAML SSO, admin controls, data
   residency, commercial terms (seats/credits from Phase 0, cost center, renewal) all
   in contract.
2. Okta SAML SSO, groups → Lovable roles, SSO enforcement.
3. Workspace config WITH the preventive enforcement settings named: default project
   visibility restricted, public publishing/external sharing off platform-side (the
   25527 machinery is detective, not preventive; workspace settings ARE the
   enforcement for a team-level-scoped platform).
4. Finalize approved-platforms docs: update the policy page's Lovable entry, drop the
   stale under-evaluation text, reconcile Draft status.
5. One governed test app E2E (team-level by design). Entry conditions, schedulable
   into the contract wait: activate the register-app endpoint (25528), wire
   registry→risk-registry intake (register recipe 82959481 writes table 158543; the
   review recipe 82959473 reads only 158539 — intake is 25527's unbuilt last mile),
   fix the slack_bot connection and start 82959473.
6. Unlocks: 25529 Phase B starts the day this closes; 29701's Wiz rollout attaches to
   the same inventory.

## Dissent outcome (2026-10-18)

Dissenter verdict: SHIP-WITH-CHANGES, 5 material findings, all incorporated: (M1) the
ticket's enforcement requirement had no phase → Phase 3 now names the preventive
settings; (M2) billing/cost management was uncovered → Phase 1 commercial terms;
(M3) the "tier mapping unreadable" claim was FALSE — the Confluence policy page is
readable and carries the Lovable row (verified live by the main session too) → Phase 4
redefined as an edit of a stale page, Phase 5 test app fixed to team-level;
(M4) Phase 5's classification step rested on nonexistent intake wiring → three
prerequisites named and scheduled into the contract wait, register-app schema gap
(missing description/data sources/URL vs policy) flagged as 25528 scope; (M5) July
evaluation staleness → SKU re-validation step added. Cosmetic: dependency graph line
added; points kept at 5 with an elapsed-time caveat.

## Open items (Josh-gated)

- Josh's go to kick off execution (procurement itself is outward-facing regardless).
- Unverified: whether a Lovable workspace exists today, current SKU/pricing, Ironclad
  queue position, the framework deck itself (Google-auth; the Confluence page is the
  readable proxy).
