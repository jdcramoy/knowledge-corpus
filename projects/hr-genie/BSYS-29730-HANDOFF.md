# BSYS-29730 — HR Genie Annual Performance Review Cycle — HANDOFF (master)

**The resume doc for this epic.** Update THIS file in place; do not create dated copies.
Companion docs in this folder: `BSYS-29730-perf-review-cycle-plan.md` (build plan + probe record), `BSYS-29730-day1-spikes.md`, `BSYS-29730-week1-build.md`.
Repo source of truth: `~/orca/workspaces/workbench/Workday-Development/docs/hr-genie/perf-review-cycle/` (tech plan, PRD digest, kickoff transcript, claude-project-port/ with the full ported instructions + Career_Framework_MASTER_1.csv + review-companion template).
Jira: Epic [BSYS-29730](https://workato.atlassian.net/browse/BSYS-29730) · Stories [BSYS-29912](https://workato.atlassian.net/browse/BSYS-29912) (In Progress), [BSYS-29913](https://workato.atlassian.net/browse/BSYS-29913), [BSYS-29914](https://workato.atlassian.net/browse/BSYS-29914), [BSYS-29915](https://workato.atlassian.net/browse/BSYS-29915), [BSYS-29916](https://workato.atlassian.net/browse/BSYS-29916), [BSYS-29917](https://workato.atlassian.net/browse/BSYS-29917), [BSYS-29918](https://workato.atlassian.net/browse/BSYS-29918) (deployment + manifest thread).

## Status

**All buildable assets are BUILT, TESTED, and WIRED TO THE LIVE HR Genie.** Deadlines: dev-UAT target Nov 21, full scope Dec 1, launch December (re-baselined from the original "first week of November" — stated to the group via the tech plan doc). Remaining work is: 2 small builds (deadline-nudge runner, Sheet-writer config), externally gated items (below), and phase 4 UAT + governance.

## Assets (all in folder "Perf Review Cycle" 35943947, project Agentic | HR Self Service Genie 15643451, DEV workspace "Workato AHQ | AI" 3535597)

- Skill: resolve_nominee — recipe 83296325, skl-Ac6YM3Js-DJoRcT-CD — https://app.workato.com/recipes/83296325 — RUNNING
- Skill: get_competency_evidence — recipe 83296336, skl-Ac6YE3dW-wQDCrK-CD — https://app.workato.com/recipes/83296336 — RUNNING
- Skill: submit_nomination — recipe 83296324, skl-Ac6Y6zFc-wAMLGE-CD — https://app.workato.com/recipes/83296324 — RUNNING
- Skill: get_nine_box — recipe 83296507, skl-Ac6Ykw68-8LzgMt-CD — https://app.workato.com/recipes/83296507 — RUNNING
- Skill: register_review_draft — recipe 83296500, skl-Ac6YhR3m-FdaaLC-CD — https://app.workato.com/recipes/83296500 — RUNNING
- Skill: record_review_check — recipe 83296518, skl-Ac6YnrNH-agJccf-CD — https://app.workato.com/recipes/83296518 — RUNNING
- Skill: lookup_career_framework — recipe 83326123, skl-Ac8C3o6H-eWg3CK-CD — https://app.workato.com/recipes/83326123 — RUNNING
- Recipe: nomination_sheet_reconciler — 83296337 — https://app.workato.com/recipes/83296337 — STOPPED (activates when Jo's sheet id lands)
- Recipe: ninebox_share_watcher — 83296504 — https://app.workato.com/recipes/83296504 — STOPPED (hourly; activates at UAT)
- Tables: Review Cycle Config 164254 — https://app.workato.com/data_tables/46a47f9e-4eb0-4809-9baa-8dd8c31eeb03 · Promotion Nominations 164255 — https://app.workato.com/data_tables/863dc992-4483-4488-81f4-eabf33114360 · Review Check Ledger 164256 — https://app.workato.com/data_tables/f4bdfebf-b9ff-498e-aa52-7772eebb6cbe · Notification Ledger 164257 — https://app.workato.com/data_tables/d0579d9e-eb71-4b00-ab6a-426b5852c2c9 · Career Framework 164711 (9,170 rows) — https://app.workato.com/data_tables/b822ee8f-283b-4cec-9552-f3b7b9529aa5
- KB: Review Cycle Knowledge Base kb-Ac8ksQQs-WKeRm6-CD — https://app.workato.com/knowledge/kb-Ac8ksQQs-WKeRm6-CD — empty, awaiting the People-team writing rubric
- Sub-genies (Josh-approved multi-agent layer): Review Evidence Scout gin-Ac8aCg8x-cEnFtC-CD — https://app.workato.com/genies/gin-Ac8aCg8x-cEnFtC-CD/overview (5 search skills) · Review Checker gin-Ac8aCpDH-ND9CDa-CD — https://app.workato.com/genies/gin-Ac8aCpDH-ND9CDa-CD/overview (adversarial 6-dimension check + lookup skill) — BOTH active, NOT yet exposed as tools (blocked, see below)
- MCP server (empty, awaiting genie-as-tool binding): Review Cycle Sub-Agents MCP mcps-Ac8aEwN4-wEa-CD — https://app.workato.com/ai_hub/mcp/mcps-Ac8aEwN4-wEa-CD/overview
- Live genie: HR Genie gin-AYbxpMha-YenKAJ-CD — https://app.workato.com/genies/gin-AYbxpMha-YenKAJ-CD/overview — THE surface (Josh ruling: no separate genie)
- Living manifest: 371545 — https://app.workato.com/export_manifests/371545 — 94 rows, read-back verified. MIRROR: `manifests/BSYS-29730.manifest.json` in the Workday-Development repo. **NOTE: script-built via create_manifest.py; the 10/24 doctrine supersedes — UI-rebuild via RLM before any ticket cites it.**
- zArchive: 35969315 "Perf Review Cycle deprecated 2026-10-24" — Set B's deprecated chain (83296269, 83296106, 83296142, tables 164149/164249/164250, TEST twin 83296279) — stopped, moved, nothing deleted.

## Verified (with evidence)

- Nomination fail-closed deny (nominee not found) — case citc-Ac6YT66R-8xT4Hm-CD, job j-Ac6YYw6X-oso4NK-CD
- Competency evidence fail-closed (no active cycle) — job j-Ac6YLQta-RcYYQP-CD
- submit_nomination first-submit + sheet-pending receipt — case citc-Ac6YNDgD-JGYKBc-CD, job j-Ac6YWGmR-JspJR4-CD
- Duplicate-retry idempotency (6+ mutated resubmissions → one row, same receipt) — case citc-Ac6YNcWJ-fJ3bYt-CD + jobs j-Ac6YRkTM/j-Ac6YWaAW/j-Ac6YWktb/j-Ac6YXCQQ
- Reconciler force-run green — job j-Ac6YY646-6D3dto-CD (then re-stopped)
- Nine-box: config-not-ready / unknown-label UNKNOWN / denied-viewer / pre-sharing gate — cases citc-Ac6aCD3B, citc-Ac6aCDCX, citc-Ac6aCDJX, citc-Ac6aEWEE; case (d) caught + fixed a sharing-gate variable-staleness security bug
- Quality gate state machine 8/8 mocked — REGISTERED/INVALIDATED/INVALID-reject (j-Ac6Yw8WB-*), PROMPT_MANAGER/SUBMISSION_READY/ESCALATED_PENDING_SEND/remediation (j-Ac6Yx3QR-*)
- Share watcher idle-path force-run green — job j-Ac6Yxwea-mggdB6-CD; ledger write path proven end-to-end
- Leapsome nudge-signal PROBE: per-reviewer status = pending|complete ONLY; "started-not-submitted" = pending + lastModifiedOn present (keys omitted when untouched; cycle launch doesn't stamp) — job j-Ac8BheWE-rErQNM-CD on fixture cycle 6aa81329f26ca85bdc02cc35; probe recipe deleted post-trace
- Skill cutover on live genie: all 7 attached + verified by name; Set B's Nomination Intake detached — via POST /web_api/genies/<gin>/assign_skills.json + remove_skills.json with CSRF (mechanism captured by Builder M)
- MCP attach on live genie: Slack by Workato MCP (20 tools) + Enterprise Data MCP (4/4) + original Workday MCP (23) — all auth success, reads-only

## Blocked (on whom)

- **FY27 templates in Leapsome** — People team; unblocks config seeding (question-ID capture by text match). Asked on Slack C0C7Q62B44B 2026-10-24.
- **"Complete" semantics for a manager review** (submitted vs shared) — Brittany/People team; gates nudge precision + nine-box sharing gate. Asked same thread.
- **Writing rubric** — People team; fills the Review Cycle KB.
- **Quota bands sign-off** — People team; the 0-85/86-100/101+ ranges are draft values.
- **Enrichment privacy pass** — People team; gates real-data reads via the attached MCP servers.
- **Notification dedup** — People team (recommendation sent: HR Genie owns targeted nudges, Leapsome dial-down during cycle).
- **Snowflake grant** — [colleague]/[colleague] (asked 10/22 via Slack MPDM); gates quota attainment reads.
- **calibration_sheet_id + access list** — Jo; gates the sheet writer.
- **Jo's form answers** — question set + competency-submit rule (submit-without-evidence already ruled by Josh; Jo to bless).
- **Platform defect BSYS-29954** — 4 gateways fail genie-attach (16902 Org Chart 503, 3633 Enterprise Data DCR, 16733 Slides, 5953 AIDir empty tool list); filed with evidence. Org Chart was DROPPED (already a skill); AIDir attached-but-empty.
- **Josh decisions pending:** sub-genie MCP-server attach to the live genie (UI: Agent Studio Enterprise skills → mcps-Ac8aEwN4 → add 2 genies as tools — API path is broken, BSYS-29954-adjacent); Leapsome MCP server attach (flagged as possibly redundant); Google Slides (dropped per Josh).

## Next step (execute cold, in order)

1. Check Builder I's live-genie MCP attach completion: `GET /web_api/genies/gin-AYbxpMha-YenKAJ-CD/mcp_server_configs.json` in-page — expect Drive 7, Gmail 16, GWSemantic 3, Confluence 6, Jira 4, Workday End-User 22 + Slack 20 + ED 4. If missing, re-run the attach (Builder I's technique is on the bus thread).
2. Attach the 2 sub-genies as tools on mcps-Ac8aEwN4-wEa-CD via the Agent Studio UI (API broken), then attach that server to the live genie.
3. Build the deadline-nudge runner (small recipe reusing ninebox_share_watcher's pattern + Notification Ledger; nudge rule: managers[] status pending + lastModifiedOn present; dates from Review Cycle Config).
4. When Jo's sheet id lands: set `calibration_sheet_id` row in Review Cycle Config, start the reconciler.
5. When FY27 templates land: capture question IDs by text match → seed Review Cycle Config → the whole happy path goes live-verifiable.
6. UI-rebuild the manifest via RLM per the 10/24 doctrine before the deployment story cites it.
7. Phase 4: UAT matrix (in the tech plan) + tester cohort (Justin/Brittany own the list; include non-US + CS) + red-team Tier 1 + promotion batch.
8. Refresh the architecture maps (hr-genie/architecture/system-map.mmd is now STALE — it predates the whole review-cycle layer); run the arch-diagram skill before closing phase 4.

## Gotchas that cost this build (do not re-learn)

- AIRO `genie_update(skills_to_add=...)` returns success but silently does NOT attach — use the UI or POST /web_api/genies/<gin>/assign_skills.json with CSRF.
- `wt manifests update` strips handle/provider_id from agentic_skill rows — asset additions require create-new + delete-old.
- Docs (GWS semantic): batchUpdate trims payload-edge whitespace — newline-only inserts 400, newline-only replaces vanish; sandwich newlines between visible chars.
- Data-table `equals` = case-insensitive CONTAINS — enforce exactness in snippets.
- Okta sign-in via automation: the identifier field accumulates duplicate typing (verify 23 chars exactly); the submit control is INPUT[type=submit]; FastPass can't run in Orca; push + josh-alert.sh works.
- Skills/KBs/genies cannot change folder via API (KB/genie 422) — create in the right folder the first time.
- The CSV "20,708 lines" = 9,170 real records (embedded newlines in descriptions).
