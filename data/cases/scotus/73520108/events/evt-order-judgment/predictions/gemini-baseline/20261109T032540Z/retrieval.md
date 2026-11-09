# Retrieval Log

Consulted three `fedcourts query` lookups against the corpus to inspect resolved and granted SCOTUS priors:

1. `uv run fedcourts query --court scotus --disposition granted --limit 10`
   - `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Returned 10 recent SCOTUS granted dockets (including recent OT2025/OT2026 grants and interim applications).

2. `uv run fedcourts query --court scotus --disposition granted --decided-before 2026 --limit 10`
   - `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Returned 10 SCOTUS granted cert dockets from the OT2025 docket-number cohort.

3. `uv run fedcourts query --court scotus --disposition granted --decided-before 2025 --limit 10`
   - `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Returned 10 SCOTUS granted cert dockets from the OT2024 docket-number cohort.

No CourtListener MCP calls or open-web searches were attempted.
