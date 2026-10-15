# BTSUP-78227 customer reply — consent-ask draft (2026-10-14, NOT posted)

Replaces draft-customer-reply-2026-10-12.md. Revised after independent adversarial
review broke the earlier draft (verdict BROKEN on the draft; the Oct 10 diagnosis
survived). Confirm-gated: posts only on Josh's go. This is the postable-NOW variant;
the post-fix confirmation variant stays in the README.

Why consent-ask: the fix is a write in the customer's Production workspace and is
Josh-gated; the earlier "I'll do it and report back" framing committed that write in
prose before any go. The consent ask also earns [requester]'s go in the same message, so a
single approval chain ([requester] yes, Josh go) unblocks execution.

## Review edits applied (forced)

1. "I found the problem" -> "I found what's blocking it right now" (the two findings
   explain the post-Oct-9 silence only; the original Oct 8 break cause is still a
   guess).
2. Dropped "which is why you now have two copies" - the "(2)" name predates the
   reconnect (in the ticket Oct 8, flagged Oct 9), so the reconnect cannot have
   caused it. Restated as: the duplicate already existed; the new-trigger path
   creates more, so we reuse the existing app.
3. "Your genie itself is fine" -> evidence only shows the native chat path running
   (2 conversations / 4 messages in 30 days).
4. Dropped "Nothing needed from you unless I hit a wall" - the dead-event-
   subscriptions branch may need the Slack app admin, who may not be [requester] (he
   cannot see delivery logs).
5. Pre-empted "who switched it off?" - unknown stopper, answer not prepared.
6. Formatting: verdict first, bold leads, whitespace.

## Draft (Josh voice)

Hi [requester],

Update as promised. I got into your workspace and found what's blocking the bot
right now.

**What's going on.** The genie is switched to inactive in your Production
environment, so nothing can run. On top of that, its Slack chat interface came off
during the reconnect we tried on the 9th, so Slack messages have nothing to land on.
Either one alone gives you the silence you're seeing on DMs and mentions. The
assistant itself is working; it runs normally on its built-in chat channel. Only the
Slack path is down.

**What this doesn't cover, in fairness.** These two explain why nothing fires now,
not why it first went quiet on the 8th. My working theory there is the misregistered
Slack trigger from the duplicate apps, but I'm still guessing. The test after the
fix is what settles it.

**The fix.** A small change in your Production environment: re-attach the existing
Slack app (A0C7HLXDUEN, reusing it; no new app, since the new-trigger path is what
creates more duplicates) and switch the genie back on. OK to proceed? Once it's done,
send the bot one DM. If it replies, we're done. If it stays quiet, send me the exact
time of that message and I'll take it to the platform team with the event payloads.
One heads up: if the app's event subscriptions didn't survive the reinstall, that
step may need whoever admins the Slack app on your side, since delivery logs aren't
visible from your seat.

## Not verified

- Genie's live state in workspace 3443496 (last read 2026-10-10, read-only; may have
  drifted).
- Whether A0C7HLXDUEN still holds valid event subscriptions after the reinstall
  cycle (screenshots suggest yes).
- Who admins the Slack app on the customer side.
