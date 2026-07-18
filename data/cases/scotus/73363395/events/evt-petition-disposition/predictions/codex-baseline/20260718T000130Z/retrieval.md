# Retrieval

## Base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate.

No `fedcourts query` or `fedcourts open-events` corpus lookup was used, so there is no ranged-corpus-read line to report.

## CourtListener MCP

- Opinion search: `"Seventh Amendment" "state courts" summary judgment`, restricted to SCOTUS opinions filed before 2026-07-18 (query id `7aeea2e3`).
- Opinion search: `"Seventh Amendment" incorporated states`, restricted to SCOTUS opinions filed before 2026-07-18 (query id `6e77517d`).
- Citation search: `241 U.S. 211` (query id `e69a0c4c`), which identified *Minneapolis & St. Louis Railroad v. Bombolis*.
- Opinions endpoint: opinion id `98733`, limited to the opinion text and basic metadata. The text states that the Seventh Amendment does not govern or regulate state-court jury trials.
- Opinion search: `"summary judgment" "Seventh Amendment"`, restricted to SCOTUS opinions filed before 2026-07-18 (query id `799f2417`).
- Opinions endpoint: opinion id `109964`, *Parklane Hosiery Co. v. Shore*, limited to opinion text and basic metadata. This was background on the Seventh Amendment and pretrial adjudication; it was not treated as a factually similar prior.

No web search was used. I did not retrieve this case's current docket, disposition, or subsequent history.
