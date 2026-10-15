# Harness cost/benefit analysis — 2026-10-11

First end-to-end ROI picture, mined from live telemetry (4 parallel harvests: usage ledger, fleet plists, value/accuracy ledgers, gateway pricing research). Sources: garden-reports/usage-ledger.jsonl (5 days, 2026-10-07→11), 44 launchd plists, value-ledger.jsonl, cost-governor-2026-10-11.md, claim-verification-2026-10-11.md, model-gateway-playbook.md, workato-platform.md.

## Cost: what it takes to run

**Token volume (5 measured days, 1,542 turns):**

| day | turns | uncached in | cache read | output |
|---|---|---|---|---|
| 10-07 | 178 | 21.8M | 374M | 0.67M |
| 10-08 | 301 | 103.6M | 2,261M | 1.29M |
| 10-09 | 316 | 99.8M | 1,814M | 1.61M |
| 10-10 | 466 | 177.3M | 3,458M | 2.90M |
| 10-11 | 281 | 122.8M | 2,209M | 4.05M |
| total | 1,542 | 525.4M | 10,116M | 16.3M |

- Cache hit rate **95.1%** of prompt tokens; median turn = 175k in / 4.5k out; ~105 cold turns/wk (~110k full-prefix each, 81% of which is MCP tool definitions).
- Daily run-rate ≈ **2.13B tokens/day** (105M uncached + 2,023M cached + 3.3M out). Output/day grew 6x in the week (0.67M→4.05M).
- **Dollar cost: not directly billable.** Traffic runs on the internal AI gateway (company-provided, default budget ~$800/mo, soft/hard caps pending, no public pricing, per-token attribution approximate). Market-equivalent scenarios (cache at 10% of input, output at 4x input): ~$80/day at flash-tier list, ~$320/day at $1/M input — i.e. roughly **$2.4k-$10k/mo market-equivalent**, which only fits a company budget because the gateway doesn't bill at market and caching is at 95%.
- **Fleet schedule: 44 jobs, ~3,000 runs/day** of which ~2,850 are zero-LLM poller ticks (session-shadow, command-watcher) and ~77/day are LLM-backed claude spawns (cortex 24, dream-mini 24, jira-triage 12, rest daily/weekly). 22 of 44 jobs are zero-LLM by design.
- **Workato-side cost surface: unmeasured.** ~154 dev clock recipes + fleet-managed recipes burn tasks; the cost-heatmap pipeline returned zeros on its run. Known burn incidents (17k junk jobs/day bridge, 4k tasks/hr app flood) were caught and guarded.

## Benefit: what it returns

- **Value ledger (5 days): 197 rows, 450.5 heuristic engineering-hours returned** — build 192h, jira 102.5h, harness 64h, cortex 42h. Hours are class heuristics, conservative by policy; zero human note rows exist yet, so incident-prevented value is UNDERSTATED to the floor.
- **Triage loop: 138 outcomes, 107 accepted-or-built**, 15 rejected. Dreamer precision gate caught 2 false alarms before any build cost.
- **Concrete saves:** prod mass job-shutdown on 11 HR Genie recipes correctly blamed on platform worker backlog (averted a wrong recipe-fix cycle on live HR flows); BSYS-29418 symptom→packaged promotion in 48h; three collector failure classes root-caused, fixed, and canonized (49 regression fixtures); zombie-running-recipe delete trap canonized.
- **Throughput:** ~170-180 sessions/day touched; 10 harness improvements built the same day as the adversarial review (10-11); BSYS-29508 + BSYS-28296 prod fixes same-day (10-11).

## Accuracy

- Evidence agent claim audit: **17/18 verified, 0 FALSE** (one unverifiable, scope).
- Claim ledger: 13 active, only 1 live-probe verified — 12 unverified-but-active is the overconfidence surface.
- Calibration: mean Brier **0.1267 but n=3** resolved (21/24 predictions open) — underpowered, weakest surface.
- Regression nightly 11 pass / 4 fail / 3 errors — test fleet itself immature (61%).
- MCP call error rate 9.7% (AIRO server 10.9%), 10,356 calls, 60MB payloads; recipe-builder traffic = 64% of calls.

