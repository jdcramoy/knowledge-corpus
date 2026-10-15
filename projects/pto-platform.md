# PTO Platform (BSYS-26808) — project knowledge

- Consolidated handoff: ~/Documents/Claude/HR-Genie-Master-Knowledge-Doc.md
  (this project's five dated handoffs were consolidated there — see that
  file; older: ~/Documents/Claude/BSYS-26808-handoff-2026-07-16.md,
  HANDOFF-PTO-Notifications-BSYS-26808.md, PTO-platform-session-handoff-2026-07-23.md)
- Specs: ~/Documents/Claude/PTO-platform-refactor-spec.md,
  PTO-platform-BT-testing-plan.md

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [[Earmiel] BT Operations: Handover Checklist](../../kb-corpus/confluence/intbt/1326874625-earmiel-bt-operations-handover-checklist.md)
- [[Offboarding] BT Operations: Handover Checklist](../../kb-corpus/confluence/intbt/1316159606-offboarding-bt-operations-handover-checklist.md)
- [BT Workflow Enablement Guide](../../kb-corpus/confluence/intbt/2557640730-bt-workflow-enablement-guide.md)
- [2024/12 + 2025/01 December/Jan Lookback](../../kb-corpus/confluence/intbt/542703625-202412-202501-decemberjan-lookback.md)
<!-- kb-bridges:end -->

## BSYS-27724 Manager PTO Digest — RETIRED Won't-Do (Josh, 2026-10-11)

**Decision:** digest not wanted — single per-request notifications already ship on the
existing cadence; the digest was additive rather than consolidating, and the per_set
grouping re-digests on EVERY request arrival (≈1 digest per arrival, each restating the
full list) — worse than the pings it was meant to replace. Also gated on BSYS-27657
Business Approvals (Spike 1 NO-GO 2026-10-10), so its own AC "individually actionable
digest lines" could never be met. Closed Won't Do; never promoted; no prod copy ever
existed.

**Disposition (all verified 2026-10-11):**
- Recipe 82959475: stopped → moved to dev Archive folder **31274124** (the dev-side
  convention folder; "zArchive" is the prod-side naming) → description prefixed RETIRED
  with the decision + "do not promote or restart without Josh's explicit go".
- Removed from combined promotion manifest 361068 (wt manifests update with explicit
  asset list; renamed "HR Genie 2026-10 promotion batch (hardening)", 10 assets,
  82959475 absent — verified on read-back).
- Deploy story BSYS-29498 (this batch) updated via milestone comment 1134911: scope
  change recorded, stale 11-recipe package 42196483 superseded (re-export from updated
  manifest before import), digest ACs dropped. Its description fields are SCREEN-LOCKED
  in Final Tech Review status — field edits fail "not on the appropriate screen"; use a
  comment for scope changes in that status.
- DIGEST claim rows in 146193 left as historical audit; shared tables/messenger untouched.

**Revival criteria (recorded in the ticket):** only if BSYS-27657 re-opens with a GO AND
managers report notification volume; revival starts from a fresh scoping pass, not the
archived recipe.

**Takeaway for notification-surface builds:** any ADDITIONAL notification surface on top
of existing ones needs an explicit "what does this REPLACE vs ADD" answer at spec time —
this one shipped to UAT before the additive-vs-consolidating question was asked.
