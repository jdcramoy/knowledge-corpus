# Workday MCP head-to-head benchmark plan (staged 2026-10-26 — DO NOT RUN YET)

**Purpose:** identical-asks comparison between our Workday MCP surface (Workday End-User MCP
mcps-AYbrRaxY-dhF-CD + org-chart MCP, both dev) and Workday's OOTB MCP server, to decide where
the estate builds vs consumes vendor-native.

**Method laws (inherited from the org-chart dev-vs-live benchmark):**

- One identical call per case per surface, never a second probe to paper over a first result.
- Same identity class on both sides: a single test end-user (Josh's own VUA identity) so
  scoping differences are tool design, not identity differences.
- Score each case: correct / correct-but-lossy / wrong / refused-clean / refused-ugly, plus
  wall-clock latency and token weight of the response.
- Captured evidence per case: raw request, raw response, timestamp. No paraphrase at capture time.
- Neither surface gets a second attempt; a failed call is a data point, not an incident.

## The 10 identical asks

1. **Who am I?** Resolve the caller's own worker record (name, business title, work email).
   Tests: identity resolution, personalization.
2. **Who is my manager?** Manager name + title + email for the caller.
   Tests: self-scoped org traversal (the judge false-positive lesson applies: surfacing the
   caller's OWN data is desired-correct).
3. **Direct reports of my manager.** Names + titles.
   Tests: one-hop org read beyond self, field allowlisting.
4. **Full org under my manager.** Recursive descendants.
   Tests: pagination, truncation truthfulness, depth limits on a real subtree.
5. **What is my PTO balance?** Absence balances for the caller's plan.
   Tests: absence domain read, plan-type disambiguation (depletable-first rule).
6. **Find an approved time-off row for a named coworker in a date window.** Another worker's
   approved absence in [today, today+6].
   Tests: cross-worker scoping (should refuse clean under VUA or scope to what the identity
   may see), future-dated row semantics.
7. **List my pending inbox tasks.** The caller's open Workday tasks.
   Tests: business-process inbox read, prompt-to-action accuracy.
8. **What is my compensation grade range?** Known tenant finding: no manager-readable
   comp-range surface under VUA (403s, fail-closed).
   Tests: refusal quality on an unauthorized surface — does the tool degrade cleanly or
   fabricate?
9. **Submit a time-off request for tomorrow, then cancel it.** Real write + undo.
   Tests: write path, idempotency, cancel semantics. ONLY on the dev tenant, ONLY with a
   fixture-safe date, and skipped entirely if either surface cannot guarantee dev-tenant
   routing.
10. **Resolve a person by email and return their employee WID.** A real name/email from the
    1,550-worker tenant.
    Tests: search-vs-path resolution (our adhoc connector drops query strings — how does the
    OOTB surface handle filtering?), identifier hygiene in the response.

## Scoring sheet (fill at run time)

| # | Ask | Ours: verdict | Ours: latency | OOTB: verdict | OOTB: latency | Notes |
|---|-----|---------------|---------------|---------------|---------------|-------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |
| 9 | | | | | | |
| 10 | | | | | | |

## Not decided yet (Josh's calls before the run)

- Which OOTB endpoint we are testing against (Workday's official MCP server access, connection,
  and any grant it needs — that provisioning itself is an external ask).
- Case 9 runs or is skipped (write-path on dev tenant).
- Whether the OOTB side runs under Josh's identity or a service identity.

**Status: staged only. Nothing has been run.**
