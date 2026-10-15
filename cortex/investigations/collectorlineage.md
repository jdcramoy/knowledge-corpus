# Collector copy lineage 82862205 vs 82178793 — RESCUED from dispatch log
_Dispatch 2026-10-10T06:33Z (autopsy lookup). Findings-file write was blocked by the headless sensitive-path gate; persisted by the cortex pulse 07:40Z from dispatch-20261010-063348-collectorlineage.log._

[claude-code:unrecognized_model] {"model":"fireworks/glm-5.3-flash","query_source":"sdk"}
The append was denied by the write gate — per your instructions I did not bypass it, so here are the full findings inline.

# Lineage findings: 82862205 vs 82178793

## Headline: they are not copies of each other

The "same name" is a near-name collision (plus dashboard truncation "Conversation Event Coll."). Live names from `recipe_get` on the DEV AIRO MCP:

| | 82862205 | 82178793 |
|---|---|---|
| Live name | REC \| HR Genie \| **Conversation Event Collector** | REC \| HR Genie \| **Conversation Tool Event Collector** |
| Folder | 35712141 (Intelligence Platform) | 32985204 (Operational Monitoring) |
| Project | 15643451 (shared) | 15643451 (shared) |
| Running | True, 15-min scheduler | True, 15-min scheduler |
| Job history | 324 jobs, 23 failed | 2,985 jobs, 19 failed |
| Scope | ALL conversation events, masked+classified in-job, emits to App Event Ledger via shared emitter FUNC 82862028 | ONLY terminal `tool_execution_completed` events, privacy-minimized, upserts legacy table 145706 |
| Collector State key (table 156849) | `conversation_events` | `conversation_tool_events` |

**Lineage:** 82178793 is the legacy/v1 tool-only writer (older, 10× the job history, legacy folder + legacy table). 82862205 is the newer v2 full-conversation collector. Both are independently live, independently ticketed under BSYS-29488 (plan sections A.1/A.2 repair them as separate collectors). Neither is a versioned copy or backup of the other — there is exactly one live copy of each.

## Q1 — which is canonical/live

Both are live but different generations:

- **82862205 = canonical conversation-event telemetry.** Post-fix scheduler runs are green: j-AbsmHw49 (06:24:38→06:25:03Z today) succeeded; the last failure was j-AbskKeQa at 05:24Z, *before* the final pushes. Ledger correction to the prompt's premise: the repair session pushed **8 times, not 3** — 04:21, 04:24, 04:29, 04:44, 05:06, 05:23, **05:37, 05:48**Z (the fix-state file's 06:00Z evidence window ended at ledger line 5858 and missed the last two). The **05:37/05:48 pushes are the phantom-row fix**: live code now shows step 14 as an `if page.size > 0` guard ("an empty page must not fabricate a blank phantom conversation") with the insert moved to step 15. The `COLLECTOR_ALL_CONVERSATIONS_SKIPPED` crash class is fixed in live code and 3+ consecutive scheduler runs succeeded since.
- **82178793 = legacy tool-event writer, live but unhealthy operationally.** Jobs run ~24 min against a 15-min trigger (back-to-back chain j-AbskAABx → j-Abskrkcw), and one hung "Processing event" job j-Abskrmw8 started 06:22:44Z with no completion — the known no-leader-election overlap issue from the BSYS-29488 plan.

## Q2 — does 82178793 carry the blank-id phantom-row defect?

**No.** It is structurally incapable of it:

- It never blind-inserts `data[0]` into a list. Both page fetches (steps 19/27) pass the raw page to a Ruby validation snippet (steps 20/28) that raises `CONV_PAGE_EMPTY_RESPONSE`/`EVT_PAGE_EMPTY_RESPONSE` on a blank body, `CONV_PAGE_MALFORMED`/`EVT_PAGE_MALFORMED` on non-array data, and builds the batch only from actual page rows.
- It has an `EVT_MISSING_ID` guard that **raises** on blank event_ids — the opposite posture to the phantom bug.
- An empty page yields `batch=[]` → foreach no-op. No blank row, no 1970-01-01 timestamp, and `COLLECTOR_ALL_CONVERSATIONS_SKIPPED` exists nowhere in its code.
- Its real residual failures are `CONV_PAGE_MALFORMED` transients (live at 01:06Z, j-Absk4hA3) and the hung-job overlap — both already scoped in plan A.1a/A.1c.

## Q3 — does the active work risk a split fix?

**No split-phantom-fix risk** — the defect only ever existed in 82862205 and is already fixed and observed-green there; 82178793 needs no phantom fix.

**But a real coordination risk exists, different in kind.** The ledger shows **five** sessions have touched 82178793 today: `repair` (push 04:32Z), `rebind-20261010b` (04:39, 04:45Z), `repair2` (05:06–05:10Z), `landing` (push 05:58:46Z), and `hrg-coll-82178793-v3-20261010` — which began 06:27:58Z and **is mutating the recipe right now** (42 mutations, last entry 06:35:59Z: a remove_step sweep then add_step/set_input_field rebuild, **zero pushes so far**). The snapshot I read is the 05:58Z "landing" state; v3 is unpushed and in-flight. Risks:

1. **Session-stacking on one recipe** — the plan's own addendum warned "one session per recipe." A half-rebuilt v3 push would take the legacy tool collector down while v2 is healthy, splitting telemetry coverage.
2. **Guard-logic divergence** — the two collectors implement similar protections (cursor-cycle, page validation, checkpoint-hold) in different shapes; a fix proven on one does not transfer automatically. Any future "port the fix" work must diff both, not assume parity.
3. The v3 add/remove pattern suggests a large restructure mid-flight — its first push should be read back fully (and diffed) before anything is declared done on 82178793.

## Verdict

- Canonical: **82862205** (v2, healthy post-fix, phantom row fixed at 05:37/05:48Z pushes, green since). Legacy: **82178793** (v1, live, mid-restructure by the v3 session right now).
- No versioned-copy relationship — name collision only.
- Phantom defect: fixed in 82862205, never present in 82178793.
- Active BSYS-29488 work on 82178793: no single-copy-fix risk on the phantom class; the live risk is the five-session pile-up and the unpushed in-flight v3 rebuild.

The findings file write was blocked by the sensitive-path gate as anticipated; this reply is the full record. Nothing was changed anywhere — read-only throughout (no recipe edits, no prod touches, no stops/starts).
