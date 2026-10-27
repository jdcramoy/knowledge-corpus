# P1 — Recipe 83197291 (Holiday Calendar Sync) trigger liveness — 2026-10-25

## VERDICT: TRIGGER ALIVE
Scheduled trigger fires on schedule, daily at ~07:00:07 PT. Failure is downstream at
step 3 (Workday Get_Holiday_Calendars): "HTTP request failed: Processing error occurred.
The task submitted is not authorized." — the known ISU-grant issue.

## Job evidence (10 most recent; recipe has 5 total jobs — no ACL denial, read succeeded)
| Job ID | Started at (PT) | Trigger ts (scheduled) | Status |
| --- | --- | --- | --- |
| j-Ac8HJbc3-znL3zm-CD | 2026-10-24 07:00:23 | 2026-10-24 07:00:07 | failed (Workday not-authorized) |
| j-Ac6kGKNK-JeYzsX-CD | 2026-10-23 07:00:24 | 2026-10-23 07:00:06 | failed (same class) |
| j-Ac6FE6wt-gbPW4G-CD | 2026-10-22 07:00:23 | 2026-10-22 07:00:08 | failed (same class) |
| j-Ac4gBmtR-nJYWLD-CD | 2026-10-21 07:00:20 | 2026-10-21 07:00:08 | failed (same class) |
| j-Ac4D9XPm-H843te-CD | 2026-10-20 07:00:19 | 2026-10-20 07:00:09 | failed (same class) |

All 5 jobs in history failed; totals succeeded=0, failed=5. Latest confirmed error detail
(job j-Ac8HJbc3-znL3zm-CD, read directly): failed at line 3, workday Search_business_object,
Get_Holiday_Calendars_Request → "The task submitted is not authorized."

## Implication
One line: the scheduler is healthy — fix the Workday ISU grant for Holiday Calendar Sync and
the 07:00 PT runs should go green; nothing to repair in the trigger itself.
