# Investigation: addCommentToJiraIssue "stale commentVisibility" failures (BSYS-29510)

Read-only investigation, 2026-10-12 ~21:5xZ, session in ~/Documents/workbench. No Jira writes
performed; nothing modified outside this file. Evidence: transcripts cba0c1a8 (parent,
JIRA-Management workspace) + subagent agent-a93a7ec8efcc9c36e, plus control transcripts.

## Verdict (one line)

There is no stale serialization anywhere: the gateway model generated an optional
`commentVisibility` param in its own tool-call JSON on every attempt, Jira rejected the
visibility values with a real 400, and the session misread that as harness-level injection.
The fix is to OMIT the param — the minimal call shape is proven working against this cloudId.

## (1) Where the "stale commentVisibility" originates

**Answer: model output behavior on the gateway model — not the served schema, not the client
harness, not session state.** Evidence from `~/.claude/projects/-Users-<user>-orca-
workspaces-workbench-JIRA-Management/cba0c1a8-...jsonl`:

- Every tool_use block recorded in the transcript (L224, L234, L239, L250, L257, L268, L274,
  L285, L306, L347, L429, L451 — 12 direct attempts) already contains
  `"commentVisibility": {...}` inside the model-emitted input, alongside
  `['cloudId','commentVisibility','contentFormat','issueIdOrKey','commentBody']`. The transcript
  records the model's own emission; there is no post-hoc injection layer between it and the log.
- The values CHANGE across attempts in a way no cache would produce: `Developers` →
  `Administrators` → `atlassian-addons-project-access` → back to `Developers` (x5). The failing
  session's own narration ("harness replaying a cached commentVisibility: Developers") is
  contradicted by its own transcript — it kept changing the value itself.
- The fresh subagent independently generated `commentId: "0"` AND
  `commentVisibility: Administrators` — a value nobody ever set anywhere. `commentId: "0"` is a
  model confabulation, which also rules out any parent→subagent state inheritance.
- Served schema (extracted from the failing session's own prompt_snapshot, attachment.tools[24],
  byte-identical to the schema served today): `required: [cloudId, issueIdOrKey, commentBody]`;
  `commentVisibility` and `commentId` are OPTIONAL. The schema invites but never demands the param.
- MCP config is stock: `~/.claude.json` → atlassian = `{type: http, url:
  https://mcp.atlassian.com/v1/mcp/authv2}`, no project-level override, no tool filtering, no
  schema cache on disk. Tool_use ids (`chatcmpl-too...`) confirm a chat-completions gateway
  backend where input = model emission, verbatim.

Related but distinct failure mode seen in OTHER sessions (Google-Semantic-MCP 9f2bd9b7,
~/.claude/-claude c65db63c): `<tool_use_error>InputValidationError ... could not be parsed as
JSON`, with the model's emitted JSON truncated at ~90 bytes right after `"commentVisibility": `.
Same root family — model output corruption around this specific optional param — but the
BSYS-29510 session's 8 failures were all the 400/404 path, not the parse path.

## (2) Does the current server accept a minimal well-formed call?

**Yes — proven, not inferred.**

- Served schema today requires only `cloudId`, `issueIdOrKey`, `commentBody`.
- Control transcript 46a3bfd8 (Documents project) posted 3 comments against the SAME cloudId
  (99bd32a1-58a6-41d6-8e61-c98194c68259) with the 4-key shape
  `{cloudId, issueIdOrKey, contentFormat, commentBody}` and no visibility param — real 200
  responses with comment ids 1043979 / 1043980 / 1043981.
- The BSYS-29510 failures were all Jira-side `commentLevel` validation, meaning everything else
  about the call (routing, issue resolution, body) was fine; the ONLY defect was the param:
  - 7x: `{"errors":{"commentLevel":"Role with id: Developers does not exist."}}` (400)
  - 1x: `"You are currently not a member of the project role: Administrators."` (400)
  - 1x: `"You are currently not a member of the project role: atlassian-addons-project-access."` (400)
  - subagent 4x: `404 "Can not find a comment for the id: 0."` — caused by the invented
    `commentId: "0"` turning the add into an update of a nonexistent comment.

## (3) The exact corrected invocation for the blocked session

Target: BSYS-29510, cloudId `99bd32a1-58a6-41d6-8e61-c98194c68259`. Body = full text of
/tmp/bsys29510_comment.md (re-review verdict: asset-identical to rejected 17:21 package; 5
blocking incl. auto-deploy-fired-after-blocking-review; 5 non-blocking).

```
mcp__atlassian__addCommentToJiraIssue:
  cloudId:       "99bd32a1-58a6-41d6-8e61-c98194c68259"
  issueIdOrKey:  "BSYS-29510"
  contentFormat: "markdown"
  commentBody:   <full contents of /tmp/bsys29510_comment.md, verbatim>
  # commentId:      OMIT — omitting adds a new comment; any value turns it into an update
  # commentVisibility: OMIT — omitting posts a normal (non-restricted) comment, as every
  #                    prior successful review post did. Do not "fix" the role name; Jira
  #                    rejects role visibility this account cannot set on this project.
```

One-sentence instruction for the retry session: "Post the comment with exactly cloudId,
issueIdOrKey, contentFormat: markdown, and commentBody — pass no other parameters." If the
gateway model re-inserts commentVisibility anyway (the behavioral-stickiness risk), fall back to
the REST API (`POST /rest/api/3/issue/BSYS-29510/comment`) or hand Josh the artifact — do not
retry the same shape a third time.

## What was NOT verified

- The corrected call was NOT executed (read-only mandate; posting needs Josh's gate). The minimal
  shape is proven by the 46a3bfd8 control transcript, not by a fresh live post.
- Whether the gateway model (glm-flash class) reliably omits the param on a fresh attempt — the
  stickiness risk above is unquantified.
- Nothing about prod (atlassian MCP is the same site either way here; no prod gates touched).
