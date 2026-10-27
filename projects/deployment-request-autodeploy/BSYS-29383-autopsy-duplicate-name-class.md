# BSYS-29383 — autopsy: the 30-job "Recipe function execution error" class (duplicate-name resolution)

Date: 2026-10-16 · Source: `wt jobs list 3792733 --status failed --raw` (bt-prod, workspace 800229),
701 failed jobs classified on `error_parts.message`. Companion to `BSYS-29383-plan.md`.

## The class

All 30 non-memory function-execution failures on prod 3792733 ("Get Folder ID for Deployment") are
the same thing: **duplicate-name resolution failures.**

The deploy path (3792733 → 3792735 "Get Resource Path" → 3792734 "Get Recipe Folder Path") resolves
each manifest asset's folder by asset **name** against the live workspace. When two assets share a
name, resolution is ambiguous and the call hard-fails:

> "There are duplicate recipes with the name X, so we were unable to automatically determine the
> root folder"

Breakdown of the class (dissent-verified): **24 duplicate recipe names** (resolver 3792734),
**3 duplicate connection names** (resolver 3792732), **2 duplicate project names** (resolver
56324388) — 29 of 31 non-memory function errors in the 2026-07-28 → 2026-10-13 window. The other
two: one 502 (the known transient class, needs retry semantics) and one empty inner error. Repeat
offenders include "New Critical Ticket CSM Notification", "search_jobs", "[TSR] LF| Process
TechRequest", "Add Attachment to Objects" (3 each).

## Shape and cadence

- Spanned 2026-07-28 → 2026-10-13; ~2–3/week, chronic, **ongoing** (3 jobs on 10-13).
- Independent of manifest size, independent of the memory class. The `code`-strip fix in the dev
  twin (3383902) will not touch this class — that is why the plan held one autopsy back before close.
- Unlike the memory class (ramping), this one is flat: it fires whenever a deployment's manifest
  happens to contain an asset whose name collides with anything already in the workspace.

## Root cause

Name-based folder resolution is load-bearing in the deploy path, but the BT prod workspace does not
keep asset names unique (and nothing forces it to). Any collision inside a deployment's asset set
fails the whole deploy with a hard error no retry can clear.

## Fix direction (revised after dissent)

1. **Real fix, all three resolvers:** switch folder resolution from name-based to a deterministic
   key in **3792734 (recipes), 3792732 (connections), and 56324388 (projects)** — patching only
   3792734 leaves 5/29 failures live.
2. **The key is the manifest's folder path, not the asset ID.** RLCM manifest rows carry
   source-workspace IDs; cross-workspace deploys mint new destination IDs, so ID-based lookup
   resolves nothing in the destination. The manifest's `folder`/`absolute_path` is the durable
   key (same-workspace deploys may additionally use asset IDs).
3. **Fallback is load-bearing, not optional:** when a name/path still matches multiple assets
   (hand-built or partial manifests), prefer the asset inside the deployment's destination
   project; if still ambiguous, fail with the candidate list attached so the operator can fix the
   collision rather than guess.
4. **Retry semantics** for the residual transient class (502/503) live in the same envelope the
   plan already proposes for the 502 — not part of this class's fix.
5. **Hygiene:** the duplicate assets themselves (e.g. three recipes named "search_jobs") are their
   own cleanup queue, but the pipeline must not depend on name uniqueness either way.

## Evidence

- `wt jobs list 3792733 --profile bt-prod --status failed --raw` → 701 failures, classified:
  639 list-view-empty (older/mostly memory-class), 31 explicit memory shutdowns, 30 function
  execution errors, 2×503, 1×502.
- Detailed trace j-AbxAMeso-9YLBRw-CD (memory class, full chain 3792733→3792735→3792734→3792740).
- Sample duplicate-name failure: j-AbwaCaLY-6gbtXb-CD (2026-10-13).

Dissent verdict: SHIP-WITH-CHANGES (2026-10-16, independent re-pull reproduced the 24/2/3 split);
all three material changes incorporated above. Unverified at dissent time: DEPLOYMENT.FOLDERS
bookkeeping side-effects of these failures, live duplicate enumeration (the API's name filter
ignored the param).
