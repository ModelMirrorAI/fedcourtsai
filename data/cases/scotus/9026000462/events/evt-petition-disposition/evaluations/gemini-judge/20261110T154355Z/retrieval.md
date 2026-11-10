# Retrieval log

- Rebuilt the statpack in force when the candidates ran (`run_id: 20261008T143010Z`):
  `uv run fedcourts statpack-at data/cases/scotus/9026000462/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  Resolved build `1c4f550b7b750b758c0f5dbb4d505b8159cd8e93fee5` (`sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`, landed `2026-09-28T08:12:04-04:00`).
- No `fedcourts query` or `fedcourts open-events` corpus lookups, no CourtListener MCP lookups, and no web searches were performed beyond the provisioned inputs.
