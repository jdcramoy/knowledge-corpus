# Re-verification: PROD 82872520 'GSlidesMCP | Append Guidance' + caller 82090477
**Verified:** 2026-10-12 20:38 EDT (17:38 PT) — ~12h after the original stopped-at-07:55-PT verdict
**Method:** read-only wt CLI prod reads (wt recipes get, wt jobs list, wt api GET /api/recipes) with --profile josh-prod (workspace 3535598). No writes, no restarts, no edits.

## (1) Is 82872520 still stopped? — NO. It is RUNNING and serving live traffic.
- wt recipes get 82872520: running=true, stop_cause=null, stopped_at=2026-10-12T13:17:20 PT, last_run_at=2026-10-12T13:17:42 PT, updated_at unchanged since 2026-10-08 (no recipe edit).
- Job feed (authoritative): steady SUCCEEDED jobs at 17:27–17:28 PT — minutes before verification — from multiple MCP tool callers (74736347/Set_Element_Text, 74736325/Get_Element, 74736311/Check_Widowing, 74736339/Render_Slide, 74736307/SlidesA_Add_Text_Box, 74736304/Add_Shape).
- One own-side failure today at 14:14:27 PT ("Failed to list documents", caller 74736327) — a runtime data/connector error while running, NOT a stopped-recipe error. Lifetime: 7,164 succeeded / 43 failed.

## (2) Are 82090477's calls still failing? — NO. Last failure 12:54:20 PT; latest job succeeded.
Today (PT), 82090477 'Extract Design System' ran 23 jobs: 13 succeeded, 10 failed.
- All 10 failures are the same unguarded-call-site error: Can't call a stopped recipe (id: 82872520) / Recipe function is not running:
  - 08:24:02, 08:36:00 (morning wave)
  - 10:41:49, 10:42:11, 10:43:25 (matches original verdict's through-at-least-10:43)
  - 12:48:18, 12:48:46, 12:49:53, 12:53:59, 12:54:20 (midday wave — NEW since the original verdict)
- Successes interleave with failures: 10:40:58, 12:45:11, 12:51:43 succeeded while adjacent invocations failed — not every invocation reaches the unguarded Append Guidance call site (likely cache-hit vs live-call path), or 82872520 flapped stop/start midday. Either reading: the original fails-on-EVERY-invocation framing is too strong — it fails on every invocation that reaches the call site while the function is down.
- Latest job: 13:59:21 PT SUCCEEDED. No invocations at all in the last ~3.7h (13:59 to 17:38 PT), so currently-healthy rests on one post-restart success plus 82872520's live traffic from other callers.

## (3) What else restarted or changed
- Folder 32312724 (17 recipes, read via GET /api/recipes?folder_id=32312724): ALL 17 now running=true. Sixteen show stopped_at around 2026-10-12T07:48:29-30 PT (the maintenance-window stop) — restarted at/after the window and stayed up.
- 82872520 is the outlier: its last stop event is 13:17:20 PT, i.e. it went down again (or was only then stopped/started) hours after the maintenance window, then was started again — running=true since, serving jobs from 13:17:42 PT onward. Who/what restarted it is not visible from these reads.
- 82090477 (folder 32312723): running=true, last stop 07:45:47 PT, updated_at unchanged since 2026-10-09 — the unguarded call sites are STILL UNGUARDED. The failure mode is dormant, not fixed.

## Bottom line
The outage is over: 82872520 is up and taking live calls successfully; 82090477 has had zero failures since 12:54:20 PT. The underlying defect (unguarded recipe-function call in 82090477) is unchanged — the next time 82872520 stops for any reason, the same hard failures return. That fix remains the open work.
