# Retrieval log

Forward cell; retrieval unrestricted. Beyond the provisioned inputs (`record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/petition.txt`, `record/documents/questions-presented.txt`, `record/documents/documents.json`) and the committed `metrics/statpack.md` / `metrics/statpack.json`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   Returned eight recency-ranked resolved SCOTUS rows from September 2026 (denials, one dismissal, one withdrawal, one grant on an application-shaped docket). None resembled a pro se paid cert petition from a state court; the result did not inform the number.

## CourtListener MCP lookups

None.

## Web searches

None.
