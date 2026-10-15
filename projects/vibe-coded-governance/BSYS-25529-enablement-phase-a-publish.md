# BSYS-25529 — Builder enablement materials (Phase A publish plan)

Ticket: https://workato.atlassian.net/browse/BSYS-25529 (epic BSYS-25523, Backlog, points 5).
Plan posted 2026-10-10 (comment 1134769), Phase A built 2026-10-10 (comment 1134807). This file holds the 2026-10-11 publish plan.

## Live evidence (2026-10-11)

- Phase A staged as four unpublished Confluence drafts in the BTI space, parented under the governance policy page: Builder Enablement hub (2942992465), Tier and SDLC Quick Reference (2943254533), Platform Decision Tree (2942632094, mermaid verified rendered), Builder Enablement FAQ (2942894180). All four passed read-back verification per the build record; source of truth in the kit repo at docs/enablement/ with manifest.
- Dependency check today, live: BSYS-25526 (platform procurement, https://workato.atlassian.net/browse/BSYS-25526) still In Progress, so Phase B (onboarding guides per platform, starter templates, placeholder replacement) stays gated, as planned.

## Remaining work

1. Josh reviews the four drafts. Publishing new Confluence pages is his gate under the standing rules; publish only after his go, sanitizer + read-back each time.
2. On approval: publish hub, quick reference, decision tree, FAQ, in that order so links resolve.
3. Phase B starts when BSYS-25526 completes. Nothing pre-built that risks rework.

## Acceptance criteria (ticket)

- [ ] Central Builder Enablement hub published (draft staged; publish gated on Josh)
- [ ] Quick-reference card published (draft staged)
- [ ] Decision tree page + diagram published (draft staged; platform nodes stay placeholders until 25526)
- [ ] Onboarding guides per platform (gated on 25526)
- [ ] Starter template per platform (gated on 25526)
- [ ] FAQ published (draft staged)

## UAT Evidence

Read-back record per published page, plus one builder walkthrough of the decision tree for a sample scenario. Phase B: a starter template actually deploys to the 25526 test platform.

## Risks

Unchanged from the 2026-10-10 plan: 25526 procurement lead time may slip Phase B independently; the FAQ references the registry endpoint flow, which is one step behind its own activation (BSYS-25528).

## Points

2 remaining for the publish pass; Phase B accounted when it unblocks.
