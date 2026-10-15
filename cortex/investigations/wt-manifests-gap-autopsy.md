# Autopsy: `wt manifests` create/list failures (blocks BSYS-29458 VUA flip path)

**Date:** 2026-10-09 · **Investigation only — no assets touched, no fixes applied.**

## TL;DR

| Command | Observed | Root cause | Fix class |
|---|---|---|---|
| `wt manifests list` | HTTP 404 `{"message": "API not found"}` | The endpoint **does not exist** in the Workato Developer API. `wt` invented `GET /api/export_manifests` (list-all); the docs' quick reference has only `folder_assets`, `POST /export_manifests`, `PUT|GET|DELETE /export_manifests/:id` | Remove/alias the op — no server fix possible |
| `wt manifests create` | 400 "Missing parameter name" / sometimes 500 | **Two stacked CLI bugs:** (A) the `--data` JSON string is double-encoded (`json.dumps` applied twice) so the server receives a JSON *string literal*, not an object; (B) even a correctly-encoded payload must be wrapped in `{"export_manifest": {...}}` and `wt` neither requires nor adds the wrapper | Code fix in `~/.local/bin/wt` (diff below). The API contract did NOT change |

Not an auth/profile/environment problem: the same dev profile + keychain token returns **200** on `wt manifests get 360395` while `wt manifests list` 404s in the same minute. The 404 is route-shaped, not workspace-shaped.

## Evidence

### Source location

- CLI: `~/.local/bin/wt` — single-file Python 3, 40.8 KB, last modified 2026-10-09 01:39. Not under version control (no repo, no symlink).
- Reproduced live (read-only):
  - `wt manifests list` → `HTTP 404 / {"message": "API not found"}` (GET, harmless)
  - `wt manifests get 360395` → HTTP 200, full manifest record ("GSlides MCP | Frontify design-token refresh 2026-10 promotion batch")
  - `wt manifests create --help` → only `--file` and `--data` exist; **no `--name`, no `--assets-file`** despite the module docstring advertising `wt manifests create --name "HR batch" --folder 30275122 --assets-file m.json` (those flags would die at argparse with exit 2, before any HTTP)

### Bug A — `--data` double-encoding (systemic, every subcommand)

`add_json_body` (line 553) binds `--data` to `a.body` as a **raw string**. Every consumer passes that string straight into `request()`, whose data branch re-encodes it (lines 110–112):

```python
elif data is not None:
    body = json.dumps(data).encode()          # data is already a str!
    hdrs["Content-Type"] = "application/json"
```

Empirical replication (offline, no live call) of the exact create path:

```
a.body = '{"export_manifest": {"name": "t", "assets": []}}'
wire body = b'"{\\"export_manifest\\": {\\"name\\": \\"t\\", \\"assets\\": []}}"'
          -> server parses it as a Python/JSON STRING, not an object
```

Downstream mapping of the observed errors:

- **500**: a string body means `params[:export_manifest]` is nil server-side; Rails raises on nil — matches the intermittent 500 and the prior knowledge note "export_manifests API 500s on guessed payloads" (`~/.claude/knowledge/projects/google-semantic-mcp.md`).
- **400 "Missing parameter name"**: a *correctly-encoded* dict **without the `export_manifest` wrapper** (e.g. `--file m.json` where `m.json` puts `name`/`assets` at top level) — the API looks for `name` inside `export_manifest` and reports it missing.

`a.body` is never `json.loads`-ed anywhere in the file (verified by grep). Affected call sites: lines 176, 180, 232, 236, 283, 287, 310, 383, 392, 408, 495, 500, 521, 571 — i.e. recipes copy/connect, connections, lookup add/update-row, properties upsert, **manifests create/update**, packages export, dt create/update-record, apic, testcases. The dt `query` path builds a real dict and works.

### Bug B — payload contract requires the `export_manifest` wrapper

