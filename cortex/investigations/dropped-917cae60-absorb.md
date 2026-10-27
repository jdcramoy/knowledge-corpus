# Dropped-session absorb: 917cae60 (Google Semantic MCP pre-demo UAT, 2026-10-13)

- **Session:** `917cae60-1363-457b-a45f-2f28c963e157.jsonl` — 670 turns, 2026-10-13 19:15→23:38 UTC (~4.4h), $71.09, model fireworks/glm-5.3-flash.
- **Verdict up front:** this session was NOT actually dropped mid-work. It ended cleanly at 23:38 UTC with a complete final answer, and it logged **six** mission-control closeout rows (19:28 → 23:35, workstream `google-semantic-mcp`, visible in `mission-control/events.jsonl`). The dropped-session deadman flag is a false positive — the folded `registry.json` does not carry those rows, which is likely why the sweep saw nothing. Detector/fold worth tuning.

## 1. What the session actually did/built

Context: final UAT + fix pass of the **Google Workspace Semantic MCP** server (`mcps-AbYzPeKh-QHG-CD`, 21123.apim) the evening before Josh's BT Monthly Lookback demo. Code freeze requested; session stayed inside it except for the named fixes.

| Asset | ID | Action |
|---|---|---|
| workspace_capabilities quickstart recipe | **82272066** | pulled, step-9 quickstart_json rewritten (stale drafts.create worked-mutation → typed body shape + self-heal/checksum line), **pushed 3×** (sessions `bsys-29643-quickstart`, `-v2`) |
| `workspace_semantic_registry` data table | 147343 | ~20 row edits: identity projection on **7/7 quickAdd rows** (truncated 40-path default_projection was the root cause, BSYS-29625 class); rfc822 content_envelope + typed slots grafted onto **6 drafts.create rows**; freebusy typed operation_list + calendars-only projection on **6/6 rows**; getBatchGet person projection 4/4; listDirectoryPeople sources+read_mask defaults 4/4 |
| `workspace_semantic_request_examples` | — | updated stale drafts.create golden example (7f413eb0); **created** updateContact etag example (396fbac1); created freebusy golden example |
| Sync Google Workspace Discovery Catalog | 82272892 | read-only — mapped as the hourly materializer (regenerates index FROM registry; registry edits ride through) |
| Health-monitor recipe | 82273312 | 8 job_gets + job_lists — hourly runs all green |
| Living export manifest | manifest 362789 inspected; `BSYS-29643.manifest.json` | created via the manifest path, mirrored to repo, **UI + commit verified** |
| Jira | **BSYS-29643** (created, 4/4 fixes, closed Done), **BSYS-29644** (created, quickAdd+freebusy, closed Done), **BSYS-29651** (created, 3 deferred residuals, Backlog) | |
| Memory / repo | session-state memory file edited 8×; repo commits `19dc6f9`, `608c304`, `7be70e1`, `cbc76b0` | |
| Subagent | `a5b22b7e72bcbc0da` 'Aggressive cross-service MCP UAT' — 70 probes across all 7 services | |

## 2. Claims vs. in-transcript evidence

| Claim | Evidenced? | Notes |
|---|---|---|
| Pre-demo UAT 23/24 green, zero residue (19:28) | ✅ | REGISTRY_CURRENT canaries on all 7 services, checksum efe173f9, receipts for the 9-call write lifecycle |
| BSYS-29643: 4/4 fixes landed, retest first-try green | ✅ | live plan→confirm→MUTATION_COMMITTED traces in-transcript; corrected example served back from the retest commit itself |
| quickAdd root cause = alphabetically-truncated 40-path default_projection (all 7 rows) | ✅ | dumped row shown; fix live-proven with full event identity (id e99jgffe…) |
| freebusy fix (typed operation_list at policy top level; nesting inside selection_contract is SILENTLY IGNORED) | ✅ | took 3 attempts, reverted clean per stop rule, then landed 6/6 with populated busy intervals in job traces |
| Checksum rotation law (registry edits rotate checksum next materialization, ~90 min; fail-closed read gate rejects stale) | ✅ | observed twice in-transcript (efe173f9→14ccd21e); quickstart now carries a self-heal line |
| Aggressive 70-probe UAT: 4 of 7 findings fixed same-session, 3 filed BSYS-29651 | ✅ | subagent output + commit cbc76b0 |
| Persistence/self-healing: NO scheduled writer can overwrite the layer | ✅ | swept ~700 recipes for writers of the 3 semantic tables; connector code of 82272892 read; edits survived 3 hourly rotations (21:25/22:25/23:25) byte-identical; final serving canary green on current checksum |
| 'Paper trail: BSYS-29651, BSYS-29644 (Closed)' + verdict comment on BSYS-29643 | ⚠️ **PARTIAL** | **The BSYS-29643 verdict comment NEVER landed.** 4 addCommentToJiraIssue attempts all failed (2× `commentId: undefined` Not-Found, 2× InputValidationError); the session gave up without re-verifying. Verdict survives only in the ticket **description**. Live check today: BSYS-29643 has **0 comments**; BSYS-29644's comment landed fine; BSYS-29651 also 0 comments (never attempted) |
| 'Zero residue' cleanup after write probes | ✅ | verified 404s/empty reads in-transcript; never sent email, never touched real content |

## 3. Unfinished work / open decisions

1. **BSYS-29651 sits in Backlog with 3 root-caused, deliberately-deferred residuals** (verified still open today): docs.documents.get tabs-mode guaranteed 400 (needs conditional-fieldmask support in the projection layer — a real layer enhancement, not a data-row fix); calendar.events.get serves stale cache 3+ min after events.delete; opaque (unmapped 404) error on delete-of-deleted. Nothing scheduled them post-demo.
2. **BSYS-29643 verdict comment missing** — if Josh's standard is verdict-on-record as a comment, it needs a one-shot backfill; the description carries it meanwhile.
3. **Demo start time never resolved in-session:** at 23:35 UTC (7:34 PM ET) the session flagged the Monthly Lookback event's etag had changed and it showed 5:30–6:45 PM ET — a window that had already passed vs. Josh's 'we have 2 hours' framing earlier. Genuine timezone/etag anomaly, never answered in-transcript (moot now, but worth knowing which was right).
4. Two latent doc divergences (threads.list, slides.get) logged as zero-behavior-impact — no ticket; easy follow-up if the class sweep is revisited.

## 4. What Josh needs to see

- **Nothing is broken or dangling on the platform.** All fixes live-verified, monitor green, freeze honored, manifest + commits in place. The scary headline is the false-positive dropped flag, not the work.
- **The one real claim-evidence gap is the BSYS-29643 comment** (see above) — 4 failed attempts, no re-check. Formatting rule (re-fetch after posting) was the standing order and is exactly what would have caught it.
- **BSYS-29651 needs a post-demo decision** on the conditional-fieldmask layer work — it's the only residual that can't be closed with data rows.
- **Detector tuning:** the deadman sweep flagged a session that had 6 closeout rows in events.jsonl but nothing in the folded registry.json — check whether the fold window/fold logic is eating same-day rows (the absorb-note for this very session landed in the fold, so it's not a write failure).
- Governance note (informational): all same-day serving-stack edits were dev-workspace (3535597) data-row/recipe changes ahead of the BSYS-29592 prod DR (handed to Final Tech Review that morning) — no red-team gate applies to dev fixes, and no prod write occurred in this session.
