# BSYS-29383 — Auto-deploy memory failures (BT AHQ workspace: dev 800219, prod 800229)

Filed: 2026-10-07. Status: full-stack trace COMPLETE 2026-10-16, fix plan v2 posted to Jira,
awaiting Josh's build authorization. Size 5 points.
Ticket: https://workato.atlassian.net/browse/BSYS-29383 (High, In Progress)

## Root cause (verified 2026-10-16 from live reads — supersedes the 10-15 manifest-unzip theory)

- **The memory hog is `[DEPLOY] LF | Build recipes table`** (prod 3792740, dev twin 3383902):
  lists ALL recipes in the workspace via the Workato connector (each list item carries the full
  recipe DSL in `code`), accumulates every page into ONE in-memory list, upserts into
  `DEPLOYMENT.RECIPES` (Snowflake). Jasper's `bytesize >= 16000000 → nil` guard only protects the
  Snowflake 16MB column limit — the payload still sits in job memory.
- **Deploy path**: 3792728 Deploy Manifest → 3792733 Get Folder ID → 3792735 Get Resource Path →
  3792734 Get Recipe Folder Path. On a lookup MISS, 3792734 fires Build folders + Build recipes
  table INLINE and waits — the deploy job dies there.
- **Daily path**: 3792738 Build deployment tables daily → per workspace 3792742 Run deployment
  setup workflow → Build folders/connections/recipes async. ~85 rebuilds/day across workspaces,
  ~7 min each.
- **Failure history**: memory failures ramp continuously since 2026-07-20 (1–2/day Jul-Aug →
  2–7/day Sep → peak 11 on Sep 23 → sustained 2–8/day Oct). Growth signature: unchanged recipe,
  workspace code volume creeping past the job memory ceiling. The ticket's "started 2026-10-06"
  and "manifest size" theories are both wrong.
- **Caller attribution (100-job sample)**: 979 from daily setup, 21 from deploy-path misses —
  misses are rare; the rebuild is routine daily maintenance (decoupling the inline rebuild is an
  optimization, NOT urgent).

## Sen Rong guidance (2026-10-15, verified)

- Product (SR): drop the `code` field from the recipes-table build — Jasper added it for
  Snowflake code-based dependency search, superseded by WDT; code is recoverable from GitHub.
- Consumer check DONE and clean: no recipe in the 23-recipe prod deploy family reads `code` back
  (all SQL touches only id/name/path/folder_id/workspace_user_id); `[RTE] Workspace Entity
  Events` topic (16265) messages carry no code. Residual gap: non-Workato Snowflake consumers —
  close with an ACCESS_HISTORY/QUERY_HISTORY scan (BT data team).

## Fix plan v2 (posted to Jira 2026-10-16, dissenter-fact-checked SHIP-WITH-CHANGES)

1. Step 0: verify code actually flows — inspect one 3792740 job trace (Orca browser) for code
   bytes in the List Recipes output; replaces SR's ~90% estimate with a measurement.
2. Dev twin 3383902 first: strip code at (a) page-item mapping before list accumulation,
   (b) the upsert row. Snowflake column stays (no ALTER in scope). Dev 5,379 recipes = 2× stress.
3. Measure peak memory before/after in dev; if raw page responses stay resident in step-output
   retention, the accumulation pattern itself needs rework.
4. Snowflake consumer scan (BT data team) for DEPLOYMENT.RECIPES.CODE, 90–180 days.
5. Retry envelope for the transient 502, placed where it actually surfaces (verify at trace time).
6. One autopsy of the 30-job "Recipe function execution error" class before closing — the memory
   fix won't cure that class; the minority manifest-unzip path may live there.
7. Prod promotion via DR flow: red-team Tier 2 first, manifest at build start, per-action prod
   confirmation.

## Dev build (2026-10-16 — DONE, verified; awaiting Josh for prod promotion)

