# Retrieval

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic "expressive association" --era 2020s --limit 8`
  - Failed before returning rows because the runner could not resolve the corpus S3 endpoint (`EndpointConnectionError`).
  - No `ranged corpus reads: ...` line was printed because the remote connection failed before a read completed.

## Base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert dispositions, relist counts, CVSG status, and the 2025 Term row.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition grant estimate.

## CourtListener MCP

- Opinion search for `"expressive association" AND (antidiscrimination OR discrimination) AND (leadership OR membership)` in federal appellate courts since 2020: no results.
- Semantic opinion search for `expressive association anti-discrimination law membership leadership` since 2020: returned general modern expressive-association and antidiscrimination decisions; used only as background on the developing legal context.
- Opinion search for *American Alliance for Equal Rights v. Fearless Fund Management* in the Eleventh Circuit during 2024: confirmed the published decision at 103 F.4th 765, filed June 3, 2024.
- Opinion search for *National Association of Diversity Officers in Higher Education v. Trump* in the Fourth Circuit since January 2026: no results.

No web searches were used. No lookup sought this case's disposition or subsequent history.
