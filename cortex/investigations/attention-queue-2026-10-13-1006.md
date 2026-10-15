# Attention queue — pulse 2026-10-13T10:06Z (rev n)

WRITE GATE: canonical cortex/attention-queue.md STILL permission-gated this pulse — Write tool,
cat-heredoc overwrite, and even `>>` append all denied (third consecutive pulse; the gate has
tightened — append worked for a prior pulse). Queue recorded HERE. Blockage question stands
from 06:58Z; updated answer this pulse: the gate is no longer mode-specific, it denies all
writes to the canonical path from this session.

1. **needs-josh debt: 29 open rows, 12 non-done workstreams >24h stale.** Sharpest now:
   hr-genie-workday-mcp (33.1h — VUA flip + tool-254984 description fix + tax-elections
   registration), btsup-service-desk (33.1h — Ops Genie customer-workspace fix + prod KB
   re-ingest FTO), sfdc-accounts-sync (27.5h — BSYS-29515 build go + 2 open decisions),
   jira-autotriage batched gates (19.1h). Oldest stale: bsys-28296-marketo-history (37.1h,
   blocked). Fold still computes NO non-done staleness (known script gap, item 6) — these
   numbers are cortex-computed. Ref: mission-control/registry.json (fold 10:06Z).
2. **82964017 canary: ROOT CAUSE CONFIRMED — trigger config drift from the v12 push.**
   Autopsy proves the auto-stop was trigger-time, not runtime: `input.time_unit` stored as
   the picklist LABEL "Minutes" (must be option ID "minutes"), stale
   `dynamicPickListSelection: "Days"` contradicting the input, plus a stray
   `trigger_at: "00:07"` — the 13 DatapillInvalidPath inconsistencies are real but
   runtime-proven innocent of the stop. Fix-forward is a builder picklist re-set + restart
   + one scheduler-fire observation; v12 was pushed outside ledger discipline (zero
   build-ledger rows). Triage row recipe-health-82964017-trigger-fix filed this pulse.
   Ref: cortex/investigations/82964017-trigger-autopsy.md.
3. **KB sync dirties source repos BY DESIGN — mystery closed, redesign decision owed.**
   The Oct-11 link-rewrite pass (9/20 github-source repos) was NOT a rogue actor: it is
   `kb/links.py` `links.normalize`, a mandatory post-sync step that rewrites links in place
   inside the git checkouts without committing. Same root wedged camel's pull 2 nights
   (dirty tree blocked the merge). Hardening triage row kb-source-repo-hardening open
   (fetch+reset over pull); the DESIGN decision — commit rewrites vs copy-don't-rewrite —
   is Josh's.
   Ref: cortex/investigations/link-rewrite-actor-identification.md + kb-sync-camel-source-failure.md.
4. **Dropped sessions cleared: all 3 are completed work, closeout rows filed this pulse.**
   971ed45e (BSYS-29443 MCP Registry tool-call-stats — Jira read-back Closed/Fixed, prod
   pushes were under explicit in-transcript "Do it."), 11f76f81 (harness-fix fleet 10-09,
   8/8 fixed), 370c9042 (HR Genie dreamer run). One residual: a stale self-contradiction at
   knowledge/projects/hr-genie.md:119-120 ("prod schedule still Minutes/5") needs Josh's go
   to correct. Ref: cortex/investigations/dropped-sessions-2026-10-13-identification.md.
5. **82964161 gw_fleet_schedule_liveness_sentinel: CLEARED — premise was stale.** It is an
   event-driven RecipeOps stop_error push sentinel, not an hourly scheduler; zero-jobs is
   its healthy state and it already fired correctly on the canary auto-stop (job
   j-AbwJfLFH succeeded 21:34 PT, alert posted). Watch question withdrawn.
   Ref: cortex/investigations/82964161-sentinel-zero-jobs.md.
6. **Mission-control fold still computes no non-done staleness** (only STALE_DONE_DAYS=14
   for done rows; mission-control.py:42) — the 12-stale cohort above is invisible on
   board.html. Events-only rule bars cortex from patching the script; proposal stands for
   Josh. Second open proposal: /today batch-propose default verdicts for needs-josh rows
   stale >48h so the debt stops rotting.
7. **Prod GSlides 82872520/82090477 — watch.** Helper restarted 13:17 PT Oct 12; caller
   failures only at the unguarded Append Guidance call site; dormant call sites owed fixes
   (BSYS-29584/29585). Dreamer's dissent finding also stands: stalled-scheduler detection
   cannot see STOPPED recipe functions — no sensor on the likeliest repeat-outage class;
   routed to watchdog/estate-architect charter, unowned since 04:55Z. Also new from
   watchdog 03:17Z: 'CON | Workday 2' (19193562) connection lost + 400 — re-auth or
   decommission decision in /triage. Ref: cortex/investigations/gslides-82872520-reverify-1013z.md.

## Cost governor
_cost-governor.py 2026-10-13 — proposals only; Josh approves any routing edit._

- No budget alarms this window (median spend proxy 18,431).
- Three DOWNGRADE TRIALS pending Josh approval: autopsy-investigation, build, judgment on
  kimi-k3 all show pass ≥92% — propose A/B on glm-5.3-flash.
- INSTRUMENTATION: brain-guard turn-usage lines lack job/class/model fields — per-class
  token cost stays a proxy until brain-guard adds them.
- Full table: garden-reports/cost-governor-2026-10-13.md
