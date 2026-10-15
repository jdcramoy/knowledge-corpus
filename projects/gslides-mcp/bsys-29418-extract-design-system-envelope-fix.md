# BSYS-29418 — Extract Design System raw job errors on 403/404 instead of structured envelope

Status: fixed-awaiting-UAT. Dev fix verified 2026-10-09 03:14; prod envelope fix
SHIPPED 2026-10-09 16:10 under Josh's approved stop-push-start.

## Fix arc

- Dev twin [78677477](https://app.workato.com/recipes/78677477): steps 2 and 25
  wrapped 2026-10-08 23:59; UAT evidence same night (403 j-AbsDCNEp-nhFbeY-CD,
  404 j-AbsDA3Qk-HBprzP-CD, cache-hit and fresh-extraction paths unchanged).
- Third unguarded call site found via a REAL prod 404 failure
  (j-AbsJQ8BX-gx4kwb-CD): `make_design_carrier`. Wrapped dev-first, then ported
  to prod [82090477](https://app.workato.com/recipes/82090477) 2026-10-09 16:10
  (Josh-approved stop-push-start). Prod read-back: envelope present, Running=true.

## Open items at close of the 16:10 comment (still open 2026-10-11)

- make-carrier-404 path never live-proven (needs the replay-state fixture; the
  catch is pattern-identical to two live-proven monitors).
- First post-push prod job evidence pending the mock-probe cadence.
- Prod VUA connection-mode read-back not yet re-verified after the push.
- Final acceptance signal: prod 82090477 failure count goes flat.

## Trap recorded

Prod pushes can revert VUA/connection-mode settings (BSYS-26815 class). Read-back
verify after every push on identity-sensitive skills.
