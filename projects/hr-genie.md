# HR Genie — project knowledge

- **Architecture maps LIVE (2026-10-08)**: `architecture/system-map.mmd` +
  `architecture/asset-graph.mmd` (+ rendered SVGs) under this project's
  knowledge dir, built by the `arch-diagram` skill — system map covers all
  subsystems; asset graph covers BP Completion + Consumer Endpoints families
  (omitted families listed in the file header). Maintained at handoff;
  QA'd by project-dreamer's 5b lens. CORRECTION (tracker-verified
  2026-10-08): Consumer Endpoints recipes now live in folder 35712142, not
  35693717 as cited in the 2026-10-05 build note below.
- Convention (2026-10-22): NEW notification families adopt the Event Outbox pattern —
  `Workday-Development/docs/workday/build-specs/EVENT-OUTBOX-PATTERN.md` (per-family semantic
  matrix first; state machine, dedup, retry caps, audit columns, kill switch; no shared
  recipe, legacy assets never retrofitted outside a promotion window).
- Canonical master doc: ~/Documents/Claude/HR-Genie-Master-Knowledge-Doc.md
  (created by consolidating five fragmented dated handoffs — do not add
  dated handoff files next to it; update in place).
- Related: PTO notifications platform (BSYS-26808); weekly Zoom transcript
  intake feeds the AI Enablement knowledge base (skills: weekly-intake,
  zoom-transcript-intake, weekly-session-transcript-intake).
