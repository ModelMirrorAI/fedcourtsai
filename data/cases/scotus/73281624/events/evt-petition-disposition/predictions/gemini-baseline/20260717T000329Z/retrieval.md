# Retrieval

- `uv run fedcourts query --help`
  - Explored corpus query options. (Command failed due to incorrect usage, checked help).
- `mcp_courtlistener_search` (Court: scotus, Query: `"market participant exception" AND "state action immunity"`)
  - Found 3 priors: *Federal Trade Commission v. Phoebe Putney Health System, Inc.* (568 U.S. 216), *South-Central Timber Development, Inc. v. Wunnicke* (467 U.S. 82), and *City of Columbia v. Omni Outdoor Advertising, Inc.* (499 U.S. 365).
- `mcp_courtlistener_search` (Court: all circuits, Query: `"market participant exception" AND "Parker immunity"`)
  - No results.
- `mcp_courtlistener_search` (Court: all circuits, Query: `"market participant exception" AND "state action immunity"`)
  - No results.
- `metrics/statpack.md`
  - Consulted base rates for modern discretionary-cert petitions and originating circuit (ca4 base rate: ~4.6% granted).
