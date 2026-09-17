# Retrieval record

- Read the provisioned event, context, September 15, 2026 snapshot, questions presented, document manifest, petition main argument, and opposition passages addressing the question, claimed splits, and vehicle. No disposition or evaluator artifact was read.
- Read `metrics/statpack.md`: modern discretionary-cert, originating-court, paid-segment relist/CVSG, and sal-v4 reached-band context. Inspected `metrics/statpack.json` and pooled baseline reached-band rows for Terms 2017–2024 using `jq`: 593 / 11,580 = 0.05120898100172712. No corpus `query` or `open-events` call was made; there is no ranged-corpus transfer line to report.
- Web search attempt, queries: `site.law.cornell.edu/uscode/text/11/561 subsection d chapter 15` and `site.supremecourt.gov Rule 10 considerations governing review certiorari`. The tool returned no usable results or text; no external factual material was obtained.
- Web open attempt: `https://www.law.cornell.edu/uscode/text/11/561`. The tool returned no usable page content. This was a general statutory check, not a lookup of this petition's outcome.
- CourtListener MCP `search(type="o", citation="601 F.3d 319", num_results=1)` sought the preexisting Condor opinion. The tool returned HTTP 429, with no opinion or result. Did not retry through REST or seek credentials.
- Ran the required predictor-role path resolver. Its initial invocation failed because the default uv cache was read-only; rerunning with a temporary writable cache succeeded. Path resolution supplied no case history.

No retrieved material revealed this event's outcome. External research attempts did not change the information set; the substantive analysis rests on provisioned materials and the committed statistical pack.
