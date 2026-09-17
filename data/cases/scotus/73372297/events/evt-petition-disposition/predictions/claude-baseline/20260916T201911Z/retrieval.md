# Retrieval log

## Provisioned inputs read

- `data/cases/scotus/73372297/record/context.json`
- `data/cases/scotus/73372297/record/snapshots/2026-09-16.json`
- `data/cases/scotus/73372297/record/documents/documents.json`
- `data/cases/scotus/73372297/record/documents/questions-presented.txt`
- `data/cases/scotus/73372297/record/documents/petition.txt`
- `data/cases/scotus/73372297/events/evt-petition-disposition/event.yaml`
- `metrics/statpack.md` (modern discretionary-cert dispositions, originating
  circuit, relist count, CVSG status, salience band, per-Term table, and the
  sal-v4 segment base rate by salience band)

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   Returned five recent grants (four substantive applications and one cert
   grant), none resembling a pro se Vaccine Act petition. The surface filters
   on structured fields only, so the result did not inform the forecast.

## CourtListener MCP lookups

None.

## Web searches

None.
