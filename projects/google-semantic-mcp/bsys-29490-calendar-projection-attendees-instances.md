# BSYS-29490 — GW Calendar projections strip attendees (events.list) and mis-project instances (end:null)

Status: fixed-awaiting-UAT. Full fix and evidence shipped 2026-10-10, the same
day the ticket was filed. Authoritative evidence comment: 2026-10-10 00:54.

## Root cause

Overlay `semantic/capabilities.v1.json` omitted `attendees` from the events.list
projection (mirrored into registry 147343), and the instances row had an
empty-inherit projection that projected `end:null`.

## Fix and evidence

- Overlay flipped, indexes regenerated, fix commit a3b66e8.
- Scoped promote to registry 147343 (3 rows) plus a sibling sweep of 1,042 rows
  with 5 stale curator rows repaired.
- Live probes green on both capabilities: attendees flowing on the Sen Rong 1:1
  series; instances project `{id, summary, start, end, attendees[]}` with
  `end:null` gone.
- Floor regression green on 240 families.
- Independent post-deploy probe 2026-10-10 01:14 confirms list@v3 returns
  attendees. Its "instances probe pending" line is stale — the 00:54 comment
  already probed instances green (two parallel sessions).

## Residual

Ticket in UAT awaiting Josh's close. When closing, read the 00:54 comment as the
authoritative evidence; the 01:14 "pending" line contradicts it cosmetically only.
