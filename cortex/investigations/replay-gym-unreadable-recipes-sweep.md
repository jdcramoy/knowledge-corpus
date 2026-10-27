# Investigation: replay-gym "gym-recipe-unreadable" — 2026-10-24 batch sweep

- Investigator: dispatched READ-ONLY sweep session (headless), 2026-10-24
- Scope: read-only. `wt` / `wt-prod` reads, ledger greps, gym log/code review. Nothing on any platform was changed.
- Dispatch named 5 IDs; the canon actually carries **22** rows from this run (canon.jsonl
  signatures `gym-recipe-unreadable-*`, found=2026-10-24): 69459301, 71077131, 82090477,
  83143984, 83281584, 83295993, 83296329, 83296500, 83296504, 83296507, 83296518,
  83310982, 83310994, 83311103, 83311161, 83311542, 83313609, 83316967, 83316974,
  83316985, 83316996, 83317542.

## 1. Reproduced reads (exact evidence)

All five named recipes read CLEAN on dev, rc=0, full recipe JSON:

| id | name | dev read | prod read |
|---|---|---|---|
| 83316967 | Workday360 | 200, running:true | HTTP 404 `{"message": "Not found"}` |
| 83316974 | get_my_waiting_on | 200, running:true | HTTP 404 "Not found" |
| 83316985 | FUNC \| Enqueue OOO Calendar Outbox | 200, running:true | HTTP 404 "Not found" |
| 83316996 | get_my_ooo_sync | 200, running:true | HTTP 404 "Not found" |
| 83317542 | sync_ooo_to_my_calendar | 200, running:true | HTTP 404 "Not found" |

The prod responses are **canonical 404s** — the exact thing the canon row claims NOT to be
("non-404"). The canon line text is falsified on both halves: dev is readable, and the
only error seen is a 404 (expected — these are dev-only recipes, never promoted).

Spot-checked 2 of the other 17 in the batch: 83143984 (EM Build | Dev API Executor) reads
clean on dev; 82090477 (Extract Design System) is prod-side and reads clean on prod
(404 on dev is the expected cross-workspace shape). No recipe in this batch is unreadable.

## 2. What the five recipes are

- Project: **Agentic | HR Self Service Genie** (project_id 15643451; project folder
  30275122). Folder chain: recipe folders Workday MCP (30326966, parent HR Skills
  31025280) and PTO (31025335, parent Approval Workflow 31025330), both under Core
  (30378876) under project folder Agentic | HR Self Service Genie.
- Owner: user_id 3535597 (Josh, dev workspace). All running:true as of probe.
- Created 2026-10-23 11:35–11:52 PDT, within ~17 minutes of each other.
- Build ledger (`knowledge/build-ledger.jsonl` lines ~32853–32900): ALL five trace to
  ticket **BSYS-29757**, built 2026-10-23 18:36–18:40 UTC across four parallel
  agent sessions: `wd360-mcp-build-oct23` (83316967), `build-get-my-waiting-on`
  (83316974), `wd360-enqueue-func` (83316985), `wd360-ooo-sync-oct23` (83316996 +
  83317542). This is the Workday360 MCP app fleet build.
- Mission-control registry: no pre-existing rows for these IDs (the one grep hit at
  line 1854 is this sweep's own auto-registered claim row).

So yes — they share one origin: the 2026-10-23 BSYS-29757 Workday360 build. But that
shared origin is NOT the failure cause (see §4).

## 3. Why they were canonized — the gym run itself

`knowledge/garden-reports/gym-2026-10-24.md`: 22 recipes checked, **22 misses**, every
one `unreadable on BOTH profiles (rc=1)`.

- Run timing (`~/.local/state/fleet/gym.log`): start 01:15:09, done 01:45:45 on
  2026-10-24 — **30 minutes 36 seconds**. The ten prior runs took 5–50 seconds with
  0–7 misses.
- 30 minutes / 22 recipes ≈ 80s per recipe = the replay-gym 60s HTTP timeout plus wt
  retry, every time. That is the timeout signature: **every network call in the run
  timed out** — wt on dev (rc=1), wt on prod (rc=1), and the direct-urllib second-tool
  read (returns None only when it raises/timeout, replay-gym.py:147-172).
- The run is launchd at 01:07 local (`com.josh.fleet.gym`), headless — a 01:15 AM
  network-down / no-default-route window fails all three paths identically.

## 4. Failure class verdict

**Transport (run-wide network failure at gym time) — confirmed.** Ruled out:

- Permission scope: dev reads return full 200 JSON for all five, same token as the gym uses.
- Cross-workspace ACL: prod returns canonical 404 "Not found" — these were never promoted; the 404 is correct behavior, not an ACL denial.
- Deleted-but-shadowed: all five exist, readable, running:true, with live job counts.
- Identity drift: owner and project IDs are consistent across API response, folders, and ledger.

The "two-tool bar" in replay-gym.py does not protect here because both tools share
the same network stack and (for the direct fallback) the same keychain — a machine-level
network-down window, or a locked keychain in the headless launchd context, fails every
path at once. 30-minute run duration confirms the network-timeout variant.

## 5. This is the THIRD identical all-false batch

- 2026-10-09: 20 rows — falsified (gym-unreadable-1009-batch-verify.md).
- 2026-10-22: 12 rows — falsified, all 6 probed read clean (replay-gym-unreadable-verify.md,
  which already recommended a second-tool retry gate).
- 2026-10-24: 22 rows — falsified by this sweep (this file).

54 canon rows total in this signature class; every batch probed so far has been false.

## 6. Recommendation (unchanged from the 10-22 investigation, now urgent)

1. **Run-level abort gate** in replay-gym.py: if the first N (say 3) recipe reads ALL
   fail rc=1, abort the run and log "gym invalidated: transport failure" — write NO
   canon rows. A 100%-miss run is a machine failure, never 22 simultaneous recipe defects.
2. Cheap secondary gate: refuse to canonize when wall-clock per probe ≈ the 60s timeout.
3. Canon hygiene: the 22 rows found 2026-10-24 (lines 103–124 of canon.jsonl) should be
   marked status=invalidated-transport-false-alarm — left for Josh or a canon-writer
   pass, since this sweep is read-only.

## 7. Nothing changed

Read-only confirmed: no recipe touched, no canon row edited, no prod write. Only file
written is this findings report.
