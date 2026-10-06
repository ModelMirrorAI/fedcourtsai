# Retrieval record

## Provisioned material

Read this cell's event definition, context, October 5, 2026 snapshot, documents manifest, questions presented, and principal argument/vehicle sections of the petition and BIO. The filed reply's text was not retrieved. No other predictor's output, outcome record, or labeling-measurement artifact was read.

## Committed context and administrative commands

- Consulted `metrics/statpack.md` for the modern-cert, paid relist, CVSG, and sal-v4 reached-band cuts; inspected the relevant segments in `metrics/statpack.json`. Computed the prior-Term high-band pool as 314 grants / 898 weighted resolved petitions across 2017–2024. No individual corpus case was retrieved.
- `git log -1 --format='%h %cI' -- metrics/statpack.md` reported `808f812e9 2026-09-28T12:02:50Z`. This is the pack's commit vintage, not a corpus pull timestamp.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed because the service backend has no client-side connection. It returned no corpus vintage, case facts, or ranged-read transfer line. No `fedcourts query` or `open-events` call was made.
- Ran `uv run fedcourts paths --court scotus --docket 73281354 --event evt-order-cvsg-disposition --role predictor`; the first attempt encountered a read-only default uv cache. Retrying with a temporary cache succeeded. Consulted output schemas and path/serialization helpers for artifact construction, not case evidence.

## General-precedent retrieval

The following web requests returned no usable source content to this session and supplied no evidentiary input:

1. Search: `site.supremecourt.gov opinions Apple Pepper Illinois Brick direct purchasers 2019`.
2. Search: `Apple Inc v Pepper 17-204 supreme court opinion 2019`.
3. Open: the Supreme Court's official Apple opinion, resource `https://www.supremecourt.gov/opinions/18pdf/17-204_bq7d.pdf`.

CourtListener MCP then supplied the pertinent historical precedent:

1. `search(type="o", citation="587 U.S. 273", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: Apple, Inc. v. Pepper, decided May 13, 2019; returned opinion ID 4396211 and cluster path `/opinion/4618958/apple-inc-v-pepper/`.
2. `search_document(opinion_id=4396211, query="unrelated", snippet_size=1100)`: read the majority's discussion of separate injuries and liability unrelated to passed-on overcharges.
3. `search_document(opinion_id=4396211, query="bright-line rule", snippet_size=550)`: read the majority's categorical direct/indirect purchaser discussion and rejection of individualized exceptions.

These searches concerned a 2019 precedent, not this petition's outcome. No current docket lookup, subsequent-history search, or lookup of the related United Biologics petition was performed. The related petition enters the analysis only through the provisioned BIO.
