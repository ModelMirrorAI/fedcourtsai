# Retrieval beyond provisioned case inputs

- Read the committed `metrics/statpack.md`: modern cert, originating-circuit, paid-segment relist/CVSG, and prior-Term sal-v4 reached-band tables. Computed an approximate denominator-weighted baseline reached rate from the displayed 2017–2024 rows: 5.12025%, weighted n = 11,580. No live corpus query or corpus refresh was performed.
- Web search attempt: `site.supremecourt.gov Rule 10 considerations governing review certiorari`. The tool returned no usable search content.
- Web open attempt: the Supreme Court's `2023RulesoftheCourt.pdf` under its filing-and-rules directory. The tool returned no usable content. No rule text was retrieved or quoted.
- CourtListener MCP `search`: type `o`, citation `877 F.3d 200`, limit 3. Returned *Flynn v. United States Securities & Exchange Commission*, December 7, 2017, cluster 4449525, opinion 4226778, and one irrelevant citation-match result. The latter was disregarded.
- CourtListener MCP `search_document`: opinion 4226778, literal query `1201.111`, context 1,500 characters. Read the discussion of the omitted Rule 900(b) claim, the requirement of findings on material issues, and remand rather than harmless-error treatment.
- Local contract/schema reads and `uv run fedcourts paths --court scotus --docket 73358594 --event evt-petition-disposition --role predictor` resolved the cell contract and paths. The first paths attempt failed on the default cache location; retry with a writable temporary cache succeeded. These were not corpus lookups and emitted no ranged-read transfer line.

No `fedcourts query` or `open-events` call was made, so there are no corpus transfer lines to report. No search sought this petition's outcome or subsequent history. No other predictions, evaluator artifacts, or QP-labeling artifacts were consulted.
