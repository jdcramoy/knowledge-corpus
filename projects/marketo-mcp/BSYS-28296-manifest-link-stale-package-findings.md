---
name: BSYS-28296-manifest-link-stale-package-findings
description: Investigation findings 2026-10-21 — dead manifest link (361307 deleted) + package 42201610 ships v37 which FAILED red-team; fix = re-point field to 361382 + re-export v38 package
metadata:
  type: project
---

# BSYS-28296 — Final Tech Review blockers (investigated 2026-10-21)

Parent: [[BSYS-28296-activity-history-plan]]. Ticket: https://workato.atlassian.net/browse/BSYS-28296

## Verified live (read-only: Jira REST v2, `wt manifests get`, `wt recipes get`)

- **Manifest Link field** (`customfield_10494`) = `https://app.workato.com/export_manifests/361307#content`.
  361307 returns **404** — it was deleted 2026-10-12 (built against wrong source folder, packaged an
  incomplete set). Rebuilt as **361382** (live, 19 assets, last exported 2026-10-12 → package
  **42201610**). Field was never re-pointed because it's only editable on a transition screen.
  That dead link is what Patricia hit (comment 2026-10-21 03:53Z).
- **v37 vs v38:** package 42201610 carries get_lead_activities **v37**, which **FAILED** red-team
  2026-10-12 (unvalidated caller-supplied paging cursor → trailing `#` could strip lead/type filters;
  `~/.claude/knowledge/redteam/BSYS-28296-marketo-get-lead-activities.md`). v38 cursor-guard build
  (charset allowlist at steps 9+16) pushed 2026-10-14, re-review **PASS-WITH-NOTES**
  (`...-v38-re-review.md`). Live dev recipe [72856618](https://app.workato.com/recipes/72856618) runs v38.
- **Trap noted:** `wt manifests assets 361382` returns a 13k-row cross-folder listing stamped
  folder 25730943 — the documented manifest-creation trap 5b; don't use it for row-level reads.

## Fix (both needed; no code change — v38 already running and re-reviewed clean)

1. **Re-export:** refresh manifest 361382's get_lead_activities row to v38 (or rebuild via
   `manifest-creation` script), re-export package. Destinations unchanged (prod connection 19943717,
   table 137886, folder 32369005) → repackage, not re-scope. ZIP-verify new package shows cursor
   guards before any import. **Do not let Final Tech Review import 42201610.**
2. **Re-point** `customfield_10494` from 361307 → 361382 (direct edit if permitted, else next transition).

Draft comment for Patricia ready (in session transcript 2026-10-21); not posted — dissenter gate
pending, then Josh's go (outward under his name).
