# Retrieval log — claude-baseline / 20261008T143010Z

Mode: `forward` (retrieval unrestricted). Roughly 12 retrieval calls in total.

## Corpus tooling
- `uv run fedcourts paths --court scotus --docket 73279966 --event evt-petition-disposition --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --era 2020s --citation "596 U.S. 832"` — attempted lookup of United States v. Washington as a prior. Returned nothing; stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)` plus a `note:` that the citations filter is served off only ~200 scotus rows.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s` — recent granted scotus rows for shape only (top row: Missionaries of Saint John the Baptist v. Frederic, No. 25-1131, granted 2026-10-01 after 2 distributions). Nothing topically close. stderr: `ranged corpus reads: 45 GET(s), 11730944 byte(s)`.
- `metrics/statpack.md` (committed): modern cert disposition section, CVSG cut, relist cut, salience-band per-Term table (sal-v4), per-Term cert table.

## CourtListener MCP
- `search` (type=o, court=scotus, q="Hencely Fluor", filed_after 2025-10-01) — located Hencely v. Fluor Corp., No. 24-924, decided 2026-04-22, author Thomas; opinion id 11314033.
- `read_document` (opinion_id=10846666, chunk 0) — the cluster id, which turned out to be an unrelated W.D. Wash. fee order; discarded.
- `read_document` (opinion_id=11314033, chunk 0, 7000 chars) — Hencely syllabus and holding.

## Web fetches (this docket's own filings and a companion docket; all predate the snapshot)
- `https://www.supremecourt.gov/DocketPDF/25/25-828/424228/20260915105245693_25-828cvsg_GEO_Nwauzor_final.pdf` — SG's CVSG brief (WebFetch could not read the PDF; text extracted locally with pypdf in an ephemeral uv environment). Recommends grant.
- `https://www.supremecourt.gov/DocketPDF/25/25-828/425985/20260929160222360_StateSupplBr.pdf` — Washington's supplemental brief (same extraction).
- `https://www.supremecourt.gov/DocketPDF/25/25-828/425966/20260929142637616_2026.09.28%20Nwauzor%20Supplemental%20Brief.pdf` — individual respondents' supplemental brief (fetched with curl, same extraction).
- `https://www.supremecourt.gov/docket/docketfiles/html/public/26-71.html` — docket page for GEO Group v. Ferguson, No. 26-71: BIO filed 2026-09-16, distributed 2026-09-30 for the 10/16 conference, rescheduled 2026-10-06, redistributed 2026-10-07 for the 11/6 conference.

No search for this petition's own disposition was made and none surfaced.
