# BTSUP-77184 — draft requester reply

- Ticket: BTSUP-77184, https://workato.atlassian.net/browse/BTSUP-77184
- Reporter: [requester]. (Sydney). Status: Awaiting information.
- State when drafted: Josh posted the backend reset + 11-step Slack reconnect
  on 2026-10-10 09:08Z. No reply from [requester] since, on the ticket or in the
  Slack thread. The backend connection reset was already performed; nothing
  left to do on our side until he responds.
- Draft saved 2026-10-11, NOT posted. Confirm with Josh before sending.

Context for the draft: Josh's posted steps cover the Slack path only. The
original report mentioned both surfaces, so the nudge asks the one confirming
detail (which surface) and carries both paths so Josh can paste whichever
fits. Cannot verify [requester]'s personal connection state from here; per-user
VUA connections are not observable in the dependency tracker.

---

## Variant A: follow-up nudge (he stays silent or reports failure)

Hi [requester], following up on this. The connection reset on our side is done, so
the stored one that was blocking you is gone. One thing would help me point
you at the right steps: are you hitting this in Slack with the HR Self Service
Genie, or through the MCP server in Claude or ChatGPT?

If it's Slack: open the HR Self Service Genie, send Hi, and click the connect
button it shows. On the Workato login screen, disconnect the Workday
connections first, then connect again and sign in through Workday, and finish
with Complete Connection. The disconnect step before reconnecting is the part
that's easy to skip, and skipping it is what keeps the old login alive.

If it's Claude or ChatGPT: disconnect the Workday MCP server in your settings,
reconnect it, and complete the Workday login when prompted.

If any step looks different from what I described, tell me which step number
and what you see, and we pick it up from there. The reset is done on our side;
the reconnect just needs to run once, in order.

## Variant B: closing note (he confirms it worked)

Hi [requester], glad that landed. I'll close this out. If the login prompt ever
shows up again, start with the reconnect steps from my earlier note, and if it
still fails we'll reset the connection on our side and run it once more.

---

## Not verified

- [requester]'s connection state post-reset (no read path to personal VUA
  connections), whether he has attempted the reconnect since 10-10, and which
  surface he is actually on.
- The prod end-user MCP server's VUA Required flag (the BSYS-26815 revert
  trap, residual risk from the 10-09 pass). One UI look on the prod MCP server
  page settles it when Josh is there.
