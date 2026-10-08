# Retrieval record

Beyond the provisioned case inputs, I consulted the committed metrics/statpack.md and metrics/statpack.json: modern-cert disposition and circuit cuts, paid-segment relist/CVSG cuts, and sal-v4 segment rates. I pooled the baseline reached rates over the displayed prior Terms 2017–2025, obtaining 638 / 12,720 = 0.0501572327. I checked the statpack's last commit date with git log. No live corpus query or open-events command was used, so there is no ranged-corpus transfer line.

External lookups, in order:

1. Web search: "Peter F Gaito Architecture 602 F.3d 57 substantial similarity ordinary observer dismissal Second Circuit opinion". The tool returned no usable results.
2. Web open: a Justia page for the Second Circuit's Gaito decision, under its ca2/09-2613 path. The tool returned no usable page content; no proposition relies on that attempted retrieval.
3. CourtListener MCP search: type=o, citation="602 F.3d 57", num_results=1. Returned Peter F. Gaito Architecture, LLC v. Simone Development Corp., decided April 7, 2010, opinion/cluster 1331.
4. CourtListener MCP search_document: opinion_id=1331, query="as a matter of law", snippet_size=1500. Read the decision's treatment of judicial resolution of substantial similarity and dismissal.
5. CourtListener MCP search_document: opinion_id=1331, query="dissect", snippet_size=1200. Read the discussion of unprotectable elements and overall concept and feel.

The precedent is cited conventionally in reasoning.md. No lookup targeted this petition's outcome, later docket, or decision coverage. No prior predictions, outcome files, or labeling artifacts were read. I also read the task/schema contracts and path/serialization helpers for output compliance; these supplied no case evidence.
