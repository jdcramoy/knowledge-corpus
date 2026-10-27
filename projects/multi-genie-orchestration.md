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

## AWS migration (started 2026-10-24, dev live 2026-10-25 — BSYS-29946)

Josh directed a full GCP→AWS migration, dev first, prod-separable, with TRUE
token streaming. Decisions (grill-gate, 2026-10-24): App Runner (not Lambda —
native streaming, container lift-and-shift), SQS FIFO token side channel +
Workato poller recipe for Slack rendering, ONE account with two cloned CDK
environments + dev→prod pipeline (not multi-account), CDK TypeScript.

- Live dev gateway: App Runner `mg-dev-gateway` (account 649832717182,
  us-east-1), URL `yzwhvnjabf.us-east-1.awsapprunner.com`,
  `/v1/health` → 200 `{status:ok, durable_state:true, state_schema:2}`.
- CDK app: `~/Documents/ChatGPT/Multi-Genie Orchestration/infra-aws/` —
  FOUR stacks per env, strict deploy order: `mg-dev-ecr` → `mg-dev-secrets`
  → (docker push) → `mg-dev-gateway`. mg-prod stacks synthesized, NOT
  deployed. `maxScale`: dev 10 (budget), prod 100 (GCP parity).
- Port architecture: single DynamoDB table `mg-dev-gateway-state`
  (pk=namespace, sk=entity:opaqueDocId, ttl attribute, `seq` CAS counter);
  SAME state-crypto envelope as GCP. `DynamoDbStateStore` = interface-exact
  port of `FirestoreStateStore` with optimistic CAS retry loops (lost race →
  re-read → re-decide; StateStoreError propagates without retry).
- TRUE streaming: `TokenStreamPublisher` → `mg-dev-token-stream.fifo`
  (MessageGroupId=runId, per-run seq, content = {run_id, seq, mode, delta});
  deltas extracted from `agent.message` SSE events, best-effort with a
  3-failure degrade budget; end marker published in the single `finishRun`
  chokepoint. Poller recipe (Workato, NOT BUILT) renders Slack.
- Secrets: `mg-dev/gateway` (Secrets Manager) = JSON env-var map loaded at
  container boot by `aws-runtime-secrets.mjs` (fills only unset env vars).
  Loader: `infra-aws/scripts/load-aws-gateway-secrets.py` reads the 0600
  bundle's `aws_secrets_manager_entries`, skips GCP-only invoker key.
  **Bundle is MISSING headless keys for Deal Desk + Enterprise Data** —
  those routes cannot wire until sourced.
- Telemetry: `safeLog` was ALWAYS console→Cloud Logging (no in-app Pub/Sub
  code) — AWS chain is pure infra: CloudWatch Logs → subscription filter →
  forwarder Lambda → `mg-dev-telemetry` SQS → API platform. NOT yet built
  (the GCP forwarder Pub/Sub push → AWS SQS poller lambda still TODO).
- Suite: 97 tests / 94 pass / 3 skipped (Firestore-emulator trio). 7 new:
  3 DynamoDB-Local (concurrency, first-writer-wins with 25-way contention,
  restart-resume) + 4 publisher unit tests.

AWS gotchas paid for in session:
1. App Runner needs BOTH roles: instance role (runtime: ddb/sqs/secrets) AND
   an ECR access role trusted by `build.apprunner.amazonaws.com` — omitting
   the latter fails CreateService with "Authentication configuration is
   invalid" (misleading; it's image-pull auth).
2. App Runner service creation GATES on health checks — a fail-closed
   container with an empty secret bundle never stabilizes and the deploy
   rolls back, ORPHANING the DynamoDB table on rollback failure. Hence the
   pre-deploy ecr/secrets stacks. Clean up orphans (delete-table + watch
   status) before redeploy; "Early validation: already exists" during
   changeset creation = stale orphan, not a CDK bug.
