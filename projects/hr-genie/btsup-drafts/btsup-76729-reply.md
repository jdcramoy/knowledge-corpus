# BTSUP-76729 — draft requester reply

- Ticket: BTSUP-76729, https://workato.atlassian.net/browse/BTSUP-76729
- Reporter: [requester] ([requester] hit the behavior). Status: In Triage.
- Status: In Triage (fix shipped in dev by Josh 2026-10-10, no requester
  response since). Draft saved 2026-10-11, NOT posted. Confirm with Josh
  before sending.

Fresh state check 2026-10-11 ~20:00Z (live, read-only): the production KB
([kb-AYcm4ggH-L9o6zm-CD](https://app.workato.com/knowledge/kb-AYcm4ggH-L9o6zm-CD))
still holds the stale FTO doc (1,003 bytes, updated 2026-04-03, never
refreshed). The dev KB doc is fresh (3,924 bytes, page version 2026-09-17,
re-ingested 10-10) and the freshness sentinel
[82959482](https://app.workato.com/recipes/82959482) is Running. So the draft
below stays worded as a status update, not a "fixed" message, because the
employee-facing genie still serves the stale copy until the prod re-ingest
lands. No changes to the body were needed; the underlying state has not
moved since the earlier pass.

---

Hi [requester] Yen,

Thanks for the report, and apologies for the slow turnaround. Where things
stand: we reproduced what [requester] saw and found the cause. The Confluence page
itself was always current; the genie's knowledge layer was holding an older
snapshot of the Flexible Time Off page from an early ingest, and that snapshot
was outranking the live page in search results. That's the "pdf from an
earlier version" you saw.

The fix is built and verified in our build workspace: the stale copy is
removed, the current page is re-ingested, and a check now compares the
knowledge base against the live Confluence page on a weekly schedule so drift
gets caught on its own instead of waiting on a report. The last step is
rolling that out to the live genie, which runs through our standard release
process. I'll confirm here the moment it's live.

Verdict: this was a stale snapshot in the genie's knowledge layer, not a
problem with the Confluence page or the policy itself, and once the rollout
lands the genie will only ever cite the current version.
