# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9526000370 --event evt-brief-response-disposition --role predictor`
- `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 15`
  stderr: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
- `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 15`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
- Read the committed `metrics/statpack.md`, section "The interim docket (applications)".

## CourtListener MCP

- `search` type `o`, q "Jensen v. Thornell receiver", courts ca9 and azd, filed after 2026-01-01: 0 results.
- `search` type `d`, q "Jensen v. Thornell", court ca9, filed after 2026-01-01: 2 dockets (26-5060 id 73734346; 26-1746 id 73291278).
- `call_endpoint` docket-entries, docket 73734346, filed on or after 2026-08-01.
- `call_endpoint` docket-entries, docket 73291278, filed on or after 2026-07-01.

## Web

- Fetched the respondents' opposition PDF from the Supreme Court docket URL recorded in the snapshot's September 25 entry (supremecourt.gov, DocketPDF/26/26A370/425682/...Respondents Stay Opp Jensen v Thornell.pdf) and extracted its text locally with pypdf. Filed 2026-09-25, before the cutoff.

No search touched this application's disposition or any material postdating the snapshot.
