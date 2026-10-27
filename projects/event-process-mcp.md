---
project: event-process-mcp
updated: 2026-10-13
---
**ESTATE MONITOR: moved to [[estate-monitor]]** (2026-10-12 — own repo ~/orca/projects/estate-monitor/, own knowledge file, epic BSYS-29554). This project's ops-monitoring family is in a parity window with it.
# Event Process MCP (Event360) — project knowledge

Canonical repo (Orca home, absorbed 2026-10-06 from the unborn-git evidence
bundle in ~/Documents/ChatGPT/Event Process MCP/):
`~/orca/projects/event-process-mcp/`

- Master handoff (read first, evidence-labelled): repo
  `docs/EVENT_PROCESS_MCP_ORCA_HANDOFF.md`
- Plan-doc status map: repo `docs/plans/INDEX.md`
- Evidence ledger (append-only): repo `docs/EVIDENCE_LOG.md`
- Project skills: `.claude/skills/event360-ops` (incident runbooks) and
  `.claude/skills/event360-live-refresh` (live asset revalidation, identity
  map dev↔prod)
- Jira: epic BSYS-28196, stories BSYS-28197–28204; scalability work
  BSYS-28478; adjacent Marketo MCP BSYS-28296
- Identity: Dev project 14570285 (folder asset 31646573); Prod project
  17429278, path `Home/MCP | MOPs/Campaign Copilot by Workato MCP`, Event360
  folder 35283758. Full dev↔prod ID map lives in the
  event360-live-refresh skill — never mix environments' IDs.

State (2026-10-06): system live in Production (two workflows: event program
creation; async Marketo bulk lead import). Open risks, priority order: (1)
no pre-side-effect durable claim before Calendar create (replay can
duplicate), (2) `mcp_mock_*` correlation not replay-safe, (3) Prod
ProgramCreation `82043948` still stamps `environment=Development` and embeds
Dev recipe IDs in signal payloads (Oct 1 hotfix fixed Prepare only —
live-verified 2026-10-06), (4) hard-coded `-07:00` calendar offset in BOTH
envs (DST bug, never fixed), (5) Prod lacks Dev's `addCalendarEvent` toggle
(dev/prod drift), (6) FileStorage worker subscription health unprovable
without heartbeat, (7) Slack adapter prototype not deployable (identity
boundary unconfigured).

**2026-10-11 BSYS-29508/29509: FIXED IN BOTH ENVIRONMENTS.**
Resolved the Oct 9 contradiction: Prod 82043948 v7's fix covered only the
FAILURE-ledger write — success-ledger (step 17) still stamped "Development",
steps 14/23 still embedded Dev recipe_id/recipe_url/job_url literals. Dev
73594487 now fully property/context-driven (env stamps → project_property
'Event360 Environment'; signal IDs → job_context) and DST-aware (step 6
formulas). Formula whitelist gotcha: AIRO ruby() rejects Date.new — DST
boundary via Zeller's congruence integer math; Nov 1 ≡ Mar 1 weekday (245
days) collapses both boundary Sundays to first_sun = 1 + ((4 - t) % 7), t =
k + k/4 + j/4 + 5j; 17/17 local dates pass. Verified by fresh API read
(zero Development/-07:00 literals); dev restarted, running:true. PROD
82043948 v8 pushed the same definition (stop → push → start, rollback =
v7 id 154153649), running:true verified; live-UAT rows open on both tickets
(first real PST-date creation proves the calendar offset; next prod creation
proves environment=Production ledger row). wt has a prod
profile: `wt --profile josh-prod` (profiles in ~/.workato/profiles) —
properties/connections/recipes readable prod-side; wt warns and gates writes.

Related: [[marketo-eventops]] (July 2026 Marketo EventOps MCP App,
BSYS-26824 — likely predecessor lineage; separate assets), and domain file
[[workato-platform]] (wt CLI wrapper, lifecycle SOPs).

