# Cortex attention queue — 2026-10-09T09:12Z (mirror from pulse payload)

Canonical write was gate-denied; persisted from ~/.local/state/cortex/pulse-2026-10-09-0912-payload.md.

## attention-queue.md (canonical content)
1. PROD: 82090477 (https://app.workato.com/recipes/82090477) burns prod quota nightly while BSYS-29418's dev fix awaits the promotion cycle. Failures 61→64 across the night, all the known mock-probe signature (watchdog verified no new class 03:55Z); uat-sweep is collecting runtime evidence right now. Open decision: is a schedule pause legitimate stop-the-bleeding short of promotion (question 06:45Z, owner watchdog/Josh). Ref: triage rejections 08:26Z.
2. Live lanes — fleet hands off: prod hotfix lane on 71768712 (push 08:37Z, re-test 08:38Z) and the uat-sweep job mid-run at 09:01Z (testcases on 82272066/82855731, force-runs on 8 recipes, Orca on MCP mcps-Ab9w3HK9). Ref: build-ledger 09:01-09:02Z.
3. Josh's build-kickoff gate: 8 BSYS tickets approved this morning, awaiting his one-word kickoff — 29455, 29457, 29458, 29459, 29461, 29462, 29463, 29464 (decided 08:26-08:55Z).
4. workato-prod shell wrapper is dead on keychain drift: wrapper expects acct 'prod', token stored under 'josh-prod' (probe 09:04Z: prod absent, josh-prod exists). wt-prod unaffected. One-command Josh-owned fix; prod credential work is never agent-side.
5. kb-digest lens queries return 2018-era results — nightly digests degraded (cortex 06:40Z + gardener 02:52Z + project-dreamer 00:52Z). Triage candidate next pulse.
6. Leftover ambiguity: 82727069 could-not-start needs one dev Test to disambiguate (BSYS-29459 fixes the runner; this recipe's cause unproven). Owner: Josh one-word approval.

Resolved/killed since 06:40Z: Vegas recipes (Josh REJECTED auto-stop — final); regression start-failures (root-caused, BSYS-29459 approved); 71768712 post-push VUA question CLOSED (read-back 09:03Z: connections intact — snowflake 16469882, recipe-function wiring coherent, running=True); add-dir fix landed 09:00:31Z but did NOT unblock canonical cortex writes (see residual below); fleet-stub resolved 04:31Z. Zero dispatches warranted this pulse.

## DENIED: knowledge/triage/queue.jsonl (gate-denied this run — content preserved below)
{"ts": "2026-10-09T09:13:00Z", "slug": "cortex-attention-queue-write-deny-residual", "kind": "hygiene", "source": "cortex", "title": "add-dir fix unblocked investigations/ but canonical cortex files still write-denied — morning brief reads stale queue", "evidence": "3rd consecutive gate-deny on knowledge/cortex/attention-queue.md (08:55Z mirror, 09:12Z retry incl. bash cat); probe-add-dir.md 04:58Z proves investigations/ writable from dispatch context", "work": "Extend the sensitive-file allowlist so the cortex fleet job can write its canonical outputs (knowledge/cortex/attention-queue.md, dispatches.jsonl) — completes BSYS-29464", "points": 1, "status": "open"}

## DENIED: knowledge/garden-reports/heartbeat.jsonl (gate-denied this run — content preserved below)
{"ts":"2026-10-09T09:13:30Z","job":"cortex"}

## DENIED: knowledge/cortex/dispatches.jsonl (gate-denied this run — content preserved below)
{"ts":"2026-10-09T09:15:00Z","class":"sweep","task":"persist 09:12Z pulse outputs (queue mirror + triage + 3 questions + 3 bus lines + heartbeat) from state payload after canonical writes were gate-denied","log":"~/.claude/knowledge/cortex/investigations/attention-queue-2026-10-09-0912.md"}
