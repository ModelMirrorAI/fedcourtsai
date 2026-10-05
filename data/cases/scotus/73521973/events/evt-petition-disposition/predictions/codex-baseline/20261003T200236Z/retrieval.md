# Retrieval record

- Local inputs: event.yaml; record/context.json; record/snapshots/2026-10-03.json; record/documents/documents.json; questions-presented.txt; substantive portions of petition.txt and brief-in-opposition.txt. No target-case outcome or subsequent-history material was requested.
- Local general context: metrics/statpack.md, including modern-cert, circuit, paid-segment relist/CVSG, capital, and sal-v4 prior-Term reached-band cuts. Inspected top-level keys of metrics/statpack.json; no additional rates were taken from it. Computed the approximate pooled 2017–2024 baseline reached rate locally from the rendered table: 592.925 estimated weighted grants / 11,580 weighted resolved petitions = 0.051203.
- CourtListener MCP search: type=o, citation="466 U.S. 668", num_results=1. Retrieved Strickland v. Washington metadata, not a target-case search.
- CourtListener MCP search_document: opinion_id=9429592, query="actual process", snippet_size=1700. Read the passage on reasonable probability, record evidence, and totality of the evidence at 466 U.S. 694–96. Used only as general doctrinal context.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings misapplication properly stated rule law`. The tool returned no usable result.
- Web open attempted for the official Court's 2023 rules PDF (`https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`). The tool returned no usable content; nothing from this attempt informed the forecast.
- Ran `fedcourts paths --court scotus --docket 73521973 --event evt-petition-disposition --role predictor`. Initial uv invocation failed because its default cache location was read-only; retry with a writable temporary cache succeeded. This was path resolution, not a corpus lookup.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were generated. No live target-case CourtListener or web search was made.
