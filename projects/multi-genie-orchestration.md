# Multi-Genie Orchestration

One Slack-facing Main Genie routes each employee request to exactly one of 12
existing specialist Genies through a private Cloud Run gateway. Development
POC, **complete and frozen pending Product/leadership/BT direction** (Confluence
banner, 2026-10-03).

## Canonical pointers

- Canonical workspace (100+ files, exports, gateway code):
  `~/Documents/ChatGPT/Multi-Genie Orchestration/`
- Architecture diagram source of truth (Mermaid, created 2026-10-08, moved
  into the knowledge tree 2026-10-08 per the arch-diagram location rule):
  `~/.claude/knowledge/projects/multi-genie-orchestration/architecture/architecture-diagram.md`
  (the workspace copy was replaced by a pointer). Update it in the same
  session whenever revision/routes/auth/telemetry/drift flags change; the
  closeout PNG/SVG in the workspace are historical renders.
- Master handoff (read in full before any work):
  `ORCA-CLAUDE-CODE-HANDOFF.md` there. Source precedence order is documented
  in its "Source precedence and freshness" section — trust the UAT ledger
  (2026-10-05) > program memory (2026-10-02) > routing-policy JSON > Sept
  runbooks > evidence log > old handoffs.
- Session stub repo: `~/orca/projects/multi-genie/` (empty git repo, session
  root only; do not duplicate workspace files into it).
- Living Confluence FAQ: page 2870903050 (BTI space, extbt).
- Onboarding FAQ: page 2872377507. Governing epic: BSYS-28503.

## Architecture in one line

Main decides **who** owns a request; the specialist decides **what** it may do
for the authenticated employee; Cloud Run (project `mult-genie-poc`, us-east1,
service `multi-genie-grc-streaming-canary`, revision `00079-xqq`) makes the
handoff and return path reliable without owning either decision.

- Main Genie `WKTO GENIE POC` `gin-AbWrNKh8-wCbern-CD` (immutable dev ID 34579),
  front door = Workato BT AI Slack workspace DM (`D0C6B0FSAHF`; NOT the old
  `D0C079EJK7V`).
- Workato project 17923915, root folder 35320784; active routes in Skills
  folder 35409717; Operational Monitoring 35684224; Automation 35409712
  (terminal ingress + connection health); zArchive excluded from RecipeOps.
- 12 route recipes, all Running, all with `route_key` + literal handle,
  masked lines 0–4, canonical `gateway_status` (verified live 2026-10-07):
  HR 82247224, CPQ 82247223, Deal Desk 82269830, Enterprise Data 82270328,
  Calendar 82279424, Gmail 82279805, CSM 82279804, GRC 82245408,
  Cora 82248493, BT 82252220, Support IDOL 82248279, Salesforce Reader 82280113.
- Legacy exceptions still running: HR 82148855, CPQ 82148859 (do not treat as
  current routes, do not delete casually).
- Gateway code: `streaming-gateway/src/*.mjs` (server, router-auth, identity,
  route-registry [fail-closed, INACTIVE], headless-client, sse,
  completion-result, firestore-state-store V2, state-crypto, lease-heartbeat).
  Local suite 85 passed (needs localhost bind; `listen EPERM` under sandbox is
  not a code failure).

## Identity invariant (non-negotiable)

User text is NEVER authority for identity, permissions, connection state,
confirmation, or source conversation. Trusted subject comes from Workato skill
context, forwarded server-side as `X-IDP-User-Id`. Main never passes a user's
VUA/OAuth token to a sub-agent; the specialist is the authorization boundary
and emits `runtime_connection.auth_required` → official short-lived link only.
Never copy auth URLs into docs/logs/Jira/chat. Never accept user-supplied
genie handles, user IDs, emails, attempt IDs, or conversation IDs.

## Product vision

Employees get one Genie front door; domain ownership stays distributed — each
specialist keeps its own instructions, skills, knowledge, source connections,
VUA, and confirmation policy. No tool sprawl on Main (rejected: attaching all
specialist tools to Main, and Decision Models that would bypass the trusted
gateway). A future Decision Model may only run as a shadow evaluator.

