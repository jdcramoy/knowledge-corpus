# Workato Dev KB — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the installable internal knowledge pack `workato-dev-kb` (RAG++ + fractal + curated playbooks) with a kit-grade hardened installer, plus the `pack-export` bridge from Josh's private KB repo.

**Architecture:** Two repos, one boundary. Josh's private `~/Documents/workato-kb` stays upstream for pipeline code; a new export script strips the two sensitive sources (confluence, harness) and copies generic code into `~/Documents/workato-dev-kb`, which carries curated content by explicit promotion only. Nothing syncs from `~/.claude` into the pack; the first push to GitHub is Josh-gated.

**Tech Stack:** Bash (macOS 3.2-compatible), Python 3.12 venv, sqlite-vec + bge models, FTS5, git hooks.

**Spec:** `~/.claude/knowledge/specs/2026-10-10-workato-dev-kb-design.md` (read both; the spec's privacy guarantee and install-hardening sections are binding).

## Global Constraints

- Repo lives locally at `~/Documents/workato-dev-kb`. NO remote, NO `gh repo create`, NO push until Josh approves the first push.
- The pack NEVER contains: BT Confluence content, `harness://` source, people files, Josh's workspace/recipe/table IDs, `~/.claude/knowledge` paths, personal names, Jira keys from his estate (BSYS-####, etc.).
- Pack code must not reference the confluence/harness sources at all (not stubbed — absent), so no import path can resurrect them.
- Bash must run on macOS default bash 3.2 (no `mapfile`, no `${var,,}`). Python: 3.12 only (torch has no 3.14 wheels).
- Kit hardening parity (from `~/Documents/agentic-workato-kit/install.sh`): `set -euo pipefail`, tee'd timestamped log, STEPS/CURRENT_STEP/COMPLETED/DEGRADED tracking, EXIT trap report, ERR trap, `with_retry` + `classify_failure`, `fix_or_fail` interactive/headless, idempotent re-runs.
- Every git commit ends with `Co-Authored-By: Claude Code <noreply@anthropic.com>`.
- Execution lanes (Josh's agent-swarm rule): Tasks 1–2 (lane B), Task 3 (lane A, private repo), Tasks 4–7 (lane B, after 1), Task 8 is Josh-gated, Task 9 needs all lanes. Lanes A and B touch disjoint repos — run in parallel.

## File Structure

```
~/Documents/workato-dev-kb/          # NEW repo (this plan)
├── install.sh                       # hardened installer (Tasks 5–6)
├── verify.sh                        # doctor (Task 7)
├── README.md
├── .gitignore
├── config.example.sh
├── sources/public.json              # enabled public-source sync config
├── kb/                              # exported by pack-export (Task 3) — never hand-edited
├── knowledge/
│   ├── INDEX.md
│   ├── memory-rules.md
│   └── domains/                     # promoted, generic-form playbooks (Task 8)
├── skills/                          # promoted skill packs (Task 8)
└── .githooks/pre-push               # secret scan (Task 2)

~/Documents/workato-kb/              # PRIVATE repo (Task 3 only)
└── scripts/pack-export.sh           # the only automated path between repos
```

---

### Task 1: Repo scaffold + git init (lane B)

**Files:**
- Create: `~/Documents/workato-dev-kb/README.md`, `.gitignore`, `config.example.sh`, `sources/public.json`, `knowledge/INDEX.md`, `knowledge/memory-rules.md`, `knowledge/domains/.keep`

**Interfaces:**
- Produces: repo root other tasks assume; `sources/public.json` consumed by the first-sync step (Task 6) as `["docs","changelog","blog","inspiration","github","eip","claude"]`.

- [ ] **Step 1: Create the tree and git init**

```bash
mkdir -p ~/Documents/workato-dev-kb/{sources,knowledge/domains,skills,.githooks}
cd ~/Documents/workato-dev-kb && git init -b main
```

- [ ] **Step 2: Write `.gitignore`** — install-local state never commits:

```gitignore
install-logs/
.venv/
__pycache__/
*.pyc
config.sh
.DS_Store
```

- [ ] **Step 3: Write `config.example.sh`**

```bash
# workato-dev-kb consumer config. cp config.example.sh config.sh and edit.
KB_INSTALL_DIR="$HOME/.claude/workato-kb"   # corpus + index data root
KB_PORT=8765                                # daemon port (daemon optional)
```

- [ ] **Step 4: Write `sources/public.json`** — the single place source enablement lives:

```json
{"sources": ["docs", "changelog", "blog", "inspiration", "github", "eip", "claude"],
 "excluded_by_design": ["confluence", "attachments", "harness"]}
```

- [ ] **Step 5: Write `knowledge/INDEX.md`** — router with one placeholder line per future promoted file (Task 8 replaces `Placeholder — pending promotion`):

```markdown
# Workato Dev KB — knowledge index

One line per file. Read the line, then the file.

## Domains
- (Placeholder — pending promotion)

## Rules
- memory-rules.md — how to author files here so the fractal layer indexes them (one file one topic, ## sections written AS queries, INDEX line per file)
```

- [ ] **Step 6: Write `knowledge/memory-rules.md`** — port the memory-authoring rules block from `~/Documents/agentic-workato-kit/kb-pipeline/INSTALL.md` ("Memory-authoring rules" section), de-personalized (drop "your brain/memory rulebook" phrasing, keep the five rules verbatim otherwise).

- [ ] **Step 7: Write README.md** — sections: what this is (one paragraph: RAG++ + fractal + curated playbooks over public Workato sources), 3-command quickstart (clone / `./install.sh` / `kb "<query>"`), source table (public only, mirror the spec's layout section), what is deliberately NOT here (BT Confluence — deferred tier), provenance line ("content is curated and generic-form; not a mirror of any internal wiki").

- [ ] **Step 8: Commit**

```bash
cd ~/Documents/workato-dev-kb
git add -A && git commit -m "chore: scaffold workato-dev-kb repo

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 2: Secret-scan pre-push hook (lane B)

**Files:**
- Create: `~/Documents/workato-dev-kb/.githooks/pre-push`, `.githooks/patterns.txt`
- Test: scan behavior verified against fixture files in `/tmp` (throwaway)

**Interfaces:**
- Produces: hook active via `git config core.hooksPath .githooks`; exit non-zero blocks the push; `patterns.txt` is the allowlist-editable leak-class file later tasks depend on.

- [ ] **Step 1: Write `patterns.txt`** — one regex per line, comment lines start with `#`:

```bash
# workspace/asset numeric IDs in workato URLs
workato\.com/(recipes|data_tables|folders|jobs)/?[0-9]{6,}
# bare large IDs that are Workato asset-shaped (tune on false positives)
# personal names blocklist lives in .githooks/names.txt (one per line)
# internal jira keys from Josh's estate projects
\b(BSYS|HROPS|PSY?M|AAI|CT)-[0-9]+\b
# people-file paths
knowledge/people/
\.claude/knowledge/people
```

- [ ] **Step 2: Write `names.txt`** — seed with Josh's own name and direct ring (verify against `~/.claude/knowledge/people/README.md` at execution time; one full name per line, e.g. `Josh Cramoy`). This file is the one intentional place a name appears in the repo — it lives in `.githooks/` and exists to BLOCK names elsewhere.

- [ ] **Step 3: Write the hook**

```bash
#!/usr/bin/env bash
# pre-push secret scan — blocks pushes containing leak-class content.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0
while read -r local_ref local_sha remote_ref remote_sha; do
  [ "$remote_sha" = "0000000000000000000000000000000000000000" ] && base=$(git rev-parse "$local_sha" ^ 2>/dev/null | tail -1) || base="$remote_sha"
  # files added/modified between remote and local
  for f in $(git diff --name-only "$base" "$local_sha" 2>/dev/null); do
    [ -f "$f" ] || continue
    while IFS= read -r pat; do
      case "$pat" in \#*|"") continue;; esac
      if grep -qiE "$pat" "$f" 2>/dev/null; then
        echo "BLOCKED: $f matches pattern: $pat"
        fail=1
      fi
    done < .githooks/patterns.txt
    while IFS= read -r name; do
      [ -z "$name" ] && continue
      if grep -qi "$name" "$f" 2>/dev/null; then
        echo "BLOCKED: $f contains personal name: $name"
        fail=1
      fi
    done < .githooks/names.txt
  done
done
[ "$fail" -eq 0 ] && echo "secret-scan: clean" || echo "secret-scan: FIX the files above or remove them from the push"
exit "$fail"
```

- [ ] **Step 4: Activate + fixture-test**

```bash
cd ~/Documents/workato-dev-kb
git config core.hooksPath .githooks && chmod +x .githooks/pre-push
printf 'see https://app.workato.com/recipes/82862205 for details\n' > /tmp/leak-fixture.md
grep -qiE 'workato\.com/(recipes|data_tables|folders|jobs)/?[0-9]{6,}' /tmp/leak-fixture.md && echo "scan pattern matches (expected)" || { echo "PATTERN BROKEN"; exit 1; }
grep -qi "Josh Cramoy" /tmp/leak-fixture.md || echo "name check correctly silent on this fixture"
rm /tmp/leak-fixture.md
```

Expected: `scan pattern matches (expected)` printed.

- [ ] **Step 5: Commit**

```bash
git add .githooks && git commit -m "feat: pre-push secret-scan hook (leak-class patterns + names blocklist)

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 3: `pack-export.sh` in the PRIVATE workato-kb repo (lane A)

**Files:**
- Create: `~/Documents/workato-kb/scripts/pack-export.sh`
- Modify: `~/Documents/workato-kb/README.md` (one line under a new "Export" heading)

**Interfaces:**
- Produces: `~/Documents/workato-dev-kb/kb/` populated with the pipeline minus sensitive sources; exit non-zero if the target dir doesn't look like the dev-kb repo (guard against exporting anywhere else).
- Consumes: the source-of-truth file list below.

- [ ] **Step 1: Determine the exact sensitive-file set from the live tree** — `ls ~/Documents/workato-kb/kb/` and confirm: `confluence_ingest.py`, `confluence_sync.py`, `attachments.py`, `harness_source.py`, plus any module importing them (`grep -l "confluence\|harness_source" ~/Documents/workato-kb/kb/*.py`). Record the list; the export script embeds it literally (no dynamic globs that could pick up new sensitive files silently).

- [ ] **Step 2: Write `pack-export.sh`**

```bash
#!/usr/bin/env bash
# pack-export.sh — copy the KB pipeline into the dev-kb pack, MINUS the
# confluence/harness sources. The ONLY automated path between the private
# repo and the shareable pack. Code only; no corpus, index, or config data.
set -euo pipefail
SRC="$(cd "$(dirname "$0")/.." && pwd)"
DST="${1:-$HOME/Documents/workato-dev-kb}"
[ -f "$DST/sources/public.json" ] || { echo "REFUSING: $DST is not the dev-kb repo (no sources/public.json)"; exit 1; }
# embedded, explicit: new sensitive files must be ADDED here consciously
SENSITIVE=(confluence_ingest.py confluence_sync.py attachments.py harness_source.py)
mkdir -p "$DST/kb"
rsync -a --delete "$SRC/kb/" "$DST/kb/"   # mirror, so deletions propagate
for f in "${SENSITIVE[@]}"; do rm -f "$DST/kb/$f"; done
# fail the export if any survivor imports a stripped module
if grep -rl "confluence_ingest\|confluence_sync\|harness_source\|attachments" "$DST/kb" --include='*.py' | grep -v __pycache__; then
  echo "EXPORT FAILED: a copied module imports a stripped source — fix the import before exporting."; exit 1
fi
find "$DST/kb" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
echo "exported kb/ -> $DST/kb (sensitive sources stripped: ${SENSITIVE[*]})"
```

- [ ] **Step 3: Run it and verify the negative space**

```bash
chmod +x ~/Documents/workato-kb/scripts/pack-export.sh && ~/Documents/workato-kb/scripts/pack-export.sh
ls ~/Documents/workato-dev-kb/kb/ | grep -E "confluence|harness|attachments" && echo "FAIL: sensitive file present" || echo "clean: no sensitive modules"
grep -rl "confluence\|harness_source" ~/Documents/workato-dev-kb/kb --include='*.py' | grep -v __pycache__ || echo "clean: no imports of stripped modules"
```

Expected: `clean:` on both lines. Note: `sync.py` likely references the confluence source in its SOURCES registry — if step 2's import-check trips on it, edit the EXPORTED copy's registry (not the private original) to drop those entries, and record the edit as a follow-up consideration for upstreaming a `SOURCES_ENABLED` env into the private repo.

- [ ] **Step 4: Negative test of the guard**

```bash
~/Documents/workato-kb/scripts/pack-export.sh /tmp && echo "GUARD FAILED" || echo "guard works (refused non-pack target)"
```

- [ ] **Step 5: Commit in the PRIVATE repo**

```bash
cd ~/Documents/workato-kb
git add scripts/pack-export.sh README.md
git commit -m "feat: pack-export.sh — one-way code export to workato-dev-kb, sensitive sources stripped

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 4: install.sh — hardening framework + prereqs + venv (lane B)

**Files:**
- Create: `~/Documents/workato-dev-kb/install.sh`

**Interfaces:**
- Produces: `begin_step`/`finish_step`/`degraded`/`fail_step`/`with_retry`/`with_retry_stream`/`fix_or_fail`/`ensure` functions; `LOG` variable. Task 6's steps plug into this framework — names must match exactly.
- Consumes: `config.sh` (Task 1).

- [ ] **Step 1: Write the framework** — port the kit's proven blocks nearly verbatim (do NOT reimplement from scratch): the log/exec-tee block, STEPS/COMPLETED/DEGRADED arrays, `on_exit` trap, ERR trap, `classify_failure`, `with_retry`, `with_retry_stream`, `fix_or_fail`, `ensure` — copy each function body from `~/Documents/agentic-workato-kit/install.sh` and change only: log dir stays `install-logs/`, kit-specific `KIT_HOME` references removed. STEPS pipeline for this installer:

```bash
STEPS=(prereqs venv config models sync index fractal smoke)
```

- [ ] **Step 2: Write the prereqs step** — brew as fix engine, then: `git`, `jq`, `python3.12` (fix: `brew install python@3.12`), disk-space preflight before any download:

```bash
begin_step prereqs
ensure git "brew install git"
ensure jq "brew install jq"
ensure python3.12 "brew install python@3.12"
FREE_GB=$(df -g "$HOME" | awk 'NR==2 {print $4}')
[ "${FREE_GB:-0}" -ge 5 ] || fail_step "only ${FREE_GB}GB free — models + index need ~5GB. Free space and re-run."
echo "  ok: ${FREE_GB}GB free"
finish_step prereqs
```

- [ ] **Step 3: Write the venv step with repair** — stale/wrong-python venvs are the top KB-onboarding failure:

```bash
begin_step venv
VENV=".venv"
if [ -f "$VENV/pyvenv.cfg" ] && ! grep -q "python3.12" "$VENV/pyvenv.cfg"; then
  degraded("existing .venv is not python3.12 — removing and recreating")
  rm -rf "$VENV"
fi
if [ ! -f "$VENV/bin/activate" ]; then
  with_retry "create venv" 3 python3.12 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
pip install -q --upgrade pip
with_retry "install kb dependencies (torch, sentence-transformers, sqlite-vec)" 3 \
  pip install -q sentence-transformers sqlite-vec
finish_step venv
```

- [ ] **Step 4: Write the config step** — mirror the kit's onboarding shim: no `config.sh` + interactive → prompt for install dir inline (2 questions, not 14 — this pack has 2 settings); headless → copy example with a NOTE. Guard: `KB_INSTALL_DIR` must not be inside the repo checkout (corpus is gitignored, but keeping data out of the clone avoids accidental commits of a 2GB dir).

- [ ] **Step 5: Syntax-check and smoke the framework**

```bash
bash -n install.sh && echo "syntax ok"
bash -c 'source /dev/stdin <<< "$(sed -n "/^with_retry/,/^}/p" install.sh)" && type with_retry >/dev/null && echo "functions load"'
```

- [ ] **Step 6: Commit**

```bash
git add install.sh && git commit -m "feat: installer framework — kit-grade hardening (steps, traps, retry, fix_or_fail) + prereqs/venv

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 5: install.sh — KB steps: models, sync, index, fractal, smoke (lane B)

**Files:**
- Modify: `~/Documents/workato-dev-kb/install.sh` (append steps; Task 4's framework is load-bearing)

**Interfaces:**
- Consumes: Task 4's functions; `sources/public.json`; `KB_INSTALL_DIR` from config.
- Produces: working `kb` CLI at `.venv/bin/kb`-invokable; per-source degraded semantics later verified by Task 7.

- [ ] **Step 1: models step** — model fetch is the longest network op; make retries resumable rather than restarting the download:

```bash
begin_step models
with_retry "pre-download bge models (~2GB, resumable)" 3 python3 - <<'PY'
from sentence_transformers import SentenceTransformer
for m in ("BAAI/bge-base-en-v1.5", "BAAI/bge-reranker-base"):
    print("fetching", m); SentenceTransformer(m)
print("models ready")
PY
finish_step models
```

- [ ] **Step 2: sync step with per-source degraded semantics** — a source being down must NOT kill the install. Run the sync once per source from `sources/public.json` so one failure degrades instead of aborting:

```bash
begin_step sync
mkdir -p "$KB_INSTALL_DIR"
FAILED_SRC=()
for src in $(python3 -c "import json;print(' '.join(json.load(open('sources/public.json'))['sources']))"); do
  if ! with_retry "sync source: $src" 2 python3 -m kb.sync --source "$src"; then
    FAILED_SRC+=("$src")
  fi
done
if [ "${#FAILED_SRC[@]}" -gt 0 ]; then
  if [ "${#FAILED_SRC[@]}" -eq 7 ]; then
    fail_step "all 7 sources failed to sync — network/proxy issue (see classify above)"
  fi
  degraded("sources failed to sync: ${FAILED_SRC[*]} — KB works on the rest; re-run ./install.sh later to retry")
fi
finish_step sync
```

Note: `kb.sync` must accept `--source` — if the private repo's sync entrypoint doesn't, adapt the exported copy's CLI in the pack (Task 3 territory); verify the actual invocation form at execution time from `kb/sync.py`'s argparse.

- [ ] **Step 3: index + fractal steps with the coverage gate**:

```bash
begin_step index
with_retry "build index (FTS5 + vectors + entropy layers)" 2 python3 -m kb.indexer --build
finish_step index

begin_step fractal
with_retry "build fractal projection" 2 python3 -m kb.fractal --rebuild
COV=$(python3 -m kb.fractal coverage 2>&1) || fail_step "fractal coverage audit crashed: $COV"
echo "$COV" | grep -qi "AIRTIGHT" || degraded("fractal coverage not AIRTIGHT — audit says: $COV")
echo "  fractal: $COV"
finish_step fractal
```

(Exact module/flag names must be read from the exported `kb/` CLI at execution time — `python3 -m kb.fractal coverage` per the kit's INSTALL.md; adjust the invocation, never the AIRTIGHT gate.)

- [ ] **Step 4: smoke step — prove the user's first command works before claiming success**:

```bash
begin_step smoke
OUT=$(python3 -m kb.search "how do connectors handle pagination" 2>&1) || fail_step "smoke search crashed: $OUT"
echo "$OUT" | grep -qE '"doc_id"|url|\[source' || fail_step "smoke search returned no hits-shaped output: $OUT"
echo "  ok: kb search returns results. Try it: source .venv/bin/activate && kb \"your question\""
finish_step smoke
```

- [ ] **Step 5: End-to-end rehearsal in a sandbox HOME** (the consumer experience, not Josh's):

```bash
H=$(mktemp -d)
HOME="$H" git clone -q ~/Documents/workato-dev-kb "$H/dev-kb" && cd "$H/dev-kb"
HOME="$H" ./install.sh 2>&1 | tail -20; echo "exit: $?"
```

Expected: completes or DEGRADES on network-flaky sources; on failure the EXIT-trap report names the step, completed steps, degraded items with fix commands, and log path. Clean up `$H`.

- [ ] **Step 6: Commit**

```bash
git add install.sh && git commit -m "feat: KB install steps — resumable models, per-source degraded sync, fractal AIRTIGHT gate, smoke query

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 6: verify.sh — post-install doctor (lane B)

**Files:**
- Create: `~/Documents/workato-dev-kb/verify.sh`

**Interfaces:**
- Produces: PASS/WARN/FAIL table, exit non-zero only on FAIL — mirrors kit `verify.sh` structure exactly (`row()` helper, sectioned checks, summary line).

- [ ] **Step 1: Write it** — copy the kit's `row()` + section skeleton; checks for THIS pack: git/python3.12/jq present; `config.sh` present + `KB_INSTALL_DIR` set and outside the checkout; `.venv/bin/python` exists and is 3.12; index DB exists at `$KB_INSTALL_DIR/index/kb.db` and has >0 rows in the FTS table; `kb search "pagination"` returns hits; `kb fractal coverage` includes AIRTIGHT (WARN, not FAIL, if not); at least 1 knowledge domain file present; daemon check as WARN-only (optional layer — CLI cold-load works without it):

```bash
DB="$KB_INSTALL_DIR/index/kb.db"
[ -f "$DB" ] && [ "$(sqlite3 "$DB" "select count(*) from chunks_fts 2>/dev/null" 2>/dev/null | tr -d ' ')" != "0" ] \
  && row PASS "index db" "$(du -h "$DB" | cut -f1)" || row FAIL "index db" "missing/empty — re-run ./install.sh"
```

(Table name read from the exported indexer at execution time — verify, don't guess.)

- [ ] **Step 2: Run it post-install in the sandbox HOME from Task 5's rehearsal** — expected: all PASS or WARN-only; any FAIL names its fix.

- [ ] **Step 3: Commit**

```bash
git add verify.sh && git commit -m "feat: verify.sh doctor — index, fractal coverage, smoke search, daemon-optional

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 7: Content promotion — ⛔ JOSH'S GATE BEFORE ANY PROMOTION RUNS

**Files:**
- Create: `~/Documents/workato-dev-kb/knowledge/domains/*.md`, `skills/<name>/SKILL.md` (one per promoted item)
- Modify: `knowledge/INDEX.md` (one line per promoted file)

**Candidate list (proposed — Josh approves/edits before Task 7 executes):**

| Private source | Promoted as | Why |
|---|---|---|
| `domains/workato-platform.md` (trap sections only) | `domains/workato-platform-traps.md` | the highest-value trap catalog |
| `domains/agentic-platform-lessons.md` | `domains/agentic-platform-lessons.md` | generic agent-platform lessons |
| `domains/mcp-operations.md` | `domains/mcp-operations.md` | MCP ops practices |
| `domains/architecture-maps.md` | `domains/architecture-patterns.md` | pattern, not his estate |
| `domains/claude-code-docs-canon.md` | `domains/claude-code-canon.md` | doc-mining method |
| `domains/workato-slack-bot-connections.md` | `domains/slack-bot-connections.md` | the governed Slack-bot SOP |
| skills: `airo-mcp-playbook`, `workato-kb`, `verify`, `diff-reading`, `workato-development-playbook` (Josh added at approval, 2026-10-10 — the cross-project operating model; strips: 2 estate IDs, BT-Confluence KB-grounding wording, KB-bridges trailer, kit-only skill pointers annotated) | same names under `skills/` | sanitized |

Excluded by default: `writing-voice`, `josh-voice-corpus`, `brain-gardener`, `dream-loop`, `cortex`, `measure-learn-apply`, `harness-docs`, `workday-platform`, `model-gateway-playbook` (personal-harness, voice, or estate-specific).

- [ ] **Step 1: BLOCKED — present this table to Josh, get the final list.** No promotion file is written before his one-line approval.

- [ ] **Step 2: Per approved file, the promotion loop** (swarmable — one agent per file, disjoint ownership):

1. Read the private source file.
2. Rewrite into the pack: strip workspace/recipe/table IDs → generic placeholders like `<workspace-id>`; strip personal names → roles; strip BT-internal specifics (ticket keys, internal URLs); keep every generalizable trap, playbook step, and lesson. First person → neutral imperative.
3. Write to the pack path; add the INDEX.md line.
4. Run the scan patterns from `.githooks/patterns.txt` + `names.txt` against the new file manually before staging.

- [ ] **Step 3: Worked example of the rewrite (first file, sets the bar)** — private `workato-platform.md` line:

> `wt v2 (2026-10-07): wt testcases run/status/cases = Test Automation API ... workspace 3535597`

becomes pack copy:

> `Test Automation API: recipe test cases are runnable via the Test Automation API (run/status/cases), not UI-only. Self-serve scope grant via the client-roles editor.`

- [ ] **Step 4: Batch commit per file group**

```bash
git add knowledge skills && git commit -m "docs: promote curated knowledge (generic-form rewrites)

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 8: Handoff — the Josh-gated first push

**Files:** none created. This task is the gate itself.

- [ ] **Step 1: Full re-verification:** re-run Tasks 5 (sandbox rehearsal) and 6 against the final content; run the secret scan across the WHOLE tree (`git grep -iE` with each pattern) — not just the hook's diff scope.
- [ ] **Step 2: Write the promotion-readiness summary for Josh:** what shipped, scan results, what is deliberately absent, remaining v1.1 items (seed claims ledger, kit `install.sh` channel that offers cloning this pack, launchd daemon setup note, `--source` upstreaming to the private repo).
- [ ] **Step 3: STOP. Present Josh: `gh repo create Workato-All/workato-dev-kb --internal` + first push.** Nothing goes to GitHub without his explicit go.

---

## Self-Review

- **Spec coverage:** privacy guarantee → Tasks 1–3 + 7 (no inbound sync, export filter, allowlist review, secret scan); install hardening (kit parity + KB additions) → Tasks 4–6; fractal wired into read path + AIRTIGHT gate → Tasks 5–6; memory-rules shipped → Task 1 Step 6; content promotion curated/rewritten → Task 7; claims deferred → noted Task 8 Step 2; consumer experience → Tasks 4–6; first push gated → Task 8. No gaps.
- **Placeholder scan:** no TBD/TODO; every code step has real code; execution-time verification points are explicit instructions to read from the exported tree, not hand-waves.
- **Type consistency:** Task 5 consumes exactly Task 4's function names (`begin_step`, `with_retry`, `degraded`, `fail_step`); `sources/public.json` key names match across Tasks 1, 5, 6.
