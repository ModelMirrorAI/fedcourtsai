# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Result: eight recent granted SCOTUS rows (emergency applications and high-profile petitions such as Second Amendment and election matters). None comparable to an interlocutory state OWI prosecution; not used in the number.

## CourtListener MCP lookups

- `call_endpoint` `dockets`, `id=73309407`, fields id/case_name/docket_number/date_filed/date_terminated/date_modified/court_id.
  Result: docket 25-1263, filed 2026-05-07, `date_terminated` null, last modified 2026-06-24. Confirms the petition is pending (forward cell correctly provisioned). No outcome material.
- `call_endpoint` `docket-entries`, `docket=73309407`.
  Result: 0 entries (CourtListener carries no entry rows for this SCOTUS docket).

## Web searches

None.
