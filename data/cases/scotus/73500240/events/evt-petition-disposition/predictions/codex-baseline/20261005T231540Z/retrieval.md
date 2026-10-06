# Retrieval record

## Provisioned inputs

- Read AGENTS.md, .github/prompts/predict.md, and the prediction/tooling/flags schemas.
- Read this cell's event.yaml, record/context.json, record/snapshots/2026-10-05.json, and record/documents/documents.json.
- Read questions-presented.txt; the petition's factual and procedural account, selected argument sections, and relevant appended panel/rehearing opinions; and the brief in opposition. Did not retrieve the videos or the actual amici brief.

## Additional local context

- Read metrics/statpack.md's modern-cert, circuit, paid relist/CVSG, and sal-v4 reached-band tables and metrics/statpack.json's corresponding data.
- Used jq to pool the baseline prefix_est_grant_rate weighted by prefix_weighted_resolved for Terms 2017–2024: 593 / 11,580 = 0.05120898100172712.
- Ran `git log -1 --format='%cs %h %s' -- metrics/statpack.json`: September 28, 2026, commit 808f812e9. This identifies the committed pack's revision, not the corpus's last pull.
- Ran `uv run fedcourts paths --court scotus --docket 73500240 --event evt-petition-disposition --role predictor`; the default cache was read-only. Repeated successfully with a temporary writable cache. The output identified the event path and explicitly withheld the evaluator-only outcome.
- Inspected serialization helpers solely for output formatting and used local date/schema/validation tooling. No corpus query or open-events call was made; no ranged-corpus transfer line was emitted.

## Web attempts

The web tool returned no usable content for these requests; no result text or factual assertion from them was used:

1. Search: `site.supremecourt.gov "Zorn v. Linton" "2026"`.
2. Search in the same call: `site.supremecourt.gov "Barnes v. Felix" "2025" opinion`.
3. Search: `Supreme Court Rule 10 erroneous factual findings misapplication`.
4. Open the official Supreme Court Zorn opinion at the opinions/25pdf/25-297_bqm2.pdf path.

No search targeted Granado's Supreme Court disposition, docket update, or subsequent history.

## CourtListener MCP

All calls concerned a general precedent predating the supplied snapshot, not this petition's outcome:

1. `search(type="o", case_name="Zorn v. Linton", court="scotus", num_results=3, fields=["id", "caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: one result, decided March 23, 2026; opinion 11280281, cluster path /opinion/10813527/zorn-v-linton/. The tool warned that the requested top-level id field was unavailable; the opinion id was present.
2. `search_document(opinion_id=11280281, query="We have not yet decided", snippet_size=700)`: no matches.
3. `read_document(opinion_id=11280281, chunk_index=[0,1], chunk_size=6500)`: per curiam facts and clearly-established-law discussion, including footnote 3's assumption without decision about controlling circuit precedent.
4. `search_document(opinion_id=11280281, query="petition for a writ", snippet_size=800)`: no matches.
5. `search_document(opinion_id=11280281, query="granted", snippet_size=900)`: one match concerning the district court's summary judgment; not the Supreme Court disposition.
6. `read_document(opinion_id=11280281, chunk_index=2, chunk_size=6500)`: the per curiam's concluding grant-and-reverse order and the opening of the dissent identifying the action as a summary reversal.

Zorn supplied general legal context only. No own-case outcome, evaluator artifact, other predictor output, or data/qp-topics material was read.
