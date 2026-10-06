# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000455 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --caption Chaffins` — refused (no such flag; printed usage, no corpus read).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Returned five recent OT2026 grants (none comparable: two federal-petitioner
  immigration cases, a capital stay application, a religious-liberty case, and
  a family-law case with retained Supreme Court counsel). Used only to confirm
  the corpus service was live; no prior informed the number.
- `metrics/statpack.md`: modern discretionary-cert by disposition, by
  originating circuit (ca8 row), relist-count and CVSG cuts, per-Term table,
  and the sal-v4 segment base rate by salience band (baseline column, Terms
  2017 through 2025).

## CourtListener MCP

- `search` type=o, q="Chaffins Sharp", court=ca8 — HTTP 429 (daily rate limit exceeded).
- `search` type=r, q="Chaffins", court=[ca8, ndd] — HTTP 429 (daily rate limit exceeded).

No CourtListener data reached this cell.

## Web

- WebSearch: `"Chaffins" "Sharp" Eighth Circuit 25-2049 North Dakota` —
  surfaced the Justia listing of the Eighth Circuit decision (affirmance of a
  pro se section 1983 dismissal, January 20, 2026). Nothing about the cert
  petition's disposition appeared.
- WebFetch of the petition PDF linked in the snapshot
  (`supremecourt.gov/DocketPDF/26/26-455/428497/...6384.pdf`); the fetcher
  could not read the scanned file, so I extracted its OCR text layer locally
  with pypdf (20 pages, questions presented, statement, and argument all
  readable).
- WebFetch `law.justia.com/cases/federal/appellate-courts/ca8/25-2049/...` — HTTP 403.
- WebFetch `ecf.ca8.uscourts.gov/opndir/26/01/252049U.pdf` — the Eighth
  Circuit's unpublished per curiam, extracted locally with pypdf (2 pages).
- WebFetch of an ndcourts.gov news page from the search results — described a
  different case (Poemoceah v. Morton County); not used.
