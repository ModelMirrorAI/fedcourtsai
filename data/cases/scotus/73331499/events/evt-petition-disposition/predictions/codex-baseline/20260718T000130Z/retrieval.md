# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 Term paid/IFP detail in `metrics/statpack.json`; the paid-petition estimated grant rate was 5.36%.

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 10`
  - No results and no `ranged corpus reads` line were returned; the corpus-service request ultimately timed out.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 5`
  - Error: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`
  - No `ranged corpus reads` line was printed.

## CourtListener MCP

- Opinion search for `"shed DNA" warrant Fourth Amendment genetic profile abandoned`, limited to filings before July 18, 2026. It returned metadata for five results, including *State v. Sharpe*, *Raynor v. State*, and *State of Iowa v. Jerry Lynn Burns*.
- `get_endpoint_item` for opinion API id `10692515` initially received a short throttle response and then returned an unrelated *Hawkins* opinion because the web-result cluster id had been mistaken for an opinion API id. That opinion was excluded and did not inform the forecast.
- Exact opinion search for `State v. Sharpe` in Connecticut, limited to January 1, 2025 through July 18, 2026. This resolved cluster `10692515` to opinion API id `11297993`.
- Three attempts to retrieve opinion API id `11297993` were throttled and returned no opinion text.
- A further opinion search for `"shed DNA" "State v. Sharpe"` was also throttled and returned no result.

No web searches were used. No CourtListener search targeted this case, its docket, or its disposition.
