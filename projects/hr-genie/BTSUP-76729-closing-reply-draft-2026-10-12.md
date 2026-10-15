# BTSUP-76729 closing-reply draft (staged 2026-10-12, NOT posted)

Feeds the open harness-fix row `btsup-76729-closing-reply-confirm`. Nothing customer-visible
has been posted since the 2026-09-17 acknowledgment (25 days); fix landed in DEV 2026-10-10
and is verified live. This reply should ride with (or just after) the prod promotion of the
re-ingest + freshness sentinel, so the "rolling out" claim is true when sent.

## Underlying facts (evidence)

- HR Genie KB kb-AYc8DXFF-rzGerR-CD: FTO doc 242843660 "Flexible Time Off Program" re-ingested
  2026-10-10T08:23Z from the current Confluence page. Stale snapshot gone in dev.
- Root cause (autopsy): collector 71498060 sat stopped Apr 29 to Jul 21, so the May page edit
  fell inside the dead window and the July rescan skipped the page.
- Freshness sentinel 82959482 (MON | HR Genie | KB Source Freshness) green on its Monday
  cadence, latest run 2026-10-12 13:00 PDT.
- Caveat: many other KB docs still show 2026-03-31 timestamps; the KB-wide v2 sweep (2pt,
  proposed 2026-10-12) is unapproved.

## Draft (Josh voice, no internal IDs)

Hi [requester],

Quick update on this one. We found why the genie was quoting an old version of the policy:
the sync that keeps its knowledge current had been down for a stretch earlier this year, so
it missed the page update and kept serving the older copy it already had.

The current page has been refreshed into the genie's knowledge and is verified up to date in
our test environment. It rolls out to the live assistant with our next release, and I'll
confirm here as soon as it's live.

Thanks!

## Not verified

- Prod KB state (dev-verified only until promotion).
- Exact release timing for "next release".
