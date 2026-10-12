# Retrieval beyond provisioned inputs

- Read the merits section of committed `metrics/statpack.md` and the `merits` object of `metrics/statpack.json`. Computed the eligible 2017–2024 rows within the 2015–2024 window: 360/516 disturbed; 516/539 parsed coverage; 56 exclusions outside the granted denominator. No live corpus query was made, so there are no ranged-read transfer lines.
- Web search: `site.supremecourt.gov Timbs Indiana 17-1091 opinion excessive fines Bajakajian 2019`. No usable content returned.
- Web search: `United States v Bajakajian 524 U.S. 321 1998 supreme court opinion gross disproportional`. No usable content returned.
- Web open attempt: Justia's U.S. Reports 524/321 Bajakajian page. No usable content returned.
- Web open attempt: Supreme Court official biographies page, to check the bench. No usable content returned; this was not a source for any factual assertion.
- CourtListener MCP `search(type="o", citation="524 U.S. 321", num_results=1)`. Verified United States v. Bajakajian, decided June 22, 1998; cluster/opinion 118234, majority opinion 9433683. Used citation, opinion identity, and Thomas authorship metadata; no target-case retrieval.
- CourtListener MCP `search_document(opinion_id=118234, query="instrumentalit", snippet_size=900)`. Consulted the historical-forfeiture and instrumentality distinctions, including footnotes 8–9. The combined record contains majority and dissent; they are not treated as interchangeable holdings.
- CourtListener MCP `search_document(opinion_id=9433683, query="grossly disproportional", snippet_size=350)`. Checked the majority's formulation of the punitive-forfeiture standard and its application to the defendant's offense.

No search sought Jouppi's disposition or post-decision commentary. No outcome-revealing material was encountered. General-web attempts supplied no sources; successful supplemental legal retrieval was limited to an older precedent through the sanctioned CourtListener MCP tools.
