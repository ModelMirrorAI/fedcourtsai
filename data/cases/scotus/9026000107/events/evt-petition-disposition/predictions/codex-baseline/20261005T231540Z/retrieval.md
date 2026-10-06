# Retrieval record

## Provisioned inputs

Read the case-level October 5, 2026 snapshot and context, the event definition, document manifest, questions presented, petition, and opposition. No outcome file, other predictor output, evaluator material, or labeling-measurement artifact was read.

## Committed calibration material

- Read `metrics/statpack.md`: modern-cert disposition, originating-circuit, paid-segment relist/CVSG, and sal-v4 per-Term reached-band tables. Material from other table sections appeared in adjacent command output but was not used as a cert anchor.
- Read selected fields from `metrics/statpack.json`; pooled the baseline reached rate over all displayed prior Terms, 2017–2025, using `prefix_est_grant_rate * prefix_weighted_resolved` over the sum of `prefix_weighted_resolved`: 638 / 12,720.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json`: `808f812e9 2026-09-28T12:02:50Z`. This dates the committed artifact, not the latest underlying corpus pull.
- No `fedcourts query` or `fedcourts open-events` lookup was made, so there is no ranged-corpus transfer line to report.

## External retrieval

All external attempts concerned general prior law or procedure, not this petition's outcome or subsequent history.

1. Web search query: `site.supremecourt.gov opinions 2020 Pakdel 20-1212 finality`.
2. Web search query, in the same call: `site.supremecourt.gov rules Rule 15 brief opposition 14 days distribution`.
3. Web open attempted: `https://www.supremecourt.gov/opinions/20pdf/20-1212_3204.pdf`.

Those web calls returned no usable visible content. I do not claim to have verified a scheduling rule through them and did not rely on a precise waiting-period rule.

4. CourtListener MCP `search(type="o", citation="594 U.S. 474", court="scotus", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Located *Pakdel v. City and County of San Francisco*, decided June 28, 2021, opinion ID 4699044. An unrelated citation-search result for *Pruessner v. Benton* also appeared and was not used.
5. CourtListener MCP `read_document(opinion_id=4699044)`. Read the prior Supreme Court opinion; the full tool response was display-truncated.
6. CourtListener MCP `read_document(opinion_id=4699044, chunk_index=[1,2], chunk_size=6500)`. Revisited the finality/exhaustion analysis and disposition to supplement the full read. The relevant authority is 594 U.S. 474, 478–80 (2021).

No search for Walls, No. 26-107, the linked extension docket, the related pending petition, or the present case's lower-court docket was made. No current-case outcome-revealing material surfaced.

## Contract and tooling

Read the repository instructions, prediction prompt, prediction/tooling/flags schemas, and path/serialization helpers. `uv run fedcourts paths --court scotus --docket 9026000107 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only; repeating it with a temporary writable cache succeeded. Local arithmetic and schema checks are not corpus retrieval. Validation is performed after writing the cell artifacts.
