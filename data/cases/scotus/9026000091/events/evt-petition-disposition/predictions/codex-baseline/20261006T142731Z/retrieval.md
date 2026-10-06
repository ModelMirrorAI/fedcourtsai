# Retrieval record

- Read committed `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist/CVSG cuts, and sal-v4 segment table. Read `metrics/statpack.json` for exact baseline reached-rate arithmetic across the displayed prior Terms 2017–2025. No individual case outcome was read.
- Web search: `site.supremecourt.gov opinions CRST Van Expedited EEOC 2016 preclusive judgment prevailing defendant`. The tool returned no usable result content.
- Web open attempt: `https://www.supremecourt.gov/opinions/15pdf/14-1375_6k47.pdf`. The tool returned no usable document content; this attempt did not verify the authority.
- CourtListener MCP `search`: type `o`, query `caseName:"CRST Van Expedited"`, court `scotus`, three results requested. Failed with HTTP 429, daily rate limit exceeded. No opinions were returned or read.
- Corpus fallback: `uv run fedcourts query --court scotus --citation '578 U.S. 419' --limit 1`. Returned no prior; stderr explained that only 200 SCOTUS rows carry reporter citations and the empty match is likely a coverage gap. Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
- Freshness check: `uv run fedcourts corpus-info`. Failed because the service backend has no client-side connection. No corpus freshness stamps were obtained and no transfer line was printed.

The initial `uv run fedcourts paths --court scotus --docket 9026000091 --event evt-petition-disposition --role predictor` failed because the default cache path was read-only. Repeating with a writable temporary cache succeeded. Subsequent CLI calls used the same temporary-cache override. Path resolution and schema reads were operational checks, not case retrieval.

No query sought this petition's disposition or subsequent history. No retrieval supplied outcome-revealing material.
