# Autopsy: 2026-10-22 regression "could not start run" cluster (read-only)

**Date:** 2026-10-22 · **Mode:** READ-ONLY (no runs fired, no recipe edits, GET-only probes)
**Trigger:** `garden-reports/regression-2026-10-22.md` — 0 passed / 0 failed / 19 errors.
15 recipes errored "could not start run" (user's list of 14 + **83230036 Frontify MCP -
Get Current User**, also in the report), plus 3 fixture timeouts (82863111, 82921718,
82959481) and 1 fixture config gap (83113565).

## VERDICT FIRST

**Shared root, NOT per-recipe: a local egress network blackhole on the runner Mac during
the run window (2026-10-21 23:58:58 → 2026-10-22 00:35:55 EDT).** Every outbound HTTP call
from the nightly runner hung at the transport layer that night — the recipe-list scan GET,
all 15 run-start POSTs, and both fixture invocation paths (app.workato.com force_run AND
the webhook gateway). The recipes, their test cases, their connections, the runner config,
the wt binary, and the Workato platform are all provably healthy. The cluster needs **no
asset fix** — it self-clears on the next network-healthy night. The durable fixes are
three runner blind spots (below), one of which was already prescribed on 2026-10-17 and
never landed.

Classification bucket: **platform/environment — local runner-host network failure**
(neither connection-auth nor code bug nor input-contract). Fix class for the runner
hardening below: `root-fix` (signal integrity), not containment.

## The onset evidence (nightly history)

| Night | Result | Notes |
|---|---|---|
| 10-18, 10-19, 10-20 | 13 pass / 5 fail / 7 err | Errors = 3 chronic per-asset cases (82239660, 82727069, 82959480) + 4 masked. All 15 of last night's victims **passed or ran normally** |
| 10-21 | 17 pass / 4 fail / 5 err | Greenest night yet. 82248358 passing. Chronic trio evicted from registry (BSYS-29459 fix working). Only error = 83230036 + 4 masked |
| 10-22 | **0 pass / 0 fail / 19 err** | Every runnable recipe flipped to "could not start run" simultaneously |

A 15-recipe same-night flip after a green 10-21, spanning 6+ folders/projects (HR Genie,
Seismic, Google Semantic, Certinia, Frontify, CSM, zArchive), cannot be per-recipe rot.
Uniform simultaneous onset = shared cause, full stop.

## The discriminating evidence (why network-blackhole, specifically)

