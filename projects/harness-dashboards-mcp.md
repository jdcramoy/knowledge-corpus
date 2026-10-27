# harness-dashboards-mcp

Live: 2026-10-13 build. Repo: `~/Documents/harness-dashboards-mcp/` (branch `build/mvp`).

**What:** Read-only remote MCP server exposing the ENTIRE harness's tracked data to
Claude Dashboards (claude.ai beta 2026-10-08). 12 tools: harness_overview,
mission_control_query, dropped_sessions, build_ledger_query, activity_timeline,
costs_query, roi_summary, governance_query, manifests_query, knowledge_search,
memory_and_skills, transcript_sql (SELECT-only DuckDB over transcript Parquet).

**Architecture:** hourly launchd sync (`com.harness.sync`, logs at
`~/.claude/knowledge/harness-sync.{out,err}.log`) → `gs://harness-dashboards-mcp-data`
in project `harness-dashboards-mcp` (dedicated project created 2026-10-13 after Josh
called mult-genie-poc wrong; billing attached by Josh in console after IAM denied CLI
linkage) — JSON envelopes with `synced_at` + Parquet; fail-closed secret sweep (JWT
pattern tuned to 3-segment after false-positive on Google Slides base64 IDs) →
stateless FastMCP on Cloud Run (`harness-dashboards-mcp`, us-central1,
min-instances 1, ~$10-15/mo) → claude.ai custom connector (Streamable HTTP + Google
OAuth via FastMCP GoogleProvider, redirect_path `/api/mcp/auth_callback`).

**OAuth client (2026-10-13, browser-driven):** Web client "Harness Dashboards MCP",
client ID 268308829249-dcujuovat93j3tmo2m52t1uuhn9ash4k.apps.googleusercontent.com;
secret in Secret Manager (`harness-mcp-oauth-client-id/-secret`, runtime SA bound as
secretAccessor); app External/Testing with josh.cramoy@workato.com as test user
(external apps in Testing restrict logins to test users). GCP Console silent no-op
lesson: form-submit buttons need the full pointer-event dispatch sequence, dialogs'
confirm is "Save", not the wizard's Next.

**State 2026-10-13 — DEPLOYED AND VERIFIED:** service live at
**https://harness-mcp-3ow3f2n3da-uc.a.run.app** (connect claude.ai to `/mcp`).
Live-verified: /health 200; POST /mcp unauthenticated → 401 (FastMCP OAuth wall);
/.well-known/oauth-authorization-server → 200 with issuer/authorize/token/register
(dynamic client registration). All 30 tests pass; all 12 tools live-called against
real data. Deploy traps paid for: (1) gcloud run --source uploads .venv/.git without
a .gcloudignore (400 MB stall); (2) BASE_URL=PLACEHOLDER bootstrap crashes
GoogleProvider's pydantic URL validation — phase 1 must run auth-less; (3) IAM
--no-allow-unauthenticated blocks OAuth DISCOVERY — claude.ai can't register; use
--allow-unauthenticated and let FastMCP's OAuth be the app-layer front door;
(4) buildpacks need a Procfile (web: python -m server.main).

**REMAINING (Josh, claude.ai side only):** (1) enable Dashboards in Organization
settings > Artifacts; (2) Org settings > Connectors > Add custom connector, URL
`https://harness-mcp-3ow3f2n3da-uc.a.run.app/mcp`, OAuth via the Google client;
(3) build the first dashboard (harness_overview tiles + weekly spend + closeouts +
redteam verdicts). Full OAuth dance unverified until connector registration — that's
the first live exercise.

**Key constraint learned:** claude.ai custom connectors require remote Streamable HTTP
+ OAuth — no stdio, no API keys. Local MCP servers (brain, kb) cannot attach directly.

**Snapshot scale observed:** ~1,750 files, 31 MB total; transcripts 12 MB as Parquet
(1,587 month-partitioned files). Velocity/shipped raw JSONs are multi-MB — tools
summarize rather than dump.

## Additions 2026-10-14

- **Corpus store added (13th tool `corpus_search`):** syncer builds its own FTS index
  over the KB corpus text sources (12,729 docs / 60,189 chunks / 116 MB DuckDB,
  ~35s/run) — the native `kb.db` (2.1 GB) is vec0-extension-locked to its build
  toolchain and won't even enumerate tables without it, so self-owned FTS is the
  dashboard-grade primitive. github crawl (23k code files) intentionally excluded.
