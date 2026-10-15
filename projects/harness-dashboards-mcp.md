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
