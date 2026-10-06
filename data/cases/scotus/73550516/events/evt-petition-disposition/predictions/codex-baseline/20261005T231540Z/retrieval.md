# Retrieval record

## Provisioned evidence

Read the event definition and the case-level `record/context.json`, `record/snapshots/2026-10-05.json`, and the document manifest, questions presented, and petition with its appended lower-court decisions. No opposition was provisioned. No realized-outcome file, another predictor's output, or topic-label artifact was read.

## Committed base-rate material

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid-segment relist and CVSG cuts, and the sal-v4 Term-by-band reached table.
- Read the corresponding structure and exact baseline risk-set fields in `metrics/statpack.json`. Pooled every displayed OT2017–OT2024 baseline reached row: 593 estimated grant-family outcomes / 11,580 weighted resolved petitions = 0.05120898100172712. Excluded OT2025 and OT2026 from the anchor.
- No `fedcourts query` or `fedcourts open-events` call was made. No ranged corpus-read transfer line was produced, and no live corpus freshness is claimed.

## Web attempts

1. One `web.run` search call with queries `site.supremecourt.gov opinions 2019 GE Energy Outokumpu 18-1048` and `site.ca9.uscourts.gov Setty Shrinivas Sugandhalaya 2021 18-35573`.
2. Direct historical-opinion open: `https://www.supremecourt.gov/opinions/19pdf/18-1048_8ok0.pdf`.
3. Direct historical-opinion open: `https://cdn.ca9.uscourts.gov/datastore/opinions/2021/07/07/18-35573.pdf`.

These calls returned no usable visible content or source identifiers. No factual proposition in the forecast relies on them. CourtListener MCP provided the successful verification below.

## CourtListener MCP

1. `search(type="o", q='caseName:("Setty" "Shrinivas")', court="ca9", filed_before="2022-01-01", num_results=5)`. Located the July 7, 2021 published opinion, 3 F.4th 1166, opinion ID 4701830, along with earlier 2021 versions/orders. Used the July opinion, not its superseded predecessor.
2. `read_document(opinion_id=4701830)`. Returned the July 2021 *Setty* majority and dissent; the tool display was truncated.
3. `search_document(opinion_id=4701830, query="federal substantive law", snippet_size=1300)`. Checked the majority's federal-law treatment and the disagreement over state contract law; did not treat the dissent's position as the holding.
4. `search(type="o", q='"GE Energy" "Outokumpu"', court="scotus", filed_before="2021-01-01", filed_after="2020-01-01", num_results=3)`. Located *GE Energy*, 590 U.S. 432, decided June 1, 2020, cluster 4757656, lead opinion 9889180. Other returned 2020 snippets were unrelated and not used.
5. `search_document(opinion_id=9889180, query="which body", snippet_size=1800)`. Verified section IV's express reservation of the governing-law question and its limited nonsignatory-enforcement holding.

No search concerned this petition's outcome or later history. The companion's current Supreme Court status was not retrieved. Historical precedent supplied legal context only.

## Contract and operational checks

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, flags, and tooling schemas. Ran `fedcourts paths` with the authoritative cell identifiers; the first attempt failed because the default cache was read-only, and the retry succeeded with a writable temporary cache. Inspected path and serialization helpers to keep output within the assigned cell. These were operational reads, not additional case evidence.

Validated the three JSON files with their Pydantic models, checked the five declared claims and matching disposition probability, confirmed the two prose references and absence of harness-owned fields, and canonically serialized all six outputs through repository helpers. `uv run fedcourts validate data` then passed: **32,956 artifacts valid; 44,630 references consistent**. The output-directory check found exactly the six contract files. No commit, push, or PR operation was performed.
