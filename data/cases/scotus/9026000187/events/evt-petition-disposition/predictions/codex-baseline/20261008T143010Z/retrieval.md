# Retrieval record

## Local context beyond the provisioned case inputs

- Read the prediction contract, repository instructions, and prediction/tooling/flags schemas.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read `metrics/statpack.json` to pool the 2017–2025 baseline reached estimates: 638 / 12,720 = 0.05015723270440252. The table's entire displayed prior-Term window was used.
- Ran `uv run fedcourts paths --court scotus --docket 9026000187 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; repeating with a writable temporary cache succeeded. This resolves paths, not case outcomes.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were produced. No live corpus freshness claim is made.

## Web attempts

The following returned no usable text or search results and contributed no substantive evidence:

1. Search: `site.ca4.uscourts.gov Short Hartman 21-1396 Kingsley objective December 2023`.
2. Search: `site.ca10.uscourts.gov Strain Regalado 977 984 Kingsley 2020`.
3. Open: `https://www.ca4.uscourts.gov/opinions/211396.P.pdf`.
4. Open: `https://www.ca10.uscourts.gov/opinion/19-5071`, attempted twice. This unverified address yielded nothing; it is not a verified docket identification or source citation.

## CourtListener MCP

1. `search(type="o", citation="87 F.4th 593", num_results=2)`: returned Charles Short v. J. Hartman, December 8, 2023, Fourth Circuit, opinion ID 9908572.
2. `search_document(opinion_id=9908572, query="objective", snippet_size=550)`: consulted excerpts concerning extension of Kingsley and the competing circuit approaches; the response displayed only the first 20 matches, not the full opinion.
3. `search_document(opinion_id=9908572, query="negligence", snippet_size=600)`: consulted the distinction between objective recklessness and negligence, including opinion pages 27–29.
4. `search_document(opinion_id=4575076, query="Kingsley", snippet_size=400)`: followed the Strain opinion reference present in Short's citation markup; excerpts confirmed retention of a subjective component for medical deliberate indifference. The response displayed only the first 20 matches.

These were prior legal authorities, not retrieval of this petition's resolution. No target-case disposition or outcome-revealing material was encountered.
