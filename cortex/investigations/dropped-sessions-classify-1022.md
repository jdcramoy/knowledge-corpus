# Dropped-sessions classification — 2026-10-22 (read-only investigation)

## Verdict first

Of 39 drops in 48h, 23 transcripts live in the workbench project dir. Only **1 of 23 is
genuinely mid-flight dropped work** (609a5f17 — died on an API error with 22 edits on disk).
~4 more completed real work with artifacts delivered but skipped the closeout row. The other
~18 are scheduled cortex pulses and bounded read-only briefs that self-record their output —
the detector over-fires on sessions that never write mission-control rows by design.

## Detection logic

- **Emitter:** `~/.claude/hooks/session-drop-guard.py` (SessionEnd hook) → appends to
  `~/.claude/knowledge/mission-control/dropped-sessions.jsonl`.
- **Scoring:** a session qualifies if it has ≥ **8 assistant turns** (non-sidechain assistant
  messages) AND no mission-control event within **900 s (15 min)** of the session's last real
  message timestamp (2026-10-16 deadman FP fix). "Files touched" = distinct `file_path` values
  from `Edit`/`Write`/`MultiEdit` tool_use only — Bash writes, `Write_Table_Cells`,
  `Set_Element_Text` etc. are invisible to the counter, so file counts are undercounts.
- **Window:** morning-digest.py reads the ledger and keeps rows where `ts` is younger than
  **48 h**, dedupes by session_id (the sweep re-appends the same sessions every startup).
  39 unique sessions / 23 with workbench transcripts.

## Classification of the 23 workbench drops

| Bucket | Count | Sessions | Note |
|---|---|---|---|
| Scheduled cortex pulses (self-record) | 14 | d00f245a, 06842dbc, a17782ea, dc3de68f, 570b4ca7, e6b11eab, 42b02019, b33a0d3c, e603000f, 4ab98eab, c16c5463, ae267b5c, 09dcd850, a9f3cfdd | Hourly `[cortex-coordinator-pulse]` runs; each ended "Pulse complete" and wrote `cortex/attention-queue.md`. Closeout row is redundant — state lives in the queue file. Noise. |
| Completed bounded read-only briefs | 4 | a473065f (receipts-gate TCC diagnosis), 81916177 (mood-setter diagnosis), c9598902 (recipe-deletion 404s = intentional), 0f50f497 (fleet-job corruption brief) | Finished, verdict delivered, findings file written. Arguably closeout-worthy but nothing mid-flight to lose. |
| Real work, artifact delivered, no closeout row | 4 | 9d2cc9db (/today, 253 turns, proposal-decide.py + harness docs edits), e897ba34 (proposal-stamp audit, findings staged to workbench after write gate-denied), fa8b44c4 (LinkedIn post), 10758267 (demo-ideas doc) | Deliverables exist on disk; only the registry row is missing. Medium. |
| **Genuinely dropped mid-work** | **1** | **609a5f17** | Ended on `API Error: ENOTFOUND` mid-run. Real dropped state. |

## Top 3 by files touched (workbench sample)

1. **609a5f17** — 7 files, 22 edits, 373 turns: GitHub repo consolidation for Josh's
   three-repo sharing problem — edited `jira.py`, wrote `github-two-account-layout.md` memory,
   and modified CI workflows + `harness-backup.sh` in /tmp staging trees (agentic-kit-work,
   devkb-work). **Died on API ENOTFOUND** — staging-tree state needs absorbing before rework.
2. **9d2cc9db** — 5 files, 253 turns: `/today` chief-of-staff run that went further — approved
   proposals via edited `proposal-decide.py`, updated `mods-deploy.sh` and harness docs
   (03-mods.md, 05-schedules.md) in agentic-workato-kit, posted the digest.
3. **e897ba34** — 2 files, 47 turns: audit of 11 proposal "claimed-built" stamps; verdict
   11/11 EVIDENCED, but the findings file landed in workbench only because the
   `cortex/investigations/` write was gate-denied — the copy-back is still pending.

(Outside the workbench sample, the ledger shows two bigger drops in other project dirs:
7ea75378 — 10 files, the nightly guidance-compiler GSlides run; da6d24d5 — 8 files, 690 turns.
Those transcripts weren't read per brief scope.)

## Recommendation

The 39/48h headline is mostly detector FPs on by-design-non-closeout sessions. Two cheap
fixes: (1) exempt sessions whose opening prompt matches `[cortex-coordinator-pulse]` /
`ONE-JOB BOUNDED BRIEF` (scheduled fleet runs self-record), and (2) have /today and
bounded-brief templates emit a mission-control row on completion — that alone would clear
~18 of the 23.
