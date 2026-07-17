# Retrieval log — scotus/73266074 evt-petition-disposition (claude-baseline, 20260717T180352Z)

Beyond the provisioned inputs (snapshot 2026-07-17, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `documents.json`, `record/context.json`)
and the committed `metrics/statpack.md` / `metrics/statpack.json`:

## Corpus lookups (`fedcourts query`, service-free ranged backend)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   — stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3`
   (re-run with full field inspection of the top row)
   — stderr: `ranged corpus reads: 145 GET(s), 37879808 byte(s)`

Used to see the docket shape of recently granted Term-2025 petitions
(e.g. Monsanto v. Salas, 24-1097: 4 conference distributions before grant),
against this case's single distribution interrupted by a call for a response.

## CourtListener MCP lookups

1. `search` (type=o, q="Hastings College Conservation Committee") — confirmed the
   two published California Court of Appeal opinions below (A166898, 2023-06-05;
   A170255, 2025-10-15). Forward-mode cell; the petition is pending (BIO due
   2026-08-21) so no disposition exists to leak, and none surfaced.

## Web searches

None.
