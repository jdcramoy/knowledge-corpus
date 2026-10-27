
## knowledge-remote-creds-split (2026-10-16, read-only probe)

VERDICT: ACCOUNT-WIDE credential expiry, NOT repo-specific loss.

Evidence (all GIT_TERMINAL_PROMPT=0):
- origin of ~/.claude/knowledge: https://github.com/Workato-All/josh-knowledge.git
- git ls-remote josh-knowledge → "remote: Repository not found." / fatal
- git ls-remote Workato-All/workato-agentic-kit → IDENTICAL "Repository not found."
- git ls-remote Workato-All/josh-orca → IDENTICAL "Repository not found."
- Control: git ls-remote github.com/git/git (public, no auth) → SUCCEEDS (f57c9a7 HEAD)
- Credential helper: osxkeychain; stored GitHub acct "jcramoyWKTO"

Reasoning: GitHub HTTPS returns 404 "Repository not found" both for missing repos AND when the
presented credentials lack access to a private repo. Anonymous public access works, so transport
and DNS are fine. Three distinct private Workato-All repos fail with the identical signature —
simultaneous deletion of all three is implausible; the stored token is dead/expired/revoked.

Consequence: repo existence (was josh-knowledge deleted or moved?) is UNTESTABLE until creds are
refreshed. Fix path (Josh-gated, no action taken): re-auth the osxkeychain GitHub credential
(gh auth login or new PAT for jcramoyWKTO), then re-run ls-remote on josh-knowledge — if it then
404s, the repo itself is gone; if it succeeds, everything is fine.
