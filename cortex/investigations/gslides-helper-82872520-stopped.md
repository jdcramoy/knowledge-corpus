# Investigation: prod 82872520 "GSlidesMCP | Append Guidance" STOPPED — partial restart after 07:45–07:56 PT window

Read-only investigation, 2026-10-12 (~12:20 PT). Sources: `wt` CLI prod reads only
(`recipes get`, `jobs list/get`, `api GET /api/recipes[/...]`, `--profile josh-prod`,
workspace 3535598). No writes, no restarts, no edits. Builds on same-day companion note
`prod-82090477-quota-burn.md` (~09:00 PT), which first captured the error text
`Can't call a stopped recipe (id: 82872520)`.

## Headline

82872520 is still STOPPED (as of ~12:20 PT). It was the only asset in folder 32312724 not
restarted after the 07:45–07:56 PT maintenance window. Of the three "parent tool recipes"
named in the report, only **82090477 "Extract Design System" actually calls the helper** —
its two call sites are unguarded, so every invocation since 07:55:55 PT fails. Failures are
ONGOING: after the reported 08:24 and 08:36 PT failures, three more hit at 10:41, 10:42,
10:43 PT. 82090474 and 82090475 do not reference the helper at all and are unaffected.

## (1) Current running state of 82872520

- https://app.workato.com/recipes/82872520 — folder 32312724, project 13755171.
- `running: false`. `stopped_at: 2026-10-12T07:55:55.136-07:00`. `stop_cause: null`.
- `last_job_started_at: 2026-10-12T07:55:26 PT` — its final jobs all SUCCEEDED (last completed
  07:55:27 PT). It was healthy when stopped; nothing in its own job history precipitated the stop.
- Lifetime: 6,705 succeeded / 42 failed (42-failure cluster is all 2026-10-07, during
  build/shakedown; code last modified 2026-10-08 23:56 PT, version 6, author Josh).
- Internals (16 steps): enterprise_context reads + custom Ruby, with internal try/catch around
  document search (steps 9–11) and telemetry add_record (13–15) — the "fail-open" in its
  description covers INTERNAL lookups only. A platform-level STOP cannot fail open: callers get
  `Can't call a stopped recipe` before any helper code runs.
- All four config entries are platform-native with `account_id: null`
  (workato_recipe_function, enterprise_context, workato_custom_code, workato_db_table) —
  no external connections, nothing to re-auth on restart.

## (2) Stop cause and job history around the window

- `stop_cause: null` (API exposes no actor/reason). Folder-wide evidence: ALL 18 recipes in
  folder 32312724 show `stopped_at` in a tight wave at 07:48:29–07:48:30 PT — except 82872520,
  whose stop is stamped **07:55:55**, ~7.5 min later, at the very end of the reported
  07:45–07:56 PT window. Every sibling came back Running; 82872520 did not.