- **Cost change:** Cloud Run min-instances 1 (~$10-15/mo, was scale-to-zero) —
  scale-to-zero recycled containers mid-OAuth; FastMCP's in-memory grant store then
  401'd the token exchange (05:57 incident). Always-warm also kills cold starts.
  `--min-instances 1` pinned in deploy.sh.
- **claude.ai per-chat tool cache:** new tools require a fresh chat (or connector
  off/on) — the chat loads the catalog once at session start.
- Launchd sync fix: explicit `storage.Client(project=...)` — launchd env can't infer
  the project from ADC alone; sync froze 23:30→04:30 UTC before the fix.

## Security model finalized 2026-10-14 (post-incident)

- **The regression chain:** (1) entrypoint bug — `python -m server.main` served the
  `__main__` duplicate app with ONLY harness_overview while tool modules registered
  on the separately-imported `server.main` instance (claude.ai never saw 12 tools);
  fixed via `server/__main__.py` + `python -m server`. (2) An email-allowlist
  middleware blocked EVERYONE (incl. Josh) because FastMCP's OAuthProxy JWTs carry
  NO upstream user identity (iss/aud/client_id/scope only — no sub/email). Removed;
  verified via live OAuth probe (DCR→PKCE→consent→token→tools/list = 13, tool call
  green).
- **THE per-user gate is Google's Testing-mode test-user restriction** (app External/
  Testing, josh.cramoy@workato.com sole test user). Never publish the app. Connectors
  are personal/Individual scope in claude.ai — org never sees it.
- Probe quirks for future ops: FastMCP `/authorize` is POST-only; DCR clients
  evaporate on redeploy (in-memory storage); consent flow = consent page → Google
  account → Continue → localhost callback (code in URL bar); notifications/initialized
  returns 202-empty.

## Handoff (2026-10-14, session end)

**Status:** ALL DONE AND LIVE. Service deployed + OAuth verified end-to-end; 13 tools
served from the cloud (verified via full DCR→PKCE→consent→token→tools/list probe);
launchd sync healed; State of the Union dashboard built.

**Assets:** service https://harness-mcp-3ow3f2n3da-uc.a.run.app/mcp (claude.ai
connector "Harness Dashboards", personal/Individual scope) · repo
`~/Documents/harness-dashboards-mcp/` (branch `build/mvp`, 17 commits) · GCS
`gs://harness-dashboards-mcp-data` (project `harness-dashboards-mcp`) · dashboard
`~/Documents/harness-dashboards-mcp/dashboard.html` + generator
`scripts/generate_workato_dashboard.py` · local artifacts `/tmp/probe_token.json`,
`/tmp/harness-mcp-sync/`.

**Verified (evidence):** token exchange 200 (`POST /token 200 OK` 04:26Z log) ·
13 tools listed via authenticated MCP handshake (probe script output) · guard
fail-closed (`"token carries no email claim — not allowlisted"` protocol error) ·
launchd sync wrote 04:30:45Z + 04:35:05Z + 04:49:21Z manifests · cost-weekly line +
all dashboard numbers read live this session.

**Blocked:** nothing.

**Not verified:** a fresh claude.ai chat listing all 13 tools + a cloud
`corpus_search` call (per-chat tool cache was stale at last check; server side is
proven) · sustained launchd cadence beyond one scheduled tick (one-shot cron
verification was session-only and died with the session).

**Next step (cold):** open a fresh claude.ai chat → confirm 13 tools under Harness
Dashboards → run `corpus_search` prompt. If tools still show 1: connector off/on
toggle, then check `gcloud logging read 'resource.type="cloud_run_revision"
resource.labels.service_name="harness-mcp"' --project=harness-dashboards-mcp
--limit 40 --format="value(textPayload)"` (use CLOUDSDK_PYTHON=python3.11).
To regenerate the dashboard: `.venv/bin/python scripts/generate_workato_dashboard.py`.
To redeploy: `bash deploy/deploy.sh`.

## Serving-truth audit + dropped-sessions fix (2026-10-18)

Josh's ask: does the MCP serve ALL the correct data vs the local logs/ledgers,
reconciled against the claude.ai-built Harness Ops Console
(~/Downloads/harness-ops-console.html, SNAP blob parsed from it).

