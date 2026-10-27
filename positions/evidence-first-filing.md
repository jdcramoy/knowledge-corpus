# Position: evidence-first filing (narrowed to outward-facing filings)

Status: PROVISIONAL house position (librarian weekly pass 2026-10-19,
v2 after same-day dissenter attack). Review date: 2026-10-26. The
dissenter's core attack STOOD against the v1 draft: both the scope and
the mechanism were wrong as written. This v2 is the narrowed
survivor; see the Dissent log for what was cut and why.

Origin: Josh verbatim 2026-10-17 (ASEE Confluence-space session,
transcript `~/.claude/projects/-Users-<user>-Documents-workbench/
444dbc4b-e5af-44f5-955d-f16bdf5363bb.jsonl`, captured in
`garden-reports/garden-2026-10-17.md` section 1e): "I would just file
them with PSM ticket but make sure you have evidence and logs before
you go down that route. They will hammer us if we don't back our shit
up with real evidence."

## The position (v2)

1. **Outward-facing filings carry their evidence at filing time.**
   "Outward-facing" means a party who can push back sees it: PSM and
   vendor tickets, prod-bound promotion evidence, customer-visible
   artifacts, Jira comments a reviewer will act on. The evidence is a
   trace line, job ID, API response, or file path with the load-bearing
   line quoted, captured when observed.
2. **Evidence is RE-CHECKED at filing time, not assumed from memory.**
   (v1 said "captured at observation time, never reconstructed"; the
   dissenter showed the house's one real filing failure, the 2026-10-17
   morning brief's false "night chain broke" alarm, was a CAPTURE-TIME
   misread by a writer who believed it had evidence. The discipline
   that caught it was re-verification by another session. So the rule
   is re-check the artifact against the live source when you file, not
   a provenance folklore about when you first saw it.)
3. **The disclosure escape hatch is closed on tier-1 surfaces.** "Says
   what is unverified" is NOT compliance for a PSM ticket or prod
   promotion: those file with evidence or do not file (the origin
   rule). The NOT-verified list convention remains for INTERNAL
   surfaces only, where it is genuinely useful.
4. **Internal surfaces keep their existing charters; one gap gets one
   line, not a constitution.** Watchdog autopsies, triage cards,
   uat-evidence, redteam verdicts, deployment-request, jira-story-
   standards already mandate cited evidence by charter. The residual
   uncovered surface is morning-brief rows and bus posts: proposed
   convention, one line, "brief rows cite the check command" ( gardener
   can plant it or a brief run adopts it).

## What was NOT adopted (the dissenter was right)

- No fleet-wide four-rule filing constitution. Zero incident data
  supports extending the mandate to every internal surface, and the
  cost lands in a harness whose measured number one cost is context
  tax (`domains/harness-benchmarking.md`).
- No claim that evidence capture is "nearly free". No measurement
  backs it and the v1 form was unfalsifiable.
- No enforcement hook this pass. A remembered rule is not a mechanism
  (accepted dissent finding F2, `positions/event-sourced-fleet-state.md`).
  If the incidence rate justifies it, the candidate mechanisms are an
  evidence-required field in mission-control events or a Jira-posting
  gate; both are hook-class installs and therefore never_auto,
  Josh-gated.
- No internal rollout before a baseline. If this position is to grow
  teeth, the first step is a 7-day incidence count of filings shipped
  without evidence, not a rule.

## Evidence from this house

- 2026-10-17: Josh's PSM quote (origin above) is the only recorded
  instance of a filing being "hammered" for missing evidence. One data
  point; the position is scoped to exactly that surface for that
  reason.
- 2026-10-17: morning-brief false alarm ("repair the broken night
  chain") corrected by 08:11 same day; night chain was verified live
  and repaired (gardener `garden-2026-10-17-late.md` L4). Shows the
  failure vector is misread-at-capture and that cross-session
  re-verification catches it.
- Existing charters already cover the high-stakes surfaces (list in
  rule 4). This position adds the PSM/outward minimum plus the brief-row
  convention; it deliberately adds nothing else.

## Dissent log (constitutional section)

Attack: dissenter agent run 2026-10-19, full report in
`dreams/bus/dissenter.jsonl` thread `dissent-evidence-first-filing`
(2026-10-19T02:10:56Z). Verdict: survive-with-amendments. Seven
attacks; the two that stood and forced this rewrite:

1. SCOPE: the draft's own cited source scopes the rule to PSM; v1
   generalized to every internal surface with zero supporting
   incidents. ACCEPTED in full; v2 narrows to outward-facing.
2. MECHANISM: rule 2's "reconstruction is where fabrication enters"
   was empirically wrong for the house's one real incident (capture-
   time misread, caught by re-verification). ACCEPTED; replaced with
   re-check-at-filing. The dissenter's strongest one-sentence
   objection: "The draft's own cited source scopes the rule to PSM
   filings, and the house's one real incident shows the failure vector
   is capture-time misreading rather than filing-time reconstruction,
   so both the scope and the mechanism are wrong as drafted."

Attacks rebutted or parked, with reasons:

- Attack 3 (no mechanism, repeats the remembered-rule failure):
  REBUTTED only partially. A position piece is not a mechanism, the
  dissenter is right; but the narrowed rule is a filing DISCIPLINE for
  sessions that already gate on the verify skill, and the hook
  candidates are named above with the correct never_auto routing.
  Parked, not claimed as solved.
- Attack 4 (cost unfalsifiable): ACCEPTED by deletion. v2 makes no
  cost claim and requires a baseline before any expansion.
- Attack 6 (residual gap is one surface): ACCEPTED; became rule 4.
- Attack 7 (escape hatch swallows the mandate): ACCEPTED; became
  rule 3.

## Related

- `garden-reports/garden-2026-10-17.md` section 1e (origin capture)
- `positions/event-sourced-fleet-state.md` (precedent for the
  survive-with-amendments outcome and the dissent-log format)
- `domains/managed-agents-policy-watch.md` (the other filing-quality
  liability register this house maintains)
