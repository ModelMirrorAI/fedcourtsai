# Retrieval beyond the provisioned inputs

- Read the committed metrics/statpack.md: modern discretionary-cert disposition, originating-court, paid relist/CVSG, per-Term and sal-v4 band sections. Read metrics/statpack.json's Term records to calculate the exact 2017–2024 baseline reached pool: 593 / 11,580. No live corpus query or open-events call was made; no ranged-corpus transfer line was produced.
- Web search: site:supremecourt.gov opinions Turner Rogers 2011 10-10 pdf. No usable result content returned.
- Web open: official Supreme Court opinion endpoint with path /opinions/10pdf/10-10.pdf. No usable content returned.
- Web open: Library of Congress U.S. Reports PDF endpoint with path /storage-services/service/ll/usrep/usrep564/usrep564431/usrep564431.pdf. No usable content returned.
- CourtListener MCP search: type=o, citation=564 U.S. 431, num_results=1. Returned City of Concord v. N. New Eng. Tel. Operations LLC., dated November 30, 2015, rather than Turner. Disregarded; no pagination or document read.
- CourtListener MCP search: type=o, case_name=Turner v. Rogers, court=scotus, filed_before=2012-01-01, num_results=1. Returned June 20, 2011 Turner opinion, cluster 7345716, majority opinion 7263684.
- CourtListener MCP search_document: opinion_id=7263684, query=safeguards, snippet_size=1300. Read the majority's alternative procedural safeguards and limits of its counsel holding, particularly 564 U.S. 447–49.

The historical primary-source lookup concerns Turner, not the target petition. No search sought this case's own disposition, subsequent history, current docket, or commentary. All case-specific evidence used came from the provisioned record.

Local contract/schema reads and the fedcourts paths command were administrative rather than additional factual retrieval. The first paths command failed on the default cache location; it succeeded with the cache redirected to /tmp/uv-cache.
