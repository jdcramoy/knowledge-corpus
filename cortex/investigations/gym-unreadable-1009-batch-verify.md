
## gym-recipe-unreadable 2026-10-09 batch — re-probe 2026-10-22 (read-only)

Two read paths per recipe: (1) `wt recipes get <id> --raw` (dev profile, then prod profile
`josh-prod` to test the canon's "dev AND prod" claim), (2) AIRO MCP `recipe_get` (dev-scoped).
All wt failures are CLEAN HTTP 404s — real API responses, no transport errors.

| recipe_id | wt dev | wt prod | AIRO MCP (dev) | verdict |
|---|---|---|---|---|
| 71768712 | rc=1 HTTP 404 | **rc=0 OK** — "FUNC \| List MCP Tools with Tool Call Stats" | perm-denied (folder ACL) | CONTRADICTED — reads clean on prod |
| 74736304 | rc=1 HTTP 404 | **rc=0 OK** — "Add Shape" | perm-denied | CONTRADICTED |
| 82090477 | rc=1 HTTP 404 | **rc=0 OK** — "Extract Design System" | perm-denied | CONTRADICTED |
| 82872520 | rc=1 HTTP 404 | **rc=0 OK** — "GSlidesMCP \| Append Guidance" | perm-denied | CONTRADICTED |
| 82873160 | rc=1 HTTP 404 | **rc=0 OK** — "GSlidesMCP \| Sync Guidance from Confluence" | perm-denied | CONTRADICTED |
| 82929351 | rc=1 HTTP 404 | **rc=0 OK** — "CACHE \| MCP Tool Call Stats filler" | 404 | CONTRADICTED |
| 82919741 | rc=1 HTTP 404 | rc=1 HTTP 404 | 404 | not-confirmed — clean 404 both profiles (deleted, not "non-404 unreadable") |
| 82920816 | rc=1 HTTP 404 | rc=1 HTTP 404 | perm-denied | not-confirmed — clean 404 both profiles |
| 82928684 | rc=1 HTTP 404 | rc=1 HTTP 404 | 404 | not-confirmed — clean 404 both profiles |
| 82912295 | rc=1 HTTP 404 (single probe) | withheld per one-probe limit | withheld | BLIND-SPOT-CONSTRAINED — known grc-gdpr prod pulse-lane ACL gap; single probe returned clean 404, not re-probed |

### Verdict

- 6 of 10 canon rows are flatly CONTRADICTED by live evidence: the recipes read clean on the prod
  workspace right now. The 2026-10-09 gym run probed them from a context that could not see prod
  and recorded the failure as asset unreadability.
- The other 3 (82919741, 82920816, 82928684) return clean HTTP 404 on BOTH dev and prod — i.e. the
  recipes do not exist in either workspace. That is a DELETED/NOT-FOUND state, which contradicts
  the signature's own "non-404" wording. 0 of 10 rows confirm "unreadable (non-404)" as written.
- 82912295 (grc-gdpr prod) is blind-spot-constrained: one probe, clean 404, not re-probed per the
  ACL exception. It cannot confirm the canon row, and live evidence does not contradict it either.
- **Recommendation: YES — the canon should require a two-tool retry policy before canonizing any
  "unreadable non-404" row.** All 13 failure signatures in this batch (this re-probe plus the
  2026-10-22 six-batch) dissolved under a second read path / profile. Minimum bar: wt on the
  correct profile for the asset's workspace + one independent path (AIRO MCP or API), and a
  profile check (dev vs josh-prod) before writing "dev AND prod" into a row. A single-path
  404/ACL/transport failure should be recorded as UNVERIFIED-TRANSPORT, never as a regression.

Probe commands used (read-only): `wt recipes get <id> --raw [--profile josh-prod]`,
`mcp__workato-airo-mcp-server__recipe_get`. Nothing was modified anywhere.
