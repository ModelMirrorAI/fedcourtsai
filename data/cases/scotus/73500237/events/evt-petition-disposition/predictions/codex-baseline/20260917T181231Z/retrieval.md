# Retrieval record

## Local inputs and aggregate context

- Read AGENTS.md, .github/prompts/predict.md, prediction and tooling schemas, the event definition, and provisioned context, snapshot, document manifest, questions presented, and selected petition passages including Appendix A. Did not open any outcome, other prediction, or labeling-measurement artifact.
- Read metrics/statpack.md: modern discretionary-cert, originating-circuit, paid-segment relist and CVSG, and sal-v4 per-Term band sections. Read metrics/statpack.json for the exact 2017-2024 baseline prefix rates and denominators; pooled 593 grant-family equivalents over 11,580 weighted resolved petitions. No corpus query or open-events command was used, so no ranged-read transfer line exists.
- Path resolution: `uv run fedcourts paths --court scotus --docket 73500237 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Retried successfully using a writable temporary cache and `--no-sync`. The resolver did not expose an outcome path.

## General web attempts

1. web.run search queries: `site.supremecourt.gov opinions 2025 A.J.T. Osseo heightened standard` and `site.ca5.uscourts.gov Strife Aldine 2025 23-20527 accommodation delay`. The second query's docket string was a search guess, not relied on; CourtListener subsequently identified the actual Strife appeal as 24-20269. Tool returned no usable payload, excerpts, or sources.
2. web.run open attempt: `https://www.supremecourt.gov/opinions/24pdf/24-249_a86c.pdf`. Tool returned no usable payload. No contents from this guessed path informed the prediction.

## CourtListener MCP

1. `search(type="o", case_name="Strife", q="Aldine", num_results=3, filed_before="2026-05-28")`: returned Strife v. AISD, 138 F.4th 237, May 16, 2025, cluster 10585779, opinion 11052367, appeal 24-20269. Used the pre-petition opinion, not its subsequent citation history.
2. `search_document(opinion_id=11052367, query="delay", snippet_size=1000)`: returned the delay-based failure-to-accommodate discussion and disposition. Used the passages distinguishing an ultimately provided accommodation from an alleged six-month period without accommodation and identifying qualification as undisputed.
3. `search(type="o", citation="605 U.S. 335", num_results=1)`: returned A.J.T. v. Osseo Area Schools, June 12, 2025, cluster 10776841, opinion 11243428.
4. `search_document(opinion_id=11243428, query="do not decide", snippet_size=850)`: retrieved the majority's refusal to reach the broader across-the-board liability question outside the question presented and unresolved below.

These were checks of earlier precedent only. No query sought Redding's Supreme Court disposition or subsequent history; no such material surfaced.