- **Manifest first (standing order):** `BSYS-29383 — auto-deploy memory fix (dev)`, id
  **366061**, anchored at folder 1604941 — read-back verified (5 rows: recipe 3383902 +
  topic 16251 + custom_adapter 186326 + 2 connections). Mirror:
  `bt-auto-deploy/manifests/BSYS-29383.manifest.json`. Script amendments: `topic` added to
  FOLDERLESS_TYPES; `* Connections` root exempted from the multi-project guard (both are
  structural Workato facts — every manifest with connection deps trips the old guard).
- **Step 0 DONE — code measured, not estimated:** live trace of prod 3792740 (job
  j-AbxnoEYM-tm6xXX-CD): connector page = 59 recipes / 167KB, **code = 43.2%** of every page
  (SR guessed ~90%). Item also carries dead `parameters_schema`/`config`/`parameters`.
- **Edit applied via `PUT /api/recipes/3383902` with `{"code": <dsl>}`** (works with the
  workspace JWT; recipe was stopped). Diff verdict: code removed at exactly steps
  2 (list schema), 7 (insert_to_list_batch mapping), 21 (upsert rows — 16MB guard gone with
  it); retained keys byte-identical; step 13 sample restored without code. Versions 40–43.
- **Pre-existing dev rot found on the way:** dev twin was UNSTARTABLE — step 8
  (insert_to_list_batch) failed validation "Code: Please complete this required field"
  because the editor had stale list schema; **Refresh in the editor regenerates schema and
  clears it**. Dev daily chain (3383898 → 3383903) has been failing NIGHTLY for months with
  `Can't call a stopped recipe (3383901)` — dev deploy tooling is degraded, prod is the live
  path. Dev 3383902 last ran 2025-07-28.
- **Live test RESULT: SUCCEEDED** — job `j-Abxw4fn9-cktKQo-CD`, version 43, 2026-10-16
  02:51:46→02:57:47 UTC, 110 business actions. All 5,379 dev recipes (2× stress) in 6m01s.
  Trace-verified: list items carry only id/name/folder_id/description; upsert rows
  code-free with correct params. 2.2× faster per recipe than prod's pre-fix 7-min runs.
  Recipe left RUNNING in dev.
- Force-run via `wt`/fixture = 401 missing_privilege (JWT lacks it) — editor TEST is the way.
- Josh decided: Snowflake data-team scan DESCOPED from blockers (kept as optional note).

## Autopsy of the "function execution error" class (DONE 2026-10-17 — two passes, reconciled)

- Parallel session posted an autopsy first (Jira comment 1140960, 2026-10-16): 29 duplicate-name
  failures (24 recipe resolver 3792734 / 3 connection 3792732 / 2 project 56324388) + 1× 502;
  cadence flat 2–3/week since Jul 28; recommends resolver rework on all three resolvers with
  folder-path as the durable key + destination-project preference fallback.
