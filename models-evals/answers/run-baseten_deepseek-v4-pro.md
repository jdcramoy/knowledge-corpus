## 1. TOP IDEAS

1. **Value Receipts, not just build reports**  
   Every Doer fix produces a machine-readable receipt: failure signature, estimated recurrence frequency, business impact, diff hash, risk score, token cost, and predicted recurrence.  
   *Why it compounds:* Turns the platform from “AI fixed a ticket” into “AI avoided $X/month in repeat failures.” Dreamer can rank proposals by value; leadership gets ROI.  
   *Cheap to build:* You already log action/why/confidence, have Jira tickets, and can add a value judge on top.

2. **Autonomy Credit Score per recipe/project**  
   Compute 0–100 from first-pass fix rate, reviewer reject rate, human revert rate, failure recurrence, KB freshness, and route risk. Use it to gate autonomy: 80+ full 3 passes; 40–79 propose-only; <40 human-required.  
   *Why it compounds:* Trust becomes operational, not anecdotal. Stops the AI from thrashing on known-bad recipes and gives humans a clear signal.  
   *Cheap:* Every input already exists in your audit rows, grades, and Build Memory.

3. **Shadow Doer / Proposed-Diff Mode**  
   For risky or first-time fixes, Doer runs non-mutating: it generates a patch proposal and predicted behavior on a copied recipe/workspace. Human reviews diff before any mutation even in AI environments.  
   *Why it compounds:* Prevents containment breaches, creates a rich dataset of accepted/rejected diffs, and lowers the fear of letting AI touch builds.  
   *Cheap:* Point executor at a duplicate workspace; reuse diff hash and manifest tooling.

4. **Red Team Genie in the loop**  
   After Doer but before reviewer, add a third adversarial Genie that tries to break the proposed fix using historical failures, edge cases, route gotchas, and malformed inputs. Outputs a break report.  
   *Why it compounds:* Reviewer stops being a style-check and becomes evidence-based. Catches regressions before human time is spent.  
   *Cheap:* Use same executor in read-only test mode with a different prompt/model.

5. **Live Runbook Cards**  
   When Doer finishes, send an interactive Slack/Teams card: diff summary, confidence, cost, risk, affected recipes, buttons Approve / Request Changes / Deploy to AI Prod / Escalate. Capture reject reason as structured feedback.  
   *Why it compounds:* HITL goes from Jira tab friction to two-tap decisions; every click is labeled training data.  
   *Cheap:* Slack webhook + Jira API; build report already exists.

6. **Estate Watchtower (proactive trigger surface)**  
   Stop waiting for failures. Scheduled scans compare recipe/connection metadata to Workato changelog, connector deprecations, schema drift, and unused recipes. Raise pre-failure tickets with affected recipes and recommended actions.  
   *Why it compounds:* Shifts from reactive firefighting to preventive maintenance; increases platform value beyond incident response.  
   *Cheap:* You already have route catalog + Workato audit API access.

7. **Knowledge Debt Ledger**  
   Each KB doc/route spec tracks last used, last confirmed, yield (how often it contributed to a successful fix), and how many times it was implicated in wasted passes. Stale or low-yield docs auto-flag for curation. Doer can propose KB edits as first-class outputs.  
   *Why it compounds:* Prevents knowledge poisoning and keeps the estate sharp; bad docs stop silently hurting fixes.  
   *Cheap:* Log retrieval IDs and increment counters per pass.

8. **Revert/Thrash Memory**  
   Capture every human revert or edit of an AI change as a high-priority memory. If a new failure matches a known thrash signature, force propose-only or STOP-and-escalate.  
   *Why it compounds:* Prevents repeating expensive mistakes; gives reviewer and Doer strong negative examples.  
   *Cheap:* Audit logs already track state changes; just add a revert event type.

---

## 2. INTELLIGENCE LAYER DEEP-DIVE

### Capture
- **Action events:** actor (Doer/reviewer/Red Team/Dreamer), ticket ID, recipe/project ID, route/method/path, request body hash, response hash, model + prompt hash, KB doc IDs/versions retrieved, token usage, latency, confidence score, why, evidence refs, before/after asset manifest hash, build report ID.
- **Human decisions:** approve/reject/edit/revert/promote, reason, timestamp, and which AI pass it refers to.
- **Disagreement log:** Doer vs reviewer vs Red Team conflicts, including exact diff points and reviewer rejection reasons.
- **Environment snapshot:** Workato project version, recipe export hash, connection names, failure signature, and recent changes.
- **Critical:** Capture at source immediately. Do not rely on Agent Studio event API retention. Store in your own data table; retain raw events for at least 90 days, aggregated trends indefinitely.

