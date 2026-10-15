# BSYS-25529 plan — Create builder enablement materials

Ticket: https://workato.atlassian.net/browse/BSYS-25529 (epic BSYS-25523, aged since May, Backlog, points 5). Plan posted to Jira 2026-10-09.

## Context

- Sibling plans filed 2026-10-09 in this folder: BSYS-25528 (app registry, points 3), BSYS-25527 (classification process + internet gate, points 3). Dependency verified live: BSYS-25524 (governance framework) Closed; BSYS-25526 (platform procurement/configuration, https://workato.atlassian.net/browse/BSYS-25526) In Progress.
- The earlier sibling note marked 25529 "parked" pending BSYS-25526. That is half right: the ticket's deliverables split cleanly into framework-dependent material (unblocked now, since 25524 is Closed) and platform-dependent material (gated on 25526). This plan builds the unblocked phase and pre-stages the gated phase so nothing re-designs later.
- Audience spans non-technical vibe-coders to Tier 3 AWS Amplify engineers; the harness-docs publishing machinery (kit repo source of truth, weekly Confluence sync, sanitizer) already exists and is reused, not rebuilt.

## Business Requirements

- Platform selection guide: decision tree mapping tier + sharing scope to the recommended platform.
- Onboarding guide per approved platform (account setup, first deployment, key guardrails).
- At least one starter template per platform.
- Quick-reference card for tier classification and the SDLC.
- FAQ covering common scenarios.
- All materials reachable from one central Confluence location; written for builders, not policy readers.

## Technical Requirements

- Central hub: one Confluence parent page "Builder Enablement" in the governance epic's space, linking all five deliverable types. Repo source of truth mirrors the harness-docs pattern: `~/Documents/agentic-workato-kit/docs/enablement/` with a manifest mapping file to page ID (re-read, never quote from memory), the same weekly Tue 06:57 sync can carry it after Josh approves new pages.
- Phase A (unblocked now, depends only on the Closed framework):
  - Quick-reference card: tier classification + SDLC on one page, printable one-pager structure.
  - Decision tree: Confluence page plus a mermaid flowchart (tier + sharing scope to platform), drafted from BSYS-25524's approved rules; platform nodes render as "approved platform per BSYS-25526" placeholders until the platform list lands.
  - FAQ shell seeded from the framework, the 25527 checklist/classification flow, and the registry flow (25528) — the questions those processes generate.
- Phase B (gated on BSYS-25526 completing: platform list with tier restrictions, first test app deployed):
  - Onboarding guide per approved platform, using each platform's real first-deployment path validated against the test app from 25526's AC.
  - Starter templates: one per platform in the kit repo (`docs/enablement/templates/<platform>/`), each with a README that walks the guardrails from the framework.
  - Decision tree placeholders replaced with real platform names.
- Publish policy per existing rules: new Confluence pages are Josh-gated; sanitizer applied (no workspace IDs, tokens, internal identifiers); contentFormat "markdown" explicit on every write; read-back verification after each publish.
- Prose in Josh's voice (josh-writing-voice): no em/en dashes, minimal bold, close on a verdict.

## Acceptance Criteria

- [ ] Central "Builder Enablement" hub page published; every deliverable reachable from it in one click.
- [ ] Quick-reference card (tier classification + SDLC) published.
- [ ] Decision tree page + mermaid diagram published, mapping tier + sharing scope to platform (real names once 25526 supplies them).
- [ ] Onboarding guide published for each approved platform (gated on 25526; one per platform).
- [ ] At least one starter template per platform available in the kit repo, linked from its onboarding guide.
- [ ] FAQ published with answers traceable to the framework or sibling process stories.
- [ ] Every published page passes read-back rendering check; sanitizer applied.

## UAT Evidence

- Read-back verification record per published page (rendered correctly, no internal IDs).
- One walkthrough: a builder follows the decision tree end to end for a sample scenario and lands on a platform + onboarding guide without reading the policy.
- Phase B: starter template actually deploys to the 25526 test platform.

## Risks

- BSYS-25526 has legal/procurement lead-time history (Ironclad, months) — Phase B may slip independent of this ticket; Phase A ships regardless.
- Decision tree accuracy depends entirely on the approved framework's tier definitions; if 25527's classification process changes them, the tree must be updated in the same session.
- Enablement content ages fast once platforms change; the weekly sync catches drift only for pages in the manifest.

## Points

5 (2-3 days): five deliverable types, hub + repo structure, phased on 25526, UAT walkthrough.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [BTSUP Workflow Enablement Guide](../../../kb-corpus/confluence/intbt/2005893143-btsup-workflow-enablement-guide.md)
- [[CS-12] Changelog BSYS-5834 - Implement Stage gates for Renewal with Upgrade](../../../kb-corpus/confluence/intbt/385450154-cs-12-changelog-bsys-5834---implement-stage-gates-for-renewal-with-upgrade.md)
- [2026/01 January Lookback](../../../kb-corpus/confluence/intbt/2264989702-202601-january-lookback.md)
- [BT Workflow Enablement Guide](../../../kb-corpus/confluence/intbt/2557640730-bt-workflow-enablement-guide.md)
<!-- kb-bridges:end -->
