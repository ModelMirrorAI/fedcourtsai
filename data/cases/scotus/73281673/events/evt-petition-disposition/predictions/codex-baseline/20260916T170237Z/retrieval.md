# Retrieval record

## Local materials beyond the provisioned case inputs

- Read the governing `AGENTS.md`, `.github/prompts/predict.md`, and schemas for prediction, flags, and tooling outputs.
- Read `metrics/statpack.md`: modern discretionary-cert context, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Only displayed Terms 2017–2024 informed the elevated-band numerical anchor for this Term-2025 petition.
- Inspected scalar metadata in `metrics/statpack.json` for provenance; no build timestamp was present among those values. No case-level data was retrieved from that file.
- Executed a local Python weighted calculation over the markdown table: sum of reached-rate times denominator divided by total denominator = approximately 0.17237936, total denominator 2,810.
- `uv run fedcourts paths --court scotus --docket 73281673 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. This was path resolution, not a corpus lookup.
- No `fedcourts query` or `open-events` calls were made; no ranged corpus transfer line was emitted.

## External attempts

1. Web search: `site.supremecourt.gov "532 U. S. 774" "final"`. No usable result content returned.
2. CourtListener MCP `search(type="o", citation="532 U.S. 774", num_results=1)` to verify the general finality precedent Florida v. Thomas. Failed with HTTP 429, 300/hour limit, stated availability in 617 seconds. No opinion content returned. No REST fallback attempted.
3. Web search: `Florida v Thomas 532 U.S. 774 2001 final judgment Cox`. No usable result content returned.
4. Web open of official U.S. Reports PDF: `https://www.govinfo.gov/content/pkg/USREPORTS-532/pdf/USREPORTS-532-774.pdf`. No usable document content returned.

No external search sought Gasper's disposition, subsequent history, or current docket. No outcome-revealing material was encountered. No other predictor's output or labeling-measurement artifact was read. The failed external attempts contributed no substantive evidence.
