# BSYS-29418 — Extract Design System skill raw errors on source-access failures: verification record

Ticket: https://workato.atlassian.net/browse/BSYS-29418 (UAT, 3 pts, parent BSYS-29417).
Not a build plan: the structured-failure-envelope fix shipped 2026-10-09 (dev
[78677477](https://app.workato.com/recipes/78677477) + prod
[82090477](https://app.workato.com/recipes/82090477)). This records the 2026-10-11
verification pass; full verification comment posted on the ticket (comment 1134989).

## What this pass added

The 10-09 comment listed the prod acceptance signal as pending ("first post-push
prod job evidence pending the mock-probe cadence"). Live prod read 2026-10-11:

- Prod [82090477](https://app.workato.com/recipes/82090477) totals 78 succeeded /
  65 failed of 143. Failed count flat at 65, exactly where it stood right after
  the port; last failure in the recent list is the pre-fix 01:41 run
  j-AbsJQ8BX-gx4kwb-CD.
- Every mock-probe job since the fix succeeded: j-Absbnwb9-Lt9LDH-CD,
  j-AbscWRd9-6QLxYx-CD, j-AbscWw6G-C86FGh-CD, all error-free.
- Closes the "failure count stops climbing from probe traffic" acceptance criterion.

## Still unverified (carried from 10-09, not re-checked this pass)

- The make-carrier-404 path specifically (catch is pattern-identical to the two
  live-proven monitor envelopes; needs the replay-state fixture shape).
- VUA connection-mode read-back on the prod serving MCP (Orca check).

## Remaining

No build. Josh's judgment on close, optionally after an Orca VUA read-back.
