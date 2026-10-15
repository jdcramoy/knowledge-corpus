# Attention queue — pulse 2026-10-13T18:32Z

1. **needs-josh debt: 32 open rows, 20 workstreams >24h stale — debt still growing (was 25/14 two pulses ago).**
   Sharpest fresh decisions: consumer-endpoints (calendar-fallback B vs hold for CJ, 0.9h),
   harness-dashboards-mcp (OAuth client, 2.0h), session-shadow (go-ahead on plist interpreter
   fix, 3.1h — see item 4), jira-autotriage (BTSUP-76729 prod promotion + BTSUP-78227
   Slack re-attach go/no-go, 5.0h), gws-mutation-chain-canary (fix-forward on 82964017, 10.3h).
   Oldest stale: bsys-28296-marketo-history 45.6h blocked on Marketo prod import. Ref:
   mission-control/registry.json (fold 18:32Z).
2. **Prod-write gate breached twice on 10-12 — actor audit verdict (NEW, high governance weight).**
   The 82872520 audit (cortex/investigations/82872520-restart-actor-audit.md, 13:45 PT) confirms:
   Josh's 13:01 PT recovery restart was manual/clean, but (a) session `jira-sweep-1012` stopped
   prod 82872520 + 16 folder siblings at 07:48-07:55 PT under a BLANKET delegation — causing the
   multi-hour outage — and (b) hotfix session `a8411ab8` stop+started the live prod recipe
   mid-import-probe (13:17/13:17 PT) with zero per-action confirmation. Both fired under Josh's
   CLI token, so audit-log actor names cannot discriminate human vs agent. Josh decision owed:
   enforcement/routing fix so prod stop/start via `wt --profile josh-prod` needs first-hand
   confirmation. Triage row filed (guard-prod-cli-stop-start).
3. **grc-gdpr-emails: prod-facing in-flight row 35.9h stale, no closeout — possible unfinished
   prod state (constitutional row 1).** Blank-messages-for-long-emails defect on a customer-facing
   GDPR channel; live-state lookup dispatched 14:20Z, results not yet harvested. Josh should
   verify with prod MCP attached before anything else touches it. Ref:
   cortex/investigations/grc-gdpr-emails-prod-state.md.
4. **session-shadow blind 19h: now-file frozen 2026-10-12T23:27:58Z.** Exit-78 root cause
   confirmed — Homebrew's Oct-12 19:29 operation unlinked `/opt/homebrew/bin/python3`; plist
   hardcodes it; script is healthy. Repair is one plist edit, gated on Josh (needs-josh 3.1h).
   Until fixed, the pulse's live-session check cannot run. Ref:
   cortex/investigations/session-shadow-exit78.md.
5. **Registry hygiene: double-registered workstreams inflate Josh's needs-josh count.**
   Confirmed pair (stale-jira-review + jira-stale-review, identical session); how many others is
   unmeasured — lookup dispatch launched this pulse (registry-dup-sweep). Triage row open
   (registry-dupe-jira-stale-review); dedupe edit is Josh/orchestrator-side (events-only rule).
6. **82964017 gw_semantic_mutation_chain_canary still down; fix-forward gated on Josh 10.3h.**
   Trigger config drift root-caused; canary cannot bark for itself while stopped. Also open:
   should the regression nightly exclude 82272814 (false-FAIL by construction) until registry-
   hygiene verdicts land (Josh + regression owner). Ref: cortex/investigations/82964017-
   trigger-autopsy.md.
7. **Cost governor: three downgrade trials awaiting Josh (autopsy-investigation, build, judgment
   off kimi-k3 → glm-5.3-flash A/B), plus brain-guard instrumentation ask (job+model fields on
   turn-usage lines) so per-class cost stops being a proxy.** No budget alarms this window.
   Ref: garden-reports/cost-governor-2026-10-13.md.

## Mission-control pulse note (18:32Z)

fold + board run clean (94 workstreams). The fold computes NO staleness for non-done rows —
staleness above was computed externally (cortex, registry.json direct read). Proposal to add a
non-done staleness pass to fold remains with Josh (cortex cannot edit the script, events-only).

## Prior pointer

Pulse 2026-10-13T11:15Z items carried: grc-gdpr-emails (now item 3), needs-josh debt (item 1),
82964017 canary (item 6). Full prior queue: cortex/investigations/attention-queue-2026-10-13-1115.md
