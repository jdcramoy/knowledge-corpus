# Downloads secrets-shaped file inventory — 2026-10-23

Trigger: downloads-secrets-guard bus finding 2026-10-23T13:23Z (flagged
`analytics-codex-tokens-used_workspace-workato-enterprise_by-model_2026-06-01-to-2026-10-12.csv` mode 0o644).
Method: read-only name sweep + header/classification pass over ~/Downloads. No file contents with secret
values were printed; no permissions, moves, or deletions were made.

## Inventory

| File | Perms | Size | mtime | Content class | Exposure assessment |
|---|---|---|---|---|---|
| `AuthKey_Y23V88BQ58.p8` | 0644 | 257 B | 2026-09-26 | **Live private key** — Apple App Store Connect API key (`-----BEGIN PRIVATE KEY-----` confirmed, header only) | Raw ES256 signing key. 0644 = group/everyone-readable on the Mac; any local process or second account could read it. 4 weeks old; treat as valid until proven rotated. |
| `manamargin-firebase-adminsdk-fbsvc-b851e9e417.json` | 0644 | 2.4 KB | 2026-09-26 | **Live service-account credential** — Firebase admin SDK JSON with 1,704-char `private_key` + `client_email` | Full admin access to a Firebase project. Same 0644 local-read exposure; 4 weeks old; highest-impact item in the folder. |
| `github-recovery-codes.txt` | 0644 | 206 B | 2026-08-05 | **2FA recovery codes** (GitHub, ~10 codes) | Bypasses GitHub 2FA outright. Aug set is likely invalidated by the two later regenerations below — unconfirmed. |
| `github-recovery-codes (1).txt` | 0644 | 206 B | 2026-10-01 | **2FA recovery codes** (regenerated set) | 3 weeks old; possibly still active. |
| `github-recovery-codes (2).txt` | 0644 | 206 B | 2026-10-09 | **2FA recovery codes** (newest set) | 2 weeks old; almost certainly the live set for some GitHub account. |
| `claude_api_tokens_2026_07.csv` | 0644 | 1.4 MB | 2026-07-27 | Usage export w/ embedded identifiers — 10,531 rows, 430 distinct `api_key` values (34-char key NAMES, not raw secrets; zero `sk-` patterns) | Per-key usage, workspace, inference geo. Metadata-sensitive, not credential material. 3 months stale. |
| `cost_2026-09-01_2026-10-01.csv` | 0644 | 1.1 MB | 2026-10-05 | Cost export w/ embedded identifiers — `user_email`, `user_id`, `api_key_id`, project/org names, per-line-item spend | Internal emails + per-person spend. PII-adjacent, no secrets. 2.5 weeks old. |
| `user-spend-export_2025-10-31_to_2026-01-29.csv` | 0644 | 26 KB | 2026-01-30 | Spend report (header banner + 353 rows) | Internal spend data; 9 months stale. |
| `analytics-codex-tokens-used_workspace-workato-enterprise_by-model_2026-06-01-to-2026-10-12.csv` | 0644 | 9.5 KB | 2026-10-11 | Usage export — time buckets × model columns ONLY (132 rows). **Zero identifier columns**; the workspace name lives in the filename | Bus finding overstated "embedded identifiers": body is aggregate token counts. Sensitivity = filename discloses workato-enterprise workspace usage. 12 days old. |
| `analytics-codex-credits-used_workspace-workato-enterprise_by-model_2026-06-01-to-2026-10-12.csv` | 0644 | 10.6 KB | 2026-10-11 | Usage export — same shape, credit counts | Same as above. |
| `default.json` | 0644 | 188 B | 2026-08-13 | Config with `apiKey` field of length 4 — placeholder/short, not a credential | Harmless at current inspection. |
| `claude_desktop_config.seismic-example.json` | 0644 | 1.9 KB | 2026-09-15 | MCP config EXAMPLE, no secret fieldnames | Clean. |
| `hr-genie-*.zip` (20 files, 2026-09-08→10-05) | 0644 | 34–55 KB | Sep–Oct | Workato recipe export packages; grep across all: **0** credential-fieldname hits | Internal recipe code = internal IP, not secrets. Duplicate downloads inflate the count (3× identical oauth-remediation-proactive zip). |

Adjacent (PII, not secrets-shaped — flagged for the same sweep next pass): `members-*.csv` (Slack workspace member exports),
`data_table_slack_mcp_user_directory.csv` (4.3 MB user directory), `tool-logs*.csv`, `data_table_hr_genie_*log*.csv`.
False positive: `MCP - Zero to Connected.key` is a Keynote presentation, not a key file.

## Verdict (one line per class)

- **ACT NOW** — `AuthKey_Y23V88BQ58.p8`, `manamargin-firebase-adminsdk-*.json`, all three `github-recovery-codes*.txt`: live credentials sitting 0644 in Downloads; move to keychain/1Password, `chmod 600` originals or delete after confirm-rotate (p8 + Firebase key should be rotated given 4-week exposure).
- **HYGIENE** — `claude_api_tokens_2026_07.csv`, `cost_*.csv`, `user-spend-export_*.csv` (+ the PII exports): no credentials but internal-identifying; move out of Downloads or delete; not urgent.
- **IGNORABLE** — the two `analytics-codex-*` CSVs (aggregate counts, filename-only disclosure), `default.json`, example config, `hr-genie-*.zip` recipe packages, Keynote `.key`: delete at leisure, no exposure beyond filename/workspace-name leakage.
