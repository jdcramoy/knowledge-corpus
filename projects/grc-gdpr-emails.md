# [GRC] GDPR Emails — privacy@ email to Slack

Built 2026-10-08 in DEV (ws 3535597). Source request: BTSUP-78086
("GDPR requests Slack channel + privacy inbox notifications" — In Triage).
Goal: emails addressed to the privacy@workato.com DL get posted, full body,
to the private #gdpr-requests Slack channel.

## Assets (dev)

- Project [GRC] GDPR Emails — folder 35744031, project 18219804.
- Recipe **Post GDPR emails to Slack = 82910707**
  https://app.workato.com/recipes/82910707 — 3 steps:
  1. Gmail `new_email` polling trigger on connection 13670970.
  2. IF `"privacy@workato.com" in f"{new_email_1['to_emails']}"` (the DSL
     stringifies the to_emails array — substring contains).
  3. Workbot `post_bot_message` to C0C7MB6K18B, one `section_with_text`
     block: `*From:* / *Subject:* / full body_plain` (f-string pills).
- Connections: **Gmail (integrations.ai@workato.com) = 13670970**
  (pre-existing, already authorized — REUSED, do not recreate) and
  **gdpr-request-bot = 22271669** (slack_bot, custom OAuth profile 46185,
  folder 35744031, authorized by Josh 2026-10-08).
- Slack: private channel **#gdpr-requests = C0C7MB6K18B**, team T02MRTQUB.
  Bot user **GRC-GDPR-REQUESTS = U0C8N2YSC9E** (bot B0C7VKJSCJD, app
  A0C7N9U7WCD). Josh created the app + channel + invited the bot himself.

## Verified (2026-10-08, both paths, job traces on 82910707)

- Negative: JIRA notification to integrations.ai@workato.com →
  job j-Abrwe4wm-WkTsnr-CD, condition False, Slack step skipped.
- Positive: same email class with test filter → job j-Abrwfsht-d4DE9z-CD,
  condition True, bot message ts 1791476330.899679 landed in C0C7MB6K18B
  FROM THE BOT. Test method: temporarily flip the IF rhs to
  integrations.ai@workato.com, editor Test via Orca, revert + push. No
  test email was sent.

## State / remaining

- **Spam coverage ON (2026-10-08 prod hotfix, Josh-confirmed):**
  `includeSpamTrash="true"` on the trigger — same recipe now covers
  spam+trash (the default No excluded them; Josh bet test mail was
  spam-filtered). Mirrored to dev golden copy. Cursor keeps applying, so
  no old-spam dredge; spam purges at 30 days. VERIFIED post-toggle: two
  fresh privacy@ test emails (distinct subjects, no dupe) caught in one
  5-min cycle and posted from the bot (ts 1791482759/760), jobs
  j-AbrzPMee-*.
- **"Stall" false alarm (12:45 UTC-day, 2026-10-08):** polls with no new
  mail create NO jobs, so an idle inbox looks like a stalled trigger.
  Diagnostic: `running=True`, `stop_cause=None`, no `is_poll_error` jobs,
  and `wt-prod recipes poll-now <id>` advances `trigger_closure.after` and
  creates a job if mail exists. Polling trigger looks stalled? → poll-now
  before believing it.
- **DL dupe vector observed:** one privacy@ test email produced TWO Gmail
  messages (likely dual delivery: direct + DL expansion or two DLs) → two
  jobs, two Slack posts. Per-message dedupe can't catch this; if it
  matters, dedupe on Gmail message-id/thread-id in the recipe.
- **DEPLOYED TO PROD 2026-10-08 by Josh via manual manifest export/import
  (BT approval skipped, his call — low-risk 3-step asset).**
- **Prod recipe = 82912295**, folder 35744842, project 18220156
  https://app.workato.com/recipes/82912295 — RUNNING, 5-min interval and
  privacy@ filter carried over intact; prod connections gmail 14442932 +
  slack_bot 22272101 both authorized (jobs green, bot posts landed).
  NOTE: prod import minted NEW asset IDs — dev 13670970/22271669/
  82910707 do not exist in prod.
- **Double-post incident (resolved)**: prod's first poll swept the same
  1-day backlog dev had already posted (4 emails × 2 = 8 bot messages in
  #gdpr-requests). Root cause: dev recipe left running after prod start —
  both recipes poll the same mailbox with independent cursors. Dev
  82910707 STOPPED 2026-10-08; prod is the only poster. Lesson: the moment
  a prod twin of a same-mailbox poller goes live, stop the dev one.
- Poll interval set to 5 min in dev before export (hot-swapped
  stop→push→start, running verified). Polling trigger dedupes per message
  via its cursor — no double-posts across restarts; only manual job rerun
  can duplicate.
- Dev recipe 82910707 kept (stopped) as the dev-side golden copy; live
  UAT in dev had PASSED first (3 backlog emails posted from the bot,
  ts 1791477246/247/248, JIRA noise filtered).
- Promotion: standard BT managed path via Jira; prod needs both
  connections re-established (Gmail re-auth to integrations.ai mailbox,
  slack_bot profile 46185 clone/rebuild) + bot invited to the prod-side
  channel mapping.

## Lessons

- **Developer-API-created projects are ACL-locked**: `wt folders create`
  (federated token identity) makes a project with ZERO project_grants —
  AIRO (Josh identity) can list but not write it ("Permission denied …
  target folder"). Fix is a Project-admin grant on the project
  (GET/POST /api/projects/<id>/project_grants exists; grant creation was
  classifier-gated — Josh granted access manually). Diagnose with
  `GET /api/projects/<id>/project_grants` (empty = locked).
- **Orca browser**: `orca goto` fails with `browser_no_tab` when zero tabs
  exist — `orca tab create --url ...` is the tab creator (`tab new` does
  not exist).
- **AIRO f-string pills**: slices inside `{pill[0:4000]}` are unsupported
  (Unsupported datapill part Slice) — no truncation in f-strings; use
  ruby() bindings or pre-truncate in a prior step.
- recipe_builder_save on a freshly-init'd recipe creates a SECOND recipe —
  init already saved; use push after init, delete the duplicate via
  `wt api DELETE /api/recipes/<id>`.
- Gmail trigger pill is `to_emails` (array), not `to_email`.

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [Workato GO - Crawler failure notifications](../../kb-corpus/docs/en/agentic/workato-go/data-sources/crawler-failure-notifications.md)
- [Custom OAuth profiles for Slack](../../kb-corpus/docs/en/custom-oauth-profiles/slack.md)
- [Developer API quotas](../../kb-corpus/docs/en/workato-api/limits.md)
- [[BT-23] [AEM] Automated Error Monitoring v2 - DRAFT](../../kb-corpus/confluence/intbt/2932932888-bt-23-aem-automated-error-monitoring-v2---draft.md)
<!-- kb-bridges:end -->