- BSYS-28312 `check_business_process_status` skill built in dev 2026-10-02
  (recipe 82778233, audit table 155277, attached to HR Genie as skill 26);
  UAT blocked on end-user WQL grant. Canonical as-built record lives in the
  Workday-Development repo: `docs/workday/project-memory/EXECUTION-BSYS-28312-BP-STATUS-SKILL-2026-10-02.md`
  (build spec §9 in the same repo's build-specs folder).

## BSYS-28313 — BP Completion Notification Platform (2026-10-02, UAT signed off)

Proactive Slack notification when a Workday BP completes, to every approval-chain
participant. Assets (dev, folder 32175654, project 15643451): ledger table
`HR Genie | BP Completion Notification Log` (155278, UUID c6b5e889-…);
[REC | BP Completion Discovery Hub 82778372](https://app.workato.com/recipes/82778372)
cron */5 WQL over businessProcessTransactions, NO type allowlist;
[FUNC | Resolve BP Completion Recipients 82778326](https://app.workato.com/recipes/82778326)
(approval chain from WQL approvedByWorkers, Get_Workers email + terminated guard);
[FUNC | Process BP Completion Row 82778367](https://app.workato.com/recipes/82778367)
(event-level dedup, log-before-send, <2 approvers ⇒ SKIPPED_SINGLE_APPROVER audit row,
message carries "Approval chain: …"); [REC | BP Completion Retry Handler 82779006](https://app.workato.com/recipes/82779006)
(hourly, FAILED only, 3-attempt cap). Project properties via CLI: BP Completion Notify
Go-Live Date / Lookback Days. HR Genie instructions have a "BP completion notification
events" section (deliver verbatim). Full build state + traps:
Workday-Development repo `docs/workday/project-memory/BSYS-28313-BP-Completion-Notifications-2026-10-02.md`.
Jira comments 1127309 + 1127703. UAT signed off by Josh 2026-10-02; promotion handoff
issued, awaiting BT managed promotion via Jira. Probe recipe 82778137 to delete at promotion.

## Consumer Endpoints / OOO Status API (BTSUP-72246, planned 2026-10-05, no build yet)

Vlad Sharikov (Team UI, ~30 ppl) wants boolean is-OOO from Workday via HTTP for
his Engineering Utilities recipes (PR-reviewer assignment; ~1-week PR lifecycle →
also needs "OOO within next 7 days"). Governance precedent BTSUP-72726 (Konstantin):
**no direct Workday creds** — centrally managed API only; sensitive-leave-type
filtering is impossible in Workday, so minimization must happen BT-side.
Plan: `docs/workday/consumer-endpoints/PLAN-BTSUP-72246-OOO-STATUS-API-2026-10-05.md`.
Decisions locked by Josh 2026-10-05: roster = Slack #team-ui seed (GitHub connector
has NO team-members action); **LOA in scope** (union with WQL leave sources —
candidates `leaveOfAbsenceOutstandingByDateRange` / `leaveOfAbsenceRequests` /
"Approved Leaves of Absence", probe at build; NOT the inbox query — that only
shows pending approvals); real Team UI roster OK in dev (reads only).
Design: new `Consumer Endpoints` folder under project root 30275122; roster table,
hourly WQL snapshot reusing the PTO-hub-validated `timeOffByDateTaken` source
(approved rows, window [today, today+6] — the hub's REMINDER detector proves
future-dated rows return; select NO type/reason fields) into a 30-row snapshot
table (`is_ooo` + `ooo_within_7d` booleans, merged so vacation vs LOA is
indistinguishable — deliberate privacy property, never add a source column);
`workato_api_platform` receive_request/return_response endpoint reads ONLY the
snapshot, roster-allowlist-gated (unknown identity → not_in_scope), audit table
per call. No free-form withinDays param (would force per-day storage = absence
dates); new horizons = new fixed boolean columns. Reuses backend ISU conns
19760013 (SOAP/WQL) + 19218617 (REST) — zero new Workday creds. API
collection/client/rate-limit are UI-only steps (orca-browser). Build assigned to
glm-5.3-flash; est. 5 pts; prod promotion = separate approval.
**BUILT + VERIFIED IN DEV 2026-10-05 (glm-5.3-flash session)** — folder
`Consumer Endpoints` (35693717): [REC | Consumer Roster Sync 82823992](https://app.workato.com/recipes/82823992) RUNNING,
[REC | OOO Snapshot Refresh 82824104](https://app.workato.com/recipes/82824104) RUNNING,
[API | Get OOO Status 82824133](https://app.workato.com/recipes/82824133) RUNNING;
tables Roster 156260 / Snapshot 156261 / Audit 156262; API collection
[HR Genie | Consumer Endpoints](https://app.workato.com/api_groups/1404598)
(endpoint `v1/ooo-status` ACTIVE, client team-ui-eng-utilities 1285074 +
policy 60/min 5000/30-days, key issued); properties via `POST /api/properties`
with STRING project_id (env-scoped reads as empty in recipes — project-scope
them). **Roster source = workspace-owned Slack bot (Josh's ruling: end-user
credentials NEVER in long-running integrations):** app **BT Consumer
Endpoints** A0C6Y8E5U3C (scopes groups:read/users:read/users:read.email), bot
user U0C7TT30QKA, in #team-ui (G9ZJS0F0U, private); custom OAuth profile
45994 (dev) + connection **22250878 "BT Consumer Endpoints Bot"** (authorized
2026-10-05 20:35 PT); client + signing secrets ROTATED and profile synced
2026-10-06 (values had transited session context). 32/32 roster rows active,
bot-sourced (source=slack). **Zero-member guard** in sync step 12 (a Slack
failure once mass-deactivated all 32 rows via channel_not_found → empty
member list → departed-check; guard trips on member_count<1). Roster cron
0 6,18 * * * (twice daily). LOA solved via `allWorkers.onLeave` fields (see
workday-platform domain) — NO LOA WQL grant needed. Live curl proof: member
→ ok/false/false AND ok/true/true (row-write + self-heal recompute); unknown
→ not_in_scope; auth = `Api-Token:` header only; 32/32 batch ok. UAT complete
in dev; Jira comment 1129172 posted. **Vlad's dev handoff sent 2026-10-06
via Slack DM** (endpoint `https://apim.workato.com/workato-bt-ai-dev/
hr-genie-consumer-endpoints-vv1/v1/ooo-status` + Api-Token key 1372333
value, DM D0C7QHWUNN4 ts 1791258235) — awaiting his test feedback. Prod
triggers: roster cron set via custom_schedule+cron_expression DSL (works);
snapshot still on Minutes/5 in dev — set `7 * * * *` via UI editor at
promotion. Residuals: obsolete Consumer Roster Seed Emails property; dev
scheduler anomaly (new recipes' ticks only observed at start — ops to watch
06:00 PT tick). PROD profile 45993 (accidental) DELETED 2026-10-06 with
Josh's consent. Build traps in domains/workato-platform.md. **2026-10-06 Vlad's test
dispute RESOLVED by ±7d probe:** Petrakov/Gavrilov correct (approved PTO,
July approval dates); Gniteev/Filin/Kudrin/Grunin have ZERO rows in
Workday absence data (plus "nickbullock" = Nikita Balakirev's Slack display
name — he IS rostered fine, so all five reduce to the tenant gap) (not approved/pending/LOA — while other workers' pending
rows DO appear, so the source isn't hiding them); their Slack statuses are
user-set. ("Bullock roster gap" was WRONG — nickbullock IS Balakirev, rostered fine.) Endpoint logic verified
correct; oooWithin7d 0-day-lookahead BUG fixed live (window_end = now+6d,
snapshot rebuilt, both flags now differ). Diagnosis ran via raw
Developer-API recipe-code surgery. **2026-10-08: PROMOTED TO PROD + first prod hotfix.**
Prod assets: recipe 82917290, tables 157752/157753(+audit), folder 35747461,
project 15783895, workday conn 19909763. Josh spotted isOOO=true ⇒
oooWithin7d=true always (structural: today ∈ window range; LOA in_window
unconditional). FIXED in dev (82824104) + prod (82917290) same day:
in_window = strictly-FUTURE days only (d > today); LOA in_window requires
est_end empty-or->today (open-ended leave stays in-window); window_end
today+7. Verified live: Gavrilov (last day of leave) → true/false in dev.
Prod push required: browser env→Production→Stop, AIRO-prod push, browser
Start (wt is dev-only; prod AIRO has no lifecycle tools). Prod verified
12:52 tick succeeded, window 10-08→10-14. NOTE: prod schedule still
Minutes/5 (checklist said hourly 7 * * * * — not yet applied). **JOSH'S CLOSE (2026-10-06): the whole
dispute was a TENANT artifact** — backend ISU conn 19760013 reads the
Workday IMPL tenant (wd108); real PTO bookings live in Workday PROD, so the
DEV endpoint can never be 100% accurate for live absences (the 4 "wrong"
people are expected false negatives; Petrakov/Gavrilov matched via seeded
data). Accuracy arrives at prod promotion (prod ISU connection). DO NOT
re-diagnose the "missing PTO" in dev again. Still real: oooWithin7d window
bug (fixed), Bullock roster resolution (fix before promotion), pending-
approval semantics (decide at promotion). during an AIRO full project-access outage
(pull/init/push + UI 404s workspace-wide; bound-session reads + wt PUT
worked) — method in domains/workato-platform.md. **v1.1 hardening pass
2026-10-06 (post pen-test):** 400s on bad input (type errors only — anti-enumeration
preserved), JSON-null not_in_scope booleans, audit rows now carry caller ip + client
+ key + rejected count; snapshot recipe silently self-stopped once (01:37 PT,
stop_cause null — recommend recipe-stopped email alert at promotion).

**2026-10-12 prod validation (Vlad's 4-email dispute #2, read-only — no assets touched):**
Vlad: daniil.demenev / alexey.uzlov / ruslan.trashchotkin / petr.gavrilov @workato.com "OOO in
Slack, not OOO in Workday — did we miss a rare case?". Verified via prod job traces + tables:
API recipe (flow_id 82917288, ONE version, unchanged since 10-08; the API-platform
`updated_at` 10-12 09:50 was a platform-object touch, not code) returned `ok / isOOO=false /
within7d=false` for ALL FOUR (jobs 10:57–11:01 PT, client team-ui 1288384, access profile
**OOO Checker 1375760** — Vlad's team's own profile). Snapshot 157753: 32 rows, as_of 10-12,
all four FALSE/FALSE; TRUE/TRUE = borisov, utkin, kudrin, balakirev, gniteev (kudrin+gniteev
were the 10-06 "zero Workday rows" people — Workday data since appeared). Snapshot recipe
82917290 v4 healthy: 97/0 jobs, hourly :07 (Minutes/5 residual CLOSED), kill-switch off,
stale=false, loaDegraded=false. WQL window verified live: `timeOffDate >= '2026-10-12' AND
<= '2026-10-19'`. Merge semantics pinned from prod code: PTO isOOO = today ∈ approved dates;
within7d = strictly-future approved dates ≤ today+7; LOA isOOO = on_leave AND start≤today
AND (est_end≥today OR open). **Diagnosis: NO defect — same shape as 10-06:** Slack statuses
are user-set, never synced from Workday; if someone's leave ended before today endpoint
correctly says false. Two REAL remaining v1 edges (not bugs): pending-unapproved time off is
invisible (approved>0 filter — semantics still undecided); future-dated LOA starts don't
flag until start date. Raw per-person Workday rows unreachable: job traces truncate record
lists at ~11 (roster shows 10 of 32) — trace total/count fields ARE accurate. **Test harness
shipped:** `Workday-Development/docs/workday/consumer-endpoints/ooo-harness.py` (batch POST
to prod/dev endpoint, token via --token/$OOO_STATUS_TOKEN/keychain svc `ooo-status-token`;
no token stored — prod key is Vlad's "OOO Checker" profile; minting a BT-owned key = prod
write, Josh's gate). Browser traps learned: prod env table pages use NUMERIC ids
(/data_tables/157753); job-detail canvas re-renders every ~1s resetting scrollTop — step
drawer step selection by coordinate click is unreliable; `wt api GET /api/data_tables`
caps at 100, no pagination.

## Oct 2026 changed-asset promotion batch (2026-10-04/05)

- **Authoritative dev export manifest:** [`HR Genie promotion batch - BP Completion Notifications + Inbox Title Detail + Reminder Caps (2026-10-05)`](https://app.workato.com/export_manifests/356204#content) (name has a stray "e at " prefix — UI rename would not commit) — 23 recipes / 6 tables / 7 project properties / 5 connections / 1 genie / 1 KB / 1 skill / 1 env property. 356201 + 356203 are superseded records.
- Jira story **BSYS-29279** (under epic BSYS-26808, 1 point) is the deployment container. Josh's scope rule (2026-10-05): only tested, working changes promote — nothing waiting on a decision or permission. **Deployment request: BSYS-29283** (Story, 1 pt, Relates-linked to 29279; Reason-for-Change field `customfield_10578` is required on BSYS deployments). **SUBMITTED for BT deployment 2026-10-05** — Josh picked up the deferred BSYS-28312 work (WQL-grant-blocked check_business_process_status, to be registered as a Workday End-User MCP skill) himself.
- **BSYS-28312 check_business_process_status is DEFERRED out of the batch** (WQL grant pending; Josh: it should be an **MCP skill on the Workday End-User MCP server, not a genie skill**). Detached from the HR Genie genie 2026-10-05 via `genie_update skills_to_remove` (skl-AbnepHdT-Rch4YQ-CD; skills 25→24 verified).
- **Manifest dependency-closure trap:** checking any recipe that reaches `FUNC | Send Genie Event` (74094657) force-includes the HR Genie genie → its attached skills (check_business_process_status, create_hr_ticket) → their deps (JSM chain, audit tables). While the skill was genie-attached, NO manifest could exclude it. Detaching the skill from the genie was the only release path. Manifest selections are FROZEN at creation — later edits/detaches do not recompute an existing manifest (Update does not re-evaluate the closure).
- **Folder correction:** the BSYS-28313 BP Completion recipes live in `/Core/Approval Workflow/Inbox Tasks/BP Completion Notifications` (folder **35673674**, created 2026-10-03) — NOT in 32175654 as the BSYS-28313 build doc says. Prod counterpart **35683212** created 2026-10-04 via the Production UI (env switcher → Production; Create → Folder) — the prod tree otherwise already mirrored dev exactly, **including a live `/Vegas Demo Cadence` folder (35591119, all 8 lanes running since the Sep 21 demo promotion)** — so changed Vegas lanes promote as in-place updates, not exclusions.
- Escalator: Josh directed run-and-drain at cap 3; drain converged (0 failures, 22-min backlog passes → clean 2-s passes).
- Ledger table "Include data" chip is not editable from the manifest view — import schema-only if BT tooling permits.

## Genie conversation spam investigation + reminder-cap hotfix (2026-10-03/04)

3,658 HR Genie conversations in 30 days, ALL participant Chris Landry, all "🔔
Action needed" tax-election notifications, 5–15 min apart. Root cause chain:

- **Chris Landry is a demo persona** in the Workday impl tenant
  (impl-services1.wd108.myworkday.com) with two eternally-pending onboarding
  tax-election tasks (Federal + State, due 2026-08-09, never completed, only
  participant = self). Rows in `HR Genie | Inbox Task Notification Log`
  (132894) therefore never reach a terminal state.
- **Senders** are the two 15-min sidecars, not the Discovery Hub:
  [Reconciler 74506733](https://app.workato.com/recipes/74506733) (cron
  `2-59/15`) and [Escalator 74505400](https://app.workato.com/recipes/74505400)
  (:12/:27/:42/:57). Every conversation on page 1 lands 1–2 min after one of
  those schedules, alternating — both passes re-send the same stuck rows every
  pass; a reminder throttle either doesn't exist or is defeated because the
  dispatch reports failure after the Genie event already fired (Genie
  conversation created → Slack leg fails → status stays FAILED/DEFERRED →
  next pass retries → new conversation).
- **Uncapped retry path**: Reconciler Pass A (DEFERRED release) has NO attempt
  cap by design ("no elapsed-time terminal failure; retry until Workday
  confirms terminal state") — an uncompletable demo task makes that an
  infinite loop. Pass B (FAILED retry) is capped at 3; the loop persists via
  state flip-flop.
- **Aggravator**: 4 Vegas Demo Cadence lanes (Inbox Task Discovery Hub +
  Time-Off Event Hub, offsets 1–4m, folder 35537507) were left running after
  the Sep 21 demo, against their own description's "Stop all Vegas folder
  recipes after demos." A notification throttle must therefore live in the
  SENDER, not the demo cadence.
- Baseline Discovery Hub 74482795 jobs were failing in <1s ("Scheduler by
  Workato" error summary; Workday SOAP returning 500 Service unavailable on
  wd108) — fast-failing hub jobs ≠ safe; check sidecars too.
- Diagnostic technique: Genie conversations page (Trigger column = FUNC | Send
  Genie Event) + job_list timestamps of every scheduled sender, matched against
  conversation start times, identifies the firing sender without table access
  (data_table_query 404s on this server — UI or job traces instead).

**FIXED 2026-10-04 (v19)** — but read the CORRECTED cause first: the
background spam was the Reconciler's Pass A re-sending DEFERRED rows whose
send leg fails downstream of the Genie event; attempts only increment on the
send-failure path (validator-leg failures write nothing), so rows sat at
attempts=2 and no cap tripped. Property `Inbox Task Reminder Max Count` = 3
(blank fails safe); Reconciler Pass A entry gated on `Delivery Attempts <
cap`; Pass B cap property-driven AND numeric (`to_i` — old string compare
`< "3"` was lexicographically wrong for attempts ≥ 10); Escalator cap
property-driven. Verified by runtime traces (Pass A gate False, zero
Workday calls, 1.5 min vs v18's 24-min passes). Vegas lanes are permanent
architecture (1-min latency) — the send-side cap is the only storm gate.
Full record: Workday-Development repo
`docs/workday/project-memory/HOTFIX-BSYS-27874-REMINDER-CAP-2026-10-04.md`.

**Escalator blast lesson (2026-10-04)**: raising a reminder cap makes every
row at the OLD ceiling eligible again in one pass — a one-time mass
notification wave (~1,200 over 2h, peak 46/min in dev; Josh accepted).
Converged: counts advance only on SENT, so the drain terminated and the
population gated out (16+ min verified silence, escalator no-work tick =
2s). When changing cap semantics: expect the transition wave, consider one
pass with test_recipient routing first, and beware concurrent catch-up
"Processing event" passes double-sending (no leader election).

Gotchas: AIRO recipe pushes materialize unmapped data-table update fields as
explicit `None` in exports (null = not sent at runtime — inert); CLI stop on
custom-schedule recipes lags propagation (queued ticks fire after Running
shows False — verify by absence of new TICKS, not the flag); editor minimap
"ERROR FOUND? Yes" can be static-check noise with a clean runtime run;
validator-leg failures never increment ledger attempts (unbounded silent
retry, but cannot spam because nothing is sent).

**BSYS-29283 review feedback applied — FINAL design (2026-10-04/05)**: [requester]'s
tech-review non-blockers, iterated to Josh's final semantics. (1) Project
property **`Test Send Email Address`** (dev value `not-configured`) is a GLOBAL
notification override implemented in the messenger choke point
[FUNC | Send Genie Event 74094657](https://app.workato.com/recipes/74094657):
value blank/not-an-email → normal end-user delivery everywhere AND the
truncation operator-alert branch returns SKIPPED (new `operator_alert` mode,
`recipient_email` now optional); value = real email → EVERY notification (inbox,
BP completion, retry, reminders) routes to it — same semantics as the PTO
hubs' blank `test_recipient` channel (verified blank/clean on 74094662 + 4
Vegas lanes). Hubs (BP 82778372 step 12, inbox 74482795 step 10, Vegas
82531467/69/70/80 step 10) carry ZERO recipient logic: plain `total > 1000`
truncation condition + `mode="operator_alert"`. `invoke_skill` mode untouched
(real-user enrollment preserved). Interim designs rejected by Josh: hardcoded
email in live paths, AND populating the property with his address (that would
wire the test recipient into live recipes). (2) Formula-mode `+` concatenation
→ text mode: accepted, deferred for this batch (UAT-signed-off + manifest
356204 built; cosmetic churn before promotion buys nothing) — new builds use
text mode. **Promotion:** manifest 356204 UPDATED 2026-10-05 (Review manifest changes →
Edit manifest content → checked the "Added" `Test Send Email Address` row →
Update manifest; 7→8 project properties, all Updated badges cleared, no
recreate needed); property imports as `not-configured` = desired Prod value.
No test sends were performed; override-positive UAT = populate the property,
watch one hub cycle, clear it. All 7 recipes verified via recipe_get + Running;
hub cycles 20:05/20:10 PDT succeeded post-change. Prod run-book addendum on
BSYS-29283: verify imported messenger's genie_id/chat_trigger_handle re-mapped
to the Prod Genie (literal dev handle in code, RLM remap since Genie is in
package); truncation operator-alert is OFF in Prod until the property gets a
real address; smoke tests double as override-inert proof (recipients must be
real users). Full record: BSYS-29283 comments. Follow-up filed: **BSYS-29288** (Story, 3 pts, under epic
BSYS-26808) — BP hub static go-live window is monotonically growing; fix =
rolling watermark from ledger max completion timestamp (+ boundary dedup via
SKIPPED_DUPLICATE); truncation alert stays as backstop.


**False-success incident (2026-10-05, BSYS-29292)**: Shin How Liu rejected the
MCP connection consent on a PTO approval; the tool call never ran; the Genie
still said "successfully approved in Workday. She'll be notified" — request
stayed open, no notification. RCA: success text ungrounded in any tool result;
instructions lack a no-ungrounded-success rule. FIX PENDING: hard grounding
rule in genie gin-AYbxpMha-YenKAJ-CD instructions — genie_get returns EMPTY
payload (known AIRO trap, twice-seeded session) and genie_update REPLACES the
whole instruction text, so the edit is blocked on reading the instructions via
the Workato UI (Orca session was down) — do NOT blind-write. Evidence to pull:
MCP Tool Usage Events table 5c1e0b4e (not API-readable; needs UI session).
Regression: rejected-path must say "NOT taken"; accepted-path must land.
- ⚠️ TESTING RULE (2026-10-05): test ONLY in the Workato BT AI workspace (dev), and ONLY against the agent named **HR Genie 2** — the sole HR Genie test surface. The corporate Slack "HR Genie" agent (workspace T02MRTQUB) is PRODUCTION (912+ channels) — never message it for testing; Josh once had to shut down a session that created a real HROPS ticket through it. Smoketests only when Josh explicitly declares them.

## check_business_process_status v3 — subject-scoped discovery live (2026-10-05, BSYS-28312)

- Skill 82778233 now resolves via three paths: EVENT_WID (validated 32-hex),
  INBOX_SEARCH (caller's live tasks), and SUBJECT_EVENTS — search_workers →
  get_business_process_events(worker=<first match>) → In-Progress events
  filtered by BP-type TOKENS. Subjects and past approvers can now find their
  processes ("Where is the promotion for David Martinez?" verified live,
  audit AUTHORIZED/SUBJECT_EVENTS). Scoping stays native VUA — foreign subject
  → clean NOT_FOUND.
- One boundary remains: past-approver SELF-discovery with no WID and no
  longer-held task (Workday has no "events I participated in" search).

## Notification formatting — mrkdwn probe (2026-10-06, Tier 1 experiment)

Q: can HR Genie notifications use Slack formatting/Block Kit? Verified: the
unified messenger 74094657 delivers via `workato_genie.send_business_event`
(plain-text inputs only — NO Slack blocks param exists on that action), so
**Block Kit is structurally impossible on the current transport**; the Genie's
Slack app controls rendering. Probe recipe
[PROBE | Mrkdwn Rendering Test 82831542](https://app.workato.com/recipes/82831542)
(dev folder 31025390, scheduler-triggered, inactive, test-only job
j-AbpdJFzr-XpazHR-CD) called the untouched messenger twice in one run: control
plain-text vs mrkdwn template (bold `*labels*`, `•` bullets, `:white_check_mark:`,
italic `_footer_`), both to Josh's DM. Result: **both SENT; formatting renders**
— the genie's outgoing message shows emoji shortcodes converted to real emoji,
emphasis + bullets preserved (verified via Workato conversation transcripts
conversation-01M47QSAAWWRA0FS5SF0ZRZ5DX probe / …63JZ3Q2Z5J9XFD03XZP control).
**Gotchas:** (1) the genie RE-RENDERS, not passes verbatim — it stripped the
"Hi Josh Cramoy," salutation in BOTH conversations (despite the "deliver
verbatim" instruction section) and re-emitted markdown in its own voice, so
per-character template control is approximate; keep templates simple and
eyeball each rendering in Slack before rollout. (2) The genie emits STANDARD MARKDOWN, not Slack mrkdwn — Slack-side screenshot
proof (Josh, 2026-10-06): single-asterisk `*labels*` rendered ITALIC on Slack
too, not bold. For bold labels in rollout templates use `**double asterisks**`;
emoji shortcodes render either way; bullets get real indentation. (3) RTS Slack search does not index
fresh genie DMs (probe text unsearchable minutes later); read the DM directly.
Upgrade tiers: T1 = mrkdwn in existing templates (proven viable, zero plumbing);
**TEMPLATE CENSUS (2026-10-06, subagent audit of all 74094657 callers — 17
recipe_gets): 16 distinct templates (T1–T16) across 17 composing recipes.**
Families: inbox-task T1–T3 + detail block (74482074 s25/s23, Reconciler 74506733
s9/s35, Escalator 74505400 s9) — ALREADY emoji/bold-formatted, but carry a
user-visible `[HR_GENIE_INTERNAL] task_id=… source=… [/HR_GENIE_INTERNAL]`
machine block inside the body; PTO T11–T15 (Process New Request 74247462,
Decision 74247862, Reminder 74248295, PTO Escalator 74248506 via gate
82202341) — ALREADY formatted (🔔/✅/❌/📅 + bold); operator alerts T4/T5
(identical in 74482795 s10 + 4 byte-identical Vegas lanes; 82778372 s12) —
already formatted; **ACTUALLY FLAT and the real work: BP completion T6/T7
(82778367 s17/s19), retry T8/T9 (82779006 s6/s8 — greeting drift `Hello,` vs
`Hi {name},`), anniversary T10 (Work Anniversary Notifier 74380245 s19/s28)**
= 5 templates / 3 recipes. Work Anniversary Notifier and FUNC | Dispatch PTO
Notification 82202341 were unknown callers found by the audit. Rollout scope
≈ 2–3 pts, not 5. Messenger guard wrapper T16 (s19/s27) untouched.
T2 = messenger gains a chat.postMessage blocks leg — **REJECTED by Josh
2026-10-06, permanently unless the platform someday fully migrates to Slack-
native models/buttons for approvals**: it would kill the conversation-per-
notification record (secondary audit surface + reply-with-context) and split
Slack identity; conversation-per-notification was NOT the spam disease (uncapped
sender retries was, fixed v19). T3 = Workbot buttons (overkill, same objection).
**Tier 1 is the endpoint.**

**BSYS-29309 (2026-10-06) — house-style rollout BUILT in dev:** T6–T9
(82778367 s17/s19, 82779006 s6/s8) + T10 (74380245 s19/s28) rewritten to the
PTO/inbox idiom (emoji header, *label* emphasis, italic footer, no salutation;
`approvers_line` untouched — ledger column format frozen, retry reads it);
retry `Hello,` drift eliminated. Jira comment 1129442. Edit path: CLI stop →
AIRO recipe_builder push → CLI start; all three Running. New traps learned:
(a) `recipe_builder_set_input_field` on a template string: pass pills as
f-string Mode 3 (`'f"... {pill['x']} ..."'`) — passing static text SILENTLY
REPLACES ALL DATAPILLS with sample literals; (b) double-escaped `\\n` in the
value → literal backslash-n in output; single `\n` in the JSON value = real
newline; (c) ruby() concat with single-quoted Ruby strings cannot contain `\n`
(Ruby single quotes don't escape it) → converted anniversary template to
text-mode f-string (integer pills coerce fine in DSL f-strings); (d) genie
re-render is NONDETERMINISTIC — kept the header in probe 1, DROPPED the
`✅ *Business process completed*` header in the BSYS-29309 render (fields +
footer always render). If the header matters: hard "reply must begin with the
message verbatim" instruction in the BP-completion-notification genie section
— bundle with the pending BSYS-29292 grounding-rule instruction edit (one
instruction write covers both).

**Instruction hardening APPLIED + VERIFIED (2026-10-06, BSYS-29309):** both
the time-off and BP-completion "deliver exactly as written, then stop"
sentences in genie gin-AYbxpMha-YenKAJ-CD's job description were strengthened
via the Workato UI builder (genies/gin-.../build → Job description → Edit;
NOT genie_update — its whole-text replace stays banned) to require the reply
to BEGIN with the message's first line verbatim incl. the emoji header, no
preamble/omission. Post-edit probe render
conversation-01M47SK58RFDZ034F8NA8ND7F7: header line SURVIVES (kept). Also
corrected stale notes: BSYS-29292's grounding rule is ALREADY in the
instructions (time-off section: "If the skill did not run or did not succeed,
do not claim any Workday action happened"; plus line-94 blanket rule) — that
fix landed in a later session, knowledge note was stale; and the
[HR_GENIE_INTERNAL] block is ALREADY mandated hidden from users (never
display/quote/remove-it instruction) — not a design gap.

**HOUSE STYLE IS BOLD — Josh's ruling 2026-10-06: "No one wants italics.
I want bold. The format should be like `**Time**: 2 hrs.`"** The genie
emits standard markdown (single `*` = italic — useless for labels); all
labels/headers must use `**double asterisks**`. Verified by probe render
conversation-01M47WSVP80Y5F0RQ5CT7FAX84: `**✅ Business process completed**`
+ `**Outcome:**` render BOLD (footer `_…_` stays quiet-italic). All 5
BSYS-29309 templates re-swept to bold same day (82778367 s17/s19,
82779006 s6/s8, 74380245 s19/s28; hub 82778372 + all three stopped/pushed/
restarted in one window). **FOLLOW-UP: the older T1–T3 inbox + T11–T15 PTO
templates use single-asterisk markers → they render ITALIC on Slack and are
now non-conformant with the bold standard; migrating them = a later sweep
touching 74482074, 74505400, 74506733, 74247462, 74247862, 74248295,
74248506 (+ 4 byte-identical Vegas inbox lanes).**

**FOLLOW-UP EXECUTED same day (Jira comment 1129492): the FULL platform bold
sweep is DONE — all 16 templates on `**bold**`.** Window 1 (inbox): 74482074
s25, 74506733 s9/s35, 74505400 s9, T4/T5 operator alerts in 74482795 s10 +
Vegas lanes 82531467/69/70/80 s10 + 82778372 s12. Window 2 (PTO): 74247462
s7/s17, 74247862 s14/s23, 74248295 s6/s15, 74248506 s9 (+ bold
**approve**/**reject** inline markers). [HR_GENIE_INTERNAL] blocks, three-choice
closing copy, ledger/dedup/cap logic, and all bindings preserved byte-identical;
16 recipes touched total, all Running. Escalator + Process Decision ruby
formulas display UNESCAPED `"\n"` in pulls (unlike the Reconciler's `\"\\n\"`)
— reproduce each recipe's own display format when editing; set_input_field
normalizes to canonical `\"\\n\"` form on save.

**UAT EXECUTED (2026-10-06, Jira comment 1129551) — real-event evidence.** Josh
ordered all ledgers + claims truncated (155278, 132894, 127804, 146193, 143128,
142091) and schedules re-run. Real sends verified: inbox family (Clayton [requester] /
Hailey Ward promotion review, conversation-01M47ZHTX8JZ3FBCZE8FRXG271 — bold
title, Markdown Detail/Info table, bold Approve/Deny/Reject/Send Back closing,
**[HR_GENIE_INTERNAL] block confirmed hidden from the user-facing message**);
PTO (Pavlo Perkin / Roman Iudin, conversation-01M47ZM7N78A0VWGS4G9TA08G9 — bold
header; genie bolds leave type + dates on its own); anniversary test
j-AbpfQBch-CHWKxs-CD succeeded; BP completion's two in-window events both resolve
NO_RECIPIENTS (no approvers — T6/T7 verified by content-identical probe render +
clean pipeline; real multi-participant BP completion will exercise it naturally).
OPS: BP hub 82778372 hit the dev scheduler anomaly (no ticks 23:05–23:51 after
stop/restart churn — stop/start fixes it, tick fires on start); Vegas lanes
82531470/80 had hung pending jobs, cleared by stop/start. All 19 recipes Running.
Story BSYS-29309 promotion-ready for the next batch.

**"Manufacture the scenario" play (2026-10-06, Josh doctrine: when the test
scenario doesn't exist, create it — don't wait):** Josh approved two real stuck
BPs from his own Workday inbox (workday-mcp list_my_pending_tasks →
action_inbox_task). Libby Alden comp change → BP COMPLETED → hub detected in
~60s → resolver built the real chain → **SKIPPED_SINGLE_APPROVER fired live**
(his own BSYS-28313 sole-participant rule — trace 82778367 job j-AbpkgEGh-
xzGYac-CD) → next cycle SKIPPED_DUPLICATE. Promotion: David Martinez (stuck
since Sep 21) → approved, chain advanced to 6 awaiting parties → fresh T1s to
them. Every pipeline hop now real-event-proven; only T6-with-≥2-recipients
remains composition-of-proven-paths (fires naturally at first multi-approver
completion). Lesson: the end-user Workday MCP + stuck demo-tenant BPs = an
on-demand BP-completion scenario generator; sole-approver completions can
never produce T6 sends (by design).
Existing senders' templates live in 82778367 steps 17/19 (BP completion),
inbox hub 74482795 step 10, Reconciler 74506733 / Escalator 74505400. Batch
manifest 356204 is SUBMITTED — template changes ride the NEXT dev cycle, do
not churn the frozen batch. Probe 82831542 is disposable after the experiment.

## Skills Repository sheet ↔ Jira mapping (2026-10-06)

Filled the 5 rows missing JIRA links in the "HR Genie Skills Repository"
Google Sheet (1GOn_nrmjk19_XiHrC3JTF_9Zi_sygAIc, gid 1986319682), row = sheet row:
- r44 Make Leave of Absence Notifiable (Done) → BSYS-28309 (Backlog)
- r51 JSM Deflection enhanced → BSYS-27771 (fallback-detection logic, Backlog)
- r52 JSM ticket interactivity / responses update HR Genie thread → BSYS-27775 (conversation-log + ticket-key write-back, Closed — actual two-way sync is still-unticketed Phase 2)
- r53 Inbox task proposed business title not showing → BSYS-29261 (Closed; fix shipped to dev 2026-10-02, so the sheet's "Not Started" status is stale)
- r54 JSM request type = HR Genie + hrgenie label question → BSYS-27772 (UAT; label part CLOSED in dev 2026-10-08 — see BSYS-27772 section)
- Side effect to re-check: the sheet's basic filter (29/53 rows shown) was
  removed during editing and its criteria could not be recovered — Josh
  reapplies if wanted. See [[google-sheets-browser-editing]] for the method/traps.

- 2026-10-06 BSYS-28314 FTO gate BUILT (Phase 1, Option D): new steering skill
  get_my_time_off_options (recipe 82839617, skl-AbphJwLz-EY3t6D-CD, folder
  30326966, VUA rest 19218617) — REST get_worker(me) → get_staffing_worker
  country (ISO alpha-3) → get_eligible_absence_types → get_absence_balances →
  Ruby classifier (substring plan matching; depletable-first rule; USA
  exemption). Ranked result: preferred/allowed/blocked + guidance. Registered
  as tool #25 on Workday End-User MCP mcps-AYbrRaxY-dhF-CD; Genie selection
  24 of 25 (view_payment_elections stays intentionally deselected); Genie
  instructions updated (options-first routing + never-offer-blocked rule).
  New project properties: HR Genie Depletable Plans=Annual Leave,
  HR Genie FTO Gate Exempt Countries=USA (nil-tolerant defaults if absent).
  Evidence: classifier fixtures pass; editor test j-Abphb6Kz-XsQAxH-CD; E2E
  via Genie TEST tab GREEN — Genie ran the tool and correctly applied USA
  exception (job j-AbpkBxCa-oEBmok-CD). Remaining UAT: non-US caller (block +
  exhausted-AL cases) — needs a non-US person chatting with the Genie.
  NOT promoted; handoff in build-specs/BSYS-28314 (as-built rewrite).

- 2026-10-06 Telemetry platform DESIGNED v2 (not built):
  docs/workday/build-specs/HR-GENIE-INTELLIGENCE-PLATFORM-DESIGN-2026-10-06.md.
  Josh rejected v1's scoped-metrics framing: wants TOTAL observability —
  event-sourced ledger of the whole app, every user action + every piece of
  data reportable (anonymized). v2 = App Event Ledger (event-sourced,
  append-only), Telemetry Schema Registry (per-field transform contract:
  categorical/bucket/hmac/bool/features/drop; unregistered = drop+alert),
  value-level arg capture (e.g. PTO type + bucketed duration), Coverage
  Auditor (dark-surface detection vs live discovery), Analyst Genie for
  self-serve queries w/ k-anonymity>=5, Metric Dictionary. Awaiting Josh
  review; Phase 0 = Agent Studio events API fidelity + push-vs-poll +
  feedback surfaces + Insights + cost spikes.
- 2026-10-06 RESEARCH COMPLETE (3 agents):
  project-memory/RESEARCH-HR-GENIE-INTELLIGENCE-PLATFORM-2026-10-06.md.
  (a) Events API live-probed: FULL user/Genie message text, per-LLM-call
  model+input/output tokens, W3C traceparent, UUIDv7 event ids — span
  hierarchy + per-turn cost natively achievable. Feedback exists 4 ways
  (feedback[] filter behind workspace feature flag, post-purge retention,
  UI tab, Event Streams topic Agentic|User Feedback 74141). Agentic Event
  Streams topics exist (56213 notifications, 58868 errors, 74141 feedback)
  — platform-populated? unverified, one probe. Audit log streaming = push,
  schema parity, workspace-admin + pricing gated = Josh decision. HARD
  DEADLINE: Workato purges conversation content 90d after last message.
  (b) Estate: dev handled-error recorder = 76419393 (not 82120578=prod);
  live deflection path 82178793/82179257/82179287; monitoring folder =
  Operational Monitoring 32985204; DARK: check_business_process_status
  (82778233, live on MCP, zero telemetry) + 3 whole planes (inbox pipeline,
  BP completion, PTO detectors/escalators); NO retention sweep exists;
  8 Vegas offset demo clones still running; Genie Enrollment State 0 rows
  despite running writer (verify).
  (c) Benchmark: best-in-class = Langfuse/LangSmith layer (LLM-judge scores,
  agreement analytics, annotation queues, eval datasets/harness, topic
  clustering, per-span cost) — none of it exists natively in Workato =
  whitespace. Adopt k>=10 + complementary suppression, EDPB salt-rotation
  epochs, Presidio entity-count metadata. Design revised to v3.

- 2026-10-06 (evening) BSYS-28314 Option 2 HARD BLOCK BUILT per Chen Yoon decision:
  shared pure classifier FUNC | Time Off Policy Classify (82862012, no
  connectors — data-in/data-out; recipe functions run fixed identity so
  Workday-reading FUNCs were a non-starter); options skill 82839617 refactored
  to call it; submit_time_off_request 78622059 gained a fail-closed guard
  (get_worker→staffing country→balances→classify→if blocked: audit BLOCKED +
  refuse before request_time_off; ALLOWED audit on pass; ERROR audit in
  catch). New audit table HR Genie | Time Off Policy Audit Log (156829,
  d33e94ae-2798-4713-b405-bfe756fe218b). Verified: ALLOWED E2E via Genie TEST
  (job j-AbrAKWKc-d9xkGw-CD, audit row confirmed via wt dt query);
  BLOCKED steering + firm push-through refusal proven at Genie level with
  temporary properties (Depletable=Volunteer Time Off, Exempt=CAN — REVERTED
  to Annual Leave/USA after); cancel + non-FTO regression green; test VTO
  request cancelled. call_recipe pills are ['result'][...] NOT ['output'].
  Remaining: real non-US UAT (first live exercise of the submit BLOCKED
  branch); promotion via managed batch. L3 tenant enforcement dropped by Josh.

- **2026-10-07 Consumer Endpoints PROD promotion SUBMITTED, rejected at intake:**
  dev export manifest **358521 "BSYS-29340 - OOO Endpoint"** (project_path
  Agentic | HR Self Service Genie/Consumer Endpoints); deployment story
  [BSYS-29340](https://workato.atlassian.net/browse/BSYS-29340). Bot rejection
  03:20 UTC "Invalid Manifest … not found in the Workato AHQ | AI Production
  workspace" = env fields SWAPPED on the ticket (10446 target had Development
  31162, 10588 source had Production 31163). Correct map (BSYS-29283-verified,
  now codified in the jira-story-standards skill): 10446 = parent 31164
  Production + child = prod folder path option; 10588 = 31161 Development.
  Prod destination folder **Consumer Endpoints 35712143** pre-created 2026-10-06
  22:19 ET (+ Intelligence 35712144) — but the 10446 cascade child option for
  it did NOT exist in Jira yet (option list lags the prod folder tree or is
  manual) — check the option exists before resubmitting. Manifest
  last_exported_at = null is expected at submission.

- 2026-10-06/07 Intelligence Platform BUILD phase 1 LIVE (Josh approved full
  build; SIEM rail ruled out -> FileStorage redacted transcripts + data-table
  retention tiers instead; k-floor = min cell size 10, k=5 HR-admin view).
  New folder Intelligence Platform (35712141): Telemetry Schema Registry
  (156841, 122 rows, schema v1), App Event Ledger (156842), Collector State
  (156849), Topic Taxonomy (156850, 13 topics), Coverage State (156843),
  FUNC|Emit App Event (82862028, 105/105 green), REC|Conversation Event
  Collector (82862205, 15-min, first pass 25 conv -> 104 events, redacted
  transcripts to WFS), TEST harness (82862165, stopped). Project props at
  PROJECT scope (Salt masked 64-hex, epoch 2026-10, Mode SHADOW).
  Verified: unregistered field -> drop + telemetry_registry_violation row
  (names only); user text with email+longnum -> features only; HMAC actors.
  New platform traps (see workato-platform.md + build-spec 18):
  wt dt create-record double-encodes string bodies -> curl data-tables
  .workato.com {"document":{...}}; Workato API custom connector adhoc maps
  only top-level declared keys; conn 13685697 has agentic admin privilege,
  22080724 401s; genie list items carry gin-handle in `id` not `handle`;
  store_file needs ensure_dir_exists; no DELETE API for env properties.
  REMAINING: Coverage Auditor v1, dark-skill fix (browser-only,
  check_business_process_status 82778233), Ledger Correlator, quality plane,
  reporting plane, Retention Sweeper, SHADOW->ACTIVE gate.

- **2026-10-06/07 BSYS-29314 enrollment-state gate SHIPPED in dev (promotion-ready):**
  thread error table (6,420 HANDLED_EXCEPTION_IN_SUCCESSFUL_JOB on FUNC|Send
  Genie Event prod 82120574) root-caused via prod traces: recipients with no
  Slack/Workato Identity account (sandbox test fixtures — Test Hourly et al.)
  fail "User doesn't have access to Genie" and every notification attempt burns
  the full Slack→Identity→app-link cascade before the platform caps park the
  row. KEY CORRECTION (Josh challenged, recipes proved him right): retry caps
  and terminal parking ALREADY existed — PTO detectors flip to FAILED_PERMANENT
  at `PTO Max Retry Attempts`; Inbox Reconciler (74506733) Pass B →
  Outcome=Undeliverable at `Inbox Task Reminder Max Count` (default 3); Pass A
  already protects deferred/pre-hire workers (fresh Workday re-read; future
  hire date → extend Deferred Until, never send early, never park). Don't
  re-derive "uncapped retry" claims from volume graphs again — read the
  reconciler first. Built: Genie Enrollment State ledger (156515),
  FUNC|Record Genie Enrollment State (82840791, single async writer; 24h
  UNENROLLABLE/INITIAL cooldowns so pre-hires re-probe fast, 1h TRANSIENT),
  Create App Link for User (74253452) records all 4 terminal branches,
  Send Genie Event (74094657) suppression gate → FAILED+
  error_class=RECIPIENT_SUPPRESSED with zero cascade calls; other failures
  carry RECIPIENT_NO_GENIE_ACCESS/DELIVERY_ERROR. UAT via stopped TEST|Genie
  Enrollment Suppression Harness (82862836, force-run only — force_run needs
  the recipe RUNNING, start→force-run→stop; wt rate-limits fast). Live-trace
  evidence in docs/workday/project-memory/INVESTIGATION-Genie-Event-Access-
  Churn-2026-10-06.md. Dev traps hit: AIRO folder picklist table_id wants the
  NUMERIC id (UUID silently breaks dependent schema); new db-table column
  fields only appear after a VALID table_id lands; pre-existing return_result
  steps keep stale schemas after trigger schema edits (get_input_schema
  refreshes them); AIRO dev identity lost project access mid-session (restored
  by Josh); workato-dev.py must run with absolute path (no ./tools/ at repo
  root). Product follow-up flagged: released deferred rows burn 3 attempts in
  ~30-45 min post-hire-date; slow Slack provisioning can kill welcome-class
  notifications as Undeliverable (pre-existing; needs a product decision).

- 2026-10-07 BUILD continued (Josh: "fix everything, keep UI cleanup record"):
  Ledger Correlator (82863111, 30-min) folds usage/outcomes/handled-errors
  into ledger w/ per-source watermarks (first pass: 72 tool_result events);
  Emitter v2 hashes session_id (raw conv ids never stored; pre-v2 rows
  retire via sweeper); Retention Sweeper (82863150, daily 06:15) purge-
  audits ledger + WFS transcripts; Coverage Auditor v2 = code-truth
  instrumentation check (DARK now means truly uninstrumented), QUIET/STOPPED
  statuses, self-healing orphan rows; check_business_process_status
  instrumented + VUA flag repaired VIA API. UI cleanup ledger at
  project-memory/UI-CLEANUP-LEDGER-HR-GENIE-INTELLIGENCE-2026-10-07.md.
  MAJOR playbook corrections: (1) AIRO <REQUIRED FIELD PLACEHOLDER> is a
  pull artifact only, push is SAFE (old browser-only rule retired; verify
  raw JSON after push); (2) real VUA trap = push can strip
  personalization:true from workday_rest config - detect via API read-back,
  repair via direct PUT /api/recipes/:id {name,description,code,config-as-
  json-string}; (3) AIRO push can SILENTLY persist empty trigger + drop
  steps (correlator build) - always raw-verify after push; (4) ruby()
  formula whitelist bans .map/map blocks - use custom-code steps w/
  bindings passthrough (ruby bindings.x.to_json works, .map does not);
  (5) wt dt create-record double-encodes bodies (curl {"document":{...}});
  (6) Orca browser is on AHQ Production workspace, cannot open dev recipes.
  REMAINING: quality plane (LLM-judge/agreement/annotation queue/eval
  harness), reporting plane (Metric Dictionary/rollups/Insights/Analyst
  Genie/digest), Event Streams probe, SHADOW->ACTIVE gate, notification+
  admin-plane emitters.

- 2026-10-07 BUILD session 2 COMPLETE: Quality Judge (82863299, nightly,
  gpt-4o-mini over REDACTED FileStorage transcripts, 30 score events all on
  hashed sessions), Intelligence Rollup (82863448, hourly idempotent ->
  Intelligence Metrics 156862: 707 events / 38 sessions / topic leaderboard
  PAY 13 PTO_POLICY 10), Correlator 2 Notifications (82863630, folds PTO/
  Inbox/BP ledgers -> notification lifecycle events ZERO hot-path edits),
  Weekly Digest (82863670, Mondays 08:00 -> private ops channel via Workbot
  20369210), Analyst Genie (gin-AbrCztoB-bxckro-CD, active, 3 skills:
  query_telemetry_events/get_intelligence_metrics/get_telemetry_coverage,
  privacy-instructed: pseudonym-only, <10 -> band). TRANSCRIPT FILENAMES now
  use session HASH (collector v2) - judge works on hashed pipeline only.
  Remaining: agreement rollup (needs real feedback), annotation queue,
  eval harness, notification metrics in rollup, Event Streams probe,
  SHADOW->ACTIVE, Insights dashboards (Josh UI), promotion handoff.

- 2026-10-07 BUILD session 3 COMPLETE: rollup adds notification metrics
  (notifications_total/sent/failed by class; 289 today: 56 pto + 233 inbox)
  + sessions_by_genie_version (regression slicing; collector v3 captures
  genie_version); Knowledge Gap Miner (82863884) + Gap Queue (156866)
  live, 0 gaps correctly; Event Streams feedback consumer (82863906)
  subscribed to topic 74141, running, forwards platform feedback as Rail B
  (population confirmed with first real thumbs-up); Eval Harness (82863915)
  + Eval Dataset (156867, 5 cases) + Eval Runs (156868) built but DORMANT -
  HARD BOUNDARY: assign_task_to_genie refuses VUA-skill genies, headless
  rejects Dev tokens; regression signal = version-sliced judge scores on
  real traffic instead. Remaining: agreement rollup (needs feedback data),
  annotation queue (Workflow app, UI-only), Insights dashboards (Josh),
  SHADOW->ACTIVE (Josh gate), promotion handoff.

- 2026-10-07 EVAL HARNESS WORKING (Josh overrode my 'hard boundary' - he was
  right): assign_task_to_genie IS blocked for VUA-skill genies, BUT the
  headless-orchestration pattern from the Multi-Genie estate works:
  workato_genie.send_business_event(chat_trigger_handle=<genie chat trigger
  ginct-...>, user_email, notification_text with [EVAL:case_id] marker,
  business_event_data with 'case: <id>') drives the REAL Genie; response
  lands in the Agent Studio conversation; Phase B judge pass matches
  conversations by marker in the AUTO-TOPIC (business_event_data becomes
  the topic, not notification_text!), extracts final agent_message from
  events API, judges vs expected, updates run rows. HR Genie chat trigger:
  ginct-AbbxJxmX-gchtnT-CD (from genie detail .triggers[]). First verified
  run scored 3/5 with honest low scores - the Genie treats business-event
  text as notification, not a user question (real product finding).
  LESSON: 'impossible' platform boundaries deserve a search of the estate
  for a working example before being declared.

- 2026-10-07 EVAL HARNESS v2 MARKER-FREE (Josh caught the artifact): the
  Genie's guardrails DETECT [EVAL:case_id]-style markers in
  notification_text and decline to engage (canned greeting) - so
  marker-era scores (three 1/5s) were artifacts of the harness, not the
  app. V2: send the dataset prompt VERBATIM as notification_text AND
  business_event_data (no marker anywhere the Genie sees; still from
  josh.cramoy@ via chat trigger ginct-AbbxJxmX-gchtnT-CD). Matching without
  markers: judge pass pairs pending runs to conversations by dispatch
  window (ran_at -10min..+1h, earliest-unclaimed-first, author-filtered
  via started_by.email - extend the adhoc HTTP output schema with nested
  started_by/email or the connector won't map it), then VERIFIES first
  user_message == case prompt (boolean match + is_true if-guard) before
  scoring. The guard PROVED itself live: it refused to score a mismatched
  real conversation. Fresh run: 5/5, 5/5, 5/5, 1/5 (real signal:
  identify-manager returned another employee's data - review), 5/5.
  PRINCIPLE: evals must be indistinguishable from production traffic;
  markers belong in YOUR tables, never in the agent's input.
- 2026-10-07 INSIGHTS DASHBOARD AUTOMATION COMPLETE: 4-chart dashboard
  (idb-AbrEEP4W-4EcChp-CD) built fully via Orca browser. Key techniques:
  (1) adding a chart to the canvas needs REAL OS-LEVEL DRAG (orca mouse
  move/down/move-steps/up) - synthetic DragEvent AND MouseEvent sequences
  are both ignored by the editor; (2) modal dropdowns: atomic async eval -
  open w-select via elementFromPoint + full MouseEvent sequence
  (pointerdown/mousedown/pointerup/mouseup/click), poll <=12x350ms for
  option ROW [class*=option], click ROW center; (3) 'Select value' is NOT
  a w-select - it's w-collapsible-multi-select-value, target by
  coordinates; (4) the condition dropdown sometimes spawns a stray second
  filter row instead of committing - re-pick, then delete stray via trash;
  (5) chart title: focus + native HTMLInputElement setter + input/change
  events, and RE-VERIFY after 'Save to page' (title can silently revert);
  (6) source picker is a two-level cascade (Workspace data -> Data tables
  -> table); (7) viewport 1231x838 CSS, screenshots 2x DPR, displayed-2000
  coords *0.6155. Topic demand chart = Intelligence Metrics metric_name
  'user_turns' with dimension=topic (user_turns has no 'all' row).

- 2026-10-07 UNBLOCK PASS (Josh: 'unblock everything, take it across the
  finish line'): (1) case-004's 'wrong answer' was a JUDGE FALSE-POSITIVE -
  the genie correctly answered 'Who is my manager?' and gpt-4o-mini scored
  the manager's contact details as 'another employee's data'. Rule: eval
  rubrics AND judge prompts must state that surfacing the CALLER'S OWN HR
  data (manager contact, balances, payslips) is desired correct behavior.
  Re-judged 5/5. (2) Gap queue unblocked by design: seed the dataset with
  off-KB probe cases dispatched as natural prompts -> collector marks
  UNKNOWN -> miner clusters (demand 5 incl. 2 real unknown turns) -> judge
  honestly scores kb_miss on the probes. Gap row: pattern withheld, pointer
  to redacted transcript. (3) HR Genie conversation list serves HEAVY real
  traffic (~100 convs/15min, page 1 spans ~15 min) - any consumer that
  fetches 'recent conversations' MUST paginate backward from the newest
  with cursor chaining; probed: no order=asc, no author filter param, and
  nested started_by does NOT map through adhoc connectors (top-level keys
  only, confirmed again). Fixed 3-page chain covers 30-min cadence.
  (4) Feedback plane probed to certainty: Agent Studio feedback filters
  WORK (flag on, UI+API) but ZERO feedback exists in 30 days; no API write
  path (POST /feedback 404); conversation UI read-only; the genie's Slack
  app lives in the BT workspace (not reachable from Workato-Slack MCP,
  browser, or exposed desktop windows). First-ever human thumbs-up is the
  arm switch for agreement% + Event Streams topic population.

- 2026-10-07 DEV MCP WIRED: HR Genie Intelligence (Dev) mcps-AbrGbzWN-3Af-CD
  at https://30188.apim.mcp.workato.com — 3 analyst tools
  (query_telemetry_events, get_intelligence_metrics, get_telemetry_coverage).
  TRAPS: (1) AIRO mcp_server_create REJECTS workato_genie tools (skills
  only); (2) the source workato_skill recipes MUST BE RUNNING or the wire
  server advertises capabilities:{} and every call returns 'tools not
  supported' — starting the 3 recipes fixed it live; (3) token auth: MCP
  settings → Access Method → Token-based → Create new token → URL becomes
  ?wkt_token=<hash> (shown once); (4) wired into Claude Code via `claude mcp
  add --transport http <name> <url-with-token>` (project-local); (5) tool
  params validate as strings over the wire (limit:"5"); (6) smoke-test
  recipe: POST JSON-RPC to <url>/mcp?wkt_token=... — initialize then
  tools/list/tools/call, stateless (no session header needed).

- 2026-10-07 NAMING RULE (Josh, hard): NOTHING named TEST outside the dev
  cycle - even in dev, permanent consumers must never carry TEST| names.
  Renamed TEST | Event Streams Feedback Probe -> REC | HR Genie | Event
  Streams Feedback Consumer (stop -> rename -> start); deleted the TEST |
  Telemetry Emit Harness fixture (UAT evidence already recorded in Jira).
  Post-cleanup auditor run: 16 COVERED / 10 QUIET / 2 STOPPED / 1
  UNINSTRUMENTED_OFF / 0 DARK.

- 2026-10-07 FEEDBACK LOOP CLOSED (the last data-blocked item, unblocked):
  Event Streams topic 74141 DISCONFIRMED - a REAL confirmed thumbs-up
  (testing-group rep, has_positive filter) produced ZERO topic events after
  5+ min; the probe recipe stays running as the population canary. Built
  REC | HR Genie | Feedback Poll Consumer (82872626, 15-min): polls the
  conversations feedback filter (has_positive/has_negative - the ONLY
  surface exposing thumbs; detail API exposes NONE), dedupes vs a
  collector-state cursor (feedback_consumer row; token scan
  conversation-<id>:[pn] - NEVER JSON-parse the Ruby-inspect state blob,
  escaped quotes + Time objects break it), emits ledger feedback events
  via the emitter. First run: 3 real events (1 pos / 2 neg). NOTE: two
  force-runs raced a scheduled tick and double-emitted; deleted the dupes
  by record_id. Digest agreement section auto-armed (overlap % lands when
  the nightly judge samples a feedback'd session). ALSO FIXED: rollup
  metric_date binding was MISSING (all metric_keys landed under empty date
  -> digest showed adoption zeros); added code_input metric_date=
  today.strftime('%Y-%m-%d'), deleted 35 stale dateless rows, digest now
  shows Conversations 101 / turns 103. gw-semantic watchdog false alarm
  fixed (it counted workspace_learning_candidates 155485 - miner STAGING,
  2.4k pending - as the flywheel queue; real queue is 156859 pending_canary,
  fully drained: 4 promoted / 2 retired); failure spike 54/hr -> 2/hr.
  Copy 82868967's schedule STILL never registered (platform-side new-
  schedule stall; recipe runs fine on demand) - support ticket pending.

- 2026-10-07 ANALYST GENIE SLACK WIRING (the 'wired to nothing' gap, 90% done):
  the Analyst (gin-AbrCztoB) had ZERO triggers - active+skilled but
  unreachable. Driven the Add a Slack trigger wizard to its last step:
  Slack app 'HR Genie Analyst' CREATED (A0C89EVARR6, Workato workspace,
  manifest prefilled by Workato: right scopes + event webhooks), app
  credentials saved into the wizard (Client ID/Secret/Signing Secret),
  custom OAuth profile 46093 auto-created with 1 shared account. Wizard
  LEFT OPEN at 'Create Slack trigger'. ONE HUMAN STEP REMAINS: Josh clicks
  'Create Slack trigger' (pops the start_auth OAuth) then Allow in Slack -
  the start_auth spinner is the KNOWN dead end for automation (slack-bot-
  connection skill: only Josh's real-browser click completes it; manual
  authorize URLs fail with 'Unknown/invalid shared account'). GOTCHAS for
  the drive: (1) synthetic clicks don't count as user gestures - popups
  get blocked ('Browser has blocked new window'); (2) the Slack manifest
  dialog's workspace selector: real-click then screenshot-read the options
  (keyboard Down/Enter lands on the first option 'Workato BT AI' - WRONG
  for internal genies; pick 'Workato'); (3) the Slack 'Click here to
  verify' URL check FAILS until the trigger exists (endpoint 404s
  pre-registration) - verify AFTER creating the trigger; (4) eval and
  screenshot surfaces DIVERGED mid-session (stale rendered frame vs live
  DOM) - trust eval + wt API, not stale screenshots.

- 2026-10-07 ANALYST SURFACE DECISION (Josh): the Analyst Genie is NOT
  Slack-facing (unlike HR Genie the employee surface). Slack trigger wizard
  CANCELLED before creating a trigger; analyst stays reachable via (1)
  Agent Studio chat (native, already there) and (2) the hr-intelligence-dev
  MCP tools (3 telemetry skills in Claude Code). The orphan Slack app
  A0C89EVARR6 (created, never installed) + custom OAuth profile 46093 stay
  dormant/inert — delete via Slack app settings + Workato UI if wanted.
  RULE: Slack surfaces are for EMPLOYEE-facing genies; internal analyst
  tools surface via MCP + Agent Studio.

- 2026-10-07 TRANSCRIPT ENCRYPTION AT REST (Josh: FileStorage is
  workspace-wide, conversations too sensitive for plaintext at rest):
  envelope encryption via AES-256-GCM. Key = project property 'HR Genie
  Transcript Key' (64-hex, project 15643451; per-env, never promotes —
  same model as the pseudonym salt; created via Dev CLI `workato
  properties upsert --project-id N --property K=V`, wt's --data shape
  400s 'Missing parameter properties'). Collector step 12 encrypts
  (base64(iv||ct||16-byte auth tag), random IV per file) and writes
  <session_hash>.txt.enc; Judge step 7 decrypts with auth-tag check —
  TAMPERING FAILS LOUDLY. Migration recipe REC | HR Genie | Transcript
  Re-encrypt Migration (82884094, 60-min cadence but force-run per env):
  search dir → skip .enc → encrypt → store .enc → DELETE plaintext .txt;
  idempotent. VERIFIED end-to-end: collector writes .enc, judge
  decrypts+scores (3 score events on a decrypted transcript).
  GOTCHA THAT BIT: the new encrypt/decrypt steps lacked mask_data —
  plaintext transcripts appeared in JOB TRACES until masked (trace
  retention ages them out; forward-masked). GOTCHA: pulling a second
  recipe into the same builder session silently replaces the working
  copy — collector edits were lost and had to be re-applied (session
  holds ONE recipe; use one session per recipe for multi-recipe edits).

- 2026-10-07 JIRA TREE + CONFLUENCE DOC: 8 child stories filed under
  BSYS-29352 (Relates links): BSYS-29369 write path 5pt / 29370 collector+
  encryption 5pt / 29371 correlators 3pt / 29372 auditor+sweeper 3pt /
  29373 judge+eval 5pt / 29374 gaps+feedback 3pt / 29375 surfaces 5pt /
  29376 promotion readiness 3pt (= 32 pts + umbrella 8pt). All bare-create
  then editJiraIssue (description double-escape trap), all verified
  rendering. Confluence: 'HR Genie Intelligence Platform' sub-page of HR
  Genie Architecture Overview (page 2938175596, space extbt/BTI id
  105054224) — full 11-step data flow + privacy model + state. GOTCHA:
  Confluence createConfluencePage with contentFormat markdown stores
  markdown as LITERAL text in one <p> — use contentFormat html (read the
  getContentFormatGuide first); space key 'extbt' resolves to numeric id
  105054224 for the API. Atlassian MCP 403 'app is not installed' is
  TRANSIENT (dropped mid-session, recovered ~20 min later without
  re-auth).

- 2026-10-07 SINGLE PANE DONE: dashboard idb-AbrEEP4W-4EcChp-CD now 9
  charts (added: outcomes verified, feedback thumbs, gap queue direct
  source, notifications by type, genie versions). Rollup additions:
  feedback_total + feedback[pos|neg] metrics; rollup reads today DESC
  (day volume exceeded the 1,000-row page — dev inflated by notification
  backfill; prod volumes fit; scale pagination = BSYS-29307-class item).
  Dashboard-chart drag drop target must be a VISIBLE canvas area (drop
  below the fold does nothing). Director of People Ops = the audience;
  zero maintenance (all live reads).

- 2026-10-07 DASHBOARD VISUAL REBUILD (Insights editor, Orca): chart-type
  conversions live — Conversations per day → LINE, Topic demand → PIE,
  Human feedback → PIE, Judge score averages → BAR; noise columns
  unchecked on all 5 tables (telemetry keeps asset_name+event types;
  genie versions/notifications/self-serve keep dimension+metric_value;
  gaps keep topic+demand_count). Two KPI cards in an orange section
  Container with a Text block ("01 ADOPTION —…"): "Conversations ·
  today" (conversations_total) + "User turns · today"
  (user_turns_total) — Labels set via the chart editor's Label field
  (fixes the default "metric_value" caption). TECHNIQUES: when orca
  mouse click no-ops on Workato buttons, use press-emulation (move →
  down → 150-300 ms → up) — that's what actually opens "Edit chart
  data" and picks dropdown rows; Backspace deletes the selected chart
  (trash icon clicks are unreliable); card selection is sticky — always
  verify WHICH chart the editor holds (read the Label input) before
  editing; CATEGORIES/Data-column dropdown for pie grouping would NOT
  accept option selection by any click/keyboard method (pie groups by
  metric_key composite "2026-10-07|user_turns|BENEFITS" instead of
  dimension/topic — cosmetic, follow-up).

- 2026-10-07 DASHBOARD SECOND PASS (Josh: "not enough columns, all
  whacked"): the trim pass had gutted the narrow tables (dimension-only,
  counts cut off by the card width) and the container dwarfed the KPIs.
  Fixed by: deleting the Genie versions chart (aria-label toolbar:
  Edit/Clone/Select parent container/Delete — query + press-click exact
  coords; Delete WORKS, trash-icon guesswork doesn't), converting the 3
  narrow tables to PIE (legends show category+count+% so numbers survive
  any card width), stretching the orange container to full row and both
  KPI cards wide inside it (resize handles =
  .lcap-widget-editor__resize-handle — query live coords, container edges
  resize reliably, free-chart edges barely), and redistributing charts
  left/right by dragging the toolbar 6-dot handle (auto-flow reflows
  everything after each move). CDP screenshots can DIE mid-session
  ("Screenshot timed out — tab may not be visible") while eval + DOM
  probes keep working: verify layout via element positions + svg counts,
  not pixels. STILL COSMETIC: pie legends group by metric_key composite,
  axis labels metric_value/metric_date (CATEGORIES dropdown rejects
  automation), needs two human clicks in the editor.

- 2026-10-07 DASHBOARD COST RULING (Josh): an hour and a half of Insights-
  editor automation was the wrong spend — "editing a dashboard should be an
  easy task." The new dashboard (idb-AbrbGR8C-bNwDAk-CD, replaces
  idb-AbrEEP4W-4EcChp-CD) is saved with 5 clean charts (2 KPIs, line,
  telemetry table, topic pie grouped by dimension) and STOPS THERE. The 5
  remaining charts (feedback pie, judge bar, notifications/gaps/self-serve
  tables) go to Josh as a 10-minute manual checklist, NOT automation.
  AUTOMATABILITY LEDGER for the Insights editor (what worked / what died):
  WORKS: press-click emulation (move→down→200-300ms→up) for toolbar
  buttons + dropdown rows; palette drag with drop ONLY on empty canvas;
  CodeMirror setValue for text blocks; native-setter for Title/Label
  inputs; checkbox columns via real clicks; chart editor "Save to page"
  persists; per-chart search-trick for dropdown options. DEAD ENDS: free-
  chart resize handles (only containers resize reliably); palette drags
  while any modal/dropdown is open (drops vanish or land in the modal);
  search_in_open_dd types into the PALETTE search when no dropdown is open
  (bricks the palette until cleared); stale z-stacked duplicate cards from
  drag chaos (saves land on the wrong instance — rebuild, don't repair);
  unsaved drops evaporate on reload (Save to page or lose them).
  SUPPORT TICKET DRAFT (2 items: recipe 82868967 schedule stall; Event
  Streams topic 74141 non-delivery) at /tmp/support-ticket-draft.md —
  awaiting Josh's go to file externally.

- 2026-10-07 SUPPORT-TICKET CORRECTION (Josh: "can't we fix or monitor
  this ourselves?"): NO EXTERNAL TICKET. (1) Recipe 82868967 is
  gw_semantic_alert_autopsy_responder — a GOOGLE-SEMANTIC project asset
  (project 17981834, #gw-semantic-alerts watcher), NOT HR Genie; it was
  mis-filed as a promotion blocker by session adjacency. Its schedule
  stall IS real and repeated (original 82866722 stalled in stop/edit/
  start churn; the fresh-scheduler copy 82868967 also never registered —
  2 consecutive = probable platform scheduler bug), but the responder
  runs fine on demand and nothing depends on its clock. If it ever needs
  a reliable cadence: wire it into the launchd fleet (wt force-run every
  15 min), don't wait on the platform. (2) Event Streams topic 74141:
  already routed around (poll consumer live, canary 82863906 watching) —
  zero dependency. GRADUATION RULE: a THIRD unrelated recipe stalling
  its schedule = real platform regression, ticket with 3-repro story.
  Draft kept at /tmp/support-ticket-draft.md (throwaway).

- 2026-10-07 FILESTORAGE "EMPTY" MYSTERY + PATH-CASE FIND: Josh's empty
  /hr-genie-telemetry view was just the "HR" name filter — transcripts are
  named by session hash (hex .txt.enc), no "HR" substring, so the filter
  hides every file and matches only the directory. REAL BUG FOUND WHILE
  VERIFYING: the retention sweeper (82863150) hardcodes
  'hr-genie-telemetry/redacted-transcripts/Development' (capital D,
  plaintext-era casing) while the collector builds its path from the
  'HR Genie Telemetry Environment' property (lowercase today) — if both
  casings exist as dirs, the sweeper watches the OLD tree and never
  purges the live one. Fix: sweeper should read the property, not a
  literal. FileStorage search is name-only (no content search); the
  files API v2 (/api/v2/files) 404s in this workspace — UI or
  search_files-in-recipe are the only listing paths.

- 2026-10-07 PATH-DISCREPANCY FIX: VERIFIED ZERO DISCREPANCY (corrects
  the entry above — the sweeper does NOT hardcode the path; that was the
  property's RESOLVED value in the job trace, masking hides property
  values in property_list so they read as blank). AUDIT RESULT: all four
  FileStorage-touching recipes (collector 82862205, sweeper 82863150,
  judge 82863299, migration 82884094) derive the tree from the same
  'HR Genie Telemetry Environment' property (= "Development", capital D
  — that IS the canonical casing). Sweeper force-run j-AbrdgGzK proof:
  search_files via property → 100 files, ALL .txt.enc (migration
  completed 11:13), ZERO plaintext, 0 expired, purge-audit emitted.
  ACTIONS: one-time migration STOPPED (was scheduled hourly forever —
  perpetual-bot violation); sweeper verified live + running (daily
  06:15); collector running (15 min); judge path property-driven.
  LESSON: job-trace resolved values are not hardcoded literals — pull
  the recipe DSL before claiming a path bug. FileStorage UI renders
  stale/empty listings unreliably — the trace is ground truth.

- 2026-10-08 CONFLUENCE DOC TREE (Josh: one overview + module child pages):
  RESTRUCTURED — overview 2862809419 (v3) is now: at-a-glance + one-line
  flow + MODULE MAP table linking 5 children + shared principles +
  ownership + status. NEW children (all under the overview, extbt/BTI):
  2939093004 Conversational Self-Service and Skills (front door, skill
  catalog table, VUA identity paths, experience contract); 2939650050
  Proactive Notifications and Lifecycle Tracking (2 pipelines table,
  delivery-state-not-truth, enrollment gate BSYS-29314, reconciler);
  2939355140 Action Safety and Live Validation (4-point recheck, action
  requirements table, currently-awaiting doctrine); 2938961957 Knowledge
  Base and HR Service Fallback (governed KB, JSM path, verified outcomes,
  OOO API BSYS-29340); existing 2938175596 Intelligence Platform kept.
  Prod Deployment Checklist (2745008431) stays a sibling, linked from the
  overview. All content preserved from v2 (deep sections moved into
  children verbatim-in-spirit, nothing dropped); Josh's voice throughout;
  HTML format (markdown format stores literal text — known trap). TOC
  worth adding later if the tree grows past ~8 children.

- 2026-10-08 OPERATIONAL MONITORING child page added (2940272642): what-
  watches-what table (auditor/sweeper/watchdog/morning-brief/canaries),
  five coverage states (COVERED/QUIET/STOPPED/DARK/UNINSTRUMENTED_OFF,
  DARK = the only P2), audited-deletion retention, autopsy discipline
  (origin step, 54→2 failures/hr story), the alerting contract (P1/P2/
  self-heal/report-only), monitoring-the-monitoring. Overview module map
  now 6 rows (v4). TRAP: writing HTML with literal mdash entities slipped
  into v1 of the page (the voice rule bans em dashes) — caught on
  read-back, fixed v2; the guardrail re-read step earns its keep for
  voice rules, not just markup.

- **2026-10-08 BSYS-29429 provisioning-grace build SHIPPED in dev (promotion-ready):**
  follow-up to BSYS-29314: delivery attempts now count only when delivery was
  actually possible. Inbox Reconciler (74506733) Pass A + Pass B failure paths
  classify via Dispatch's new error_class passthrough (82059061 result schema)
  + enrollment-ledger first_seen_at vs new project property `Inbox Task
  Provisioning Grace Days = 14` (created via `wt api POST /api/properties
  ?project_id=... --data '{"properties":{"Name":"14"}}'` — property-map body +
  project_id QUERY PARAM; the knowledge note saying properties are UI-only is
  superseded). Unprovisioned+in-grace → error note only, attempt NOT consumed
  (row stays retry-eligible until provisioned); unprovisioned past grace OR
  cap-reached real failure → UNDELIVERABLE/Undeliverable (Pass A zombie state —
  deferred rows that silently stopped processing at cap — is dead). UAT green
  via forced reconciler runs on rebuilt fixture (sam.allen+test row
  6256e5f7): attempts stayed 0 through a full forced pass (grace), then
  backdated first_seen → UNDELIVERABLE (expiry). TRAPS: (1) builder
  conditional-if chains are SEQUENTIAL not exclusive — an existing if/else's
  ELSE still runs after a preceding if matched; gate its update fields with
  the same classification formula (increment/no-increment + note label) rather
  than trusting the if above; (2) else-blocks nested inside another if's
  TRUE-branch reject add_step/move ("not a container") — fold the logic into
  the existing update's field formulas instead, and place a lookup step inside
  the try container (parent=monitor step number works); (3) every
  recipe_builder insert RENUMBERS subsequent steps and their variable names —
  re-derive pill names (call_recipe_40→41) AFTER each insert or pills render
  None_None; (4) data-tables REST: PUT/POST /api/v1/tables/{uuid}/records[
  /{record_id}] {"document":{field:value}}; wt dt needs UUID not numeric id.
  Enrollment writer preserving first_seen_at on update is what makes the
  grace window sound — do not "fix" the writer to refresh it.

## FY27 Year-End / Leapsome integration (2026-10-08, PLANNING COMPLETE + PHASE 0 PROBES DONE, pre-build)

- **Plan:** `~/Documents/Workday/build-specs/PLAN-FY27-YEAR-END-LEAPSOME-INTEGRATION-2026-10-08.md` (now includes the Phase 0 probe-results section);
  **handoff/resume:** `~/Documents/Workday/project-memory/HANDOFF-FY27-LEAPSOME-PLAN-2026-10-08.md`.
  Source: "FY27 Year End Optimization Requirements" gdoc (1IvdeZfDC4J9TW-P-QcrFwUOMC_4ANcMHiLIGqZdULkc) — 3 areas: promotion nominations, 9-box ratings, responsible-AI review checks. Deadline: dev-UAT + guidelines by Nov week 1; Dec cycle launch.
- **Josh's locked decisions:** HR Genie primary surface (not PM Genie); phasing 1→2→3; **submission CORRECTED 2026-10-08 evening: the requirements doc explicitly KEEPS the Google Form** ("Start with the current Google Form", Apps Script FormResponse bridge to be tested, competency upload replaced by Leapsome data, fallback = prefilled-link form-completion step) — data table = ledger/idempotency/audit, bridge = primary submit path if green, Sheet never appears in the doc (evidence inputs only); policy in FY27 Cycle Config table + project properties. **BUILD DEFERRED to Josh's 10/15 call** with the requesting team (8-question decision pack in the plan; ~4-5 pts of submission-independent scope — config schema, resolve_nominee, competency-evidence gate — can start early on his go).
- **Estate discovery:** Leapsome already integrated outside HR Genie — custom connector `leapsome_connector_748504_1726020954` (637599, generic adhoc HTTP), connection **[PER] Leapsome 19006083** active in dev; 13 running "Leapsome: ..." MCP skills folder 31530739 project 15317113 (Get Reviewee Overview 73290823, List Review Cycles 73290820, List Review Participants 73290822, List Employees 73291906 + goals/feedback writes); **Performance Management Genie v2 gin-AaD4awRp-4xXomC-CD** (started, 17 skills) = the doc's "Claude Performance Review Assistant". Older estate folders 29801476 + 31225099 (stopped). Jira: nothing filed; GAS-52 (James Allen) adjacent.
- **PHASE 0 PROBE RESULTS (probe recipe 82919752, STOPPED; jobs j-Abs4EpJo-AAEwtp-CD + j-Abs4MrBk-rwMseN-CD):**
  conn 19006083 = **PROD Leapsome** (1,380 employees — dev builds read live data, mask from day one; prod ws needs its own conn at promotion). Admin token **
- **Traps deposited:** AIRO `recipe_builder_init` creates an EMPTY shell recipe and `recipe_builder_save` then creates the real one under a SECOND id — delete the shell (82919741 deleted); cron-scheduler probes: `wt recipes start` + `force-run` works, `poll-now` is a no-op for cron triggers; adhoc custom-connector fields unlock progressively (mnemonic+verb first, then response_type/path/output, then input.schema, then input.data.*); "input.schema missing" sticky warning is cosmetic for paramless GETs.
- **Sub-docs READ 2026-10-08 evening** (Josh shared them + VUA identity back to josh.cramoy@): nomination form = the Area 1 payload schema (4 rationale pillars, IC/PM question, level +1 guidance, mandatory Leapsome Competency Assessment PDF, explicit leadership-support Yes/No/Other, chain-based delegate rule — in-chain leader may submit while manager OOO); FY27 review forms doc = label sets: skill-development **Developing/Skilled/Excelling** with quantified competency-percentage definitions (>30% below / 80%+ at-above / 70%+ above-none-below), goal-achievement **Below/On/Above Target** (P&E variant rewords to performance/deliverables; Sales question NEW in FY27), competency scale **Below/At/Above Required Level** (dynamic per employee). Full deltas in the plan's "Sub-doc contents" section. PREVIOUS MISDIAGNOSIS resolved: the sub-doc RECONNECT_REQUIREDs were a sharing-403 alias, not tokens (parent doc read fine throughout; diagnostic rule deposited in google-semantic-mcp.md).

## Phase 2 research: two-way Slack ⇄ JSM interactivity (2026-10-08, feeds unticketed Phase 2 of r52/BSYS-27775)

**BT Genie reference architecture** (dev ws 3535597, project 10615261 "[GENIE] [BTG] BT Genie",
folder 21479670; subfolders "JSM Triggers" 29090923 + "Slack" 28676079). Five running recipes:

- **Join table 57271 "Conversation Metadata"** — the linchpin: conversation_id (primary),
  user email/name, **Slack thread_ts** (16282931-…), channel_id (f60b5113-…), **Jira ticket key**
  (1f58b52b-…), origin, boolean flags (manual-assist). This is exactly the BSYS-27775 schema
  (closed Won't Do → does NOT exist for HR yet; Phase 2 starts by building it).
- **Inbound router 68926526 "Process message from Slack"** — Workbot `new_event(message)` trigger;
  lookup conversation by `thread_ts.presence or ts`; skip own-bot/Assist messages; approved-channels
  project property OR `D`-prefixed DM channels; if record already has ticket key → call writer
  function; else new conversation → ":loading:" placeholder → `assign_task_to_genie(conversation_id=…)`
  → replace placeholder with response (ts= placeholder ts updates in place) → upsert join record.
- **Comment writer 69457185 (recipe function)** — params ticket_key/user_email/slack ids;
  JSD `GET request/{key}`; `conversations.replies` for exact text; `jira.find_user` by email →
  accountId; rewrites Slack `<@U…>` mentions to `[~accountid:…]`; adds mentioned users as JSM
  **request participants** (`POST request/{key}/participant`); attachments via JSD
  `attachTemporaryFile` → comment-with-attachment; else `jira_service_desk.create_comment(public=true)`
  with `*Comment by [~accountid:X]:*` attribution prefix.
- **Outbound 71077131 (new JSD comment)** — Jira webhook → join lookup by ticket key → skip if
  no record/no thread_ts → skip if comment `public != true` (internal comments never forwarded) →
  resolve author email → Slack identity → `chat.postMessage` into stored thread_ts/channel with
  **username+icon_url spoofed to the author** → JSD comment attachments (`X-ExperimentalApi: opt-in`)
  uploaded to the thread.
- **Outbound 71074365 (status changes)** — same shape; resolution/statusCategory=done handling;
  origin branch: Slack → thread post, GO → GO notification.

**Platform fact (docs, channel-support)**: genies natively receive full thread history and respond
to every message in a thread they participate in; `assign_task_to_genie(conversation_id=…)`
continues an existing conversation (BT uses this for in-thread continuation).

**HR design options** (full comparison delivered in session 2026-10-08):
- **A. Genie-native (recommended)**: join record written by create_hr_ticket skill flow; outbound =
  Jira webhooks → lookup join → `Send Genie Event`/assign_task_to_genie into the SAME conversation_id
  (update lands in original DM thread, genie identity, preserves conversation-per-notification audit);
  inbound = native thread-reply continuation + new genie skill "comment on JSM ticket" (public comment,
  accountId attribution, participants). No Workbot router, no chat.postMessage leg (T2 rejection honored).
- **B. BT mirror**: Workbot router + chat.postMessage spoofed-author posts. Rejected for HR: T2-style
  Slack identity split + kills conversation-per-notification audit surface.
- Verify-in-dev risks: (1) does the messenger choke point 74094657 / genie event support targeting an
  existing conversation_id vs always creating one; (2) do employee replies in genie DM notification
  threads actually re-trigger the genie (test on HR Genie 2 only); (3) HROPS employee-as-JSM-customer
  resolution via jira.find_user; (4) comment-author attribution = bot account, prefix required.

## BSYS-27772 label part CLOSED in dev (2026-10-08) — hrgenie label on Genie-created JSM tickets

- create_hr_ticket (74304659→74349819, [URL](https://app.workato.com/recipes/74349819)) now tags every
  ticket it creates with label `hrgenie`. **Platform fact: JSM create-request API REJECTS labels —
  `400: The field 'labels' is not valid for this request type` (requestFieldValues only accepts fields
  on the request-type form; proven by failed test job j-Abs3gHzQ-k8h4WX-CD).** Labels must be set
  post-create via the platform issue API: new steps 12-14 = WorkatoMonitor(retries=0) wrapping
  `jira.update_issue(labels="hrgenie", project_issuetype="HROPS--Questions for HR")` with an EMPTY
  catch (swallow + continue) so a label failure can never fail an already-created ticket (AC 12/13).
  Empty catch = intentional; the EmptyBlock inconsistency warning is cosmetic and pushes fine.
- **E2E evidence**: HR Genie dev test chat sabbatical-escalation → job j-Abs3mJ3J-YcmHNT-CD:
  create OK (HROPS-232, raiseOnBehalfOf = Josh), update_issue labels OK, recorder fired, skill returned
  success + key/URL, Genie confirmed to employee. HROPS-232 = sandbox test artifact. Jira comment posted
  on BSYS-27772 (1133201). Recipe left Running in dev; VUA/MCP wiring untouched (no personalization on
  this recipe — shared Jira connections by design, identity via trigger context).
- project_issuetype picklist ID convention: "PROJECTKEY--IssueType" ("HROPS--Questions for HR");
  request type "HR Genie" (1358) maps to issue type "Questions for HR". Picklist discovery via
  recipe_builder_get_picklist(field_path="project_issuetype", parent_id="Global People Operations@@HROPS").

- **2026-10-08 BSYS-27771 ticket-creation challenge SHIPPED in dev (instructions-only):**
  Josh's ask: the Genie should push back on direct "open a ticket" asks (KB-first,
  self-service offer, not belligerent). ROOT CAUSE was one clause in the genie
  gin-AYbxpMha-YenKAJ-CD job description: "OR the employee explicitly asks you to
  escalate or open a ticket (even for something you could otherwise help with)"
  routed direct asks straight to create_hr_ticket with no KB check. Fixes (UI
  builder edit, genie_update still banned): classifier item (3) requires the
  KB/self-service check before filing; direct asks treated as "a request to be
  checked, not an order to execute" (one plain offer, no arguing, honor the
  choice); decline window hardened ("wait for their reply before calling
  create_hr_ticket — never create the ticket in the same message where you
  announce it", implements parent BSYS-27769 AC 5/6). VERIFIED 3 tests in the
  TEST tab: PTO-balance ticket ask → challenge + KB check + two tool runs +
  answer, no ticket; parking-pass ask (uncovered) → KB check → escalation →
  HROPS-233 filed in sandbox JSM (ran pre-hardening, filed same-turn; the
  decline-window sentence fixed that); "never mind" → no ticket, 1 LLM call.
  create_hr_ticket 74349819 untouched. Ticket re-described as-built, 2 pts,
  comment 1133222. Genie job description rides the next dev-to-prod cycle.
  Jira comment also flags HROPS-232 + HROPS-233 as sandbox test artifacts.
  ORCA TECHNIQUES for genie builder + TEST tab: (1) genie page is a BUILD/TEST
  SPA — the toggle text is "Build"/"Test" (title case) in the current UI, top
  center ~y=42; (2) job description Edit opens a plain textarea (~34k chars) —
  native setter + input event works for BOTH reading and writing; dump via
  JSON.stringify(ta.value) and re-parse the orca JSON properly (find-based
  slicing breaks); python len() counts code points, value.length counts UTF-16
  units — a small mismatch is emoji surrogates, not drift; (3) in the TEST tab
  there are TWO visible textareas: "Ask AIRO anything" (sidebar) and "Ask Genie
  anything" (chat) — DOM order picks the AIRO box first; always select by
  placeholder, and SEND via the accessibility snapshot's button "send" ref
  (orca click --element eNN); press-emulation on coordinates hits the wrong
  icon and Enter on the synthetic value does nothing; (4) stray clicks can
  NAVIGATE the tab off Workato entirely (landed on id.atlassian.com from a
  stale ref) — re-goto the genie URL, the Workato session survives; (5) verify
  saves by reopening the Edit dialog and reading the textarea, not by the page
  preview (collapsed, won't contain deep changes).

**Messenger code fact (2026-10-08, resolves verify-risk #1):** FUNC | Send Genie Event 74094657
delivers via `workato_genie.send_business_event(genie_id, user_email, notification_text,
business_event_data, chat_trigger_handle)` — NO conversation_id param, so every send spawns a NEW
conversation/thread. Continuation exists as a different native action: `assign_task_to_genie(
conversation_id=…)` (BT-proven for in-thread delivery). Phase 2 messenger extension = new mode
"ticket_update" (or param) calling assign_task_to_genie with the join-record conversation_id,
carrying the READ-ONLY guard wrapper; keeps choke point (Test Send Email override, error classes,
enrollment suppression gate) intact. Remaining probe: whether assign_task_to_genie on a
Slack-chat-interface-bound conversation AUTO-RENDERS the reply in the native DM thread (BT's genie
has no chat interface — their recipe posts the response itself, so their wiring proves nothing
about interface-bound rendering). If it does not auto-render: fallback = per-update threads via
send_business_event (each JSM update = new notification thread, still interactive) — degraded but
workable. Also note BT needed their Workbot router ONLY because BT Genie lacks a Slack chat
interface binding; HR Genie owns one, which is what makes the router-free design possible.

## Phase 2 BUILT in dev (BSYS-29430, 5 pts, UAT since 2026-10-09) — Slack ⇄ JSM two-way interactivity

Architecture settled on **App Events Continue Conversation** (Workato's own documented pattern for
exactly "a ticket they created was updated"), NOT assign_task_to_genie (headless, no thread, VUA-
incompatible — "platform constraints, not configuration choices"). Built:

- **Data table 157888** `HR Genie | JSM Ticket Conversation Map` (folder 32092194 "JSM"):
  ticket_key (primary, 37c5bdad-…), genie_conversation_id (36bb6f0f-…), requester_email
  (9504504a-…), requester_name (a39ce201-…), ticket_created_at (30f65c27-…).
- **create_hr_ticket 74349819** (+): step 16 upsert into 157888 (ticket_key=issueKey,
  conversation_id/user_email/user_name from skill trigger context, created_at=job_created_at),
  placed between the deflection recorder and the workflow_return_result inside the else body.
- **FUNC | Send Genie Event 74094657** (+): trigger schema gained optional `conversation_id`
  param + mode hint `ticket_update`; both notify-branch send steps (6, 18) pass
  `conversation_id = test_override.has('@') ? nil : param` — continue-conversation must be
  DROPPED under test routing (the conversation belongs to the original requester). Editor
  open+Save (Orca) done for function-schema re-registration; call sites immediately saw the
  new param. invoke_skill branch untouched.
- **Notify requester on JSM ticket comment 82919876** (RUNNING): webhook → HROPS+comment filter →
  JSD get_comment_by_ID → join lookup by ticket key → (public AND conversation present) →
  messenger ticket_update with guard-wrapped verbatim delivery text.
- **Notify requester on JSM ticket status change 82919975** (RUNNING): same shape; new status read
  from payload issue.fields.status.name (json_parser action is DEPRECATED in the builder — read
  webhook payload fields instead of parsing changelog items).
- **add_hr_ticket_comment skill skl-Abs4KExE-pwt4Wt-CD / recipe 82919977** (ATTACHED to HR Genie,
  25→26 proven additive): param comment_text + optional ticket_key (param wins, else join lookup
  BY conversation_id — reverse lookup on the same table); blank-ticket guard returns a clean
  ask-me error; JSD create_comment public=true `*{user_name} replied via Slack:*` prefix;
  monitor → friendly failure return.

**Continue-conversation PROVEN live** (probe recipe, deleted after): notify send created a
Josh-owned conversation on the messenger's chat trigger; ticket_update with that
conversation-… id APPENDED to the same conversation and the genie replied verbatim ("PROBE OK"),
0 skills / 0 KB. Error semantics learned: bare id (no `conversation-` prefix) → opaque "Internal
error"; wrong chat trigger (test-mode conversation) → "Conversation not found for this genie and
trigger"; wrong user → "Conversation ID does not exist or does not belong to the user". All three
impossible in the real flow (join record carries the same trigger's conversation + its owner).

**AIRO traps (new, for the playbook):** (1) `recipe_builder_add_step` requires SNAKE_CASE MODULE
NAMES (workato_variable, workato_db_table, workato_skill) — display names ("Variables by
Workato") fail with a reason-less "Failed to add step"; trigger steps accept them, actions don't.
(2) add_step appends AFTER a terminal step instead of displacing it (position=16 landed at 17
past the return) — always move_step back before the terminal. (3) data-table picklists want
NUMERIC ids (table_id="157888") and COLUMN FIELD UUIDs (primary_field_id), and record fields
appear only after both are set (paths like `parameters.<hash_underscored>`); filter paths are
`filters.field_id` (builder renders `filters.0.…`). (4) DSL f-string values cannot contain raw
newlines (unterminated literal) — use \n escapes inside the expression; plain values take real
newlines. (5) `genie_get` returns "retrieved successfully" with NO payload on this server — use
genie_list for config. (6) recipe_builder_save on an init'd session creates a NEW recipe id
(shell left behind — delete it); recipe_builder_push updates in place (skill handles require
push, never save). (7) property_list(project_id=…) 401s; `wt properties list` covers env props
only — project-scoped properties unreadable from here.

**Open for UAT (Josh):** (1) Jira webhook registration on the HROPS project → the two recipe
webhook URLs (suffixes jsm-ticket-comment / jsm-ticket-status; URLs visible in each trigger
step, recipes must be stopped to view/edit) — needs Jira admin; (2) Slack-thread rendering
eyeball in the Workato BT AI workspace; (3) real E2E: genie-created ticket → agent public
comment → thread delivery; employee reply → comment on ticket; (4) notify/invoke_skill
regression. Ticket-update latency = genie round trip (minutes), acceptable for this use.
Dev only — promotion via BSYS-29430 handoff when UAT passes.

**E2E OUTBOUND VERIFIED IN THE REAL FLOW (2026-10-09 01:00 EDT, dev):** Josh created HROPS-234
through the genie (rooster test) — join row AUTO-WRITTEN at 05:00:04Z by the new create_hr_ticket
step 16 (no backfill). Two status changes (Open → Awaiting Employee Response) + one public agent
comment ("Testing Write Back to Slack") all delivered to the SAME conversation thread
(conversation-01M4FFWP4R8HNBNAHE9T6819ZN), genie identity, verbatim, in Slack. Jobs j-AbsEs9td
(status) + j-AbsEsfRK (comment) succeeded; automation rules (Work item commented / Field value
changed = Status → Send web request) registered by Josh as PROJECT ADMIN in the sandbox
(workato-sandbox.atlassian.net) — company-managed JSM has NO project-admin webhooks UI; Jira
automation with custom JSON payloads is the path. Payload contract: comment rule sends
{issue:{id,key},comment:{id}}; status rule sends {issue:{id,key,fields:{status:{name}}},
changelog:{items:"status-changed"}} (literal satisfies the changelog gate). Loop guard live on
82919876: comment author not-contains integrations.hr@workato.com. REMAINING: inbound direction
(employee replies in thread → genie calls add_hr_ticket_comment → public comment on ticket) and
notify/invoke_skill regression → then promotion handoff via BSYS-29430. NOTE: Orca env reverts
to Production on every new navigation — re-flip via home (/airo) picker
[aria-label="Open environment picker"] before any dev page.

**INBOUND VERIFIED — E2E COMPLETE (2026-10-09 01:35 EDT):** Josh replied in the HROPS-234 thread →
genie CALLED add_hr_ticket_comment (job j-AbsFREYd, conversation-01M4FFWP4R8HNBNAHE9T6819ZN,
success in 1.9s) → public comment on HROPS-234; webhook fired for the skill's own comment 4s later
and the LOOP GUARD silently skipped it (j-AbsFRGk8). Both directions + echo suppression proven.
Regression: zero new failures on 74094657 post-push. **Root cause of the "I don't have the
ability" failures: the skill recipe had NEVER been running (blank JSD connection blocked start)
+ skill schema never platform-registered (editor open+Save needed — same rule as recipe
functions). Fix order: select connections → push → editor save → start → genie_update
remove+re-add the skill.** ALSO: genie_update skills_to_remove/skills_to_add RE-ADD path works
for re-registration without UI. Session-id collision reconfirmed: genie_update with a
recipe_builder session_id poisons genie_id with the recipe dump ("Genie with id '{...}' was not
found") — always seed a fresh genie session with genie_get first. Jira milestone comment
1133702 on BSYS-29430. Remaining for sign-off: Test Send Email override for ticket_update (AC 5).

**BSYS-29477 WATERMARK FIX BUILT + UAT-VERIFIED (2026-10-09 ~14:00Z, dev):** collector 82862205
boundary bug fixed — Agent Studio conversations API `from` filter is INCLUSIVE and the watermark
was the boundary conversation's own created_at, so when the newest conversation IS the boundary it
was re-fetched every 15-min run forever (state frozen at 10:42:18Z since 10-08, events_emitted 0,
masked by emitter source_job_id idempotency). Fix = one line in step 4 ("Resolve genie and
window"): `from_t = Time.parse(last) + 1` (offset +1s). Safety argument: created_at is
second-granular, watermark = batch max, so every conversation in the watermark's second was
already in that batch — +1s skips nothing; no processed-ids exclusion needed. Events fetch (step
11) takes NO from filter (whole-conversation by ID) — no offset needed there. UAT: watermark set
to 10:42:17Z via data-tables API, run 1 (j-AbsPQPwN-Ykkhef-CD) processed exactly the boundary
(watermark → 10:42:18Z, processed 492→493, condition True), run 2 (j-AbsPQth6-Kcg4Hx-CD)
window 10:42:19Z → condition False, state untouched — the old code would have refetched forever.
Hot-swapped running: stop → push → start → running flag re-verified. End state: watermark at
10:42:18Z = true newest conversation (none newer exist; the 29455 "skipped 13:41-13:46"
concern was moot). Ticket left In Progress for Josh's close; evidence comment 1134199.
**Pattern to reuse on ANY watermark-poll collector: when the window filter is inclusive, ALWAYS
offset the watermark by the filter's granularity (+1s for second-granular timestamps) or the
boundary row pins the watermark forever.**

**Directive-pass audit (2026-10-09 ~14:00Z):** all build claims re-verified live (Running=True,
step-4 offset present, both UAT traces confirmed succeeded in job list; re-verification comment
1134200 on BSYS-29477). One audit lesson: editor-Test runs in the verification window leave
FAILED jobs (error type "Test Automation error", "Output check failed ... Extra keys: log" —
stale snapshot comparisons) that pollute the post-fix job list. When auditing a just-fixed
recipe's job list, separate test-mode jobs by error type before judging the fix — same class as
BSYS-29396 canon (snapshot checks, never record literals for volatile steps).

**jira-triage fleet pass (2026-10-09 ~21:30Z):** BSYS-29283 (Deploy HR Genie Oct
batch) autopsy complete — prod import 42148590 failed closed on a duplicate
connection name: the prod HR Genie project's ENTIRE connection set (incl. CON |
Workato2 ISU Connection 22080797) sits in zArchive 32273844, not Config/Connection;
Workato import matches connections only inside the destination folder. Remediation
plan posted (comment 1134648) + projects/hr-genie/BSYS-29283-deployment-failed-autopsy.md;
awaiting Josh's gate (prod writes). Status syncs: BSYS-29477 → UAT, BSYS-29456 →
In Progress, BSYS-27450 → UAT, BSYS-26815 → UAT (builds re-verified live first:
82759555, 74912047). BTSUP service-desk lane triaged with drafts awaiting
Josh-confirmation: projects/hr-genie/btsup-service-desk-triage-2026-10-09.md
(Workday VUA reauth trio fleet-healthy verdict: 827 Workday runtime connections,
per-user stale tokens, not an outage). **Lesson: the h2. wiki-notation trap
shipped AGAIN this morning (BSYS-29461 verification comment used h2.) — fixed in
place 2026-10-09 21:14Z; the rule lives in the skill but headless passes keep
regressing on it; consider a PostToolUse lint for h2./h3. in Jira comment bodies.**

**BSYS-29488 four-collector repair LANDED (2026-10-10 ~07:00Z, dev, milestone comment
1134792):** Codex's 17h session built ~all test infrastructure (92-step queued owner,
fixtures) and ZERO collector changes; the repair pass fixed all four collectors with
per-defect native evidence — 78545249 (9 defects: single-page inventory, 1000-job cap +
wm→now skip, counters, unmasked alerts; 4,144/0 job history proves nothing — monitor
failures close "succeeded"), 82863111 (sync emitter + ack gate EMITTER_ACK_REJECTED —
proven zero-wm-movement on a failed run; `st < wm` equal-timestamp fix; filtered reads
with fail-red CORRELATOR_SOURCE_TRUNCATED; tri-state; 140219 has ≥500-row backlog →
correlator fails-visible until a one-time backfill decision — scope item 2 decision
for Josh), 82862205 (cursor drain, first(25) removed, +0 literal counter bug, tri-state,
sync acks, 7-day resweep 00/06/12/18), 82178793 (had NO checkpoint at all — rescan of
same 100 convs forever; rebuilt: list-slot state carry, property handle, 61 upserts /
1000 convs proven, sweep_truncated fires natively at >1000-conv window). **Platform
laws proven with unmasked traces (in airo-mcp-playbook): Variables-connector updates
inside loops do NOT persist across iterations (silent page-1 refetch loops inside green
jobs — use declare_list/insert_to_list/clear_list + ruby aggregation, the 82862205
idiom); nested repeat-in-foreach bodies don't execute; Orca Test click can silently
no-op (use `wt recipes force-run`); multi-page EVENT drain needs a flattened
conversation×page queue design.** Jira trap: addCommentToJiraIssue with commentId
UPDATES that comment — omit commentId to add new; caught and restored Codex's handoff
comment 1134780 verbatim after accidentally overwriting it.

**BSYS-29498 PAGE-COMMIT CUTOVER SPEC written (2026-10-11, read-only spec task):**
`projects/hr-genie/page-commit-cutover-spec-20261011.md` — full current-state map of
collector 82862205 (v30, step-uuid level), target topology (Commit Collector Page
82936791 IS the async queue owner — caller≠owner only via call_recipe_async +
wait_for_async_jobs, strictly sequential per page; no separate owner recipe needed),
collector step-level change list (additive fact lane, Mode-property gate, ledger emit +
watermark + heartbeat untouched), verified Caller Registry seed row (record_key formula
byte-verified against the live TEST row; LIVE collector row fe36b526… must be seeded
before cutover), test plan (4 existing TESTs + 5 new cases), promote-time deltas (env
from property = verifier is env-clean; registry re-seed id-dependent; Telemetry Genie
Handle property NOT import-remapped — LINKAGE LAW), rollback via git c78863a
(PRE-CUTOVER snapshot with full step tree; prior files are 0-byte stubs). 6 open
questions incl. capture_cycle_hmac LIVE tuple + progress-envelope key derivation.

**BSYS-29498 PAGE-COMMIT CUTOVER BUILT + PROVEN IN DEV (2026-10-11, build-agent session):**
collector 82862205 v40 now carries the page-commit fact lane behind the mode gate
(project property `HR Genie Telemetry Mode` = **PAGE_COMMIT**, kill switch; ACTIVE =
legacy). Final state: Mode=PAGE_COMMIT, collector + commit function 82936791 both
RUNNING, 0 new handled-error rows. Full record + evidence table:
`projects/hr-genie/page-commit-cutover-spec-20261011.md` §10. Shape: 16 additive
steps in two mode-gated 7-step blocks (N1 identity from verbatim-lifted
CheckpointState/projector modules of test 82939872 → G1 get 158155 predecessor → N2
signed proposal (AgentStudioQueuedPageProposal) → A1 call_recipe_async 82936791 → W1
wait → G2 readback → V1 fail-closed verify revision+1/coverage); page-1 block inside
try 2a45a2c0 after if b8736adc, round block inside foreach af14ac1a after guard
5171577f. Registry 158157 seeded: LIVE row caller 82862205/owner 82936791 (record_key
fe36b526…, verified 3 ways). Evidence: PAGE_COMMIT force-run 4 convs → 4 commit jobs
green, 158099 +15 / 158155 +4 LIVE rows rev 1 COMPLETE, wm→08:29:06Z; REPLAY force-run
= 158099 +0 (perfect dedup), progress rev→2; ACTIVE-mode run = zero commits (gate
proven); real scheduled tick green. 158100 observations GROW per capture cycle by
design (per-capture-job provenance grain — not a dedup bug; the EVENT grain 158099
never duplicates). NEW PLATFORM LAWS: (1) a recipe function must be RUNNING to be
called via call_recipe_async ("Can't call a stopped recipe") — promote checklist must
start the prod commit function BEFORE the collector; (2) raw-PUT surgery: step-level
name must be the generic op name (custom names fail start-validation), code_input.data
drops without visible_config_fields + extended_input_schema (form-schema-builder) +
extended_output_schema, and function-call parameters drop EVEN WITH vcf — async-call
parameters are builder-only (set_input_field_v4_mode; ruby() mode needs
ruby("bindings.x…", bindings={…}) shape); (3) batch test_scope values are
"false"/"" — translate to LIVE/UNKNOWN at the proposal boundary. OPEN for Josh: (a)
UNKNOWN-scope conversations are committed under the LIVE row (spec default; one
condition to filter if he wants explicit-LIVE only); (b) RESOLVED 2026-10-11: stale collector test case
citc-AbsPGsnb (BSYS-29455 guard-empty-batch) RE-RECORDED GREEN — orphaned
call_recipe_async_4f4b mock re-pointed to its converted sync twin call_recipe_4f4b,
all 11 must-be-mocked v4 steps stubbed, strict object-equality check on the
batch-builder snippet output now expects
{batch:[],batch_size:0,max_created_iso:"",fresh_count:0,log:""} (the test-run runtime
injects a log key into EVERY snippet output — strict expectations must include it;
proven by 3 diagnostic runs, recipe in workato-platform.md 2026-10-11 section); pass =
run cirr-AbtKg9Ma-mF9Pcz-CD, job j-AbtKg9MQ-KYfGXb-CD, recipe v40, guard proven
(watermark field untouched, only the liveness heartbeat wrote); (c) wait_for_async_jobs timeout=1
observed waiting ~20s and green — unit likely minutes; confirm at promote; (d) round
lane is wiring-proven only — no >100-event conversation exists in dev yet; watch the
first real multi-page drain (158156 cursor-history rows never written by a LIVE commit
so far).

## Approved HR Genie fixes EXECUTED (2026-10-20, Josh "approve all") — BSYS-26810/27818

All in dev. Recipes touched: [update_my_contact_info 82959472](https://app.workato.com/recipes/82959472) (tool 254984), [view_my_tax_document_elections 82959476](https://app.workato.com/recipes/82959476) (new tool 276755).

1. **Tool 254984 VUA flip: DONE + verified.** Root cause was NOT the tool binding; the recipe's workday_rest config entry had NO `personalization: true` (the binding flag mirrors it). Repair = stop recipe → direct `PUT /api/recipes/82959472 {name,description,code,config}` with personalization:true (BSYS-26815 method; code byte-verified identical post-PUT) → start. Tool binding flipped to VUA=Yes WITHOUT any tool PATCH — recipe-side config propagates to the binding flag live.
2. **Served description fix: DONE + verified, with a mechanism observation.** Recipe push (trigger description via builder set_input_field_v4_mode plaintext + recipe description via update_asset_metadata) did NOT update the served tool description — the binding snapshots the concatenation (trigger desc + recipe desc, blank-line separated) at add/re-save time. Fixed via MCP server page (`/mcp/<handle>/details`, the /ai_hub/mcp path 404s now) → "Edit tool description" dialog (textarea, native setter + input event) → Save = `PATCH /web_api/mcp/servers/<handle>/tools/254984.json` 200. Catalog read-back showed SOAP text immediately.
3. **Tax-elections registered: tool 276755, Active + VUA=Yes on first add.** Order mattered: set personalization:true on BOTH connections (workday_rest 19218617 + workday 19760790) of 82959476 BEFORE the Add-tools flow (add-time-only law). UI: server details → Add tools → "Add from this project" → one checkbox (view_my_tax_document_elections) → Add tools. 27→28 tools, all 27 prior tools verified untouched. Note the recipe ALSO lacked personalization on both conns before this (caught pre-registration).
4. **First live test of 82959476 (job [j-Ac46xxec-KmkXWr-CD](https://app.workato.com/recipes/82959476/job/j-Ac46xxec-KmkXWr-CD)): identity worker=me resolved, but SOAP Get_Tax_Document_Deliveries REJECTED: `Company_Reference` + `Form_Group_Reference` are REQUIRED in Request_Criteria, and only Form Groups `Canada` / `Canada_Electronic_Only_Default` / `USA` are supported.** The built envelope carries only Worker_Reference (the plan said Worker_Reference-only scoping was schema-confirmed — it is not). Monitor's clean-error design worked (structured error, no opaque fault).

   **FIX EXECUTED same day (Josh design call: USA + Canada form groups) — envelope rebuilt, VUA intact, end-user grant now the only blocker:**
   - New flow: step 6 `Get_Workers` (Human_Resources, Request_References Worker=WID, Response_Group `Include_Employment_Information,Include_Organizations`) → step 7 custom-code resolves the worker's primary Company (pods under `Position_Organizations_Data` where `Organization_Type_Reference` Descriptor = 'Company'; prefer `Organization_Reference` subtree WID; org-type objects carry their OWN WIDs — the naive first-WID scan grabbed the org-TYPE WID once, bug fixed) → guard returns friendly error if no company → steps 10/11/12 `Get_Tax_Document_Deliveries` **user-defined-payload XML**, one call per form group (`Form_Group_Reference` is max_occurs=1 in the WSDL; `Delivery_Group` is the non-WID ID type, proven values USA / Canada / Canada_Electronic_Only_Default) with Company_Reference + caller-Worker_Reference (WID) → step 13 custom-code merge dedupes by (delivery reference ID + form group descriptor + override), key = `delivery_id|formGroup|e/p` → single return.
   - **Workato workday-connector gotchas (new, costly):** (a) setting `Request_Criteria` as a WHOLE object in recipe_builder silently DROPS the `Worker_Reference__ref` object key at push even though `recipe_builder_show` renders it — set subfields individually by path, and the live-accepted path is `Request_Criteria.Worker_Reference` (string ref field), not `__ref`; (b) string ref-field values with spaces/colons: the `Type:value` customization + `<!--no_split-->` wrapper did NOT make guided mode work — the reliable form is `use_user_payload=true` + hand-built XML with explicit `wsdl:type` attrs (pills interpolate fine inside the f-string payload); (c) `snake_case` module name for custom code = `workato_custom_code`, action `invoke_custom_ruby_code`.
   - **Company_Reference resolution (live-verified):** worker Josh → Company "Workato Inc.", org code `E1`, WID `3ed7b665cef21001256a4153abd10000`; the connector normalizes response reference IDs to flat `<Ref>_<IDType>` keys (`Organization_Reference_WID`, `Organization_Reference_Company_Reference_ID` = "Workato Inc."). CompanyReferenceEnumeration = WID / Company_Reference_ID / Organization_Reference_ID.
   - **SPLIT-TEST VERDICT (the important finding):** identical payload runs green on the backend ISU conn 19760013 (clean `{asOf, noElections: true, elections: []}` — worker has no elections on file in the impl tenant) and fails on the end-user conn 19760790 with Workday's `Specify a valid company. The company you submitted is invalid for your request.` — same XML, same tenant ⇒ **the end-user identity lacks the Workday domain permission for tax-document-delivery reads and Workday masks it as a validation error.** Recipe shipped on the approved VUA configuration (end-user connection, personalization:true restored after the connection swap dropped it — second observed push-drift repair via direct PUT, code byte-identical). Remaining: Workday admin grant (Payroll tax-document-delivery read domain for the employee security group) OR Josh approves re-pointing the SOAP data leg at ISU with worker-WID scoping (scoping is criteria-pinned to the caller's own WID either way).
   - Test surface: MCP gateway tools/call (OAuth DCR + PKCE + Orca consent; cookbook recipe works — note Orca's `localhost` callback needs a dual-stack listener, IPv4-only bind misses `::1`).
5. **Grant request FILED (comment 1143551 on BSYS-26810):** Change Home Contact Information (SOAP Service) initiating action on the Home Contact Change BP for the employee security group; Human_Resources Change_Home_Contact_Information + Get_Change_Home_Contact_Information for the end-user token; Person Data + Self-Service Home Address/Phone/Email domains. REST grants explicitly not requested (path abandoned). Waiting on the Workday admin.
6. **Manifest verified (not rebuilt):** all three skills are agentic_skill rows in manifest **361068** "HR Genie 2026-10 promotion batch" (folder Core/HR Skills/Workday MCP) — but `checked: false, state: new`; the promotion batch assembler must tick them. Manifests read route: in-page `/export_manifests/<id>.json` (assets array; agentic_skill rows key the recipe as `provider_id` — the row `id` is a row id, NOT the asset id; ID-matching on `id` gives false negatives).
7. UI route notes: Enterprise MCP server pages now live at `/mcp/<handle>` (+ `/details`), NOT `/ai_hub/mcp/...` (404); the Test-recipe caret menu remains flaky (opened 2 of 3 attempts; hover+ref-click is the reliable sequence).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [HR Genie — Architecture Map](../../kb-corpus/confluence/extbt/2939977789-hr-genie-architecture-map.md)
- [Plan your genie scope](../../kb-corpus/docs/en/agentic/agent-studio/plan-genie-scope.md)
- [HR Genie Prod Deployment Checklist](../../kb-corpus/confluence/extbt/2745008431-hr-genie-prod-deployment-checklist.md)
- [HR Genie and Workday MCP - Architecture Overview](../../kb-corpus/confluence/extbt/2862809419-hr-genie-and-workday-mcp---architecture-overview.md)
<!-- kb-bridges:end -->

## Triage pass 2026-10-11 — four backlog Story plans refreshed (BSYS-26810/26816/27818/28314)

Fresh-read re-verification of the four remaining epic BSYS-26808 backlog Stories; per-ticket remaining-work plans posted as Jira comments 1134953-1134956 and saved as plan files in projects/hr-genie/BSYS-<key>-<slug>.md.

- BSYS-26810 update_my_contact_info 82959472: built, running. **Tool 254984 VUA Required STILL reads No** (drift flagged 2026-10-10, confirmed again 2026-10-11 read-back) — flip + read-back before UAT; promotion blocked on Workday tenant grants (Home Contact Change BP initiating actions).
- BSYS-26816 view_total_compensation 82959479: built, tool 254985 VUA=Yes holds. Only open item: second-identity scoping UAT (editor Test runs as connection owner, cannot prove scoping).
- BSYS-27818 view_my_tax_document_elections 82959476: saved+running but ZERO jobs ever run (Orca contention 2026-10-10); not yet registered on the End-User MCP server; first trace must confirm Form_Group descriptors survive the push (Response_Group drop). WSDL v46.2 re-query confirms only Put/Get/Import_Tax_Document_Delivery exist; Phase 2 stays BSYS-29494.
- BSYS-28314 FTO gate: all 5 assets live, tools VUA=Yes; only open item is the non-US UAT volunteer (blocked since August) then promotion.

## Workato API 401 missing_privilege on the Connection Health monitor — prod fix pattern (2026-10-12)

 Josh confirmed prod was already fixed; solution = mint a NEW Workato API key with the
privileges the monitor needs (projects list + recipes list reads) and create a FRESH
connection with it, scoped for the environment it serves. Live evidence, both sides:

- PROD fixed: [MON | HR Genie | Connection Health 82120581](https://app.workato.com/recipes/82120581)
  binds Workato API connection **16521378**, Running every 5 min, 10,614/10,617 jobs
  succeeded lifetime, every recent run green.
- DEV still failing: [MON | HR Genie | Connection Health 82044941](https://app.workato.com/recipes/82044941)
  binds connection **19190788 "Workato API (License Genie | Prod)"** — a key minted for the
  License Genie, auth-OK but lacking the monitor's API privileges. Fails at line 1 every
  5 minutes with `401 {"message":"Unauthorized","reason":"missing_privilege"}` — example
  job j-AbtmbeXz-we6tCb-CD (2026-10-12 00:32 ET). ~288 failed tasks/day while it runs.
- Lesson: `missing_privilege` on the Workato API connector is a KEY-SCOPE failure, not a
  broken OAuth — re-authorizing does nothing; mint a scoped key and a fresh connection.
  And a connection named "...| Prod" used by a dev monitor is the anti-pattern that
  caused this (hard-correction rule: dedicated path, not the shared/nearby key).
- RESOLVED 2026-10-13 (BSYS-29527, comment 1136575): dev fix shipped — new dev-scoped API
  client key + fresh connection [22291197 "Workato API (HR Genie Monitoring | Dev)"](https://app.workato.com/connections/22291197),
  monitor 82044941 re-pointed (v7, binding-only diff), running green on schedule (jobs
  j-AbwJwdLL-rN3stJ-CD, j-AbwJwfMF-bD4Csh-CD). Wire-format lesson: Developer API connection
  create/update wants params under `input` (not `fields`); this connector's token field is
  `api_token`. Wrong-scoped keys 19190788 + 22080724 now unbound — decommission is Josh's call.
- Watchdog tie-in: the 2026-10-11 watchdog P3 ("CON | Workato API HR Genie 22080724 lost
  authorization") is the same failure class; its "all HR Genie monitors are currently
  green" note was wrong — this dev monitor was failing throughout.

## Confluence doc tree: dev-vs-prod child pages added (2026-10-13, docs-only session)

Four new children of the Architecture Overview (2862809419): **2946040154 "In
Development: Not Yet in Production"** (the itemized ledger, 11 items with status
lozenges: promotion-ready / in-UAT / blocked / gate-pending), **2947088469 "Time
Off Steering and the FTO Gate (BSYS-28314)"**, **2946040211 "Slack and JSM
Two-Way Interactivity (BSYS-29430)"**, **2946564156 "BP Completion Notifications
and the Discovery Hub (BSYS-28313)"**. Updated in place: Intelligence Platform
2938175596 v4 (hardening section: BSYS-29477 watermark fix, BSYS-29488
four-collector repair, BSYS-29498 page-commit cutover + promote-order law;
dashboard pointer to idb-AbrbGR8C), Conversational Self-Service 2939093004 v2
(new "Skills in development" table: 5 skills + 1 upgrade), Overview 2862809419
v5 ("In development" section + callout links), Proactive Notifications
2939650050 v2 (BSYS-29429 provisioning-grace section + dev-only status note).
OOO Status API correctly EXCLUDED from the dev-only ledger (promoted 2026-10-08).
Doc-trap confirmed: create target pages BEFORE the index that links them
(placeholder IDs get burned into v1 and need a rewrite pass); Confluence
child-page creation order matters. Content sourced from this file; FTO skill
82839617 spot-verified Running live during the pass.

## CORRECTION: BSYS-29283 batch DEPLOYED — BP Completion Notifications live in prod (2026-10-13)

Josh corrected the doc pass: BP Completion Notifications IS in prod. Verified live in the
Orca browser (Production env, folder 35683212, path Agentic | HR Self Service
Genie/Core/Approval Workflow/Inbox Tasks/BP Completion Notifications): all four recipes
ACTIVE since Saturday 2026-10-11 ~5:46 PM, ZERO lifetime failures — Discovery Hub 769
successful, FUNC Process BP Completion Row 71,959, FUNC Resolve Recipients 255, REC Retry
Handler 64. So the BSYS-29283 duplicate-connection remediation (comment 1134648) was
applied and the managed import re-ran successfully after 2026-10-10; this file's "failed
at intake, awaiting Josh's gate" state was stale. Probe 82778137 still exists in dev,
stopped (deletion at promotion not yet done).
INTELLIGENCE PLATFORM **still dev-only**: prod folder "Intelligence Platform" 35774483
exists but holds ZERO recipes (verified same navigation). No "Intelligence Platform"
assets promoted with this batch.
CONFLUENCE: itemized page 2946040154 updated (BP moved to a "Recently promoted" panel,
items renumbered 1-10) + BP page 2946564156 rewritten as deployed + Overview bullet
updated. (Confluence writes 403'd mid-pass — same transient "app is not installed" as
Jira; retry after ~20 min, no re-auth needed.)
BROWSER LESSON (orca-browser traps ledger candidate): the env-switcher dropdown items
(button.app-menu-item with exact text Development/Test/Production) are INVISIBLE to the
a11y snapshot (no ref) and `orca find --locator text` clicks NO-OP on them; press-click
at guessed coordinates also no-opped. What WORKS: open the dropdown, then ONE eval that
finds the button by exact textContent and dispatches the full
pointerdown/mousedown/pointerup/mouseup/click sequence with clientX/Y — env flips and
the page navigates to /airo. Also: snapshot JSON can lag the visible dropdown entirely
(pixels showed the menu, JSON had no Production node) — trust pixels over snapshot for
menu-open state.

## Connection hygiene system efficacy audit (2026-10-13, wt josh-prod)

Verdict: the system genuinely resets, not just logs. Evidence from the three prod tables
(146753 reset audit / 146752 associations / 155761 epoch state) + job histories:

- **206 error cases caught AND remediated** since 2026-09-11: 166 DELETION_QUEUED
  (127 `workday_rest` runtime children + 39 `mcp` children) + 40
  RESET_QUEUED_NATIVE_REFRESH_EVENT (`400 Bad Request` → MCP session reset).
- Delete worker [82242826](https://app.workato.com/recipes/82242826): **166 jobs / 166 succeeded / 0 fail** — 1:1 with DELETION_QUEUED rows. External check: 6/6 most-recent deleted child IDs absent from the live 355-connection list.
- Reset chain [82242828](https://app.workato.com/recipes/82242828) 41/41, resolve v2 [82795216](https://app.workato.com/recipes/82795216) 92/92, correlate [82242825](https://app.workato.com/recipes/82242825) 816/0.
- All 51 ELIGIBLE epochs were subsequently deleted — no stuck cases. 182 AUDIT_ONLY rows are legacy-era stale children (July loss dates from legacy recipe 71538650) deliberately not auto-deleted.
- 253 distinct end users remediated; top user needed 9 resets (chronic offender, re-caught every time).
- Open item: audit sweep [82242831](https://app.workato.com/recipes/82242831) has 196 lifetime failed jobs (of 9,437) — never autopsied.
- Worker traces are mask_data=true, so verification must go through the connection list, not trace bodies.

## BSYS-29773/29774/29775 — Org Chart → Workday pipeline (2026-10-17/18, Phase 0 code done + Phase 1 BUILT in dev)

Plan: Workday-Development repo `docs/workday/org-chart-integration/PLAN-BSYS-16390-ORG-CHART-TO-WORKDAY-2026-10-17.md`.
Epic **BSYS-29773** (26 pts, VMT BSYS-21305, Relates: BSYS-16390 + BSYS-28841); stories 29774 (Phase 0 form
instrumentation), 29775 (Phase 1 intake), 29776 (Phase 2 pre-BP approvals), 29777 (Phase 3 manager-VUA BP kickoff).

- **Phase 0 chart-side CODE DONE** (branch `suggest-change-impact-preview`, commit 363f49f, patch at
  `docs/workday/org-chart-integration/0001-...patch`): impactOf/receivingManagerOf/impactNote in
  `src/lib/suggestChange.ts` (client tier: reporting_line | cross_business_unit; the chart can NEVER derive
  "routine" — proposedManager never proposes the current manager, so a no-derivation team sends NO impact
  block), review-screen warning callout, `context.impact` riding the §14.2 body backward-compatibly,
  api-contract §14.2/§14.4 updated, 47/47 tests green. **PR blocked: Josh (`jcramoyWKTO`) has push:false on
  the repo — Weizhuang must add him as collaborator (Write).**
- **Repo access playbook** (see auto-memory org-chart-repo-access): gh CLI org-SSO grant broken via Okta
  (Authorize step never renders); fine-grained PATs org-blocked; classic PAT (`ghp_`) + Configure SSO →
  Authorize reads fine; clone via `git -c credential.helper= clone https://oauth2:$(cat /tmp/gh_pat)@github.com/...`
  (http.extraheader route failed; strip clipboard whitespace FIRST — trailing newline = "invalid credentials"
  while curl works). Repo's PR rules: feature PRs → `preview` (squash-merge), main only via promote PRs.
- **Phase 1 BUILT in dev (2026-10-18):** folder **35873299** "Org Change Suggestions - Org Chart" under
  Consumer Endpoints (35693717 — the 35712142 correction in older notes is WRONG for dev; 35712142 is the
  OOO endpoint's SUBfolder "Get OOO Status - #team-ui" under 35693717); table **Org Change Suggestions
  161963** (27 cols, State machine VALIDATED→TICKETED/REJECTED/WITHDRAWN); recipe **API | Receive Org
  Change Suggestion 83152837** (21 steps, RUNNING, jira 18136359 + jira_service_desk 18136383) — 400 shape
  gate with specific reason, idempotent replay by Idempotency-Key, server tier ROUTINE/REPORTING_LINE/
  CROSS_BU/UNKNOWN derived independently of the chart's advisory, HROPS JSM request filed AS THE SENDER
  (find_user → raiseOnBehalfOf, fail-closed on unresolvable), best-effort org-chart-suggestion label in
  empty catch, outer catch parks the record REJECTED + clean 500 (two-signal rule). API endpoint
  **24139439** POST /v1/org-change-suggestions in collection 1404598 (created via
  `wt api POST /api/api_collections/1404598/api_endpoints`). Manifest **367064** (project-folder anchor
  30275122), read-back verified 2 rows; mirror in Workday-Development/manifests/.
- **BLOCKED on Josh:** endpoint 24139439 activation is UI-only, and **the Orca browser session has NO
  "Workato BT AI" membership** — the workspace picker lists only AHQ | BT / AHQ | AI / AHQ | HR / HR
  (Sensitive) + others. Dev-workspace UI steps (endpoint activation, access-profile/token, Okta/OpenID
  Connect policy) need Josh's own browser. The recipe records requester identity source per call
  (`jwt_claim` vs `header_fallback_dev_only`) so the token-policy period can't fake verified identity.
- **AIRO gotchas hit (new):** `set_condition` rhs must be the RAW string (`"true"` — passing `"\"true\""`
  double-quotes and compares against the literal quote-wrapped text); `set_condition` requires TOP-LEVEL
  `operand` ("and"/"or") — omitting it errors misleadingly as "operand: Field required" on the condition;
  ruby() formula whitelist bans `.size` in conditions too (use a unary `present` on `records[0]` key field
  instead); project_property pills in set_input_field need the `f"{...}"` prefix like any pill (bare
  `{project_property['X']}` → "Unsupported expression type: Set"); adhoc action fields unlock
  progressively (mnemonic+verb → path/types → input.schema/output → input.data.*); error_handling blocks
  show an explicit numbered catch step whose children take parent=<catch step number>; every insert
  renumbers downstream steps AND the catch steps (re-get datapills after each insert).
- **Workday find (2026-10-18):** Staffing REST v6 has a DRAFT-THEN-SUBMIT org-assignment flow —
  `POST /workers/{ID}/organizationAssignmentChanges` creates the change event as a DRAFT ("same Workday UI
  validations apply", nothing persists), `POST /organizationAssignmentChanges/{ID}/submit` initiates the
  Change Organization Assignments BP (empty body = Submit button; Save-for-Later = status id
  d9e41a8c446c11de98360015c5e6daf6), `GET /organizationAssignmentChanges/{ID}` reads it back. Secured by
  **Business Process Type: Change Organization Assignments for Worker** (Scope: Organizations and Roles) —
  so the manager-VUA kickoff needs NO new ISU write grants. Workday REST secures by domain/BP-type, not
  OAuth scopes (spec's OAuth2 has empty scopes). Config-request draft updated:
  `docs/workday/org-chart-integration/WORKDAY-CONFIG-REQUEST-ORG-CHANGE-PIPELINE.md`.

- **2026-10-18 (later) WORKDAY-FIRST REDESIGN + S21 BLOCKER:** Josh corrected the design — the
  HROPS ticket is ACCOMPANYING only (best-effort retries=0 monitor, gated on find_user, can
  never fail the flow), the terminus is the Workday Change Organization Assignments event.
  Built + live: WID resolution via the ORG-CHART SNAPSHOT index (table 137030, col
  Normalized Work Email 170e70e3 → Employee WID f8a2c86e; Josh resolved to
  8ec8136c…c5e0000), unknown-person 400 at the door, record State WORKDAY_EVENT_CREATED +
  workday_event_id folded into the Validation Result column, catch parks REJECTED with the
  Workday error. **TERMINUS BLOCKED: `404 S21 "not found: organizationAssignmentChanges"`** =
  the permission-masked 404 (OOO precedent) — the ISU/ISSG lacks the Change Organization
  Assignments for Worker BP-type + Staffing Organizations domain grant; config request doc
  carries the S21 evidence. **NEW PLATFORM FACTS:** (1) the Workday REST adhoc connector
  DROPS QUERY STRINGS — `GET /workers?email=…` (even %-encoded) returned the unfiltered
  1,550-worker set; worker resolution must be path-based (WID from a source-side index) or
  WQL — never query params; (2) Workato adhoc actions on absent request fields deliver ""
  (empty string), not nil; (3) `JSON.parse("null")` RAISES on Workato's json gem — a
  `rescue → return raw` parser turns "null" into the literal string "null"; normalize
  before parse; (4) undeclared request headers are DROPPED by the API-platform trigger —
  every header the recipe reads must be in request.headers schema; (5) object pills MUST
  bind via `ruby("bindings.x.to_json")` — f-string interpolation of an object pill yields
  Ruby-hash-inspect (`=>`) which fails JSON.parse. Test UAT artifacts: HROPS-236..239
  (real JSM tickets, marked safe-to-close). Dev endpoint live:
  https://apim.workato.com/workato-bt-ai-dev/hr-genie-consumer-endpoints-vv1/v1/org-change-suggestions
  (access profile org-chart-app 1384853, token in keychain `org-chart-app-token`).
  The Orca browser "workspace problem" was a FALSE diagnosis — fetch('/recipes/<id>')
  XHR probes 404 on HTML routes; the browser was on the right workspace all along (Josh
  corrected; trust rendered page text + sight.py, not fetch-status probes of HTML routes).

- **2026-10-18 (final) PHASE 2 BUILT — conversational confirmation loop live:** assets (all
  folder 35873299, manifest 367064 = 5 rows verified): table **Org Change Suggestion
  Confirmations 161970** (per-confirmer rows: role/state REQUESTED→CONFIRMED|DECLINED/attempts
  cap 3/requester email); **confirmation router** in 83152837 (plan step → tier recipient set:
  REPORTING_LINE = receiving manager, CROSS_BU = + people partner; VP confirmation deferred to
  the org-lookup follow-up); **skill Confirm Org Change Suggestion 83152934**
  (skl-Abzzr48F-bdLtab-CD, ATTACHED to HR Genie gin-AYbxpMha via genie_update after
  genie_get in the same session — fresh-session-only update fails with a session-keyed
  lookup bug) — identity = start_workflow context user_email (Genie-verified, never
  user-claimed); **REC | Org Change Confirmation Reminders 83152938** (daily 8:15, cap 3,
  bump-on-send). **Messenger switched to invoke_skill mode**: skill_instruction carries the
  suggestion + "run the skill Confirm Org Change Suggestion with record_id=… decision=…"
  → the Genie PRESENTS the task and captures the decision conversationally (fixes the
  notify-mode "doesn't recognize the task" gap Josh caught). **CRITICAL TABLE TRAP
  CONFIRMED:** data_table_update with columns REPLACES ALL COLUMN UUIDS (the recipe step
  bindings silently go stale — the step still shows old param keys and FAILS at runtime);
  after ANY column change: re-select table_id on every step touching that table, re-map
  params with the new field ids, remove the old keys, and re-check the ruby CODE strings
  that embed field-id keys (the chain-state reader needed the new State id too).
  **PIPELINE STATE:** full E2E green through the S21 wall (fail-open on the Workday refusal:
  error recorded on the record + State stays VALIDATED via the conditional ruby on
  update_record_16's Error Message; flips fail-closed at Phase 3). Awaiting: (a) Josh sends
  the Workday config request (S21 evidence in
  docs/workday/org-chart-integration/WORKDAY-CONFIG-REQUEST-ORG-CHANGE-PIPELINE.md), (b)
  Weizhuang collaborator Write → Phase 0 PR, (c) a real confirm conversation in Josh's
  Genie DM → PRE_APPROVED flip proof. Gateway 504s on ~9s jobs — the chart's 20s client
  timeout + idempotent replay absorb it.

- **2026-10-18 (E2E CHAIN COMPLETE) Submitter + authority check built:** **REC | Org Change
  Suggestion Submitter 83153929** (hourly): State=PRE_APPROVED records with a Workday Event Id →
  POST organizationAssignmentChanges/{id}/submit → SUBMITTED_TO_WORKDAY; per-item monitor
  retries=2 + FAILED parking. Intake gained the **server-side authority check** (Josh's Option
  B): requester resolved in snapshot 137030, authorized = self | direct_manager (verified from
  Employee ID b034d738 vs Manager Employee ID 3148b9b7) else chart_asserted (PP/deeper —
  recorded, gated by the confirmation chain; strict server-verify for those needs hrbp data in
  the snapshot); 403 refusal at the door. Suggestions table grew Authority Check +
  Workday Event Id columns — **BOTH tables truncated + re-schema'd** (all field ids
  regenerated again; every step in 83152837 + 83152934 rewired to the new ids and
  persisted-verified). Final manifest 367064 = 6 rows (3 recipes + 2 tables), all 4 recipes
  RUNNING. **THE CHAIN IS COMPLETE ON PAPER:** intake → authority → classify → Workday draft
  (S21-walled, fail-open, error recorded) → accompanying ticket → invoke_skill confirmations →
  PRE_APPROVED → hourly submit → Workday BP. Remaining: (a) the S21 grant (config request with
  Josh), (b) a live confirm conversation (PRE_APPROVED flip proof), (c) the Okta/OIDC policy
  swap to kill the header fallback, (d) Weizhuang collaborator Write → Phase 0 PR, (e) red-team
  before any promotion (Tier 1: external trigger + PII).

## 2026-10-21: [requester] FTR fixes on BSYS-29498 (dev, pending Josh QA + Jira reply GATED)
[requester]'s comment 1144476 → 5 items, 4 fixed in dev, package re-cut 42285005 (ZIP-verified), NO Jira reply until Josh manual QA.
1. **v2 rename**: 82794233 → "FUNC | HR Genie | Resolve Active MCP Runtime Child". Metadata rename requires the recipe STOPPED ("can't modify running recipe") — stop → rename → start.
2. **Hardcoded folder (auditor 82862838)**: ad-hoc HTTP step had folder_id=30326966 baked into the URL (URL literals are NOT import-remapped — the step's own "deployment-remapped" comment was wrong; [requester] caught it). Fix = sibling 78545249's pattern: list projects + ruby resolver (explicit PROJECT_NOT_FOUND raise) + dynamic path. TRAP: **recipe_builder CANNOT author project_property pills** — bound the project name as a literal "Agentic | HR Self Service Genie" (identical name both envs, zero env-specific ids, fail-closed). v4-mode plaintext REJECTS raw `#{_dp(...)}` pill markers.
3. **Batch upsert (rollup 82863448)**: live loop → single `upsert_records_batch` (max 1000/batch, PK metric_key) via list-comprehension on `records` — set path `records` with one comprehension string `[{'parameters': {...}} for item in source]`, AIRO compiles to mapped pills. TRAPS: (a) **upsert_records_batch FAILS "Records value must be present" on EMPTY records** — old loop was a silent no-op; wrap in `if candidate_count > 0`; (b) `now` keyword unusable inside a comprehension (compiles as None_None pill) — capture in a DateTime declare_variable first; (3) positive+empty paths both proven by forced runs (j-Ac4TdeDf-xk4Pzc-CD: 3 records in one call).
4. **MCP server rename** (UI-only, no REST surface — Developer API 404s /api/mcp_servers): env-switch to Development first (header showed Production), server page /mcp/<handle>/settings → name Edit → **contenteditable span + ✓/✗ icon buttons (no "Save" text button)** → Meta+A → type → click `.editable-text__control_confirm`. First attempt silently cancelled on blur — keep the sequence in one block; verify persistence after RELOAD.
- **ACCESS ANSWER (recommendation, Josh decides)**: end-user groups gate Slack/Teams/GO deployments only; the Analyst genie is collaborator-gated (Agent Studio) + token-based MCP (hashed, read-only) → an end-user group is NOT required today; create one (Workato Identity, e.g. "BT Enterprise Architecture" mapped to Okta) only if the analyst genie goes to a broader Slack/GO audience.
- **wt dt records API route truth (cost a row!):** `--data '{where/sort/continuation}'` route IGNORES where+sort+continuation silently (returns first 20 rows always); the `--where 'col=val'` GET route DOES filter — string equality only (booleans 400). **DELETED the wrong row by trusting the --data where filter** — restored the 2026-10-07 test tool_call row from captured output (new record id; corpus intact). LAW: never delete by a record id obtained from a route whose filters are known-ignored — locate client-side or via the equality route, count matches, then delete.
- All 4 fixes ZIP-verified in package 42285005 (resolver new name; auditor 30326966 only in an audit-trail comment, 0 in code; rollup foreach count 0; MCP name clean). Smoke: force-run j-Ac4TmhDH + replay j-Ac4TncP4 green.

### 2026-10-21 addendum: hardcoded-id sweep found a SECOND defect in the auditor (Josh: "no hardcoded recipes anywhere?")
- **The instrumentation detector hardcoded emitter ids**: auditor's Diff-coverage ruby matched skill code against literal dev ids 78563374 (Record MCP Tool Usage Identity) / 82862028 (Emit App Event). Import remaps structural refs, NOT string literals → in prod every skill misreports DARK/UNINSTRUMENTED_OFF. Same class as [requester]'s folder finding; caught by the package-wide sweep.
- **FIRST FIX WAS ITSELF A REGRESSION (caught same session)**: I re-resolved the folder to the project ROOT — but 30326966 was the "Workday MCP" skills LEAF folder; the root query returns 0 recipes and the orphan cleanup then DELETED all 41 mcp_skill coverage rows. Repaired: the "bound skills folder" now resolves from NEW env-scoped project property 'HR Genie Telemetry Skills Folder Id' (dev=30326966) and emitter ids from 'HR Genie Telemetry Emitter Recipe Ids' (dev=78563374,82862028) — both fail-loud if blank. Force-run j-Ac4kbCYc rebuilt 41 mcp_skill rows. **PROD IMPORT RUNBOOK (CORRECTED per Josh 2026-10-21: property ROWS travel with RLM, VALUES do not): after import the 2 new property rows exist in prod BLANK — set prod values on them BEFORE starting 82862838 (the fail-loud guard covers exactly that blank window).** Ticket description edit pending Josh's go.
- **recipe_builder DOES support property pills natively**: `set_input_field` with `ruby("bindings.prop.to_s", bindings={"prop": project_property['Property Name']})` — works (rendered `project_property['...']` in the DSL). The raw-pill-marker route is unnecessary. (Learned AFTER two raw PUTs; the pills also survive raw PUT → AIRO pull+push round-trip, which is the repair for raw-PUT code_errors — the round-trip DID drop unset code_input.data bindings, so re-set schema+data after any raw PUT.)
- **Raw-PUT lessons**: PUT body = {name, description, code} only (full GET payload 400s on config/account_id); platform DSL `as` names are STABLE random suffixes (no renumbering when deleting steps — just splice + fix `number` fields incl. LOOP CHILDREN, else start fails "number out of sequence"); start-validation errors surface in `wt recipes start` stdout — the CLI "silent no-op" is often these code_errors.
- **wt properties API truth**: POST /api/properties?project_id=<id> (query param, STRING) with {"properties": {name: value}} HASH form; list form {"properties": [{name,value}]} 400s "Must be a Hash".
- Final package 42289965 ZIP-verified: 0 folder-ids in URLs, 0 bare emitter ids, 0 gin/ginct/mcps/skl handles anywhere; rollup batch upsert in, foreach 0.

**BTSUP-79353 duplicate-chats hotfix (2026-10-21, prod v3 + dev backport):** the BSYS-29757 atomic claim
worked, but the claim key was minted fresh every pass — `event_id` was the unstable WQL document.id (NOT the
request WID; Resolve Time-Off Context returns no request WID despite its schema hint) and Process
Decision/Reminder minted `RETRY_(attempts+1)` occurrences on every pass whenever the tracker row read
PENDING (lane races) — so the dedupe never matched. One approval → 5 chats; Send Genie Event ramped
27/day (10-16) → 338/day (10-20). Fix (formula-only, dispatcher+claim untouched): dispatch event_id →
span-stable `worker_wid|type_descriptor|span_start|span_end`; retry gate FAILED-only (drop PENDING);
SUPPRESSED marks tracker terminal. Red-team PASS-WITH-NOTES — known gaps: identical-span re-decisions
suppress permanently (claim-TTL follow-up needed), crash-between-claim-and-send unrecoverable, nil spans
degenerate keys. NEW TRAPS: (1) Workato formula validation fires at START, not PUT — a malformed pill
(truncated `}')` when slicing a pill out of an existing formula) PUTs fine, then start fails with
"expression is unsafe" and the recipe is left STOPPED — always re-GET running:true and restart; (2)
`wt manifests assets --include-all` dep-crawl cascades across projects via genie/skill deps — for a
focused recipe-chain manifest, build rows directly from the listing (row_from) instead of the recursive
dep walk; (3) create-manifest response may print rows:0 while the record actually persists — verify via
the in-page /export_manifests/<id>.json route. Evidence: docs/hr-genie/BUG-evidence-BTSUP-79353-*.md;
manifest 369303.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [HR Genie](projects/hr-genie.md) — **P2 HOTFIX 2026-10-10 (~19:00 PT): 2:56 AM re-import overwrote prod messenger 82120574 chat_trigger_handle with the DEV option id (ginct-AbbxJxmX) → EVERY send failed "Genie is not found or has not been started" ~15 h, jobs green (monitor caught all) — fixed live: re-set all 4 send steps to prod handle ginct-Ab9LJNRB via set_input_field_v4_mode plaintext, push, restart, verified 12/12 clean + genie caller list repopulated; trigger handles are env-scoped picklist ids, import remap skips them (run-book gate needed); set_input_field v3 JSON-stringifies all values — use v4-mode plaintext**; **BSYS-29283 CLOSED DONE 2026-10-10 (deployed live + all import collateral repaired: stub rewiring → repointed to ISU Prod 19909763 code-identical + 31 recipes running; identity funcs re-wired to CON | Workato API HR Genie 22284446 with a Development-scoped IAM client token — Identity IAM API refuses ALL Production-scoped client tokens, key lesson — live test passed, ticket Closed/Done with canonical PROD connections table in file: ISU 19909763 / REST 19234290 / VUA 22080799 / IAM 22284446); import lessons (stub-vs-null binding inconsistency, config-level reference checks, curl --data-binary @file for oversized recipe PUTs, properties API string project_id) in file**; **BSYS-28306 US payroll-critical-data nudge BUILT+verified in dev 2026-10-10 (recipe send_payroll_data_nudges_us 82959797 STOPPED, grant-gated; US row in shared region-config 158555 set to 3 required fields + dry_run + real Workday link; bank-election scan WIRED via Get_Payment_Election_Enrollments (authorized, Role_ID_Reference_WID join) closing the non-US variant's unresolved gap; NEW domain-strip guard: blind-scan detection forces safety_hold rows, structurally cannot mass-nudge; live force-run proofs: 999 flagged → 999 safety_hold ledger rows landed (population closed) + rerun deduped 999/0-new/0-sends (j-AbspcgdB-bggboh-CD, j-AbsphHHF-6Br3Mw-CD); Get_Period_Schedules NOT authorized + personal-data values stripped 0/999 (probe jobs cited in Jira comment 1134851); BLOCKERS = Workday domain grants (Personal Data/National ID/Contact + Payroll schedules) then flip send_mode=live; traps: start-validation rejects pill-path .to_json (use ruby bindings passthrough), snippets return BARE hash (wrapped {'output'=>} silently nils pills), inspect parser needs sign-aware time token + weekday-date token, clock trigger action name = scheduled_event, get_user_by_email raises on blank email (lookup INSIDE the live gate))**; **BSYS-28307 non-US payroll-critical-data nudge BUILT+verified in dev 2026-10-10 (scheduled scan-and-dispatch recipe 82959747 RUNNING daily 07:30 + region-config table 158555 + nudge log 158554; scan→classify→dedupe→DM pipeline proven green end-to-end with ledger audit 583/583 distinct/0 dups, all dry_run zero live DMs; sends via HR Genie Operations Workbot 20369210; TWO blockers before live UAT: Workday domain grant gap (Birth/National-ID presence unreadable — 0/999 — false-flags everything, BSYS-26817-class grant needed) + truncate dev ledger before live period; test cases/editor Test + ops-channel digest + live-send flip staged as resume; NEW LAWS in domain file: select_connections commits immediately + push wipes it (select LAST), nested code_input objects arrive as inspect-strings (scalar leaves only), Get_Workers country criteria silently dropped (client-side filter is the path), Count<1000)**; **BSYS-28420 pipeline self-health watchdog BUILT+lifecycle-verified in dev 2026-10-10 (REC 82959774 every-5-min + FUNC heartbeat 82959725 + tables 158559/158560 in new Pipeline Watchdog folder 35769475; 7 monitored recipes touched with swallowed heartbeat calls only; alternate route = Email by Workato (no connection); alert/dedup/recovery/no-second-recovery all proven with job IDs; resume: dedicated Slack app + own API token + controlled-stop UAT; traps in project file)**; **BSYS-28310 view_job_compensation_range BUILT+live-verified in dev 2026-10-10 (recipe 82959755 RUNNING, skl-Absp3hhd-x6gEfC-CD; two-gate design per plan; VUA personalization flip done+verified; TENANT FINDING: no manager-readable comp-range surface — allCompensationGrades/allJobProfiles WQL 403 + SOAP Get_Compensation_Grades fail-closed under VUA, probes stopped w/ evidence; skill falls back clean non-exposing; live test j-AbspLebd-RLBp6h-CD + audit readback metadata-only; REMAINING: MCP-server picker attachment (27 tools, full-replacement trap; update_my_contact_info vua_required=false drift noted) + UAT four cases blocked on a live Job Change event in dev; set_condition rhs + CodeMirror inserttext + VUA-flip-UI traps in domain file)**; **BSYS-28309 LoA notifiable+approvable BUILT+live-verified in dev 2026-10-10 (new FUNC Resolve Inbox Leave Context 82959603 running + wired into row processor 74482074 with gated fail-open leave lines in Detail Summary; live proof: rebuild job j-Absp9HPd-49LBrP-CD → function job j-AbspEDgm-kmdX9B-CD → enriched ledger row f75983a3 SENT with "Currently marked on leave in Workday"; NEW TRAP: recipe functions default STOPPED — callers fail WRF00409 until wt recipes start; approval/refuse-list verified no-change; UAT remaining: live LoA approve by awaiting tester + approved-LoA case for typed type/dates lines)**; **BSYS-26816 view_total_compensation BUILT in dev 2026-10-10 (recipe 82959479, tool 254985 on End-User MCP vua_required=true; SOAP Include_Compensation probe CONFIRMED amounts incl. Stock_Plan_Data equity — no RaaS needed; code_input datapill + End-user-connection personalization traps in file; real end-user scoping UAT pending)**; **BSYS-26810 update_my_contact_info BUILT in dev 2026-10-10 (recipe 82959472 + tool 254984 + audit table 158542; scope-probe gate FIRED: REST contact-change 403 S22 + SOAP contact-read not authorized under end-user token — build complete on SOAP fallback, write-path UAT blocked on Workday tenant grants, full evidence in Jira comment 1134839 + project file)**; **BSYS-27818 view_my_tax_document_elections BUILT in dev 2026-10-10 (recipe 82959476, Option-1 re-scope: delivery-elections viewer not document instances, Phase 2 = BSYS-29494 blocked on RaaS authoring; catch-block placement + UI-only test-case-creation traps in file; live test + MCP wiring pending shared-browser contention)**; **BTSUP-76729 STALE FTO KB DOC FIXED 2026-10-10 (stale doc 242843660 deleted + re-ingested fresh via utility 82959474; root cause = collector 71498060 trigger silently missed page updates; new KB freshness sentinel 82959482 wired to publisher, verified both directions; Enterprise-context connector replaces deprecated Store knowledge — KB date-mangle + adhoc-output + index-lag laws in playbook/project file)**; **BTSUP-76729 PROD STILL STALE 2026-10-11 (read-verified: prod KB kb-AYcm4ggH-L9o6zm-CD doc 242843660 "Flexible Time Off" = 1,003-byte 2026-04-03 snapshot, never refreshed; dev fix NOT promoted, sentinel is dev-only — customers still hit the bug; drafts + findings in projects/hr-genie/btsup-drafts-2026-10-11.md)**; **BSYS-29455 guard case RE-RECORDED GREEN 2026-10-11 (orphaned mocks fixed + snippet-log strict-check law, workato-platform 2026-10-11 section); BSYS-29488 DONE-THRU-2026-10-10 (milestones 1134792+1134821+1134838): all 4 collectors repaired + flattened multi-page event drains landed w/ native round proof; scope-B coverage monitor 82959606 BUILT+verified (11 keyed coverage rows in 156843, DARK-detection live-proven on 82862205 pending-overlap hang — cancelled j-Abso3wzo, queue drained; sanitizer allowlist readback proof closed: registry 156841 complete + normalizer 82915212 fail-closed; scope-3 metrics recorded UNPUBLISHED per gates; UI-only dashboard KPI rebuild + hung-job-guard port staged as resume steps in project file); self-caught 100× under-collection (population-assertion law in agentic-platform-lessons); 140219 backfill COMPLETE (6,064 ledger events, correlator green, comment 1134882); PTO-Hub 61h retry explosion autopsied + BSYS-29495 BUILT (native FAILED_PERMANENT proof); dashboard audit done 2026-10-10: empty panes = UAT-gated notif evidence (all Oct-7 rows) + frozen 156862 Quality source (containment) + stale freshness KPI/coverage snapshot; pane fixes + BSYS-29499 Quality-dimension pipeline (5pts, Backlog) filed; Variables-in-loops + nested-repeat laws in playbook); FY27 Year-End/Leapsome: PLANNED + PHASE 0 PROBED 2026-10-08 (conn 19006083 = PROD Leapsome, admin token 