# GSlides MCP architecture

Two surfaces, one pipeline: the dev and prod MCP servers (mcps-Ab9w3HK9-CRK-CD,
mcps-AbEdNLHX-43z-CD) each serve a 62-tool fleet whose every recipe carries the
canonical validate → acquire → claim → connector call → release → guidance helper
→ return shape; the shared helper (dev 82864228, prod 82872520) reads the EC
knowledge base for guidance, fail-open-writes release telemetry into tables
157628/157744, and the nightly compiler agent reads that telemetry and applies
accepted improvement proposals to the Confluence guidance pages that both Confluence
syncs (dev 82864023, prod 82873160) parse back into the knowledge bases; the
Frontify refresh (82928714) closes the loop by regenerating Confluence's canonical
color region every 24h. `asset-graph.mmd` is the source of truth (render with
`npx -y @mermaid-js/mermaid-cli -i asset-graph.mmd -o asset-graph.svg`); the SVG is
the Confluence-ready render. Topology IDs were live-read from the dev workspace on
2026-10-16 (wt api folder listings); prod twins are cited from the project kf.
