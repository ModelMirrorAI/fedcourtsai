# Retrieval beyond provisioned inputs

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --limit 5`
  - `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
  - Returned five recent resolved SCOTUS priors. The useful qualitative contrast was that the returned grants had three or four distributions, while this petition has only its initial distribution; the sample was not treated as an aggregate rate.
- `metrics/statpack.md` and `metrics/statpack.json`
  - Consulted modern-cert disposition, originating-circuit, relist, CVSG, Term 2025, and paid-fee-class base rates.

## CourtListener MCP

- Opinion search for case name `Farr v. Grant`, Eighth Circuit, filed before May 26, 2026: no results.
- Opinion full-text search for `"Joan Farr" "Alexandra Grant"`, Eighth Circuit, filed before May 26, 2026: no results.
- RECAP search for appellate docket `25-1525`, Eighth Circuit, filed before May 26, 2026: no results.
- RECAP party search for `Joan Farr`, filed before May 26, 2026: identified the underlying `Farr v. Grant` district docket among broader results.
- RECAP case-name search for `Farr v. Grant`, filed before May 26, 2026: identified Western District of Missouri docket 68910257, No. 4:24-cv-00439, as a § 1983 civil-rights action terminated December 16, 2024.
- Docket endpoint item 68910257: confirmed the district docket metadata, assigned-judge resource, and termination date.
- Docket-entry endpoint schema lookup: consulted to form a docket-limited request.
- Docket-entry endpoint requests for docket 68910257: three attempts, all HTTP 429 throttled; no entries used.
- RECAP search for district docket `4:24-cv-00439`, Western District of Missouri: one throttled attempt and one successful attempt. The successful result confirmed docket metadata and exposed three service-of-process entry descriptions; those entries did not affect the forecast.
- RECAP search for `"Farr v. Grant" dismiss`: HTTP 429 throttled; no result used.
- Opinion search for `"Joan E. Farr"`, filed before May 26, 2026: returned four older Supreme Court order records under the same name; they were not used because identity and substantive relevance were not established.
- A final unrestricted RECAP search for appellate docket `25-1525`: HTTP 429 throttled; no result used.

No web searches were used. No search sought this petition's disposition or post-disposition history.