- Pattern = a family-wide stop/start (maintenance or deploy session) whose restart sweep either
  predated the helper's own stop or missed it. What performed the window: not determined
  (no audit-log read attempted — flagged in the companion note as follow-up #4).
- Helper job history 07:45–07:56 PT: continuous successful calls from GSlides tool recipes
  74736317 (Delete_Slide) and 74736326 (Get_Presentation) right up to 07:55:27 PT, then silence
  — no failed jobs, no errors. After the stop, ZERO helper jobs exist (calls to a
  stopped recipe function never enqueue), which is itself the cleanest confirmation that all
  post-07:55 guidance calls are dying at the caller.

## (3) Downstream impact on 82090477 / 82090474 / 82090475

All three returned to `running: true` (stopped_at 07:45:47 / 07:48:30 / 07:48:30 PT,
`stop_cause: null` on all) — that part of the report is accurate. The failure impact is NOT
shared across the three:

- **82090477 "Extract Design System" — IMPACTED, still failing.** Code grep confirms TWO calls
  to flow_id 82872520 (`tool_name="Extract_Design_System"`): step 8 (cache-hit early-return
  path) and step 41 (post-extraction path). The full 42-step outline shows the ONLY try/catch
  blocks wrap steps 2, 22, 31 (custom-connector calls) — steps 8 and 41 are **unguarded**, so a
  stopped-helper error is unhandled and fails the whole job. Failed jobs (all skill invocations
  by MCP user Aaron Seah): 08:24:02 (j-Abw44PFd, 13.4s — ran the full extraction incl. file
  stores + catalog upserts, then died at step 41: maximum wasted work), 08:36:00 (j-Abw4Ep8K,
  1.7s — died at step 8), then 10:41:49, 10:42:11, 10:43:25 (j-Abw8Gamw etc. — still failing).
  Job-trace error_details are masked (`mask_data: true`); the error text
  `Can't call a stopped recipe (id: 82872520)` was captured in the companion 09:00 PT note.
  Note the report's premise needs one correction: the 08:24/08:36 failures were BOTH on
  82090477; 82090474/82090475 had no window-related failures at all.
- **82090474 "Build Theme Carrier" — NOT impacted.** Zero code references to 82872520. Its 12
  lifetime failures predate the window (latest 2026-10-05). Last run 07:51:28 PT, succeeded.
- **82090475 "Get Design System Registry" — NOT impacted.** Zero code references to 82872520;
  zero lifetime failures. Last run 07:51:28 PT (it is called BY 82090477 at step 5, which
  succeeds — the failure happens later at step 8).
- **Wider family blast radius — contained but silent.** Pre-stop, the helper served the
  747363xx GSlides tool family (Delete_Slide, Get_Presentation, Get_Slide, Batch_Update,
  SlidesA_Add_Text_Box). Since 07:56 PT those tools show 25 succeeded / 0 failed (74736326) —
  their guidance calls are evidently guarded or conditional, so they keep working but their
  response envelopes now carry no/stale guidance. Meanwhile publisher 82873160 "Sync Guidance
  from Confluence" is Running and keeps publishing guidance nothing serves — guidance drift
  accumulates silently until the helper is restarted.

## (4) Is an auto-restart safe to propose? — YES (propose only; do NOT execute here)

Safe to propose, low-risk by construction:
- Stateless on-demand recipe function: no scheduler backlog, no webhook queue, no polling
  cursor, no in-flight state to corrupt. Starting it changes nothing until the next call.
- Code is last-known-good: version 6, untouched since 2026-10-08 23:56 PT (4 days of healthy
  prod traffic, 6,705 lifetime successes, final pre-stop jobs all green).
- No external connections (`account_id: null` on all four connectors) — no re-auth or
  connection-drift risk on start.
- The failure mode is unambiguous (platform-level stopped-recipe error), the fix is the exact
  inverse of the cause, and the cost of NOT restarting is live: every `Extract_Design_System`
  call fails (3 failures in the last ~2h), each burning ~7 tasks of real work before dying.
- Residual unknowns a restart does NOT resolve: who/what ran the 07:45–07:56 stop window and
  why the helper was excluded from the restart sweep (audit follow-up); sibling-tool guidance
  staleness accumulated since 07:55 (self-heals on next served call once restarted).
- Suggested action for Josh (PROD write — requires his explicit confirmation per prod gate):
  `wt recipes start 82872520 --profile josh-prod`, then verify on the next real
  `Extract_Design_System` invocation that the job reaches step 42 and `guidance_md` populates.
  Also worth the watchdog rule from the companion note: every recipe function called by a
  Running tool recipe must itself be Running — this incident is exactly what it catches.

## Not verified / caveats

- Exact per-line error text in the three newest traces is masked in job logs; attribution to
  the stopped helper rests on code structure (unguarded steps 8/41), timing (failures begin
  exactly at the stop, failure latency matches which step dies), the companion note's captured
  error string, and zero post-stop helper jobs.
- Why 747363xx callers tolerate the stopped helper (guarded call vs. conditional path) was not
  traced step-by-step; inferred from 25 successes / 0 failures post-stop.
- The actor behind the maintenance window was not investigated (no audit API read).