## Verdict

ROI is strongly positive on value delivered: ~90h/day heuristic hours returned plus real incident catches. Direct dollars run through the internal gateway budget — the measured actual is $3,371/7d (see addendum: 91% of it Workato project delivery, the harness itself ~$290/wk all-in), settling toward ~$850-1,100/wk as the build spike completes. The economics flip fragile if the gateway ever chargebacks at market: at $1/M-input rates the run-rate (~$320/day) is ~4x the $800/mo default budget, and output is growing 6x/week. Biggest levers, in order:

1. **Instrument first**: add job/class/model fields to brain-guard turn-usage lines (cost-governor already proposed) — without it cost attribution stays a byte proxy.
2. **Kill dream-mini's hourly LLM spawn** (24/day) or reduce to 2-4/day — it overlaps the nightly dreamer; biggest single spawn reduction.
3. **Resolve the kimi→glm downgrade A/B trials** (build/judgment classes, 100% pass on kimi, highest cost).
4. **Prune the cold-start prefix**: 81% of the ~110k cold prefix is MCP tool definitions across 17 servers; pruning cuts every new session's uncached cost.
5. Merge the docs-watch double and stagger the 03:17 collisions (hygiene, small).

Nothing unverified beyond what's flagged: dollar pricing is unpublished (scenarios only), Workato task burn is unmeasured (empty heatmap), and interactive-vs-fleet token split is unknown (no session-id in the ledger).

## Addendum: $3,371/7d segmentation (same day, evening)

Josh reported the gateway's actual 7-day spend: $3,371. Full session-level extraction (333 sessions, 72,277 turns, 752.8M uncached in + 16.8B cache-read + 19.5M out) allocated it by billed-equivalent tokens (cache@10%, output@4x — implied rate $1.34/M, consistent with the kimi ~$1/M effective anchor):

| bucket | sessions | $/7d | share | what it is |
|---|---|---|---|---|
| WORKATO project work | 151 | **$3,082** | 91.4% | GW Semantic MCP builds, otto port, HR Genie/estate builds & ops — the actual delivery work |
| HARNESS improvement (interactive) | 51 | **$154** | 4.6% | meta-work: reviews, harness builds, cost analysis sessions |
| FLEET run (steady state) | 131 | **$135** | 4.0% | all 22 LLM-backed scheduled jobs; cortex $53 + jira-triage $45 = 72% of it |

Key findings:
- **The harness is NOT the cost driver.** Harness build + run combined = ~$290/wk (8.6%). 91% of spend is Workato project delivery — the "setup cost" Josh suspected is real but it's Workato-build setup, not harness setup.
- **Concentration: 26 of 333 sessions = 80% of all tokens.** Top session $261 (GW Semantic deck-creation debugging, 1.22B cache-read). Long resumed sessions re-hydrating >1B-token contexts are the cost class to manage.
- **Daily trend is falling as builds complete:** Oct 6 = $1,024 (all Workato) → Oct 8 $596 → Oct 9-11 ≈ $137-220/day. Days 10-02→10-08 carried ~$2.7k of the week (build spike); the settling steady state is roughly fleet $20/day + interactive ops ~$100-140/day ≈ **$850-1,100/wk run-rate**.
- Caveats: bucket classification is cwd+keyword heuristic (workbench-main non-harness sessions include general ops; this analysis session itself is in HARNESS-BUILD); $-allocation assumes uniform $/billed-equiv across models — fleet runs the cheapest lane (glm-5.3-flash), so its true dollar share is even lower than 4%; sessions with old first-timestamps are resumed sessions whose spend lands in recent days (daily table approximate for those); extraction covers local Claude Code only.
