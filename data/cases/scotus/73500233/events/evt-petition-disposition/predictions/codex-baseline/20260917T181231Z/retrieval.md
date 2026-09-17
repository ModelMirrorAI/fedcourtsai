# Retrieval log

No lookup sought this case's disposition or subsequent history.

## Local context

- Read `metrics/statpack.md`: modern discretionary-cert disposition totals, paid-segment relist/CVSG cuts, and sal-v4 per-Term band table. Pooled baseline reached rates only for displayed Terms 2017–2024. Inspected the top-level keys of `metrics/statpack.json` for available vintage metadata; no timestamp was exposed by that inspection.
- Read the task contract and prediction/tooling schemas. Ran `uv run fedcourts paths --court scotus --docket 73500233 --event evt-petition-disposition --role predictor`. The first attempt failed on a read-only default uv cache; retry with a cache under `/tmp` succeeded. This is path resolution, not a corpus query.
- No `fedcourts query` or `open-events` calls; no ranged corpus transfer lines were produced.

## Web attempts

- One `web.run` search batch: `site.supremecourt.gov opinions Villarreal Texas 2026 testimony`; `site.loc.gov "Dowling v. United States" "493"`; `site.supremecourt.gov "Rule 10" "Review on a writ"`. The tool returned no usable results or source text.
- One `web.run` open attempt for `https://www.law.cornell.edu/supremecourt/text/493/342`; the tool returned no usable text. No propositions were sourced from these empty web responses.

## CourtListener MCP

1. `search(type="o", citation="493 U.S. 342", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: returned an unrelated Sagan result. Disregarded it.
2. `search(type="o", q='caseName:"Dowling v. United States"', court="scotus", num_results=2, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: returned same-caption historical orders, not the intended majority. Did not use them as substantive authority.
3. Repeated the same-caption SCOTUS search with `filed_after="1990-01-01"`, `filed_before="1990-12-31"`, and `num_results=1`: located 493 U.S. 342 and majority opinion 9431876.
4. `read_document(opinion_id=9431876)`: retrieved the Dowling majority. Used its holding and analysis of acquitted-conduct other-acts testimony as historical legal context; the tool's long response was truncated in display, so I do not claim to have inspected every passage. This is a different case, predating the target petition by decades.
