# BSYS-29730 — Day-1 spike findings (2026-10-22)

Epic: https://workato.atlassian.net/browse/BSYS-29730 · Plan: `BSYS-29730-perf-review-cycle-plan.md` (same folder)
Probe vehicle: TEST recipe `TEST | BSYS-29730 Spike Probe` 83290934 — https://app.workato.com/recipes/83290934 (webhook-triggered, running, dev workspace 3535597; manifest-exempt test probe). Probe jobs: j-Ac6NFTsm-96kaYE-CD, j-Ac6NHApw-bBYQs6-CD, j-Ac6NJ3b9-AcPG49-CD, j-Ac6NJsAY-dRxeaW-CD, j-Ac6NKxLf-TJtWTB-CD (all inspectable at https://app.workato.com/recipes/83290934/job/<id>).
Transport: custom connector `leapsome_connector_748504` adhoc HTTP action, base URI `https://api.leapsome.com/v1/`, dev connection `[PER] Leapsome` 19006083 (authorized, reads production Leapsome — all probes read-only or fabricated-ID; PII steps mask_data=true; the only unmasked outputs were review-cycle metadata and TEST-cycle participant rows).

Privacy note: NO review content was judged, extracted, or exported anywhere. The open external-LLM-judging decision remains Josh's, untouched — spikes were mechanics-only.

## Spike A — Leapsome review submit (gates R2 submit path)

**Question:** can the Leapsome API submit a review (or is the manual-submit fallback final)?

**Method:** route-existence probes through the dev connection. Discriminator: live routes return structured 400s on malformed input (observed on GET participants with a fabricated cycle id — `400 {"message":"Invalid or incomplete input provided","payload":{"_errors":[],"reviewCycleId":{"_errors":["Invalid id format"]}}}`); absent routes return bare `404` with an empty body.

**Evidence:**
- `POST /reviews` (bodyless, no object targeted) → `404 Not Found`, empty body. No create-cycle route.
- `POST /reviews/SPIKE-PROBE-0000/participants/SPIKE-PROBE-0001/answers` → `404 Not Found`, empty body. No answer-submit route at the REST-shaped path.
- Corroboration: Leapsome's own MCP drafts but refuses to submit (kickoff digest R2); public API docs are login-gated (www.leapsome.com/api-documentation and five sibling URLs all 404 unauthenticated).
- Read side works fine on the same connection: `GET /employees`, `GET /reviews`, `GET /reviews/{cid}/participants`, `GET /reviews/{cid}/participants/{uid}/overview` all 200.

**Verdict: BLOCKED for API submit** — no submit route found at probed paths; two empty-body 404s against a live connection whose GETs 200, with structured-400 discrimination proving the 404s are route-absence, not bad input.

**Implication for week-1/R2/R3:**
- R2 adopts the documented fallback: drafting completes in HR Genie, manager clicks submit in Leapsome. This is now the PRIMARY path, not a contingency — record it in the R2 story.
- R3 "proceeded unedited" detection uses the fallback path (Review Shared Detector compares Leapsome-submitted content against the gated draft hash); the Genie-resubmit-draft-hash path is dead with API submit.
- One residual: submit could exist at an undocumented non-REST path only the login-gated docs would reveal. If the People team can screenshot the API docs, one look settles it. Not worth blocking on.

## Spike B — Attachment mechanics (gates R4 renderer-vs-passthrough)

**Question:** can Leapsome's nine-box file attachment be retrieved through the API and passed through Workato into Slack?

**Method:** probed every review-surface path reachable with real TEST-cycle ids (TEST P&E Bi-Annual Review cycle `6679d4d91ecdaf71383ecc38`, participant `632e2837c16fe635bea9193e`) for attachment/file fields; plus the Workato-side file-column mechanics on the Nomination Log table.

**Evidence:**
- `GET /reviews/{cid}/participants` → 200. Full row shape: `{_id, reviewee:{user,name,preferredName,status,averageRating:"0 / 100",lastModifiedOn,lastModifiedBy}, managers:[…same shape…], directReports:[], peers:[], additionalManagers:[], lastModifiedOn, lastModifiedBy, __v2:true}`. **No file/attachment fields anywhere.**
- `GET /reviews/{cid}/participants/{uid}` (detail) → `404`, empty body. No detail route.
- `GET /reviews/{cid}/participants/{uid}/overview` → 200 (live). Shape per the reused v2 skill schemas: `questions[{_id,name,average}]`, `answers[{authorId,receiverId,question,type,rating,scale,comment}]`, `users[{_id,fullName,preferredName,email,teams,location}]`. **No file fields.**
- Workato side: data-table file column rejects REST writes — `update-record` with a string → `400 "field 'competency_file': expected type file, got: string"`; object shapes `{link}`, `{url}`, `{file_name,link}` → `400 "Expected input type ApiValue"`. File columns are recipe-runtime/UI-only.
- Per-reviewer status values observed: `complete` / `pending` — consistent with the plan's open item D (signatureManager/signatureReviewee ≠ shared; per-participant status is what the detector will actually see).

**Verdict: BLOCKED for passthrough** — no nine-box attachment surface exists on any probed Leapsome path; the "translate the attachment" premise from the kickoff digest is unproven and now evidentially weak.

**Implication for week-1/R4:**
- The renderer fallback activates, per the plan's pre-committed condition. Build the nine-box visual from the proven overview data: per-question averages on a 0–100 scale. The renderer's "potential" axis still does not exist in the API (Phase 0 finding re-confirmed by the shapes above) — render the two real axes only, and say so on the slide.
- R4 story must not carry an "attach Leapsome's file" task; replace with "render from overview averages".
- Open item D (exact shared signal) still gates the detector's trigger semantics — spike B does not resolve D.

