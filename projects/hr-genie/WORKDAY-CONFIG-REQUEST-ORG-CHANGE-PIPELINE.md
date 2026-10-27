# Workday Config Request — Org Change Suggestion Pipeline (BSYS-29773, Phase 3 prerequisites)

**Prepared:** 2026-10-17 · **Updated 2026-10-18** (REST draft-then-submit discovered — kickoff needs NO new ISU write grants) · **Rebuilt 2026-10-26** at the knowledge-tree path from the repo original plus the Worker Index extension decision.
**Status:** DRAFT — do not send until Josh approves (external request).
**Why now:** BP configuration is the longest-lead item for Phase 3 (manager-VUA BP kickoff). Everything in Phases 0–2 proceeds without it.
**Connections affected:** same ISU/ISSG as the OOO request (`CON | Workato2 ISU Connection` 19760013 SOAP/WQL, `CON | Workday REST API` 19218617 REST).

## Key finding (2026-10-18): use the REST draft-then-submit flow, not SOAP writes

Workday Staffing REST (v6 spec, developer.workato.com openApiFiles) has a first-class
organization-assignment-change flow:

- `POST /workers/{ID}/organizationAssignmentChanges` (or `POST /organizationAssignmentChanges`) —
  **creates the change event as a DRAFT**; "the same Workday UI validations apply"; nothing
  persists until submit. Secured by **Business Process Type: Change Organization Assignments
  for Worker** (Scope: Organizations and Roles), not by a plain domain.
- `POST /organizationAssignmentChanges/{ID}/submit` — **initiates the Change Organization
  Assignments business process**; empty body = the Submit button; Save-for-Later supported.
- `GET /organizationAssignmentChanges/{ID}` (+ comment/costCenter/businessUnit subresources) —
  read the event back: kickoff verification and status tracking.

**Consequence:** the primary kickoff runs under the requesting manager's VUA identity with the
permissions that manager already has in the Workday UI — **no new ISU write grants and no new
domain grants for the kickoff itself**. The draft step also gives Phases 1–2 a Workday-native
parking place: the request can exist as a draft event while pre-approvals run, then submit fires
the BP only after the chain confirms.

## The blocking evidence (S21 permission-masked 404)

**LIVE evidence, 2026-10-18, job j-AbzzJDK6 on recipe 83152837:** `POST /workers/{WID}/organizationAssignmentChanges`
with the person's real WID answers `404 {"error":"not found: organizationAssignmentChanges","code":"S21","severity":"Critical"}`
after retries — the same S21 permission-masked-404 pattern as the OOO holiday request (BTSUP-72246 §3).
Worker resolution (`GET /workers/{WID}` via the org-chart snapshot WID) works on the same connection,
so the connection is healthy: only the organizationAssignmentChanges surface is refused. Diagnosis:
the ISU/ISSG lacks the **Change Organization Assignments for Worker BP-type + Staffing Organizations
domain** grant. Granting it is the terminus ask below.

## Asks (for the Workday config/integration team)

1. **BP configuration check** (impl wd108 first, then prod):
   - Is `Change Organization Assignments` BP configured/enabled, and what is its routing
     (approval chain steps, people-partner/VP conditions)?
   - Confirm a manager initiating via REST lands identically to UI initiation (initiator identity,
     review chain, notifications).
2. **ISU read grants** (Get/View) for event read-back + validation, on the ISSG securing
   connections 19760013 / 19218617:
   - The domain(s) securing `GET /organizationAssignmentChanges/{ID}` — per the spec:
     **Staffing Organizations: Business Unit / Company / Cost Center / Supervisory** family
     (verify exact set in the tenant security matrix; Scope: Organizations and Roles).
   - `Get_Supervisory_Organization_Assignment_Restrictions` (Human_Resources SOAP) for the
     allowed-assignment validation input, and `Find_Organization`/`Get_Organizations` for
     target resolution — likely already covered by the snapshot refresh's grants; verify, don't
     duplicate.
3. **ISU write grants — FALLBACK ONLY** (only if a system-initiated path is ever needed; primary
   path is manager-VUA and needs none):
   - Initiate right on the `Change Organization Assignments` BP for the ISSG
     (BP definition → Start step → Initiate → add ISSG).
   - Modify on the domain securing the write (`Worker Data: Organization Assignments` — verify
     exact name in tenant).
   - Same pattern for `Change_Job` (BP "Change Job", domain "Worker Data: Job") ONLY if the
     classifier routes manager/level changes there.
4. **ISU read grants for authority-check fields (Worker Index extension).** DECIDED (Josh,
   2026-10-23): extend org-chart snapshot table 137030 under its owning project with exactly
   two new columns — **People Partner WID** and **HRBP WID** — so the org-change pipeline can
   server-verify authority for people-partner and deeper claims instead of falling back to
   `chart_asserted`. No terminated flag (the `Active` column already carries it, inverted) and
   no version stamp (generation-pinning already covers it); refresh cadence inherits the
   existing 4h schedule. The extension needs Get/View on the People Partner and HRBP worker
   fields for the ISSG securing connections 19760013 / 19218617; exact securing domains are
   verified against the tenant security matrix before filing. If the ask is refused, the
   fallback is the status quo (`chart_asserted` with recorded advisory), recorded as the
   security posture on record.

## Notes

- Also proven live 2026-10-18: the Workday REST adhoc connector DROPS query strings
  (`GET /workers?email=…` returned the unfiltered 1,550-worker set even URL-encoded) —
  worker resolution must use path-based WID lookups (snapshot index) or WQL, not query params.
- Impl-tenant fidelity caveat (per OOO precedent): dev ISU reads wd108 while real data lives in
  Workday prod; end-to-end BP testing in dev is config-shape validation only. Final UAT happens
  after prod connection config.
- Workday REST secures by domain/BP-type, not OAuth scopes (the spec declares OAuth2 with an
  empty scope set) — the grant mechanism is the same domain-security request as the OOO holiday
  one, which is the format precedent.
- Ops verified against the Staffing/Human_Resources WSDL v46.2 index (2026-10-17) and the
  Staffing REST v6 OAS spec fetched 2026-10-18: exact operation names above are real, not guessed.
- Existing team-move route precedent: BT Dev recipe 82948089 → HR connector → HR Dev Workday
  sandbox (recipe 81992449) already proves a Workday write path from this estate; its grants are
  a floor to check, not to duplicate.
- Sequencing gates on the Worker Index extension build (not this request): the org-chart MCP
  owner is consulted before the column change, the migration guard applies (no authority-data
  widening before the red-team verdict, which must be PASS or PASS-WITH-NOTES), and the intake's
  `chart_asserted` fallback flips to strict server-verify only after the verdict AND the index
  actually carries the data.
- Original of record: `Workday-Development/docs/workday/org-chart-integration/WORKDAY-CONFIG-REQUEST-ORG-CHANGE-PIPELINE.md`
  (repo copy); this knowledge-tree copy carries the same asks plus the 2026-10-23 extension decision.
