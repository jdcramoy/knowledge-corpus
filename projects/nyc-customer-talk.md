# NYC Customer Talk — project file

DONE 2026-10-21. Josh-approved talk track for the Director+ customer briefing in NYC.

## Deliverables
- Deck (send-afterwards): https://docs.google.com/presentation/d/1ZwRGI6d7KiwYl_58BmB1alwAxiy5MAvQQ4-Vjl0o-YY/edit
  12 slides, each a 2560x1440 render of the matching HTML slide, full-bleed.
- HTML artifact (live-room surface + source of truth): ~/Documents/workbench/nyc-customer-talk/talk.html
  Fixed 1280x720 canvas scaled to viewport; click-through; edit copy HERE and re-export slides on request.
- Handoff + brief + research corpus: ~/Documents/workbench/nyc-customer-talk/ (HANDOFF.md, brief-fused.md, research-decks/internal/external.md)

## Durable lessons (full detail in handoff + auto-memory)
1. Image-based deck export: render HTML slide (headless Chrome, hash deep-link, scale 2) -> Host_Asset
   fails on >100KB base64 (transcription truncates) -> use a cloudflared tunnel, md5-verify, Add_Image
   fetches directly. Delete layout placeholders on Blank slides (they ghost).
2. Three-class number rule for customer decks: deck-sourced (keep) / live-verified org facts approved
   by Josh (keep) / personal-harness measurements (BANNED — the 81%-context, 55%-diet, 450-eng-hours
   class; Josh challenged each on sight).
3. josh-writing-voice applies to slide copy, chart tooltips, and Drive titles at BUILD time; em dashes
   are the first AI tell he catches.
4. Old native-layout deck kept for reference: 1vsBj_ykiQ0yINNaXbDgVZQLY_e4UkO6572lirEp7sb8.