Docs (Developer API → Recipe Lifecycle Management, https://docs.workato.com/en/workato-api/recipe-lifecycle-management.html, fetched live 2026-10-09): the create sample body is

```json
{
  "export_manifest": {
    "name": ":name",
    "assets": [{"id": ..., "name": ..., "type": ..., "version": ..., "folder": ...,
                "absolute_path": ..., "root_folder": ..., "unreachable": ..., "zip_name": ...,
                "checked": ...}],
    "folder_id": ...,
    "include_tags": ...
  }
}
```

`name` (required) and `assets` (required) live **inside** `export_manifest`. `wt` passes whatever the caller gives untouched (minus the double-encode), so a payload shaped like the doc's flat "Payload" parameter table 400s. `manifests update` has the same wrapper requirement.

### `list` 404 — endpoint never existed

Docs quick reference lists exactly nine RLM endpoints; there is **no** `GET /api/export_manifests` (list-all). This matches the historical note in `~/.claude/knowledge/projects/google-slides-mcp.md` ("`/api/export_manifests` now 404s — package route gone from this client" — actually it never existed on this API surface). Correct inventory routes: `GET /api/export_manifests/folder_assets` (works, 200, confirmed in the build ledger) and `GET /api/export_manifests/:id` (works, 200 above).

### API surface verdict

The endpoint contract did **not** change. Create/update/get/delete/folder_assets all exist exactly where `wt` points them. This is purely a client-side bug cluster: (A) double-encode, (B) no wrapper normalization, (C) a phantom `list` route, (D) a docstring advertising nonexistent flags.

## Proposed diff (NOT applied)

File: `~/.local/bin/wt`

### 1. Central fix: parse `--data` strings once, in `request()` (fixes every consumer at once)

```diff
--- a/wt
+++ b/wt
@@ def request(host, token, method, path, query=None, data=None, headers=None,
     if headers:
         hdrs.update(headers)
     body = None
     if raw_body is not None:
         body = raw_body
         if content_type:
             hdrs["Content-Type"] = content_type
     elif data is not None:
+        if isinstance(data, str):
+            try:
+                data = json.loads(data)
+            except json.JSONDecodeError as e:
+                die(f"--data is not valid JSON: {e}")
         body = json.dumps(data).encode()
         hdrs["Content-Type"] = "application/json"
```

### 2. `manifests` create/update: auto-add the `export_manifest` wrapper

```diff
@@ def cmd_manifests(a):
     elif a.op == "create":
         data = a.body
         if a.file:
             with open(a.file) as f:
                 data = json.load(f)
         if not data:
             die("create requires --file or --data JSON")
+        if isinstance(data, dict) and "export_manifest" not in data:
+            data = {"export_manifest": data}
         status, result = request(host, token, "POST", "/api/export_manifests",
                                  data=data)
     elif a.op == "update":
         data = a.body
         if a.file:
             with open(a.file) as f:
                 data = json.load(f)
+        if isinstance(data, dict) and "export_manifest" not in data:
+            data = {"export_manifest": data}
         status, result = request(host, token, "PUT",
                                  f"/api/export_manifests/{a.manifest_id}",
                                  data=data)
```

### 3. `manifests list`: remove the phantom route

```diff
@@ sub.add_parser("manifests")
-    p.add_argument("op", choices=["assets", "list", "get", "create",
-                                  "update", "delete"])
+    p.add_argument("op", choices=["assets", "get", "create",
+                                  "update", "delete"])
@@ def cmd_manifests(a):
-    elif a.op == "list":
-        status, result = request(host, token, "GET", "/api/export_manifests")
```

(Alternative: keep `list` as an alias that emits a clear "no list-all endpoint exists in the Workato Developer API; use `wt manifests assets <folder_id>` or `wt manifests get <id>`" message. Removal alone is cleaner; callers will discover via argparse.)

### 4. Docstring truthing (dead flags)

```diff
@@ module docstring
-  wt manifests create --name "HR batch" --folder 30275122 --assets-file m.json
+  wt manifests create --file m.json        # payload: {"export_manifest": {"name": ..., "assets": [...]}}
```

### Post-fix verification plan (when Josh approves dev work)

1. `wt manifests create --file <manifest.json>` against dev with a one-recipe manifest → expect 200 `{result: {id, name, status: "working"}}`.
2. `wt packages export <new_manifest_id>` → package ID; `wt packages get` to confirm `personalization` edit target shape for the BSYS-29458 flip.
3. Re-run the known-good flip path: export → set `personalization: true` on the mcp tool config entry → import with recipe 82059074 stopped.

## Does the same path affect `wt dt update-record`? — YES, but the recorded label is a misdiagnosis

Queue row `wt-dt-update-record-content-type` attributes the failure to a **missing Content-Type**. The code says otherwise: `request()`'s `data` branch **always sets** `Content-Type: application/json` (line 112). The real, same-root-cause defect is Bug A's double-encode — `cmd_dt` update-record/create-record pass the `--data` string to `request()` (lines 495, 500), producing a JSON string body, which the data-tables host rejects ("Expected input type UpdateRecordRequest, found ..."). This is already corroborated in `~/.claude/knowledge/domains/workato-platform.md` ("**wt trap: `wt dt create-record/update-record --data '<json>'` double-encodes the body**") from the BSYS-29477 UAT session.

Two additional notes for that fix:

1. Even after the double-encode fix, the data-tables records API requires the **document envelope**: `{"document": {"<column_name or field_uuid>": value}}` — not a flat column map. Diff #1 alone is necessary but not sufficient for dt record writes.
2. Rename the queue row's diagnosis when it's worked: it should be `wt-dt-update-record-double-encode` (or folded into the same Bug A fix ticket — one central diff fixes both, plus the dt `document` wrapper as a cmd_dt-local change).

## Blocker unblock for BSYS-29458

The flip path is NOT blocked on Workato — it is blocked on a ~15-line client patch to `~/.local/bin/wt` (diffs 1–3 above). Interim workaround that needs no code change: craft `m.json` with the `export_manifest` wrapper and use the Orca Export UI, or bypass the CLI with the raw API using the keychain token (`security find-generic-password -s workato-platform-cli -w`) and a correctly wrapped `curl`. The knowledge note that "the package route needs debugging first" can be retired once the diff lands.

Sources: live repro (commands above), https://docs.workato.com/en/workato-api/recipe-lifecycle-management.html (Developer API — the surface `wt` targets; NOT the OEM/Embedded API, which uses `/api/managed_users/:id/export_manifests` and is a different product surface), and the corroborating history in `~/.claude/knowledge/projects/google-slides-mcp.md`, `~/.claude/knowledge/projects/google-semantic-mcp.md`, `~/.claude/knowledge/domains/workato-platform.md`.
