# Retrieval record

## Provisioned inputs

Read the event definition, context, September 24, 2026 snapshot, document manifest, questions presented, and portions of the petition, opposition, and both merits briefs identified in `reasoning.md`. No case-outcome file, other predictor output, or labeling-measurement artifact was consulted.

## Committed context

- Read the merits section of `metrics/statpack.md` and the matching `merits.terms` entries in `metrics/statpack.json`; inspected the pack's headings, introductory coverage, and JSON metadata keys. Only the strictly prior grant-Term merits pool was used as the anchor, not the cert tables or mixed-court headline rates.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the checked-out artifact's commit vintage: `808f812e9 2026-09-28T12:02:50Z`.
- Used `jq` to select `2015 <= term < 2025` from `merits.terms` and sum `disturbed`, `parsed`, `granted`, and `cert_order_excluded`: 360, 516, 539, and 56 respectively.
- Consulted the prediction, tooling, and flags schemas and searched `docs/decision-model.md` for vote-name conventions. These are output-contract checks, not substantive case retrieval.

## Web attempts

The following calls produced no usable returned content or source references. None informed the forecast or surfaced the target case's outcome.

1. Search queries: `site.supremecourt.gov opinions Egbert Boule 2022 Carlson Bivens 21-147` and `site.supremecourt.gov opinions Goldey Fields 2025 Bivens Carlson`.
2. Search queries: `Egbert Boule supremecourt.gov pdf 21-147` and `Goldey Fields supremecourt.gov 2025 per curiam`.
3. Attempted to open the unverified candidate path `https://www.supremecourt.gov/opinions/24pdf/24-809_9o6b.pdf` for Goldey. No document was returned; this path is not relied on as a valid source.

## CourtListener MCP

1. `search(type="o", citation="596 U.S. 482", num_results=2)` returned Egbert v. Boule, decided June 8, 2022, combined opinion ID **6347905**. An unrelated Figueroa result was not pursued.
2. `search_document(opinion_id=6347905, query="ROBERTS", snippet_size=1000)` verified the Egbert voting alignment and separate writings.
3. `search(type="o", case_name="Goldey v. Fields", court="scotus", filed_before="2026-09-24", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])` located the June 30, 2025 opinion, 606 U.S. 942. Multiple publication versions appeared; the first was selected.
4. `read_document(opinion_id=11243402)` retrieved Goldey's published opinion, including its distinction between recognized Bivens contexts and an excessive-force extension, and its remedial and separation-of-powers reasoning.
5. `search_document(opinion_id=6347905, query="single question", snippet_size=1400)` retrieved Egbert passages on the relationship between new context, special factors, and congressional competence, together with competing separate-opinion views.

These requests concern historical precedents, not Nielsen v. Watanabe or its subsequent history. No live CourtListener docket lookup, direct REST request, or opinion-citation graph expansion was performed.

## Corpus commands and environment

No `fedcourts query` or `open-events` lookup was used; no ranged-corpus transfer line was produced. `fedcourts paths --court scotus --docket 73278422 --event evt-brief-judgment --role predictor` resolved the cell paths. Its first invocation failed because the default uv cache location was read-only; rerunning with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This was a local execution issue, not an upstream retrieval failure.