## Gotchas and hard-won lessons

- **Workato synchronous boundary ≈ 120 s** regardless of the 180 s the action
  UI shows. Gateway source budget is 112 s. Do not raise it without
  remeasuring.
- Headless base URL must be `https://genie-api.workato.com`, NOT
  `app.workato.com`. Canonical health path `/v1/health` (`/healthz` is
  intercepted by Cloud Run).
- A stopped source Genie returns HTTP 422 on conversation creation (CSM,
  2026-10-01). Gateway was repaired to return safe HTTP 200 `gateway_error`
  with durable `gateway_run_id`.
- Newest Headless message is selected by timestamp, not array order.
- Per-affinity turn leases prevent concurrent turns from turning a real 409
  into false stale-affinity recovery.
- V1→V2 Firestore migration done (0 assertions, 13 affinities, 68 runs
  imported; TTL active). NEVER roll post-V2 traffic back to a V1 revision.
- Local exports are evidence, never proof of remote state. No exported route
  recipe even contains the later `route_key` field.
- Genie "Add tools" is a replacement set — snapshot the full tool list before
  saving.
- Deployment requests are Stories, never the "Deployment Request" issue type
  (see jira-story-standards skill).
- The 2026-10-05 short CSM-health phrase that once selected Enterprise Data
  right after a recipe restart must stay in the regression corpus
  (`routing-regression-set.json`, 51 cases).

## Known open gaps (enforcement, not prompting)

1. Cora: 4 create-ticket skill triggers have `requires_user_confirmation=false`;
   model-supplied Jira Reporter is not bound to trusted identity.
2. BT: Firefighter request recipe 67011294 has no confirmation, accepts
   model-supplied beneficiary/requester; validity-check recipe 75113193 has
   unresolved output datapill paths (`valid`, `invalid_type`, `invalid_reason`).
3. Deal Desk: Slack escalation consumer lacks durable idempotency/ack.
4. CPQ: no licensed-user real Salesforce-backed action proof.
5. Support IDOL: authorized-group-member path never exercised.
6. Route registry: code-ready, template fail-closed, NOT active/release-ready.
7. Docs drift: README/runbooks/openapi/.env.example still describe 00065 /
   150 s / 7 specialists; reconcile before any release gate.

## Operating rules

- Development only. Any Production mutation needs explicit action-time
  authority (Josh confirms). Prod MCP server `workato-airo-mcp-prod` is
  read-allowlisted, write-gated.
- Promotion is via Workato RLM UI dependency graph, never a local manifest.
- Gateway deploy: `deploy-grc-canary.sh` (legacy name, deploys the shared
  service), zero-traffic candidate first, numeric secret pins only, keep a
  V2-compatible rollback revision.
- 14 gateway secrets in `mult-genie-poc` Secret Manager (router token, state
  key, 12 per-specialist headless keys). Local
  `multi-genie-gateway-secrets.json` is 0600, gitignored, never read into
  model context.
- Telemetry chain: Cloud Logging → Pub/Sub `mg-telemetry-terminal-dev` →
  forwarder Cloud Run → API platform → ingress recipe 82285725 → data tables.
  Privacy-safe only; gateway never waits on it.
- HR notification path (publisher 82252949, topic 97588, dispatcher 82252944,
  sender 82252940, ledger table 2007586b) is SEPARATE from interactive
  routing and from orchestration operational alerts.

## Gateway code repairs (2026-10-07, local only — NOT yet deployed)

The handoff's five code-review suspicions were all CONFIRMED, and the two
correlation defects are now fixed in the local checkout with regression tests
(suite 85 → 87 passing):

1. `conversation_busy` (`server.mjs`): was thrown after durable run creation
   with no terminalization/decoration → generic 400 + non-terminal run. Fixed:
   terminalizes via `finishInitializationFailure`, decorated with
   `withGatewayRunId`, added to `KNOWN_CODES` with stage
   `conversation_coordination`. Caller now gets 200 `gateway_error` + run ID.
   Still open by design: the V2 design's five-second bounded wait is NOT
   implemented (still fails immediately) — behavior change needing Josh's
   sign-off.
