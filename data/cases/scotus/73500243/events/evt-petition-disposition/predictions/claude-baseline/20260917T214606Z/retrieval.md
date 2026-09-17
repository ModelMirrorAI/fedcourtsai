# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`,
`documents/petition.txt`, `documents/questions-presented.txt`,
`event.yaml`) and the committed `metrics/statpack.md`:

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned eight recent granted SCOTUS rows (election and stay applications,
  Second Amendment petitions); no qualified-immunity comparables. Not used in
  the number.

## CourtListener MCP

- `search` (type `o`, court `scotus`, q `"fabricated evidence" "qualified immunity" "due process"`,
  filed after 2017-01-01, newest first, 10 results): **0 results**. Not retried.

## Web fetches (forward mode; this case's own later filings, both predating the snapshot)

- https://www.supremecourt.gov/DocketPDF/25/25-1341/422609/20260831180409169_25-1341%20Brief%20in%20Opposition.pdf
  (brief in opposition, filed August 31, 2026). The fetch tool could not read
  the PDF's text layer, so I extracted it locally with pypdf from the saved
  binary and read the full brief.
- https://www.supremecourt.gov/DocketPDF/25/25-1341/423837/20260910162001537_25-1341%20Reply%20Brief.pdf
  (reply brief, filed September 10, 2026). Same extraction path; read in full.

No search for this case's disposition was made; the docket's last entry is
the October 9, 2026 distribution and the petition is pending.
