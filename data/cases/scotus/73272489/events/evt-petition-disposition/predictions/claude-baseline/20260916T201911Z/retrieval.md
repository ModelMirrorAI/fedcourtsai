# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Used for the shape of the recent denied population (several pro se petitioners in a similar posture).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   Used for contrast: every returned granted prior was represented by experienced counsel.

Also ran `uv run fedcourts paths --court scotus --docket 73272489 --event evt-petition-disposition --role predictor` to resolve the cell paths (no corpus read).

## CourtListener MCP lookups

1. `call_endpoint` `docket-entries` with `docket=73272489`, fields `date_filed, description, entry_number`, ordered by date filed. Result: 0 entries. No post-snapshot docket activity could be confirmed or refuted from this source; the provisioned snapshot stands as the record.

## Web searches

None.
