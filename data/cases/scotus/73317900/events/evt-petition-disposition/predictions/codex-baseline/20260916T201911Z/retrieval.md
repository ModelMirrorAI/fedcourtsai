# Retrieval log

- Read the committed metrics/statpack.md modern-cert, originating-circuit, paid-segment relist, CVSG, and sal-v4 band sections. Read top-level keys of metrics/statpack.json only. Computed the denominator-weighted 2017-2024 baseline reached rate from the displayed Markdown rows: approximately 0.05120250 over 11,580 weighted resolved petitions. No live corpus query or open-events call; no ranged-read transfer line was produced.
- Ran `uv run fedcourts paths --court scotus --docket 73317900 --event evt-petition-disposition --role predictor`; the default uv cache was read-only. The same lookup succeeded with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 73317900 --event evt-petition-disposition --role predictor`. This resolved paths only and did not retrieve an outcome.
- Web search: `site.supremecourt.gov opinions 2026 Jules Andre Balazs Properties 25-83`. The tool returned no usable results.
- Web open attempt: `https://www.supremecourt.gov/opinions/25pdf/25-83_3e04.pdf`. The tool returned no usable content; no proposition relies on this attempt.
- CourtListener MCP `search(type="o", case_name="Jules", court="scotus", num_results=3, order_by="dateFiled desc")`: returned Jules v. Andre Balazs Properties, No. 25-83, May 14, 2026, cluster 10858761, opinion 11326163, plus two unrelated older Jules cases. Those unrelated results did not inform this forecast.
- CourtListener MCP `read_document(opinion_id=11326163, chunk_index=[0,1,2], chunk_size=9000)`: consulted the syllabus and opening portions of the companion precedent; the returned display was partially truncated.
- CourtListener MCP `search_document(opinion_id=11326163, query="1782", snippet_size=750)`: zero literal matches. This is not a substantive ruling about Section 1782.
- CourtListener MCP `read_document(opinion_id=11326163, chunk_index=3, chunk_size=9000)`: read the circuit-split discussion and the Court's retained-jurisdiction analysis, including slip-opinion pages 6-8.

Jules is a separate case decided before the provisioned snapshot. No lookup sought this cell's own disposition or subsequent history. No material under data/qp-topics was read.
