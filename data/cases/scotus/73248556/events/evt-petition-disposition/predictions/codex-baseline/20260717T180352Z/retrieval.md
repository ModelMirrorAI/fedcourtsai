# Retrieval beyond provisioned inputs

## Corpus and base-rate material

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Relevant estimates were: 5.36% grants for paid Term 2025 petitions; 4.8% grants for modern discretionary-cert petitions originating in the Fifth Circuit; 0.8% grants for petitions with zero relists; and 3.0% grants where there was no CVSG.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  - `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
  - Returned recent granted SCOTUS priors. They supplied general calibration but no close doctrinal comparator.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 8`
  - `ranged corpus reads: 197 GET(s), 51511296 byte(s)`
  - Returned recent denied SCOTUS priors. They supplied general calibration but no close doctrinal comparator.

## CourtListener MCP

- Searched published SCOTUS opinions for `United States v. Hemani`, limited to June 17–19, 2026. The search returned the June 18, 2026 opinion at `/opinion/10876933/united-states-v-hemani/` (cluster 10876933; opinion 11344434).
- Retrieved opinion 11344434 from the opinions endpoint. The opinion confirms a unanimous judgment affirming the Fifth Circuit, with a seven-Justice opinion holding the § 922(g)(3) prosecution unconstitutional, expressly reserving § 922(g)(1), and separate concurrences.
- Searched SCOTUS dockets filed in 2026 for `United States v. Cockerham`, `United States v. Mitchell`, and `United States v. Doucet`. Each search returned zero results. The cited denial dates therefore come from the provisioned brief in opposition, not from those MCP searches.

No search targeted this case's disposition or post-snapshot history.
