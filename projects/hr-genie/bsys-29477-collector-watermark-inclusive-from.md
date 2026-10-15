# BSYS-29477 — HR Genie Collector 82862205 watermark never advances past boundary conversation

Status: fixed-awaiting-UAT (Josh's close pending). Fixed and verified 2026-10-09.

## Root cause

Recipe [82862205](https://app.workato.com/recipes/82862205) used an inclusive
`from` filter on the conversation list, so the boundary conversation at the
watermark matched every run and was reprocessed forever.

## Fix

Step 4 offsets the window by one second: `from_t = Time.parse(last) + 1`.
Second-granular `created_at` means nothing is skipped; the per-conversation
events fetch takes no `from` filter so there is nothing to offset there.

## UAT boundary proof (2026-10-09)

- Run 1 [j-AbsPQPwN-Ykkhef-CD](https://app.workato.com/recipes/82862205/job/j-AbsPQPwN-Ykkhef-CD):
  processed exactly the boundary conversation, watermark advanced 10:42:17Z -> 10:42:18Z.
- Run 2 [j-AbsPQth6-Kcg4Hx-CD](https://app.workato.com/recipes/82862205/job/j-AbsPQth6-Kcg4Hx-CD):
  boundary conversation excluded (guard False, state untouched).

## Separate: new-failures finding is NOT this bug

Six failed jobs 2026-10-10 04:24-05:24 UTC autopsied; the +1s offset is intact and
the watermark is not the failure surface. Root cause is a phantom-conversation
regression from the BSYS-29488 repair session's pushes (empty List-conversations
page materializes a blank row, conv_id '', epoch-0 created_at, defeating the
empty-batch guard). Owned by BSYS-29488; not auto-remediated. See
`bsys-29477-collector-newfailure-autopsy-2026-10-10.md`.
