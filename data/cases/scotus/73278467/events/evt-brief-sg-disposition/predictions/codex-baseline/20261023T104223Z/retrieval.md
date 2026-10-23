# Retrieval log

- Read the provisioned event, context, September 26, 2026 snapshot, document manifest, questions presented, SG invited brief, and relevant portions of the petition, brief in opposition, and cert reply. No other cell's output or realized outcome was read.
- Consulted committed `metrics/statpack.md`: paid scored-segment relist and CVSG cuts and the sal-v4 reached-band table. Inspected `metrics/statpack.json` for generation/vintage metadata; no relevant metadata was exposed by that check. Computed the prior-Term high-band mean from the displayed markdown rows: approximately 34.951%, weighted n=898, Terms 2017–2024. No live corpus query was made, so there is no ranged-corpus-read transfer line.
- General-law web search: `site.supremecourt.gov Lawrence v Chater 516 U.S. 163 GVR reasonable probability`. No usable result returned.
- General-law web search: `Lawrence v. Chater 516 U.S. 163 1996`. No usable result returned.
- Attempted to open the official reporter PDF at `https://www.govinfo.gov/content/pkg/USREPORTS-516/pdf/USREPORTS-516-163.pdf`. No usable content returned. Relied on the provisioned SG brief's discussion, not on any successfully retrieved external opinion.
- No CourtListener MCP requests, current-docket requests, or case-outcome searches were made. No substantive web material informed the forecast.

Local tooling: `uv run fedcourts paths --court scotus --docket 73278467 --event evt-brief-sg-disposition --role predictor` initially failed because the default uv cache was read-only; the same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache`. This changed no input or pipeline file.
