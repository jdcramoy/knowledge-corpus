# BSYS-29646 reply to Nicholas — DRAFT (confirm-gated, 2026-10-22)

Staged after the live membership check (2026-10-22) and the dissenter pass
(verdict STANDS-WITH-CHANGES; all four corrections incorporated). Never
auto-post: outward-facing under Josh's name, needs his confirmation. Post via
`jira.py comment BSYS-29646 --file <this-adjacent-txt>` after Josh's go.

Evidence for the diagnosis: `bsys-29646-membership-check-2026-10-22.md`
(same folder) + screenshot `bsys29646-susie-not-in-group.png`.

---

🎯 Verdict: I checked her membership in the gate group live just now. Susie is not in [TEAM] T32 | CSM, which is consistent with the error she sees. That settles the Workato-side half of the open question from my last update.

The remaining fix is a provisioning add, done the way that survives the Okta group sync (I'm confirming that mechanism before I touch anything), plus a fresh re-login on her side. The only thing between here and done is the internal go for the production access change, which I'm chasing on my side. Honest timeline: same day once that lands. I don't have a clock on the approval itself, so I won't pretend to. The last step is Susie's: a fresh login to pick up the group.

I'll post here the moment the add goes through, with the re-login instruction for her.

Verified today: the gate group's live membership. I searched the 104-member group for her and got no match, and a control search for a known member returned as expected. Not verified yet: whether her end-user record exists in Workato at all, and why the sync missed her; that check happens first when I execute. If she is already in the Okta group and the sync is what dropped her, the durable fix moves to the Okta side and I'll say so here.

Where I could be wrong: my working theory is the Firefighter grant never reached the gate group. The alternative is that the grant landed in Okta but never synced into Workato. The group membership alone can't separate those two; the Okta-side check can, and it's part of the same go.