3. `/v1/health` is now UNAUTHENTICATED (App Runner probes cannot present
   credentials; body is content-free). GCP gated it behind IAM. Data paths
   unchanged. Posture delta: App Runner endpoint is public + app-token
   gated — the GCP dual-layer (IAM ID token + workload token) is down to
   one layer (workload token) on AWS. Document for prod design.
4. Failed CFN deploys can leave ROLLBACK_COMPLETE stacks — delete the stack
   before redeploying (CDK cannot update it).
5. `aws secretsmanager` package = `@aws-sdk/client-secrets-manager`
   (hyphenated; `secretsmanager` 404s on npm).
6. DynamoDB CAS loop must CATCH `TransactionCanceledException` and continue —
   forgetting it converts lost races into thrown 500s (first-writer-wins
   dies silently until a concurrency test catches it).
7. AWS CLI v2.38 prompts "Configure AWS skills and the AWS MCP server for
   your AI coding agent(s)? [y/n/never]" after `aws configure` — answer n.

Pending for done-criteria: Workato dev route re-point + SQS poller recipe
(Phase 4 = Workato build: Jira + living manifest at build start), telemetry
forwarder lambda, dev→prod pipeline, key rotation (josh-admin key exposed in
a session screenshot 2026-10-24 — rotate at Phase 2 cutover).

## Phase 4 COMPLETE (2026-10-25): e2e WORKING through AWS + the subject-format root cause

- **Live proof**: direct completion through the AWS gateway returned
  `finished` in **75.8s** with a REAL Workday answer (FTO policy) via the HR
  specialist + tool trail `get_my_time_off_completed`. Run c6b54f1b.
- **Workato assets built** (manifest 371553, mirror
  `~/orca/projects/multi-genie/manifests/BSYS-29946.manifest.json`, 79 rows,
  5 selected, zero Not-found): canary recipe **83330363** "Route to HR
  Genie — Streaming Gateway (AWS)" (skill skl-Ac8XJp4d-oYxoXn-CD, converted
  to skill, ATTACHED to Main), poller **83330387** "MG AWS Token Stream
  Poller (dev)" (SQS FIFO trigger + data-table proof rows, RUNNING),
  connections **22372771** "CON | Multi-Genie Gateway | AWS App Runner"
  (header-auth Bearer workload token, base URL = App Runner) + 22372634
  (SQS), data table **1adeae6e** "MG AWS Canary Token Stream".
- **Main Genie cut over for HR in dev**: instructions mapping edited
  "HR → Route to HR Genie — Streaming Gateway **(AWS)**" (11,113→11,119
  chars, everything else byte-identical). Canary skill attached to Main via
  AIRO `skills_to_add` (additive; 13 skills, 0 inactive).
- **THE ROOT CAUSE of every 401** (`user_nonactive_or_missing`): the
  Headless API resolves `X-IDP-User-Id` against **Workato Identity** — the
  subject must be the Identity user ID (`kfW3CihtZuxE3cSNmqJESt` format,
  from `GET /api/iam/users?query=<email>`), NOT an email, NOT the numeric
  workspace user id. User must be active AND in a user group allow-listed
  on the genie (HR genie allowlists "Everyone"; its user-group config was
  touched 2026-10-22). Cited:
  docs.workato.com/en/agentic/agent-studio/chat-interface/headless-api-troubleshooting.md.
- **Headless API does NOT stream tokens** (definitive, decoded from a real
  75s turn): SSE = `processing.started, skill.running, system.ping×N,
  skill.completed, agent.message` — ONE full agent.message at the end. True
  token-by-token streaming is impossible via Headless on ANY compute until
  Workato emits token-level events. The FIFO side channel WORKS (end
  markers per run + poller drain verified); today it can carry event-
  lifecycle progress, not token deltas.
