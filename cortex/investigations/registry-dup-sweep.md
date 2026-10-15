# Registry duplicate sweep — mission-control/registry.json (read-only)

- Swept: 2026-10-13, registry `folded_at 2026-10-13T18:31:54Z`, 94 rows; events.jsonl 273 events.
- Method: full-row sweep for (a) identical `(jira_title, project)`, (b) shared Jira keys,
  (c) ts pairs within 60s, (d) near-identical `what` first-120-chars, (e) identical `needs`
  text, (f) same workstream slug; then events.jsonl clustered by `by` + 5-min windows to find
  closeout bursts that wrote a second row for one session.
- Read-only: nothing in the registry or events was changed.

## Duplicate groups (action needed)

| # | Dup group | Rows involved | Keep | Evidence |
|---|-----------|---------------|------|----------|
| A | **Confirmed pair (Josh-flagged).** One session's read-only staleness review closed out twice under two slugs, 1s apart, same project `jira-autotriage`. Two different ticket-set claims (18 vs 12 tickets) = the session re-ran the review wider and re-closed-out instead of updating. | `stale-jira-review` ts 2026-10-12T02:43:11Z (jira_title "Stale-status review of 18 open Workato-site tickets (read-only)", needs-josh) **+** `jira-stale-review` ts 2026-10-12T02:43:12Z (no jira_title, needs-josh) | **Keep `stale-jira-review`** (the one with jira_title). | Events show both closeouts 1s apart, `by josh (session)`. |
| B | **Confirmed dup via events.jsonl.** BSYS-29585 discovery-catalog sync failure tracked under two workstream slugs and two project spellings. Earlier row = bug filed, needs-josh (build approval pending); 80 min later same arc closed out as done under a new slug, superseding the first row's ask. | `gws-semantic-catalog-sync` ts 2026-10-13T03:20:19Z (project "Google Workspace Semantic MCP", state needs-josh) **+** `google-workspace-semantic-mcp` ts 2026-10-13T04:41:59Z (project "google-workspace-semantic-mcp", state done) | **Keep `google-workspace-semantic-mcp`** (state=done, current; has jira_title). Fold row 18's two facts in first: autopsy at `artifacts/autopsy-discovery-catalog-82272892.md`; fix plan was "reconcile-don't-abort". | events.jsonl shows three closeouts for this arc (two under gws-semantic-catalog-sync 02:36/03:20, one under google-workspace-semantic-mcp 04:41) — the fold collapsed the same-slug pair but not the cross-slug pair. |
| C | **State-conflict pair (not a text dup — a stale-done hazard).** `manifest-review` closed out state=done at 17:47; the 23:33 note explicitly corrects it: "only the VERDICT-DELIVERY is done... the workstream is not done - builder must fix the 5 blocking items." Board currently shows a false `done` for BSYS-29510. | `manifest-review` ts 2026-10-12T17:47:33Z (closeout, state **done**) **+** `manifest-review-bsys-29510` ts 2026-10-12T23:33:53Z (note, state in-flight) | **Keep both, but make `manifest-review-bsys-29510` the governing state.** Fix `manifest-review`'s state done -> in-flight (or annotate) so the board stops showing a closed BSYS-29510 manifest review while 5 blocking items are open. | The note row self-declares the correction ("CORRECTION to my closeout a moment ago"). |

## Checked and NOT duplicates (do not merge)

| Rows | Why distinct |
|------|--------------|
| BSYS-28296 x 4 rows (`bsys-28296-marketo-history` blocked plan-state 10-11; `bsys-28296-marketo-mcp` manifest rebuild in-flight; `jira-autotriage-verify` verify-pass done; `harness-manifest-standing-order` manifest-guard hook done) | Four different sessions doing four different facets (plan / manifest / verify / hook hardening). Shared ticket only. |
| `stale-jira-queue-sweep` (02:46:58) vs pair A | Different activity: 92-ticket sweep with 43 transitions executed by 7 evidence agents - not the read-only review. Keep. |
| `jira-sweep-1012` + `gslides-mcp-prod-incident` (BSYS-29458, 26s apart) | Complementary halves of one incident resolution (execution audit + outage resolution), both done, both current. Keep both. |
| 10-13 10:09 cluster (`ops-visibility`, `mcp-registry-tool-call-stats`, `harness-fix-fleet-1009`, `hr-genie-dreamer-1010`) and 10-12 01:02 cluster | Parallel fleet lanes closing out simultaneously; distinct workstreams, no shared ticket or text. |
| Estate-monitor event-level re-closeouts (BSYS-29565/29589/29595/29600 pairs) | Already collapsed by the fold - only one row per slug survives in the registry. Events-only phenomenon, no registry action. |

## Root cause + prevention for Josh

1. **Mechanism:** the fold dedupes by workstream slug, so a session that closes out the same
   work under a second slug produces a permanent registry pair (groups A, B). Two fixes worth
   a build: (a) fold should also key on shared Jira key + near-ts, (b) closeout writer should
   reject a second closeout from the same `by` within N minutes unless the workstream matches.
2. **GWS Semantic MCP slug fragmentation (adjacent finding, drives group B):** one program is
   spread across 9 workstream slugs (`gws-semantic-*`, `google-semantic-mcp`, `gw-semantic-mcp`,
   `google-workspace-semantic-mcp`, `gws-semantic-mcp`) and 3+ project spellings
   ("Google Semantic MCP" / "Google Workspace Semantic MCP" / "google-workspace-semantic-mcp").
   Recommend a canonical slug + project name and a one-time alias map for the fold.
3. **Group C is the stale-done class Josh has flagged before:** a closeout says done, a later
   correction note never flips the original row's state. Recommend mission-control.py treat
   `note` events that name a workstream as state-overriding.

## Merge instructions (Josh to approve - this sweep changed nothing)

- **Group A:** merge `jira-stale-review`'s two unique facts into `stale-jira-review` (its 12-ticket
  scope note incl. BSYS-28420 Backlog->In Progress ask), then delete the `jira-stale-review` row.
- **Group B:** append to `google-workspace-semantic-mcp`'s `what`: "supersedes gws-semantic-catalog-sync
  row; autopsy at artifacts/autopsy-discovery-catalog-82272892.md", then delete the
  `gws-semantic-catalog-sync` row.
- **Group C:** flip `manifest-review` state to in-flight and keep the note row as governing.

*Nothing unverified beyond the read itself: all rows quoted above were read live from
registry.json and events.jsonl this sweep; no Jira, Workato, or file state outside the two
files was checked.*
