# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-16.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --limit 6`
  stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  Returned six recent SCOTUS rows, five of them stay applications and one dismissed IFP petition; none was a useful prior for a paid Rule 52(a) petition, so the result did not move the forecast.

## CourtListener MCP

- `call_endpoint` on `dockets`, id 73364890, fields id/case_name/docket_number/court_id/date_filed/date_terminated/date_last_filing/date_modified.
  Result: docket 25-1294, filed 2026-05-19, `date_terminated: null`, last modified 2026-06-24 (the distribution). Confirms the cell is genuinely pending and that no filing post-dates the snapshot on CourtListener's copy.

## Web

None.
