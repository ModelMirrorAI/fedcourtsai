# Retrieval beyond provisioned inputs

- Read the committed `metrics/statpack.md` merits-docket section and computed the prior-grant-Term pool from its published counts: 360/516 disturbed, with 516/539 parsed coverage. No corpus query or open-events call was made; there is no ranged-corpus-read line to report.
- General web search via `web.run`: `site.supremecourt.gov opinions 22pdf Jones Hendrix 21-857 475 place manner sentence` and `site.uscode.house.gov 18 3632 d 4 C time credits prerelease custody shall transfer`. The tool returned no usable results.
- General web opens: `https://www.supremecourt.gov/opinions/22pdf/21-857_4357.pdf` (two attempts) and `https://uscode.house.gov/view.xhtml?req=title:18%20section:3632%20edition:prelim`. These returned no usable content and informed no factual conclusion.
- CourtListener MCP `search(type="o", citation="599 U.S. 465", num_results=2, fields=["id", "caseName", "dateFiled", "opinions", "citation"])`: identified Jones v. Hendrix, decided June 22, 2023, including opinion ID 10516269 and majority author metadata.
- CourtListener MCP `search_document(opinion_id=10516269, query="place or manner", snippet_size=1500)`: read the page-475 passage about detention challenges not attacking sentence validity and its custody/credit examples. This is a different case and general legal context, not this cell's outcome.
- CourtListener MCP `search(type="o", citation="411 U.S. 475", num_results=1, fields=["caseName", "dateFiled", "opinions"])`: returned an unrelated Cidale tax case. Discarded; no opinion body read and no inference drawn.

No search or lookup sought Maxwell's disposition, subsequent history, merits briefs, oral argument, or decision coverage. All case-specific evidence used was provisioned.
