# Needs-josh backlog classification — 15 oldest rows

**Sweep date**: 2026-10-20/21 (fold 01:14Z) · **Mode**: READ-ONLY (registry read + bus/dreams/reports/live cross-check; nothing changed except this file)
**Source**: mission-control/registry.json — 262 workstreams, 83 needs-josh. These are the 15 oldest by age_hours.
**Method**: for each row, grepped dreams/bus/*.jsonl, dreams reports, reports/, cortex/investigations/, and (where applicable) live local state (git status, launchctl, bus_post.py, lint-changed.py, wt recipes get) for follow-up work that supersedes the original decision.

## Verdict summary

**7 SUPERSEDED · 8 STILL-OWED** (2 of the still-owed are reduced-scope residuals).

| # | Workstream | Age | Verdict |
|---|---|---|---|
| 1 | harness-linting | 208h | SUPERSEDED |
| 2 | corpus-maintenance | 207h | STILL-OWED (1 residual item) |
| 3 | estate-review | 207h | STILL-OWED |
| 4 | estate-architect | 206h | STILL-OWED (reduced — 1 of 3 cards resolved) |
| 5 | bus-clock-census | 203h | SUPERSEDED |
| 6 | regression-registry-hygiene | 201h | STILL-OWED (urgent if nightly re-arms) |
| 7 | manifest-order-verification | 193h | SUPERSEDED |
| 8 | harness-benchmarking | 193h | STILL-OWED (or drop) |
| 9 | seismic-mcp (BSYS-29582) | 190h | STILL-OWED |
| 10 | gws-semantic-catalog-sync (BSYS-29585) | 190h | SUPERSEDED |
| 11 | estate-monitor-harness-hook (BSYS-29604) | 188h | STILL-OWED (low urgency) |
| 12 | kb-wave3-sources | 185h | SUPERSEDED |
| 13 | harness-machine-health | 175h | SUPERSEDED |
| 14 | seismic-test-recipe-loop | 171h | STILL-OWED (low urgency) |
| 15 | agent-gossip-bus | 169h | STILL-OWED |

---

## Row 1 — harness-linting (208h) — ✅ SUPERSEDED
Row asked: hook 14 in workato-guardrails vs fold into lint-changed.py.
**Evidence**: `scripts/lint-changed.py` now contains the full `insertion_clobber()` post-edit check (lines 24–61, citing `cortex/investigations/insertion-edit-clobber-class.md`) and is wired live as a PostToolUse hook in `~/.claude/settings.json` (27 hook entries; the lint-changed entry verified). Option 2 was implemented — the decision is moot; the lint is already running.
**Close as**: superseded by implementation (option B landed). No approval needed; optionally Josh notes he's fine with option B.

## Row 2 — corpus-maintenance (207h) — ⚠️ STILL-OWED (1 residual)
Row asked: approve 3 INDEX.md fixes + dedup artifact-exclusion list.
**Evidence**: (a) `projects/drift-fix-project.md` has been recreated (head shows frontmatter) — repoint fix moot; (b) INDEX.md:118 now carries the BSYS-25529 builder-enablement line — fix 2 done; (c) `projects/agent-harness-operations/` exists on disk but has NO INDEX.md line (grep: only lines 59/118 match) — fix 3 still owed; (d) dedup shortlist artifact-exclusion list — no approval on record.
**Recommended answer**: "Add the agent-harness-operations line to INDEX.md; dedup exclusion list approved as drafted."

## Row 3 — estate-review (207h) — ❌ STILL-OWED
Row asked: approve frontify token rotation, HR Genie telemetry privacy knobs, archive pass on test-asset list.
**Evidence**: no bus/report trace of rotation, knob settings, or archive pass since 2026-10-12. The newer frontify-mcp workstream (BSYS-29746 manifest, frontify-mcp UAT in the 00:29Z cortex pulse) is feature work, not the security item — a live plaintext Frontify token in an environment property is still unrotated.
**Recommended answer**: "Rotate the Frontify token now (dedicated path: new token → swap into env property → re-verify connection); set telemetry knobs to salted+k=5+90d retention; archive pass approved."

## Row 4 — estate-architect (206h) — ⚠️ STILL-OWED (reduced scope)
Row asked: verdict 3 triage cards + name a lineage folder.
**Evidence**: card 2 (OPS Listener 72253397 22% fail-rate) RESOLVED by watchdog live-verify 2026-10-13T04:05Z — fail rate is historical accumulation (10,954/49,262 lifetime; only 2 fails in last 30d, newest 2026-10-08, ticking green). Cards 1 (prod personal-connection remediation — 6 live personal connections incl. 'My Workato genie slack connection 14' 19182094, the 320-task billing-incident signature) and 3 (indexer last_run_at fix) have no verdict on record.
**Recommended answer**: "OPS Listener card closed (historical). Personal-connection remediation: proceed (swap to bot-owned connections per slack-bot-connection SOP). Indexer fix: approved."

## Row 5 — bus-clock-census (203h) — ✅ SUPERSEDED
Row asked: approval to edit bus_post.py:39 to UTC + line-75 cutoff.
**Evidence**: `scripts/bus_post.py` line 41 now stamps `dt.datetime.now(dt.timezone.utc)` with Z suffix; line ~77–79 cutoff likewise UTC, with a comment naming the exact skew this fixes. Live outboxes (session-shadow, brain-gardener) all stamp UTC-Z consistently as of 2026-10-20/21.
**Close as**: fix applied and verified live.

## Row 6 — regression-registry-hygiene (201h) — ❌ STILL-OWED (urgent if nightly re-arms)
Row asked: verdict on 6 removals/manual-only demotions + 3 empty-shell case deletions.
**Evidence**: the census (cortex/investigations/regression-unsatisfiable-tests.md, 2026-10-12) is the row's own source. Newer: the nightly itself was CronDeleted 2026-10-12 04:43Z by an agent misreading it as a duplicate and stayed off 4+ nights (cortex/investigations/regression-nightly-off-fleet.md, 2026-10-15) — so the false alarms are silent only because the suite is unloaded. Also 2026-10-16: the runner auto-seeded 6 open "Untitled test case 1" entries in canon.jsonl. The verdict is still owed BEFORE any re-arm, else re-arming resurrects 6 nightly false alarms.
**Recommended answer**: "Demote 82272814 / 82248514 / 82256903 to tag-and-skip (VUA-identity-unsatisfiable); delete the 3 empty-shell cases (82239660, 82727069, 82959480); then re-arm the nightly."

## Row 7 — manifest-order-verification (193h) — ✅ SUPERSEDED
Row asked: backfill BSYS-29488/29495/29499 manifest + build a periodic sweep for sessions dying before the Stop guard.
**Evidence**: `~/Documents/workbench/manifests/bsys-29488-29495-29499-backfill-2026-10-20.manifest.json` exists (dated 2026-10-20). The periodic sweep exists and runs — `reports/claims-sweep-latest.json` (regenerating; it now echoes this very row in its output).
**Close as**: both tails delivered.

## Row 8 — harness-benchmarking (193h) — ❌ STILL-OWED (or explicitly drop)
Row asked: post the LinkedIn reply + decide whether to build the follow-up method/raw-outputs post.
**Evidence**: no post on record anywhere (bus, slack-posts.jsonl, reports). bench4 results (harness 6.0 vs vanilla 4.5, vanilla confabulating task-billing) decay in value weekly.
**Recommended answer**: "Post the reply this week, or drop the follow-up post explicitly so the row can close."

## Row 9 — seismic-mcp / BSYS-29582 (190h) — ❌ STILL-OWED
Row asked: nightly registry policy for VUA-bound skills — tag-and-skip vs identity-carrying harness run; BSYS-29281 prod-import gate holds until nightlies run clean.
**Evidence**: this is the SAME policy decision still pending in rows 6 and 11 (the tag-and-skip vs identity question appears in three separate needs-josh rows). BSYS-29281 additionally parked 5d on Patricia's connection-naming answer (external, per garden-reports finding 2026-10-11). No verdict recorded anywhere.
**Recommended answer**: "Tag-and-skip for VUA-bound skills (matches the row-6 demotion); identity-carrying runs only when Josh explicitly asks for UAT-grade verification."

## Row 10 — gws-semantic-catalog-sync / BSYS-29585 (190h) — ✅ SUPERSEDED
Row asked: approve the dev build.
**Evidence**: the build landed without needing the row — newer registry row `escalation-82272892-contract-conflict` (2026-10-15) states "autopsy + fix already landed BSYS-29585"; and `google-workspace-semantic-mcp` Phase 2 (2026-10-20, state=done) authored both regression test cases on 82272892 (deleteContactPhoto double-row conflict reproducer + clean counter-test). 48h failure-free AC is the remaining check.
**Close as**: superseded — build approved-by-action, tested 2026-10-20. (Residual "verify-holding vs risk-accept" lives in the separate escalation row, not this one.)

## Row 11 — estate-monitor-harness-hook / BSYS-29604 (188h) — ❌ STILL-OWED (low urgency)
Row asked: (1) should the AHQ AI identity keep stop/starting the dev test recipe; (2) monitored scope vs unmonitored canary; (3) 20-min Slack-page hold for automated-identity stops.
**Evidence**: recipe 82256903 verified `running: True` live just now (wt recipes get, read-only); no error-guide fires recently — the cycling has quieted since Oct-12/13. But none of the three decisions was recorded, and the FIXLOOP GATE that exists in watchdog/ops-autopsy/jira-triage prompts came from this cluster without the scope/paging decisions.
**Recommended answer**: "Risk-accept the AHQ identity cycling; move 82256903 to an unmonitored canary scope; approve the 20-min automated-identity page hold."

## Row 12 — kb-wave3-sources (185h) — ✅ SUPERSEDED
Row asked: (1) commit or discard uncommitted code in ~/Documents/workato-kb; (2) live post-fix KB sync proof.
**Evidence**: `git -C ~/Documents/workato-kb status --porcelain` = 0 entries — tree clean, nothing left to commit/discard. The KB MCP server is connected and serving (session-start health check ✔) with eval indexes rebuilt (wave-3 closeout), i.e. a post-fix sync has plainly run since.
**Close as**: tail 1 resolved (clean tree); tail 2 satisfied by the live connected server + rebuilt indexes.

## Row 13 — harness-machine-health (175h) — ✅ SUPERSEDED
Row asked: approve repointing com.josh.session-shadow and com.josh.agent-command-watcher plists to a versioned interpreter + launchctl reload.
**Evidence**: both plists now pin `/usr/bin/python3` (session-shadow plist line 8 verified); both are loaded in launchctl with exit status 0 (`com.josh.session-shadow`, `com.josh.agent-command-watcher` both `0`); session-shadow auto-commits are visibly landing in the knowledge repo git log (5 most recent commits).
**Close as**: fix applied and verified working.

## Row 14 — seismic-test-recipe-loop (171h) — ❌ STILL-OWED (low urgency)
Row asked: fix path for AHQ identity cycling of recipe 82256903 — escalate / re-scope / risk-accept.
**Evidence**: this is the escalation-card twin of rows 9/11 — one underlying decision asked three times. Recipe verified running=True now; no recent incident fires. Interim mitigations (FIXLOOP GATE) live in prompts, but Josh's path choice was never recorded.
**Recommended answer**: "Risk-accept + re-scope to canary (single decision closes rows 9/11/14's shared question)."

## Row 15 — agent-gossip-bus (169h) — ❌ STILL-OWED
Row asked: re-scope the bus promise to broadcast+aggregate, OR enforce corroboration in agent prompts as a protocol step with teeth.
**Evidence**: bus remains healthy on traffic (~30–44 posts/day) but deliberation data was unchanged as of the Oct-13 census (138/141 finding-threads zero cross-agent response; corroboration 10×/7d). Agent .md files mention "corroboration" only as boundary text (e.g. brain-gardener: "post a bus corroboration post naming the dreamer's incomplete run") — no enforced protocol step. No re-scope on record.
**Recommended answer**: "Re-scope to broadcast+aggregate (cheapest, matches observed reality); revisit enforcement only if deliberation quality becomes a bottleneck."

---

## Pattern worth noting

One decision (nightly-registry policy for VUA-bound skills + the Seismic/AHQ test-recipe disposition) is pending across THREE rows (9, 11, 14) plus blocks row 6's re-arm. A single Josh verdict — tag-and-skip + canary re-scope + risk-accept — closes four rows at once. That cluster is the highest-leverage approval in the backlog.

## Suggested bulk-approve bundle (all one-liners)

1. "Lint: option B fine, close." (row 1 — merely confirm)
2. "INDEX line for agent-harness-operations; dedup exclusions approved." (row 2)
3. "Rotate Frontify token; telemetry salted/k=5/90d; archive pass approved." (row 3)
4. "Close OPS card; personal-connection remediation proceed; indexer fix approved." (row 4)
5. "Demote 3 VUA recipes, delete 3 empty shells, re-arm nightly." (row 6)
6. "Post LinkedIn reply or drop it." (row 8)
7. "Risk-accept Seismic/AHQ cycling, canary scope, 20-min page hold." (rows 9/11/14)
8. "Re-scope bus to broadcast+aggregate." (row 15)
