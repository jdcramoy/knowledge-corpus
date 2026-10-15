# Spec: AI-spend ROI framework + shipped-work ledger + dashboard

Written: 2026-10-11. Owner: josh (session). Status: BUILDING.

## Goal

Give Josh a leadership-defensible answer to "the AI spend is up — what did it buy?"
in the form: cost in ($) → Workato work shipped (tickets, story points, assets) out,
with a business-value thesis per work block, and velocity evidence (before/after AI,
me vs team baseline).

## Scope IN

- Shipped-work ledger keyed to Jira BSYS: tickets that went through Final Technical
  Review with manifest + source/destination workspace fields filled = shipped.
- Weekly/monthly rolls: shipped tickets, story points (1pt ≈ 1 developer day),
  per work block (epic), per builder class (josh vs team aggregate).
- Cost ledger: gateway $ figure (Josh supplies, authoritative) + local telemetry
  attribution (usage-ledger.jsonl session→project buckets, harness-cost-benefit
  methodology made repeatable).
- Value thesis per work block (epic-level, NOT per ticket): LLM-drafted from ticket
  content + manifests, Josh-approved before it reaches any leadership artifact.
- Velocity analysis: resolved tickets + points per week per builder, full BSYS
  history; inflection date picked BY THE DATA, then stated.
- Peer framing (Josh ruling 2026-10-11): TWO-TIER. Leadership artifact shows
  "Team baseline (aggregate)" vs "You (AI-augmented)" only. Internal dashboard
  keeps named per-builder rows (Josh, [requester], [colleague]).
- Local HTML dashboard (board.html pattern) + monthly one-pager generator
  (exportable to deck/Confluence).
- Fleet job for weekly derive + monthly report roll.

## Scope OUT

- Real dollar business-value accounting (no data exists; heuristic + thesis only).
- Per-ticket value theses (noise; epic-level only).
- Any Jira ticket writes beyond read (no comments, no edits).
- Any Workato recipe edits or prod anything.
- Named peers in the leadership-facing artifact (two-tier rule above).

## Done criteria (objectively verifiable)

- [ ] `knowledge/roi/data/shipped-ledger.jsonl` populated from live Jira queries
      with manifest-era shipped tickets (ticket, builder, points, dates, epic,
      manifest fields).
- [ ] `knowledge/roi/data/cost-ledger.jsonl` populated: weekly gateway $ (Josh's
      numbers + telemetry estimate fallback) + per-bucket attribution.
- [ ] Velocity curve computed with data-picked inflection date, written to
      `knowledge/roi/data/velocity.json` — the inflection is cited, not assumed.
- [ ] Dashboard renders locally (roi/board.html) with: cost in vs work out,
      velocity before/after, team-vs-you, work-block theses.
- [ ] `scripts/roi/one-pager.py` generates the monthly one-pager (markdown)
      suitable for paste into a deck.
- [ ] Framework doc `knowledge/roi/framework.md`: the value heuristic, the
      conversion (points → engineer-day → loaded-rate $), the defense narrative,
      known weaknesses stated honestly.
- [ ] Weekly/monthly fleet job defined (config, not necessarily armed — arming
      is Josh's).

## Design gate (prior art — extend, don't rebuild)

| Existing | Reused for |
|---|---|
| `garden-reports/usage-ledger.jsonl` (14.5k rows) | cost attribution telemetry |
| `reviews/harness-cost-benefit-2026-10-11.md` ($3,371 7d segmentation) | methodology for session→bucket costing, made repeatable |
| `value-ledger.py` / `value-report.py` | capability-level hours (internal); new ROI layer is leadership-facing and Jira-keyed — separate files under knowledge/roi/, cross-linked |
| mission-control registry | session closeouts feed the work narrative |
| ops-visibility dashboard + board.html | dashboard rendering pattern |

Delta: nothing existing is Jira-keyed, velocity-analyzing, or leadership-facing.
This is a new layer under `knowledge/roi/`, not a rebuild of value-ledger.

## Risks / known weaknesses (stated in the framework doc)

- Story points are self-estimated by ticket creators — consistency across builders
  varies. Mitigation: report ticket-count AND points, flag estimator variance.
- "Shipped" defined by Final Technical Review + manifest = promotion work only;
  ops/intelligence work without manifests is undercounted. Mitigation: secondary
  count of all resolved BSYS tickets, shown as range.
- Attribution of Josh's velocity to AI vs learning-curve is confounded; the
  framework claims throughput change, not causality proof.
- Gateway $ supplied manually → gaps if Josh forgets; telemetry fallback labeled
  as estimate.
