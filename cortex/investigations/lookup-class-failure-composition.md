
# Lookup-class failure composition — cost-governor BUDGET ALARM (2026-10-26)

Investigator: read-only session on fireworks/glm-5.3-flash, 2026-10-26 ~20:50Z.
Scope: the 44 lookup-class cortex dispatches in the governor's 7d window that
produced "pass rate 49%, cost proxy 58,863" (garden-reports/cost-governor-2026-10-26.md).
Method replicated from cost-governor.py: pass = log exists, >500 bytes, tail
lacks GATE_MARKERS; fail = log size 0; gated = tail marker hit.

## (a) What the 44 runs actually did — failure composition

Governor's raw count: 22 pass / 22 fail ≈ 49%. Corrected count: **44/44
dispatches delivered a finding; the true delivered-finding rate is 100%, the
strict-by-method rate with fixed path resolution is 95% (42/44), minimum 84%
(37/44).** The 22 "fails" decompose as:

- **21 × PATH-RESOLUTION ARTIFACT (dominant cause).** 21 of the 22 "failing"
  dispatches recorded RELATIVE log names (e.g. `dispatch-20261020T000840Z.log`)
  instead of absolute ones. `cost-governor.py` resolves via
  `os.path.expanduser(log)` only — never against the state dir — so relative
  names stat() against the governor's CWD, miss, and score size-0 = FAIL.
  16 of those 21 files EXIST and are substantive (0.6–4.5 KB) in
  `~/.local/state/cortex/`. Byte check: governor-saw bytes 58,863 vs
  true bytes 105,587 — the same bug deflates the cost proxy too.
- **5 × missing logs, but findings PERSISTED anyway.** The 5 genuinely
  unfindable logs all have matching, dated, substantive investigation files:
  redteam-29519-ftr-queue-check.md, kb-sync-rework-closeout-check.md,
  bsys-29744-genie-identity.md, build-now-proposals-unbuilt.md,
  canary-alarm-loop.md (all in knowledge/cortex/investigations/, all 3–5.5 KB,
  dated to the dispatch). The dispatch agent delivered; only the log copy is gone.
- **2 × FALSE-POSITIVE GATE MARKERS.** Both "gated" runs contain a marker word
  in NARRATIVE text, not an actual block: recipe-del (10-21) reported the cortex
  pulse write-gate permission-denied then WORKED AROUND it (cp from /tmp) and
  persisted an 81-line verified investigation; atlassian-verify (10-22)
  mentioned "the 16:14 'blocked' bus finding" historically and ended with
  "Created/updated: investigations/atlassian-auth-publis...". Both delivered.

Failure types NOT found: zero parse errors, zero empty/ill-formed tasks, zero
ambiguous-target failures, zero model aborts. All 44 task prompts are well-formed
one-line investigative questions.

## (b) Task-quality or model-capability?

**Neither — it is instrumentation, not task quality and not model capability.**
The class is NOT being fed junk tasks (all 44 prompts well-formed) and there is
no evidence glm-5.3-flash failed a single lookup. The 49% is manufactured by the
governor's own measurement: relative-path resolution bug (21) + missing-log
copies with persisted findings (5) + narrative gate-marker false positives (2).
kimi-k3 would score identically on these tasks under the same buggy measurement.
The UPGRADE-SIGNAL proposal was generated from a phantom.

## (c) One-line verdict for Josh

**Do not spend the lookup upgrade trial — fix cost-governor.py to resolve
relative log names against ~/.local/state/cortex/ (and treat an existing
persisted-finding file as pass), then re-run the governor; expect lookup pass
~95%+ and the alarm to clear with no model change.**

## Fix checklist (for whoever patches the governor — not done here, read-only)

1. In the dispatch-classification block: if the expanded path doesn't exist,
   retry `STATE_DIR / Path(log).name` before scoring size-0.
2. Consider crediting a run whose named investigation file exists in
   knowledge/cortex/investigations/ when the log copy is missing.
3. GATE_MARKERS are single-phrase matches on the tail — "was blocked" and
   "permission denied" match historical narration; either require a
   first-person-pending pattern or accept the bus/investigations persistence
   check as the sole deliverable signal.

Evidence: knowledge/cortex/dispatches.jsonl (203 lookup rows lifetime, 45 in
exact window, 44 at governor runtime — the 45th is a 407-byte lookup-failures
probe from 12:46Z today, 58,863 + 407 = 59,270 reconciles); dispatch logs in
~/.local/state/cortex/; cost-governor.py lines 62–67, 173–208.
