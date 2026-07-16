# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” and “SCOTUS cert petitions by Term.”
- Consulted `metrics/statpack.json` for the 2025-Term paid-petition estimate (5.3649956%).

## Corpus lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '602 U.S. 1' --limit 8 --corpus-backend ranged`
- Result: failed before any rows or ranged-read statistics were produced because the runner could not resolve the corpus S3 endpoint (`EndpointConnectionError`). No corpus prior informed the prediction.

## CourtListener MCP

- Opinion search for `"Louisiana v. Callais"`, Supreme Court, filed after January 1, 2026. Located the April 29, 2026 opinion, docket 24-109.
- Opinion search for `"Bost v. Illinois State Board of Elections"`, Supreme Court, filed after January 1, 2026. Returned no results.
- Opinion search by Supreme Court docket 24-109. Identified the revised *Callais* combined opinion as CourtListener opinion 11320154.
- Opinion search within docket 24-109 for `"predominant consideration" "current conditions"`.
- Retrieved the `html_with_citations` field for CourtListener opinion 11320154 and consulted the syllabus's statement of the holding and updated *Gingles* framework.

No general web search was used.
