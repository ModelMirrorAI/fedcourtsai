# Retrieval log

## Local inputs and base-rate material

- Read the supplied event definition, `record/context.json`, `record/snapshots/2026-09-25.json`, `record/documents/documents.json`, and `record/documents/application.txt` for scotus/9526000406. No other predictor output or outcome file was read.
- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas to establish the output contract.
- Read `metrics/statpack.md`, especially the interim-application section, and inspected the corresponding `interim.terms` entries in `metrics/statpack.json`. Computed the 2016–2025 pool as 31 grants / 296 substantive resolutions with `jq`.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `96ebdd342 2026-09-26T12:03:37Z`. This identifies the committed pack, not the source corpus's newest pull stamp.
- Ran `uv run fedcourts paths --court scotus --docket 9526000406 --event evt-motion-disposition --role predictor`. The default cache was read-only; retrying with a writable temporary cache succeeded. This resolved paths only, not corpus facts.
- No `fedcourts query` or `fedcourts open-events` lookup was made, and no ranged-corpus transfer line was emitted.

## General web attempts

1. Search query: `site.supremecourt.gov Nken Holder 556 U.S. 418 stay likelihood success irreparable injury`. The tool returned no usable results or content.
2. Attempted to open `https://www.law.cornell.edu/supct/html/08-681.ZO.html` for the historical general stay standard. The tool returned no usable content. Neither attempt supplied evidence used in the forecast.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=1, fields=["caseName", "dateFiled", "citation", "id", "absolute_url", "snippet"])`: returned *Hollingsworth v. Perry*, January 13, 2010, and its opinion path. Some requested search fields were unavailable.
2. `get_endpoint_item(endpoint_id="clusters", item_id=1747, fields=["sub_opinions", "case_name", "date_filed"])`: identified the opinion records for that historical case.
3. `search_document(opinion_id=1747, query="reasonable probability", snippet_size=900)`: returned the general stay-pending-certiorari standard, including prospects of certiorari and reversal, irreparable harm, and balancing in close cases. Used only to verify the legal framework.

No lookup sought 26A406's disposition, later docket entries, subsequent history, or decision coverage. The earlier 2025 stays discussed in the rationale came from the provisioned application, not from retrieval of this target's outcome.