- **HTTP connection URL allowlist**: a rest connection with a base URL
  REJECTS absolute URLs to other hosts ("only request with base URL … is
  allowed") — the canary needed its own connection (22372771), not URL
  override against 22111204.
- **Header-auth connection contract** (Dev API): `auth_type: "headers"` +
  `header_pair: [{"param": <name>, "value": <value>}]` + `url` (base) +
  `case_sensitive_headers: true`. The UI Connect flow is the only thing
  that flips authorization for HTTP connections (API create/update stores
  fields, status stays null → AIRO refuses the connection as inactive).
- **Recipe-account_id swap**: raw PUT IGNORES config account_id changes
  (silent); the working path = AIRO `select_connections` + `push` (stop →
  select → push → start).
- **Skill activation gotcha (new)**: `convert_to_skill` while the backing
  recipe is STOPPED registers the skill INACTIVE on the genie
  (`inactive_skills_count: 1`) — the genie then silently calls the OLD
  route. Fix: restart the recipe (skill flips active immediately).
- **Deviation logged**: I regenerated the HR Worker genie client key
  (gincl-AbWrGoYr-NBbHtC-CD) while chasing the 401 — the old key was fine.
  The regeneration INVALIDATED the key GCP Secret Manager holds → the GCP
  HR route (82247224) is broken until GCP's secret is refreshed (needs
  `gcloud auth login` — Josh, interactive). AWS already has the new key
  (secret version 0c9cee3b) and works.
- **GCP HR route also 400s on assign_task probes** — pre-run rejection
  (app_type/identity gate) — the gateway correctly refuses non-Slack
  contexts; the REAL e2e front door is a Slack DM to Main (not yet run —
  needs one Slack message from Josh in the BT AI workspace).
- TEST-probe assets (manifest-exempt, standing order): TEST AWS Migration
  Probe Genie (gin-Ac8YFcKG-Dcm9se-CD, inactive), TEST AWS e2e probe runner
  (83331083, stopped — force-run on demand).
- Slack progressive render: the poller's Slack step is REMOVED for now (the
  Alerts Dispatcher bot's postable channel is unknowable from this
  session's Slack scope — workato.slack.com ≠ BT AI workspace). Data-table
  proof surface stands in. One channel ID from Josh completes the render.

## FULL CUTOVER (2026-10-25): ALL 12 routes live through AWS in dev

- 11 remaining routes ported by a builder agent following the proven canary
  template (210 tool calls, zero failures): CPQ 83332882, Ask Deal Desk
  83332883, Enterprise Data 83332885, Calendar 83332891, Gmail 83332894,
  CSM 83332895, GRC 83332899, Cora 83332907, BT 83332911, Support IDOL
  83332914, Salesforce Reader 83332927 — all RUNNING, all converted to
  skills while running, all attached to Main (24 skills, 0 inactive).
- Main instructions: ALL 12 domain mappings now point at the (AWS) routes
  (11,185 chars; only the mapping lines changed). GCP routes remain
  attached-but-unmapped until decommission at promotion.
- **Missing specialist keys SOLVED**: Enterprise Data + Deal Desk had no
  headless keys in the bundle — new genie clients created + attached via
  the Developer API (`POST /api/agentic/genies/clients` → attach via
  `POST /api/agentic/genies/:id/clients`), keys into the AWS secret
  (version f43e6621, 14 keys), App Runner recycled (pause→resume).
- Spot-verified through the AWS gateway: GRC `finished` 17.6s (real
  WSPL009 policy answer), CSM `auth_required` (canonical official-link
  path), Enterprise Data `auth_required` (same). All three terminal paths
  proven across specialists.
- Slack progressive render LIVE: poller posts each FIFO message to BT AI
  workspace channel C0C228C00BU (4/4 + sweep jobs green). v1 renders raw
  stream JSON; parse-based pretty render blocked on formula whitelist
  (no JSON.parse) — upgrade when formulas allow or via js_eval if the
  degradation lifts.
- **GCP secret repair DONE**: fresh HR key added as GCP secret version 3,
  Cloud Run revision redeployed at 100% (`--update-secrets` targeted
  update). GCP HR route restored.
- Manifest 371553 updated cumulatively: 90 rows, 16 selected (all AWS
  assets), zero Not-found. Mirror committed (154fd97).
