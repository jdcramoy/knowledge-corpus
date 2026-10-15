# BSYS-29701 — Lovable Cloud × Wiz CNAPP integration (plan)

Ticket: https://workato.atlassian.net/browse/BSYS-29701 (New Project/Feature, created
2026-10-15 by Archeshma Bodhanapu, label `proj-genie-created`). Plan posted as
comment 1139707 (2026-10-15T11:41Z), points 3. Grouping: vibe-coded-governance
(epic BSYS-25523) — this is CNAPP coverage for the same Lovable-built app
population that governance tracks.

## Classification

Two-vendor configuration task, no Workato assets. Lovable mounts project code in
its own sandbox and runs the Wiz CLI there (SCA + SAST); findings land in each
project's Security view and in Wiz's Code & Build Scans page. BT's role:
coordination, credential discipline, verification.

## Correction to the ticket

The ticket's step list ("Connect to Wiz page", "configure Wiz CLI in Lovable")
matches neither vendor's documented flow. Real path: Wiz integration deployment
(Settings > Deployments) + Lovable Connectors > Wiz > Add connection. No
user-facing Wiz CLI step exists.

## Step zero: workspace inventory

Docs allow exactly ONE Wiz connection per Lovable workspace, private to creator,
owner/admin-only. Ticket says "teams" plural. N workspaces = N deployments, N
connections, N quota draws. Inventory decides the shape of execution.

## Execution (per workspace)

1. Confirm Token URL with Wiz admin (default Cognito auth.app.wiz.io; Auth0
   tenants auth.wiz.io).
2. Wiz: create Lovable integration deployment, capture Client ID + Secret into
   1Password same-sitting (secret displays once; miss = rotate).
3. SecOps sign-off on CI/CD scan policy list (blank = tenant defaults; wrong
   policy name = "Wiz scan failed" findings). Policies/credentials editable
   later — quality gate, not a one-way door.
4. Lovable: Connectors > Wiz > Add connection, invite entire workspace
   (private-by-default otherwise = silent coverage gap).
5. Roll out per workspace.

## Verification

- Throwaway project pinning a KNOWN-VULNERABLE dependency (so green can't mean
  "not scanning"): Wiz section appears with deep links.
- Same scan on Wiz Code & Build Scans page (verifier needs Wiz portal access).
- Severity map holds: Critical>Error, High>Warning, Medium<Info.
- Dependency update + rescan flips old findings to outdated.

## Dissent outcome (2026-10-15)

Dissenter (independent model) verdict: plan stands. Fixed its findings:
(1) "single connection = one-time policy decision" was FALSE — policies and
credentials are editable later; only the secret's initial display is one-shot.
(2) Ticket-vs-docs flow contradiction now stated in the comment. Added: step
zero inventory, Wiz-side-steps-are-inferred disclosure (Wiz guide is
login-gated; docs.wiz.io returned 500 twice), known-vulnerable-dependency
verification pin, points 2→3.

## Open items (Josh-gated)

- Josh's go to kick off execution.
- Identify Lovable workspace count + owners (informational, SecOps/Wiz admin).
- "Method: M1" on the ticket = probably intake boilerplate (guess); if it's an
  engagement model it changes who executes step 4.
