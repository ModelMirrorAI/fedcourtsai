# Retrieval record

## Committed context beyond the provisioned record

- Read the merits-docket section of `metrics/statpack.md` and the corresponding `merits.terms` counts in `metrics/statpack.json`. Computed the 2015–2024 grant-Term window with `jq`; available rows were 2017–2024, totaling 360 disturbed / 516 parsed, with 539 qualifying grants and 56 separately excluded cert-order dispositions. No corpus query or open-events call was made, so there is no ranged-corpus transfer line to report. This is the committed pack, not an independently refreshed corpus read.
- Read the task instructions and the prediction, flags, and tooling JSON schemas. Ran the path resolver for this event. Its initial invocation failed because the default uv cache location was read-only; retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No evaluator-only file was opened.

## External legal context

1. Web searches: `site.supremecourt.gov opinions 18pdf Kisor Wilkie 18-15` and `site.loc.gov "Stinson v. United States" "508" "36"`. The tool returned no usable results or text. An attempted open of the official Supreme Court Kisor PDF, filename `18-15_9p6b.pdf`, likewise returned no usable text. These attempts contributed no substantive evidence.
2. CourtListener MCP `search(type="o", citation="508 U.S. 36", num_results=1)`, with case-name/date/opinion/citation fields. This broad citation filter returned an unrelated Morley v. Central Intelligence Agency result rather than Stinson. It was not used as legal evidence, and no follow-up read of Morley was made.
3. CourtListener MCP `search(type="o", q='caseName:"Stinson v. United States" AND citation:"508 U.S. 36"', court="scotus", filed_before="1994-01-01", num_results=1)`. Located Stinson v. United States, decided May 3, 1993, opinion 112854.
4. CourtListener MCP `read_document(opinion_id=112854)`. Consulted the original Stinson opinion for its authoritative-commentary rule and relationship to Williams and agency deference. The returned full text was long and partly display-truncated, so the next targeted lookup checked the relevant analogy.
5. CourtListener MCP `search_document(opinion_id=112854, query="not precise", snippet_size=800)`. Confirmed the qualification of the agency analogy and the distinction between commentary and delegated legislative rulemaking. The precedent supports the competing arguments; it does not supply the outcome of Beaird.

No external request sought this case's disposition, subsequent history, post-argument reporting, or any other predictor's output. No outcome-revealing material about this case was encountered.
