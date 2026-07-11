# Retrieval

## Corpus lookup

- Attempted: `uv run fedcourts query --court ca11 --decided-before 2024 --limit 10 --corpus-backend ranged`
- Result: failed before returning any priors because the configured object-store endpoint could not be resolved or reached. The command printed no `ranged corpus reads: ...` line.

## Base rates

- Consulted `metrics/statpack.md`, especially the resolved-case distribution for `ca11`. This is not motion-specific and was given little weight.

## CourtListener MCP

- Attempted an opinions search limited to the Eleventh Circuit and filings before March 25, 2024 for `"motion for reconsideration" "panel order"`, requesting five results.
- Result: no results were returned because the MCP server reported that its session-store configuration was unavailable.

No web searches were used. No case-specific retrieval was attempted after the provisioned snapshot disclosed the outcome.