- REMAINING for prod promotion: telemetry forwarder Lambda (CloudWatch →
  SQS → API platform), dev→prod CDK pipeline, Slack e2e from a REAL
  employee DM (the true front door), red-team gate, deployment request.
- SECURITY NOTE: a Headless auth-link JWT was briefly visible in session
  output (expired by design); redact that class from all future output.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Multi-Genie Orchestration POC Architecture](../../kb-corpus/confluence/extbt/2870903050-multi-genie-orchestration-poc-architecture.md)
- [Adding specialist Genies and MCPs to Multi-Genie Orchestration](../../kb-corpus/confluence/extbt/2872377507-adding-specialist-genies-and-mcps-to-multi-genie-orchestration.md)
<!-- kb-bridges:end -->

## End-to-end verification sweep + DD/BT replacement-genie repair (2026-10-25, session 30a54eab)

- **11-probe Main→canary wiring proof**: cloned the TEST probe runner
  (assign_task_to_genie → Main) and fired one safe-read prompt per route.
  Every canary received Main's call (CPQ canary job + Gmail artifact +
  graceful Main degradation on the gateway 400s) — per-route Main→canary
  wiring proven 11/11. Re-confirmed the known finding: the assign-task path
  emits a non-Slack app_type and the gateway's router gate correctly refuses
  it (router_context_invalid). The TRUE front-door proof remains one real
  Slack DM from Josh (pending).
