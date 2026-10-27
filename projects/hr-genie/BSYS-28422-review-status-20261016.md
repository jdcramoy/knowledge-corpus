# BSYS-28422 — pre-go-live security review: state + closure plan (2026-10-16)

Posted as [comment 1140632](https://workato.atlassian.net/browse/BSYS-28422?commentId=1140632) on
[BSYS-28422](https://workato.atlassian.net/browse/BSYS-28422). Drafted through the
jira-autotriage loop; dissenter gate ran twice (round 1 BROKEN the draft — F2 had already been
decided 2026-10-14; round 2 raised the second-identity dependency, probe-target rule, and a
voice break; all applied). Findings on the bus: thread `bsys-28422-draft-comment`.

## Why this comment exists

HR Genie has been live in prod since at least April (prod KB doc dated 2026-04-03; real-user
ticket BTSUP-76729 filed 2026-09-17), but the pre-go-live review story's last milestone was
Aug 26 (masking, 47 of 48 recipes). The story was silently stale against a live surface.

## State per acceptance criterion

- Done: masking (Aug 26, jobs on ticket); red-team clean passes on secrets / injection / commit
  caller registry / MCP auth across the 44 batch assets (verdict
  `redteam/BSYS-29498-hr-genie-oct-prod-batch.md`, 2026-10-12). VUA identity paths excluded
  from that review.
- Gap found: the F2 processor decision (comment 1138897 on BSYS-29498, 2026-10-14 19:32Z)
  accepts "recipe configuration, not sensitive data" while the verdict documents decrypted
  employee transcripts (names intact) going to OpenAI nightly. The recorded acceptance doesn't
  name the flow that exists. Fix: re-record naming the flow, or ship the name-suppression pass.
- Open, no evidence anywhere (verified by dissenter sweep of the project folder): signed
  least-privilege inventory; the ticket's 6-case negative-authorization matrix + positive
  proofs; Slack/Workday scope review; retention/purge rules for notification + incident
  ledgers.

## The 3-point plan (on the ticket, awaiting Josh's go)

1. Re-record F2 acceptance naming the actual data flow (or route to name-suppression), 0.5d.
2. Negative-authorization matrix: dev genie absorbs single-identity cases; cross-user cases run
   prod-primary (second dev identity blocked since August, per BSYS-26816 + BSYS-28314 scoping
   notes), every probe targeted at Josh's own tasks or a test worker, per-action go at fire
   time, 1.5d.
3. Signed inventory + scope review + retention rules from the live estate, 1d.

## Not verified

- Whether Josh's F2 wording was deliberate shorthand for the whole judge flow (his call; if so,
  item 1 is a one-line wording note).
- Dev-genie vs prod-genie identity-path parity (red team excluded VUA paths).
- The F1 re-export still owed on BSYS-29498 (last checked 2026-10-14 21:12Z, not re-probed here).
