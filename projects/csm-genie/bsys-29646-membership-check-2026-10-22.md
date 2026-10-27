# BSYS-29646 live membership check — 2026-10-22

Read-only prod investigation (UI path, Production environment 3535598,
signed-in Orca browser). No writes performed.

## What was checked

1. Environment flipped in-page to Production (AHQ | AI).
2. CSM Genie = `gin-AaTBfBon-TNoQgC-CD` (https://app.workato.com/genies/gin-AaTBfBon-TNoQgC-CD).
   End user access still lists exactly ONE gate group: **[TEAM] T32 | CSM,
   104 users** (confirms the 10-16 finding).
3. Group detail page: https://app.workato.com/members/access_control/environments/3535598/groups/fv1Cic8dCSZcEf8hZnc9Ec
4. Member search "shaver" → **No end users found**. Also "susan" → no match.
5. CONTROL TEST: search "abhishek" → "Showing 1" (Abhishek Dixit, known
   member). The search demonstrably works, so the negative is a true negative.
6. Screenshot evidence: `bsys29646-susie-not-in-group.png` (this folder).

## Conclusion

Susie Shaver is NOT in the CSM Genie's gate group. Her 2026-10-09
Firefighter grant never landed in `[TEAM] T32 | CSM`. Dissenter pass
(STANDS-WITH-CHANGES) noted the alternative: grant may have landed in Okta
but never synced into Workato (Workato syncs groups at login; a user who
belongs to the right IdP group but never logged in has no record to find).
The two are separated by an Okta-side check, not by Workato reads.

## Not resolvable read-only from here

- Global end-user record check (does Susie have a Workato Identity record):
  no UI page or in-page JSON route exposes a global end-user list (two API
  probes 404'd — two-strike rule applied). First execution step in the
  firing session.
- Manual-add persistence on an IdP-mapped group (docs say IdP sync can
  revert manual adds at next login): confirm the sync-surviving path before
  the add.

## Gate state

Prod write (group add via Okta path or manual Add end users) still gated.
Josh's 10-16 go lives in the triage ledger, not in a firing session; per
the blanket-delegation rule this session did not execute. Draft reply to
Nicholas staged at `bsys-29646-nicholas-timeline-reply-draft.md`.
