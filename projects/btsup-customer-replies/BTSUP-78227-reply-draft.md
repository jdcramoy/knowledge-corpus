# BTSUP-78227 — customer reply draft (status-only, confirm-gated)

**Ticket:** https://workato.atlassian.net/browse/BTSUP-78227 — Slack app not triggering Genie jobs
**Status when drafted:** 2026-10-14 fleet pass. Root-cause read posted internally 2026-10-10 (genie inactive in customer Production, Slack chat interface missing after the reconnect cycle). Fix is staged: re-add the Slack chat interface on the genie build page selecting the existing app A0C7HLXDUEN, start the genie, verify a DM creates a job. Both the fix (prod write in the customer's workspace) and this reply are held for Josh's go. Customer last replied 2026-10-09 ("im blocked already").
**Dissent gate:** skipped — status-only, states no new diagnosis (the diagnosis was Josh's Oct 10 post).

---

Hi [requester],

Quick update so you're not left waiting. We found what's wrong: the genie itself ended up stopped, and its Slack connection was removed during the earlier reconnect attempt, so nothing was listening when you messaged the bot. The genie and its skills are fine — it's the Slack wiring that needs to go back on.

The remaining step touches your production workspace, so it's going through our approval process rather than something I fire unannounced. Once it's in, the test is simple: send the bot one DM and a job should appear in the genie's job history. I'll follow up here as soon as it's done, and if anything still doesn't land after that, I'll take it to the platform team with the event details.
