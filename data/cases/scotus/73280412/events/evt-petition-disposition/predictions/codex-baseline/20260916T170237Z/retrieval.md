# Retrieval log

## Local inputs and aggregate context

- Read the cell contract, prediction/tooling/flags schemas, provisioned event, context, September 16 snapshot, manifest, QPs, and petition excerpts. No other predictor output, outcome artifact, or QP-topic artifact was read.
- Ran `uv run fedcourts paths --court scotus --docket 73280412 --event evt-petition-disposition --role predictor`. The initial default-cache attempt failed; rerunning with a writable temporary uv cache succeeded. The resolver did not expose outcome content.
- Read `metrics/statpack.md`: modern discretionary-cert, paid relist/CVSG cuts, and sal-v4 segment table; a headings/Term-row scan also displayed aggregate interim and merits rows, which were not used as anchors. Read `metrics/statpack.json` structure and the high-band reached fields for 2017–2024. Local arithmetic gave 314 grants over 898 weighted resolved cases. These are committed-pack figures, not a refreshed remote-corpus observation.
- No `fedcourts query`, `open-events`, corpus hydration, or CourtListener MCP lookup was made. There is consequently no ranged-corpus transfer line to report.

## Official filed PDFs

Both URLs were taken directly from the provisioned snapshot; neither was discovered through an outcome search.

**R1 — State of Washington respondent brief, filed June 2, 2026, 26 PDF pages.**

`https://www.supremecourt.gov/DocketPDF/25/25-901/412472/20260602165555690_StateBOR.pdf`

Used printed pp. 1–2, 14–20 for the State's request for GVR, its account of intervening Callais, and its alternative mootness defense. These are the State's representations and arguments. No independent current-state lookup of the companion litigation followed.

**R2 — Garcia reply supporting certiorari, filed June 10, 2026, 18 PDF pages.**

`https://www.supremecourt.gov/DocketPDF/25/25-901/413041/20260610143309236_6.10.2026%20Garcia%20v.%20Hobbs%20Reply%20ISO%20Cert%20Petition.pdf`

Used printed pp. 1–2, 5–7, and the concluding argument to distinguish petitioner's continuing request for review from the respondent's remand request.

Access sequence: one `web.open` attempt for each URL returned no usable text. A `curl` request for R1 piped to `pdftotext` could not extract text because that executable was absent. After checking available PDF libraries, two in-memory `urllib.request`/`pypdf.PdfReader` fetches of R1 were made: an initial extraction whose displayed output was truncated, then PDF pages 7, 20–23 for targeted context. Two equivalent fetches of R2 followed: an initially truncated full extraction and then PDF pages 7–8 and 11–13. No downloaded filing was saved into the repository or copied into an output file.

No web search query was made. No current docket, petition disposition, or later history was requested. The filings' accounts of earlier cases and of the intervening April 29 decision predate the September 16 baseline and are legitimate forward context; they do not reveal the outcome of this petition.
