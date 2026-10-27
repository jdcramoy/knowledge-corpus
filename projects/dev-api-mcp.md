# dev-api-mcp — Workato Developer API Semantic MCP (BSYS-29894)

> Created by project-dreamer 2026-10-26 (auto-safe knowledge-file write, recorded in
> the 2026-10-26 dream report). Until tonight this was the most active project in the
> estate with ZERO presence in the knowledge tree — the router (INDEX.md) could not
> route to it and cross-agent corroboration could not find it.

**What it is:** a 3-tool semantic MCP server over the Workato Developer API
(`workato_api` heavy lifter + `workato_api_capabilities` + `workato_api_policy_lookup`)
in the DEV workspace, with a plan→confirm→byte-exact-commit mutation gate, an offline
learning flywheel (curator → promoter → 3-model jury), and a platform-scope KB corpus.
Mirrors the Google Workspace Semantic MCP (BSYS-29502/29569 pattern).

**Authoritative sources (read these, not this stub):**
- Repo + HANDOFF: `~/orca/projects/dev-api-mcp/HANDOFF.md` (live ids, traps, next steps)
- Auto-memory build state: `~/.claude/projects/-Users-<user>-orca-projects-dev-api-mcp/memory/dev-api-mcp-build-state.md`
- Confluence architecture tree: parent page 2983329823 (BTI space) + 6 deep-dive children
- Spec: `~/orca/projects/dev-api-mcp/SPEC.md`

**Live assets (2026-10-26):** MCP server `mcps-Ac6JB4fW-H9T-CD`; gateway 83281584,
capabilities 83280134, policy 83281173; registry 163957 (332 intents / 33 families);
KB corpus kb-Ac6Msopr-4zERzp-CD (1268 docs); steward genie gin-Ac6MxcbM-HGP6Ya-CD;
manifest 371191 (v3). Fleet also: sync 83284865, curator 83285929, promoter 83286359,
discovery 83284655, retention 83290173, feeder 83290345, stats materializer 83337024,
lessons curate 83333225, lessons promote 83333230.

**Status:** Phase 5 complete (41/41 suite, Confluence published, red-team cycle closed
PASS-WITH-NOTES). Phase 6c lessons loop + 6d efficiency stats loop live. Phase 6e
(BSYS-29961) AIRO-killer benchmark harness built + smoke-proven — Josh decision pending:
full 127×3 campaign (~150-200M tokens) vs 30-task pilot (mission-control needs-josh).

**Cross-project relation:** shares the flywheel pattern (and jury adjudication rules)
with [google-semantic-mcp](google-semantic-mcp.md); its 200,944-phrase intent corpus
(also feeds GWS) lives in `~/orca/databases/claude-intents-raw.db`.
