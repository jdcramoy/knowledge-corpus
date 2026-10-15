# Spec: Harness store discipline, slice 1 (ranked #1 of the 2026-10-11 next-10 review)

## Goal

Make the harness's shared ledgers safe under ~20 concurrent writers before any other
improvement lands. Source: `reviews/harness-next10-2026-10-11.md` (6-lens adversarial
panel, adjudicated). Status: spec only, awaiting Josh's build approval.

## Background

The knowledge git tree is simultaneously the versioned document store and the append-only
event log for ~20 writers. Documented consequences: 49 uncommitted triage/proposal
decisions destroyed 2026-10-11 by `git checkout -f` over a dirty tree; queue.jsonl
corruption (commit 31ac8df, repair file `triage/queue.jsonl.pre-repair-2026-10-10`);
98 files uncommitted right now; predict.py rewrites its entire store with `write_text`
on every check while `atomic_io.py` (flock + temp + os.replace) sits unused in the same
directory; heartbeat timestamps appear in three formats in one ledger.

## Scope

IN:
1. Extend `scripts/atomic_io.py` with `atomic_append_validated(path, row, schema)`:
   per-ledger JSON schema (required fields, enum fields, ISO-8601-ts-with-offset
   timestamp format) validated at append time; invalid row = loud refusal, never silent
   coercion.
2. Route `triage-outcomes.jsonl`, `proposal-outcomes.jsonl`, and predict.py's prediction
   store through it (predict.py check becomes append + compaction-on-read, or
   atomic_replace via the existing module).
3. `scripts/voices.json` v0: per-agent writable-path registers and append-vs-rewrite
   mode for the five shared jsonl surfaces plus INDEX.md (INDEX.md = append-line-only,
   named writers).
4. One brain-guard lint rule: out-of-register or whole-file-rewrite-of-shared-jsonl
   writes produce an annotation citing the rule and the two prior incidents. Shipped
   with a test that FAILS before the rule and PASSES after.
5. `scripts/rebuild-queue.py`: regenerate queue.jsonl purely from the immutable
   triage-outcomes log; run once to prove the projection matches, keep as the
   documented recovery path.

OUT:
- No new schedules, no new agents, no LLM calls.
- No retirement of any existing mechanism (fencing/leases is a later slice; this
  slice does not block or gate any write, it validates and annotates).
- Markdown files other than INDEX.md untouched.

## Acceptance criteria (objectively verifiable)

- [ ] Appending a row with a bad status enum or a naive timestamp to a routed ledger
      exits nonzero and writes nothing.
- [ ] predict.py's store is never written via bare `write_text` (grep-verified).
- [ ] brain-guard lint test suite: out-of-register write → annotation fires; in-register
      append → silent; includes the failing-before/passing-after test.
- [ ] rebuild-queue.py output byte-compares (modulo ordering) against the live queue on
      a drill run, or documents the delta rows explicitly.
- [ ] No uncommitted state beyond what existed at start (tree hygiene preserved).

## Design-gate note

Existing mechanisms already solving parts of this: `atomic_io.py` (proven torn-write
fix, adopted 2026-10-09), decision-inbox already uses it, the librarian's
additive-to-main/edits-to-branch rule is the voices.json grammar in miniature. This
spec generalizes those to fleet-wide enforcement; it does not invent a new storage
layer.

## Risks

- brain-guard annotations erode trust if they false-positive on a new agent with no
  register entry → default register is append-only-everywhere/rewrite-nowhere (safe
  default), and the gardener's weekly architecture pass adds entries for new writers.
- Rebuilding the queue mid-day could race an appender → rebuild only reads the
  outcomes log (append-only) and writes the projection via atomic_replace; drill run
  is done once, Josh-supervised, before it becomes the recovery path.

## First slice timing

One working day, zero LLM surface, four small diffs each with a test.
