# Registry-writer lookup: 82272892 fail-closed data states (2026-10-12) — SOLVED

Follow-up to `82272892-canon-vs-sweep.md` (Class A risk/confirmation invariant + Class B conflicting activation).
Investigation read-only (no Workato writes); evidence = live data-table reads + session transcripts.
All times UTC unless tagged PDT/EDT. Machine-local TZ is EDT (-0400); PDT = UTC-7.

Registry: `workspace_semantic_registry`, uuid `b64781ad-06b6-44db-bfde-09daeba8e801`, numeric 147343, folder 35404886.
Data-table rows carry NO updated_by metadata — writer identification is from transcripts + timestamp correlation.

## The writer behind BOTH classes: session d880a437-9963-427d-8aae-8b2605de96b1

`~/.claude/projects/-Users-<user>-orca-workspaces-workbench-Google-Semantic-MCP/d880a437-9963-427d-8aae-8b2605de96b1.jsonl`,
active until 02:42Z 10-13 — this IS the "gws-semantic-catalog-sync session active 2026-10-13T02:36Z"
(it was staging promotion batch BSYS-29583 at that moment). Its parallel subagents did the writes.

## Class A — docs.documents.batchUpdate@v1 risk=external_side_effect + confirmation=intent_scoped

Jobs j-AbwDFzAT-JYdJbm-CD (22:54:54Z) + j-AbwDG6JL-mrp9wg-CD (22:55:07Z) = 15:54/15:55 PDT.

**Two-layer answer.**

(1) ORIGIN of the offending state (legacy, days old): the generate→promote pipeline itself. The 17-capability
create/update/copy-family rows (batchUpdate incl.) were created 2026-10-02T08:44–08:45Z / 10-03 with
risk=external_side_effect + confirmation=intent_scoped, policy_version 1.3.0 — the generator
(`scripts/build-semantic-indexes.mjs`) emitted that pairing with no guard, and the seeder's rank-1000/1001
mechanical fallback rows copied it. NOT written on 10-12; it sat in the table until the new guard made it fatal.

(2) The 10-12 writer that made it FATAL: same session, subagent `agent-ad2d628b02efd4d4d`
("Build 17-row relabel + guard", dispatched 22:51:01Z). Sequence:

- ~22:50Z — runtime connector 1356281 **v119 RELEASED** with the fail-closed pairing guard at index-compile
  (commit a4b456c, 22:59:04Z, documents it).
- 22:52:34.926Z — subagent ran `promote-workato-semantic-registry.mjs --apply --capability docs.documents.batchUpdate@v1,...`:
  relabeled the MAIN rows (evidence: rank-1/2 rows 48c2f7fe/da285985 sys_updated 22:52:36Z, domain updated_at
  22:52:23Z, now reversible_internal/intent_scoped). But promote CANNOT see seeder-managed rank-1000 mechanical
  rows (the deposited ORDERING TRAP) — 17 of them kept the old pairing.
- 22:54:54 + 22:55:07Z — scheduled 15-min sync runs failed on the 17 stale mechanical rows (offender: rank-1000
  row da41983a "batch update documents", domain updated_at still 2026-10-03).
- 22:55:52 / 22:56:54Z — subagent scanned the live table, found exactly 17 external_side_effect+non-always rows.
- 22:57:07.609Z — subagent PUT-relabeled all 17 mechanical rows → reversible_internal (row da41983a sys_updated
  22:57:09Z). Green run 22:57:13Z (15:57:13 PDT), 4 seconds later.
- Closeout (mission-control + INDEX.md) records it explicitly: guard "proven live — it caught+rejected the stale
  rows on sync 82272892 before the repair"; ORDERING TRAP deposited: "reconcile seeder-managed mechanical rows
  BEFORE releasing the guard".

**Verdict Class A: the offending rows were pre-existing generator/seeder output (10-02/03, pre-guard policy 1.3.0);
the connector v119 release beat the mechanical-row repair by ~3 minutes and two scheduled ticks paid for it.
Root cause = release-ordering race, not a rogue writer.**

