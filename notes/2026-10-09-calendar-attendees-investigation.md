# Calendar attendees stripped from list projections — investigation 2026-10-09

## Defect statement

Reads through `calendar.events.list@v3` (intents "list events" / "find meeting") never return
`attendees[]`, even for meetings that certainly have attendees. The raw Google Calendar API v3
`events.list` returns attendees by default, so the stripping happens in the semantic layer's
reviewed projection, not at Google.

## Evidence per probe (live, 2026-10-09, registry checksum e067a431…)

1. `calendar.events.get@v3` on event id `uk1sgn8g41aoigdmh41jn1t3s8` — READ_EXECUTED.
   Its projection DOES carry attendees (verbatim fragment):
   `"attendees":[{"email":"josh.cramoy@workato.com","organizer":true,"self":true,"responseStatus":"accepted"}]`
   → the connector/VUA transport and projection machinery pass attendees through fine. The
   defect is projection-authoring-specific, not a platform limitation.

2. `calendar.events.list@v3` on `search_expression="Josh / Sen Rong 1:1"` — READ_EXECUTED.
   Every item carries exactly `id, etag, summary, start, end, htmlLink` and no `attendees`
   key anywhere, including the confirmed 1:1 series
   `"summary":"Sen Rong / Josh | 1:1 "` (id `5qjv6bbdvd688eq1l00a5pseum`) and the
   recurring `1shs5ir7ebdm5qt234aca6kpgv_*` instances.

3. `calendar.events.instances@v3` on series id `dslt6vmmili5g5m5vjkjoj9h1g` (bare id, no
   suffix needed) — READ_EXECUTED, but items project only
   `{"created":"2025-12-15T14:16:25.000Z","creator":{"self":true},"end":null}` — no summary,
   no start, no attendees. The default projection it inherits is near-useless.

4. Static — `~/Documents/ChatGPT/Google Workspace MCP/semantic/capabilities.v1.json` (overlay):
   - `calendar.events.get@v3` projection = `[id, etag, summary, start, end, attendees, recurrence, htmlLink]` — attendees present.
   - `calendar.events.list@v3` projection = `[items.id, items.etag, items.summary, items.start, items.end, items.htmlLink, nextPageToken]` — **attendees absent**.
   - `calendar.events.instances@v3` projection = `[]` (empty-projection "inherit default" convention; the inherited default omits attendees/start).

5. Static — live registry agrees (policy lookup, the slot/contract authority per the project
   knowledge file): `calendar.events.list@v3` `projection_json` =
   `["items.id","items.etag","items.summary","items.start","items.end","items.htmlLink","nextPageToken"]`;
   `calendar.events.instances@v3` `projection_json` = `[]`. The list response shape matches the
   projected field set exactly — the projection is the served truth.

## Root-cause classification: (a) overlay/registry gap — locally fixable

Citation: `semantic/capabilities.v1.json` (canonical repo `~/Documents/ChatGPT/Google Workspace MCP/`),
rows `calendar.events.list@v3` (projection array missing `items.attendees`) and
`calendar.events.instances@v3` (projection `[]`), mirrored 1:1 into registry 147343
(`workspace_semantic_registry`, field `projection_json`, confirmed live via
`workspace_policy_lookup` 2026-10-09). It is authored reviewed content, not compiler behavior:
the sibling `events.get` row proves the compiler serves `attendees` when the projection names it.
Same defect class as BSYS-29328 (gmail messages.get projection lacked `payload.parts`) and the
slides `presentations.get` projection gap.

## Fix-ready technical plan

1. Overlay edit in the canonical repo:
   - `calendar.events.list@v3`: add `"items.attendees"` to the projection (matching
     `events.get`'s granularity; optionally bound to `items.attendees.email` +
     `items.attendees.displayName` if token cost matters).
   - `calendar.events.instances@v3`: replace `[]` with a pinned projection, e.g.
     `[items.id, items.summary, items.start, items.end, items.attendees]` — the empty
     inheritance currently yields `created/creator/end:null` junk.
   - If a validator requires a covering ruling, none needed: this is a read-projection
     extension, not a not_supported capability.
2. Rebuild + promote (the proven pipeline): `node scripts/build-semantic-indexes.mjs` →
   `node scripts/promote-workato-semantic-registry.mjs --capability calendar.events.list@v3 --apply`
   and `--capability calendar.events.instances@v3 --apply` (data-tables REST PUT with the
   `{"document": …}` envelope; writes need the table UUID, not numeric id).
