# Retrieval log

- Read the committed metrics/statpack.md modern-cert, circuit, relist, CVSG, and sal-v4 band tables. Read metrics/statpack.json to pool the baseline band's prefix_est_grant_rate with prefix_weighted_resolved over Terms 2017–2024: 593 / 11,580. Checked the statpack's last modifying commit timestamp with git log. No live corpus query or open-events lookup was made; no ranged-corpus transfer line was emitted.
- CourtListener MCP search: type=o, citation="252 F.3d 862", num_results=1. Returned Christian v. Wal-Mart Stores, Inc., Sixth Circuit, June 6, 2001, opinion 773564.
- CourtListener MCP search_document: opinion_id=773564, query="markedly hostile", snippet_size=800. Read six returned excerpts about the commercial-establishment test and its application, including the shopper's forced departure. This was historical legal context, not retrieval of the target petition or its subsequent history.
- web.run search_query: "site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings misapplication properly stated rule law". The tool returned no usable result or source text.
- web.run open: official Supreme Court 2023 Rules PDF at host www.supremecourt.gov, path /filingandrules/2023RulesoftheCourt.pdf. The tool returned no usable result or source text. No external rule text was relied upon.
- Local contract/schema reads and the read-only paths command were operational checks, not case-outcome retrieval. The first uv invocation failed because its default cache was read-only; repeating with a temporary writable cache succeeded.

No target-case disposition, later docket state, prediction from another cell, or outcome-linked topic artifact was consulted.
