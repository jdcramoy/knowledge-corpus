# Enterprise Data MCP — project knowledge

Sibling semantic-layer design (Track A/B epics in BSYS: 28046 Semantic
Foundation, 28047 Self-Healing Semantic Layer, 28048 Semantic Learning
Flywheel — all in-progress, points on epics).

## Model

- Track A: retrieval algorithms/prompt/ranking; Track B: learning flywheel
  converting conversation telemetry into semantic improvements (metadata
  improvements, governed VQR promotion from recurring novel SQL, data-coverage
  gap classification).
- Epics define the taxonomy: retrieval hit/miss/missing-VQR/definition-gap/
  coverage-gap; promotion follows validation → approval → regression testing.
- Related stories: BSYS-27886 (index/semantic_model tools), BSYS-27064
  (Snowflake Semantic Views/RBAC/MCP evaluation), BSYS-28514 (ai_usage_mcp
  semantic layer files), BSYS-26681 (DSPy/GEPA prompt optimization).

## Related (KB bridges)

<!-- kb-bridges:v1 begin -->
- [How Workato Built Enterprise Data MCP](../../kb-corpus/blog/how-workato-built-enterprise-data-mcp.md)
- [Beyond APIs: How Enterprise MCP Powers the Next Generation of Data and AI Orchestration](../../kb-corpus/blog/enterprise-mcp-data-orchestration.md)
- [2026/06 June Lookback](../../kb-corpus/confluence/intbt/2612592679-202606-june-lookback.md)
- [MCP servers - Employee Offboarding Process](../../kb-corpus/docs/en/mcp/prebuilt-mcps/employee-offboarding-process-mcp-server.md)
<!-- kb-bridges:end -->