## Class B — people.people.deleteContactPhoto@v1 duplicate/conflicting activation

Job j-AbwFbQAo-TrkPQ4-CD, 01:21:46Z (18:21:46 PDT).

**Writer: subagent `agent-a41a02512d3fbb989` (BSYS-29570 demotion-mechanism probe, same parent session d880a437).**
Direct evidence from its transcript:

- 01:20:30.972Z — POSTed a SCRATCH PROBE ROW into the LIVE registry b64781ad: capability_id
  `people.people.deleteContactPhoto@v1`, intent_key `"scratch suspended routing probe"`, index_key
  `people.people.deleteContactPhoto@v1|scratch suspended routing probe`, rank 2001, activation=cataloged
  (cloned from the real row via `/tmp/deletephoto_base.json`). Record id 03c66f5a-73f2-47de-986e-0d24296842c0.
  This created the SECOND row for the capability.
- 01:21:43.788Z — PUT activation cataloged→`suspended` on the scratch row ("same update the demotion performs").
  The PUT response embeds `"job_handles": ["j-AbwFbQAo-TrkPQ4-CD"]` — the failing job was the sync tick fired by/
  coincident with this write. Two rows, same capability, different activation (cataloged rank-1 vs suspended
  rank-2001) → recipe step "Derive unique operation contracts" threw `Conflicting generated operation contracts
  for people.people.deleteContactPhoto@v1: activation.` Fail-closed working as designed.
- 01:23:06.916Z — `curl DELETE .../tables/b64781ad.../records/03c66f5a...` (scratch row removed from the live
  registry) + force-run 82272892 (j-AbwFcNC8-cgEQNc-CD) → green; "scratch row in routing AFTER DELETE + sync: GONE".
  Matches the observed 18:23:08 PDT green run.
- The agent's own finding (BSYS-29570 manifest, committed): activation=suspended does NOT leave the routing
  surface — demotion = DELETE the registry row. "scratch probe row deleted" recorded.

Correction to the autopsy: j-AbwFbQAo was not an ordinary scheduled tick — the trigger payload's "fresh rows
updated_at 01:21:54Z" were the scratch row's own timestamps from the probe write.

Current live state verified clean: exactly 1 deleteContactPhoto row (1b3029d5, rank 1, cataloged,
external_side_effect + confirmation=always = CORRECT pairing for a destructive capability, untouched since 10-05);
8 batchUpdate rows all reversible_internal/intent_scoped; 0 inconsistent rows table-wide per the 22:58Z verify sweep.

## Recurrence risk

- Class A: LOW. Guard now mechanical in BOTH layers (generator throws; connector v119 fail-closes at compile),
  relabel verified complete. Residuals: (a) the ordering trap — any future policy-bump/release must reconcile
  seeder-managed mechanical rows BEFORE releasing the guard, else repeat; (b) raw-PUT writers (agents doing direct
  data-table writes, as the relabel agent itself did) bypass the generator guard — the connector catches those at
  materialize, which self-heals within one tick but still fail-closes sync runs in the window.
- Class B: MODERATE-HIGH — this was a deliberate live-table probe, and the BSYS-29570 lane is now a standing
  planter/demoter. ANY second row sharing a real capability_id with divergent generated-contract fields trips the
  derive-step conflict detector on the next sync tick (≤15 min). The probe used a REAL capability on purpose (to
  observe routing materialization). Recommended hardening (NOT applied — read-only scope):
  (1) probe/scratch rows must use synthetic capability_ids that cannot collide (the conflict is per-capability);
  (2) demotion windows/probe plants should expect a mid-window sync tick to fail-closed — expected + self-clearing;
  (3) consider making the derive step skip rank>=2000 scratch-tier rows rather than conflict on them.
  Also flag: live-registry DELETEs by agents are one-way ops on a live asset — per the standing micro-target rules
  these need an explicit go outside a Josh-approved UAT plan.
