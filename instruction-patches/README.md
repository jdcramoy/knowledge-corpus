# instruction-patches — the correction-to-instruction loop

Corrections Josh gives agents become edited skills/playbooks/CLAUDE.md lines
automatically — as dissenter-reviewed diffs Josh approves. Self-learning that
is real: the harness's instructions get better without Josh writing them.

## Pipeline: mine -> queue -> dissenter -> Josh approve -> apply

1. **MINE (nightly, zero LLM)** — `~/.claude/knowledge/scripts/instruction-miner.py`
   reads the latest 2 dream reports (`knowledge/dreams/2026-*.md`, the
   "Corrections" sections), any gossip-bus findings tagged `correction`
   (`knowledge/dreams/bus/*.jsonl`), and rejected-for-cause outcomes from
   `garden-reports/proposal-outcomes.jsonl`. It clusters the evidence into
   correction CLASSES by keyword and checks each class against the current
   instruction surface: does the target skill/playbook/CLAUDE.md already
   contain a counter-rule? Every UNCOVERED class becomes one queue entry in
   `queue.jsonl` (`status: pending`). Every covered class is PROVEN by quoting
   the counter-rule line found, into `coverage-<date>.md` — coverage is never
   assumed.
2. **QUEUE** — `queue.jsonl`, one line per uncovered class:
   `{ts, slug, class, evidence_ref, evidence_count, evidence_sample,
   target_file, suggested_patch (one line), status}`. Default posture:
   **pending entries stay pending forever** until a human-visible path moves
   them.
3. **DISSENTER (weekly, Sunday)** — the instruction-miner output feeds the
   brain-gardener's weekly report. The gardener's "modularize/patch"
   proposals carry the queued classes through **dissenter review**
   (`knowledge/dreams/bus/dissenter.jsonl`) before Josh sees them: the
   dissenter attacks each suggested patch (is the class real? is the
   counter-rule genuinely missing? does the one-liner fight an existing
   rule?). Surviving patches land on Josh's desk as review-ready diffs, not
   raw irritations.
4. **JOSH APPROVE** — `instruction-patch.py --approve <slug>` flips a pending
   entry to `approved`. Nothing applies without this. Entries can be killed
   with `--reject <slug>`.
5. **APPLY** — `~/.claude/knowledge/scripts/instruction-patch.py --apply <slug>`
   appends the one-line suggested patch to the target file, records
   `{ts, slug, target, applied: true, diff_note}` to `applied.jsonl`, and
   flips the queue entry to `applied`. The applier refuses: pending/rejected
   entries, unknown slugs, targets outside the allowlist, and patches whose
   text is already present.

## Target-file mapping (class -> instruction surface)

| correction class | target file |
|---|---|
| wrong-tool-choice | `~/.claude/skills/airo-mcp-playbook/SKILL.md` |
| build-order-skip-verify | `~/.claude/skills/workato-development-playbook/SKILL.md` AND `~/.claude/skills/workato-skill-builder/SKILL.md` |
| uat-evidence-gap | `~/.claude/skills/uat-evidence/SKILL.md` |
| premature-success-claim | `~/.claude/skills/verify/SKILL.md` |
| stale-recap, browser-ui-loop, scope-drift | `~/Documents/CLAUDE.md` |

The applier enforces this set as a hard allowlist — a queue entry pointing
anywhere else is refused even if approved. New targets mean editing the miner
taxonomy AND the allowlist together, on purpose.

## Files

- `queue.jsonl` — pending/approved/applied patch queue (append-only discipline)
- `applied.jsonl` — audit trail of every applied patch
- `coverage-<date>.md` — per-run coverage proof (counter-rules quoted)

## Correction classes of record

From the 2026-10-09 insights report: premature success claims, stale recaps,
wrong-approach rework, browser-UI loops, scope drift. The taxonomy adds
wrong-tool-choice, build-order-skip-verify, and uat-evidence-gap from the
dreamer's correction stream.

## Operations

```
python3 ~/.claude/knowledge/scripts/instruction-miner.py            # nightly pass
python3 ~/.claude/knowledge/scripts/instruction-miner.py --dry-run  # no queue writes
python3 ~/.claude/knowledge/scripts/instruction-patch.py --list     # show queue
python3 ~/.claude/knowledge/scripts/instruction-patch.py --approve <slug>
python3 ~/.claude/knowledge/scripts/instruction-patch.py --apply <slug>
python3 ~/.claude/knowledge/scripts/instruction-patch.py --reject <slug>
```

Heartbeat: each nightly run appends `{"ts", "job": "instruction-miner"}` to
`garden-reports/heartbeat.jsonl`.

## Seed run — 2026-10-09

Latest dream reports were 2026-10-08.md and 2026-10-07.md (no 2026-10-09
report existed at build time). Result: 9 evidence items clustered, **0
uncovered classes** — all 8 correction classes already have counter-rules on
the instruction surface. Proof: `coverage-2026-10-09.md` (each class quotes
the exact counter-rule line found). The loop is live and will queue the first
time a correction class fires that no rule covers yet.


<!-- demoted from INDEX.md 2026-10-25, librarian pass, branch librarian/2026-10-25. Content preserved verbatim; the INDEX line is now a routing hook. -->

## INDEX line history (demoted 2026-10-25)

- - [Instruction-patch loop](instruction-patches/README.md) — corrections-to-instructions self-learning (2026-10-09, committed 8eb8039): instruction-miner.py (nightly, zero LLM — latest 2 dream reports + bus correction findings -> 8 keyword-clustered correction classes -> coverage check vs instruction surface -> UNCOVERED classes queued pending in instruction-patches/queue.jsonl, covered classes PROVEN with quoted counter-rules in coverage-<date>.md); instruction-patch.py applier (--approve/--apply gate, hard target allowlist, applied.jsonl audit); weekly Sunday path: gardener modularize/patch proposals -> dissenter review -> Josh approve; seed run 2026-10-09: 8/8 classes already covered (0 uncovered)