# Dissenter-flagged drafts: disposition sweep (2026-10-16 ~23:15Z)

Read-only disposition check of the four dissenter-flagged drafts (cortex dispatch 23:10:37Z,
attention-queue items 2+7). Every verdict below cites live evidence: file mtimes, bus lines,
and Jira comments read back live from the `workato` site during this sweep.

## Verdict table

| Draft | Dissent (bus) | Exists? | Corrected post-dissent? | Sent? |
|---|---|---|---|---|
| BSYS-28422 status comment | FATAL, 2026-10-16T00:00Z | Original gone (rewritten in place); record file remains | YES — rewritten through 2 dissenter rounds | POSTED as comment 1140632, 2026-10-16 05:34Z |
| perf-review stakeholder overview | SHIP-WITH-FIXES, 2026-10-16T00:00Z | YES, at Orca workspace path | YES — all 8 must-fix items applied, file mtime 01:50 Oct 16 | NOT SENT — awaiting Josh approval |
| BSYS-29646 Susie-access reply | material (wrong-surface), 2026-10-16T00:00Z | Superseded by verified-path file | YES — SHIP-WITH-CHANGES, all corrections incorporated | POSTED as comment 1141196, 2026-10-16 13:57Z |
| BTSUP-76729 prod-reingest draft | FATAL, ~2026-10-12/13 | Original with false claim no longer on disk | YES — rewritten around Agent Studio API + direct doc read | POSTED as comment 1138909, 2026-10-14 19:37Z |

No draft is in a dangerous state: nothing uncorrected is sitting in a sendable position, and
nothing was posted carrying the dissent's fatal/material claims.

## 1. BSYS-28422 status-comment draft — CORRECTED AND POSTED

- Dissent: bus thread `bsys-28422-draft-comment`, dissenter.jsonl lines 80-85 (FATAL + 4),
  2026-10-16T00:00Z. FATAL: draft claimed the F2 processor decision "is not on record",
  contradicted by BSYS-29498 comment 1138897 (2026-10-14 19:32Z).
- Draft file: no standalone draft file survives; the durable record is
  `~/.claude/knowledge/projects/hr-genie/BSYS-28422-review-status-20261016.md`, which states
  the draft went through TWO dissenter rounds (round 1 BROKE it on exactly the F2 claim;
  round 2 added the second-identity dependency, probe-target rule, and a voice fix).
- Disposition: POSTED — comment 1140632 on BSYS-28422, created 2026-10-16T05:34:00Z, read
  back live this sweep. The FATAL claim is absent: the posted text correctly says the
  October 14 decision "accepts the flow" but its wording "doesn't match the transcript flow"
  — i.e. the dissent's reframe (wording gap, not unmade decision) replaced the false claim.
  Also incorporated: April-not-September dating ("the prod knowledge base dates to April"),
  the prod-touching-probe disclosure with per-action go, and a "Where I could be wrong"
  section. The 3-point plan on the ticket is awaiting Josh's go — no further action taken.

## 2. perf-review-stakeholder-overview-2026-10-15 — CORRECTED, NOT SENT

- Dissent: bus lines 86-92, verdict SHIP-WITH-FIXES with an 8-item must-fix list,
  2026-10-16T00:00Z.
- Doc: `~/orca/workspaces/workbench/Workday-Development/docs/hr-genie/perf-review-cycle/STAKEHOLDER-OVERVIEW-draft-2026-10-15.md`,
  mtime Oct 16 01:50 (about 2h AFTER the dissent timestamp) — edited post-dissent.
