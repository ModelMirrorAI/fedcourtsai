# Retrieval

## Committed base rates

- `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” the originating-circuit, relist, CVSG, and per-Term tables.
- `metrics/statpack.json`, 2025 Term paid-petition detail (estimated grant rate 5.36%).

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '84 F.4th 378' --limit 8`
  - The lookup failed before returning rows because the remote corpus host could not be resolved. It printed no `ranged corpus reads` line.

## CourtListener MCP lookups

- Opinion search for `"Takings Clause" "law enforcement" property damage`, limited to opinions filed from 2020 onward. Results included the relevant Seventh, Sixth, Ninth, Fifth, and Eleventh Circuit decisions: *Hadley*, *Slaybaugh*, *Pena*, *Baker*, and *Alford*. The search was used only to confirm the recent doctrinal landscape described in the provisioned briefs, not to seek this petition's disposition.
- Supreme Court opinion search for `"Baker v. City of McKinney" "Sotomayor" "Gorsuch"`; no results.
- Citation search for `145 S. Ct. 11`; the returned matches were not relevant to this prediction.

No web search was used.