### Judge
- **Technical judge:** Did the fix resolve the failure? Did it introduce regressions? Does it pass Red Team? Use deterministic checks from Workato run history plus adversarial eval.
- **Value judge:** Estimate business impact using recurrence frequency, severity, affected recipes, and compare to actual token/compute cost.
- **Pass-level judge:** Score each of the max 3 Doer passes 0–1 for progress. Two scores below threshold = thrash; force STOP or propose-only.
- **Human judge is ground truth:** Every human override/revert/re-grade becomes a labeled example. No human action is neutral; all are data.

### Rollup
- **Conversion funnel:** detected → triaged → Doer attempted → reviewer approved → human approved → promoted to real production → recurrence-free for 30 days.
- **Metrics by slice:** first-pass fix rate, reviewer reject rate, human revert rate, MTTR (detection to promotion), recurrence rate, token cost per verified resolved incident, autonomy credit distribution, value receipt sum.
- **Weekly digest:** top 3 wins (high value, low cost), top 3 thrash cases, top 3 knowledge gaps, and top 3 recipes with declining autonomy score.

### Mine
- **Knowledge Gap Miner:** Routes/errors with repeated failed passes or human intervention → new KB docs or route gotchas.
- **Thrash Miner:** Cluster sequences where 3 passes still failed. Auto-escalate those signatures; block autonomous future attempts.
- **Value Miner:** Find high-cost recurring failures solved cheaply by AI vs low-value failures where AI spends too much tokens. Use this to tune autonomy budgets.
- **Autonomy Miner:** Identify recipe clusters ready for more autonomy or needing permanent human gating.
- **Eval dataset builder:** Every human-adjudicated case becomes a regression example. Hold out by time, not random split. Run before every Doer/reviewer model or prompt change. This is the single most important intelligence-layer component; without it, you are tuning in production.

### Analyst Genie
- Queries the telemetry data table in natural language. Example queries: “Which recipes have worsening autonomy scores?”, “What were the top reviewer rejection reasons this week?”, “What is cost per value receipt by domain?” Outputs Slack digests and dashboard-ready numbers.

---

## 3. GAPS

- **No eval harness before first Doer deployment.** You will burn trust and tokens tuning prompts in production. Build a regression dataset from Triage Genie historical tickets immediately.
- **No per-incident token/cost budget or kill switch.** Max 3 passes/2 reviews can still blow hundreds of dollars per ticket. Set hard caps per severity and a global monthly budget.
- **No sandbox parity fixtures.** “Dedicated AI environments” may not mirror production connections, data shapes, or rate limits. Fixes will pass in AI env and fail in real production. Create synthetic fixtures or mirrored recipe copies.
- **Human feedback capture is not explicit enough.** “Human reviews” is not a data contract. Require structured reject reasons, revert capture, and a one-click “this fix was wrong” signal.
- **Knowledge KB freshness/versioning not operationalized.** Many small KBs will drift. Without a freshness ledger and owner per KB, Doer will act on stale specs.
- **Static route guardrails are insufficient.** Allow/deny lists miss dangerous side effects. Route risk should be dynamic: publish, delete, connection edits, and batch mutations need higher risk scores and extra human gates.
- **No rollback audit for partial mutations.** If the executor makes a multi-step change and fails midway, audit rows may not reconstruct final state. Log every mutation attempt with before/after hashes and a rollback action.

---

## 4. RISKS

1. **Success theater / deployment gap.** Doer produces plausible fixes that pass reviewer but never get promoted to real production, or fail after promotion. Dashboards show high approval rates and low MTTR, but actual recurrence in production is unchanged. The platform quietly becomes a very expensive ticket commenter.  
2. **Self-reinforcing knowledge drift.** Build Memory and lessons are written by the same Genies that use them. If adversarial review is weak or human sampling is absent, models learn to satisfy reviewer approval rather than solve real failures. Confidence scores stay high while actual quality degrades; nobody notices because the numbers look good.

---

## 5. METRICS

1. **Verified production resolution rate:** % of AI-built fixes promoted to real production and recurrence-free for 30 days. This is the only number that proves actual value.  
2. **Median MTTR from detection to production promotion**, compared to historical human baseline for the same failure archetype.  
3. **Human rework rate:** % of AI-approved fixes later reverted/edited by a human. Low is good; a very low number combined with low verified resolution rate means humans are rubber-stamping.  
4. **Cost per verified resolved incident:** total token + compute + human review time, divided by number of verified production-resolved incidents. Compare against value receipts.  
5. **Autonomy score calibration gap:** difference between reviewer confidence/grade and actual production success. If high-confidence fixes still require human rework >10% of the time, the AI’s self-assessment is untrustworthy.