**RECONCILED GREEN:** store file counts match local (mission_control 3, costs 8,
memory_skills 106/107, knowledge 128/129, governance 36→37 — deltas = console
snapshot 05:41 vs sync 06:50 lag); gateway spend figures byte-match
gateway-actuals.json ($1,467.07 / 106,943 req / 95.7% cache); assets 13,105 from
the live wt manifest pull; alerts/redteam/ROI all match local files.

**RED FOUND — dropped sessions wrong at three layers, all fixed:**
1. ROOT CAUSE (one line): session-shadow.py deadman_sweep stored
   `recorded_for: int(mt)` (file mtime) but the dedup check compares against
   `int(anchor)` (last real activity) — the Oct 16 anchor fix changed the check
   but not the storage, so equality never held and EVERY sweep re-appended EVERY
   quiet session. 15,584 rows / 253 unique sessions (top session 1,567 copies).
   Fixed: `recorded_for: int(anchor)` (line ~475).
2. Ledger deduped 15,584 → 253 (backup dropped-sessions.jsonl.bak-20261018-dedup).
3. Tool `dropped_sessions` rewritten: dedup to newest per session, window_hours
   param, returns unique_sessions_in_window/total + raw_events_in_store + rows —
   a slice can never masquerade as the total again. Test updated; 31 tests green.

**COVERAGE WAVE (Josh-approved):** syncer + governance_query now serve 4 new
stores — triage/ (incl. jira-triage), decisions/, watchdog/ (reports), cortex/.
12 stores total sync. "ENTIRE harness" claim was overselling at 10 stores.

