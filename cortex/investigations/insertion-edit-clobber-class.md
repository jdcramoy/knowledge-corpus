# Insertion-edit clobber: Edit replaces a def/lambda/class anchor line

Investigated 2026-10-12 (read-only). Flagged by harness-dreamer 2026-10-12T03:49:44Z.
Sources: session transcripts f38d9d11-3323-4bba and f7acbe35-edc5-44dd-96fd-5fd69a8e3a80
(`~/.claude/projects/-Users-<user>-Documents-workbench/`).

## The failure class

The model intends to INSERT new code adjacent to an existing definition. It uses the
definition's first line as the Edit `old_string` anchor, writes the new content into
`new_string`, and forgets to re-include the anchor line. The Edit then REPLACES the
def/lambda/class line instead of inserting beside it: the definition is deleted, its body
dangles (attaching to whatever follows), and the breakage is silent until runtime or a
later syntax check.

Both confirmed instances:

### Instance 1 - session f38d9d11, `def _edge_neighbors` (kb/search.py)

- 2026-10-10T04:11:22Z, Edit on `~/Documents/workato-kb/kb/search.py`.
- Intent: insert two helper functions (`_chunk_cosine`, `_title_overlap`) between
  `_edge_neighbors` and `search`.
- old_string was EXACTLY ONE LINE: `def _edge_neighbors(db: sqlite3.Connection, seed_urls: list[str], per_seed: int = 2) -> list[Hit]:`
- new_string = the two new functions ending in `def search(` - the `_edge_neighbors` def
  line is NOT re-included. The tell: new_string ends with the FOLLOWING symbol's def
  (`def search(`), showing the model was composing "insert before X" but anchored on the
  PREVIOUS def line and dropped it.
- Result: `_edge_neighbors` signature deleted; its docstring/body then dangles directly
  after `def search(` (unclosed paren -> SyntaxError).
- Self-repaired 13 s later (04:11:35Z) by an Edit whose old_string was
  `def search(\n    """One-hop doc_neighbors...` - i.e. the repair had to reconstruct the
  exact merged-broken state. Repair succeeded.

### Instance 2 - session f7acbe35, `stat = lambda` (brain-dashboard.py)

- 2026-10-08T02:56:47Z, Edit on `~/.claude/knowledge/scripts/brain-dashboard.py`.
- Intent: insert counter variables above the `stat` lambda definition.
- old_string was EXACTLY ONE LINE: `    stat = lambda label, value, sub="": f"""\n      <div class="stat">..."""` (the full lambda assignment).
- new_string = four `sum(...)`/counter lines. The `stat = lambda` definition is NOT
  re-included at all - the anchor was consumed and dropped entirely.
- Result: `stat` undefined; every later `stat(...)` call in the dashboard template raises
  NameError at render.
- Self-repaired 40 s later (02:57:27Z) by re-appending the lambda after the counters. The
  same anchor-edit churn also duplicated the `ok_timers`/`agents_speaking` lines, needing
  a separate dedup Edit (02:56:58Z) - collateral of the same pattern family.

## Pattern characterization

Both instances share one exact shape:

1. Edit intent is insertion; the anchor chosen for old_string is a definition's first line.
2. old_string is EXACTLY ONE def/class/lambda line (no body attached). This is the
   load-bearing detail - it distinguishes clobber from legitimate def edits.
3. new_string omits a definition of the anchored symbol.
4. In the def case, new_string typically ends with the NEXT symbol's def line (the
   "insert-before" tell). In the lambda case new_string is pure new content.
5. Damage is silent at Edit time; detected only by later failure or in-session re-inspection.

## Retro-scan results (proposed lint applied to both transcripts)

Naive rule (old_string[0] matches `^(async )?def |^class |^\s*\w+ = lambda` and that exact
line is absent from new_string) flags 5 edits in f38d9d11 and 1 in f7acbe35. Manual review:
3 of the 6 are FALSE POSITIVES - legitimate signature changes (`_refresh_manifest_shas`
param add, `normalize` param add, `_kb_chunkable_paths` rename) where the symbol name
survives or the edit is a genuine multi-line replacement including the body.

Refined rule kills the false positives: fire ONLY when

- old_string is a SINGLE line (after strip) matching `^(async\s+)?def\s+\w+\(|^class\s+\w+|^\s*[\w.]+\s*=\s*lambda\b`, AND
- new_string contains no definition of that symbol (`def <name>\b`, `class <name>\b`, or `<name>\s*=\s*lambda`).

Measured on both sessions: 2/2 true positives (the two clobbers), 0 false positives.
Remaining accepted risk: a single-line def->def rename (old `def foo():` -> new
`def bar():`) would flag as a warning; that edit class is rare (renames need call-site
edits too) and warn-level is the right severity.

## Proposed lint heuristic (concrete)

Where to enforce (pick, in order of preference):
1. A PreToolUse hook on Edit (workato-guardrails already has the hook infra, v1.0.0,
   13 hooks) - block or warn at tool-call time, zero latency cost, catches the class
   before the file is touched.
2. Add to `~/.claude/knowledge/scripts/lint-changed.py` as a post-edit checker (weaker:
   catches it after the write, but still same-turn).

Pseudocode:

    DEF_LINE = re.compile(r'^(?:(async\s+)?def\s+(\w+)\s*\(|class\s+(\w+)|\s*[\w.]+\s*=\s*lambda\b)')
    def insertion_clobber(old_string, new_string):
        stripped = old_string.strip()
        if '\n' in stripped: return None            # multi-line edit: not the anchor pattern
        m = DEF_LINE.match(stripped)
        if not m: return None
        name = m.group(2) or m.group(3) or stripped.split('=')[0].strip()
        if re.search(rf'def\s+{re.escape(name)}\b|class\s+{re.escape(name)}\b|{re.escape(name)}\s*=\s*lambda', new_string):
            return None                             # anchor re-included (possibly modified) - fine
        return f"Edit drops definition of '{name}' used as insertion anchor; re-include the def line in new_string"

Severity: WARN (not block) initially - the one-line-def rename edge case is a legitimate
if rare edit; block only after a week of zero false-positive warnings. Log hits to the
guardrails telemetry so the dreamer can track class recurrence.

## Why this matters beyond the two hits

- Both clobbers were caught and repaired IN-SESSION this time; the class becomes
  dangerous when the orphaned body happens to be syntactically valid (a dangling
  expression attaching to the next def parses fine and just silently drops a function).
- Frequency: 14 of 117 Edits across the two sessions anchored on a def/class/lambda
  first line; 2 of those dropped the anchor (~14% of def-anchored edits). Small base,
  high blast radius.
- Related same-family damage seen in f7acbe35: duplicated variable blocks from
  re-anchoring on already-inserted content (line 699 dedup repair).

Nothing else was modified (read-only investigation; findings file is the only write).
