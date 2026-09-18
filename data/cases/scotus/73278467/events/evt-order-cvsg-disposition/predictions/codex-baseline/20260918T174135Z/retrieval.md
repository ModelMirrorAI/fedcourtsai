# Retrieval record

## Provisioned inputs

Read the event definition, case-level July 1, 2026 snapshot, context, document manifest, questions presented, and relevant portions of the petition and opposition. No present-docket or outcome lookup was made for this case. No other cell's outputs or labeling-measurement artifacts were read.

## Local reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-tooling and agent-flags schemas.
- Read `metrics/statpack.md`: modern-cert disposition and circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Read the corresponding `metrics/statpack.json` high-band reached fields for Terms 2017–2024 and computed 314/898 with `jq`.
- Ran `git log -1 --format='%cI %h' -- metrics/statpack.md` to identify the committed artifact's vintage: September 14, 2026, 11:02 UTC. No live corpus freshness was inferred from this date.
- Ran `uv run fedcourts paths --court scotus --docket 73278467 --event evt-order-cvsg-disposition --role predictor`. The first attempt failed on the default cache's read-only location; retry with a writable temporary cache succeeded. This is a path resolver, not a corpus query.
- Consulted the local path and serialization helpers to write the cell consistently with repository conventions.
- No `fedcourts query` or `open-events` call was made; there are no ranged-corpus transfer lines to report.

## Web attempts

One `web.run` search call contained these two general-precedent queries:

1. `site.supremecourt.gov opinions 2004 Johnson California 543 499 Turner strict scrutiny prison racial classifications`
2. `site.supremecourt.gov opinions 24pdf Skrmetti 23-477 2025`

A second call attempted to open `https://www.supremecourt.gov/opinions/24pdf/23-477_2cp3.pdf`. Both calls returned no usable source content or results. They did not supply facts used in the prediction and surfaced no case outcome.

## CourtListener MCP

1. `search(type="o", citation="145 S. Ct. 1816", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: returned United States v. Skrmetti, decided June 18, 2025; cluster 10610020; parallel citation 605 U.S. 495.
2. `get_endpoint_item(endpoint_id="clusters", item_id=10610020, fields=["case_name", "date_filed", "sub_opinions"])`: identified opinion 11076608.
3. `search_document(opinion_id=11076608, query="medical use", snippet_size=500)`: returned six excerpts, including the majority's age/medical-use classification analysis and explanation that the case did not decide suspect-class status. This narrow check verified the scope of preexisting authority discussed in the provisioned briefs. The full opinion was not downloaded or read.

These calls concerned a different, previously decided precedent, not this petition's disposition or subsequent history. No direct CourtListener REST calls were made.
