# Retrieval log

- Read the committed `metrics/statpack.md`, especially “The interim docket (applications),” its caveats, and Term rows. Used only 2016–2025 for the Term-2026 disposition baseline. Inspected top-level keys and searched timestamp-related keys in `metrics/statpack.json`; no corpus freshness timestamp was recovered. No individual cases were retrieved from it.
- Web search: `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 190 stay reasonable probability fair prospect irreparable harm`. The tool returned no usable result content. This was a general preexisting authority search, not a search for this application's outcome.
- Web open: the exact pre-decision application URL in the provisioned manifest, `https://www.supremecourt.gov/DocketPDF/26/26A449/428352/20261002161514837_26A449.pdf`. The tool returned no usable content. No current docket or subsequent history was requested.
- CourtListener MCP `search`: `type=o`, `citation=558 U.S. 183`, `num_results=1`, fields `caseName`, `dateFiled`, `citation`, `absolute_url`, `opinions`. Returned HTTP 429, reporting the 300/hour limit and an approximately 512-second wait. No case content returned; no REST fallback or retry.
- No `fedcourts query` or `open-events` calls. No ranged corpus reads or transfer lines were produced. The local `fedcourts paths --court scotus --docket 9526000449 --event evt-motion-disposition --role predictor` command resolved paths only; its initial cache-permission failure was remedied by using a temporary writable cache.

No outcome-revealing material was obtained. Contract/schema reads and local validation are administrative rather than substantive retrieval.
