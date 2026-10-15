=== mirror ===
# Attention queue — rebuilt 2026-10-09 08:50Z (cortex pulse)

> MIRROR FILE: the gate denied the write to the canonical attention-queue.md this pulse
> (same class as triage slug cortex-dispatch-add-dir-fix). Next pulse / morning brief:
> promote this file's top 3. Josh: approving the add-dir fix ends these mirrors.

1. **LIVE FRONT: prod hotfix on [71768712](https://app.workato.com/recipes/71768712) mid-flight right now** — build ledger 08:26-08:38Z shows Orca Test fired, `wt-prod` start/stop, `recipe_builder_push` (session hotfix-71768712-slim), Orca re-test firing. Do not touch or dispatch against this recipe. Standing rule applies: verify VUA/connection mode via read-back once the hotfix settles. Ref: build-ledger tail 08:37Z.
2. **BSYS-29418: dev fix on [78677477](https://app.workato.com/recipes/78677477) structurally in but runtime-unproven** (zero post-fix jobs as of 01:25Z). Prod [82090477](https://app.workato.com/recipes/82090477) keeps failing on mock 403 probes until it ships — health sweep still flags it hourly (latest 06:31Z). One dev Test + Josh's prod-promote gate closes it. Ref: investigations/78677477-dev-fix-verification.md.
3. **Regression runner registry-cache bug is now the only real defect from the nightly "3 of 4 could not start" scare** — autopsy (06:35Z dispatch) verdict: 82273581/82794233 test cases were deleted under Josh's own accepted 10-08 triage verdicts and the runner's registry cache keeps case-less recipes in the run set, so the errors repeat nightly until fixed; 82727069's cause still ambiguous (needs one write-capable dev Test to disambiguate). Findings rescued to investigations/regression-start-failures-2026-10-09.md this pulse. Open triage: regression-runner-registry-cache-bug.
4. **CLAIM LEDGER LOOP: clm-001 (vua-persistence-after-push) reverify CONFIRMED 2026-10-08 (investigations/clm-001-vua-persistence-reverify.md) but the claim's last_verified still reads 2026-10-06** — so the dreamer's workshop re-queues it every ~2h against a claim that was actually verified. Gardener action: bump last_verified from the investigation. Cortex never promotes claims. Ref: dreamer workshop lines 06:28Z-23:59Z.
5. **Dispatch add-dir fix still pending Josh (open triage: cortex-dispatch-add-dir-fix).** Built-in sensitive-file gate denies headless Write to knowledge/cortex/ root files; every dispatch needs the stdout-rescue workaround (done manually for two reports now, latest this pulse). Fix is `--add-dir "$HOME/.claude/knowledge"` in the fleet cortex prompt + one probe. Ref: dispatch-20261009-022333-gaterule.log.
6. **Ledger blind spot: [DRIFT FIX] project 10593549 and BTSUP-72246 prod fleet 82917288-90 have zero build-ledger entries** — multi-agent ledger is convention-only at write time. Open triage: drift-fix-project-unledgered; fix is a write-path enforcement proposal for the dreamer queue. Ref: watchdog-2026-10-09 P2#2.
7. **IDENTITY: List_Design_Systems VUA flag is WRONG (single tool, not a class — parity sweep 60/62 VUA-Yes, the VUA-No pattern is caller-data-free tools which this violates).** Needs Josh-approved flag fix (prod write) or documented exception. Open triage: listdesignsystems-vua-flag-fix. Ref: investigations/mcp-vua-flag-parity-sweep.md.

Filed to triage this pulse: none (no new work-shaped items; all open slugs current).

Decided/parked, not slots: Vegas demo recipes — Josh REJECTED auto-stop 03:50Z; fresh read this pulse: all 8 (82641521-28) still running, 82641528 newest job 01:37Z. Decision respected; item closed pending reversal. Regression start-failures resolved by autopsy (see item 3). 82090477 = known mock-probe class (BSYS-29418). Fleet-stub false alarm resolved 04:31Z. AI-judge-as-prod-gate parked (dissenter FATAL).

## Cost governor
_cost-governor.py 2026-10-09 — proposals only; Josh approves any routing edit._

- No budget alarms this window (median spend proxy 5,184).
- DOWNGRADE TRIAL: `judgment` on kimi-k3 shows pass 100% over 9 runs at the class's highest cost — propose an A/B trial on glm-5.3-flash (Josh approves).
- INSTRUMENTATION: brain-guard has logged 617 turn-usage lines with in/out token counts but NO job/class/model field, so per-class token cost is a proxy. Propose: brain-guard adds job+model to turn-usage lines.
- FLYWHEEL GAP: no outcomes ledger exists yet for verified-pass posteriors; when the failure-flywheel write-back ships its outcomes jsonl, this governor consumes it first.
- Full table: garden-reports/cost-governor-2026-10-09.md
