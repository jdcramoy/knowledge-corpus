# BSYS-29519 v43 classifier dissent — disposition lookup (READ-ONLY)

Investigated: 2026-10-17 ~20:00Z. Dispatched by cortex pulse 19:52Z (thread
bsys-29519-v43-dissent-disposition-lookup) to reconcile the
dissent-bsys-29519-v43-classifier verdicts against live dev recipe 82862205
state. No writes made to any asset.

## 1. Dissent thread state (gossip bus, dissenter.jsonl)

Thread `dissent-bsys-29519-v43-classifier` — 3 material + 1 cosmetic + 1 note
findings (entries carry no ts field; cortex 09:27:35Z post treated them as
filed "this morning", ~07:26Z Oct 17):

1. **MATERIAL — anchor-2 regex**: `/\b404\b[^0-9\n]{0,20}\bnot[ _-]?found\b/`
   reintroduces the v42 data-loss mode in narrowed form (20-char window lets
   "after 404 ms: host not found" / "port 404 - host not found" / "read 404
   bytes; record not found" classify as permanent conversation_gone_404 →
   watermark advance = silent loss).
2. **MATERIAL — branch ordering**: lossy (terminal-success/poll-404) branch
   tested FIRST; input "page_commit_async_job_failed: failed=0 timed_out=1
   detail: poll status 404" satisfies both branches and would take the lossy one.
3. **MATERIAL — 404 anchor semantics**: `err.http.response.client_error.not_found`
   is documented for the PLAIN HTTP connector, not this recipe's custom adhoc
   connector (workato_api_connector_748504).
4. **COSMETIC** — "I reproduced that loss locally" overstates (reproduced the
   misclassification output, not the loss).
5. **NOTE** — what survives (downcase-before-match defeats case attacks).
   Plus: v42's ~52.5h live exposure window flagged unaudited.

## 2. Live recipe state (wt recipes get 82862205, read-only)

- Name: REC | HR Genie | Conversation Event Collector. **Running: true**,
  last job 2026-10-17T12:38 PT. **version_no: 45**.
- Version history: v42 = Oct 12 07:58 PT · v43 = Oct 14 12:31 PT ·
  **v44 = Oct 14 13:11 PT** · **v45 = Oct 16 00:08 PT** (all Joshua Cramoy,
  no comments).

**Verdict: the draft is NOT unchanged — both material code defects are absent
from the live v45 code.** The dissent attacked the v43-era draft text; v44
pushed 40 minutes after v43 on Oct 14 already corrected it, per the shipped
classifier Ruby read from the live recipe code:

- **Finding 1 (anchor-2 regex): FIXED.** Live anchor-2 is
  `/\b404\b[ ]?\(?(?:not[ _-]?found)\b/` — adjacency-only (optional single
  space + optional paren), NOT the 20-char window. The code comment explicitly
  documents that "read 404 bytes; record not found" and "after 404 ms: host
  not found" (transient shapes) do NOT match and re-raise. The dissenter's
  three attack strings no longer classify as permanent.
- **Finding 2 (lossy-first ordering): FIXED.** Live branch order: (1)
  wait-timeout (`page_commit_async_job_failed` + `failed=0` + `timed_out>=1`)
  → permanent=**false**, page UNCOMMITTED, watermark retries — tested FIRST;
  (2) poll-404 terminal; (3) budget-exhausted; (4) structural http_404; (5)
  else re-raise. A wait-timeout can no longer take a permanent path.
- **Finding 3 (404 anchor semantics): PARTIALLY ADDRESSED — documented
  residual.** The `err.http.response.client_error.not_found` include is
  retained as one of four anchors, but the code comment flags it "UNVERIFIED
  for this recipe's custom adhoc connector, whose catch-message shape has
  never fired in job history". Accepted-risk with audit trail (skip telemetry
  makes every firing auditable), not a code fix. The poll-404 terminal-success
  branch itself carries the caveat "record gone = committed is UNPROVEN; if
  the first real occurrence shows an uncommitted page, this branch must flip
  to deferral" — i.e. the dissenter's Branch-1 premise objection is
  acknowledged in-code and mitigated by telemetry, per Josh's approved
  amendment scope.
- **v42 exposure window (52.5h): AUDITED** per the registry row — "a backwards
  audit of the v42 window (179 runs classified; the two deepest backlog drains
  trace-audited clean)".

## 3. Disposition surfaces since 09:26Z today

- **Bus**: cortex pulses 17:45Z and 18:41Z Oct 17 still describe the "v43
  draft" as dissenter-blocked and re-verify the red-team gap — they have NOT
  registered that v44/v45 already ship the corrections. The 19:44:16Z lookup
  dispatch (this investigation) is the only reconciliation action on record.
- **Registry** (`mission-control/registry.json`, workstream hr-genie-collector,
  ts 2026-10-14T20:44:27Z): the v44 build row IS the substantive disposition —
  "An adversarial review broke the first push (v43) before it was announced;
  v44 corrects all four material defects... Proven with 22 local cases run
  against the exact shipped code, a full hot-swap..., a green forced run
  (j-AbxCkDkG-L9KDfJ-CD), and a backwards audit of the v42 window." Row state
  in-flight; needs: none — 24h clean-cadence clock accruing.
- **Triage queue**: no new or updated 29519 row since 09:26Z; all 29519 rows
  predate the dissent (latest decisions 2026-10-14/16). No triage card closes
  the dissent thread.

## Bottom line

**The 3 dissenter findings have no EXPLICIT disposition post (bus/triage) since
09:26Z, but they are SUBSTANTIVELY disposed of in the shipped code:** findings
1 and 2 were fixed in v44 (Oct 14 13:11 PT, 40 min after v43) and confirmed
absent from live v45; finding 3 survives as a documented, telemetry-auditable
residual inside the approved amendment scope. The open governance item is not
the classifier — it is (a) the cortex pulses' stale "v43 draft still blocked"
claim, and (b) the standing red-team verdict gap for BSYS-29519 (zero verdicts
in knowledge/redteam/ as of the 18:55Z re-verify) which must close before any
DR/production move.

Investigator: read-only lookup session (glm-5.3-flash), 2026-10-17.
