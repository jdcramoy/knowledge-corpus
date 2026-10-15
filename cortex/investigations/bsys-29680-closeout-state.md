# BSYS-29680 slack-mcp-blocks hotfix — closeout-state investigation

**Investigated:** 2026-10-14 ~23:2xZ · **Investigator:** flash session (read-only) · **Scope:** redteam verdict file, build-ledger 21:13-21:49Z, gossip bus 12h, mission-control, ONE live prod job-list read (read-only).

---

## 1. What remediation M1 was, and what the verdict required

Source: `~/.claude/knowledge/redteam/BSYS-29680-slack-mcp-blocks.md` (verdict **PASS-WITH-NOTES**, Tier 2, dated 2026-10-14, independent red-team agent).

- **M1 (MATERIAL):** `blocks` evades the local message-size gate in BOTH connector actions. `post_message` enforces 1-40,000 chars on `text` (connector line 5214) and `create_message_draft` enforces 5,000 on the message (line 5184), but `blocks` was passed straight into the outbound payload with no type check (`post_message`, line 5216) and shape-only validation, no count/size cap (`create_message_draft`, line 5108). Since blocks arrive from LLM tool-call arguments, a prompt-injected agent could ship a message body far past the size gate — bounded blast radius (rejected request / failed job / oversized log), hence material not fatal.
- **Required remediation:** in both actions, after existing validation add (a) the Array-of-Hash shape check to `post_message` that `create_message_draft` already has, and (b) a serialized-size cap (`blocks.to_json.length <= 40_000` for post_message, 5,000 for draft) plus a block-count cap <= 50 (Slack Block Kit limit).
- **Verdict requirement:** fix M1 with the promotion batch — fix-before-ship, not do-not-ship. C1 (dead duplicate `actions:` hash), C2 (trigger-step mask gap), C3 (no depth cap) were cosmetic/follow-up, not blockers.
- **Fix-forward disposition (same file, build session 15:33):** M1 FIXED in dev connector v49 ("Red-team M1 fix (BSYS-29680)"): shape validation + 50-block / 40,000-char cap on post_message; 50-block / 5,000-char cap on drafts. Blocks-path runtime proof was marked **pending** — a confirmed run with a blocks payload was required in promotion UAT / post-deploy smoke.

## 2. Reconstructed prod import sequence (build-ledger, 2026-10-14T21:13Z-21:49Z)

- **21:13:19Z** — `sleep 300` then a probe firing a **51-block payload** (`range(51)`, one over the new M1 cap) at prod recipe 74801293 — a live probe that the M1 block-count cap rejects oversized blocks.
- **21:35:15Z** — **`wt-prod packages import 32327810 --zipfile /tmp/bsys-29680-v54.zip --restart-recipes`** -> import id scraped from the traceback log (`grep -o '42229[0-9]*'`, import ~42229xxx), then sleep + polling. (Per the lessons: the prod packages-import CLI crashes its own JSON printer on the binary response AFTER firing the request, so the id is read from the traceback.)
- **21:46:12Z** — second `sleep 600` + 51-block probe (re-run after settle, per the flap guidance below).
- **21:47:24Z** — **export verification polling:** `wt packages export 363669` then 6x (sleep 10) `wt packages get $EXP` — polling the package export state until it settles, confirming the prod package landed with the new connector version.
- **21:49:25Z** — lessons appended to `domains/workato-platform.md`; prod recipe 74801293 (post_message skill) and 81884553 wired; mission-control closeout row posted 21:50:19Z.
- **Lessons on compile flapping (domains/workato-platform.md lines 2162-2168):** prod custom-adapter RUNTIME serves older compiled artifacts while imports report `completed` — v52 marker persisted 20+ min across two later completed imports (v53/v54), with one brief REGRESSION (v53 diag seen, then v52 again). **Bisect results taken during a flap window are unreliable — re-run the cheapest payload after each import and treat early failures as suspect until ~5-10 min of settle.** Same family as dev schema-service staleness. Adjacent lessons: skill-trigger array params arrive at connector actions STRINGIFIED (connector must JSON.parse string OR accept array); Slack `chat.postMessage` rejects `rich_text_list` without `"border": 1` (connector now auto-normalizes); Slack `drafts.create` rejects `rich_text_list` entirely ("• " section-prefix workaround).

