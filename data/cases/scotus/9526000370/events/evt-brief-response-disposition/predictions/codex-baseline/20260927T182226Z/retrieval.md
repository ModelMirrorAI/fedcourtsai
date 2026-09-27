# Retrieval log

- Read the committed `metrics/statpack.md` introductory metadata and "The interim docket (applications)" section. Used the 2016–2025 application-Term pool for a Term 2026 cell; no live corpus query or refresh was performed.
- Web search query: `site.supremecourt.gov opinions Nken Holder 556 418 stay irreparable injury 2009`. The tool returned no usable result or source text. No external legal proposition was taken from it.
- Web open: the September 25, 2026 respondents' stay-opposition PDF linked in the provisioned snapshot, `https://www.supremecourt.gov/DocketPDF/26/26A370/425682/20260925153133136_20260925%20Respondents%20Stay%20Opp%20Jensen%20v%20Thornell.pdf`. The tool returned no usable content. This was a specific pre-disposition filing request, not a docket or outcome search.
- No CourtListener MCP lookup, `fedcourts query`, or `open-events` call was made. There are no ranged-corpus-read transfer lines to report.
- Local contract/schema reads and `fedcourts paths --court scotus --docket 9526000370 --event evt-brief-response-disposition --role predictor` were administrative checks, not case retrieval. The first CLI attempt could not initialize the default read-only cache; retrying with a writable temporary cache succeeded.

No case outcome or subsequent history was sought or surfaced.
