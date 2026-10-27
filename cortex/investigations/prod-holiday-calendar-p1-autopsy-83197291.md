# Autopsy: REC | Holiday Calendar Sync (prod 83197291) — 4/4 failures since 2026-10-20 deploy

**Date:** 2026-10-24 · **Mode:** READ-ONLY (no writes, no stop/start, no connection touches)
**Recipe:** REC | Holiday Calendar Sync — https://app.workato.com/recipes/83197291
**Workspace:** PROD — Workato AHQ | AI (josh-prod, workspace 3535598) · project 15783895 · folder 35747461
**Error (all 4 runs):** `HTTP request failed: Processing error occurred. The task submitted is not authorized.`

## VERDICT

**Not an expired token. Not a broken connection. A Workday-side task-permission gap.**
The prod ISU account behind connection "CON | ISU Prod" (19909763) authenticates fine — it is running
other Workday operations green this week on other recipes — but it is NOT authorized in the prod
Workday tenant for the `Get_Holiday_Calendars` web service task. Re-authing the Workato connection
will NOT fix this.

## Evidence chain

1. **Failing step located** — job j-Ac6kGKNK-JeYzsX-CD (2026-10-23 07:00, error_id
   c22ad4ef-1db0-4101-861d-6f3bdfd780f1): recipe line 3, adapter `workday`, op `Search_business_object`,
   web_service `Human_Resources/Get_Holiday_Calendars`. Job dies ~0.5s in, first real step.
2. **All 4 failures identical**, daily 07:00: 10-20 (j-Ac4D9XPm-H843te-CD), 10-21 (j-Ac4gBmtR-nJYWLD-CD),
   10-22 (j-Ac6FE6wt-gbPW4G-CD), 10-23 (j-Ac6kGKNK-JeYzsX-CD).
3. **Connection state unchanged at deploy** — 19909763 "CON | ISU Prod": authorized 2026-08-11,
   authorization_status `success`, no connection_lost. Nothing rotated at the 10-20 deploy.
4. **Same connection, other op, GREEN** — REC | Consumer Roster Sync (82917289, same folder, same
   connection 19909763) succeeded 2026-10-23 18:01 and 06:01 calling `get_wql_report`. Authentication
   path is healthy; only the holiday task is refused. (A Workday login failure returns
   "invalid username/password"; "the task submitted is not authorized" is the authenticated-but-
   not-authorized faultstring.)
5. **Dev twin runs the exact same op GREEN** — dev recipe 83190408 (josh-us), same name, succeeded
   TODAY 2026-10-23 07:00:33 (job j-Ac6kGKNL-B3f6Ac-CD) on the same
   `Search_business_object / Get_Holiday_Calendars` call, via dev connection 19760013
   "CON | Workato2 ISU Connection" (7 ok / 1 fail lifetime).
6. **Smoking gun for design intent** — the 10-20 01:03:32 deploy (manifest import) created prod
   connection 22340993 **"CON | Workato2 ISU Connection" — NEVER authorized** (authorized_at null),
   one second before the recipe itself (01:03:33). The recipe was then (updated 01:08:02) bound to the
   pre-existing "CON | ISU Prod" instead. The manifest intended this recipe to run as the Workato2 ISU;
   it is running as the old ISU Prod, which apparently lacks the holiday-calendar grant.

## Root cause

First recipe in prod to call `Get_Holiday_Calendars`. The old ISU Prod account was never granted that
web service task in the prod tenant (latent gap, invisible until this deploy). The manifest's own
intended identity — Workato2 ISU — has the grant in the dev/sandbox tenant (dev twin green) but its
prod connection shell was never authorized and the recipe was rebound away from it.

## Blast radius (connection 19909763 "CON | ISU Prod")

24 prod recipes bound to it; ALL others healthy on their own operations — the gap is per-task, not
per-connection. Only 83197291 calls Get_Holiday_Calendars. Sample: FUNC | Process Inbox Task Row
(82120559, 10.2M ok), REC | Inbox Task Discovery Hub (82120563, 12.6k ok), Time-Off Event Hub fleet
(82641524-28, 5.6k ok each), REC | Consumer Roster Sync (82917289, green 10-23), REC | BP Completion
Discovery Hub (82960043, 3.8k ok). Connection 22340993 (Workato2 ISU): zero recipes bound, never
authorized. Side observation (unverified): several hub recipes show last_run 2026-10-10 despite
running=true — worth a separate glance, may be list-API staleness.

## Adjacent prod issue spotted (same project, BSYS-29799 OOO merge)

**REC | OOO Snapshot Refresh (82917290)** — https://app.workato.com/recipes/82917290 — is STOPPED
(stop_cause `trigger_errors_limit`) since the same 10-20 01:07 deploy window. Its 4 failures were
10-16/17 "Service unavailable" (different error, likely Workday maintenance) but it was never
restarted. The OOO snapshot project currently has one recipe failing and one stopped.

## Remediation — two paths, A is the designed one

**Path A (recommended — run as the ISU the manifest intended):**
1. Confirm with the Workday admin that a Workato2 ISU exists in the PROD tenant with
   Get_Holiday_Calendars access (it has it in the tenant dev points at — proof: dev twin green today).
2. Workato prod UI → Connections → open "CON | Workato2 ISU Connection" (22340993) → enter the prod
   Workato2 ISU credentials/tenant endpoint → **Connect/Authorize**.
3. Recipe 83197291 → step 3 (Workday Search business object) → switch connection from
   "CON | ISU Prod" to "CON | Workato2 ISU Connection" → Save.
4. Jobs → rerun j-Ac6kGKNK-JeYzsX-CD → verify green before the next 07:00 tick.

**Path B (keep ISU Prod):** Workday admin adds the ISU Prod integration security group to the domain
security policy granting the Get_Holiday_Calendars web service operation (Integration GET), then runs
"Activate Pending Security Policy Changes" in the prod tenant. No Workato edit needed; rerun the
failed job to verify.

**Do NOT waste a cycle on:** re-entering the ISU Prod password / clicking Reconnect on 19909763 —
authentication is proven working on that connection today.

## Not verified (read-only scope)

- Whether Workato2 ISU exists in the prod tenant with the holiday grant (needs Workday admin console).
- The exact prod tenant security policy name for the holiday task.
- OOO Snapshot Refresh's last-run-at (10-20 01:07) vs its 10-16/17 failures — stop timing inferred.
- Dev twin's single lifetime failure — not inspected.
- Connection endpoint URLs (credentials/endpoints not exposed via API — intentionally).