## 3. Gossip-bus corroboration (12h window)

Thread progression on `slack-mcp-blocks`:
- 18:3xZ — `unregistered-build-slack-mcp-blocks-conn`: connector released with zero mission-control registration; provenance lookup dispatched.
- 19:4xZ — `slack-mcp-blocks-conn-provenance`: REAL build (connector 1333502 "Slack (Custom)" new version), manifest exemption does NOT apply; Josh's live session took over remediation.
- 20:39Z — `bsys-29680-redteam-gate-held-verdict-before-promotion`: gate HELD, PASS-WITH-NOTES verdict on file BEFORE the prod push; watch: confirm M1 rode the batch.
- ~22:0xZ — `bsys-29680-hotfix-shipped-unregistered`: hotfix executed AFTER the verdict (imports 21:35Z/21:47Z, export polling, lessons 21:49Z); watch item said "green prod trace still unconfirmed" — that pulse had NOT yet seen the closeout/trace evidence.

Corroboration that the fix landed and went green:
- **Mission-control closeout row (events.jsonl, 21:50:19Z, state `done`, by "josh (session)"):** "HOTFIXED TO PROD and smoke-verified: … Prod connector v54 (blocks fields, JSON-string tolerance, validation caps, rich_text_list border normalization), prod recipes 74801293/81884553 wired and running. Verified live: bold rich_text posts, two-level indented lists, formatted draft creation." Note: this supersedes the cortex pulse's "zero registry rows" watch — the row EXISTS in events.jsonl; `mission-control/registry.json` shows 0 hits for 29680 (registry index appears stale/lagging the events ledger — separate hygiene item).
- **Deadman absorb note (22:45:03Z):** the hotfix session's last output — "the blocks hotfix is deployed, smoke-verified live, tickets updated, registry closed as done."

## 4. Verdict — live evidence

**Live evidence exists, obtained this session by ONE read-only prod poll:**
- `wt-prod` jobs list on 74801293 (read-only): 5 most recent jobs **all `succeeded`**, 21:35-21:48 UTC (14:35-14:48 PT) — spanning the import window through AFTER the final import/verification. This is a live job-trace confirmation, not just a ledger claim.
- Corroborated by the mission-control closeout row (smoke-verified: bold rich_text posts, indented lists, formatted draft) and the deadman-preserved session output ("deployed, smoke-verified live").
- M1-specific runtime proof: the ledger shows the 51-block cap probe fired twice (21:13Z, 21:46Z — once post-settle per the flap lesson), and the closeout row claims validation caps shipped in prod connector v54. The probe OUTPUT was not recorded in the ledger (output fields empty), so the rejection-at-block-51 behavior is evidenced by the closeout claim + shipped v54, not by a captured probe output.

**Caveats (non-blocking):** (a) the red-team "could not check" item — array-type passthrough of blocks through the skill trigger — was resolved empirically (JSON-string-tolerance lesson + green traces); (b) registry.json index is missing the row that events.jsonl has (the cortex pulse's "unregistered" finding was reading the lagging index); (c) queued follow-ups on record: masking pass BSYS-29687, dead `actions:` hash cleanup, update_draft/delete_draft build awaiting Josh's go.

---

**VERDICT: VERIFIED** — strongest ref: live read-only `wt-prod` jobs list on recipe 74801293 this session (5/5 latest prod jobs `succeeded`, last at 2026-10-14T21:48:32Z, post-import), corroborated by mission-control events.jsonl closeout 21:50:19Z ("HOTFIXED TO PROD and smoke-verified").