2. Final-message fetch + runtime-connection-link fetch after the run already
   terminalized: both now decorated with `withGatewayRunId` so failures return
   correlated 200 `gateway_error` instead of generic 400. Note: the durable
   record stays `finished` (first-writer-wins cannot flip it) while the caller
   sees `gateway_error` — accepted mismatch, correlation is the fix.
3. Migration script TERMINAL_STATUSES omits `source_timeout` — confirmed,
   unfixed (forensic-only path; fix when migration is next touched).
4. Forwarder acks non-429 4xx after sanitized log (event dropped, no DLQ) —
   confirmed, unfixed (needs a reconciliation design decision).
5. Forwarder lacks deploy script/.env.example/health/e2e test — confirmed,
   unfixed.

These are LOCAL fixes; serving revision `00079-xqq` still has the old code.
Deploying requires the full gateway deployment procedure (zero-traffic
candidate first).

## GCP audit (verified live 2026-10-07)

- Cloud Run: 100% traffic on `00079-xqq` ✓; rollback `00077-28d` at 0% with
  tag `rk-rb` ✓; minScale 2, 1 vCPU / 512 Mi, concurrency 8 ✓.
- Firestore: native-mode `(default)` DB in us-east1 ✓.
- Secret Manager: all 16 secrets present (14 gateway + invoker key +
  telemetry token) ✓.
- Telemetry forwarder `multi-genie-telemetry-forwarder-dev` live, 100% on
  revision `-00002-5rl`.
- **Drift found:** both services have `run.googleapis.com/ingress: all`
  (`ingress-status: all`). The handoff prose says "private ingress" — privacy
  is currently enforced by IAM (`roles/run.invoker` on the Workato invoker),
  not by network ingress. Either fix the prose or set ingress to `internal`
  (with Serverless VPC/allowlist as appropriate) before any release gate.
- Josh initially linked GCP project `workato-gws-semantic-mcp-poc` — wrong
  project; corrected to `mult-genie-poc`.

## Legacy-tree mining additions (2026-10-10, from the ChatGPT archive docs)

Platform lessons NOT in the sections above (several miner "NEW" items were
already captured in Gotchas — the 120s boundary, headless base URL, 422
stopped-source, timestamp-order selection, per-affinity leases are up there;
Jira connector traps + zArchive semantics + RecipeOps design went to
domains/workato-platform.md):

- **VUA does not propagate through Headless sub-agent calls** —
  `X-IDP-User-Id` establishes Workato Identity for the Headless conversation
  but the user's provider OAuth/VUA does NOT transfer to the specialist; the
  specialist must emit `runtime_connection.auth_required` (this is the
  trusted-authorization-bridge invention around a platform limitation).
- **`auth_required` is TERMINAL** — some source Genies emit it then only SSE
  heartbeats; waiting for `processing.finished` after it converts a valid
  login requirement into a user-visible timeout or misleading rate-limit
  error. A runtime-connection pause never resumes the original stream.
- **`authorized` runtime-connection state ≠ license/permission/action
  success** — existing connection proves existence only; Genie user-group
  entitlement and downstream connector auth are separate gates; a missing
  wrapper end-user-group grant fails Headless with `403 access_denied`
  before VUA/OAuth even starts.
- **Workato HTTP connection header-auth trap**: connection must be
  `auth_type=headers` with `header_pair` as header-name/value array objects;
  a mis-shaped connection (`auth_type=header`) reports
  `authorization_status=success` while silently omitting the Authorization
  header at runtime — "appears authorized", 401 on first real call.
