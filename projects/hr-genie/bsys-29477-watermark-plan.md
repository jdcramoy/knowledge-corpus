# BSYS-29477 Technical Plan — Collector 82862205 watermark never advances past the boundary conversation

Ticket: [BSYS-29477](https://workato.atlassian.net/browse/BSYS-29477) (Bug, UAT, Medium)
Parent: [BSYS-26808](https://workato.atlassian.net/browse/BSYS-26808) Workday MCP/HR Genie Development
Recipe: [REC | HR Genie | Conversation Event Collector 82862205](https://app.workato.com/recipes/82862205) (dev, folder 32175654)

**Status: fix already built, pushed, and verified 2026-10-09. This plan records the
root cause and the as-implemented fix shape for the canon. Ticket is open only for
Josh's close on the posted UAT evidence.** Re-verified live 2026-10-11: the +1s
offset is intact in step 4 and the 15-min cadence is green (8/8 recent jobs
succeeded, latest [j-AbtXELpm-ptbsDE-CD](https://app.workato.com/recipes/82862205/job/j-AbtXELpm-ptbsDE-CD)).
Not hotfix class: dev recipe, no prod surface, no data loss.

## Problem statement

The collector polls Agent Studio conversations with `?from=<watermark>` and then
sets the watermark to the batch's max `created_at`. The API's `from` filter is
inclusive, so when the newest conversation IS the watermark boundary, every run
re-fetched that same conversation and the watermark could never advance past it.
Masked in the totals by the emitter's `source_job_id` idempotency (events
deduped downstream), but every 15-min run burned the full per-conversation
pipeline on the same row.

Evidence at discovery (2026-10-09): state row `last_conversation_at =
2026-10-09T10:42:18Z`, every run since 10:42 executed the step-9 guard condition
True, `events_emitted_total` stayed 0.

## Root cause (with evidence)

Inclusive `from` filter semantics plus a watermark set to the last processed
conversation's own `created_at`:

1. Step 5 (List conversations) requested `from = last_conversation_at`. With an
   inclusive filter, the boundary conversation always matched, every run.
2. The batch max `created_at` equals the watermark itself, so the state write
   re-committed the same value. The watermark was a fixed point.
3. Step 9's "new conversations in batch" guard evaluated True on every run
   because the boundary conversation kept coming back in the batch.

Trace evidence (the two-run UAT boundary proof, 2026-10-09):
[Run 1 j-AbsPQPwN-Ykkhef-CD](https://app.workato.com/recipes/82862205/job/j-AbsPQPwN-Ykkhef-CD)
shows window 10:42:18Z inclusive, guard True, full pipeline, state advanced
10:42:17Z to 10:42:18Z;
[Run 2 j-AbsPQth6-Kcg4Hx-CD](https://app.workato.com/recipes/82862205/job/j-AbsPQth6-Kcg4Hx-CD)
shows window 10:42:19Z, guard False, zero downstream lines. Under the old code
Run 2 would have re-fetched the boundary.

## Fix (as implemented, diff shape)

Step 4 ("Resolve genie and window") offsets the poll window by one second:

```ruby
# before
from_t = Time.parse(last) rescue (Time.now.utc - 86400)

# after (live in the recipe, verified 2026-10-11)
from_t = (Time.parse(last) + 1) rescue (Time.now.utc - 86400)
# BSYS-29477: from filter is INCLUSIVE, and the watermark is the boundary
# conversation's created_at; +1s keeps the boundary out of the next window
```

Why it is safe, and why no processed-ids exclusion is needed: `created_at` is
second-granular (step 6 truncates to whole seconds) and the watermark is the
processed batch's max `created_at`, so every conversation in the watermark's
second was already inside that batch, and a conversation cannot arrive after its
second has passed. `from + 1s` skips nothing.

Per-conversation events fetch (step 11) takes no `from` filter at all: it pulls
the whole conversation's events by ID, so inclusive-filter semantics do not
apply there and no offset is needed. (Note: BSYS-29488 later added a
late-event resweep to this recipe for a different gap; that change is out of
scope here and covered by the new-failures finding.)

Alternative rejected: keep the inclusive `from` and carry a processed-ids
exclusion list. More state, more failure modes, no benefit over the offset
given second-granularity.

## Regression test that would catch it

Two-run boundary fixture against the live genie (this is exactly what the UAT
run proved; codified as the assertion pair):

1. Seed the watermark one second BELOW the newest conversation's `created_at`
   (force the boundary case).
2. Run 1: assert the boundary conversation is fetched exactly once, the guard
   is True, and the state row advances `last_conversation_at` to the boundary's
   `created_at`.
3. Run 2 (no new data): assert the guard is False, zero downstream steps, and
   the state row is byte-identical to Run 1's. Under the bug, Run 2 shows guard
   True and a re-fetched boundary.

Secondary assertion: `conversations_processed_total` advances by the real delta
between runs, and `events_emitted_total` stays 0 when the only reprocessed
events are already ledgered (idempotency absorbing the boundary).

## Risks

- **Idempotency at the boundary**: the fix relies on the emitter's
  `source_job_id` idempotency absorbing any residual same-second reprocessing
  during the transition. Mitigation already in place and proven (events total
  stayed 0 across the UAT pair).
- **Sub-second ordering**: if Agent Studio ever returns sub-second or
  non-monotonic `created_at`, `+1s` could skip a conversation inside the
  boundary second. Current API is second-granular; if that changes, switch to
  inclusive `from` plus a processed-ids exclusion. Documented in the ticket.
- **Clock/parse failure path**: the `rescue (Time.now.utc - 86400)` fallback
  widens the window to 24h on a parse failure; with an inclusive filter that
  reprocesses up to a day of conversations. Safe only because idempotency
  dedupes; unchanged by this fix.
- **Downstream consumers of the state row**: any tooling that assumed the
  watermark can equal the newest conversation (it now must be strictly past it
  or one second beyond) should treat the value as an exclusive boundary.

## Story points

2 points. The fix itself is a one-line offset plus a boundary proof run
(~half day); the balance of the ticket was the two-run trace evidence and the
no-skip reasoning. The 2026-10-09 build consumed roughly this.
