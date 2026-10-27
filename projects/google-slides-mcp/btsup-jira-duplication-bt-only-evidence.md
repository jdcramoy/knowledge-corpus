🧾 *Evidence: Jira is duplicating posted comments — BT Support's own automation is hit (live example, untouched)*

*What:* Jira server-side comment duplication — one comment POST → multiple identical rows · *Since:* ~2026-10-23 (an ×2 variant visible as far back as July) · *Still live:* ✅ yes, on BTSUP-79476 right now

*The untouched example*
• [BTSUP-79476](https://workato.atlassian.net/browse/BTSUP-79476) — a real customer request ("@BT Genie could we please assign someone else…") posted by the **Workato Integrations** account (BT Genie's own Slack→Jira bridge)
• Two identical rows exist: comment `1147627` created `13:04:50.097Z` and `1147628` created `13:04:50.190Z` — **93 ms apart**, byte-identical
• Nobody deleted them — visible on the ticket to anyone

*More survivors (all non-human authors)*
• BSYS-29684 — "AI Integrations" account, ×2 rows 5 s apart, Oct 19
• BTSUP-69368 — "Atlassian Assist" account, ×2 rows 1.2 s apart, back in **July** — so a low-grade version of this has existed for months

*Our own deeper finding (verified by controlled experiment)*
• Since Oct 23 ~16:24Z there's a worse, flapping **×3** form: one API POST → exactly 3 rows (consecutive ids, ~1 s spacing), server-side — not the client, not size, not format, hits BSYS and BTSUP both
• Downstream effect: every duplicate row fires its own webhook → duplicate Slack mirrors to customers

*What we already did on our side* — mirror dedupe + auto-cleanup, so our surfaces show one copy. But BT Support's pipeline (Workato Integrations comments, customer-visible tickets) has no such protection — the BTSUP-79476 example is still sitting on the ticket.
