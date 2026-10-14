# Retrieval record

## Provisioned material

Read the event definition; `record/context.json`; `record/snapshots/2026-10-14.json`; `record/documents/documents.json`; `questions-presented.txt`; and the petition body plus selected appendix passages in `petition.txt`. The companion grant and request for a hold came from petition pages 5–6, not an external search. No outcome or other predictor's output was read.

## Additional local context

- Read the prediction contract and output schemas.
- Read the committed `metrics/statpack.md` modern-cert, originating-circuit, paid relist/CVSG, and sal-v4 Term tables. Inspected top-level keys of `metrics/statpack.json` for metadata. Pooled the displayed reached rates for 2017–2025 locally; baseline approximately 0.04997 (weighted n=12,877), federal approximately 0.70463 (weighted n=203). Rates are approximate because the displayed percentages are rounded.
- Ran `uv run fedcourts paths --court scotus --docket 9026000145 --event evt-petition-disposition --role predictor`. The default cache path was read-only; retrying with a writable temporary uv cache succeeded. No corpus query or open-events lookup was made, so no ranged-corpus-transfer line was emitted.
- Read the path and serialization helper interfaces solely to produce the contracted files. Validation is a schema check, not substantive retrieval.

## External retrieval

1. Web search for `site.ca4.uscourts.gov "Obando-Segura" "2021" "fees"` and `site.supremecourt.gov "Rule 10" "Considerations Governing Review"`. The tool returned no visible results or source content; neither supplied evidence.
2. Attempted web open of the official Fourth Circuit PDF at `https://www.ca4.uscourts.gov/opinions/197736.P.pdf`. The tool returned no visible content; no inference was drawn from that attempt.
3. CourtListener MCP `search(type="o", citation="999 F.3d 190", num_results=1)`: returned *Jose Obando-Segura v. Merrick Garland*, Fourth Circuit, May 28, 2021, cluster 4887467, opinion 4691246.
4. CourtListener MCP `search_document(opinion_id=4691246, query="civil action", snippet_size=350)`: read the returned excerpts supporting the Fourth Circuit's exclusion of immigration habeas from the EAJA and its discussion of contrary authority. The tool returned the first 20 of 50 matches; this was a targeted excerpt review, not a full-opinion read.

No search sought this petition's disposition, later history, or the lead case's merits outcome. No outcome-revealing material was encountered.
