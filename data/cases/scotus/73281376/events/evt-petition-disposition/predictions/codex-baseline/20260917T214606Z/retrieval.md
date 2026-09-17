# Retrieval record

- Read the committed metrics/statpack.md modern-cert, relist, CVSG, circuit, and sal-v4 segment sections, and the corresponding prior-Term prefix fields in metrics/statpack.json. Pooled the elevated reached rates for Terms 2017–2024. Checked the pack's last relevant git commit date; did not query or pull the live corpus.
- Ran `uv run fedcourts paths --court scotus --docket 73281376 --event evt-petition-disposition --role predictor`. The default cache location was read-only; rerunning with a temporary writable cache succeeded. This resolves paths, not historical priors. No `fedcourts query` or `open-events` calls were made and no ranged-corpus transfer lines were emitted.
- Web search queries: `site.law.cornell.edu/supremecourt/text/485/112 delegating policymaking authority` and `site.law.cornell.edu/rules/supct/rule_10`. Both were issued in one search call; no usable results were returned. A subsequent open of the Cornell Praprotnik opinion page likewise returned no usable content. Neither attempt supplied evidence or any information about this petition.
- CourtListener MCP `search(type="o", citation="80 F.4th 704", num_results=1)` returned Robinson v. Midland County, Texas, decided September 14, 2023; cluster 9426308, opinion 9839933.
- CourtListener MCP `search_document(opinion_id=9839933, query="policymak", snippet_size=600)` returned three excerpts. Subsequent searches of that same opinion for `decline` and `reach`, with snippet_size 500, returned no matches.
- CourtListener MCP `read_document(opinion_id=9839933, chunk_index=2, chunk_size=8000)` supplied footnote 4 and surrounding discussion. Used that footnote to test the parties' competing descriptions of the alleged Fifth Circuit split. It leaves the nondelegable-duty theory undecided because the pleaded claim fails even under that theory.

No live docket lookup, current-case search, outcome file, other predictor's output, or labeling-measurement artifact was consulted.
