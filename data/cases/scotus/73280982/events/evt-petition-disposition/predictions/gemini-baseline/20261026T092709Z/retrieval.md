# Retrieval Log

## Corpus Lookups (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73280982 --event evt-petition-disposition --role predictor`
   - Verified case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Inspected recent 2020s SCOTUS granted petitions and their distribution counts / metadata as priors.

## CourtListener MCP & Web Search

- None (no CourtListener MCP calls or web searches were performed; relied on the provisioned snapshot, provisioned briefs in `data/cases/scotus/73280982/record/`, and committed base rates in `metrics/statpack.md`).
