# BSYS-29680 slack-mcp blocks hotfix — PROD TRACE verification (fresh read-only)

**Investigated:** 2026-10-15 (session ~02:1xZ Oct 16 PT window) · **Investigator:** headless flash session (reads only)
**Method:** `wt --profile josh-prod` (Production workspace 3535598) — jobs list, recipes get, custom_connectors list + code fetch. **No writes, no starts, no stops, no pushes.** Note: the prod CLI profile is named `josh-prod` in `~/.workato/profiles` ("wt-prod" in the ledger shorthand = this profile).

---

## 1. Prod package/recipe state — import landed clean, jobs green

**Connector (prod):** "Slack (Custom)", id **1336152**, name `slack_custom__connector_3535598_1787024780`. `latest_released_version = 10`. Prod release chain, 2026-10-14 (times PT / UTC-7):

| v | released | note |
|---|---|---|
| 5 | 13:37 (20:37Z) | Red-team M1 fix: blocks shape validation + caps (50 blocks, 40k post / 5k draft serialized) |
| 6 | 13:43 (20:43Z) | Smoke fix: accept blocks as JSON string or array at the action boundary |
| 7 | 13:51 (20:51Z) | auto-set border=1 on rich_text_list elements |
| 8 | 13:58 (20:58Z) | diagnostic marker in blocks over-50 error (temporary) |
| 9 | 14:01 (21:01Z) | temporary border-normalization diagnostic |
| 10 | 14:02 (21:02Z) | "BSYS-29680 final: blocks border normalization, JSON-string tolerance, validation caps; diagnostic removed" |

All six hotfix releases (v5→v10) landed 2026-10-14 13:37–14:02 PT — i.e., BEFORE the 21:35Z/21:47Z package imports; the imports carried the recipes/package wiring after the connector releases were already out.

**Recipes (prod), both `running: true`:**
- `post_message` 74801293 — 221 succeeded / **0 failed** lifetime.
- `create_message_draft` 81884553 — 107 succeeded / **0 failed** lifetime.

**Post-import green traces (live job-ledger read this session):**
- 74801293: **18 jobs since the import window opened (2026-10-14T14:30 PT), all `succeeded`; 16 jobs since the final import (14:47 PT = 21:47Z), all `succeeded`**, continuing through the latest job completed 2026-10-15T18:50:53 PT — the recipe ran green all day today, ~24h after the import.
- 81884553: **10 jobs since the final import, all `succeeded`**, latest 2026-10-15T09:57:26 PT.
- Zero non-succeeded jobs in any window on either recipe.

Package records: the export id cited in the ledger (363669) no longer resolves via `GET /api/packages/:id` (404 — export records are ephemeral), and no package-listing endpoint exists; the connector version chain + job traces above independently prove the landing without it.

## 2. M1 fix — verified present in BOTH actions in the released prod code

Source: `GET /api/custom_connectors/1336152/code` (prod, live read this session; 5,848 lines). Live `actions:` block = second hash (line 3009+). Verbatim findings:

**`post_message` (lines 5231–5248)** — the full M1 remediation exactly as the verdict prescribed:
- JSON-string tolerance: `blocks_value = JSON.parse(blocks_value) if blocks_value.is_a?(String)` inside `begin/rescue JSON::ParserError` → clean `error(...)`.
- Shape check (new in M1): `unless blocks_value.is_a?(Array) && blocks_value.all? { |e| e.is_a?(Hash) }` → error.
- **50-block cap**: `unless blocks_value.length <= 50` (line 5239).
- **40,000-char serialized cap**: `unless blocks_value.to_json.length <= 40_000` (line 5240).
- rich_text_list `border=1` auto-normalization (lines 5241–5247); `payload[:blocks] = blocks_value` into `chat.postMessage`.

**`create_message_draft` (lines 5107–5124)** — same tolerance + shape check, plus:
- **50-block cap** (line 5115) and **5,000-char serialized cap** (line 5116, mirroring its 5,000 text cap).
- border=1 normalization; sends `blocks: blocks.to_json` form-encoded.

**Verdict item closed:** M1 (blocks evading the message-size gate) is remediated in the released prod code in both actions, with the exact shape check + caps the red-team prescribed. The runtime "could not check" item (array-vs-string passthrough through the skill trigger) is also addressed in code (JSON-string tolerance in both actions) and empirically by the green traces.

## 3. Blemishes observed (cosmetic, on record — no action taken, read-only session)

1. **v10 release note inaccuracy:** v10 says "diagnostic removed," and the v9 border diagnostic IS gone — but the v8 error-text marker survived into released v10: line 5239 reads `error("Message blocks exceed the maximum of 50 blocks [marker-v52] [BSYS-29680]")`. Harmless (error text on the over-50 rejection path only), but the note overstates the cleanup. Candidate for the next connector-touching pass, alongside:
2. **C1 dead code persists in prod:** duplicate top-level `actions:` keys at lines 108 (dead) and 3009 (live); the dead draft branch (lines 2189–2210) has no blocks caps — dead-code hazard unchanged, matching the red-team C1 follow-up (cleanup still owed).
3. **Version-number reconciliation:** the mission-control closeout row (21:50:19Z) said "Prod connector v54" — that is the DEV connector's version ledger; the PROD connector's own chain tops out at **v10**. No substance issue (v10 carries the full fix, verified above), but future sessions should cite v10 for prod.

## VERDICT: VERIFIED — import landed clean, fix confirmed in prod code, jobs green

Strongest evidence, all read live this session: (a) prod connector 1336152 `latest_released_version=10` carrying the complete M1 remediation in both actions (`/code` fetch, 5,848 lines); (b) 26 post-final-import jobs across the two recipes, 100% `succeeded`, zero failures lifetime, runs continuing ~24h post-import.
