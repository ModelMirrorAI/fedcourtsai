# Retrieval record

## Provisioned baseline

Read the cell's event definition, `record/context.json`, snapshot
`record/snapshots/2026-09-17.json`, document manifest, QP, and selected substantive
portions of `petition.txt` and `brief-in-opposition.txt`. No outcome or other
prediction was consulted.

## Committed statistical context

- Read `metrics/statpack.md`: modern-cert disposition and originating-court
  sections, paid-segment relist/CVSG cuts, and sal-v4 reached-band Term table.
- Read `metrics/statpack.json` for exact Term 2017-2024 high-band reached
  denominators and rates; computed 314/898 with local Python.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` solely for the
  committed statistical artifact's vintage: 55121cdb8, 2026-09-14T11:02:00Z.

## Official predecision filings beyond the provisioned text

Both URLs were taken directly from the provisioned snapshot, not discovered
through a case-outcome search.

1. United States amicus brief, filed August 31, 2026:
   `https://www.supremecourt.gov/DocketPDF/25/25-590/422539/20260831142837907_25-590_Aldridge_Final.pdf`
   - Two `web.run` direct-open attempts returned no usable content.
   - A shell `curl`/`pdftotext` attempt failed because `pdftotext` was absent;
     it yielded no substantive text.
   - Two subsequent `uv run python` calls fetched the same exact PDF using
     `httpx` and extracted selected pages in memory with the installed `pypdf`.
     HTTP 200; 333,041 bytes; 28 pages. Consulted the question and contents,
     introduction, discussion, vehicle/split analysis, and conclusion, including
     printed pp. 1-2, 8, 14-18, and 22.
   - The government recommends denial while recognizing the surcharge conflict
     and disputing the Sixth Circuit's categorical reasoning. This was a
     material downward adjustment. It is not the Court's outcome.
2. Petitioners' supplemental reply, dated/submitted September 16, 2026:
   `https://www.supremecourt.gov/DocketPDF/25/25-590/424443/20260916105340066_Aldridge%20Supplemental%20Reply_Final.pdf`
   - Two direct `httpx`/`pypdf` in-memory reads, the second targeted to printed
     pp. 3-5 after the first display was truncated. HTTP 200; 213,224 bytes;
     17 pages. Consulted the introduction, response to the vehicle objection,
     statutory-exemption argument, and conclusion, especially pp. 1-5 and 10-12.
   - Petitioners argue that the broad remedial holding is reviewable while
     fiduciary status and ultimate liability can remain for remand. This
     supports a non-negligible grant probability despite government opposition.

No web search, CourtListener MCP lookup, or `fedcourts query`/`open-events`
lookup was made. Consequently there is no ranged-corpus-transfer line to report.
No direct CourtListener REST request or credential access was attempted.
No retrieved material disclosed this petition's disposition.

## Local contract tooling

Ran `uv run fedcourts paths --court scotus --docket 73279035 --event
evt-petition-disposition --role predictor`. The first invocation failed on a
read-only default uv cache; retrying with a temporary cache succeeded. This
resolved paths only, without reading the evaluator-only outcome. Read the
prediction, flags, and tooling schemas for output compliance.
