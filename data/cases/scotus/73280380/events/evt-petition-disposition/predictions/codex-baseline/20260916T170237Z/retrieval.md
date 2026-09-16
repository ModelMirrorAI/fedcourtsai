# Retrieval record

- Read `metrics/statpack.md`: modern discretionary-cert disposition section, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Used only Terms 2017-2024 for the reached-band anchor. Calculated an approximately 17.24% denominator-weighted reached rate from the published rounded figures (n approximately 2,810).
- `web.run` search: `site.supremecourt.gov opinions 2025 Bost Illinois State Board Elections January 14 2026 24-568`. No usable result was returned.
- `web.run` search: `site.supremecourt.gov "24-568" "2026" "Bost"`. No usable result was returned.
- `web.run` attempted open of `https://www.supremecourt.gov/opinions/25pdf/24-568new_4gcj.pdf`. No usable output; this attempted locator was not verified and is not an evidentiary source.
- CourtListener MCP `search`: `type=o`, `case_name="Bost v. Illinois State Board"`, `court=scotus`, `num_results=3`, `filed_before=2026-01-17`. Returned HTTP 429, with a reported wait of 332 seconds. No opinion text obtained; no REST fallback used.
- No `fedcourts query` or `open-events` lookup and therefore no ranged-corpus transfer line. No target-case live docket lookup, subsequent-history search, or other predictor's output was consulted.

Operational, not substantive retrieval: read task instructions and output schemas; ran `fedcourts paths` for this cell. The initial uv invocation could not write its default cache; rerunning with a writable temporary cache and `--no-sync` succeeded. Provisioned filings and snapshot are identified in `reasoning.md`.
