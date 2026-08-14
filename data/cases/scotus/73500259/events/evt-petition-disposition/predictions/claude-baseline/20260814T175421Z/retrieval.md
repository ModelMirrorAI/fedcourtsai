# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, event.yaml, context.json,
questions-presented.txt, petition.txt, brief-in-opposition.txt, documents.json)
and the committed `metrics/statpack.md`:

## Corpus (`fedcourts`, service backend)

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
  - Returned mostly interim applications rather than comparable cert petitions;
    one granted cert petition (scotus/73275187, No. 25-246, distribution_count 3).
    Not load-bearing for the numbers.

## CourtListener MCP

- `search(type=d, court=scotus, case_name="Motorola Mobility AU Optronics")` —
  0 results.
- `search(type=o, court=scotus, q="Motorola Mobility" "AU Optronics")` —
  confirmed cert denied in Motorola Mobility LLC v. AU Optronics Corp.,
  No. 14-1122, June 15, 2015 (135 S. Ct. 2837). Pre-decision context for the
  claimed split's history; predates this case entirely (no leakage surface).

No web searches. Forward mode; nothing outcome-revealing about this case was
sought or surfaced (the petition is pending, next conference 2026-09-28).
