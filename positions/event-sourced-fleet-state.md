# Position: shared ledger-like state must be rebuildable and drift-checked

Status: PROVISIONAL house position (librarian weekly pass 2026-10-11, revised
same day after dissenter attack). Review date: 2026-10-25. Zero days of
operating history behind mission-control, the flagship build; this piece is
rated provisional BY HOUSE RULE (claims and positions need last-verified
dates; "shipped this morning" is not evidence).

## The position (v2, amended after dissent)

For every shared, multi-writer, ledger-like file in the harness (queues,
registries, rankings, boards, anything script-regenerable):

1. Writes go through ONE validated path (schema-checked, atomic).
2. A full-fidelity or documented-lossy append-only twin exists.
3. A SCHEDULED rebuild-and-diff runs mechanically and ALARMS on drift
   between projection and log. (v1 said "the log wins, never patch" with
   nothing detecting disagreement; the dissenter called that operationally
   unfalsifiable. Corrected: drift must be machine-detected.)
4. The operational file remains truth until the twin provably carries the
   complete schema. (Amendment accepted: today's rebuild recovered 113 of
   138 queue rows, 18% unrecoverable, 6 fields degraded, because the
   outcomes log was designed as an audit side-output. The state-plus-twin
   arrangement is retained until the twin is full-fidelity, not abolished.)

What changed from v1: the headline. v1 claimed "state files are projections,
never patched; the log wins." The dissenter showed v1's own evidence
undermined that: the 82%-fidelity rescue was performed BY the state-truth-
plus-audit-twin arrangement v1 wanted to abolish. The defensible claim is
rebuildability with drift detection, not projection supremacy.

## Evidence from this house (amended)

- 2026-10-11: git checkout -f over the dirty tree destroyed ~49 uncommitted
  decisions. HONESTY AMENDMENT (dissenter F1, accepted): the event log lives
  in the same failure domain and was itself uncommitted that day (281 dirty
  files by evening). What actually mitigates checkout-class loss is COMMIT
  CADENCE (5 commits on 10-11, nightly auto-backup, restore drill). Event
  sourcing is orthogonal insurance against write-path races and hand-edit
  drift; it is NOT the cure for destructive tree operations. Do not build
  event logs and skip commits.
- 2026-10-10: queue.jsonl corruption (commit 31ac8df, repair file). The
  cause was a whole-file rewrite racing appenders; the mechanical fix was
  atomic appends. A projection layer was not required for that fix.
- 2026-10-11: mission control shipped event-sourced; rebuild-queue.py
  regenerated 113 of 138 rows; the gaps (20 never-decided rows, missing
  kind/evidence/work/points/urgency fields) are now visible instead of
  silent. The twin's schema debt is the next build, not a footnote.
- predict.py ran append-only with last-line-wins compaction before this
  position existed (dissenter C3, accepted as the strongest supporting
  fact): the fleet converged on the pattern organically.

## What we do and do not claim

We claim this for LEDGER-LIKE state only. The markdown knowledge tree is
curated, not derived, and is explicitly OUT of scope (dissenter M4,
accepted: the currently rotting store, INDEX.md 39.4KB to 64.8KB in 30h,
sits in that excluded zone; this position does not address it. The
index-budget gate does.)

## Enforcement status (honest, per dissenter F2)

- Validated write path: SHIPPED (atomic_append_validated in triage-decide,
  proposal-decide, predict.py, mission-control.py).
- Scheduled rebuild-and-diff with drift alarm: SHIPPED 2026-10-11 as fleet
  job `queue-drift` (daily) after the dissenter found rebuild-queue.py
  unscheduled. A deliberate-corruption drift drill is part of its script.
- Write gate on hand-edits of projections: NOT SHIPPED. brain-guard
  store-discipline-01 is advisory. Until it blocks, "not a mechanism"
  rhetoric is DOWNGRADED: this is a convention with mechanical checks, not
  an enforcement layer. The v1 sentence "a rule that must be remembered is
  not a mechanism" applies to v2 as written; the hook-gate upgrade is the
  standing follow-up.
- Read-path liveness: the fold is owned by the cortex pulse, the layer the
  review caught silently dead for two days (dissenter F2, accepted).
  Mitigation: the external dead-man scaffold and 1.5x health thresholds
  shipped the same week; the fold job itself is zero-LLM and cheap enough
  to also run in the morning brief.

## Dissent log (constitutional section)

Attack: dissenter agent run, 2026-10-11, full report in
dreams/bus/dissenter.jsonl thread event-sourced-fleet-state. Verdict:
survive-with-amendments; amendments invert the headline.

- F1 (log shares the checkout failure domain): ACCEPTED in full; drove the
  commit-cadence honesty amendment and the "do not build event logs and
  skip commits" law.
- F2 (position fails its own mechanism test): ACCEPTED; drove the
  queue-drift fleet job, the drift drill, and the enforcement-status
  downgrades.
- M3 (outcomes log lossy; ranking collapses on rebuild): ACCEPTED; drove
  amendment 4 (operational file stays truth until full-fidelity twin).
- M4 (scope excludes the rotting markdown store): ACCEPTED as stated;
  explicitly out of scope here.
- M5 (agent-discipline logs rot; machine logs thrive; four timestamp
  formats already on the bus): HALF-ACCEPTED. The writer-class concern
  stands and is why mission-control events are schema-validated and the
  closeout is a CLAUDE.md rule. Rebuttal on the general: the bus's dead
  logs belong to agents whose charters do not mandate posting; watch the
  2026-10-25 review for whether mission-control's event cadence decays.
- M6 (readership and liveness are the wound, not write integrity):
  ACCEPTED; the position now says it addresses write integrity only.
- M7 (zero operating history): ACCEPTED; status downgraded to PROVISIONAL
  with a 2026-10-25 review date.
- C1 (fold lag up to 1h on the board): ACCEPTED; cosmetic, noted.

If a future incident shows the twin diverging silently, this position
fails its own drift-alarm test and reverts to draft.

## Sources

- reviews/harness-next10-2026-10-11.md (the adjudicated review).
- rebuild-queue.py drill output (113 vs 138, 2026-10-11).
- dreams/bus/dissenter.jsonl (the attack, 2026-10-11).
- garden-reports/harness-health-2026-10-11.md (morning-fleet outage).