**2026-10-07 addCalendarEvent deployment (BSYS-29325, Deployment Request
type):** three import failures, all manifest-side (no code changes needed).
(1) Manifest 357964 held only the touched assets — package import resolves
recipe-function references ONLY in-package → added the three callees (Index
Marketo Events 74768289, Notify Event360 Slack 75089241, OPS | Emit
Event360 Signal 76418726). (2) The API update rewrote asset rows'
zip_name/folder with the folder-assets endpoint's project-name-prefixed
paths (`MCP | MOPs/…`) — the resolver matches the JSONs' project-root-
relative reference strings against member paths → restored project-root-
relative rows. (3) The MCP server asset references ALL 7 app skills →
expanded to the full 18-asset closure (recipe + skill + mcp_server + 3
callees + 6 remaining skills incl. event360/lead-import family + their 6
provider recipes; verified against the ORIGINAL proven app manifest
**333119 "BSYS-28478 - Deploy Event Process MCP"**, the Sep 2 promotion —
export 42165339 zip = ground-truth closure). Tables/connections excluded
(refs resolve against destination — proven 3×). Key mechanism: the deploy
bot builds its import zip from the manifest's stored per-asset zip_name
rows; the API package export is NOT evidence of what the bot ships (its
zip paths prefix the project name). Full gotchas in jira-story-standards.
Awaiting Josh's 4th Re-Deploy; on success this closes risk (5), the
dev/prod addCalendarEvent drift. Scope caveat: 12 more assets ship their
current dev state (Prepare prod got the Oct 1 hotfix — dev copy must carry
it; the Automation/Ops-Monitoring families stay OUT). Pre-deploy open
items on the ticket: hardcoded "true" ledger columns c5a66c57/3b0422a2,
blank calendar_url handling in Notify Event360 Slack.

**2026-10-07 dev-side parity fixes (pre-redeploy):** (1) Prepare 74768204
env-stamp now reads project property `Event360 Environment` (dev value
`Development`) — kills the regression class; prod property `Production`
must exist before the next deploy. (2) Notify 75089241 Sep 3 dedupe hotfix
PORTED into dev (steps 9/10 conditional on Slack body.ok: sent/failed,
slack_api_rejected code/message, nil sent_at, slack_channel_id write —
dev ledger 139415 has all 21 columns with identical UUIDs; also fixed
prod's cosmetic bug where step 10's message interpolated the ternary
literally). (3) Search 74768205 Oct 1 "email typeahead" dev change REVERTED
to prod's JS (not UAT-covered, step-7 numeric-ID gap, index-content
dependency) — feature JS preserved in
orca/projects/event-process-mcp/pending-features/search-email-typeahead-
step4-DEV.js for its own ticket. Set_input_field datapill mode accepts
project_property['Name'] refs (f-string wrapped); v4-mode plaintext on a
top-level snippet `code` param cleanly replaces JS AND normalizes away the
payload_asset_type/REQUIRED-FIELD-PLACEHOLDER corruption. Remaining prod
writes (Josh confirm pending): prod property Event360 Environment=Production,
rename prod MCP Skills→Skills (path-match for in-place import), delete
inert duplicate tree 35712655.

**2026-10-07 04:57 UTC — DEPLOYED CORRECTLY (5th attempt).** Renamed DEV's
Skills folder → MCP Skills via wt API (`PUT /api/folders/:id` — dev token is
env-scoped, no prod API access; folder renames are dev-side fixes when dev
naming is the odd one) so dev-true reference paths = prod tree; re-deploy
landed IN PLACE (same IDs 82043947–53 + 82043929, updated_at bumped, NO new
tree — the earlier duplicate tree vanished with the successful import).
Import leaves overwritten RUNNING recipes STOPPED — post-deploy restart
needed (82043948 + 82043929 restarted). MCP server single
(mcps-AbR6YwoM-JX8-CD) + updated. Prod property created via Orca UI
(angular: synthetic dispatch clicks WORK — real orca-mouse clicks landed
wrong/never focused; inline property rows commit via dispatching
mousedown/up/click on the aria-label='Save row' button). Bot needed
"Submit for Tech Review" (81, needs an ADF comment in the transition
update — plain string 400s) then "Deploy" (91) from Final Tech Review.
Residuals: c5a66c57/3b0422a2 hardcoded "true" columns shipped as-is;
ProgramCreation's env=Development stamp + dev recipe IDs (risk #3) still
literal — extend the property pattern; email-typeahead parked in
pending-features/. Risk (5) CLOSED.

## 2026-10-09 notification/observability round (mined 2026-10-10; newer than the BSYS-29325 section above; live state NOT re-verified today)

