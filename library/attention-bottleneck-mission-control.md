# The attention bottleneck: what the field says about running many agents

Procured 2026-10-11 (librarian weekly pass, beats: multi-agent orchestration
and the human bottleneck; agent observability patterns). Sources fetched
2026-10-11. Motivation: Josh, 2026-10-11, "I'm finding it hard to keep up
with the pace of development we've now exploded into... I don't want to get
out over my skis."

## What's new

1. **The human attention constraint is now a named research problem.**
   AgentGUI (arXiv 2607.26300, fetched 2026-10-11,
   https://arxiv.org/html/2607.26300) is a locally hosted GUI for observing
   and steering multiple concurrent long-running agents. Measured result
   that matters to this house: statistically significant 38% faster
   identification of key elements in agent traces, and automated drift
   prevention raising small-model task completion by up to 34 percentage
   points. The paper's premise is ours verbatim: studying agent traces
   personally defeats the time-savings that delegation promised.

2. **"The real constraint is not the agents; it is the human trying to
   keep track of which one needs attention."** (voxos.ai, "The Attention
   Bottleneck: Managing 10 AI Coding Agents at Once",
   https://voxos.ai/blog/terminal-focus-routing-multiplexer/, fetched
   2026-10-11.) Their answer: focus routing, one surface that tells the
   operator which agent needs eyes next.

3. **Control-plane pattern for human-governed fleets.** Agent Task
   Control Plane (ATCP, exa.ai library,
   https://exa.ai/library/publication/q946v9m0grj, fetched 2026-10-11): a
   reference architecture for governing parallel agent work, aimed exactly
   at the growing cognitive burden. Ramparte's playbook pattern
   "Supervise Many Agents Through One Interface"
   (github.com/ramparte/agent-building-playbook, fetched 2026-10-11) says
   the same in one line: as agents multiply, the limiting factor is the
   human's ability to see them.

4. **Observability = decision logs + staleness signals + thresholds, not
   dashboards you stare at.** (jeremyknox.ai,
   https://www.jeremyknox.ai/blog/ai-agent-observability/, fetched
   2026-10-11: "only page a human when something actually needs one."
   munderdiffl.in, fetched 2026-10-11: four at-a-glance questions: who is
   working, what are they doing, what is blocked, what changed.)

## Why it matters to this house

Mission Control (built 2026-10-11, this same week) is the house's
implementation of the emerging consensus, not a lagging imitation:

- Its event log IS the decision log the field calls for; its staleness
  check (cortex flags workstreams silent >24h) is the staleness signal.
- The board + brief + /today triangulation matches the ATCP
  control-plane shape; the focus-routing question ("which one needs eyes
  next") is answered by needs-josh ranking.
- The algedonic gap the cybernetics panelist named (review, 2026-10-11)
  matches Knox's "only page a human when something needs one": the
  external dead-man + P1 bypass design is that threshold, pending Josh's
  two secrets.

What the field has that we do not yet: AgentGUI's automated drift
prevention (steering small agents back mid-task) and its interactive
steering. Our cortex can only flag drift, not prevent it. That is a
credible future build; claim filed below. Also credible: their measured
framing (38% faster triage) suggests mission control's success metric:
time-from-needs-josh-event to Josh-seeing-it. Nothing in the house
measures that yet; approver-load telemetry (review rank 8, de-scoped)
was the first sketch of it.

## Claims filed

- See claims/claims.jsonl: aggui-drift-prevention-pattern (candidate;
  filed 2026-10-11) for drift-prevention as a future capability with this
  evidence base.

## Sources (all fetched 2026-10-11)

- https://arxiv.org/html/2607.26300 (AgentGUI)
- https://voxos.ai/blog/terminal-focus-routing-multiplexer/
- https://exa.ai/library/publication/q946v9m0grj (ATCP)
- https://github.com/ramparte/agent-building-playbook/blob/534aa66d/patterns/supervise-many-agents.md
- https://www.jeremyknox.ai/blog/ai-agent-observability/
- https://munderdiffl.in/blog/observability-for-agent-fleets/
- https://midfleet.ai/learn/agent-fleet-visibility/
- https://tensorops.ai/blog/agent-observability-documenting-the-work
