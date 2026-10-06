# Retrieval log

## Provisioned baseline

Read the event definition, `record/context.json`, `record/snapshots/2026-10-05.json`, and the document manifest, extracted question, and petition with appendices. No outcome artifact, another predictor's output, or QP-labeling artifact was read.

## Additional local context

- Read the committed `metrics/statpack.md`: modern cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Inspected only the top-level keys of `metrics/statpack.json` for metadata. Pooled displayed baseline reached rates for Terms 2017–2025 with a local arithmetic script: weighted denominator 12,720, approximate rate 5.010888%.
- Read output schemas and the prompt contract. Ran `uv run fedcourts paths --court scotus --docket 9026000002 --event evt-petition-disposition --role predictor`; the initial invocation failed because the default uv cache was read-only, then succeeded using a temporary writable cache.
- No `fedcourts query` or `open-events` calls; no ranged corpus transfer lines were generated.

## Web attempts

1. Search query: `site.supremecourt.gov opinions 2019 GE Energy Outokumpu 18-1048 which body of law governs`. The tool returned no usable content.
2. Attempted to open the historical opinion at `https://www.supremecourt.gov/opinions/19pdf/18-1048_8mjp.pdf`. The tool returned no usable content. No legal conclusion rests on this attempted URL.

## CourtListener MCP

1. `search(type="o", citation="590 U.S. 432", num_results=1)`: returned the June 1, 2020 GE Energy opinion cluster 4757656, including lead opinion 9889180.
2. `search_document(opinion_id=9889180, query="which body", snippet_size=650)`: verified the express reservation of the applicable body of law and the limited nonsignatory-enforcement holding.
3. `search(type="o", citation="3 F.4th 1166", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])`: returned Setty, July 7, 2021, opinion 4701830.
4. `search_document(opinion_id=4701830, query="federal", snippet_size=550)`: read excerpts concerning federal substantive law, the federal-claims setting, the factual failure of estoppel, and the dissent's state-law position. The tool reported more matches than it displayed; I did not read the full opinion.

These were historical legal-context lookups only. I did not search this petition's current docket, disposition, subsequent history, or the disposition of the suggested lead litigation. No outcome-revealing material for this cell surfaced.
