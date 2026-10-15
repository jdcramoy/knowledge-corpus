# Stale-registry census — 2026-10-15 (fold 06:22:29Z)

**VERDICT: NOT AN EXPLOSION OF WORK — AN EXPLOSION OF DEADMAN AUTO-ROWS.**
Headline 122 stale non-done is real, but 79 of 122 (65%) are `dropped-<session>` rows the
deadman sweep auto-registered. True stale human-work count is **43** (24% of 177 non-done),
up modestly from the 2026-10-14 08:12Z count of 41. needs-josh is the only state that grew
in substance: 32 → 53 headline, 33 of them genuinely stale real work.

## Sources

- `$HOME/.claude/knowledge/mission-control/registry.json` (250 workstreams, folded_at 2026-10-15T06:22:29Z)
- Read-only census; registry.json and board.html untouched.

## The math

| measure | 2026-10-14 08:12Z | 2026-10-15 06:22Z | Δ |
|---|---|---|---|
| total workstreams | — | 250 | — |
| non-done | — | 177 (122 in-flight / 53 needs-josh / 2 blocked) | — |
| stale non-done (>24h) | 41 | 122 | +81 |
| **stale real work (excl. dropped-*)** | **~41** | **43** | **+2** |
| needs-josh | 32 | 53 headline / **33 stale** | real growth is the stale 33 |
| agent-auto stale rows (deadman) | — | 79 | the entire "explosion" |

## (a) Agent-auto-registered rows: 79 of 122

Every one is `dropped-<uuid8>-<suffix>` in-flight, `by = deadman-sweep`, age 25–32h, all
marked `state: in-flight` with `what: "DROPPED SESSION auto-absorb (deadman): N turns; …"`.
These are dead sessions the sweep absorbed; they carry no Josh decision and pollute the
stale count. Median 32h — they age out of nothing because nothing ever closes them.
The 2026-10-15T05:59 session-start sweep reported **74 dropped sessions in 48h** — the
absorb pipeline outruns closeout.

## (b) Real stale human-work rows: 43

**5 OLDEST (with what they need):**

1. **bsys-28296-marketo-history** — blocked, 81.4h, BSYS-28296 (Marketo get_lead_activities
   incomplete history). NEEDS: Marketing Ops quota headroom confirmation before kickoff.
2. **hr-genie-workday-mcp** — needs-josh, 77.4h, BSYS-26810/26816/27818. NEEDS: Josh to
   authorize remaining fixes (VUA flip + description fix on tool 254984, tax-elections tool
   registration + first live tests) and Workday tenant security grants for the contact-info
   write path.
3. **jira-autotriage-hr-genie** — in-flight, 77.4h, BSYS-28309/28310/28311. NEEDS: Josh
   decides when to run the blocked UAT cases (live Job Change event, live LoA manager
   decisions) and whether to attach the two comp skills to the End-User MCP server.
4. **btsup-service-desk** — needs-josh, 77.4h, BTSUP-78227 (Slack app not triggering Genie
   jobs). NEEDS: Josh's go on the Ops Genie fix in the customer workspace, prod KB re-ingest
   for the FTO policy, confirmation of 4 staged customer replies.
5. **ai-roi-framework** — needs-josh, 75.8h. NEEDS: Josh to approve per-work-block value
   theses and confirm the loaded engineer-day rate (600/day default).

(Three rows tie at 77.4h; all are HR-Genie/BTSUP cluster work. Next runners-up at 75.7–75.0h:
stale-jira-review + jira-stale-review — a DUPLICATE PAIR for the same BSYS-28800–28803
transition — and workato-watchdog's two /triage connection-hygiene findings.)

**Shape of the real 43:** 33 needs-josh (every one carries a concrete needs sentence — the
closeout discipline holds), 8 in-flight, 2 blocked. Cluster themes: HR Genie/Workday UAT
gating (4 rows), GWS-semantic gateway/catalog (3), estate review verdicts (3), manifest
hygiene (3), harness infrastructure decisions (6+). At least one duplicate pair
(jira-stale-review / stale-jira-review) and a twin-row BSYS-28296 (history + mcp).

## True stale-work ratio

- Headline: 122/177 non-done = **69% stale** — misleading.
- **True: 43/177 = 24.3%** of non-done workstreams are genuinely stale human work.
- needs-josh specifically: 33 stale of 53 = 62% of Josh's decision queue has sat >24h —
  this is the real backlog, and it is a queue of Josh decisions, not agent noise.

## Nothing unverified beyond these bounds

Counts computed directly from registry.json as folded at 06:22:29Z; no live re-folding was
performed and no cross-check against board.html (read-only mandate). The 2026-10-14
41/32 baseline is taken from the fold evidence in the dispatch, not re-derived.