- **Prod EventOps_ProgramCreation 82043948 v7 STOPPED pending Marketo
  connection repair.** After a bounded stop/edit/start for
  exception-surfacing changes, Workato refused to restart it: Production
  Marketo connection 19943717 (CON | Marketo MCP) went `Connection lost`
  — the Marketo tenant hit its daily API quota (`Daily quota '100000'
  reached` appeared in a caught error the same day). Recovery deferred:
  reconnect 19943717 when the quota window resets, then start 82043948 and
  verify. Dev mirror: 73594487 also stopped, Dev Marketo conn 19655486
  lost. LIVE-CHECK NEEDED: whether the reconnect + restart happened.
- **Platform lesson (NEW): a recipe whose connection is in `Connection
  lost` cannot be started — no API/CLI/lifecycle bypass exists.**
  `Check connection` on a quota-dead connection still fails; only
  credential reauthorization by the owner repairs it. Also: stop → edit →
  start forces Workato to re-evaluate connection state at start time, so a
  "was running fine" connection can silently be invalid by restore time.
- **"Dev recipe IDs in Prod signals" risk (open risk #3 above): detector
  path FIXED 2026-10-09.** The promoted Production detector 82043940 (v1)
  still carried literal Development constants (environment=Development,
  source recipe 73594487, collector 76419431, Dev URLs) so a real Prod
  caught failure rendered as an unresolvable Development link. Corrected
  in Production detector 82043940 v3; 82043948 v7 also corrected a stale
  `environment=Development` literal in its failure-ledger write. Caveat:
  fixed by literal correction, NOT yet property-driven.
- **CONTRADICTION FLAG:** the BSYS-29325 section above says the env stamp
  became property-driven (Oct 7), yet Oct 9 evidence shows literal
  `environment=Development` stamps still being hand-corrected in
  82043948's ledger-write path and in the detector. Either the
  property-driven fix covered only the addCalendarEvent toggle path, or it
  regressed / never covered the ledger-stamp paths — verify against the
  live recipe before trusting either claim.
- **Caught-error text propagation pattern (NEW, cross-recipe):** the
  catch → ledger → detector → router chain was dropping canonical error
  text (catch returned `catch_27.message` to the caller but the ledger
  persisted only stage/error UUID/type/`adapter:action`; detector wrote
  the literal `degraded_or_terminal` into `Raw context excerpt`; router
  had nothing to render). Fix: `error_category = connector:action —
  message` (message truncated to 500 chars), detector maps ledger
  `error_category` into `Raw context excerpt`, router appends
  `Exception: <value>` only when non-blank. Deployed in Dev (73594487
  step 28 / detector 76419431 step 3 / router 76364470 step 8) and Prod
  (82043948 v7 / 82043940 v3 / router 82043946 v5).
- **Environment-coded Slack alert contract (NEW pattern):** Dev router
  76364470 renders `🔵 [DEVELOPMENT]`, Prod router 82043946 v5 renders
  `🔴 [PRODUCTION]` + explicit `Environment:` line; severity text stays
  independent of environment color; unknown environment/ownership →
  `UNKNOWN ENVIRONMENT` label and OMIT the link rather than fabricate one.
- **Maintenance pattern (NEW):** stop the Production router first so
  lifecycle signals queue during edits instead of paging Slack; on
  restart it drains the backlog (used as health proof: job count 694→698,
  queue 0). Corollary: restarting a router DRAINS its backlog —
  intentional but consequence-bearing.
- **Asset-ID additions:** Production incident router 82043946 (v5) and
  Production detector 82043940 (v3) — neither ID was in the register
  before. Dev router 76364470 intentionally STOPPED (avoid draining its
  backlog to Slack); Dev detector 76419431 active.
- **Platform facts (NEW):** Workato Scheduler minimum accepted interval is
  5 minutes (the dynamic connection-health scanner runs at exactly that).
  Marketo quota exhaustion signature for autopsies: `Daily quota '100000'
  reached` on connector actions while the parent job stays Successful
  under a monitor/catch — and it simultaneously kills the OAuth
  connection validation (connection appears dead, not just rate-limited).
- Archive-repo confirmation: the ChatGPT folder's git repo still has zero
  commits (everything untracked) — the committed evidence bundle refers to
  the orca canonical repo only.
- Superseded-but-durable lessons all already in the master handoff
  (idempotency ordering, key-only notification dedupe, pagination caps,
  batch vs atomic writes, positive allowlists for active-state alerts,
  Marketo filterValues `+` percent-encoding, null-vs-empty-string for
  date columns, never fabricate derived values). Plan headers can lie —
  trust the dated implementation section.



<!-- kb-bridges:v1 begin -->
- [MCP servers - IT Support Ticket Lifecycle](../../kb-corpus/docs/en/mcp/prebuilt-mcps/it-support-ticket-lifecycle-mcp-server.md)
- [Workato MCP Server Development Framework](../../kb-corpus/confluence/extbt/2159444213-workato-mcp-server-development-framework.md)
- [Internal MCP Roadmap](../../kb-corpus/confluence/extbt/2514223105-internal-mcp-roadmap.md)
<!-- kb-bridges:end -->

## 2026-10-11 BSYS-28296 FIXED in dev (Marketo get_lead_activities)
- Adjacent Marketo MCP ticket (not Event360 proper) — full loop in
  domains/workato-platform.md 2026-10-11 section. Short version: quota
  recovered → stale Not-authorized flag cleared via connection-page Connect
  → live repro proved Marketo's empty-page-while-moreResult behavior →
  get_lead_activities 72856618 (Marketo by Workato MCP family, project
  13683566) rebuilt with bounded 10-page auto-pagination (list-carried
  state, post-loop aggregate+return) → repro returns the Fill Out Form
  event with type name + attributes. v37 Running. Rollback snapshot:
  repo app-snapshots/bsys-28296/. Residuals: assertions + caller-cursor
  regression case not authored (test-case API 422s); cursor/has_more nil
  under test sandbox — confirm on a real MCP call; prod promotion of the
  fix NOT started (dev-only so far).

## 2026-10-19 BTSUP-79202: "Campaign Copilot MCP shows no tools" — server side verified healthy

Ticket filed 18:54Z by Perri Bronson (MOPs), Marc Parilla pinged Josh 19:02Z.
No description, no client info.

Live evidence (wt --profile josh-prod, 2026-10-19 ~20:00Z):
- MCP server `Campaign Copilot by Workato MCP` (mcps-AbR6YwoM-JX8-CD): published=true,
  tools_count=7 (all tool rows present), mcp_url https://18680.apim.mcp.workato.com,
  auth=workato_idp scoped to ONE idp_user_group (hYq3WdMefHkN2eest6Beq3),
  has_vua_dependent_tools=false, config unchanged since 2026-09-12.
- ALL MCP skill recipes running (82043947-82043953), all automation/functions/ops
  recipes running. The Oct-09 Marketo-quota stop of 82043948 was resolved earlier.
- Gateway live: /.well-known/oauth-protected-resource returns valid metadata.
- NOT verified: an end-to-end tools/list over a live OAuth session — the id.workato.com
  authorize flow bounces to Okta sign-in (Workato GO | Home Agentic SSO) needing Josh.
- NOT knowable from here: which client/user the reporter means, IDP group membership.

Working theory (labeled as such): consumer-side stale sign-in or group membership;
some clients show "connected, empty tools" on failed entitlement. Reply posted asks
for client + user + reconnect behavior. If recurrence: the OAuth end-to-end check
(OAuth dance per wt-cookbook) is the next decisive probe, needs Josh's browser.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Event Process MCP / Event360](projects/event-process-mcp.md) — Event360/Campaign Copilot MCP app (BSYS-28196); ops-monitoring parity-window with [[estate-monitor]]; canonical repo ~/orca/projects/event-process-mcp/ (absorbed 2026-10-06, committed evidence bundle); master handoff docs/EVENT_PROCESS_MCP_ORCA_HANDOFF.md; project skills event360-ops + event360-live-refresh; open risks: calendar replay/claim ordering, env stamps in Prod signals (detector half FIXED 2026-10-09 via literal correction — property-driven claim needs live verify), -07:00 DST bug; **addCalendarEvent toggle DEPLOYED TO PROD 2026-10-07 (BSYS-29325, 5th attempt — in-place import verified); email-typeahead parked**; **2026-10-09 round (mined 2026-10-10): Prod 82043948 v7 + Dev 73594487 STOPPED pending Marketo reauth (quota-killed conns 19943717/19655486 — connection-lost blocks recipe start, NO bypass; LIVE-CHECK restart status); error-text propagation pattern (error_category=connector:action—message, 500-char cap) + env-coded 🔵/🔴 Slack labels + router-drain-on-restart deployed; new IDs: prod router 82043946 v5, prod detector 82043940 v3; scheduler min interval 5 min; Marketo quota signature `Daily quota '100000' reached` kills OAuth validation too**