- **Direct-gateway smoke matrix** (curl, workload token script-side, Slack
  interface, subject = Workato Identity ID kfW3CihtZuxE3cSNmqJESt): CPQ
  finished 22s; DD finished 13s (after repair below); Calendar finished 21s
  (2 tools); Gmail finished 21s (4 tools); GRC finished 29s (2 tools); Cora
  finished 14s (1 tool); Salesforce Reader finished 4s; Enterprise Data
  auth_required (correct); CSM auth_required (correct); Support IDOL
  access_denied (correct group boundary); BT access_denied (correct gate,
  pending owner's group grant — see below). My Oct-7 correlation fixes are
  LIVE on App Runner (correlated gateway_error + run ID + terminal ledger).
- **SUBJECT GOTCHA (cost me a smoke run)**: the Headless subject is the
  Workato Identity ID (kfW… string via GET /api/iam/users?query=<email>),
  NOT the numeric collaborator member ID (6939715) — wrong namespace gives
  401 user_nonactive_or_missing on EVERY route at once.
- **DD + BT source genies were REPLACED by their owners** (discovered via
  the 422-on-conversation_create signature): BT Genie GO
  (gin-AWWsELCn-DatcpM) → **BT Genie 2.0** (gin-AbzEtfoT-LgXXem-CD);
  Ask Deal Desk (gin-AaQ9DkRJ-9Ppmwx-CD, renamed "OUTDATED…") →
  **Ask Deal Desk Genie** (gin-AbrwJXaE-AxzbQE-CD). Repair: fresh headless
  clients created + attached (attach param is **genie_client_id**, NOT
  client_id — 400 "Missing parameter genie_client_id" otherwise), keys into
  bundle + AWS secret (version 0ae72319, 14 keys), CDK env handles +
  ALLOWED_GENIE_HANDLES updated, cdk deploy recycled App Runner, canary
  recipes 83332883/83332911 re-pointed. Committed 7a6e316.
- **TRAP: raw recipe PUT silently ignores code changes** (same class as the
  account_id silent-ignore): handle patch via `PUT /api/recipes/<id>`
  returned success and persisted NOTHING. Working path = AIRO
  recipe_builder (pull → set_input_field request.body.genie_handle → push)
  with stop → push → start.
- **TRAP: local bundle vs AWS secret drift** — the full-cutover session
  loaded DD/ED keys straight into the AWS secret without the bundle; my
  bundle-based loader run then OVERWROTE the secret minus those two keys
  (caught before any recycle; repaired by adding both entries to the
  bundle). Rule: the 0600 bundle is the single source; always add entries
  there BEFORE running the loader.
- Duplicate-canary hygiene: this session briefly created 9 duplicate AWS
  canary recipes (unaware of the parallel builder session's port); all 9
  created-and-deleted same session, never attached, never in the manifest.
  One stopped leftover "Copy of Route to HR Genie — Streaming Gateway
  (AWS)" recipe **83332952** from that session's pipeline remains — delete
  candidate, not mine.
- **Remaining Josh items**: (1) one real Slack DM to Main in the BT AI
  workspace = the true-front-door e2e (the only proof still missing);
  (2) BT Genie 2.0 user-group grant so the BT route serves Josh's identity
  (source-owner decision); (3) GCP DD/BT route recipes now equally broken
  (old handles) — GCP is rollback-only; repair at promotion time or let
  GCP roll off.

## TRUE-FRONT-DOOR INCIDENT (2026-10-26): Josh's real Slack DM failed — root-caused and fixed

- Symptom: "Who is my manager" DM to Main in the BT AI workspace → Main
  relayed a correlated `gateway_error` (run 36a3d864).
- Routing reality: Main picked the **GCP** HR route skill (82247224, both
  HR skills attached per the deliberate dual-attachment cutover), so the
  turn went through **Cloud Run**, not App Runner.
- Root cause: Cloud Run traffic was serving revision **`00077-28d`** (the
  Oct-1 rollback revision) instead of `00080-ttk` (the Oct-25 13:17 UTC
  `--update-secrets` repair deploy). `00077`'s warm instances carried the
  PRE-regeneration HR key → Headless 401 at conversation_create. The
  full-cutover session's "redeployed at 100%" was never actually re-proven:
  its evidence job (j-Ac96DAzT, "succeeded") WAS this failed DM (HTTP 200
  envelope carrying the gateway_error inside).
- Fix: `update-traffic --to-revisions …00080-ttk=100` (rollback `00077`
  retained at 0% with tag rk-rb). Verified with a real HR turn through
  Cloud Run: **`finished` in 81.2 s — "Your manager is [colleague]…"**,
  tool trail `get_my_manager`. GCP HR route is green again.
- Lessons: (1) a route recipe job showing `succeeded` can still be a
  specialist failure — the gateway_error travels inside a 200; check
  `gateway_status`, not the Workato job flag. (2) Secret-repair deploys are
  not done until traffic actually serves the new revision AND a live turn
  proves the credential. (3) Cloud Run secrets bind at INSTANCE boot when
  unpinned ("latest") — warm instances of an old revision keep stale
  credentials indefinitely.
- Note: AWS gateway (App Runner) unaffected; its HR path was separately
  proven (75.8 s Phase-4 + smoke matrix).


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Multi-Genie Orchestration](projects/multi-genie-orchestration.md) — Main Genie routes to 12 specialist Genies via private Cloud Run gateway (mult-genie-poc, rev 00079-xqq); POC complete and FROZEN pending Product/leadership/BT direction; canonical workspace ~/Documents/ChatGPT/Multi-Genie Orchestration/ — read ORCA-CLAUDE-CODE-HANDOFF.md in full before any work; Workato project 17923915, epic BSYS-28503; open enforcement gaps (Cora/BT/Deal Desk), registry inactive, ingress=all drift found 2026-10-07
## ITERATION 1 DIRECTION (2026-10-26, Josh + Patricia + Sen Rong session) — tickets filed

- Overall build endorsed. Direction: (1) descope the raw-MCP Gmail + Calendar
  specialists for iteration 1; (2) dynamic genie-access discovery — sync each
  user's accessible genies from the Developer APIs into an indexable data
  table, consulted OUTSIDE the hot path, so Main presents/routes only what
  the caller can access; (3) v2: decision engine for routing (Jev / Workato
  Decision Models) as shadow evaluator only; (4) use the Internal AI
  Directory to enumerate production genies and onboard candidates.
- Tickets (all under epic BSYS-28503, Story type, points set at creation):
  BSYS-29996 complete-AWS-cutover (3) — DONE 2026-10-26: 12 GCP skills
  removed via the documented remove_skills API (AIRO genie_update silently
  no-ops on skill attachment changes!), skills_count 12→, verified 12 active
  AWS skills, GCP recipes still running as rollback, evidence comment posted.
  BSYS-29997 Gmail/Calendar descope (2) — DONE 2026-10-26: correct attached
  handles skl-Ac8mnhbF/skl-Ac8mmeWr removed (12→10 skills), Main instructions
  edited (GMAIL/GOOGLE_CALENDAR now out-of-scope bullets, map lines removed,
  scope-response sentence updated; byte-verified after PUT), behavioral proof:
  calendar + mailbox probes returned the EXACT scope response with
  artifacts:[] and no canary jobs. BSYS-29998 access-discovery build (5) —
  IN PROGRESS: manifest 372064 created (116 rows), table MG Genie Access
  Index 6b606ebe/165362 (per-user design: identity_user_id +
  accessible_genies CSV + via_user_groups + synced_at — chosen over
  user×genie rows for task cost), sync + access-check recipes being built by
  a builder agent. BSYS-29999 AI-Directory intake (3) — blocked on the
  ai-directory MCP being up. BSYS-30000 v2 decision engine (2) — backlog.
- Design notes for the access index: one row PER USER with a precomputed
  accessible-genies CSV (computed at sync from genie user-group allowlists ∩
  user groups from /api/iam/users — 1738 users, 18 pages of 100); runtime
  check = one indexed table search using the TRUSTED caller identity.
  Task-cheap via upsert_records_batch + delete_records_by_condition (the
  proven primitives in the Registry Refresh recipe 82285271).
- 10 serving routes after descope: HR, CPQ, Ask Deal Desk, Enterprise Data,
  CSM, GRC, Cora, BT, Support IDOL, Salesforce Reader.

## ACCESS DISCOVERY BUILD COMPLETE (2026-10-26) — BSYS-29998

- Data table MG Genie Access Index (6b606ebe / 165362): ONE row per active
  Identity user — identity_user_id, accessible_genies (CSV of handles,
  computed at sync), via_user_groups, synced_at. Per-user-CSV design chosen
  over user×genie rows for task cost (batch upsert = 1 task per page).
- Sync recipe 83347201 (hourly, Automation folder, RUNNING): refreshes 10
  genies' group allowlists → 18 IAM user pages → one Ruby join per page →
  batch upsert → prune stale. Full pass 17 s. mask_data on user-data steps.
- Access-check skill 83347839 (skl-Ac9KoPar-c6tcdP-CD, attached to Main,
  RUNNING — note the stopped-recipe skill-inactivation gotcha forced a
  start): reads ONE row by the caller's TRUSTED identity.
- Main instructions: Access Control rule — check before any specialist call;
  inaccessible = scope response with no call; "which genies can I use"
  answered ONLY from the check.
- Proven: sync pass differentiates correctly (Everyone-only = 7 genies;
  T32-CSM member gains CSM; BT 2.0 + Support IDOL reachable by nobody);
  "which genies" probe → honest table-driven answer; "Who is my manager"
  from a zero-access caller → check ran → refused with NO specialist call.
- New traps paid for: adhoc HTTP foreach items are {value:…} wrappers (path
  pills must index ['value'] — two failed runs); Ruby-step input mapped the
  pill NAME literally ("foreach_4") writing garbage into the index (caught
  by table read-back, fixed via datapill mode); recipe start failed
  "account_id can't be blank" → fix = AIRO select_connections + push;
  RLM does NOT package agentic_genie rows (Main missing from the export
  ZIP — genie import is a manual deployment-planning step); the export
  pre-signed URL expires in 10 SECONDS (download immediately).
- Manifest 372064: 119 rows, 4 selected, export 42326741 completed +
  ZIP-verified.
- Josh's real-user positive-path proof: one Slack DM "which genies do I
  have access to" — expect his ~7 accessible specialists.
