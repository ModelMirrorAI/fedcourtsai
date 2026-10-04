# Retrieval log

## Local inputs and reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Ran `uv run fedcourts paths --court scotus --docket 73281056 --event evt-brief-judgment --role predictor`. The default cache location was read-only; rerunning with a writable temporary uv cache succeeded. No corpus retrieval occurred.
- Read this cell's `event.yaml`, case-level `record/context.json`, snapshot `2026-08-29.json`, document manifest, questions presented, petition excerpts, and selected substantive portions of the petitioner merits brief, Arizona's partial-support respondent merits brief, and retained cert-stage opposition.
- Consulted only the merits section and general metadata of committed `metrics/statpack.md` and the merits rows of `metrics/statpack.json`. Calculated the strictly-prior grant-Term pool with `jq`: 360 disturbed, 516 parsed, 539 granted, and 56 separately excluded. No `fedcourts query`, `open-events`, or live corpus read was used; therefore no ranged-transfer line was emitted.

## External calls

1. Web search, two queries: `site.supremecourt.gov opinions 2012 Arizona Inter Tribal Council 12-71 pdf` and `site.uscode.house.gov 52 20507 systematic remove ineligible voters 90 days`. The tool returned no usable content.
2. Web open of the Office of the Law Revision Counsel's preliminary-title page for 52 U.S.C. § 20507. The tool returned no usable content. No statutory text was obtained from this call; the parties' quoted provisions were used instead.
3. CourtListener MCP `search(type="o", citation="570 U.S. 1", num_results=2)`, query ID `7c5b1b84`. Returned an irrelevant Gilkerson v. Chasewood Bank result, disregarded, and Arizona v. Inter Tribal Council of Arizona, Inc., decided June 17, 2013, cluster 902770. No pagination was requested.
4. CourtListener MCP `search_document(opinion_id=9515775, query="state-developed", snippet_size=1800)`. Read the single primary-opinion excerpt around reporter pages 12–13 concerning state forms and the federal-form backstop. This was the only externally retrieved substantive authority used.

No lookup targeted this case's disposition, subsequent history, current docket, or decision coverage. No outcome-revealing material was encountered in the external results.