- Diff against the must-fix list (all 8 verified present in current text):
  1. Workday people-partner spike hedged: "Some of those fields need permission work on my
     side before they're real, and I'll flag it plainly if any of them can't come over."
  2. Competency auto-attach spike hedged: "That one is still being proven on my end."
  3. Nine-box Slack spike hedged: "the piece I still have to prove."
  4. The month added: "The cycle is roughly a month out."
  5. "Mostly kindly." cut — the standalone wink line is gone. RESIDUE: the softened
     "will let you know kindly and decline" keeps the word "kindly"; the dissent objected to
     the cheeky wink, and the plain phrasing likely clears it, but it is the one spot worth
     a second look before sending.
  6. "ten fields" cut — 7 fields named concretely, no invented count.
  7. Tester SWAT ask restored (Timing section, Brittany+Justin named) AND the
     leadership-support question restored ("keep-or-drop the leadership-support question").
  8. Claude project line added (opening paragraph) and sheet-ACL claim hedged ("I'll confirm
     the exact list with Jo before launch... enforced by the sheet permissions we set up,
     not inherited from the old form").
  Cosmetic items: internal header removed, "two clicks" gone. The Leapsome-to-Workday ~6-month
  migration note is still unmentioned (was cosmetic, never applied — acceptable).
- Disposition: NOT SENT. Registry row (mission-control/registry.json, hr-genie-perf-reviews)
  records the need as "approve stakeholder overview before it goes out", and events.jsonl has
  no send record after the 01:50 edit. It sits with Josh for approval.

## 3. BSYS-29646 Susie-access reply — CORRECTED AND POSTED (remediation still gated)

- Dissent: bus lines 97-101, 2026-10-16T00:00Z. Key material finding: wrong-surface remedy —
  the failure is in Slack, but the draft's step quoted the Workato GO re-login doc
  (intbt 2532671573); the fix per ASEE 2118942766 is the Slack `logout` command / CSV preload.
- Original: posted plan comment 1137701 (2026-10-13 21:28Z) had prescribed the Workato-GO
  re-login and an absolute "No manual Workato-side adds".
- Correction: live-verified pass recorded in
  `~/.claude/knowledge/projects/csm-genie/bsys-29646-access-path-verified.md` (2026-10-16):
  gate = exactly one End User Group `[TEAM] T32 | CSM` (104 members, updated 2026-09-30,
  predating Susie's 10-09 grant); dissenter verdict SHIP-WITH-CHANGES with all three
  corrections incorporated before posting.
- Disposition: POSTED — comment 1141196 on BSYS-29646, 2026-10-16T13:57:48Z, read back live
  this sweep. Step 3 now reads "Have her run the `logout` command against any genie she's
  logged into" — the Slack-surface remedy the dissent demanded. The too-absolute UI-add ban
  was softened ("marked not-applicable" per intbt 1689976864), and the ASEE sync claim is
  flagged as an unverified guess in "Where I could be wrong". DEVIATION: the dissent's
  escalation remedy (engineering backend CSV preload) was replaced by "Invite End User
  record, then SAML claims with the Okta admins" — the CSV preload path is not in the posted
  sequence. Current state: Nicholas Chiodo gave requester-side go (comment 1141149, 12:58Z);
  the prod access change itself still awaits Josh's per-action confirmation. Nothing executed.

## 4. BTSUP-76729 prod-reingest draft — REWRITTEN AND POSTED

- Dissent: bus lines 56-60 (subject `dissent-btsup-76729-prod-reingest`; rows predate the
  2026-10-16 block — era ~2026-10-12/13; ts field empty on these rows). FATAL: draft claimed
  "The Developer API has no KB endpoints (both candidate paths return 404)" and "I could not
  re-ingest directly or even snapshot the prod doc counts" — falsified by the documented
  Agent Studio API under /api/agentic/ with a live-verified prod read.
- Draft file: the file carrying the false claim no longer exists anywhere in the knowledge
  tree (text appears only in dissenter.jsonl and trigger-log.jsonl). Surviving 76729 draft
  files (`projects/hr-genie/btsup-drafts-2026-10-11.md`, mtime Oct 11 23:09;
  `BTSUP-76729-closing-reply-draft-2026-10-12.md`, mtime Oct 12 19:46) do not contain it.
- The rewrite HAPPENED: mission-control registry row (btsup-76729-hr-genie-kb workstream)
  records the discovery executed via `GET /api/agentic/knowledge_bases` (522 prod docs) and
  first-hand proof that doc 242843660 is stale (created=updated 2026-04-03T07:32:38, never
  re-ingested).
- Disposition: POSTED — comment 1138909 on BTSUP-76729, 2026-10-14T19:37:44Z, read back live
  this sweep. Every dissent point incorporated: cites the Agent Studio API path ("The public
  Developer API covers KB-level reads under /api/agentic/knowledge_bases (I used it for the
  doc inventory above)"), states the direct doc-242843660 proof with the April 3 seed date
  (not the unsupported "March snapshot"), softens the skip claim ("The skip I saw in dev left
  the prod copy stale the same way"), and discloses the passed shortcuts including the prod
  Agent Studio delete path in "Where I could be wrong". Aftermath: all build comments flipped
  internal-only (comment 1140365, 2026-10-15 22:16:50Z); the actual prod fix remains blocked
  on the DR promotion of 82959474 + 82959482.
- Note on the "22:05Z queue item": no queue row timestamped exactly 22:05Z was found in
  triage/queue.jsonl or the decision inbox during this sweep. Its two demands (Agent Studio
  API under /api/agentic/, direct KB read of doc 242843660) are both demonstrably satisfied
  by comment 1138909, so the rewrite verdict does not depend on locating that row.

## Bottom line

All four drafts cleared their dissent gates: three were corrected and posted (1140632,
1141196, 1138909 — each read back live with the fatal/material claims absent), one
(perf-review overview) is corrected and parked awaiting Josh's approval. The only open
executions are Josh-gated: the BSYS-28422 3-point plan, the BSYS-29646 prod access add, and
the BTSUP-76729 DR promotion.

## Not verified in this sweep

- Whether Josh has approved/sent the perf-review overview since the 01:50 edit (no send
  record found as of sweep time; file remains a draft).
- Susie's actual group membership and any executed fix on BSYS-29646 (gated, nothing fired).
- ASEE page 2118942766 content (login-walled; the posted comment itself flags it as unverified).
- The exact 22:05Z queue row for the 76729 rewrite (see note above).
