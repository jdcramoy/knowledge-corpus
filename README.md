# josh-knowledge

The durable knowledge tree behind the Agentic Workato Harness. Every
session loads `INDEX.md` as its router: one line per knowledge file, and
the line tells you whether to load the file.

## Layout

- `INDEX.md` — the routing table. Read the line, load the file if relevant.
- `domains/` — cross-project doctrine (platform behavior, orchestration,
  benchmarking, governance). Load when working in that domain, any project.
- `projects/` — per-project state files.
- `scripts/` — operational tooling. Notable: `mission-control.py` (session
  closeout registry), `orchestration-router.py` (decides solo / fanout /
  pipeline / team for multi-part work), `predict.py` (prediction ledger).
- `people/`, `claims/`, `cortex/`, `bus/`, `dreams/` — the fleet's living
  state: people files, claim ledger, attention queue, gossip bus, dream
  reports.

## Orchestration router

`scripts/orchestration-router.py` answers "who does this work?" without a
human deciding. Hard rules override scores: production writes are never
delegated, adversarial review needs a persistent team role, high collision
risk forces disjoint ownership. Everything else scores seven features and
picks among solo, fanout, pipeline, and team. Doctrine:
`domains/orchestration-router.md`.

## Rule of the tree

All durable knowledge lives here. Lessons from every true build task land
in `domains/` or `projects/` and get an `INDEX.md` line the same session.
