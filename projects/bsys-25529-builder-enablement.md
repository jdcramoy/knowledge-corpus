# BSYS-25529 — Builder enablement materials

Jira: BSYS-25529 (Story, Backlog, points 5). Epic BSYS-25523 vibe-coded app governance; siblings BSYS-25527 (classification/gate) and BSYS-25528 (registry). Dependency BSYS-25524 (framework) Closed; BSYS-25526 (platform procurement) In Progress and gates Phase B.
Plan posted 2026-10-09 (Jira comment 1134769); Phase A built 2026-10-10 (comment 1134807); updated plan posted 2026-10-11 (comment 1134967).

## Phase A (built, UNPUBLISHED Confluence drafts in BTI space, parented under the governance policy page)

- Builder Enablement hub — page 2942992465
- Tier and SDLC Quick Reference — page 2943254533
- Platform Decision Tree — page 2942632094 (mermaid verified rendered; platform nodes are "approved platform per BSYS-25526" placeholders)
- Builder Enablement FAQ — page 2942894180

Source of truth: kit repo agentic-workato-kit/docs/enablement/ + manifest.json mapping file → page ID. All four passed read-back verification at draft time. Publishing is Josh-gated (new Confluence pages): on his go, publish hub → quick reference → decision tree → FAQ, in that order so links resolve, sanitizer + read-back each time.

## Phase B (gated on BSYS-25526 — do not pre-build)

Onboarding guide per approved platform (validated against 25526's first-deployment test app), one starter template per platform in the kit repo, and placeholder replacement in the decision tree.

## 2026-10-11 triage note

The updated-plan comment (1134967) flagged it had not re-read the draft pages that pass; next session touching this ticket should re-verify draft content live before reporting state. Remaining points: 2 for the publish pass; Phase B accounted when it unblocks.