- This session's pass (comment 1141773) adds the live-trace evidence the first pass lacked:
  failing inner job j-AbwaCaXx-xQtYN8-CD shows the Snowflake lookup is ALREADY workspace-scoped
  (`where name = :name and workspace_user_id = :workspace_user_id`); the collision is inside
  workspace **3535597** (Josh's US dev) — TWO recipes named `New Critical Ticket CSM
  Notification` (66937514 + 66835227) in the SAME folder 26978285 (`Home/[Genie] CSM
  Genie/CSM Genie/Support Tickets`) — a deploy ran twice, copied instead of updated. Prod
  800229 has ZERO same-named recipes. (API `name` filter silently ignores the param — count
  client-side; both passes hit this.)
- Verdict: memory fix does NOT touch this class. Short term = data cleanup (dedupe the pair in
  3535597 — a delete, needs Josh's go); long term = the first pass's resolver hardening
  (separate ticket).
- The 502: 1 occurrence in recent 100 — retry envelope NOT warranted on this evidence;
  revisit only if it recurs post-promotion. (Plan v2 item 5 resolved by evidence.)

## PROD DEPLOYED (2026-10-18)

- Josh confirmed the prod write; executed stop → PUT → start on 3792740 in the confirmed quiet
  window (last call 01:06 PT, next daily run ~00:00 PT). **Running: true, version 35.**
- **KEY LESSON — five touch points, not four:** the first start FAILED validation
  (`list_items.code can't be blank`) — the step-level `extended_input_schema`,
  `extended_output_schema`, and `visible_config_fields` blocks (SIBLING keys of `input` on the
  step block) still declared Code as required. Stripping only the input/DSL mappings is not
  enough for start validation; the dev twin's editor-Refresh had silently done this cleanup.
  Any future DSL-level recipe edit must strip code (or the edited field) from ALL of:
  input mappings, step schemas, extended_input_schema, extended_output_schema,
  visible_config_fields.
- Red-team Tier 2 verdict: FAIL on arrival → both material findings closed by evidence
  (MATERIAL-1: upsert does NOT null unmapped columns — probe 83152838 / job
  j-AbzxXeda-cbabBE-CD returned `code_rows=3944` post-code-free-rebuild; MATERIAL-2: quiet-window
  procedure) → effective PASS-WITH-NOTES.
- Manifest 367065 (prod, 5 rows): created + record-confirmed via `wt manifests get`; in-page
  read-back BLOCKED by an unresolvable browser env-switch (dev→prod of AHQ|BT — the env menu
  items ignore clicks; ~10 attempts) — complete at review time.
- Smoke: tonight's 00:00 PT daily rebuild; automated morning check scheduled (8:23 daily,
  session cron). Acceptance: 2–3 consecutive green days on 3792740 (baseline 2–8 failures/day).
- DR story: BSYS-29778 (parent BSYS-27911). Probe recipe 83152838 kept (only Snowflake read
  surface we have; delete after DR closes).

## SMOKE: GREEN (2026-10-19 morning check)

- **Zero memory shutdowns on 3792740 since the Oct 18 07:46 PT fix** — baseline 2–8/day, 150
  memory failures in the pre-fix history (latest Oct 17 00:37 PT). Two full overnight rebuild
  chains green (Oct 18 + Oct 19; 68 runs the second night). Acceptance at 2 of 2–3 green days.
- Chronic non-memory failure discovered: every midnight ~00:01 PT one workspace's rebuild fails
  with `400: No value found for secret key Client Secret` — 12 consecutive days (Oct 10–19),
  pre-existing, unrelated to the fix. Candidate small ticket: identify workspace, rebind secret.
- Evidence posted to BSYS-29778 (comment 1142747) + BSYS-29383 (1142748). ⚠️ Atlassian MCP 403s
  all calls today ("app not installed") — posted via the REST v2 fallback (basic-auth credential
  from keychain `atlassian-confluence`; api/2 takes plain text, api/3 ADF got INVALID_INPUT).
- Manifest 367065 verification: rows verified id-by-id against the live bt-prod listing; package
  export (pkg 42264345) FAILS — Workato's exporter refuses connections outside the anchor
  project ("* Connections" vs "[BT] .../Setup") — fine for an in-place-edit DR, would matter
  for any cross-workspace import. In-page read-back still pending the env-switch problem.

## Secret-key nightly failure: identified + filed (2026-10-19)

- Workspace identified: **`Workato Internal` (workspace_user_id 10596, env "Development")** —
  Workato's own internal workspace, in the deploy roster since 2023-07-25. Evidence: failing job
  j-Ac3WL6zP-8bpPKA-CD (3792740) → caller j-Ac3WKN6g-ftThnt-CD (3792742) → roster in root daily
  job j-Ac3WKML4-P6aToD-CD (3792738) — data-table row maps 10596 → connection 1260638 "Workato
  Internal".
- Root cause: connection 1260638 (in AHQ | BT Production) references a secrets-stash key
  `Client Secret` whose value is empty → every rebuild API call 400s. Josh's direct-paste attempt
  got 401 = wrong-workspace credential: **API-client tokens are workspace-scoped** — the token
  must come from an API client created INSIDE Workato Internal (10596)
  (docs.workato.com/en/workato-api/api-clients.md). Josh lacks admin there.
