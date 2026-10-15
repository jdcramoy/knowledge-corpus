# Seismic by Workato MCP — project knowledge

Created 2026-10-10 by the legacy-tree mining pass (the ChatGPT archive
folder `~/Documents/ChatGPT/Seismic by Workato MCP/` held the full record;
its git repo has ZERO commits — files untracked, exports are evidence not
proof of remote state).

## State (as recorded in the archive)

- Custom Connector SDK connector `1355883` v100, 46 actions; MCP server
  `mcps-AbYXRs4T-YNH-CD`, 30 VUA tools; prod project 35673912
  (structure only, never imported); RLM manifest 355903 / package 42139110;
  Jira BSYS-29281 under epic BSYS-28828. Deployment Request was open but
  never authorized for import.
- `Seismic Proxy MCP` sibling folder is EMPTY (bare git, no commits).

## Seismic API specifics (durable)

- OAuth 2.0 auth-code + PKCE (no client secret) against
  `https://auth.seismic.com/tenants/{tenant}/connect/authorize|token`;
  callback `https://www.workato.com/oauth/callback`; API base
  `api.seismic.com` / `api-sandbox.seismic.com`.
- Scopes: `offline_access, seismic.self.view, seismic.search,
  seismic.gen-search, seismic.engagement.view/.manage, seismic.delivery,
  seismic.workspace.view, seismic.library.view` — `seismic.reporting`
  deliberately EXCLUDED: scope changes create a NEW app version/client
  identity and must be governed as rotation.
- Rate limits by endpoint class: LiveSend ~30 req/min, folder listing
  ~60/min, most others ~600/min; honor 429; bounded retry only for
  idempotent reads.

## Intelligence entitlement fallback contract

On `USER_NOT_ALLOWED` with an explicit caller-supplied business query:
fall back to authorized-catalog search with `sourceMode=authorized_search_fallback`,
`partial=true`, machine-readable warning. Never convert email/CRM
identifiers into queries; never claim personalization.

## Related (KB bridges)

## 2026-10-11 deploy gate on BSYS-29281 (jira-triage pass)

- [Deploy Seismic by Workato MCP to Production](https://workato.atlassian.net/browse/BSYS-29281) sits in Final Tech
  Review with manifest 355903 / package 42139110, target prod project 35673912.
- Gate posted as comment 1135005: the Oct 11 00:50Z nightly regression shows 2 Seismic skill FAILs + a
  workspace_vua_identity_probe FAIL, and at least one failure was swallowed into a DEPENDENCY_UNAVAILABLE fallback
  envelope that still scored green — so current dev-side greens on the four Seismic VUA skills are untrustworthy as
  promotion smoke evidence. Verdict posted: hold the prod import until the nightly runs clean.
- The two queue findings driving this: `regression-seismic-pair-vua-probe-1011` (autopsy, 3pt) and
  `nightly-pass-envelope-aware` (score fallback envelopes as masked-FAIL). Both still awaiting Josh's /triage verdict.
- Unrelated open thread on the ticket: Patricia's Oct 6 question (prod connection created before or after deployment)
  was never answered; raise it at cutover scheduling.

## 2026-10-12 BSYS-29582 dev remediation (recipe 82256903)

- Dev fix shipped: recipe 82256903 v12 — step 2 wrapped in WorkatoMonitor; catch returns the
  safe DEPENDENCY_UNAVAILABLE envelope (ok=false, sourceMode=unavailable), mirroring 82256904.
  Proof: test run cirr-AbwGre4Q-bC4neA-CD / job j-AbwGre4J-Bxz3Qr-CD — catch caught "Missing
  connection" headless, envelope returned, job SUCCEEDED (first green since 10-01).
- The automated Estate-Monitor triage on BSYS-29582 claimed "unbound Seismic connection" — WRONG.
  Live config showed account_id 22111194 + personalization: true throughout. Real cause: headless
  harness cannot resolve VUA runtime identity on a personalized step. Verify live config before
  trusting auto-triage root-cause claims.
- VUA binding survived this AIRO push (read-back: personalization true, acct 22111194) — the
  vua-revert-on-push trap did NOT fire here; still verify after every push.
- Manifest 362111 on project folder, mirrored to repo manifests/BSYS-29582.manifest.json,
  ZIP-verified (export 42209431). Jira comment 1136460.
- STILL OPEN: nightly registry runs VUA-bound skills headless — failures continue (or pass as
  masked-green envelopes) until Josh picks tag-and-skip vs identity-carrying harness. BSYS-29281
  prod gate hold unchanged.
