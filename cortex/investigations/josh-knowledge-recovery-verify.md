# josh-knowledge recovery verify — lookup dispatch 2026-10-16T04:40Z, persisted 07:40Z

Headless lookup (flash) completed 04:40Z but the knowledge write gate denied its file
append (Bash heredoc AND Write tool). Findings delivered in dispatch stdout; persisted
here by the 07:35Z pulse per the sanctioned-persistence rule. Verdict below is the
dispatch's, quoted with its evidence; the remote check was re-verified live by the
07:35Z pulse (`git ls-remote origin main` from this clone → `Repository not found`, fatal).

## Verdict: RECOVERABLE — pre-rewrite blobs confirmed on origin/main, all objects intact locally

**(1) Pre-rewrite blobs covering Oct 14: YES.** All reads against the already-fetched
`refs/remotes/origin/main` (= `82d686793a4…`, tip carries the Oct-15 18:08 "history-rewrite
record" commit). No fetch/pull/checkout/restore was run.

| File | Pre-rewrite commit | Blob hash |
|---|---|---|
| `jira-triage/runs.jsonl` | `80e14dae2591e11716e0fb477a7ddc691cea37b3` — "nightly auto-backup 2026-10-14 23:33:06" | `9f9fc48e510f76152c3d156197f31dabf2746816` |
| `jira-triage/last-sweep.txt` | same commit `80e14dae` | `7bd69178d6e8cc7d3e9cb70df96cd0858c9f1a07` |

`80e14dae` is an ancestor of origin/main; all objects verified present via `git cat-file -t`.
Blob contents: **22 runs.jsonl rows including the 2 Oct-14 rows** (`14:15:58Z` fleet pass,
`18:14:56Z` convergence pass) and **last-sweep.txt = `2026-10-14T18:13:47Z`** — exactly the
pre-rewrite marker.

**(2) Exact commits / rows recoverable:**
- `80e14dae` — full 22-row blob, Oct 8 → Oct 14 18:14:56Z (this is the recovery source).
- Older snapshots: `5bccf9c1` (Oct 13), `91742da7` (Oct 12).
- **Not in git:** anything appended after Oct 14 23:33:06 — never committed. The two vanished
  Oct-15-era rows aren't recoverable from history.

**Key discovery — the Oct-14 loss is already repaired locally.** Local `jira-triage/runs.jsonl`
(24 lines) is byte-identical to the origin blob's 22 rows PLUS two Oct-15 rows marked
`"restored 2026-10-15: original row lost to the knowledge-tree revert mechanism … see
runs.jsonl.bak-restore-20261015"`. Both local Oct-14 rows match the origin blob exactly.
Recovery with `git show 80e14dae:jira-triage/runs.jsonl` remains available as the clean source.

**Caveats — what was NOT verified by the dispatch:**
- `git ls-remote origin main` failed: `Repository not found` on
  `github.com/Workato-All/josh-knowledge.git`. **Re-verified live by the 07:35Z pulse from
  this clone: same fatal.** Either the repo was deleted/moved or auth expired (GitHub returns
  "not found" for private repos with dead creds too). The nightly auto-backup commit chain
  therefore has no confirmed off-box destination; all verified objects sit in local
  `.git/objects` only.
- No fetch authorized → no check for pushes after the local fetch (the tip already post-dates
  the rewrite).
- Local main is 5 ahead / 0 behind origin/main (merge-base = `82d6867`).

Pulse note: recoverability of the Oct-14 loss is CONFIRMED and the local repair is already
byte-exact, so the data-loss blast radius is bounded. The live finding this pulse is the
remote: origin is unreachable, so the backup/recovery path that just proved its value is
itself unverifiable beyond this machine.
