# BSYS-29519 v45 anchor inheritance — INHERITED/FIXED/NOT-FOUND verdict (READ-ONLY)

Investigated: 2026-10-20. Dispatch: cortex attention-queue item, dispatches.jsonl
2026-10-20T04:29:37Z ("does the v45 collector from the BSYS-29498 re-export still
carry the v43 classifier's lossy anchors?"). Question origin: cortex questions.jsonl
2026-10-19T04:42Z. No writes made to any asset.

## VERDICT: FIXED

The v45 collector does NOT carry the v43 classifier's lossy anchors. The getaddrinfo
misclassification (transient DNS failure -> permanent conversation_gone_404 ->
watermark advance = silent loss) is absent from the live v45 code, and a live
execution of the exact shipped v45 Ruby against the dissenter's attack strings
proves it.

## Evidence

### 1. Live recipe pulled and version-verified

`wt recipes get 82862205` (read-only, dev workspace): REC | HR Genie | Conversation
Event Collector, running=true, **version_no: 45**, updated 2026-10-16T00:08 PT,
version author Joshua Cramoy — matches the BSYS-29498 re-export build (package
42247217, collector v45, per mission-control registry triage-pass-2026-10-16 row).
Recipe URL: https://app.workato.com/recipes/82862205

### 2. The classifier code, read from the v45 payload (step 46, invoke_custom_ruby_code_dc75)

v43's lossy anchor (per dissenter.jsonl, thread dissent-bsys-29519-v43-classifier):

    /\b404\b[^0-9\n]{0,20}\bnot[ _-]?found\b/   # 20-char window — getaddrinfo attacks match

v45's shipped anchor-2 (verbatim from the pulled code):

    lmsg =~ /\b404\b[ ]?\(?(?:not[ _-]?found)\b/

Adjacency only: optional single space + optional open paren, then "not found" must
follow 404 immediately. The 20-char window is gone. The in-code comment names the
exact transient shapes as non-matching: "'read 404 bytes; record not found' or
'after 404 ms: host not found' (transient shapes) do NOT match".

Branch order (verbatim order in the shipped code):
1. wait-timeout signature (`page_commit_async_job_failed` + `failed=0` +
   `timed_out=[1-9]`) => permanent=false, page UNCOMMITTED, watermark retries — FIRST
2. poll-404 terminal (`page_commit_async_job_failed` + structural http_404) => permanent=true
3. page_budget_exhausted => permanent=false
4. any other structural http_404 => conversation_gone_404, permanent=true
5. else re-raise

The lossy-first ordering defect (dissenter finding 2) is gone: a mixed
timeout-plus-404 input takes the deferral branch.

### 3. Live execution of the exact v45 classifier (system Ruby, 2026-10-20)

    "getaddrinfo failed after 404 ms: host not found"   => RE-RAISE (visible failure)
    "getaddrinfo: port 404 - host not found"            => RE-RAISE (visible failure)
    "read 404 bytes; record not found"                  => RE-RAISE (visible failure)
    "page_commit_async_job_failed: failed=0 timed_out=1 detail: poll status 404"
                                                        => DEFER wait_timeout permanent=false
    "404 Not Found"                                     => PERMANENT conversation_gone_404
    "Response code 404"                                 => PERMANENT conversation_gone_404
    "HTTP 404"                                          => PERMANENT conversation_gone_404
    "Error: 404 (Not Found)"                            => PERMANENT conversation_gone_404

All three dissenter attack strings — including both getaddrinfo variants — now
re-raise (job fails visibly, cycle replays) instead of taking terminal-success.
True 404 shapes still classify permanent, so the intended behavior is preserved.

### 4. Documented residual (not the lossy anchor, not a blocker for this verdict)

Anchor 4 (`err.http.response.client_error.not_found`) is retained with an in-code
UNVERIFIED caveat for the custom adhoc connector (workato_api_connector_748504)
— accepted-risk with skip telemetry making every firing auditable. Poll-404
terminal-success carries the in-code caveat that "record gone = committed" is
UNPROVEN and must flip to deferral if the first real occurrence shows an
uncommitted page. Both are documented inside the shipped code, per Josh's
approved amendment scope.

### 5. Corroborating record

- Prior reconciliation (~/.claude/knowledge/cortex/investigations/bsys-29519-v43-dissent-disposition.md,
  2026-10-17): v44 (Oct 14 13:11 PT, 40 min after v43) already shipped both
  material fixes; confirmed absent from v45. This investigation independently
  re-pulled v45 and re-executed the classifier — same conclusion, fresh evidence.
- Cadence log (~/.claude/knowledge/projects/hr-genie/BSYS-29519-collector-cadence-log.md):
  "v44 dissent-review corrections... (D1) 404-adjacency anchor tightened from
  20-char window (kills 'after 404 ms: host not found'...); EXACT shipped v44
  code executed locally: 11/11 cases incl. all dissenter adversarial inputs."

## What was NOT verified

- No live job trace of a real poll-404 firing (no real occurrence has fired in
  job history — the residual caveat stands).
- Whether the BSYS-29498 prod-path package itself embeds this v45 code (the
  package was ZIP-verified at re-export per the registry row; this investigation
  verified the live dev recipe the export was taken from, not the prod import —
  prod currently ships collector v40 per cortex questions.jsonl 2026-10-20T00:09Z).
- The standing red-team verdict gap for BSYS-29519 (zero verdicts in
  knowledge/redteam/ as of the Oct-17 disposition) is unchanged by this verdict
  and still gates any production move.

Investigator: headless read-only session (kimi-k3), 2026-10-20.
