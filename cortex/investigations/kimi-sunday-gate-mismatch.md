# kimi Sunday lens-gate self-refusal — findings (read-only investigation, 2026-10-12)

Dispatched by cortex pulse 05:50Z (thread `kimi-sunday-gate-self-contradiction`),
from harness-dreamer bus line 2026-10-12T03:49:44Z. No code changed anywhere;
this file is the only write.

## 1. Exact locations

- Config/registry side: `~/Documents/workato-kb/kb/lens_call.py:122-126` —
  `tonight_kimi_lens()`. Line 124 `if day == 6:` (0=Mon .. 6=Sun), line 125
  returns `"ALL (Sunday deep pass — full board on the frontier model)"`.
- Gate side: `~/Documents/workato-kb/kb/lens_call.py:130-135` — inside `call()`.
  Line 131 fetches `lens_tonight = tonight_kimi_lens()`; line 132 is the
  predicate `if lens_tonight != "ALL" and lens_tonight != persona:`; line 134 is
  the refusal string ending "...(or wait for the Sunday full-board pass)".
- Registry display (where the dream report read `kimi_lens_tonight` from):
  `kb/lens_call.py:153` — `--models` prints the same decorated Sunday string.
- Consumer contract: `~/.claude/agents/harness-dreamer.md:115-126` — the dreamer
  is told "the Sunday deep pass is the full board on Kimi" and calls
  `python -m kb.lens_call --model kimi --persona <each>` per persona.

## 2. The predicate mismatch

Both sides share the SAME day check — the gate has no independent Sunday test;
it calls `tonight_kimi_lens()`, the same function the registry prints. The
mismatch is in the SENTINEL, not the calendar:

- Sunday, the advertise path returns a SUFFIX-DECORATED string:
  `"ALL (Sunday deep pass — full board on the frontier model)"`.
- The gate compares exact equality against the bare sentinel `"ALL"`.
- So on Sunday for ANY persona: `lens_tonight != "ALL"` is True (the suffix
  makes them unequal) AND `lens_tonight != persona` is True -> refuse.
- The gate IS the Sunday pass: the "wait for the Sunday full-board pass" advice
  is emitted on Sunday, pointing at the thing currently refusing. The weekly
  kimi deep pass is unreachable by construction (dreamer confirms glm/deepseek
  covered 2026-10-11).

One-line characterization: the allow-all sentinel leaks a display suffix into
the enforcement comparison.

## 3. Minimal fix — one line, gate side (`kb/lens_call.py:132`)

    before: if lens_tonight != "ALL" and lens_tonight != persona:
    after:  if not lens_tonight.startswith("ALL") and lens_tonight != persona:

Recommended over the alternative because it preserves the registry display the
dream report quotes verbatim. Equivalent one-line config-side alternative:
line 125 -> `return "ALL"` (and move the decoration into the `--models` print at
line 153) — but that changes the registry string consumers already read.
Suggested regression probe: fake the date to `weekday() == 6` and assert
`call('kimi', persona)` returns a `model`/`text` key (not `skipped`) for every
persona in `PERSONAS`.

## 4. Same-shape scan (other day-of-week / persona pairs)

- Weekday rotation is SOUND: `KIMI_ROTATION` (line 31) returns bare persona
  keys; all 7 (artist, contrarian, musician, doctor, ceo, analogist, cto) are
  exact `PERSONAS` keys, so the `!= persona` comparison matches on weekdays.
- The 5 personas NOT in the rotation (lawyer, engineer, accountant, pm,
  architect) are refused kimi on all six weekdays — same refusal shape, but
  by design (rotation names 7 of 12), and post-fix they would be allowed on
  Sunday, matching "full board".
- No other sentinel-comparison day gates in the kb repo: `kb/sync.py:120` uses
  `weekday() == 6` as a positive Sunday trigger for jira-cases (no sentinel
  compared) — healthy.
- Adjacent latent risks (different bug class, NOT this gate's shape, no day
  logic involved):
  - `kb/gym_judgment.py:63` imports `_call` directly, bypassing the cost gate
    entirely; the judge default is deepseek, but a caller passing
    `judge_model="kimi"` would escape governance.
  - The Agent-tool `model` override path (harness-dreamer.md subagent lenses,
    opus/fable -> kimi-k3) is a second kimi dispatch path the lens_call gate
    does not cover at all.

## Status

Already open as triage row `kimi-sunday-lens-gate-mismatch`
(`triage/queue.jsonl:175`, cortex-sourced, status open). This file supplies the
fix-ready line references; the one-line gate fix awaits Josh's dev gate.