3. Sibling intent rows: the promoter touches only build-generated rows; curator-promoted
   paraphrase rows for these capabilities keep stale contracts. Sweep all
   `calendar.events.list@v3` / `calendar.events.instances@v3` rows in registry 147343 by
   `index_key` and repair stragglers the same way (BSYS-29328 did a 14-tuple sibling sweep).
4. Wait one 15-min sync tick; re-query `workspace_capabilities(service="calendar")` (checksums
   rotate — never reuse e067a431…) and confirm the routing surface still serves both.
5. Verify live: re-run the list probe (`{"calendar_id":"primary","search_expression":"Josh /
   Sen Rong 1:1"}`, intent "list events") and assert `result_json.items[*].attendees` is
   present; same for instances on `dslt6vmmili5g5m5vjkjoj9h1g`. Optionally re-run
   `scripts/tuple-workflow-regression.mjs` (the floor test after any registry change).
6. Check `response_contract_json.default_projection` on the same rows — per BSYS-29328, both
   fields may need the change if the list executor sends a fields mask (for Calendar v3
   events.list it likely does not; verify the compiled provider request before skipping).

## Triage

File as a BSYS Bug under epic **BSYS-29262** (Google Workspace Semantic MCP epic), via the
/triage → BSYS-standards flow; ~2 points (overlay edit + promote + live verify; pipeline is
proven). Related precedent: BSYS-29328 (gmail projection gap, closed same-day class).

## Not verified

- ~~Whether the calendar list executor sends a `fields` mask (response_contract default_projection)
  — the projection-only fix may be insufficient if it does.~~ RESOLVED at build time 2026-10-09:
  `response_contract_json.default_projection` is DERIVED from the same overlay `projection`
  (`build-semantic-indexes.mjs` line ~331: `semantic.projection.length ? semantic.projection : generatedProjection(...)`),
  so one overlay edit flips both. No separate executor `fields=` mask to Google was found —
  the gateway strips post-response via the registry projection.
- ~~The fix itself~~ FIXED 2026-10-09, see below.
- The exact source of the inherited default projection for `instances` (why `end:null`) —
  moot after pinning; the schema-derived `generatedProjection` fallback was the junk source.

## FIX APPLIED — 2026-10-09 (BSYS-29490)

Commit `a3b66e8` (canonical repo): overlay projections flipped, indexes regenerated.

- `calendar.events.list@v3`: projection += `items.attendees` (full granularity, matches `events.get`).
- `calendar.events.instances@v3`: `[]` → pinned `[items.id, items.summary, items.start, items.end, items.attendees]`.
- Mask (`response_contract_json.default_projection`) flipped identically on every row — derived, not separate.
- Promoted scoped (`--capability calendar.events.list@v3,calendar.events.instances@v3 --apply`):
  3 generated rows updated, 0 creates, read-back verified.
- Sibling sweep (registry 147343, 1042 rows scanned): 5 curator paraphrase rows were stale and
  repaired to match generated siblings — `list@v3|what's on my calendar this week`,
  `list@v3|show my upcoming events`, `list@v3|calendar window regression probe`,
  `instances@v3|show the occurrences of that recurring meeting`, `instances@v3|list the instances of
  that repeating event` (the last two also had the giant schema-derived mask). All 8 rows now
  OK on both projection and mask.
- Served immediately — no 15-min sync tick was needed; the policy/execution path reads the
  registry live. Routing checksum `e067a431…` covers selection routing only (capability/intent/
  activation), not projections, so it was unchanged and still valid.

### After-probe evidence (live, 2026-10-09 ~01:15 UTC)

- `calendar.events.list@v3`, intent "list events", `search_expression="Josh / Sen Rong 1:1"`:
  READ_EXECUTED; every item now carries `attendees[]`. Series `5qjv6bbdvd688eq1l00a5pseum`
  ("Sen Rong / Josh | 1:1 ") returns
  `[{"email":"senrong@workato.com","responseStatus":"accepted"},{"email":"josh.cramoy@workato.com","organizer":true,"self":true,"responseStatus":"accepted"}]`.
  displayName, resource attendees, and even decline `comment` fields flow through.
- `calendar.events.instances@v3`, intent "instances events", on `dslt6vmmili5g5m5vjkjoj9h1g`
  (attendee-less "Home" series): items project `{id, summary, start, end}` — `end:null` GONE,
  no created/creator junk. On `1shs5ir7ebdm5qt234aca6kpgv` (Sen Rong 1:1 series): every
  instance returns `{id, summary, start, end, attendees[]}` with the full two-person roster.
- Floor regression `tuple-workflow-regression.mjs`: 240 families, `{"fail_closed":174,"executed":65,"skipped_discovery":1}`,
  FLOOR IS GREEN, zero bugs.