## Spike C — Competency attach mechanics (gates R1 step 5 shape)

**Question:** how does a Leapsome competency assessment concretely attach to a nomination row (link / extracted text / file), and does the foundation table hold it?

**Method:** live reads on the TEST cycle + end-to-end row round-trip on the newly created foundation table in the new `Perf Review Cycle` folder.

**Evidence:**
- Created folder `Perf Review Cycle` (35943947) under the HR Genie project root 30275122 — https://app.workato.com/recipes?fid=35943947.
- Created `TBL | Perf Cycle | Nomination Log` (UUID c1d43596-8060-4123-988e-eb73c5d2e02f, numeric 164149) — https://app.workato.com/data_tables/c1d43596-8060-4123-988e-eb73c5d2e02f — 16 columns including `competency_attach_ref`, `competency_attach_type`, `competency_source_id`, `competency_file` (file), `policy_flags`, `ai_preeval_verdict`, `sheet_sync_state`.
- The `/competencies` endpoint 404 (plan's Phase 0) re-confirmed by absence: competency evidence lives in the overview endpoint's per-question answers/averages — extractable as text, linkable as the review UI path.
- Row round-trip PROVEN end-to-end: created a test row with `competency_attach_type="link"`, `competency_attach_ref` = Leapsome review URL, `competency_source_id` = `cycle:<id> user:<id>`, `sheet_sync_state="pending"` → read back intact via `wt dt query` (record `86f86e30-c65f-454d-9d98-7e922b4b73aa`), then deleted; table back to 0 rows.
- File-column result: NOT writable via REST (see Spike B) — recipe-runtime write is the only programmatic path, unverified for recipes.

**Verdict: WORKS** — attach-ref design proven live end-to-end.

**Implication for week-1/R1:**
- R1 step 5 lands on the nomination row as: `competency_attach_type="link"` (Leapsome review path) or `"text"` (extracted overview-answer evidence) + `competency_source_id`. No file column dependency; AC-4 ("no manual PDF upload") is satisfiable without any file mechanics.
- Schema replace caveat honored: columns were added while the table was empty; NEVER use `data_table_update` columns on a table with rows (playbook non-negotiable).

## Assets touched (all dev, ws 3535597)

- Folder 35943947 `Perf Review Cycle` (new)
- Data table 164149 / c1d43596-8060-4123-988e-eb73c5d2e02f `TBL | Perf Cycle | Nomination Log` (new, 0 rows)
- TEST recipe 83290934 (probe vehicle, running, manifest-exempt; candidate for deletion after week-1 wiring proves out)
- Living export manifest 370467 "BSYS-29730 HR Genie Perf Review Cycle" (1 asset row + folder chain; mirror `~/Documents/workbench/manifests/bsys-29730-hr-genie-perf-review-cycle.manifest.json`; in-page + ZIP verification still PENDING — do before any promotion citation)

## Builder H probe — manager-role status vs "started but not submitted" (2026-10-24)

**Vehicle:** TEST recipe `TEST leapsome status probe` 83326117 (folder 35947367, scheduler force-run, mask_data on read step; manifest-exempt test probe). **DELETED post-capture** — its step-3 `code_input` echo logged participant names unmasked in job logs; deleting purged them. Jobs: j-Ac8BheWE-rErQNM-CD (FY26 Year-End cycle `6aa81329f26ca85bdc02cc35`), j-Ac8BkL4s-NGGtD3-CD (TEST P&E cycle `6679d4d91ecdaf71383ecc38`). Read-only GETs only.

**Findings:**
1. **Status value set is exactly `pending` | `complete`** — observed on both `reviewee` and `managers[i]` entries, both cycles. No `started`/`in_progress`/`draft` value exists.
2. **The started-but-not-submitted signal = `lastModifiedOn` + `lastModifiedBy` PRESENT on the reviewer entry while status stays `pending`.** Untouched reviewer entries omit both keys entirely (they are absent, not null). FY26 crosstab: row A manager pending+lastModified(2026-09-22, by manager's own id) = started-drafted; rows B/C managers pending with NO lastModified = not started; row B reviewee `complete` shows a completed entry keeps lastModified. TEST-cycle row shows the same shape with 2024 timestamps (touched 2024-06-24, still pending). Caveat: lastModifiedBy is always the entry owner's own id — the probe cannot distinguish "manager saved a draft" from any other owner-side touch, but mere cycle launch does NOT stamp it (rows B/C prove the negative). **Nudge rule: `managers[i].status == 'pending' AND lastModifiedOn present` → started-not-submitted.**
3. **signatureManager/signatureReviewee: NOT re-confirmable when set** — zero rows in either cycle carry them; keys are omitted entirely when unset. Live-confirmed the unset side only: row B has reviewee `complete` with NO signatureReviewee (independence-from-completion re-confirmed directionally). Phase-0 shapes remain the sole evidence for set-state; the watcher's presence gate (`signatureManager present`) is safe precisely because unset = key omitted.
4. Peripheral: averageRating scale is per-cycle ("0 / 3" FY26 3-pt labels, "0 / 100" TEST cycle 0–100).

## Not verified / open

- Whether an undocumented Leapsome submit route exists (login-gated docs would settle it in one look).
- Recipe-runtime (not REST) writes to the `competency_file` column.
- The exact "shared review" signal (open item D, People team) and the calibration Sheet ID/owner (open item E) — both still open, both pre-tracked in the plan.
- The overview 200 was shape-confirmed live but its payload stayed masked (PII discipline); exact answer-text extraction is a week-1 build step.
