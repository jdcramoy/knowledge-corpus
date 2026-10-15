# BSYS-29490 plan — calendar projections strip attendees (events.list) and mis-project instances (end:null)

Ticket: https://workato.atlassian.net/browse/BSYS-29490 (UAT, 2 pts, epic BSYS-29262).
Status: plan posted on the ticket 2026-10-11 (comment 1134988). FIX ALREADY SHIPPED,
so the plan documents verification evidence, not a diff.

## Problem statement

Calendar reads through the gateway returned events with no `attendees[]`, and
recurring instances projected only `created`/`creator` with `end: null`.

## Root cause (evidence-cited)

Overlay `semantic/capabilities.v1.json` omitted `items.attendees` from the
`calendar.events.list@v3` projection (mirrored verbatim into registry 147343), and
the `calendar.events.instances@v3` row carried an empty-inherit projection. The
served mask and projection both derive from the same overlay entry in
`build-semantic-indexes.mjs`, so the transport and compiler were never at fault.
Fix commit `a3b66e8` (2026-10-09): projection += items.attendees on list@v3;
instances pinned to `[items.id, items.summary, items.start, items.end,
items.attendees]`; scoped promote (3 rows) plus sibling sweep of 1,042 rows
(5 stale curator rows repaired).

## Verification evidence (live probes, 2026-10-11, this pass)

- `calendar.events.list@v3` probe (intent `list events`, search "Josh / Sen Rong
  1:1"): READ_EXECUTED, 25 items, all carry full `attendees[]` including
  organizer/self/responseStatus/displayName and decline comments. Series
  `1shs5ir7ebdm5qt234aca6kpgv` returns senrong@workato.com (organizer) and
  josh.cramoy@workato.com (self) per instance.
- `calendar.events.instances@v3` probe (intent `instances events`,
  event `1shs5ir7ebdm5qt234aca6kpgv`): READ_EXECUTED, 5 items, all
  `{id, summary, start, end, attendees[]}`. `end` populated, no created/creator.
- Registry checksum `195c4463…` serves both rows read_enabled with pinned
  projections; the fix is live on the serving path.
- Prior passes: build probe + post-deploy probe 2026-10-09 (ticket comments
  00:54 and 01:14). The 01:14 "instance-probe pending" line was stale; this
  pass's instances probe settles it a third time.

## Test that catches it

`tuple-workflow-regression.mjs` floor (240 families) plus a live-probe assertion
in the calendar sweep: any events.list/instances item with attendees in raw
Google but none in the projection fails the sweep.

## Risks

Low. Projection widening only; no mutation surface. Curator paraphrase rows were
already swept, but new paraphrases generated after the sweep should be spot-checked
for stale projections (the sweep rule from BSYS-29397/29398 applies to any future
projection change).

## Remaining

None to build. Josh's close is the only step.
