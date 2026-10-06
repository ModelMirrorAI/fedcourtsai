# Retrieval record

- Read the committed `metrics/statpack.md`: modern discretionary-cert population, originating-circuit context, paid-segment relist and CVSG cuts, and sal-v4 per-Term reached-band table. Used only Terms 2017–2024 for the band anchor. Computed its denominator-weighted percentage locally from the displayed rounded values.
- Ran `uv run fedcourts paths --court scotus --docket 73500214 --event evt-order-cvsg-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded. This was path resolution, not a corpus lookup.
- Web search query: `site.supremecourt.gov opinions 2024 Cantero 22-529 May 30 2024`. No usable result content returned.
- Web open attempt: `https://www.supremecourt.gov/opinions/23pdf/22-529_1b7d.pdf`. No usable content returned; the URL was an attempted location, not a verified source.
- Web search query: `site:supremecourt.gov/opinions/23pdf "22-529" "Cantero"`. No usable result content returned.
- Repeated the same web open attempt once, again without usable content. These attempts targeted the 2024 opinion only, not the disposition of the pending petition. No external legal assertions were added from them.
- No `fedcourts query` or `open-events` calls, no ranged corpus reads, and no CourtListener MCP lookups. No target-case outcome, other prediction, or labeling-measurement artifact was consulted.

Local contract and schema reads and output validation are operational checks, not additional case evidence.
