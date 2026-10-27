# BTSUP-79354 — reply draft (staged, confirm-gated)

Requester: Ashok Kumar Jagannadham. His nudge "any update please?" landed
2026-10-22 16:35Z. Ball is with Marc (create a dev-only end-user group mapped
to Okta per Josh's 2026-10-21 19:34Z comment), then Josh attaches it to the
Career Coach Genie project. No end-user group is API-visible, so the pass
could not verify whether Marc's group exists yet. Status-only reply, dissent
not required.

## Draft (Josh voice, public)

Hi Ashok,

Thanks for the nudge. The group you need doesn't exist yet, and that is the
whole story: the existing HR Genie user group carries production access, and
we're not putting that on a build project. The fix is a new development-only
group mapped through Okta, which Marc is setting up; once it exists I'll add
it to the Career Coach Genie project and your access works.

I'll post here as soon as the group lands. If it's blocking something urgent
in the meantime, ping me in the Slack thread and I'll bump it.

## After confirm

Post via addCommentToJiraIssue (markdown, BTSUP-79354). If the group landed
before posting, replace the first paragraph's status with the real one and
skip the bump offer.
