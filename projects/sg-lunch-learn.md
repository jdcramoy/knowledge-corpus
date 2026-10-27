# SG Lunch and Learn: the harness story

Tue session for the Singapore office, ~30 min: from out-of-the-box AI tools to the
self-learning Workato build harness. Fusion-pass story brief (acts, timeline, war stories,
reconciled numbers, honesty rails, 18-slide outline) lives at
~/Documents/workbench/sg-lunch-learn/story-brief.md (2026-10-25).

Status: story brief delivered, needs Josh review; deck build via google-slides MCP
(workato-brand-2026 + enhanced-gslides-template-workflow) after approval.
Key evidence: KT/roi/framework.md, WB/memory/codex-memory-migration.md,
KT/projects/workato-kb.md, KT/domains/harness-benchmarking.md,
KT/reviews/harness-cost-benefit-2026-10-11.md.

## Deck first draft BUILT (2026-10-25)

Deck: https://docs.google.com/presentation/d/1B_0lvLXkxwt1lnYjc0Y9Ir95wTZOq_nlzZxaYfp52ao/edit
(22 slides, design system af64c8e1..., 2026 Official Workato Template snapshot 830e03cd).
QA: all 22 slides rendered + inspected; 3 defects found and fixed (frontier-II title overflow,
two-column rebalance x2); chart slide verified at LARGE; Check_Widowing findings triaged as
expected noise (auto-fit titles, mixed-size elements confirmed by render).
Optional outsourced hero images: ~/Documents/workbench/sg-lunch-learn/image-prompts.md.

## Design rebuild v2 (2026-10-25, after Josh rejected flat layout use)

Josh: "54+ layouts and you used 5." Rebuilt on 15 distinct native layouts: 01 Title, 15 Card
Four Up (stat wall), 07 Basic x4, 25 Quote (problem), 08 Two Column (Act 1), 27 Divider Teal
(thesis), 19 Callout Dewy A ("81% waste" badge on Dewy's signboard), 37/40 dark (Frontier
II/III), 14 Card Three Up (org chart), 38 Two Column Dark (prove it), 17 Callout 1/2 (diet),
13 Card Two Up (Act 7), 20 Callout Dewy B (zoom result, badge replaced with text box: Dewy B
has no rendered signboard), 09 Three Column (today), 39 Three Column Dark (close), 53 Thank
You Dewy. Plus mermaid zoom-cone diagram on Frontier I and the corpus line chart.
14 superseded slides deleted via Delete_Slide chain (Batch_Update request JSON kept getting
corrupted with \r\r escapes in slideIds; fell back after two 400s).
Lessons recorded: Dewy A has a real signboard, Dewy B does not; full-deck render QA every time.

## Final trim to 15 slides (2026-10-25 v3, after Josh: "too long, text too small, HOW not WHAT")

22 to 15 slides. Josh's mid-turn directive: talk about HOW we solved problems, not just that
we solved them. Merged: Act 0 into the quote slide; foundation+fleet into Card Two Up with
mechanism bodies ("HOW:" lines); frontier II+III into Card Two Up Dark; diet+zoom+value-ledger
into a stat-infographic numbers wall (Figtree Bold 30pt values + 14pt labels, template recipe).
Every surviving slide carries its mechanism. Stat values capped at 32pt (40pt overflows the
129pt card columns and wraps mid-number; 32pt verified). Layouts used: 01, 15, 25, 08, 27, 13,
19, 07+diagram, 07+chart, 14, 38, 41-style wall, 39, 53.

## v4 story-beat rewrite (2026-10-25, after Josh: big statements, no jargon, then demos)

Opening fixed to the TRUE framing: "The memory existed. The system didn't." (Josh: memories,
skills, and scripts DID exist pre-harness; what was missing was organization, self-improvement,
depth). Stat wall moved to slide 12 (useless as opener, good as scale-at-the-end). Every slide
is now a story beat in plain words: "So I cleaned house." / "Then I gave it a nervous system."
/ "Then I taught it to read everything." / "Then it started teaching itself." / "Now it's a
team, not a pile." / "The receipts." / "It read everything." Jargon stripped (Maildir, factlets,
launchd plists, verdict ledger all translated). Three-chapter feel → hand-off to live demos.
Stray rectangle on the stat-wall screenshot = Slides UI editor artifact, not slide content
(object model shows only the 6 elements).

## v4.1 dark stat wall (2026-10-26, after Josh: "could be much cooler")