- **Filed: BSYS-29797** (Bug, 1pt, parent BSYS-27911, assigned [requester]) — regenerate/
  create the API client in Workato Internal, store the view-once token in the stash key
  `Client Secret`, next 00:01 PT run verifies on its own.
- Session note: Orca browser's Workato session logged out (needs manual sign-in) — blocked the
  manifest in-page read-back + any browser-driven prod work this session.

## CLOSED (2026-10-20)

- Day 3 green: Oct 20 chain 69 runs / 68 green / 0 memory (the 1 failure = Workato Internal
  credential 401, BSYS-29797/Patricia). Three consecutive green nights. All AC met.
- BSYS-29383 closed (resolution Done; day-3 evidence comment 1143722) + BSYS-29778 closed.
- Probes deleted: 83192578 (prod smoke, Oct 19), 83152838 (dev Snowflake, Oct 20).
- Only tail: BSYS-29797 (Patricia). Manifest 367065 read-back stayed pending (browser session
  logged out); rows verified against the live listing instead.

## Post-close watch (2026-10-21)

- Day 4: memory still zero (4th green night). Workato Internal slot REGRESSED: back to the
  original missing-secret 400 (not the 401) — Weizhuang's 08:41 PT re-auth appears to have wiped
  the stash binding for `Client Secret`. Follow-up comment posted on BSYS-29797 (comment
  1145337, REST fallback — Atlassian MCP needs /mcp re-auth again). Ticket ownership on the
  mission-control board sits with estate-monitor (BSYS-29797 claim).

## Post-close watch (2026-10-23)

- Day 6: memory zero (6th green night, 154/156 green in 24h). Workato Internal slot STILL failing
  (13 nights now; the Oct 20 re-auth didn't hold). Persistence threshold passed — nudge comment
  posted on BSYS-29797 (comment 1147619) with the exact closing check. Next: daily cron keeps
  watching; if still failing by Oct 25, escalate to Sen Rong (Patricia's manager).

## Post-close watch (2026-10-25)

- Days 7-8: memory zero (8th green night; 134/136 green in 24h). Workato Internal still failing
  (15 nights). ESCALATED per the Oct 23 threshold: comment 1148339 on BSYS-29797 with real
  mention nodes for Sen Rong (Patricia's manager) + Patricia, the closing check, and the
  probe-re-run offer. Watch continues daily; next nudge only if the escalation stalls a week.

## Access (set up 2026-10-15)

- `wt` profiles `bt-dev` (workspace 800219) and `bt-prod` (800229) — keychain
  `workato-platform-cli` / accounts `bt-dev`, `bt-prod`; both verified via `/api/users/me`.
- ⚠️ Both tokens LACK data-table record read scope (403 on `[DEPLOY] Internal Workspace Workato
  API Connections` rows — couldn't count workspaces; caller attribution settled the question
  instead). AIRO MCP is bound to AHQ|AI workspaces — cannot see BT at all.
- wt recipe reads: `GET /api/recipes/:id` (NOT /api/v2). Job history: `/api/recipes/:id/jobs`.

## Dissent record

- Round 1 (10-15): BROKEN — falsified the Snowflake-lookup draft diagnosis.
- Round 2 (10-15): REVISE — sandbox destination for tests, named trace-pull executor.
- Round 3 (10-16, this session): SHIP-WITH-CHANGES — added Step-0 code-flow verification,
  memory measurement (not pass/fail), Snowflake consumer scan, demoted decoupling behind the
  code-less inline rebuild, dev-twin Snowflake-target disclosure, governance gates (manifest +
  red-team Tier 2). The miss-rate objection (~95/day) was REFUTED by caller attribution data.
  Full text: knowledge/dreams/bus/dissenter.jsonl, thread BSYS-29383.
