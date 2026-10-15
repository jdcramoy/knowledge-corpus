# Investigation: grc-gdpr-emails prod state (cortex, 2026-10-13)

Read-only investigation of mission-control workstream `grc-gdpr-emails` (BTSUP-78086,
"[GRC] GDPR Emails — privacy@ to Slack"). Live prod/dev reads done via `wt-prod`/`wt`
CLI (READ calls only — no mutations).

## (1) What was built and deployed, and to which environment

**Built in DEV (2026-10-08, build-ledger.jsonl lines 2287–2341):**
- Project `[GRC] GDPR Emails` (folder 35744031, project 18219804), created via
  `wt folders create` at 2026-10-08T15:52Z.
- Recipe **Post GDPR emails to Slack = 82910707** (dev): 3 steps — Gmail
  `new_email` polling trigger (conn 13670970), IF `to_emails` contains
  privacy@workato.com, Workbot `post_bot_message` to #gdpr-requests (C0C7MB6K18B).
- Slack bot connection `gdpr-request-bot` = 22271669 (custom OAuth profile 46185).
- Manifest: `wt manifests create --folder 35744031 --file ".../GDPR Emails to
  Slack/manifest-gdpr-emails.json"` (ledger 16:46–16:49Z); mirror file lives at
  `~/orca/projects/GDPR Emails to Slack/manifest-gdpr-emails.json`.

**Deployed to PRODUCTION (2026-10-08):**
- Dev verified both paths (jobs j-Abrwe4wm-WkTsnr-CD negative, j-Abrwfsht-d4DE9z-CD
  positive, bot ts 1791476330.899679 in-channel).
- **Prod recipe = 82912295** (folder 35744842, project 18220156),
  https://app.workato.com/recipes/82912295. Deployed by Josh via manual manifest
  export/import; prod import minted new asset IDs (prod conns gmail 14442932,
  slack_bot 22272101). Ledger shows post-import prod health checks, poll-now, and
  the 2026-10-08T17:53Z prod hotfix (`includeSpamTrash` toggle: prod
  set_input_field+push on recipe 82912295, mirrored to dev at 17:56Z).
- Double-post incident resolved by stopping dev 82910707 (still stopped today —
  live read: `running: False`).
- Live state 2026-10-13: prod 82912295 **running: true**, 106 jobs succeeded,
  0 failed, latest job j-AbwT9Gmn-rReWrB-CD at 2026-10-13T05:17 PT.

**Red-team gate:** NO verdict on record — `~/.claude/knowledge/redteam/` has no
BTSUP-78086/GDPR file (5 files, all other assets). Deploy predates the 2026-10-12
standing order; project file records "BT approval skipped, his call" for Josh.

## (2) The recorded defect — evidence lines

- **registry.json fold (line 483), claim row 2026-10-12T06:39:30Z:**
  `"what": "Session resumed on the privacy@ to Slack deploy: prod posts blank
  messages for long emails"` and `"why": "Workbot connector silently drops Slack
  section blocks over 3000 chars and posts only the New message fallback"`.
- cortex/attention-queue.md:52 — "PROD-facing deploy (blank messages for long
  emails), 28.5h no closeout — possible unfinished prod state".
- cortex/questions.jsonl:163 (2026-10-13T11:15Z) — "Is the prod privacy@ to Slack
  deploy still posting blank messages for long emails right now, or was it
  fixed/superseded after the session went silent?".
- Supporting code evidence: projects/grc-gdpr-emails.md:94-96 — AIRO f-string pills
  don't support slices, so no in-f-string truncation exists in the shipped code.

## (3) Closeout?

**None.** events.jsonl contains exactly one grc-gdpr-emails row — the 2026-10-12T06:39Z
claim. No `closeout` event has ever been written. The row is in-flight 30h+.

## (4) Verdict: POSSIBLE UNFINISHED PROD STATE — yes, and now CONFIRMED, not just possible

Live evidence (read-only, 2026-10-13):

- **Dev 82910707 WAS fixed**: `updated_at 2026-10-11T23:21:45 PT` (= 06:21 UTC, 18
  minutes before the claim row was written at 06:39 UTC) and its code now contains
  a guard truncating body_plain over 2900 chars with
  `_[body truncated - full text in Gmail]_` fallback.
- **Prod 82912295 was NOT fixed**: `updated_at 2026-10-08T10:53:41 PT` (the
  spam-toggle push) — untouched since 2026-10-08, and its code contains NO
  truncation guard (grep for `truncated`/`2900`: both absent).
- Prod is LIVE and actively processing privacy@ mail (jobs succeeded today,
  2026-10-13 03:42–05:17 PT).

**Conclusion:** the fixing session got the dev-side fix pushed, wrote the in-flight
claim row ("fix dev and prod, confirm with the owners"), and died before pushing
prod or closing out. The prod recipe is running unpatched with the known blank-post
defect; every long privacy@ email since 2026-10-08 posts a fallback/blank message to
#gdpr-requests. This is a genuinely unfinished prod state, not a bookkeeping gap.

**Unblocks it:** Josh attach prod MCP (or approve the `wt-prod` push of the dev
truncation guard to 82912295) — then stop→push→start 82912295, verify a long email
posts with truncated-but-non-empty body, and write the closeout row.

**Nothing else was changed in this investigation** — reads only; the only write is
this findings file.
