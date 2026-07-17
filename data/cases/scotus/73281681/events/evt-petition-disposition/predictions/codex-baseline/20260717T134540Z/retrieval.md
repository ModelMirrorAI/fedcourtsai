# Retrieval

## Corpus tooling

- Attempted: `uv run fedcourts query --court scotus --era 2020s --citation '570 U.S. 595' --citation '601 U.S. 267' --limit 10`
  - The lookup failed because the remote corpus host could not be resolved. It returned no priors and printed no `ranged corpus reads` accounting line.
- Consulted `metrics/statpack.md`, especially modern cert dispositions, relist and CVSG cuts, and the 2025 Term table.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36% granted).

## CourtListener MCP

- Opinion search for `"monetary exactions" Koontz "in lieu" permit`, limited to opinions filed from 2021 onward. Results included *Anderson Creek Partners, L.P. v. County of Harnett* (N.C. 2022), the New York Court of Appeals opinion provisioned in the petition, and the July 29, 2025 *Sheetz* remand opinion.
- Opinion search for `Sheetz El Dorado County Koontz traffic impact fee`, limited to opinions filed from 2024 onward. Results included the Supreme Court's 2024 *Sheetz* opinion and the California Court of Appeal's 2025 remand opinion.
- Retrieved CourtListener cluster 10643795 and opinion 11110382 for the 2025 *Sheetz* remand. The opinion applied Nollan/Dolan to the monetary traffic-impact fee and affirmed because the record established nexus and rough proportionality.
- Searched the SCOTUS docket collection for docket `25-958`, the overlapping petition identified in the provisioned petition. CourtListener returned no result.

No web search was used. No lookup sought the disposition of scotus/73281681.
