
# uat-sweep 09:01Z run — evidence linkage investigation

Investigated 2026-10-09 by the cortex-dispatched lookup (dispatch-20261009-110546-uatsweep).
Scope: read-only over ~/.claude/knowledge — build-ledger.jsonl 08:20-09:06Z, triage/queue.jsonl,
garden-reports/ (fleet-validation.jsonl, heartbeat.jsonl, harness-health-2026-10-09.md,
value-ledger.jsonl, proposal-outcomes.jsonl, roi-2026-10.md), dreams/bus/cortex.jsonl,
dreams/proposals/2026-10-09-parallel-uat-fleet-sweep.md, cortex/questions.jsonl, attention-queue.
Written via python3 append per the headless write-path finding (BSYS-29464).

## 1. Where the run evidence landed

- /tmp/uat-sweep/ — recipes.jsonl (full-estate enumeration, pages 1-70), sel-*.tsv category
  selections, force-run outputs, force-run-retries.tsv. Volatile scratch, gone on reboot.
- ~/harness/uat-sweep/ — the durable outputs: results-guardrail-selfcheck.md (append-only
  per-category results, proposal contract) and brief-2026-10-09.md (coordinator brief with the
  pass/fail matrix, written 09:05:46Z). This directory sits OUTSIDE the knowledge tree, so no
  brain surface (gardener, cortex, evidence, watchdog) indexes or re-reads it.
- garden-reports/heartbeat.jsonl — two bare completion rows only (08:25:53Z, 09:05:49Z), no payloads.
- garden-reports/fleet-validation.jsonl — NO row for the 09:01Z run; the run-validation contract
  captured only the 2026-10-08 stub rows for the other five jobs.
- build-ledger.jsonl — 19 command rows 08:20-09:06Z. Every uat-sweep row carries ticket: null.

## 2. Which approved tickets reference it

None. The morning batch (decided 08:26-08:52Z, status built) covers BSYS-29418 (rejected row,
superseded) plus approved work on BSYS-29455, 29456, 29457 (three rows), 29458, 29459, 29460,
29461, 29462, 29463, 29464. Zero of those queue rows cite the sweep brief, a results file, or any
recipe ID the sweep actually ran (82273312, 82273581, 82893591, 82862838, 82928715, 82928666,
82915212, 82929715, 82921534, 82248364; testcase runs on 82272066 and 82855731). The reverse link
is equally absent: no queue row or ticket field appears on any sweep ledger row.

- Contrast that proves the wiring exists and is simply unused: ledger rows at 08:51:38/08:51:43Z
  for healer verification in the same window carry ticket: BSYS-29396.
- Flagged as an unverified claim: attention-queue states uat-sweep was collecting runtime evidence
  for BSYS-29418 (recipe 82090477). The ledger shows no sweep touch of 82090477 in this run — that
  claim is not backed by the ledger rows visible here.

## 3. Missing linkage, minimal wiring fix, owner

Missing — three hops, all in one direction (run to ticket):
1. The brief lands outside the knowledge tree, so nothing downstream ever reads it.
2. No append to triage/queue.jsonl, so sweep failures never become verdict cards and never reach
   BSYS tickets through the standing /triage pipeline.
3. Ledger rows carry no ticket field, so even a human grepping the ledger cannot join run to ticket.
Additionally fleet-validation.jsonl receives no uat-sweep row, so the run contract is not applied
to this job at all.

Minimal wiring fix (no new system — the proposal contract already names the route: drafts stay in
the brief, filing goes through /triage): in the uat-sweep coordinator step (kit repo fleet job,
deployed to ~/.local/bin/fleet), after writing the brief:
1. Copy the brief into ~/.claude/knowledge/garden-reports/ as uat-sweep-<date>.md (or append one
   summary row to garden-reports/fleet-validation.jsonl carrying the brief path).
2. For each recipe failing twice, append an open card to triage/queue.jsonl via the existing
   triage_append path, with evidence pointing at the results file path plus the job IDs.
Filing then flows through the existing /triage to BSYS pipeline; no Jira API change is needed.

Owner: the uat-sweep fleet job itself — the coordinator script in the kit repo and
~/.local/bin/fleet (dream-loop build lane). This is a harness script change of the same class Josh
approved this morning (BSYS-29461 heartbeat wiring), so it needs his one-word build-kickoff on the
diff; the evidence agent is the natural auditor that the linkage exists on its next nightly pass.

## Verdict

The 09:01Z run produced real UAT evidence — testcase runs, force-runs, job IDs cirr-AbsJk9KE-GYe8NF-CD
and cirr-AbsJk9cN-AXFdLg-CD, jobs j-AbsJkDEt-f4tRo3-CD, j-AbsJkzkM-RBFNMY-CD, j-AbsJmFRA-WKNhQf-CD —
but it is stranded: zero linkage in either direction between the run and BSYS-29418 or any of the
ten approved tickets. One coordinator edit closes the loop.

Not verified here: the brief and /tmp scratch files themselves sit outside the permitted read scope,
so the pass/fail matrix contents are inferred from the ledger heredoc header, not read directly.