- **Cloud Run dual-auth wiring**: Google audience-bound ID token in
  `X-Serverless-Authorization`, application workload credential in
  `Authorization`; both layers enforced independently (IAM success ≠ the
  gateway's own credential check).
- **Skill re-registration + fresh conversations**: after editing/restarting
  an attached skill recipe, wait for Agent Studio skill re-registration and
  always test in a NEW source conversation — existing ones retain prior
  state, prior failures, and the tool catalog they started with.
- **Wrapper-Genie job-description mirroring rule**: tool descriptions are
  model guidance, not enforcement — the wrapper JD must mirror the source
  MCP's contract (capability scope, preferred tool sequence, deprecated
  labels, auth semantics, bounded call shape; worked example: Gmail Genie
  discovery restricted to `search_mail` → `read_thread`).
- **Slack rendering constraint**: Slack does not render Markdown pipe
  tables — Main converts returned pipe tables to compact bullets without
  changing values. No supported way to inject nested specialist `skill.*`
  events into the parent's native Slack card — the tool trail embedded in
  response text is the deterministic pattern.
- **Workspace/trigger mismatch silent death**: one Genie can hold multiple
  Slack-workspace chat interfaces, and a Slack-by-Workato MCP connection in
  a DIFFERENT workspace than the active trigger (Workato vs Workato BT AI)
  posts fine and produces ZERO Genie conversations. Prove delivery via the
  Agent Studio conversation API (count conversations since timestamp). A new
  trigger needs a fresh Slack app (client ID/secret/signing secret — no
  existing-app picker). Cross-ref: the silent-death triage discriminator in
  [[workato-slack-bot-connections]].
- **Telemetry transport poison-message semantics**: acknowledge
  malformed/contract-invalid payloads and non-retryable 4xx after a
  sanitized failure log (no poison retry); return non-2xx on 429/5xx/
  timeouts (retry); the gateway never waits on the telemetry path; no DLQ
  (named gap). Telemetry field contract: a field is allowed only with a
  verified producer or documented projection derivation; "empty" is never a
  placeholder; deliberately-absent fields documented with reasons.
- **Registry-activation gate pattern**: fail-closed checked-in template with
  `__REQUIRED__` markers; additive `route_key` compatibility before cutover;
  never edit a registry doc in place (new versioned generation, validate at
  zero traffic, verify targeted route fails closed while unaffected routes
  pass); partial activation prohibited.
- **Fault-injection honesty**: explicitly name what cannot be simulated
  (caller timeout/disconnect, real source timeout, real omission of
  `processing.finished`) rather than claiming a complete matrix.
- **Latency benchmark cohorts**: separate clean cohorts from queue-stress
  evidence; concurrent batch times excluded from percentiles; bucket-derived
  p50/p95 are upper bounds; never set SLOs from one-sample observations;
  match auth-first vs already-authorized attempts separately.
- **Cost model (POC closeout)**: Cloud Run gateway infra is NOT the cost
  center — warm baseline ~$9.86/mo, ~$0.00217 for a complex 86s turn,
  $10–118/mo across modeled scenarios; specialist/LLM/source latency and
  per-user auth dominate the experience.
- **Notification-lane design rules**: acquire the durable business claim
  before async dispatch; test-recipient overrides belong at ingress/recipient
  selection, never in shared downstream dispatch; Event Streams topic as
  decoupled transport with versioned event contract (`event_id` dedupe,
  allowlisted publishers/types, `recipient_subject` never from prose).
- **State additions**: active Slack trigger `ginct-AbnfxRDe-RArLEb-CD` in
  the Workato BT AI workspace (DM `D0C6B0FSAHF`); serving revision digest
  `sha256:2f0862bf...`. The workspace git repo has ZERO commits — every
  file untracked, no rollback baseline (first-commit recommended).
  Multi-MCP Orchestration sibling folder is an empty shell (bare git, no
  commits) — all Multi-MCP substance was absorbed here.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Multi-Genie Orchestration POC Architecture](../../kb-corpus/confluence/extbt/2870903050-multi-genie-orchestration-poc-architecture.md)
- [Adding specialist Genies and MCPs to Multi-Genie Orchestration](../../kb-corpus/confluence/extbt/2872377507-adding-specialist-genies-and-mcps-to-multi-genie-orchestration.md)
<!-- kb-bridges:end -->