Rebuilt "What exists today" on Blank layout + #083763 background: 52pt Figtree Bold values in
the four brand accents (teal #00D4D8, violet #C3A9FF, gold #FFC700, lime #C8E832), matching
60x4pt underline bars, Figtree 14pt white labels, Besley title. Old light-blue card version
deleted. Lesson: Blank + brand accent composition beats the pale Card Four Up for stat walls;
the light cards left 70% dead space.

## FINAL (2026-10-26, Josh): deck is good the way it is — hands off

ChatGPT (Josh's session) added two OpenAI ImageGen illustrations to the "nervous system" slide
(mcp_img_sgll-img-guardrail-v1 / mcp_img_sgll-img-helpers-v1, 244x122 per card) and bumped its
card text to 25pt bold, with an attribution speaker note. Josh ruled the deck FINAL.
Honesty note: 8 Style_Text bumps (frontier-dark2up cards 12->22, orgchart 12->18, close columns
12->20) landed in the minute before Josh's stop message; deck untouched since. If any of those
sizes look wrong on the big screen, previous values were 12pt across.

## Harness architecture HTML map (2026-10-26)

Self-contained branded diagram at ~/Documents/workbench/sg-lunch-learn/harness-architecture.html
(Workato 2026 tokens inline, Besley + Figtree, headless-Chrome render verified). Six layers:
L0 Josh approval gates, L1 fleet (12 agents role-coded), L2 attention/memory core (bus, claim/
error ledgers, mission control), L3 the brain (corpus/fractal/zoom/evals/precedent judge),
L4 execution surfaces, L5 the work; plus the 5-step self-learning loop and stat rail.
Note: arch-diagram skill's .mmd convention stays for project maps; this HTML is the harness-
level companion to the 3D atlas (harness-graph.py serve).

## v2 flow tab (2026-10-26, after Josh: show the connections, nothing is linear)

harness-architecture.html now has two tabs: "Layers" (the original stack) and "How it connects"
(a hand-composed SVG network graph, 8 nodes / 18 edges: Me <-> brain <-> corpus <-> nervous
system <-> hands <-> the work <-> the learning loop, plus the fleet node; approval routes around
the right edge, proposals return up the left, canon write-backs close the cycles; color-coded
edge families with a legend; #flow URL hash deep-link; verified by headless render).

## v3 flow cleanup (2026-10-26, after Josh: lines chaotic)

Rewrote the flow graph with orthogonal border routing: short straight arrow pairs for adjacent
nodes (Me<->brain, brain<->corpus, corpus<->nervous, hands<->work, work<->learning), the three
long connections (proposals up, standing orders down, closeouts across the top) routed along
the canvas margins as orthogonal polylines. ZERO edge crossings; middle of the canvas stays
open; legend below. Design lesson: for hand-built SVG graphs, border-route every edge that
spans more than half the canvas; the center is for adjacency, the margins are for reach.

## v5 presenter mode (2026-10-26, after Josh: good not great; click-through layers)

Flow tab rebuilt as a 9-step story player following Josh's arc (Me > brain > corpus > nervous
system > hands > fleet > work > learning loop > whole system): canvas extended taller (viewBox
1160x1070, generous gaps), each node/edge group tagged data-step, and JS steps through them:
current step glows, past steps fade to 15% + dashed edges, future hidden. Sticky caption bar
(step title + one speakable line + Replay/Prev/Next + counter), arrow-key navigation, deep
links like #flow-5 open mid-story, finale lights everything. Verified at steps 1, 5.

## v6 widescreen + fullscreen + layers presenter + AI polish (2026-10-26)

Josh approved the look ("looking really good") and asked for: presenter mode on Layers (done:
7-step player, sticky top caption bar, defaults to all-lit, Replay walks it, #layers-N deep
links), widescreen (wrap 1180 -> 1600px), fullscreen (button in tab row + 'f' key +
fullscreenchange label swap; headless can't exercise the API — needs one real click), and the
AI feel: aurora background (two slow brand-glow blobs), gradient headline (mint>teal>violet),
pulsing glow on the current step (flow + layers), animated footer bar, card hover lift/glow,
stat text-shadows, backdrop-blur caption bars, reduced-motion respected.

## v6.1 unified fullscreen (2026-10-26, after Josh: fullscreen must span both tabs)

Tabs bar made sticky (pinned pill, blur backdrop, never scrolls away), Fullscreen restyled as a
right-aligned control (dashed violet, not a tab), keys: 1 = Layers, 2 = Flow, Tab = cycle views,
arrows step whichever view is active, f = fullscreen. Verified sticky behavior + deep links.

## v6.2 presenter font scale (2026-10-26, after Josh: fonts bigger on layers)

Layer titles 20->27px, card h3 13.5->17px, card body 12->14.5px, flowpills 12->13.5px, stats
22->30px + labels 11.5->13.5px, loop steps bumped, caption bars h4 17->22px / p 13->15px.
Render-verified at 1800px.

## v7 camera (2026-10-26, after Josh: camera should follow the presentation)

Layers view wrapped in a #stage camera div. While stepping: renderLayers() scrollIntoView-centers
the current layer (smooth pan; the camera follows). Parallax: the .aurora backdrop translates at
-0.12x scroll rate, so background drifts slower than content = depth while panning. At the last
step (7): the stage scales down (k = min(1, (innerHeight-240)/stageHeight), 1.1s ease, negative
margin trims dead space) and scrolls to top: the camera zooms OUT to frame the full stack.
Going back/Replay resets scale(1). Verified panning via deep link.

## v8 the app is the show (2026-10-26, Josh: slides in-app, film tab, story realigned)

harness-architecture.html is now a 4-tab app: Slides (all 15 deck slides rebuilt as native HTML,
fixed 1280x720 canvas uniformly scaled, player with counter + captions + #slides-N deep links,
same glow/aurora styling, "Now: the demos." closer), Layers (unchanged presenter), How it
connects (unchanged), The film (local embed of ~/Downloads/a-way-for-the-system-to-know-itself.mp4,
76MB, copied to sg-lunch-learn/; Fullscreen-film + Restart buttons; video element fullscreen).
Slides reordered to match the layers arc: nervous system -> 81% diet -> hands/read-everything ->
growth -> teaching itself -> team -> receipts -> scale -> numbers -> three things -> thank you.
ChatGPT's two ImageGen illustrations could NOT be extracted from the Google deck (auth-gated
URLs return HTML); HTML slides use native visuals instead (cone rows, chart SVG, stat walls).
Keys: 1..4 jump tabs, Tab cycles, arrows step the active player, f fullscreen.

## v8.1 landing + fullscreen persistence (2026-10-26)

App lands on the Slides tab by default (HTML show class + activeView init moved); fullscreenchange
now re-asserts the active tab (activate(activeView)) and re-fits the slide canvas, so entering or
exiting fullscreen can never bounce to another tab; fullscreen padding selector fixed to
html:fullscreen body (body:fullscreen never matched since html is the fullscreen element).

## v8.2 slides fullscreen fixed + test-first (2026-10-26, after Josh: test and validate)

ROOT CAUSE of the earlier "loses tab focus" was mine: the Fullscreen button carried class "tab",
so querySelectorAll('.tab') bound it into activate(t.dataset.view) = activate(undefined) which
stripped .show from every view. Fixed: selector now .tab[data-view] + activate() guards unknown
names. Slides fullscreen: html.fs-slides hides page chrome and fits the slide to the viewport
(uncapped scale); BUG FOUND BY SCREENSHOT TEST: absolute+margin-auto centering broke because
backdrop-filter on .slideareawrap creates a positioning containing block -> switch to flex
centering on a 100vh slideareawrap; verified with the #slides-fs test hook (same class+scale path
the real fullscreenchange handler runs). Click on the slide advances in fs mode.

## v9 feedback batch (2026-10-26, Josh's slide-by-slide + behaviors)

1. 81% tool-cleanup slide REPLACED: now "What a knowledge lookup cost: 10.4x less content per
answer, once the zoom went live" (before: whole files / after: right 200 words, 64->92%).
2. Chart label moved off the line (top-right, anchor end).
3. Cone slide: nested viewfinder frames (hubs > factlets > sections > chunks > glowing 200-word
core) replace stacked rows; description broadened: integration patterns, AI engineering,
connected platforms, CS underneath.
4. Measurements labels: 55% "after the tool cleanup"; +37pts "of accuracy judging my triage
queue, vs a model 25x the price".
5. Layers reset to position 1 on tab-away (activate() resets + renders without scrolling).
6. Flow tab got the camera: pan to current node, finale zoom-out; BOTH zoom-outs floored at 0.8
(layers was zooming too far).
7. Film sound: ffprobe confirms h264+aac stereo track exists; film.volume=1 set; if still silent
in-browser it is system/tab volume, not the file.
8. NEW Ops console tab: iframe embed of harness-ops-console.html (220KB self-contained claude.ai
artifact copy); renders verified; its own Fullscreen console button.
9. NEW 3D atlas pop-out link in the tab bar (localhost:8770, new tab).
All verified by headless renders except the real Fullscreen API click (human-only).

## v8.3 (2026-10-26): title slide now "From Out-of-the-Box to a Workato Building Powerhouse" (render-verified)

## favicon (2026-10-26): WKTO logo added as inline data-URI favicon (128px png, 7.3KB b64)
Caveat: Chrome does not display favicons for file:// pages at all; it will show when served over
http. Source file kept at sg-lunch-learn/wkto-logo.png.

## ops console replaced (2026-10-26): swapped in Harness Ops Console.html (newer export). Note:
## the console's own header says Snapshot 2026-10-22 — that date is baked into the export; if
## fresher numbers are wanted, re-export the artifact from claude.ai and re-copy.

## descender fix (2026-10-26): gradient-clip titles clip descenders at tight line-height; .sl-title.grad
now line-height 1.22 + padding-bottom .14em (margin-compensated). The "g" in "Building" renders fully.
Apply the same treatment to any future background-clip:text headline over dark slides.

## v10 layout-variance round (2026-10-26, after Josh: "strongly dislike the repeated two-box layout")

Four slides rebuilt as distinct compositions, no two-card repeats left:
S3 cleaned house = text + before/after SVG (scattered colored cards -> teal arrow -> tidy folder
with lime checks); S5 nervous system = full-width SVG nervous-system band (spine, branching
neurons, shield nodes "blocks bad writes", synapses "checks each other's work"/"saved with
receipts", speech bubble "asks me real questions" to a gold person icon); S9 teaching itself =
cycle diagram (nightly 3am -> mine -> propose -> build -> back) + two callouts ("I approve from a
list" / "It learned my judgment: +37pts of accuracy, vs 25x the price" - overflow fixed by
rewrapping); S11 receipts = typographic scoreboard (orange X "7 tasks" vs glowing teal check
"cited the real doc", 1.7x as footnote). S7 cone slide text now credits physics, neuroscience,
biology + fractal explainer (lungs/ferns/coastlines/lightning). Header h1 descender fix
(line-height 1.22 + padding). All render-verified.

## v11 copy-clarity round (2026-10-26)

Receipts slide: context added ("12 real platform questions: billing, limits, how-things-work");
real bench numbers used: Without 11 of 12 (the miss: billing question answered "7 tasks",
confident, no source) vs With it 12 for 12, every answer citing the real doc. Measurements slide:
rubric subtitle added ("accuracy against my own past verdicts, backtested on 80 real findings; a
point = the judge's call matched the call Josh actually made"). Cycle slide rebuilt as a clean
ring (5 nodes ON the circle, labels outside with halo, no overlaps). Layers: prod writes moved
LAST in the approval cards (rare + big deal), Red team wording ("before anything is submitted for
production promotion"), SRE spelled out, MRR spelled out (mean reciprocal rank: how high the
right answer ranks), KB daemon explained (one shared always-warm search index). All verified.

## v12 finale-step split (2026-10-26, after Josh: zoom-out was firing before the loop)

The layers presenter now has 8 steps: the self-learning loop is presented FOCUSED at full size as
step 7, and the zoom-out happens only on Next PAST it (step 8 "The whole system"). Verified at
7/8: camera panning, Next enabled.

## v13 console freshness + live link (2026-10-26)

Caption bar removed from the Ops console tab (Josh hated it; global Fullscreen button covers
fs; verified 0 page errors after removal). Snapshot staleness explained: the console goes live
ONLY via window.claude.use("mcp") inside claude.ai; any downloaded copy renders its embedded
snapshot (both of Josh's exports were byte-identical, snapshot 2026-10-22). Added a
"Live console" pop-out link to the claude.ai artifact (sk token included in the app file -
local-only file, acceptable) next to the Ops console tab. Josh will re-export a fresher
snapshot; swap = copy over harness-ops-console.html.
Playwright-core CAN drive local-file pages here (found at @playwright/mcp/node_modules with the
1248 chromium binary) - used for ground-truth page tests; the Workato/Google-UI Playwright ban
does not apply to local fixtures.

## v14 (2026-10-26 evening): voice rule + RAG++ explainer + six things + fresh counts

VOICE HARD RULE saved to memory (voice-skill-everything-including-decks.md + MEMORY.md): josh-
writing-voice applies to EVERY artifact including decks; zero em/en dashes, grep before handoff.
App purged (0 em dashes). RAG++ explainer added to the zoom slide ("why the double plus": RAG =
one lookup; RAG+ = keywords AND meaning + reranker; RAG++ = fractal zoom + rarity/importance-
bending relevance + eval gates on every leg). Takeaways slide = SIX things 3x2 (foundation,
organize files, measure everything, trust is earned via the trust ladder, attention mechanism,
give it hands / build missing tools); plus closing statement slide (If you can think it... /
steady measurement + big ideas). Session count freshened everywhere: 2,311 in last 30 days
(live ops console 10-26), replaces 751 in stat wall + surfaces card + loop rail ($1.86 rail
slot retired per Josh).

## v15 final copy-precision round (2026-10-27)

37pts framing CORRECTED per Josh's clarification: the +37pts is the context uplift (flash 0.25
alone -> 0.62 with precedents, same residue, 80 findings); separately, that cheap model WITH
context beat kimi-k3 WITHOUT it (0.62 vs 0.35). Callout: "+37pts of accuracy, from context
alone. / The same cheap model with precedents beat a bigger model without them." The 25x claim
REMOVED (it was backtest arm spend ratio, not official list pricing - not defensible as a price
claim). Cycle slide: even pentagon spacing, labels radially outside with halo, node subs
shortened inside circles, no overflows (settled-render verified). Voice rule holding: 0 em
dashes. Session stats: 2,311/30d live-verified.

## v16 truth-pass (2026-10-27, Josh's metrics-accuracy round)

10.4x slide: credit corrected ("once RAG++ went live"; "We already had RAG. Then came the fractal
zoom and entropy scoring, and efficiency and accuracy took off") - not zoom-alone, not a gimmick.
"zoom trick" language purged everywhere ("one zoom method"; "deliberate architecture, not a
gimmick" eyebrow). Measurements subtitle: short + truthful method line (0.25 alone -> 0.62 with
RAG++ precedents, beating a bigger model without them; NOT vs Jev directly - the TypeSafe framing
removed). 450 hrs: "of measured engineering value, per the ledger" (measured across a 5-day
window, not PRODUCED in 5 days). Nervous-tree lower branch now ends at a "the claim ledger"
node chip (was dead-ending in air).

## v17 (2026-10-27): retrieval naming precision

Layers L3 "Zoom retrieval" card renamed "Layered lookup" with the full mechanism chain (parallel
keyword+meaning, reranker, entropy scoring, then the zoom; 64->92%). Slide 6: "Why the double
plus" -> "That is the RAG++ in the name:" so the term is actually said. Zoom is one mechanism
among several, never the whole story.

## v18 (2026-10-27): Ops console tab removed

The in-app snapshot console is gone (too stale-prone to keep re-downloading); the Live console
pop-out link to the claude.ai artifact is THE console surface now. Tabs: Slides / Layers /
How it connects / The film. Verified: 4 tabs, slides landing, 0 page errors. The stale
harness-ops-console.html copy remains on disk unused. Keymap: 1..4 = tabs, Tab cycles, arrows
step the active player, f = fullscreen.

## 450-hrs methodology verified and stated (2026-10-27, Josh asked for the real number)

Verified from KT/reviews/harness-cost-benefit-2026-10-11.md: 450.5 hrs = sum of per-item CLASS
heuristics (how long the work would take a person) over 197 completed ledger rows in a 5-day
measurement window (build 192h, jira 102.5h, harness 64h, cortex 42h); conservative by policy,
incident-prevented value NOT counted (understated to the floor). Slide label now states the
method: "of class-scored engineering work: 197 ledger items in 5 days, each scored by how long
it would take a person" (both spots). So yes: real number, story-point-style scoring, and the
5 days is the measurement window.

## v27 (2026-10-27): "A Brief History of Me and AI" slide added after the title

Hawking play (with-apologies subtitle), Chapter 0 eyebrow, six wry beats in Josh's voice (2016
Alexa naming / 2023 one email whole weekend / 2024 tabs / Jul 2026 two robots one caffeine
budget / Sep 2026 the boring load-bearing folder / Oct 2026 this talk), name + Enterprise
Architect title in the footer. 17 slides now.
Title corrected to "Josh Cramoy · BT Enterprise Architect, Workato" (render-verified 2026-10-27).

## v30 history beats (2026-10-27, Josh's dictated chronology + click-reveal)

Slide 2 beats, his words: 2016 Alexa naming / 2019 "I start asking Siri questions. She
immediately hates me." / 2023 ChatGPT one email whole weekend / 2024 "Vibe code my first full
stack AI app. Still not retired, so..." / Jul 2026 "Two Robots, 1 Man, Too much caffeine. I get
stern emails from my VP." / Aug 2026 "the AI Model Gateway finds me, lost and broken. A
lifeline." / Sep 2026 boring load-bearing folder / Oct 2026 this talk. Each beat appears on
click (fade-rise + teal glow pulse), Next/arrows/clicks sub-step through them before advancing;
Prev un-reveals. Playwright-verified: 2 beats shown after 2 presses, 0 errors.

## v31 (2026-10-27): four opening beats added to the history slide

2008 full time wannabe rockstar / 2012 coffee brewers + free ones if they got mad enough / 2013
learned HTML/CSS and broke a dog walker's website / 2014 learned what an API was. 12 beats
total, all click-revealed, verified 12/12 shown at font 20/lh 1.6 with no overflow.
Sep 2026 beat reworded: "I put everything into organized folders." (2026-10-27)
Removed the stray "haha" from the history slide footer (2026-10-27); it made no sense there.
Added closing beats: "Oct 2026: Anthropic files to go public. Coincidence? 🤔" and "Today: this
talk." 13 beats total, all click-revealed, fits the canvas (verified at full reveal).

## session-count resolution (2026-10-27, Josh's mining question)

The 751 was a slide-stat error by the builder (me): a point-in-time ls of ONE project dir
(workbench), presented as the harness total. Reality: dream-mine.py ALREADY dynamically
enumerates ALL of ~/.claude/projects/* (91 dirs, sorted listdir, mtime-filtered .jsonl per
window) - no registration needed, new projects self-register by existing. Live counts:
2,604 transcripts across 91 projects (805 workbench); ops console 30-day distinct: 2,311.
Slide + brief updated to 2,311/2,604; "HTML/CSS" -> "HTML/CSS/JS" per Josh.

## v32 stage-setter slide (2026-10-27)

New slide 3 "What is this thing?" (dark): What it is (self-learning AI dev system, one builder +
12 governed agents) / What it does (plans-builds-tests-documents-promotes; triages Jira; writes
its own knowledge) / Why it matters (it compounds) / Shipped so far (Google Workspace MCP,
Multi-Genie Orchestration, Google Slides v2, Dev API Semantic MCP, Workday payment elections v2,
HR Genie skills, the harness) / chips: 517 points, 130 tickets, 2,311 sessions (30d).
INCIDENT during insert: a duplicated footer tail closed #slideboxwrap early and dropped all later
slides from the player DOM (count 2); repaired by deleting the 3 stray lines; verified 18 slides
in the player, correct order, slide 3 renders. Lesson: multi-editing one live HTML with racing
python inserts needs a structure check after each write.
2024 beat: "I'm still not retired, so...🤷" wording (2026-10-27).
Emoji corrected to the proper 🤷‍♂️ ZWJ sequence (first pass wrote 🤣 by mistake).

## v33 (2026-10-26 late): hands slide + shipped additions, second seam corruption repaired

- Added "Then I gave it hands." slide (index 7, after the nervous-system slide): introduces the
  tool cadre (AIRO MCP, wt CLI wrapper, Atlassian MCP, Slack MCP, skills, Orca browser) wired to
  the Workato lifecycle (intake, build, test, promote, document, watch).
- "Shipped so far" extended with Estate Monitor + Auto-Triage & Investigation.
- **Second structural corruption from a racing python insert, same class as the first:** the
  hands-slide insert duplicated the nervous slide's tail ("Anything risky..." + sl-bar + close)
  at the seam, closing #slideboxwrap early (7 slides inside, 12 outside). Root cause pattern:
  anchoring an insert on the END of a slide and re-emitting the anchor tail. Fixed by deleting
  the orphan fragment. Playwright ground truth after fix: 19 slides in wrap, 0 page errors,
  clean render at #slides-6.
- LESSON (twice now): slide-insert scripts must anchor on the NEW slide's OPENING tag and never
  re-emit the anchor's closing tags; verify with in-wrap slide count + pageerror listener every time.