1. **`scan: 0 recipes` in the run log** (`~/.local/state/fleet/regression.log`, line 448).
   Every prior night: `scan: 1000 recipes`. The scan's FIRST call — `GET /api/recipes.json`
   — returned nothing, so the estate walk broke on page 1 and the cached 19-recipe registry
   silently carried the run (the report renders no banner for a zero-page walk — blind
   spot #2). **The GETs failed too**, not just the POSTs.
2. **Runtime math: 36m57s vs the normal ~13m.** Fast HTTP rejections (401/403/500) would
   finish in under 2 minutes. Observed time fits ~75s TCP-connect hangs per call: 1 scan
   GET + 15 POSTs + 4 fixture invocations + fixture poll timeouts ≈ 33-37 min. This is the
   signature of SYN blackholes, not API answers.
3. **Multi-destination failure.** Dead that window: app.workato.com API (scan + 15 POSTs +
   2 force_run fixtures), the webhook gateway (82921718's fixture POST to its webhook_url),
   and — per the heartbeat/validation ledgers — the claude-spawn plane (`heartbeat.jsonl`
   has a 32-min gap 03:59:02Z→04:31:48Z; `fleet-validation.jsonl` shows value-ledger rc=2
   at 03:58:59Z, one second into the window, and nothing else until 04:52Z). Three+
   unrelated destinations dead simultaneously = local egress, not a Workato incident.
4. **Workato execution plane green all night.** This morning's watchdog (07:29 EDT):
   dev schedulers running and recently updated, canary 82964017 green, no P1, live API
   calls succeeding. Server-side execution never blinked; only this Mac's egress did.
5. **Corroborating context:** the same night produced the fleet-wide rc=1/rc=2 degradation
   cluster the watchdog filed as P2 #1 (11 stale jobs, validation failures across
   backup/gardener/dreamer/cortex/etc.) — a local machine having a bad night, not 15
   recipes having one. Machine was awake (caffeinate PID 18861 active 67h+, no pmset
   sleep events in the window) — so: awake machine, dead network path.

## Live probes this morning (all GETs, all healthy NOW)

| Recipe | URL | running | test cases live | Note |
|---|---|---|---|---|
| 82855731 audit_conversation_case_file | https://app.workato.com/recipes/82855731 | true | 1 (citc-AbpxcLar, created 10-06 — the same case that passed 10-18→10-21) | folder 35404885 |
| 82252165 Seismic Save to Workspace | https://app.workato.com/recipes/82252165 | true | 2 | matches registry cache |
| 82089919 Go-Live Announcement | https://app.workato.com/recipes/82089919 | true | 1 | last_run 10-20 22:54 |
| 82863111 Ledger Correlator (fixture) | https://app.workato.com/recipes/82863111 | true | 0 (fixture-phase recipe, force-run kind) | fixture passed 10-21 |

`GET /api/recipes.json?per_page=1` (the exact scan call) and
`GET /api/recipes/:id/test_cases` both return 200 with data right now. Whatever killed
last night's window is gone.

## Exact error text (task 1 — and the gap)

The report's exact text for all 15: `ERROR: could not start run` (runner line 129:
`POST /api/test_cases/run_requests` via `wt testcases run` returned no `data.id` — which
also covers total transport failure). **The underlying error body does not exist anywhere
on disk**: the runner captures it into a `detail` field but the report renderer drops it,
and the launchd log (`/tmp/fleet-regression.out`) has been 0 bytes since Oct 19 (run-job.sh
v2 logs to `~/.local/state/fleet/regression.log`, which holds only the runner's own prints).
This is precisely the gap the 2026-10-17 start-error-attribution investigation prescribed
a one-line fix for — **still unlanded**, and it cost this autopsy the exact error text
twice now.

## The fixture-phase triage

- **82863111, 82921718** — passed 10-21, timed out 10-22: same cluster (invocation POSTs
  hung; no job could be created). Part of the shared root.
- **82959481** — timed out BOTH 10-21 and 10-22: pre-existing per-fixture issue, NOT part
  of the cluster. Separate autopsy candidate.
- **83113565** — `webhook kind needs fixture webhook_url`: a local fixture-config gap
  (fixture lacks the trigger Request URL), pre-existing, unrelated to the cluster.

## Single most likely fix

**For the cluster itself: none — no asset is broken.** Tonight's 23:50 EDT run on a healthy
network should return to the ~10-17 pass baseline with the known masked/failed set. That
green-by-itself result IS the verification criterion.

**For the harness (so the next bad-network night doesn't produce a 19-error false alarm):**
1. Render `detail` on start-ERROR lines (the 10-17 one-liner; STILL not landed — do it first).
2. Zero-scan abort: `scan: 0 recipes` on a 1000+ estate must abort the run as
   "infrastructure failure" (or at minimum banner the report), not silently charge into 15
   doomed POSTs on a cached registry.
3. Give wt's `request()` an explicit timeout (~30s) and add a one-call pre-flight GET
   before the run loop; on transport failure, write one "runner environment down" verdict
   instead of N per-recipe ERRORs.

## What was NOT verified

- The exact API error body for last night's POSTs (unrecoverable — see gap above; needs the
  detail-render fix or a Josh-approved live POST probe, which read-only scope forbids).
- Anthropic-plane reachability in the window is inferred from the heartbeat/validation
  silence of claude-spawned jobs, not from a directly logged connection error.
- Root of the local blackhole itself (VPN drop, DNS resolver hang, proxy/LuLu rule, ISP
  blip) — out of reach of this evidence set; only its existence and bounds (23:59–00:35 EDT)
  are proven.
- Remaining 11 erroring recipes probed by registry-cross-check only, not individual GETs
  (uniform-onset + scan-zero makes per-recipe causes impossible; the 4 probed span the
  affected projects).

## Follow-ups (for Josh / triage, not executed — read-only scope)

- Land the three runner hardening fixes (BSYS Story candidate; item 1 is a re-file of the
  10-17 recommendation with tonight as the second proof of cost).
- Canonize this failure CLASS if it recurs tonight (signature: `regression-infra-egress-
  blackhole` — the two prior "could not start run" canon entries are closed and were the
  per-asset variety; this environmental variety is a distinct class).
- Separate autopsy for fixture 82959481 (two-night timeout, pre-dates the cluster).
- Mission-control closeout row deliberately not written: dispatch mandate was
  findings-file-only, change nothing else.
