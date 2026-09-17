# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73344703 --event evt-petition-disposition --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  — stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`. Returned
  recent granted rows (applications and high-profile petitions), none
  comparable to this petition's profile; not used for the number.
- `uv run fedcourts query --court scotus --era 2020s`
  — stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Same
  character; not used for the number.
- Base rates: the committed `metrics/statpack.md` (sections "Modern
  discretionary-cert petitions by disposition", "Cert petitions by relist
  count", "by CVSG status", "by salience band", "SCOTUS cert petitions by
  Term", and "Segment base rate by salience band (sal-v4)").

## CourtListener MCP (forward mode)

- `get_endpoint_item` dockets/73344703 (fields id, case_name, docket_number,
  date_filed, date_terminated, date_last_filing, date_modified) — confirmed the
  docket is open (`date_terminated` null, last modified 2026-07-01), i.e. not
  mis-provisioned. Nothing outcome-revealing surfaced.
- `call_endpoint` docket-entries for docket 73344703 — returned 0 entries, so
  the mirror could not confirm or refute the absence of a waiver/BIO entry.

## Web

No web searches.
