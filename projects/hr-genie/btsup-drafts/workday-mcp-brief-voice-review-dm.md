# DM draft to Josh — voice review of the Workday MCP head-to-head brief (DRAFTED 2026-10-26, NOT POSTED)

**Destination:** Josh Cramoy (Slack DM)
**Ask:** his voice review of the head-to-head benchmark brief before it goes anywhere.

---

Hi Josh — the Workday MCP head-to-head benchmark is staged and waiting on you, nothing has run.

The plan: 10 identical asks fired once each at our Workday MCP and at Workday's OOTB MCP, scored on correctness, refusal quality, latency, and token weight. The asks cover identity resolution, org traversal, PTO balance, cross-worker scoping, inbox tasks, the known comp-range refusal case, a dev-tenant write+cancel (your call whether case 9 runs at all), and email-to-WID resolution.

Three things need your call before the run:

1. Which OOTB endpoint we're testing against — do we have access to Workday's official MCP server yet, or does that provisioning become an external ask first?
2. Does the write+cancel case (9) run on the dev tenant, or get skipped?
3. Does the OOTB side run under your identity or a service identity?

The full plan with the scoring sheet is at `~/.claude/knowledge/projects/hr-genie/workday-mcp-head-to-head-plan.md`. If the shape looks right, I'll run it as soon as the OOTB endpoint lands.

---

**Reminder:** this is a draft only. Never posted. Per Slack presence rules, posting needs Josh's explicit confirmation.