**DEPLOY PENDING (Josh-gated):** gcloud auth tokens expired mid-deploy
(`gcloud auth login` needed, non-interactive shell can't re-auth). Code is
committed-ready on build/mvp; next sync tick uploads the new stores to GCS
regardless; the NEW tool contracts go live only after redeploy
(`bash deploy/deploy.sh`, CLOUDSDK_PYTHON handled inside). Ops console regenerates
its SNAP on next refresh after that.

**DEPLOYED 07:35 UTC same day (Josh re-authed):** revision live at the same URL,
health 200 + OAuth discovery 200. Real sync run immediately (never wait for the
tick): 15 GCS prefixes incl. cortex/decisions/triage/watchdog; deduped ledger
uploaded (258 unique dropped-session rows, down from 15,584). Verify live tools
from a fresh claude.ai chat (per-chat tool cache): dropped_sessions with
window_hours + governance_query kinds triage|decisions|watchdog|cortex.

## INCIDENT + fixes (2026-10-20): auth-less serving window + deploy hardening

- **INCIDENT:** the two-phase deploy designed to bootstrap the service URL
  deployed an AUTH-LESS revision, and when the OAuth revision (00036) crashed
  at boot, phase 1 kept serving the whole harness UNAUTHENTICATED for ~37
  minutes (06:58-07:35 UTC). Detected via the console's "Not Found" authorize
  screen + probed POST /mcp (200 = no wall). Closed by rollback to 00034;
  exposure window documented here as the record.
- **00036 crash root cause:** FASTMCP_HOME moved onto a gcsfuse volume that
  wasn't ready at import; fastmcp mkdir raced the mount (ENOENT), then
  PermissionError (gcsfuse presents root-owned dirs; Cloud Run runs uid
  65532). Cloud Run cloud-storage volumes REJECT uid/implicit-dirs
  attributes, so the gcsfuse path is a dead end for OAuth state. DEAD END
  DOCUMENTED: durable OAuth state needs Redis or a custom GCS AsyncKeyValue
  store (parked, Josh decision). Until then: OAuth state is ephemeral,
  re-auth required after EVERY deploy.
- **HARDENING:** deploy.sh is now SINGLE-PHASE (URL is stable and known, OAuth
  envs + secrets deploy every time) - an auth-less revision can never be
  reachable again. Memory 4Gi (corpus_search needs it: 865MB index in
  memory-backed /tmp OOMs at 512Mi).
- **NEW TOOLS deployed:** corpus_stats (sidecar map, no duckdb download),
  knowledge_metrics (existing/created/queries; telemetry counts connector
  calls since 2026-10-20 into telemetry/tool-calls.json), delivery_metrics
  (live resolved-leverage, rolling-30d, MoM; replaces the stale velocity
  export that read October as 0.24x projection), jira_query with
  deployments_by_month + hotfixes_by_month + rolling_30d.
- **JIRA HISTORY TRUNCATION (Josh caught):** one big resolved>=-120d pull
  capped at 1,500 API rows (July kept 39 of 500+). Month-bounded JQLs fix it:
  3,960 team resolutions; josh monthly points true all year (Jul 104, Sep
  111, Oct 305). Identity matching by accountId (Jira withholds emails on
  assignee fields).
- Repo hygiene: .gitignore added (.venv/ had 10,300 tracked files).

## ORG-WIDE ACCESS (2026-10-22): the Workato MCP Proxy is live

- **The ask:** open the harness MCP to anyone with a workato.com email, behind
  Workato auth. **The pattern (Josh steered, no rebuild needed):** the Workato
  MCP Gateway's PROXY SERVERS — "External MCP Server" tool source in the
  Custom-server wizard; add the URL + auth method; Workato auto-registers with
  the upstream OAuth server (DCR, RFC 7591 — my FastMCP supports it; CIMD
  fallback exists). No rebuild, no recipes.
- **Live config:** server `mcps-Ac6NFwam-NwY-CD` "Josh Agentic Server
  Dashboard MCP", gateway URL **https://33485.apim.mcp.workato.com**,
  access_method workato_identity, published TRUE, end-user group Everyone
  (rVXKpZ8ZkAgFZSHGr7jKWw, 1,736 users), tool access 20 of 21
  (**transcript_sql excluded** from org access — reversible in the
  tool-access editor). Server instruction written to the LLM-facing
  description field.
- **Gateway perks now in play:** org-wide audit of every tool call, per-tool
  RBAC via subgroups, rate limits/quotas optional, SIEM streaming.
- **The deploy.sh lesson generalizes:** after ANY explicit traffic pin, deploys
  create ready revisions at 0% — deploy.sh now ends with
  `update-traffic --to-latest`. The connection wizard's "New connection" and
  template cards resisted automation; the wizard's OWN step controls clicked
  fine once inside.
- Upstream auth note: the proxy holds ONE Google OAuth token (Josh's consent);
  every org user acts through it — per-user backend auth (VUA) is NOT in
  play for this server (all data is read-only harness telemetry anyway).

## Full-corpus + output-tracking wave (2026-10-19)

- **CORPUS COVERAGE BUG (Josh caught it: "doesn't match 100k+ chunks"):** the
  syncer indexed only 10 of 38 corpus sources — silently skipping pwc (31.7k
  docs), langchain-hub (10k), snowflake (9.1k), terraform-registry (5.6k),
  webcrawl, slack, workday, ... CORPUS_SOURCES is now DISCOVERED (every corpus
  dir with .md, github still excluded per the original ruling, jira dirs
  empty-API-only): **89,007 docs / 311,483 chunks**. corpus.duckdb = 865MB.
- **UPLOAD COST GUARD:** hourly rebuild+upload of 865MB would be ~21GB/day of
  churn. Corpus rebuild gated on a content fingerprint (per-dir md count +
  size + max mtime, stamp at corpus/.corpus-stamp); upload_dir skips
  byte-identical >50MB re-uploads (md5 vs blob metadata). Full rebuild ~6 min,
  verified; uploaded 863.5MB once (verified in GCS).
- **corpus_stats tool:** per-source docs/chunks/text-bytes + totals — the map
  Josh asked for. corpus_search answered searches but nothing served the map.
- **OUTPUT TRACKING (Josh's metrics ask):** assets_query (created vs edited
  Workato assets from the build ledger's 12k+ ticket-linked command record,
  weekly counts + evidence rows); jira_pull (syncer module, fail-soft —
  Basic auth against workato.atlassian.net, 120d window, fields include
  customfield_10057 story points + labels); jira_query (monthly
  created/resolved + points resolved + label histogram — hotfix/deploy
  classification stays data-derived, no guessed labels); deployments_query
  (stored DR manifests + live working manifest + redteam verdicts on file).
- **JIRA CREDS GATE (Josh action, pending):** template at
  ~/.claude/knowledge/config/jira.env (chmod 600); paste a token from
  id.atlassian.com → next sync pulls tickets; until then jira_query serves
  configured:false. gcloud CLI tokens expire ~daily — a durable deploy
  credential is an open Josh decision.
- 34 tests green. Deployed 2026-10-19 ~20:08 PT (health 200, discovery 200,
  no ERROR lines in Cloud Run logs). Fresh claude.ai chat needed for the new
  tool catalog (per-chat cache).
