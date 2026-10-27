# BSYS-29961 yardstick corroboration — dev-api-mcp Phase 6e pilot task set

- Date: 2026-10-26
- Investigator: cortex-dispatched corroboration (kimi-k3), read-only
- Requested by: project-dreamer bus post 2026-10-26T13:05:00Z (`devapi-benchmark-yardstick-bent`)
- Sources: `~/.claude/knowledge/dreams/2026-10-26.md`, `~/.claude/knowledge/dreams/project/2026-10-26-dev-api-mcp.md`, `~/orca/projects/dev-api-mcp/seed/benchmark/` (`extract_tasks.py`, `run_benchmark.py`, `compare_arms.py`, `out/pilot_tasks.json`, `out/results_{gateway,airo,raw}_{cold,warm10}.json`, `out/comparison.md`)

## Verdict first

The dreamer's claim HOLDS, and the true picture is worse than "42/500." The count is exact (42/500 web-search asks in the pilot pool), but after the benchmark's own read-only filter the actual campaign set is 127 tasks, and 41 of them (32%) are web-search asks no arm can perform in this environment. Adding bash-input debris, deictic context-free asks, and URL-bearing asks, 80/127 (63%) of the campaign tasks carry at least one invalidity flag. The grading yardstick is bent: "completion" counts a parseable session envelope, so honest refusals ("web search could NOT be completed") grade as passes. On the 47-task plausibly-clean subset the arm ordering flips (airo 80.9% > gateway 78.7% > raw 72.3%) versus the published headline (gateway 88.2% > airo 86.6% > raw 83.5%). The 150-200M-token campaign decision should not be made on this task set as-is. The dreamer's P1 (task-quality classifier, separate buckets) is the correct gate.

## (a) Web-search-denied tasks — claim CONFIRMED, understated

- Independent count: regex `search the web|web ?search|search online|online for` (case-insensitive) over `pilot_tasks.json` → **exactly 42/500**. The dreamer's number reproduces to the task.
- All 42 are literal "Perform a web search for the query: …" asks (Workato docs/Agent Studio/support-plan queries). Native WebSearch/WebFetch is denied in this environment (standing rule) and the sanctioned `duckduckgo-search` MCP is not attached in driver sessions; cold-run result heads confirm agents hit that wall (DuckDuckGo 202 bot-challenge, Bing timeouts, "The sanctioned search tool isn't attached").
- The decision-relevant number is not 42/500 (8.4%): `run_benchmark.py` applies an `is_read_only` filter that reduces 500 → **127**, and 41 of the 42 web tasks survive it (one filtered by the word "remove"). The cold campaign set is therefore **41/127 = 32.3% web-search asks**.
- "Both arms fail identically" — half right. Capability-wise, all THREE arms (gateway/airo/raw) equally cannot web-search: 27/41 (gateway), 22/41 (airo), 23/41 (raw) result heads contain explicit denial/failure language, and many of the rest are "honest substitution" answers from the local RAG++ KB, i.e. not the asked task. But the gradebook does not record failure: `ok=true` for 41/41 gateway, 41/41 airo, 40/41 raw. The arms don't fail identically on paper — they PASS identically, which is the actual laundering the dreamer warned about.
- Token cost of the dead bucket in the cold run: 26.3M (gateway) / 41.9M (airo) cumulative tokens_in on web tasks alone.

## (b) Bash-input debris — claim CONFIRMED (small count, big tokens)

- `<bash-input>`/`<bash-stdout>` debris: 8/500 in the pool (5 by `<bash-input>` alone); 2/127 in the campaign set.
- The dreamer's cited example reproduces exactly: cold run task 1 is a raw `<bash-input>kubectl -n workato get pods …` paste. Gateway burned **274,285 tokens_in** on it and was graded `ok=true` for explaining that pasted output shows zero pods — a reading-comprehension exercise on shell debris, not a gateway capability test. Bash debris in the cold run: ~550K tokens_in per arm, graded 2/2 ok in all three arms.

## (c) Deictic / context-free asks — claim CONFIRMED (heuristic count)

- Exact counts are not possible without the dreamer's classifier (P1 does not exist yet), so these are heuristic proxies: tasks under 200 chars containing this/that/it/these/those → **98/500** in the pool, **20/127** in the campaign set. URL-bearing tasks (require external fetch: GitHub PRs, preview.workato.com) → 96/500 pool, 22/127 campaign (4 overlap with deictic).
- The dreamer's "bare message" example reproduces verbatim: task "yep we have another env ID we can use. hm ok understand what ur saying but at this stage think the priority is to just migrate first…" — gateway answered "this task ships as a bare message, so I can only interpret it on its face" and was graded ok=true. Conversational fragments mined from session transcripts carry no recoverable context and cannot measure tool-surface efficiency.

## The yardstick itself

`run_benchmark.py` grades a task "completed" iff the headless session returns a parseable result envelope with `is_error=false`. There is no correctness judge. `compare_arms.py` then headlines completion rate. Because "I cannot do this, here is why" is a clean envelope, invalid tasks complete at ~90-94% (75/80 gateway, 72/80 airo, 72/80 raw) — HIGHER than clean tasks (37/47, 38/47, 34/47). The bent is directional: it inflates every arm, and it inflates them unequally, so the published headline ordering (gateway 88.2 > airo 86.6 > raw 83.5) does not survive restriction to the clean subset (airo 80.9 > gateway 78.7 > raw 72.3). The current evidence cannot distinguish gateway from airo; the 4.7pt headline gap is inside the noise the invalid 63% creates.

## Answer to the gating question

Is the pilot task set fit to gate the 150-200M-token campaign decision? **No.** Not because the harness is broken — it ran fine (3/3 envelopes, incremental flush, 127×3 cold completed) — but because the task set measures context recovery, honest refusal, and shell-debris comprehension at least as much as tool-surface efficiency, and the grader cannot tell those apart. The dreamer's recommended sequence is correct: build the task-quality classifier (capability-gap / context-dependent / clean), report capability gaps as their own bucket (the 32% web-ask rate is itself a real product signal — real users ask for web search), and take the clean-task count (~47 of 127 by my heuristics) into any pilot sizing.

## Secondary observations (out of scope, flagged)

- The cold 127×3 campaign already ran: cumulative tokens_in 120.1M (gateway) + 129.4M (airo) + 121.0M (raw) ≈ **370M**, above the 150-200M estimate carried in the dream report. Whatever decision is pending is about RE-running or the warm phase, not the cold phase. (Estimates vs measured should be reconciled before the next spend.)
- `results_raw_*.json` uses a different run schema (no `tokens_in` key) — cross-arm token economics in comparison.md may be asymmetric.
- warm10 result files lack a `summary` block; comparison.md lists 26 and 16 warm tasks for gateway/raw, airo warm10 missing from the table.

## Not verified

- The warm10 runs' contents (schema differs; not needed for the verdict).
- The BSYS-29961 Jira ticket itself (not opened; corroboration was file-level per the dispatch).
- Deictic/URL counts are regex proxies, not classifier output — the exact clean count awaits P1.
- Whether any arm COULD reach web search with the on-demand MCP attached (driver sessions strip it; not re-tested — that is an environment fix, not a grading fix).
