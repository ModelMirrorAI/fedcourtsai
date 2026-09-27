# Retrieval log

- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition counts, originating-court cuts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Read matching structured fields in `metrics/statpack.json`; pooled the elevated reached population over all displayed strictly prior Terms, 2017–2025, obtaining 521 weighted grants among 3,085 weighted resolved petitions. No individual case outcomes were retrieved.
- General web search: `site.supremecourt.gov Lawrence Chater GVR intervening developments 516 163`. Tool returned no usable results; nothing used.
- General web search: `Lawrence v Chater 516 U.S. 163 1996 GVR intervening developments`. Tool returned no usable results; nothing used.
- No CourtListener MCP lookup, `fedcourts query`, or `fedcourts open-events` call. No ranged-corpus transfer lines were emitted. No own-case outcome search was made.
- Local operational reads: task contract, artifact schemas, path and serialization helpers. `fedcourts paths --court scotus --docket 9026000139 --event evt-petition-disposition --role predictor` resolved the authorized paths. Its initial invocation failed because the default uv cache was read-only; retry using a temporary cache succeeded. These operations supplied no external case facts.

Provisioned factual inputs were the September 27 snapshot, context, event definition, document manifest, questions presented, petition's substantive pages 1–4, and respondent's complete response. The companion-case discussion was already present in those filings; no companion opinion was fetched.
