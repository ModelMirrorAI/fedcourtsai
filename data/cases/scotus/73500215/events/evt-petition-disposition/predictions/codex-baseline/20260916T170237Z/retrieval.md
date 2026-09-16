# Retrieval record

## Provisioned material

Read event.yaml, record/context.json, record/snapshots/2026-09-15.json, and record/documents/documents.json, questions-presented.txt, and petition.txt. Read the petition's arguments and appended appellate memorandum and rehearing order. Read the prediction prompt, repository instructions, and the prediction/tooling/flags schemas. Did not read any outcome file, other predictor output, or labeling artifacts.

## Base-rate context

Read metrics/statpack.md: modern-cert dispositions, paid-segment terminal relist and CVSG cuts, and the sal-v4 segment table. Read metrics/statpack.json's Term/segment data and computed the prior-Term baseline reached-rate pool in memory: Terms 2017–2024, 593 weighted grants / 11,580 weighted resolved = 0.05120898100172712. No corpus query or open-events lookup was made, so there is no ranged-corpus-reads transfer line.

## Web and filed-document retrieval

1. Attempted web.open of the exact September 14 opposition PDF URL already named in the snapshot. The tool returned no usable content.
2. Attempted web.search_query with `site.supremecourt.gov "Zorn" "Linton" "2026"`. The tool returned no usable results. This was a search for an earlier precedent, not for this petition's outcome.
3. Used a shell HTTP HEAD request to the exact opposition URL, confirming an accessible PDF, then four in-memory HTTP GETs with httpx and pypdf to read page groups: PDF pages 1–6; 7–11; 12–19; and 15–16 again to recover display truncation. The PDF has 19 pages, including its cover and front matter. No PDF or extracted text was written outside this cell's output files. This is Supreme Court filed-document retrieval, not a CourtListener REST fallback.

Exact filed-document source:

```text
https://www.supremecourt.gov/DocketPDF/25/25-1314/424147/20260914154313299_Gomez%20v.%20Saccoccio%20BIO%2025-1314.pdf
```

The response is pre-decision advocacy submitted September 14, 2026, as shown in the provisioned snapshot. Its recommendation to deny is advocacy, not an actual disposition. No search for Gomez's disposition, subsequent history, or live docket was made.

## CourtListener MCP

- `search(type="o", case_name="Zorn v. Linton", court="scotus", filed_before="2026-05-22", num_results=3)`: returned Zorn v. Linton, No. 25-297, decided March 23, 2026; cluster 10813527, opinion 11280281. Used as pre-petition legal context.
- `read_document(opinion_id=11280281, chunk_index=0, chunk_size=14000)`: read the beginning of the per curiam opinion, including its factual posture, reversal, and specificity analysis. The response was display-truncated; no claim relies on unread dissent text.
- `search_document(opinion_id=11280281, query="petition for a writ", snippet_size=500)`: no matches; supplied no additional evidence.

## Local tooling and validation

Ran the predictor-role paths command using the literal cell identifiers. Its first invocation failed because the default uv cache location was read-only; the same command succeeded with a temporary writable cache location. This resolved a local tooling issue without changing repository files. Used shell reads and in-memory JSON arithmetic for the base-rate calculation. After writing the outputs, `uv run fedcourts validate data` with the temporary writable cache completed successfully: 29,077 artifacts valid and 40,901 references consistent. All substantive retrieval occurred on September 16, 2026.
