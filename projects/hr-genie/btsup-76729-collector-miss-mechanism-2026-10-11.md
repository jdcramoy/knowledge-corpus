# Collector miss mechanism — BTSUP-76729 follow-up (2026-10-11 ~22:00 PT)

Investigation only. No recipe edited, no status change, no prod touch.
Posted as BTSUP-76729 comment 1135182 (Service Desk Agents visibility).

## Question

The 10-10 record said collector 71498060 (HR Genie Confluence) "silently
missed both page-update events" on FTO page 242843660 with no mechanism.
Why does a polling trigger miss updates while still processing other pages?

## Evidence (live, dev workspace + Confluence API)

1. **Stop window.** Recipe `stopped_at: 2026-04-29T22:00`, restarted
   2026-07-21 18:31 UTC. The May FTO edit fell entirely inside the dead
   window. Nothing was polling; the edit was never going to arrive.
2. **Restart rescan skipped the page anyway.** The Jul 21 restart did a full
   reseed: ~55 deliveries in the 18:31-18:33 burst, walking the space forward
   in ID order. The burst delivered 2452619338 and 2391408725, the pages on
   either side of 242843660 in that walk, and skipped 242843660 itself.
3. **Confluence enumeration is clean.** Space listing today (HRKB, id
   74088637, sorted by id): 242843660 present at position 142 of 250 in the
   first batch, status current. The API does not hide the page.
4. **Delivery is lossy in both directions.** Duplicate deliveries are common:
   page 2923954217 (Bulgaria 101) delivered 12:49 and 12:59 on Oct 6, ten
   minutes apart; Portugal/Philippines leave pages doubled the same day;
   [GENIE] Instructions delivered 8+ times Sep 9-15. Upserts are
   doc_id-keyed so duplicates are harmless, just wasted tasks.
5. Cursor is alive (deliveries through Oct 6, 764 jobs, 0 failures, no poll
   errors), and 232 of 235 visible deliveries were below-cursor pages, so
   ID-ordered cursor position does NOT block update delivery generally.

## Verdict

Two compounding causes: (a) the May miss is explained by the 3-month stop
window (edits in a stop window are lost permanently, no backfill guarantee);
(b) the rescan skip has no external explanation left, so it is inside the
trigger's poll walk. Working theory: pagination seam, pages shifting between
limit-250 cursor batches. Not provable from outside the platform.

Actionable conclusion, mechanism-independent: the Confluence polling trigger
cannot be trusted alone for page-update delivery. Compensating control =
version-compare sentinel, not collector trust.

## Proposed (plan-lane, awaiting Josh's go, folded into 76729)

1. **Sentinel v2** (2 pts): extend 82959482 from one page to a full-KB sweep
   (every HRKB page version vs its KB doc updated_at, weekly, same P3
   publisher). Neutralizes the lossy-trigger class for the whole space.
2. **Ops rule:** any collector stop/restart requires a backfill check before
   it is called healthy (restart does not reliably backfill).

## Not verified

- The trigger's internal poll/dedupe mechanism (black box outside Workato
  platform internals).
- Whether the NEXT edit to 242843660 will be delivered (provable only by
  editing the live HR page, an outward content change).
- Whether a prod-side sentinel/re-ingest promotion is queued (nothing seen;
  prod KB doc still 1,003 bytes from 2026-04-03 per the 20:00Z pass).

## Cross-project lesson (candidate for domains/workato-platform.md)

Workato polling triggers on external content (Confluence et al) are lossy on
updates: stop windows lose edits with no replay, restart rescans can skip
pages mid-walk, and duplicate deliveries are normal. Any KB/content mirror
built on one needs a version-compare sweep against the source, scheduled,
not just the collector.
