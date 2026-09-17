# Retrieval record

## Local inputs and aggregates

- Read the prompt, repository instructions, prediction and feedback schemas, and this cell's provisioned event, context, snapshot, petition, QP, and document manifest.
- Read the modern-cert, paid-segment relist, paid-segment CVSG, and per-Term salience sections of `metrics/statpack.md`; inspected matching aggregate fields in `metrics/statpack.json`. Pooled `sal-v4` reached-baseline values for Terms 2017–2024 only: weighted numerator 593, denominator 11,580, rate 0.05120898100172712.
- Ran `uv run fedcourts paths --court scotus --docket 73500217 --event evt-petition-disposition --role predictor`. The default cache was read-only; reran successfully with the cache redirected to `/tmp/uv-cache`.
- No `fedcourts query`, `open-events`, or individual corpus-case lookup was used; no ranged-transfer stderr line was produced. No realized-outcome file or other predictor output was read.

## Web attempts

1. `web.run` searches: `site.law.cornell.edu/uscode/text/21/337`; `site.law.cornell.edu/uscode/text/21/360bbb-3`; `site.supremecourt.gov Alexander Sandoval 532 275 private rights action`. No usable search results or source text were returned.
2. `web.run` open of the Cornell statutory page identified by `/uscode/text/21/337`. No usable source text was returned. No claim relies on successful web verification of either statute.

## CourtListener MCP

1. `search(type="o", case_name="Harkins v. United States", filed_before="2026-05-18", num_results=3)`: returned the January 23, 2025 Court of Federal Claims opinion, cluster 10320527, opinion 10787115; unrelated United States Steel cases also appeared and were not used.
2. `search_document(opinion_id=10787115, query="Tucker", snippet_size=2000)`: read the military-pay relief and Tucker Act jurisdiction discussion. This informed the assessment that the asserted conflict compares different remedial vehicles.
3. `search(type="o", citation="531 U.S. 341", num_results=1)`: returned an unrelated Virgin Islands case, rather than Buckman. Disregarded it and narrowed by case name and court.
4. `search(type="o", court="scotus", case_name="Buckman", filed_before="2002-01-01", num_results=1)`: located Buckman, decided February 21, 2001, including opinion 118406.
5. `search_document(opinion_id=118406, query="337", snippet_size=900)`: read two passages addressing federal enforcement, including footnote 4.
6. `search(type="o", court="scotus", case_name="Alexander v. Sandoval", filed_before="2002-01-01", num_results=1)`: located Sandoval, decided April 24, 2001, including majority opinion 9795078.
7. `search_document(opinion_id=9795078, query="private remedy", snippet_size=800)`: read the congressional-intent and private-remedy passages.

These lookups concerned general precedents, not this petition's disposition or later history. No outcome-revealing material about this event surfaced.
