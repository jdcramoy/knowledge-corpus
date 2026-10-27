# Project: knowledge-corpus (team-shared brain export)

## State (2026-10-15): v1 LIVE — org repo pushed, weekly job scheduled

- **Repo:** `Workato-All/knowledge-corpus` (INTERNAL) —
  https://github.com/Workato-All/knowledge-corpus. 495 files, ~8.7MB: domains,
  projects, architecture, decisions, positions, reviews, specs, workato-terms,
  kb-digests, claims, scripts. Audience = Workato employees (workspace IDs,
  Jira keys, app.workato.com URLs are in-scope for this audience).
- **Exporter:** `~/.claude/knowledge/scripts/knowledge-export.sh` — one-way,
  git-preserving rebuild of `~/Documents/knowledge-corpus`. Deny-lists 32
  operational/estate/personal dir classes + ledgers. Redaction layer: support-
  channel requester names → `[requester]` (file-scoped bare first names),
  EVERY people-file full name → `[colleague]` (auto-generated from the live
  people dir at export time — never goes stale), claude.ai org-wide extract
  files dropped, INDEX people/ pointers stripped. Sweeps (all fail-loud, text
  files only): secrets patterns, people full names, personal identifiers
  (<user>/<user> in any form incl. CC slugs), non-org emails. Home
  paths genericized to `~/`.
- **Weekly job:** `com.josh.fleet.kb-corpus-sync`, Tuesdays 07:27, job def at
  `config/fleet/jobs/kb-corpus-sync.{env,prompt}`. Swept export → commit →
  bus review digest → push. Never edits sources to pass sweeps, never widens
  scope at runtime. First live run pending (first Tuesday).
- **What ships vs what installs:** the corpus DOCS (7.1GB, 25+ sources) do NOT
  ship — teammates install the public sources via the workato-dev-kb pack
  installer. This repo is the authored brain layer only.

## Audit trail (2026-10-15, independent agent)

285 files content-audited. Dropped: org-wide claude.ai projects extract (CSV
+ JSON: ~470 employee emails × private project titles with deal sizes/customers).
Redacted: BTSUP/hr-genie requester names (Ruben F., Rodrigo M., Anna M., Patricia
G., Choon Yen K., [requester]., Ai I., Yu L.), colleague names (Pikin, Shepard,
Seligman, Ng, Tan, Cox, Yuen). Flagged-review: anthropic-compliance-api.md
keychain pointer redacted; hr-genie.md Leapsome prod-access note redacted;
grc-gdpr-emails.md kept (infra doc, no requester data). Per-dir verdicts:
claims/specs CLEAN, domains/cortex CLEAN-WITH-NOTES, projects NEEDS-WORK→fixed.

## Related privacy fix (same session)

`josh-knowledge` had 61 voice/people files TRACKED and org-visible. Untracked
+ gitignored 2026-10-15 (commit 08daea0); **they remain in git history** until
a purge (force-push rewrite, Josh-gated, not done).

## Stubs (2026-10-15, Josh)

Excluded dirs keep their SKELETON in the export: 32 `EXPORT-STUB.md` stubs
(dir name + why-not-exported + "the weekly exporter keeps this empty; policy
changes populate here"). The claude-projects-extract dir is denied WHOLESALE —
a third extract file (org-wide-projects-joined, plus dan-org-emails.json and
cs-org-dan-kennedy CSVs) landed in the source tree the same afternoon and two
of them were briefly pushed (commit efb93ad) before the sweep caught the
third. Sweeps now exclude .git plumbing; rsync exclude anchoring fixed;
export failures no longer chain into commits.

## Rules

- The export is ONE-WAY: team repo never merges back into the brain.
- Widening what ships = human edit to knowledge-export.sh include/deny lists,
  never a runtime choice.
- Personal identity content (people/, voice-reps/, voice skill) never ships in
  ANY export — enforced by deny lists + sweeps, templates for teammates live
  in the kit at `personal-identity-templates/`.
