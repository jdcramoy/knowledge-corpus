# BTG 2.0 — lineage map (v1, system/object level)

Generated 2026-10-26 by estate-architect weekly pass. Edges are description-derived
heuristics from the corpus index (`garden-reports/recipes-index.jsonl`) — labeled as
such; not DSL-verified. Field-level lineage not run (only on Josh's named folders,
capped at 10 recipes).

## Capability: BTG 2.0 eval + feedback loop (dev, folder "Automations")

```mermaid
graph LR
    subgraph Agent Studio
        GS[Agent Studio conversations<br/>BT Genie feedback]
        GQ[Message queue<br/>declined/queued messages]
    end
    subgraph BTG 2.0 wave (dev 3535597)
        FC[83295770<br/>Genie Feedback Capture<br/>watermarked poll]
        SW[83291436<br/>Pending Message Sweeper<br/>BSYS-29734 race fix drain]
        EJ[83295997<br/>Nightly Eval Judge<br/>BSYS-29739 golden set]
        GT[Eval Golden Set]
    end
    DT[(Feedback / verdict<br/>data tables)]

    GQ -->|poll / drain| SW
    SW -->|re-dispatch| GQ
    GS -->|watermarked poll| FC
    FC --> DT
    GT --> EJ
    EJ --> DT
```

## Recipes and links

| Recipe | URL | Role | Health (2026-10-26 index) |
|---|---|---|---|
| [BTG 2.0] Pending Message Sweeper | https://app.workato.com/recipes/83291436 | drain side of the BSYS-29734 race fix: re-dispatch queued messages that were declined | running, 368 jobs, 75 failed (20% fail rate) |
| [BTG 2.0] Genie Feedback Capture | https://app.workato.com/recipes/83295770 | Phase 0 floor: watermarked poll of Agent Studio conversations feedback | running, 332 jobs, 1 failed — healthy |
| [BTG 2.0] Nightly Eval Judge | https://app.workato.com/recipes/83295997 | nightly judge over the Eval Golden Set | running, 8 jobs, 2 failed (nightly cadence — low counts expected) |
| [BTG] GENIE \| BT Genie (prod) | https://app.workato.com/recipes/58511202 | the prod Genie this loop measures | running, 58 jobs, 6 failed |

## Watch items

- Sweeper's 20% fail rate is the wave's quality risk; recent DNS preflight
  gate skips (9 jobs on DNS failures) may share a cause — not yet verified.
- The prod BT Genie (58511202) appears in ORPHANED_IN_PROD (no dev twin) —
  confirm intent per the drift rule; never auto-remediate.
