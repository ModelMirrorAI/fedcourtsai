# Retrieval log

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” relist and CVSG cuts, and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025 Term's paid-petition estimate (5.36% grant rate) and the very small Supreme Court of Kentucky bucket (two resolved petitions, both denied; not treated as a stable case-specific rate).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation '574 U.S. 352' --era 2020s --limit 10 --corpus-backend ranged`
- Result: failed before returning any rows because DNS resolution for the configured S3 corpus store failed. No `ranged corpus reads: …` line was printed.

## CourtListener MCP

- Opinion search: `RLUIPA "Equal Terms" "substantial burden" land use`, filed January 1, 2015 through July 16, 2026, ordered by relevance. The results confirmed recent appellate authorities discussed by the petition, including *Spirit of Aloha Temple v. County of Maui*, *New Harvest Christian Fellowship v. City of Salinas*, and *Canaan Christian Church v. Montgomery County*.
- Citation search: `727 S.W.3d 400`. It returned no results, so no independent CourtListener copy of the Kentucky Supreme Court opinion was available.

No web searches were used. No retrieval sought or revealed this petition's Supreme Court disposition.
