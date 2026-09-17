# Retrieval log

Mode: `forward` (retrieval unrestricted). Three calls in total.

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  Returned eight recent SCOTUS rows, mostly substantive emergency applications
  and one pending petition; none is a comparable pro se employment petition and
  the result did not move the forecast.

## CourtListener MCP

- `get_endpoint_item` on `dockets` id 73318133 (fields: id, case_name,
  docket_number, date_filed, date_terminated, date_modified, court_id,
  appeal_from_str). Result: No. 25-1270, filed 2026-05-08, `date_terminated`
  null, last modified 2026-06-24. Used to confirm the docket has not moved
  past the provisioned snapshot.
- `search` type `o`, query "Veto v. Boeing", court `ca9`, 5 results. Returned
  unrelated Ninth Circuit opinions; the unpublished memorandum in No. 24-7060
  was not surfaced. Not used.

## Committed base rates

- `metrics/statpack.md`: "Segment base rate by salience band (sal-v4)"
  (baseline band, OT2017 through OT2024 bracketed `reached` figures pooled),
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", and "Modern cert petitions by
  originating circuit" (ca9 row).

No web searches.
