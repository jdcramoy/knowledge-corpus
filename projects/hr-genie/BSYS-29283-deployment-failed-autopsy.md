# BSYS-29283 — Deployment Failed: auto-deploy duplicate-connection error

Ticket: https://workato.atlassian.net/browse/BSYS-29283
Status 2026-10-09: plan ready — awaiting Josh's authorization (plan posted as ticket comment 1134648).

## Root cause (live-verified, prod read-only)

Oct 5 auto-deploy failed in recipe [3792736, job j-AbpJTfoE-EHPo6n-CD](https://app.workato.com/recipes/3792736/job/j-AbpJTfoE-EHPo6n-CD):
importing package 42148590 tried to place `Config/Connection/con_workato2_isu_connection.connection.json`
into `Home/Agentic | HR Self Service Genie/Config/Connection` and aborted with
"found a duplicate in Home/Agentic | HR Self Service Genie/zArchive".

Prod estate evidence (wt-prod, 2026-10-09):

- Prod HR Genie project folders: Config 32273841, Core 32273842, Extensions 32273843 — **zero connections in any of them**.
- All six runtime connections sit in zArchive (folder 32273844):
  22080797 CON | Workato2 ISU Connection (Workday), 22080798 CON | Workday REST API,
  22080796 CON | Workato API HR Genie, 22080794 CON | Corp API HR Genie Dev,
  22080795 CON | HR Self Service Genie (genie slack), 19908082 CON | Workday Sandbox - Smoke Test.
- Import matches a package connection only inside the destination folder; same name anywhere else
  in the project = duplicate = fail-closed. Nothing imported, no partial state.

Consistent with the Oct 5 Vegas-folder cleanup (Josh moved recipes out, deleted Vegas folders) and
Patricia's Oct 6 comment (connection names differ Dev/Prod).

## Remediation plan (prod writes — Josh's gate)

1. Move the manifest connections (at minimum 22080797; preemptively 22080798, 22080796, 22080794,
   22080795) from zArchive into prod `Config/Connection`. Leave 19908082 (sandbox smoke test) in
   zArchive. Folder move only — no re-auth, no credential change, folder does not affect runtime references.
2. Re-run the import (auto-deploy re-run, or `wt-prod packages import` of package 42148590).
3. Verify per runbook addendum (ticket comment 1128118): mapped folders, 8 project properties
   incl. `Test Send Email Address = not-configured`, `FUNC | Send Genie Event` genie-binding re-map,
   schema-only notification-log table, three smoke cycles with real-recipient verification.
4. Optional hygiene: the six connections never belonged in zArchive; delete only confirmed orphans.

Points: 2. Risks: the same-folder-map mechanism is inferred; a failed re-import is a no-op (fail-closed
proven by the first failure).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [HR Genie Prod Deployment Checklist](../../../kb-corpus/confluence/extbt/2745008431-hr-genie-prod-deployment-checklist.md)
- [Workato Genie & MCP Development Guide](../../../kb-corpus/confluence/intbt/2423914526-workato-genie-mcp-development-guide.md)
- [Change log: Wave 7 Automation Updates](../../../kb-corpus/confluence/extbt/2939977886-change-log-wave-7-automation-updates.md)
- [[MK-8] Lead Genie: Deployment Plan](../../../kb-corpus/confluence/intbt/961576972-mk-8-lead-genie-deployment-plan.md)
<!-- kb-bridges:end -->
