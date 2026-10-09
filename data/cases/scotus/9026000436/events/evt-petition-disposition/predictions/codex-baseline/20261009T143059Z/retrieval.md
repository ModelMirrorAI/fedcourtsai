# Retrieval record

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas.
- Ran `uv run fedcourts paths --court scotus --docket 9026000436 --event evt-petition-disposition --role predictor`. The first invocation failed on a read-only cache; the retry with a temporary writable cache succeeded. This resolves paths and does not retrieve case outcomes.
- Read the provisioned event, context, October 9 snapshot, document manifest, questions presented, and selected petition passages including Appendix A's pre-cert appellate order.
- Consulted `metrics/statpack.md`: modern-cert disposition and originating-circuit context; paid-segment relist and CVSG cuts; and the `sal-v4` reached-band table. Consulted `metrics/statpack.json` for exact prior-Term baseline-band counts. The pooled 2017-2025 result is 642 / 12,871 = 0.04987957423665605. No current-Term rate is used as the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` to establish committed artifact vintage: `3f3ca14f4`, October 8, 2026 at 21:56:24 UTC. This does not establish corpus pull freshness.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus transfer lines were produced.

## External retrieval, confined to general precedent

1. Web search: `site.supremecourt.gov opinions 2023 Loper Bright statutory stare decisis special justification Chevron 22-451`. No usable response content returned.
2. Web open of the Supreme Court's Loper Bright slip-opinion PDF, path `/opinions/23pdf/22-451_7m58.pdf`. No usable response content returned.
3. CourtListener MCP `search`: type `o`, citation `603 U.S. 369`, two results, requesting case name, date, citations, opinions, and path. Returned Loper Bright, decided June 28, 2024, with opinion IDs 11066629 and 10452863 among the metadata. No target-petition query was made.
4. CourtListener MCP `search_document`: opinion 11066629, literal `special justification`, context 800. No literal match.
5. CourtListener MCP `search_document`: opinion 10452863, literal `statutory stare decisis`, context 900. Returned the majority's passage preserving prior statutory holdings against overruling based only on their reliance on Chevron. This corroborates the petition's own discussion at printed page 9.

No external search sought Radiall's disposition, subsequent history, or current docket. No outcome-revealing material about the target event was encountered.
