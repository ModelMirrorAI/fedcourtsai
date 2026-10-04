# Retrieval record

No lookup sought this case's disposition, subsequent history, later docket, or decision coverage. No other predictor output, realized outcome, or labeling artifact was read.

## Local inputs and baseline

- Read the cell contract, relevant JSON schemas, event definition, provisioned context, snapshot, document manifest, questions presented, and selected substantive portions of both merits briefs.
- Read the merits section of `metrics/statpack.md` and the merits counts in `metrics/statpack.json`. A local calculation restricted rows to `2015 <= term < 2025` and returned 539 granted, 516 parsed, 360 disturbed, and 56 excluded; disturbed rate 0.6976744186046512. No live corpus query or corpus hydration was performed, so no ranged-corpus transfer line was produced.
- Ran `uv run fedcourts paths --court scotus --docket 73279026 --event evt-brief-judgment --role predictor`. The initial attempt failed on a read-only default cache. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`. The command withheld the evaluator-only outcome path, and no outcome file was opened.

## Browser attempts

The browser returned no usable result content for each of these calls; none supplied evidence:

1. Search batch: `site.supremecourt.gov opinions 2021 Fulton Philadelphia 19-123`; `site.supremecourt.gov opinions Carson Makin 20-1087`; `site.supremecourt.gov about biographies current members Court`.
2. Open of the official Fulton slip-opinion PDF, Court website path `/opinions/20pdf/19-123_g3bi.pdf`.
3. Search: `site.supremecourt.gov "20–1087" "Carson"`.

## CourtListener MCP

1. `search(type="o", case_name="Fulton v. City of Philadelphia", filed_before="2021-06-18", court="scotus", num_results=2)`: no matches.
2. `search(type="o", citation="593 U.S. 522", court="scotus", num_results=2)`: returned Fulton v. Philadelphia, decided June 17, 2021, cluster 4892570, opinion 4696349. Also returned an irrelevant 2017 Ascira Partners entry, which was not used.
3. `search_document(opinion_id=4696349, query="exception", snippet_size=450)`: read excerpts concerning individualized exemptions, the Commissioner's discretion, and the specific justification for denying an accommodation. Used the majority-opinion excerpts, not later citing decisions or the separate opinions, for the doctrinal comparison.

## Official roster check

Fetched the Supreme Court's official Current Members biographies page, host `www.supremecourt.gov`, path `/about/biographies.aspx`, with `curl --max-time 20 -fsSL`; stripped HTML and extracted the nine sitting Justices' names. The returned names matched the nine Justices in the vote forecast. This was a roster-only lookup, not a search about the predicted litigation.
